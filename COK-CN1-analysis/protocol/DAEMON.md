# COK 直连常驻监控器

脱离 App,持续跟踪游戏状态;可自动签到、自动领奖、推送告警。

```bash
cd ~/workspace/me/cok/COK-CN1-analysis/protocol

python3 cok_daemon.py                          # 默认轮询 6 项, 每 5 分钟
python3 cok_daemon.py --interval 60             # 60 秒一轮
python3 cok_daemon.py --once                   # 只跑一轮
python3 cok_daemon.py --json                   # 机器可读(每行一个 JSON)
python3 cok_daemon.py --log /tmp/cok.log       # 追加日志
python3 cok_daemon.py --watch dailySign boss   # 只看指定项
python3 cok_daemon.py --auto-sign              # 自动每日签到(幂等)
python3 cok_daemon.py --account-device         # 从设备自动读账号与服务器地址
python3 cok_daemon.py --claim                  # 自动领奖(有副作用)
python3 cok_daemon.py --speedup                # 用加速道具加速主城建造队列(有副作用)
python3 cok_daemon.py --webhook <URL> --webhook-type wechat   # 推送到企业微信/钉钉
```

## 账号与服务器地址：自动从设备读取

不需要手工填 token —— `cok_account.py` 直接读 App 的 SharedPreferences：

```bash
python3 cok_account.py                    # 打印读到的参数
python3 cok_account.py --write acc.json   # 导出账号文件
python3 cok_daemon.py --account-device    # 常驻工具直接用设备账号
```

读到的字段：`pfId` / `platformToken`（渠道 roleid）、`gameUid`、`deviceId`、`uuid`、
`buildCode`、`signCode`、`zn`，以及**游戏服地址** `host` + `port`
（`txaia-cok.elexapp.com:32231`，用域名不怕 IP 轮换）。

## 前置条件

**同账号双开会被服务端断开**,所以跑脚本前必须停掉 App:

```bash
adb shell am force-stop com.hcg.cok.nearme.gamecenter
```

跑完之后再把 App 拉起来即可。

## 监控项

| 名称 | 命令 | 提取内容 |
|---|---|---|
| `dailySign` | `monthlySign.info` | 今日是否已签、已签日期、剩余补签次数、月卡档位与发放日、每日奖励道具 |
| `dailyQuest` | `dailyQuest2025.data` | 周任务积分、可领周奖励、周期结束时间、已达成的日常任务 |
| `lordTask` | `lordTask.data` | 领主任务进度、档位、已领档位数、可领奖励、未完成任务 |
| `storyTask` | `story.task.info` | 章节、已完成任务的奖励 id、任务数 |
| `boss` | `allianceNewBoss.bossMainInfo` | 每个联盟 boss 的在位状态与冷却结束时间 |
| `overview` | `overview_new.data` | 建造/队列进度、未开启项 |

## 输出语义

* **只在状态变化时输出**(状态指纹对比),不会每轮刷屏;
* 事件类型: `connected` / `started` / `state` / `sign` / `sign_skip` / `claim` /
  `claim_result` / `reconnect` / `error` / `stopped`;
* `state` 里带 `_server_date`,用的是**服务器时间**(UTC+8 换算今天),不受本机时区影响;
* `--json` 输出每行一个 JSON,便于接看板。

## 自动签到(`--auto-sign`)

* 命令:`monthlySign.sign`(无参),实现在 `game/WelfareIntegrate/signIn/integrateSignInCmd.lua`;
* **幂等**:先看 `monthlySign.info` 的 `days` 是否已含今天,已签则 `sign_skip`,不重复发;
* 成功会返回 `reward` 逐项奖励(实测当天签到拿到金币 211508 ×20000);
* `monthlySign.claimMultiRewards` 带 `multiDays` 参数(3 或 5),用于领月卡当天奖励,
  需要时手动发:`--cmd monthlySign.claimMultiRewards --params '{"multiDays":3}'`。

## 自动领奖(`--claim`)

