# 小七(x7sy)渠道登录逆向笔记

> 对应果盘那篇 `RE-渠道登录逆向方案.md`。这份记的是**小七渠道**的实测结论。
> 采集时间 2026-11-12/13，真机 PHK110(Android 16, root) + 模拟器无关。
> 原始素材在 `reverse/evidence/x7sy/`，抓包脚本 `frida/capture_x7_login.js`。

## 0. 一句话结论

小七 COK 渠道包 `com.hcg.cok.ewanqf.x7sy` 的**游戏账号不是小七账号**，
而是海尔 eWan(果盘同族)账号 —— 游戏里的平台身份是
`pfId = ewanqf:<eWan openid>`，pf 仍然是 `cn_ewanqf`。
小七平台账号(`x7_cs_member_*`)只负责**换取**这个 eWan 账号。

```
小七平台账号(邮箱/手机 + 密码)
   │  ① 小七平台登录  user.x7sy.com  (XNetDealer: 自研 native + AES)
   ▼
小七 token / guid
   │  ② SuperSDK 账号转换  loginsupersdk.gzxian.com/superv300ppt
   │     (AES/ECB/PKCS5 + RSA sign, appid=10710 cooperationid=1230)
   ▼
eWan openid + token
   │  ③ 游戏 pfId = ewanqf:<openid>   pf = cn_ewanqf
   ▼
④ 游戏服 getserverlist.php 按 pfId 解析角色 -> gameUid/uuid/区服/buildCode
```

③④ 与果盘完全一致(代码复用)；**要新做的是 ①②**。

## 1. 包与素材

| 东西 | 位置 |
|---|---|
| 小七平台 App | `com.smwl.x7market` v6.94.0.10009 (网易 NIS 加固) |
| 小七 COK 渠道包 | `com.hcg.cok.ewanqf.x7sy` v12.08.0 (**未加固**，11 个 dex) |
| 渠道包从哪来 | 手机上 `/sdcard/Android/data/com.smwl.x7market/apk/com.hcg.cok.ewanqf.x7sy.apk` (小七平台下载目录) |
| 工作副本 | `reverse/work/x7sy/cok_x7sy.apk` (gitignored) |

包内关键件：

| 路径 | 作用 |
|---|---|
| `classes8.dex` | `cn.ewan.supersdk.*` (eWan SuperSDK，**方法体在爱加密 native 里**，见 `NCall.IL`) |
| `classes10/11.dex` | `com.smwl.smsdk.*` + `com.smwl.base.x7http.*` + `com.smwl.x7enc.XNetDealer` |
| `classes.dex` | `com.xmgame.sdk.*`(U8SDK/EWanUser/EWanPay 插件) |
| `lib/arm64-v8a/libx7NativeEncrypt.so` | 小七自研加密壳(252KB)，内部调 `javax.crypto.Cipher` 做 AES |
| `assets/xmgame_developer_config.properties` | `EW_APPID=10710` `EW_SIGN_KEY=eUFL7lOyguzYA3cr` `EW_PACK_ID=125405` `XMGame_Channel=89226` `XMGame_APPID=978346284672876544` `XMGame_APPKEY=65a0501e…` `XMGameSERVER_URL=https://u8sdk.publish.migames.com/u8server/` |
| `assets/xmgame_plugin_config.xml` | `<plugin name="com.xmgame.sdk.EWanUser" type="1"/>` (登录) `<plugin name="com.xmgame.sdk.EWanPay" type="2"/>` (支付) |
| `assets/x7PluginConfig.properties` | `sdkChannel=0` `x7VersionForCN=8.70.0` `x7GamePackTaskId=205160` |

⚠ 果盘包与小七包的 `xmgame_developer_config.properties` **完全一样** ——
说明 ELEX 国服底包共用 eWan 账号体系，渠道差异只在 SDK 层。

## 2. 设备上的凭据落点(root 可读)

| 文件 | 字段 |
|---|---|
| `shared_prefs/wk_account_config.xml` | `wk_UID = x7_cs_member_21921411`、`wk_Token = 86610102593f867776ff244e70b8bba5` |
| `shared_prefs/Cocos2dxPrefsFile.xml` | `last_platformUID = ewanqf:1230144206527`、`account_uuid = cokb3d9731a4353807a6e7c422e07059224`、`game_uid = 205603687002224`、`theSignCode = b59b27917b9434f54a4106fbff208fce`、`server_id = 2224` |
| `shared_prefs/COK_GAMEUID.xml` | `GAMEUID = 205603687002224` |
| `shared_prefs/unionsdk.xml` | `core_data` = base64(Java 序列化的 SuperSDK GlobalData) |
| `shared_prefs/ShadowPlugin_appPlugin_config.xml` | `present_login_way = login_way_apk_temp_jwt`、`sp_presentlogin_guid = 144206527`、`device_channel = 38256` |

`unionsdk.xml` 的 `core_data` 解开是 SuperSDK 的 GlobalData，字段：

```
xp  = https://duoinitsupersdk.ewan.cn/superv300          (初始化)
pt  = https://loginsupersdk.gzxian.com/superv300ppt      (登录/账号)
hp  = https://paycallbacks.supersdk.ewan.cn/callback/1230_10710
t   = cwQ52wanEJkW56Xc        ← AES 密钥(见 §4)
qw  = eUFL7lOyguzYA3cr        ← 签名盐(= EW_SIGN_KEY)
zs  = MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDdhZ6…   ← RSA 公钥(证书)
uy  = 1230144206527           ← eWan openid
px  = 1794479209029           ← 时间戳
ut / on / ql / hl / xf / bs   ← 设备与渠道 id
```

## 3. SuperSDK 请求格式(已实测解出明文)

