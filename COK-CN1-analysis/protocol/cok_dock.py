#!/usr/bin/env python3
"""COK 港口(码头航海贸易)直连封装。

⚠️ 命令族更正(2026-10-25 实测)
--------------------------------
APK 里有**三套**并行的航海贸易命令族, 名字不同但 Lua 注释都写"码头航海贸易":

  newBoat.*      game/NewNavigation/NewNavigationCtl.lua   ← **当前区服实际启用**
  dockTrade.*    game/SeaTrade/SeaTradeCtl.lua             ← 旧版, 服务端回 102192
  nightCityDock.* game/NightCity/control/NCTradeController.lua ← 夜城专用, 回 102192

实测(区服 2223):
  newBoat.data       -> 真实返回 ships 数组(4 条) + shipLimit
  dockTrade.data     -> {"errorCode": "102192"}  (功能未开启)
  nightCityDock.data -> {"errorCode": "102192"}  (功能未开启)

所以"102192 = 功能未开启"这个结论**当时是接错了命令族**;
正确族是 newBoat, 它在本区服是开着的。

newBoat 命令族(来源 NewNavigationCtl.lua):
  newBoat.data            无参                     -> 港口数据(ships 数组 / shipLimit)
  newBoat.select          {uuid,itemId,rewardConfigId} -> 选择载货
  newBoat.sendShip        {uuid}                   -> 派船出去
  newBoat.recallShip      {uuid}                   -> 召回
  newBoat.speedUp         {uuid}                   -> 加速
  newBoat.shipReward      {uuid}                   -> 领取单条船的奖励
  newBoat.oneKeySendShip  无参                     -> **一键派遣**(所有空闲船)
  newBoat.oneKeyShipReward 无参                    -> **一键领取**(所有可领奖的船)

船只状态(NewNavigationCtl.SHIPSTATE, 与 SeaTradeCtl 一致):
  0 = LOCK   未解锁
  1 = FREE   空闲中
  2 = TRADE  贸易中(在途)
  3 = REWARD **可领奖**   <- 定时检查"是否可领取"就看这个

船只字段(newBoat.data 实测):
  uuid / configId / itemId / count / cTime / endTime /
  state / speedLimit / speedTimes / type
  `type` 是**货物类别**: 0 / 1 / 2 / 3。
  ⚠️ **`type == 0` 的那条根本不是船**, 是"码头宝箱"(港口活动奖励位):
  客户端 NewNavigationCell:refreshCell 明确分流 ——
      if info.type ~= "0" then refreshBoatCell(...)      -- 船
      else                    refreshTimeRewardCell(...) -- 码头宝箱
  码头宝箱格子在游戏里显示"当前奖励物品 + 到下一次刷新的倒计时",
  物品每隔几分钟换一件(领完 → 倒计时 → 换新物品), 所以它**永远不是"空载"**。

码头宝箱的数据**不在 newBoat.data 里**, 而在登录后服务端下发的 `init` 推送:
  init.cargo = {rewardTime, times, rewardInfo}
    rewardInfo = "goods,{itemId},{count}"  (客户端 CargoRewardDialog:initView
               按逗号切: [1]=道具id [2]=数量)
    rewardTime = 下次刷新时间(ms, 服务器时钟)
    times      = 次数(语义服务端未明确, 只透传给页面)
"""

import json
import time

SHIP_STATES = {
    0: "未解锁",
    1: "空闲",
    2: "贸易中",
    3: "可领奖",
}

# `type == 0` 的那一格不是船, 是"码头宝箱"(港口活动奖励位)。
# 客户端 NewNavigationCell:refreshCell:
#   type ~= "0" -> refreshBoatCell      (普通船)
#   type == "0" -> refreshTimeRewardCell (码头宝箱: 奖励物品 + 刷新倒计时)
ACTIVITY_TYPE = 0
ACTIVITY_NAME = "码头宝箱"

# "您未达到领取奖励的条件" —— 宝箱还没到刷新时间/次数用完, 属于**正常状态**,
# 不是故障(别写进错误日志, 否则每轮轮询都刷一条"失败")。
CARGO_NOT_READY = "E100148"

