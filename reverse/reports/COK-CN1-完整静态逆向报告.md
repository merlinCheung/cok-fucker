# COK-CN1 APK 完整静态逆向分析报告

> 目标:`5396(12.06.0)-COK_CN1--20260923-1727-10.apk`
> 工具:REA 6.5.0(jadx-headless-mcp 0.7.1 / apktool 3.0.3 / GNU objdump / Ghidra 12.1.4)
> 模式:**纯静态** —— APK 从未被执行
> 产物目录:`~/workspace/me/cok/COK-CN1-analysis/`

---

## 0. 一句话结论

这是一个 **Cocos2d-x + Lua 的 SLG 手游**(海尔 COK,Clash of Kings 中国服)。游戏主协议是 **SmartFoxServer 2X over TCP**,经 JNI 桥接在 `libgame.so`(59MB)里实现;**1063 个协议命令字全部是明文 Lua**,所以这层逻辑没有混淆保护。聊天走 Elex 自研 WebSocket 协议,账号/支付走 REST。原生库含 **BlowFish + AES + CAST** 密码套件。

---

## 1. 制品身份与完整性

| 项 | 值 |
|---|---|
| 文件 | `5396(12.06.0)-COK_CN1--20260923-1727-10.apk` |
| 压缩体积 / 解压体积 | 380 MB / **1326 MB** |
| SHA-256 | `067ffa43e000e51d3eea060b5460fbead45d90cf6e63286071232e349a37c399` |
| 包名 | `com.hcg.cok.cn1` |
| versionName / versionCode | `12.06.0` / `5396` |
| minSdk / targetSdk / compileSdk | 16 / 28 / 35 |
| Lua 资源版本 | `release_12.06.0_11` |
| Lua 脚本 hash | `e39e5eae2273e5417bbc2e11fbf07b26fa597775` |
| 资源 hash | `fb1c28a71715f04e6d98bf25168d8add012bb1f9` |
| 签名 | `META-INF/CERT.RSA` + `CERT.SF` + `MANIFEST.MF`(V1 签名,**未验证**) |
| ZIP 清单 | 26580 文件条目 / 25324 节点 / 26579 边 / **0 完整性矛盾** / `source_complete: true` |

---

## 2. 分层架构(实测)

```
┌─ Java/Kotlin 层 ────────────────────────────────────────┐
│  com.clash.of.kings.*   (98)   应用壳:Application/更新/截图/分享 │
│  org.hcg.IF.*           (101)  IF 框架:Net / Jni / Payment / SDKConfig │
│  org.hcg.stac.empire.*  (55)   STAC Empire:发布渠道/支付/FB 绑定 │
│  org.hcg.notifies.*     (16)   本地通知 / 推送              │
│  org.hcg.util.*         (13)   EncryptUtil / DeviceUtil     │
│  com.elex.*            (2683)  Elex 聊天 SDK + 账号 SDK       │
├─ JNI 桥 ────────────────────────────────────────────────┤
│  org.hcg.IF.Jni (29 方法)  org.hcg.IF.Net (19)  Payment (7)│
│  org.hcg.stac.empire.sns.FBUtil (11)                     │
│  Java_com_elex_chatservice_host_GameHost_* (174)         │
├─ native ────────────────────────────────────────────────┤
│  libgame.so  59 MB   Cocos2d-x 引擎 + SFS 客户端 + 加密    │
├─ Lua 逻辑层 ────────────────────────────────────────────┤
│  assets/lua_static/  11785 个 .lua(明文,未混淆)          │
│  1063 个协议命令字 · 235 个功能模块                        │
└─────────────────────────────────────────────────────────┘
```

**关键判断**:`libgame.so` 是引擎+协议栈,`assets/lua_static` 才是游戏业务逻辑。Lua 是明文 `.lua` 源文件(不是 `.luac`),意味着**游戏协议、请求参数、业务规则全部可读**。

---

## 3. 制品结构(26579 条)

| 顶层 | 条目数 | 解压体积 | 说明 |
|---|---|---|---|
| `assets/` | 23825 | **1180.6 MB** | 游戏资源主体 |
| `res/` | 2521 | 8.4 MB | Android 资源 |
| `lib/` | 11 | 106.0 MB | 原生库 |
| `META-INF/` | 14 | 5.2 MB | 签名 + 构建信息 |
| `org/` `net/` `google/` `kotlin/` `okhttp3/` | 101 | 0.6 MB | 被打进根目录的库资源 |
| 根目录 | 7 | 25.0 MB | 3 个 dex + resources.arsc |

