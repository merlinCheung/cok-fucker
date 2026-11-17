#!/usr/bin/env python3
"""COK 福利中心(日常福利)直连封装。

两个**每天都能领**的免费奖励(客户端源码位置):

1) **每日好礼**(`game/WelfareIntegrate/dailyRecharge/DailyRechargeController.lua`)
   读:  `everydayexchange.data`   (无参)
        → {freeRewarded, freeReward, payRewarded, payReward,
           commonExchangeIds, specialExchangeId, oneClickBuyExchangeId}
        `freeRewarded` = 今天的**免费**奖励领了没(true = 已领)
   领:  `everydayexchange.reward`  (无参) → {rewardArray}

2) **龙之馈赠**(`game/activity/UserReward/UserRewardController.lua`)
   读:  `userpayreward.newinfo`   (无参)
        → {currDay, configArray, processConfigArray,
           "<exchangeId>": {isBuy, rewardDays, specialRewardDays,
                            specialActivityOpen, process, processStr, ...}}
        `rewardDays` = "0;1" 这种"已领的天"(0=周日 … 6=周六), `currDay` = 今天是周几
   领:  `userpayreward.newaccept`  {exchangeId, specialReward}
        → {rewardArray, ...刷新用的 A 对象}

   黑龙(默认 exchangeId 760359)是买过的那个; 蓝龙(764116)要主城等级 10+。

**谁能领**(客户端 UserRewardController 注释里的规则):
   活动开 + 付费   → 普通 + 尊享 两份
   活动开 + 没付费 → 只有普通
   活动没开 + 付费 → 只有普通
   活动没开 + 没付费 → 都没有
所以普通奖励 = (isBuy 或 specialActivityOpen) 且 今天不在 rewardDays 里。

⚠ 领奖是**真实写操作**(会消耗每日次数), 所以脚本只在"确定可领"时才发命令。
"""

# --- 包自举: 让本文件既能 `python3 cok/core/xxx.py` 直接跑, 也能被平铺 import ---
import os as _os
import sys as _sys

_PKG_ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
if _os.path.isdir(_PKG_ROOT) and _PKG_ROOT not in _sys.path:
    _sys.path.insert(0, _PKG_ROOT)
_CORE = _os.path.join(_PKG_ROOT, "core")
if _os.path.isdir(_CORE) and _CORE not in _sys.path:
    _sys.path.insert(0, _CORE)

import json

# 黑龙的默认 exchangeId(客户端 UserRewardController:getBlackDragonId 的兜底值)
BLACK_DRAGON_ID = "760359"
# 蓝龙(客户端注释里写死过 764116)
BLUE_DRAGON_ID = "764116"


def _days(v):
    """"0;1" → [0, 1]。rewardDays / specialRewardDays 都用这个格式。"""
    out = []
    for x in str(v or "").split(";"):
        x = x.strip()
        if x.isdigit():
            out.append(int(x))
    return out


def _rewards(arr):
    """rewardArray → [{itemId, num, type}]。

    奖励项格式: {type: "7", value: {num: 100, id: "200200"}}
    """
    out = []
    for it in arr or []:
        if not isinstance(it, dict):
            continue
        v = it.get("value") or {}
        if not isinstance(v, dict):
            continue
        iid = str(v.get("id") or "")
        if not iid:
            continue
        out.append({
            "itemId": iid,
            "num": v.get("num") if v.get("num") is not None else v.get("rewardAdd"),
            "type": it.get("type"),
        })
    return out


def _err(p):
    return p.get("errorCode") or p.get("error") or ""


# ---------------- 每日好礼 ----------------

def read_daily_gift(client):
    """每日好礼状态(everydayexchange.data)。"""
    try:
        r = client.call("everydayexchange.data", {})
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "error": str(e)[:160]}
    p = r.get("__params__") or {}
    if p.get("errorCode"):
        return {"ok": False, "errorCode": p.get("errorCode"), "error": _err(p)}
    return {
        "ok": True,
        # 免费奖励今天领了没
        "freeRewarded": bool(p.get("freeRewarded")),
        "freeReward": str(p.get("freeReward") or ""),
        # 充值奖励: 脚本**不碰**(要花钱)
        "payRewarded": bool(p.get("payRewarded")),
        "payReward": str(p.get("payReward") or ""),
        "commonExchangeIds": str(p.get("commonExchangeIds") or ""),
    }


def claim_daily_gift(client):
    """领取每日好礼的**免费**奖励(everydayexchange.reward, 无参)。

    ⚠ 真实副作用: 真的领了(每天一次)。
    """
    try:
        r = client.call("everydayexchange.reward", {})
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "error": str(e)[:160]}
    p = r.get("__params__") or {}
    if p.get("errorCode"):
        return {"ok": False, "errorCode": p.get("errorCode"), "error": _err(p)}
    rewards = _rewards(p.get("rewardArray"))
    return {"ok": True, "count": len(rewards), "rewards": rewards}


