# COK-CN1 APK 静态逆向报告

> 生成时间:2026-10-21 · 工具:REA (rea-agents 6.5.0) · 引擎:jadx-headless-mcp 0.7.1 / apktool 3.0.3
> 分析模式:纯静态,APK 从未被执行

---

## 1. 制品身份

| 项 | 值 |
|---|---|
| 文件 | `5396(12.06.0)-COK_CN1--20260923-1727-10.apk` (380 MB) |
| SHA-256 | `067ffa43e000e51d3eea060b5460fbead45d90cf6e63286071232e349a37c399` |
| 包名 | `com.hcg.cok.cn1` |
| versionName / versionCode | `12.06.0` / `5396` |
| minSdk / targetSdk / compileSdk | 16 / 28 / 35 |
| 类数 / 资源数 | 10715 / 26579 |
| DEX | classes.dex, classes2.dex, classes3.dex (共 3 个) |
| 签名 | **未验证**(REA 未做签名校验) |

---

## 2. 架构结论(重要)

**聊天/游戏后端不是 REST,是 WebSocket + JSON 命令协议。**

- 传输层:`org.WsClient` + TooTallNate Java-WebSocket + okhttp3 WebSocket
- 协议层:`sfs2x.*`(SmartFoxServer 2X 多服游戏协议客户端) + 自有 `push.*` / `roomgroup.*` / `history.*` 命令
- 配置下发:走 HTTPS(`api-config.*` / `cok-chat.elex.com:9443/api/v1`)
- 消息解析:`parseMsgItem` / `parseUserMsgItem` / `parseAttachment`(JSON → `MsgItem`)

所以「API」在这里 = **WebSocket 命令字**,不是 HTTP 路径。

---

## 3. 硬编码服务端地址

### 3.1 聊天 / 配置(CN)

```
https://cok-chat.elex.com:9443/api/v1
https://cok-chat.elex.com:9443/api/v1global_config
https://api-config.service.cok.chat/api/v1
https://api-config.service.cok.chat/api/v1global_config
https://api-config.middle.elexapp.com/api/v1
https://api-config.middle.elexapp.com/api/v1global_config
gcdn.servers.cok.chat                 ← WebSocket 服务器列表下发域
```

### 3.2 账号 / 社区

```
https://accountapi1.elexapp.com
https://accountapi1.elexapp.com/services
https://accountapi1.elexapp.com/services/v3/wb/config/10001001
https://accountapi1.elexapp.com/services/v3/wb/like/10001001
https://accountapi1.elexapp.com/services/v3/wb/list/10001001
https://accountapi3.elexapp.com
```

### 3.3 业务 / 资产 / 日志 / 埋点

```
http://collect.service.cok.chat/collect
http://collect.service.cok.chat/collect/history
http://collect.service.cok.chat/collect/tick
https://collect.service.cok.chat/collect        ← /collect 同时存在 http 与 https 两种形式
https://asset.cok.chat/100001/video/presentation/name=COK-AD-02&width=1280&height=720&duration=21.mp4
https://cdn-service.middle.elexapp.com/public/client_log
https://cok.middle.elexapp.com
https://bi-us-app.elexapp.com/client/loading
https://bi-us-app.elexapp.com/client/loadingcn
https://bisdk.elexapp.com/clientloading_switch_android.php
https://bisdk-us.elexapp.com/clientloading_switch_android.php
https://api-survey.elex.com/action/close
http://f.elex.com/forums/1-Clash-of-Kings
http://f.elex.com/game_login.php?username=
http://f.elex.com/game_login.php?lang=
https://f.elex.com/game_login.php?username=     ← 同上,同时有 http/https 两套
```

### 3.4 翻译

```
https://translate.elexapp.com/api/v2
https://translate.elexapp.com/feedback
https://translate.elexapp.com/newTranslate1.php
https://translate.elexapp.com/translate2.php
https://lx3.cok.elexapp.ccgslb.net/newTranslate1.php
http://184.173.82.76/translate/add?sign=f33b1689f9a6532115c201aed977b450&uid=1381424418000001&userLang=en&fromLang=zh-Hans
https://184.173.82.76/translate/add?sign=f33b1689f9a6532115c201aed977b450&uid=1381424418000001&userLang=en&fromLang=zh-Hans
```

> ⚠️ 翻译接口把 `sign` 与 `uid` 直接写死在 URL 里 —— 固定凭据,任何人都能直接调用。

### 3.5 支付

