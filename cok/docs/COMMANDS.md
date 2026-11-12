# COK 游戏服直连命令清单(2026-11-11 实测)

全部经 `cok_client.py` 直连真实服务器验证,响应字段为服务器真实返回。

```bash
cd ~/workspace/me/cok
python3 cok_client.py --cmd <命令名>                   # 单条
python3 cok_client.py --cmd <命令名> --params '<JSON>'  # 带参数
```

> 用前先停 App(同账号双开会被服务端断开):`adb shell am force-stop com.hcg.cok.nearme.gamecenter`

## 一、只读命令 — 实测成功 98 条

| 命令 | 返回字段(前几个) |
|---|---|
| `accountLock.getUnlockView` | locked |
| `achieve.ls` | list, stageRewardInfo |
| `act.ls` | act |
| `al.rank` | allianceTitle, rankName, allianceApply, list |
| `al.donate.rank.all` | donateRank (联盟捐献排行·总) |
| `al.donate.rank.today` | refreshTime, donateRank (联盟捐献排行·今日) |
| `al.donate.rank.week` | refreshTime, donateRank (联盟捐献排行·本周) |
| `al.donate.res.info` | res, resMax, item, num, stoneFactoryNum (联盟资源池) |
| `al.get.url` | success |
| `al.mission.show` | random, common, **alliance_sign_in**(联盟使命/日常 + 5 天联盟签到) |
| `al.point.find` | targetPoint (联盟成员点位) |
| `al.ref.list` | forces, list |
| `al.science.fresh` | low/mid/high × {Contribute, Num, Progress, Res, ResFlag} (捐献面板, 需 `scienceId`) |
| `al.shop.show` | alliancePoint, goods (联盟商店) |
| `al.task.get.available` | taskList, record, gold, nextGold, freequeue (可接的联盟任务) |
| `al.task.get.published` | taskList, leftRequestCount (已发布的联盟任务) |
| `al.task.get.detail` | publishName, acceptReward, publishUid, acceptStat (需 `taskUid`, 任务会过期) |
| `al.task.record` | freequeueTime, refreshCount, itemPublishCount, refreshTime, conditionTime, maxPublishRewardCount |
| `allianceNewBoss.bossMainInfo` | bossInfo |
| `alliance.recharge.getRank` | success (联盟充值排行) |
| `alliance.team.ls` | list, helplist (联盟集结) |
| `allianceMillitaryPower` | 联盟战力 |
| `alquick.data` | nextCallHelpTime |
| `mine.help.info` | result (我发出的求助; 不稳定, 有时 E000000) |
| `territory.check` | res, resMax, item (联盟领地/资源池) |
| `auction.getView` | gold, diamond, inActivity, endTime, list, globalList |
| `aw_formula.getData` | conf_k3, conf_k5, queue |
| `buidlingextension.resEffect` | res_effect |
| `cargo.open` | isOpen, isDouble (码头宝箱活动开关; 奖励明细在 init 推送的 cargo 字段) |
| `castle.data` | castleLv, giftIds, time |
| `castleLevelUp.getLevel` | castlelevel |
| `cemetery.get.info` | kingdomCemetery, beforeDead, activity, userCemetery, quickNeed, countDown |
| `chat.room.invitee` | invitee |
| `everydayexchange.data` | freeRewarded, freeReward, payRewarded, payReward, commonExchangeIds (福利中心·每日好礼) |
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
| `login.init` | qqq, **rlQW45Y**(混淆键; 解开是 133 键 / 95 万字节的整包数据, 其中 **`items` = 玩家背包**)。⚠️ 这个响应是**裸 zlib 流**, 见 §4.2 |
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
| `res.tile.find` | x, y (⚠️ **"没找到" 有两种空形态**, 见下面注释) |
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
| `userpayreward.newinfo` | currDay, configArray, processConfigArray, `<exchangeId>`:{isBuy,rewardDays,specialRewardDays,specialActivityOpen} (福利中心·龙之馈赠) |

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
| **`cargo.reward`** | **无参**(带任何参数都回 E100148) | `reward.goods[]` + `cargo`(新状态) + `isDouble` | **会领码头宝箱**(港口活动奖励位)。每日次数有限 |
| **`build.collect`** | `uuid`(STRING, `;` 分隔的**建筑实例 uuid**) | 资源快照(`food`/`wood`/`iron`/`stone`/`silver`…) | **批量收取资源**(秘银矿场/伐木场/铁矿场/农田)。对未知 uuid 宽容(只回快照不报错)。uuid 取自 `build.info` 的 `building[]` 数组 |
| **`sagatower.collect`** | `uuid`(STRING, `;` 分隔) | `refreshTime` + `uuid` | **批量收取科研石**(科研工坊)。实测传建筑实例 uuid 成功 |
| **`civilizationCastle.oneKeyCollect`** | **无参** | `itemArray[]`(itemId/itemNum) | **文明要塞一键采集**(实测领到 211508×8 / 212069×30 / 210090×6) |
| **`everydayexchange.reward`** | **无参** | `rewardArray` | **会领每日好礼的免费奖励**(福利中心·每日好礼)。每天一次 |
| **`userpayreward.newaccept`** | `exchangeId`(STRING) + `specialReward`(BOOL) **两个都要传** | `rewardArray` + 刷新用的 A 对象 | **会领龙之馈赠的每日奖励**(黑龙=760359)。每天一次; 缺参数回 E000000 |
| **`item.use`** | `uuid`(STRING, **道具实例 uuid**, 32 位 hex) + `num`(**SFS INT**) | `itemId` + `itemEffectObj`(如 `{"stamina":300}`) + `count` | **会消耗道具**(实测: 喝 1 瓶 200381 → 体力 +50)。见 §4.2 |
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

