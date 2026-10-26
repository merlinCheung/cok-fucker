# COK-CN1 Native 层深度分析(libgame.so)

> 目标:`lib/arm64-v8a/libgame.so` · SHA-256 `3aefc658b6171b1c9193b63dd5d793fef3db18053e20602d70f3ddda83bbed80`
> 方法:GNU objdump / nm 符号分析 + 自写 ELF 常量解析 + Ghidra 12.1.4 headless 反编译
> 前提:**libgame.so 未 strip**,2200+ 个 C++ 符号完整保留,类结构与方法名可直接还原

---

## 1. 结论先行

游戏主协议 = **SmartFoxServer 2X (SFS2X)**,双通道:

- **TCP**(`TCPSocketLayer` / `TCPClientSSL`,含 SSL 变体)—— 登录、房间、指令
- **UDP**(`UDPSocketLayer` / `Bitswarm::UDPManager`)—— 实时移动、位置同步(斗地主类 SLG 的高频状态同步)

加密:**AES-128-CBC**,密钥 **握手时由服务器下发**(`SFSEvent::CRYPTO_INIT`),不硬编码在客户端。
另有一套 **BlowFish** 走 JNI(`Native::BlowFishDecrypt`),与 SFS 主通道是两回事。

---

## 2. 符号概览

| 指标 | 值 |
|---|---|
| ELF 格式 | elf64-littleaarch64,入口 `0x8ff000` |
| `.text` | 40.4 MB |
| `.rodata` | 2.3 MB |
| 动态符号 | 14063(总)/ 14496(条目) |
| JNI 导出 | 336 |
| **SFS2X C++ 符号** | **2296** |
| 依赖 | libEGL libGLESv1_CM libGLESv2 libOpenSLES libandroid libc libdl liblog libm libstdc++ |
| 未 strip | ✅ 全部 C++ 符号可 demangle |

---

## 3. SFS2X 命名空间结构(从符号表还原)

| 命名空间 | 符号数 | 职责 |
|---|---|---|
| `Sfs2X::Entities` | 851 | 领域模型(SFSUser/SFSRoom/SFSBuddy/MMOItem/变量) |
| `Sfs2X::Requests` | 496 | 请求对象(28 个请求类) |
| `Sfs2X::Core` | 285 | 编解码、IO、事件、线程 |
| `Sfs2X::Util` | 188 | ByteArray、LagMonitor、ConfigData、CryptoKey、XMLParser |
| `Sfs2X::Bitswarm` | 179 | 位群协议层(UDP 实时) |
| `Sfs2X::SmartFox` | 104 | 客户端门面 |
| `Sfs2X::Protocol` | 69 | 序列化协议 |
| `Sfs2X::Controllers` | 64 | 业务控制器 |
| `Sfs2X::Logging` / `FSM` / `Exceptions` / `Http` | 60 | 日志/状态机/异常/HTTP |

---

## 4. 协议栈关键类

### 4.1 编解码核心

```cpp
Sfs2X::Core::SFSProtocolCodec          (19 方法)
  ├─ PrepareTCPPacket(IMessage)         ← TCP 封包
  ├─ PrepareUDPPacket(IMessage)         ← UDP 封包
  ├─ OnPacketRead(ISFSObject)           ← 解析
  ├─ OnPacketRead(ByteArray)            ← 解析
  ├─ OnPacketWrite(IMessage)            ← 序列化
  ├─ DispatchRequest(ISFSObject)        ← 请求分发
  └─ 常量: ACTION_ID / CONTROLLER_ID / PARAM_ID / USER_ID / UDP_PACKET_ID
```

### 4.2 封包头 `Sfs2X::Core::PacketHeader`(17 方法)

标志位(每个都有 getter + setter):

