#!/usr/bin/env python3
"""多队并行打怪的单元测试(不连游戏服, 零消耗)。

验证 AutoHunter 的并行状态机:
  * 每队绑定**互不相同**的兵种
  * 出征后 state=marching, 并记下该兵种 march 的基线
  * 该兵种 march 回到基线 -> 该队判定"已回来"(其他队不受影响)
  * 体力不足时不派出, 等恢复
  * 达到 max_kills 自动停
"""

import os
import tempfile
import sys
import types

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

# 测试用**独立**的账号锁文件, 否则会跟正在运行的网页控制台抢同一个账号
os.environ['COK_ACCOUNT_LOCK_FILE'] = os.path.join(
    tempfile.gettempdir(), 'cok-test-account-%d.lock' % os.getpid())
import cok_hunt  # noqa: E402


class FakeClient(object):
    """假客户端: 只实现 AutoHunter 用到的那几个调用。"""

    def __init__(self, army):
        self.army = {a["id"]: dict(a) for a in army}
        self.marched = []      # [(army_id, num)]
        self.find_count = 0
        self.stamina = 100

    def call(self, cmd, params=None, retries=1):
        if cmd == "world.user.march":
            return {"__params__": {"army": [dict(v) for v in self.army.values()]}}
        if cmd == "autoQueue.status":
            return {"__params__": {"stamina": self.stamina, "max": 100,
                                   "lastStaminaTime": 0, "status": 0}}
        if cmd == "res.tile.find":
            self.find_count += 1
            return {"__params__": {"x": 500 + self.find_count, "y": 900,
                                   "level": params.get("level", 1)}}
        if cmd == "world.march":
            aid = list((params.get("soldiers") or {}).keys())[0]
            n = int((params.get("soldiers") or {})[aid])
            self.marched.append((aid, n))
            self.army[aid]["march"] = int(self.army[aid].get("march") or 0) + n
            self.army[aid]["free"] = int(self.army[aid]["free"]) - n
            self.stamina -= 10
            return {"__params__": {}}
        raise AssertionError("未预期的命令 %s" % cmd)

    def bring_back(self, aid):
        """让某个兵种的部队回来(march 归零)。"""
        self.army[aid]["march"] = 0


def check(name, cond, detail=""):
    print("[%s] %s%s" % ("PASS" if cond else "FAIL", name,
                         ("  — " + detail) if detail else ""))
    return bool(cond)


