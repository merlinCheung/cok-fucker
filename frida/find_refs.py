#!/usr/bin/env python3
"""在 AArch64 ELF 中找引用某个字符串地址的代码位置(ADRP+ADD 配对扫描)。

用法: python3 find_refs.py <elf> <string_addr_hex> [--max 20]
输出: 每处 "<code_addr>  <func_hint>"  (func_hint = 该地址前最近的 PAC/NOP 前的函数入口不可得时给 ±)
"""
import re
import struct
import sys


def adrp_target(insn, pc):
    if (insn & 0x9F000000) != 0x90000000:
        return None
    immlo = (insn >> 29) & 0x3
    immhi = (insn >> 5) & 0x7FFFF
    imm = (immhi << 2) | immlo
    if imm & (1 << 20):
        imm -= (1 << 21)
    return (pc & ~0xFFF) + (imm << 12)


def add_imm(insn):
    # ADD (immediate) 64-bit: sf=1 op=0 S=0 100010 sh(1) imm12 Rn Rd
    if (insn & 0x7F000000) != 0x11000000:
        return None
    if insn & 0x00200000:   # 32-bit variant
        return None
    return ((insn >> 10) & 0xFFF, (insn >> 5) & 0x1F, insn & 0x1F)


def main():
    path = sys.argv[1]
    target = int(sys.argv[2], 16)
    data = open(path, "rb").read()
    page = target & ~0xFFF
    off = target & 0xFFF
    hits = []
    n = len(data)
    i = 0
    while i + 4 <= n:
        insn = struct.unpack_from("<I", data, i)[0]
        t = adrp_target(insn, i)
        if t == page:
            rd = insn & 0x1F
            for j in range(1, 9):
                k = i + 4 * j
                if k + 4 > n:
                    break
                ins2 = struct.unpack_from("<I", data, k)[0]
                a = add_imm(ins2)
                if a and a[1] == rd and a[0] == off:
                    hits.append((i, k))
                    break
                if adrp_target(ins2, k) is not None:
                    break
        i += 4
    print("目标 0x%x (page 0x%x, off 0x%x) -> 命中 %d 处" % (target, page, off, len(hits)))
    for a, b in hits[:40]:
        print("  adrp @ 0x%x   add @ 0x%x" % (a, b))


if __name__ == "__main__":
    main()