| 标志 | 含义 |
|---|---|
| `Encrypted()` | 载荷已 AES 加密 |
| `BlueBoxed()` | 混淆/蓝盒标记 |
| `Compressed()` | 载荷已压缩 |
| `BigSized()` | 长包(超过 2 字节长度字段) |
| `Binary()` | 二进制模式 |
| `ExpectedLength(long)` | 期望载荷长度 |
| `FromBinary(long)` | 从位域构造 |
| `Encode()` | 编码为线格式 |
| `ToString()` | 调试输出 |

`FromBinary` 反汇编显示位域布局:

```
bit3  → +0x0c  Compressed
bit4  → +0x0b  BlueBoxed
bit5  → +0x09
bit6  → +0x0a
+0x08 = 1        (Binary)
+0x00 = -1       (未初始化长度)
```

### 4.3 序列化 `DefaultSFSDataSerializer`(71 方法)

18 种数据类型,每个都有 Bin/BinDecode 对。**类型标签(从 `DecodeObject` 的 switch 直接读出)**:

| 标签 | 类型 | 标签 | 类型 |
|---|---|---|---|
| `0x00` | NULL | `0x09` | BOOL_ARRAY |
| `0x01` | BOOL | `0x0A` | BYTE_ARRAY |
| `0x02` | BYTE | `0x0B` | SHORT_ARRAY |
| `0x03` | SHORT | `0x0C` | INT_ARRAY |
| `0x04` | INT | `0x0D` | LONG_ARRAY |
| `0x05` | LONG | `0x0E` | FLOAT_ARRAY |
| `0x06` | FLOAT | `0x0F` | DOUBLE_ARRAY |
| `0x07` | DOUBLE | `0x10` | UTF_STRING_ARRAY |
| `0x08` | UTF_STRING | `0x14` | TEXT |

`0x11` / `0x12` / `0x13` **未处理** → 落入默认分支,报错
`"Unknow SFSDataType ID: %d"`(注意源码里就是拼错的 "Unknow")。

伪代码形态:

```c
switch ((ulong)local_5c[0]) {          // 读 1 字节类型标签
  case 0:  BinDecode_NULL(buf);          break;
  case 1:  BinDecode_BOOL(buf);          break;
  ...
  case 8:  BinDecode_UTF_STRING(buf);    break;
  ...
  case 0x14: BinDecode_TEXT(buf);        break;
  default:  "Unknow SFSDataType ID: %d";
}
```

→ **载荷 = 1 字节类型标签 + 该类型的数据**,与 4 字节封包头拼接后整体 AES-128-CBC。

### 4.4 事件 `Sfs2X::Core::SFSEvent`(57 个)

```
握手/连接   HANDSHAKE  CONNECTION  CONNECTION_ATTEMPT_HTTP  CONNECTION_LOST
            CONNECTION_RESUME  CONNECTION_RETRY  SFS_SOCKET_ERROR
登录        LOGIN  LOGIN_ERROR  LOGOUT  CRYPTO_INIT  UDP_INIT
房间        ROOM_JOIN  ROOM_JOIN_ERROR  ROOM_ADD  ROOM_REMOVE
            ROOM_NAME_CHANGE  ROOM_CAPACITY_CHANGE  ROOM_PASSWORD_STATE_CHANGE
            ROOM_GROUP_SUBSCRIBE  ROOM_GROUP_UNSUBSCRIBE
            ROOM_VARIABLES_UPDATE  ROOM_FIND_RESULT
用户        USER_ENTER_ROOM  USER_EXIT_ROOM  USER_COUNT_CHANGE
            USER_VARIABLES_UPDATE  USER_FIND_RESULT  PROXIMITY_LIST_UPDATE
消息        PUBLIC_MESSAGE  PRIVATE_MESSAGE  OBJECT_MESSAGE  MODERATOR_MESSAGE
            ADMIN_MESSAGE  EXTENSION_RESPONSE  DEBUG_MESSAGE
其他        PING_PONG  INVITATION  INVITATION_REPLY  PLAYER_TO_SPECTATOR
            SPECTATOR_TO_PLAYER  MMOITEM_VARIABLES_UPDATE
            CONFIG_LOAD_SUCCESS  CONFIG_LOAD_FAILURE
```

