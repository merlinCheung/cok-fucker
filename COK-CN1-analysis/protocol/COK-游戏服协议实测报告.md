# COK（列王的纷争 / Clash of Kings 中国服）游戏服协议实测报告

> 目标：判定「游戏命令是否加密」，并判断「能否脱离 App 直连服务器」。
> **结论：协议外壳完全明文；`params` 仅用一把会话级 32 字节 XOR 密钥混淆（响应再叠一层 zlib）。
> 请求与响应现已双向 100% 可解码 —— 直连只差「拿到那把会话密钥」。**
>
> 样本：设备上的海尔渠道包 `com.hcg.cok.nearme.gamecenter` 12.06.0（versionCode 1896）
> 分析包：`5396(12.06.0)-COK_CN1--20260923-1727-10.apk`
> 设备：OnePlus PHK110 / Android 16 / arm64-v8a / Magisk root / serial `3e61bd21`
> 实测时间：2026-10-22

---

## 1. 结论速览

| 问题 | 结论 | 证据强度 |
|---|---|---|
| 游戏服地址 | `42.192.152.154:32231`（TCP 长连接） | 运行时 socket 表 + 抓包 |
| 协议 | SmartFoxServer 2X（SFS 2X）二进制协议 | 字节级解码全部自洽 |
| 包体是否整体加密 | **否**。命令名、字段名、类型标签全部明文可见 | 线上原始字节 |
| `params` 是否加密 | **是，但很轻**：32 字节循环 XOR；响应再叠 zlib 压缩 | 明/密文成对抓取 1191 字节密钥流 |
| 那把密钥 | 32 字节 ASCII，**每会话一把**；来源 = **登录响应明文字段 `id`**，密钥 = `md5_hex(id 的下划线前缀)` | 3 个会话 3 把不同密钥 + 端到端 71/71 解密成功 |
| AES-128-CBC（libgame.so 里那套） | **死代码**，运行时从未被调用 | 300+ 次 hook 零命中 + Java 侧开关=0 |
| BlowFish（`Native.BlowFishDecrypt`） | 存在但**密钥槽为空**，本 build 未启用 | 内存直读 + 零命中 |
| 能否脱离 App 直连 | **能**。请求/响应现已全部可解码；**密钥获取通道已定位**（登录握手全程明文）；**登录请求四个本地字段的算法也已全部逆出**（§5、§6）。剩余门槛是渠道账号鉴权，不是协议问题 | 见 §8 |

---

## 2. 关键纠偏：真正的实现在 Java，不在 libgame.so

静态分析第一轮盯的是 `libgame.so` 里的 C++ SFS2X SDK（`DefaultPacketEncrypter::Decrypt` 用
`EVP_aes_128_cbc` + `CryptoKey::Key/IV`），看起来「AES 密钥握手下发，静态不可得」。

**这是错的。** 运行时 hook 全部 0 命中，追查调用栈才发现：

```
libopenjdk.so!FileDispatcherImpl_write0   ← 游戏服流量走 JVM 的 NIO
```

真正在跑的是 **APK 内两份 Java 实现**：

| 层 | 位置 | 角色 |
|---|---|---|
| 官方 SDK | `com.smartfoxserver.v2.*`（classes2/3.dex） | 只用它的**序列化器** `DefaultSFSDataSerializer` 与实体类 |
| **游戏自移植版** | `sfs2x.client.*`（classes3.dex，237 类） | 真正的客户端：socket、协议编解码、握手、请求发送 |
| 业务胶水 | `org.hcg.IF.NetClient` | `send(cmd, params)` / `onResponse(map)` → 组包、解包 |
| native | `org.cocos2dx.ext.Native`（libgame.so） | 只提供 `nativeData` / `nativeDataR` / `BlowFishDecrypt` 三个 JNI |

因此 `libgame.so` 里的 `Sfs2X::Core::*` 整套 C++ SDK **一行都没执行**。

### 三层「加密」的真实状态

1. **SFS 包级 AES**（`sfs2x.client.core.DefaultPacketEncrypter`）
   实现完整（`AES/CBC/PKCS5PADDING`，key/IV 取自 `BitSwarmClient.getCryptoKey()`），
   **但开关关闭**：`cfgB + 0x11f4 == 0`（运行时内存直读），此时 `Cipher.init` 根本不会被调用。
2. **官方 SDK 的 `DefaultPacketEncrypter`**：`encrypt()` / `decrypt()` 直接 `return null`（空实现）。
3. **`Native.BlowFishDecrypt`**：存在，密钥取自 `cfgA + 0x1d8`；该槽位在本 build **为空字符串**，
   运行时 0 命中。

**真正生效的只有第 4 层：**

4. **`params` 参数体的 32 字节循环 XOR**（见 §4）。

---

## 3. 线格式（字节级，已验证）

```
+--------------------+---------------------------+
| 3 字节包头         | SFS 载荷                  |
| flags(1)           | SFSObject 编码            |
| length(2, 大端)   |                           |
+--------------------+---------------------------+
```

`flags` 位义（来自 `sfs2x.client.core.SFSIOHandler`，smali 实证）：

| 位 | 含义 |
|---|---|
| `0x80` | 长度按大端解释（本游戏恒为 1） |
| `0x40` | BlueBoxed |
| `0x20` | **载荷为 zlib 压缩**（length 是压缩后长度） |
| `0x10` | 加密（本 build 未使用） |

SFS 载荷（来自 `com.smartfoxserver.v2.protocol.serialization.DefaultSFSDataSerializer` 的 smali）：

```
SFSObject : [0x12][count : 2 字节大端]
            之后 count 组: [keyLen : 2 字节大端][key 字节][value]
value     : [typeID : 1 字节][数据]
```

| typeID | 类型 | 载荷 |
|---|---|---|
| 0x00 | NULL | — |
| 0x01 | BOOL | 1 字节 |
| 0x02 | BYTE | 1 字节 |
| 0x03 | SHORT | 2 字节大端 |
| 0x04 | INT | 4 字节大端 |
| 0x05 | LONG | 8 字节大端 |
| 0x06 | FLOAT | 4 字节 |
| 0x07 | DOUBLE | 8 字节 |
| 0x08 | UTF_STRING | [len:2 大端][UTF-8] |
| 0x09 | BOOL_ARRAY | [count:4 大端][数据] |
| 0x0a | BYTE_ARRAY | [len:4 大端][数据] |
| 0x0b–0x0f | SHORT/INT/LONG/FLOAT/DOUBLE_ARRAY | [count:4][数据] |
| 0x10 | UTF_STRING_ARRAY | [count:4][(len:2)(bytes)]* |
| 0x11 | SFS_ARRAY | [count:2 大端][value]* |
| 0x12 | SFS_OBJECT | [count:2][(keyLen:2)(key)(value)]* |
| 0x13 | CLASS | `$C` / `$F` 变体 |
| 0x14 | TEXT | [len:2][文本] |

> 注意 `0x11 SFS_ARRAY` 的 count 是 **2 字节**（不是官方 SFS2X 的 4 字节），
> 元素是纯 value 列表。这两点与官方 SDK 有出入，是实测踩过的坑。

### 请求 / 响应的外层信封（明文）

```
请求: { p: { p: { params: <密文 blob> }, r: -1, c: "<命令名>" }, a: 13, c: 1 }
响应: { p: { p: { qqq: 65, <混淆键名>: <密文 blob> }, c: "<命令名>" }, a: 13, c: 1 }
```

- `p.c` = **命令名（明文）**
- 请求的 `p.p.params` = 加密后的参数体
- 响应的 `p.p` 里是 `qqq`（整数）与一个**混淆过的二进制键名**（如 `rlQW45Y` 之外还有 20 多字节的二进制键），
  值同样是密文 blob

### 登录阶段（明文，可直接复现）

```
→ 登录请求: { p: { bin: true, cl: "Android", api: "1.8.0" }, a: 0, c: 0 }
→ 带凭证请求: { p: { appVersion: "12.06.0", luaVersion: "release_12.06.0_25",
                    pfId: "nearme:g1385224335121502465",
                    signCode: "02aad0f0e9c4323135bd50af79bcd20d",
                    buildCode: "c7d89544df01787870515c10fba1cd68",
                    deviceId: "1e933e9e19504d5", isSmall: "kao", ... } }
← 登录响应: { p: { ct: 1000001, ms: 1000000, tk: "6d0cb4f72fec985b7ed4b9ac67af1477" }, a: 0, c: 0 }
```

`tk` = 登录 token（32 位 hex）。**登录请求与登录响应全程明文、且未加密。**

---

## 4. params 加密：32 字节循环 XOR，会话级密钥

### 4.1 怎么抓到的

hook `libgame.so` 里的 `FUN_00ae02b8(data, len, keyStr*, offset)`（JNI `Native.nativeData` 的实现）。
该函数**原地加密**：进入时 `data` 是明文 SFS 字节，返回时同一 buffer 已是密文。
于是一次 hook 同时拿到明文与密文，二者 XOR 即得密钥流。

反编译确认算法（`FUN_00ae02b8`）：

```c
for (i = 0; i < len; i++)
    data[offset + i] = key[i % keylen] ^ data[offset + i];
```

