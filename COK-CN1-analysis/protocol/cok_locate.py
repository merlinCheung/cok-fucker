#!/usr/bin/env python3
"""COK 玩家坐标查询(按名字找人 -> 地图坐标)。

协议链路(来源客户端 `game/Spy/PlayerSearchView.lua` + `PlayerSearchListView.lua`):

  1. `search.player.spy {userName, item}`  -> 返回候选玩家列表 [{name, uid}, ...]
  2. 选中某个玩家后再发一次同样的命令(带 item=212054 坐标侦查道具),
     这次返回里带 `location` —— **地图点位 index**
  3. index -> (x, y) 用 `WorldController::getPointByIndex` 的反函数换算:
        index = x + 1 + int(1201 * y)   =>   x = (index-1) % 1201,  y = (index-1) // 1201

客户端里 `item` 的取值:
  212054 = 坐标侦查  -> 目标返回 location(我们要的)
  212055 = 战争守护侦查 -> 返回保护罩信息(不是坐标)

⚠️ 坐标侦查是**消耗道具**的功能: 服务端会扣「坐标侦查」道具。
   所以这个查询本质上是"用道具换坐标", 频率由玩家自己的道具库存决定。

⚠️ 名字重名: 服务端返回的是候选列表, 需要**多个同名玩家**时
   只能靠 uid 区分(uid 是服务端唯一 id)。
"""

# 世界 x 方向格数(来自 login.dataconfig 的 worldmap_map.k1 = 1201)
WORLD_W = 1201

# 侦察道具 id
SPY_ITEM_LOC = "212054"      # 坐标侦查
SPY_ITEM_SHIELD = "212055"   # 战争守护侦查


def index_to_point(index, w=WORLD_W):
    """地图点位 index -> (x, y)。

    `WorldController::getPointByIndex` 是 `getIndexByPoint` 的反函数,
    两者必须互逆。getIndexByPoint:
        index = (uint)x + 1 + (uint)(1201 * y)
    所以:
        x = (index - 1) % 1201
        y = (index - 1) // 1201
    """
    try:
        i = int(index)
    except (TypeError, ValueError):
        return None
    if i <= 0:
        return None
    n = i - 1
    return (n % w, n // w)


def _dig_location(params):
    """在响应里找 location 字段(可能在顶层, 也可能嵌在子结构里)。"""
    if not isinstance(params, dict):
        return None
    if params.get("location") is not None:
        return params.get("location")
    for v in params.values():
        if isinstance(v, dict) and v.get("location") is not None:
            return v.get("location")
    return None


def _params(resp):
    return resp.get("__params__") or resp or {}


def _err_hint(code):
    """错误码 -> 人话提示(告诉用户下一步该做什么)。"""
    c = str(code or "").strip().upper()
    if c in ("E100165", "100165"):
        return ("没有「坐标侦查」道具 —— 服务端要消耗 1 个(道具 id 212054)才能查坐标。"
                "请先在游戏里获得坐标侦查道具, 或到商城/活动里换取。")
    if c in ("E000000", "000000"):
        return "服务端认为参数无效(命令名存在, 但参数不对)"
    if c in ("102192", "E102192"):
        return "该功能未开启"
    if c in ("E100047", "100047"):
        return "体力不足"
    return "服务端拒绝(%s)" % code


def _players_from(params):
    """从响应里挖出玩家列表。

    服务端可能用几种形状返回:
      {array: [...]} / {list: [...]} / {players: [...]} / 直接是 list
    每个元素: {name, uid, ...}
    """
    for key in ("array", "list", "players", "records", "result"):
        v = params.get(key)
        if isinstance(v, list):
            return [x for x in v if isinstance(x, dict)]
    if isinstance(params.get("__params__"), list):
        return params["__params__"]
    # 兜底: 找所有看起来像玩家的子字典
    out = []
    for k, v in params.items():
        if k.startswith("_"):
            continue
        if isinstance(v, dict) and ("uid" in v or "name" in v):
            out.append(v)
    return out


def search_players(client, name, item=SPY_ITEM_LOC, limit=20):
    """按名字搜索玩家(第一次请求, 拿候选 uid 列表)。

    返回 {ok, errorCode, error, players:[{name, uid, ...}], raw}
    """
    if not name or not str(name).strip():
        return {"ok": False, "error": "请输入玩家名字"}
    try:
        r = client.call("search.player.spy",
                        {"userName": str(name).strip(), "item": str(item)})
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "error": str(e)[:160]}
    p = _params(r)
    if p.get("errorCode"):
        return {"ok": False, "errorCode": p.get("errorCode"),
                "error": _err_hint(p.get("errorCode"))}
    players = _players_from(p)
    return {
        "ok": True,
        "errorCode": None,
        "players": [{"name": x.get("name"), "uid": x.get("uid"),
                     "level": x.get("level"), "alliance": x.get("allianceName")
                     or x.get("alliance")}
                    for x in players[:limit]],
        "total": len(players),
        "location": _dig_location(p),
        "raw": p,
    }