### 4.5 请求类(28 个)

```
BaseRequest                 ← 基类:Id / Type / TargetController / IsEncrypted
                             KEY_ERROR_CODE / KEY_ERROR_PARAMS
HandshakeRequest            ← 握手
LoginRequest                ← 登录
                             KEY_USER_NAME / KEY_PASSWORD / KEY_PARAMS / KEY_ROOMLIST
LogoutRequest
PingPongRequest             ← 心跳
GenericMessageRequest       ← 通用消息
                             KEY_MESSAGE / KEY_MESSAGE_TYPE / KEY_RECIPIENT
                             KEY_RECIPIENT_MODE / KEY_ROOM_ID / KEY_SENDER_DATA
                             KEY_USER_ID / KEY_XTRA_PARAMS
ExtensionRequest            ← ★ 游戏自有命令走这里
                             KEY_CMD / KEY_PARAMS / KEY_ROOM
CreateRoomRequest  ChangeRoomNameRequest  ChangeRoomCapacityRequest
ChangeRoomPasswordStateRequest  JoinRoomRequest  SetRoomVariablesRequest
SetUserVariablesRequest  FindRoomsRequest  FindUsersRequest
SubscribeRoomGroupRequest  UnsubscribeRoomGroupRequest
PlayerToSpectatorRequest  SpectatorToPlayerRequest
ManualDisconnectionRequest  RoomSettings  RoomPermissions  RoomEvents
RoomExtension  Buddylist  Game  MMO
```

> **游戏自己的 2158 条命令**(如 `al.rank`、`achieve.find`)走 `ExtensionRequest`:`cmd` + `params`。
> `Sfs2X::Requests::RequestType` 枚举区分请求类型。

---

## 5. 加密层(已确证)

### 5.1 SFS 主通道 = AES-128-CBC

`Sfs2X::Core::DefaultPacketEncrypter`(4 方法)反汇编:

```asm
; Decrypt(ByteArray) @ 0x2a39844
  ldr  x0, [x0, #0x8]
  bl   Sfs2X::Bitswarm::BitSwarmClient::CryptoKey@plt   ; ← 取密钥
  bl   EVP_CIPHER_CTX_new@plt
  bl   EVP_CIPHER_CTX_reset@plt
  bl   EVP_aes_128_cbc@plt                             ; ← AES-128-CBC
  bl   Sfs2X::Util::CryptoKey::Key@plt                 ; ← 16 字节 key
  bl   Sfs2X::Util::CryptoKey::IV@plt                  ; ← 16 字节 IV
  bl   EVP_CipherInit_ex@plt                           ; enc=0 解密
```

`Encrypt(ByteArray)` @ 0x2a38e2c 同构,`enc=1`。

### 5.2 密钥来源 = 服务端下发

```
Sfs2X::Util::CryptoKey::CryptoKey(shared_ptr<ByteArray> key,
                                   shared_ptr<ByteArray> iv)   @ 0x29bc814
  ├─ Key()  @ 0x29bc970  → 返回 [this+0x10] 的 shared_ptr
  └─ IV()   @ 0x29bc944  → 返回 [this+0x18] 的 shared_ptr
```

`Key()`/`IV()` 只是**返回构造时注入的成员**,没有硬编码常量 → 密钥由
`SFSEvent::CRYPTO_INIT` / 握手响应下发,运行时注入 `BitSwarmClient`。

**结论:静态分析拿不到密钥,必须抓一次握手流量。**

### 5.3 BlowFish(独立于 SFS 主通道)

