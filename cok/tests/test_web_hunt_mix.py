#!/usr/bin/env python3
"""网页层「自动打怪混编 + 打怪击杀计入任务达成明细」的单元测试(零消耗)。

覆盖:
  * `_auto_squad_spec(num, squads, mix)` 返回**新格式** spec:
    `[{"troops":[{army_id,num}, ...]}]` —— 一支队 = 一个编成(可多兵种)
  * `mix>=2` 时每队带多个**同类**兵种(跨类会被服务端拒)
  * `_record_hunt_kills()` 按**增量**记账(不把累计值反复累加)
  * 打怪击杀以 `hunt_kills` 记进"任务达成明细", 面板 label = "打怪击杀",
    且**不记明细**(details 为空)

跑法:
    python3 test_web_hunt_mix.py
"""

import argparse
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "core"))
sys.path.insert(0, os.path.join(HERE, "..", "tools"))

os.environ['COK_ACCOUNT_LOCK_FILE'] = os.path.join(
    tempfile.gettempdir(), 'cok-test-webmix-%d.lock' % os.getpid())
import cok_web  # noqa: E402
import cok_hunt  # noqa: E402


def make_args(**over):
    a = argparse.Namespace(
        host="127.0.0.1", port=8771, account_device=True, account=None,
        interval=300, timeout=60.0, webhook=None, webhook_type="generic",
        alert_rules=list(cok_web.D.ALL_RULES), autoshield=False,
        speedup_item="200201", speedup_count=1, speedup_queue_type=1,
        shield_slot=1, shield_cover_old=1, shield_cooldown=600.0,
        shield_trigger=[], shield_trigger_force=[], persistent=False,
        watch=list(cok_web.D.WATCHERS.keys()), once=False, retry_delay=10.0,
        claim=False, claim_limit=5, claim_max_total=20, auto_sign=False,
        speedup=False, speedup_gold=False, log=None, json=False,
    )
    for k, v in over.items():
        setattr(a, k, v)
    return a


class FakeDaemon(object):
    def __init__(self, args, client=None):
        self.args = args
        self.client = client
        self.emitted = []

    def ctx(self):
        return {"today": 1, "month": 1, "now": 0, "date": "2026-11-09"}

    def emit(self, kind, payload):
        self.emitted.append((kind, payload))


class FakeClient(object):
    """只回 army 清单的假客户端(够 `_auto_squad_spec` 用)。"""

    def __init__(self, army):
        self.army = army

    def call(self, cmd, params=None, retries=1):
        if cmd == "world.user.march":
            return {"__params__": {"army": [dict(a) for a in self.army],
                                   "m": []}}
        raise AssertionError("未预期的命令 %s" % cmd)


def check(name, cond, detail=""):
    print("[%s] %s%s" % ("PASS" if cond else "FAIL", name,
                         ("  — " + detail) if detail else ""))
    return bool(cond)


ARMY = [
    {"id": "107110", "free": 100000, "march": 0, "speed": 9, "load": 13,
     "power": 10.8, "attack": 1, "defen": 1},
    {"id": "107012", "free": 90000, "march": 0, "speed": 9, "load": 13,
     "power": 10.1, "attack": 1, "defen": 1},
    {"id": "57580718", "free": 500000, "march": 0, "speed": 9, "load": 13,
     "power": 12.0, "attack": 1, "defen": 1},
]