> 关键字串在老版 libstdc++ ABI 下的位置是 **数据指针 - 0x18**（不是 `std::string::size()`），
> 按新 ABI 读会拿到垃圾。

### 4.2 结论

| 属性 | 实测 |
|---|---|
| 算法 | 字节级 XOR，密钥循环使用 |
| 密钥长度 | **32 字节（ASCII 十六进制字符）** |
| 密钥作用域 | **每会话一把**，会话内 260 次调用恒定；换会话必变 |
| 长度 | 不改变（XOR 非分组密码） |
| 样本密钥 A | `1204cff38117966b849be6a4b5aeef16` |
| 样本密钥 B | `274b9c246377e566ddf53c1c815d4826` |
| 样本密钥 C | `54b32b2e56a8cfddb2a5a17faa27aded` |

**请求与响应用同一把密钥**，差别只在压缩：

| 方向 | 处理链 |
|---|---|
| 请求 | `params = XOR(key, SFS(params))` |
| 响应 | `params = inflate( XOR(key, blob) )`，即 `blob = XOR(key, zlib(SFS(params)))` |

> 踩坑记录：密钥是 **32 字节**，我一度抄成 31 字节（index 15 写成 `f` 应为 `d`）。
> 后果很有迷惑性：**小于 31 字节的包能正常解，大包在第 31 字节后错位**，
> 表现为「zlib 头能解出但 inflate 中途报 invalid literal/lengths」。

### 4.3 解密后的 params 长什么样

请求侧（每个命令都带这三个公共字段）：

```json
{
  "_cok_":       "641015000016",              // 会话/账号前缀(6位) + 请求序号(6位)
  "cmdBaseTime": "1792641035",                // 服务器基准时间(Unix 秒)
  "newbasekey":  "c993db7169b4acb6668c49e61d47ca15"   // 每请求随机的 32 位 hex
}
```

命令特有字段按命令追加，例如 `pb`、`phoneDevice`、`batteryStates`、`config`、`army`、
`battleStats`、`verifyCode`、`prestigeLev`、`castlelevel`、`civilizationValueLimit` 等。

响应侧：

```json
// castleLevelUp.getLevel
{ "_cok_": "641015000006", "castlelevel": 30 }
// save.phone.device
{ "success": true }
// cmd.ping
{ "serverNowTime": 1792641030334 }
```

### 4.4 密钥从哪来 —— 已完全定位（2026-10-22 实证）

**会话 XOR 密钥 = `md5_hex(登录响应明文字段 id 中下划线之前的部分)`。**

服务端在**登录响应（明文）**的 `params` 里下发一个 `id` 字段，格式是 `<前缀>_<密钥ID>`：

```
登录响应 params.id = 4c462c581c94244362f283cd83766e4b_85
                            └─ 前缀 ─────────────┘ └ 密钥ID = 85
```

客户端（`libgame.so` 的 `FUN_0101a260`，被 `LoginCommand` 调用）的处理逻辑：

```c
id = response.params["id"];
idx = id.find('_');
prefix = id[0:idx];              // "4c462c581c94244362f283cd83766e4b"
keyId = atoi(id[idx+1:]);        // 85
md5_hex = MD5(prefix) 的小写 hex; // 5c64b9a7217a78b2e96ae87d4beaa36b
cfg->map[keyId] = md5_hex;       // map<int,string>，cfg+0x1a8
cfg->prefix = prefix;            // cfg+0x1d8
current_key_id = keyId;          // 全局，请求侧用
```

**MD5 已被字节级确认**：`FUN_017aa7e8` 写入标准 IV `0x67452301 / 0xefcdab89 / 0x98badcfe / 0x10325476`，
`FUN_017aadec` 输出 16 字节并 hex 化成 32 字符。

#### 运行时实证（同一会话全部命中）

| 用途 | 密钥 | 来源 | 实测 |
|---|---|---|---|
| 业务请求/响应 XOR（`nativeData` / `nativeDataR`） | `5c64b9a7217a78b2e96ae87d4beaa36b` | `md5("4c462c581c94244362f283cd83766e4b")` | 70+ 次加解密全部命中 |
| `ver` 热更新包解密（`FUN_0101a260` 内） | `0beb70e623638b0cc8d01dca0966f0ec` | `md5("4c462c581c94244362f283cd83766e4b_85")`（**完整 id 串**） | 解出 Lua 源码 `local curTab; function add(a,b)…` |

端到端自检：用派生的密钥解码整场会话，**71/71 个 params 解密成功，0 失败**（`verify_key.py`）。

#### 密钥 ID 的作用

- 响应里的 `p.p.qqq` 就是**密钥 ID**（本次实测 `85`），客户端把它作 `nativeDataR` 的第 4 参数，
  去 `map<int,string>` 查表取对应密钥。**同一个 `qqq` ⇒ 同一把密钥**，此前观察到的 28/65/82
  是不同会话/不同下发批次。
- 请求侧用全局 `current_key_id`（`FUN_0101a260` 写入），同样指向这把 map。

#### 因此直连客户端的密钥获取流程（全部明文，无需逆向）

```
1. TCP 连 42.192.152.154:32231
2. → {p:{bin:true, cl:"Android", api:"1.8.0"}, a:0, c:0}        # bin 握手
3. ← {p:{ct:1000001, ms:1000000, tk:"<32hex>"}, a:0, c:0}       # 拿 token
4. → {p:{appVersion,luaVersion,pfId,signCode,buildCode,deviceId,…}, zn:"COK2223", un:"<gameUid>"}, a:1, c:0
5. ← {p:{…资源版本/MD5…, id:"<前缀>_<密钥ID>", ver:"<base64>", …}}  # 明文
6. key = md5_hex(id.split('_')[0])   # 会话 XOR 密钥
   keyId = int(id.split('_')[1])     # 响应里的 qqq 也用这个
```

**步骤 1–5 全部明文**，因此独立客户端**不需要**逆向任何加密握手，只需复现第 4 步的登录参数。

---

## 5. 登录请求的四个本地字段（已全部逆出，2026-10-22）

登录请求（`a=1, c=0`）全程明文。里面有四个**客户端本地计算**的字段，逐一逆出如下，
并用**两个独立会话**的线上实测值做了交叉验证。

### 5.1 结论

| 字段 | 公式 | 是否随会话变化 |
|---|---|---|
| `signCode` | `md5( sprintf("%x", Arrays.hashCode(certDER)) + "." + 小写hex(certDER) )` | **否**（只跟 APK 签名证书有关） |
| `buildCode` | 渠道下发的固定值，存于 `UserDefault["buildcode"]` | **否**（本渠道本账号恒定） |
| `SecurityCode` | `md5( str(cmdBaseTime) + "e01684719c1bec876c10bb124a6d65aa" + game_uid )` | 是（依赖 cmdBaseTime） |
| `cc` | `md5( "d6b63d01d640fb78c979912ec839a0de" + appVersion + str(cmdBaseTime) + game_uid )` | 是（依赖 cmdBaseTime） |

`game_uid` = 账号 gameUid（如 `136063574002223`）；`appVersion` = 如 `12.06.0`；
`cmdBaseTime` = 请求里的秒级时间戳。

### 5.2 逐字段的代码依据

**`signCode`** —— `Java_org_cocos2dx_ext_Native_nativeAPKCode`：

```c
sig   = PackageManager.getPackageInfo(pkg, GET_SIGNATURES).signatures[0];
cert  = sig.toCharsString();                 // 小写 hex(DER)
sprintf(buf, "%x.", sig.hashCode());        // hashCode = Arrays.hashCode(DER)
str   = buf + cert;
signCode = md5(str);
UserDefault["theSignCode"] = signCode;      // 登录时从这里读
```

`Arrays.hashCode(byte[])` 是 Java 语义（有符号字节、`result = 31*result + b`）。
`toCharsString()` 用 `Integer.toHexString`，输出**小写**。

**`buildCode`** —— `UserDefault["buildcode"]`，由渠道侧写入
（`FUN_00cf1ef0` = `GmController::ChangeGameUID` 与 `nativeSetPlatformUID` 都会动这个键）。
本渠道实测恒为 `c7d89544df01787870515c10fba1cd68`。

**`SecurityCode` / `cc`** —— 都在登录请求构造函数 `FUN_00c2ee8c` 内，
用 `FUN_017a99e0`(MD5_Init) / `FUN_017aa548`(MD5_Update) / `FUN_017aadec`(MD5_Final+hex)：

```c
// SecurityCode
local_340 = str(cmdBaseTime);
local_340 += "e01684719c1bec876c10bb124a6d65aa";
local_340 += game_uid;                       // local_468 = UserDefault["game_uid"]
md5(local_340) -> params["SecurityCode"];

// cc
local_3f8  = "d6b63d01d640fb78c979912ec839a0de";
local_3f8 += appVersion;                     // local_418 = FUN_00a97d04()
local_3f8 += str(cmdBaseTime);               // lVar9
local_3f8 += game_uid;                       // local_468
md5(local_3f8) -> params["cc"];
```

### 5.3 数值交叉验证（三个独立会话 + 运行时 md5 输入实证）