**扩展名分布**:`.lua` 12297 · `.ccbi` 8223(Cocos2d 编译态 UI)· `.plist` 1722 · `.png` 1398 · `.xml` 1161 · `.json` 553 · `.pkm` 508 · `.atlas` 58 · `.ogg` 53 · `.c3b` 18 · `.lua` 脚本另计 11785

**assets 子目录**:`ccbi` 6706 · `particle` 1721 · `hdccbi` 670 · `dresource` 69 · `local` 50 · `localGreen` 48 · `model3d` 42 · `Imperial` 42 · `World` 30 · `Common` 204 · `Paoku` 63 · `lua_static` 22 · `h5` 11 · `video` 2 · `pbs` 2

---

## 4. Native 库清单(11 个 .so)

| 库 | 大小 | ABI | 职责 |
|---|---|---|---|
| **libgame.so** | 59.02 MB | arm64-v8a | Cocos2d-x 引擎 + SmartFoxServer 客户端 + 密码套件 + JNI 实现 |
| libgame.so | 44.95 MB | armeabi-v7a | 同上(32 位) |
| libuptsmaddon.so | 0.74 MB | arm64-v8a | 上报 SDK(国内) |
| libuptsmaddonmi.so | 0.74 MB | arm64-v8a | 上报 SDK(小米) |
| libBugly.so | 0.18 MB | arm64-v8a | 腾讯 Bugly 崩溃 |
| libentryexpro.so | 0.17 MB | arm64-v8a | 启动/退出埋点 |
| libpingpp.so | 0.02 MB | arm64-v8a | Ping++ 支付 |
| libtobEncrypt.so | 0.01 MB | arm64-v8a | TOB 加密 |
| libBugly.so | 0.15 MB | armeabi-v7a | — |
| libpingpp.so | 0.02 MB | armeabi-v7a | — |
| libtobEncrypt.so | 0.01 MB | armeabi-v7a | — |

### 4.1 libgame.so 结构

```
格式      elf64-littleaarch64
入口      0x8ff000
.text     0x0268c68c (40.4 MB)   引擎代码
.rodata   0x002358e5 (2.3 MB)    字符串常量
动态符号  14063 个
JNI 导出  336 个
依赖      libEGL libGLESv1_CM libGLESv2 libOpenSLES libandroid libc libdl liblog libm libstdc++
```

### 4.2 JNI 桥映射(Java → native)

**静态注册(`Java_` 符号,26 个 org.hcg + 1 个 com.clash):**

```
Java_org_hcg_IF_Jni_nativeGetAppId              ← appId 从 native 取
Java_org_hcg_IF_Net_native{AddStringToCCArray, AddStringToCCDictionary,
                            AddByteArrayToCCArray, AddByteArrayToCCDictionary,
                            AddCCObjectToCCArray, AddCCObjectToCCDictionary,
                            CCDictionary, CCArray}
Java_org_hcg_IF_Payment_native{CallPaySuccess, CallPayFailed, GetUserUid,
                               CallSamsungPaySuccess, CallSamsungPayFailed,
                               CallPurchaseHistoryErro, CallSamsungHistoryErro}
Java_org_hcg_stac_empire_sns_FBUtil_native{SetFBUID, SetIsLogin, SetIsFBFan,
                            SetFeedDialogResult, FbDialogResult, SendHeadImgUrl,
                            SendFriendsList, SendInviteFriendsList,
                            SendRequestFriendsList, SetRequestResult}
Java_com_clash_of_PayGoogle_nativeCallPayInfo
Java_com_clash_of_pay_PaySamsung_nativeCallPayInfo
```

**引擎侧(126 个):** `Java_org_cocos2dx_ext_Native_*` —— 含 `BlowFishDecrypt`、`nativeAPKCode`、`nativeAPKpackageName`、`nativeAPPLink`、`nativeAPPLinkSendImmediate`、`MessageCallback`、`DebugTimeBegin/End`

**聊天 SDK 侧(174 个):** `Java_com_elex_chatservice_host_GameHost_*` —— 与 Java 侧 `GameHost` 接口的 134 个方法一一对应

**动态注册(`RegisterNatives`):** `org.hcg.IF.Jni` 中 `relogin` / `finishGame` / `doSetBranch` / `getCredit` / `redeemCredit` / `clipboardGetText` / `nativeGetAppId` 等方法名在 `.rodata` 中出现(注册表),说明走动态绑定

### 4.3 密码套件(libgame.so 内置)

