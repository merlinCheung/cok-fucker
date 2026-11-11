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
                    pfId: "<pfId-example>",
                    signCode: "<signCode>",
                    buildCode: "<buildCode>",
                    deviceId: "<deviceId>", isSmall: "kao", ... } }
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

`game_uid` = 账号 gameUid（如 `<uid-main>`）；`appVersion` = 如 `12.06.0`；
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
本渠道实测恒为 `<buildCode>`。

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

`signCode` 三会话同为 `<signCode>`，且由 APK 证书
（`META-INF/ANDROID_.RSA` 里的 X.509 DER，`Arrays.hashCode = 0x54168fb4`）独立算出同值 ✓

**运行时实证**（hook 设备版 native `MD5_Update`，抓到真实输入缓冲）：

```
1792658351e01684719c1bec876c10bb124a6d65aa<uid-main>
    → SecurityCode = md5(...) = 014707b6687e72c32caeb40200833222   与线上完全一致
d6b63d01d640fb78c979912ec839a0de12.06.01792658351<uid-main>
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
[+] 已从设备读取账号: {"pfId":"<pfId-example>","gameUid":"<uid-main>",
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

### 6.14 背包与体力药水（2026-11-10 真机实测）

#### 6.14.1 `login.init` = 直连拉全背包（只读）

**这一条推翻了 2026-10-25 的旧结论**「直连拉全背包的命令名仍未定位」。
旧结论的成因是：当时把 `rlQW45Y` 解开后**递归扫了整棵树**，
带 `uuid` 的 dict 只有 101 个、且全是 `building[]`（建筑实例），
于是判成「init push 里没有背包」—— **那次扫法漏掉了 `items` 这一层的匹配形态**
（`items` 的元素里 `uuid` 和 `itemId` 是**平级**的，按「uuid 所在 dict 里有没有 itemId」
去匹配是能匹配上的，问题在于当时的扫描器只认嵌套在 `itemObj` 里的 uuid）。

**实测**（2026-11-10，4 个账号）：

```
login.init  ->  {"qqq": <keyId>, "rlQW45Y": "<30 万 hex>"}
rlQW45Y     ->  XOR(会话密钥) -> zlib -> SFS 对象(133 个顶层键 / 95 万字节)
其中 items = [{"itemId":"200381","count":40,"uuid":"94e0...","para1":"107","para2":"50"}, ...]
```

* **`items` 就是玩家背包**：每条带 `itemId` / `count` / `uuid`(道具实例 id) /
  `para2`(体力值) / `useDate` / `vanishTime`
* 道具是**堆叠**的（一个实例 `count=N`），实例 uuid 在 count 用完前**稳定**
  ⇒ **拉一次缓存起来能长期用**，不需要反复拉
* 实测背包规模：`<uid-guopan>` → 770 件；`<uid-main>` → 515 件；
  `<uid-guopan-intl>` → 685 件

**⚠️ 坑 1：这个响应是「裸 zlib 流」** —— 服务端**不发帧长度**，
帧头 3 字节直接就是 zlib 流的开头（`78 9c …`）。
按长度字段读会读出 39936 而实际约 13 万字节，**后面所有帧全部错位**。
⇒ `cok_client._recv_frame` 新增 `_is_zlib_head` / `_read_zlib_stream`，
必须解到 zlib 流自然结束才算一帧。

**⚠️ 坑 2：服务端会发 5 字节心跳帧**（`a8 00 02` + 2 字节载荷）。
按压缩帧解会抛 `zlib.error` —— 现在按心跳跳过。

**⚠️ 坑 3：服务端丢弃新连接的首条业务请求** —— `login.init` 第一次常常超时，
**重发一次**才有响应（`retries=1`）。

**耗时 40~50 秒**（响应 95 万字节）⇒ 只在真需要时拉一次，然后缓存到
`accounts/<uid>.items.json`。

#### 6.14.2 `item.use` = 用掉一个道具实例

```jsonc
{ "uuid": "<道具实例 uuid, 32 位 hex>", "num": <SFS INT> }
```

```python
from cok_sfs import TypedInt, SFS_INT
client.call("item.use", {"uuid": uuid, "num": TypedInt(1, SFS_INT)}, retries=1)
```

**实测响应**（真服，喝 1 瓶 200380）：

```json
{"itemId": "200380", "itemEffectObj": {"stamina": 300}, "count": 1}
```

体力 **290 → 300（+10）** —— 真的生效。

**三个必死的点**：

- `uuid` 是**道具实例 id**，不是模板 id —— 传 `"200381"` → `E000000`
- `num` **必须编码成 SFS INT**（`TypedInt(n, SFS_INT)`），传普通 int → `E000000`
- uuid 不存在 → `E100166`（没有该道具）；数量不够 → `E100165`（道具数量不足）

#### 6.14.3 体力药水（自动打怪喝药用）

| 道具 id | 恢复体力 | 来源 |
|---|---|---|
| `200380` | +10 | 客户端道具表 `para` 字段 |
| `200381` | +50 | 同上 |
| `200382` | +100 | 同上 |

客户端配置 `data_config.auto_kill_monster.k1 = "200380;200381"`。

**已排除的路线（别再试）**：

| 路线 | 结论 |
|---|---|
| 服务端代喝药 `autoQueue.status {status:1}` | ❌ 需「自动打怪周卡」（客户端 k2=766437），4 个账号全部 `E000000` |
| `autoQueue.status {status:0}` | ✅ 能读回 stamina，但只是关着，不代喝 |
| `autoQueue.data` | ✅ 可读（saveItems/useItems/status/lv/autoCount/force/format） |
| 商城买 `mall.info` / `mall.data` | ❌ 这 4 个号（497 条商品 / `mallId:"15"` 206 件）**不卖** 200380/200381/200382；换 mallId → `E000004` |
| `item.buy {id, num}` | 参数名是 **`id`**（传 `itemId` 报 `E000000`），能返回 uuid，但买体力药水 → `E000000` |

**错误码速查**：`E100047`=体力不足 / `E100165`=道具数量不足 /
`E100166`=没有该道具 / `E000000`=参数错误 / `E000004`=对象不存在。

**落地**：控制台「自动打怪」新增开关「体力不足自动喝体力药水」（PC + 安卓都有）。
没缓存到实例时自动拉一次背包（40~50 秒）→ 喝 → 计数减一 → 用完丢掉 uuid。
喝药失败**不计入打怪 fails**。

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
   （`<pfId-example>` 这类 token）。**目前用的是从 App 抓包复原的现成 token**；
   要长期脱离 App，需要解决渠道 token 的获取与续期——这是**账号体系问题，不是协议问题**。
   （协议层的 `signCode`/`buildCode`/`SecurityCode`/`cc` 已全部可本地计算。）
2. **设备标识**：`deviceId`（`<deviceId>`）与 `uuid`（`cok` + 32 hex）
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

## 8.1 多账号登录：怎么登录"其他账号"（2026-10-28 实证）

### 8.1.1 一句话结论

**登录另一个号 = 拿到另一套凭据。协议侧没有障碍，唯一的卡点是"新号的凭据从哪来"。**

登录请求里真正跟"账号"绑定的字段只有 4 个：

| 字段 | 含义 | 作用域 |
|---|---|---|
| `pfId` | `<渠道>:<平台token>`（nearme:`g1385224335121502465`） | **每账号** |
| `platformToken` | 同上的 token 部分 | **每账号** |
| `gameUid` | 游戏角色 id | **每账号** |
| `uuid` | `cok` + 32hex | **每账号** |

其余（`signCode`/`buildCode`/`packageName`/`pf`/`channelSign`/`deviceId`/`host`/`port`/`zn`/
`device_info`…）都是**每设备/每包/每区服**的公共字段，账号库里用模板补齐即可。

### 8.1.2 凭据是长期有效的 bearer token（已实证）

`<pfId-example>` 是 **2026-10-22** 抓的，**2026-10-28 仍然能登录**（当天实测
`bin 握手 → 登录 → id 派生密钥` 全通）。→ 平台 token 实质是**长期用户标识**，不是会话 token，
**抓一次就能长期用**；账号入库后**完全不依赖手机**。

### 8.1.3 游戏自带的"设备绑定 / 切换账号"—— 本服暂不可用（已证伪）

客户端里有一整套官方多账号机制（lua `game/deviceAccount/`）：

| 命令 | 参数 | 作用 |
|---|---|---|
| `device.bind.info` | — | 列出**绑定到本设备**的所有账号（gameUid / buildcode / ip / port / zone / uuid / greenServer） |
| `device.bind.export` | `opUid` | 导出某账号 → 返回 `{code, expireTime}` **授权码**（可把号搬到别的设备） |
| `device.bind.import` | `code` | 用授权码把账号导入本设备 |
| `device.bind.hide` | `opUid` | 隐藏某账号 |

文案也证实了这是官方多号入口：*"开始新游戏之后，您可通过**切换账号功能**找回当前账号"*
（`E100180`）；v2 界面的账号切换走 native `changeDeviceUser`，列表项含
`gameUid/gameUserName/gameUserLevel/greenServer`。

**实测（2026-10-28，正式服 COK2223）**：
* `device.bind.info` 服务端**认识这个命令**，但回 `errorCode=E000000`；
* 试了 19 组参数（`type` / `serverType` / `greenServer` / `old` / `gmFlag` / `serverId` / `zn` /
  `gameUid` / `uid` / `opUid` 及其组合，INT 与 STRING 两种写法）**全部 E000000**；
* 登录响应已整份 dump 过：只有资源版本 + `id` + `ver`，**没有任何角色/账号列表**。

对照实验（重要）：**未知命令会被服务端直接断连**（`zzz.no.such.cmd` 实测 = 连接被关闭，
不是 E000000）。所以 `E000000` 意味着"**命令存在、请求被拒**"，而不是"命令不存在"。
→ 结论：**当前 build / 正式服上这条路走不通**；若要定论，必须在手机上抓一次真实
`device.bind.info` 请求（native 侧 `requestDeviceAccount` 发的，参数名在加密的
libgame.so 字符串里，静态反不出来）。

### 8.1.4 两条会伪装成"协议失败"的坑（本次踩到）

1. **同账号只允许一个连接**：第一次探针连主号立刻被断连，一度以为是协议问题；
   真相是**网页控制台正在用主号**（`.cok-account-<uid>.lock` 的 mtime 暴露了它在占用哪个号）。
   → 探针/抓包**必须换一个控制台没在用的号**，或者先停掉控制台。
2. **每条连接的首条业务请求会被丢弃**（丢 = 超时，不是断连），`call()` 自带重试能兜住。
   两次 `cmd.ping` **挡不住**（实测 ping 之后第一条业务命令照样被丢）。

### 8.1.5 候选方案（按性价比排序）

| # | 方案 | 做法 | 成本 | 备注 |
|---|---|---|---|---|
| **A** | **抓包收割（推荐）** | 手机 `tcpdump -i any "tcp port 32231"` → **登录帧是明文** → 直接抽出 `pfId/platformToken/gameUid/uuid` → 自动入库 | 一次性写脚本 | 跨渠道/跨包通用；用户在手机上切号登录一次就收一个号 |
| B | frida 收割 | hook native 登录参数构造（`FUN_00c2ee8c`）或 `nativeSetPlatformUID` | 要 frida 环境 | 比 A 干净，但更折腾 |
| C | `device.bind.*` | 一次列出本机所有绑定号 | 先要手机抓真实请求 | 当前服 E000000，待验证 |
| D | 渠道 SDK 直连 | 逆 nearme/ewanqf 登录协议，自己换 token | 高 | 最彻底，可彻底脱离手机 |
| E | 手填 | 网页加表单手填 4 个字段 | 最低 | 值还是得从手机拿，只是搬运 |

**推荐 A**（手机当"发卡机"，PC 当"大脑"）：手机只负责登录/切号，
PC 侧自动收割凭据并写进 `protocol/accounts/<gameUid>.json`。
工具底座已有：`/tmp/cokccbi/pcap_sfs.py`（pcap → TCP 流重组 → SFS 帧）+
`cok_sfs.parse_best`（明文登录帧直接可解）。

### 8.1.6 「没有手机」怎么拿到新号的凭据（2026-10-28 追加）

**前提**：手机只在**产生凭据的那一刻**需要；凭据一旦入库就与设备无关（见 8.1.2）。
所以问题不是"要不要手机"，而是"**谁去跑那一次渠道登录**"。三条路：

#### 路径 1（对朋友最友好）：游戏自带的「账号绑定 / 导出 / 切换账号」

客户端 `game/deviceAccount/` 的语义已确认：**绑定 = 把游戏角色绑到 elex 账号（手机号）**，
不是"设备上的多个角色"。文案：*"为了您的账户安全，您需要将当前账号绑定后才能开始新游戏。
开始新游戏之后，您可通过**切换账号功能**找回当前账号"*（`E100180`）。

所以官方设计的跨设备流程是：

```
朋友手机: 设备账号 → 导出账号  →  得到 {code, expireTime} 授权码  →  发给我们
我们 PC  : device.bind.import {code}  →  拿到账号(gameUid/uuid/ip/port/zone)
```

**优点：对方零门槛**（不用 root、不用 USB、不用我们碰他的手机），**我们这边零依赖**
（直接调游戏服命令）。
**未解**：`device.bind.*` 直连被 `E000000` 拒（19 组参数全试过），
真实参数在 native `requestDeviceAccount` 里（libgame.so 加密串）→ **必须抓一次真机请求**。
注意 `device.bind.export` 是**写操作**（会生成授权码），跑之前要用户点头。

#### 路径 2（完全不需要手机）：PC 端复刻 elex 账号服务 —— **已复刻成功（2026-10-28）**

**1) elex 账号服务的接口（APK `com.elex.account.client` 全明文）**

base（CN）：`https://accountapi3.elexapp.com` / `https://accountapi1.elexapp.com`
（debug 环境：`http://169.53.247.133:81`）

