# COK 联盟功能 —— 可移植清单(2026-10-30 实测 + 静态逆向)

> 口径:
> **✅ 实测** = 2026-10-30 直连游戏服(账号 `<uid-main>`, 区服 2223)拿到真实响应;
> **🧩 静态反出** = 参数从 `libgame.so` 交叉引用反出, 命令名确凿但**未在服务端跑过**;
> **❌** = 服务端有响应但返回业务错误(命令存在, 当前条件不满足或缺参数)。

测试账号所在联盟:
`allianceId = 30e750abfa2745289e13e1f4377a0976`(联盟标题含 "LISA®")

复现命令:

```bash
cd ~/workspace/me/cok
python3 probe_alliance.py --round all    # 三轮一起跑(单连接, ~4 分钟)
python3 probe_alliance.py --round 1     # 只读全景
python3 probe_alliance.py --round 2     # 修正命令名 + 带参
python3 probe_alliance.py --round 3     # 定向带真实 id
# 原始响应: evidence/alliance-probe-rall.json
```

**全量跑完一轮的结果: 21 条 OK / 24 条 ERR / 1 条超时。**

---

## 一、结论速览(能移植什么)

| # | 功能 | 读 | 写 | 难度 | 建议 |
|---|---|---|---|---|---|
| 1 | **联盟任务板**(工事/任务发布与接取) | ✅ | 🧩 | 中 | **最值得做** —— 数据齐全,写参数已反出 |
| 2 | **联盟捐献**(科技/资源) | ✅ | 🧩 | 中 | **最值得做** —— 三档面板已读通,差一次实测 |
| 3 | **联盟科技树**(65 项科技进度) | ✅ | — | 低 | 纯展示,半天上线 |
| 4 | **联盟使命/日常**(mission) | ✅ | 🧩 | 低 | 进度类,只读即可用 |
| 5 | **联盟商店** | ✅(空) | 🧩 | 中 | 商店要 `alliancePoint>0` 才有货 |
| 6 | **联盟签到**(5 天一轮) | ✅(在 mission 里) | ❓ | 低 | 领奖命令未确认(`signIn.info` → 102192) |
| 7 | **联盟捐献排行** | ✅ | — | 低 | 一次请求,零风险 |
| 8 | **联盟资源池/领地** | ✅ | — | 低 | 捐献前的资源快照 |
| 9 | **请求帮助**(加速/治疗) | ✅ | 🧩 | 中 | 需要队列 uuid + qType |
| 10 | 联盟BOSS(已有) | ✅ | 🧩 | — | 控制台**已接** `allianceNewBoss.bossMainInfo` |
| 11 | 联盟集结/宴会/税收/赏金/文明技能 | ❌ | — | 高 | 服务端返回 102192/E000000, 本区服没开或走 native 专属流程 |

---

## 二、已实测可用的只读命令(直接能用)