# 探测顺序: 先试实测可用的 newBoat, 再回退到旧族。
# 服务端对不存在的族回 102192(功能未开启), 对未知命令回超时 —— 两种都能识别。
FAMILIES = (
    {
        "name": "newBoat",
        "data": "newBoat.data",
        "oneKeyReward": "newBoat.oneKeyShipReward",
        "oneKeySend": "newBoat.oneKeySendShip",
        "shipReward": "newBoat.shipReward",
        "sendShip": "newBoat.sendShip",
        "recallShip": "newBoat.recallShip",
        "speedUp": "newBoat.speedUp",
    },
    {
        "name": "dockTrade",
        "data": "dockTrade.data",
        "oneKeyReward": "dockTrade.oneKeyShipReward",
        "oneKeySend": "dockTrade.oneKeySendShip",
        "shipReward": "dockTrade.shipReward",
        "sendShip": "dockTrade.sendShip",
        "recallShip": "dockTrade.recallShip",
        "speedUp": "dockTrade.speedUp",
    },
    {
        "name": "nightCityDock",
        "data": "nightCityDock.data",
        "oneKeyReward": "nightCityDock.shipAllReward",
        "oneKeySend": "nightCityDock.sendAllShip",
        "shipReward": "nightCityDock.shipReward",
        "sendShip": "nightCityDock.sendShip",
        "recallShip": "nightCityDock.recallShip",
        "speedUp": "nightCityDock.speedUp",
    },
)

# 服务端"功能未开启"错误码(文本 id 同码: 功能未开启, 敬请期待)
DISABLED_CODE = 102192


def _ships(params):
    """把服务端 ships 数组整理成带中文状态的列表。"""
    out = []
    raw = (params.get("ships") or [])
    if not isinstance(raw, list):
        return out
    for s in raw:
        if not isinstance(s, dict):
            continue
        st = s.get("state")
        try:
            st = int(st)
        except (TypeError, ValueError):
            st = None
        try:
            typ = int(s.get("type"))
        except (TypeError, ValueError):
            typ = None
        # type==0 不是船, 是"码头宝箱"(港口活动奖励位) —— 单独标出来,
        # 别当成"空闲的空船"显示成"空载"(那正是第一行一直空载的原因)。
        is_activity = (typ == ACTIVITY_TYPE)
        out.append({
            "uuid": s.get("uuid"),
            "configId": s.get("configId"),
            "state": st,
            "state_text": ACTIVITY_NAME if is_activity else SHIP_STATES.get(st, "未知"),
            "kind": "activity" if is_activity else "boat",
            "itemId": str(s.get("itemId") or ""),
            "count": s.get("count"),
            "cTime": s.get("cTime"),
            "endTime": s.get("endTime"),
            "speedLimit": s.get("speedLimit"),
            "speedTimes": s.get("speedTimes"),
            "type": typ,
            # 码头宝箱(以及没装货的船)都不算可派遣/可领奖
            "dispatchable": (st == 1 and typ not in (None, ACTIVITY_TYPE)),
            "rewardable": (st == 3 and typ not in (None, ACTIVITY_TYPE)),
            "reward": s.get("reward"),
        })
    return out


def _params(resp):
    return resp.get("__params__") or resp or {}


def read_dock(client, family=None):
    """读港口数据(只读)。返回 {ships, rewardable, idle, trading, ...}

    family: 指定命令族名(None = 自动探测)。自动探测会依次试 newBoat / dockTrade /
    nightCityDock, 选第一个服务端真正放行的。
    """
    fams = FAMILIES if family is None else tuple(
        f for f in FAMILIES if f["name"] == family)
    last = None
    for f in fams:
        try:
            r = client.call(f["data"], {})
        except Exception as e:  # noqa: BLE001
            last = {"ok": False, "error": str(e)[:160], "family": f["name"]}
            continue
        p = _params(r)
        code = p.get("errorCode")
        if code:
            last = {"ok": False, "errorCode": code, "family": f["name"]}
            continue
        ships = _ships(p)
        return {
            "ok": True,
            "errorCode": None,
            "family": f["name"],
            "ships": ships,
            "shipLimit": p.get("shipLimit"),
            "speedTimes": p.get("speedTimes"),
            "gold": p.get("gold"),
            # 汇总: 定时检查就靠这几个
            "rewardable": [s for s in ships if s["rewardable"]],
            "idle": [s for s in ships if s["dispatchable"]],
            "trading": [s for s in ships if s["state"] == 2],
            "locked": [s for s in ships if s["state"] == 0],
            # 码头宝箱(港口活动奖励位): 不是船, 单独拎出来给页面显示
            "activity": [s for s in ships if s.get("kind") == "activity"],
        }
    return last or {"ok": False, "error": "无可用命令族"}


