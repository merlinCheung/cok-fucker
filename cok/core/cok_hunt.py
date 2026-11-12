#!/usr/bin/env python3
"""COK 打野怪(体力 / 野怪等级 / 自动打怪队列)直连封装。

已实测的命令族(全部实测, 见 README/报告):

  autoQueue.data            无参            -> 自动打怪设置(lv/format/autoCount/force/status)
  autoQueue.levelMaxMonster 无参            -> 玩家当前可打的最高怪等级(maxLevel)
  autoQueue.status {status} status=INT      -> 开关(0关/1开); **响应里带 stamina/lastStaminaTime**
  autoQueue.save {lv|format|saveItems|autoCount|force}
  autoQueue.search {autoQueue}             -> 搜索目标(需先开启; 未开启返回 E000004)
  world.user.march          无参            -> 部队清单(army: id/free/march/speed/load/...)
  res.tile.find {type,level,NoRecord}      -> 搜索野怪坐标(x/y)

⚠️ 重要约束(实测):
  * `autoQueue.status {status:1}`(开启自动打怪)需要**自动打怪周卡**
    (道具 771836, 状态 id 22604360)。没有周卡时服务端返回 E000000。
  * `autoQueue.status {status:0}`(关闭)总是成功, 且响应里带当前体力,
    所以**读体力用 status:0 是零副作用的**(不改变状态)。
  * `lv` 是**范围** "下限;上限"(客户端 AutoQueueMainView:saveData("lv"))。
  * `format` 是**部队编成**, 但**游戏客户端存的是编队槽位索引**("1" / "1;2;3"),
    服务端原样存储(实测: 写 "1" 读回来还是 "1")。详见 read_autoqueue。
  * 体力上限**服务端不下发**, 来自客户端配置表
    `ItemSpec id=auto_kill_monster` 的 `k4` = **1000**
    (客户端 `AutoQueueController:getStaminaLimit()` ->
    `getPropByIdGroup('data_config','auto_kill_monster','k4')`)。
    实测服务端 stamina 能到 990(国服号), 所以之前写死的 100 是错的。
    见 game-config.json; 可用环境变量 COK_STAMINA_MAX 覆盖。
"""
# --- 包自举: 直接 `python3 cok/core/xxx.py` 时把 cok/ 加进 sys.path ---
import os as _os
import sys as _sys

_PKG_ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
if _os.path.isdir(_PKG_ROOT) and _PKG_ROOT not in _sys.path:
    _sys.path.insert(0, _PKG_ROOT)
_CORE = _os.path.join(_PKG_ROOT, "core")
if _os.path.isdir(_CORE) and _CORE not in _sys.path:
    _sys.path.insert(0, _CORE)
import cok_paths  # noqa: E402
from cok_paths import resource as _res  # noqa: E402

import hashlib
import json
import os
import time
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))

#: 世界 x 方向格数(客户端 WorldController::getIndexByPoint 的 w1; 服务端
#: `login.dataconfig` 的 worldmap_map.k1 = 1201)。
WORLD_W = 1201

#: 打野怪行军类型(客户端 gameConst.lua: MarchMethodType.MethodFieldMonster = 6)
MARCH_TYPE_FIELDMONSTER = 6

#: marchKey 固定盐(客户端 AutoQueueInfo:autoMarch / OpenGranaryMarchCommand)
MARCH_KEY_SALT = "wNSc5Mm8YwiOhAab"

def _stamina_max():
    """体力上限。

    服务端**不下发**这个字段, 来自客户端配置表
    `ItemSpec id=auto_kill_monster` 的 `k4`(客户端
    `AutoQueueController:getStaminaLimit()`)。实测 = 1000。
    之前这里写死 100, 于是页面显示成 "154/100" / "990/100"。
    """
    env = os.environ.get("COK_STAMINA_MAX")
    if env:
        try:
            return int(env)
        except ValueError:
            pass
    try:
        with open(_res("game-config.json"), encoding="utf-8") as fh:
            cfg = json.load(fh)
        v = cfg.get("stamina_max")
        if v:
            return int(v)
    except Exception:  # noqa: BLE001
        pass
    return 1000


#: 体力上限(客户端配置表 auto_kill_monster.k4 = 1000)
STAMINA_MAX = _stamina_max()

#: 同一支队伍两次派出之间的**最小间隔**(秒)。
#: 刚派出时服务端的行军统计还没更新, 早判"已回来"会疯狂重复派出
#: (实测一次烧掉 574 体力 = 57 只怪, 而 kills 计数还是 0)。
#: 30 秒足够覆盖"统计刷新 + 低等级怪秒回"这两种情况。
MIN_LAUNCH_GAP = 30.0

#: 用**行军 uuid** 判定"部队回来了"时的最小观察时间(秒)。
#: uuid 判定是精确的(部队回家了 uuid 就从服务端列表里消失),
#: 但刚派出的一瞬间服务端可能还没把这次行军登记进列表 —— 所以留 8 秒保险,
#: 免得"刚派出就查不到 -> 以为没派出去 -> 又派一次"重复烧体力。
UUID_RETURN_GAP = 8.0

#: 体力消耗速率熔断: 60 秒内体力掉超过这个数就自动停(正常打怪远达不到)。
#: 4 队并行时正常大约 20~40 点/分钟, 200 是很宽松的阈值。
STAMINA_BURST_LIMIT = 200
STAMINA_BURST_WINDOW = 60.0

#: 一轮(轮询周期)里最多派几支队伍。
#: 每派一队都要一次 `res.tile.find`(找怪), 连续太多次会被服务端节流,
#: 所以一轮内不宜连派太多 —— 但也不能只派一队, 否则"设 8 队"要等 8 个
#: 轮询周期才开满, 同兵种拆出的多队会被拖成串行。
#: 实测每队行军+战斗+返程约 60 秒, 轮询 2 秒 —— 一轮派 4 队足够开满 8 队
#: (两轮之内), 又不会把 find 打爆。
MAX_LAUNCH_PER_ROUND = 4

#: 非 VIP 账号的**每日找怪次数**(服务端 `world.maxSearchCount` 也是这个值)。
#:
#: ⚠️⚠️ **不要拿它当拦截阈值**(2026-11-12 修):
#: 服务端对 **SVIP 账号不限次数**(客户端提示 113230「激活VIP可以无限制」),
#: 但下发的 `world.maxSearchCount` **照样是 6** —— 用它硬拦会把 SVIP 号卡死。
#: 之前就因为这个把 SVIP 号打几轮就卡成「今日找怪次数已用完」。
#:
#: ⇒ **服务端才是唯一权威**: 只有服务端真的返回空坐标(次数用完)才算数,
#: 本地计数只用来**显示**「今日已用 N 次」, 绝不用来拦。
FIND_LIMIT_DAILY = 6

#: 每打一只野怪消耗的体力(实测 9: 113->104, 108->99)
STAMINA_COST = 9


def _is_fatal_conn_error(msg):
    """这个异常是不是"连接已经死了, 重试也没用"。

    致命错误的特征: 管道断了 / 服务端关了连接 / 连接被重置。
    遇到这种必须**立刻停止**并把账号还回去 —— 否则循环会一直重试,
    一直占着连接, 整个控制台的轮询都被跳过。

    ⚠ 但"连接被踢掉"这类错误**可以救**: 同账号双连接时服务端会踢掉
    其中一条, 重建连接通常就能抢回账号(2026-11-01 安卓端实测:
    hunt_error -> hunt_reconnect -> hunt_reconnected -> 继续打怪)。
    所以这里只负责"识别", 真正的重连由 AutoHunter._try_reconnect 决定。
    """
    m = str(msg)
    return ("Broken pipe" in m or "连接被服务端关闭" in m
            or "ConnectionReset" in m or "Connection refused" in m
            or "BrokenPipeError" in m
            # 被服务端踢掉时的另一种表现(安卓端 2026-11-01 实测)
            or "Software caused connection abort" in m
            or "Connection aborted" in m)


def _is_stamina_error(code):
    """服务端错误码是不是"体力不足"。

    E100047 = "体力不足, 不能发起攻击"(设备 text_zh_CN.ini 实测)。
    这**不是失败**, 是正常等待体力恢复 —— 不该计入 fails。
    """
    if code is None:
        return False
    c = str(code).strip().upper()
    if c.startswith("E"):
        c = c[1:]
    return c == "100047"

#: 自动打怪周卡道具 id(客户端 data_config.auto_kill_monster.k2)
WEEK_CARD_ITEM = 771836
#: 自动打怪周卡状态 id(客户端 data_config.auto_kill_monster.k3)
WEEK_CARD_STATUS = 22604360
#: 体力道具 id(客户端 data_config.auto_kill_monster.k1 = "200380;200381")
#: 统一表在 cok_stamina.STAMINA_ITEMS(200380=10 / 200381=50 / 200382=100 体力)
STAMINA_ITEMS = ["200380", "200381", "200382"]


def load_levels(path=None):
    """本地野怪等级表(客户端配置 field_monster 组里 usePower=10 且 type=0 的世界野怪)。"""
    path = path or _res("monster-levels.json")
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f).get("levels") or []
    except (OSError, ValueError):
        return []


def level_name(levels, lv):
    for x in levels:
        if x.get("level") == int(lv):
            return x.get("name")
    return None


