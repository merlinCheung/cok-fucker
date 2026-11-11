#!/usr/bin/env python3
"""探测 3: dataConfig.world_rally 全量 + 首领怪地块(world.get.detail / get.monster)。"""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import cok_accounts as accounts  # noqa: E402
from cok_client import CokClient  # noqa: E402


def main():
    key = sys.argv[1] if len(sys.argv) > 1 else "<uid-main>"
    acc = accounts.get_account(key)
    c = CokClient(account=acc, timeout=25.0).connect()
    c.bin_handshake()
    c.login()
    for _ in range(2):
        try:
            c.call("cmd.ping")
        except Exception:
            pass

    r = c.call("login.dataconfig")
    p = r.get("__params__") or {}
    dc = p.get("dataConfig")
    if isinstance(dc, str):
        dc = json.loads(dc)
    print("\n=== dataConfig.world_rally ===")
    print(json.dumps(dc.get("world_rally"), ensure_ascii=False)[:3000])
    print("\n=== dataConfig.boss_decr / boss_max_member / arrange_arms ===")
    for k in ("boss_decr", "boss_max_member", "arrange_arms", "camp_limit",
              "staminaCostPerTime", "city_barracks_userPower"):
        if k in dc:
            print("  %s = %r" % (k, dc[k]))

    # 首领怪地块: 用 res.tile.find 拿到的坐标换算 index, 再 world.get.detail
    import cok_hunt
    for lv in (12, 21, 30):
        rr = c.call("res.tile.find", {"type": 7, "level": lv, "NoRecord": 1})
        pp = rr.get("__params__") or {}
        x, y = pp.get("x"), pp.get("y")
        idx = cok_hunt.point_index(x, y)
        print("\n--- 活动怪 lv=%d 坐标(%s,%s) index=%s" % (lv, x, y, idx))
        for cmd, params in (("world.get.detail", {"point": idx, "serverId": 2223}),
                            ("world.get.monster", {"point": idx}),
                            ("world.get.monster", {"index": idx}),
                            ("world.get.monster", {"type": 7, "level": lv})):
            try:
                r2 = c.call(cmd, params)
                p2 = r2.get("__params__") or {}
                print("  %s %s ->" % (cmd, json.dumps(params, ensure_ascii=False)),
                      json.dumps(p2, ensure_ascii=False)[:600])
            except Exception as e:  # noqa: BLE001
                print("  [%s] %s 失败: %s" % (cmd, json.dumps(params, ensure_ascii=False),
                                             str(e)[:120]))

    # 看看 world.get 一整片里 activity boss 地块长什么样(用搜索到的坐标附近)
    print("\n=== world.get 原始 points 结构(取 activity 附近) ===")
    rr = c.call("res.tile.find", {"type": 7, "level": 12, "NoRecord": 1})
    pp = rr.get("__params__") or {}
    x, y = pp.get("x"), pp.get("y")
    r3 = c.call("world.get", {"x": x, "y": y, "type": 0, "serverId": 2223,
                              "timeStamp": int(time.time())})
    p3 = r3.get("__params__") or {}
    print("  响应键:", sorted(p3.keys()))
    pts = p3.get("points") or []
    print("  points 条数:", len(pts), "类型:", type(pts[0]).__name__ if pts else "-")
    for it in pts[:2]:
        s = it if isinstance(it, str) else json.dumps(it, ensure_ascii=False)
        print("   ", s[:800])

    c.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
