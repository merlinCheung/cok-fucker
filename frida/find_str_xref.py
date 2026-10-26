#!/usr/bin/env python3
"""在 ELF arm64 的 .text 里找"某个字符串的 rodata 地址"被 ADRP+ADD 引用的位置。

用途: 找到"哪个函数读了这个参数字符串" -> 推断参数怎么传。
用法: python3 find_str_xref.py <libgame.so> <rodata_addr> [rodata_addr ...]

注意: AArch64 的 ADRP 立即数是 **页内偏移(<<12)**, 后续 ADD 的立即数是 **<<0**。
本脚本按 ADRP+ADD 组合匹配, 且容忍中间插入其它指令(最多 6 条)。
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
    _n, typ, flags, addr, off, size, link, info, align, entsize = \
        struct.unpack_from("<IIQQQQIIQQ", d, o)
    return _n, typ, flags, addr, off, size


sections = [sh(i) for i in range(e_shnum)]

# .text 段: 取**所有**可执行段(而不是第一个), 覆盖完整代码区
texts = []
for _nm, typ, _fl, addr, off, size in sections:
    nm = d[off:off + size].split(b"\0")[0].decode("utf-8", "replace")
    if nm == ".text":
        texts.append((addr, off, size))
if not texts:
    for _nm, typ, _fl, addr, off, size in sections:
        if typ == 1 and (_fl & 0x4):
            texts.append((addr, off, size))
print("[可执行段] %d 个" % len(texts))
for a,o,s_ in texts:
    print("   vaddr=0x%x off=0x%x size=0x%x" % (a,o,s_))

def decode_adrp(insn, pc):
    rd = insn & 0x1f
    imm = (insn >> 5) & 0x7ffff
    if imm & 0x40000:
        imm -= 0x80000
    return rd, (pc & ~0xfff) + (imm << 12)


def decode_add_imm(insn):
    rd = insn & 0x1f
    rn = (insn >> 5) & 0x1f
    imm = (insn >> 10) & 0xfff
    sh = (insn >> 22) & 1
    if sh:
        imm <<= 12
    return rd, rn, imm


hits = []
STEP = 4
for taddr, toff, tsize in texts:
    count = tsize // STEP
    for i in range(count):
        off = toff + i * STEP
        insn = struct.unpack_from("<I", d, off)[0]
        if (insn & 0x9f000000) != 0x90000000:   # ADRP
            continue
        pc = taddr + i * STEP
        rd, page = decode_adrp(insn, pc)
        for j in range(1, 7):
            if i + j >= count:
                break
            off2 = toff + (i + j) * STEP
            ins2 = struct.unpack_from("<I", d, off2)[0]
            if (ins2 & 0xff800000) != 0x91000000:  # ADD (immediate)
                continue
            rd2, rn2, imm2 = decode_add_imm(ins2)
            if rd2 != rd or rn2 != rd:
                continue
            full = page + imm2
            if full in targets:
                hits.append((pc, full))
            break

print("命中 %d 处:" % len(hits))
for pc, tgt in hits:
    print("  0x%x  ->  0x%x" % (pc, tgt))