| 会话 | cmdBaseTime | SecurityCode 线上/实算 | cc 线上/实算 |
|---|---|---|---|
| A | 1792654361 | `9de83bd25fad72dc018bf289ba42d89b` ✓ | `811a6a9b03d1f4fd7e9a2e257606a8e6` ✓ |
| B | 1792641027 | `91fc6034a167caec1fd5b126ba175206` ✓ | `ec59169ac5eae4845393b7bd9f0acf81` ✓ |
| C | 1792658351 | `014707b6687e72c32caeb40200833222` ✓ | `2a6cb8e03c0cac24492d589d1dede6fb` ✓ |

`signCode` 三会话同为 `02aad0f0e9c4323135bd50af79bcd20d`，且由 APK 证书
（`META-INF/ANDROID_.RSA` 里的 X.509 DER，`Arrays.hashCode = 0x54168fb4`）独立算出同值 ✓

**运行时实证**（hook 设备版 native `MD5_Update`，抓到真实输入缓冲）：

```
1792658351e01684719c1bec876c10bb124a6d65aa136063574002223
    → SecurityCode = md5(...) = 014707b6687e72c32caeb40200833222   与线上完全一致
d6b63d01d640fb78c979912ec839a0de12.06.01792658351136063574002223
    → cc = md5(...) = 2a6cb8e03c0cac24492d589d1dede6fb                与线上完全一致
```

即：**静态推导的拼接顺序与运行时真正送进 MD5 的字节逐字符一致**。

### 5.4 工具

```bash
cd ~/workspace/me/cok/COK-CN1-analysis/protocol
# 登录字段派生
python3 cok_sfs.py login-fields <cmdBaseTime> <gameUid> [appVersion] [signCode] [buildCode]
# 由 APK 证书派生 signCode
openssl pkcs7 -inform DER -in ANDROID_.RSA -print_certs > cert.pem
openssl x509 -in cert.pem -outform DER -out cert.der
python3 cok_sfs.py sign-code cert.der
```

---

## 6. 直连客户端（已实现，离线帧级等价验证通过）

`protocol/cok_client.py` —— 纯 Python 实现，无第三方依赖：

```bash
cd ~/workspace/me/cok/COK-CN1-analysis/protocol
python3 cok_client.py --dump-only          # 离线自检（5 项，含帧级等价）
python3 cok_client.py --cmd cmd.ping        # 直连：bin 握手 → 登录 → 派生密钥 → 发命令
python3 cok_client.py --cmd daily.quest.ls  # 只读命令
python3 cok_client.py --host s2223.cok.elexcok.com --cmd cmd.ping   # 走域名
```

流程：`bin` 握手 → 明文登录 → 从响应 `id` 派生会话密钥 → XOR 加解密业务命令。

### 6.1 关键实现细节：SFS 整数字段必须显式指定类型

客户端**不是**按值大小选最小整数类型，而是**按字段语义固定类型**。这一点做错，
服务端会**建连后立刻关闭连接**（本地实测：帧只差 1 字节就被断）。

| 位置 | 字段 | 类型 |
|---|---|---|
| 顶层 | `a`（扩展号） | **SHORT (0x03)** —— 即使值是 0 |
| 顶层 | `c`（命令号） | **BYTE (0x02)** |
| `p`（业务） | `r`（请求序号，-1） | **INT (0x04)** |
| `p`（业务） | `c`（命令名） | **STRING (0x08)** |
| `p.p`（登录参数） | 除 `gmLogin`(INT) 外**全部 STRING** —— 连 `cmdBaseTime`/`gameUid`/`serverId`/`isHDLogin` 都是字符串 |
| `device_info` | `screen_h`/`screen_w`/`screen_density`/`network_type` | **INT (0x04)** |

协议库用 `TypedInt(value, sfs_type)` 表达（`cok_sfs.py`），例如
`TypedInt(0, SFS_SHORT)`。

### 6.2 帧级等价验证

用线上抓包的真实参数重建帧，与线上帧**逐字节比对**：

```
bin 帧   : 真实 57B / 我 57B  逐字节一致 ✓
登录帧   : 真实 1368B / 我 1368B  仅 cmdBaseTime 取值不同（测试脚本填错），键序与类型完全一致 ✓
```

帧结构（登录请求，37 个参数，按客户端原键序）：

```
{ "p": { "p": {appVersion, luaVersion, pfId, gaid, isHDLogin, pfchild, signCode,
                buildCode, deviceId, isSmall, uuid, serverId, phoneDevice, gmUid,
                packageName, lang, SecurityCode, cc, fromCountry, gmLogin,
                cmdBaseTime, subscriberId, gameUid, newbasekey, afUID, googlePlay,
                pfSign, platformToken, device_info{…}, parseRegisterId, _cok_, pf,
                channelSign, baseActiveKey, linkname, region, instantAppCookie},
         "zn": "COK2223", "pw": "", "un": "<gameUid>" },
  "a": SHORT(1), "c": BYTE(0) }
```

### 6.3 服务器地址

- 线上抓到：**`42.192.152.154:32231`**（TCP）
- 对应域名：**`s2223.cok.elexcok.com`**（`s<serverId>.cok.elexcok.com`）
  —— 该域名**只在海尔渠道的 DNS 下有 A 记录**，公网 DNS（223.5.5.5 / 119.29.29.29 / 8.8.8.8）均无记录，
  所以直连优先用 IP，需要时用 `--host` 指定域名。

### 6.4 在线端到端验证（已完成，2026-10-23）

直连实测（真实服务器响应，非模拟）：

```
[*] 已连接 42.192.152.154:32231
[+] bin 握手成功 tk=de8197750240a7ecb009514a4aec41c3 ct=1000001 ms=1000000
[+] 登录成功  id=34eab6314cf5842907a74c04da2eca79_79
[+] 会话密钥 = 86138df71f1656c49cbe5fb577ce892e   密钥ID = 79
```

只读命令实测（均为服务器真实返回）：

| 命令 | 结果 |
|---|---|
| `cmd.ping` | ✓ `serverNowTime` |
| `monthlySign.info` | ✓ `multiDays` / `rewardObj` / `days` / `leftLostSignTimes` / `day2ItemIdStr`（签到状态） |
| `allianceNewBoss.bossMainInfo` | ✓ `bossInfo`（联盟 boss 明细，qqq=79） |
| `overview_new.data` | ✓ `queueList` / `noOpenList` |
| `daily.quest.ls` | 需带 `type` 参数；无参时服务端不回包（客户端会先收到 `push.*` 推送帧） |

**这证明：明文握手 → 密钥派生 → 请求加密 → 响应解密 → 真实业务数据 全链路已通。**

### 6.5 实测发现的两个服务端行为（务必知悉）

1. **新连接登录后，服务端会丢弃第一条加密业务请求**（不回任何东西，客户端表现为读超时）。
   重发同一条命令即可正常响应。客户端已内置自动重发（`call()` 默认 `retries=1`）。
   （`cmd.ping` 是明文响应，不受此影响。）

2. **同账号双开会被服务端主动断开**：App 仍在运行时用脚本连同一账号，
   脚本的连接会被服务端 close。**用脚本前请先停掉 App**（`adb shell am force-stop <pkg>`），
   否则会表现为「连接被服务端关闭」。

> 注意：服务器节点 IP 会随区服/负载变化，域名 `s<serverId>.cok.elexcok.com` 只在渠道 DNS 下有记录。
> 直连前建议先从设备侧确认当前节点：
> ```bash
> adb shell "cat /proc/net/tcp /proc/net/tcp6" | grep -i ":7DE7"   # 32231 的十六进制
> ```

---

### 6.6 直连能力实测清单（2026-10-23）

用 `probe_readonly.py` 批量跑了 82 条只读命令（带 App 真实参数），并单独验证了写操作。

| 类别 | 数量 | 说明 |
|---|---|---|
| 只读命令 **实测成功** | **76** | 响应字段均为服务器真实返回（玩家/联盟/商城/科技/任务/活动/签到/排行/皮肤…） |
| 只读命令 返回业务错误 | 6 | 其中 4 条 **App 自己也是同样的错误码**（正常业务状态）；2 条是游标依赖 |
| 只读命令 超时 | 0 | — |
| **写操作 实测成功** | 3 | 见下表 |

实测成功的写操作：

| 命令 | 参数 | 响应 | 副作用 |
|---|---|---|---|
| `save.phone.device` | `phoneDevice` / `batteryStates` | `{"success": true}` | 无（纯设备上报） |
| `resource.client.reward.get` | `rewardId` | `award[]` 逐项奖励明细 | **会领奖**（小号已验证：领奖后 `monthlySign.info` 状态变化） |
| `resource.client.reward.getmulti` | `rewardIds`（`;` 分隔） | `rewardsObj`：每个 id 的 award | **会批量领奖** |

实测领奖返回（`reward.get {rewardId:43011278}`）：
```
{ "type":7, "num":1,     "id":"212588" }
{ "type":7, "num":5000,  "id":"36005606" }
{ "type":7, "num":5000,  "id":"36007998" }
{ "type":7, "num":40000, "id":"211508" }
```

### 6.7 参数类型敏感（服务端会因类型不对返回 E000000）

