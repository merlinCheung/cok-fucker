# COK 直连工具(列王的纷争 / Clash of Kings 国服)

脱离 App 直连 COK 游戏服务器的逆向与工程化工具集: 协议编解码、地图坐标索引、
自动打怪、港口贸易、网页控制台。

区服 2223 · 客户端 12.06.0(海尔渠道包) · 协议 SmartFoxServer 2X (SFS) over TCP

## 目录结构

```
cok/
├── COK-CN1-analysis/          逆向分析产物 + 工具代码
│   ├── protocol/              ★ 核心: 协议/工具代码(见下)
│   ├── native/                native 层分析产物
│   ├── apktool/               apktool 反编译输出(大, 不入 git)
│   ├── apk-extract/           解包产物(大, 不入 git)
│   ├── ghidra-project/        Ghidra 工程(大, 不入 git)
│   ├── scripts/               辅助脚本
│   └── *.md *.txt             静态/深度分析报告、协议命令表
├── frida/                     frida 注入与抓包脚本(COK 专用)
├── device/                    设备侧产物
├── 5396(12.06.0)-COK_CN1--*.apk   分析素材(不入 git)
└── COK-CN1-静态API分析报告.md
```

## 核心代码 `COK-CN1-analysis/protocol/`

| 文件 | 作用 |
|---|---|
| `cok_sfs.py` | SFS 协议编解码(帧格式、数组的 val/kv 双模式) |
| `cok_client.py` | 连接、登录、会话密钥、`call` 重试、socket 残留清理 |
| `cok_map.py` | `world.get` 地图接口: 覆盖区扫描、坐标索引、众数投票校正 |
| `scan_world.py` | 全图扫描器(独立进程、断点续扫、扫描历史) |
| `cok_excel.py` | 标准库手写 xlsx 导出(零第三方依赖) |
| `cok_hunt.py` | 自动打怪(多队并行、行军/回城) |
| `cok_dock.py` | 港口航海贸易(三套命令族自动探测) |
| `cok_locate.py` | 按名字查坐标(道具路径兜底) |
| `cok_web.py` | 网页控制台后端(端口 8770) |
| `cok_webui.html` | 网页前端(单文件) |
| `verify_points.py` | 坐标抽样复核(回查服务端确认记录是否还有效) |
| `diag_world_get.py` / `diag_cover.py` | 协议诊断工具 |

## 快速开始

```bash
cd COK-CN1-analysis/protocol

# 启动网页控制台
python3 cok_web.py --port 8770
# 打开 http://127.0.0.1:8770/?t=$(cat .cok-web-token)

# 全图扫描(独立进程, 可断点续扫)
python3 scan_world.py --out map-index.json --step 12
python3 scan_world.py --resume            # 从断点继续

# 导出 Excel
python3 export_excel.py --out cok-players.xlsx --csv --top 20
python3 export_excel.py --real-only        # 只导真实玩家

# 坐标抽样复核
python3 verify_points.py 30
```

## 必知的几条铁律

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

## 文档

- `COK-CN1-analysis/protocol/WEB.md` —— 网页控制台完整说明(协议细节、坑位、API)
- `COK-CN1-analysis/COK-CN1-完整静态逆向报告.md`
- `COK-CN1-analysis/COK-CN1-Native层深度分析.md`
- `COK-CN1-analysis/COK-CN1-静态API分析报告.md`
- `COK-CN1-analysis/game-protocol-commands-union.txt` —— 全量协议命令表
