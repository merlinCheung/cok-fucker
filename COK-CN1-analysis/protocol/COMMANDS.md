# COK 游戏服直连命令清单(2026-10-23 实测)

全部经 `cok_client.py` 直连真实服务器验证,响应字段为服务器真实返回。

```bash
cd ~/workspace/me/cok/COK-CN1-analysis/protocol
python3 cok_client.py --cmd <命令名>                   # 单条
python3 cok_client.py --cmd <命令名> --params '<JSON>'  # 带参数
```

> 用前先停 App(同账号双开会被服务端断开):`adb shell am force-stop com.hcg.cok.nearme.gamecenter`

## 一、只读命令 — 实测成功 76 条

| 命令 | 返回字段(前几个) |
|---|---|
| `accountLock.getUnlockView` | locked |
| `achieve.ls` | list, stageRewardInfo |
| `act.ls` | act |
| `al.rank` | allianceTitle, rankName, allianceApply, list |
| `al.task.record` | freequeueTime, refreshCount, itemPublishCount, refreshTime, conditionTime, maxPublishRewardCount |
| `allianceNewBoss.bossMainInfo` | bossInfo |
| `alquick.data` | nextCallHelpTime |
| `auction.getView` | gold, diamond, inActivity, endTime, list, globalList |
| `aw_formula.getData` | conf_k3, conf_k5, queue |
| `buidlingextension.resEffect` | res_effect |
| `castle.data` | castleLv, giftIds, time |
| `castleLevelUp.getLevel` | castlelevel |
| `cemetery.get.info` | kingdomCemetery, beforeDead, activity, userCemetery, quickNeed, countDown |
| `chat.room.invitee` | invitee |
| `check.result` | success |
| `civilization.prestige.info` | civilization_prestige_max, prestigeLev, prestigeExp, civilizationValueLimit, civilization_score, prestiges |
| `civilizationCastle.info` | def, maxAidSoldierCount, maxMarchSoldierCount, resourceNum, output, allianceId |
| `cmd.finishinit` | success |
| `cmd.ping` | serverNowTime |
| `contact.get.server.current` | contactList |
| `convoy.activityData` | data |
| `convoy.login` | convoyData |
| `crossthrone.time` | success |
| `dailyQuest2025.data` | dailyTaskId2025, newWeekRewardList, curReward, weekEndTime, rewardList, dailyQuest |
| `directUpgrade.data` | activityArray |
| `dragon.playoff.info` | success |
| `drawNew.info` | pools |
| `featureStateChange.data` | feature |
| `festivalview.data` | maxLevel, unlock, openBoxCfg, level, noticeHistoryArray, boxItemCount |
| `formation.getData` | uid, numOrder, level, typeOrder, percent, lvOrder |
| `formationTrain.bag` | freeTimes, score, pageCount, totalPage, pool, updateTime |
| `gem.getDigView` | curTimes, rare_show, redPoint, noticeArray, noticeHistoryArray, leftFreeTimes |
| `generalBP.data` | start, end, list |
| `general_choice.data` | rewardId, dataList, time |
| `get.clash.server.list` | clashServerList, groupId |
| `godGift.info` | finishTime, item, rewardCount, helpMax, canTwice, signCount |
| `heaven.task.info` | tasks |
| `heroBadge.badgeList` | list |
| `itemcollection.data` | collectedItemStr, shieldedItemStr |
| `kingdom.officers` | kingdomName, thronePic, banner, officers |
| `kingdomBiography.info` | biographies |
| `kingdomtask_new.data` | stageBuffArr, stageArray |
| `lordTask.data` | task_arr, curProgress, stages, awardIndex, rewards |
| `luckyday.effect` | success |
| `magic.effectList` | magicEffectCdTime, magicEffectList, skillList, magicAtlasEffectList, magicStarEffectList, magicWearInfo |
| `magic_weapon.data` | magicWeaponList |
| `mall.info` | shoppingMallCurrency, shoppingMall |
| `matchAct.info` | nextFreeTime |
| `medal.list` | medal |
| `miraclestone.data` | newRewardNum, returnExchangeIds, alreadyGetNum, lastRewardMirStoneTime, collectNum, isBoughtMirStoneVIP |
| `monthlySign.info` | multiDays, rewardObj, days, leftLostSignTimes, day2ItemIdStr |
| `newBoat.data` | ships, shipLimit |
| `newHeaven.info` | unlockGeneralNum, exploreNum, unlockDragonNum, curCrystal, sky_city_guide, chooseRewards |
| `newServerPower.info` | base_now, sky_piea_now, tech_config_max, tech_max, building, building_config_max |
| `nfight.data` | restTime, sumScore, actId, maxScore, actInfos, shopScore |
| `nightPet.list` | power, list |
| `oneKeyLoad.data` | cost, loadData |
| `overview_new.data` | queueList, noOpenList |
| `permitCommandInfo` | success |
| `redPackets.rvd.id` | records |
| `relic.getRelicList` | groupIds, buildingList |
| `scanctuary.data` | haveUserData, subState, mainState, mainBeginTime, mainEndTime, season  |
| `science.data.cond` | arrays |
| `science.data.init` | allianceScience, science, civilization_science |
| `score.login` | success |
| `shadowDragon.data` | dragons |
| `show.status.item` | statusItems, extraStatus |
| `skill.state.get` | conVal, km, kmsg, uss, khis, kss |
| `skin.effect_new` | new_enchant_skills |
| `skin.introduction` | skills, can_dress, avatar_id, level, enchant_skills, base_skills |
| `soldierHelp.info` | state |
| `stat.tt` | success |
| `story.task.info` | section, storyTaskList |
| `strengthen.info` | blessCost, transfer, blessBuffId, blessCount, count, blessTotal |
| `tactics.getData` | generalId |
| `treasuremap.info` | remainTimes, items, status |