**URL = base + 路径 + appId（appId 是路径的一段，不是 query！）** —— 这是最关键的坑：
```
https://accountapi1.elexapp.com/services/v1/user/login/10001001
https://accountapi1.elexapp.com/services/v1/user/token/10001001
https://accountapi1.elexapp.com/services/v1/user/register/10001001
https://accountapi1.elexapp.com/services/v1/user/editpass/10001001
https://accountapi1.elexapp.com/services/v1/verifycode/getcode/10001001
https://accountapi1.elexapp.com/services/v1/user/addantiaddiction/10001001
```
少了末尾的 `/10001001` 就是 `500 Internal server error`（被 WAF 挡着，看着像服务挂了）；
带上就是正常 JSON。方法：`POST` + `Content-Type: application/json`。

**2) 请求体**

```
登录: {"email": "<账号>", "passmd5": "<md5(md5(pwd)+'p392SYseXuu9wot9').lower()>"}
公共参数(JsonHelper.fillCommonParams): ip / lang / country / time(ms) / sig
```
**3) 签名（SignUtil.createAccountSign）**
```
每个字段拼成 "k=v&"（嵌套 JSONObject 递归）→ 大小写不敏感排序 → 拼接
sig = md5( 拼接结果 + "key=zOXjcEOc48UAj7fY" ).lower()     # sig 自身不参与签名
```