| 命令 | 参数 | 返回要点 |
|---|---|---|
| `al.rank` | `{allianceId}` (可省) | `allianceTitle[]` `rankName` `allianceApply[]` `list[]`(68 个联盟的战力/主城等级) |
| `al.task.record` | — | `record{refreshCount, publishCount, acceptCount, itemPublishCount}` `gold` `nextGold` `freequeue` `maxPublishCount=8` `maxAcceptRewardCount=10` |
| `al.task.get.available` | — | `taskList[]{uid, stat, finishTime, baseReward, taskId, vanishTime, publishUid}` + `record` + `freequeue` |
| `al.task.get.published` | — | `taskList[]{uid, publishName, publishUid, allianceId, acceptStat, publishStat, requested, startTime, finishTime, acceptReward, baseReward, freequeue, pic, picVer, taskId}` + `leftRequestCount` |
| `al.task.get.detail` | `{taskUid}` | 单个任务详情(同上字段) |
| `al.mission.show` | — | `random[]` `common[]` + **`alliance_sign_in{signIn_reward, signInReward_state, signIn_days}`** |
| `al.donate.rank.all` | — | `donateRank[]{uid, name, donation, rank, power, alliance_honor, donateTime}` |
| `al.donate.rank.today` | — | 同上 + `refreshTime` |
| `al.donate.rank.week` | — | 同上(含 allianceId) |
| `al.shop.show` | `{type?}` | `alliancePoint` + `goods[]` |
| `al.point.find` | — | `targetPoint` |
| `al.ref.list` | — | `list[]` `forces` |
| `alquick.data` | — | `nextCallHelpTime`(帮助冷却, 实测 18000000ms) |
| `mine.help.info` | — | `result[]`(我发出的求助) —— ⚠ **不稳定**: 有一次回 OK(空 result), 另一次回 E000000 |
| `al.donate.res.info` | — | `res{}`(各资源库存) `resMax{}`(上限) `item{}` `num` `stoneFactoryNum` |
| `territory.check` | — | 与 `al.donate.res.info` 同结构(联盟资源池/领地) |
| `science.data.init` | — | **`allianceScience[]` 65 项**联盟科技: `scienceId, level, star, currentPro, needPro, totalPro, startTime, finishTime, speedUp, points, para1, para2` |
| `al.science.fresh` | `{scienceId}` | **捐献面板**: `low/mid/high` 三档 × `{Contribute, Num, Progress, Res, ResFlag, Available}` |
| `allianceNewBoss.bossMainInfo` | — | `bossInfo[]` ✅ **控制台已接** |
| `alliance.team.ls` | — | `list[]` `helplist[]`(集结) |
| `alliance.recharge.getRank` | — | `success` |
| `allianceMillitaryPower` | — | 联盟战力 |
| `al.get.url` | — | `success` |

### 捐献面板实测样例(`al.science.fresh {scienceId:251600}`)

```
low : contribute=200   num=3000  progress=40    res=3  resFlag=0  available=0
mid : contribute=1000  num=3000  progress=?     res=3  resFlag=0  available=0
high: contribute=5000  num=3000  progress=1000  res=3  resFlag=0  available=0
```

→ **捐献是三档**(低/中/高),服务端把「消耗资源种类/数量 → 得到的联盟贡献/科技进度」
算好发下来,客户端只传 `scienceId` + 档位。

### 联盟签到(藏在 mission 里)

`al.mission.show` 的 `alliance_sign_in`:

```json
{"signIn_reward": "251492", "signInReward_state": 0, "signIn_days": 5}
```

→ 5 天一轮的联盟签到,`signInReward_state=0` = 今天还没签。
⚠ **领奖命令没找到**:客户端 native 里的 `signIn.info` / `signIn.reward` 实测都回
`102192`(未开放),`al.mission.reward` 才是对应的领取命令(待实测)。

---

## 三、写操作命令(静态反出参数, 未实测)

来源: `frida/elf_xref.py` + `frida/disasm_strings.py` 在
`apk-extract/lib/arm64-v8a/libgame.so` 上做的字符串交叉引用与函数区聚类。

| 命令 | 参数 | 用途 |
|---|---|---|
| `al.science.donate` | **`scienceId`, `option`** | 捐献联盟科技(option = 低/中/高档位) |
| `al.science.donate.new` | `scienceId`, `option` | 新版捐献 |
| `al.science.fresh` | `scienceId` | 拉捐献面板 ✅实测 |
| `al.science.fresh.new` | `scienceId` | 新版面板 |
| `al.science.donate.cd` | — | 捐献 CD 查询(实测 E100160) |
| `al.science.research` | `scienceIds` | 联盟科技研究/解锁 |
| `al.task.accept` | **`taskUid`**(+ `acceptUid`) | 接取联盟任务 |
| `al.task.award` | **`taskUid`** | 领联盟任务奖励 |
| `al.task.publish` | `publishName`, `finishTime`, `acceptReward`, `freequeue`, `itemId`, `itemNum`, `gold`, `description`, `pic`, `picVer` | 发布联盟任务 |
| `al.task.refresh` | `taskUid` | 刷新任务 |
| `al.task.auto.refresh` | — | 一键刷新 |
| `al.task.spd` | `taskUid`, `num` | 加速联盟任务 |
| `al.callhelp` | **`queueId`, `qType`** | 向联盟请求帮助(加速/治疗) |
| `al.helpall` | — | 帮助全体 |
| `al.shop.buy.al` | `allianceShopId`, `allianceShopNum`, `num`, `id`, `itemId`, `goodsId` | 联盟商店购买 |
| `al.shop.buy.usr` | 同上 | 个人商店购买 |
| `al.targetscience.set` | `isuse`, `scienceId` | 设捐献目标科技(lua 侧确认) |
| `al.donate.tool.resource` | `resourceType`, `count`, `num`, `type`, `itemId` | 用资源道具捐献 |
| `al.mission.reward` | — | 领联盟使命奖励 |
| `al.mission.reward.single` | — | 领单个使命奖励 |

