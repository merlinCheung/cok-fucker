#!/usr/bin/env python3
"""探测 6: 搜索次数限制 + 不用 res.tile.find 定位巨型狮鹫地块。

问题: res.tile.find 每日次数有限(已用完), 而自动打怪必须能**反复**找到 boss。
所以要搞清:
  1. 剩余次数从哪读(maxSearchCount / resSearchCount 在哪下发)
  2. world.get 能不能直接看到 boss 地块(monsterId=902113 等)
  3. 有没有别的命令能列出世界上的 boss
"""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import cok_accounts as accounts  # noqa: E402
import cok_hunt  # noqa: E402
from cok_client import CokClient  # noqa: E402
from cok_sfs import TypedInt, SFS_INT  # noqa: E402


def I(v):
    return TypedInt(int(v), SFS_INT)


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

    # 1. dataconfig 里搜索次数相关
    r = c.call("login.dataconfig")
    p = r.get("__params__") or {}
    dc = p.get("dataConfig")
    if isinstance(dc, str):
        dc = json.loads(dc)
    print("\n=== dataConfig 里含 search / find / count 的键 ===")
    for k in sorted(dc.keys()):
        if any(s in k.lower() for s in ("search", "find", "vip", "count", "boss", "rally")):
            v = dc[k]
            s = json.dumps(v, ensure_ascii=False)
            print("  %-28s %s" % (k, s[:160]))

    # 2. login 响应里的 maxSearchCount / worldConfig
    print("\n=== 登录推送/响应里的 worldConfig ===")
    try:
        r2 = c.call("login.other")
        p2 = r2.get("__params__") or {}
        wc = p2.get("worldConfig")
        if isinstance(wc, dict):
            for k in sorted(wc.keys()):
                if any(s in k.lower() for s in ("search", "find", "boss", "rally", "vip")):
                    print("  worldConfig.%-24s %r" % (k, wc[k]))
        else:
            print("  worldConfig 非 dict:", str(wc)[:200])
        print("  login.other 顶层键:", sorted(p2.keys())[:40])
    except Exception as e:  # noqa: BLE001
        print("[!] login.other 失败:", str(e)[:160])

    # 3. world.get 看 boss 地块 —— 扫之前搜到的坐标附近
    print("\n=== world.get 扫 boss 坐标附近(找 monsterId 字段) ===")
    for (x, y) in ((1002, 668), (978, 693), (1014, 689), (1019, 692)):
        try:
            r3 = c.call("world.get", {"x": I(x), "y": I(y), "type": I(0),
                                      "serverId": I(2223),
                                      "timeStamp": I(int(time.time()))}, retries=0)
            p3 = r3.get("__params__") or {}
            if p3.get("errorCode"):
                print("  (%d,%d) errorCode=%s" % (x, y, p3.get("errorCode")))
                continue
            pts = p3.get("points") or []
            tiles = []
            for it in pts:
                try:
                    got = json.loads(it) if isinstance(it, str) else it
                except Exception:
                    continue
                if isinstance(got, list):
                    tiles += [g for g in got if isinstance(g, dict)]
                elif isinstance(got, dict):
                    tiles.append(got)
            print("  (%d,%d) 地块数=%d  键样例=%s"
                  % (x, y, len(tiles), sorted(tiles[0].keys()) if tiles else "-"))
            for t in tiles:
                s = json.dumps(t, ensure_ascii=False)
                if "90211" in s or "650066" in s or "m" in t and str(t.get("m")).startswith("902"):
                    print("    ★", s[:400])
            if tiles:
                print("    样例:", json.dumps(tiles[0], ensure_ascii=False)[:400])
        except Exception as e:  # noqa: BLE001
            print("  (%d,%d) 失败: %s" % (x, y, str(e)[:140]))
        time.sleep(0.4)

    # 4. 试别的 boss 列表命令
    print("\n=== 试列出世界 boss 的命令 ===")
    for cmd, params in (("world.get.monster", {}),
                        ("worldboss", {"op": 0, "type": 16}),
                        ("push.world.boss", {}),
                        ("world.get", {"x": I(1002), "y": I(668), "type": I(1),
                                       "serverId": I(2223), "timeStamp": I(int(time.time()))})):
        try:
            rr = c.call(cmd, params)
            print("  %s -> %s" % (cmd, json.dumps(rr.get("__params__") or {},
                                                  ensure_ascii=False)[:400]))
        except Exception as e:  # noqa: BLE001
            print("  %s 失败: %s" % (cmd, str(e)[:120]))

    c.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