```
https://payapi1.elexapp.com
https://payapi3.elexapp.com
http://121.15.180.66:801/netpayment/BaseHttp.dll?MB_EUserP_PayOK
https://ok.yeepay.com/paymobile/api/pay/request?merchantaccount=%s&encryptkey=%s&data=%s
https://ok.yeepay.com/paymobile/query/pay/success?
http://mobiletest.yeepay.com/paymobile/api/pay/request?merchantaccount=%s&encryptkey=%s&data=%s
http://mobiletest.yeepay.com/paymobile/query/pay/success?
http://shouyin.yeepay.com/nc-cashier-wap/wap/query/result
```

> 易宝(yeePay)同时打通了**生产 `ok.yeepay.com`** 与**沙箱 `mobiletest.yeepay.com`**,沙箱地址打进生产包。
> `121.15.180.66:801` 是裸 IP 的支付回调(`BaseHttp.dll?MB_EUserP_PayOK`),不走域名。

### 3.6 版本检查 / 论坛

```
http://p1cok.elexapp.com/gameservice/api/get_cn_apk_ver.php
https://p1cok.elexapp.com/gameservice/api/get_mi_cn_ver.php
```

> 同一个版本检查服务,两个接口一个用 http 一个用 https。

---

## 4. REST 路径(账号 / 支付 / 认证)

```
/services/v1/user/login/
/services/v1/user/register/
/services/v1/user/token/
/services/v1/user/editpass/
/services/v1/user/addantiaddiction/
/services/v1/verifycode/getcode/
/services/pay/createNewPay
/services/pay/handlePayment
/mobilePush/bindToken
/elva/api/v3.0/crmtoken
/elva/api/v3.0/sdk/getusertoken
/auth/O2/create/codepair
/auth/create/oneTimeCode
/auth/o2/token
/auth/relyingPartyLogout
/api/v1  /api/v1ui  /api/v2  /api/v1global_config
```

---

## 5. WebSocket 协议命令字(DEX 字符串池实测值)

### 推送(服务端 → 客户端)

| 命令 | 含义 |
|---|---|
| `push.chat` | 单聊推送 |
| `push.chat.room` | 房间消息 |
| `push.chat.roomgroup` | 群组消息 |
| `push.chat.user` | 用户维度推送 |
| `push.live.room` | 直播间 |
| `push.player.expression` | 表情 |
| `push.room.change` | 房间状态变更 |

### 客户端 → 服务端

| 命令 | 含义 |
|---|---|
| `user.init` | 初始化用户(登录握手) |
| `login.success` / `login.failed` | 登录结果 |
| `roomgroup.create` | 建群 |
| `roomgroup.invite` | 拉人 |
| `roomgroup.kick` | 踢人 |
| `roomgroup.quit` | 退群 |
| `roomgroup.modifyname` | 改群名 |
| `roomgroup.all` | 群组列表 |
| `room.leave` | 离开房间 |
| `history.roomv2` / `history.roomsv2` | 房间历史消息 |
| `history.users` | 用户历史 |
| `like.add` / `like.del` | 点赞 |
| `record.message` | 消息记录 |
| `server.config` | 服务器配置 |

### 房间 / 频道分组(`GROUP_*`)

```
GROUP_ALLIANCE      GROUP_BATTLE_CHAT     GROUP_BATTLE_CHAT_CAMP
GROUP_CAMP          GROUP_COUNTRY         GROUP_DRAGON_DANMU
GROUP_DRAGON_OBSERVER GROUP_GAME_TEAM      GROUP_LIVE
GROUP_ORIGINAL      GROUP_RANDOM_GLOBAL  GROUP_RANDOM_LOCAL
GROUP_SECT_FORCE
```

### 用户可见的聊天模式(`USER_CHAT_MODE_*`)

`NORMAL` / `NEARBY` / `MOD` / `ALLIANCE_EMAIL` / `DRIFTING_BOTTLE`

---

## 6. 鉴权模型

**配置查询(`BaseConfigImpl.getQueryUrl`):**

```
GET <config-url>?appId=<appId>&userId=<uid>&sign=<sign>&time=<epochMillis>
```

- `sign = getSign(appId, uid, timestamp)`,`BaseConfigImpl.getSign(String,String,String)`
- `Authorization` 由 SDK 自行处理,不在 URL 参数里
- `WebSocketManager.getAppId()` 提供 appId

**WebSocket 服务器发现:**

1. `WebSocketUrlManager.parse(JSONObject)` 解析服务端下发配置
   - 新开关 `ECG_CHANGE_WEBSOCKET_URL_CONFIG_SWITCH` 开启 → `websocket.urlArray`
   - 旧路径 → `url.websocket`
2. `WebSocketUrlManager.select()` 从 `LinkedList` 轮询选取(多节点容灾)
3. `WebSocketManager.WS_SERVER_LIST_URL` / `WS_ALL_SERVER_LIST_URL` 拉取节点列表
4. 节点结构 `StandaloneServerInfo(address, port, protocol)`;带 `delay` / `loss` / `testCount` 测速字段,`testServers()` 选最优节点