def read_cargo(client):
    """码头宝箱(港口活动奖励)状态。

    数据来源: **登录后服务端下发的 `init` 推送**里的 `cargo` 字段:
        {rewardTime, times, rewardInfo:"goods,{itemId},{count}"}
    `newBoat.data` 里**没有**这些字段 —— 所以以前港口卡片第一行(type=0)
    只能显示"空载", 而游戏里那一格明明是有奖励物品的。

    客户端怎么用(见 NewNavigationCell:setPortActItem / CargoRewardDialog):
        rewardInfo "goods,200343,50" -> 显示 "5,000钢 x50"
        rewardTime -> 下一次刷新的时间; 到点后按钮变成"领取奖励",
                      领完换一件新物品(所以是"每几分钟刷新一次")

    返回 {ok, itemId, count, rewardTime, times, rewardInfo}
    """
    init = getattr(client, "init_params", None) or {}
    cargo = init.get("cargo") if isinstance(init, dict) else None
    if not isinstance(cargo, dict) or not cargo:
        return {"ok": False, "error": "init 推送里没有 cargo 字段(需要重新登录)"}
    info = str(cargo.get("rewardInfo") or "")
    parts = [x.strip() for x in info.split(",")]
    item_id = ""
    count = None
    if len(parts) >= 3 and parts[0] == "goods":
        item_id = parts[1]
        try:
            count = int(parts[2])
        except (TypeError, ValueError):
            count = None
    return {
        "ok": True,
        "rewardInfo": info,
        "itemId": item_id,
        "count": count,
        "rewardTime": cargo.get("rewardTime"),
        # times 的确切语义服务端没写清楚(是今日已领次数还是刷新轮次),
        # 这里只透传, 页面不硬下结论。
        "times": cargo.get("times"),
    }


def merge_cargo(client, cargo):
    """把一份 cargo 状态写回客户端缓存(init_params['cargo'])。

    三个来源都会带**最新**的宝箱状态:
      * init 推送(登录时)
      * `cargo.reward` 的响应(领取后 —— 领完立刻就是新物品+新倒计时)
      * 带 cargo 的推送
    不写回缓存的话, 领取后页面还显示旧物品。
    """
    if not isinstance(cargo, dict) or not cargo:
        return False
    init = getattr(client, "init_params", None)
    if not isinstance(init, dict):
        return False
    init["cargo"] = cargo
    return True


def cargo_claimable(cargo, now_ms=None):
    """码头宝箱现在能不能领。

    客户端逻辑(CargoRewardDialog:updateView):
        rewardTime > now  → 还在倒计时, 按钮不可点
        rewardTime <= now → 按钮变成"领取奖励", 可领
    """
    if not isinstance(cargo, dict) or not cargo:
        return False
    try:
        rt = int(cargo.get("rewardTime"))
    except (TypeError, ValueError):
        return False
    if rt <= 0:
        return False
    if now_ms is None:
        now_ms = int(time.time() * 1000)
    return rt <= now_ms