**同一个字段用 STRING 传 → `E000000`；用 INT/LONG 传 → 正常返回。**
例如 `worldboss` 的 `op`/`type`、`itemcollection.data` 的 `itemType`、
`check.result` 的 `cP` 在 App 侧都是 **INT**，改对类型后命令立刻成功。

已从抓包复原出**带 SFS 类型**的参数目录 `command-catalog-typed.json`
（61 条命令），客户端 `cok_client.py` 默认按它编码，使用者无需关心类型。

### 6.8 本游戏服务端的 SFS 数组 count 是 2 字节（非官方 4 字节）

这是本项目最隐蔽的解码坑，已实测确认：

| 类型 | 含义 | count 长度 |
|---|---|---|
| `0x11` | SFS_ARRAY | **2 字节** |
| `0x10` | SFS_STRING_ARRAY | **2 字节**（元素是 `[len:2][data]`） |

按官方 4 字节读会整体错位，表现为 `unpack_from requires a buffer of at least N bytes`
或 `not enough values to unpack` —— `skin.introduction` 就是这样解不出来的。

另外两点：
- **每个数组要独立探测编码模式**（纯值 `val` vs `(key,value)` 对 `kv`）：
  同一份响应里可以两种模式并存，全局传一个模式必然有一处解错。
  判据是「数组首字节是否为合法 SFS 类型（0x00–0x14）」。
- 客户端解码统一走 `parse_best()`（会遍历模式并要求完整消费缓冲区），
  不要直接用 `read_value()`。

完整清单见 [`COMMANDS.md`](COMMANDS.md)；机器可读版见 `command-catalog.json`、
`command-catalog-typed.json`、`readonly-commands.json`。

---

### 6.9 常驻监控器（已实测，2026-10-23）

`protocol/cok_daemon.py` —— 脱离 App 持续跟踪游戏状态，详见 [`DAEMON.md`](DAEMON.md)。

```
python3 cok_daemon.py                # 每 5 分钟一轮
python3 cok_daemon.py --interval 60  # 60 秒一轮
python3 cok_daemon.py --json         # 机器可读
python3 cok_daemon.py --claim        # 自动领奖(有副作用)
```

已实现：自动连接/自动重连、`cmd.ping` 保活、**状态指纹去重（只在变化时输出）**、
服务器时间基准（UTC+8 判定“今天”，不受本机时区影响）、`--log` 追加日志、
`--json` 机器可读输出、领奖已领记忆 + 单轮/全局双上限。

监控 6 项：每日签到、周任务、领主任务、主线任务、联盟 boss、建造队列。

实测输出（节选）：

```
[11:12:34] state {"watch":"dailySign","state":{"今日已签":false,"今日(第23天)":true,
                       "已签日期":[16,17,18,19,20,21,22],"剩余补签次数":3,
                       "月卡档位":"3;5","本月月卡发放日":["10-3","10-5"],"今天是月卡日":true}}
[11:12:35] state {"watch":"dailyQuest","state":{"周任务积分":1513,
                       "周任务可领奖励":["5000210","5000211"],"可领日常任务":[...]}}
[11:12:35] state {"watch":"storyTask","state":{"章节":1,"已完成任务奖励":["254310"],"任务数":4}}
```

自动领奖实测（`--claim`）：

```
[11:16:41] claim        {"note":"准备领奖","rewardIds":["5000210","5000211","254310"]}
[11:16:41] claim_result {"rewardId":"5000210","award":[]}
[11:16:41] claim_result {"rewardId":"5000211","award":[]}
[11:16:41] claim_result {"rewardId":"254310","award":[{"type":7,"value":{"num":1,"id":"200393"}}]}
```

> 踩坑：`story.task.info` 的 `state==1` 表示**任务已完成**，**不等于“可领”** ——
> 实测领完 `254310` 后 `state` 仍是 1（多个任务可共用同一奖励 id）。
> 所以常驻工具只报「已完成任务的奖励」，是否真的可领以领奖接口返回的 `award` 为准，
> 并用「已领记忆」避免重复领。

---

### 6.10 自动签到与告警（已实测，2026-10-23）

**自动签到**（命令来自 `game/WelfareIntegrate/signIn/integrateSignInCmd.lua`）：

| 命令 | 参数 | 说明 |
|---|---|---|
| `monthlySign.info` | — | 查询签到状态（已验） |
| **`monthlySign.sign`** | — | **每日签到**（已实测成功） |
| `monthlySign.claimMultiRewards` | `multiDays`（3 或 5） | 领月卡当天奖励 |

实测签到闭环：

```
签到前: 已签日期 = 16;17;18;19;20;21;22      剩余补签次数 = 3
→ monthlySign.sign
响应:  {"reward":[{"type":7,"value":{"itemId":"211508","rewardAdd":20000,"count":709717, ...}}]}
签到后: 已签日期 = 16;17;18;19;20;21;22;23    剩余补签次数 = 3
```

**告警**：`--webhook <URL> --webhook-type {generic,wechat,dingtalk}`，
规则 `sign` / `claim` / `task` / `boss` / `error` 可用 `--alert-rules` 选。
载荷格式（generic）：
`{"kind":"sign","title":"每日签到完成","text":"...","value":{...},"ts":"2026-10-23 11:23:06"}`。
推送失败不会中断监控，只在本地打印 `[alert:alert_error]`。

> ⚠️ **服务端允许重复发放同一签到奖励** —— 实测手动签到后 `monthlySign.info` 的
> `days` 已含今天，但再发一次 `monthlySign.sign` 仍会返回奖励。
> 所以常驻工具用「`days` 是否已含今天」做**幂等判断**，已签则 `sign_skip` 不再发。

---

### 6.11 命令全集与精确领奖命令（2026-10-23）

**从 Lua 的 `utils.requestServer(...)` 调用里提取到 757 条命令名**（存档 `command-names.json`），
远多于此前从抓包复原的 101 条。这些命令名带**权威的参数语义**（Lua 里就是怎么拼的），
是扩充命令面的最佳来源。

由此找到的**精确领奖命令**（比通用 `resource.client.reward.get` 语义更明确）：

| 命令 | 参数(Lua 实证) | 语义 | 实测返回 |
|---|---|---|---|
| `lordTask.reward.process` | `index` = **INT**（`CCInteger:create(index)`） | 领阶段奖励 | `index=19`→E000004；`index=0`→164317(已领) |
| `lordTask.reward.task` | `taskId` = **STRING**（`CCString:create(taskId)`） | 领任务奖励 | 10200062(已领) |
| `monthlySign.sign` | — | 每日签到 | 奖励明细（实测金币 ×20000） |
| `monthlySign.claimMultiRewards` | `multiDays` = **INT** | 领月卡当天奖励 | INT→E000004；STRING→E000000 |

> `multiDays` 传 STRING 得到 **E000000**、传 INT 得到 **E000004** ——
> 再次印证「服务端对参数类型敏感」：E000000 = 参数类型/结构错，E000004 = 类型对了但业务状态不满足。

**Lua 侧命令提取方法**（可复用）：

```bash
grep -rhoE "requestServer\(\s*'[a-zA-Z0-9_.]+'" assets/lua_static/ | sed "s/.*'//;s/'//" | sort -u
```

同目录下 `initWithName('...')` 只能覆盖约 80 条，`requestServer` 才是全集入口。

---

### 6.12 渠道 token 自动化：直接读设备本地（已完成，2026-10-23）

不必再从抓包复原 token —— **账号参数全部存在 App 的 SharedPreferences 里**，
用 `protocol/cok_account.py` 读取即可（需 root）：

| 来源文件 | 键 | 用途 |
|---|---|---|
| `com.nearme.gamecenter.open.xml` | `gcsdk_tag_local_role_info` → `roleid` | **渠道 token** = `platformToken`；`pfId` = `"nearme:" + roleid` |
| `Cocos2dxPrefsFile.xml` | `game_uid` | `gameUid` |
| `Cocos2dxPrefsFile.xml` | `device_uid` | `deviceId` |
| `Cocos2dxPrefsFile.xml` | `account_uuid` | `uuid` |
| `Cocos2dxPrefsFile.xml` | `buildcode` | `buildCode` |
| `Cocos2dxPrefsFile.xml` | `theSignCode` | `signCode` |
| `Cocos2dxPrefsFile.xml` | `account_ip` / `account_port` | **游戏服地址**（`txaia-cok.elexapp.com` / `32231`） |
| `Cocos2dxPrefsFile.xml` | `account_zone` | `zn`（`COK2223`） |

```bash
python3 cok_account.py                 # 打印读到的参数
python3 cok_account.py --write acc.json # 导出成账号文件
python3 cok_client.py --account-device --cmd monthlySign.info   # 一键直连
```

实测（`--account-device` 端到端）：

```
[+] 已从设备读取账号: {"pfId":"nearme:g1385224335121502465","gameUid":"136063574002223",
                        "host":"txaia-cok.elexapp.com","port":32231}
[*] 已连接 txaia-cok.elexapp.com:32231
[+] bin 握手成功 tk=… ct=1000001 ms=1000000
[+] 登录成功  id=617993ea3d2fcbe7b9c80780815e01f4_96
[+] 会话密钥 = f60f744c0fb4bef298c089831d1a032f   密钥ID = 96
```

