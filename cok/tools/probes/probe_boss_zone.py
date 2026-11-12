#!/usr/bin/env python3
"""一次性探测: 把巨型狮鹫刷新区域的**边界**探清楚, 存成 boss-zone.json。

用法: python3 probe_boss_zone.py [account]
"""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

# world.get 覆盖窗口(实测): x 中心 ±12, y 中心 -13~+11 -> 24 x 25
WIN_X = 24
WIN_Y = 25


def sweep():
    from cok_accounts import get_account
    from cok_client import CokClient
    import cok_rally as R

    acc = get_account(sys.argv[1] if len(sys.argv) > 1 else "<uid-main>")
    cl = CokClient(account=acc, timeout=25.0).connect()
    cl.bin_handshake()
    cl.login()
    for _ in range(2):
        try:
            cl.call("cmd.ping")
        except Exception:
            pass

    # 大范围网格: x 894..1134 / y 595..795
    xs = list(range(906, 1123, WIN_X))
    ys = list(range(608, 784, WIN_Y))
    grid = [(x, y) for y in ys for x in xs]
    print("网格 %d 个中心 (%d 列 x %d 行)" % (len(grid), len(xs), len(ys)))

    seen = {}
    t0 = time.time()
    for n, (cx, cy) in enumerate(grid, 1):
        for attempt in range(3):
            try:
                tiles = R.fetch_area(cl, cx, cy)
                break
            except Exception as e:  # noqa: BLE001
                if attempt == 2:
                    print("  [%d] (%d,%d) 三次都失败: %s" % (n, cx, cy, e))
                    tiles = []
                else:
                    print("  [%d] (%d,%d) 重试 %d: %s" % (n, cx, cy, attempt + 1, e))
                    time.sleep(1.0)
        nb = 0
        for t in tiles:
            if int(t.get("t") or 0) != 15:
                continue
            i = int(t.get("i") or 0)
            if not i or i in seen:
                continue
            seen[i] = t
            nb += 1
        if nb:
            print("  [%2d/%d] (%4d,%4d) +%d -> 共 %d 只 (%.0fs)"
                  % (n, len(grid), cx, cy, nb, len(seen), time.time() - t0))
        time.sleep(0.2)
    cl.close()
    return seen


def main():
    seen = sweep()
    out = {}
    for i, t in seen.items():
        n = i - 1
        out[str(i)] = {
            "x": n % 1201,
            "y": n // 1201,
            "monsterId": str(t.get("t1") or ""),
            "hp": t.get("mchp"),
            "maxHp": t.get("mmhp"),
            "st": t.get("st"),
            "rt": t.get("rt"),
        }
    xs = [v["x"] for v in out.values()]
    ys = [v["y"] for v in out.values()]
    bbox = (min(xs), max(xs), min(ys), max(ys)) if xs else (0, 0, 0, 0)
    print("\n共 %d 只巨型狮鹫" % len(out))
    print("bbox x %d..%d  y %d..%d" % bbox)
    from collections import Counter
    print("按 monsterId:", Counter(v["monsterId"] for v in out.values()))
    path = os.path.join(HERE, "boss-zone.json")
    with open(path, "w") as f:
        json.dump({"bbox": list(bbox), "tiles": out}, f, ensure_ascii=False, indent=1)
    print("已写入", path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