**4) 实测（假账号）**
```
POST .../services/v1/user/login/10001001
{"email":"nobody@example.com","passmd5":"<md5(md5('wrongpass')+'p392SYseXuu9wot9')>",...}
→ {"code":105201,"message":"no account or pass error","body":null}
```
**手机号登录**(PhoneLoginActivity.requestLogin 原始字段，实测 accountType=1 才通：
0→500、2/3→param error)：
```
{"accountType":1, "mobile":"<手机号>", "countryCode":"86", "passmd5":"<同上>", ...公共参数}
```
→ **参数形状 + 签名全部正确**（已经走到账号校验这一步）。
`tools`: `protocol/cok_elex_account.py`（login / phone-login / getcode / token / raw）、
`protocol/cok_elex_game_login.py`（拿到 token → 直接试登游戏服）。

**5) 最关键的桥：elex 账号就是一条合法的游戏登录通道**

`com.clash.of.kings.COK_CN1.onCreate` →
```java
ElexAccount.getsInstance().initlizePhone(ctx, "10001001", callback);   // 手机号登录已开
```
`COK_CN1$1.onLoginSuccess(userId)` →
```java
Native.nativeSetPlatformUID("elextech:" + userId);      // ← 平台身份 = elextech:<elex uid>
```
→ **elex 手机号登录成功后，游戏把平台身份设成 `elextech:<uid>`**，
于是游戏服登录参数就是 `pfId = "elextech:<elex uid>"`、`platformToken = <elex token>`。
**这意味着：手机号+密码 → elex token → 直接在 PC 上登录游戏服，全程不需要手机、不需要渠道 SDK。**

