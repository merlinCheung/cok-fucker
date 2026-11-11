#!/usr/bin/env python3
"""「一次出征多兵种(混编)」+「同兵种连续/并行多队」的单元测试(零消耗)。

覆盖 2026-11-09 真服实测确认的协议规则:
  * 一次出征可以带**多个兵种**(混编): 标准+标准 OK / 活动+活动 OK;
    **跨类混编被拒**(活动 57580718 + 普通 107012 -> E000000)
    ⇒ 混编只在同类里做(见 `cok_hunt._army_class`)
  * marchKey 的多兵种拼接顺序 = **兵种 id 字典序升序**(倒序/原始顺序会被拒)
  * soldiers 的数量必须编码成 SFS **INT**(否则 E000000)
  * 同一种兵可以**并行开多队**, 判回按**行军 uuid** 精确区分
  * 混编队整队共用一个 uuid, 外勤数 = 各兵种外勤数之和
  * 判回后清空 uuid -> 同一队可以**连续再次出征**
"""

import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

os.environ['COK_ACCOUNT_LOCK_FILE'] = os.path.join(
    tempfile.gettempdir(), 'cok-test-mix-%d.lock' % os.getpid())
import cok_hunt  # noqa: E402
from cok_sfs import SFS_INT  # noqa: E402


class MixFakeClient(object):
    """假客户端: 支持**多兵种**出征(标准兵种明细是 list, 活动兵种明细内嵌 id)。"""

    def __init__(self, army):
        self.army = {a["id"]: dict(a) for a in army}
        self.marched = []          # [(army_id, num)]
        self.marches = {}          # uuid -> {"uuid","army":[{total,dead}]}
        self.find_count = 0
        self.stamina = 1000
        self._seq = 0
        self.last_soldiers = None   # 最近一次 world.march 的 soldiers
        self.last_march_key = None

    def call(self, cmd, params=None, retries=1):
        if cmd == "world.user.march":
            return {"__params__": {
                "army": [dict(v) for v in self.army.values()],
                "m": [dict(v) for v in self.marches.values()]}}
        if cmd == "autoQueue.status":
            return {"__params__": {"stamina": self.stamina, "max": 1000,
                                   "lastStaminaTime": 0, "status": 0}}
        if cmd == "res.tile.find":
            self.find_count += 1
            return {"__params__": {"x": 500 + self.find_count, "y": 900,
                                   "level": params.get("level", 1)}}
        if cmd == "world.march":
            soldiers = params.get("soldiers") or {}
            self.last_soldiers = soldiers
            self.last_march_key = params.get("marchKey")
            self._seq += 1
            uuid = "u%03d" % self._seq
            detail = []
            for aid, n in soldiers.items():
                n = int(n)
                detail.append({"total": n, "dead": 0, "armId": int(aid)})
                self.marched.append((aid, n))
                a = self.army.get(aid)
                if a:
                    a["march"] = int(a.get("march") or 0) + n
                    a["free"] = int(a["free"]) - n
            self.marches[uuid] = {"uuid": uuid, "army": detail}
            self.stamina -= 9
            return {"__params__": {"$_monitor_log_$": {"uuid": uuid}}}
        raise AssertionError("未预期的命令 %s" % cmd)

    def bring_back(self, uuid):
        e = self.marches.pop(uuid, None)
        if not e:
            return
        for item in (e.get("army") or []):
            aid = str(item.get("armId"))
            n = int(item.get("total") or 0)
            a = self.army.get(aid)
            if a:
                a["march"] = max(0, int(a.get("march") or 0) - n)
                a["free"] = int(a["free"]) + n

    def marches_map(self):
        """服务端行军明细: uuid -> 明细(和 `cok_hunt.read_march` 一样是 dict)。"""
        return dict(self.marches)


def check(name, cond, detail=""):
    print("[%s] %s%s" % ("PASS" if cond else "FAIL", name,
                         ("  — " + detail) if detail else ""))
    return bool(cond)