def _write(client, cmd, params, tries=3):
    """写操作专用: 服务端会丢弃新连接的首条业务请求, 且偶发回 E000000。

    这里独立重试(每次换一次参数顺序无意义, 只是等服务端状态回落),
    返回最后一次的 params 明文。
    """
    last = {}
    for i in range(tries):
        try:
            r = client.call(cmd, params)
            p = r.get("__params__") or {}
            if not p.get("errorCode"):
                return p
            last = p
        except Exception as e:  # noqa: BLE001
            last = {"error": str(e)[:160]}
        if i < tries - 1:
            time.sleep(1.5)
    return last


def read_data(client):
    """自动打怪设置快照。"""
    r = client.call("autoQueue.data")
    return r.get("__params__") or {}


def read_autoqueue(client):
    """读游戏里「自动打怪」面板的当前设置(autoQueue.data)。

    ⚠️ `format` 字段有**三种形态**(2026-10-27 实测):
      1. `""`            —— 没设过
      2. `"1"` / `"1;2;3"` —— **编队槽位索引**(游戏客户端正常存的形式;
         客户端 `AutoQueueController:updateFormat()` ->
         `autoQueueInfo.format = atoi(formats[index])`, 服务端**原样存储**)
      3. `"107110,50|107012,50|…"` —— **编成串**。这是本工具早期用
         `autoQueue.save` 写进去的, 游戏客户端读回后 `atoi()` 得到 107110,
         超过编队数(11)会被**直接丢弃** -> 游戏面板的编队显示成空。
         所以看到这种形态就说明**游戏里的设置被写坏了**。

    返回:
      format    原始 format 串
      kind      "empty" / "index" / "army"
      indices   槽位索引列表(仅 kind=="index")
      squads    [{army_id, num}]   (仅 kind=="army" 时解得出)
      lv        "下限;上限" 野怪等级范围
      autoCount 游戏里设的并行队数
      force     严格模式
      status    自动打怪开关状态
      indexed   True = format 是槽位索引(解不出编成)
    """
    p = read_data(client) or {}
    if p.get("errorCode"):
        return {"ok": False, "errorCode": p.get("errorCode")}
    fmt = str(p.get("format") or "")
    # 槽位索引: 纯数字, 或用 ";" 分隔的一串数字("1;2;3")
    indices = []
    if fmt:
        parts = [x.strip() for x in fmt.split(";")]
        if all(x.isdigit() for x in parts):
            indices = [int(x) for x in parts]
    kind = "empty" if not fmt else ("index" if indices else "army")
    # parse_format 返回 {"id":..}, 这里换成打怪用的 {"army_id":..}
    squads = [{"army_id": s.get("id"), "num": s.get("num")}
              for s in parse_format(fmt)]
    lv = str(p.get("lv") or "")
    return {
        "ok": True,
        "format": fmt,
        "kind": kind,
        "indices": indices,
        "squads": squads,
        "indexed": kind == "index",
        "lv": lv,
        "lvLow": _as_int(lv.split(";")[0]) if lv else 0,
        "lvHigh": _as_int(lv.split(";")[1]) if ";" in lv else _as_int(lv),
        "autoCount": _as_int(p.get("autoCount")),
        "force": _as_int(p.get("force")),
        "status": _as_int(p.get("status")),
    }


def _as_int(v, default=0):
    try:
        return int(v)
    except (TypeError, ValueError):
        return default


def read_max_level(client):
    """玩家当前可打的最高怪等级(实测 30)。"""
    r = client.call("autoQueue.levelMaxMonster")
    p = r.get("__params__") or {}
    return int(p.get("maxLevel") or 0)


def read_stamina(client):
    """当前体力。

    用 `autoQueue.status {status: <当前状态>}` 读: 传当前值不改变状态,
    服务端仍会回 stamina/lastStaminaTime。status=0 最安全(关闭态)。
    """
    cur = int((read_data(client) or {}).get("status") or 0)
    r = client.call("autoQueue.status", {"status": cur})
    p = r.get("__params__") or {}
    return {
        "stamina": int(p.get("stamina") or 0),
        "lastStaminaTime": int(p.get("lastStaminaTime") or 0),
        "max": STAMINA_MAX,
        "status": int(p.get("status") or cur),
    }


def save_level(client, lo, hi=None):
    """设置野怪等级范围("下限;上限")。实测: `autoQueue.save {lv:"1;3"}` 成功。"""
    hi = lo if hi is None else hi
    return _write(client, "autoQueue.save", {"lv": "%s;%s" % (int(lo), int(hi))})


def save_format(client, fmt):
    """设置部队编成 "兵种id,数量|兵种id,数量"。"""
    return _write(client, "autoQueue.save", {"format": str(fmt)})


def set_status(client, on):
    """开关自动打怪。开启需要自动打怪周卡, 否则服务端返回 E000000。"""
    p = _write(client, "autoQueue.status", {"status": 1 if on else 0})
    if p.get("errorCode"):
        return {"ok": False, "errorCode": p.get("errorCode"),
                "note": "开启自动打怪需要「自动打怪周卡」(道具 %d)" % WEEK_CARD_ITEM}
    return {"ok": True, "stamina": p.get("stamina"),
            "lastStaminaTime": p.get("lastStaminaTime"), "status": p.get("status")}


def read_march(client):
    """一次读到 **部队清单 + 每支在外部队的明细**。

    返回 {"army": [...], "all": [...], "marches": {uuid: 明细}}

    `world.user.march` 的响应里有两个东西:
      * `army` —— 每个**兵种**一行(id/free/march/speed/load/...)
        `march` 是该兵种**在外总数量**(同兵种可以有多支部队在外面),
        单看它**分不清是哪一支**回来了。
      * `m` —— **每一支在外部队**一行(uuid/st/et/army[].total/army[].dead)
        这才是"哪支部队回来了"的精确依据。

    ⚠️ `army` 只列了 free>0 的兵种, 而**部队全派出去时 free=0**,
      那个兵种就会从 `army` 里消失 -> 查不到它的外勤总量。
      所以额外返回 `all`(**全部**兵种, 不过滤), 算外勤量要用它。

    ⚠️ 实测(2026-11-09, 66手游号 1 级怪 50 人):
        派出后 0.5 秒 m 里就有这一支;
        行军 14 秒 -> 到达 -> 战斗 -> 返程(**uuid 不变, st/et 刷成返程段**);
        部队到家后这一条才从 m 里消失, 同时 army[].march 归零、free 还原。
      ⇒ **uuid 不在 m 里 = 这支部队已经回家了**(不是"到达"就消失)。
    """
    r = client.call("world.user.march")
    p = r.get("__params__") or {}
    all_rows = []
    for a in (p.get("army") or []):
        all_rows.append({
            "id": str(a.get("id")),
            "free": int(a.get("free") or 0),
            "march": int(a.get("march") or 0),
            "speed": a.get("speed"),
            "load": a.get("load"),
            "power": a.get("power"),
            "attack": a.get("attack"),
            "defen": a.get("defen"),
            "health": a.get("health"),
            "level": a.get("level"),
        })
    all_rows.sort(key=lambda x: float(x.get("power") or 0), reverse=True)
    army = [a for a in all_rows if a["free"] > 0]
    marches = {}
    for e in (p.get("m") or []):
        u = str(e.get("uuid") or "")
        if u:
            marches[u] = e
    return {"army": army, "all": all_rows, "marches": marches}


def _march_troops(entry):
    """从**行军明细**里取出 (在外总数, 阵亡数)。

    服务端的 `army` 字段有三种形态(实测 2026-11-09):
      * 标准兵种单兵种: `[{"total": 50, "dead": 0, "knight_dead": 0, ...}]`
      * 标准兵种**混编**: `[{"total": 50, ..., "armId": 0},
                            {"total": 50, ..., "armId": 1}, {"is1518": true}]`
        —— 混编时每个兵种一项, `armId` 是兵种序号。
      * 活动限定兵种(575xxx): `[{"57580718": {"total": 20000, "dead": 0,
                                             "15_18_id": "57580718"}, "is1518": true}]`
        —— 兵力数字**按兵种 id 再嵌一层**; 混编时一个 dict 里嵌多个兵种 id。
    三种都要认, 否则"在外人数"会算成 0(混编队伍尤其容易踩)。
    """
    total = 0
    dead = 0
    raw = (entry or {}).get("army")
    if isinstance(raw, dict):
        # 活动兵种混编: {兵种id: {total, dead}, ..., "is1518": true}
        raw = [raw]
    for a in (raw or []):
        if not isinstance(a, dict):
            continue
        if "total" in a or "dead" in a:
            total += int(a.get("total") or 0)
            dead += int(a.get("dead") or 0)
            continue
        for _k, v in a.items():
            if isinstance(v, dict) and ("total" in v or "dead" in v):
                total += int(v.get("total") or 0)
                dead += int(v.get("dead") or 0)
    return total, dead