- `Java_org_cocos2dx_ext_Native_BlowFishDecrypt` @ 0x175527c(JNI,薄封装)
- 底层密码套件全量内置:`BF_encrypt/decrypt/ecb/cbc/ofb64/cfb64`、`AES_*`、`CAST_*`
- **`BF_set_key` 只被 `EVP_CIPHER_meth_get_ctrl` 调用** → BlowFish 走 OpenSSL EVP,
  没有直接 `BF_encrypt` 调用点
- 该 JNI 函数内部走 JNI vtable(`[x19+0x558/0x5c0/0x580/0x680]`),**不直接调 BF_***

---

## 6. JNI 桥完整映射

### 6.1 应用层(`org.hcg` / `com.clash` / `com.hcg`)

```
Java_org_hcg_IF_Jni_nativeGetAppId                    ← appId 从 native 取
Java_org_hcg_IF_Net_native{AddStringToCCArray, AddStringToCCDictionary,
                            AddByteArrayToCCArray, AddByteArrayToCCDictionary,
                            AddCCObjectToCCArray, AddCCObjectToCCDictionary,
                            CCDictionary, CCArray}      (9)
Java_org_hcg_IF_Payment_native{CallPaySuccess, CallPayFailed, GetUserUid,
                               CallSamsungPaySuccess, CallSamsungPayFailed,
                               CallPurchaseHistoryErro, CallSamsungHistoryErro}  (7)
Java_org_hcg_stac_empire_sns_FBUtil_native{SetFBUID, SetIsLogin, SetIsFBFan,
                            SetFeedDialogResult, FbDialogResult, SendHeadImgUrl,
                            SendFriendsList, SendInviteFriendsList,
                            SendRequestFriendsList, SetRequestResult}  (10)
Java_com_clash_of_PayGoogle_nativeCallPayInfo
Java_com_clash_of_pay_PaySamsung_nativeCallPayInfo
```

### 6.2 引擎层(`org.cocos2dx`,126 个)

```
Java_org_cocos2dx_ext_Native_BlowFishDecrypt
Java_org_cocos2dx_ext_Native_nativeAPKCode
Java_org_cocos2dx_ext_Native_nativeAPKpackageName
Java_org_cocos2dx_ext_Native_nativeAPPLink
Java_org_cocos2dx_ext_Native_nativeAPPLinkSendImmediate
Java_org_cocos2dx_ext_Native_MessageCallback
Java_org_cocos2dx_ext_Native_DebugTimeBegin / DebugTimeEnd
Java_org_cocos2dx_ext_Native_logOut
```

### 6.3 聊天 SDK 层(174 个)

`Java_com_elex_chatservice_host_GameHost_*` —— 与 Java 侧 `GameHost` 接口的
134 个方法一一对应(createChatRoom / sendChatMessage / banPlayerByIndex / …)。

### 6.4 动态注册(`RegisterNatives`)

`org.hcg.IF.Jni` 中 `relogin` / `finishGame` / `doSetBranch` / `getCredit` /
`redeemCredit` / `clipboardGetText` / `nativeGetAppId` 等方法名在 `.rodata` 中出现
(注册表),走动态绑定而非静态 JNI 符号。

---

## 7. 服务端地址(native `.rodata`)

```
游戏/战斗
  169.45.155.123:8080        ← 游戏服 TCP
  169.45.155.123:8081        ← 游戏服 TCP
  47.92.107.65  169.55.23.180  103.70.29.34

账号/支付
  cnac.cok.elexapp.com       cnpay.cok.elexapp.com:9527
  gm.cok.elexapp.com         hk.cok.elexapp.com
  tencent.cok.elexapp.com    txaia-cok.elexapp.com

CDN/资源
  c3cdn.elexapp.com          c3cok.elexapp.com
  cok.eleximg.com            cokcn.eleximg.com
  cok.elex-tech.com          cok.elexapp.com
  p1cok.elexapp.com          p3cok.elexapp.com
  dsap1cok.elexapp.com       dsap3cok.elexapp.com
  public.cok.elexapp.com     sid.cok.elexapp.com
  linebak.elexapp.com        log.cok.elexapp.com
  bi-us-app.elexapp.com      cokbattle.elexapp.com
  coktx.elex.com
```