**6) 官方通道包的常量（我们分析的这个 APK 就是它）**

| 项 | 值 | 来源 |
|---|---|---|
| 包名 | `com.hcg.cok.cn1` | apktool/AndroidManifest.xml |
| 渠道 | `cn1` | `PublishImpl.getPublishChannel()` 返回 "cn1" |
| signCode | `df0b8b7ab5a75e84f8f7cfccd0a5d165` | 由本包 CERT.RSA 派生(`sign_code_from_cert`) |
| pf | 推测 `cn_cn1` | 规律: nearme→`cn_nearme`、ewanqf→`cn_ewanqf` = "cn_"+渠道 |
| appId | `10001001` | `initlizePhone(ctx, "10001001", ...)` |

**未解**（需要一次真实 elex 账号做实验）：
1. elextech 通道的 `pf` 取值（`cn_cn1` / `cn1` / `elextech` 三个候选，脚本会挨个试）；
2. `gameUid` 怎么给（服务端按 elex uid 绑定角色？还是首次登录自动建号 → **PC 端直接开新号**）；
3. 已存在的渠道号（nearme/ewanqf）**能不能**改用 elex 身份登（要先在游戏里「账号绑定」）。

**7) 实测（真实账号，2026-10-28 下午）**

用手机号 `18153242005` 走完了整条 elex 链路：

| 步骤 | 结果 |
|---|---|
| `phone-login`（密码登录） | `105201 no account or pass error` → **该手机号在 elex 原本没有账号** |
| `getcode`（发短信验证码） | `{"code":0,"message":"success"}`（⚠️ 对任意号码都 success，不能用来判断账号是否存在） |
| `register`（验证码+密码） | `{"code":0,"message":"success","body":{"uid":"304352946010873"}}` → **账号创建成功** |
| `phone-login`（再登） | `{"code":0,"body":{"uid":"304352946010873","t":"1793165300204","token":"bfd6f405…"}}` → **拿到 token** |

→ **elex 账号体系在 PC 上完全跑通**：注册 / 登录 / 换 token 三个接口都实测可用。

**8) elex 身份登游戏服：到了服务端，但差"角色"**

用 `pfId=elextech:<elex uid>` + `platformToken=<elex token>` 打游戏服（12 组参数组合都试过）：

| 条件 | 服务端返回 | 含义 |
|---|---|---|
| `gameUid=""` | `{"ep":["E100111",ts],"ec":28}` | **E100111 = 无法获取服务器信息**（`text_zh_CN.ini` 查表）→ 服务端找不到这个身份对应的角色/区服 |
| `gameUid="0"` / 随机 15 位 | `{"ep":["E002",ts],"ec":28}` | E002 = 登录服自己的错误码（token/角色不匹配） |
| `pf=elextech` + `gameUid=<elex uid>` | `{"ep":["E001"],"ec":28}` | 又一个不同的码 → **pf=elextech 确实被区别对待**（其余组合都只回 E002） |

