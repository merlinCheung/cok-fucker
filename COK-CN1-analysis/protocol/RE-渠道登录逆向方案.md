# 渠道登录协议逆向方案（可执行性评估 + 分阶段实施）

> 状态：**方案已定，待执行**（2026-10-29）
> 目标：**纯 PC 端**用「渠道账号 + 密码」换出可直接登录游戏服的凭据，
> 从而不再需要手机 / root / 模拟器 / 别人的真机。
> 适用渠道：**果盘（ewanqf / flamingo SDK）优先**；**oppo / nearme 判定为不可行**（见 §6）。

---

## 0. 为什么做这件事（价值与边界）

| 需求 | 现状 | 本方案解决后 |
|---|---|---|
| 给 5-10 个人各自开号 / 交接账号 | 每个号必须有人拿手机登录一次 | 只要账号密码，云端随时开号 |
| 云端批量发卡 | 模拟器一��一个实例，慢且吃资源 | 纯 HTTP 调用，可并发、可脚本化 |
| 凭据可移植性 | token / signCode 绑不绑设备未知 | **实测已确认不校验**（见 §2） |

**不做也不影响主流程**：模拟器发卡机（`cok_emu_login.py`）已经跑通，是本方案的**兜底方案**。
本方案是"去掉安卓依赖"的那一步。

---

## 1. 目标与成功标准

### 1.1 目标产物
一个 Python 脚本（建议 `protocol/cok_channel_login.py`），输入渠道账号+密码，输出：

```python
{
  "pfId":       "ewanqf:<perGameId>",   # 游戏服真正认的平台身份
  "pf":         "cn_ewanqf",
  "gameUid":    "1125641597002221",
  "uuid":       "cok05009672d131fc1eb1f4a0becfd0ed77",
  # 以下可选, 服务端不校验(§2)
  "platformToken": "...", "signCode": "...", "deviceId": "...",
}
```

### 1.2 验收标准（必须全部满足）
1. **脚本在无 Android 设备、无 root 的纯 PC 环境**跑通：给定果盘账号密码 → 输出上面那组字段。
2. 输出��凭据能被 `protocol/cok_client.py` 直接登录游戏服：
   ```bash
   python3 - <<'EOF'
   import sys; sys.path.insert(0,'protocol')
   from cok_client import CokClient, load_account
   acc = load_account('<凭据.json>')
   c = CokClient(account=acc); c.connect(); c.bin_handshake(); c.login()
   EOF
   ```
   → 必须出现 `登录成功 id=<prefix>_<keyId>`。
3. **不依赖**任何 `.pcap`、模拟器、真机、frida（frida 只在开发期使用，见 §4 Phase 1/2）。
4. 至少用**两个不同的账号**验证（避免把"某个账号特例"当成协议）。

---

## 2. 关键事实（已实测，**别重复踩坑**）

### 2.1 服务端到底校验哪些字段（2026-10-29 实测，用鸭皇号做对照）
| 字段 | 服务端是否校验 | 证据 |
|---|---|---|
| `gameUid` | ✅ 校验 | 换成主号的 gameUid → `E002` |
| `uuid` | ✅ 校验 | 换成主号的 uuid → `E002` |
| `pfId` | ✅ 校验 | 换成主号的 pfId → `E002` |
| `pf` | ✅ 校验 | `cn_nearme` 能登；`nearme` / `cn_ewanqf` / 乱填 → `E002` |
| `platformToken` | ❌ **不校验** | 换成随机串 `deadbeef…` **照样登录成功** |
| `signCode` | ❌ **不校验** | 换成主号的 signCode **照样登录成功** |

> **推论**：游戏服真正认的只有 **(pfId, gameUid, uuid) 三元组 + pf**。
> `platformToken` 只是渠道统计用的装饰品 → **逆向时不必追求"完整正确"的 token**。

### 2.2 果盘渠道协议（真机抓包实证）
```
POST http://userapi.guopan.cn/gamesdk/140514 HTTP/1.1
Host: userapi.guopan.cn
Content-Type: application/x-www-form-urlencoded
Content-Length: <n>

<body = MIME 换行(76 列)的标准 base64 → 解出 <n> 字节密文>
```
* **路径 = base + appid**（`appid=140514` 是路径的一段，**不是 query**）。少了它 → `500 Internal server error`。
* 响应同样是 base64 密文（`Content-Type: text/plain`）。
* 同族端点（同一批抓到）：
  `http://userapi.guopan.cn/gamesdk/init/140514`、
  `http://open.guopan.cn/gamesdk/recommend/140514`、
  `http://open.guopan.cn/gamesdk/float/…`、`…/paycenter/…`、
  `http://dr.sdk.guopan.cn/xxdatareport.php?platform=android&appid=140514`、
  `http://sapi.guopan.cn/time.php`。
* appId = `140514`，appKey = `WVI2EOLJIW5YEE1Z`（来自设备 `GPUSER.xml`）。
* **签名盐**：`#%$*)&*M<><vance`（`com.flamingo.sdk.u7.b` / `dex3.request.a`）。
* **账号身份三元组**（设备 `SuperSDK.xml` 里的 base64 JSON，已解出）：
  ```json
  {"OpenId":"1084D65F5A7FCB599158","ChannelOpenId":"C654F5A7FCB599158","Token":"abf6839f913043b8813f863bdee6976c51084"}
  ```
* **登录流程**（`PasswordLoginTab`）：先取 **salt**（错误码 `ELogin_RequestSaltOK`）→
  `signMD5(密码, salt)` → 提交登录 → 拿 `loginKey`。
  协议命令名：`SUBCMD_ACCOUNT_*REQ/RES`（二进制 subcmd，不是 REST 路径）。
* **游戏的 pfId 与 SDK 的 OpenId 不同**（20 位 hex，差两位）：
  `ewanqf:1084D654F5A7FB599158` vs SDK `OpenId=1084D65F5A7FCB599158`
  → 游戏服**另外分配了一个 per-game id**（对应 `SUBCMD_ACCOUNT_LOGINBETWEENAPPREQ`）。
  **这是本方案必须攻克的一段映射**。

### 2.3 加密层
* 库：`libEncryptorP.so`（75,744 B，**stripped arm64**，只导出 `JNI_OnLoad`，
  内部动态注册 native 方法 **`ttEncrypt`**）。
* **已确认是 AES 实现**：文件内找到 **AES 逆 S-box @ 0xf650**、**AES rcon @ 0xcf6b**；
  正 S-box 未按连续 16 字节命中（可能运行时生成或另存）。
