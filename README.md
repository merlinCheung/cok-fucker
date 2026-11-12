# COK 直连工具(列王的纷争 / Clash of Kings 国服)

脱离 App 直连 COK 游戏服务器的逆向与工程化工具集: 协议编解码、地图坐标索引、
自动打怪、港口贸易、联盟集结、网页控制台 —— **桌面端和安卓 App 共用同一套
Python 核心**。

区服 2223 · 客户端 12.06.0(海尔渠道包) · 协议 SmartFoxServer 2X (SFS) over TCP

---

## 一句话上手

```bash
make run          # 启动桌面端控制台 → http://127.0.0.1:8770/?t=<token>
make build-apk    # 编译安卓 App(debug APK)
make install-app  # 编译并直接装到已连接的手机
make test         # 跑离线回归测试(26 个用例, 几秒钟)
make help         # 看全部入口
```

不想用 make 也行, 任何命令都能直接跑:

```bash
python3 -m cok console     # 等价于 make run
python3 -m cok list        # 列出所有子命令
```

---

## 目录结构

```
cok/
├── cok/                       ★ 唯一的 Python 包(桌面端 / 安卓端共用)
│   ├── core/                  协议与业务实现(26 个模块, 纯逻辑, 不含 CLI)
│   ├── tools/                 命令行动手工具(扫描 / 导出 / 校验)
│   ├── tools/probes/          协议逆向期的一次性探针(归档, 不在运行时路径上)
│   ├── tests/                 离线回归测试(+ run_all.py 汇总入口)
│   ├── resources/             只读资源(协议目录、道具表、前端页面)
│   ├── data/                  运行时数据(账号库、地图索引、token、锁)
│   ├── docs/                  协议文档、命令表、逆向方案
│   └── __main__.py            统一入口: python3 -m cok <子命令>
├── android-app/               安卓 App(Kotlin + Compose + Chaquopy 内嵌 Python)
│   ├── app/src/main/java/     Compose 界面与后台服务
│   ├── app/src/main/python/   安卓端启动器(android_entry.py)
│   ├── mobile-console.css     注入 WebView 的移动端样式
│   ├── mobile-console.js      注入 WebView 的移动端交互
│   ├── gradlew                一键构建(已提交, 无需装 gradle)
│   └── local.properties       本机 SDK 路径(不入库)
├── reverse/                   逆向产物(报告、Frida 脚本、抓包、截图、大体积解包)
├── apk-material/              分析素材 APK(不入 git)
├── frida/                     Frida 注入与抓包脚本
├── device/                    设备侧产物
└── Makefile                   一键入口
```

**两个目录的分工是这套结构的核心:**

| | 目录 | 内容 | 生命周期 |
|---|---|---|---|
| **只读** | `cok/resources/` | 协议命令表、道具配置、前端页面 | 随代码走, 打包进 APK |
| **可写** | `cok/data/` | 账号库、地图索引、运行时 json、锁文件 | 随账号/设备走, **不入库** |

数据目录可用 `COK_DATA_ROOT` 覆盖(安卓端由 `android_entry.py` 指向 `files/cok/data`)。

---

## 核心模块 `cok/core/`

| 文件 | 作用 |
|---|---|
| `cok_sfs.py` | SFS 协议编解码(帧格式、数组的 val/kv 双模式、params XOR) |
| `cok_client.py` | 连接、登录、会话密钥、`call` 重试、跨进程账号锁 |
| `cok_accounts.py` | 多账号注册表 + 协议公共字段真值(baseActiveKey 等) |
| `cok_map.py` | `world.get` 地图接口: 覆盖区扫描、坐标索引、众数投票校正 |
| `cok_hunt.py` | 自动打怪(多队并行、行军/回城、体力管理) |
| `cok_rally.py` | 联盟集结(巨型狮鹫等) |
| `cok_dock.py` | 港口航海贸易(三套命令族自动探测) |
| `cok_web.py` | 网页控制台后端(本地 HTTP, 带 token 鉴权) |
| `cok_daemon.py` | 轮询/推送引擎、事件规则、WebHook 通知 |
| `cok_channel_login.py` | 渠道账号密码登录(果盘 / 海尔等渠道包) |
| `cok_daily_quest.py` | 每日任务、签到、宝箱 |
| `cok_excel.py` | 标准库手写 xlsx 导出(零第三方依赖) |
| `cok_paths.py` | **唯一的路径解析入口**(资源目录 / 数据目录) |

