#!/usr/bin/env python3
"""探测 2: 集结时间配置(world_rally_k1..k4) + 首领怪地块细节。"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import cok_accounts as accounts  # noqa: E402
from cok_client import CokClient  # noqa: E402


def walk_rally(obj, path="", out=None, depth=0):
    """在任意嵌套结构里找 world_rally / boss_decr / worldConfig 相关键。"""
    if out is None:
        out = []
    if depth > 6:
        return out
    if isinstance(obj, dict):
        for k, v in obj.items():
            p = "%s.%s" % (path, k) if path else str(k)
            lk = str(k).lower()
            if ("rally" in lk or "boss_decr" in lk or lk == "worldconfig"
                    or "stamina" in lk or "stamine" in lk):
                out.append((p, v if not isinstance(v, (dict, list)) else "<%s>" % type(v).__name__))
            walk_rally(v, p, out, depth + 1)
    elif isinstance(obj, list):
        for i, v in enumerate(obj[:50]):
            walk_rally(v, "%s[%d]" % (path, i), out, depth + 1)
    return out


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
    print("\n=== dataConfig 类型:", type(dc).__name__)
    if isinstance(dc, str):
        try:
            dc = json.loads(dc)
        except Exception as e:
            print("  解析失败:", e)
            dc = {}
    if isinstance(dc, dict):
        print("  顶层键(%d):" % len(dc), sorted(dc.keys())[:60])
        for k in ("worldConfig", "world_rally_k1", "world_rally_k2",
                  "world_rally_k3", "world_rally_k4"):
            if k in dc:
                print("  ★ %s = %r" % (k, dc[k]))
        hits = walk_rally(dc)
        print("  rally/boss 相关命中 %d 条:" % len(hits))
        for path, v in hits[:40]:
            print("    %s = %r" % (path, v))
    else:
        print("  dataConfig 非 dict:", str(dc)[:300])

    # 首领怪地块细节
    for lv, (x, y) in ((12, (1002, 668)), (21, (1040, 692)), (30, (1019, 692))):
        try:
            r = c.call("world.get", {"x": x, "y": y, "type": 0,
                                     "serverId": 2223,
                                     "timeStamp": int(__import__("time").time())})
            pp = r.get("__params__") or {}
            pts = pp.get("points") or []
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
            boss = [t for t in tiles if t.get("t") in (15, 49, 17, 51)
                    or "boss" in json.dumps(t, ensure_ascii=False).lower()
                    or t.get("m") in ("902113", "902114", "902115", "902150", "903116")]
            print("\n--- lv=%d 中心(%d,%d) 地块数=%d 疑似首领=%d"
                  % (lv, x, y, len(tiles), len(boss)))
            for t in boss[:4]:
                print("   ", json.dumps(t, ensure_ascii=False)[:400])
        except Exception as e:  # noqa: BLE001
            print("[!] world.get lv=%d 失败: %s" % (lv, str(e)[:160]))

    c.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