# ---------------- 龙之馈赠 ----------------

def read_dragon_gift(client):
    """龙之馈赠状态(userpayreward.newinfo, 无参)。

    返回 {ok, currDay, dragons:{exchangeId:{...}}, today:[当天奖励配置]}
    """
    try:
        r = client.call("userpayreward.newinfo", {})
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "error": str(e)[:160]}
    p = r.get("__params__") or {}
    if p.get("errorCode"):
        return {"ok": False, "errorCode": p.get("errorCode"), "error": _err(p)}
    try:
        curr_day = int(p.get("currDay"))
    except (TypeError, ValueError):
        curr_day = 0

    dragons = {}
    for eid, info in p.items():
        if not isinstance(info, dict):
            continue
        if "rewardDays" not in info and "specialRewardDays" not in info:
            continue
        eid = str(eid)
        got = _days(info.get("rewardDays"))
        got1 = _days(info.get("specialRewardDays"))
        is_buy = bool(info.get("isBuy"))
        act_open = bool(info.get("specialActivityOpen"))
        d = {
            "exchangeId": eid,
            "isBuy": is_buy,
            "specialActivityOpen": act_open,
            "rewardDays": str(info.get("rewardDays") or ""),
            "specialRewardDays": str(info.get("specialRewardDays") or ""),
            "claimed_today": curr_day in got,
            "special_claimed_today": curr_day in got1,
            # 普通奖励: 买过 或 活动开着, 且今天没领
            "claimable": (is_buy or act_open) and curr_day not in got,
            # 尊享好礼: 得买过 且 活动开着, 且今天没领
            "special_claimable": is_buy and act_open and curr_day not in got1,
        }
        dragons[eid] = d

    # 当天的奖励内容(configArray 里 day == currDay 的)
    today = []
    for c in (p.get("configArray") or []):
        if not isinstance(c, dict):
            continue
        try:
            day = int(c.get("day"))
        except (TypeError, ValueError):
            continue
        if day != curr_day:
            continue
        today.append({
            "exchangeId": str(c.get("exchangeId") or ""),
            "rewardId": str(c.get("rewardId") or ""),
            "day": day,
            "rewards": _rewards(c.get("rewards")),
            "specialRewards": _rewards(c.get("specialRewards")),
        })
    return {
        "ok": True,
        "currDay": curr_day,
        "dragons": dragons,
        "today": today,
        "blackId": _pick_black(dragons),
    }


def _pick_black(dragons):
    """挑出黑龙的 exchangeId。

    客户端是本地缓存的 black_id/blue_id(服务端下发的配置), 我们没缓存。
    退化办法: 优先用写死的 760359; 否则取"买了的"那个(蓝龙要等级 10+ 且没买)。
    """
    if BLACK_DRAGON_ID in dragons:
        return BLACK_DRAGON_ID
    bought = [d for d in dragons.values() if d.get("isBuy")]
    if bought:
        return bought[0]["exchangeId"]
    return ""


def claim_dragon_gift(client, exchange_id, special=False):
    """领龙之馈赠的每日奖励(userpayreward.newaccept)。

    参数: exchangeId(STRING) + specialReward(BOOL, 尊享好礼)
    ⚠ 真实副作用: 真的领了(每天一次/份)。
    """
    params = {"exchangeId": str(exchange_id), "specialReward": bool(special)}
    try:
        r = client.call("userpayreward.newaccept", params)
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "error": str(e)[:160]}
    p = r.get("__params__") or {}
    if p.get("errorCode"):
        return {"ok": False, "errorCode": p.get("errorCode"), "error": _err(p),
                "exchangeId": str(exchange_id), "special": bool(special)}
    rewards = _rewards(p.get("rewardArray"))
    return {"ok": True, "count": len(rewards), "rewards": rewards,
            "exchangeId": str(exchange_id), "special": bool(special)}


# ---------------- 汇总(给网页用) ----------------

def read_all(client):
    """两个功能的状态一起读。单个失败不影响另一个。"""
    out = {"ok": True}
    try:
        out["daily_gift"] = read_daily_gift(client)
    except Exception as e:  # noqa: BLE001
        out["daily_gift"] = {"ok": False, "error": str(e)[:160]}
    try:
        out["dragon_gift"] = read_dragon_gift(client)
    except Exception as e:  # noqa: BLE001
        out["dragon_gift"] = {"ok": False, "error": str(e)[:160]}
    return out


def claimable_count(state):
    """一共有几项现在能领(页面计数用)。"""
    n = 0
    dg = (state or {}).get("daily_gift") or {}
    if dg.get("ok") and not dg.get("freeRewarded"):
        n += 1
    dr = ((state or {}).get("dragon_gift") or {}).get("dragons") or {}
    for d in dr.values():
        if d.get("claimable"):
            n += 1
        if d.get("special_claimable"):
            n += 1
    return n