def claim_cargo(client):
    """领取码头宝箱(港口活动奖励位)。

    命令 `cargo.reward` —— **必须无参**(实测带任何参数都回 E100148;
    `cargo.seead` 回 E000000, 根本不用发)。

    响应:
        reward.goods[] -> {itemId, count, uuid, para1, para2}  领到的东西
        cargo          -> **领取后的新状态**(rewardTime/times/rewardInfo)
        isDouble       -> 本次是否双倍

    ⚠ 真实副作用: 真的把宝箱领了(每日次数有限), 会消耗一次机会。
    """
    try:
        r = client.call("cargo.reward", {})
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "error": str(e)[:160]}
    p = r.get("__params__") or {}
    cg = p.get("cargo")
    if isinstance(cg, dict) and cg:
        merge_cargo(client, cg)
    code = p.get("errorCode")
    if code:
        # 服务端拒绝时也会回当前 cargo 状态(顺手刷新缓存)
        return {"ok": False, "errorCode": code, "cargo": cg}
    rewards = []
    goods = ((p.get("reward") or {}).get("goods") or [])
    for it in goods:
        if not isinstance(it, dict):
            continue
        rewards.append({
            "itemId": str(it.get("itemId") or ""),
            "count": it.get("count"),
            "uuid": it.get("uuid"),
            "para1": it.get("para1"),
            "para2": it.get("para2"),
        })
    return {
        "ok": True,
        "count": len(rewards),
        "rewards": rewards,
        "cargo": cg,
        "isDouble": p.get("isDouble"),
    }


def one_key_reward(client, family=None):
    """一键领取所有可领奖船只的奖励(无参)。

    ⚠️ 真实副作用: 领取奖励(本来就是要领的, 风险低)。

    返回结构:
      count    —— 领到的**条数**(每条船算一条)
      rewards  —— 领到的东西明细 [{itemId, addNum, uuid}]
                  (客户端读的是 tbl.array[i].goodsObj.addNum / .itemId / .uuid,
                   见 NewNavigationCtl:mergeReward)
      array    —— 原始返回
    """
    fams = FAMILIES if family is None else tuple(
        f for f in FAMILIES if f["name"] == family)
    for f in fams:
        try:
            r = client.call(f["oneKeyReward"], {})
        except Exception as e:  # noqa: BLE001
            return {"ok": False, "error": str(e)[:160], "family": f["name"]}
        p = _params(r)
        if p.get("errorCode"):
            continue
        arr = p.get("array") or []
        rewards = []
        for it in arr:
            if not isinstance(it, dict):
                continue
            g = it.get("goodsObj") or {}
            rewards.append({
                "itemId": str(g.get("itemId") or ""),
                "addNum": g.get("addNum") or 0,
                "uuid": g.get("uuid") or it.get("uuid")
                        or (it.get("ship") or {}).get("uuid"),
            })
        return {
            "ok": True,
            "errorCode": None,
            "family": f["name"],
            "count": len(rewards),
            "rewards": rewards,
            "array": arr,
        }
    return {"ok": False, "errorCode": p.get("errorCode") if 'p' in dir() else None,
            "error": "所有命令族都被服务端拒绝"}


def one_key_send(client, family=None):
    """一键派遣所有空闲船只(无参)。

    ⚠️ 真实副作用: 会**派出船只**(消耗载货/资源), 属于写操作。
    """
    fams = FAMILIES if family is None else tuple(
        f for f in FAMILIES if f["name"] == family)
    for f in fams:
        try:
            r = client.call(f["oneKeySend"], {})
        except Exception as e:  # noqa: BLE001
            return {"ok": False, "error": str(e)[:160], "family": f["name"]}
        p = _params(r)
        if p.get("errorCode"):
            continue
        return {
            "ok": True,
            "errorCode": None,
            "family": f["name"],
            "count": len(p.get("array") or []),
            "array": p.get("array") or [],
        }
    return {"ok": False, "error": "所有命令族都被服务端拒绝"}


def ship_reward(client, uuid, family=None):
    """领取单条船的奖励。"""
    fams = FAMILIES if family is None else tuple(
        f for f in FAMILIES if f["name"] == family)
    for f in fams:
        try:
            r = client.call(f["shipReward"], {"uuid": str(uuid)})
        except Exception as e:  # noqa: BLE001
            return {"ok": False, "error": str(e)[:160], "family": f["name"]}
        p = _params(r)
        if p.get("errorCode"):
            continue
        return {"ok": True, "errorCode": None, "family": f["name"], "result": p}
    return {"ok": False, "error": "所有命令族都被服务端拒绝"}
