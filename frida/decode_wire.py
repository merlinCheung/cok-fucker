#!/usr/bin/env python3
"""从 frida 线路抓包重组 fd 上的 SFS 帧并解码(明文阶段直接解析)。"""
import binascii
import collections
import json
import sys

sys.path.insert(0, "/Users/a1234/workspace/me/cok/COK-CN1-analysis/protocol")
from cok_sfs import parse_packet, flatten, read_value, Reader, xor_buf  # noqa: E402


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


def main(path, fd_filter=None, key_hex=None, maxdump=40):
    KEY = bytes.fromhex(key_hex) if key_hex else None
    wires = []
    for ln in open(path, encoding="utf-8", errors="replace").read().splitlines():
        try:
            rec = json.loads(ln)
        except Exception:
            continue
        pl = rec.get("msg", {}).get("payload")
        if isinstance(pl, dict) and pl.get("t") == "wire":
            wires.append(pl)
    if not wires:
        print("没有 wire 事件")
        return 1
    streams = collections.defaultdict(lambda: collections.defaultdict(bytearray))
    for w in wires:
        streams[w.get("fd")][w.get("dir")].extend(binascii.unhexlify(w["hex"]))

    for fd, d in streams.items():
        if fd_filter and str(fd) != str(fd_filter):
            continue
        for dirn, buf in d.items():
            frames = extract_frames(bytes(buf))
            if not frames:
                continue
            print("\n############ fd=%s dir=%s  帧数=%d ############" % (fd, dirn, len(frames)))
            for idx, (fr, obj) in enumerate(frames):
                if idx >= maxdump:
                    print("  ... 还有 %d 帧" % (len(frames) - idx))
                    break
                f = flatten(obj)
                cmd = f.get("p.c") or f.get("p.p.c") or f.get("c")
                print("--- [%d] len=%d cmd=%s" % (idx, len(fr), cmd))
                for k, v in f.items():
                    if k.endswith("params"):
                        print("      %-14s = <%d 字节>" % (k, len(v) // 2))
                    else:
                        print("      %-14s = %s" % (k, str(v)[:120]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None,
                  sys.argv[3] if len(sys.argv) > 3 else None))