def main():
    ok = True
    tmp = tempfile.mkdtemp(prefix="cokweb-mix-")
    try:
        cok_web.Engine.SETTINGS_FILE = os.path.join(tmp, "web-settings.json")
        args = make_args()
        eng = cok_web.Engine(args)
        eng.daemon = FakeDaemon(args, FakeClient(ARMY))
        # 统计账本写到临时目录, 不污染真实账号数据
        eng._data_dir = lambda: tmp

        # ------------------------------------------------------------------
        # 1) _auto_squad_spec: 新格式 + mix
        # ------------------------------------------------------------------
        spec1 = eng._auto_squad_spec(1000, 4, 1)
        ok &= check("_auto_squad_spec: 返回新格式 spec",
                    bool(spec1.get("spec")) and "troops" in spec1["spec"][0],
                    str(spec1.get("spec"))[:120])
        ok &= check("_auto_squad_spec: mix=1 每队一种兵",
                    all(len(s["troops"]) == 1 for s in spec1["spec"]),
                    str([len(s["troops"]) for s in spec1["spec"]]))
        spec2 = eng._auto_squad_spec(1000, 4, 2)
        n_troops = [len(s["troops"]) for s in spec2["spec"]]
        ok &= check("_auto_squad_spec: mix=2 每队最多 2 个兵种",
                    all(t <= 2 for t in n_troops), str(n_troops))
        ok &= check("_auto_squad_spec: mix=2 至少有一队混编了 2 个兵种",
                    any(t == 2 for t in n_troops), str(n_troops))
        ok &= check("_auto_squad_spec: 只有一种兵的兵种不会被硬凑",
                    # 活动兵只有 1 种 -> 活动兵那队仍然是 1 个兵种
                    all(len(s["troops"]) == 1 for s in spec2["spec"]
                        if cok_hunt._army_class(s["troops"][0]["army_id"]) == "act"),
                    str([s["troops"] for s in spec2["spec"]]))
        ok &= check("_auto_squad_spec: mix=2 不跨类混编",
                    all(len(set(cok_hunt._army_class(t["army_id"])
                                for t in s["troops"])) == 1
                        for s in spec2["spec"]))
        ok &= check("_auto_squad_spec: spec 里每项都有 army_id/num",
                    all(all(t.get("army_id") and int(t.get("num") or 0) > 0
                            for t in s["troops"]) for s in spec2["spec"]))

        # ------------------------------------------------------------------
        # 2) 打怪击杀计入任务达成明细(增量记账)
        # ------------------------------------------------------------------
        eng._hunt_kills_seen = 0
        d1 = eng._record_hunt_kills(3)
        ok &= check("击杀 3 -> 记入 3", d1 == 3, str(d1))
        d2 = eng._record_hunt_kills(3)
        ok &= check("同样的累计值不重复记", d2 == 0, str(d2))
        d3 = eng._record_hunt_kills(5)
        ok &= check("累计值涨到 5 -> 只记增量 2", d3 == 2, str(d3))
        events = [e for e in (eng.task_stats.get("events") or [])
                  if e.get("kind") == "hunt_kills"]
        ok &= check("账本里有 hunt_kills 记录", len(events) == 2, str(len(events)))
        total = sum(int(e.get("count") or 0) for e in events)
        ok &= check("账本里的击杀总数 = 5", total == 5, str(total))
        ok &= check("只记累计数, 不记明细(detail 为空)",
                    all(not e.get("detail") for e in events),
                    str([e.get("detail") for e in events]))

        # 面板视图
        view = eng._task_stats_view()
        day_rows = {r["key"]: r for r in (view["periods"]["day"]["breakdown"])}
        row = day_rows.get("hunt_kills")
        ok &= check("面板有「打怪击杀」这一行", row is not None, str(list(day_rows)))
        if row:
            ok &= check("面板 label = 打怪击杀", row["label"] == "打怪击杀", row["label"])
            ok &= check("面板显示累计击杀 5", row["count"] == 5, str(row["count"]))
            ok &= check("面板不展开明细", not row.get("details"), str(row.get("details")))

        # ------------------------------------------------------------------
        # 3) 重新开一轮打怪: 计数从 0 重新开始(不接着上一轮累加)
        # ------------------------------------------------------------------
        eng._hunt_kills_seen = 0
        d4 = eng._record_hunt_kills(2)
        ok &= check("新一轮打怪: 击杀数从头记", d4 == 2, str(d4))
        total2 = sum(int(e.get("count") or 0)
                     for e in (eng.task_stats.get("events") or [])
                     if e.get("kind") == "hunt_kills")
        ok &= check("两轮合计 7", total2 == 7, str(total2))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print()
    if ok:
        print("全部通过")
        return 0
    print("有失败项")
    return 1


if __name__ == "__main__":
    sys.exit(main())
