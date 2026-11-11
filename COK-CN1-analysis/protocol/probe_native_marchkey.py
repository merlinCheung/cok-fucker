#!/usr/bin/env python3
"""在 libgame.so 里定位 marchKey 盐 / "1021" 的引用点(用于反汇编核对)。"""
import struct

SO = "/Users/a1234/workspace/me/cok/COK-CN1-analysis/apk-extract/lib/arm64-v8a/libgame.so"
TEXT_OFF = 0x8ff000
TEXT_SIZE = 0x268c68c
PAGE = 0x2fc4000
TARGETS = {
    0x2fc4e58: "salt wNSc5Mm8YwiOhAab",
    0x2fc4e00: "1021",
    0x2fc4e70: "marchKey",
    0x2fc4dd8: "WorldMarchCommand targetpoint: %d",
    0x2fc4e40: "wtIndex",
    0x2fc4e08: "ownerFlag",
    0x2fc4e30: "generals",
}

data = open(SO, "rb").read()


def adrp_page(i):
    w = struct.unpack_from("<I", data, i)[0]
    if (w & 0x9F000000) != 0x90000000:
        return None
    immlo = (w >> 29) & 3
    immhi = (w >> 5) & 0x7FFFF
    imm = (immhi << 2) | immlo
    if imm & (1 << 20):
        imm -= 1 << 21
    return (i & ~0xFFF) + (imm << 12)


found = {}
for i in range(TEXT_OFF, TEXT_OFF + TEXT_SIZE, 4):
    if adrp_page(i) != PAGE:
        continue
    rd_adrp = struct.unpack_from("<I", data, i)[0] & 0x1F
    for j in range(1, 12):
        w = struct.unpack_from("<I", data, i + 4 * j)[0]
        if (w & 0xFF000000) != 0x91000000:
            continue
        imm = (w >> 10) & 0xFFF
        rn = (w >> 5) & 0x1F
        if rn != rd_adrp:
            continue
        addr = PAGE + imm
        if addr in TARGETS:
            found.setdefault(TARGETS[addr], []).append(i)

for k, v in sorted(found.items()):
    print("%-40s refs=%-4d %s" % (k, len(v), [hex(x) for x in v[:10]]))
