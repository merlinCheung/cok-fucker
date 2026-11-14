#!/usr/bin/env python3
"""COK 巨型狮鹫(活动怪首领) + 联盟集结(rally) 直连封装。

⚠️ 来源与风险(先读)
------------------------
本模块的命令**全部已在真服实测通过**(2026-11-01 / 11-02), 但集结出征**有真实副作用**:
消耗体力(首领怪 20/次) + 士兵, 并在联盟里建一个集结(其他人能加入)。
所以对外只提供**显式触发**的接口, 不放进自动循环里偷偷发。

协议链(客户端逆向 + 真服实测)
--------------------------------
巨型狮鹫是「活动怪首领」(客户端 ItemSpec id 902113/902114/902115/902150,
name=650066, boss="2" 表示首领怪):

  1. 找怪   res.tile.find {type:7, level:N}   -> 活动怪坐标(x/y)
     ⚠️ 但这个命令**每日次数有限**(客户端 maxSearchCount, 测到用完就找不到)。
        → 所以本模块改用下面的 world.get 方式, 不限次。

  2. 定位   world.get {x,y,type:0,serverId,timeStamp}  -> 一整片地块
     地块里 **t=15**(WorldCityType.ActBossTile) 且 **t1=monsterId** 的就是首领怪:
         {"t":15, "i":803271, "t1":"902113", "mchp":720000, "mmhp":720000,
          "st":...,"rt":...}
     - t1 = 902113(12级) / 902114(21级) / 902115(30级) / 902150(35级)
     - i = 地图 index(与 point_index(x,y) 互逆)
     - mchp/mmhp = 当前/最大血量; st/rt = 出现/刷新时间
     → 实测一次能扫到几十只巨型狮鹫, **不限次数**。

  3. 集结   world.march {point, type:4, soldiers, marchKey, wtIndex:N}
     - type=4 = MarchMethodType.MethodRally(客户端 gameConst.lua)
     - wtIndex = **集结时长档位序号 1..4**, 客户端只发序号, 服务端按自己的
       配置换算成实际分钟数。
     - 集结时长来自服务端 `login.dataconfig` 的 `dataConfig.world_rally`:
       k1=5 / k2=10 / k3=30 / k4=60 分钟(2026-11-01 实测, 区服不同会不同)
     - marchKey 用 type=4 参与计算(和打野怪的 type=6 不同!)
     → 真服实测: 一次成功, 体力 154->134(-20), 联盟集结列表出现本队

实测确认的"档位 -> 实际时长"(2026-11-02, 只读 alliance.team.ls 交叉验证)
----------------------------------------------------------------------
  服务端下发的集结列表里, 每支集结都有 createTime / waitTime / marchTime
  (单位是**毫秒**!), 差值就是真实时长:
      21 级巨型狮鹫的 3 支集结, waitTime - createTime = **正好 5.0 分钟**
      → wtIndex=1 对应 k1=5 分钟, 服务端精确按配置执行。
  (客户端显示值还会被"集结时间"作用号 JIJIE_TIME/JIJIE_SUBT 修正,
   那是客户端本地显示, 服务端实际执行的是 k 值。)

错误码(设备 text_zh_CN.ini 实测)
------------------------------
  115212 = 对同一个敌人只能创建一支队伍   (同一目标已有集结)
  115218 = 需要加入联盟才能使用集结功能
  115219 = 队伍已经出发，不能加入
  113228 = 今日剩余使用次数不足            (res.tile.find 用完)

⚠️ 服务端限流(2026-11-02 实测)
------------------------------
  * 连续 `world.get` **不间隔**时, 服务端会直接**不响应**(客户端超时)。
    → 扫描必须带 SCAN_INTERVAL 间隔。
  * 连续 `world.get` 约 **70 次**后, 服务端会**主动断开连接**
    ("连接被服务端关闭(已收 0/3 字节)"), 之后重试全是 Broken pipe。
    → 扫描必须能**重建连接**后继续(on_reconnect 回调)。
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
import os
import time

from cok_sfs import TypedInt, SFS_INT

HERE = os.path.dirname(os.path.abspath(__file__))

#: 客户端 MarchMethodType.MethodRally(集结)
MARCH_TYPE_RALLY = 4

#: WorldCityType.ActBossTile(活动怪 boss 地块)
ACT_BOSS_TILE = 15

#: 巨型狮鹫 ItemSpec id -> 等级
#: (客户端配置 field_monster 组, name=650066, monster="shi_ying_3_X")
BOSS_IDS = {
    "902113": 12,
    "902114": 21,
    "902115": 30,
    "902150": 35,
}
#: 等级 -> ItemSpec id(反查)
BOSS_ID_BY_LEVEL = {v: k for k, v in BOSS_IDS.items()}

#: 集结时长档位数(客户端 4 个按钮 m_btn1..m_btn4)
RALLY_SLOTS = 4

#: 集结时间配置的兜底值(服务端没给时用)
#: 实测 2026-11-01 区服 world_rally: k1=5 k2=10 k3=30 k4=60(分钟)
RALLY_FALLBACK_MINUTES = (5, 10, 30, 60)

#: 首领怪每次攻击消耗的体力(客户端 ItemSpec usePower; boss_decr=20)
BOSS_STAMINA_COST = 20

#: 连续 world.get 之间至少隔这么久(秒)。
#: ⚠️ 实测: 不间隔连打 20 次 world.get, 服务端会**直接不响应**(客户端超时)。
SCAN_INTERVAL = 0.15

#: world.get 单次覆盖窗口(实测 2026-11-02)。
#: x 中心 ±12 (24 格宽), y 中心 -13~+11 (25 格高)。空地块不下发, 所以返回条数远小于窗口面积。
SCAN_WIN_X = 24
SCAN_WIN_Y = 25

#: 世界尺寸(客户端 WorldController.lua: _tile_count_x/_tile_count_y = 1201)
WORLD_SIZE = 1201

#: 采样步长。world.get 一次只覆盖 24x25 格, 步长 > 它就是"抽样"而不是"铺满"。
#: ⚠️ 实测(2026-11-02): 巨型狮鹫是**全图分布**的 —— 随机取 16 个点, 14 个点都
#:    扫到了 boss(18 只)。所以**不需要知道出生区域**, 随便扫就能找到。
#:    (之前误以为 boss 只在一个小区域内, 是因为那里恰好是个密集区。)
#:    步长只决定"多久把全图扫一遍": 50 -> 24x24 = 576 个采样点。
SCAN_STRIDE = 50

#: 已知巨型狮鹫注册表: index -> {index, monsterId, level, hp, maxHp, x, y, seen_at}
#: 用**累积**而不是"只留本轮": 首领怪会动态刷新(被打掉后换位置),
#: 注册表让页面随着扫描慢慢补全目标列表。
#:
#: ⚠️ **按账号隔离**: 这是**进程内共享**的可变状态, 五个引擎并行跑时如果共用一份,
#:    A 号扫到的怪会混进 B 号的目标列表, 落盘也会写到同一个文件
#:   (表现为"我点 A 号的扫描, B 号的狮鹫列表也变了")。
#:   所以按 uid 分桶: `_known_for(uid)` 返回该账号的桶, 所有读写都走它。
_KNOWN_BY_UID = {}
#: 多久没再见到就认为这只已经消失(被打掉 / 刷新到别处)
_KNOWN_TTL = 6 * 3600.0

#: 轮转扫描游标(**按账号**, 同上): 下一次从网格里的第几个中心开始
_CURSOR_BY_UID = {}

#: 注册表落盘目录(**按账号**, 同上)
_DIR_BY_UID = {}

#: 兼容: 无 uid 调用点(单账号 / 老脚本)用的"默认桶"
#: ⚠️ 这两个名字必须继续存在: 老代码 / 老测试直接用 `cok_rally._KNOWN` 读写。
#: 默认桶就是"没传 uid 的那一份", 语义与改造前一致。
_DEFAULT_UID = ""
#: 默认桶的注册表(就是改造前的那个模块级 `_KNOWN`, 名字保留给老代码/老测试)。
#: ⚠️ `_known_for("")` / `_cursor_for("")` **故意**映射到这两个对象: 老测试
#: 直接 `cok_rally._KNOWN.clear()` / `cok_rally._CURSOR = 0` 仍然生效,
#: 不需要改测试写法。非空 uid 才走按账号分桶。
_KNOWN = {}
_CURSOR = 0
_KNOWN_BY_UID[_DEFAULT_UID] = _KNOWN
_CURSOR_BY_UID[_DEFAULT_UID] = _CURSOR

#: 注册表落盘文件(按账号隔离: 多账号时 COK_DATA_DIR 各不相同)
#:
#: ⚠️ **安卓端不能回退到模块所在目录**(那在 Chaquopy 的 assets 里, 只读)——
#:    运行时会写进打包资源目录, 重装即丢还污染 APK(安卓 README 记的坑 #2)。
#:    所以默认回退到 `accounts.DATA_ROOT`(安卓端 = files/cok/data)。
try:
    import cok_accounts as _accounts
    DATA_DIR = os.environ.get("COK_DATA_DIR") or _accounts.DATA_ROOT
except Exception:  # noqa: BLE001
    DATA_DIR = os.environ.get("COK_DATA_DIR") or HERE
REGISTRY_FILE = os.path.join(DATA_DIR, "boss-registry.json")

#: 集结时长档位缓存(服务端配置基本不变, 缓存久一点省一次 dataconfig)
#: ⚠️ **按区服分桶**: 不同账号可能在不同区服, 各区的集结时长档位不同;
#:   共用一份缓存 = 后一个账号拿到前一个区服的时长, 于是"集结 5 分钟"变 60 分钟。
_SLOT_CACHE = {}
_SLOT_TTL = 120.0

#: 网格中心缓存(纯本地计算, 区服无关, 全局一份即可)
_GRID_CACHE = {"at": 0.0, "centers": []}


def _I(v):
    """强制 INT 类型(服务端对类型敏感)。"""
    return TypedInt(int(v), SFS_INT)


def _params(resp):
    return resp.get("__params__") or resp or {}


def _as_int(v, default=None):
    try:
        return int(v)
    except (TypeError, ValueError):
        return default


def _as_float(v, default=None):
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


def _ms(v):
    """服务端时间戳是**毫秒**(实测 2026-11-02), 统一成秒。"""
    n = _as_int(v)
    if n is None:
        return None
    if n > 100000000000:  # 13 位 = 毫秒
        return n / 1000.0
    return float(n)


# --------------------------------------------------------------------------
# 集结时长配置
# --------------------------------------------------------------------------

def read_rally_slots(client, use_cache=True, server_id=None):
    """读服务端下发的 4 档集结时长(分钟)。

    来源: `login.dataconfig` -> `dataConfig.world_rally` 的 k1..k4。
    实测: k1=5 k2=10 k3=30 k4=60(分钟)。不同区服可能不同, 所以**每次都读**,
    不写死。

    ⚠️ 缓存按**区服**分桶(server_id): 不同账号可能在不同区服, 档位不同,
    共用一份缓存会让"集结 5 分钟"变成另一个区的 60 分钟。
    返回 [{slot:1, minutes:5}, {slot:2, minutes:10}, ...]
    """
    now = time.time()
    ckey = str(server_id or "")
    cached = _SLOT_CACHE.get(ckey)
    if use_cache and cached and (now - cached["at"]) < _SLOT_TTL:
        return [dict(s) for s in cached["slots"]]
    minutes = list(RALLY_FALLBACK_MINUTES)
    try:
        r = client.call("login.dataconfig")
        p = _params(r)
        dc = p.get("dataConfig")
        if isinstance(dc, str):
            try:
                dc = json.loads(dc)
            except (ValueError, TypeError):
                dc = None
        if isinstance(dc, dict):
            wr = dc.get("world_rally")
            if isinstance(wr, dict):
                for i in range(RALLY_SLOTS):
                    v = _as_int(wr.get("k%d" % (i + 1)))
                    if v:
                        minutes[i] = v
    except Exception:  # noqa: BLE001
        pass
    slots = [{"slot": i + 1, "minutes": minutes[i]} for i in range(RALLY_SLOTS)]
    _SLOT_CACHE[ckey] = {"at": now, "slots": slots}
    return [dict(s) for s in slots]


# --------------------------------------------------------------------------
# 区域 / 扫描网格
# --------------------------------------------------------------------------

def map_centers():
    """全图采样中心网格(缓存)。

    步长 SCAN_STRIDE > world.get 窗口, 所以这是**抽样**: 每个点大概能碰到
    1 只巨型狮鹫(实测密度)。轮转扫完一轮 = 全图扫了一遍。
    """
    now = time.time()
    if _GRID_CACHE["centers"] and (now - _GRID_CACHE["at"]) < 300.0:
        return list(_GRID_CACHE["centers"])
    step = SCAN_STRIDE
    off = 12
    xs = list(range(off, WORLD_SIZE, step))
    ys = list(range(off, WORLD_SIZE, step))
    centers = [(x, y) for y in ys for x in xs]
    _GRID_CACHE.update({"at": now, "centers": centers})
    return list(centers)


# --------------------------------------------------------------------------
# 扫描地块
# --------------------------------------------------------------------------

def fetch_area(client, x, y, server_id=2223, retries=2):
    """拉一片地块(world.get)。返回地块 list。

    ⚠️ 服务端在高频 world.get 下会**丢响应**(不回复), 所以这里要:
       1) 每次换新的 timeStamp(否则会拿到错位的旧响应)
       2) 失败后 sleep 一小会再重试(最多 retries 次)
       3) 调用方之间留 SCAN_INTERVAL 间隔
    """
    last = None
    for attempt in range(retries + 1):
        try:
            r = client.call("world.get", {
                "x": _I(x), "y": _I(y), "type": _I(0), "serverId": _I(server_id),
                "timeStamp": _I(int(time.time() * 1000) % 100000000),
            }, retries=0)
            p = _params(r)
            if p.get("errorCode"):
                return []
            return _parse_tiles(p)
        except Exception as e:  # noqa: BLE001
            last = e
            if attempt < retries:
                time.sleep(0.8)
    if last is not None:
        raise last
    return []


def _parse_tiles(p):
    """把 world.get 的 points 拆成地块 list。"""
    out = []
    for it in (p.get("points") or []):
        if isinstance(it, dict):
            out.append(it)
            continue
        if not isinstance(it, str):
            continue
        try:
            got = json.loads(it)
        except (ValueError, TypeError):
            continue
        if isinstance(got, list):
            out.extend(g for g in got if isinstance(g, dict))
        elif isinstance(got, dict):
            out.append(got)
    return out


def _uid_key(uid):
    """把 uid 归一成桶名。空 / None ⇒ 默认桶(兼容单账号与老调用点)。"""
    return str(uid or _DEFAULT_UID)


def _known_for(uid=None):
    """该账号的注册表桶(进程内、按 uid 隔离)。"""
    return _KNOWN_BY_UID.setdefault(_uid_key(uid), {})


def _cursor_for(uid=None):
    return _CURSOR_BY_UID.setdefault(_uid_key(uid), 0)


def set_cursor(uid, value):
    """设置该账号的扫描游标(测试 / 手工跳转用)。"""
    _CURSOR_BY_UID[_uid_key(uid)] = int(value or 0)
    return _CURSOR_BY_UID[_uid_key(uid)]


def _dir_for(uid=None):
    """该账号的注册表目录。没显式设过 ⇒ 默认数据根目录。"""
    return _DIR_BY_UID.get(_uid_key(uid)) or DATA_DIR


def _registry_file(uid=None):
    return os.path.join(_dir_for(uid), "boss-registry.json")


def _merge_tiles(tiles, now, uid=None):
    """把地块并进该账号的注册表, 返回新发现的数量。"""
    known = _known_for(uid)
    new = 0
    for t in tiles:
        if _as_int(t.get("t")) != ACT_BOSS_TILE:
            continue
        mid = str(t.get("t1") or "")
        if mid not in BOSS_IDS:
            continue
        idx = _as_int(t.get("i"))
        if not idx:
            continue
        n = idx - 1
        tile = {
            "index": idx,
            "monsterId": mid,
            "level": BOSS_IDS.get(mid),
            "hp": _as_int(t.get("mchp")),
            "maxHp": _as_int(t.get("mmhp")),
            "x": n % WORLD_SIZE,
            "y": n // WORLD_SIZE,
            "start": _ms(t.get("st")),
            "refresh": _ms(t.get("rt")),
        }
        if idx not in known:
            new += 1
        known[idx] = tile
        known[idx]["seen_at"] = now
    return new


def _prune_known(now, uid=None):
    """太久没再见到 -> 认为这只已经消失。"""
    known = _known_for(uid)
    for idx in list(known):
        if now - known[idx].get("seen_at", 0) > _KNOWN_TTL:
            del known[idx]


def set_data_dir(path, uid=None):
    """把注册表目录指到 path(切账号时由网页调用)。

    和 `cok_map.set_data_dir` 一个套路: 跟着账号隔离, 每个账号一份注册表。
    path 为空 -> 回到默认的可写数据根目录(安卓端 = files/cok/data)。

    ⚠️ **uid 是隔离的关键**: 给了 uid 只影响该账号的桶; 不给 ⇒ 只改"默认桶"
    (单账号 / 老脚本)。**绝不能**再改模块级全局 REGISTRY_FILE —— 五个引擎并行时,
    后解析的账号会把前面的目录覆盖掉, 于是所有号的注册表都写到最后一个账号的文件里。
    """
    global DATA_DIR
    try:
        import cok_accounts as _accounts
        default = _accounts.DATA_ROOT
    except Exception:  # noqa: BLE001
        default = HERE
    DATA_DIR = path or default
    _DIR_BY_UID[_uid_key(uid)] = DATA_DIR
    try:
        os.makedirs(DATA_DIR, exist_ok=True)
    except Exception:  # noqa: BLE001
        pass
    return DATA_DIR


def load_registry(uid=None):
    """从磁盘读回已知的巨型狮鹫(让页面重启后不用重新扫)。"""
    try:
        with open(_registry_file(uid)) as f:
            data = json.load(f)
    except Exception:  # noqa: BLE001
        return
    tiles = data.get("tiles") if isinstance(data, dict) else None
    if not isinstance(tiles, dict):
        return
    now = time.time()
    known = _known_for(uid)
    for k, v in tiles.items():
        if not isinstance(v, dict):
            continue
        idx = _as_int(v.get("index"))
        if not idx:
            continue
        v["index"] = idx
        v["seen_at"] = _as_float(v.get("seen_at"), 0.0) or 0.0
        if now - v["seen_at"] > _KNOWN_TTL:
            continue
        known[idx] = v


def save_registry(uid=None):
    """把该账号的注册表写到磁盘(按账号隔离的数据目录)。"""
    try:
        d = _dir_for(uid)
        os.makedirs(d, exist_ok=True)
        path = _registry_file(uid)
        tmp = path + ".tmp"
        with open(tmp, "w") as f:
            json.dump({"at": time.time(), "tiles": _known_for(uid)}, f,
                      ensure_ascii=False)
        os.replace(tmp, path)
        return True
    except Exception:  # noqa: BLE001
        return False


#: 「扫描」按钮一次多扫多少个采样点(约 0.7s/点 -> 24 个约 17s)
SCAN_BATCH = 24


def scan_bosses(client, server_id=2223, levels=None, full=False, slice_size=8,
                on_reconnect=None, save=True, uid=None):
    """扫描地图上的巨型狮鹫。

    ⚠️ 两个服务端限制决定了这里的设计(2026-11-02 实测):
       1. 连续 world.get 不间隔 -> 服务端不响应
       2. 连续 world.get 约 70 次 -> 服务端**主动断开连接**
       所以: **每次只扫一小片**(轮转), 靠注册表累积出目标列表;
       连接断了用 on_reconnect 回调重建后继续。

    full=True: 一次多扫 SCAN_BATCH 个采样点(用户点「扫描」),
       仍然**不是**全图 —— 全图 576 个点要 7 分钟, 不能让人干等。
    uid: 账号 id。**必须传**(网页端每个引擎传自己的), 否则会串到默认桶,
       表现为"多账号扫描结果混在一起"。

    ⚠️ **返回值里的 bosses 是该账号注册表的累积结果**(老行为), 不是"本轮扫到的"。
       要判断"本轮新发现", 看 `new_bosses`。
    """
    centers = map_centers()
    cursor = _cursor_for(uid)
    n = SCAN_BATCH if full else max(1, min(slice_size, len(centers)))
    todo = [centers[(cursor + i) % len(centers)] for i in range(n)]
    _CURSOR_BY_UID[_uid_key(uid)] = (cursor + n) % len(centers)

    now = time.time()
    cl = client
    scanned = 0
    new_tiles = []      # 本轮扫到的地块(累积进注册表之前先留一份)
    for cx, cy in todo:
        try:
            tiles = fetch_area(cl, cx, cy, server_id=server_id)
        except Exception:  # noqa: BLE001
            if on_reconnect is None:
                break
            try:
                cl = on_reconnect(cl)
            except Exception:  # noqa: BLE001
                break
            try:
                tiles = fetch_area(cl, cx, cy, server_id=server_id)
            except Exception:  # noqa: BLE001
                break
        scanned += 1
        new_tiles.extend(tiles)
        _merge_tiles(tiles, now, uid)
        time.sleep(SCAN_INTERVAL)

    _prune_known(now, uid)
    if save and scanned:
        save_registry(uid)
    known = _known_for(uid)
    # 本轮扫到的(去重、按等级过滤)—— 给"多账号同时跑"用: 否则 A 号会看到
    # B 号注册表里的目标, 一次出征可能打到别人的图上(而且扫完永远只报同样的列表)。
    scanned_set = {}
    for t in new_tiles:
        if _as_int(t.get("t")) != ACT_BOSS_TILE:
            continue
        mid = str(t.get("t1") or "")
        if mid not in BOSS_IDS:
            continue
        idx = _as_int(t.get("i"))
        if not idx or idx in scanned_set:
            continue
        n_ = idx - 1
        scanned_set[idx] = {
            "index": idx,
            "monsterId": mid,
            "level": BOSS_IDS.get(mid),
            "hp": _as_int(t.get("mchp")),
            "maxHp": _as_int(t.get("mmhp")),
            "x": n_ % WORLD_SIZE,
            "y": n_ // WORLD_SIZE,
            "start": _ms(t.get("st")),
            "refresh": _ms(t.get("rt")),
        }
    bosses = [dict(t) for t in known.values()]
    new_bosses = list(scanned_set.values())
    want = set(BOSS_IDS) if not levels else {
        bid for bid, lv in BOSS_IDS.items() if lv in levels}
    bosses = [b for b in bosses if b["monsterId"] in want]
    bosses.sort(key=lambda b: (b.get("level") or 0, b.get("index") or 0))
    new_bosses = [b for b in new_bosses if b["monsterId"] in want]
    new_bosses.sort(key=lambda b: (b.get("level") or 0, b.get("index") or 0))
    return {
        "bosses": bosses,
        "new_bosses": new_bosses,
        "scanned": scanned,
        "grid": len(centers),
        "cursor": _cursor_for(uid),
        "known": len(known),
    }


def find_boss_tiles(client, levels=None, server_id=2223, centers=None,
                    use_cache=True, expand=True, slice_size=8):
    """兼容入口: 拿巨型狮鹫地块 list。

    (老参数 centers/use_cache/expand 保留, 但现在走轮转扫描。)
    """
    r = scan_bosses(client, server_id=server_id, levels=levels,
                    slice_size=slice_size)
    return r["bosses"]


def pick_boss_tile(client, level=None, server_id=2223, exclude=(), uid=None):
    """挑一个巨型狮鹫地块。

    优先: 血量最少(快打死的) -> 等级最接近要的 -> index 小。
    同一目标只能有一支集结(错误码 115212), 所以 exclude 里的 index 别选。
    """
    tiles = scan_bosses(client, server_id=server_id,
                        levels=(level,) if level else None,
                        uid=uid)["bosses"]
    busy = set(int(x) for x in (exclude or ()))
    tiles = [t for t in tiles if t["index"] not in busy]
    if not tiles:
        return None
    tiles.sort(key=lambda b: (b.get("hp") if b.get("hp") is not None else 10 ** 12,
                               b.get("index") or 0))
    return tiles[0]


# --------------------------------------------------------------------------
# 集结出征
# --------------------------------------------------------------------------

def rally_march(client, index, army_id, speed, load, num,
                slot=1, monster_id="", general_id="", pet_dragon_uid="",
                aormation_id=""):
    """向巨型狮鹫发起**集结**(type=4)。

    ⚠️ **真实副作用**: 扣体力(首领怪 20) + 士兵, 并在联盟里建一个集结。
    slot: 集结时长档位 1..4(实际分钟数由服务端 world_rally 决定)

    返回 {ok, errorCode, note, uuid, ...}
    """
    from cok_hunt import march_key

    slot = max(1, min(RALLY_SLOTS, int(slot or 1)))
    army = {str(int(army_id)): (speed, load, int(num))}
    key = march_key(int(index), army, march_type=MARCH_TYPE_RALLY)
    params = {
        "point": _I(index),
        "type": _I(MARCH_TYPE_RALLY),
        "soldiers": {str(int(army_id)): TypedInt(int(num), SFS_INT)},
        "generalId": general_id or "",
        "petDragonUid": pet_dragon_uid or "",
        "aormationId": aormation_id or "",
        "autoQueue": 0,
        "marchKey": key,
        # ★ 集结时长档位序号(客户端只发序号, 服务端换算成分钟)
        "wtIndex": _I(slot),
    }
    r = client.call("world.march", params)
    p = _params(r)
    code = p.get("errorCode")
    if code:
        return {"ok": False, "errorCode": code, "slot": slot,
                "note": _rally_error_note(code)}
    abt = p.get("allianceBattleTeam") or {}
    return {
        "ok": True,
        "slot": slot,
        "uuid": abt.get("uuid"),
        "teamId": abt.get("teamId"),
        "monsterId": abt.get("monsterId") or monster_id,
        "startTime": _ms(abt.get("startTime")),
        "endTime": _ms(abt.get("endTime")),
        "arrivalTime": _ms(abt.get("arrivalTime")),
        "member": abt.get("member") or [],
        "totalTroops": abt.get("totalTroops"),
        "result": p,
    }


def _rally_error_note(code):
    """把服务端错误码翻成人话(设备 text_zh_CN.ini 实测)。"""
    return {
        "115212": "对同一个目标只能有一支集结(等这次的结束, 或换一个 boss)",
        "115218": "需要加入联盟才能使用集结功能",
        "115219": "队伍已经出发，不能加入",
        "113228": "今日搜索次数不足(找怪用完了)",
        "E100047": "体力不足",
    }.get(str(code), "服务端拒绝(%s)" % code)


# --------------------------------------------------------------------------
# 联盟集结列表
# --------------------------------------------------------------------------

def read_alliance_rallies(client, side=1):
    """读联盟集结列表。

    实测 `alliance.team.ls {side:1}` 可用(不需要额外参数), 返回:
      list[]  各集结队伍
      helplist[] 求助列表

    list 里每条集结(2026-11-02 实测字段):
      targetType=15  -> 目标是活动怪首领(ActBossTile)
      targetId       -> **目标的地图 index**(判定"这个 boss 已有集结"要用它,
                        不能用 monsterId —— 同一个等级有几十只 boss)
      monsterId      -> 902113/902114/902115/902150
      createTime / waitTime / marchTime  -> **毫秒**时间戳
          waitTime - createTime = 集结等待时长(分钟) = 服务端实际执行的档位时长
      attackId       -> 发起人 uid
      attackName     -> 发起人名字
    """
    r = client.call("alliance.team.ls", {"side": int(side)})
    p = _params(r)
    if p.get("errorCode"):
        return {"ok": False, "errorCode": p.get("errorCode"), "list": []}
    out = []
    for it in (p.get("list") or []):
        if not isinstance(it, dict):
            continue
        ct = _ms(it.get("createTime"))
        wt = _ms(it.get("waitTime"))
        out.append({
            "uuid": it.get("uuid"),
            "teamId": it.get("teamId"),
            "monsterId": it.get("monsterId"),
            "targetType": it.get("targetType"),
            "targetId": _as_int(it.get("targetId")),
            "attackId": it.get("attackId"),
            "attackName": it.get("attackName"),
            "createTime": ct,
            "waitTime": wt,
            "marchTime": _ms(it.get("marchTime")),
            # 服务端实际执行的集结等待时长(分钟)
            "wait_minutes": round((wt - ct) / 60.0, 1) if (ct and wt) else None,
            "totalTroops": it.get("totalTroops"),
            "currSoldiers": it.get("currSoldiers"),
            "mySide": it.get("mySide"),
            "member": it.get("member") or [],
            "members": len(it.get("member") or []),
        })
    return {"ok": True, "list": out, "helplist": p.get("helplist") or []}


def my_rallies(client, game_uid=None, side=1):
    """只挑出**本账号**发起/参与的集结。

    归属判定(2026-11-02 实测字段): attackId == 本账号 uid,
    或 member 里的 uid / userId == 本账号 uid。
    """
    r = client.call("alliance.team.ls", {"side": int(side)})
    p = _params(r)
    uid = str(game_uid or "")
    out = []
    for it in (p.get("list") or []):
        if not isinstance(it, dict):
            continue
        if uid and str(it.get("attackId") or "") == uid:
            out.append(it)
            continue
        for m in (it.get("member") or []):
            if not isinstance(m, dict):
                continue
            if str(m.get("uid") or "") == uid or str(m.get("userId") or "") == uid:
                out.append(it)
                break
    return out


def busy_targets(client, game_uid=None, side=1):
    """已经有人建了集结的目标 index 集合。

    ⚠️ 用 targetId(目标地块 index), **不是 monsterId** ——
    同一个等级有几十只 boss, 用 monsterId 会把整片都标成"已有集结"。
    """
    r = client.call("alliance.team.ls", {"side": int(side)})
    p = _params(r)
    busy = set()
    for it in (p.get("list") or []):
        if not isinstance(it, dict):
            continue
        if _as_int(it.get("targetType")) != ACT_BOSS_TILE:
            continue
        tid = _as_int(it.get("targetId"))
        if tid:
            busy.add(tid)
    return busy


# --------------------------------------------------------------------------
# 快照
# --------------------------------------------------------------------------

def snapshot(client, server_id=2223, force=False, slice_size=8,
             on_reconnect=None, game_uid=None, save=True, uid=None):
    """一次拿到网页需要的全部只读信息。

    force=True 时多扫几片(用户点了「扫描」), 否则只推进一小片(轮转)。
    uid: 账号 id。**必须传**(网页端每个引擎传自己的), 否则注册表/游标会串到默认桶。
    """
    uid = uid if uid is not None else game_uid
    load_registry(uid)
    slots = read_rally_slots(client, server_id=server_id)
    sc = scan_bosses(client, server_id=server_id, full=force,
                     slice_size=slice_size, on_reconnect=on_reconnect,
                     save=save, uid=uid)
    bosses = sc["bosses"]
    # 页面上的「狮鹫列表」应当反映**本账号**当前实际能打的:
    # 有 force(用户点了扫描) -> 本轮扫到的; 否则 -> 轮转扫描的累积注册表。
    # (以前一律用注册表, 多账号并行时 A 号会看到 B 号扫到的怪。)
    if force:
        bosses = sc.get("new_bosses") or bosses
    r = read_alliance_rallies(client)
    rlist = r.get("list") or []
    busy = set()
    for it in rlist:
        if _as_int(it.get("targetType")) == ACT_BOSS_TILE:
            tid = _as_int(it.get("targetId"))
            if tid:
                busy.add(tid)
    for b in bosses:
        b["busy"] = b["index"] in busy
    mine = []
    uid = str(game_uid or "")
    for it in rlist:
        is_mine = bool(uid) and str(it.get("attackId") or "") == uid
        if not is_mine and uid:
            for m in (it.get("member") or []):
                if isinstance(m, dict) and (
                        str(m.get("uid") or "") == uid
                        or str(m.get("userId") or "") == uid):
                    is_mine = True
                    break
        if is_mine:
            mine.append({
                "uuid": it.get("uuid"),
                "teamId": it.get("teamId"),
                "monsterId": it.get("monsterId"),
                "targetId": it.get("targetId"),
                "wait_minutes": it.get("wait_minutes"),
                "createTime": it.get("createTime"),
                "waitTime": it.get("waitTime"),
                "totalTroops": it.get("totalTroops"),
                "members": it.get("members"),
            })
    return {
        "slots": slots,
        "bosses": bosses,
        "boss_levels": sorted({b["level"] for b in bosses if b.get("level")}),
        "rally_count": len(rlist),
        "rally_list": rlist,
        "my_rallies": mine,
        "stamina_cost": BOSS_STAMINA_COST,
        "boss_ids": BOSS_IDS,
        "scan": {"scanned": sc["scanned"], "grid": sc["grid"],
                 "cursor": sc["cursor"], "known": sc["known"]},
    }


def main():
    """CLI: 读集结状态 / 发起集结。

    用法:
      python3 cok_rally.py --account device            # 读状态(只读)
      python3 cok_rally.py --account device --start 12 # 对 12 级巨型狮鹫发起集结(档位1)
      python3 cok_rally.py --account device --start 12 --slot 3
    """
    import argparse
    import sys

    sys.path.insert(0, HERE)
    from cok_accounts import get_account
    from cok_client import CokClient

    ap = argparse.ArgumentParser(description="COK 巨型狮鹫 + 联盟集结")
    ap.add_argument("--account", default="", help="账号 id(gameUid)或 device")
    ap.add_argument("--start", type=int, default=0, help="要打的等级(0=只读)")
    ap.add_argument("--slot", type=int, default=1, help="集结时长档位 1..4")
    ap.add_argument("--num", type=int, default=200, help="派兵数量")
    ap.add_argument("--full", action="store_true", help="全量扫描(慢, 会自动重连)")
    args = ap.parse_args()

    acc = None
    if args.account and args.account != "device":
        acc = get_account(args.account)
    cl = CokClient(account=acc, timeout=25.0).connect()
    cl.bin_handshake()
    cl.login()
    for _ in range(2):
        try:
            cl.call("cmd.ping")
        except Exception:
            pass

    def _reconnect(old):
        nonlocal cl
        try:
            old.close()
        except Exception:
            pass
        cl = CokClient(account=acc, timeout=25.0).connect()
        cl.bin_handshake()
        cl.login()
        return cl

    try:
        snap = snapshot(cl, force=args.full, on_reconnect=_reconnect)
        print("集结时长档位:", json.dumps(snap["slots"], ensure_ascii=False))
        print("扫描网格 %d 格, 本次扫 %d 格, 已知巨型狮鹫 %d 只"
              % (snap["scan"]["grid"], snap["scan"]["scanned"],
                 snap["scan"]["known"]))
        print("地图上的巨型狮鹫 %d 只:" % len(snap["bosses"]))
        for b in snap["bosses"][:40]:
            print("  index=%-8s 等级=%-3s hp=%s/%s%s"
                  % (b["index"], b["level"], b["hp"], b["maxHp"],
                     "  [已有集结]" if b.get("busy") else ""))
        print("联盟现有集结 %d 支, 我的 %d 支"
              % (snap["rally_count"], len(snap["my_rallies"])))
        for m in snap["my_rallies"]:
            print("  我的集结 target=%s monster=%s 时长=%s分钟"
                  % (m.get("targetId"), m.get("monsterId"), m.get("wait_minutes")))
        if args.start:
            from cok_hunt import list_army, standard_army
            tile = pick_boss_tile(cl, level=args.start)
            if not tile:
                print("[!] 没找到 %d 级巨型狮鹫" % args.start)
                return 1
            army = standard_army(list_army(cl))
            a = army[0]
            num = min(args.num, a["free"])
            r = rally_march(cl, tile["index"], a["id"], a.get("speed"),
                            a.get("load"), num, slot=args.slot,
                            monster_id=tile.get("monsterId") or "")
            print(json.dumps({k: v for k, v in r.items() if k != "result"},
                             ensure_ascii=False, default=str, indent=1))
    finally:
        cl.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
