#!/usr/bin/env python3
"""机会性测量: 服务端对 world.get 有累计限流, 只能"抓到"少量成功请求。

循环尝试, 每次成功后立刻打印:
  * 响应里到底有哪些字段(确认 x/y 回显)
  * 这次响应的**真实覆盖区**(所有带 uid 地块相对请求中心的偏移范围)
  * 响应回显的中心是否与请求一致
  * 同一个 uid 在这次响应里出现几次

用法:  python3 diag_cover.py [中心x] [中心y] [最大尝试次数]
"""
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "core"))

import cok_client  # noqa: E402
import cok_map  # noqa: E402

W = cok_map.WORLD_SIZE


def pt(i):
    n = int(i) - 1
    return (n % W, n // W)


def main():
    cx = int(sys.argv[1]) if len(sys.argv) > 1 else 531
    cy = int(sys.argv[2]) if len(sys.argv) > 2 else 931
    tries = int(sys.argv[3]) if len(sys.argv) > 3 else 30
    I = cok_map._I
    ok = 0
    for t in range(tries):
        try:
            c = cok_client.CokClient(timeout=25.0).connect()
            c.bin_handshake()
            c.login()
            for _ in range(2):
                try:
                    c.call("cmd.ping")
                except Exception:
                    pass
            try:
                r = c.call("world.get", {"x": I(cx), "y": I(cy), "type": I(0),
                                         "serverId": I(2223),
                                         "timeStamp": I(int(time.time()))})
            finally:
                try:
                    c.close()
                except Exception:
                    pass
        except Exception as e:
            print("  尝试%2d 失败 %s" % (t + 1, str(e)[:60]))
            time.sleep(4)
            continue

        ok += 1
        p = r.get("__params__") or {}
        print("\n=== 尝试 %d 成功 | mode=%s ===" % (t + 1, r.get("__mode__")))
        print("  响应字段: %s" % sorted(p.keys()))
        print("  回显 x=%s y=%s (请求的是 %d,%d)" % (
            p.get("x"), p.get("y"), cx, cy))
        pts = cok_map._parse_points(p)
        withuid = [t2 for t2 in pts if t2.get("uid")]
        print("  地块 %d, 带 uid %d" % (len(pts), len(withuid)))
        if withuid:
            dxs = sorted(pt(int(t2["i"]))[0] - cx for t2 in withuid)
            dys = sorted(pt(int(t2["i"]))[1] - cy for t2 in withuid)
            print("  偏移 dx: %d ~ %d   dy: %d ~ %d" % (
                dxs[0], dxs[-1], dys[0], dys[-1]))
            cnt = {}
            for t2 in withuid:
                cnt[str(t2["uid"])] = cnt.get(str(t2["uid"]), 0) + 1
            multi = {k: v for k, v in cnt.items() if v > 1}
            print("  同一 uid 出现多次的: %d 个" % len(multi))
            for k, v in list(multi.items())[:5]:
                print("     uid=%s 出现 %d 次" % (k, v))
        if ok >= 2:
            break
        time.sleep(4)
    return 0


if __name__ == "__main__":
    sys.exit(main())
