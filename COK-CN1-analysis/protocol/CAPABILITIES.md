# COK 直连能力盘点（2026-10-23 实测口径）

> 口径：**实测跑通** = 有服务端真实响应作为证据；
> **已定位未实测** = 命令名/参数已从二进制或 App 真实请求反出，但没在服务端跑过；
> **未打通** = 只知道存在/知道接口，拿不到可用数据。

---

## 一、基础设施：完全脱离 App 直连游戏服 ✅

| 能力 | 状态 | 证据 |
|---|---|---|
| bin 握手 | ✅ | 重建帧与线上真实帧**逐字节一致** |
| 登录（37 参数） | ✅ | 登录响应明文可解 |
| 登录请求 4 个本地字段算法 | ✅ | `signCode` / `buildCode` / `SecurityCode` / `cc` 全部本地可算，与线上同值 |
| 会话密钥派生 | ✅ | `md5_hex(登录响应 id 前缀)`，端到端 71/71 解密成功 |
| 任意命令发送 + 响应解码 | ✅ | 请求/响应双向全链路通 |
| 账号自动读取 | ✅ | 直读设备 SharedPreferences（渠道 token / gameUid / deviceId / 服务器地址） |
| 服务器地址用域名 | ✅ | `txaia-cok.elexapp.com:32231`，不硬编码 IP |

---

## 二、只读查询：76 条命令返回真实数据 ✅

```
cmd.ping                   overview_new.data          monthlySign.info
allianceNewBoss.bossMainInfo  al.rank                 kingdom.officers
achieve.ls                 act.ls                     itemcollection.data
gem.getDigView             stat.tt                    science.data.cond
festivalview.data          generalBP.data             formationTrain.bag
accountLock.getUnlockView  mall.info                  get.clash.server.list
kingdomtask_new.data       castleLevelUp.getLevel     cemetery.get.info
civilization.prestige.info oneKeyLoad.data            alquick.data
buidlingextension.resEffect strengthen.info           kingdomBiography.info
treasuremap.info           soldierHelp.info           permitCommandInfo
magic.effectList           science.data.init          score.login
featureStateChange.data    scanctuary.data            newBoat.data
auction.getView            miraclestone.data          newServerPower.info
shadowDragon.data          convoy.login               convoy.activityData
dailyQuest2025.data        cmd.finishinit             story.task.info
civilizationCastle.info    formation.getData          skin.introduction
skill.state.get            general_choice.data        castle.data
heroBadge.badgeList        nightPet.list              matchAct.info
relic.getRelicList         tactics.getData            skin.effect_new
magic_weapon.data          godGift.info               directUpgrade.data
lordTask.data              crossthrone.time           show.status.item
medal.list                 drawNew.info               nfight.data
newHeaven.info             aw_formula.getData         dragon.playoff.info
contact.get.server.current redPackets.rvd.id          chat.room.invitee
heaven.task.info           al.task.record             check.result
luckyday.effect            al.donate.res.rank.day …
```

另有 **4 条**返回业务状态错误（命令存在、条件未达成，非缺陷）：
`daily.quest.ls` / `hero.introduction`（102192）、`worldboss`（103864）、`dragon.battle.info`（102192）。

**命令名规模**：Lua 侧 757 条 → 类型目录 **844 条** → native 二进制侧另有 **1246 条候选**（未逐条验证）。

---

## 三、写操作：8 类实测成功 ✅

| 命令 | 参数 | 说明 |
|---|---|---|
| **`queue.ccd`** | `qUUID`/`itemUUID`/`isGold`/`itemCount` | **建造 & 训练队列加速**（道具或金币，见 §五） |
| `monthlySign.sign` | 无 | 每日签到（实测领到金币 211508×20000） |
| `monthlySign.claimMultiRewards` | `multiDays`(INT) | 月卡多日奖励 |
| `lordTask.reward.process` | `index`(INT) | 领主任务阶段奖励 |
| `lordTask.reward.task` | `taskId`(STRING) | 领主任务奖励 |
| `resource.client.reward.get` | `rewardId` | 通用领奖（返回 award 明细） |
| `resource.client.reward.getmulti` | `rewardIds`(`;` 分隔) | 批量领奖 |
| `save.phone.device` | `phoneDevice`/`batteryStates` | 设备上报（无害） |

> ⚠️ 服务端**允许重复发放同一奖励** → 必须靠已领记忆做幂等（daemon 已实现）。

---

## 四、常驻监控器 `cok_daemon.py` ✅

| 能力 | 参数 | 说明 |
|---|---|---|
| 7 项监控 | `--watch` | `dailySign` `dailyQuest` `lordTask` `storyTask` `boss` `overview` `buildQueue` |
| 状态指纹去重 | 默认 | 只在变化时输出 |
| 自动签到 | `--auto-sign` | 幂等（查 `days` 再决定） |
| 自动领奖 | `--claim` | 已领记忆 + 单轮上限 + 全局上限 |
| **自动加速** | `--speedup` | 道具优先；`--speedup-item` / `--speedup-count` / `--speedup-queue-type` / `--speedup-gold` |
| 告警推送 | `--webhook` | 通用 / 企业微信 / 钉钉；规则 `sign` `claim` `task` `boss` `error` |
| JSON / 日志 | `--json` `--log` | 机器可读 / 追加落盘 |

---

## 五、加速系统（完整闭环）✅

**命令**：`queue.ccd`

