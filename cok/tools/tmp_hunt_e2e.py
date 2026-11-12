#!/usr/bin/env python3
"""自动打怪**真机端到端**验证(2026-11-09)。

用真实游戏服跑一遍 AutoHunter, 检查:
  1. 设 5 队 -> 真的开 5 队(同兵种可以拆多队)
  2. 每队兵力按用户填的上限, 库存不够时按库存摊薄
  3. **行军 uuid 判回**: 部队没到家不会被判回来(不会重复派队烧体力)
  4. 体力消耗速率正常(没有"疯狂重复派出")

用法: python3 cok/tools/tmp_hunt_e2e.py <gameUid> [squads] [num] [maxKills]
"""
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "core"))
import cok_hunt as H                       # noqa: E402
from cok_client import CokClient, account_lock, apply_account_types  # noqa: E402
import cok_accounts as cas                 # noqa: E402

uid = sys.argv[1] if len(sys.argv) > 1 else "351542128002216"
squads = int(sys.argv[2]) if len(sys.argv) > 2 else 5
num = int(sys.argv[3]) if len(sys.argv) > 3 else 20000
max_kills = int(sys.argv[4]) if len(sys.argv) > 4 else 3
level = int(sys.argv[5]) if len(sys.argv) > 5 else 1

acc = apply_account_types(dict(cas.get_account(uid)))
cl = CokClient(timeout=25, account=acc)

events = []


def on_event(kind, payload):
    events.append((kind, payload))
    st = payload.get("squads") or []
    if kind in ("tick", "start", "done", "stopped"):
        desc = " ".join(
            "#%d %s %s/%s %s" % (s.get("slot"), s.get("army_id"),
                                  s.get("num"), s.get("out"), s.get("state"))
            for s in st)
        print("[%s] %s | kills=%s stam=%s | %s"
              % (kind, payload.get("note", "")[:60], payload.get("kills"),
                 payload.get("stamina"), desc), flush=True)


with account_lock(timeout=5, purpose="probe", key=uid):
    cl.connect()
    cl.bin_handshake()
    cl.login()
    mk = H.read_march(cl)
    print("库存:", [(a["id"], a["free"], a["power"]) for a in mk["army"]], flush=True)
    plan = H.plan_squads(mk["army"], num, squads)
    print("编排:", plan["squads"], "队 x", plan["num"], "人 short=%s %s"
          % (plan["short"], plan["note"]), flush=True)
    print("     ", [(s["army_id"], s["num"]) for s in plan["slots"]], flush=True)
    spec = [{"army_id": s["army_id"], "num": s["num"]} for s in plan["slots"]]

    st0 = H.read_stamina(cl)
    print("起始体力:", st0, flush=True)

    hunter = H.AutoHunter(cl, level=level, num=num, squads=squads,
                          squad_spec=spec, max_kills=max_kills,
                          on_event=on_event, poll=2.0)
    t0 = time.time()
    hunter.run()
    dur = time.time() - t0
    st1 = H.read_stamina(cl)
    print("\n=== 结果 ===", flush=True)
    print("用时 %.0f 秒, 击杀 %d, 体力 %s -> %s (消耗 %s)"
          % (dur, hunter.state["kills"], st0.get("stamina"), st1.get("stamina"),
             (st0.get("stamina") or 0) - (st1.get("stamina") or 0)), flush=True)
    print("失败次数:", hunter.state["fails"], flush=True)
    for s in hunter.state["squads"]:
        print("  队%d %s %s人 状态=%s 击杀=%d 在外=%s uuid=%s"
              % (s.get("slot"), s.get("army_id"), s.get("num"), s.get("state"),
                 s.get("kills"), s.get("out"), (s.get("uuid") or "")[:8]), flush=True)
cl.close()
