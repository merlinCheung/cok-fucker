#!/usr/bin/env python3
"""还原 WorldMarchCommand 构造处的字符串顺序(字段名 -> 用途)。"""
import struct

SO = "/Users/a1234/workspace/me/cok/reverse/apk-extract/lib/arm64-v8a/libgame.so"
data = open(SO, "rb").read()

# 已知函数起点(从 ADRP 引用点倒推附近)
FUNCS = [0xc69c00, 0x144f900, 0x1475300, 0x147d100, 0x221bc00]


def cstr(addr):
    end = data.find(b"\x00", addr)
    try:
        return data[addr:end].decode("ascii", "ignore")
    except Exception:
        return "?"


def disasm_window(start, end):
    out = []
    i = start
    while i < end:
        w = struct.unpack_from("<I", data, i)[0]
        # ADRP
        if (w & 0x9F000000) == 0x90000000:
            immlo = (w >> 29) & 3
            immhi = (w >> 5) & 0x7FFFF
            imm = (immhi << 2) | immlo
            if imm & (1 << 20):
                imm -= 1 << 21
            page = (i & ~0xFFF) + (imm << 12)
            rd = w & 0x1F
            out.append((i, "adrp x%d, %#x" % (rd, page), rd, page))
            i += 4
            continue
        # ADD imm12
        if (w & 0xFF000000) == 0x91000000:
            imm = (w >> 10) & 0xFFF
            rn = (w >> 5) & 0x1F
            rd = w & 0x1F
            shift = (w >> 22) & 3
            if shift == 1:
                imm <<= 12
            out.append((i, "add x%d, x%d, %#x" % (rd, rn, imm), rn, None))
            i += 4
            continue
        i += 4
    return out


for fs in FUNCS:
    print("\n================ function near %#x ================" % fs)
    ins = disasm_window(fs, fs + 0x900)
    regs = {}
    for addr, txt, rn, page in ins:
        if page is not None:
            regs[rn] = page
        elif rn is not None and rn in regs and "add" in txt:
            full = regs[rn] + (int(txt.split(", ")[-1], 0))
            s = cstr(full)
            if s and all(32 <= ord(ch) < 127 for ch in s[:16]) and len(s) > 1:
                print("  %#x  %-28s -> %r" % (addr, txt, s))