```
AES:   AES_cbc_encrypt  AES_encrypt  AES_decrypt  AES_set_encrypt_key
       AES_set_decrypt_key  AES_wrap_key  AES_unwrap_key
BlowFish: BF_encrypt  BF_decrypt  BF_ecb_encrypt  BF_cbc_encrypt  BF_ofb64_encrypt  BF_cfb64_encrypt
CAST:  CAST_encrypt  CAST_decrypt  CAST_ecb_encrypt  CAST_cbc_encrypt
       CAST_ofb64_encrypt  CAST_cfb64_encrypt
```

JNI 导出里有 `BlowFishDecrypt` —— **游戏主协议有 BlowFish 加解密**。

### 4.4 Native 内的服务端地址(23 个 elex 域 + 10 个裸 IP)

```
cok.elexapp.com          p1cok.elexapp.com       p3cok.elexapp.com
cnac.cok.elexapp.com     cnpay.cok.elexapp.com    dsap1cok.elexapp.com
dsap3cok.elexapp.com     c3cok.elexapp.com        c3cdn.elexapp.com
cokbattle.elexapp.com    hk.cok.elexapp.com       log.cok.elexapp.com
gm.cok.elexapp.com       public.cok.elexapp.com   sid.cok.elexapp.com
tencent.cok.elexapp.com  txaia-cok.elexapp.com    linebak.elexapp.com
cok.elex-tech.com        cok.eleximg.com          cokcn.eleximg.com
bi-us-app.elexapp.com    coktx.elex.com

裸 IP: 169.45.155.123:8080   ← 游戏服 TCP
       169.45.155.123:8081   ← 游戏服 TCP
       169.55.23.180  103.70.29.34  47.92.107.65
       10.1.2.231(内网)  10.1.3.209:8181(内网文档)
```

---

## 5. 游戏主协议:SmartFoxServer 2X

**决定性证据** —— `org.hcg.IF.Net` 的方法签名直接引用 SFS 类型:

```java
sfsObjectToCCDictionary(com.smartfoxserver.v2.entities.data.ISFSObject): long
sfsArrayToCCArray(com.smartfoxserver.v2.entities.data.ISFSArray): long
nativeConnectMode(java.lang.String): void      ← 连接模式
nativeOnResponse(long): void                   ← 响应回调
nativeAppendNetMsgCensus(String, int, boolean) ← 消息统计
transportMailArray(String): void
transportMailInfo(String, int): void
```

Lua 侧连接器 `CommonLib/Network/NetworkConnector.lua`(178 行):

```lua
NetworkConnector = class("NetworkConnector")
NetworkConnector.EventType = {
    CONNECT_SUCCESS=0, CONNECT_FAILED=1, CONNECT_LOST=2,
    LOGIN=3, LOGOUT=4, PUBLIC_MSG=5, EXTENSION_RESPONSE=6, PINGPONG=7, LOGIN_ERROR=8
}
function NetworkConnector:ctor(ip, port)      -- ← TCP 直连
    self.serverController = ServerController:new()   -- native
    self.pingPongInterval = 3    -- 3s 心跳
    self.reconnectDelay = 5      -- 5s 重连
end
function NetworkConnector:login(zone, uid, params)
    self.serverController:login(zone, uid, luaTableToDict(params))
end
function NetworkConnector:sendCmd(cmd, params, callback)
    self.serverController:sendCmd(cmd, dict)  -- cmd + CCDictionary
end
```

**协议形态**:`TCP 长连接` + `cmd 字符串` + `CCDictionary 参数` + `SFSObject/ISFSArray` 响应
**心跳**:3 秒一次,连续 3 次无响应判定断链并重连
**服务器地址来源**:`CCUserDefault` 持久化键 `account_ip`(各玩法模块都会读回 `original_account_ip`),启动时从 `getserverlist.php` / `getserverlist_memoryold.php` 拉取

---

## 6. 游戏协议命令字:1063 个(明文 Lua)

命令定义在 `initWithName("xxx")`,共 **235 个功能模块、1237 处调用点**。完整映射见 `game-protocol-commands-by-module.txt`。

### 6.1 命令数 top 25 模块

| 命令数 | 模块 | 玩法 |
|---|---|---|
| 125 | `game/command` | 通用命令集 |
| 78 | `game/FestivalActivities` | 节日活动 |
| 29 | `game/worldCraft/match` | 旷世(match) |
| 27 | `game/TreasureFam` | 宝藏家族 |
| 26 | `game/SkyBattlefield/SBFCamp/controler` | 天空战场-营地 |
| 24 | `game/NewDragon` | 新龙 |
| 22 | `game/commercialDarts` | 商业飞镖 |
| 22 | `game/SkyBattlefield/SBFMineEscort/controler` | 天空战场-矿洞护送 |
| 22 | `game/SkyBattlefield/SBFEscort/controler` | 天空战场-护送 |
| 21 | `game/hero` | 英雄 |
| 18 | `game/CommonPopup/ChangeServer` | 换服 |
| 17 | `game/revive2` | 复活 |
| 17 | `game/formationTrain/models` | 阵容训练 |
| 14 | `game/TradeCaravan` | 商队 |
| 14 | `game/crossThrone` | 跨服王座 |
| 14 | `game/worldCraft/battle` | 旷世(战斗) |
| 13 | `game/worldCraft/room` | 旷世(房间) |
| 13 | `game/allianceTerritory/civiMiracle` | 联盟领地-文明奇迹 |
| 12 | `game/fightDeath` | 死亡fight |
| 12 | `game/activity/CallOfSoldiresAct` | 士兵召唤活动 |

