#!/usr/bin/env python3
"""巨型狮鹫区域边界探测(第 2 轮): 往外扩一圈, 并**自动重连**。

⚠️ 实测(2026-11-02): 游戏服在**连续约 70 次 world.get 之后会主动断开连接**
   ("连接被服务端关闭(已收 0/3 字节)"), 之后重试全是 Broken pipe —— 必须重建连接。

用法: python3 probe_boss_zone2.py [account]
"""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

WIN_X = 24
WIN_Y = 25


class Session:
    """带自动重连的 world.get 会话。"""

    def __init__(self, account):
        from cok_client import CokClient
        self.account = account
        self.cl = None
        self.n = 0

    def open(self):
        from cok_client import CokClient
        self.cl = CokClient(account=self.account, timeout=25.0).connect()
        self.cl.bin_handshake()
        self.cl.login()
        for _ in range(2):
            try:
                self.cl.call("cmd.ping")
            except Exception:
                pass
        return self

    def fetch(self, x, y):
        from cok_rally import fetch_area
        for attempt in range(3):
            try:
                self.n += 1
                return fetch_area(self.cl, x, y)
            except Exception as e:  # noqa: BLE001
                print("    连接断了(%s), 重连后重试" % e)
                try:
                    self.cl.close()
                except Exception:
                    pass
                time.sleep(1.5)
                self.open()
        return []


def main():
    from cok_accounts import get_account
    acc = get_account(sys.argv[1] if len(sys.argv) > 1 else "<uid-main>")

    path = os.path.join(HERE, "boss-zone.json")
    data = json.load(open(path)) if os.path.exists(path) else {"bbox": [], "tiles": {}}
    tiles = data.get("tiles") or {}
    print("已有 %d 只" % len(tiles))

    # 已扫过的区域(第 1 轮): x 894..1134 / y 595..795
    # 这轮往外扩: x 846..1182 / y 556..807
    xs = list(range(858, 1179, WIN_X))
    ys = list(range(563, 803, WIN_Y))
    done = set()
    for x in range(906, 1123, WIN_X):
        for y in range(608, 784, WIN_Y):
            done.add((x, y))
    todo = [(x, y) for y in ys for x in xs if (x, y) not in done]
    print("待扫 %d 个中心" % len(todo))

    sess = Session(acc).open()
    t0 = time.time()
    try:
        for n, (cx, cy) in enumerate(todo, 1):
            pts = sess.fetch(cx, cy)
            nb = 0
            for t in pts:
                if int(t.get("t") or 0) != 15:
                    continue
                i = int(t.get("i") or 0)
                if not i or str(i) in tiles:
                    continue
                m = i - 1
                tiles[str(i)] = {
                    "x": m % 1201, "y": m // 1201,
                    "monsterId": str(t.get("t1") or ""),
                    "hp": t.get("mchp"), "maxHp": t.get("mmhp"),
                    "st": t.get("st"), "rt": t.get("rt"),
                }
                nb += 1
            if nb:
                print("  [%2d/%d] (%4d,%4d) +%d -> 共 %d 只 (%.0fs, 已发 %d 次)"
                      % (n, len(todo), cx, cy, nb, len(tiles), time.time() - t0, sess.n))
            time.sleep(0.2)
    finally:
        try:
            sess.cl.close()
        except Exception:
            pass

    xs2 = [v["x"] for v in tiles.values()]
    ys2 = [v["y"] for v in tiles.values()]
    bbox = (min(xs2), max(xs2), min(ys2), max(ys2))
    print("\n共 %d 只  bbox x %d..%d  y %d..%d" % (len(tiles), *bbox))
    from collections import Counter
    print("按 monsterId:", Counter(v["monsterId"] for v in tiles.values()))
    data["bbox"] = list(bbox)
    data["tiles"] = tiles
    with open(path, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    print("已写入", path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
