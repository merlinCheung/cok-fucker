#!/usr/bin/env python3
"""解析 capture_plain.js 抓到的双向明文。

  dir='req'  -> SFS 明文(直接 parse_best)
  dir='resp' -> zlib(SFS) 明文(decompress 后 parse_best)

用法:
  python3 parse_plain.py <capture.jsonl> [--grep CMD] [--hex] [--keys K1,K2]
"""
import argparse
import json
import sys
import zlib

PROTO = "/Users/a1234/workspace/me/cok/cok"
sys.path.insert(0, PROTO)
from cok_sfs import parse_best, flatten  # noqa: E402


def load(path):
    for line in open(path, encoding="utf-8", errors="replace"):
        line = line.strip()
        if not line:
            continue
        try:
            o = json.loads(line)
        except Exception:
            continue
        p = (o.get("msg") or {}).get("payload") or {}
        if p.get("t") == "x":
            yield p


def decode(rec):
    raw = bytes.fromhex(rec["hex"])
    if rec["dir"] == "resp":
        try:
            raw = zlib.decompress(raw)
        except Exception as e:
            return None, "zlib:%s" % str(e)[:60]
    try:
        obj, mode = parse_best(raw)
    except Exception as e:
        return None, "parse:%s" % str(e)[:60]
    return obj, None


def cmd_of(obj):
    """从 SFS 对象里找命令名

    请求结构: {p:{p:{params:...}, r:INT, c:"cmd.name"}, a:SHORT, c:BYTE}
    """
    if not isinstance(obj, dict):
        return None
    p = obj.get("p")
    if isinstance(p, dict):
        c = p.get("c")
        if isinstance(c, str):
            return c
        pp = p.get("p")
        if isinstance(pp, dict):
            c = pp.get("c")
            if isinstance(c, str):
                return c
    c = obj.get("c")
    if isinstance(c, str):
        return c
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path")
    ap.add_argument("--grep", help="只显示命令名含该串的")
    ap.add_argument("--hex", action="store_true", help="同时打印原始 hex")
    ap.add_argument("--keys", help="只打印这些 key 的值(逗号分隔)")
    ap.add_argument("--max", type=int, default=40, help="最多显示多少条")
    args = ap.parse_args()

    only = set(k for k in (args.keys or "").split(",") if k)
    shown = 0
    errs = 0
    for rec in load(args.path):
        obj, err = decode(rec)
        if err:
            errs += 1
            if errs <= 5:
                print("  [decode fail] %s" % err)
            continue
        cmd = cmd_of(obj)
        flat = flatten(obj) if isinstance(obj, dict) else {}
        if args.grep and (not cmd or args.grep not in cmd):
            continue
        shown += 1
        if shown > args.max:
            break
        print("=== %s  cmd=%s" % (rec["dir"], cmd))
        if only:
            for k in only:
                for fk, fv in flat.items():
                    if fk == k or fk.endswith("." + k):
                        print("    %-22s = %r" % (fk, fv))
        else:
            for fk, fv in list(flat.items())[:40]:
                print("    %-26s = %r" % (fk, fv))
        if args.hex:
            print("    hex:", rec["hex"][:200])
    print("\n(显示 %d 条, 解码失败 %d)" % (shown, errs))


if __name__ == "__main__":
    main()
