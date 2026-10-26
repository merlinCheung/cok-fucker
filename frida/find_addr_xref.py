#!/usr/bin/env python3
"""在 ELF arm64 的 .text 里找"某函数地址"被 ADRP+ADD 引用的位置。

用途: 反查"哪个消息分发表/注册表把 handler 指向了某个函数"。
用法: python3 find_addr_xref.py <libgame.so> <0xADDR> [0xADDR ...]
"""
import struct
import sys

P = sys.argv[1]
targets = set(int(a, 16) for a in sys.argv[2:])

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

hits = []
for i in range(0, len(buf) - 4, 4):
    w = struct.unpack_from("<I", buf, i)[0]
    if (w & 0x9F000000) != 0x90000000:
        continue
    rd = w & 0x1F
    imm = ((w >> 29) & 0x3) | (((w >> 5) & 0x7FFFF) << 2)
    if imm & (1 << 20):
        imm -= (1 << 21)
    page = ((base + i) & ~0xFFF) + (imm << 12)
    for j in range(1, 40):
        if i + 4 * j + 4 > len(buf):
            break
        w2 = struct.unpack_from("<I", buf, i + 4 * j)[0]
        if (w2 & 0x7F800000) != 0x11000000:
            continue
        sf = (w2 >> 31) & 1
        op = (w2 >> 30) & 1
        rn = (w2 >> 5) & 0x1F
        sh2 = (w2 >> 22) & 0x3F
        imm2 = (w2 >> 10) & 0xFFF
        if sh2 == 1:
            imm2 <<= 12
        elif sh2 != 0:
            continue
        if sf == 0 or op != 0:
            continue
        val = page + imm2
        if val in targets and rn == rd:
            hits.append((base + i, base + i + 4 * j, val, rd))

for a, b, t, r in hits:
    print("  adrp 0x%x  ->  add 0x%x   => 0x%x  (x%d)" % (a, b, t, r))
if not hits:
    print("  (没有 ADRP+ADD 直接引用)")