### 6.2 命令命名风格(三种并存)

```
点分小写:   alliance.hospital.firewounded
           smeltGoods.getView / smeltGoods.unlock
驼峰点分:   AllianceRallyPoint.add
点分驼峰:   Get.King.Present.Info
全大写点分: Get.King.Present.Record
```

### 6.3 样例命令(来自实际源码)

```
smeltGoods.getView / smeltGoods.unlock          炼金
achieve.unlock / achieve.stageReward             成就
al.rank / al.task.get.available / al.invite      联盟
ad.reward                                          广告奖励
alliance.team.ls / alliance.recharge.getRank      联盟捐献
roomgroup.create / .invite / .kick / .quit        群组
```

---

## 7. 聊天协议(Elex ChatService,WebSocket)

### 7.1 传输与命令

`com.elex.chatservice.net.WebSocketManager`(187 方法 / 111 字段),常量值从 DEX 串池提取:

```
推送:  push.chat  push.chat.room  push.chat.roomgroup  push.chat.user
       push.live.room  push.player.expression  push.room.change
房间:  roomgroup.create  .invite  .kick  .quit  .modifyname  .all   room.leave
鉴权:  user.init  login.success  login.failed
历史:  history.roomv2  history.roomsv2  history.users
其它:  like.add  like.del  record.message  server.config
```

### 7.2 频道分组(`GROUP_*`)

```
GROUP_ALLIANCE  GROUP_BATTLE_CHAT  GROUP_BATTLE_CHAT_CAMP  GROUP_CAMP
GROUP_COUNTRY   GROUP_DRAGON_DANMU  GROUP_DRAGON_OBSERVER  GROUP_GAME_TEAM
GROUP_LIVE      GROUP_ORIGINAL  GROUP_RANDOM_GLOBAL  GROUP_RANDOM_LOCAL
GROUP_SECT_FORCE
```

### 7.3 配置查询协议

`BaseConfigImpl.getQueryUrl()`:

```
GET <config-url>?appId=<appId>&userId=<uid>&sign=<sign(appId,uid,ts)>&time=<epochMillis>
```

服务器地址由服务端下发:`WebSocketUrlManager.parse(JSONObject)` 读
`websocket.urlArray`(新)或 `url.websocket`(旧),`select()` 轮询选取。
节点结构 `StandaloneServerInfo(address, port, protocol)`,带 `delay`/`loss`/`testCount` 测速字段。
节点列表域:`gcdn.servers.cok.chat`

### 7.4 Java 侧 API 契约(接口 → 实现)

```
com.elex.ecg.chatui.data.api.BaseApi          (2 方法:init/destroy)
com.elex.ecg.chatui.data.api.ConversationApi   (14 方法)
com.elex.ecg.chatui.data.api.FriendApi
com.elex.ecg.chatui.data.api.GroupApi
com.elex.ecg.chatui.data.api.impl.{Conversation,Friend,Group}ApiImpl
com.elex.chatservice.host.{IHost, GameHost, DummyHost}   GameHost = 134 方法桥
com.elex.chatservice.controller.ServiceInterface           ≈250 方法门面
```

---

## 8. 账号 / 支付 / 第三方(Java 侧)

### 8.1 账号体系

```
com.elex.account.client.activity.LoginActivity
                        .RegisterActivity
                        .ChangePasswordActivity
                        .PhoneLoginActivity
                        .PhoneRegisterActivity
                        .PhoneChangePasswordActivity
                        .AuthenticationActivity   ← 实名认证
REST:  /services/v1/user/{login,register,token,editpass,addantiaddiction}/
       /services/v1/verifycode/getcode/
       /auth/O2/create/codepair  /auth/create/oneTimeCode  /auth/o2/token
       /auth/relyingPartyLogout
       /mobilePush/bindToken
       /elva/api/v3.0/crmtoken  /elva/api/v3.0/sdk/getusertoken
```

### 8.2 支付