def _march_troops_by_army(entry):
    """从行军明细里取出 {兵种id: (在外数, 阵亡数)}。

    ⚠️ 标准兵种混编时明细给的是 `armId` **序号**而不是兵种 id,
    要对上号得知道这一队出征时的兵种顺序 —— 所以调用方要传 `order`。
    """
    out = {}
    raw = (entry or {}).get("army")
    if isinstance(raw, dict):
        raw = [raw]
    items = [a for a in (raw or []) if isinstance(a, dict)]
    for a in items:
        if "total" in a or "dead" in a:
            aid = a.get("armId")
            if aid is None:
                continue
            out[int(aid)] = (int(a.get("total") or 0), int(a.get("dead") or 0))
            continue
        for k, v in a.items():
            if isinstance(v, dict) and ("total" in v or "dead" in v):
                out[str(k)] = (int(v.get("total") or 0), int(v.get("dead") or 0))
    return out


def list_army(client):
    """部队清单: 只返回有空闲兵(free>0)的兵种, 按战力从高到低。

    带 `march` 字段(该兵种当前在外勤的总数量)。
    """
    return read_march(client)["army"]


def standard_army(army):
    """只取**标准兵种**(6 位 107xxx 系列)。

    ⚠️ 实测: 编成里混入活动限定兵种(575xxxxx / 40400xxx 这类 8 位 id)时,
    服务端会回 E000000 —— 单独一个 575 兵种可以, 但和普通兵种混编不行。

    ⇒ **混编**的场合(集结派兵 / 手动编成)必须用它过滤;
      **单兵种**的场合(打怪, 每队只有一种兵)可以用全部兵种, 见 `usable_army`。
    """
    std = [a for a in army if len(a["id"]) == 6 and a["id"].startswith("10")]
    return std


def usable_army(army):
    """所有**有空闲兵**的兵种(含活动限定兵种), 按战力从高到低。

    ⚠️ 为什么打怪可以用活动兵种(2026-11-09 实测):
      * 服务端拒绝的是「活动兵种 + 普通兵种**混编**」(E000000),
        **单兵种**出征完全没问题;
      * 实测 57580718(遗迹天使巨像) x20000 出征野怪成功(dp 481657 / sp 526109);
      * 活动兵种**战力更高、库存大得多**:
        66手游号实测 标准兵种 18000/种, 活动兵种 7 万~115 万/种。
      * 标准兵种库存天花板就在 1.8~2 万 —— 这就是「每队最多 2w」的真正原因,
        不是我们的上限, 是标准兵种自己就那么多。

    ⇒ 打怪可以用全部兵种(每队只有一种兵); 队伍数由**库存总量**决定,
      同一种兵可以拆成多队(见 `plan_squads`), 号上只有 2 种兵也能开满 5~8 队。
    """
    return sorted(army, key=lambda a: -float(a.get("power") or 0))


def _army_class(aid):
    """兵种类别: "std" 普通兵种 / "act" 活动限定兵种。

    ⚠️ 服务端**拒绝**跨类混编(实测 2026-11-09: 活动兵 57580718 + 普通兵
    107012 -> E000000), 但**同类之间可以混编**(标准+标准 ✅ / 活动+活动 ✅)。
    ⇒ 混编只能在同一类里做。
    """
    aid = str(aid)
    return "std" if (len(aid) == 6 and aid.startswith("10")) else "act"


