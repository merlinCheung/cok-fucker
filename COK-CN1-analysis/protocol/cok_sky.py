#!/usr/bin/env python3
"""COK 天空之境(TheHeavens)直连封装 —— 一键探索 / 一键领取。

⚠️ 来源与风险(必须先读)
------------------------
与港口(cok_dock)不同, 天空之境的命令**目前没有实测抓包背书** ——
命令目录 command-catalog-typed.json 里 skyCity.* / heaven.* 的参数都是空的,
说明从没抓到过包。本模块的命令名与参数是**从客户端反编译 Lua 源**重建的:
    apk-extract/assets/lua_static/game/TheHeavens/TheHeavensController.lua
所以这里按「双命令族自动探测 + 防御式」写, 真正能不能跑通要连真服验证。

命令族(来源 TheHeavensController.lua, 与港口同构的新旧两套)
------------------------------------------------------------
  newHeaven.*   新版(skyLand_opti2 功能开启时) ← 优先
  heaven.*      旧版

  info   : newHeaven.info      / heaven.info                无参 -> 页面数据
  explore: newHeaven.explore   / heaven.explore             开始探索
  reward : newHeaven.reward    / heaven.get.explore.reward  无参 -> 领探索奖励

探索参数(关键差异)
    新版 newHeaven.explore : { num: INT }   num=探索次数(1 起)
    旧版 heaven.explore    : { heroId, dragonId, reward }  需要先选将/龙/奖励
尽管旧版也能探索, 但它要求先选英雄/龙/奖励, 无法无脑自动化 ——
所以本模块**只在新版命令族上支持一键探索**; 旧版只支持读数据和领奖。

状态机(info 返回的 tbl.state, 来源 parseData 注释)
    0 = 空闲(可开始探索)
    1 = 探索中(等 endTime)
    2 = 完成未领奖(可一键领取)

⚠️ 真实副作用
    探索会按服务端规则消耗战力/部队(info 里带 fightPower/armyType),
    **不是**像扫地图那样零成本。所以自动探索默认关闭, 由用户显式打开。
"""

import time

from cok_sfs import TypedInt, SFS_INT

#: 探索状态机
STATE_IDLE = 0        # 空闲, 可开始探索
STATE_EXPLORING = 1   # 探索中
STATE_DONE = 2        # 完成未领奖, 可领取
STATE_TEXT = {
    STATE_IDLE: "空闲",
    STATE_EXPLORING: "探索中",
    STATE_DONE: "可领取",
}

# The packaged 12.06.0 client defines sky_island.explore_time entries 1..10.
# Values outside this discrete set are rejected by the game server as E000004.
DEFAULT_ALLOWED_EXPLORE_COUNTS = tuple(range(1, 11))

#: 命令族(先试新版, 回退旧版)。explore 仅新版无脑可用。
FAMILIES = (
    {
        "name": "newHeaven",
        "new": True,
        "info": "newHeaven.info",
        "explore": "newHeaven.explore",
        "reward": "newHeaven.reward",
    },
    {
        "name": "heaven",
        "new": False,
        "info": "heaven.info",
        "explore": "heaven.explore",
        "reward": "heaven.get.explore.reward",
    },
)


def _params(resp):
    return resp.get("__params__") or resp or {}


def _as_int(v):
    try:
        return int(v)
    except (TypeError, ValueError):
        return None


def allowed_explore_counts(_land_id=None):
    """Return valid counts for the current bundled sky-island configuration."""
    # Keep this function so future config versions can provide per-island sets.
    return DEFAULT_ALLOWED_EXPLORE_COUNTS


def normalize_explore_count(value, allowed_counts=None):
    """Validate an exploration count without issuing a game-server request."""
    try:
        count = int(value)
    except (TypeError, ValueError):
        return None, "探索次数必须是整数"
    allowed = tuple(allowed_counts or DEFAULT_ALLOWED_EXPLORE_COUNTS)
    if count not in allowed:
        return None, "当前版本仅支持探索 %s 次" % "、".join(str(v) for v in allowed)
    return count, ""