* 配套 `libgism.so`（风控）。
* 载荷格式 **GPXX Proto**（`com.GPXX.Proto.*`，**2357 个类且类名全混淆**，
  但 **proto 描述符里的字段名是明文**）：
  `account / userName / user_name / username / password / passwd / salt / loginType /
   appId / appKey / appid / appkey / sign / timestamp / timeStamp / imei / oaid / vaid /
   aaid / fdid / platform / sdkVersion / openId / token / uid / cmd / subcmd / phone / mobile`。
* SDK 整体是**重度混淆**（`com.flamingo.sdk.*` + `com.flamingo.sdk.m6.*` 等）。

### 2.4 官方跨设备通道：**本服已关闭**（别再试）
| 命令 | 状态 |
|---|---|
| `device.bind.info` | 19 组参数组合 → 全 `E000000` |
| `device.bind.export` / `import` / `hide` | 同上 |
| `user.bind`（设置里"账号绑定"，`PermitCommandView.JumpBanding=1006`） | 10 组参数组合 → 全 `E000000`（连全空参数也是同一个码）|

旁证：客户端里 v1 界面（带导出按钮）的入口被注释、导出按钮 handler 的 body 也被注释；
v2 界面（设置里能进的"账号中心"）**没有导出按钮**。
`user.bind` 本来是最理想的通道（成功响应直接回 `gameUid/buildcode/ip/port/zone/uuid/serverId`），
但服务端把整个命令关掉了。

### 2.5 免 root 不可能（已实测，模拟器 `adb unroot` 模拟普通手机）
| 手段 | 结果 |
|---|---|
| 读 `/data/data/<包>/shared_prefs` | `Permission denied` |
| `run-as <包>` | `package not debuggable`（release 包） |
| `adb backup` | 清单 `allowBackup="false"` + Android 12+ 废止 |
| `uiautomator dump` | 可用，但游戏界面无凭据字段 |
| `content query` → SDK `LoginContentProvider` | 插件框架拒：`UnsupportedOperationException: No external query` |

### 2.6 oppo / nearme：判定为**不可行**
* gcsdk / heytap SDK 内置于游戏包，账号体系在 **OPPO 自己的 App**（`com.nearme.gamecenter`）里。
* 角色信息明文（`com.nearme.gamecenter.open.xml` → `gcsdk_tag_local_role_info`）：
  ```json
  {"gameSysID":"com.hcg.cok.nearme.gamecenter","ssoid":"1385224335",
   "gcuid":"com.hcg.cok.nearme.gamecenter","roleid":"g1385224335121502465",
   "roleName":"GU521946202610161131912","roleShareStatus":"0"}
  ```
  → `roleid` 就是游戏侧的 `nearme:<roleid>` 平台身份。
* 密码校验在 OPPO 服务端 + gcsdk 原生（设备指纹/短信风控）→ **PC 端复刻不可行**。
* **不做**。若将来 oppo 有需求，只能走"安卓环境跑一次登录"（模拟器/红手指等）。

---

## 3. 素材清单（已归档到仓库）

```
protocol/evidence/chanlogin/
├── gp_sdk_plugin_5_5_4_3.apk      果盘 SDK 插件（10.7MB，6 个 dex + libEncryptorP.so + libgism.so）
├── libEncryptorP_arm64.so         加密库（75KB，stripped）
├── capture_phone_gcsdk.pcap        真机抓包（30KB，含一次完整 SDK 交互 + 一次 /gamesdk/140514 请求 704B / 响应 476B）
└── capture_emulator_login.pcap     模拟器抓包（4.6KB，含一次**登录尝试** 448B 请求 / 244B 响应，账号为测试假号)
```
md5：`gp_sdk_plugin` dcbbbf913bf567e7349deaec382c5ace / `libEncryptorP` e02eb152878c8f5f8d1a725321df17a0 /
`capture_phone` fe4c237ed6829a39f347ac53b90138d0 / `capture_emulator` fec56b53a4e0d6e6d57b9629731e0743

可复用工具：
| 工具 | 位置 | 用途 |
|---|---|---|
| dex 反汇编器（自研，含 xref 模式） | `COK-CN1-analysis/scripts/dexdis.py` | 列类/方法、反汇编、字符串交叉引用 |
| pcap → SFS/TCP 流解析 | `/tmp/cokccbi/pcap_sfs.py`（或自行实现，见 §4 Phase 0） | 从抓包提取 HTTP 请求/响应 |
| 游戏服直连客户端 | `protocol/cok_client.py` | 最终验收：拿凭据登录游戏服 |
| 模拟器发卡机（兜底方案，已跑通） | `protocol/cok_emu_login.py` | 不做本方案时的替代路径 |

环境（已在本机验证可用）：
* 模拟器 AVD `medium_phone`（Android 16 / arm64-v8a），镜像在
  `/opt/homebrew/share/android-commandlinetools/system-images/android-36/default/arm64-v8a/`
* `adb root` 可用 → **可以在模拟器上跑 frida 抓明文**（这是本方案的关键加速手段）
* Ghidra 工程：`COK-CN1-analysis/ghidra-project/`（针对 libgame.so；针对 libEncryptorP.so 需新开）

---

## 4. 分阶段实施（每阶段都有独立验收）

> **总体策略：不要一上来就啃 .so。**
> 先用 frida 把**明文抓出来**（绕过 GPXX 格式逆向），再用**已知明文/密文对**判定加密算法，
> 最后才需要动 .so 拿 key。顺序反过来能省掉 80% 的工作量。

### Phase 0 —— 素材解包与索引（0.5h）
1. 解包插件 apk：`unzip gp_sdk_plugin_5_5_4_3.apk -d gp_plugin/`，取出 6 个 `classes*.dex`。
2. 用 `scripts/dexdis.py` 建立索引：
   ```bash
   python3 scripts/dexdis.py gp_plugin/classes.dex --xref "password|salt|loginKey|signMD5" | head -200
   ```
3. 目标：**列出**与登录相关的类/方法清单（salt 请求、密码哈希、登录请求组装、token 存取）。

**验收**：能指出"哪个方法算 signMD5"、"哪个方法组装登录请求"。

### Phase 1 —— 用 frida 抓 GPXX 明文（2-4h，**最高性价比**）
1. 模拟器装插件宿主（果盘游戏包 `com.hcg.cok.ewanqf.guopan`，已在仓库里：
   从真机 `pm path` 拉取的 base.apk）。