```
Java 侧: org.hcg.IF.Payment (7 个 JNI 回调) + com.clash.of.PayGoogle + com.clash.of.pay.PaySamsung
渠道:    支付宝 / 微信支付(Ping++) / PayPal / 易宝(YeePay) / 三星支付 / Google Pay
活动:    com.pingplusplus.android.PaymentActivity
         com.hcg.cok.cn1.wxapi.WXPayEntryActivity (activity-alias)
         com.alipay.sdk.app.{H5PayActivity, PayResultActivity, AlipayResultActivity}
服务器:  payapi1.elexapp.com / payapi3.elexapp.com
         cnpay.cok.elexapp.com:9527
         121.15.180.66:801/netpayment/BaseHttp.dll?MB_EUserP_PayOK   (裸 IP)
```

### 8.3 应用自有类(98 个,`com.clash.of.*`)

```
com.clash.of.kings.COKApplication          Application
com.clash.of.kings.COK_CN1                  Launcher Activity
com.clash.of.kings.UpdateManager             自更新(含 downloadApkThread)
com.clash.of.kings.CheckManager              (org.hcg.IF 侧)
com.clash.of.kings.ParseXmlService
com.clash.of.kings.COKInstallReceiver        INSTALL_REFERRER
com.clash.of.kings.UtilCOKApplication
com.clash.of.screenshot.ScreenShotListenManager   ← 截图监听(MediaContentObserver)
com.clash.of.share.{BaseShare, FacebookShare, IShare}
com.clash.of.publish.PublishImpl
```

### 8.4 org.hcg.IF 框架(101 类)要点

```
org.hcg.IF.IF                 主入口
org.hcg.IF.Jni                Java→native 桥(29 方法)
org.hcg.IF.Net                SFS 协议桥(19 方法)
org.hcg.IF.NetClient / NetClientManager
org.hcg.IF.Payment            支付
org.hcg.IF.SDKConfig
org.hcg.IF.CheckManager       强制更新检查
org.hcg.IF.LanguageAdaptation 多语言
org.hcg.IF.chatservicereflect.ChatServiceJniHandle   聊天 SDK 的 native 回调
org.hcg.IF.jsondeserializer.ChatServiceJsonDeSerializer
org.hcg.IF.crash.CrashReportManager
org.hcg.IF.permission.{PermissionHelper, PermissionSupervisor}
org.hcg.util.EncryptUtil      加密工具
org.hcg.util.DeviceUtil$CMDExecute  ← 执行 shell 命令
org.hcg.util.AOEUtil$MD5
org.hcg.util.Constants$Platform
org.hcg.stac.empire.publish.{AbstractPublishImpl, IPublishChannel}
org.hcg.stac.empire.pay.PayItemData
org.hcg.stac.empire.sns.FBUtil
```

---

## 9. 端点总表

### 9.1 业务域名(全部来自 DEX 串池 / native .rodata,已逐条回验)

```
游戏/配置
  https://cok-chat.elex.com:9443/api/v1
  https://cok-chat.elex.com:9443/api/v1global_config
  https://api-config.service.cok.chat/api/v1[global_config]
  https://api-config.middle.elexapp.com/api/v1[global_config]
  gcdn.servers.cok.chat                          (WS 节点列表)

账号
  https://accountapi1.elexapp.com
  https://accountapi1.elexapp.com/services/v3/wb/{config,like,list}/10001001
  https://accountapi3.elexapp.com

资源/埋点/日志
  https://c3cdn.elexapp.com   https://c3cok.elexapp.com
  https://cdn-service.middle.elexapp.com/public/client_log
  https://log.cok.elexapp.com  https://linebak.elexapp.com
  https://bi-us-app.elexapp.com/client/loading[cn]
  https://public.cok.elexapp.com  https://sid.cok.elexapp.com
  https://dsap1cok.elexapp.com  https://dsap3cok.elexapp.com
  https://hk.cok.elexapp.com  https://gm.cok.elexapp.com
  https://tencent.cok.elexapp.com  https://txaia-cok.elexapp.com
  https://cok.elexapp.com  https://p1cok.elexapp.com  https://p3cok.elexapp.com
  https://cokbattle.elexapp.com  https://cok.eleximg.com  https://cokcn.eleximg.com
  https://cok.elex-tech.com  https://coktx.elex.com

采集
  http://collect.service.cok.chat/collect[|history|/tick]
  https://collect.service.cok.chat/collect
  https://asset.cok.chat/100001/video/presentation/...

翻译
  https://translate.elexapp.com/{api/v2,feedback,newTranslate1.php,translate2.php}
  https://lx3.cok.elexapp.ccgslb.net/newTranslate1.php
  http(s)://184.173.82.76/translate/add?sign=..&uid=..&userLang=en&fromLang=zh-Hans

支付
  https://payapi1.elexapp.com  https://payapi3.elexapp.com
  https://ok.yeepay.com/paymobile/api/pay/request?merchantaccount=%s&encryptkey=%s&data=%s
  https://ok.yeepay.com/paymobile/query/pay/success?
  http://mobiletest.yeepay.com/paymobile/...        (沙箱混进生产包)
  https://shouyin.yeepay.com/nc-cashier-wap/wap/query/result
  http://121.15.180.66:801/netpayment/BaseHttp.dll?MB_EUserP_PayOK

版本 / 社区
  http://p1cok.elexapp.com/gameservice/api/get_cn_apk_ver.php
  https://p1cok.elexapp.com/gameservice/api/get_mi_cn_ver.php
  http(s)://f.elex.com/forums/1-Clash-of-Kings
  http(s)://f.elex.com/game_login.php?username= / ?lang=
  http://cokindex.elex.com
  http://morethan.cc/access/cokindex?uid=..&uuid=..&sig=..&lang=
  https://cokplayer.elexapp.com:8070/sharecode/test?code=
  http(s)://cokplayer-sharecode.elexapp.com/sharecode/common/openlink?activityTag=reward&lang=zh_CN&pf=abc&code=efg
  https://api-survey.elex.com/action/close
  https://bisdk.elexapp.com/clientloading_switch_android.php
  https://bisdk-us.elexapp.com/clientloading_switch_android.php
```

