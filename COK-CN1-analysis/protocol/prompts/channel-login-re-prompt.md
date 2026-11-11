# 提示词：逆向果盘渠道登录协议（可直接投喂给另一个 agent）

> 用法：把下面 `====` 之间的内容整段复制给执行任务的 agent。
> 它是**自包含**的：不需要读我们的会话记录，所有关键事实都在里面。
> 配套详细方案：`COK-CN1-analysis/protocol/RE-渠道登录逆向方案.md`

====

你是一名逆向工程 agent。目标：**在纯 PC 环境（无 Android 设备、无 root、无模拟器）复刻"果盘(ewanqf)渠道账号 + 密码 → 游戏服登录凭据"的协议**，产出一个可执行 Python 脚本。

## 0. 背景（你需要知道的就这些）

有一个游戏（列王的纷争 中国服 / COK）的直连客户端，能绕过 App 直接跟游戏服务器说话。已支持多账号：每个账号的"凭据"是一组字段，登录时发给游戏服。

**服务端到底校验哪些字段（已实测，别重测）**：

| 字段 | 校验? |
|---|---|
| `gameUid` | ✅ 校验（换错 → E002） |
| `uuid` | ✅ 校验 |
| `pfId` | ✅ 校验 |
| `pf` | ✅ 校验（如 `cn_ewanqf` 才对） |
| `platformToken` | ❌ **不校验**（换随机串照样登录成功） |
| `signCode` | ❌ **不校验** |

所以游戏服真正认的只有 **(pfId, gameUid, uuid) 三元组 + pf**。`platformToken` 是装饰品 → **你不必追求"完全正确的 token"，只要换出角色身份即可**。

要登一个别人的号，需要它的 (pfId, gameUid, uuid)。本任务就是：**用账号密码把这三元组换出来**（pfId 是渠道发的 per-game 角色 id，gameUid/uuid 由游戏服在"SDK 账号登录游戏"那一步分配）。

## 1. 工作目录与素材

仓库根：`/Users/a1234/workspace/me/cok/COK-CN1-analysis/`

已归档素材（**不要重新去手机/模拟器上抓**，先看这些）：
```
protocol/evidence/chanlogin/
├── gp_sdk_plugin_5_5_4_3.apk      果盘 SDK 插件 (10.7MB)：6 个 classes*.dex + lib/arm64-v8a/libEncryptorP.so + libgism.so
├── libEncryptorP_arm64.so         加密库 75KB (stripped arm64)
├── capture_phone_gcsdk.pcap        真机抓包 30KB
└── capture_emulator_login.pcap     模拟器抓包 4.6KB
```

可复用工具：
- `scripts/dexdis.py` —— **自研 dex 反汇编器**（本机没有 apktool/jadx，所以自己写的）。
  用法：
  ```bash
  python3 scripts/dexdis.py <dex文件> <类名正则>          # 列类/方法 + 反汇编
  python3 scripts/dexdis.py <dex文件> --xref "字符串正则"   # 字符串交叉引用
  ```
- `protocol/cok_client.py` —— 游戏服直连客户端（**最终验收要用**）
- `protocol/cok_accounts.py` —— 账号库；`probe_pf(acc)` 会**登录实测**出正确的 pf（服务端会校验 pf，别猜）
- `protocol/cok_emu_login.py` —— 模拟器发卡机（兜底方案，已跑通；**本任务不要求做它**）

详细方案（含全部实测数据、抓包分析、风险清单）：`protocol/RE-渠道登录逆向方案.md`，**开工前先读一遍**。

## 2. 已知的协议事实（直接用，别重复推导）

### 2.1 果盘 API（真机抓包实证）
```
POST http://userapi.guopan.cn/gamesdk/140514 HTTP/1.1
Host: userapi.guopan.cn
Content-Type: application/x-www-form-urlencoded
Content-Length: <n>

<body = MIME 换行(76 列)的标准 base64 → 解出 <n> 字节密文>
```
- **路径 = base + appid**（`appid=140514` 是路径的一段，不是 query）。少了它 → `500 Internal server error`。
- 响应同样是 base64 密文（`Content-Type: text/plain`）。
- 同族端点：`http://userapi.guopan.cn/gamesdk/init/140514`、
  `http://open.guopan.cn/gamesdk/recommend/140514`、`http://open.guopan.cn/gamesdk/float/…`、
  `http://open.guopan.cn/gamesdk/paycenter/…`、`http://dr.sdk.guopan.cn/xxdatareport.php?platform=android&appid=140514`、
  `http://sapi.guopan.cn/time.php`。
