#!/usr/bin/env python3
"""**混编出征**的真机端到端验证(2026-11-09)。

用真实游戏服跑一遍 AutoHunter(mix=2), 检查:
  1. 一支队伍带**多个同类兵种**能真的出征成功(服务端接受 mixed soldiers)
  2. 行军 uuid 判回: 部队到家才判"已回来"(不会重复派队烧体力)
  3. 判回后清空 uuid -> 同一队可以**连续再次出征**
  4. 库存按各兵种分别扣, 回来后各自还原
  5. 击杀数被记进"任务达成明细"(只记累计数, 不记明细)

⚠️ 会真实消耗士兵与体力 —— 故意用**最小规模**(1 队 / 100 人 / 1 级怪)。

用法: python3 probe_hunt_mix_e2e.py <gameUid> [mix] [num] [maxKills] [level]
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
import tempfile
import time

_C = os.path.join(HERE, "..", "..", "core")
sys.path.insert(0, _C)
os.environ['COK_ACCOUNT_LOCK_FILE'] = os.path.join(
    tempfile.gettempdir(), 'cok-probe-mix-e2e-%d.lock' % os.getpid())

import cok_hunt as H                                     # noqa: E402
from cok_client import CokClient, account_lock, apply_account_types  # noqa: E402
import cok_accounts as cas                               # noqa: E402

uid = sys.argv[1] if len(sys.argv) > 1 else "<uid-other>"
mix = int(sys.argv[2]) if len(sys.argv) > 2 else 2
num = int(sys.argv[3]) if len(sys.argv) > 3 else 100
max_kills = int(sys.argv[4]) if len(sys.argv) > 4 else 2
level = int(sys.argv[5]) if len(sys.argv) > 5 else 1

acc = apply_account_types(dict(cas.get_account(uid)))
cl = CokClient(timeout=25, account=acc)

events = []


def on_event(kind, payload):
    events.append((kind, payload))
    if kind in ("tick", "start", "done", "stopped", "error"):
        st = payload.get("squads") or []
        desc = " ".join(
            "#%d[%s]%s人/在外%s/%s" % (s.get("slot"),
                                      (s.get("name") or "")[:26],
                                      s.get("num"), s.get("out"), s.get("state"))
            for s in st)
        print("[%s] kills=%s stam=%s | %s"
              % (kind, payload.get("kills"), payload.get("stamina"), desc),
              flush=True)


with account_lock(timeout=5, purpose="probe", key=uid):
    cl.connect()
    cl.bin_handshake()
    cl.login()
    mk = H.read_march(cl)
    print("库存:", [(a["id"], a["free"], a.get("power")) for a in mk["army"]],
          flush=True)
    plan = H.plan_squads(mk["army"], num, 1, mix)
    print("编排: %d 队 x %d 人 mix=%s short=%s"
          % (plan["squads"], plan["num"], mix, plan["short"]), flush=True)
    for i, s in enumerate(plan["slots"]):
        print("   队%d %s  types=%d  troops=%s"
              % (i + 1, s["name"], s.get("types") or 1,
                 [(t["army_id"], t["num"]) for t in s["troops"]]), flush=True)
    # 新格式 spec: 一支队 = 一个编成(可多兵种)
    spec = [{"troops": [{"army_id": str(t["army_id"]), "num": int(t["num"])}
                        for t in s["troops"]]} for s in plan["slots"]]

    before = {a["id"]: int(a["free"]) for a in mk["army"]}
    st0 = H.read_stamina(cl)
    print("起始体力:", st0, flush=True)

    hunter = H.AutoHunter(cl, level=level, num=num, squads=1,
                          squad_spec=spec, max_kills=max_kills,
                          mix=mix, on_event=on_event, poll=2.0)
    t0 = time.time()
    hunter.run()
    dur = time.time() - t0

    mk2 = H.read_march(cl)
    after = {a["id"]: int(a["free"]) for a in mk2["army"]}
    st1 = H.read_stamina(cl)
    print("\n=== 结果 ===", flush=True)
    print("用时 %.0f 秒, 击杀 %d, 体力 %s -> %s (消耗 %s)"
          % (dur, hunter.state["kills"], st0.get("stamina"), st1.get("stamina"),
             (st0.get("stamina") or 0) - (st1.get("stamina") or 0)), flush=True)
    print("失败次数:", hunter.state["fails"], flush=True)
    for s in hunter.state["squads"]:
        print("  队%d %s %s人 状态=%s 击杀=%d uuid=%s"
              % (s.get("slot"), s.get("name"), s.get("num"), s.get("state"),
                 s.get("kills"), (s.get("uuid") or "")[:8]), flush=True)
    print("库存变化:", {k: (before.get(k), after.get(k))
                        for k in set(before) | set(after)
                        if before.get(k) != after.get(k)}, flush=True)
    # ---- 击杀增量记账(和网页层同一套逻辑) ----
    seen = {"n": 0}
    print("\n=== 击杀记账 ===", flush=True)
    for kind, payload in events:
        k = int(payload.get("kills") or 0)
        if k > seen["n"]:
            print("  新增击杀 %d (累计 %d)" % (k - seen["n"], k), flush=True)
            seen["n"] = k
    print("  记入任务达成明细的击杀总数 =", seen["n"], flush=True)
cl.close()