**连接管理:** `connect()` / `connect2ws()` / `forceReconnect()` / `checkReconnect()`;`RECONNECT_INTERVAL`、`RECONNECT_MAX_RETRY` 控制重连退避。

---

## 7. 凭据 / 密钥 / AppID(静态可见)

| 类型 | 值 |
|---|---|
| appId | `10001001`(CN1 主用)、`10000360` |
| 高德地图 Key | `36be0233604092feeaf593c856860e99` |
| Branch.io Key | `key_live_knjHdkLtLaoWWChZ9ZmCIgipAAnT53Wn` |
| 40 位 hex 常量(疑似签名/加密密钥,共 7 个) | `a4b7452e2ed8f5f191058ca7bbfd26b0d3214bfc`、`2438bce1ddb7bd026d5ff89f598b3b5e5bb824b3`、`8a3c4b262d721acd49a4bf97d5213199c86fa2b9`、`9b8f518b086098de3d77736f9458a3d2f6f95a37`、`c56fb7d591ba6704df047fd98f535372fea00211`、`cc2751449a350f668590264ed76692694a80308a`、`df6b721c8b4d3b6eb44c861d4415007e5a35fc95` |
| 微信 AppID(11 个) | `wx13ee52a3795c04aa`、`wx18e5b56e133c99a5`、`wx503a55c1e924f85f`、`wx9fdda23457a62fb5`、`wxa4d30f0cfb6521ce`、`wxb8f607f2592a07e5`、`wxcb5a0382c8a0c3a6`、`wxd7cd8ec74fd1f290`、`wxedc6253224f99470`、`wxee86b4ee723cf1a5`、`wxf68615eaffac5e0b` |
| 翻译硬编码凭据 | `http://184.173.82.76/translate/add?sign=f33b1689f9a6532115c201aed977b450&uid=1381424418000001&userLang=en&fromLang=zh-Hans` |
| 测试账号(明文残留) | `f.elex.com/game_login.php?username=ceshi&userid=222&useremail=test@qq.com&accesstoken=b9656cbedd14b59e139bdb14379312f2` |

> ⚠️ 以上均为**客户端硬编码**,不等于服务端当前有效凭据。仅作逆向事实记录。

---

## 8. 应用组件

| 类型 | 值 |
|---|---|
| Application | `com.clash.of.kings.COKApplication` |
| Launcher Activity | `com.clash.of.kings.COK_CN1` |
| Deep Link | `cok://`、`cokBranch://open`、自定义 action `org.hcg.stac.empire.intent.action.IF` |
| 通知组件 | `org.hcg.notifies.{IFJobService, LocalNotificationIntentService, LocalBroadcastReceiver, NotificationReceiver, HFParseCustomReceiver}` |
| 聊天 SDK Activity | `com.elex.chatservice.view.*`(ChatActivity / ChannelListActivity / ForumActivity / MemberSelectorActivity / WriteMailActivity / AllianceShare* / ChatRoomSettingActivity / NearByActivity / EmojSubscribActivity / Recycler*ListActivity / MsgListActivity / BlogActivity / WebViewActivity / DanmuService,约 25 个) |
| FileProvider | `com.hcg.cok.cn1.fileprovider` |
| 安装来源监听 | `com.clash.of.kings.COKInstallReceiver`(INSTALL_REFERRER) |
| 社交 SDK | `com.clash.of.twitter.TwitterReceiver`、微信/微博/Facebook 分享 |
| queries 包可见性 | 微信 `com.tencent.mm`、FB `com.facebook.katana`、微博、VK |
| 其他 | `com.google.android.gcm.*`、百度推送、`com.amazonaws.mobileconnectors.s3.transferutility.TransferService` |

---

## 9. 权限(21 个)

```
INTERNET                     ACCESS_NETWORK_STATE      ACCESS_WIFI_STATE
CHANGE_WIFI_STATE            READ_PHONE_STATE          READ_EXTERNAL_STORAGE
WRITE_EXTERNAL_STORAGE        ACCESS_FINE_LOCATION      READ_LOGS
WRITE_SETTINGS               REQUEST_INSTALL_PACKAGES  VIBRATE
WAKE_LOCK                    POST_NOTIFICATIONS
ACCESS_DEVICE_STATS          com.google.android.providers.gsf.permission.READ_GSERVICES
com.google.android.c2dm.permission.RECEIVE
com.google.android.finsky.permission.BIND_GET_INSTALL_REFERRER_SERVICE
baidu.push.permission.WRITE_PUSHINFOPVIDER.com.hcg.cok.cn1
com.hcg.cok.cn1.permission.C2D_MESSAGE
```