> **服务器地址改用域名 `txaia-cok.elexapp.com`**（解析到 42.192.152.154），
> 就不怕 IP 轮换了。`s2223.cok.elexcok.com` 只在渠道 DNS 下有记录，公共 DNS 查不到。

### 6.13 建造/加速命令族（`queue.ccd` 已定位并实测成功，2026-10-23）

**探测方法**：`build.info` 等命令直接盲试，用**返回 errorCode 还是超时**区分
「命令存在但参数不足」与「命令名不存在」。

| 命令 | 参数 | 实测 | 判定 |
|---|---|---|---|
| **`queue.ccd`** | 7 个字段（见下表） | ✓ **`finished:true`，建造立即完成，金币 48035→47460** | **存在，已实测成功** |
| `build.info` | 无 | ✓ 返回 `gold` / `resource` / **`buildingQueue`** / `building` | **存在，已实测** |
| `build.upgrade` / `build.create` / `build.destroy` | 缺 | `E000000` | 存在，参数不足 |
| `build.collect` | 缺 | `E000004` | 存在，业务状态不满足 |
| `build.ccd` | 缺 | 无响应 | 只见于响应分发函数，客户端不主动发 |
| `queue.finish` | `uuid`(STRING) | `E100159` | 存在，状态不允许（该 uuid 是建造队列） |
| `queue.open` / `queue.cancel` / `queue.rent` / `queue.tool` / `queue.one.key` | 缺 | `E000000` | 存在，参数不足 |
| `civilizationQueue.speedQueue` / `finishQueue` / `cancelQueue` | 缺 | `E000000` | 存在（**内城文明队列**，非主城） |
| `civilizationCastle.info` / `upgradeBuilding` / `createBuilding` / `destroyBuilding` / `getBuildingView` / `addNewPos` | 缺 | `E000000` | 存在，参数不足 |
| `newBoat.speedUp` | `uuid`(STRING) | 无参超时；`uuid=""`→`E000000` | 存在 |
| `newBoat.oneKeySendShip` | 无 | ✓ `{"array": []}` | 存在，已实测 |
| `dockTrade.speedUp` / `nightCityDock.speedUp` | `uuid`(STRING) | — | 存在（Lua 实证） |

#### 6.13.1 主城建造队列加速 = `queue.ccd`（实测生效）

```jsonc
{
  "qUUID":     "f2bb9577d6e1409a9688b22ffbc2a6c0",  // STRING —— 队列 uuid(不是建造物 uuid!)
  "itemUUID":  "",                                   // STRING —— 加速道具 id, 空 = 用金币
  "isGold":    1,                                    // INT    —— 1 = 用金币
  "itemCount": 1,                                    // INT    —— 道具数量
  "queueId":   "1",                                  // STRING —— qid(注意是字符串!)
  "queueType": "1",                                  // STRING —— 1 = 建造队列, 2 = 造兵队列
  "goldcost":  "0"                                   // STRING —— 金币消耗(上报值, 服务端自算)
}
```

**成功响应**：

```json
{"remainGold": 47460, "itemObj": {}, "totalTime": 0, "startTime": 0, "updateTime": 0,
 "finished": true, "endTime": 0, "type": 0,
 "uuid": "f2bb9577d6e1409a9688b22ffbc2a6c0", "qid": 1}
```

**交叉验证（加速前后两次 `build.info` 对比）**：

| 字段 | 加速前 | 加速后 |
|---|---|---|
| `buildingQueue[0].totalTime` | `45342176`（≈12.6 小时） | `0` |
| `buildingQueue[0].startTime` | `1792716532553` | `0` |
| `buildingQueue[0].itemObj` | `{building:"410000;26", opType:1, para1:"12500", …}` | `{}` |
| `gold` | `48035` | `47460`（扣 575） |

加速后再次调用同一命令 → `E100179`（队列已完成，状态不允许），与「已经生效」自洽。

> **注意**：`qUUID` 取的是 `buildingQueue[].uuid`（**队列** uuid），
> **不是** `buildingQueue[].itemObj.uuid`（建造物 uuid）。用错会一直 `E000000`。
> `queueId` / `queueType` / `goldcost` 三个字段**必须存在**，缺任一 → `E000000`；
> 它们的值是**字符串**（native 侧用 `%d` 格式化），传 INT 会失败。

#### 6.13.2 定位方法（可复现，无需用户在 App 手点）

盲试命令名不可行（服务端对未知命令**静默忽略**，超时无法区分存在性）。
最终靠**静态定位 + 定点实测**闭环：

1. **Lua 侧**：`game/speedup/UseSpeedUpView.lua` / `game/buildQueue/BuildQueueLineCell.lua`
   给出入口 —— `FunBuildController:call("costCD", buildingKey, itemId, …)` 与
   `QueueController:call("startCCDQueue", qid, itemId, isGold, gold, "", type, "", itemUseCount)`。
   **CCD = ccd** —— 命令名后缀由此确定。
2. **device 版 `libgame.so` 字符串表**：`queue.open | queue.ccd | queue.finish | queue.cancel |
   queue.rent | queue.tool | queue.one.key`（主城队列族）与
   `civilizationQueue.speedQueue | finishQueue | cancelQueue`（内城文明队列族）成组出现。
3. **ARM64 静态 xref**（自写 `elf_xref.py` + `disasm_strings.py`，capstone）：
   在 device 版 ELF 里对 `queue.ccd` 做 `ADRP+ADD` 引用扫描 → 命中 `0xfded00`；
   反汇编该窗口 → 拿到该请求的**全部 7 个字段名**及其类型
   （`qUUID`/`itemUUID`/`queueId`/`queueType`/`goldcost` 为 STRING，`isGold`/`itemCount` 为 INT）。
4. **定点实测**：只测 `queue.ccd`（不再盲试名字），用上表参数 → 成功。

> device 版与分析版 libgame.so **不是同一构建**（`release_12.06.0_25` vs `_11`），
> 静态偏移会变；device 版比分析版**多 3 个字段**（`queueId`/`queueType`/`goldcost`），
> 字段名以 **device 版为准**（运行时跑的就是它）。

#### 6.13.3 `build.info` 的队列结构（修正）

```
buildingQueue = [
  { uuid:"f2bb9577…", qid:1, type:0, isHelped:1, startTime:1792716532553,
    totalTime:45342176, endTime:0, updateTime:…,
    itemObj:{ uuid:"3276c0a3…", building:"410000;26", opType:1, para1:"12500", … } },  ← 建造中
  { uuid:"8d7bfc50…", qid:3, type:0, totalTime:0, endTime:1792121533661, itemObj:{} },  ← 已完成
  { uuid:"94e8cdae…", qid:2, type:0, totalTime:0, endTime:1792664645808, itemObj:{} } ]  ← 已完成
]
```

> 注意：**`overview_new.data` 的 `queueList` 不给 uuid，`build.info` 的 `buildingQueue` 才给** ——
> 这是之前找不到可加速对象的原因。
> 队列 uuid = 顶层 `uuid`；`itemObj.uuid` 是**建造物** uuid，两者不可混用。

> **关键校准（对照实验实测）**：服务端对**未知命令名是静默忽略**——不回包、也不断连。
> 因此「超时」**不能**证明命令不存在，盲试命令名这条路整体不可行。
> 对照组：`cmd.ping`→DATA / `daily.quest.ls`→DATA(102192) / `zzz.definitely.not.a.cmd`→超时。
> **有响应**（含 errorCode）才能证明命令存在：`E000000`=参数类型/结构错，
> `E000004`/`102192`/`E100159`/`E100179`/`164317`=类型对但业务状态不满足。
>
> **另一条校准（同日实测）**：**已知命令缺必需参数**时，服务端**可能直接关闭连接**而不是回 errorCode
> （`hot.item.get` 无参 → 连接被服务端关闭）。所以「连接被关闭」= 命令存在但参数不合规，
> 与「超时（静默忽略）」是**两种不同的失败信号**。

#### 6.13.4 加速道具：用道具而不是烧金币

道具路径与金币路径**只有两个字段不同**：

| 字段 | 金币（**已实测成功**） | 道具（配方已反出，未跑通） |
|---|---|---|
| `itemUUID` | `""` | **道具实例 uuid**（32 位 hex，如 `3757a02129df4a5ba8c25e59f3495678`） |
| `isGold` | `1` | `0` |

其余 `qUUID` / `itemCount` / `queueId` / `queueType` / `goldcost` 完全相同。

**加速道具一共有 471 个 / 35 类** —— 城建、造兵、科技、陷阱、伤兵治疗、行军、联盟、阵法… 各有各的。
道具配置来源：客户端**服务端下发**的
`/data/data/com.hcg.cok.nearme.gamecenter/files/database.local.xml`（45.8 MB 明文 XML，
`su -c cat` 读；adb pull 权限拒绝）。字段含义：

- `type=2` → `ITEM_TYPE_SPD` 加速道具（Lua `gameConst.lua`）
- `type2` → `ItemSpdMenu_*`（同文件 `ItemSpdMenu = {...}` 定义，共 0–23）
- 时长 → `para` 第 3 段（秒），缺失时取 `display_quantity` 第 2 段

**`ItemSpdMenu` 真实定义**（第一次整理时把 3/9/19/2 的标签贴错了，以本表为准）：