def locate(client, name, uid=None, item=SPY_ITEM_LOC, server_id=None):
    """按名字(可选 uid)查玩家坐标。

    流程: 先搜出候选 -> 选中目标(有 uid 用 uid, 否则取第一个) -> 再发一次
    拿 location -> 换算成 x,y。

    返回 {ok, errorCode, error, name, uid, location, x, y, candidates}
    """
    if not name or not str(name).strip():
        return {"ok": False, "error": "请输入玩家名字"}
    key = str(name).strip()

    # 第 1 步: 搜候选
    s = search_players(client, key, item=item)
    if not s.get("ok"):
        return s
    cands = s.get("players") or []
    # ⚠️ 如果第 1 次就带回了 location, **不要**再发第 2 次 ——
    #    每次请求服务端都可能扣一个「坐标侦查」道具, 发两次就白费一个。
    loc0 = s.get("location")
    if loc0 is None:
        loc0 = _dig_location(s.get("raw") or {})
    if loc0 is not None:
        pt = index_to_point(loc0)
        if pt:
            return {"ok": True, "errorCode": None,
                    "name": (cands[0].get("name") if cands else key),
                    "uid": (cands[0].get("uid") if cands else None),
                    "location": int(loc0), "x": pt[0], "y": pt[1],
                    "candidates": cands, "raw": s.get("raw")}
    if not cands:
        return {"ok": False, "error": "没有找到叫「%s」的玩家" % key,
                "candidates": []}

    # 选中目标
    target = None
    if uid:
        for c in cands:
            if str(c.get("uid")) == str(uid):
                target = c
                break
    if target is None:
        target = cands[0]

    # 第 2 步: 再发一次拿 location
    # 客户端是选中后用**同一个命令**再查一次, 服务端这次才回 location
    params = {"userName": key, "item": str(item)}
    if target.get("uid"):
        params["uid"] = str(target["uid"])
    if server_id is not None:
        params["serverId"] = int(server_id)
    try:
        r = client.call("search.player.spy", params)
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "error": str(e)[:160], "candidates": cands}
    p = _params(r)
    if p.get("errorCode"):
        return {"ok": False, "errorCode": p.get("errorCode"),
                "error": _err_hint(p.get("errorCode")),
                "candidates": cands}

    loc = _dig_location(p)
    if loc is None:
        return {"ok": False, "error": "服务端没有返回坐标(可能没有坐标侦查道具, "
                                      "或该玩家当前不在可侦察状态)",
                "candidates": cands, "raw": p}

    pt = index_to_point(loc)
    if not pt:
        return {"ok": False, "error": "无法解析点位 index %r" % loc,
                "candidates": cands}
    return {
        "ok": True,
        "errorCode": None,
        "name": target.get("name") or key,
        "uid": target.get("uid"),
        "location": int(loc),
        "x": pt[0],
        "y": pt[1],
        "candidates": cands,
        "raw": p,
    }
