#!/usr/bin/env python3
"""按 SFS 字节流解析出 (键序, 类型) 序列, 用于精确复刻客户端的编码。"""
import struct
import sys


def parse_pairs(buf, off=0, end=None):
    """返回 [(key, type_byte, value_repr)]，对象层。"""
    if end is None:
        end = len(buf)
    assert buf[off] == 0x12, "expect SFS_OBJECT, got 0x%02x" % buf[off]
    count = struct.unpack_from(">H", buf, off + 1)[0]
    i = off + 3
    out = []
    for _ in range(count):
        klen = struct.unpack_from(">H", buf, i)[0]
        i += 2
        key = buf[i:i + klen].decode("utf-8", "replace")
        i += klen
        t = buf[i]
        i += 1
        if t == 0x00:
            val = None
        elif t == 0x01:
            val = bool(buf[i]); i += 1
        elif t == 0x02:
            val = buf[i]; i += 1
        elif t == 0x03:
            val = struct.unpack_from(">h", buf, i)[0]; i += 2
        elif t == 0x04:
            val = struct.unpack_from(">i", buf, i)[0]; i += 4
        elif t == 0x05:
            val = struct.unpack_from(">q", buf, i)[0]; i += 8
        elif t == 0x06:
            val = struct.unpack_from(">f", buf, i)[0]; i += 4
        elif t == 0x08:
            n = struct.unpack_from(">H", buf, i)[0]; i += 2
            val = buf[i:i + n].decode("utf-8", "replace"); i += n
        elif t == 0x0a:
            n = struct.unpack_from(">I", buf, i)[0]; i += 4
            val = "<%d bytes>" % n; i += n
        elif t == 0x10:
            n = struct.unpack_from(">I", buf, i)[0]; i += 4
            arr = []
            for _ in range(n):
                kl = struct.unpack_from(">H", buf, i)[0]; i += 2
                arr.append(buf[i:i + kl].decode("utf-8", "replace")); i += kl
            val = arr
        elif t == 0x11:
            n = struct.unpack_from(">I", buf, i)[0]; i += 4
            arr = []
            for _ in range(n):
                sub, i = parse_one(buf, i)
                arr.append(sub)
            val = arr
        elif t == 0x12:
            # 类型字节已被消费, 递归时需退回 1 字节让 parse_pairs 看到 0x12 头
            sub, i = parse_pairs(buf, i - 1)
            val = sub
        else:
            raise ValueError("unknown type 0x%02x at %d" % (t, i - 1))
        out.append((key, t, val))
    return out, i


def parse_one(buf, i):
    t = buf[i]; i += 1
    if t == 0x00:
        return None, i
    if t == 0x01:
        return bool(buf[i]), i + 1
    if t == 0x02:
        return buf[i], i + 1
    if t == 0x03:
        return struct.unpack_from(">h", buf, i)[0], i + 2
    if t == 0x04:
        return struct.unpack_from(">i", buf, i)[0], i + 4
    if t == 0x05:
        return struct.unpack_from(">q", buf, i)[0], i + 8
    if t == 0x08:
        n = struct.unpack_from(">H", buf, i)[0]; i += 2
        return buf[i:i + n].decode("utf-8", "replace"), i + n
    if t == 0x0a:
        n = struct.unpack_from(">I", buf, i)[0]; i += 4
        return buf[i:i + n], i + n
    if t == 0x12:
        return parse_pairs(buf, i)
    raise ValueError("unknown type 0x%02x" % t)


if __name__ == "__main__":
    import binascii
    data = binascii.unhexlify(sys.argv[1])
    pairs, _ = parse_pairs(data)
    for k, t, v in pairs:
        print("  %-20s type=0x%02x  value=%r" % (k, t, v))
