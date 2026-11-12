# COK-CN1 APK 逆向 · 产物索引

> 目标:`5396(12.06.0)-COK_CN1--20260923-1727-10.apk`
> SHA-256 `067ffa43e000e51d3eea060b5460fbead45d90cf6e63286071232e349a37c399` · 380 MB
> 模式:第一轮纯静态(APK 从未执行)+ 第二轮**运行时实测**(设备 OnePlus PHK110 / Android 16 / root)
> 工具:REA 6.5.0(jadx-headless-mcp 0.7.1 / apktool 3.0.3 / GNU objdump / Ghidra 12.1.4) + Frida 17.13.0

---

## 运行时实测(第二轮 · 权威结论)

| 文件 | 内容 |
|---|---|
| `protocol/COK-游戏服协议实测报告.md` | **协议权威报告**:线格式字节级定义、三层加密真相、params XOR 密钥、实测命令清单、直连可行性评估、与静态结论的差异表 |
| `protocol/cok_sfs.py` | 协议库:SFS 编解码 + params XOR 加解密 + 请求组包(`decode` / `xor` / `build`) |
| `protocol/decode_capture.py` | 把 Frida 抓包 JSONL 还原成 SFS 帧并解出 params 明文 |
| `protocol/evidence-sample.txt` | 一次完整会话的解码输出(命令统计 + 逐包明文) |
| `protocol/frida/` | 12 个 hook 脚本 + 驱动(socket / 加密器 / 密钥表 / ART 探针) |
| `protocol/evidence/*.jsonl` | 同会话原始抓包(游戏服字节 + 543 组明/密文对) |

> 关键结论:**协议外壳完全明文**(命令名/字段名可见);只有 `params` 被**32 字节循环 XOR** 混淆,
> 密钥每会话一把、由服务端下发;`libgame.so` 里的 AES-128-CBC SFS SDK 是**死代码**。
> **直连可行,唯一硬门槛是拿到会话密钥(需走完登录/配置握手)。**

---

## 第一轮:静态逆向报告

| 文件 | 内容 |
|---|---|
| `COK-CN1-完整静态逆向报告.md` | **主报告**:分层架构、制品结构、1063 命令、SFS 协议、native 库与 JNI 桥、端点总表、凭据、12 项安全观察、限制与下一步 |
| `COK-CN1-Native层深度分析.md` | **native 专项**:SFS2X 命名空间/类/方法全量、AES-128-CBC 调用链、密钥来源论证、JNI 桥映射、封包头位域、事件与请求清单 |
| `COK-CN1-静态API分析报告.md` | API 专项(第一轮):HTTP 端点、聊天 WebSocket 协议、鉴权模型、凭据 |

## 命令词表

| 文件 | 内容 |
|---|---|
| `game-protocol-commands-union.txt` | **权威命令词表 2158 条**,带来源标记 N(native 独有)/L(Lua 独有)/B(共有) |
| `game-protocol-commands.txt` | Lua `initWithName()` 提取的 1063 条命令字 |
| `game-protocol-commands-by-module.txt` | 1237 处调用点 → 235 个功能模块 → 源文件 完整映射 |

## Native 分析产物

| 文件 | 内容 |
|---|---|
| `native/hosts-elex.txt` | 23 个 elex 业务域名 |
| `native/native-command-strings.txt` | native `.rodata` 的 1182 条命令串 |
| `native/sfs2x-classes.txt` | SFS2X 全部 2296 个符号 demangle + 类结构统计 |
| `native/sfs2x-request-classes.txt` | 28 个 SFS 请求类 |
| `native/jni-org.hcg.txt` | 26 个 org.hcg JNI 符号 |
| `native/jni-org.hcg.IF.Jni.txt` | Jni 桥方法名 |
| `native/libgame-symbols-demangled.txt` | 11767 行全量 demangle 符号表 |
| `native/libgame-decompiled.c` | Ghidra 关键函数伪代码(自动分析完成后生成) |
| `native/*.strings.txt` | 7 个 .so 的 SHA-256 / URL / 主机 / 字符串 |

## 解码产物

| 目录 | 内容 |
|---|---|
| `apktool/` | apktool 3.0.3 完整解码:`AndroidManifest.xml`(30262 B)/ `apktool.yml` / `res/` / `assets/` / `lib/` / `original/` |
| `apk-extract/lib/` | 11 个 .so 原样(arm64-v8a + armeabi-v7a) |
| `apk-extract/assets/lua_static/` | 11785 个明文 .lua 游戏逻辑 |

## 类清单

| 文件 | 内容 |
|---|---|
| `dex-class-census.txt` | 21107 个定义类(从 DEX class_defs 精确解析)+ 命名空间统计 |

## 脚本(可复现)

| 文件 | 用途 |
|---|---|
| `scripts/DecompileTargets.java` | Ghidra headless 脚本:批量反编译指定函数 |
| `scripts/elfstrings.py` | ELF 段/节解析 + 符号表提取 + 字符串值解析 |
| `scripts/dexstrings.py` | DEX 字符串池解析(URL / 常量提取) |
| `scripts/dexclasses.py` | DEX class_defs 解析(类清单) |

---

## 关键结论速查

```
架构      Cocos2d-x + Lua SLG(海尔 COK 中国服)
主协议    SmartFoxServer 2X over TCP+UDP(协议栈未混淆,符号全保留)
游戏服    42.0.152.154:32231(TCP)
加密      ⚠️ 静态结论已被运行时推翻:libgame.so 的 AES-128-CBC SFS SDK 是死代码;
          真正生效的只有 params 的 32 字节循环 XOR(会话级密钥,服务端下发)。
          详见 protocol/COK-游戏服协议实测报告.md
命令数    2158(native 词表 ∪ Lua 词表);运行时实证 37 条带完整参数
类数      21107(DEX 定义类)
native    libgame.so 59MB / 14063 符号 / 336 JNI 导出 / 2296 SFS2X 符号
```
