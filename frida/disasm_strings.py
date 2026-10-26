#!/usr/bin/env python3
"""反汇编 ELF arm64 的一段, 列出其中引用到的所有字符串(按出现顺序)。

用法: python3 disasm_strings.py <libgame.so> <start_addr> <end_addr> [start_addr2 ...]
"""
import struct
import sys
import pickle
from capstone import Cs, CS_ARCH_ARM64, CS_MODE_ARM


def load_sections(d):
    e_shoff = struct.unpack_from('<Q', d, 0x28)[0]
    e_shentsize, e_shnum, e_shstrndx = struct.unpack_from('<HHH', d, 0x3a)

    def sh(i):
        o = e_shoff + i * e_shentsize
        name, typ, flags, addr, off, size, link, info, align, entsize = \
            struct.unpack_from('<IIQQQQIIQQ', d, o)
        return dict(name=name, addr=addr, off=off, size=size)

    st = sh(e_shstrndx)

    def nm(x):
        s = d[st['off'] + x:]
        return s.split(b'\x00')[0].decode()

    return [dict(sh(i), sname=nm(sh(i)['name'])) for i in range(e_shnum)]


def cstr_at(d, addr, maxlen=80):
    e = d.find(b'\x00', addr)
    if e < 0 or e - addr > maxlen:
        return None
    s = d[addr:e]
    if not s:
        return None
    try:
        t = s.decode('ascii')
    except UnicodeDecodeError:
        return None
    if not all(32 <= ord(c) < 127 for c in t):
        return None
    return t


def main():
    path = sys.argv[1]
    ranges = []
    for a in sys.argv[2:]:
        x = int(a, 16)
        ranges.append((x, x + 0x600))
    d = open(path, 'rb').read()
    secs = load_sections(d)
    md = Cs(CS_ARCH_ARM64, CS_MODE_ARM)
    md.detail = False

    for start, end in ranges:
        print('===== 0x%x .. 0x%x =====' % (start, end))
        code = d[start:end]
        # 跟踪 ADRP 寄存器 -> page
        regpage = {}
        seen = []
        for ins in md.disasm(code, start):
            m = ins.mnemonic
            op = ins.op_str
            if m == 'adrp':
                parts = op.split(',')
                reg = parts[0].strip()
                try:
                    page = int(parts[1].strip().lstrip('#'), 0)
                except ValueError:
                    continue
                regpage[reg] = page
            elif m in ('add', 'ldr') and '#' in op:
                parts = op.split(',')
                if len(parts) < 3:
                    continue
                base = parts[1].strip()
                if base not in regpage:
                    continue
                try:
                    imm = int(parts[2].strip().lstrip('#'), 0)
                except ValueError:
                    continue
                addr = regpage[base] + imm
                s = cstr_at(d, addr)
                if s and len(s) >= 2:
                    seen.append((ins.address, s))
        for a, s in seen:
            print('  0x%x  %r' % (a, s))


if __name__ == '__main__':
    main()