def read_sky(client, family=None):
    """读天空之境数据(只读)。返回 {ok, family, state, state_text, endTime, ...}

    family=None 时自动探测: 依次试 newHeaven.info / heaven.info,
    选第一个服务端真正放行(不回 errorCode)的。

    ⚠️ 探索前提(来自实测抓包字段 + 客户端 onClickStartExplore 校验):
        newHeaven.info 真实响应含 21 个字段, 关键的有:
          state(0空闲/1探索中/2完成未领), exploreLv, endTime,
          chooseGeneral(已选英雄), chooseDragon(已选龙), chooseRewards(已选奖励),
          curPower/needPower(战力), curCrystal/needCrystal(水晶)
        客户端点"开始探索"前会依次校验: exploreLv>=1 → 已选奖励 → 已选英雄,
        都满足才发 explore。所以**没在游戏里预选过英雄/奖励时, 探索必被拒** ——
        这就是一键探索"无法使用"的根因。
    """
    fams = FAMILIES if family is None else tuple(
        f for f in FAMILIES if f["name"] == family)
    last = None
    for f in fams:
        try:
            r = client.call(f["info"], {})
        except Exception as e:  # noqa: BLE001
            last = {"ok": False, "error": str(e)[:160], "family": f["name"]}
            continue
        p = _params(r)
        code = p.get("errorCode")
        if code:
            last = {"ok": False, "errorCode": code, "family": f["name"]}
            continue
        state = _as_int(p.get("state"))
        explore_lv = _as_int(p.get("exploreLv"))
        # chooseGeneral / chooseRewards 可能是 list 或 dict, 非空即"已选"
        has_general = _non_empty(p.get("chooseGeneral"))
        has_reward = _non_empty(p.get("chooseRewards"))
        cur_power = _as_int(p.get("curPower"))
        need_power = _as_int(p.get("needPower"))
        cur_crystal = _as_int(p.get("curCrystal"))
        need_crystal = _as_int(p.get("needCrystal"))
        # 按客户端真实校验顺序算"能不能一键探索", 并给出不能的原因
        explore_reason = ""
        if state != STATE_IDLE:
            explore_reason = "当前%s, 不能开始新探索" % STATE_TEXT.get(state, "状态未知")
        elif (explore_lv is not None) and explore_lv < 1:
            explore_reason = "探索等级未达 1 级"
        elif not has_reward:
            explore_reason = "还没选探索奖励(请先在游戏里选一次)"
        elif not has_general:
            explore_reason = "还没选出战英雄(请先在游戏里选一次)"
        elif (need_power is not None and cur_power is not None
              and cur_power < need_power):
            explore_reason = "战力不足(%s/%s)" % (cur_power, need_power)
        elif (need_crystal is not None and cur_crystal is not None
              and cur_crystal < need_crystal):
            explore_reason = "水晶不足(%s/%s)" % (cur_crystal, need_crystal)
        allowed_counts = allowed_explore_counts(p.get("landId") or p.get("forceLandId"))
        can_explore = (f["new"] and state == STATE_IDLE and not explore_reason)
        return {
            "ok": True,
            "errorCode": None,
            "family": f["name"],
            "new": f["new"],
            "state": state,
            "state_text": STATE_TEXT.get(state, "未知"),
            "endTime": _as_int(p.get("endTime")),
            "landId": p.get("landId") or p.get("forceLandId"),
            "exploreLv": explore_lv,
            "exploreNum": _as_int(p.get("exploreNum")),
            "allowedExploreCounts": list(allowed_counts),
            "maxExploreCount": max(allowed_counts),
            "fightPower": p.get("fightPower"),
            "armyType": p.get("armyType"),
            # 真实前提
            "has_general": has_general,
            "has_reward": has_reward,
            "curPower": cur_power,
            "needPower": need_power,
            "curCrystal": cur_crystal,
            "needCrystal": need_crystal,
            # 便捷布尔: 定时检查就看这两个(can_explore 已按真实前提收紧)
            "can_explore": can_explore,
            "explore_reason": explore_reason,
            "can_reward": (state == STATE_DONE),
        }
    return last or {"ok": False, "error": "无可用命令族"}