## 二、只读命令 — 返回业务错误 6 条

| 命令 | errorCode | 判定 |
|---|---|---|
| `chat.get.new.mails` | E000000 | 参数值/游标依赖,待查 |
| `chat.get.system.mails` | E000000 | 参数值/游标依赖,待查 |
| `daily.quest.ls` | 102192 | **与 App 实测一致** —— 该账号/时段的服务端正常业务状态,非参数问题 |
| `dragon.battle.info` | 102192 | **与 App 实测一致** —— 该账号/时段的服务端正常业务状态,非参数问题 |
| `hero.introduction` | 102192 | **与 App 实测一致** —— 该账号/时段的服务端正常业务状态,非参数问题 |
| `worldboss` | 103864 | **与 App 实测一致** —— 该账号/时段的服务端正常业务状态,非参数问题 |

## 三、只读命令 — 超时 0 条

## 四、写操作 — 已实测成功

| 命令 | 参数 | 响应 | 副作用 |
|---|---|---|---|
| **`queue.ccd`** | `qUUID`/`itemUUID`/`isGold`/`itemCount`/`queueId`/`queueType`/`goldcost` | `finished:true` + `remainGold` + `totalTime` | **会立刻完成主城建造队列**(实测: 12.6h→0, 金币 48035→47460) |
| `monthlySign.sign` | 无 | `reward[]` | **会签到**(金币 211508×20000) |
| `monthlySign.claimMultiRewards` | `multiDays`(INT) | 奖励明细 | 会领月卡多日奖励 |
| `lordTask.reward.process` | `index`(INT) | 奖励明细 | 会领领主任务奖励 |
| `lordTask.reward.task` | `taskId`(STRING) | 奖励明细 | 会领领主任务奖励 |
| `save.phone.device` | `phoneDevice` / `batteryStates` | `{"success": true}` | 无(纯设备上报) |
| `resource.client.reward.get` | `rewardId` | `award[]` 逐项奖励明细 | **会领奖**(小号已验证,领后签到状态变化) |
| `resource.client.reward.getmulti` | `rewardIds`(`;` 分隔) | `rewardsObj` 每个 id 的 award | **会批量领奖** |
| `trigger.activity` | `request_flag` / `type` | E000000(参数待调) | 可能有副作用,**未成功前别乱试** |

### 4.1 `queue.ccd` = 主城建造队列加速（已实测生效）