def main():
    ok = True
    army = [
        {"id": "107110", "free": 100000, "march": 0, "speed": 9, "load": 13,
         "power": 10.8, "attack": 1, "defen": 1},
        {"id": "107012", "free": 21000, "march": 0, "speed": 9, "load": 13,
         "power": 10.1, "attack": 1, "defen": 1},
        {"id": "107111", "free": 29000, "march": 0, "speed": 9, "load": 13,
         "power": 10.1, "attack": 1, "defen": 1},
        {"id": "107212", "free": 1000, "march": 0, "speed": 9, "load": 13,
         "power": 10.1, "attack": 1, "defen": 1},
        {"id": "999999", "free": 500, "march": 0, "speed": 9, "load": 13,
         "power": 99.0, "attack": 1, "defen": 1},
    ]
    cl = FakeClient(army)
    h = cok_hunt.AutoHunter(cl, level=15, num=1000, squads=4,
                            squad_spec=[{"army_id": "107110", "num": 1000},
                                        {"army_id": "107012", "num": 1000},
                                        {"army_id": "107111", "num": 1000},
                                        {"army_id": "107212", "num": 1000}])

    # 手动驱动状态机(不跑线程)
    slots = h._assign(cok_hunt.list_army(cl))
    ok &= check("分配了 4 支队伍", len(slots) == 4, "实际 %d" % len(slots))
    ids = [s["army_id"] for s in slots]
    ok &= check("各队兵种互不相同", len(set(ids)) == len(ids), ",".join(ids))
    ok &= check("活动限定兵种(8位id)被排除",
                all(len(i) == 6 for i in ids), ",".join(ids))

    # 派出第一队
    o1, _ = h._launch(slots[0], cok_hunt.list_army(cl))
    ok &= check("第一队出征成功", o1)
    ok &= check("第一队状态=出征中", slots[0]["state"] == "marching",
                slots[0]["state"])
    ok &= check("第一队记下了 march 基线", slots[0]["base_march"] == 0,
                str(slots[0]["base_march"]))

    # 别的队还没动
    ok &= check("其他队仍在待命",
                all(s["state"] == "idle" for s in slots[1:]),
                ",".join(s["state"] for s in slots[1:]))

    # 只让第一队回来 → 只有第一队判定完成
    cl.bring_back("107110")
    h._check_returned(cok_hunt.list_army(cl))
    ok &= check("第一队判定已回来", slots[0]["state"] == "done", slots[0]["state"])
    ok &= check("其他队不受影响",
                all(s["state"] == "idle" for s in slots[1:]),
                ",".join(s["state"] for s in slots[1:]))
    ok &= check("击杀数 +1", h.state["kills"] == 1, str(h.state["kills"]))

    # 第二队出征
    o2, _ = h._launch(slots[1], cok_hunt.list_army(cl))
    ok &= check("第二队出征成功", o2)
    ok &= check("两队同时在外",
                sum(1 for s in slots if s["state"] == "marching") == 1,
                "marching=%d" % sum(1 for s in slots if s["state"] == "marching"))

    # 状态快照带得出每队信息(页面要显示进度)
    h._sync_squads(cok_hunt.list_army(cl))
    sq = h.state.get("squads") or []
    ok &= check("state 带出每队进度", len(sq) == 4, "队伍数 %d" % len(sq))
    ok &= check("每队有 slot/状态/数量",
                all("slot" in s and "state" in s and "num" in s for s in sq))

    # 体力不够时不派出(而且**不去找怪** —— 找怪是网络往返, 白费)
    cl.stamina = 3
    h.state["stamina"] = 3
    _find_called = {"v": False}
    _orig_find = cok_hunt.find_monster
    def _no_find(*a, **k):
        _find_called["v"] = True
        return {"ok": True, "x": 1, "y": 1}
    cok_hunt.find_monster = _no_find
    try:
        _ok2, _info2 = h._launch(slots[2], cok_hunt.list_army(cl))
    finally:
        cok_hunt.find_monster = _orig_find
    ok &= check("体力不足时不出征", not _ok2 and slots[2]["state"] != "marching",
                "state=%s" % slots[2]["state"])
    ok &= check("体力不足时不白跑找怪", not _find_called["v"])
    ok &= check("体力不足不计入 fails", h.state["fails"] == 0,
                "fails=%s" % h.state["fails"])

    # 并发数随体力自动收缩: 体力只够 1 队时不能派第 2 队
    cl.stamina = 12
    h2 = cok_hunt.AutoHunter(cl, level=15, num=1000, squads=4,
                             squad_spec=[{"army_id": "107110", "num": 1000},
                                         {"army_id": "107012", "num": 1000},
                                         {"army_id": "107111", "num": 1000},
                                         {"army_id": "107212", "num": 1000}])
    h2._assign(cok_hunt.list_army(cl))
    st2 = {"stamina": 12}
    launched = 0
    for s in h2._squads:
        if st2["stamina"] - 10 < 0:
            break
        ok, _ = h2._launch(s, cok_hunt.list_army(cl))
        if ok:
            launched += 1
            st2["stamina"] = max(0, st2["stamina"] - 10)
    ok &= check("并发数随体力自动收缩(12点只够1队)", launched == 1,
                "实际派出 %d 队" % launched)

    # 体力充足时可以派满 4 队
    cl.stamina = 100
    h3 = cok_hunt.AutoHunter(cl, level=15, num=1000, squads=4,
                             squad_spec=[{"army_id": "107110", "num": 1000},
                                         {"army_id": "107012", "num": 1000},
                                         {"army_id": "107111", "num": 1000},
                                         {"army_id": "107212", "num": 1000}])
    h3._assign(cok_hunt.list_army(cl))
    st3 = {"stamina": 100}
    launched3 = 0
    for s in h3._squads:
        if st3["stamina"] - 10 < 0:
            break
        ok, _ = h3._launch(s, cok_hunt.list_army(cl))
        if ok:
            launched3 += 1
            st3["stamina"] = max(0, st3["stamina"] - 10)
    ok &= check("体力充足时能派满 4 队并行", launched3 == 4,
                "实际派出 %d 队" % launched3)

    # 兵种中文名
    ok &= check("兵种中文名可解析", bool(cok_hunt.army_name("107110")),
                cok_hunt.army_name("107110"))

    # ---- 体力不足(E100047) 不算失败 ----
    ok &= check("E100047 识别为体力不足",
                cok_hunt._is_stamina_error("E100047")
                and cok_hunt._is_stamina_error("100047"))
    ok &= check("其它错误码不算体力不足",
                not cok_hunt._is_stamina_error("E100048")
                and not cok_hunt._is_stamina_error("E000000")
                and not cok_hunt._is_stamina_error(None))
    # _launch 遇到体力不足: 不找怪、不计 fails
    cl2 = FakeClient(army)
    h = cok_hunt.AutoHunter(cl2, level=15, num=1000, squads=4,
                            squad_spec=[{"army_id": "107110", "num": 1000},
                                        {"army_id": "107012", "num": 1000},
                                        {"army_id": "107111", "num": 1000},
                                        {"army_id": "107212", "num": 1000}])
    h._assign(cok_hunt.list_army(cl2))
    h.state["stamina"] = 2          # 低于 STAMINA_COST
    sq = h._squads[0]
    called = {"find": False}
    def fake_find(*a, **k):
        called["find"] = True
        return {"ok": True, "x": 1, "y": 1}
    orig_find = cok_hunt.find_monster
    cok_hunt.find_monster = fake_find
    try:
        okr, info = h._launch(sq, army)
    finally:
        cok_hunt.find_monster = orig_find
    ok &= check("体力不足时直接返回, 不去��怪",
                not called["find"], "find被调用=%s" % called["find"])
    ok &= check("体力不足不计入 fails",
                h.state["fails"] == 0 and sq.get("fails", 0) == 0,
                "fails=%s sq=%s" % (h.state["fails"], sq.get("fails")))
    ok &= check("体力不足时队伍标为等体力",
                sq.get("note") == "等体力", str(sq.get("note")))
    ok &= check("体力不足返回 errorCode=E100047",
                info.get("errorCode") == "E100047", str(info))

    print("\n%s" % ("全部通过" if ok else "存在失败项"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
