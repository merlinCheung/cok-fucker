#!/usr/bin/env python3
"""命令存在性探测器。

原理(已实测): 服务端遇到**未知命令名会直接关闭连接**; 已知命令但参数不对会回
`errorCode`。所以:
    断连            -> 该命令名不存在
    返回 errorCode  -> 该命令名存在
    返回业务数据     -> 该命令名存在且参数刚好够用

用法:
  python3 probe_cmds.py build.upgrade build.create ...     # 指定候选
  python3 probe_cmds.py --from-lib                          # 从 libgame.so 提取候选
  python3 probe_cmds.py --filter build,queue,speed           # 按关键词筛
"""
import argparse
import binascii
import os
import re
import struct
import subprocess
import sys
import time

sys.path.insert(0, "/Users/a1234/workspace/me/cok/cok")
from cok_client import CokClient  # noqa: E402

LIB = "/Users/a1234/workspace/me/cok/frida/devlib/lib/arm64-v8a/libgame.so"
CMD_RE = re.compile(r"^[a-z][a-zA-Z0-9_]{1,24}\.[a-z][a-zA-Z0-9_.]{1,32}$")


def lib_commands():
    out = subprocess.run(["strings", "-a", LIB], capture_output=True, text=True).stdout
    res = set()
    for line in out.splitlines():
        s = line.strip()
        if CMD_RE.match(s) and not s.endswith(".png") and "/" not in s and "." not in s[:-4]:
            res.add(s)
    return sorted(res)


def probe_one(cmd, timeout=8.0):
    """返回 (status, detail): exists / missing / data"""
    c = CokClient(timeout=timeout)
    try:
        c.connect(retries=1, backoff=1)
        c.bin_handshake()
        c.login()
        try:
            c.call("cmd.ping")
        except Exception:
            pass
        r = c.call(cmd, None, retries=0)
        p = r.get("__params__") or {}
        err = p.get("errorCode") if isinstance(p, dict) else None
        if err:
            return "exists", "errorCode=%s" % err
        return "exists", "data: " + ",".join(list(p.keys())[:5]) if isinstance(p, dict) else "data"
    except Exception as e:  # noqa: BLE001
        msg = str(e)
        if "关闭" in msg or "Connection" in msg or "reset" in msg:
            return "missing", msg[:40]
        return "unknown", msg[:50]
    finally:
        try:
            c.close()
        except Exception:
            pass


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmds", nargs="*", help="候选命令名")
    ap.add_argument("--from-lib", action="store_true", help="从 libgame.so 提取候选")
    ap.add_argument("--filter", default="", help="按关键词筛(逗号分隔)")
    ap.add_argument("--timeout", type=float, default=8.0)
    ap.add_argument("--out", default="cmd-existence.json")
    args = ap.parse_args()

    cands = list(args.cmds)
    if args.from_lib or args.filter:
        pool = lib_commands()
        if args.filter:
            keys = [k.strip() for k in args.filter.split(",") if k.strip()]
            pool = [c for c in pool if any(k.lower() in c.lower() for k in keys)]
        cands = list(dict.fromkeys(cands + pool))
    if not cands:
        print("没有候选")
        return 1

    print("探测 %d 个候选命令..." % len(cands))
    result = {}
    for i, cmd in enumerate(cands, 1):
        st, detail = probe_one(cmd, args.timeout)
        result[cmd] = {"status": st, "detail": detail}
        mark = {"exists": "存在", "missing": "不存在", "unknown": "?"}.get(st, st)
        print("  [%3d/%d] %-40s %-6s %s" % (i, len(cands), cmd, mark, detail))
        sys.stdout.flush()
    import json
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(result, fh, ensure_ascii=False, indent=1)
    exists = [c for c, v in result.items() if v["status"] == "exists"]
    print("\n存在 %d / 探测 %d -> %s" % (len(exists), len(cands), args.out))
    return 0


if __name__ == "__main__":
    main()