### 9.2 裸 IP

```
169.45.155.123:8080 / :8081    游戏服 TCP
169.55.23.180 / 103.70.29.34 / 47.92.107.65
10.1.2.231 / 10.1.3.209:8181  内网(开发文档)
```

---

## 10. 硬编码凭据(客户端常量)

| 类型 | 值 |
|---|---|
| GMS Games APP_ID | `312229299745` |
| Elex appId | `10001001`(CN1) / `10000360` |
| Branch key | `key_live_knjHdkLtLaoWWChZ9ZmCIgipAAnT53Wn` |
| 高德 AMap key | `36be0233604092feeaf593c856860e99` |
| 40 位 hex(疑似签名/加密密钥,7 个) | `a4b7452e2ed8f5f191058ca7bbfd26b0d3214bfc`、`2438bce1ddb7bd026d5ff89f598b3b5e5bb824b3`、`8a3c4b262d721acd49a4bf97d5213199c86fa2b9`、`9b8f518b086098de3d77736f9458a3d2f6f95a37`、`c56fb7d591ba6704df047fd98f535372fea00211`、`cc2751449a350f668590264ed76692694a80308a`、`df6b721c8b4d3b6eb44c861d4415007e5a35fc95` |
| 微信 AppID(11 个) | `wx13ee52a3795c04aa` `wx18e5b56e133c99a5` `wx503a55c1e924f85f` `wx9fdda23457a62fb5` `wxa4d30f0cfb6521ce` `wxb8f607f2592a07e5` `wxcb5a0382c8a0c3a6` `wxd7cd8ec74fd1f290` `wxedc6253224f99470` `wxee86b4ee723cf1a5` `wxf68615eaffac5e0b` |
| 翻译接口固定凭据 | `184.173.82.76/translate/add?sign=f33b1689f9a6532115c201aed977b450&uid=1381424418000001` |
| 测试账号 | `f.elex.com/game_login.php?username=ceshi&userid=222&useremail=test@qq.com&accesstoken=b9656cbedd14b59e139bdb14379312f2` |

> 均为**客户端硬编码**,不等于服务端当前有效凭据。

---

## 11. 清单与组件(完整 35794 码元已读)

| 类型 | 数量 |
|---|---|
| activity | 69 |
| service | 8 |
| receiver | 10 |
| provider | 6 |
| activity-alias | 1 |
| meta-data | 17 |
| intent-filter | 22 |

**Deep Link scheme**:`cok` · `cokBranch` · `dmmcok` · `amzn` · `fbconnect`

**应用入口**:`com.clash.of.kings.COKApplication` / Launcher `com.clash.of.kings.COK_CN1`

**文件提供方 authority**:`com.hcg.cok.cn1.fileprovider`(FB + 微博共用)· `com.hcg.cok.cn1.wbsdk.fileprovider` · `com.hcg.cok.cn1.sobot_fileprovider` · `com.hcg.cok.cn1.com.liulishuo.okdownload` · `com.hcg.cok.cn1.FacebookInitProvider`