- appId = `140514`，appKey = `WVI2EOLJIW5YEE1Z`。
- 签名盐：`#%$*)&*M<><vance`。
- 账号身份三元组（设备 `SuperSDK.xml` 的 base64 JSON）：
  `{"OpenId":"1084D65F5A7FCB599158","ChannelOpenId":"C654F5A7FCB599158","Token":"abf6839f913043b8813f863bdee6976c51084"}`
- 登录流程：先取 **salt**（错误码 `ELogin_RequestSaltOK`）→ `signMD5(密码, salt)` → 登录 → `loginKey`。
  协议命令名形如 `SUBCMD_ACCOUNT_*REQ/RES`（二进制 subcmd，不是 REST 路径）。
- 游戏的 pfId 与 SDK 的 OpenId **不同**（20 位 hex，差两位）：
  `ewanqf:1084D654F5A7FB599158` vs SDK `OpenId=1084D65F5A7FCB599158`
  → 游戏服**另外分配**了一个 per-game id（对应 `SUBCMD_ACCOUNT_LOGINBETWEENAPPREQ`，参数含 OpenId/Token/appid）。**这段映射必须攻克**。

### 2.2 加密层
- `libEncryptorP.so` 75,744 B，**stripped arm64**，只导出 `JNI_OnLoad`，内部动态注册 native 方法 **`ttEncrypt`**。
- **已确认含 AES 实现**：文件内 **AES 逆 S-box @ 0xf650**、**AES rcon @ 0xcf6b**（正 S-box 未按连续 16 字节命中，可能运行时生成）。
- 载荷格式 **GPXX Proto**（`com.GPXX.Proto.*`，**2357 个类且类名全混淆**，但 **proto 字段名是明文**）：
  `account / userName / username / password / passwd / salt / loginType / appId / appKey / appid /
   appkey / sign / timestamp / timeStamp / imei / oaid / vaid / aaid / fdid / platform /
   sdkVersion / openId / token / uid / cmd / subcmd / phone / mobile`
- SDK 整体重度混淆（`com.flamingo.sdk.*`、`com.flamingo.sdk.m6.*` 等），但**字符串常量大多可读**。

### 2.3 pcap 解析
抓包是 Linux SLL2（linktype **276**），TCP 重组后按 HTTP 解析即可。
参考实现：`/tmp/cokccbi/pcap_sfs.py`（若已被清理，用 `python3 -c "import scapy"` 或自己写 TCP 重组亦可）。
**两个样本**：
- `capture_phone_gcsdk.pcap`：真机一次完整 SDK 交互，含一个 704B 请求 + 476B 响应（`/gamesdk/140514`）。
- `capture_emulator_login.pcap`：模拟器上用**假账号** `gptest001` 的一次登录尝试，448B 请求 + 244B 响应。

### 2.4 免 root / 官方通道：都别试了（已证伪，别浪费时间）
- `device.bind.info` / `device.bind.export` / `user.bind` → 服务端**整体关闭**，任何参数都回 `E000000`。
- 无 root 读 `/data/data/<包>/shared_prefs` → Permission denied；`run-as` → not debuggable。
  （"免 root"这条路已经排除，本任务不必再考虑。）

## 3. 执行顺序（**严格按这个顺序，不要一上来就啃 .so**）

### Phase 0 — 解包与索引（~0.5h）
```bash
mkdir -p /tmp/gp && cd /tmp/gp
unzip -o /Users/a1234/workspace/me/cok/COK-CN1-analysis/protocol/evidence/chanlogin/gp_sdk_plugin_5_5_4_3.apk -d gp_plugin/
ls gp_plugin/*.dex gp_plugin/lib/arm64-v8a/
python3 /Users/a1234/workspace/me/cok/COK-CN1-analysis/scripts/dexdis.py gp_plugin/classes.dex --xref "signMD5|salt|loginKey|login" | head -200
```
产出：登录相关的类/方法清单（谁算密码哈希、谁取 salt、谁组装请求、token 存在哪）。