---

## 四、错误码词典(实测归纳)

| 错误码 | 含义 | 例子 |
|---|---|---|
| `E000000` | 通用失败: **缺参数** 或 **权限/条件不满足** | `al.check` `al.commentview` `al.userapplylist` `al.ref.cnt` `al.abbr` `al.search` `al.event` `al.fight.bulletin` `al.science.fresh`(不带 id) |
| `E100057` | 参数格式错 | `al.rank` 传空 `allianceId` |
| `E100123` | id 不存在 | `al.task.get.detail` 传空/无效 `taskUid` |
| `E100160` | 状态不允许 | `al.science.donate.cd` |
| `115286` | 特殊业务错误 | `al.attr` |
| `102192` | **玩法未开放 / 本区服没有这个功能** | `allianceTax.data` `allianceNewBuilding.data` `alliancebounty.openUI` `allianceChest.simpleInfo` `signIn.info` `signIn.reward` `allianceBoss.enter` |
| 无响应 | 命令名错(那是客户端通知名, 不是请求名) | `al.territory.data.back`(真名 `territory.check`)、`allianceScience.data`、`al.helpdata.back` |

> ⚠ **`al.territory.data.back` / `al.helpdata.back` / `allianceScience.data` 不是命令名**,
> 是 lua 里的 `postNotification` 通知名。照抄必然超时。

---

## 五、移植清单(建议分三期)

### 第一期:纯展示(零风险, 只读命令已通)

新增 `cok_alliance.py` 封装 + 网页「联盟」卡:

1. **联盟科技树**: `science.data.init` 的 `allianceScience[]` → 表格(等级/星级/进度/是否加速中)
2. **捐献面板**: `al.science.fresh {scienceId}` → 三档(贡献/数量/进度/能否捐)
3. **捐献排行**: `al.donate.rank.today` → 前 N 名
4. **联盟任务板**: `al.task.get.available` + `al.task.get.published` + `al.task.record`
5. **联盟资源池**: `al.donate.res.info` → 库存/上限
6. **联盟使命**: `al.mission.show` → 进度条

**落点**:
- 新模块 `cok/core/cok_alliance.py`(仿 `cok_welfare.py` / `cok_sky.py` 的写法)
- `cok_web.py` 快照里加 `alliance` 字段 → `cok_webui.html` 加一张「联盟」卡
- 安卓端 `SnapshotParser.kt` 解析新字段 → `OperationsScreen.kt` 加对应分组
  (安卓端是网页控制台的镜像, 走同一条 snapshot JSON, 不用改协议层)

### 第二期:写操作(需实测一次确认参数)

按"收益/风险"排序, 建议一次只做一个, 且**先在测试号上跑**:

| 操作 | 命令 | 收益 | 风险 |
|---|---|---|---|
| **一键捐献**(低档) | `al.science.donate {scienceId, option}` | 每天固定收益 | 低(消耗资源换贡献, 玩家天天做) |
| **接联盟任务** | `al.task.accept {taskUid}` | 任务奖励白拿 | 低(占用 1 个任务位, 10 个上限) |
| **领联盟任务奖励** | `al.task.award {taskUid}` | 领 exp+资源 | 低 |
| **发布联盟任务** | `al.task.publish {...}` | 给联盟供任务 | 中(参数最多, 需完整对齐) |
| **请求联盟帮助** | `al.callhelp {queueId, qType}` | 治疗/加速白嫖 | 低 |
| **联盟商店购买** | `al.shop.buy.al {...}` | 联盟币换东西 | 中(要钱, 且 `alliancePoint=0` 时是空的) |