```jsonc
// 道具模式（推荐，不烧金币）—— 4 个字段，实测跑通
{"qUUID":"<队列uuid>","itemUUID":"<道具实例uuid>","isGold":0,"itemCount":1}

// 金币模式 —— 7 个字段，实测跑通（主城建造）
{"qUUID":"…","itemUUID":"","isGold":1,"itemCount":1,
 "queueId":"1","queueType":"1","goldcost":"0"}
```

**实测证据**（两次独立验证）：道具 `count` 39920→39918、金币 `remainGold` 47460 **未变**、
道具回显 `itemId:"200201"`、`errorCode: null`。

**配套能力**：

| 能力 | 来源 |
|---|---|
| 队列清单（25 条，带 `uuid` + `type`） | 登录后服务端的 **`init` 推送**（混淆键里用会话密钥解） |
| 加速道具全表 **471 个 / 35 类** | 服务端下发的道具配置 `files/database.local.xml`（`type=2`，`type2=ItemSpdMenu_*`） |
| 背包持有快照 **15 种** | App 侧探针抓的 `items`（`itemId` → 实例 uuid / count） |
| 道具适用规则 | `type2`：0 拆除 / 1 **通用** / 2 行军 / 3 造兵 / 4 治疗 / 5 陷阱 / 6 科技 / 7 城建 / 8 锻造 / 9 联盟 / 10 造材料 / 11 新科技 / 12 戒律大厅 / 13 文明堡垒分城 / 14 阵法 / 19 先祖之魂 / 21 军械库 / 22 士兵改造 / 23 外来文明科技 |
| 开箱工具 | `cok_speedup.py`（`--list` / `--item` / `--count` / `--queue-type` / `--gold`） |

**队列 type**：0 建造 / 1 造兵 / 2 行军 / 9 联盟 / 12 戒律 / 43 联盟…；`totalTime>0 && startTime>0` = 进行中。

---

## 六、逆向工具链（可复用）✅

| 工具 | 作用 |
|---|---|
| `elf_xref.py` | ELF64 arm64 里做 `ADRP+ADD` 字符串引用扫描（纯位运算，不依赖反汇编器）→ **替代盲试命令名** |
| `disasm_strings.py` | capstone 反汇编一段并列出引用到的所有字符串 → 拿请求字段名与类型 |
| `capture_full2.js` | frida 探针：hook XOR 引擎拿**双向明文 + 会话密钥**，配合 wire 帧可解出任意命令的完整请求/响应 |
| `parse_plain.py` | 解析探针明文（请求直接 parse，响应先 zlib） |
| `decode_wire2.py` | 用探针读出的密钥解 wire 帧 → 命令名 + params 明文 |
| Ghidra 脚本 | `FindString` / `FindXref` / `FindCallers` / `DecompileAt` / `ReadData` |

---

## 七、已定位但未实测 ⚠️

| 项 | 状态 |
|---|---|
| `build.upgrade` | 8 字段已反出（`buildingId`/`level`/`star`/`process`/`position`/`costTime`/`gold`/`isInstant`），未跑过（会消耗资源升级建筑） |
| `queue.open` / `queue.cancel` / `queue.rent` / `queue.tool` / `queue.one.key` | 命令存在（`E000000`），参数未知 |
| `civilizationQueue.speedQueue` / `finishQueue` / `cancelQueue` | 内城文明队列；字段名 **`qUuid` / `itemUuid`（小写 u！）** / `isGold` / `itemCount` / `mark` |
| `civilizationCastle.info` / `upgradeBuilding` / `createBuilding` / `destroyBuilding` / `getBuildingView` / `addNewPos` | 命令存在，参数未知 |
| `build.ccd` / `build.collect` / `build.done` / `build.move` | 命令存在，参数未知 |
| 联盟 / 科技 / 治疗 / 陷阱 / 新科技 / 军械库 等队列的加速 | 道具 `type2` 已知，但**对应命令名未知**（不一定都是 `queue.ccd`） |
| 1042 条 native 候选命令 | 只有名字，无参数 |

---

## 八、还没打通 ❌

| 项 | 现象 | 影响 |
|---|---|---|
| **背包 `items` 接口直连** | `cemetery.get.info` 返回 474 条背包（`itemId`/`uuid`/`count`），但**直连调它服务端主动踢连接**（重试、先 ping、换顺序均无效） | 道具实例 uuid 目前只能用 App 侧抓的快照 → **「直连自动找道具」差这一步** |
| 响应混淆键命名规则 | 已能解开，规则未明 | 无影响 |
| 渠道 token 续期 | 读的是 App 现有 token | 长期运行需解决（账号体系问题，非协议问题） |
| `deviceId` / `uuid` 生成规则 | 未逆（直连端可自造并保持稳定） | 换设备需复现 |

---

## 九、明确的风险

1. **风控**：`_cok_` 序号 / `cmdBaseTime` / `newbasekey` 说明服务端做重放与时序校验；
   模拟客户端的频率、来源 IP、设备指纹异常可能被判定为外挂。
2. **重复发放**：服务端允许同一奖励重复领 → 必须幂等。
3. **写操作不可逆**：领奖消耗次数/CD；加速**立即完成**队列并消耗道具/金币。
4. **地址会变**：IP/端口随区服与负载轮换（已改用域名）。
5. **只读 ≠ 自动化**：只读查询与自动化操作是两件事，后者可能违反用户协议并触发封号。