def _non_empty(v):
    """chooseGeneral/chooseRewards 这类字段非空判定(兼容 list / dict)。"""
    if isinstance(v, (list, tuple)):
        return len(v) > 0
    if isinstance(v, dict):
        return len(v) > 0
    return bool(v)


def explore(client, num=1, family=None, allowed_counts=None):
    """开始探索。仅新版命令族(newHeaven.explore {num})可无脑调用。

    ⚠️ 真实副作用: 按服务端规则消耗战力/部队。

    num: 探索次数(1 起)。会编码成 INT(服务端对类型敏感)。
    family: 指定族(None=自动探测, 但只认 new=True 的族)。
    """
    allowed = tuple(allowed_counts or DEFAULT_ALLOWED_EXPLORE_COUNTS)
    n, count_error = normalize_explore_count(num, allowed)
    if count_error:
        return {"ok": False, "error": count_error, "num": num,
                "allowedExploreCounts": list(allowed)}
    fams = FAMILIES if family is None else tuple(
        f for f in FAMILIES if f["name"] == family)
    # 只在新版族上探索(旧版要先选将/龙/奖励, 无法无脑自动化)
    fams = tuple(f for f in fams if f.get("new"))
    if not fams:
        return {"ok": False,
                "error": "当前区服是旧版天空之境(heaven.*), 旧版探索需先选将/龙/奖励, "
                         "无法一键自动; 请在游戏里手动探索"}
    last = None
    for f in fams:
        try:
            r = client.call(f["explore"], {"num": TypedInt(n, SFS_INT)})
        except Exception as e:  # noqa: BLE001
            last = {"ok": False, "error": str(e)[:160], "family": f["name"]}
            continue
        p = _params(r)
        code = p.get("errorCode")
        if code:
            last = {"ok": False, "errorCode": code, "family": f["name"],
                    "num": n, "allowedExploreCounts": list(allowed)}
            continue
        return {
            "ok": True,
            "errorCode": None,
            "family": f["name"],
            "num": n,
            "state": _as_int(p.get("state")),
            "endTime": _as_int(p.get("endTime")),
        }
    return last or {"ok": False, "error": "探索失败"}


def get_reward(client, family=None):
    """领取探索奖励(无参)。返回 {ok, family, count, rewards}

    ⚠️ 真实副作用: 领取奖励(本来就该领, 风险低)。

    响应字段(来源 TheHeavensGetExporeRewardCommand:handleReceive):
        reward / exploreReward / fightReward  —— 奖励数组(新版 UI 会合并三者)
    """
    fams = FAMILIES if family is None else tuple(
        f for f in FAMILIES if f["name"] == family)
    last = None
    for f in fams:
        try:
            r = client.call(f["reward"], {})
        except Exception as e:  # noqa: BLE001
            last = {"ok": False, "error": str(e)[:160], "family": f["name"]}
            continue
        p = _params(r)
        code = p.get("errorCode")
        if code:
            last = {"ok": False, "errorCode": code, "family": f["name"]}
            continue
        rewards = _collect_rewards(p)
        return {
            "ok": True,
            "errorCode": None,
            "family": f["name"],
            "count": len(rewards),
            "rewards": rewards,
            "state": _as_int(p.get("state")),
        }
    return last or {"ok": False, "error": "领取失败"}


def _collect_rewards(p):
    """从响应里收集奖励明细(合并 reward / exploreReward / fightReward)。"""
    out = []
    for key in ("reward", "exploreReward", "fightReward"):
        arr = p.get(key)
        if not isinstance(arr, list):
            continue
        for it in arr:
            if not isinstance(it, dict):
                continue
            out.append({
                "itemId": str(it.get("itemId") or it.get("id") or ""),
                "count": it.get("count") or it.get("num") or it.get("addNum"),
                "uuid": it.get("uuid"),
            })
    return out


def remain_seconds(info, now_ms=None):
    """探索中还剩多少秒(endTime - 现在)。非探索中返回 0。"""
    if not isinstance(info, dict) or info.get("state") != STATE_EXPLORING:
        return 0
    end = info.get("endTime")
    if not end:
        return 0
    if now_ms is None:
        now_ms = int(time.time() * 1000)
    return max(0, int((int(end) - now_ms) / 1000))