| type2 | ItemSpdMenu | 含义 | 适用 queueType |
|---|---|---|---|
| **1** | **`ALL`** | **通用：城建，造兵，科技，造陷阱，治疗** | **1,2 都行** ★ |
| 7 | City | 城建 | 1 |
| 3 | Soldier | 造兵 | 2 |
| 6 | Science | 科技 | 1 |
| 4 | Heal | 伤兵治疗 | 1 |
| 5 | Trap | 造陷阱 | 1 |
| 9 | Alliance | 联盟 | 1 |
| 10 | Mate | 造材料 | 1 |
| 11 | HighTech | 新科技 | 1 |
| 12 | JieLv | 戒律大厅 | 1 |
| 13 | Civ_City | 文明堡垒分城城建 | 1 |
| 14 | Tactical | 阵法研习 | 1 |
| 19 | RaceScience | 先祖之魂 | 1 |
| 21 | Armament | 军械库 | 1 |
| 22 | ArmyReform | 士兵改造 | 1 |
| 23 | ForeignCiviTech | 外来文明科技 | 1 |
| 2 | Troop | 行军 | 不走队列（`SpeedUpMarch`） |
| 8 | DuanZao | 锻造 | 不走队列 |
| 0 | BuildingRemove | 拆除 | 1 |

> `type2` 为 15/16/17/25/26/28/30/32/33/34/37/38/39/50/58/61/98/99 的是**其它用途道具**
> （联盟任务道具等），`ItemSpdMenu` 未定义，加速面板不会显示，**不是加速道具**。

**「具体用哪个道具」是能确定的** —— 三个字段各管一件事：

| 字段 | 作用 | 取值来源 |
|---|---|---|
| `queueType` | **加速哪条队列** | `1`=建造队列，`2`=造兵队列 |
| `qUUID` | **具体是哪个功能**（主城/联盟/科技/治疗…） | `build.info` 等命令返回的**队列 uuid** |
| 道具 `type2` | **道具本身适不适用** | 服务端按道具 type2 校验 |

Lua 调用点印证 `queueType` 的含义：`productionSoldier` 用
`startCCDQueue(qid, "", false, gold, "", 2)`（造兵=2），其余建造类一律 `…, "", 1`。

**选型结论**：

- 主城建造队列（`queueType=1`）→ 用 **`type2=7`**（城建专用）或 **`type2=1`**（通用）
- 造兵队列（`queueType=2`）→ 用 **`type2=3`**（造兵专用）或 **`type2=1`**（通用）
- **`type2=1` 通用道具最省心**：两类队列都能用，无需判断场景

**城建专用（type2=7，10 个）**：

| id | 200229 | 200215 | 200251 | 200252 | 200216 | 200253 | 200254 | 211523 | 211524 | 211525 |
|---|---|---|---|---|---|---|---|---|---|---|
| 时长 | 1分 | 5分 | 10分 | 15分 | 2时 | 12时 | 1天 | 3天 | 7天 | 15天 |

**通用（type2=1，18 个）**：

| id | 200224 | 200201 | 200222 | 200235 | 200236 | 200200 | 200223 | 209200 | 200202 | 200231 | 200237 | 200232 | 200233 | 200238 | 200234 | 211511 | 211512 | 211513 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 时长 | 1分 | 5分 | 5分 | 10分 | 15分 | 1时 | 1时 | 1时 | 8时 | 12时 | 12时 | 16时 | 1天 | 1天 | 32时 | 3天 | 7天 | 15天 |

完整 471 个道具（含每个 type2 的 `queue_type` 适用标注）见 `speedup-items.json`。

> **诚实标注**：道具路径的命令名、7 个字段名、字段类型**全部来自 device 版二进制与 App 真实代码路径**
> （`UseSpeedUpView.lua` → `QueueController:call("startCCDQueue", …)` → native 构造），
> 属**静态反推**；**尚未在服务端跑通一次道具加速**（需要一条进行中的建造队列作为加速对象，
> 且需确认账号持有哪些道具、各多少）。金币路径是唯一已跑通的路径。
> 验证手段：`frida/capture_queue.js` 探针（hook device 版 `0x9e7dec` `set_value` 与 `0x2ce70ec`
> `get_string`），在 App 里用道具加速一次即可读到真实 `itemUUID` / `itemCount` / `isGold`。

#### 6.13.5 道具加速的 App 侧实证（2026-10-23，已抓到真实请求）

frida 探针（hook device 版 `0x9e7dec` `set_value` + `0x2ce70ec` `get_string`）
抓到 App 加速面板里点 3 次（3 种不同加速）时**真实发出的请求**：

| 次 | qUUID（队列） | itemUUID（道具） | isGold | itemCount |
|---|---|---|---|---|
| 1 | `9f993a6425a64d6cb48d9289a628ecc5` | `3757a02129df4a5ba8c25e59f3495678` | 0 | 68 |
| 2 | 同上 | `1de38e919ce743c1ad69fdebb45a11ba` | 0 | 2 |
| 3 | 同上 | `4600cedc8e8a43aeaa5aefba97b7bfa7` | 0 | 1 |

**三条修正**（与早期静态推断不同，以此为准）：

1. **`itemUUID` 是道具实例 uuid（32 位 hex），不是配置里的数字道具 id。**
   `speedup-items.json` 里的 `200229` / `200224` 是**道具模板 id**（配置表 `ItemSpec.id`），
   **不能直接填进协议**；协议要的是背包里该道具条目的实例 uuid。
2. **造兵加速只发 4 个字段** —— `queueId` / `queueType` / `goldcost` **一个都不发**；
   而主城建造（实测跑通那次）发的是 7 个字段。
   → **字段集随场景变化；队列类型由 `qUUID` 自身决定，不靠 `queueType`。**
3. **造兵队列 uuid 不在 `build.info` 的 `buildingQueue` 里**（那里只有建造队列）。

**探针方法**（可复用）：

- device 版 `set_value` = `0x9e7dec`，`get_string` = `0x2ce70ec`，
  `make_str` = `0x2f7a6fc`（三者都是真函数，可直接 Interceptor）；
  `set_str` = `0x8fb620` **是 PLT 存根**，要从 GOT `base+0x3acc9f0` 读真实地址再挂。
- **key 不用读 std::string**：`make_str` 刚构造的**字面量**就是 key
  （反汇编里顺序固定：`make_str(key)` → `get_string(value)` → `set_value(key, value)`），
  维护最近字面量环形缓冲即可 100% 命中。
  （踩坑：libc++ `std::string` 布局判错 → key 全是乱码 → 被过滤器全丢，**hook 却显示成功**。）
- **终极方案**：XOR 引擎 device 版 `0x9e02b8`，签名
  `void xor_at(char* buf, int len, std::string* key, int offset)`，**原地**异或。
  同一函数两个方向共用：`onEnter` 读 buf = 调用前，`onLeave` 读 buf = 调用后。
  首字节 `0x78`(zlib) = 响应方向、`0x12`(SFS_OBJECT) = 请求方向。
  → **一个 hook 就能拿到双向明文**（`capture_plain.js` + `parse_plain.py`）。

**已打通的环**（2026-10-23）：① 目标队列 uuid ← 登录后 `init` 推送的 `queue[]`；
② 道具实例 uuid ← App 侧探针抓的背包快照 `speedup-owned.json`。
**仍未自动化**：道具实例 uuid 的服务端下发接口（`cemetery.get.info` 直连被踢连接），
所以"直连自己找道具"还差这一步，见 §6.13.6。

#### 6.13.6 加速道具路径：直连实测跑通（2026-10-23，闭环完成）

```jsonc
{"qUUID":"9f993a6425a64d6cb48d9289a628ecc5",   // 队列 uuid
 "itemUUID":"4600cedc8e8a43aeaa5aefba97b7bfa7", // 道具**实例** uuid
 "isGold":0, "itemCount":1}
```

**实测响应**：

```json
{"count":39919,"itemId":"200201","remainGold":47460,"finished":false,
 "type":1,"uuid":"9f993a6425a64d6cb48d9289a628ecc5","qid":1,
 "totalTime":491086044,"startTime":1792750070271,"endTime":0}
```

| 检验点 | 结果 |
|---|---|
| 道具消耗 | `count` **39920 → 39919** |
| 金币 | `remainGold` **47460 未变**（没烧金币） |
| 道具回显 | `itemId: "200201"` |
| 目标队列 | `uuid` = type=1 造兵队列 |

**三处字段名纠正（响应回显证实）**：

- 请求道具数量 = `itemCount`；**响应**回显的是 `count`
- 请求道具实例 = `itemUUID`；**响应**回显的模板 id = `itemId`
- 响应 `totalTime` **不因加速而变** —— 加速是**时间抵扣**，不是重置 totalTime

**队列 uuid 的来源：登录后服务端的 `init` 推送**（直连可收）：

```python
from cok_sfs import decode_params
o, mode, raw = decode_params(bytes.fromhex(混淆键), 会话密钥)
queues = o["queue"]        # 25 条
```

每条 `{itemObj, totalTime, startTime, updateTime, endTime, type, uuid, qid, isHelped}`；
`type` = 队列类型（`0`=建造、**`1`=造兵**、`2`=行军、`9`=联盟…），
`totalTime>0 && startTime>0` = 进行中。收帧时 **recv 超时要 continue 不要 break**。