2. 装 frida-server（arm64），`adb root` 后 attach 到游戏进程。
3. hook `libEncryptorP.so` 导出的 `ttEncrypt`（动态注册，需按
   `RegisterNatives` 的签名定位：搜字符串 `ttEncrypt` 的引用点，
   或直接 hook `RegisterNatives` 打印注册表）。
   - 要抓的是**入参（明文 buffer + 长度）**和**出参（密文）**。
4. 在模拟器上用 UI 自动化登录一次（`cok_emu_login.py` 的 `do_login` 已有可用实现：
   资源 id `view_login_user_name` / `view_login_password` / `view_protocol_checkbox` / `view_login_btn_login`）。

**验收**：拿到至少 2 组 (明文, 密文) 对，且明文里能看到 `gptest001` 这类账号明文。

> **这一步直接消灭了 GPXX 格式逆向**：知道明文长什么样，GPXX 的字段号/编码就清楚了，
> 甚至可以"照抄明文结构"来构造请求。

### Phase 2 —— 判定加密算法（1-2h）
用 Phase 1 的 (明文, 密文) 对：
1. **长度关系**：密文长度是否 = 明文长度（流/XOR）还是 +16/对齐（AES-ECB/CBC）。
2. **同明文两次**：连抓两次同账号登录（salt/时间戳不同 → 明文不同）。
   * 若两段密文相同 → ECB；不同 → CBC/CTR/含随机数。
3. **已知 S-box 证据**：`libEncryptorP.so` 内含 **AES inv S-box @ 0xf650**、**rcon @ 0xcf6b**
   → 优先假设 **AES**（ECB 或 CBC）。
4. 若 AES-CBC：从 .so 的 `.rodata/.data` 里找 **16/24/32 字节高熵常量**（用
   `readelf -x .rodata` + 熵筛，或在 Ghidra 里从 inv S-box 的 xref 回溯 key）。
   **候选 key 源**（按可能性）：`appKey=WVI2EOLJIW5YEE1Z` 的 MD5/AES 派生、
   常量字符串、appId+固定串派生。
5. 验证：用候选 key/IV 重算密文，与抓包逐字节比对。

**验收**：能用 Python 对任意明文算出与 SDK 完全一致的密文。

### Phase 3 —— 复刻"取 salt"与"登录"两个请求（2-4h）
1. 从 Phase 1 的明文里读出：请求里的 `appId / appKey / deviceId / imei / oaid / vaid /
   sign / timestamp / account / salt / 密码哈希` 各是什么、从哪来。
2. 用 `cok_elex_account.py` 里已逆出的 **elex 账号服务**同类手法（md5+盐+排序签名）实现果盘版：
   * `signMD5(密码, salt)` 的确切拼接顺序（从明文对照反推，别猜）
   * `sign` 的字段集合与排序规则
3. 实现 Python 客户端：
   ```
   salt = GET/POST <salt接口>            # 用 Phase 1 明文里的路径
   resp = POST /gamesdk/140514  {account, passHash, appId, sign, timestamp, device...}
   → 解出 {uid, token, loginKey}
   ```

**验收**：脚本能对**真实账号**换出 token（先用假号验证服务端返回"账号不存在"这类业务错，
而不是协议错）。

### Phase 4 —— 复刻 `LOGINBETWEENAPP`，拿 per-game id（1-3h）
1. 从 Phase 1 的明文/流量里找到"用 SDK 账号换游戏 uid"的那条请求
   （`SUBCMD_ACCOUNT_LOGINBETWEENAPPREQ`，参数含 OpenId/Token/appid）。
2. 调它 → 得到游戏侧 per-game id → 组装 `pfId = "ewanqf:<id>"`。
3. 交叉验证：把抓包里的 `ewanqf:1084D654F5A7FB599158` 与 SDK 的
   `OpenId=1084D65F5A7FCB599158` 的映射关系弄清（是否固定变换/查表）。

**验收**：能用账号密码换出 `pfId`。

### Phase 5 —— 端到端打通 + 出脚本（1-2h）
1. 串联 Phase 3+4 → 输出 §1.1 那组字段 → 写入 `protocol/accounts/<gameUid>.json`
   （用 `cok_accounts.save_account(acc, owner=...)`）。
2. `pf` 用 `cok_accounts.probe_pf()` 实测确定（**别猜**，服务端会校验 pf）。
3. 用 `cok_client.py` 登录游戏服验收。

**验收**：§1.2 的 4 条全部满足。

---

## 5. 风险与备选

| 风险 | 概率 | 影响 | 应对 |
|---|---|---|---|
| `ttEncrypt` 用的是 AES-CBC 且 IV 随机、key 运行时派生 | 中 | Phase 2 卡住 | Phase 1 的 (明文,密文) 对里能直接读出 IV；key 用 .so xref 找；再不行用 frida 直接调 native（= 回到"需要设备在线"） |
| GPXX 格式复杂（2357 混淆类） | 中 | Phase 1/3 变慢 | **Phase 1 用 frida 绕开**；编码器实现通常在 `com.GPXX.Proto` 的 writer 类里，字段名明文可搜 |
| salt/登录接口不是 `POST /gamesdk/{appid}` 而是别的 | 低 | Phase 3 返工 | Phase 1 抓的明文里能看出完整请求；抓包样本里已有 704B 的完整请求 |
| 果盘服务端改了协议 | 低 | 全线返工 | 抓包时间戳已记录（2026-10-29），失败先复抓 |
| 风控要求真实设备指纹 | 中 | 登录被拒 | 明文里的 imei/oaid/vaid 字段照抄真机值；必要时 Phase 1 就在真机上做 |

**兜底**：本方案任何阶段卡住，模拟器发卡机（`cok_emu_login.py`，已跑通）都能交付可用功能，
只是需要一台安卓环境。**不要为了做 C 而推迟 B 的产品化。**

---

## 6. 渠道优先级

| 渠道 | 包名 | 可行性 | 备注 |
|---|---|---|---|
| **果盘 ewanqf** | `com.hcg.cok.ewanqf.guopan` | ✅ **本方案目标** | HTTP + 插件 APK 已在手，salt+MD5 流程清楚 |
| 官方 elex | `com.hcg.cok.cn1` | 🟡 可行但优先级低 | elex 账号服务（`accountapi1.elexapp.com/services/v1/user/login/`）**已完全复刻**（`protocol/cok_elex_account.py`），只差"建号"的 gameservice sig（同一类 native 加密） |
| 小七 | `com.smwl.x7market`（手机上是市场包） | ❓ 未知 | 渠道 SDK 待确认 |
| oppo / nearme | `com.hcg.cok.nearme.gamecenter` | ❌ **不可行** | gcsdk 原生 + OPPO 服务端风控（§2.6） |

