#!/usr/bin/env python3
"""找 "ADRP 某页 + LDR 某偏移" 的指令位置(GOT 间接引用)。

用法: python3 find_got_load.py <libgame.so> <page_hex> <lo12_hex> [rd]
"""
import struct
import sys

P = sys.argv[1]
PAGE = int(sys.argv[2], 16)
LO12 = int(sys.argv[3], 16)
RD = int(sys.argv[4]) if len(sys.argv) > 4 else None

d = open(P, "rb").read()
e_shoff = struct.unpack_from("<Q", d, 0x28)[0]
e_shentsize, e_shnum, e_shstrndx = struct.unpack_from("<HHH", d, 0x3a)


def sh(i):
    o = e_shoff + i * e_shentsize
    name, typ, flags, addr, off, size, link, info, align, entsize = \
        struct.unpack_from("<IIQQQQIIQQ", d, o)
    return dict(name=name, addr=addr, off=off, size=size)


st = sh(e_shstrndx)


def nm(x):
    return d[st["off"] + x:].split(b"\x00")[0].decode()


secs = []
for i in range(e_shnum):
    s = sh(i)
    s["sname"] = nm(s["name"])
    secs.append(s)
text = [s for s in secs if s["sname"] == ".text"][0]
base = text["addr"]
buf = d[text["off"]:text["off"] + text["size"]]

out = []
for i in range(0, len(buf) - 4, 4):
    w = struct.unpack_from("<I", buf, i)[0]
    if (w & 0x9F000000) != 0x90000000:
        continue
    rd = w & 0x1F
    imm = ((w >> 29) & 0x3) | (((w >> 5) & 0x7FFFF) << 2)
    if imm & (1 << 20):
        imm -= (1 << 21)
    page = ((base + i) & ~0xFFF) + (imm << 12)
    if page != PAGE:
        continue
    for j in range(1, 12):
        if i + 4 * j + 4 > len(buf):
            break
        w2 = struct.unpack_from("<I", buf, i + 4 * j)[0]
        # LDR (unsigned imm12, 64-bit): 1111 1001 01 imm12 Rn Rt
        if (w2 & 0xFFC00000) != 0xF9400000:
            continue
        imm12 = (w2 >> 10) & 0xFFF
        rn = (w2 >> 5) & 0x1F
        rt = w2 & 0x1F
        if rn == rd and imm12 == LO12 and (RD is None or rt == RD):
            out.append((base + i, base + i + 4 * j, rn, rt))
for a, b, rn, rt in out:
    print("  adrp 0x%x (x%d)  ->  ldr 0x%x  (x%d = [x%d, #0x%x])" % (a, rn, b, rt, rn, LO12))
if not out:
    print("  (没找到)")