### 第三期:自动化(接进 daemon)

`cok_daemon.py` 的 `WATCHERS` 字典加:

```python
"allianceTask":    ("al.task.get.published", "alliance_task"),
"allianceDonate":  ("al.donate.rank.today",  "alliance_donate"),
"allianceMission": ("al.mission.show",       "alliance_mission"),
"allianceScience": ("science.data.init",     "alliance_science"),
```

再配合 `--auto-*` 开关做「捐献提醒 / 有新任务就提醒 / 使命完成就提醒」。

---

## 六、坑

1. **同账号只允许一个连接** —— 联盟功能全是写操作, 一旦网页轮询 + 打怪 + 扫描同时跑,
   会互踢(老毛病)。做联盟自动化时沿用现有让路机制。
2. **第一条业务请求会被丢弃** —— 新连接第一发要重试(探针里已看到)。
3. **`option` 的取值还没验** —— 大概率是 0/1/2 或 1/2/3 对应低/中/高, 实测一次即可定死。
4. **联盟商店返回空** —— 实测 `alliancePoint: 0` 且 `goods: []`, 不是命令错, 是这个号没联盟币。
5. **`al.rank` 传空 allianceId 会报 E100057** —— 要么省略参数, 要么传真实 id。
6. **写操作前先 `al.task.get.available` 看 `record.acceptCount`**(上限 10),
   `record.publishCount`(上限 8), 避免把队友的任务位占满。
7. **安卓端不用改协议层** —— 它只解析网页控制台的 snapshot JSON, 后端加字段后
   改 `SnapshotParser.kt` 即可。
8. **⚠ 桌面端和手机端不能同时开自动规则** —— 同账号只允许一个连接, 两个控制台
   同时跑会**互踢**, 表现就是"自动任务一个都没执行"(一边把另一边踢了,
   被踢的那边那轮直接断档, 历史里会看到时间跳空)。跨设备互相看不见锁文件,
   只能靠人避开: 手机在跑自动时, 桌面端就只用来看看, 别同时开。
8. **联盟任务会过期** —— `al.task.get.published` 的任务带 `vanishTime`,
   实测隔 ~1 小时那条 MissVenom 的任务就查不到详情了(回 E100123)。
   做自动化时**必须**每次重新拉列表, 不要缓存 taskUid。
9. **`mine.help.info` 不稳定** —— 同一账号同一命令, 一次 OK 一次 E000000,
   大概率依赖"当前是否有正在等待帮助的队列"。读不到不能当故障。

## 七、联盟签到(2026-10-31 补上领奖)

之前只做了**读**(`al.mission.show` 的 `alliance_sign_in`),没做领奖 ⇒ 页面上
一直显示"今日未签"却没人领。

| 命令 | 参数 | 说明 |
|---|---|---|
| `al.mission.show` | 无参 | 读状态: `alliance_sign_in{signIn_reward, signInReward_state, signIn_days}` |
| **`alliance.signIn.reward`** | **无参** | 领奖 ⚠ 真副作用(每天一次) |

⚠ 命令名是 **`alliance.signIn.reward`**,不是 `signIn.reward` —— 后者回
`102192 = 功能未开启,敬请期待`,差点让我以为这功能没开。

2026-10-31 实测(国服号): 签到前 `signInReward_state=0` → 领奖 → 变成 `1`,
领到 goods 若干(209993×15、209997×15、211997×591 …), 连续签到天数 23。

**自动规则** `allianceSignIn`(默认关): 每轮读状态, 没签就领, 已签就记
"今日已签(连续 N 天)"。手动按钮: 联盟卡「领取联盟签到」。

---

## 八、已实现的移植(2026-10-30 一期 + 二期)

### 代码落点