→ **游戏服认识 elextech 这个通道**（不然会像未知命令那样直接断连），差的是**该身份在区服上还没有角色**。

**9) 建号入口在 HTTP gameservice，且需要 native 里的 sig**

新身份要先拿到"区服 + gameUid"，走的是 HTTP（`libgame.so` 明文 URL）：
```
https://%s/gameservice/getserverlist.php?uuid=%s&loginFlag=%d
https://p3cok.elexapp.com/gameservice/getpfbydeviceid.php?deviceId=
```
实测：这些 PHP 接口都会校验 `sig`（`sig error` / `sig fail`）。
→ **sig 的 key 在 libgame.so 的加密字符串里**（该库除了 URL 之外全加密，静态 grep 不到），
用 elex 账号服务那两把 key（`zOXjcEOc48UAj7fY` / `…swWXswowW`）各种拼法都试过，全部 `sig error`。
→ 要继续只能：(a) frida 在真机 runtime dump 解密后的字符串；(b) 静态解 libgame.so 的字符串加密（Ghidra 工程已在）。

> ### ✅ 订正（2026-10-29 21:4x）：**sig 已破解，`getserverlist` 已可用**
>
> 上面的判断（"key 在加密串里、静态 grep 不到、只能 frida"）**不成立**。真正的破法是**游戏自己把带签名的 URL 打进 logcat**：
> ```
> adb logcat -d | grep -oE "https://[^ ]+gameservice/[^ ]+"
> ```
> 于是直接拿到 **明文参数 + sig** 的成对样本（4 组），直接爆破即得：
>
> ```
> sig = md5( uuid + str(t) + "@z4LugUwrDN0MqOJtzmHPK7Ss-k4taAUOZh1M3Yu9" )
> ```
> 密钥常量在 `lib/arm64-v8a/libgame.so` 里**明文可见**（`strings` 能捞到）——
> 之前"grep 不到"是因为搜的是**加密后的字符串池**，而这个常量是裸常量。
> 4/4 真机样本逐字节一致（详见 `RE-渠道登录逆向方案.md` §8.13）。
>
> `getserverlist.php?uuid=<设备16hex>&pfId=<渠道身份>&loginFlag=1&sig=...` 响应里**直接含**：
> ```
> gameUid / 账号uuid / zone / ip / port / buildCode / gameUserName / gameUserLevel
> ```
>
> ### 🔓 由此推翻「uuid 强绑定设备」这一结论（§8.9 的实验 Y 需要重读）
>
> | 实验 | 结果 |
> |---|---|
> | 同一个 pfId + **全新随机设备 uuid** | 仍返回**同一个角色**（原 gameUid / 账号 uuid / 昵称） |
> | 合法 pfId + **全新 deviceId** 走 SFS 登录 | **✅ 登录成功** |
>
> ⇒ **uuid 绑定的是"账号"而不是"设备"；服务端会按 pfId 主动把正确 uuid 下发给你。**
> ⇒ **拿到 pfId = 拿到该账号的全部游戏服凭据**，不需要手机 / root / 模拟器 / 官方转移通道。
> （实验 Y「换全新 uuid → E002」仍然成立：那是因为 uuid 是**错的**；正确 uuid 来自服务端，不是来自设备。）

**10) 因此当前可落地的路径：装官方包 + 登一次 + 网页「＋」**

仓库里就有官方包：`5396(12.06.0)-COK_CN1--20260923-1727-10.apk`（= `com.hcg.cok.cn1`）。
装上 → 用刚注册的 elex 账号登录一次 → 网页点「＋」自动入库（`cok_account.list_packages()`
按 `com.hcg.cok.*` 扫全部包，**新渠道零代码**）→ 之后 PC 端独立使用，不再需要手机/root/USB。
顺带还能测出"官方通道的 account_zone / account_ip / account_port 是不是和渠道包一样"。

### 8.1.7 渠道「账号 / 密码」方式（2026-10-29 真机取证）

手机连上后，对 **oppo(nearme)** 和 **果盘(ewanqf)** 两个在装的渠道做了取证。

#### 果盘（`com.hcg.cok.ewanqf.guopan`）—— 账号密码制，可复刻但要逆加密

* SDK 是**插件式**的：`guopan/sdk/plugin/gp_sdk_plugin_5_5_4_3.apk`（10.7MB，6 个 dex +
  `libEncryptorP.so` / `libgism.so`），主包 `com.flamingo.sdk.dex1`（重度混淆）。
* 账号方式：**手机号/账号 + 密码**（另有短信验证码 `XXSMSCodeReqType_LOGIN`、微信登录、游客）。
* 登录流程：
  1. **先取 salt**（错误码 `ELogin_RequestSaltOK`）→ 2. `signMD5`(密码, salt) → 3. 登录 → 4. 拿 `loginKey`
  （存于 `SP_KEY_APP_LOGIN_KEY`）。
