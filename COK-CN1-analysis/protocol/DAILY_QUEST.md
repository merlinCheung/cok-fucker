# COK 每日任务 (dailyQuest2025) 协议可行性分析

> 口径：全部基于 `dailyQuest2025.data` 直连真实服务器验证，配合本地 APK 解包的
> `database.local.xml`（`daily_quest_2025` 组）和 `JumpHandler.lua` 反查 gotype/go 语义。

## 一、结论（一句话）

**直连协议目前只能安全做一件“一键完成”：** 领取已完成任务对应的活跃宝箱
(`dailyQuest2025.reward` / `dailyQuest2025.weekReward`，不消耗道具)。

其余 **18 个未完成任务的“正常完成”**（建造、研究、签到、龙塔试炼等）需要在
游戏 App 内手动点页面跳转执行，直连工具**无法模拟 UI 点击**。
`immediateTask` / `immediateAllTask` 虽可直连调用，但**消耗道具**，用户已明确排除。

## 二、协议命令（全部来自 `NewDailyActiveController2025.lua`）

| 命令 | 参数 | 方向 | 说明 |
|---|---|---|---|
| `dailyQuest2025.data` | 无 | 读 | 拉取每日任务列表（20 项）、活跃点、周活跃点、已领宝箱记录 |
| `dailyQuest2025.reward` | `{id: STRING}` | 写 | 领取日活跃宝箱（需 activePoints >= 宝箱点数且未领） |
| `dailyQuest2025.weekReward` | `{id: STRING}` | 写 | 领取周活跃宝箱（需 weeklyActivePoints >= 宝箱点数且未领） |
| `dailyQuest2025.immediateTask` | `{id: STRING}` | 写 | 快速完成单个任务（**消耗道具**，已排除） |
| `dailyQuest2025.immediateAllTask` | 无 | 写 | 快速完成全部任务（**消耗道具**，已排除） |

补充的直连协议命令（供各任务的“完成动作”参考，参数见 `command-catalog-typed.json`）：

| 命令 | 参数 | 方向 | 说明 |
|---|---|---|---|
| `build.info` | 无 | 读 | 拉取建筑信息（含 `building[]`、`buildingQueue`），取建筑 uuid |
| `build.upgrade` | `{uuid, cmd:'build.upgrade', param, multySpeedType, ...}` | 写 | 主城建筑升级（消耗资源，参数未完全反出，未实测） |
| `res.tile.find` | `{type, level, NoRecord, item}` | 读 | 大地图寻找野怪/资源点坐标（每日限 6 次，只读；不等于击杀/采集） |
| `arena.apply` | 无 | 写 | 进入皇家角斗场界面（完成需参战，协议无法直接触发） |
| `dragontower.quickbattle` | `{dealObject:'auto'}` | 写 | 龙塔扫荡（消耗真实次数，用户已排除自动化） |
| `newgeneral.recruit` | `{id}` | 写 | 英雄招募（消耗招募道具，用户已排除自动化） |
| `hot.item.v2.buy` / `hot.item.v3.buy` | `{itemId,itemNum,price,priceType,num}` | 写 | 旅行商人购买（消耗货币，用户已排除自动化） |
| `al.renderhelp` | `{helpId}` | 写 | 联盟帮助（消耗帮助次数，用户已排除自动化） |
| `allianceNewBoss.bossMainInfo` | 无 | 读 | 联盟 boss 主界面信息（只读；不等于参与击杀） |
| `allianceNewBoss.summon` | `{uid}` | 写 | 联盟 boss 召唤（消耗道具，用户已排除自动化） |
| `allianceNewBoss.donate` | `{uid,count}` | 写 | 联盟 boss 捐献（消耗道具，用户已排除自动化） |
| `al.targetscience.set` | `{scienceId,isuse}` | 写 | 联盟科技推荐（非研究；`science.research` 未定位） |
| `newHeaven.info` / `heaven.task.info` | 无 | 读 | 天空之境数据查看（无完成命令） |

读取返回字段：`dailyTaskId2025`、`newWeekRewardList`、`curReward`、`weekEndTime`、
`rewardList`、`dailyQuest`（数组，每项含 id/num/times/totalTimes/hasCom 等；**不含**
gotype/go/point，需从本地 XML 补全）。

## 三、20 个任务项详细分析

下表按 XML 配置表顺序列出所有 21 条配置（ID 57621763 不存在，实际下发 20 项）。
其中 2 项已完成（✓），18 项未完成。