请求体 = **表单编码**，整体用 **AES/ECB/PKCS5Padding** 加密(key 见 §4)，
密文 hex 上行。实测样例(apiver=200 = 初始化/校验)：

```
apiver=200&appid=10710&appname=列王的纷争&appversion=12.08.0&appversioncode=1901
&channeluid=144206527&connecttype=WiFi&cooperationid=1230&devicecode=2ce61978ad20ffd3
&imei=0&imsi=0&iosflag=0&language=2&mac=02%3A00%3A00%3A00%3A00%3A00&model=OnePlus+PHK110
&oaid=98EC29…&openid=1230144206527&packetid=172550&packetname=com.hcg.cok.ewanqf.x7sy
&pf=1&plat=1&protocol=191210&resolution=1240*2772&sdkversionid=522&sysversion=16
&sysversioncode=36&targetsdkversion=28&token=1794479209029&tpsdkvid=522&tpsdkvname=5.2.2
&uniid=01da64766f81ee6c&visitor=0
```

- `appid=10710` = `EW_APPID`；`cooperationid=1230`；`packetname` = 渠道包名
- `pf=1` `plat=1`；`protocol=191210`(初始化) / `191209`(另一类)
- `token` 这里放的是时间戳(px)，登录后才是真 token

## 4. 加密方案(已逐字节验证)

| 用途 | key(ASCII 16 位) | 模式 |
|---|---|---|
| SuperSDK 请求 | `cwQ52wanEJkW56Xc` | AES/ECB/PKCS5Padding |
| 埋点 involvement | `WTJkNmdoVGY1aElm` | AES/ECB/PKCS5Padding |
| 埋点 heartbeat | `c2FWU0RndHNkcmVh` | AES/ECB/PKCS5Padding |

- key **就是配置里那串 16 位字符串本身**(看着像 base64，但**不是** base64 解码后当 key，
  也不是 MD5/SHA 派生 —— 实测过 md5/sha256 都对不上)
- IV 捕获到过 `6rfcqu6ffqinqlqh`，但 **ECB 下用不上**
- `libx7NativeEncrypt.so` 本身不做加密，它只是调 `javax.crypto.Cipher`
  (字符串 `AES/CBC/PKCS5Padding` + `SecretKeySpec`/`IvParameterSpec` 都在里面)，
  真正的 key 派生在 native 里 —— 所以**用 frida 抓 Cipher/SecretKeySpec 比逆 .so 省事得多**

## 5. 抓包方法(踩过的坑都记这儿)

**frida 的 Java bridge 不是 agent 自带的**，而是 frida-tools 宿主按需回灌的：
脚本访问 `Java` → 发 `{"type":"frida:load-bridge"}` → 宿主把
`frida_tools/bridges/java.js` post 回来求值。
自己用 Python API 驱动时没人回灌 ⇒ `ReferenceError: 'Java' is not defined`
（frida CLI 默认能工作就是因为它实现了这个协议）。

⇒ `frida/frida_capture.py` 已加 `preload_bridge()`：把 `bridges/java.js`
前置进脚本并 `Object.defineProperty(globalThis,'Java',{value:bridge})`。

其它坑：

- `send('type', {...})` 第一个参数是**消息类型**，不是 payload ——
  正确写法是 `send(payload)`；写错报 `unsupported data value`
- 自定义 helper 不要叫 `send`
- frida 17 的 `Module.findExportByName` 已移除 → 用 `Module.getGlobalExportByName`
  / `Process.getModuleByName(x).getExportByName(y)`
- Android 16 上 `RegisterNatives` **不导出**(`libart.so` 里也查不到)，
  但 **Java bridge 可以直接 hook native 方法**(`Java.use(...).method.implementation=…`)，
  所以 `XNetDealer.encryptNative` / `getResultNative` / `getUrlNative` 能直接拿到明文
- frida-server 会被 app 重启/系统清理带走 —— 挂了之后要重新
  `adb shell "su -c 'nohup /data/local/tmp/frida-server >/dev/null 2>&1 &'"`

钩子清单见 `frida/capture_x7_login.js`：XNetDealer(Java+native)、Cipher、
SecretKeySpec、IvParameterSpec、MessageDigest(抓密码哈希)、okhttp Request、
SuperSDK 的 `cn.ewan.supersdk.a.v` 全部方法、SuperLogin getters。

## 6. 登录 UI 在哪

- 游戏里点登录 → `com.smwl.smsdk.login.AuthorizedLoginActivity`（**在游戏进程里**，
  WebView + ShadowPlugin 插件）→ 会拉起**小七平台 App** 的
  `com.smwl.x7market/.activity.my.PasswordManageAct` 等页面（**跨进程 AIDL**：
  `com.smwl.aidl.IAppAuxiliaryCallback` / `IPackageAuxiliaryCallback`）
- 游戏端当前是 **免密登录**：`present_login_way = login_way_apk_temp_jwt`
  —— 游戏向平台 App 要一个临时 JWT，所以游戏里看不到密码框
- 账号密码只在小七平台 App 的登录页输

## 7. 还差什么

**只差"带密码的一次登录"**：要在小七平台 App 里退出登录、用账号密码登一次，
才能抓到 ① 小七平台登录请求(明文 JSON + AES key/IV + URL) 与
② SuperSDK 账号转换请求。抓完就能在纯 PC 复刻。

## 8. 代码侧

- 渠道档案/调度: `cok/core/cok_channels.py`(profile 表) + `cok/core/cok_channel_login.py`
  的 `login()/list_channels()/build_account()` 统一入口
- 小七协议模块(待写): `cok/core/cok_channel_x7sy.py`
  —— 实现 `channel_login()` / `list_identities()` / `build_account()`
