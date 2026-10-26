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
  `type` 是货物类别(0 = 空船无货物, 1/2/3 = 三种货物);
  客户端判定"这艘船可派遣/可领奖"用的是 `type != "0" and state == FREE/REWARD`。
"""

SHIP_STATES = {
    0: "未解锁",
    1: "空闲",
    2: "贸易中",
    3: "可领奖",
}

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
        out.append({
            "uuid": s.get("uuid"),
            "configId": s.get("configId"),
            "state": st,
            "state_text": SHIP_STATES.get(st, "未知"),
            "itemId": str(s.get("itemId") or ""),
            "count": s.get("count"),
            "cTime": s.get("cTime"),
            "endTime": s.get("endTime"),
            "speedLimit": s.get("speedLimit"),
            "speedTimes": s.get("speedTimes"),
            "type": typ,
            # type==0 是空船(无货物), 客户端不会把它当可派遣/可领奖
            "dispatchable": (st == 1 and typ not in (None, 0)),
            "rewardable": (st == 3 and typ not in (None, 0)),
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
        }
    return last or {"ok": False, "error": "无可用命令族"}


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