| # | 任务 ID | gotype | go | 点数 | 类型（来自 XML + JumpHandler.lua） | 完成 | 可协议完成 | 协议命令 |
|---|---|---|---|---|---|---|---|---|
| 1 | 57621751 | 16 | 7 | 3 | 大地图搜索栏 → 巨型狮鹫 | ✓ | — | —（已完成） |
| 2 | 57621752 | 1 | 428000 | 1 | 主城建筑（ID 428000） | 未完成 | ❌ 需手动 | build.info → build.upgrade（消耗资源，未实测） |
| 3 | 57621753 | 106 | — | 2 | 联盟 boss | 未完成 | ❌ 需手动 | allianceNewBoss.bossMainInfo(只读) / summon(消耗道具) |
| 4 | 57621754 | 16 | 8 | 10 | 大地图搜索栏 → 普通怪 | 未完成 | ❌ 需手动 | res.tile.find {type:8}(只读坐标) / world.march(未定位) |
| 5 | 57621755 | 16 | 11 | 12 | 大地图搜索栏 → 超级营地 | 未完成 | ❌ 需手动 | res.tile.find {type:11}(只读坐标) / world.march(未定位) |
| 6 | 57621756 | 7 | 25 | 4 | 功能跳转 → 英雄招募 | 未完成 | ❌ 需手动 | newgeneral.recruit {id}(消耗道具，已排除) |
| 7 | 57621757 | 107 | — | 5 | 联盟宝藏 | 未完成 | ❌ 需手动 | 无直接协议完成命令 |
| 8 | 57621758 | 1 | 426000 | 5 | 主城建筑（ID 426000） | 未完成 | ❌ 需手动 | build.info → build.upgrade（消耗资源，未实测） |
| 9 | 57621759 | 16 | 10 | 20 | 大地图搜索栏 → 奇迹宝藏 | 未完成 | ❌ 需手动 | res.tile.find {type:10}(只读坐标) / world.march(未定位) |
| 10 | 57621760 | 105 | — | 4 | 联盟帮助 | 未完成 | ❌ 需手动 | al.renderhelp {helpId}(消耗次数，已排除) |
| 11 | 57621761 | 16 | 2 | 5 | 大地图搜索栏 → 粮食采集 | 未完成 | ❌ 需手动 | res.tile.find {type:2}(只读坐标) / build.collect(世界采集需 world.march) |
| 12 | 57621762 | 7 | 28 | 20 | 功能跳转 → 日常奖励-签到 | ✓ | — | —（已完成） |
| 13 | 57621764 | 7 | 26 | 5 | 功能跳转 → 皇家角斗场 | 未完成 | ❌ 需手动 | arena.apply(无参数，仅进入界面) |
| 14 | 57621765 | 7 | 23 | 2 | 功能跳转 → 旅行商人 | 未完成 | ❌ 需手动 | hot.item.v2.buy / v3.buy(消耗货币，已排除) |
| 15 | 57621766 | 1 | 400000 | 30 | 主城建筑（ID 400000） | 未完成 | ❌ 需手动 | build.info → build.upgrade（消耗资源，未实测） |
| 16 | 57621767 | 1 | 403000 | 30 | 主城建筑（ID 403000） | 未完成 | ❌ 需手动 | build.info → build.upgrade（消耗资源，未实测） |
| 17 | 57621768 | 7 | 18 | 1 | 功能跳转 → 龙塔试炼 | 未完成 | ❌ 需手动 | dragontower.quickbattle(消耗次数，已排除) |
| 18 | 57621769 | 109 | — | 2 | 联盟科技 | 未完成 | ❌ 需手动 | al.targetscience.set(仅推荐) / science.research(未定位) |
| 19 | 57621770 | 7 | 117 | 2 | 功能跳转 → 福利界面某一页 | 未完成 | ❌ 需手动 | 纯 UI 跳转，无协议完成命令 |
| 20 | 57621771 | 7 | 65 | 1 | 功能跳转 → SVIP 界面 | 未完成 | ❌ 需手动 | 纯 UI 跳转，无协议完成命令 |
| 21 | 57621772 | 7 | 125 | 6 | 功能跳转 → 天空之境 | 未完成 | ❌ 需手动 | newHeaven.info / heaven.task.info(仅查看数据) |

**已完成任务（✓）**：57621751（16/7，巨型狮鹫）、57621762（7/28，签到）。
**未完成任务（18 项）**：其余全部，直连协议均**不能**替用户完成，只能拉取进度展示。

### gotype/go 语义参考（JumpHandler.lua）

- `gotype=1`：主城建筑，`go` 是建筑 ID（如 428000、426000、400000、403000）
- `gotype=7`：功能跳转，`go` 是子项：
  - 18 龙塔试炼、23 旅行商人、25 英雄招募、26 皇家角斗场、28 日常奖励-签到、
  - 65 SVIP 界面、117 福利界面某一页、125 天空之境
