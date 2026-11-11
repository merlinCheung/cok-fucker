#!/usr/bin/env python3
"""定位 'useritemlist' 所在函数 → 调用者 → 调用者引用的字符串 —— 2026-11-10。

用法:
    python3 locate_bag_cmd.py <libgame.so> <字符串> [函数入口]
不带函数入口时自动往上找最近的 `stp x29,x30,[sp,#-N]!` prologue。
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


def find_prologue(data, addr):
    """往上找最近的 stp x29,x30,[sp,#-N]!"""
    for back in range(0, 0x1000, 4):
        c = addr - back
        if c < TEXT_OFF:
            break
        insn = struct.unpack_from("<I", data, c)[0]
        # stp x29, x30, [sp, #imm]!  -> 1010 1001 00 imm7 11110 011001
        if (insn & 0xFFE00000) == 0xA9800000 and (insn & 0x003F0000) == 0x00300000:
            return c
        if (insn & 0x7FC00000) == 0xA9000000 and (insn & 0x003F0000) == 0x00300000:
            return c
    return None


def rodata_strings_near(data, adrp, lo, hi):
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
                        txt = ""
                    if txt and all(32 <= ord(c) < 127 for c in txt) and len(txt) > 2:
                        hits.append((i, txt))
        i += 4
    return hits


def disasm(binpath, lo, hi):
    r = subprocess.run([OBJDUMP, "-d", "--start-address=0x%x" % lo,
                        "--stop-address=0x%x" % hi, binpath],
                       capture_output=True, text=True, timeout=180)
    return r.stdout


def main():
    binpath = sys.argv[1]
    target_s = sys.argv[2]
    data = open(binpath, "rb").read()
    adrp = adrp_pages(data)
    offs = find_str(data, target_s)
    print("字符串 %r @ %s" % (target_s, [hex(o) for o in offs]))
    forced = int(sys.argv[3], 0) if len(sys.argv) > 3 else None
    for off in offs:
        if not (RODATA_OFF <= off < RODATA_OFF + RODATA_SIZE):
            continue
        for x in xrefs(data, adrp, off):
            fstart = forced if forced else find_prologue(data, x)
            if not fstart:
                continue
            print("\n引用 0x%x, prologue ~0x%x" % (x, fstart))
            for F in {fstart}:
                callers = bl_callers(data, F)
                print("  F=0x%x 的调用者: %s" % (F, [hex(c) for c in callers]))
                for c in callers:
                    cg = find_prologue(data, c)
                    print("   caller 0x%x 所在函数 ~0x%x" % (c, cg))
                    strings = rodata_strings_near(data, adrp,
                                                 max(TEXT_OFF, c - 0x400),
                                                 min(TEXT_OFF + TEXT_SIZE, c + 0x400))
                    seen = []
                    for _, s in strings:
                        if s not in seen:
                            seen.append(s)
                    print("     引用字符串: %s" % seen[:50])
                    # 再往上: 调用者的调用者
                    if cg:
                        cc = bl_callers(data, cg)
                        print("     上层调用者: %s" % [hex(x) for x in cc][:10])
                        for x2 in cc[:5]:
                            s2 = rodata_strings_near(data, adrp,
                                                    max(TEXT_OFF, x2 - 0x600),
                                                    min(TEXT_OFF + TEXT_SIZE, x2 + 0x200))
                            u = []
                            for _, s in s2:
                                if s not in u:
                                    u.append(s)
                            print("       0x%x -> %s" % (x2, u[:60]))


if __name__ == "__main__":
    main()