SFS 配置:`sfs-config.xml` · `sfsHttp` · `SFSDATATYPE_*`

---

## 8. 命令词表交叉验证

| 来源 | 命令数 | 说明 |
|---|---|---|
| native `.rodata` | 1182 | 服务端完整命令词表 |
| Lua `initWithName()` | 1063 | 客户端实际发起的命令 |
| 交集 | 87 | 两边都有 |
| **并集** | **2158** | **权威服务端命令词表** |

native 独有 1095 条(Lua 未使用但服务端支持),Lua 独有 976 条。
→ 完整词表见 `game-protocol-commands-union.txt`(带来源标记 N/L/B)。

native 独有样例:

```
ability.confirm  ability.random   achieve.find   achieve.ls   achieve.reward
act.ex.flush     act.ex.reward    act.exchange   act.ls       act.popup
al.acceptapply   al.applylist     al.blacklist.query
al.comment.shield.add / .list / .remove
al.donate.res.info  al.get.url   al.invite.move  al.leader.replace
```

---

## 9. Ghidra 反编译

REA 的 provider 有 330 秒硬超时,40MB `.text` 必然超时 → **改为直接用 Ghidra headless**
(不限时),脚本见 `scripts/DecompileTargets.java`,启动器见 `scripts/run-ghidra-decompile.sh`。

```bash
$GHIDRA_INSTALL_DIR/support/analyzeHeadless <proj> COK \
  -import libgame.so -overwrite \
  -postScript scripts/DecompileTargets.java out.c \
    DefaultPacketEncrypter CryptoKey PacketHeader SFSProtocolCodec \
    SFSIOHandler FnHandshake BlowFishDecrypt HandshakeRequest \
    LoginRequest ExtensionRequest GenericMessageRequest \
  -scriptPath scripts
```

**踩到的四个坑(全部已解决)**:

1. **REA 的 provider 超时** — `rea analyze --provider ghidra` 报 `provider_timeout`
   (`details.timeout_ms=330000`,卡在 `list_documents`)。必须绕开 REA 直接调 Ghidra。
2. **Java 脚本不自动编译** — 报 `The class could not be found. It must be the public class
   of the .java file`。必须自己预编译:
   ```bash
   javac -nowarn -cp "$(find $GHIDRA_INSTALL_DIR/Ghidra -name '*.jar' | tr '\n' ':')" \
         -d scripts scripts/DecompileTargets.java
   ```
3. **Ghidra API 变化** — `DecompInterface.setOptions()` 收 `DecompileOptions` 不是 String,
   写字符串编译不过。
4. **别加 `-deleteProject`** — 加了分析完项目被删,伪代码没生成还得重来;而且上一轮残留的
   `COK.lock` 会让下一轮导入卡在项目锁上(看起来像卡死,实则是等锁)。**每轮先清空项目目录**。
   另外后台任务有 1 小时硬上限,长分析要用 `nohup` 脱离任务生命周期。

目标函数:

| 函数 | 地址 | 目的 |
|---|---|---|
| `DefaultPacketEncrypter::Decrypt` | 0x2a39844 | AES-128-CBC 调用链 |
| `DefaultPacketEncrypter::Encrypt` | 0x2a38e2c | 同上 |
| `DefaultPacketEncrypter::CryptoKey` | 0x2a38d7c | 构造 |
| `CryptoKey::Key` / `IV` / `CryptoKey` | 0x29bc970 / 0x29bc944 / 0x29bc814 | 密钥存取 |
| `PacketHeader::FromBinary` / `Encode` | 0x2addfd0 / 0x2ade0b0 | 封包头位域 |
| `SystemController::FnHandshake` | 0x29ed7c8 | 握手 |
| `Native::BlowFishDecrypt` | 0x175527c | JNI 薄封装 |
| `SFSProtocolCodec` / `SFSIOHandler` | 0x2ade0b0 附近 | 编解码与 IO 通路 |

