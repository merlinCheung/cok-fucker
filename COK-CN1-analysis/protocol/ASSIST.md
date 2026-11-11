# 一键完成(CityAssist)—— 面板全清单与自动化

> 游戏内那个「一键完成」面板的完整解剖 + 直连自动化。
> 2026-10-31 实测(区服 2223, 账号 `<uid-guopan-intl>`)。

---

## 一、面板不是服务端数据

客户端 `game/city/CityAssistController.lua`:

```lua
function CityAssistController:getData()
    if self.v_xmlData == nil then
        self.v_xmlData = CCCommonUtilsForLua:getGroupByKey("territory_assist")
    end
    ...
    local _config = taskHandle[v.type] and taskHandle[v.type].config(v) or {}
```

⇒ 清单来自**客户端配置表** `territory_assist`,"能不能做/要花什么"由
`taskHandle[type].config()` 在本地算, 点一下再各自发各自的业务命令。
**没有一条统一的"一键完成"命令**, 要自动化只能逐类接。

## 二、游戏里那个按钮到底做了什么(2026-10-31 读透)

```lua
function CityAssistController:doTask()
    -- 执行：可顺序执行的任务
    for i,v in ipairs(self.v_data or {}) do
        for _,vv in ipairs(v.items or {}) do
            if vv.exeOrder == nil and vv.isOpen == 1 and vv.pass == nil then
                ...
                if taskHandle[vv.type] then
                    taskHandle[vv.type].doTask(vv)
                end
                return i     -- 一项做完再由 "CityAssistView:doTask" 接力下一项
```

⇒ **它不是一条协议命令, 是客户端的一次编排**: 遍历面板, 挑出
"已开启 + 没通过 + (进度未满 或 CD 已过)"的, 逐项调用该项自己的 `doTask`,
**串行**做完全部。

所以直连的正确做法就是**照这个顺序逐项发各自的命令** —— `cok_assist.run_all()`
就是这么做的, 不用一项项点。

## 三、面板 13 项

配置表 `territory_assist`(Group)共 13 条, 3 组:

| 组 | type | 名称 | 执行入口(lua) | 代价 | 本工具 |
|---|---|---|---|---|---|
| 试炼 | 1 | 英雄试炼 | HeroTowerCleanController | 道具 213575 + 金币 | ❌ 不自动 |
| 试炼 | 2 | 龙塔试炼 | `dragontower.quickbattle` | 体力 | ❌ 不自动 |
| 养成 | 6 | 普通研习 | MagicLuckDraw:reqLuckDraw | 道具 | ❌ 不自动 |
| 养成 | 7 | 高级研习 | MagicLuckDraw:reqLuckDraw | 道具 | ❌ 不自动 |
| 养成 | 8 | 普通招募 | hero recruit | **金币** | ❌ 不自动 |
| 养成 | 10 | 联盟宝藏 | 挖宝 | 体力 | ❌ 不自动 |
| 养成 | 11 | 献祭 | `alliancecivilization.sacrifice` | 联盟资源 | ❌ 不自动 |
| 养成 | 16 | 宝石挖掘 | `gem.dig` | 免费次数内 | 🟡 **暂未接入**(见下) |
| 收取 | 9 | 装卸货物 | `PortActController:startTimeRwd` | 无(港口奖励) | ➡️ 由**港口自动领取**规则覆盖 |
| 收取 | 12 | 文明结晶 | `civilizationCastle.oneKeyCollect` | 无 | ✅ 自动 |
| 收取 | 13 | 科研工坊 | `sagatower.collect` | 无 | ✅ 自动 |
| 收取 | 14 | 资源收取 | `build.collect` | 无 | ✅ 自动 |
| 收取 | 15 | 一键增产 | (native 层, lua 无实现) | ? | ❌ 未接入 |

> 客户端注释里另有 3=幸运转盘(废弃) / 4,5=精铁/水晶转盘 / 17=阵法演练,
> 但这几个**不在 `territory_assist` 配置表里**(本区服面板上不显示)。

### 四种 kind

| kind | 含义 | 项 |
|---|---|---|
| `free` | **无损** —— 只把已产出的结算入库, 不消耗任何东西, 领完就是 0(天然幂等) | 资源收取 / 科研工坊 / 文明结晶 |
| `cost` | **要烧金币/道具/体力** | 英雄试炼 / 龙塔试炼 / 普通研习 / 高级研习 / 普通招募 / 联盟宝藏 / 献祭 |
| `dock` | 由**港口自动领取**那条规则覆盖, 不重复跑 | 装卸货物 |
| `none` | 客户端没有可直连的实现(或服务端不收) | 宝石挖掘 / 一键增产 |

**手动「一键完成」**默认只跑 `free`; 勾上「连消耗项一起」会把 `cost` 里
**已在真服验证过的**也跑掉 —— 目前只有**龙塔试炼**
(`dragontower.quickbattle {dealObject:"auto"}`)。

其余 `cost` 项**参数虽已从客户端源码确认, 但在真服一律回 E000000**, 而且
**不是参数错**:

| 项 | 命令 | 参数 | 真服结果 |
|---|---|---|---|
| 英雄试炼 | 两步(`PveGetAllLevelsCmd` + 扫荡) | 命令名没定位到 | 未接 |
| 龙塔试炼 | `dragontower.quickbattle` | `{dealObject:"auto"}` | ✅ **通过** |
| 普通/高级研习 | `magic.receive` | `{senior:"1"/"2", num, groupType:1}` | E000000 |
| 普通招募 | `newgeneral.luckdraw` / `newgeneral.recruit` | `{itemId:"212587", num}` / `{drawId:"40895001", count}` | E000000 |
| 联盟宝藏 | (客户端无 taskHandle) | — | 未接 |
| 献祭 | `alliancecivilization.sacrifice` | `{type:1, num}` | E000000 |

⚠ **研习和招募消耗的是玩家自己的道具/金币, 照样被拒** ⇒ 说明是**该账号
功能未开通/权限不足**, 不是参数写错。献祭同理(`sacrificeInfo` 能读到
`freeTimes:3`, 但 `sacrifice` 被拒 —— 献祭要盟主权限)。

所以这些项一律标「未接入」, **不盲发** —— 没验证过的参数发出去可能白烧钱。

2026-10-31 实测(含消耗项模式):

```
资源收取  完成      科研工坊  完成      文明结晶  完成
龙塔试炼  完成      ← dragontower.quickbattle 参数正确, 真服跑通
其余消耗项  未接入 / 服务端拒绝
```

## 四、已实现的自动化

模块 `cok_assist.py`:

| 函数 | 作用 |
|---|---|
| `run_free(client)` | 跑一遍无损项, 返回 {steps[], panel[], changed} |
| `summary(client)` | 只读: 面板 13 项的清单与当前状态 |
| `panel_view(steps)` | 把面板清单和执行结果合成一张表 |

命令:

| 项 | 命令 | 参数 |
|---|---|---|
| 资源收取 | `build.collect` | `{uuid: "u1;u2;…"}` —— 只带**资源产出建筑**的 uuid |
| 科研工坊 | `sagatower.collect` | `{uuid: "u1;u2"}` —— 只带科研工坊(437000)的 uuid |
| 文明结晶 | `civilizationCastle.oneKeyCollect` | 无参 |

**建筑类型的取法**(实测):
* `build.info` 的 `building` 字段 = `"<类型id>;<等级>"`, 如 `"412000;20"`
* 新城市系统的建筑 `building` 为空, 类型藏在
  `star_building_new`(`"<类型id*10+星级>,数量"`)
* 资源产出建筑 = `412000/413000/414000/415000`(秘银矿场/伐木场/铁矿场/农田…)
* 科研工坊 = `437000`
* `build.collect` 对未知 uuid 宽容(只回资源快照不报错), 所以多发不会误伤

## 五、宝石挖掘为什么没接

`gem.getDigView` 明确回 `leftFreeTimes: 6`(剩余免费挖掘次数)、`maxRcvdTimes: 6`。
按客户端 `EquipmentGemCommand.reqDig(times, isAuto)` 的写法, 应该发:

```
gem.dig {"times": 1, "isAuto": true}
```

**但实测所有参数组合都被服务端拒(`E000000`)**(2026-10-31):

```
{"times":1,"isAuto":True}          -> E000000
{"times":1}                        -> E000000
{"times":1,"isAuto":1}              -> E000000
{"times":1,"isAuto":True,"isVideo":0} -> E000000
{"times":1,"isVideo":0,"videoType":0} -> E000000
{"times":3}                        -> E000000
```

原因未查明(可能是需要铁匠铺等级 / 幸运值门槛 / 还缺参数)。
⇒ 暂时**不纳入自动**, 面板上如实标「免费次数 N/M(暂未接入自动)」,
免得每轮白发一条必失败的命令。

## 六、开关与接口

| 设置 | 取值 | 默认 | 说明 |
|---|---|---|---|
| `assistAuto` | bool | 关 | 定时跑一键完成 |
| `assistAutoCostly` | bool | 关 | 定时执行时**连消耗项一起**跑(会烧钱) |
| `assistAutoInterval` | 秒, ≥300 | 1800 | 节流(默认 30 分钟) |

```
POST /api/action {action:"assist-onekey"}                  手动跑一遍(仅无损项)
POST /api/action {action:"assist-onekey", costly:true}     连消耗项一起(和游戏按钮一样)
```

### 两种模式的区别

| | 无损项 | 消耗项 |
|---|---|---|
| 手动点「一键完成」 | ✅ 跑 | 默认不跑; 勾上「连消耗项一起」才跑(带确认弹窗) |
| 定时自动执行 | ✅ 跑 | 默认不跑; `assistAutoCostly` 开了才跑 |

手动是用户主动点的, 和游戏里一样所以可以带消耗; 定时是无人值守,
默认不许烧钱 —— 要烧得用户自己明确开开关。

网页「一键完成」卡 / 安卓「操作 → 一键完成」分区会列出面板 13 项,
每项显示:名称 / 是否自动 / 代价 / 当前状态。

## 七、坑

1. **收取是无损的但也别调太密** —— 每轮都发会拖慢轮询, 所以按 30 分钟节流。
2. **宝石挖掘的免费次数是真的, 但服务端不收自动请求** —— 别去掉那层拦截去硬发。
3. **面板清单在客户端配置里**, 服务端不下发 —— 换版本/换渠道可能多几项少几项,
   以客户端表为准。
4. **「一键增产」(type 15) 在 lua 里没有实现** —— 走 native, 参数未知, 没接。
