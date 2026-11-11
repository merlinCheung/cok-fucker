#!/usr/bin/env python3
"""纯 Python 的 aarch64 ADRP/ADD xref 扫描器 (2026-11-10)。

libgame.so 已 strip, 没有符号表, 但 .rodata 的 file offset == vaddr,
所以可以用「ADRP 立即数 + ADD 立即数」把 .text 里的引用精确还原出来。

用法:
    python3 xref.py <libgame.so> <目标字符串> [输出函数前若干字节的反汇编]

输出: 所有引用该字符串的指令地址(以及 +/- 上下文里的其它字符串)。
"""
import re
import struct
import subprocess
import sys

RODATA_OFF = 0x2f8b690
RODATA_SIZE = 0x2358E5
TEXT_OFF = 0x8FF000
TEXT_SIZE = 0x268C68C


def find_str(data, s):
    b = s.encode() if isinstance(s, str) else s
    return [m.start() for m in re.finditer(re.escape(b), data)]


def scan_xrefs(data, target_addr, text_off=TEXT_OFF, text_size=TEXT_SIZE):
    """返回 [(insn_addr, kind)]"""
    out = []
    end = text_off + text_size
    i = text_off
    # 预扫: 记录每个 ADRP 的 (pc, rd, page)
    adrp = {}
    while i < end - 4:
        insn = struct.unpack_from("<I", data, i)[0]
        if (insn & 0x9F000000) == 0x90000000:
            immlo = (insn >> 29) & 3
            immhi = (insn >> 5) & 0x7FFFF
            imm = (immhi << 2) | immlo
            if imm & 0x100000:
                imm -= 0x200000
            rd = insn & 0x1F
            page = (i & ~0xFFF) + (imm << 12)
            adrp[(i, rd)] = page
        i += 4
    # 二扫: 找引用
    i = text_off
    while i < end - 4:
        insn = struct.unpack_from("<I", data, i)[0]
        # ADD/SUB immediate
        if (insn & 0x7F800000) == 0x11000000:
            rd = insn & 0x1F
            rn = (insn >> 5) & 0x1F
            sh = (insn >> 22) & 3
            imm12 = (insn >> 10) & 0xFFF
            if sh == 1:
                imm12 <<= 12
            base = adrp.get((i - 4, rn))
            if base is not None:
                if (insn & 0x40000000):  # SUB
                    tgt = base - imm12
                else:
                    tgt = base + imm12
                if tgt == target_addr:
                    out.append((i, "add"))
        # LDR unsigned immediate (64-bit): ldr Xt, [Xn, #imm12*size]
        if (insn & 0x3F400000) == 0x39400000 or (insn & 0xFFC00000) == 0xF9400000:
            rn = (insn >> 5) & 0x1F
            imm12 = (insn >> 10) & 0xFFF
            base = adrp.get((i - 4, rn))
            if base is not None and base + imm12 * 8 == target_addr:
                out.append((i, "ldr"))
        i += 4
    return out


def disasm(binpath, addr, back=64, fwd=160):
    lo = max(TEXT_OFF, addr - back)
    hi = min(TEXT_OFF + TEXT_SIZE, addr + fwd)
    cmd = ["llvm-objdump", "-d", "--start-address=0x%x" % lo,
           "--stop-address=0x%x" % hi, "-C", binpath]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        return r.stdout
    except Exception as e:  # noqa: BLE001
        return "disasm 失败: %s" % e


def main():
    binpath = sys.argv[1]
    target = sys.argv[2]
    data = open(binpath, "rb").read()
    offs = find_str(data, target)
    print("字符串 %r 出现于: %s" % (target, [hex(o) for o in offs]))
    if not offs:
        return
    for off in offs:
        # 找到字符串所在节, 假定 .rodata off==addr
        addr = off if RODATA_OFF <= off < RODATA_OFF + RODATA_SIZE else None
        if addr is None:
            print("  偏移 0x%x 不在 .rodata, 跳过" % off)
            continue
        print("\n=== 0x%x ===" % addr)
        xs = scan_xrefs(data, addr)
        print("  xref 数: %d" % len(xs))
        for a, kind in xs[:20]:
            print("  -> 0x%x (%s)" % (a, kind))
        for a, kind in xs[:6]:
            print(disasm(binpath, a))


if __name__ == "__main__":
    main()