| 文件 | 改动 |
|---|---|
| `cok_alliance.py` | **新增** —— 联盟功能封装(读 + 写), 仿 `cok_welfare.py` 的写法 |
| `cok_web.py` | 快照加 `alliance` 段; 新增 `action=alliance` 端点; 轮询里 60 秒节流读一次 |
| `cok_webui.html` | 新增「联盟」卡(科技/捐献面板/任务板/使命/排行/资源池/商店)+ 4 个按钮 |
| `android-app/.../Model.kt` | 新增 `AllianceStatus` / `AllianceDonateTier` + 3 个 `QuickAction` |
| `android-app/.../SnapshotParser.kt` | 解析快照的 `alliance` 段 |
| `android-app/.../ConsoleViewModel.kt` | 3 个动作的请求体 |
| `android-app/.../OperationsScreen.kt` | 新增 `AllianceCard` 组件 |
| `cok_alliance.py` | 增补 `read_sign_in` / `claim_sign_in`(联盟签到领奖) |
| `cok_web.py` | 增补 `allianceSignIn`(联盟自动签到)与 `assistAuto`(领地自动收取)两条规则 |
| `test_alliance.py` | **新增** —— 回归测试(全绿) |
| `COMMANDS.md` | 只读命令表补进 21 条联盟命令 |

### 网页端 API

```
GET  /api/state              -> 快照里的 alliance 段
POST /api/action {action:"alliance", op:"read"}         读一次(强制刷新)
POST /api/action {action:"alliance", op:"accept"}       接任务 {taskUid}
POST /api/action {action:"alliance", op:"accept-all"}   一键接所有可接的
POST /api/action {action:"alliance", op:"award"}        领奖 {taskUid}
POST /api/action {action:"alliance", op:"help"}         请求帮助 {queueId, qType}
POST /api/action {action:"alliance", op:"help-all"}     帮助全体
POST /api/action {action:"alliance", op:"donate"}       捐献 {scienceId, tier}
```

### 写操作的实测状态(诚实版)

| 操作 | 命令 | 状态 |
|---|---|---|
| 接取联盟任务 | `al.task.accept {taskUid}` | ✅ **实测成功**(主号接了 MissVenom 的任务) |
| 领取任务奖励 | `al.task.award {taskUid}` | ✅ 命令通(任务未完成时回 134042 = "挖掘未完成") |
| 请求联盟帮助 | `al.callhelp {queueId, qType}` | ✅ **实测成功**(返回 `success:true`) |
| 帮助联盟全体 | `al.helpall` | ✅ **实测成功** |
| 捐献联盟科技 | `al.science.donate {scienceId, option}` | 🧩 参数已定, **未能正向验证** |

### 捐献为什么没能正向验证(重要)

`al.science.donate` 在**三个账号**(主号/鸭皇/国服号)× **所有科技 id** ×
**option 0/1/2/3/5/21/22/字符串形式** × **补各种参数** 下, 一律回 `E000000`(操作无效)。

根因(已定位到证据链):

1. native 里 `al.science.donate` 的参数**就是两个**:
   `scienceId`(INT) + `option`(INT) —— 逐条反汇编确认(见
   `libgame.so` 0xdd6da0 那个函数), 类型也对(客户端用 CCInteger 封的)。
2. `al.science.donate.new` 回 **102192** = 本区服**没开**新科技系统,
   所以老命令才是对的。
3. 三个号所在联盟的**在研科技都是满进度**
   (`currentPro == needPro`, 100%), 客户端文案:
   `E100126 = 该科技已经进入可研究状态, 无法继续捐献`。
   ⇒ 当前**没有可捐献的目标**, 服务端自然一律拒绝。
4. **捐献只能给"正在研究的那一个科技"** —— 2026-10-31 在主号上做了对照实验:
   在研的 `251600`(进度 128000/128000, 满)→ 拒;
   **未满但没在研**的 `250000`(2440/24000)→ option 0/1/2/3 **同样全拒**。
   ⇒ 不是"进度满"这一个问题, 是**必须是在研的那个**。

所以命令和参数是对的, **差的是游戏里有一个"新的在研科技"**。
等联盟换研究下一个科技, 捐献就能正向验证了。

