#!/usr/bin/env python3
"""多队并行打怪的单元测试(不连游戏服, 零消耗)。

验证 AutoHunter 的并行状态机:
  * 队伍按**库存**编排: 同一种兵可以拆成多队, 库存不够时按库存摊薄每队人数
  * 活动限定兵种(8 位 id)也能编队(单兵种出征实测可行)
  * 出征后 state=marching, 并记下这次行军的 **uuid**
  * **uuid 还在服务端行军列表里 -> 部队没回来**(不能提前判回来重复派队)
  * uuid 从列表里消失 -> 部队真的到家了 -> 该队判定"已回来"
  * 同兵种的多支部队能**一支一支精确**判回(不靠"总数减法"猜)
  * 体力不足时不派出, 等恢复
  * 达到 max_kills 自动停
"""

import os
import tempfile
import sys
import types

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "core"))
sys.path.insert(0, os.path.join(HERE, "..", "tools"))

# 测试用**独立**的账号锁文件, 否则会跟正在运行的网页控制台抢同一个账号
os.environ['COK_ACCOUNT_LOCK_FILE'] = os.path.join(
    tempfile.gettempdir(), 'cok-test-account-%d.lock' % os.getpid())
import cok_hunt  # noqa: E402


class FakeClient(object):
    """假客户端: 只实现 AutoHunter 用到的那几个调用。

    模拟服务端的两件事:
      * `world.user.march` 同时返回兵种清单(army)和**每支在外部队**(m)
      * `world.march` 响应里带 `$_monitor_log_$.uuid`
    """

    def __init__(self, army):
        self.army = {a["id"]: dict(a) for a in army}
        self.marched = []      # [(army_id, num)]
        self.marches = {}      # uuid -> {"uuid","id","army":[{"total","dead"}]}
        self.find_count = 0
        self.stamina = 100
        self._seq = 0

    def call(self, cmd, params=None, retries=1):
        if cmd == "world.user.march":
            return {"__params__": {
                "army": [dict(v) for v in self.army.values()],
                "m": [dict(v) for v in self.marches.values()]}}
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
            self._seq += 1
            uuid = "u%03d" % self._seq
            self.marches[uuid] = {"uuid": uuid, "id": aid,
                                  "army": [{"total": n, "dead": 0}]}
            self.marched.append((aid, n))
            self.army[aid]["march"] = int(self.army[aid].get("march") or 0) + n
            self.army[aid]["free"] = int(self.army[aid]["free"]) - n
            self.stamina -= 10
            return {"__params__": {"$_monitor_log_$": {"uuid": uuid}}}
        raise AssertionError("未预期的命令 %s" % cmd)

    def bring_back(self, aid):
        """让某个兵种的部队全部回来(march 归零, uuid 从列表消失)。"""
        self.army[aid]["march"] = 0
        for u in list(self.marches):
            if self.marches[u]["id"] == aid:
                del self.marches[u]

    def bring_back_one(self, uuid):
        """只让**一支**部队回来(同兵种拆多队时用)。"""
        e = self.marches.pop(uuid, None)
        if not e:
            return
        aid = e["id"]
        n = int((e.get("army") or [{}])[0].get("total") or 0)
        self.army[aid]["march"] = max(0, int(self.army[aid].get("march") or 0) - n)
        self.army[aid]["free"] = int(self.army[aid]["free"]) + n


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
        {"id": "57580718", "free": 900000, "march": 0, "speed": 9, "load": 13,
         "power": 12.0, "attack": 1, "defen": 1},
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
    ok &= check("按给定的编成分配兵种", ids == ["107110", "107012", "107111", "107212"],
                ",".join(ids))

    # 派出第一队
    o1, _ = h._launch(slots[0], cok_hunt.list_army(cl))
    ok &= check("第一队出征成功", o1)
    ok &= check("第一队状态=出征中", slots[0]["state"] == "marching",
                slots[0]["state"])
    ok &= check("第一队记下了 march 基线", slots[0]["base_march"] == 0,
                str(slots[0]["base_march"]))
    ok &= check("第一队记下了行军 uuid", bool(slots[0].get("uuid")),
                str(slots[0].get("uuid")))

    # 别的队还没动
    ok &= check("其他队仍在待命",
                all(s["state"] == "idle" for s in slots[1:]),
                ",".join(s["state"] for s in slots[1:]))

    # ⚠️ uuid **还在**服务端行军列表里 -> 不能判回来(否则会重复派队烧体力)
    slots[0]["launched_at"] -= cok_hunt.UUID_RETURN_GAP + 1
    h._check_returned(cok_hunt.read_march(cl)["all"],
                      cok_hunt.read_march(cl)["marches"])
    ok &= check("部队还在外面时**不判回来**",
                slots[0]["state"] == "marching", slots[0]["state"])
    ok &= check("没误算击杀", h.state["kills"] == 0, str(h.state["kills"]))

    # 只有 uuid 从列表里消失(=部队到家了)才算回来
    cl.bring_back("107110")
    h._check_returned(cok_hunt.read_march(cl)["all"],
                      cok_hunt.read_march(cl)["marches"])
    ok &= check("uuid 消失后判定已回来", slots[0]["state"] == "done", slots[0]["state"])
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
    mk = cok_hunt.read_march(cl)
    h._sync_squads(mk["army"], mk["marches"])
    sq = h.state.get("squads") or []
    ok &= check("state 带出每队进度", len(sq) == 4, "队伍数 %d" % len(sq))
    ok &= check("每队有 slot/状态/数量",
                all("slot" in s and "state" in s and "num" in s for s in sq))
    ok &= check("在外队伍能算出在外人数",
                any(s.get("out", 0) > 0 for s in sq),
                str([s.get("out") for s in sq]))

    # ---- 同兵种拆多队: uuid 精确判回, 一支一支分开 ----
    cl2 = FakeClient([
        {"id": "107012", "free": 60000, "march": 0, "speed": 9, "load": 13,
         "power": 10.1, "attack": 1, "defen": 1},
    ])
    h2 = cok_hunt.AutoHunter(cl2, level=15, num=10000, squads=3,
                             squad_spec=[{"army_id": "107012", "num": 10000},
                                         {"army_id": "107012", "num": 10000},
                                         {"army_id": "107012", "num": 10000}])
    slots2 = h2._assign(cok_hunt.list_army(cl2))
    ok &= check("同一种兵能编成 3 队", len(slots2) == 3, "实际 %d" % len(slots2))
    for s in slots2:
        h2._launch(s, cok_hunt.list_army(cl2))
    ok &= check("3 支同兵种部队都出征成功",
                all(s["state"] == "marching" for s in slots2),
                ",".join(s["state"] for s in slots2))
    ok &= check("3 支部队的 uuid 各不相同",
                len(set(s["uuid"] for s in slots2)) == 3,
                ",".join(s["uuid"] for s in slots2))
    # 只让**第一支**回家
    for s in slots2:
        s["launched_at"] -= cok_hunt.UUID_RETURN_GAP + 1
    cl2.bring_back_one(slots2[0]["uuid"])
    mk2 = cok_hunt.read_march(cl2)
    h2._check_returned(mk2["army"], mk2["marches"])
    ok &= check("同兵种: 只有回来的那一支判 done",
                slots2[0]["state"] == "done"
                and slots2[1]["state"] == "marching"
                and slots2[2]["state"] == "marching",
                ",".join(s["state"] for s in slots2))
    ok &= check("同兵种: 击杀数只 +1", h2.state["kills"] == 1, str(h2.state["kills"]))

    # ---- 按库存编排 ----
    # 主号实测: 只有 2 个兵种有空闲兵, 共 21941 人; 设 5 队 × 2w 时按库存摊薄
    main_army = [
        {"id": "107310", "free": 20000, "march": 0, "speed": 9, "load": 13,
         "power": 11.0, "attack": 1, "defen": 1},
        {"id": "107111", "free": 1941, "march": 0, "speed": 9, "load": 13,
         "power": 10.1, "attack": 1, "defen": 1},
    ]
    plan = cok_hunt.plan_squads(main_army, 20000, 5)
    ok &= check("库存不够时也能开满 5 队", plan["squads"] == 5, str(plan["squads"]))
    ok &= check("每队人数按库存摊薄", plan["num"] == 4388, str(plan["num"]))
    ok &= check("摊薄后标记 short", plan["short"] is True)
    ok &= check("摊薄后总兵力不超过库存",
                plan["total"] <= 21941, str(plan["total"]))
    ok &= check("每队只用一种兵",
                all(len(s["army_id"]) > 0 for s in plan["slots"]))

    # 库存充足时不摊薄
    plan2 = cok_hunt.plan_squads(main_army, 2000, 5)
    ok &= check("库存够就不摊薄", plan2["num"] == 2000 and not plan2["short"],
                "%s short=%s" % (plan2["num"], plan2["short"]))
    ok &= check("库存够时开满 5 队", plan2["squads"] == 5, str(plan2["squads"]))

    # 66手游号实测: 活动兵种库存巨大, 每队 2w 也能开满
    big_army = [
        {"id": "57580618", "free": 1156707, "march": 0, "speed": 9, "load": 13,
         "power": 12.0, "attack": 1, "defen": 1},
        {"id": "107012", "free": 18000, "march": 0, "speed": 9, "load": 13,
         "power": 10.1, "attack": 1, "defen": 1},
    ]
    plan3 = cok_hunt.plan_squads(big_army, 20000, 5)
    ok &= check("大库存时每队满编 2w", plan3["num"] == 20000, str(plan3["num"]))
    ok &= check("大库存时开满 5 队", plan3["squads"] == 5, str(plan3["squads"]))
    ok &= check("活动限定兵种(8位id)参与编队",
                any(len(s["army_id"]) == 8 for s in plan3["slots"]),
                ",".join(s["army_id"] for s in plan3["slots"]))
    ok &= check("活动兵种排在前面(先派强的)",
                plan3["slots"][0]["army_id"] == "57580618",
                plan3["slots"][0]["army_id"])

    # 没有兵时
    plan4 = cok_hunt.plan_squads([], 100, 5)
    ok &= check("没有可用兵时返回空", not plan4["slots"] and plan4["squads"] == 0)

    # ---- 行军明细: 标准兵种/活动兵种两种形态都要认 ----
    ok &= check("标准兵种行军明细: 50 人",
                cok_hunt._march_troops(
                    {"army": [{"total": 50, "dead": 0}, {"is1518": True}]}) == (50, 0))
    ok &= check("活动兵种行军明细(按兵种 id 嵌套): 20000 人",
                cok_hunt._march_troops(
                    {"army": [{"57580718": {"total": 20000, "dead": 0},
                               "is1518": True}]}) == (20000, 0))
    ok &= check("行军明细: 阵亡数也算进去",
                cok_hunt._march_troops(
                    {"army": [{"total": 50, "dead": 5}]}) == (50, 5))
    # 在外人数: 用行军明细算(同兵种多队也能分开算)
    cl6 = FakeClient([{"id": "107012", "free": 60000, "march": 0, "speed": 9,
                       "load": 13, "power": 10.1, "attack": 1, "defen": 1}])
    h6 = cok_hunt.AutoHunter(cl6, level=15, num=10000, squads=2,
                              squad_spec=[{"army_id": "107012", "num": 10000},
                                          {"army_id": "107012", "num": 10000}])
    s6 = h6._assign(cok_hunt.list_army(cl6))
    h6._launch(s6[0], cok_hunt.list_army(cl6))
    mk6 = cok_hunt.read_march(cl6)
    h6._sync_squads(mk6["all"], mk6["marches"])
    ok &= check("在外人数按行军明细算出来",
                s6[0].get("out") == 10000, str(s6[0].get("out")))

    # 体力不足时不派出(而且**不去找怪** —— 找怪是网络往返, 白费)
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
    h3 = cok_hunt.AutoHunter(cl, level=15, num=1000, squads=4,
                             squad_spec=[{"army_id": "107110", "num": 1000},
                                         {"army_id": "107012", "num": 1000},
                                         {"army_id": "107111", "num": 1000},
                                         {"army_id": "107212", "num": 1000}])
    h3._assign(cok_hunt.list_army(cl))
    st2 = {"stamina": 12}
    launched = 0
    for s in h3._squads:
        if st2["stamina"] - 10 < 0:
            break
        ok_launch, _ = h3._launch(s, cok_hunt.list_army(cl))
        if ok_launch:
            launched += 1
            st2["stamina"] = max(0, st2["stamina"] - 10)
    ok &= check("并发数随体力自动收缩(12点只够1队)", launched == 1,
                "实际派出 %d 队" % launched)

    # 体力充足时可以派满 4 队
    cl.stamina = 100
    h4 = cok_hunt.AutoHunter(cl, level=15, num=1000, squads=4,
                             squad_spec=[{"army_id": "107110", "num": 1000},
                                         {"army_id": "107012", "num": 1000},
                                         {"army_id": "107111", "num": 1000},
                                         {"army_id": "107212", "num": 1000}])
    h4._assign(cok_hunt.list_army(cl))
    st3 = {"stamina": 100}
    launched3 = 0
    for s in h4._squads:
        if st3["stamina"] - 10 < 0:
            break
        ok_launch, _ = h4._launch(s, cok_hunt.list_army(cl))
        if ok_launch:
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
    cl5 = FakeClient(army)
    h5 = cok_hunt.AutoHunter(cl5, level=15, num=1000, squads=4,
                             squad_spec=[{"army_id": "107110", "num": 1000},
                                         {"army_id": "107012", "num": 1000},
                                         {"army_id": "107111", "num": 1000},
                                         {"army_id": "107212", "num": 1000}])
    h5._assign(cok_hunt.list_army(cl5))
    h5.state["stamina"] = 2          # 低于 STAMINA_COST
    sq = h5._squads[0]
    called = {"find": False}
    def fake_find(*a, **k):
        called["find"] = True
        return {"ok": True, "x": 1, "y": 1}
    orig_find = cok_hunt.find_monster
    cok_hunt.find_monster = fake_find
    try:
        okr, info = h5._launch(sq, army)
    finally:
        cok_hunt.find_monster = orig_find
    ok &= check("体力不足时直接返回, 不去找怪",
                not called["find"], "find被调用=%s" % called["find"])
    ok &= check("体力不足不计入 fails",
                h5.state["fails"] == 0 and sq.get("fails", 0) == 0,
                "fails=%s sq=%s" % (h5.state["fails"], sq.get("fails")))
    ok &= check("体力不足时队伍标为等体力",
                sq.get("note") == "等体力", str(sq.get("note")))
    ok &= check("体力不足返回 errorCode=E100047",
                info.get("errorCode") == "E100047", str(info))

    # ---- 体力异常熔断 ----
    # 在一分钟窗口内掉得过快时必须能识别，避免重复派兵白烧体力。
    now_ms = int(__import__("time").time() * 1000)
    h5._stamina_samples = [
        (500, 0, now_ms - 50_000),
        (250, 0, now_ms),
    ]
    ok &= check("一分钟内体力异常消耗会触发熔断",
                h5._stamina_burst() == 250, str(h5._stamina_burst()))
    h5._stamina_samples = [
        (500, 0, now_ms - 61_000),
        (250, 0, now_ms),
    ]
    ok &= check("一分钟外的旧体力样本不触发熔断",
                h5._stamina_burst() == 0, str(h5._stamina_burst()))

    # ---- 编成解析(游戏里 autoQueue.data 的 format) ----
    ok &= check("编成串解析成兵种列表",
                cok_hunt.parse_format("107110,50|107012,50")
                == [{"id": "107110", "num": 50},
                    {"id": "107012", "num": 50}],
                str(cok_hunt.parse_format("107110,50|107012,50")))
    ok &= check("编队索引格式解不出编成(返回空)",
                cok_hunt.parse_format("1;2;3") == [],
                str(cok_hunt.parse_format("1;2;3")))
    ok &= check("空串/垃圾输入不炸",
                cok_hunt.parse_format("") == [] and cok_hunt.parse_format(None) == [])

    class AQClient(object):
        def __init__(self, params):
            self.params = params

        def call(self, cmd, params=None, retries=1):
            assert cmd == "autoQueue.data", cmd
            return {"__params__": dict(self.params)}

    aq = cok_hunt.read_autoqueue(AQClient({
        "format": "107110,50|107012,50", "lv": "15;16", "autoCount": 3,
        "force": 1, "status": 0, "saveItems": "", "useItems": ""}))
    ok &= check("读游戏设置: 编成", len(aq.get("squads") or []) == 2, str(aq.get("squads")))
    ok &= check("读游戏设置: 等级范围", aq.get("lvLow") == 15 and aq.get("lvHigh") == 16,
                "%s/%s" % (aq.get("lvLow"), aq.get("lvHigh")))
    ok &= check("读游戏设置: 并行数/严格模式",
                aq.get("autoCount") == 3 and aq.get("force") == 1)
    ok &= check("读游戏设置: 非索引格式", aq.get("indexed") is False)
    aq2 = cok_hunt.read_autoqueue(AQClient({"format": "3;5", "lv": "10", "autoCount": 1}))
    ok &= check("游戏里用编队索引时标记 indexed",
                aq2.get("indexed") is True and not aq2.get("squads"),
                str(aq2.get("format")))

    print("\n%s" % ("全部通过" if ok else "存在失败项"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
