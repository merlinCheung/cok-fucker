#!/usr/bin/env python3
"""从 frida 抓包(capture_full2.js)里解出「命令名 + 全部 params」。

原理:
  * wire 帧里 p.p.c (命令名) 是明文; p.p.params 是加密的
  * 抓包里的 'key' 事件给出**会话密钥**(XOR 用的 32 字节 ASCII)
  * 请求 params = XOR(明文 SFS); 响应 params = XOR(zlib(明文 SFS))
    (客户端解密时先 zlib 再 XOR, 服务端发的是 XOR(zlib(...)))

用法:
  python3 decode_hunt.py /tmp/hunt_capture.jsonl [--grep world.march] [--json]
"""
import argparse
import json
import sys
import zlib

PROTO = "/Users/a1234/workspace/me/cok/COK-CN1-analysis/protocol"
sys.path.insert(0, PROTO)
from cok_sfs import parse_packet, read_value, Reader, xor_buf, parse_best, flatten  # noqa: E402


def load_events(path):
    keys = []
    wires = []
    plains = []
    for ln in open(path, encoding="utf-8", errors="replace"):
        ln = ln.strip()
        if not ln:
            continue
        try:
            o = json.loads(ln)
        except Exception:
            continue
        p = (o.get("msg") or {}).get("payload") or {}
        t = p.get("t")
        if t == "key" and p.get("key"):
            keys.append(bytes.fromhex(p["key"]))
        elif t == "w" and p.get("hex"):
            wires.append((o.get("ts", 0), p["hex"]))
        elif t == "x" and p.get("hex"):
            plains.append((o.get("ts", 0), p["dir"], p["hex"]))
    return keys, wires, plains


def frame_params(payload):
    """从 SFS 信封里取出 p.p.params 的原始字节(可能是 BYTE_ARRAY)。"""
    # 信封结构: { p: { p: { params: <bytes>, r: int, c: "cmd" }, a: int, c: int } }
    # 手工下钻: 用 read_value 读最外层
    try:
        r = Reader(payload)
        top = read_value(r)
    except Exception:
        return None, None
    if not isinstance(top, dict):
        return None, None
    p1 = top.get("p")
    if not isinstance(p1, dict):
        return None, None
    # 业务帧结构: { p: { p: {params: <bytes>}, r: -1, c: "<命令名>" }, a: 13, c: 1 }
    cmd = p1.get("c")
    p2 = p1.get("p")
    params = p2.get("params") if isinstance(p2, dict) else None
    return cmd, params


def decode_params(raw, key):
    """raw = 线上 params 字节; 返回明文 SFS 对象。"""
    if raw is None:
        return None
    if isinstance(raw, str):          # 解析器可能把 BYTE_ARRAY 变成 hex 串
        try:
            raw = bytes.fromhex(raw)
        except Exception:
            return None
    if not isinstance(raw, (bytes, bytearray)):
        return None
    x = xor_buf(bytes(raw), key)
    if x[:2] == b"\x78\x9c":
        try:
            x = zlib.decompress(x)
        except Exception:
            try:
                x = zlib.decompressobj(-15).decompress(x[2:])
            except Exception:
                return None
    try:
        obj, _mode = parse_best(x)
    except Exception:
        return None
    return obj


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("capture")
    ap.add_argument("--grep", help="只显示命令名包含该串的")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()

    keys, wires, plains = load_events(args.capture)
    if not keys:
        print("[!] 抓包里没有会话密钥事件, 无法解密")
        return 1
    key = keys[-1]
    print("[*] 会话密钥:", key.decode("ascii", "replace"), " (共 %d 个)" % len(keys))

    out = []
    for ts, hexs in wires:
        try:
            raw = bytes.fromhex(hexs)
        except Exception:
            continue
        if len(raw) < 3:
            continue
        try:
            flags, payload, obj, consumed = parse_packet(raw)
        except Exception:
            continue
        f = flatten(obj)
        cmd, praw = f.get("p.c"), f.get("p.p.params")
        if cmd is None:
            continue
        obj = decode_params(praw, key)
        if obj is None:
            out.append((ts, cmd, None))
        else:
            out.append((ts, cmd, obj))

    n = 0
    for ts, cmd, obj in out:
        if args.grep and args.grep not in str(cmd):
            continue
        n += 1
        if args.limit and n > args.limit:
            break
        if args.json:
            print(json.dumps({"cmd": cmd, "params": obj}, ensure_ascii=False, default=str))
        else:
            print("%-28s %s" % (cmd, json.dumps(obj, ensure_ascii=False, default=str)[:400]))
    print("[*] 共 %d 个命令帧" % len(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