#### 2026-10-31 15:54 的时间线(研究刚结束, 仍然没得捐)

| 时刻 | 事件 |
|---|---|
| 10-30 15:40:09 | 盟主开 `251600` 研究(startTime=1793360409594) |
| 10-31 15:43:11 | 文档里的旧估值(来自早期估算, **不准**) |
| **10-31 15:54:26** | 真实 finishTime=1793433266394 —— 研究**真的结束**了 |
| 10-31 15:58:28 | 重测: 科技树 65 项**全部 startTime=0** → 没有在研目标 → 没法捐 |
| 10-31 16:02+ | 起后台守候轮询(`retest_donate_poll.py`), 等盟主开下一个 |

结束后 `251600` 变成 **lv3 star1, 6480/160000, startTime=0**:
进度**不是满的**(还有 92%), 但**没在研** → 服务端照样不收捐献。
⇒ 再次印证第 4 条:**只有"正在研究的那一个"才是合法捐献目标**,
   跟"进度满不满"无关。

另外确认: `al.science.fresh {scienceId}` 对**非在研**科技照样返回完整档位面板
(`251600` 返回 low/mid/high 三档, `midAvailable=0` `highAvailable=0`),
所以**面板能拿到 ≠ 能捐** —— 门槛只在 donate 那一步。

> `option` 的确切取值(0-based 还是 1-based)也因此没能定死 ——
> `cok_alliance.donate()` 会按候选值依次尝试, 第一个被接受的即为本服取值。
> 守候脚本 `retest_donate_poll.py` 就是干这个的: 见到在研未满的科技就
> 依次试 option=0/1/2/3, 第一个被接受的就是本服编码。

#### 在研判定的坑(已修)

`cok_alliance.read_science()` 原来用 `startTime>0 且 finishTime>now` 判在研。
**服务端刚开研究时 `finishTime` 可能还没填**, 那时会被误判成"没在研",
自动捐献整轮跳过 → 白等一轮。已改成
`startTime>0 且 (finishTime 为空 或 finishTime>now)`。
(`retest_donate_poll.py` 更是直接按原始字段判定, 不依赖这个标志。)

#### 服务端的捐献门槛模型(2026-10-31 16:30 补测)

用**只读**命令 `al.science.donate.cd {scienceId}` 探测四个不同科技 id
(251600 / 250000 / 253200 / 254400), **全部**回 `E100160`(状态不允许)。
⇒ 捐献是**全局状态门控**, 不是按 scienceId 区分的:

| 联盟状态 | 服务端对 `al.science.donate` 的回应 |
|---|---|
| 没有在研科技 | `E100160` 状态不允许(任何 scienceId 都一样) |
| 有在研科技, 但进度已满 | `E100126` / `E000000` |
| 有在研科技、进度未满, 但 scienceId 不是在研那个 | `E000000` 参数无效 |
| scienceId = 在研科技, 进度未满 | ✅ 接受 |

所以**必须等盟主开一个新科技**才可能捐出去, 别的试法都是白试。
（`al.science.donate.cd` 可以当"现在能不能捐"的只读探针。）

#### 重测用的三个脚本

| 脚本 | 作用 |
|---|---|
| `retest_donate.py` | 一次性重测: 读科技 → 找「在研未满」→ 读面板 → 依次试 option=0/1/2/3 → 出结论 |
| `retest_donate_poll.py` | **守候版**: 在同一条连接上轮询, 盟主一开新科技就立刻试捐; 成功会自动落盘 |
| `apply_donate_encoding.py` | 编码定死后: 改 `DONATE_TIERS` 单候选 → 跑回归 → 往本文追加结论 |

```bash
cd ~/workspace/me/cok
python3 retest_donate.py                     # 立刻测一次
python3 retest_donate_poll.py --minutes 120  # 守候(按账号锁, 网页端会优雅让路)
```

⚠ 守候脚本**用按账号的锁**(`.cok-account-<gameUid>.lock`), 所以网页控制台
拿不到锁时会显示「账号正被占用」并跳过本轮 —— 不会在游戏服上互踢。