**背包 `items`**（474 条，`{itemId, uuid, count, useDate, vanishTime}`）在
`cemetery.get.info` 响应里，**但直连调该命令会被服务端主动踢连接**（重试/先 ping 均无效）——
**道具实例 uuid 的全自动获取尚未闭环**，目前用 App 侧探针抓到的实例 uuid
（清单见 `speedup-owned.json`）。

**开箱工具**：`cok_speedup.py`（列队列 + 道具/金币加速）。

#### 6.13.7 `build.upgrade`（顺带定位，未实测）

同样用「静态 xref → 反汇编」定位，参数集（8 个字段，全 int）：

```
buildingId  ← 建筑对象 +0x24     level   ← +0xc8      star   ← +0x44
process     ← +0x158            position← +0xac      costTime← 栈参数
gold        ← 栈参数            isInstant ← 常量
```

`build.info` 的 `building[]` 给出 `building`（格式 `"400000;17"` = buildingId;position）、
`level`、`starNum`、`pos` 等，可据此拼参数。**未实测**（该命令会消耗资源升级建筑）。

---

#### 6.13.8 世界行军 / 回城 / 保护罩（命令层已定位，2026-10-23）

用 §6.13.2 的静态链路（Lua `initWithName` 清单 → native 字符串表 → ARM64 xref → 反汇编取字段）
定位到三个新能力的命令层：

| 能力 | 命令 | 参数 | 状态 |
|---|---|---|---|
| **保护罩查询** | `onekeybuff.get` | 无 | ✅ **直连实测跑通**：`{"backList":[{"statusList":[],"name":"","type":1},{"…","type":2},{"…","type":3}]}` |
| **开保护罩** | `onekeybuff.use` | `type`(INT) + `coverOld`(BOOL) | ✅ 参数取自 `OneKeyBuffManager.lua` 明文（`putParam`），未实测 |
| 保存预设 | `onekeybuff.save` | `statusList`(STRING) + `type`(INT) | ✅ 同上 |
| 预设改名 | `onekeybuff.rename` | `name`(STRING) + `type`(INT) | ✅ 同上 |
| **回城(通用)** | `march.cancel` | `marchId`(STRING) + `type`(INT) | ✅ 字段已定位（`WorldMarchCancelCommand`，0x11dd628） |
| **回城(世界)** | `world.march.retreat` | `uuid`(STRING) + `itemUUid`(STRING) + `type`(INT) | ✅ 字段已定位（注意 `itemUUid` 是**两个 U**） |
| **派遣部队(世界采集)** | `world.march` | `point` / `type` / `ownerFlag` / `team` / `is` / `marchKey` / `pointX` / `pointY` / `tileServerId` / `index` / `cityType` / `playerUid` / `marchId` | ⚠️ 参数大半定位，`team` 结构与 `marchKey` 生成规则待补 |

**被攻击信号**（服务端 push，直连已能收）：

```
push.world.injured        部队被攻击/受伤
push.world.cannon.injured  炮台被攻击
push.world.march.fail      行军失败
push.world.march.win       战斗胜利
push.world.march.retreat   行军被撤回
push.protect.time          保护罩时间变更
```

**三个能力的落地度**：

1. **自动开保护罩** —— 最接近可用。`onekeybuff.get` 已实测通，`backList` 有 3 个预设组
   （`type` = 1/2/3），`onekeybuff.use {type, coverOld}` 参数完全确定。
   **待定**：哪个 `type` 是保护罩（`statusList` 存的是该组道具 id，账号当前 3 组全空 = 没开过罩），
   以及账号是否有保护罩道具 —— 需要在 App 里开一次罩，用探针抓真实参数即可确定。
2. **被攻击自动回城** —— 命令与信号都确定了，**缺 `marchId` 的获取通道**
   （`world.get.march` 无参会断连，需要参数）。
   逻辑链：收 `push.world.injured` → 取该部队 `marchId` → 发 `march.cancel {marchId, type}`。
3. **世界自动采集** —— 命令与大半参数已定位，但 `world.march` 还要补 `team` 结构与
   `marchKey` 生成规则（`marchKey` 看着像带签名的串，native 里有个常量 `wNSc5Mm8YwiOhAab`）。
   而且**"自动"是策略层工程**：选资源点 → 派兵 → 等待采集完成 → 撤回，
   命令只是执行器，不是自动化本身。

> ⚠️ **这三个都是有真实副作用的操作**：派遣/撤回消耗部队与体力，
> 开保护罩消耗道具，回城可能损失战利品。**风控上也更敏感**（主动出征比只读/领奖更容易被识别）。
> 建议顺序：保护罩（最简单、纯道具）→ 回城（纯防守）→ 采集（主动出征，最后做）。

## 7. 抓到的真实命令

一次 200 秒会话内实证到的命令（请求 194 帧 / 响应 177 帧）：

```
cmd.ping                       allianceNewBoss.bossMainInfo   worldboss
login.other                    login.dataconfig              resource.client.reward.get
resource.client.reward.getmulti trigger.activity              castleLevelUp.getLevel
branchcity.enter               festivalview.data              shadowDragon.data
convoy.login                   get.user.info.multi            luckyday.effect
kingdomtask_new.data           save.phone.device              cemetery.get.info
daily.quest.ls                 civilization.prestige.info     hero.introduction
cok.proto                      allianceBoss.enter            oneKeyLoad.data
alquick.data                   buidlingextension.resEffect    strengthen.info
kingdomBiography.info          treasuremap.info               allianceBoss.enter
push.server.action             exchange.refresh               accountLock.getUnlockView
scanctuary.data                newBoat.data                   magic.effectList
stat.tt                        science.data.cond              auction.getView
formation.getData              skin.introduction              skill.state.get
matchAct.info                  relic.getRelicList              godGift.info
overview_new.data              gem.getDigView                 achieve.ls
mall.info                      drawNew.info                   nfight.data
chat.get.system.mails          chat.room.invitee              chat.get.new.mails
redPackets.rvd.id              contact.get.server.current      permissionCommandInfo
```

`resource.client.reward.get` / `resource.client.reward.getmulti`（领奖）、`daily.quest.ls`（日常任务列表）、
`allianceNewBoss.bossMainInfo` / `allianceBoss.enter`（联盟 boss）、`get.user.info.multi`、
`worldboss`、`kingdomtask_new.data`、`login.dataconfig`（配置）等都已被抓到并可完整解码参数。

> 之前静态分析出的 2158 条命令词表（`game-protocol-commands-union.txt`）依然有效；
> 这里列出的是**运行时实证**、带完整参数样本的命令。

---

## 8. 能不能脱离 App 直连？—— 分层结论

**技术上可行，而且协议侧已经没有黑盒了：请求能造、响应能读。
**直连客户端已实现在线跑通（见 §6.4），真实服务器返回了业务数据。**

### 已经解决的
- 线格式、包头位义、SFS 类型表、数组编码差异 —— 全部字节级实证
- 请求参数结构与公共字段（`_cok_` / `cmdBaseTime` / `newbasekey`）
- 响应参数结构（含混淆键名与 `qqq` key id）
- 命令名、字段名、字段值类型全部可读
- 登录握手（明文）+ token 下发流程
- **会话密钥的派生与获取**（`md5_hex(id 前缀)`，`id` 来自登录响应明文字段）
- **登录请求四个本地字段的算法**（`signCode` / `buildCode` / `SecurityCode` / `cc`，见 §5）
- **SFS 整数字段的显式类型规则**（`a`=SHORT / `c`=BYTE / `r`=INT，见 §6.1）
- **直连客户端**（§6）：握手 → 登录 → 派生密钥 → 发命令 → 解响应，已在线验证
- **主城建造队列加速命令 `queue.ccd`**（§6.13）：7 字段参数集已反出并实测生效，
  建造队列 12.6 小时 → 立即完成
- **命令名的静态定位链路**（§6.13.2）：Lua 入口 → native 字符串表 → ARM64 xref → 反汇编取字段名 → 定点实测，
  替代不可行的「盲试命令名」

### 剩下的门槛
1. **渠道账号鉴权**：`pfId` / `platformToken` / `gameUid` 来自海尔渠道登录
   （`nearme:g1385224335121502465` 这类 token）。**目前用的是从 App 抓包复原的现成 token**；
   要长期脱离 App，需要解决渠道 token 的获取与续期——这是**账号体系问题，不是协议问题**。
   （协议层的 `signCode`/`buildCode`/`SecurityCode`/`cc` 已全部可本地计算。）
2. **设备标识**：`deviceId`（`1e933e9e19504d5`）与 `uuid`（`cok` + 32 hex）
   是首次安装时本地生成并持久化在 `UserDefault` 的，换设备需要复现生成规则
   （尚未逆，但直连端可以自己生成并保持稳定）。
3. **风控**：`newbasekey`、`_cok_` 序号、`cmdBaseTime` 说明服务端在做重放/时序校验；
   模拟客户端行为异常（频率、来源 IP、设备指纹）可能被判定为外挂。
