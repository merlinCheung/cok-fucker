#!/usr/bin/env python3
"""用探针读出的会话密钥解 wire 帧, 得到「命令名 + params 明文」。

帧结构: SFS_OBJECT { p: { p: { params: <BYTE_ARRAY = XOR(key, SFS明文)> }, r:INT, c:"cmd" },
                    a:SHORT, c:BYTE }

用法:
  python3 decode_wire.py <capture.jsonl> [--grep CMD] [--max N] [--items] [--queue]
"""
import argparse
import json
import struct
import sys
import zlib

PROTO = "/Users/a1234/workspace/me/cok/COK-CN1-analysis/protocol"
sys.path.insert(0, PROTO)
from cok_sfs import parse_best, Reader, read_value  # noqa: E402


def load(path):
    keys = []
    wires = []
    for line in open(path, encoding="utf-8", errors="replace"):
        line = line.strip()
        if not line:
            continue
        try:
            o = json.loads(line)
        except Exception:
            continue
        p = (o.get("msg") or {}).get("payload") or {}
        if p.get("t") == "key":
            keys.append(bytes.fromhex(p["key"]))
        elif p.get("t") == "w":
            wires.append(bytes.fromhex(p["hex"]))
    return keys, wires


def xor_buf(data, key):
    return bytes(b ^ key[i % len(key)] for i, b in enumerate(data))


def find_params(obj):
    """在解出的帧对象里找 params 的 BYTE_ARRAY"""
    if not isinstance(obj, dict):
        return None
    p = obj.get("p")
    if isinstance(p, dict):
        pp = p.get("p")
        if isinstance(pp, dict):
            return pp.get("params")
    return None


def cmd_of(obj):
    if isinstance(obj, dict):
        p = obj.get("p")
        if isinstance(p, dict) and isinstance(p.get("c"), str):
            return p["c"]
        if isinstance(obj.get("c"), str):
            return obj["c"]
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path")
    ap.add_argument("--grep")
    ap.add_argument("--max", type=int, default=30)
    ap.add_argument("--items", action="store_true", help="只显示含 items 的响应")
    ap.add_argument("--queue", action="store_true", help="只显示含 queue 的响应")
    args = ap.parse_args()

    keys, wires = load(args.path)
    print("密钥 %d 个, wire 帧 %d 个" % (len(keys), len(wires)))
    for k in keys:
        print("   key:", k.decode("ascii", "replace"))

    shown = 0
    for fr in wires:
        if len(fr) < 3:
            continue
        # 帧头 [flags:1][len:2 BE]，flags 0x80=大端长度, 0x20=zlib
        flags = fr[0]
        if not (flags & 0x80):      # 真实 SFS 帧首字节必带 0x80(大端长度)
            continue
        ln = struct.unpack_from(">H", fr, 1)[0]
        if ln <= 0 or 3 + ln > len(fr):
            continue
        payload = fr[3:3 + ln]
        if flags & 0x20:
            try:
                payload = zlib.decompress(payload)
            except Exception:
                continue
        try:
            r = Reader(payload)
            obj = read_value(r, 0, "val")
        except Exception:
            continue
        params = find_params(obj)
        if params is None:
            continue
        plain = None
        if isinstance(params, (bytes, bytearray)):
            for k in keys:
                d = xor_buf(bytes(params), k)
                if d[:1] in (b"\x12", b"\x08"):
                    plain = d
                    break
        if plain is None:
            continue
        try:
            pobj, mode = parse_best(plain)
        except Exception:
            continue
        cmd = cmd_of(obj)
        if args.grep and (not cmd or args.grep not in cmd):
            continue
        if args.items and not (isinstance(pobj, dict) and "items" in pobj):
            continue
        if args.queue and not (isinstance(pobj, dict) and "queue" in pobj):
            continue
        shown += 1
        if shown > args.max:
            break
        print("\n=== cmd=%s  (%d bytes params) ===" % (cmd, len(plain)))
        if isinstance(pobj, dict):
            for kk, vv in list(pobj.items())[:25]:
                if isinstance(vv, list):
                    print("   %-24s list(%d)" % (kk, len(vv)))
                elif isinstance(vv, dict):
                    print("   %-24s dict(%d)" % (kk, len(vv)))
                else:
                    print("   %-24s %r" % (kk, str(vv)[:60]))
    print("\n(显示 %d 条)" % shown)


if __name__ == "__main__":
    main()