---

## 7. 立刻可做的下一步（不依赖本方案）

1. 果盘登录页还有「**快速注册**」页签 → 可以**全自动开新号**（`cok_emu_login.py` 加一段注册自动化）。
2. 模拟器发卡机封成云端 worker（redroid 容器）→ 架构③（云端多用户）闭环。
3. 网页加「提交渠道账号密码 → 后台发卡」的入口。

---

*关联文档：COK-游戏服协议实测报告.md §8.1.7（渠道账号/密码方式取证）*

---

## 8. 实测数据（2026-10-29 执行完成，纯 PC 跑通，三处事实订正）

> 状态：**已完成**。加密层 + 登录协议全部复刻，产出自包含脚本 `protocol/cok_channel_login.py`。
> 对两份抓包做到 **XXTEA + protobuf 逐字节往返一致**；假号打真服务器得到业务错（协议正确）。

### 8.1 对原方案"已知事实"的三处订正（以实测为准）

1. **`libEncryptorP.so` / `ttEncrypt` 与登录无关**。
   它属于**字节跳动埋点库** `com.bytedance.applog.encryptor.EncryptorUtil`（classes5.dex），
   是数据上报（`xxdatareport` 之外的 applog）用的，不是 `/gamesdk/` 登录加密。
   原方案 §2.3 / Phase 1 "hook ttEncrypt 抓登录明文"方向错误 → 已废弃该路径。

2. **加密算法是 XXTEA，不是 AES**。
   登录载荷加解密在纯 Java 类 `com.flamingo.sdk.ud.c`（jadx 反编译确认），
   标准 XXTEA（delta `0x9E3779B9`、小端、长度字放尾字）。
   原方案 §2.3 "已确认是 AES（inv S-box/rcon）"系对 `libEncryptorP.so` 的误判；
   那个 .so 里的 AES 是字节跳动埋点自带的，和登录无关。

3. **两个通道用两把不同的 16 字节 key**：
   - `/gamesdk/*`（登录/init/recommend 等）→ key = **appKey `WVI2EOLJIW5YEE1Z`**
   - `/xxdatareport.php`（数据上报）→ key = **签名盐 `#%$*)&*M<><vance`**
   （盐确实是 16 字节，但它只用于上报通道 + sign 计算，不是登录通道的加密 key。）

### 8.2 加密层（已逐字节验证）
- 线格式：`POST /gamesdk/140514`，body = **MIME 76 列标准 base64**（`base64.encodebytes`）→ XXTEA 密文。响应同构。
- XXTEA = `com.flamingo.sdk.ud.c` 忠实移植：`encrypt=m9439(憋)`、`decrypt=m9438(憊)`，
  `m9441` byte→int（小端）、`m9440` int→byte、原始长度写入最后一个 int 字。
- 验证：对 `capture_emulator_login.pcap` + `capture_phone_gcsdk.pcap` 的全部 5 个
  `/gamesdk/140514` 请求，`decrypt→encrypt` 与原密文**逐字节一致**；protobuf `parse→serialize` 也逐字节一致。

### 8.3 登录协议（protobuf / GPXX，已解码）
- 载荷是 protobuf。账号命令块路径：`top.f3.f17 { f1=subcmd, f2=设备指纹块, f3=账号, f4=密码哈希 }`。
- 密码登录两步（来自 `com.flamingo.sdk.dex1.request.a.m8434`）：
  1. **subcmd 101 取 salt**（`f4` 密码哈希留空）→ 响应 `f3.f18 { f1=101, f4=<salt> }`（抓包里 salt=`TB0THZGH`）。
  2. **密码哈希 = `MD5(salt + 明文密码)`** 的小写 hex（`k0.m9332(m5474.m4626()+password)`，`k0.m9332`=标准 MD5）。
  3. **subcmd 102 登录**（`f4` 填该哈希）→ 成功时响应块回 loginKey/uid；失败回业务码（如 `1026`=账号不存在）。
- `sign` 盐 `#%$*)&*M<><vance` 用于 GPXX 的 sign 字段与上报通道（见 `com.GPXX.Proto.base.a`）。

### 8.4 命令结构 / per-game id（真机抓包 + jadx 反编译已定位）
- 顶层命令**恒为 `cmd=1205`**（`top.f2.f1`）；真正的子命令由 `top.f3` 的**字段号**（= `t0.m5602(1).m5606(<subcmd>)` 里的 subcmd）决定，
  抓包里体现为 `top.f3.f2`。常见：`f1=101/102` 走 `f3.f17`（salt/密码登录）。
- 登录后的认证信封形如 `Login_<guopanUid>_<appid>_<token>`；真机抓包里 **guopanUid=305273801**。
- **102 密码登录成功响应**（真机抓包逐字节解出）直接带齐 per-game id：
  `top.f3.f18 { f1=102, f2="Login_<guopanUid>_<appid>_<token>", f3=<guopanUid>, f5=<perGameId> }`，
  其中 **`f5=D654F5A7FB599158`** 即 per-game id。
- **pfId 推导**：`pfId = "ewanqf:1084" + perGameId` → `ewanqf:1084D654F5A7FB599158`，
  与账号库 `1125641597002221.json` 完全一致（前缀 `1084` 与 SDK OpenId 前缀同源）。

> **订正（此前命名有误）**：之前把抓包里那条 `top.f3.f40 { f1=140514, f2=305273801 }`、
> `top.f3.f2=37` 的请求标成 "LOGINBETWEENAPP"，**实为 `GETSMALLACCOUNTGAMEUIN`（subcmd 37）**——
> 即"列小号 + 各自 game uin"。真正的 `LOGINBETWEENAPP` 是 **subcmd 25**。功能判断（换 per-game id）没错，
> 但命令名与 subcmd 号需以本节为准。脚本里的 `build_loginbetween_request()` 实现的就是 subcmd 37
> （函数名属历史遗留，待重命名；行为 = GETSMALLACCOUNTGAMEUIN）。