4. **写操作语义**：领奖/做任务类命令的参数与前置条件要逐个验证，
   服务端会校验活动状态、次数、CD。
   （`queue.ccd` 已逐字段验证通过；`queue.one.key` / `queue.tool` /
   `civilizationQueue.*` 已知存在但参数未反出，**缺参数时只返回 `E000000`，不猜**。）
5. **服务器地址会变**：IP/端口随区服与负载轮换，直连前需确认当前节点（见 §6.4 备注）。

### 建议路径
1. 继续用**只读**接口扩展能力（`monthlySign.info` 签到、`overview_new.data` 概览、
   `allianceNewBoss.bossMainInfo` 联盟 boss、排行类）—— 已验证可脚本化。
2. 写操作（领奖、领取奖励）先在自有小号上验证，并注意次数/CD/活动状态校验。
3. 渠道 token：先确认能否用现有登录态直接取到 `pfId`/`platformToken`；
   若不行，再看海尔渠道 SDK 的 token 换换取游戏服 `gameUid` 的那一步。

### 风险提示
这是第三方商业游戏的线上协议；**只读查询**与**自动化操作**是两件事，
后者可能违反用户协议并触发封号。

---

## 9. 工具与证据清单

```
protocol/
├── cok_sfs.py                  # 协议库：SFS 编解码 + XOR 加解密 + 请求组包 + 响应解码
│                                #   + 密钥派生(derive) + 登录字段派生(login-fields / sign-code)
├── decode_capture.py           # 把 frida 抓的 JSONL 还原成 SFS 帧并解出 params 明文
├── cok_client.py               # 直连客户端：bin 握手 → 登录 → 派生密钥 → 发只读命令
├── evidence-sample.txt         # 同会话双向解码证据（命令 + 参数 + 统计）
├── command-catalog-typed.json # 带 SFS 类型的参数目录（844 条，含 queue.ccd 实测配方）
├── cok_speedup.py             # 加速工具：列队列(init 推送) + 用道具/金币加速
├── speedup-owned.json         # 背包加速道具实例快照(itemId → uuid/count/type2/时长)
├── command-names-native.json  # 1246 条命令名候选（device 版 libgame.so 字符串表提取，未逐条实测）
├── frida/                      # 13 个 hook 脚本 + 驱动
└── evidence/
    ├── capture-session-e2e.slim.jsonl   # 同会话：游戏服原始字节 + 密钥流成对数据
    ├── capture-enc-pairs.jsonl          # 单独会话的明/密文对
    ├── capture-wire-early.jsonl         # 早期 wire 抓包
    ├── capture-keyderive.jsonl          # 密钥派生取证：登录明文握手 + XOR 密钥 + keymap
    └── capture-loginfields.jsonl        # 登录字段取证：运行时 MD5 输入(432 条) + 登录请求字段
```

> 密钥派生自检脚本在工作目录 `~/workspace/me/cok/frida/`：
> `verify_key.py`（用登录响应的 `id` 派生密钥并端到端解码整场会话）、
> `decode_wire.py`（把线路抓包重组为 SFS 帧）、`keyproof.js`（frida 取证探针）。
>
> **静态定位命令名的新工具**（同目录，用于替代「盲试命令名」）：
> - `elf_xref.py` —— 在 ELF64 arm64 二进制里做 `ADRP+ADD` 字符串引用扫描（纯位运算，不依赖反汇编器）。
>   用法：`python3 elf_xref.py <libgame.so> <str1> [str2 ...]`，输出每个字符串的代码引用地址与引用簇。
> - `disasm_strings.py` —— 反汇编一段地址区间，列出其中引用到的所有字符串（capstone）。
>   用法：`python3 disasm_strings.py <libgame.so> <start_addr>`。
> - `probe_queue_ccd.py` / `test_queue_ccd2.py` —— `queue.ccd` 参数组合穷举脚本。
>
> 组合起来就是 §6.13.2 的定位链路：**Lua 入口 → native 字符串表 → ARM64 xref → 反汇编取字段名 → 定点实测**。

复现要点：
- frida-server 17.13.0 arm64 → `/data/local/tmp/frida-server`，`su -c` 以 root 启动
- 设备在 `untrusted_app` 域，**只能 attach frida 自己 spawn 出来的进程**（普通进程 attach 报
  `ptrace pokedata: I/O error`）
- Frida 17.13 的 **ART bridge（`Java` 全局）在 attach 和 spawn 两种模式下都不存在**
  （`typeof Java === 'undefined'`），所以不能 hook Java 方法，只能走 native 层
- 抓游戏 TCP 流量：hook libc 的 `write`/`read`（JVM NIO 走 libc；`connect` 在 libsocket.so
  且 JVM 走 syscall，hook 不到），靠「首字节 0x80 + 长度自洽」筛出 SFS 帧
- hook native 偏移必须减 image base `0x100000`（Ghidra `0x00ae02b8` → 运行时 `base+0x9e02b8`）
- **设备版 libgame.so 与 CN1 分析版不是同一构建**：静态函数偏移会变
  （例：MD5 相关函数在设备版不在分析版的偏移上），只有导出符号地址一致；
  做运行时验证必须以**设备版**为准

---

## 10. 未决与风险

| 项 | 状态 |
|---|---|
| 会话密钥的下发接口 | **已定位并验证**：登录响应（明文）`params.id = "<前缀>_<密钥ID>"`；密钥 = `md5_hex(前缀)`；`qqq` = 密钥ID。端到端 71/71 解密成功 |
| `ver` 热更新包的密钥 | `md5_hex(完整 id 串)`，实测解出 Lua 源码 |
| 登录请求 `signCode` | **已逆出**：`md5(sprintf("%x", Arrays.hashCode(certDER)) + "." + 小写hex(certDER))`，由 APK 证书独立算出与线上同值 |
| 登录请求 `buildCode` | **数值已确认**（恒定 `c7d89544df01787870515c10fba1cd68`）；**写入源未定位**（渠道侧下发，存于 `UserDefault["buildcode"]`） |
| 登录请求 `SecurityCode` | **已逆出**：`md5(str(cmdBaseTime) + "e01684719c1bec876c10bb124a6d65aa" + game_uid)`，两会话交叉验证通过 |
| 登录请求 `cc` | **已逆出**：`md5("d6b63d01d640fb78c979912ec839a0de" + appVersion + str(cmdBaseTime) + game_uid)`，两会话交叉验证通过 |
| 渠道鉴权（`pfId` / `platformToken` / `gameUid`） | **未逆出**（海尔渠道登录换取，非协议层问题） |
| `deviceId` / `uuid` 生成规则 | 未逆出（首次安装本地生成并持久化；直连端可自行生成稳定值） |
| 响应混淆键名（20+ 字节二进制，如 `rlQW45Y`） | 已能解析，命名规则未明（与密钥无关，同一会话内固定） |
| BlowFish 路径 | 代码在、密钥槽为空；是否有其它 build 启用未验证 |
| 设备版与 CN1 分析版差异 | 两版 libgame.so 体积相同（61,888,728 B）、业务域名一致；**但设备版 Lua 构建号不同**（`release_12.06.0_25` vs 分析版 `_11`），协议实现同源但**静态函数偏移会变**（MD5 函数即如此），运行时验证须以设备版为准；**`queue.ccd` 的参数集也不同**（device 版多 `queueId`/`queueType`/`goldcost` 三个字段），字段名以 device 版为准 |

---

## 11. 与第一轮静态结论的差异（务必以本文为准）

| 静态结论（第一轮） | 运行时实证 |
|---|---|
| `libgame.so` 的 Sfs2X native SDK 在跑 | **死代码**，0 命中；真正实现是 `sfs2x.client.*` Java 版 |
| AES-128-CBC（`EVP_aes_128_cbc` + `CryptoKey::Key/IV`）在用 | **未启用**（开关 `+0x11f4 == 0`）；`Native.BlowFishDecrypt` 密钥槽为空 |
| 密钥握手下发，静态不可得 | 确实服务端下发，但**不是 AES**，是 32 字节 XOR 密钥；长度不变、无分组；且**可由登录响应明文字段 `id` 派生**（`md5_hex(前缀)`） |
| `ExtensionRequest::Init` 的 `+0x60` bool 是加密开关 | 那是 native C++ 侧的字段，运行时不涉及；真正的开关是 `cfgB+0x11f4` |
| 封包头是 32 位字 | 实测是 **3 字节**：`[flags:1][length:2 大端]`；第 4 字节 `0x12` 其实是 SFS_OBJECT 标签 |
| 命令名不可见（以为整包加密） | **命令名与字段名全程明文** |
| 载荷类型表 0x11/0x12/0x13 未处理 | `0x11`=SFS_ARRAY（count 为 **2 字节**）、`0x12`=SFS_OBJECT、`0x13`=CLASS |
| `speed.change.time.use.item` / `territory.levelup.speedup` 是 native 内部事件名 | **误判**。它们与 `queue.ccd` 等真实命令名混排在 device 版 libgame.so 的字符串表里；主城加速实测命令是 **`queue.ccd`**（见 §6.13） |
| 主城建造队列「加速」命令未定位 | **已定位并实测成功**：`queue.ccd`，7 字段参数集见 §6.13.1；建造 12.6h → 0 |
