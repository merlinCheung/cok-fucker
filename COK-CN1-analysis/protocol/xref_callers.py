#!/usr/bin/env python3
"""反向定位: 哪个命令的响应处理函数会用 'useritemlist' —— 2026-11-10。

思路:
  1. xref 找到引用 'useritemlist' 字符串的函数入口 F
  2. 扫 .text 找所有 `bl F` 的调用点 C
  3. 反汇编 C 附近的函数, 找它引用的 .rodata 字符串(命令名/字段名)

用法: python3 xref_callers.py <libgame.so> <字符串> [目标函数入口]
"""
import re
import struct
import subprocess
import sys

RODATA_OFF = 0x2F8B690
RODATA_SIZE = 0x2358E5
TEXT_OFF = 0x8FF000
TEXT_SIZE = 0x268C68C
OBJDUMP = "/Library/Developer/CommandLineTools/usr/bin/llvm-objdump"


def find_str(data, s):
    b = s.encode() if isinstance(s, str) else s
    return [m.start() for m in re.finditer(re.escape(b), data)]


def adrp_pages(data):
    adrp = {}
    i = TEXT_OFF
    end = TEXT_OFF + TEXT_SIZE
    while i < end - 4:
        insn = struct.unpack_from("<I", data, i)[0]
        if (insn & 0x9F000000) == 0x90000000:
            immlo = (insn >> 29) & 3
            immhi = (insn >> 5) & 0x7FFFF
            imm = (immhi << 2) | immlo
            if imm & 0x100000:
                imm -= 0x200000
            adrp[(i, insn & 0x1F)] = (i & ~0xFFF) + (imm << 12)
        i += 4
    return adrp


def xrefs(data, adrp, target):
    out = []
    i = TEXT_OFF
    end = TEXT_OFF + TEXT_SIZE
    while i < end - 4:
        insn = struct.unpack_from("<I", data, i)[0]
        if (insn & 0x7F800000) == 0x11000000:
            rd = insn & 0x1F
            rn = (insn >> 5) & 0x1F
            sh = (insn >> 22) & 3
            imm12 = (insn >> 10) & 0xFFF
            if sh == 1:
                imm12 <<= 12
            base = adrp.get((i - 4, rn))
            if base is not None:
                tgt = base - imm12 if (insn & 0x40000000) else base + imm12
                if tgt == target:
                    out.append(i)
        i += 4
    return out


def bl_callers(data, func):
    out = []
    i = TEXT_OFF
    end = TEXT_OFF + TEXT_SIZE
    while i < end - 4:
        insn = struct.unpack_from("<I", data, i)[0]
        if (insn & 0xFC000000) == 0x94000000:
            imm = insn & 0x03FFFFFF
            if imm & 0x02000000:
                imm -= 0x04000000
            if i + (imm << 2) == func:
                out.append(i)
        i += 4
    return out


def disasm(binpath, lo, hi):
    cmd = [OBJDUMP, "-d", "--start-address=0x%x" % lo,
           "--stop-address=0x%x" % hi, binpath]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
    return r.stdout


def rodata_strings_near(data, adrp, lo, hi):
    """收集 [lo,hi) 里所有 adrp+add 指向的 .rodata 字符串"""
    hits = []
    i = lo
    while i < hi - 4:
        insn = struct.unpack_from("<I", data, i)[0]
        if (insn & 0x7F800000) == 0x11000000:
            rn = (insn >> 5) & 0x1F
            sh = (insn >> 22) & 3
            imm12 = (insn >> 10) & 0xFFF
            if sh == 1:
                imm12 <<= 12
            base = adrp.get((i - 4, rn))
            if base is not None:
                tgt = base + imm12
                if RODATA_OFF <= tgt < RODATA_OFF + RODATA_SIZE:
                    end = data.find(b"\x00", tgt, tgt + 200)
                    s = data[tgt:end]
                    try:
                        txt = s.decode("utf-8")
                    except Exception:  # noqa: BLE001
                        txt = repr(s)
                    if txt and all(32 <= ord(c) < 127 for c in txt):
                        hits.append((i, txt))
        i += 4
    return hits


def main():
    binpath = sys.argv[1]
    target_s = sys.argv[2]
    data = open(binpath, "rb").read()
    adrp = adrp_pages(data)
    offs = find_str(data, target_s)
    print("字符串 %r @ %s" % (target_s, [hex(o) for o in offs]))
    for off in offs:
        if not (RODATA_OFF <= off < RODATA_OFF + RODATA_SIZE):
            continue
        xs = xrefs(data, adrp, off)
        print("\n引用点: %s" % [hex(x) for x in xs])
        for x in xs:
            # 往上找函数入口: stp x29,x30,[sp,#-N]!
            fstart = x
            for back in range(0, 0x800, 4):
                cand = x - back
                if cand < TEXT_OFF:
                    break
                insn = struct.unpack_from("<I", data, cand)[0]
                if (insn & 0xFFC003E0) == 0xA9B003E0 or (insn & 0xFF0003E0) == 0xA90003E0:
                    if (insn & 0xFFC00000) == 0xA9800000 or (insn & 0xFFC00000) == 0xA9000000:
                        fstart = cand
                        break
            print("\n  --- 引用 0x%x, 函数入口 ~0x%x ---" % (x, fstart))
            callers = bl_callers(data, fstart)
            print("  调用者: %s" % [hex(c) for c in callers])
            for c in callers[:8]:
                lo = max(TEXT_OFF, c - 0x300)
                hi = c + 0x300
                strings = rodata_strings_near(data, adrp, lo, hi)
                print("   caller 0x%x 附近字符串: %s" % (c, [s for _, s in strings][:40]))


if __name__ == "__main__":
    main()