**权限(21)**:INTERNET / ACCESS_NETWORK_STATE / ACCESS_WIFI_STATE / CHANGE_WIFI_STATE / READ_PHONE_STATE / READ_EXTERNAL_STORAGE / WRITE_EXTERNAL_STORAGE / ACCESS_FINE_LOCATION / **READ_LOGS** / **WRITE_SETTINGS** / **REQUEST_INSTALL_PACKAGES** / POST_NOTIFICATIONS / VIBRATE / WAKE_LOCK / ACCESS_DEVICE_STATS / GSF READ_GSERVICES / C2DM RECEIVE / 百度推送 / C2D_MESSAGE / Finsky INSTALL_REFERRER
自声明:`android.permission.INTERACT_ACROSS_USERS_FULL`(signature)

---

## 12. 第三方 SDK 全量

| 类别 | SDK / 类数 |
|---|---|
| 游戏引擎 | Cocos2d-x(`org.cocos2dx` 112) |
| 游戏协议 | SmartFoxServer 2X(`sfs2x.client` 235 / `com.smartfoxserver`)、`org.WsClient`、TooTallNate Java-WebSocket(77) |
| 聊天 | Elex ChatService(`com.elex` 2683 内) |
| 账号 | Elex account client(`com.elex.account.client`) |
| 客服 | AIHelp(`net.aihelp` 1238,`elex.aihelp.net` / `wss142.aihelp.net`)、Sobot 智齿(`com.sobot`) |
| 推送 | 百度推送、GCM/FCM、Firebase RTDB、腾讯 IM(`com.tencent.tmgp.cokqq`)、Amazon SNS(`org.hcg.notifies.AmazonNotificationManager`) |
| 归因 | Branch.io(`io.branch` 190)、Umeng 友盟、APMPlus(`com.bytedance` 102)、AppsFlyer、Bugly 腾讯、Reyun 热云、`fir.im` 蒲公英 |
| 社交 | Facebook SDK + AccountKit(1234)、Twitter、微博 SDK(13.10.5 / build 2310)、微信 OpenSDK |
| 支付 | 支付宝 SDK(251)、微信支付、Ping++、PayPal/Braintree、Yeepay、Samsung Pay、Google Pay |
| 下载 | OkDownload(`com.liulishuo` 142) |
| 后端 BaaS | Parse(`com.parse` 720)、AWS S3 TransferUtility + Cognito |
| 图片/网络 | Glide(`com.bumptech` 631)、OkHttp3、Apache HttpClient legacy、Netty(515)、Fastjson(219)、Gson、protobuf、JDOM |
| 地图 | 高德 AMap |
| 其他 | Amazon Login(`amzn` scheme)、Google Analytics、EasyPermissions、Room、Lifecycle |

---

## 13. REA 调用记录(可复现)

| 工具 | 用途 | 关键产出 |
|---|---|---|
| `open_binary` | 绑定制品 | sha256 / format=apk |
| `inspect_artifact` (summary) | 内容寻址清单 | 26580 条目 / 25324 节点 / **0 完整性矛盾** |
| `extract_artifact` | 全量提取 | **超时**(380MB / 26.5 万条)→ 改定向提取 |
| `inspect_android_package` (summary) | 包信息 | 包名/SDK/权限/类数/资源数 |
| `decode_android_resources` | apktool 解码 | manifest + string 资源 |
| `inspect_analysis_view` (android/manifest) | 读解码后 manifest | **4 页全读,35794/35794, exhausted** |
| `search_android_classes` | 类检索 | Api / Host / Socket / Retrofit / Request / Elex |
| `inspect_android_class` | 类结构 | WebSocketManager 187 / GameHost 134 / ServiceInterface ~250 / Jni 29 / Net 19 |
| `inspect_android_method` | 方法体 | `WebSocketUrlManager.parse`、`BaseConfigImpl.getQueryUrl`、`setUrlList` |
| `trace_android_references` | 反向引用 | WebSocketUrlManager→BaseConfigImpl→ConfigV3Impl;WebSocketManager→77 处 |
| `inspect_with_objdump` (file_headers) | native 头 | libgame.so elf64-littleaarch64 入口 0x8ff000 |

**工具边界(已知)**:
1. jadx 桥接**不支持反汇编 `<clinit>`**(报 `Static initializer disassembly requires one exact method: <clinit>()V`)→ 常量值改从 DEX 串池提取
2. `calcSign` / `getAppId` / `getServerList` / `createClient` 等方法体返回空 body → 签名算法未还原
3. `extract_artifact` 在本机超时 → 定向 `unzip` 替代
4. `close_binary` 会清空 retained evidence → 后续引用需重跑 producer

---

## 14. 安全观察