领奖来源(按优先级合并去重):

1. `lordTask.data` 的 `rewards` 减去已领的 `awardIndex`
2. `dailyQuest2025.data` 的 `weekTaskRewardId2025`
3. `story.task.info` 中 `state==1` 的 `taskReward`

安全措施:

* **已领记忆**:领到实际奖励的 id 记在内存里,不再重复领;
* **单轮上限** `--claim-limit`(默认 5);
* **全局上限** `--claim-max-total`(默认 20,本次运行累计)。

> ⚠️ **领奖有真实副作用**:会消耗奖励次数/CD,服务端也可能对同一 id 重复发放。
> 建议先在自有小号上验证,`--claim-limit 1` 起步。

> ⚠️ `story.task.info` 的 `state==1` 表示**任务已完成**,**不等于"可领"** ——
> 实测领完 `254310` 后 state 仍是 1(多个任务可共用同一奖励 id)。
> 所以判定"可领"以领奖接口返回的 `award` 为准。

## 建造队列加速(`--speedup`)

* 命令:`queue.ccd`
  * **道具模式(默认)**: `{qUUID, itemUUID, isGold:0, itemCount:N}` —— **4 个字段, 已实测跑通**
  * 金币模式: `{qUUID, itemUUID:"", isGold:1, itemCount:1, queueId, queueType, goldcost}`
* **队列清单来自登录后服务端的 `init` 推送**(daemon 在 `connect()` 后立即抓, 含 uuid 与 type):
  `type` = `0`建造 / `1`造兵 / `2`行军 / `9`联盟…;`totalTime>0 && startTime>0` = 进行中。
* **道具实例 uuid** 取自 `speedup-owned.json`(背包快照: itemId → uuid/count/type2/时长)。
  协议里填的是**实例 uuid**,不是配置表的数字道具 id。
* 加速对象按 `--speedup-queue-type` 选(默认 `1` = 造兵队列)。
* 没有符合条件的进行中队列时安全跳过。

```bash
# 默认: 用 1 个通用 5 分钟道具(200201)加速进行中的造兵队列
python3 cok_daemon.py --account-device --once --speedup --watch buildQueue

# 指定道具与数量
python3 cok_daemon.py --account-device --once --speedup --speedup-item 200208 --speedup-count 3

# 换成城建队列(type=0)
python3 cok_daemon.py --account-device --once --speedup --speedup-queue-type 0 --speedup-item 200215

# 显式用金币(会实扣金币)
python3 cok_daemon.py --account-device --once --speedup --speedup-gold
```

**实测证据**(2026-10-23, 直连, 小号):
`count` 39920→39919、`remainGold` 47460 **未变**、`itemId:"200201"` 回显、`errorCode: null`。

加速道具 id 与时长对照表见 `speedup-items.json`(`type=2` 加速道具, `type2=7` 主城 / `1` 通用 / `3` 造兵 …);
账号当前持有的实例 uuid 见 `speedup-owned.json`。

> ⚠️ **加速有真实副作用**:会消耗加速道具(或金币),并**立即完成**该队列。
> 道具路径与金币路径**均已实测成功**。

## 被攻击自动开保护罩(`--autoshield`)

**机制**：服务端主动推送(push)帧 → 客户端收集 → 命中触发名 → 判断罩状态 → 需要时才开。

* 动作:`onekeybuff.use {type: 槽位号, coverOld: 是否覆盖旧罩}`
  (参数取自 `OneKeyBuffManager.lua` 的 `putParam` 明文)
* **规格不靠参数区分** —— `onekeybuff.use` 只传槽位号,开哪种规格由**槽位里放的道具**决定。
  保护罩 = "战争守护", 共 6 种规格(1时/8时/24时/3天/7天/30天),见 `shield-specs.json`。
  要换规格就用 `onekeybuff.save {statusList, type}` 改写槽位内容。
* **服务端自带冷却**: 冷却期内重复开罩会被拒(游戏文案"无法使用，战争守护冷却中"),
  所以本地判断只是为了省一次请求。
