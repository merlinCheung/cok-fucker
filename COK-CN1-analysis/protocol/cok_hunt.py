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
  * `format` 是**部队编成** "兵种id,数量|兵种id,数量"，多个队列用 ";" 分隔。
  * 体力上限 100 来自游戏规则(服务端未下发该字段; 客户端 worldConfig.staminaMax
    只用于中立/帝国战场)。可用环境变量 COK_STAMINA_MAX 覆盖。
"""
import hashlib
import json
import os
import time

HERE = os.path.dirname(os.path.abspath(__file__))

#: 世界 x 方向格数(客户端 WorldController::getIndexByPoint 的 w1; 服务端
#: `login.dataconfig` 的 worldmap_map.k1 = 1201)。
WORLD_W = 1201

#: 打野怪行军类型(客户端 gameConst.lua: MarchMethodType.MethodFieldMonster = 6)
MARCH_TYPE_FIELDMONSTER = 6

#: marchKey 固定盐(客户端 AutoQueueInfo:autoMarch / OpenGranaryMarchCommand)
MARCH_KEY_SALT = "wNSc5Mm8YwiOhAab"

#: 体力上限(游戏内看到的 100)。服务端主世界配置里没有 staminaMax,
#: 且实测服务端 stamina 能到 108(可能含加成), 所以这是保守值; 可用环境变量覆盖。
STAMINA_MAX = int(os.environ.get("COK_STAMINA_MAX", "100"))

#: 每打一只野怪消耗的体力(实测 9: 113->104, 108->99)
STAMINA_COST = 9


def _is_fatal_conn_error(msg):
    """这个异常是不是"连接已经死了, 重试也没用"。

    致命错误的特征: 管道断了 / 服务端关了连接 / 连接被重置。
    遇到这种必须**立刻停止**并把账号还回去 —— 否则循环会一直重试,
    一直占着连接, 整个控制台的轮询都被跳过。
    """
    m = str(msg)
    return ("Broken pipe" in m or "连接被服务端关闭" in m
            or "ConnectionReset" in m or "Connection refused" in m
            or "BrokenPipeError" in m)


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
#: 体力道具 id(客户端 data_config.auto_kill_monster.k1)
STAMINA_ITEMS = ["200380", "200381"]   # 10体力 / 50体力


def load_levels(path=None):
    """本地野怪等级表(客户端配置 field_monster 组里 usePower=10 且 type=0 的世界野怪)。"""
    path = path or os.path.join(HERE, "monster-levels.json")
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


def list_army(client):
    """部队清单: 只返回有空闲兵(free>0)的兵种, 按战力从高到低。

    带 `march` 字段(该兵种当前在外勤的数量) —— 多队并行时用它判断
    某一队是否已经回来(各队绑定**不同**兵种, 判定互不干扰)。
    """
    r = client.call("world.user.march")
    army = (r.get("__params__") or {}).get("army") or []
    out = []
    for a in army:
        free = int(a.get("free") or 0)
        if free <= 0:
            continue
        out.append({
            "id": str(a.get("id")),
            "free": free,
            "march": int(a.get("march") or 0),
            "speed": a.get("speed"),
            "load": a.get("load"),
            "power": a.get("power"),
            "attack": a.get("attack"),
            "defen": a.get("defen"),
            "health": a.get("health"),
            "level": a.get("level"),
        })
    out.sort(key=lambda x: float(x.get("power") or 0), reverse=True)
    return out


def standard_army(army):
    """只取**标准兵种**(6 位 107xxx 系列)。

    ⚠️ 实测: 编成里混入活动限定兵种(575xxxxx / 40400xxx 这类 8 位 id)时,
    服务端会回 E000000 —— 单独一个 575 兵种可以, 但和普通兵种混编不行。
    """
    std = [a for a in army if len(a["id"]) == 6 and a["id"].startswith("10")]
    return std


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
    """搜索一只指定等级的野怪, 返回坐标(x/y)。搜索次数有限(实测 maxSearchCount=6)。"""
    r = client.call("res.tile.find", {"type": 6, "level": int(level), "NoRecord": 1})
    p = r.get("__params__") or {}
    if p.get("errorCode"):
        return {"ok": False, "errorCode": p.get("errorCode")}
    return {"ok": True, "x": p.get("x"), "y": p.get("y"), "level": p.get("level")}


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
    """
    x = int(x)
    y = int(y)
    if x <= 0 or y <= 0:
        return 0
    return x + 1 + int(w * y)


def march_key(index, army, march_type=MARCH_TYPE_FIELDMONSTER):
    """算 marchKey。

    客户端算法(AutoQueueInfo:autoMarch):
        md5( index + "1021" + (marchType+1)*1000 + [armyId, speed, load, num]* + 盐 )
    ⚠️ 多兵种时 army 的拼接顺序取决于客户端 `ipairs4ScatteredT`(C++ 散列表遍历顺序),
    尚未确定 —— 所以这里**只支持单个兵种**(顺序唯一, 结果可复现)。
    """
    if len(army) != 1:
        raise ValueError("march_key 目前只支持单兵种(客户端多兵种遍历顺序未确定)")
    parts = [str(int(index)), "1021", str((int(march_type) + 1) * 1000)]
    for aid, (speed, load, num) in army.items():
        parts += [str(int(aid)), str(speed), str(load), str(int(num))]
    parts.append(MARCH_KEY_SALT)
    return hashlib.md5("".join(parts).encode()).hexdigest()