**道具实例 uuid 的来源 —— 已打通(2026-11-10)**: 命令 **`login.init`** 返回的
`items` 就是玩家背包(每条带 `itemId` / `count` / `uuid`), 详见 **§4.2**。
所以直连加速的最后一环不再是问题 —— 不需要手机 / frida / root。

### 4.2 `login.init` = 拉背包 + `item.use` = 用道具(2026-11-10 实测)

#### 4.2.1 `login.init` —— 直连拉全背包(只读)

```bash
python3 cok_client.py --cmd login.init
```

响应形状：

```
{"qqq": <keyId>, "rlQW45Y": "<30 万 hex>"}
rlQW45Y  ->  XOR(会话密钥) -> zlib -> SFS 对象(133 个顶层键 / 95 万字节)
其中 items = [{"itemId":"200381","count":40,"uuid":"94e0...","para1":"107","para2":"50"}, ...]
```

* **`items` 就是玩家背包**，每条带 `itemId` / `count` / `uuid`(道具实例 id) /
  `para2`(体力值) / `useDate` / `vanishTime`
* 道具是**堆叠**的(一个实例 `count=N`)，实例 uuid 在 count 用完前**稳定**
  ⇒ **拉一次缓存起来能长期用**
* 实测背包规模: `<uid-guopan>` → 770 件; `<uid-main>` → 515 件;
  `<uid-guopan-intl>` → 685 件

**⚠️ 三个坑**:

1. **这个响应是「裸 zlib 流」** —— 服务端**不发帧长度**，帧头 3 字节直接就是
   zlib 流的开头(`78 9c …`)。按长度字段读会读出 39936 而实际约 13 万字节，
   后面**所有帧全部错位**。
   ⇒ 必须解到 zlib 流自然结束才算一帧(见 `cok_client._read_zlib_stream`)。
2. **服务端会发 5 字节心跳帧**(`a8 00 02` + 2 字节载荷)。当压缩帧解会抛
   `zlib.error` —— 现在按心跳跳过。
