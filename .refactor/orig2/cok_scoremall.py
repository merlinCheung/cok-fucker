#!/usr/bin/env python3
"""COK 积分商城(ScoreMall) —— 积分任务奖励领取。

来源(客户端反编译 Lua):
    game/ScoreMall/ScoreMallMgr.lua         积分商城管理类(shopType = 125)
    game/ScoreMall/ScoreMallSignInCell.lua  "积分好礼"任务格子(领取按钮)
    game/shop/ShopMallController.lua        mall.data 的发送方

命令
----
  读  mall.data    {mallId:"125"}
      → infoDic{mallId}, goodsArray(商品), taskArr(积分任务), monthIntegral(本月积分), curStar
  领  mall.reward  {mallId:"125", taskId:"<id>"}
      → taskArr(刷新后), monthIntegral, rewardInfo(本次奖励)
  两个参数在客户端都是 CCString, 所以这里一律传字符串。

任务格子(taskArr[i])
    taskId / rewardId / status / cur / target
    status == "0" → 未领取;  其它 → 已领取
    领取按钮可点 = status == "0" 且 cur == target   (ScoreMallSignInCell:refreshCell)
客户端是**一个任务发一次** mall.reward, 所以一键领取 = 逐个领掉可领的任务。

⚠ 这两个命令目前没有抓包样本, 字段名来自反编译。read 会把响应顶层字段名
  带回(keys), 字段对不上时能直接看出来。
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

import time

MALL_ID = "125"
CMD_DATA = "mall.data"
CMD_REWARD = "mall.reward"

#: 积分任务名(database.local.xml 的 integral_mall_task 组 + text_zh_CN.ini 文案)
#: 只有 10 个, 直接内置, 不在运行时解析 4MB 的 XML/语言包。
TASK_NAMES = {
    "52187700": "见面礼",
    "52187701": "每日签到",
    "52187702": "每周签到",       # 本周登录达到3日即可领取, 每周重置
    "52187703": "累计在线1小时",
    "52187704": "累计在线2小时",
    "52187705": "每日首充",
    "52187706": "本周累充$100",
    "52187707": "本周累充$300",
    "52187708": "本周累充$500",
    "52187709": "充值",
}


def _params(resp):
    return (resp or {}).get("__params__") or resp or {}


def _int(v):
    try:
        return int(v)
    except (TypeError, ValueError):
        return None


def _tasks(arr):
    """taskArr → 带"已领/可领"判定的列表。"""
    out = []
    for t in arr or []:
        if not isinstance(t, dict):
            continue
        status = "" if t.get("status") is None else str(t.get("status"))
        cur, target = t.get("cur"), t.get("target")
        ci, ti = _int(cur), _int(target)
        if ci is not None and ti is not None:
            done = ci >= ti
        else:
            done = cur is not None and str(cur) == str(target)
        claimed = status not in ("0", "")
        tid = str(t.get("taskId") or "")
        out.append({
            "taskId": tid,
            "name": TASK_NAMES.get(tid) or ("任务 " + tid),
            "rewardId": str(t.get("rewardId") or ""),
            "status": status,
            "cur": cur,
            "target": target,
            "done": bool(done),
            "claimed": claimed,
            "claimable": (status == "0" and bool(done)),
        })
    return out


def _rewards(info):
    """rewardInfo → [{itemId, num}]。格式没抓到过, 兼容几种常见写法。"""
    items = []
    if isinstance(info, list):
        items = info
    elif isinstance(info, dict):
        for key in ("goods", "rewardArray", "reward", "array", "rewards"):
            v = info.get(key)
            if isinstance(v, list):
                items.extend(v)
        if not items and (info.get("itemId") or info.get("id")):
            items = [info]
    out = []
    for it in items:
        if not isinstance(it, dict):
            continue
        v = it.get("value") if isinstance(it.get("value"), dict) else it
        g = it.get("goodsObj") if isinstance(it.get("goodsObj"), dict) else {}
        iid = str(v.get("id") or v.get("itemId") or g.get("itemId") or it.get("itemId") or "")
        num = None
        for src in (v, g, it):
            for k in ("num", "count", "addNum", "rewardAdd"):
                if src.get(k) is not None:
                    num = src.get(k)
                    break
            if num is not None:
                break
        if iid or num is not None:
            out.append({"itemId": iid, "num": num, "type": it.get("type")})
    return out


def read_score_mall(client, mall_id=MALL_ID):
    """读积分商城(只读)。返回 {ok, monthIntegral, curStar, tasks, claimable, ...}"""
    try:
        r = client.call(CMD_DATA, {"mallId": str(mall_id)})
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "error": str(e)[:160]}
    p = _params(r)
    if p.get("errorCode"):
        return {"ok": False, "errorCode": p.get("errorCode"),
                "keys": sorted(p.keys())}
    tasks = _tasks(p.get("taskArr"))
    return {
        "ok": True,
        "mallId": str(((p.get("infoDic") or {}).get("mallId")) or mall_id),
        "monthIntegral": p.get("monthIntegral"),
        "curStar": p.get("curStar"),
        "tasks": tasks,
        "claimable": [t for t in tasks if t["claimable"]],
        "goods": len(p.get("goodsArray") or []),
        # 诊断用: 响应顶层字段名(字段对不上时一眼能看出来)
        "keys": sorted(p.keys()),
        "has_taskArr": "taskArr" in p,
    }


def claim_task(client, task_id, mall_id=MALL_ID):
    """领取一个积分任务的奖励。⚠ 真实写操作(领奖, 本来就该领)。"""
    try:
        r = client.call(CMD_REWARD, {"mallId": str(mall_id), "taskId": str(task_id)})
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "taskId": str(task_id), "error": str(e)[:160]}
    p = _params(r)
    if p.get("errorCode"):
        return {"ok": False, "taskId": str(task_id), "errorCode": p.get("errorCode")}
    return {
        "ok": True,
        "taskId": str(task_id),
        "rewards": _rewards(p.get("rewardInfo")),
        "monthIntegral": p.get("monthIntegral"),
        "tasks": _tasks(p.get("taskArr")) if p.get("taskArr") is not None else None,
    }


def claim_all(client, mall_id=MALL_ID, state=None, delay=0.3):
    """把所有可领的积分任务逐个领掉(客户端也是一个任务一条 mall.reward)。

    state: 已读到的 read_score_mall 结果(省一次请求); 不给就先读。
    返回 {ok, results:[claim_task...], claimed, failed, before}
    """
    st = state if isinstance(state, dict) and state.get("ok") else read_score_mall(client, mall_id)
    if not st.get("ok"):
        return {"ok": False, "error": st.get("error"), "errorCode": st.get("errorCode"),
                "results": [], "claimed": 0, "failed": 0}
    results = []
    for t in st.get("claimable") or []:
        results.append(claim_task(client, t["taskId"], mall_id))
        if delay:
            time.sleep(delay)
    ok_n = sum(1 for x in results if x.get("ok"))
    return {
        "ok": True,
        "results": results,
        "claimed": ok_n,
        "failed": len(results) - ok_n,
        "pending": len(st.get("claimable") or []),
    }