def march_monster(client, index, army_id, speed, load, num,
                  march_type=MARCH_TYPE_FIELDMONSTER, general_id="",
                  pet_dragon_uid="", aormation_id=""):
    """派兵出征打野怪。会真实消耗士兵与体力。

    ⚠️ `soldiers` 的数量必须编码成 SFS **INT**(客户端 CCDictionary 里是 CCInteger);
    而 encode_value 对普通 Python int 会压成最小宽度(BYTE), 服务端会回 E000000。
    """
    from cok_sfs import TypedInt, SFS_INT
    army = {str(int(army_id)): (speed, load, int(num))}
    key = march_key(index, army, march_type)
    params = {
        "point": int(index),
        "type": int(march_type),
        "soldiers": {str(int(army_id)): TypedInt(int(num), SFS_INT)},
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
    return {"ok": True, "result": p, "marchKey": key, "point": int(index)}


# --------------------------------------------------------------------------
# 兵种中文名
# --------------------------------------------------------------------------
_NAMES_CACHE = {}


def _load_item_names():
    """id -> 中文名(id-names.json 的 item_names)。"""
    if _NAMES_CACHE:
        return _NAMES_CACHE
    try:
        with open(os.path.join(HERE, "id-names.json"), encoding="utf-8") as f:
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
      每支队伍绑定**一个互不相同的兵种**, 出发时记下该兵种 `army[].march`
      的基线; 之后只要该兵种的外勤数回到基线, 就说明这支队伍回来了。
      因为各队兵种不同, 彼此不会干扰。

    实测数据(2026-10-24/25):
      * 体力消耗按怪等级: 1 级怪 9 点 / 15 级怪 10 点(客户端 usePower 表)
      * 体力**不靠战斗返还**, 只随时间恢复, 约 **1 点 / 130 秒**
      * 行军+战斗很快(几十秒), 部队回来后 `army[].march` 归零
    """

    def __init__(self, client, level=1, num=50, troop_id=None, max_kills=0,
                 on_event=None, poll=2.0, wait_stamina=60.0,
                 squads=4, squad_spec=None, on_tick=None):
        self.client = client
        self.level = int(level)
        self.num = int(num)
        self.troop_id = troop_id
        self.max_kills = int(max_kills or 0)
        self.on_event = on_event
        self.poll = poll
        self.wait_stamina = wait_stamina
        self.squad_max = max(1, int(squads or 1))
        # 每圈的回调(在**本线程**里调用, 所以可以安全地用同一条连接发命令)
        # 用来搭顺风车做别的事, 比如港口定时检查 —— 不额外占号
        self.on_tick = on_tick
        self._last_tick = 0.0
        # 每队的兵种分配: [{army_id, num}]。None = 自动挑(按战力最高的可用标准兵种)
        self.squad_spec = squad_spec or None
        self.stop_flag = False
        self.state = {
            "running": False, "kills": 0, "fails": 0, "level": int(level),
            "num": int(num), "troop": troop_id, "stamina": None, "stamina_max": STAMINA_MAX,
            "last": None, "note": "未开始", "recover_per_min": None,
            "troops_out": 0, "wait_for": "",
            "squad_max": self.squad_max, "squads": [],
            "killed_by_squad": 0,
        }
        self._stamina_samples = []
        self._fatal_streak = 0
        self._squads = []          # 运行期的队伍对象
        self._last_find = 0.0      # 上次找怪的时间(找怪有服务端节流)

    def _emit(self, kind, payload):
        if self.on_event:
            try:
                self.on_event(kind, payload)
            except Exception:
                pass

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

    def _march_map(self, army):
        """兵种 id -> 当前外勤数量。"""
        return {a["id"]: int(a.get("march") or 0) for a in army}

    def _assign(self, army):
        """给每个队伍槽位分配一个**互不相同**的兵种。"""
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
            for a in standard_army(army)[:self.squad_max]:
                slots.append({"army_id": a["id"], "num": min(self.num, a["free"]),
                              "speed": a.get("speed"), "load": a.get("load"),
                              "name": army_name(a["id"]) or ("兵种 " + a["id"])})
        # 去掉重复兵种(各队必须不同, 否则"回来"判定会互相干扰)
        seen = set()
        uniq = []
        for s in slots:
            if s["army_id"] in seen:
                continue
            seen.add(s["army_id"])
            uniq.append(s)
        for i, s in enumerate(uniq):
            s["slot"] = i + 1
            s["state"] = "idle"       # idle / marching / done
            s["kills"] = 0
            s["fails"] = 0
            s["x"] = None
            s["y"] = None
            s["index"] = None
            s["base_march"] = None
            s["launched_at"] = 0
            s["note"] = "待命"
        self._squads = uniq
        self.state["squads"] = [dict(s) for s in uniq]
        return uniq

    def _sync_squads(self, army):
        """把队伍状态同步到 state(供页面显示进度)。"""
        mm = self._march_map(army)
        now = time.time()
        for s in self._squads:
            if s["state"] == "marching" and s["base_march"] is not None:
                cur = mm.get(s["army_id"], 0)
                s["out"] = cur - s["base_march"]
                s["elapsed"] = int(now - (s["launched_at"] or now))
            if s.get("out") is not None:
                s["out"] = mm.get(s["army_id"], 0) - (s["base_march"] or 0)
        self.state["squads"] = [dict(s) for s in self._squads]

    def stop(self, note="已停止"):
        self.stop_flag = True
        self.state["running"] = False
        self.state["note"] = note
        self._emit("stop", {"note": note})

    def _launch(self, sq, army):
        """派一支队伍出征。返回 (ok, info)。"""
        by_id = {a["id"]: a for a in army}
        a = by_id.get(sq["army_id"])
        if not a or a["free"] <= 0:
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
            sq["note"] = "没找到怪"
            sq["fails"] += 1
            self.state["fails"] += 1
            return False, {"error": "没找到怪: %s" % f.get("errorCode")}
        idx = point_index(f["x"], f["y"])
        if not idx:
            sq["note"] = "坐标换算出错"
            sq["fails"] += 1
            self.state["fails"] += 1
            return False, {"error": "坐标换算出错: (%s,%s)" % (f.get("x"), f.get("y"))}
        num = min(int(sq["num"]), int(a["free"]))
        r = march_monster(self.client, idx, sq["army_id"], a.get("speed"),
                          a.get("load"), num)
        sq["x"], sq["y"], sq["index"] = f.get("x"), f.get("y"), idx
        sq["num"] = num
        sq["base_march"] = int(a.get("march") or 0)
        sq["launched_at"] = time.time()
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
                              "ok": bool(r.get("ok")), "errorCode": r.get("errorCode")}
        if not r.get("ok"):
            if not _is_stamina_error(r.get("errorCode")):
                sq["fails"] += 1
                self.state["fails"] += 1
            return False, self.state["last"]
        return True, self.state["last"]

    def _check_returned(self, army):
        """检查哪些队伍回来了。返回本轮回来的队伍数。"""
        mm = self._march_map(army)
        back = 0
        for s in self._squads:
            if s["state"] != "marching":
                continue
            base = s["base_march"] or 0
            if mm.get(s["army_id"], 0) <= base:
                s["state"] = "done"
                s["note"] = "已回来"
                s["kills"] += 1
                s["out"] = 0
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
        while not self.stop_flag:
            try:
                st = self._read_stamina()
                army = list_army(self.client)
                if not self._squads:
                    self._assign(army)
                    if not self._squads:
                        self.state["note"] = "没有可用兵种"
                        self._emit("tick", dict(self.state))
                        time.sleep(self.wait_stamina)
                        continue
                self._check_returned(army)
                self._sync_squads(army)
                self.state["troops_out"] = sum(
                    int(a.get("march") or 0) for a in army)
                out_slots = [s for s in self._squads if s["state"] == "marching"]
                self.state["wait_for"] = ("等部队回来(还有 %d 队在外)" % len(out_slots)
                                          if out_slots else "")
                # 体力不够就等恢复
                if st["stamina"] < STAMINA_COST:
                    self.state["note"] = self.state["wait_for"] or (
                        "体力不足(还差 %d)" % (STAMINA_COST - st["stamina"]))
                    self._emit("tick", dict(self.state))
                    time.sleep(self.wait_stamina)
                    continue
                if self.max_kills and self.state["kills"] >= self.max_kills:
                    self.stop("达到目标次数 %d" % self.max_kills)
                    break
                # 派空闲队(一次只派一队, 避免连续 find 触发服务端节流)
                # ⚠️ 体力是**按怪**消耗的: 并行 N 队 = N 倍消耗速度,
                # 而体力恢复只有约 1 点/130 秒。所以每派一队前都要重新算
                # "剩下的体力够不够再派一队", 体力不够就少派, 自动收缩并发数。
                # 注意: st["stamina"] 是本轮轮询读到的值, 派出后要**立刻扣掉**,
                # 否则一轮内会按旧体力派出超出体力上限的队。
                idle = [s for s in self._squads if s["state"] in ("idle", "done")]
                launched = 0
                for s in idle:
                    if st["stamina"] - STAMINA_COST < 0:
                        self.state["note"] = "体力只够 %d 队(等恢复)" % (
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
                        self.state["note"] = "体力不足(服务端 E100047, 等恢复)"
                        break
                    if launched:
                        break
                self._sync_squads(army)
                self.state["note"] = self.state["wait_for"] or "打怪中"
                self._emit("tick", dict(self.state))
                self._maybe_tick()
                time.sleep(self.poll)
            except Exception as e:  # noqa: BLE001
                msg = str(e)
                self.state["note"] = "异常: %s" % msg[:120]
                self._emit("error", {"error": msg[:200]})
                if _is_fatal_conn_error(msg):
                    # 连接已经死了, 再重试也没用 —— 必须**停下来把账号还回去**。
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