3. **服务端丢弃新连接的首条业务请求** —— `login.init` 第一次常常超时，
   **重发一次**才有响应(`retries=1`)。扫命令时用 `retries=0` 会全部超时。

**耗时 40~50 秒**（响应 95 万字节）⇒ 只在真需要时拉一次，然后缓存。

实现: `cok_stamina.fetch_bag(client, uid)` →
缓存落盘 `accounts/<uid>.items.json`
(`{"updated": ts, "items": {"200381": {"uuid": "...", "count": 133}}}`)。

#### 4.2.2 `item.use` —— 用掉一个道具实例

```jsonc
{ "uuid": "<道具实例 uuid, 32 位 hex>", "num": <SFS INT> }
```

```python
from cok_sfs import TypedInt, SFS_INT
client.call("item.use", {"uuid": uuid, "num": TypedInt(1, SFS_INT)}, retries=1)
```

**实测响应**（真服，喝 1 瓶 200380）：

```json
{"itemId": "200380", "itemEffectObj": {"stamina": 300}, "count": 1}
```

体力 **290 → 300（+10）** —— 真的生效。

**三个必死的点**：

- `uuid` 是**道具实例 id**，不是模板 id —— 传 `"200381"` → `E000000`
- `num` **必须编码成 SFS INT**(`TypedInt(n, SFS_INT)`)，传普通 int → `E000000`
- uuid 不存在 → `E100166`(没有该道具)；数量不够 → `E100165`(道具数量不足)

#### 4.2.3 体力药水(自动打怪喝药用)

| 道具 id | 恢复体力 | 来源 |
|---|---|---|
| `200380` | +10 | 客户端道具表 `para` 字段 |
| `200381` | +50 | 同上 |
| `200382` | +100 | 同上 |

客户端配置 `data_config.auto_kill_monster.k1 = "200380;200381"`。

**已排除的路线**（别再试）：

| 路线 | 结论 |
|---|---|
| 服务端代喝药 `autoQueue.status {status:1}` | ❌ 需「自动打怪周卡」(客户端 k2=766437)，4 个账号全部 `E000000` |
| `autoQueue.data` | ✅ 可读(saveItems/useItems/status/lv/autoCount/force/format) |
| 商城买 `mall.info` / `mall.data` | ❌ 这 4 个号(497 条商品 / `mallId:"15"` 206 件)**不卖** 200380/200381/200382；换 mallId → `E000004` |
| `item.buy {id, num}` | 参数名是 **`id`**(传 `itemId` 报 `E000000`)，能返回 uuid，但买体力药水 → `E000000` |

**错误码速查**: `E100047`=体力不足 / `E100165`=道具数量不足 /
`E100166`=没有该道具 / `E000000`=参数错误 / `E000004`=对象不存在。

### 4.3 `res.tile.find` = 找野怪坐标 —— **"没找到" 有两种空形态**(2026-11-11 实测)

```jsonc
{ "type": 6, "level": <INT>, "NoRecord": 1 }   // type 6 = 普通怪
```

客户端 Lua(`game/command/IFFindResTileCmd.lua:handleReceive`)把「没找到」分成两种:

| 服务端返回 | 含义 | 客户端提示 |
|---|---|---|
| **x / y 字段缺失(None)** | **今日找怪次数用完** | 113228「今日剩余使用次数不足, 激活VIP可以无限制」 |
| **x == -1 或 y == -1** | 世界上没有这个等级的怪 | 113229「现在世界上没有您想寻找的资源点或者怪物」 |

⚠️ **两种都不是 errorCode**(errorCode 是空的), 所以**不能只看 errorCode 判断成功**。
之前本工具一律当成成功(`x=None`), 后面 `point_index(None, None)` 里 `int(None)`
抛 TypeError, **一次就把整个自动打怪循环带崩**(2026-11-11 修复)。

**找怪次数(每日)**:

* 服务端在 `login.init` 的 `world` 段里下发:
  `world.maxSearchCount` = 每日上限字段, `world.resSearchCount` = 已用次数
* ⚠️ **`maxSearchCount` 对 SVIP 账号也照样下发 6** —— 它**不代表**实际上限!
  **SVIP 无限找怪**(客户端提示 113230), 普通号 6 次(113228)。
  ⇒ **绝不能拿 `maxSearchCount` 当拦截阈值**(2026-11-12 教训: 拿它硬拦,
  把 SVIP 号打几轮就卡成「今日找怪次数已用完」)。**服务端才是唯一权威**。
* **每派一队消耗一次**; 次数**按天重置**(次日 `resSearchCount` 归 0)

**找怪类型枚举**(客户端 `game/WorldMapView/FindResTileViewV4_41.lua`):
`0木材 1粮食 2铁矿 3石头 4金币 5怪 6普通怪 7活动怪 8营地 9奇迹宝藏 10超级营地 …`

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
- `cok_stamina.py` —— **体力药水模块**: `fetch_bag`(拉背包) / `scan_potions` / `use_stamina_item` / 实例缓存读写
- `accounts/<uid>.items.json` —— **某账号的道具实例缓存**(itemId → uuid / count),由 `login.init` 拉背包后写入
- `build.info` / `build.upgrade` 字段表 —— 见报告 §6.13.3

## 七、渠道账号密码登录(纯 PC, 不需要手机/root/模拟器)

顶部网页账号徽章的 **🔑** 按钮, 或命令行:

```bash
# 账号密码 -> 完整可直连的游戏服凭据(pfId + gameUid + uuid + 区服 + buildCode)
python3 cok_channel_login.py <果盘账号> <密码> --make-account /tmp/acct.json

# 顺便写进账号库(多用户: --owner 归属)
python3 cok_channel_login.py <果盘账号> <密码> --make-account --save --label 小号A --owner alice

# 离线自证(回放归档 pcap, 不需要网络/账号)
python3 cok_channel_login.py --selftest

# 只列小号 / 建小号 / 选小号(需 --guopan-uid + --envelope)
python3 cok_channel_login.py --list-small   --guopan-uid 305273801 --envelope 'Login_...'
python3 cok_channel_login.py --create-small 新号名 --guopan-uid 305273801 --envelope 'Login_...'
python3 cok_channel_login.py --pick-small  <perGameId>  --guopan-uid 305273801 --envelope 'Login_...'

# 游戏服 HTTP: 按 pfId 解析角色(独立工具)
python3 cok_gamesvc.py --pf-id ewanqf:1084D654F5A7FB599158 --pf cn_ewanqf \
        --channel cn_ewanqf --package com.hcg.cok.ewanqf.guopan

# 回归: 每个号能否只凭 pfId 重建凭据并登录
python3 test_pfid_rebuild.py
```

**原理(三跳)**:

1. 果盘 HTTP `userapi.guopan.cn/gamesdk/140514`(XXTEA + protobuf):
   `subcmd 101` 取 salt → `MD5(salt+密码)` → `subcmd 102` 登录 → 响应 `f18.f5` = perGameId
   → `pfId = "ewanqf:1084" + perGameId`。
2. 游戏服 HTTP `gameservice/getserverlist.php`:
   `sig = md5(uuid + t + "@z4LugUwrDN0MqOJtzmHPK7Ss-k4taAUOZh1M3Yu9")`,
   `loginFlag=1` → 响应直接带 `gameUid / 账号uuid / zone / ip / port / buildCode / 角色名`。
   **角色按 pfId 查, 与请求里的设备 uuid 无关。**
3. 组装凭据 → 账号库 → 网页里切过去直接用。

⇒ **有 pfId 就能接管该账号**(不需要手机/root/官方转移通道; uuid 由服务端下发, deviceId 可随意)。
