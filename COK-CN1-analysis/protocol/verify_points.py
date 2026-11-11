#!/usr/bin/env python3
"""抽样复核索引里的坐标: 逐个回查, 看服务端是否还说"他"在那。

用法:
  python3 verify_points.py            # 抽 30 个真人玩家复核
  python3 verify_points.py 100        # 抽 100 个
  python3 verify_points.py 100 <uid-main>   # 指定 uid

原理: 索引里记了某玩家的坐标 (x,y) —— 如果那个坐标现在还是他,
说明记录是对的; 如果那个点已经站着别人, 说明这条记录过期/错位。

每次 world.get 覆盖中心 ±12 格, 而查的正是他本人的位置, 所以
"查得到"= "记录正确"。
"""
import os
import random
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import cok_client  # noqa: E402
import cok_map  # noqa: E402

_NPC = re.compile(r"#\d+$")
I = cok_map._I


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 30
    only = sys.argv[2] if len(sys.argv) > 2 else None

    idx = cok_map.load_index()
    players = idx.get("players") or {}
    if only:
        cands = [(only, players[only])] if only in players else []
    else:
        reals = [(u, v) for u, v in players.items()
                 if not _NPC.search(str(v.get("name") or ""))]
        random.seed(20261026)
        cands = random.sample(reals, min(n, len(reals)))
    if not cands:
        print("没有可复核的条目")
        return 1
    print("复核 %d 个条目(只查真人玩家, 每次一个请求)\n" % len(cands))

    ok = miss = gone = 0
    with cok_client.account_lock(timeout=60.0, purpose="verify-points"):
        c = cok_client.CokClient(timeout=25.0).connect()
        c.bin_handshake()
        c.login()
        for _ in range(2):
            try:
                c.call("cmd.ping")
            except Exception:
                pass
        for uid, rec in cands:
            x, y = rec.get("x"), rec.get("y")
            if x is None or y is None:
                continue
            got = None
            for attempt in range(3):
                try:
                    r = c.call("world.get", {"x": I(x), "y": I(y), "type": I(0),
                                             "serverId": I(2223),
                                             "timeStamp": I(int(time.time()))})
                    p = r.get("__params__") or {}
                    pts = cok_map._parse_points(p)
                    hit = [t for t in pts
                           if t.get("uid") and str(t.get("uid")) == str(uid)]
                    got = hit[0] if hit else None
                    break
                except Exception:
                    time.sleep(0.4)
            if got is None:
                gone += 1
                print("  ✗ %-20s %-14s 记录的 (%4d,%4d) 现在**没有他**" % (
                    uid, (rec.get("name") or "")[:12], x, y))
            else:
                n2 = int(got.get("i")) - 1
                nx, ny = n2 % 1201, n2 // 1201
                if nx == x and ny == y:
                    ok += 1
                    print("  ✓ %-20s %-14s (%4d,%4d) 仍然正确" % (
                        uid, (rec.get("name") or "")[:12], x, y))
                else:
                    miss += 1
                    print("  ✗ %-20s %-14s 记录 (%4d,%4d) 但服务端说他在 (%4d,%4d)" % (
                        uid, (rec.get("name") or "")[:12], x, y, nx, ny))
            time.sleep(0.2)
        try:
            c.close()
        except Exception:
            pass

    total = ok + miss + gone
    print("\n复核结果: 正确 %d / 位置不符 %d / 该点没有他 %d  —— 正确率 %s" % (
        ok, miss, gone, ("%.1f%%" % (100.0 * ok / total)) if total else "-"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