### 8.5 产物与用法
```bash
python3 protocol/cok_channel_login.py --selftest               # 离线回放抓包自证(无需网络/账号)
python3 protocol/cok_channel_login.py <果盘账号> <密码>         # 账号密码→pfId/platformToken
python3 protocol/cok_channel_login.py gptest001 wrongpass       # 假号→业务错 1026, 证明协议正确
```
脚本**自包含**（内联 XXTEA + protobuf 编解码 + 101/102/f40 三个明文模板），运行期不依赖
pcap / 模拟器 / frida；`--selftest` 会回放 `evidence/chanlogin/` 下两份归档 pcap 做离线自证。

### 8.6 成功路径（已知限制）
**果盘 HTTP 只能换出 `pfId`（+ SDK openId/token），换不出 `gameUid` / `uuid`。**
后两者**不由果盘下发** —— 它们是**游戏服**凭 `pfId` 首次登录时分配、落在设备
`Cocos2dxPrefsFile.xml`（即发卡机 `cok_emu_login.py` 的读取来源 `game_uid` / `account_uuid`）。
因此 prompt §5 要求的完整三元组 `(pfId, gameUid, uuid)` **无法只靠果盘 HTTP 补齐**：
拿到 `pfId` 后还要再走一次**游戏服登录**（新 pfId 会自动建号并分配 gameUid/uuid），
这一跳属于游戏服协议（`cok_client` 那套 SFS），不在果盘渠道协议范围内。

**真号端到端验证（2026-10-29，已通过）**：
用真实果盘账号 `niu2223` 跑 `cok_channel_login.py` 全流程：
- 取 salt（101）→ 本次 salt=`S17NHQL0`（每次请求不同，抓包里那次是 `TB0THZGH`）；
- 密码登录（102）→ **retcode=0 登录成功**（不是业务错），响应
  `f18{ f1=102, f2=认证信封, f3=305273801(guopanUid), f5=D654F5A7FB599158(perGameId) }`；
- 派生 **`pfId=ewanqf:1084D654F5A7FB599158`**、`platformToken=1084D654F5A7FB599158`，
  与账号库 `1125641597002221.json` 里已归档的值**逐字段完全一致** → 协议 + pfId 推导得到真号证实。

**自检状态（离线，--selftest）**：
- 取 salt（101）对任意账号成功，salt 固定在 `f18.f4`（抓包值 `TB0THZGH`）；
- 登录（102）对假号/错密回业务错 `1026`（`f3.f29="密码不正确,请重新输入"`），协议正确；
- 两份抓包共 13 个 `/gamesdk` 帧，XXTEA 往返 + protobuf 往返**全部逐字节一致**；
- per-game id → pfId 推导与真机值核对通过；`GETSMALLACCOUNTGAMEUIN`(subcmd 37, f40) 模板逐字节重建通过。

**仍缺的唯一一环（非果盘协议问题）**：
果盘只给到 `pfId`；`gameUid` / `uuid` 仍需游戏服凭 `pfId` 登录后分配。
对 `niu2223` 这个账号，其 `gameUid=1125641597002221` / `uuid=cok0500...` 已在账号库里（此前抓取），
故三元组已齐；但对**全新、从未登过游戏服的 pfId**，仍要再走一次游戏服登录（自动建号）才能拿到
gameUid/uuid。注意 `1125641597002221` 是用户真号，游戏服登录会踢现有在线会话，未经确认不擅自执行。

### 8.7 开发期工具（可复用）
- jadx 1.5.0 干净反编译（自研 `dexdis.py` 对该 SDK 混淆解码不全，已改用 jadx）：
  `jadx --no-res --no-debug-info -d out classes.dex` → `com/flamingo/sdk/ud/c.java` 即加密实现。
- frida-server 17.13.0 在本机 Android 16 模拟器上注入即崩（疑似 `libgism.so` 反注入），
  **本任务未依赖 frida**；改用"jadx 还原源码 + 抓包逐字节验证"的静态路线反而更快更稳。

### 8.8 小号（small account）命令族 —— 解释"登录后先进小号列表"现象（2026-10-29 实测）

**现象**：果盘账号登录后，SDK 先展示"小号列表"，点某个小号才真正进游戏。
**结论**：一个果盘账号（`guopanUid`）下挂**多个小号**，每个小号是一个独立的果盘游戏身份
（独立 `perGameId` → 独立 `pfId`）。这正是 SDK 的小号选择界面。

**subcmd 号**（来自 `jadx` 反编译 `com.GPXX.Proto.z$z2` 枚举 + `com.flamingo.sdk.dex1.request.a`）：

| subcmd | 命令 | 组装函数 | 作用 |
|---|---|---|---|
| 21 | `GETRANDOMACCOUNTNAME` | — | 取随机小号名 |
| 25 | `LOGINBETWEENAPP` | — | 真正的 app 间登录换 token（与 37 不同） |
| 37 | `GETSMALLACCOUNTGAMEUIN` | `a.m8428` | **列小号 + 各自 game uin**（入参 `{appid, guopanUid}`，即抓包里的 `f3.f40`） |
| 39 | `CREATESMALLACCOUNTGAMEUIN` | `a.m8427` | 建小号并分配 game uin（入参含小号名） |
| 41 | `MODIFYSMALLACCOUNTGAMEUIN` | `a.m8435` | 改小号 |
| 43 | `LOGINSMALLACCOUNT` | — | 登录指定小号 |

顶层包装恒为 `cmd=1205`，子命令 = `t0.m5602(1).m5606(<subcmd>)`（抓包里体现为 `top.f3.f2`）。

**实测（niu2223 登录态发 subcmd 37，只读）**：
```
果盘账号 niu2223  guopanUid=305273801
  └─ 小号[0]  角色名=小强
       perGameId = D654F5A7FB599158
       gameUin   = 1791267779
       pfId      = ewanqf:1084D654F5A7FB599158   (= "ewanqf:1084" + perGameId)
```
响应结构：`top.f3.f41.f1[] { f1=appid, f2=guopanUid, f3=perGameId, f4=gameUin, f6=角色名 }`，
retcode `f3.f1=0`、`f3.f2=38`(RES)。

**三层 ID 必须分清（关键）**：

| ID | 本例值 | 归属层 | 说明 |
|---|---|---|---|
| `guopanUid` | `305273801` | 果盘**账号**级 | 一个果盘账号一个 |
| `gameUin` | `1791267779` | 果盘**小号**级 | 果盘给小号的 id，**≠ COK gameUid** |
| `perGameId` | `D654F5A7FB599158` | 果盘**小号**级 | → `pfId=ewanqf:1084<perGameId>` |
| `gameUid` | `1125641597002221` | **COK 游戏服**角色级 | 游戏服分配，落在设备本地，**不来自果盘** |