---

## 快速开始

### 桌面端(macOS / Linux)

```bash
make run                       # 网页控制台
python3 -m cok scan            # 全图扫描(独立进程, 可断点续扫)
python3 -m cok export          # 导出 Excel
python3 -m cok verify          # 坐标抽样复核
python3 -m cok test            # 离线回归测试
python3 -m cok probe <名字>     # 跑一个协议探针
```

### 安卓端

```bash
make build-apk                 # → android-app/app/build/outputs/apk/debug/app-debug.apk
make install-app               # 直接装到已连接设备
```

安卓 App 把**同一套 Python 核心**通过 Chaquopy 内嵌进 APK:

* 原生 Compose 界面(主页 / 账号 / 操作 / 更多)走本地 HTTP API;
* 「完整高级控制台」用 WebView 加载 `cok_webui.html`, 与桌面端是同一个页面;
* 全图扫描在**进程内线程**跑(Chaquopy 没有可执行的 Python 解释器)。

### 两个前端的分工

| | 桌面端 | 安卓端 |
|---|---|---|
| 入口 | 浏览器打开 `127.0.0.1:8770` | 原生 App + 内嵌 WebView |
| Python 来源 | 仓库 `cok/core/` | 打进 APK 的同一批模块 |
| 资源目录 | `cok/resources/` | APK assets 解出的 `resources/` |
| 数据目录 | `cok/data/` | `files/cok/data` |

---

## 必知的几条铁律

0. **扫描只在页面上手动点「一键全图重扫」才开始** —— 没有任何自动扫描:
   页面加载不会扫, 后台不会扫, 定时器不会扫, 服务重启也不会扫。
   命令行 `python3 -m cok scan` 也只在你自己敲的时候跑。
1. **同账号只允许一个连接** —— 手机上的游戏 App 在线时, 我们的连接会被服务端
   主动关掉(`连接被服务端关闭(已收 0/3 字节)`)。看到这条报错, 第一件事是
   `adb shell "ps -A | grep -E 'cok|hcg|gamecenter'"`。
   扫描器会自动 `am force-stop` 掉 App。
2. **步长必须 ≤ 覆盖区直径** —— `world.get` 的实际覆盖区只有 **±12 格**,
   步长 12 才是对的。调大步长会漏掉玩家的城, 而且**看起来完全正常(不报错)**。
3. **坐标是扫描时刻的快照** —— 服务端会重排地图, 隔天的表可能整体作废。
   查当下坐标用页面的「查玩家」(会实时校验), 要全表就重扫。
4. **每条连接的第一条业务请求会被服务端丢弃** —— 预热挡不住, 要重试;
   而且**重试必须换新的 `timeStamp`**。
5. **App 在线时网页监控会暂停** —— 这是设计内的让路, 不是故障。
6. **`maxSearchCount` 不代表真实上限** —— SVIP 号实际无限找怪; 只有服务端返回
   空坐标才算次数用完。别拿服务端下发的上限字段当本地拦截阈值。
7. **释放型操作(停止/取消)必须先于它要释放的锁执行** —— 否则会自己等自己。

---

## 文档

- `cok/docs/WEB.md` —— 网页控制台完整说明(协议细节、坑位、API)
- `cok/docs/COMMANDS.md` —— 协议命令表(按模块)
- `cok/docs/COK-游戏服协议实测报告.md` —— 线格式字节级定义、加密真相、直连可行性
- `cok/docs/DAEMON.md` —— 轮询/推送引擎
- `cok/docs/DAILY_QUEST.md` —— 每日任务协议
- `cok/docs/ALLIANCE.md` / `ASSIST.md` / `CAPABILITIES.md` —— 联盟、协助、能力清单
- `cok/docs/RE-渠道登录逆向方案.md` —— 渠道登录逆向
- `reverse/reports/` —— 静态逆向报告、命令表全量、native 层分析

---

## 目录里的历史包袱

- `cok/tools/probes/` —— 52 个一次性探针。它们完成了"摸清协议"的使命,
  但**不在运行时路径上**, 只在需要回头查协议细节时翻。
- `reverse/` —— 逆向产物(含 1.4G apktool、1.5G ghidra-project)。
  这些**不入 git**, 可从 APK 重新生成。
- `cok/data/` —— 账号凭据、地图索引、token。**绝不要提交**。