* ⚠️ **自己侦查或进攻敌人会让守护自动失效**(游戏内规则),自动化**不能在进攻/侦查窗口内开罩**;
  但**被别人侦查不会让守护失效**。
* **槽位**是用户自建的"一键 buff 预设"(1/2/3),用 `onekeybuff.get` 可查每个槽位存了哪些道具:
  ```json
  {"backList":[{"statusList":[],"name":"","type":1},
               {"statusList":[],"name":"","type":2},
               {"statusList":[],"name":"","type":3}]}
  ```

### 罩状态:有罩就不重复开

保护罩开完是有持续时间的,**被连续攻击时不能每次都重开**(会瞬间烧光道具)。
daemon 维护 `shieldEndTime`(当前罩到期时间, 毫秒):

| 触发类别 | push 名 | 行为 |
|---|---|---|
| **强制续罩** | `push.world.injured`(部队被攻击) | **无视已有罩直接开** —— 被攻击说明罩已经扛不住了 |
| 条件触发 | `push.world.cannon.injured` / `push.world.march.fail` 等 | **只在无罩/罩已过期时才开** |

* 状态来源:`onekeybuff.get` 响应的 `shieldEndTime`(服务端只在有罩时才带这个字段);
  收到 `push.protect.time` 会重新拉一次刷新。
* 兜底限流:`--shield-cooldown`(默认 600 秒)。

```bash
# 被攻击后自动续罩(默认行为)
python3 cok_daemon.py --account-device --autoshield

# 只监听"部队被攻击", 且视为强制续罩
python3 cok_daemon.py --account-device --autoshield \
    --shield-trigger push.world.injured --shield-trigger-force push.world.injured

# 用槽位 2, 最短间隔 30 分钟
python3 cok_daemon.py --account-device --autoshield --shield-slot 2 --shield-cooldown 1800
```

> ⚠️ **前置条件**:槽位里要预先放好保护罩道具(在 App 的 OneKeyBuff 界面设置一次,
> 或用 `onekeybuff.save {statusList, type}` 直连写入),且账号要有该道具。
> **副作用**:开罩消耗道具;被攻击瞬间续罩属于高频写操作,**风控上比只读敏感**,
> 建议先设长冷却观察。

> **注**:客户端原本会**静默丢弃** push 帧(`_call_once` 里"推送帧等, 忽略并继续等"),
> 已改为收集到 `client.pushes`,daemon 通过 `client.take_pushes()` 取用。

## 告警(`--webhook`)

规则(用 `--alert-rules` 选,默认全开):

| 规则 | 触发时机 |
|---|---|
| `sign` | 今日从"未签"变"已签";或首次发现今天未签;或自动签到失败 |
| `claim` | 领奖拿到实际奖励 |
| `task` | 出现新的可领周任务/领主任务奖励 |
| `boss` | 联盟 boss 状态变化 |
| `error` | 连接异常 / 重连 |

载荷格式(`--webhook-type`):

* `generic`(默认):`{"kind","title","text","value","ts"}`
* `wechat` / `dingtalk`:`{"msgtype":"text","text":{"content":"标题\n正文"}}`

示例(企业微信机器人):

```bash
python3 cok_daemon.py --webhook 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=XXX' \
                      --webhook-type wechat --auto-sign
```

推送失败不会中断监控,只在本地打印 `[alert:alert_error]`。

## 已知服务端行为

* 新连接登录后,服务端会**丢弃第一条加密业务请求**,客户端已内置自动重发;
* 业务响应前可能夹着 `push.*` 推送帧,客户端会跳过继续等目标命令;
* 连接异常会自动重连(重新走 bin 握手 → 登录 → 派生密钥);
* 长时间无业务流量时服务端可能断开,每轮会先发 `cmd.ping` 保活;
* `monthlySign.sign` 服务端允许**重复发放**同一签到奖励,所以务必用 `--auto-sign`
  的幂等判断,不要手动反复签。