> 果盘侧给的 `gameUin`（1791267779）**不等于** COK 游戏服的 `gameUid`（1125641597002221）；
> 二者是不同系统的 id。果盘小号命令族只在"果盘身份"这一层打转，拿不到 COK 的 `gameUid/uuid`。

### 8.9 最后一跳的边界实测（2026-10-29 下午，游戏服直连）

用**果盘真号**（`1125641597002221`，pf=cn_ewanqf，pfId=ewanqf:1084D654F5A7FB599158）
逐项篡改登录参数，看服务端到底认什么：

| 实验 | 参数改动 | 结果 | 结论 |
|---|---|---|---|
| A2 | 原样 | ✅ 登录成功 | 基线 |
| A4 | `un` 置空(gameUid 保留) | ✅ 登录成功 | **`un` 可省**，只要 `gameUid` 对 |
| A1/A3 | `gameUid` 置空 | ❌ `E002` | gameUid 必填 |
| Y | 原 gameUid + **换全新 uuid** | ❌ `E002` | **uuid 也是强绑定**（不是自由设备号） |
| W | 空 gameUid + 全新 uuid | ❌ `E002` | 同上 |
| Z | **编造 pfId**(随机 perGameId) + 空 gameUid + 全新 uuid | ❌ `E100111` | **未知 pfId → 服务端查不到服务器信息，不自动建号** |
| — | 换 `platformToken` / `signCode` | ✅ 照样登 | 不校验(§2.1) |

> ### ⚠️ 订正（2026-10-29 21:4x，见 §8.13）：**「uuid 强绑定设备」是误判**
>
> 上面 Y/W 两行只说明"**错的** uuid 会失败"，并不等于 uuid 绑设备。
> 真相是：**uuid 绑定的是账号（角色）**，而且**服务端会按 pfId 主动把正确 uuid 下发给你**
> （`getserverlist.php` 的 `loginFlag=1` 响应里就带着）。
> 实测：**同一个 pfId + 全新随机设备 uuid → 仍返回原角色**；
> 用它下发的 uuid + **全新 deviceId** → SFS 登录 **✅ 成功**。
> ⇒ 「换 uuid → E002」依然成立，但正确解法不是去原设备捞 uuid，而是**问服务端要**。

**`E100111` 的含义被钉死了**：服务端拿 pfId 去查"这个平台身份对应哪个区服/服务器"，
查不到（果盘后端没登记这个 perGameId）→ 报"无法获取服务器信息"。
**已知 pfId + 空 gameUid → E002**：区服查到了，但角色查不到（该 pfId 下已有角色，得给对 gameUid）。

### 8.10 结论：最后一跳需要"先在果盘后端登记"

游戏服**不会**替果盘建角色。角色 (gameUid, uuid) 是**游戏服建角色时分配并落库**的，
而"这个 pfId 属于哪个区服"要果盘后端先登记。三种可能路径，现状：

| 路径 | 需要什么 | 状态 |
|---|---|---|
| A. 果盘 `subcmd 39`(CREATESMALLACCOUNTGAMEUIN) 建小号 → 果盘后端登记 perGameId → 游戏服首登建角色 | **果盘账号密码**（纯 PC 即可） | 请求模板待补（jadx 的 `a.m8427` 未留存）；密码不在仓库 |
| B. 游戏服 HTTP `getserverlist.php?uuid=&loginFlag=` 登记 uuid → 再首登 | **手机接回 USB** 抓一次真实请求 | sig 爆破失败（40+ 组合），key 在 libgame.so 加密串里 |
| C. 官方转移通道 `device.bind.*` / `user.bind` | — | ❌ **全局关闭**（2026-10-29 在 nearme **和** cn_ewanqf 两个渠道上分别实测，均 `E000000`；不是按渠道开关） |

**当前卡点**：A 和 B 都需要用户侧一个输入（果盘账号密码 / 手机接回 USB）。
其余部分（果盘协议、XXTEA、pfId 派生、pf 实测、采集、多用户骨架）都已就绪。

### 8.11 补充事实（2026-10-29 下午追加）

* **只有 `1125641597002221`（ʚAndreaɞ / 果盘号 `niu2223`）是果盘渠道**；
  `136063574002223`（元气少女李逵）和 `44056610002223`（鸭皇）都是 **nearme/oppo** 通道，
  本方案的果盘实验全部打在 Andrea 号上，结论不受影响。
* **gameservice 的 sig 不在果盘 SDK 里**：插件 dex 全量扫描没有 `getserverlist.php` / `gameservice`
  相关字符串（只有 `open.guopan.cn/gamesdk/*` 那套 GPXX 通道）→ 登记 uuid/区服这一步是
  **游戏 native(libgame.so)** 做的，sig 的 key 只在加密串里。
  已知 key 候选(appKey / 盐 `#%$*)&*M<><vance` / appId / 裸 md5 等 40+ 组合)**全部爆破失败**。
* `device.bind.*` / `user.bind` 在 **cn_ewanqf 渠道上同样 `E000000`**（在 nearme 上也测过）
  → 这两个命令是**全局关闭**，不是按渠道开关（订正了"可能按渠道开"的猜测）。
* **抓包脚本已就绪**：`protocol/capture_gamesvc.sh` —— 自动挑真机、起 tcpdump、重启 App、
  收包到 `evidence/chanlogin/capture_gamesvc_<host>.pcap`。手机接回 USB 后一条命令即可，
  目标是拿到 `getserverlist.php` 的真实 URL/参数/sig。

### 8.12 为什么这一跳值得做（价值）

游戏服**只认 (pfId, gameUid, uuid) + pf**，且三者强绑定（换任一 → E002），
`platformToken` / `signCode` 完全不校验。于是：

| 场景 | 现在 | 这一跳打通后 |
|---|---|---|
| 已有号在**原设备**上 | 已支持(采集) | 不变 |
| 已有号换到 **PC** | 做不到(uuid 绑设备) | 仍做不到(官方转移通道关闭) |
| **新号**(果盘号+密码 → 建号) | 做不到 | ✅ **纯 PC 开新号**,不需要任何安卓环境 |

→ 结论：这一跳的价值 = **"用账号密码直接开新号"**（不是接管别人的旧号)。