> 产物:`native/libgame-decompiled.c`(29506 行,202 个函数,**158 个拿到真实函数体**),
> 运行日志 `native/ghidra-run.log`,Ghidra 项目保留在 `ghidra-project/`(可 `-process -noanalysis` 复用,秒级)。

### 9.1 Ghidra 反编译实证结果

**⚠️ 第一个坑:这些导出符号是 IFUNC 形式** —— Ghidra 直接反编译符号地址会得到
thunk 桩(`(*(code *)PTR__sym_03bc2870)();`),真实函数体在指针指向处。
脚本必须**跟随指针解引用**再反编译(已实现:`resolveThunk()`)。

#### (a) AES-128-CBC —— 完全确证

`Sfs2X::Core::DefaultPacketEncrypter::Decrypt` @ 0x2a39844 真实伪代码:

```c
EVP_CIPHER_CTX *ctx;
EVP_CIPHER *cipher;

BitSwarmClient::CryptoKey(&local_58, this->client);   // 取密钥对
ctx = EVP_CIPHER_CTX_new();
EVP_CIPHER_CTX_reset(ctx);
cipher = EVP_aes_128_cbc();                            // ★ AES-128-CBC
CryptoKey::Key(&local_a8, local_58);                    // 16 字节 key
ByteArray::Bytes(&local_98, local_a8);
CryptoKey::IV(&local_c8, local_58);                     // 16 字节 IV
ByteArray::Bytes(&local_b8, local_c8);
EVP_CipherInit_ex(ctx, cipher, (ENGINE *)0x0, puVar12, (uchar *)*local_b8, 0);  // 0=解密
EVP_CipherUpdate(ctx, puVar12, &local_cc, in, iVar7);
EVP_CipherFinal_ex(ctx, (uchar *)(*local_88 + local_cc), &local_e4);
EVP_CIPHER_CTX_free(ctx);
```

`Encrypt` 同构,末参 `1`。**未出现 `EVP_CIPHER_CTX_set_padding(ctx, 0)`**
→ 使用 OpenSSL 默认 PKCS#7 padding。

#### (b) 封包头 `PacketHeader::Encode()` @ 0x2ade0b0

```c
uint flags = 0;
if (this[+8]  != 0) flags = 0xFFFFFF80;   // bit31 —— 字节序标志
if (this[+10] != 0) flags |= 0x40;         // bit6
if (this[+9]  != 0) flags |= 0x20;         // bit5
if (this[+11] != 0) flags |= 0x10;         // bit4  BlueBoxed
if (this[+12] != 0) flags |= 0x08;         // bit3  Compressed
return flags;                               // 32 位头字
```

结构体布局:`+0x08` Binary / `+0x09` bit5 / `+0x0A` bit6 / `+0x0B` BlueBoxed /
`+0x0C` Compressed;低位为载荷长度。

#### (c) 收包状态机 `SFSIOHandler`

```
HandleDataSize()        日志: "Data size is %d"
                                  "Handling Header Size. Length: %d (%s)"   ← %s = "big"|"small"
                                  "big" / "small"                          ← 字节序标记
HandleDataSizeFragment() 日志: "DataSize is ready: %d bytes"
                                  "Handling Size fragment. Data: %d"       ← 分片头
HandleNewPacket()        日志: "Handling New Packet of size %d"
HandlePacketData() / WriteTCP() / WriteUDP() / WriteBinaryData(header, data)
```

→ 收包流程:**读 4 字节头 → 解析长度与标志 → 必要时收分片 → 收载荷 → 交给 Codec**。
"big"/"small" 两个字符串直接印证 bit31 是**字节序**标志。

#### (d) 业务命令如何下发

