#!/usr/bin/env python3
"""端到端自检: 用 md5(id 前缀) 派生的会话密钥, 解码整场会话的请求/响应。

用法:
  python3 verify_key.py <frida-wire.jsonl> [--fd 135] [--id <id 串>]

id 串来自登录响应的明文字段 "id" = "<前缀>_<密钥ID>"。
"""
import binascii
import collections
import hashlib
import json
import sys

sys.path.insert(0, "/Users/a1234/workspace/me/cok/cok")
from cok_sfs import parse_packet, flatten, xor_buf, read_value, Reader, decode_params  # noqa: E402


def try_frame(buf, i):
    if i + 3 > len(buf):
        return None
    if not (buf[i] & 0x80):
        return None
    ln = (buf[i + 1] << 8) | buf[i + 2]
    if ln == 0 or i + 3 + ln > len(buf):
        return None
    fr = bytes(buf[i:i + 3 + ln])
    try:
        flags, payload, obj, consumed = parse_packet(fr)
    except Exception:
        return None
    if consumed != len(payload):
        return None
    return fr, obj, 3 + ln


def extract_frames(buf):
    frames, i, n = [], 0, len(buf)
    while i + 3 <= n:
        r = try_frame(buf, i)
        if r is None:
            i += 1
            continue
        fr, obj, size = r
        frames.append((fr, obj))
        i += size
    return frames


def find_login_id(path, fd_want):
    """从明文响应里找 "id" 字段"""
    buf = bytearray()
    for ln in open(path, encoding="utf-8", errors="replace"):
        try:
            rec = json.loads(ln)
        except Exception:
            continue
        pl = rec.get("msg", {}).get("payload")
        if isinstance(pl, dict) and pl.get("t") == "wire" and pl.get("fd") == fd_want and pl.get("dir") == "read":
            buf.extend(binascii.unhexlify(pl["hex"]))
    for fr, obj in extract_frames(bytes(buf)):
        f = flatten(obj)
        for k, v in f.items():
            if k.endswith(".id") and isinstance(v, str) and "_" in v:
                return v
    return None


def main(argv):
    path = argv[1]
    fd_want = 135
    id_str = None
    i = 2
    while i < len(argv):
        if argv[i] == "--fd":
            fd_want = int(argv[i + 1]); i += 2
        elif argv[i] == "--id":
            id_str = argv[i + 1]; i += 2
        else:
            i += 1

    if id_str is None:
        id_str = find_login_id(path, fd_want)
        if id_str is None:
            print("!! 没能在明文响应里找到 id 字段")
            return 2
    prefix, _, suffix = id_str.partition("_")
    key = hashlib.md5(prefix.encode()).hexdigest()
    print("登录响应 id      = %s" % id_str)
    print("前缀             = %s" % prefix)
    print("密钥ID           = %s" % suffix)
    print("会话 XOR 密钥    = %s   (= md5 前缀)" % key)
    print("ver 包密钥       = %s   (= md5 完整 id)" % hashlib.md5(id_str.encode()).hexdigest())
    kb = key.encode()

    streams = collections.defaultdict(bytearray)
    for ln in open(path, encoding="utf-8", errors="replace"):
        try:
            rec = json.loads(ln)
        except Exception:
            continue
        pl = rec.get("msg", {}).get("payload")
        if isinstance(pl, dict) and pl.get("t") == "wire" and pl.get("fd") == fd_want:
            streams[pl.get("dir")].extend(binascii.unhexlify(pl["hex"]))

    ok = fail = plain = 0
    cmds = collections.Counter()
    failures = []
    for dirn, buf in streams.items():
        for fr, obj in extract_frames(bytes(buf)):
            f = flatten(obj)
            cmd = f.get("p.c") or f.get("p.p.c")
            pb = f.get("p.p.params")
            if cmd is None and pb is None:
                continue
            cmds[(dirn, cmd)] += 1
            if not isinstance(pb, str):
                plain += 1
                continue
            blob = binascii.unhexlify(pb)
            try:
                if dirn == "write":
                    inner = read_value(Reader(xor_buf(blob, kb)))
                else:
                    inner, mode, raw = decode_params(blob, kb)
                ok += 1
            except Exception as e:  # noqa: BLE001
                fail += 1
                failures.append((dirn, cmd, str(e)[:60]))
    print("\n=== 解密结果 ===")
    print("  params 解密成功 : %d" % ok)
    print("  params 解密失败 : %d" % fail)
    print("  明文/无 params  : %d" % plain)
    for d, c, e in failures[:10]:
        print("    [FAIL] %s %s : %s" % (d, c, e))
    print("\n=== 命令统计 (前 25) ===")
    for (d, c), n in cmds.most_common(25):
        print("  [%-5s] %-30s x%d" % (d, c, n))
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