### 捐献相关的客户端文案(备查)

| 文案 | 含义 |
|---|---|
| `115164` | 入盟4小时之内无法进行联盟科技的捐献 |
| `115807` | {0}正在研究，无法研究其他科技！ |
| `115808` | 你获得了{0}点联盟荣誉，{1}点联盟积分 |
| `E100124` | 联盟科技已到最大等级 |
| `E100125` | 加入联盟4小时内无法捐献 |
| `E100126` | 该科技已经进入可研究状态, 无法继续捐献 |
| `E100160` | 冷却时间未到, 请稍后尝试 |
| `E100320` | 离开联盟24小时之内不可领取联盟任务奖励 |

---

## 九、联盟自动捐献(2026-10-30 加)

### 它做什么

1. 找到**正在研究**的那个联盟科技(同时只能研究一个, 客户端文案 115807)
2. 从**当前开放**的捐献档位里**随机**挑一个(低/中/高)
3. 捐献 → 进度涨 → 再挑一档继续捐
4. **科技进度攒满(`currentPro >= needPro`)就停** —— 这是游戏本身的硬上限,
   服务端此时回 `E100126`「该科技已经进入可研究状态, 无法继续捐献」
5. 捐献冷却(`E100160`)就停, 等下一轮

### ⚠ 金币重置防护(重点)

**自动捐献只会发 `al.science.donate` 这一条命令。**

绝不碰这两个:

| 命令 | 作用 | 为什么不能碰 |
|---|---|---|
| `al.science.research {scienceId, gold}` | 花金币**开启/重置**科技研究 | 会**扣金币** |
| `al.targetscience.set {scienceId, isuse}` | 改联盟的捐献目标科技 | 要 R5 权限, 也不该由脚本改 |

另外两道防线:

* 已知在研科技进度已满 → **整轮跳过, 一个命令都不发**
* 网页端在发命令前也先判一次"满了", 直接返回中文原因

回归测试里有一条专门盯这个: 跑完「捐到满」和「冷却中」两条路径后,
断言调用列表里**没有**上面那两个命令(以及 `al.science.donate.new`、
`al.task.refresh` / `al.task.auto.refresh`)。

### 档位的 option 编码(踩过的坑)

客户端 native 里 `al.science.donate` 的 option 来自 UI 选中的档位,
0-based 还是 1-based 未定死:

| 档位 | 0-based | 1-based |
|---|---|---|
| 低 | 0 | 1 |
| 中 | 1 | 2 |
| 高 | 2 | 3 |

⚠ **候选值会跨档位**(0-based 时 option=1 是中档)。所以换编码**只能**在
服务端回 `E000000`(参数无效)时进行 —— 其它错误码(冷却/已满/权限)必须
原样停下, 否则会捐到用户没指定的档位去。

### 开关与参数

| 设置项 | 取值 | 默认 | 说明 |
|---|---|---|---|
| `allianceDonate` | bool | 关 | 自动捐献总开关 |
| `allianceDonateTier` | `random` / `cheapest` / `low` / `mid` / `high` | `random` | 档位模式; `random` = 随机挑一个开放档位 |
| `allianceDonateMax` | 1~100 | 20 | **单轮**最多捐几次(防跑飞的安全兜底, 不影响"进度满就停"的语义) |

* 网页: 「联盟」卡里有开关 + 档位下拉 + 单轮上限, 另有「手动跑一轮」按钮
* 安卓端: 「操作 → 自动处理 → 联盟自动捐献」开关(档位模式在网页端调)
* 自动化框架: 挂在 `AUTOMATION_RULES` 的 `allianceDonate` 上, 走现成的
  失败退避 + 告警机制

### API

```
POST /api/action {action:"alliance", op:"donate-auto"}    手动跑一轮自动捐献
POST /api/action {action:"alliance", op:"donate", tier:"random"}  随机捐一次
POST /api/action {action:"alliance", op:"sign-in"}        领取联盟签到
```

### 自动规则一览