**对完整三元组的意义**：果盘这一层（账号密码 → guopanUid → 小号列表 → 每个小号 pfId）已可从纯 PC 全部取得；
仍缺的唯一一环是 **pfId → COK `gameUid`/`uuid`** 的映射，发生在游戏服（`txaia-cok.elexapp.com`）首登建号那一跳，
**不在果盘 SDK 协议范围内**

---

### 8.13 🔓 最后一跳已打通：`pfId` 就是万能钥匙（2026-10-29 晚，全链路实测）

> **本节推翻 §8.10 / §8.12 的结论**（那一节写于 sig 破解之前）。
> 旧结论「uuid 强绑设备 → 不能接管旧号 / 必须手机」**是错的**。

#### 8.13.1 突破口：游戏把带签名的 URL 直接打进 logcat

游戏客户端（Cocos2d-x）在启动时把自己的 HTTP 请求整条 URL 打进 logcat：

```
adb logcat -d | grep -oE "https://[^ ]+gameservice/[^ ]+"
```
```
https://dsap3cok.elexapp.com/gameservice/getline.php?uuid=f6973b30b166412&loginFlag=1
  &pfId=ewanqf:1084D654F5A7FB599158&pf=cn_ewanqf&token=CN&country=US&t=1793228008
  &sig=bb0f4e27ec93efc6e5012aad7eaed886&version=12.06.0&versioncode=1896
  &channel=cn_ewanqf&packageName=com.hcg.cok.ewanqf.guopan&serverId=COK2223
  &flag=ph&acuuid=cok05009672d131fc1eb1f4a0becfd0ed77&lang=zh_CN
```
→ 直接拿到 **明文参数 + 签名** 的成对样本（4 组），而且**不需要手机、不需要 frida、不需要动 libgame.so 的加密串**。

#### 8.13.2 `sig` 算法（已破解，4/4 样本逐字节一致）

```
sig = md5( uuid + str(t) + "@z4LugUwrDN0MqOJtzmHPK7Ss-k4taAUOZh1M3Yu9" )
```
* `uuid` = **设备侧** 16 位 hex（与账号无关，随便填）
* `t` = 秒级时间戳
* 密钥常量在 `lib/arm64-v8a/libgame.so` 里**明文可见**（`strings` 直接能捞到）

验证：

| 样本 | uuid | t | 期望 sig | 实算 sig |
|---|---|---|---|---|
| getline1 | f6973b30b166412 | 1793228008 | bb0f4e27ec93efc6e5012aad7eaed886 | ✅ 同 |
| getline2 | f6973b30b166412 | 1793243462 | 0a31e205be1f9924ad6adf26ed4eed7a | ✅ 同 |
| getparam1 | f6973b30b166412 | 1793228009 | be512b826ede32156903586d185852b9 | ✅ 同 |
| getparam2 | f6973b30b166412 | 1793243464 | 09e506626d55eb5714ef601240d20d67 | ✅ 同 |

> 破解方法：`strings libgame.so` → 拿 7 万个候选串 → 对 ~15 种规范化 × ~9 种拼接方式 × 全部候选做 md5 爆破 → 唯一命中。

#### 8.13.3 `getserverlist.php` 才是真正的入口（`loginFlag=1`）

```
GET https://p3cok.elexapp.com/gameservice/getserverlist.php
    ?uuid=<16位hex,设备侧,随便填>&pfId=<渠道身份>&loginFlag=1&pf=cn_ewanqf
    &token=CN&country=US&t=<秒>&sig=<md5>&version=12.06.0&versioncode=1896
    &channel=cn_ewanqf&packageName=com.hcg.cok.ewanqf.guopan&serverId=COK2223
    &flag=ph&lang=zh_CN
```
响应（实测，Andrea 号）：

```json
{"lastLoggedServer":"2223","serverList":[{
  "id":"2223","zone":"COK2223","ip":"47.89.213.242","port":"80",
  "uuid":"cok05009672d131fc1eb1f4a0becfd0ed77",
  "gameUid":"1125641597002221","gameUserName":"ʚAndreaɞ",
  "buildCode":"f97c622e05af38f98480958b2fbca88b","gameUserLevel":"47"}], ...}
```
→ **一次请求就吐出 `gameUid` + 账号 `uuid` + 区服 + buildCode + 角色名/等级**。

`loginFlag` 语义：`0` = 只列全服区服（无角色信息）；`1` = 带角色信息。

#### 8.13.4 三个反直觉实测（**推翻了旧结论**）

| 实验 | 请求 | 结果 | 结论 |
|---|---|---|---|
| A | 设备uuid=Andrea 的 + 合法 pfId | 返回 gameUid=1125641597002221 / uuid=cok0500… | 基线 |
| B | 设备uuid=Andrea 的 + **编造 pfId** | 落到兜底绿服 `COK10052`(serverType=23, greenServer=1)，**无任何角色字段** | pfId 必须真实存在 |
| C | 同上但 `loginFlag=0` | 只返回全服区服列表，**与 pfId 无关** | loginFlag=1 才是解析角色 |
| **D** | **全新随机设备uuid** + 合法 pfId | **仍返回同一个角色**(原 gameUid/uuid/昵称) | **角色按 pfId 查，与设备 uuid 无关** |
| **E** | **合法 nearme pfId** + 全新设备uuid | 返回该 nearme 账号的 gameUid=44056610002223 / uuid=cok0f6d… / 角色名"大鸭鸭™" | **跨渠道通用** |
| **F** | 上面 E 的凭据 + **全新 deviceId** `f00dbeef0102030` 走 SFS 登录 | **✅ 登录成功** | **deviceId 不校验；uuid 绑的是账号不是设备** |

> ⇒ **「uuid 强绑定设备」是误判**：uuid 绑定的是**账号**（角色），
> 而服务端**会主动把正确的 uuid 发给你**，条件只是给出正确的 pfId。
> ⇒ **拿到 pfId = 拿到该账号的全部游戏服凭据**，不需要手机/root/模拟器/官方转移通道。

#### 8.13.5 新的完整链路（纯 PC，零安卓依赖）

```
果盘账号 + 密码
   │  POST http://userapi.guopan.cn/gamesdk/140514  (XXTEA+protobuf)
   │    subcmd 101 取 salt → md5(salt+pwd) → subcmd 102 登录
   ▼
pfId = "ewanqf:1084" + perGameId            ← 果盘账号 → 渠道身份
   │  GET https://p3cok.elexapp.com/gameservice/getserverlist.php
   │      ?uuid=<随机16hex>&pfId=<pfId>&loginFlag=1&sig=md5(uuid+t+密钥)
   ▼
gameUid + 账号uuid + zn + buildCode + 角色名  ← 游戏服按 pfId 解析角色
   │  SFS 握手 → login(pf, pfId, gameUid, uuid, deviceId=随机)
   ▼
✅ 登录成功（任意设备、任意 IP）
```