def plan_squads(army, num, squads, mix=1):
    """按**当前库存**把兵种编成若干支队伍(每支队伍 = 一个"编成")。

    返回 {"slots": [...], "num": 每队目标人数, "squads": 实际队数,
           "total": 动用兵力, "short": 是否被库存摊薄, "note": 说明}

    每个 slot = {"troops": [{army_id, num, speed, load, name}, ...],
                 "army_id": 主力兵种 id, "num": 该队总人数, "name": 兵种名,
                 "types": 该队用了几个兵种}

    规则(2026-11-09 真服实测):
      * **一次出征可以带多个兵种**(混编): 服务端接受**同类**多兵种
        (标准+标准 ✅ / 活动+活动 ✅), 跨类混编会被拒(E000000);
      * **同一种兵可以连续/并行开多队**: 同兵种多支部队可以同时在外,
        判回按**行军 uuid** 精确区分(见 `_check_returned`);
      * 每队人数 = `num`; 库存不够"想要 N 队 × 每队 M 人"时**按库存摊薄**,
        让"设 5 队"真的能开 5 队;
      * `mix` = 每队最多用几种兵(1 = 每队一种兵; 2+ = 混编, 同类兵种平分人数);
      * 队与队之间**可以复用同一兵种**(库存够就继续开队)。
    """
    per = max(1, int(num or 1))
    want = max(1, int(squads or 1))
    mix = max(1, int(mix or 1))
    pool = usable_army(army)
    if not pool:
        return {"slots": [], "num": per, "squads": 0, "total": 0,
                "short": True, "note": "没有有空闲兵的兵种"}
    mix = min(mix, per)          # 每队人数比兵种数还少时没法混编
    total = sum(int(a.get("free") or 0) for a in pool)
    short = False
    if total < per * want:
        # 库存不够摊满 -> 按库存摊薄每队人数, 保证能开满 want 队
        per = max(1, total // want)
        short = True
    remain = {}
    for a in pool:
        remain[a["id"]] = int(a.get("free") or 0)

    def _make_slot(main):
        """用 `main` 当主力兵种造一支队伍(可再补同类兵种 = 混编)。"""
        combo = [main]
        if mix > 1:
            cands = [a for a in pool
                     if a["id"] != main["id"]
                     and _army_class(a["id"]) == _army_class(main["id"])
                     and remain.get(a["id"], 0) > 0]
            # 补位优先用**剩余库存最多**的, 免得库存浪费在快用完的兵种上
            cands.sort(key=lambda a: (-remain[a["id"]], -float(a.get("power") or 0)))
            combo += cands[:mix - 1]
        share = per // len(combo)
        extra = per - share * len(combo)
        troops = []
        for i, a in enumerate(combo):
            n = share + (1 if i < extra else 0)
            n = min(n, remain.get(a["id"], 0))
            if n <= 0:
                continue
            remain[a["id"]] -= n
            troops.append({"army_id": a["id"], "num": n,
                           "speed": a.get("speed"), "load": a.get("load"),
                           "name": army_name(a["id"]) or ("兵种 " + a["id"])})
        if not troops:
            return None
        return {"troops": troops,
                "army_id": troops[0]["army_id"],
                "num": sum(int(t["num"]) for t in troops),
                "name": " + ".join(t["name"] for t in troops),
                "types": len(troops)}

    out = []
    first_pass = list(pool)      # 第一轮: 每个兵种先来 1 队
    while len(out) < want:
        if first_pass:
            main = first_pass.pop(0)
        else:
            # 第二轮: 剩下的队数继续用**剩余库存最多**的兵种开
            # (同一种兵可以并行开多队, 也能一支队回来后连续出征)
            cand = [a for a in pool if remain.get(a["id"], 0) > 0]
            if not cand:
                break
            cand.sort(key=lambda a: (-remain[a["id"]], -float(a.get("power") or 0)))
            main = cand[0]
        s = _make_slot(main)
        if s is None:
            continue
        out.append(s)
    if len(out) < want:
        short = True
    return {"slots": out, "num": per, "squads": len(out),
            "total": sum(int(s["num"]) for s in out),
            "short": short,
            "note": ("库存只够开 %d 队(每队最多 %d 人)" % (len(out), per)) if short else ""}


def split_squads(army, num, squads, mix=1):
    """按库存切队(只返回队伍列表, 详见 `plan_squads`)。"""
    return plan_squads(army, num, squads, mix)["slots"]


def parse_format(fmt):
    """把编成串 "id,num|id,num" 解析成 [{id, num}]。"""
    out = []
    for part in str(fmt or "").split("|"):
        part = part.strip()
        if not part:
            continue
        if "," not in part:
            continue
        a, _, b = part.partition(",")
        a = a.strip()
        if not a.isdigit():
            continue
        try:
            n = int(b.strip())
        except ValueError:
            continue
        out.append({"id": a, "num": n})
    return out


def build_format(army, per_type=50, max_types=4):
    """用有兵的最高战力**标准兵种**拼一个编成串 "id,num|id,num"。

    ⚠️ 实测: 编成里混入活动限定兵种(575xxxxx / 40400xxx 这类 8 位 id)时,
    服务端会回 E000000 —— 单独一个 575 兵种可以, 但和普通兵种混编不行。
    所以这里只取 6 位 id(107xxx 系列)的标准兵种。
    """
    std = [a for a in army if len(a["id"]) == 6 and a["id"].startswith("10")]
    if not std:
        std = list(army)
    return "|".join("%s,%d" % (a["id"], min(per_type, a["free"]))
                    for a in std[:max_types])


def find_monster(client, level):
    """搜索一只指定等级的野怪, 返回坐标(x/y)。搜索次数有限(实测 maxSearchCount=6)。

    ⚠️ **"没找到" 有两种完全不同的形态**(客户端 Lua
    `game/command/IFFindResTileCmd.lua:handleReceive` 明确区分):

    | 服务端返回 | 含义 | 客户端提示 |
    |---|---|---|
    | **x / y 字段缺失(None)** | **今日找怪次数用完了** | 113228「今日剩余使用次数不足, 激活VIP可以无限制」 |
    | **x == -1 或 y == -1** | 世界上确实没有这个等级的怪 | 113229「现在世界上没有您想寻找的资源点或者怪物」 |

    ⚠️⚠️ **这两种都不能当成功**(2026-11-11 修):
    之前一律返回 `ok=True, x=None, y=None`, 后面 `point_index(None, None)`
    直接 `int(None)` 抛
    `TypeError: int() argument must be a string, a bytes-like object or a real number, not 'NoneType'`
    → 自动打怪每轮都崩 → 连续 5 次异常 → **自动停止**(用户实测遇到)。
    """
    r = client.call("res.tile.find", {"type": 6, "level": int(level), "NoRecord": 1})
    p = r.get("__params__") or {}
    if p.get("errorCode"):
        return {"ok": False, "errorCode": p.get("errorCode")}
    x, y = p.get("x"), p.get("y")
    if x is None or y is None:
        return {"ok": False, "errorCode": "SEARCH_LIMIT",
                "note": "今日找怪次数已用完(非 VIP 每天 %d 次, 每日重置; SVIP 无限)"
                        % FIND_LIMIT_DAILY}
    try:
        ix, iy = int(x), int(y)
    except (TypeError, ValueError):
        return {"ok": False, "errorCode": "BAD_COORD",
                "note": "坐标格式异常: %r/%r" % (x, y)}
    if ix <= 0 or iy <= 0:
        # x == -1 / y == -1 = 确实没有这种怪(其它非正数一律当坐标非法)
        if ix == -1 or iy == -1:
            return {"ok": False, "errorCode": "NO_TARGET",
                    "note": "世界上没有 %s 级的野怪" % level}
        return {"ok": False, "errorCode": "BAD_COORD",
                "note": "坐标非法: %d/%d" % (ix, iy)}
    return {"ok": True, "x": ix, "y": iy, "level": p.get("level")}


def point_index(x, y, w=WORLD_W):
    """世界坐标 -> 点位 index。

    来自 libgame.so 里 `WorldController::getIndexByPoint`(device 版 0xecb8d8)反汇编:
        s1 = point.x (float)      s2 = point.y (float)
        if (s1 > w1-1) return 0
        w0 = (uint)point.x + 1
        w2 = (uint)((float)w1 * point.y)
        return w0 + w2
    即 **index = x + 1 + (int)(w1 * y)**, w1 = 世界 x 方向格数(1201)。
    越界(坐标 <=0 或 > 尺寸)返回 0。

    ⚠️ **x/y 为 None 时必须返回 0 而不是抛异常**(2026-11-11 修):
    `int(None)` 会抛 TypeError, 一次就能把整个自动打怪循环带崩。
    """
    try:
        x = int(x)
        y = int(y)
    except (TypeError, ValueError):
        return 0
    if x <= 0 or y <= 0:
        return 0
    return x + 1 + int(w * y)


def march_key(index, army, march_type=MARCH_TYPE_FIELDMONSTER):
    """算 marchKey。

    客户端算法(AutoQueueInfo:autoMarch):
        md5( index + "1021" + (marchType+1)*1000 + [armyId, speed, load, num]* + 盐 )

    ⚠️ **多兵种的拼接顺序 = 兵种 id 的字典序升序**(2026-11-09 真服实测):
        客户端用 `ipairs4ScatteredT` 遍历散列表, 顺序看着随机, 但服务端
        **只认 key 升序**这一种:
          * 66手游号: 标准兵 107012 + 107111, 按 id 升序拼 -> 成功;
            按 id 倒序拼 -> **E000000**;
          * OPPO 号: 活动兵 57580218 + 57580618, 按 id 升序拼 -> 成功;
            按服务端返回的原始顺序(57580618 在前)拼 -> **E000000**。
        ⇒ 服务端是**自己按 key 升序遍历** soldiers 来校验 marchKey 的,
          所以我们只要按 id 升序拼就行, 不必还原客户端的散列表顺序。
    """
    parts = [str(int(index)), "1021", str((int(march_type) + 1) * 1000)]
    # key 升序(多兵种时唯一的正确顺序)
    for aid in sorted(army.keys(), key=lambda x: str(x)):
        speed, load, num = army[aid]
        parts += [str(int(aid)), str(speed), str(load), str(int(num))]
    parts.append(MARCH_KEY_SALT)
    return hashlib.md5("".join(parts).encode()).hexdigest()


def march_monsters(client, index, troops, march_type=MARCH_TYPE_FIELDMONSTER,
                   general_id="", pet_dragon_uid="", aormation_id=""):
    """派兵出征打野怪, **一次可以带多个兵种**(混编)。

    `troops` = [{"army_id","speed","load","num"}, ...](同一队的兵种)。

    ⚠️ 服务端限制(2026-11-09 真服实测):
      * **标准兵种之间混编 -> OK**(实测 2 种、3 种都行, 返回正常 uuid);
      * **活动限定兵种之间混编 -> OK**(8 位 id, 单独一个也行);
      * **活动限定兵种 + 普通兵种混编 -> E000000**(拒绝)。
        ⇒ 混编只在"同一类"里做, 见 `plan_squads`。

    ⚠️ `soldiers` 的数量必须编码成 SFS **INT**(客户端 CCDictionary 里是
    CCInteger); 而 encode_value 对普通 Python int 会压成最小宽度(BYTE),
    服务端会回 E000000。
    """
    from cok_sfs import TypedInt, SFS_INT
    # **按 id 升序**: 服务端就是按 key 升序遍历 soldiers 校验 marchKey 的
    items = sorted(troops, key=lambda t: str(t["army_id"]))
    army = {}
    soldiers = {}
    for t in items:
        aid = str(int(t["army_id"]))
        n = int(t["num"])
        army[aid] = (t.get("speed"), t.get("load"), n)
        soldiers[aid] = TypedInt(n, SFS_INT)
    if not army:
        return {"ok": False, "errorCode": "E_NO_TROOPS"}
    key = march_key(index, army, march_type)
    params = {
        "point": int(index),
        "type": int(march_type),
        "soldiers": soldiers,
        "generalId": general_id or "",
        "petDragonUid": pet_dragon_uid or "",
        "aormationId": aormation_id or "",
        "autoQueue": 0,
        "marchKey": key,
    }
    r = client.call("world.march", params)
    p = r.get("__params__") or {}
    if p.get("errorCode"):
        return {"ok": False, "errorCode": p.get("errorCode"), "marchKey": key,
                "point": int(index)}
    # 服务端把这次行军的明细放在 `$_monitor_log_$` 里, 里面有 **uuid** ——
    # 有了它才能精确知道"这一支部队回来了没有"(见 read_march 的说明)。
    log = p.get("$_monitor_log_$") or {}
    return {"ok": True, "result": p, "marchKey": key, "point": int(index),
            "uuid": str(log.get("uuid") or ""), "march": log,
            "troops": [{"army_id": t["army_id"], "num": int(t["num"])}
                       for t in items]}


def march_monster(client, index, army_id, speed, load, num,
                  march_type=MARCH_TYPE_FIELDMONSTER, general_id="",
                  pet_dragon_uid="", aormation_id=""):
    """派兵出征打野怪(单兵种)。会真实消耗士兵与体力。

    多兵种(混编)用 `march_monsters`。
    """
    return march_monsters(client, index,
                          [{"army_id": army_id, "speed": speed,
                            "load": load, "num": num}],
                          march_type=march_type, general_id=general_id,
                          pet_dragon_uid=pet_dragon_uid,
                          aormation_id=aormation_id)


# --------------------------------------------------------------------------
# 兵种中文名
# --------------------------------------------------------------------------
_NAMES_CACHE = {}


def _load_item_names():
    """id -> 中文名(id-names.json 的 item_names)。"""
    if _NAMES_CACHE:
        return _NAMES_CACHE
    try:
        with open(_res("id-names.json"), encoding="utf-8") as f:
            d = json.load(f)
        _NAMES_CACHE.update(d.get("item_names") or {})
    except Exception:
        pass
    return _NAMES_CACHE


def clean_name(raw):
    """把 id-names.json 里的复合名清洗成单个中文名。

    复合名形如 "{{蛮族督军|蛮族督军|蛮族督军|蛮族督军}}"(模板id|填充id...)，
    取第一段即可。普通名原样返回。
    """
    if not raw:
        return ""
    s = str(raw).strip()
    if s.startswith("{{") and s.endswith("}}"):
        s = s[2:-2]
    if "|" in s:
        s = s.split("|", 1)[0]
    s = s.strip()
    return s.replace("{", "").replace("}", "").strip()


def army_name(army_id):
    """兵种 id -> 中文名(取不到就返回空串)。"""
    raw = (_load_item_names() or {}).get(str(army_id))
    return clean_name(raw)


def army_choices(client, prefer_ids=None):
    """可选兵种列表(给页面下拉用): 带中文名/可用数/战力。

    只列**标准兵种**(6 位 107xxx 系列) —— 活动限定兵种(8 位 id)不能和普通
    兵种混编, 服务端会回 E000000, 所以不放进下拉。
    """
    army = list_army(client)
    std = standard_army(army)
    out = []
    for a in std:
        out.append({
            "id": a["id"],
            "name": army_name(a["id"]) or ("兵种 " + a["id"]),
            "free": a["free"],
            "power": a.get("power"),
            "speed": a.get("speed"),
            "load": a.get("load"),
            "attack": a.get("attack"),
            "defen": a.get("defen"),
        })
    if prefer_ids:
        want = [str(p) for p in prefer_ids]
        order = {v: i for i, v in enumerate(want)}
        out.sort(key=lambda x: (order.get(x["id"], 999), -float(x.get("power") or 0)))
    return out


def pick_troop(army, prefer=None):
    """从 army 清单里挑一个兵种: 优先指定 id, 否则取战力最高且有空闲兵的标准兵种。"""
    std = [a for a in army if len(a["id"]) == 6 and a["id"].startswith("10")]
    if prefer:
        for a in army:
            if a["id"] == str(prefer):
                return a
        return None
    if not std:
        return None
    return std[0]


class AutoHunter(object):
    """自动打怪循环: **多队并行** 找怪 -> 出征 -> 等部队回来 -> 下一只。

    * 走的是**手动出征**(`world.march` type=6), 所以**不需要「自动打怪周卡」**;
      体力照常消耗(服务端在出征时扣), 体力不足时停下来等恢复。
    * 每打一只都是真实消耗: 士兵 + 体力, 所以调用方必须显式开/关。

    **多队并行怎么保证判定准确**:
      每支队伍出发时记下这次行军的 **uuid**(服务端在 `world.march` 响应里
      给的), `world.user.march` 的 `m` 数组是"当前还在外面的每一支部队"——
      **uuid 不在里面 = 这支部队已经到家了**(实测: 行军/战斗/返程全程都在,
      到家才消失)。所以同一种兵拆成多队也能**一支一支精确**判回,
      不会认错人、不会重复派队白烧体力。

    实测数据(2026-10-24/25):
      * 体力消耗按怪等级: 1 级怪 9 点 / 15 级怪 10 点(客户端 usePower 表)
      * 体力**不靠战斗返还**, 只随时间恢复, 约 **1 点 / 130 秒**
      * 行军+战斗很快(几十秒), 部队回来后 `army[].march` 归零
    """

    def __init__(self, client, level=1, num=50, troop_id=None, max_kills=0,
                 on_event=None, poll=2.0, wait_stamina=60.0,
                 squads=4, squad_spec=None, on_tick=None, min_stamina=None,
                 on_reconnect=None, max_reconnects=2, mix=1,
                 auto_stamina=False, stamina_items=None, uid=None):
        self.client = client
        self.level = int(level)
        self.num = int(num)
        self.troop_id = troop_id
        self.max_kills = int(max_kills or 0)
        self.on_event = on_event
        self.poll = poll
        self.wait_stamina = wait_stamina
        # 连接被服务端踢掉时的补救: 由调用方重建连接(多半是同账号双连接,
        # 游戏 App 还在线)。on_reconnect(old_client) 返回新的 client,
        # 返回 None / 抛异常都按"救不回来"处理。
        self.on_reconnect = on_reconnect
        self.max_reconnects = max(0, int(max_reconnects or 0))
        self._reconnects = 0
        # The control plane may require a reserve above the protocol's hard
        # per-march cost. Never permit a configured threshold below that cost.
        self.min_stamina = max(STAMINA_COST, int(min_stamina or STAMINA_COST))
        self.squad_max = max(1, int(squads or 1))
        # 每队最多用几种兵(1 = 每队一种兵; 2+ = 混编, 同类兵种一起出征)
        self.mix = max(1, int(mix or 1))
        # 每圈的回调(在**本线程**里调用, 所以可以安全地用同一条连接发命令)
        # 用来搭顺风车做别的事, 比如港口定时检查 —— 不额外占号
        self.on_tick = on_tick
        self._last_tick = 0.0
        # 每队的兵种分配: [{army_id, num}]。None = 自动挑(按库存自动编排)
        self.squad_spec = squad_spec or None
        # 体力不足时自动喝背包里的体力药水(见 cok_stamina)
        self.auto_stamina = bool(auto_stamina)
        # {itemId: uuid} —— 道具实例 id(不是模板 id), 由调用方喂进来
        self.stamina_items = dict(stamina_items or {})
        # 账号 id(拉背包时用来落盘缓存); None = 不落盘
        self.uid = uid
        # 是否已经试过拉背包(拉一次要 40~50 秒, 别反复拉)
        self._stamina_bag_tried = False
        self.stop_flag = False
        self.state = {
            "running": False, "kills": 0, "fails": 0, "level": int(level),
            "num": int(num), "troop": troop_id, "max_kills": self.max_kills,
            "stamina": None, "stamina_max": STAMINA_MAX,
            "last": None, "note": "未开始", "recover_per_min": None,
            "troops_out": 0, "wait_for": "",
            "squad_max": self.squad_max, "squads": [],
            "killed_by_squad": 0, "mix": self.mix,
            "auto_stamina": self.auto_stamina, "stamina_potions": 0,
            "stamina_potion_item": "",
        }
        self._stamina_samples = []
        self._fatal_streak = 0
        self._squads = []          # 运行期的队伍对象
        self._last_find = 0.0      # 上次找怪的时间(找怪有服务端节流)
        #: **本进程内**已用的找怪次数 —— 只用来**显示**「今日已用 N 次」,
        #: **绝不用来拦截**(2026-11-12 改):
        #: 服务端对 SVIP 账号不限次数, 但 `world.maxSearchCount` 照样下发 6,
        #: 拿它当阈值会把 SVIP 号卡死。服务端返回空坐标才算数。
        self._find_used = 0
        #: 服务端下发的 `world.resSearchCount`(已用次数, 只作显示参考)。
        self._find_used_server = 0

    def _emit(self, kind, payload):
        if self.on_event:
            try:
                self.on_event(kind, payload)
            except Exception:
                pass

    def _try_reconnect(self):
        """连接被服务端关掉后重建连接。成功返回新的 client, 失败返回 None。"""
        if not self.on_reconnect or self._reconnects >= self.max_reconnects:
            return None
        self._reconnects += 1
        self.state["note"] = "连接被断开, 正在重连(第 %d 次)" % self._reconnects
        self._emit("reconnect", dict(self.state))
        try:
            new_client = self.on_reconnect(self.client)
        except Exception as e:  # noqa: BLE001
            self.state["note"] = "重连失败: %s" % str(e)[:100]
            return None
        if new_client is None:
            return None
        self.client = new_client
        self._fatal_streak = 0
        # 重连后队列状态还是有效的(服务端没变), 但"行军统计"可能已经过期,
        # 重新下一轮 army 再判断队伍是否回来。
        self.state["note"] = "已重连, 继续打怪"
        self._emit("reconnected", dict(self.state))
        return new_client

    def _read_stamina(self):
        st = read_stamina(self.client)
        self.state["stamina"] = st["stamina"]
        self.state["stamina_max"] = st["max"]
        now = int(time.time() * 1000)
        self._stamina_samples.append((st["stamina"], st["lastStaminaTime"], now))
        if len(self._stamina_samples) > 8:
            self._stamina_samples.pop(0)
        for i in range(len(self._stamina_samples) - 1):
            (s0, t0, w0), (s1, t1, w1) = self._stamina_samples[i], self._stamina_samples[i + 1]
            if w1 > w0 and s1 > s0:
                self.state["recover_per_min"] = round((s1 - s0) * 60000.0 / (w1 - w0), 2)
                break
        return st

    def _use_stamina_if_needed(self):
        """体力不够时自动喝背包里的体力药水。返回 True = 成功喝了一瓶。

        ⚠️ 只在 `auto_stamina` 打开时才会真的发请求。
        ⚠️ 失败**不算 fails**(不是打怪失败), 只是记在 note 里。
        ⚠️ 实例失效(E100166)时把缓存里的 uuid 丢掉, 下轮重新找。
        """
        if not self.auto_stamina:
            return False
        import cok_stamina
        iid, uuid = cok_stamina.pick_stamina(self.stamina_items)
        if not uuid:
            # 还没有药水的道具实例 uuid —— 去拉一次背包(`login.init`)。
            # ⚠️ 拉背包的响应有 95 万字节, 要 40~50 秒, 所以只拉一次:
            #    拉完还是没药水(背包里确实没有)就别再拉了。
            if self._stamina_bag_tried:
                self.state["note"] = ("体力不足, 但背包里没有体力药水"
                                      "(先在游戏里领/攒一瓶再开这个开关)")
                return False
            self._stamina_bag_tried = True
            self.state["note"] = "体力不足, 正在拉背包找体力药水…"
            self._emit("tick", dict(self.state))
            try:
                ok, info = cok_stamina.fetch_bag(self.client, self.uid)
            except Exception as e:  # noqa: BLE001
                ok, info = False, {"error": str(e)[:120]}
            if ok:
                for k, ent in (info.get("potions") or {}).items():
                    self.stamina_items[k] = dict(ent)
                # 顺带把服务端下发的「今日已用找怪次数」记下来(**只作显示**)。
                # ⚠️ **不用 `maxSearchCount` 做拦截**: SVIP 账号服务端不限次数,
                #    但那个字段照样下发 6(2026-11-12 实测)。
                srch = info.get("search") or {}
                if srch.get("used") is not None:
                    self._find_used_server = int(srch.get("used") or 0)
            iid, uuid = cok_stamina.pick_stamina(self.stamina_items)
        if not uuid:
            self.state["note"] = ("体力不足, 但背包里没有体力药水"
                                  "(先在游戏里领/攒一瓶再开这个开关)")
            return False
        ok, info = cok_stamina.use_stamina_item(self.client, uuid, 1)
        if not ok:
            code = info.get("errorCode")
            if code == "E100166":
                # 实例没了(药水用完/过期) —— 忘掉它, 让调用方重新学
                ent = self.stamina_items.get(iid)
                if isinstance(ent, dict):
                    ent.pop("uuid", None)
                else:
                    self.stamina_items.pop(iid, None)
            self.state["note"] = "喝体力药水失败: %s" % (
                info.get("error") or code or "未知错误")
            return False
        gain = int(cok_stamina.STAMINA_ITEMS.get(iid, 0))
        # 缓存里的数量减一; 减到 0 说明这一实例用完了, 丢掉 uuid
        ent = self.stamina_items.get(iid)
        if isinstance(ent, dict):
            if isinstance(ent.get("count"), int):
                ent["count"] = ent["count"] - 1
                if ent["count"] <= 0:
                    ent.pop("uuid", None)
        self.state["stamina_potions"] = int(self.state.get("stamina_potions") or 0) + 1
        self.state["stamina_potion_item"] = iid
        cur = self.state.get("stamina")
        if cur is not None:
            self.state["stamina"] = int(cur) + gain
        self.state["note"] = "体力不足, 已喝 1 瓶体力药水(+%d 体力)" % gain
        self._emit("stamina_used", dict(self.state))
        return True

    def _stamina_burst(self):
        """体力掉得太快吗? 返回掉点数(没超阈值就 0)。

        这是**保命阀**: 重复派队/异常结算会让体力在几分钟内掉几百点,
        那样等于白烧体力。正常打怪(4 队并行)大约 20~40 点/分钟。
        """
        sm = self._stamina_samples
        if len(sm) < 2:
            return 0
        # 找窗口内最早的样本。不能倒序后在第一个命中的 latest 样本上
        # 立刻 break，否则两者永远是同一条记录，熔断永远不会触发。
        latest = sm[-1]
        oldest = latest
        for sample in sm:
            if latest[2] - sample[2] <= STAMINA_BURST_WINDOW * 1000:
                oldest = sample
                break
        return max(0, int(oldest[0]) - int(latest[0]))

    def _march_map(self, army):
        """兵种 id -> 当前外勤数量。"""
        return {a["id"]: int(a.get("march") or 0) for a in army}

    def _assign(self, army):
        """给队伍槽位分配兵种和兵力。

        规则(2026-11-09 改):
          * 每支队伍 = 一个**编成**, 可以是**多个兵种**(混编) ——
            服务端接受**同类**混编(标准+标准 / 活动+活动), 跨类会被拒
            (E000000), 所以混编只在同类里做(见 `plan_squads`);
          * **同一种兵可以拆成多队**, 也能一支队回来后**连续出征** ——
            协议实测(2026-11-09): 同一个兵种连续出征 3 次都成功,
            `army[].march` 依次 30000/60000/90000, 说明 march 是
            **外勤总数量**而不是队伍数, 同兵种多支部队可以同时在外。
            判回按**行军 uuid** 精确判定(见 `_check_returned`)。
          * 优先满编(用户设的每队兵数是上限); 库存不够分满就**按库存摊薄**,
            保证"设 5 队"真能开 5 队。
          * 队数上限 = 用户设的并行队数。
        """
        by_id = {a["id"]: a for a in army}
        spec = self.squad_spec
        slots = []
        if spec:
            for s in spec[:self.squad_max]:
                aid = str(s.get("army_id") or s.get("id") or "")
                a = by_id.get(aid)
                if not a or a["free"] <= 0:
                    continue
                slots.append({"army_id": aid, "num": int(s.get("num") or self.num),
                              "speed": a.get("speed"), "load": a.get("load"),
                              "name": army_name(aid) or ("兵种 " + aid)})
        if not slots:
            slots = split_squads(army, self.num, self.squad_max, self.mix)
        for i, s in enumerate(slots):
            # 统一的队伍结构: `troops` 是这一队要带的兵种(可能多个 = 混编)
            troops = s.get("troops")
            if not troops:
                troops = [{"army_id": s["army_id"], "num": int(s.get("num") or 0),
                           "speed": s.get("speed"), "load": s.get("load"),
                           "name": s.get("name") or
                           (army_name(s["army_id"]) or ("兵种 " + s["army_id"]))}]
            s["troops"] = troops
            s["types"] = len(troops)
            s["army_id"] = troops[0]["army_id"]
            s["num"] = sum(int(t.get("num") or 0) for t in troops)
            # 每个兵种都补上中文名(页面/安卓要按兵种展示混编明细)
            for t in troops:
                if not t.get("name"):
                    t["name"] = (army_name(t.get("army_id")) or
                                 ("兵种 " + str(t.get("army_id"))))
            s["name"] = " + ".join(
                t.get("name") or (army_name(t["army_id"]) or t["army_id"])
                for t in troops)
            s["slot"] = i + 1
            s["state"] = "idle"       # idle / marching / done
            s["kills"] = 0
            s["fails"] = 0
            s["x"] = None
            s["y"] = None
            s["index"] = None
            s["base_march"] = None
            s["launch_cum"] = None
            s["launched_at"] = 0
            s["uuid"] = ""            # 本次行军的 uuid(判回用)
            s["out"] = 0
            s["launch_troops"] = []   # 本次实际派出的兵
            s["note"] = "待命"
        self._squads = slots
        self.state["squads"] = [dict(s) for s in slots]
        return slots

    def _sync_squads(self, army, marches=None):
        """把队伍状态同步到 state(供页面显示进度)。"""
        mm = self._march_map(army)
        marches = marches or {}
        now = time.time()
        for s in self._squads:
            if s["state"] != "marching":
                continue
            # 优先用**行军明细**算在外人数(能区分同兵种的多支部队)
            e = marches.get(s.get("uuid") or "") or None
            if e:
                total, dead = _march_troops(e)
                s["out"] = max(0, total - dead)
            elif s.get("base_march") is not None:
                # 没有明细(拿不到 uuid 的老路径): 按兵种总量兜底
                cur = mm.get(s["army_id"], 0)
                own = int(s.get("num") or 0)
                s["out"] = max(0, min(own, cur - int(s["base_march"] or 0)))
            s["elapsed"] = int(now - (s["launched_at"] or now))
        self.state["squads"] = [dict(s) for s in self._squads]

    def stop(self, note="已停止"):
        self.stop_flag = True
        self.state["running"] = False
        self.state["note"] = note
        self._emit("stop", {"note": note})

    def _launch(self, sq, army):
        """派一支队伍出征(可带多个兵种 = 混编)。返回 (ok, info)。"""
        by_id = {a["id"]: a for a in army}
        # 按队伍编成挑兵: 库存不够的那部分自动减掉, 全都没兵就不派
        troops = []
        for t in (sq.get("troops") or []):
            aid = str(t.get("army_id") or "")
            a = by_id.get(aid)
            if not a or a["free"] <= 0:
                continue
            n = min(int(t.get("num") or 0), int(a["free"]))
            if n <= 0:
                continue
            troops.append({"army_id": aid, "num": n,
                           "speed": a.get("speed"), "load": a.get("load")})
        if not troops:
            sq["state"] = "idle"
            sq["note"] = "无空闲兵"
            return False, {"error": "没有空闲兵"}
        # 体力预检: 不足就**别去找怪**了(找怪是网络往返, 白费)
        # ⚠️ 只在体力**已知**时才拦 —— stamina 为 None 表示还没读到,
        #    不能因为"不知道"就当"不够"(否则手动调 _launch 会被误拦)。
        cur_st = self.state.get("stamina")
        if cur_st is not None and int(cur_st) < STAMINA_COST:
            sq["state"] = "idle"
            sq["note"] = "等体力"
            return False, {"error": "体力不足", "errorCode": "E100047"}
        f = find_monster(self.client, self.level)
        if not f.get("ok"):
            code = str(f.get("errorCode") or "")
            # ⚠️ **这三种都不是"打怪失败"**, 别计入 fails(否则计数全是噪音):
            #   * SEARCH_LIMIT = 服务端说今日找怪次数用完(非 VIP; **SVIP 不会发生**)
            #   * NO_TARGET   = 世界上没有这个等级的怪
            #   * BAD_COORD   = 服务端返回了非法坐标
            if code in ("SEARCH_LIMIT", "NO_TARGET", "BAD_COORD"):
                sq["note"] = f.get("note") or ("没找到怪: %s" % code)
                return False, {"error": sq["note"], "errorCode": code}
            sq["note"] = "没找到怪"
            sq["fails"] += 1
            self.state["fails"] += 1
            return False, {"error": "没找到怪: %s" % code}
        # 这次 find 消耗了 1 次「今日找怪次数」(**只用于显示**)
        self._find_used += 1
        self.state["find_used"] = self._find_used
        idx = point_index(f["x"], f["y"])
        if not idx:
            sq["note"] = "坐标换算出错"
            sq["fails"] += 1
            self.state["fails"] += 1
            return False, {"error": "坐标换算出错: (%s,%s)" % (f.get("x"), f.get("y"))}
        num = sum(int(t["num"]) for t in troops)
        r = march_monsters(self.client, idx, troops)
        sq["x"], sq["y"], sq["index"] = f.get("x"), f.get("y"), idx
        sq["num"] = num
        # ⚠️ **不要**把实际派出的兵写回 `sq["troops"]` —— 那是这一队的
        #    **计划编成**; 写回会让"库存不足时摊薄"变成永久值
        #    (之后连续出征一直按摊薄后的小数量派)。
        sq["launch_troops"] = troops      # 本次**实际**派出的兵(显示用)
        # 本队派出后, 该兵种的**累计在外数量**(同兵种多队时用来判回)
        sq["base_march"] = max(int(by_id[t["army_id"]].get("march") or 0)
                               for t in troops) if troops else 0
        sq["launch_cum"] = sq["base_march"] + num
        sq["launched_at"] = time.time()
        # 行军 uuid —— 判回的唯一精确依据(见 read_march 的说明)
        sq["uuid"] = str(r.get("uuid") or "")
        sq["state"] = "marching" if r.get("ok") else "idle"
        if r.get("ok"):
            sq["note"] = "出征中"
        elif _is_stamina_error(r.get("errorCode")):
            # 体力不足: 正常等待, 不算失败
            sq["note"] = "等体力"
        else:
            sq["note"] = "失败 %s" % r.get("errorCode")
        self.state["last"] = {"x": f.get("x"), "y": f.get("y"), "index": idx,
                              "troop": sq["army_id"], "num": num,
                              "troops": [{"army_id": t["army_id"], "num": t["num"]}
                                          for t in troops],
                              "ok": bool(r.get("ok")), "errorCode": r.get("errorCode")}
        if not r.get("ok"):
            if not _is_stamina_error(r.get("errorCode")):
                sq["fails"] += 1
                self.state["fails"] += 1
            return False, self.state["last"]
        return True, self.state["last"]

    def _check_returned(self, army, marches=None):
        """检查哪些队伍回来了。返回本轮回来的队伍数。

        ✅ **主路径 = 行军 uuid 精确判定**(2026-11-09):
        出征成功时服务端在 `world.march` 响应里给了这支部队的 **uuid**;
        `world.user.march` 的 `m` 数组是"当前还在外面的每一支部队"。
        实测: 派出后 0.5 秒 `m` 里就有它 -> 行军 -> 到达 -> 战斗 -> 返程
        (uuid 不变, st/et 刷成返程段) -> **部队到家后这一条才消失**。
        ⇒ **uuid 不在 `m` 里 = 这支部队已经回家了**, 精确、不会认错人,
          同兵种拆多队也照样能一支一支分开判。

        ⚠️ **刚派出的一小段时间内不判**(UUID_RETURN_GAP):
        服务端可能还没把这次行军登记进 `m`, 这时"查不到"会被误当成"回来了"
        -> 立刻再派一次 -> **疯狂重复派出**, 体力几分钟能掉几百点
        (实测一次烧掉 574 点 = 57 只怪, 而 kills 计数还是 0)。

        🔁 **兜底(拿不到 uuid 时)**: 按兵种总量推算 ——
        服务端的 `army[].march` 是该兵种的**外勤总数量**, 不是队伍数,
        所以把已回来的数量按**先派先回**分配给各队; 算出来是负数就不判。
        """
        mm = self._march_map(army)
        marches = marches or {}
        back = 0
        now = time.time()
        legacy = []
        for s in self._squads:
            if s["state"] != "marching":
                continue
            u = s.get("uuid") or ""
            if u:
                if u in marches:
                    continue              # 还在外面(行军/战斗/返程)
                if now - float(s.get("launched_at") or now) < UUID_RETURN_GAP:
                    continue              # 刚派出, 服务端可能还没登记
                s["state"] = "done"
                s["note"] = "已回来"
                s["kills"] += 1
                s["out"] = 0
                # ⚠️ 清掉 uuid: 这支队接下来会**再次出征**(连续出征),
                #    留着旧 uuid 会让它一派出就被判"已回来"(等于没派出去)。
                s["uuid"] = ""
                s["launch_troops"] = []
                back += 1
                self.state["kills"] += 1
            else:
                legacy.append(s)
        if not legacy:
            return back
        # ---- 兜底: 按**编成签名**分组, 按累计在外数量判定 ----
        # (拿不到 uuid 的老路径才走这里。混编队伍不能按单个兵种分组 ——
        #  一支队有多个兵种, 外勤数是它们加起来。)
        groups = {}
        for s in legacy:
            sig = tuple(sorted(str(t.get("army_id") or "")
                               for t in (s.get("troops") or [])))
            groups.setdefault(sig, []).append(s)
        for _sig, sqs in groups.items():
            # 该组最近一次派出离现在太近 -> 行军统计可能还没更新,
            # 整个组这一轮都不判(宁可晚判, 不能误判)
            newest = max(float(s.get("launched_at") or 0) for s in sqs)
            if now - newest < MIN_LAUNCH_GAP:
                continue
            base = min(int(s.get("base_march") or 0) for s in sqs)
            launched = sum(int(s.get("num") or 0) for s in sqs)
            # 外勤总数 = 组里所有兵种的外勤数之和
            cur = 0
            for aid in set(str(t.get("army_id") or "")
                           for s in sqs for t in (s.get("troops") or [])):
                cur += int(mm.get(aid, 0))
            returned = base + launched - cur
            if returned <= 0:
                # 没回来的数量算不出来(或者为负) -> 不判
                continue
            # 先派先回: 把已回来的数量按顺序分给各队
            left = returned
            for s in sorted(sqs, key=lambda x: float(x.get("launched_at") or 0)):
                need = int(s.get("num") or 0)
                if need <= 0:
                    continue
                if left < need:
                    break
                left -= need
                s["state"] = "done"
                s["note"] = "已回来"
                s["kills"] += 1
                s["out"] = 0
                s["uuid"] = ""
                s["launch_troops"] = []
                back += 1
                self.state["kills"] += 1
        return back

    def _maybe_tick(self, min_interval=60.0):
        """按间隔触发 on_tick(在打怪线程里, 同一条连接, 不额外占号)。"""
        if not self.on_tick:
            return
        now = time.time()
        if now - self._last_tick < min_interval:
            return
        self._last_tick = now
        try:
            self.on_tick(self.client)
        except Exception:
            pass

    def run(self):
        self.state["running"] = True
        self.state["note"] = "打怪中"
        self._emit("start", dict(self.state))
        self._round = 0
        while not self.stop_flag:
            try:
                # 打点: 卡住时能看出停在哪一步(只记 step, 不记数据)。
                # 只在前几轮和之后每 30 轮打一次, 免得刷爆日志。
                self._round += 1
                if self._round <= 3 or self._round % 30 == 0:
                    self._emit("step", {"step": "stamina", "round": self._round})
                st = self._read_stamina()
                # ⚠️ 体力掉得太快 -> 立刻停(保命阀: 异常结算会白烧体力)
                burst = self._stamina_burst()
                if burst > STAMINA_BURST_LIMIT:
                    self.state["note"] = ("体力消耗异常(%.0f 秒掉了 %d 点), 已自动停止"
                                         % (STAMINA_BURST_WINDOW, burst))
                    self.stop(self.state["note"])
                    break
                if self._round <= 3 or self._round % 30 == 0:
                    self._emit("step", {"step": "army", "round": self._round})
                mk = read_march(self.client)
                army = mk["army"]
                all_army = mk["all"]      # 含 free=0 的兵种(算外勤量要用它)
                marches = mk["marches"]
                if self._round <= 3 or self._round % 30 == 0:
                    self._emit("step", {"step": "assign", "round": self._round})
                if not self._squads:
                    self._assign(army)
                    if not self._squads:
                        self.state["note"] = "没有可用兵种"
                        self._emit("tick", dict(self.state))
                        time.sleep(self.wait_stamina)
                        continue
                if self._round <= 3 or self._round % 30 == 0:
                    self._emit("step", {"step": "launch", "round": self._round})
                self._check_returned(all_army, marches)
                self._sync_squads(all_army, marches)
                self.state["troops_out"] = sum(
                    int(a.get("march") or 0) for a in army)
                out_slots = [s for s in self._squads if s["state"] == "marching"]
                self.state["wait_for"] = ("等部队回来(还有 %d 队在外)" % len(out_slots)
                                          if out_slots else "")
                # 体力不够就等恢复
                if st["stamina"] < self.min_stamina:
                    # ★ 体力不足时自动喝背包里的体力药水(可选开关)
                    if self._use_stamina_if_needed():
                        st["stamina"] = int(self.state.get("stamina") or 0)
                if st["stamina"] < self.min_stamina:
                    self.state["note"] = self.state["wait_for"] or (
                        "体力低于安全阈值 %d(还差 %d)" % (
                            self.min_stamina, self.min_stamina - st["stamina"]))
                    self._emit("tick", dict(self.state))
                    time.sleep(self.wait_stamina)
                    continue
                if self.max_kills and self.state["kills"] >= self.max_kills:
                    self.stop("达到目标次数 %d" % self.max_kills)
                    break
                # 派空闲队
                # ⚠️ 体力是**按怪**消耗的: 并行 N 队 = N 倍消耗速度,
                # 而体力恢复只有约 1 点/130 秒。所以每派一队前都要重新算
                # "剩下的体力够不够再派一队", 体力不够就少派, 自动收缩并发数。
                # 注意: st["stamina"] 是本轮轮询读到的值, 派出后要**立刻扣掉**,
                # 否则一轮内会按旧体力派出超出体力上限的队。
                #
                # ⚠️ **一轮可以派多队**(2026-11-09 改): 以前每轮只派一队
                # (`if launched: break`), 于是"设 8 队"实际要等 8 个轮询周期
                # 才开满, 而且**同一种兵拆成的多队**会被拖成串行。
                # 现在一轮内可以连续派多队 —— 唯一的硬约束是
                #   * 体力(每队 9 点, 派一队扣一队);
                #   * **并发上限**(已经在外面的队 + 本轮新派的 <= 队伍数);
                #   * 找怪节流: 每派一队都要一次 `res.tile.find`, 连续太多次
                #     会被服务端节流, 所以每轮最多派 `MAX_LAUNCH_PER_ROUND` 队。
                # ⚠️ **这里不做任何"找怪次数"拦截**(2026-11-12 改):
                # 服务端对 **SVIP 账号不限次数**, 但下发的 `world.maxSearchCount`
                # 照样是 6 —— 之前拿这个值硬拦, 把 SVIP 号打几轮就卡成
                # 「今日找怪次数已用完」。**服务端才是唯一权威**:
                # 只有它真的返回空坐标才算次数用完(见 `_launch` 的 SEARCH_LIMIT)。
                # 本地 `_find_used` 只用来显示「今日已用 N 次」。
                idle = [s for s in self._squads if s["state"] in ("idle", "done")]
                launched = 0
                round_note = ""
                for s in idle:
                    if launched >= MAX_LAUNCH_PER_ROUND:
                        break
                    if len(out_slots) + launched >= self.squad_max:
                        break        # 并行上限: 队伍数就是并发上限
                    if st["stamina"] - STAMINA_COST < 0 or st["stamina"] < self.min_stamina:
                        round_note = "体力只够 %d 队(等恢复)" % (
                            len(out_slots) + launched)
                        break
                    ok, info = self._launch(s, army)
                    if ok:
                        launched += 1
                        st["stamina"] = max(0, st["stamina"] - STAMINA_COST)
                    elif _is_stamina_error(info.get("errorCode")):
                        # 服务端说体力不足(E100047) —— 这是**正常等待**, 不是失败:
                        #   * _launch 里已经不计入 fails 了
                        #   * 立刻停止本轮派队(再派也是白费, 每个都要先 find 再 march)
                        #   * 把体力按服务端说的记为 0, 下轮直接用它
                        st["stamina"] = 0
                        round_note = "体力不足(服务端 E100047, 等恢复)"
                        # ★ 体力不足时自动喝背包里的体力药水(可选开关)
                        if self._use_stamina_if_needed():
                            st["stamina"] = int(self.state.get("stamina") or 0)
                        break
                    elif str(info.get("errorCode")) == "SEARCH_LIMIT":
                        # ⚠️ **今日找怪次数用完了**(每派一队消耗一次, 非 VIP 每天 6 次)。
                        # 次数按天重置, 再打也是空的 —— **直接停**, 别空转。
                        # (不再做 10 分钟倒计时冷却: 那个倒计时对"按天重置"
                        #  的限制毫无意义, 只会让用户盯着一个永远到不了的倒计时。)
                        self.stop("今日找怪次数已用完(非 VIP 每天 %d 次, 每日重置; "
                                  "SVIP 无限)。已停止, 明天再来" % FIND_LIMIT_DAILY)
                        break
                    elif str(info.get("errorCode")) in ("NO_TARGET", "BAD_COORD"):
                        # 世界上没有这个等级的怪 / 坐标非法 —— 不是失败, 但也派不出去。
                        round_note = info.get("error") or "没找到怪"
                        break
                self._sync_squads(all_army, marches)
                # ⚠️ 别把本轮的说明覆盖掉(原来无条件写 "打怪中",
                # 把 E100047 / 找怪次数用完这些**真正的信息**冲掉了)。
                self.state["note"] = round_note or self.state["wait_for"] or "打怪中"
                self._emit("tick", dict(self.state))
                self._maybe_tick()
                time.sleep(self.poll)
            except Exception as e:  # noqa: BLE001
                msg = str(e)
                self.state["note"] = "异常: %s" % msg[:120]
                self._emit("error", {"error": msg[:200]})
                # ⚠️ **把 traceback 记进 state**(2026-11-11 加):
                # 之前只留一行 `str(e)`, 出了 `int(None)` 这种错根本定位不到行,
                # 只能靠猜。页面/安卓端看 note 就知道是哪一行炸的。
                tb = traceback.format_exc()
                self.state["traceback"] = tb[-2000:]
                self.state["error_kind"] = type(e).__name__
                try:
                    print("[hunt] 异常 %s: %s\n%s" % (type(e).__name__, msg, tb),
                          flush=True)
                except Exception:  # noqa: BLE001
                    pass
                if _is_fatal_conn_error(msg):
                    # 连接已经死了。**先试着救一次**: 服务端把连接关掉, 绝大多数
                    # 是"同账号双连接"(游戏 App 还在线, 游戏服只留一条)。
                    # 直接放弃的话, 用户看到的就是"点打怪后立刻退出"。
                    new_client = self._try_reconnect()
                    if new_client is not None:
                        continue
                    # 救不回来 —— 必须**停下来把账号还回去**。
                    # 否则它会一直占着这个连接, 整个控制台的轮询都被跳过
                    # ("自动打怪占用连接, 已跳过本轮"), 页面看着像卡死。
                    self.state["note"] = "连接断开, 已自动停止: %s" % msg[:80]
                    self._emit("stopped", dict(self.state))
                    break
                self._fatal_streak += 1
                if self._fatal_streak >= 5:
                    self.state["note"] = "连续 5 次异常, 已停止: %s" % msg[:80]
                    self._emit("stopped", dict(self.state))
                    break
                time.sleep(3)
        self.state["running"] = False
        self._emit("done", dict(self.state))


def snapshot(client):
    """一次拿到网页需要的全部只读信息。"""
    data = read_data(client)
    st = read_stamina(client)
    try:
        maxlv = read_max_level(client)
    except Exception:
        maxlv = 0
    lv_raw = str(data.get("lv") or "")
    parts = [p for p in lv_raw.split(";") if p.strip()]
    return {
        "stamina": st["stamina"],
        "stamina_max": st["max"],
        "last_stamina_time": st["lastStaminaTime"],
        "status": st["status"],
        "lv": lv_raw,
        "lv_low": int(parts[0]) if parts else 1,
        "lv_high": int(parts[1]) if len(parts) > 1 else (int(parts[0]) if parts else 1),
        "format": data.get("format") or "",
        "auto_count": int(data.get("autoCount") or 0),
        "force": int(data.get("force") or 0),
        "max_level": maxlv,
        "week_card_item": WEEK_CARD_ITEM,
        "stamina_items": STAMINA_ITEMS,
    }


def main():
    import argparse
    import sys
    sys.path.insert(0, HERE)
    from cok_client import CokClient, load_account

    ap = argparse.ArgumentParser(description="COK 打野怪 / 体力 / 自动打怪队列")
    ap.add_argument("--account", default="device", help="device / <pfId>")
    ap.add_argument("--cmd", default="snapshot",
                    help="snapshot|stamina|levels|army|find|set-level|set-format|on|off")
    ap.add_argument("--level", type=int, help="怪等级(find / set-level 用)")
    ap.add_argument("--high", type=int, help="怪等级上限(set-level 用)")
    ap.add_argument("--format", help="部队编成串(set-format 用)")
    ap.add_argument("--per-type", type=int, default=50, help="每个兵种派出数量(生成编成用)")
    args = ap.parse_args()

    cl = CokClient(account=load_account(args.account))
    cl.connect()
    cl.bin_handshake()
    cl.login()
    try:
        if args.cmd == "snapshot":
            print(json.dumps(snapshot(cl), ensure_ascii=False, indent=1))
        elif args.cmd == "stamina":
            print(json.dumps(read_stamina(cl), ensure_ascii=False))
        elif args.cmd == "levels":
            print(json.dumps({"max": read_max_level(cl),
                              "levels": load_levels()}, ensure_ascii=False, indent=1))
        elif args.cmd == "army":
            print(json.dumps(list_army(cl), ensure_ascii=False, indent=1))
        elif args.cmd == "find":
            print(json.dumps(find_monster(cl, args.level), ensure_ascii=False))
        elif args.cmd == "set-level":
            print(json.dumps(save_level(cl, args.level, args.high), ensure_ascii=False))
        elif args.cmd == "set-format":
            army = list_army(cl)
            fmt = args.format or build_format(army, args.per_type)
            print("编成:", fmt)
            print(json.dumps(save_format(cl, fmt), ensure_ascii=False))
        elif args.cmd == "on":
            print(json.dumps(set_status(cl, True), ensure_ascii=False))
        elif args.cmd == "off":
            print(json.dumps(set_status(cl, False), ensure_ascii=False))
    finally:
        cl.close()


if __name__ == "__main__":
    main()