* **账号身份三元组**（`SuperSDK.xml` 里 base64 JSON，已解出）：
  ```json
  {"OpenId":"1084D65F5A7FCB599158","ChannelOpenId":"C654F5A7FCB599158","Token":"abf6839f913043b8813f863bdee6976c51084"}
  ```
* 换成**游戏专属 uid**：协议命令 `SUBCMD_ACCOUNT_LOGINBETWEENAPPREQ`（OpenId+Token+`appid=140514`）
  → 游戏侧就是 `pfId = ewanqf:<uid>`（本机实测 `ewanqf:1084D654F5A7FB599158`）。
* 传输：基址 `http://userapi.guopan.cn/gamesdk/`，**二进制 subcmd 协议**
  （`SUBCMD_ACCOUNT_*REQ/RES`）+ `libEncryptorP.so` 加密。
  → **PC 端复刻需要先逆那个 75KB 的 .so**（中等偏大的工程）。

#### oppo / nearme（`com.hcg.cok.nearme.gamecenter`）—— 账号密码制，但基本不可复刻

* SDK（gcsdk / heytap）**内置在游戏包里**（不是插件），账号体系在 **OPPO 自己的 App**
  `com.nearme.gamecenter` 里（`AuthLocal.xml` 只有 65 字节 ≈ 空 map，真正的会话在 OPPO 那边）。
* **角色身份明文**（`com.nearme.gamecenter.open.xml` → `gcsdk_tag_local_role_info`）：
  ```json
  {"gameSysID":"com.hcg.cok.nearme.gamecenter","ssoid":"1385224335",
   "gcuid":"com.hcg.cok.nearme.gamecenter","roleid":"g1385224335121502465",
   "roleName":"GU521946202610161131912","roleShareStatus":"0"}
  ```
  `roleid = g1385224335121502465` 就是**平台 token**（游戏侧 `pfId=nearme:<roleid>`）。
* → 账号密码校验在 OPPO 服务端 + gcsdk 原生（还要过设备指纹/短信风控），**PC 端复刻不可行**。

#### 果盘账号协议：**真机抓包实测**（2026-10-29）

设备侧 tcpdump（root）抓到了 SDK 的真实请求，协议形态确认：

```
POST http://userapi.guopan.cn/gamesdk/140514 HTTP/1.1
Content-Type: application/x-www-form-urlencoded
Content-Length: 953
<body = MIME 换行(76 列)的标准 base64 → 解出 704 字节密文>
```
同族端点（同一批抓到）：`/gamesdk/init/140514`、`/gamesdk/recommend/140514`、
`/xxdatareport.php?appid=140514`、`/time.php`。
**路径 = base + appid**（不是 query 参数）。

* body = **标准 base64** → 解出来是**高熵密文**（704 字节，16 字节分块**无重复** → 不是 ECB）。
* 加密在 `libEncryptorP.so`（75KB，**stripped**，只导出 `JNI_OnLoad`，内部动态注册 native
  方法 `ttEncrypt`）。
* 载荷格式 = **GPXX Proto**（`com.GPXX.Proto.*`，**2357 个类且名字全混淆**；proto 描述符里
  的**字段名是明文**：`account / userName / password / salt / appId / appKey / sign /
  timestamp / imei / oaid / vaid / aaid / fdid / openId / token / cmd / subcmd` …）。
* 签名盐：`#%$*)&*M<><vance`（`com.flamingo.sdk.u7.b` / `dex3.request.a` 里出现）。

→ **要在 PC 端完全复刻果盘登录 = 逆 `libEncryptorP.so` + 摸清 GPXX 消息 schema**，
属于多天工程；而**捷径**（让安卓环境替我们跑那一次密码登录）零逆向成本，见下。

#### `pf` 服务端**确实校验**（2026-10-29 实测）

鸭皇号（`nearme:g1372797742670953701`）：

| pf | 结果 |
|---|---|
| `cn_nearme` | ✅ 登录成功 |
| `nearme` / `cn_ewanqf` / 乱填 | ❌ `E002` |

→ `pf` 是**每账号**字段，"cn_<渠道段>"只是归纳，**不能当准**。
已实现 **`cok_accounts.probe_pf()`**：拿候选列表挨个**登录实测**，成功即确定并写库
（账号 JSON 里记 `pfVerified: true`）。`cok_accounts.py add --all` 默认会跑这个探测
（`--no-probe` 可关）。

#### 「上一个号」也能捞（已实现）

`cok_account.load_previous_account(pkg)`：读 `original_account_game_uid` /
`original_account_uuid` / `original_account_ip` / `original_account_zone`，
平台 token 从渠道 SDK 的角色信息取（nearme: `gcsdk_tag_local_role_info.roleid`）。
实测在 nearme 包上完整捞出主号：`<uid-main>` / `<pfId-example>` /
`<uuid>` / roleName `GU521946202610161131912`。
→ **凡是这台手机登过的号，凭据都能捞回来，不需要密码。**