STD = [
    {"id": "107110", "free": 100000, "march": 0, "speed": 9, "load": 13,
     "power": 10.8, "attack": 1, "defen": 1},
    {"id": "107012", "free": 90000, "march": 0, "speed": 9, "load": 13,
     "power": 10.1, "attack": 1, "defen": 1},
    {"id": "107111", "free": 80000, "march": 0, "speed": 9, "load": 13,
     "power": 10.1, "attack": 1, "defen": 1},
]
ACT = [
    {"id": "57580718", "free": 500000, "march": 0, "speed": 9, "load": 13,
     "power": 12.0, "attack": 1, "defen": 1},
    {"id": "57580618", "free": 400000, "march": 0, "speed": 9, "load": 13,
     "power": 11.5, "attack": 1, "defen": 1},
]


def main():
    ok = True

    # ------------------------------------------------------------------
    # 1. plan_squads: mix=1 每队一种兵; mix=2 每队两种(同类)兵
    # ------------------------------------------------------------------
    p1 = cok_hunt.plan_squads(STD + ACT, 1000, 4, 1)
    ok &= check("mix=1: 每队只用一种兵",
                all(len(s["troops"]) == 1 for s in p1["slots"]),
                str([len(s["troops"]) for s in p1["slots"]]))
    ok &= check("mix=1: 队名是单个兵种名",
                " + " not in p1["slots"][0]["name"], p1["slots"][0]["name"])

    p2 = cok_hunt.plan_squads(STD + ACT, 1000, 4, 2)
    types = [len(s["troops"]) for s in p2["slots"]]
    ok &= check("mix=2: 每队带 2 个兵种", all(t == 2 for t in types), str(types))
    ok &= check("mix=2: 队名是 'A + B'",
                " + " in p2["slots"][0]["name"], p2["slots"][0]["name"])
    ok &= check("mix=2: 队伍带 types 标记",
                all(s.get("types") == len(s["troops"]) for s in p2["slots"]))
    # **跨类不混编**: 每一队的兵种必须同类
    same_class = all(
        len(set(cok_hunt._army_class(t["army_id"]) for t in s["troops"])) == 1
        for s in p2["slots"])
    ok &= check("mix=2: 不跨类混编(活动兵不会和普通兵同队)", same_class)
    # 同类里的活动兵可以混编
    act_mix = [s for s in p2["slots"]
               if cok_hunt._army_class(s["troops"][0]["army_id"]) == "act"]
    ok &= check("mix=2: 活动兵之间可以混编",
                bool(act_mix) and len(act_mix[0]["troops"]) == 2,
                str([s["name"] for s in act_mix]))
    # 每队人数 = 各兵种之和, 且不超过用户填的上限
    ok &= check("mix=2: 每队总人数 = 各兵种之和",
                all(s["num"] == sum(t["num"] for t in s["troops"]) for s in p2["slots"]))
    ok &= check("mix=2: 每队人数不超过上限",
                all(s["num"] <= 1000 for s in p2["slots"]),
                str([s["num"] for s in p2["slots"]]))
    # 库存不能超支
    used = {}
    for s in p2["slots"]:
        for t in s["troops"]:
            used[t["army_id"]] = used.get(t["army_id"], 0) + t["num"]
    over = [a for a, n in used.items() if n > 100000]
    ok &= check("mix=2: 不会超发库存", not over, str(used))

    # ------------------------------------------------------------------
    # 2. march_key: 多兵种按 id 升序拼接(倒序会被服务端拒)
    # ------------------------------------------------------------------
    a_asc = {"107012": (9, 13, 100), "107110": (9, 13, 200)}
    k_asc = cok_hunt.march_key(12345, a_asc)
    # 我们自己**总是**按 id 升序拼 —— 传进来的 dict 顺序不影响结果
    ok &= check("marchKey: 传 dict 顺序不影响结果(内部按 id 升序)",
                cok_hunt.march_key(12345, {"107110": (9, 13, 200),
                                           "107012": (9, 13, 100)}) == k_asc)
    # 手工算一遍升序拼法, 确认算法没变
    import hashlib
    manual = hashlib.md5(("".join([
        "12345", "1021", str((cok_hunt.MARCH_TYPE_FIELDMONSTER + 1) * 1000),
        "107012", "9", "13", "100", "107110", "9", "13", "200",
        cok_hunt.MARCH_KEY_SALT])).encode()).hexdigest()
    ok &= check("marchKey: 升序拼接算法正确", k_asc == manual, k_asc)
    # **倒序拼**的 key 一定不同 —— 服务端只认升序那一种(实测倒序 -> E000000)
    manual_desc = hashlib.md5(("".join([
        "12345", "1021", str((cok_hunt.MARCH_TYPE_FIELDMONSTER + 1) * 1000),
        "107110", "9", "13", "200", "107012", "9", "13", "100",
        cok_hunt.MARCH_KEY_SALT])).encode()).hexdigest()
    ok &= check("marchKey: 倒序拼法会被服务端拒(与升序 key 不同)",
                manual_desc != k_asc, manual_desc)

    # ------------------------------------------------------------------
    # 3. march_monsters: 一次出征多个兵种
    # ------------------------------------------------------------------
    cl = MixFakeClient(STD + ACT)
    troops = [{"army_id": "107110", "speed": 9, "load": 13, "num": 300},
              {"army_id": "107012", "speed": 9, "load": 13, "num": 200}]
    r = cok_hunt.march_monsters(cl, 999, troops)
    ok &= check("march_monsters: 混编出征成功", bool(r.get("ok")), str(r.get("errorCode")))
    ok &= check("march_monsters: 返回行军 uuid", bool(r.get("uuid")), r.get("uuid"))
    ok &= check("march_monsters: soldiers 里有 2 个兵种",
                len(cl.last_soldiers or {}) == 2, str(list((cl.last_soldiers or {}).keys())))
    ok &= check("march_monsters: 数量编码成 SFS INT",
                all(int(v.sfs_type) == SFS_INT for v in (cl.last_soldiers or {}).values()),
                str([int(v.sfs_type) for v in (cl.last_soldiers or {}).values()]))
    ok &= check("march_monsters: 库存按各兵种分别扣",
                cl.army["107110"]["march"] == 300 and cl.army["107012"]["march"] == 200,
                "%s/%s" % (cl.army["107110"]["march"], cl.army["107012"]["march"]))

    # ------------------------------------------------------------------
    # 4. AutoHunter 混编队: 出征 / 判回 / 再出征
    # ------------------------------------------------------------------
    cl2 = MixFakeClient(STD)
    h = cok_hunt.AutoHunter(cl2, level=1, num=1000, squads=2, mix=2)
    slots = h._assign(cok_hunt.list_army(cl2))
    ok &= check("AutoHunter mix=2: 分配出混编队",
                bool(slots) and len(slots[0]["troops"]) == 2,
                str([s.get("name") for s in slots]))
    good, info = h._launch(slots[0], cok_hunt.list_army(cl2))
    ok &= check("AutoHunter mix=2: 混编队出征成功", good, str(info.get("errorCode")))
    ok &= check("AutoHunter mix=2: 状态=出征中",
                slots[0]["state"] == "marching", slots[0]["state"])
    ok &= check("AutoHunter mix=2: 记下了行军 uuid",
                bool(slots[0].get("uuid")), slots[0].get("uuid"))
    ok &= check("AutoHunter mix=2: 实际派出的兵写进 launch_troops",
                len(slots[0].get("launch_troops") or []) == 2,
                str(slots[0].get("launch_troops")))
    ok &= check("AutoHunter mix=2: 计划编成 troops 没被覆盖",
                len(slots[0].get("troops") or []) == 2)
    # 在外人数 = 各兵种外勤数之和
    h._sync_squads(cok_hunt.list_army(cl2), cl2.marches_map())
    ok &= check("AutoHunter mix=2: 外勤数 = 各兵种之和",
                slots[0]["out"] == slots[0]["num"], str(slots[0]["out"]))
    # uuid 还在 -> 不判回
    h._check_returned(cok_hunt.read_march(cl2)["all"],
                      cok_hunt.read_march(cl2)["marches"])
    ok &= check("AutoHunter mix=2: 还在外面时不判回来",
                slots[0]["state"] == "marching", slots[0]["state"])
    ok &= check("AutoHunter mix=2: 没误算击杀", h.state["kills"] == 0, str(h.state["kills"]))
    # 回来了 -> 判 done, uuid 清空 -> 可再次出征
    cl2.bring_back(slots[0]["uuid"])
    # 刚派出的一小段时间内不判(服务端可能还没登记行军) —— 这里把时间拨回去
    slots[0]["launched_at"] -= cok_hunt.UUID_RETURN_GAP + 1
    h._check_returned(cok_hunt.read_march(cl2)["all"],
                      cok_hunt.read_march(cl2)["marches"])
    ok &= check("AutoHunter mix=2: uuid 消失后判已回来",
                slots[0]["state"] == "done", slots[0]["state"])
    ok &= check("AutoHunter mix=2: 击杀数 +1", h.state["kills"] == 1, str(h.state["kills"]))
    ok &= check("AutoHunter mix=2: 判回后清空 uuid(可连续出征)",
                not slots[0].get("uuid"), str(slots[0].get("uuid")))
    # 再次出征
    good2, info2 = h._launch(slots[0], cok_hunt.list_army(cl2))
    ok &= check("AutoHunter mix=2: 同一队可以连续再次出征", good2,
                str(info2.get("errorCode")))
    ok &= check("AutoHunter mix=2: 第二次出征拿到新 uuid",
                bool(slots[0].get("uuid")) and slots[0]["state"] == "marching")

    # ------------------------------------------------------------------
    # 5. 同兵种并行多队 + 精确判回
    # ------------------------------------------------------------------
    cl3 = MixFakeClient(STD)
    h3 = cok_hunt.AutoHunter(cl3, level=1, num=500, squads=3, mix=1)
    s3 = h3._assign(cok_hunt.list_army(cl3))
    ok &= check("同兵种: 库存够时开满 3 队", len(s3) == 3, str(len(s3)))
    uuids = set()
    for s in s3:
        g, _ = h3._launch(s, cok_hunt.list_army(cl3))
        ok &= check("同兵种: 第 %d 队出征成功" % s["slot"], g)
        uuids.add(s.get("uuid"))
    ok &= check("同兵种: 3 队的 uuid 各不相同",
                len([u for u in uuids if u]) == 3, str(uuids))
    # 只回来一支 -> 只有那一支判 done
    first = s3[0]
    cl3.bring_back(first["uuid"])
    for s in s3:
        s["launched_at"] -= cok_hunt.UUID_RETURN_GAP + 1
    h3._check_returned(cok_hunt.read_march(cl3)["all"],
                       cok_hunt.read_march(cl3)["marches"])
    ok &= check("同兵种: 只有回来的那支判 done",
                first["state"] == "done" and s3[1]["state"] == "marching",
                "%s/%s" % (first["state"], s3[1]["state"]))
    ok &= check("同兵种: 击杀数只 +1", h3.state["kills"] == 1, str(h3.state["kills"]))

    # ------------------------------------------------------------------
    # 6. _army_class 分类规则
    # ------------------------------------------------------------------
    ok &= check("_army_class: 6位 107xxx = 普通兵种",
                cok_hunt._army_class("107110") == "std")
    ok &= check("_army_class: 8位活动兵 = 活动兵种",
                cok_hunt._army_class("57580718") == "act")
    ok &= check("_army_class: 活动兵与普通兵不同类",
                cok_hunt._army_class("57580718") != cok_hunt._army_class("107110"))

    print()
    if ok:
        print("全部通过")
        return 0
    print("有失败项")
    return 1


if __name__ == "__main__":
    sys.exit(main())
