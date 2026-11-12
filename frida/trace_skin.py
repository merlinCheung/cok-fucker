#!/usr/bin/env python3
"""抓 skin.introduction 的响应明文并逐字节追踪 SFS 结构, 定位解析断点。"""
import os
import struct
import sys

sys.path.insert(0, "/Users/a1234/workspace/me/cok/cok")
from cok_client import CokClient  # noqa: E402

TYPES = {0x00: "NULL", 0x01: "BOOL", 0x02: "BYTE", 0x03: "SHORT", 0x04: "INT",
         0x05: "LONG", 0x06: "FLOAT", 0x07: "DOUBLE", 0x08: "STRING", 0x09: "BOOLARR",
         0x0a: "BYTES", 0x0b: "SHORTARR", 0x0c: "INTARR", 0x0d: "LONGARR",
         0x0e: "FLOATARR", 0x0f: "DOUBLEARR", 0x10: "STRARR", 0x11: "ARRAY",
         0x12: "OBJECT", 0x13: "CLASS", 0x14: "UTF8"}


def trace(buf, off, depth, limit=40):
    """返回 (新offset, 输出行数)"""
    lines = []
    t = buf[off]
    name = TYPES.get(t, "?0x%02x" % t)
    if t == 0x12:  # OBJECT
        n = struct.unpack_from(">H", buf, off + 1)[0]
        lines.append("%sOBJECT(%d)" % ("  " * depth, n))
        i = off + 3
        for k in range(n):
            if i + 2 > len(buf):
                lines.append("%s  !! 越界 @%d" % ("  " * depth, i))
                return len(buf), lines
            kl = struct.unpack_from(">H", buf, i)[0]
            i += 2
            key = buf[i:i + kl].decode("utf-8", "replace")
            i += kl
            lines.append("%s  key=%r" % ("  " * depth, key))
            i, sub = trace(buf, i, depth + 1)
            lines += sub
            if len(lines) > limit * 6:
                break
        return i, lines
    if t == 0x11:  # ARRAY
        n = struct.unpack_from(">H", buf, off + 1)[0]
        lines.append("%sARRAY(%d)" % ("  " * depth, n))
        i = off + 3
        for k in range(n):
            i, sub = trace(buf, i, depth + 1)
            lines += sub
            if len(lines) > limit * 6:
                break
        return i, lines
    if t == 0x08 or t == 0x14:
        n = struct.unpack_from(">H", buf, off + 1)[0]
        s = buf[off + 3:off + 3 + n].decode("utf-8", "replace")
        lines.append("%s%s %r" % ("  " * depth, name, s[:40]))
        return off + 3 + n, lines
    if t == 0x0a:
        n = struct.unpack_from(">I", buf, off + 1)[0]
        lines.append("%sBYTES(%d)" % ("  " * depth, n))
        return off + 5 + n, lines
    sizes = {0x00: 1, 0x01: 1, 0x02: 1, 0x03: 2, 0x04: 4, 0x05: 8, 0x06: 4, 0x07: 8}
    if t in sizes:
        sz = sizes[t]
        val = buf[off + 1:off + 1 + sz]
        lines.append("%s%s %r" % ("  " * depth, name, val))
        return off + 1 + sz, lines
    if t in (0x09, 0x0b, 0x0c, 0x0d, 0x0e, 0x0f, 0x10):
        n = struct.unpack_from(">I", buf, off + 1)[0]
        lines.append("%s%s(%d)" % ("  " * depth, name, n))
        return off + 5, lines
    lines.append("%s!! 未知类型 0x%02x @%d" % ("  " * depth, t, off))
    return len(buf), lines


def main():
    c = CokClient(timeout=15)
    c.connect()
    c.bin_handshake()
    c.login()
    try:
        c.call("cmd.ping")
    except Exception:
        pass
    body = {}
    orig = c._decode_response

    def grab(obj, cmd):
        pp = c._resp_params(obj)
        for k, v in (pp or {}).items():
            if k != "qqq" and isinstance(v, str) and len(v) > 32:
                import binascii
                import zlib
                blob = binascii.unhexlify(v)
                x = bytes(b ^ c.key[i % len(c.key)] for i, b in enumerate(blob))
                if x[:1] == b"\x78":
                    body["raw"] = zlib.decompressobj(-15).decompress(x[2:])
        return orig(obj, cmd)

    c._decode_response = grab
    try:
        c.call("skin.introduction")
    except Exception as e:
        print("orig 失败:", str(e)[:80])
    c.close()
    if "raw" not in body:
        print("没抓到明文")
        return
    buf = body["raw"]
    with open("/tmp/skin_body.bin", "wb") as fh:
        fh.write(buf)
    print("明文长度 %d, 已存 /tmp/skin_body.bin" % len(buf))
    end, lines = trace(buf, 0, 0)
    print("\n".join(lines[:60]))
    print("... 解析终点 offset=%d / 总长 %d" % (end, len(buf)))


if __name__ == "__main__":
    main()