### Phase 1 — 用 frida 抓 GPXX 明文（~2-4h，**最高性价比**）
目的：**绕开 GPXX 格式逆向**，直接看到明文长什么样。
1. 本机有安卓模拟器 AVD `medium_phone`（Android 16 / arm64），
   系统镜像在 `/opt/homebrew/share/android-commandlinetools/system-images/android-36/default/arm64-v8a/`；
   启动：`~/Library/Android/sdk/emulator/emulator -avd medium_phone -no-window -no-audio -no-snapshot -gpu swiftshader_indirect -no-boot-anim &`
   然后 `adb -s emulator-5554 root`（模拟器支持 root）。
2. 果盘游戏包（宿主 App）从真机拉过：`pm path com.hcg.cok.ewanqf.guopan` → pull base.apk → 装到模拟器。
3. 装 frida-server（arm64）到模拟器，attach 游戏进程。
4. hook `libEncryptorP.so` 的 `ttEncrypt`（**动态注册**）：
   - 搜索字符串 `ttEncrypt` 的引用点找到 `RegisterNatives` 调用，拿到 `{name, signature, fnPtr}`；
   - hook 该 fnPtr，抓**入参（明文指针+长度）**与**返回值（密文）**。
5. 在模拟器上用 adb 自动化走一次登录 UI（控件 resource-id）：
   `view_login_user_name` / `view_login_password` / `view_protocol_checkbox` / `view_login_btn_login`
   （`protocol/cok_emu_login.py` 里有可复用的 `dump_ui()` / `tap()` / `input text` 实现）。
6. 抓到 **≥2 组 (明文, 密文)**，明文里应能看到账号明文、salt、密码哈希、sign 等。

**验收**：明文可读，能看出登录请求包含哪些字段、密码哈希怎么算。

### Phase 2 — 判定加密算法并用 Python 复现（~1-2h）
1. 密文长度 vs 明文长度 → 流式(XOR) 还是 +16 对齐(AES)。
2. 同一账号连抓两次（salt/时间戳不同 → 明文不同）：密文相同 ⇒ ECB；不同 ⇒ CBC/CTR。
3. 已知含 AES → 优先试 **AES-ECB / AES-CBC**。
4. 找 key：从 `.rodata/.data` 里筛 16/24/32 字节高熵常量；候选派生源包括
   `appKey=WVI2EOLJIW5YEE1Z` 的 MD5/AES 派生、appId+固定串、固定常量表。
   可用 `readelf -x .rodata`、Ghidra（工程在 `COK-CN1-analysis/ghidra-project/`，针对 libgame.so；对 libEncryptorP.so 需新开工程）。
5. **判定**：用候选 key/IV 重算密文，与抓包逐字节一致 ⇒ 成功。

**验收**：Python 能对任意明文算出与 SDK 完全一致的密文。

### Phase 3 — 复刻 salt 请求 + 登录请求（~2-4h）
1. 按 Phase 1 的明文实现：`signMD5(密码, salt)` 的**确切拼接顺序**（从明文对照反推，别猜）；
   `sign` 的字段集合与排序规则。
2. 写 Python 客户端：取 salt → 登录 → 解出 {uid, token, loginKey}。
3. 先用**假账号**验证：应返回业务错误（账号不存在），而不是协议错误。

### Phase 4 — 复刻 `LOGINBETWEENAPP`，拿 per-game id（~1-3h）
1. 找到"用 SDK 账号换游戏 uid"的请求（参数含 OpenId/Token/appid）。
2. 调它得到 per-game id → `pfId = "ewanqf:<id>"`。
3. 弄清 `ewanqf:1084D654F5A7FB599158` 与 `OpenId=1084D65F5A7FCB599158` 的映射关系。

