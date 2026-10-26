#!/usr/bin/env python3
"""
COK / SmartFoxServer 2X (SFS) 线上协议解码器
格式来源(Java SDK smali, com.smartfoxserver.v2):
  PacketHeader : [flags:1][length:2 BE]   flags bit0=big-endian
  SFSObject    : [0x12][count:2 BE] then per entry:
                   [keyLen:2 BE][key bytes][value]
  value        : [typeID:1][data]
  typeID       : 0x00 NULL 0x01 BOOL 0x02 BYTE 0x03 SHORT 0x04 INT 0x05 LONG
                 0x06 FLOAT 0x07 DOUBLE 0x08 UTF_STRING 0x09 BOOL_ARRAY
                 0x0a BYTE_ARRAY 0x0b SHORT_ARRAY 0x0c INT_ARRAY 0x0d LONG_ARRAY
                 0x0e FLOAT_ARRAY 0x0f DOUBLE_ARRAY 0x10 UTF_STRING_ARRAY
                 0x11 SFS_ARRAY 0x12 SFS_OBJECT 0x13 CLASS 0x14 TEXT
"""
import struct
import sys

TYPE = {
    0x00: "NULL", 0x01: "BOOL", 0x02: "BYTE", 0x03: "SHORT", 0x04: "INT",
    0x05: "LONG", 0x06: "FLOAT", 0x07: "DOUBLE", 0x08: "UTF_STRING",
    0x09: "BOOL_ARRAY", 0x0a: "BYTE_ARRAY", 0x0b: "SHORT_ARRAY",
    0x0c: "INT_ARRAY", 0x0d: "LONG_ARRAY", 0x0e: "FLOAT_ARRAY",
    0x0f: "DOUBLE_ARRAY", 0x10: "UTF_STRING_ARRAY", 0x11: "SFS_ARRAY",
    0x12: "SFS_OBJECT", 0x13: "CLASS", 0x14: "TEXT",
}


class R:
    def __init__(self, b):
        self.b = b
        self.i = 0

    def u8(self):
        v = self.b[self.i]
        self.i += 1
        return v

    def u16(self):
        v = struct.unpack_from(">H", self.b, self.i)[0]
        self.i += 2
        return v

    def i16(self):
        v = struct.unpack_from(">h", self.b, self.i)[0]
        self.i += 2
        return v

    def u32(self):
        v = struct.unpack_from(">I", self.b, self.i)[0]
        self.i += 4
        return v

    def i32(self):
        v = struct.unpack_from(">i", self.b, self.i)[0]
        self.i += 4
        return v

    def raw(self, n):
        v = self.b[self.i:self.i + n]
        self.i += n
        return v

    def left(self):
        return len(self.b) - self.i


def read_value(r, depth=0):
    t = r.u8()
    name = TYPE.get(t, "?0x%02x" % t)
    if t == 0x00:
        return None
    if t == 0x01:
        return bool(r.u8())
    if t == 0x02:
        return r.u8()
    if t == 0x03:
        return r.i16()
    if t == 0x04:
        return r.i32()
    if t == 0x05:
        v = struct.unpack_from(">q", r.b, r.i)[0]
        r.i += 8
        return v
    if t == 0x06:
        v = struct.unpack_from(">f", r.b, r.i)[0]
        r.i += 4
        return v
    if t == 0x07:
        v = struct.unpack_from(">d", r.b, r.i)[0]
        r.i += 8
        return v
    if t == 0x08:
        n = r.u16()
        return r.raw(n).decode("utf-8", "replace")
    if t == 0x09:
        n = r.u32()
        return [bool(r.u8()) for _ in range(n)]
    if t == 0x0a:
        n = r.u32()
        return r.raw(n).hex()
    if t == 0x0b:
        n = r.u32()
        return [r.i16() for _ in range(n)]
    if t == 0x0c:
        n = r.u32()
        return [r.i32() for _ in range(n)]
    if t == 0x0d:
        n = r.u32()
        out = []
        for _ in range(n):
            out.append(struct.unpack_from(">q", r.b, r.i)[0])
            r.i += 8
        return out
    if t == 0x0e:
        n = r.u32()
        out = []
        for _ in range(n):
            out.append(struct.unpack_from(">f", r.b, r.i)[0])
            r.i += 4
        return out
    if t == 0x0f:
        n = r.u32()
        out = []
        for _ in range(n):
            out.append(struct.unpack_from(">d", r.b, r.i)[0])
            r.i += 8
        return out
    if t == 0x10:
        n = r.u32()
        return [r.raw(r.u16()).decode("utf-8", "replace") for _ in range(n)]
    if t == 0x11:
        n = r.u32()
        return [read_value(r, depth + 1) for _ in range(n)]
    if t == 0x12:
        n = r.u16()
        out = {}
        for _ in range(n):
            kl = r.i16()
            key = r.raw(kl).decode("utf-8", "replace")
            out[key] = read_value(r, depth + 1)
        return out
    if t == 0x14:
        n = r.u16()
        return r.raw(n).decode("utf-8", "replace")
    raise ValueError("unknown type 0x%02x at %d" % (t, r.i - 1))


def parse_packet(b):
    """返回 (flags, payload, obj)"""
    flags = b[0]
    ln = struct.unpack_from(">H", b, 1)[0]
    payload = b[3:3 + ln]
    r = R(payload)
    obj = None
    try:
        obj = read_value(r)
    except Exception as e:  # noqa: BLE001
        obj = {"__parse_error__": str(e), "__at__": r.i}
    return flags, payload, obj, r.i


def fmt(o, ind=0):
    pad = "  " * ind
    if isinstance(o, dict):
        out = []
        for k, v in o.items():
            if isinstance(v, (dict, list)):
                out.append("%s%s:" % (pad, k))
                out.append(fmt(v, ind + 1))
            else:
                out.append("%s%s = %r" % (pad, k, v))
        return "\n".join(out)
    if isinstance(o, list):
        out = []
        for v in o[:40]:
            if isinstance(v, (dict, list)):
                out.append(fmt(v, ind + 1))
            else:
                out.append("%s- %r" % (pad, v))
        if len(o) > 40:
            out.append("%s... (%d more)" % (pad, len(o) - 40))
        return "\n".join(out)
    return "%s%r" % (pad, o)


if __name__ == "__main__":
    for path in sys.argv[1:]:
        data = open(path, "rb").read()
        flags, payload, obj, consumed = parse_packet(data)
        print("flags=0x%02x len=%d consumed=%d/%d" % (flags, len(payload), consumed, len(payload)))
        print(fmt(obj))
        print("-" * 60)