```jsonc
{
  "qUUID":     "f2bb9577d6e1409a9688b22ffbc2a6c0",  // STRING 队列 uuid
  "itemUUID":  "",                                   // STRING 加速道具 id，空 = 用金币
  "isGold":    1,                                    // INT    1 = 用金币
  "itemCount": 1,                                    // INT    道具数量
  "queueId":   "1",                                  // STRING qid
  "queueType": "1",                                  // STRING 1=建造队列 2=造兵队列
  "goldcost":  "0"                                   // STRING 上报的金币消耗
}
```

- `qUUID` 取 `build.info` → `buildingQueue[].uuid`（**队列** uuid），
  **不是** `buildingQueue[].itemObj.uuid`（建造物 uuid）——用错会一直 `E000000`。
- `queueId` / `queueType` / `goldcost` **三个字段缺任一 → `E000000`**，且必须是**字符串**。
- 队列已完成后重复调用 → `E100179`（状态不允许）。

#### 4.1.1 用加速道具（推荐，不烧金币）—— **已实测跑通（直连，非 App）**

```jsonc
{
  "qUUID":     "9f993a6425a64d6cb48d9289a628ecc5",  // STRING 队列 uuid
  "itemUUID":  "4600cedc8e8a43aeaa5aefba97b7bfa7",  // STRING 道具**实例** uuid(32位hex)
  "isGold":    0,                                    // INT    0 = 用道具
  "itemCount": 1                                     // INT    道具数量
}
```

**实测证据**（2026-10-23，直连）：

```json
{"count": 39919, "itemId": "200201", "remainGold": 47460, "finished": false,
 "type": 1, "uuid": "9f993a6425a64d6cb48d9289a628ecc5", "qid": 1,
 "totalTime": 491086044, "startTime": 1792750070271, "endTime": 0}
```

| 检验点 | 结果 |
|---|---|
| 道具消耗 | `count` **39920 → 39919**（用掉 1 个 200201 通用 5 分钟）✓ |
| 金币 | `remainGold` **47460 未变** —— **没有烧金币** ✓ |
| 道具回显 | `itemId: "200201"` ✓ |
| 目标队列 | `uuid` = type=1 造兵队列 ✓ |

**⚠️ 三处字段名别用错（响应回显证实）**：

- 请求里道具数量 = `itemCount`；**响应**里回显的是 `count`
- 请求里道具实例 = `itemUUID`；**响应**里回显的模板 id = `itemId`
- 响应里 `totalTime` **不因加速而改变**（仍是 491086044）—— 加速是**时间抵扣**，不是重置 totalTime

**⚠️ `itemUUID` 是道具实例 uuid（32 位 hex），不是配置里的数字道具 id。**
`speedup-items.json` 里的 `200201` / `200224` 是**道具模板 id**（配置表 `ItemSpec.id`），
**不能直接填进协议**；协议要的是背包里该道具条目的**实例 uuid**，
两者对应关系见 `speedup-owned.json`（背包快照，含 uuid / count / type2 / 时长）。

**⚠️ 字段集随场景变**：

- **造兵加速只发 4 个字段**（qUUID / itemUUID / isGold / itemCount）—— 上面的实测配方
- **主城建造发 7 个字段**（多 `queueId` / `queueType` / `goldcost`）
- → **队列类型由 `qUUID` 自身决定**，不靠 `queueType`

#### 4.1.1.1 队列 uuid 从哪来：登录后服务端的 `init` 推送

直连登录后，服务端会主动推一帧 `cmd=init`，载荷在混淆键里（如 `rlQW45Y`），
用会话密钥解开即可（86 个键）：

```python
from cok_sfs import decode_params
o, mode, raw = decode_params(bytes.fromhex(混淆键), 会话密钥)
queues = o["queue"]      # 25 条
```

每条：`{itemObj, totalTime, startTime, updateTime, endTime, type, uuid, qid, isHelped}`

- **`queue[].type` = 队列类型**：`0`=建造队列、**`1`=造兵队列**、`2`=行军、`9`=联盟…
- `totalTime > 0 && startTime > 0` → **进行中**（可加速对象）

> 收推送时 **recv 超时不要 break，要 continue** —— 推送可能延后到，25 秒内通常能收到。

#### 4.1.1.2 开箱工具 `cok_speedup.py`