```
ExtensionRequest::Validate()  错误串: "ExtensionCall request error"
                                "Missing extension command"
                                "Missing extension parameters"
LoginRequest::Validate()      错误串: "LoginRequest Error"
                                "Missing Zone name"
                                "You are already logged in. Logout first"
GenericMessageRequest::Validate*()  "PublicMessage request error" / "Request error - "
                                "Public message is empty!" / "You are not joined in the target Room: "
                                "Invalid recipient id" / "Invalid recipient id: "
                                "Private message is empty!" / "Object message is null!"
                                "Buddy message is empty!" / "Moderator message is empty!"
                                "Unsupported message type: "
ThreadManager::EnqueueSend()  参数名: "callback" / "data" / "header"
```

→ 游戏自己的 2158 条命令走 **`ExtensionRequest`**(`cmd` + `params`,缺一即报
"Missing extension command/parameters");`GenericMessageRequest` 负责聊天消息
(public/private/object/buddy/superuser 五种);`LoginRequest` 需要 zone + 凭据。

#### (e) 握手

```
SmartFox::SendHandshakeRequest(bool)
HandshakeRequest::HandshakeRequest(string, string, string)   @ 0x2ac42bc
SystemController::FnHandshake(ulong long, shared_ptr<IMessage>)
```

`FnHandshake` 体内引用的字符串只有 `"message"`,密钥/IV 走二进制字段
→ 与 `CryptoKey` 构造注入的结论一致:**AES 密钥在握手响应里下发**。

#### (f) BlowFish JNI

`Java_org_cocos2dx_ext_Native_BlowFishDecrypt` @ 0x175527c 是 JNI 薄封装,
走 JNIEnv 函数表(`[x19+0x558/0x5c0/0x580/0x680]`),**不直接调 BF_encrypt**;
BlowFish 实际经 OpenSSL EVP(`BF_set_key` 全库仅被 `EVP_CIPHER_meth_get_ctrl` 调用)。

### 9.2 本轮补充的工具经验

- **Ghidra 对 IFUNC 导出符号只出 thunk**,必须跟随 `PTR_..._<hex>` 指针再反编译
- Ghidra 项目**首次分析后务必保留**(`-process -noanalysis` 可秒级复用),
  `-deleteProject` 会让下一轮重跑 20 分钟
- 残留 `COK.lock` 会让下一次导入**静默卡在项目锁上**(看起来像挂死,实则是等锁)→ 每轮先清空项目目录
- 后台任务有 **1 小时硬上限**,长分析必须 `nohup` 脱离任务生命周期
- 定位真实函数体地址用 `nm -D`(未 strip 的导出符号),再按地址反编译

---

## 10. 结论与限制

### 已确证

1. 游戏主协议 = **SFS2X over TCP+UDP**,协议栈完整未混淆,类/方法/字段名全部可读
2. 加密 = **AES-128-CBC**,密钥**握手下发**,静态不可得
3. **2158 条服务端命令**已知(native 词表 ∪ Lua 词表)
4. 封包头 5 个标志位(Encrypted/BlueBoxed/Compressed/BigSized/Binary)已知
5. 18 种 SFS 数据类型已知
6. 57 个客户端事件已知
7. BlowFish 走 OpenSSL EVP,与 SFS 主通道独立

### 限制

- **AES 密钥需抓包**(握手响应),静态分析到此为止
- Ghidra 伪代码产物待自动分析完成后补充
- `Sfs2X::Core::SFSEvent::*` 等常量符号落在 `.bss`(运行时初始化),**无法静态取值**
- 40MB `.text` 的完整反编译未做(只针对关键函数)
- 聊天 WebSocket 的封包格式未分析(在 `com.elex` 侧 Java 层,非 native)

---

*本报告基于 GNU objdump/nm 符号分析 + 自写 ELF 解析器 + Ghidra 12.1.4;目标程序从未被执行。*