#### 8.13.6 实测端到端（2026-10-29 21:4x）

* **纯 pfId 接管旧号**：nearme「鸭皇」(gameUid=44056610002223，手机上玩过的号)
  → gamesvc 解析 → **全新 deviceId** → SFS 登录 **✅ 成功**（`id=3f130d55…_18`）
* **果盘号**：Andrea(1125641597002221) → 全新 deviceId `aabbccddeeff1122` → SFS 登录 **✅ 成功**

#### 8.13.7 产物

* `protocol/cok_gamesvc.py` —— getserverlist 客户端（sig 算法 + 角色解析）
* `protocol/cok_channel_login.py` —— 新增 `--make-account`：果盘账号密码 → **完整可直连凭据**

#### 8.13.8 仍未闭合 / 风险

1. **「开新号」**：需要一个**在果盘后端登记过、但游戏服还没有角色**的 pfId。
   * 编造 pfId → 兜底绿服 + 无角色（实验 B）。
   * 果盘 `subcmd 39`(CREATESMALLACCOUNTGAMEUIN) 建小号可产出新 pfId —— **请求模板已按 jadx 还原并离线自证通过**
     （`cok_channel_login.py --create-small`），但**需要一次真实果盘密码登录拿新信封**才能在线验证。
   * 另一条路：`subcmd 37` 列小号 → `subcmd 43`(LOGINSMALLACCOUNT) 选号进游戏。
2. **风控**：新 IP + 新 deviceId 登录是否会被判定异常，尚未长时间观察。
3. **nearme/OPPO 渠道的 pfId 仍拿不到**（OPPO SDK 原生 + 风控）；果盘渠道已可从账号密码直接换。
4. `dsap3cok.elexapp.com`（游戏客户端在用）从国内直连不通（curl http=000）；`p3cok.elexapp.com` 可用。

#### 8.13.9 §8.10 / §8.12 结论订正

| 旧结论（§8.10/§8.12） | 新结论（§8.13） |
|---|---|
| 「uuid 强绑定设备 → 不能接管别人旧号」 | ❌ **错**。uuid 绑账号；服务端按 pfId 下发 uuid |
| 「最后一跳需要 getserverlist 的 sig，sig 爆破失败」 | ✅ **sig 已破解**（§8.13.2） |
| 「新号必须走 subcmd 39 建小号」 | ⚠️ 仍需，但**模板已就绪**；且**接管已有角色**完全不依赖它 |
| 「价值 = 只能开新号」 | ✅ 价值更大：**接管旧号 + 开新号** 两条都能纯 PC 做到 |

---

## 9. 从手机批量「捞号 → 加进控制台 App」（2026-11-09 实测闭环）

### 9.1 一句话

手机上的**两个渠道包各只留着一个当前号**，凭据全在 SharedPreferences 里，
**不用密码**就能捞出来直接加进控制台 App（PC 网页端 + 安卓 App 双端都能加）。

### 9.2 渠道 ↔ 包 ↔ 号（本次实测）

| 渠道 | 包名 | platformUid / pfId | gameUid | 区服 | 端口 |
|---|---|---|---|---|---|
| **OPPO / nearme** | `com.hcg.cok.nearme.gamecenter` | `nearme:g1372797742670953701` | `44056610002223`（鸭皇） | COK2223 | 32231 |
| **66手游 / ewanqf(果盘)** | `com.hcg.cok.ewanqf.guopan` | `ewanqf:1084LL52C245E1C9A9A86E` | `351542128002216` | **COK2217** | **32171** |

⚠ **66手游那个号在 2217 区**，跟其余号（2223 区）**不同服不同端口** —— 别拿 2223 的
host/port 去拼它。`serverId` 也要跟着换（`2217` / `COK2217`）。

### 9.3 捞号（PC，root 设备）

```bash
python3 cok_account.py -p com.hcg.cok.ewanqf.guopan --json   # 当前号
python3 cok_account.py --list                                 # 列出所有渠道包
```
`cok_account.load_account()` 读的键：
`platformUid`(=pfId) / `game_uid` / `device_uid` / `account_uuid` /
`buildcode` / `theSignCode` / `account_ip` / `account_port` / `account_zone` /
`server_id`。渠道包名 → `pf` / `pfId` 前缀：`com.hcg.cok.<渠道>.<包>` ⇒ `pf=cn_<渠道>`。

### 9.4 加进**安卓控制台 App**（比 App 里的「本机导入」按钮还直接）

安卓 App 的账号注册表 = **`/data/data/com.cok.console/files/cok/accounts/<gameUid>.json`**
（就是 `cok_accounts.ACCOUNTS_DIR`，安卓端 = `files/cok/accounts`）。

```bash
adb shell am force-stop com.cok.console          # 先停, 避免内存里的旧表覆盖
adb push accounts/<gameUid>.json /data/local/tmp/
adb shell "su -c 'cp /data/local/tmp/<gameUid>.json \
    /data/data/com.cok.console/files/cok/accounts/ && \
    chown u0_a386:u0_a386 /data/data/com.cok.console/files/cok/accounts/<gameUid>.json && \
    chmod 660 ...'"
adb shell am start -n com.cok.console/.MainActivity
```

⚠ **凭据 JSON 必须自己拼完整**（模板字段 + 设备字段），不能只写渠道那几项：
`baseActiveKey` / `appVersion` / `luaVersion` / `channelSign` / `isSmall` /
`device_info` / `parseRegisterId` 等公共字段缺一个就登不上。
`cok_accounts.save_account()` 会自动垫 `cok_client.ACCOUNT` 模板 —— **在 PC 上先入库,
再把生成的 JSON push 过去**, 是最省事的做法。

### 9.5 验收（两个号都实测过）

1. PC 直连登录: `bin 握手 → login → overview_new.data / stat.tt` 全通；
   pf 用 `cok_accounts.probe_pf()` 登录实测确定（`cn_nearme` / `cn_ewanqf`）。
2. 安卓 App 里点「切换」: 两个号都显示**已连接**且有真实数据（任务奖励/港口/联盟）。
3. `.active` 记得切回原主号（`136063574002223`）。