| # | 发现 | 位置 |
|---|---|---|
| 1 | 翻译接口 `sign`+`uid` 固定写死在 URL | `184.173.82.76/translate/add` |
| 2 | 易宝**沙箱域名** `mobiletest.yeepay.com` 打进生产包 | DEX 串池 |
| 3 | 测试账号 + accesstoken 明文残留 | `f.elex.com/game_login.php?username=ceshi...` |
| 4 | 支付回调走**裸 IP + HTTP** | `121.15.180.66:801/netpayment/BaseHttp.dll` |
| 5 | `usesCleartextTraffic="true"` + 自定义 networkSecurityConfig | AndroidManifest |
| 6 | 敏感权限组合(READ_LOGS + WRITE_SETTINGS + REQUEST_INSTALL_PACKAGES + FINE_LOCATION + PHONE_STATE) | AndroidManifest |
| 7 | 截图监听(MediaContentObserver)常驻 | `com.clash.of.screenshot.ScreenShotListenManager` |
| 8 | 存在执行 shell 命令的工具类 | `org.hcg.util.DeviceUtil$CMDExecute` |
| 9 | 40 位 hex 常量疑似签名/加密密钥,用途未确证 | DEX 串池 |
| 10 | 7 个 40 位 hex + 11 个微信 AppID + 多个三方 key 明文打包 | 资源/串池 |
| 11 | 内网地址与内网文档服务器打进生产包 | `10.1.2.231` / `10.1.3.209:8181` |
| 12 | V1 签名(仅 JAR 签名),无 v2/v3 证据 | `META-INF/CERT.RSA` |

---

## 15. 未覆盖 / 限制

- **纯静态**,APK 从未执行;不建立运行时行为
- **签名未验证** —— 包名声明不等于来源可信
- **未做 Ghidra 深度反编译** libgame.so(40MB .text,336 个 JNI 导出)——本轮只做符号/段/字符串层;`BlowFishDecrypt` 等关键函数体未反编译
- **未解密 .ccbi / .pkm / .c3b** 等编译态资源(8223 + 508 + 18 个)
- **未反编译 Lua** 的具体函数体(仅提取命令字与 URL);Lua 逻辑总量 11785 文件
- **`ServerController` / `ServerController` native 实现**未反编译 —— SFS 封包格式、加密握手仍未还原
- 40 位 hex 常量用途、BlowFish 密钥、`getSign` 算法均未确证
- assets 1.2GB 中仅提取了 `lua_static/` 与顶层配置,其余(粒子/模型/CCBI)未逐一分析

---

## 16. 建议下一步(按性价比排序)

1. **Ghidra 反编译 `libgame.so` 的 `BlowFishDecrypt` 与 SFS 封包函数** —— 拿到游戏主协议握手与加密算法,这是整个逆向的最后一环
2. **反编译 `org.hcg.IF.NetClient` / `NetClientManager`** —— 搞清 HTTP 通道与 SFS 长连接如何分工
3. **解 `ccbi`(Cocos2d UI)** —— 6706 个,能还原完整界面结构与功能入口
4. **抓一次真实流量对照** —— 静态协议表(本报告)+ 一次 pcap 即可互相校验
5. **确认 40 位 hex 的用途** —— 运行时抓一次 `getSign` 入参即可反推

---

## 17. 产物清单

```
~/workspace/me/cok/COK-CN1-analysis/
├── COK-CN1-完整静态逆向报告.md          ← 本文件
├── COK-CN1-静态API分析报告.md           ← API 专项(前一轮)
├── game-protocol-commands.txt           1063 个命令字(纯列表)
├── game-protocol-commands-by-module.txt  1237 处调用 → 235 个模块映射
├── dex-class-census.txt                 21107 个定义类 + 命名空间统计
├── native/
│   ├── hosts-elex.txt                   23 个 elex 域
│   ├── jni-org.hcg.txt                  26 个 org.hcg JNI 符号
│   ├── jni-org.hcg.IF.Jni.txt           Jni 桥方法名
│   └── *.strings.txt                    7 个 .so 的 URL/主机/SHA-256
├── apktool/
│   ├── AndroidManifest.xml              30262 字节,完整解码
│   ├── apktool.yml                      3.0.3 / SDK / 版本
│   ├── res/ assets/ lib/ original/      完整解码产物
└── apk-extract/
    ├── lib/{arm64-v8a,armeabi-v7a}/     11 个 .so 原样
    └── assets/lua_static/               11785 个 .lua
```

---

*本报告全部结论来自 REA 静态分析、GNU objdump/nm 符号分析与自写 DEX 解析器;目标程序从未被执行。*