| 规则 key | 开关名 | 做什么 | 默认 |
|---|---|---|---|
| `allianceDonate` | 联盟自动捐献 | 随机挑一个开放档位捐给在研科技, 进度满就停 | 关 |
| `allianceSignIn` | 联盟自动签到 | 每天领一次联盟签到奖励 | 关 |
| `assistAuto` | 领地自动收取 | 定时结算已产出的领地资源(无损) | 关 |

`assistAuto` 有独立节流 `assistAutoInterval`(秒, 默认 1800, 最小 300)。

### 已知限制

* 捐献有服务端冷却(`al.science.donate.cd`), 所以"自动"实际是"每轮能捐就捐一把"
* 捐献只能给正在研究的那一个科技 —— 没有多个目标可选, 随机的空间只在档位上
* `option` 的确切基准要等有可捐目标时才能最终定死(模块会自己试并记住成功的那个)

### 安卓端实测(2026-10-31)

手机上的自动规则记录(国服号 `<uid-guopan-intl>`):

```
allianceDonate  waiting  在研科技 253200 进度已满, 跳过(不会花金币重置)
```

⇒ 规则**确实在每轮跑**, 且因为在研科技已满而正确地空转(一个命令都没发)。
等联盟换研究下一个科技, 就会真的捐出去。

---

## 十、附录:联盟命令全集(协议层)

从 `game-protocol-commands-union.txt`(native 1182 ∪ lua 1063)里筛出的联盟相关命令:

**联盟主体** `al.*`:
`al.check` `al.attr` `al.rank` `al.abbr` `al.name` `al.create` `al.join` `al.leave.v2`
`al.apply` `al.applylist` `al.acceptapply` `al.refuseapply` `al.cancelapply`
`al.invite` `al.acceptinvite` `al.refuseinvite` `al.cancelinvite` `al.kick`
`al.dismiss` `al.leader.trans` `al.leader.replace` `al.setrank` `al.rankname.set`
`al.permission.modify` `al.search` `al.searchuser` `al.auto.apply`
`al.blacklist.modify` `al.blacklist.query` `al.title.apply` `al.title.modify`
`al.comment` `al.comment.check` `al.commentview` `al.comment.shield.add/list/remove`
`al.msg` `al.event` `al.get.url` `al.fight.bulletin` `al.point.find` `al.point.push`
`al.ref.cnt` `al.ref.list` `al.ref.return` `al.alliancerecest`

**联盟任务** `al.task.*`:
`al.task.get.available` `al.task.get.published` `al.task.get.detail` `al.task.accept`
`al.task.award` `al.task.publish` `al.task.refresh` `al.task.auto.refresh`
`al.task.spd` `al.task.record`

**联盟捐献/科技**:
`al.science.donate` `al.science.donate.new` `al.science.donate.cd` `al.science.fresh`
`al.science.fresh.new` `al.science.research` `al.targetscience.set`
`al.donate.res.info` `al.donate.tool.resource`
`al.donate.rank.all` `al.donate.rank.today` `al.donate.rank.week`

**联盟商店**:
`al.shop.show` `al.shop.buy.al` `al.shop.buy.usr` `al.shop.br` `al.shop.update`

**联盟帮助**:
`al.callhelp` `al.helpall` `al.showhelp` `al.renderhelp` `al.helpdata.back`(通知名)

**联盟使命**:
`al.mission.show` `al.mission.reward` `al.mission.reward.single`

**其他联盟玩法**:
`allianceNewBoss.*`(BOSS) `allianceBoss.*` `allianceBanquet.*`(宴会)
`allianceTax.*`(税收) `alliancebounty.*`(赏金) `allianceCiviSkill.*`(文明技能)
`alliancecivilization.*`(文明奇迹) `allianceCollect.*`(联盟采集)
`allianceMobilization.rank` `allianceTournament.*`(联盟锦标赛)
`allianceNewBuilding.*` `allianceMillitaryPower` `allianceIcon.*`
`AllianceRallyPoint.add/remove` `alliance.team.*`(集结)
`alliance.hospital.*`(联盟医院) `al.territory.*`(领地)