```bash
# 只列队列(来自 init 推送)
python3 cok_speedup.py --list

# 用 1 个通用 5 分钟道具(200201)加速进行中的造兵队列
python3 cok_speedup.py --item 200201

# 用 3 个; 指定队列类型(1=造兵 0=城建)
python3 cok_speedup.py --item 200201 --count 3
python3 cok_speedup.py --queue-type 0 --item 200215

# 用金币(实扣, 默认不用)
python3 cok_speedup.py --gold
```

#### 4.1.2 加速道具有很多种 —— 怎么选对？

**三个字段各管一件事**：

| 字段 | 作用 | 取值来源 |
|---|---|---|
| `queueType` | 加速哪条队列 | `1`=建造，`2`=造兵（**造兵场景实际不发此字段**） |
| `qUUID` | 具体是哪个功能（主城/联盟/科技/治疗/造兵…） | 目标队列的 uuid |
| 道具 `type2` | 道具本身适不适用 | 服务端按道具 type2 校验 |

**选型结论**：主城建造 ⇒ `type2 ∈ {7 城建专用, 1 通用}`；造兵 ⇒ `type2 ∈ {3 造兵专用, 1 通用}`；
**`type2=1` 通用道具最省心**（两类队列都能用）。

**城建专用（type2=7，10 个）**：`200229`(1分) `200215`(5分) `200251`(10分) `200252`(15分)
`200216`(2时) `200253`(12时) `200254`(1天) `211523`(3天) `211524`(7天) `211525`(15天)

**通用（type2=1，18 个）**：`200224`(1分) `200201`/`200222`(5分) `200235`(10分) `200236`(15分)
`200200`/`200223`/`209200`(1时) `200202`(8时) `200231`/`200237`(12时) `200232`(16时)
`200233`/`200238`(1天) `200234`(32时) `211511`(3天) `211512`(7天) `211513`(15天)

> ⚠️ `type2` 为 15/16/17/25/26/28/30/32/33/34/37/38/39/50/58/61/98/99 的是**其它用途道具**
> （联盟任务道具等），`ItemSpdMenu` 未定义，**不是加速道具**。

**尚未打通的最后一环**：直连要自己加速，需要
① 目标队列 uuid、② 背包里加速道具的**实例 uuid**。
① 对主城建造队列可用 `build.info`→`buildingQueue[].uuid` 拿到；
造兵队列 uuid 与道具实例 uuid 的**服务端下发接口尚未定位**
（`itemcollection.data` 只是收藏列表、返回空；`mall.info` 只有商城条目）。

## 五、参数类型很关键

服务端对参数类型敏感: 同一字段用 STRING 传会返回 `E000000`,用 INT/LONG 就正常。
客户端会自动按 `command-catalog-typed.json` 里的类型编码,无需手动指定。

**错误码读法**:

| 错误码 | 含义 |
|---|---|
| `E000000` | 参数类型/结构错(字段名拼错、类型错、缺必需字段) |
| `E000004` / `102192` / `103864` / `164317` / `10200062` / `E100159` / `E100179` | 类型对,但业务状态不满足(未达成/已领过/已完成/活动未开启) |
| 超时(无响应) | **命令名不存在** 或 缺必需参数导致服务端静默忽略 —— 不能单独据此下结论 |

## 六、文件说明

- `command-catalog.json` —— 从 App 抓包复原的 101 条命令 + 真实参数(纯值)
- `command-catalog-typed.json` —— **带 SFS 类型**的参数目录(客户端默认按它编码),844 条
- `readonly-commands.json` —— 本次批量验证的逐条结果
- `probe_readonly.py` —— 批量验证脚本(自动排除写操作)
- `command-names.json` —— **757 条命令名**全集(从 Lua 的 `utils.requestServer(...)` 调用提取)
- `command-names-native.json` —— **1246 条命令名候选**(从 device 版 `libgame.so` 字符串表提取,形态过滤后 1171 条为目录新增;**未逐条实测**)
- `speedup-items.json` —— **加速道具速查表**(服务端下发道具配置解析; type=2 加速道具 × type2 分组)
- `speedup-owned.json` —— **背包加速道具实例快照**(itemId → 实例 uuid / count / type2 / 时长)
- `cok_speedup.py` —— **加速工具**: 列出队列(init 推送) + 用道具/金币加速
- `build.info` / `build.upgrade` 字段表 —— 见报告 §6.13.3