- `gotype=16`：大地图搜索栏，`go` 是目标类型：
  - 2 粮食采集、7 巨型狮鹫、8 普通怪、10 奇迹宝藏、11 超级营地
- `gotype=105`：联盟帮助
- `gotype=106`：联盟 boss
- `gotype=107`：联盟宝藏
- `gotype=109`：联盟科技

## 四、可通过协议完成的部分：领取已完成任务的活跃宝箱

### 前提条件

1. 任务已完成（`hasCom==true` 或 `times >= totalTimes`）
2. 对应的活跃点达到宝箱所需点数（`activePoints` / `weeklyActivePoints`）
3. 该宝箱尚未领取（不在 `dailyTaskId2025` / `weekTaskRewardId2025` 已领记录中）

### 命令

```python
from cok_daily_quest import read_daily_quest, claim_all_boxes

result = read_daily_quest(client)        # 拉取任务列表 + 宝箱状态
out = claim_all_boxes(client, result)    # 一键领取所有可领的日+周宝箱
# out = {"ok": bool, "claimed": [...], "skipped": [...], "activePoints": ..., "weeklyActivePoints": ...}
```

CLI 入口：

```bash
# 拉取并显示每个任务项（只读）
python3 cok_daily_quest.py --read

# 逐项分析：每个任务的 gotype/go 操作、可否协议完成、协议命令
python3 cok_daily_quest.py --analyze

# 一键领取所有可领的活跃宝箱（不消耗道具）
python3 cok_daily_quest.py --claim-boxes

# 通过 daemon 一键入口
python3 cok_daemon.py --once --daily-quest
```

### daemon 集成

`cok_daemon.py` 已增加 `--daily-quest` 参数，在 `run()` 的 `--once` 分支和主循环中
调用 `daily_quest_cmd()`，输出任务列表 + 领取可领宝箱的事件：

```
daily_quest: {activePoints, weeklyActivePoints, tasks[], boxes[], weekly_boxes[]}
daily_box_claim: {boxId, ok, error}
weekly_box_claim: {boxId, wid, ok, error}
```

不消耗道具，安全。

## 五、不能通过协议完成的部分（18 个未完成任务）

| 任务 ID | 需在 App 内手动执行的操作 | 直连工具能做什么 |
|---|---|---|
| 57621752 | 主城建筑 428000（可能是某种建筑升级/建造） | 只读进度 |
| 57621753 | 联盟 boss（参与击杀） | 只读进度 |
| 57621754 | 大地图击杀普通怪 | 只读进度 |
| 57621755 | 大地图击杀超级营地 | 只读进度 |
| 57621756 | 英雄招募 | 只读进度 |
| 57621757 | 联盟宝藏（挖掘） | 只读进度 |
| 57621758 | 主城建筑 426000 | 只读进度 |
| 57621759 | 大地图奇迹宝藏 | 只读进度 |
| 57621760 | 联盟帮助（求助/被求助） | 只读进度 |
| 57621761 | 大地图粮食采集 | 只读进度 |
| 57621764 | 皇家角斗场 | 只读进度 |
| 57621765 | 旅行商人（购买） | 只读进度 |
| 57621766 | 主城建筑 400000 | 只读进度 |
| 57621767 | 主城建筑 403000 | 只读进度 |
| 57621768 | 龙塔试炼 | 只读进度 |
| 57621769 | 联盟科技（捐献/研究） | 只读进度 |
| 57621770 | 福利界面某一页 | 只读进度 |
| 57621771 | SVIP 界面 | 只读进度 |
| 57621772 | 天空之境 | 只读进度 |

**根本原因**：直连工具只能发送游戏服协议命令，**无法模拟 App 界面的 UI 点击**。
每个任务的完成都需要用户在 App 内进入对应页面执行具体操作（建造、研究、签到、
击杀怪物等），这些操作对应的协议命令（如 `build.upgrade`、`science.research` 等）
要么参数未知、要么会消耗真实资源，未打通。

## 六、后续实现建议

1. **当前可交付**：`--analyze` / `--read` / `--claim-boxes` 三个入口，分别用于
   查看进度、逐项分析、一键领已完成任务的宝箱。
2. **18 个未完成任务**：用户需在 App 内手动完成；直连工具只负责拉取进度展示，
   在“今日待办”卡里标出“还剩什么”。
3. **如未来要自动化某个未完成任务**：需先反出该任务对应的具体协议命令（例如
   建造走 `build.upgrade`，研究走 `science.research`），并评估资源消耗与风控风险。