自声明权限 `android.permission.INTERACT_ACROSS_USERS_FULL`(signature 级)。

**安全观察:** `usesCleartextTraffic="true"` + 自定义 `network_security_config`,说明存在明文 HTTP 流量;`READ_LOGS` / `REQUEST_INSTALL_PACKAGES` / `WRITE_SETTINGS` 属高敏感权限。

---

## 10. 内嵌第三方 SDK

| 类别 | SDK |
|---|---|
| 归因/增长 | Branch.io、AppsFlyer(部分键名)、Umeng 友盟、APMPlus 腾讯、Bugly 腾讯、Reyun 热云 |
| 社交 | Facebook SDK + AccountKit、Twitter SDK、微博 SDK、微信 OpenSDK + 微信支付 |
| 客服 | Sobot 智齿、AIHelp(`elex.aihelp.net` / `wss142.aihelp.net`) |
| 推送/IM | 百度推送、Google GCM/FCM、Firebase RTDB、腾讯 IM(`com.tencent.tmgp.cokqq`) |
| 地图 | 高德 AMap(`com.amap.api.v2.apikey`) |
| 支付 | 支付宝、微信支付、PayPal/Braintree、Yeepay、易宝、汇付、红包 |
| 存储/CDN | AWS S3 TransferUtility |
| 网络 | OkHttp3、Apache HttpClient legacy、Netty、Java-WebSocket、SmartFoxServer 2X |
| 其他 | JPush? (未见)、protobuf、fastjson、gson、UniversalImageLoader |

---

## 11. REA 调用记录(可复现)

| 工具 | 用途 | 关键产出 |
|---|---|---|
| `open_binary` | 绑定 APK 制品 | sha256 / format=apk |
| `inspect_android_package` (detail=summary) | 包信息总览 | 包名/SDK/权限/类数/资源数 |
| `decode_android_resources` (include_strings) | apktool 解码 | manifest 文本 + string 资源 |
| `inspect_analysis_view` (kind=android, facet=manifest) | 读解码后 manifest | 4 页(本次读了前 2 页 / 35794 码元) |
| `search_android_classes` | 类名检索 | `Api`/`Host`/`Socket`/`Retrofit`/`Request` |
| `inspect_android_class` | 类结构(方法/字段/内部类) | WebSocketManager 187 方法 / GameHost 134 方法 / ServiceInterface ~250 方法 |
| `inspect_android_method` | 方法体反编译 | `WebSocketUrlManager.parse` / `BaseConfigImpl.getQueryUrl` / `setUrlList` |
| `trace_android_references` | 反向引用追踪 | WebSocketUrlManager→BaseConfigImpl→ConfigV3Impl;WebSocketManager→77 处引用 |

**已知工具边界:** jadx 桥接不支持反汇编静态初始化块(`<clinit>`),报
`Static initializer disassembly requires one exact method: <clinit>()V`。
因此 `WS_SERVER_LIST_URL` / `APP_ID` / 各命令常量的**字面值**改由 DEX 字符串池提取
(自写 `dexstrings.py`,解析 `string_ids` + ULEB128 + MUTF-8)。

---

## 12. 限制与未覆盖

- **纯静态观察,APK 从未执行**;不建立运行时行为
- **签名未验证** —— 包名声明不等于来源可信
- **manifest 只读了 50%**(18000 / 35794 UTF-16 码元),剩余页未展开
- **native 库未逐个分析** — 380 MB APK 内含引擎 .so,游戏主协议很可能在 native 层
- DEX 字符串池提取**不能区分"代码引用"与"仅存在于资源池"**,命中项已尽量结合类归属筛选
- 40 位 hex 常量的**具体用途未确证**(签名密钥?渠道 ID?校验值?),需运行时验证
- `calcSign` / `getAppId` / `getServerList` / `createClient` 的方法体未取到(桥接返回空 body),签名算法未还原

---

## 13. 建议的下一步

1. **补齐 manifest 剩余页** —— `inspect_analysis_view` offset=18000 / 27000
2. **native 层分析** —— 抽 `lib/*/lib*.so` 用 Ghidra 查 `getNativeSourceFolder` / `getNativeFrameFolder` 指向的协议实现,游戏主 API 协议大概率在这
3. **还原签名算法** —— 从 `BaseConfigImpl.getSign` 或 `WebSocketManager.calcSign` 的 smali 入手
4. **抓真实流量对照** —— 静态协议表 + 一次 `pcap` 抓包即可互相校验
5. **第三方端点收敛** —— 列出 `api-config.*` / `cok-chat.*` / `gcdn.servers.*` 的实际下发内容

---

*本报告全部结论来自 REA 静态分析与 DEX 字符串池提取,未运行目标程序。*