### Phase 5 — 端到端（~1-2h）
产出脚本 `protocol/cok_channel_login.py`：
```bash
python3 protocol/cok_channel_login.py --account <果盘号> --password <密码>
```
输出 dict：`pfId / pf / gameUid / uuid`（+ 可选 platformToken 等），并可选直接入库：
```python
import cok_accounts
cok_accounts.save_account(acc, owner="<用户名>")   # pf 用 probe_pf() 实测确定
```

## 4. 验收标准（全部满足才算完成）
1. 脚本在**无 Android 设备、无 root、纯 PC** 跑通：账号密码 → 输出 §5 那组字段。
2. 输出能用游戏服客户端登录成功：
   ```bash
   python3 - <<'EOF'
   import sys; sys.path.insert(0,'protocol')
   from cok_client import CokClient, load_account
   acc = load_account('<凭据.json>')
   c = CokClient(account=acc); c.connect(); c.bin_handshake(); c.login()   # 期望: 登录成功 id=...
   EOF
   ```
3. **至少两个不同账号**都通过（避免把个案当协议）。
4. 交付物：`protocol/cok_channel_login.py` + 一段话说明（怎么用、依赖什么、已知限制）+
   把新发现（算法、密钥来源、字段、映射规则）补写进 `protocol/RE-渠道登录逆向方案.md` 的"实测数据"一节。

## 5. 输出字段格式
```python
{
  "pfId":    "ewanqf:<perGameId>",   # 必需 —— 游戏服认它
  "pf":      "cn_ewanqf",            # 必需 —— 服务端会校验
  "gameUid": "<gameUid>",             # 必需
  "uuid":    "cok<32hex>",            # 必需
  "platformToken": "<可选>",          # 服务端不校验
  "signCode": "<可选>",               # 服务端不校验
  "deviceId": "<可选>",               # 服务端不校验
  "openId": "<SDK uid>", "token": "<SDK token>", "loginKey": "<SDK loginKey>"
}
```

## 6. 约束（务必遵守）
- **不要改动** `protocol/cok_client.py` / `cok_accounts.py` / `cok_emu_login.py` 的既有行为；
  新代码放新文件，需要小改就单独说明。
- **不要动**真实账号：`protocol/accounts/*.json` 里的三个号（<uid-main> / <uid-guopan> /
  <uid-guopan-intl>）是用户的真号，任何会踢掉它们的登录操作都要先确认。
- **不要**把凭据、token、密码写进 git 或提交（本仓库 `.gitignore` 已排除 `accounts/`）。
- **不要**在真机上做实验（用户手机不在手边）；用模拟器。
- 拿不到真实果盘账号时，**先做到"协议正确"**（假号返回业务错即可），并在报告里说明"成功路径未验证"。
- 卡住就**记录卡在哪一步 + 已排除的可能**，不要空转；兜底方案（模拟器发卡机）已经可用。

## 7. 汇报要求
最终回复请包含：
1. **结论**：能不能纯 PC 复刻？成功/部分成功/失败（失败在哪一步）。
2. **算法**：加密方式（mode/IV/key 来源）、密码哈希公式、sign 规则。
3. **产物**：文件路径 + 用法 + 验证输出。
4. **新发现**：任何与本提示词里"已知事实"不符的地方（以实测为准，**如果发现已知事实是错的，明确指出并给出证据**）。

====

## 附：给执行者的快速索引（路径速查）

| 用途 | 路径 |
|---|---|
| 仓库根 | `/Users/a1234/workspace/me/cok/COK-CN1-analysis/` |
| 详细方案 | `protocol/RE-渠道登录逆向方案.md` |
| 素材 | `protocol/evidence/chanlogin/` |
| dex 反汇编器 | `scripts/dexdis.py` |
| 游戏服客户端 | `protocol/cok_client.py` |
| 账号库 / pf 探测 | `protocol/cok_accounts.py`（`probe_pf()`） |
| 模拟器发卡机（兜底） | `protocol/cok_emu_login.py` |
| 协议总报告 | `protocol/COK-游戏服协议实测报告.md` §8.1.7 |
| 模拟器 | `~/Library/Android/sdk/emulator/emulator -avd medium_phone -no-window …` |
| adb | `~/Library/Android/sdk/platform-tools/adb` |