1. **"账号"是两层**：*渠道账号*（手机号/OPPO 账号 + 密码）→ 换出 **平台 token**
   （nearme 的 `roleid` / 果盘的 `OpenId`+`Token`）→ 平台 token 才是**游戏身份**（`pfId`）。
   **游戏服只认平台 token；密码只是"换 token 的手段"。**
2. **手机会记住上一个号**：nearme 包的 `Cocos2dxPrefsFile.xml` 里还有
   `original_account_game_uid=<uid-main>`、`original_account_uuid=<uuid>`、
   `original_account_ip/zone`；配合 SDK 的 `roleid`，**凡是这台手机登过的号，凭据都能捞回来，
   不需要密码**（主号那条已经这样闭环验证过）。
   果盘包没有 `original_*`（只留了当前号）。
3. **果盘 SDK 的本地存储是加密的**（`SuperSDK.xml.core_data` 是一长串 hex，
   `NormalDatabase.db` 的 `normal_data_table` 0 行）→ **多账号列表在设备上读不出来**，
   只能拿到"当前登录号"的 token。

#### 顺带修正两处常量

* `channelSign = "bang"`（来自 prefs 键 `elex_doctor_boom`）**两个渠道都一样** → 不是渠道相关项。
* `buildCode` **随游戏版本变**（游戏已更新到 13.03.11）：nearme 现在是 `71a2ca5e…`，
  ewanqf 是 `f97c622e…`；账号库里"主号"那条还是旧的 `<buildCode>`，但服务端容忍（今天仍能登录）。

#### 路径 3：模拟器当发卡机（**2026-10-29 已跑通**）

不逆 `libEncryptorP.so` 也能拿到新号凭据：**让安卓环境替我们跑那一次密码登录**。
登录成功后**游戏**会把平台身份写进自己的 prefs，我们直接读走 → PC 长期独立使用。

环境（本机）：
* 模拟器：`~/Library/Android/sdk/emulator/emulator -avd medium_phone -no-window …`
  系统镜像在 `/opt/homebrew/share/android-commandlinetools/system-images/android-36/default/arm64-v8a/`
  （Android 16 / arm64-v8a），`adb root` 可用。
* 渠道包：真机 `pm path` → `adb pull`（果盘 487MB）→ 装到模拟器。
* **模拟器没有被拦**：两个渠道包的 `forbiddenDevice` 名单只含第三方模拟器
  （MEmu / Droid4X / iToolsVM / umEM / Liaoran / qemu），Google 模拟器不在名单；
  隐私 + 权限弹窗点掉后能正常进到 SDK 的**密码登录页**
  （`view_login_user_name` / `view_login_password` / `view_protocol_checkbox` / `view_login_btn_login`）。

自动化脚本 `protocol/cok_emu_login.py`：
```
起模拟器 → 装包 → 启动 → 过隐私/权限 → 打开「密码登录」页签
→ 填账号密码 → 勾协议 → 点登录 → 等游戏写 platformUid
→ 读 prefs 导出凭据 → probe_pf() 实测 pf → 写进账号库 → PC 验一次登录
```
实测（2026-10-29）：导出 → `pf 实测确定: cn_ewanqf` → 入库 → **PC 登录成功** ✅
导出字段：`platformUid / gameUid / uuid / deviceId / buildCode / signCode / host / zn`。

**重要限制（实测）**：果盘 SDK 的会话**不能跨设备拷贝** ——
把手机上的 `shared_prefs`/`databases` 整个拷到模拟器后，SDK **拒绝并退回登录页**
（token 绑设备指纹）。→ **发卡机必须做真实的密码登录**，搬会话不管用。

#### 游戏里还有一个「账号绑定 / 切换账号」通道 —— 本服也关掉了（2026-10-29 实测）

除了 `device.bind.*`，lua 里还有 **`user.bind`**（`game/command/UserBindcmd.lua`，
设置项「账号绑定」`PermitCommandView.JumpBanding=1006`）：

```lua
ret:initWithName("user.bind")
putParam: googlePlay / facebook / deviceId / mail / pass / optType
          googleAccountName / facebookAccountName / bindId / bindPf / accessToken / inputCode
```
**成功响应直接回一整套凭据**（客户端收到后写进 prefs 再 ResetGame 切号）：
```
gameUid, buildcode, ip, port, zone, uuid, serverId, gameUserName, gameUserLevel
```
→ 这本来是**最理想的"账号密码换角色"通道**（游戏服命令，不需要 root / 渠道 SDK / 模拟器）。

**实测（2026-10-29，用鸭皇号登录后直发）**：10 组参数组合
（mail=手机号/邮箱、pass=明文/md5、optType=0/1/2/3/4、带/不带 bindPf、bindId，
甚至**全空参数**）→ **全部 `E000000`**。
连"缺参数"都返回同一个码 → **服务端把整个命令关掉了**（与 `device.bind.info` 一致）。
旁证：客户端里 v1 界面（带导出按钮）的入口被注释掉、导出按钮的 handler body 也被注释。

→ **结论：当前 build / 渠道下，"官方跨设备转移 / 用账号密码换角色"这条路是关闭的。**
→ **剩下唯一可行的是「模拟器发卡机」**（已跑通，见上）。

#### 「免 root 能不能导出凭据」—— 实测（2026-10-29，模拟器 `adb unroot` 模拟普通手机）

| 手段 | 免 root | 实测结果 |
|---|---|---|
| 读 `/data/data/<包>/shared_prefs` | ❌ | `Permission denied` |
| `run-as <包>` | ❌ | `package not debuggable`（游戏是 release 包） |
| `adb backup` | ❌ | 清单 `allowBackup="false"`，且 Android 12+ 基本废止 |
| `uiautomator dump`（读界面文本） | ✅ | 可用，但**游戏界面里没有凭据字段** |
| `content query` 到 SDK 的 `LoginContentProvider` | ❌ | 插件框架直接拒：`UnsupportedOperationException: No external query` |
| **游戏内「设备账号 → 导出账号」** | ✅ | **官方通道**，零 root、零 USB |

→ **没 root 就读不到凭据文件**（Android 沙盒的本质，改不了）。
→ 但**正确形态不是"读朋友的手机"，而是"让游戏自己把凭据交出来"**。

#### 「发给朋友的软件包」应该长什么样

游戏**官方就有**跨设备转移功能（不是我们发明的）：
```
游戏设置 → 账号中心(guiCommonLocal.open_DeviceAccountView → DeviceAccount_v2_View,
                    **无 fun open 门槛**) → 导出账号 → 得到一串 code
```
协议就是 `device.bind.export`(v1 lua) / native `requestDeviceAccount`(v2)，
导入端是 `device.bind.import {code}` → 服务端把完整凭据(gameUid/uuid/…)交回来。

**分工**：
* 朋友：装渠道包 → 登录 → 设置里点"导出账号" → 把那串 code 发过来
  （**不需要 root / USB / 装我们的软件 / 我们碰他的手机**）；
* 我们：程序发 `device.bind.import {code}` → 凭据入库 → PC 长期独立使用。

→ **这条路同时解决"免 root"和"朋友自助"两个问题**，而且它本来就是游戏为"换设备"设计的。
**前置条件**：抓一次真机的 `device.bind.export` 真实请求（直连 `device.bind.info` 已被
`E000000` 拒，19 组参数全试过；参数名在 native 加密串里）。

**兜底（导出码走不通时）**：模拟器发卡机（已跑通，见上）—— 朋友把**渠道账号密码**给你，
你在云端模拟器上登录一次 → 采集凭据入库；朋友完全不用碰手机。
代价：你要经手对方的渠道密码（安全上不如"发一串码"）。

#### 结论：想用「账号密码」在 PC 上开新号的路

| 方案 | 说明 | 成本 |
|---|---|---|
| 手机采集（现状） | 切号 → 自动入库；**登过的号连密码都不需要** | 已有，零代码 |
| **模拟器发卡机** | 模拟器上密码登录 → 导出凭据；**不用占用任何人的真手机** | **已跑通** |
| 手机半自动 | 用 adb 模拟输入在手机上完成渠道登录，再自动采集 | 小 |
| **复刻果盘登录** | 逆 `libEncryptorP.so` + 二进制 subcmd 协议 → 纯 PC 端 账号+密码 直换 token | 中偏大 |
| 复刻 oppo 登录 | gcsdk 原生 + OPPO 风控 | 基本不可行 |
| elex 官方通道 | 协议已全通，差"建号"那一步的 gameservice sig（同上，native 加密） | 中偏大 |

#### 三条路共同的未解项

1. `device.bind.*` 的真实参数（需要一次真机抓包）；
2. nearme / ewanqf 渠道 SDK 的登录协议（native + 加密字符串，需 frida 或模拟器才能看）；
3. **服务端认不认"换设备"**：`deviceId` / `uuid` 是不是绑死？
   若绑死 → 朋友的号搬过来要连 `deviceId` 一起搬，可能触发换设备风控；若不绑 → 凭据完全可移植。
   （一次登录实验即可测，但要动真号，**跑之前要用户点头**。）

---

## 9. 工具与证据清单

```
protocol/
├── cok_sfs.py                  # 协议库：SFS 编解码 + XOR 加解密 + 请求组包 + 响应解码
│                                #   + 密钥派生(derive) + 登录字段派生(login-fields / sign-code)
├── decode_capture.py           # 把 frida 抓的 JSONL 还原成 SFS 帧并解出 params 明文
├── cok_client.py               # 直连客户端：bin 握手 → 登录 → 派生密钥 → 发只读命令
├── cok_elex_account.py         # elex 账号服务客户端(手机号/邮箱+密码直登, 签名已逆出)
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
| 登录请求 `buildCode` | **数值已确认**（恒定 `<buildCode>`）；**写入源未定位**（渠道侧下发，存于 `UserDefault["buildcode"]`） |
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
