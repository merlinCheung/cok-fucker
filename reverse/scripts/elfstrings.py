#!/usr/bin/env python3
"""Resolve SFS2X constant symbols to their string values in libgame.so.

libgame.so is a PIE ELF; `KEY_*` / `SFSEvent::*` style globals are
`const char *` living in .data.rel.ro. We parse the ELF section headers
directly to build a VA -> file offset map (more precise than program
headers for this purpose), read the 8-byte pointer at each symbol, then
resolve the target string.

usage: elfstrings.py <libgame.so> [symbol-substring-filter ...]
"""
import struct
import sys

SHF_ALLOC = 0x2
SHT_DYNSYM = 11


def load(path):
    return open(path, "rb").read()


def sections(buf):
    """[(name, type, flags, addr, offset, size, link, entsize)]"""
    e_shoff, = struct.unpack_from("<Q", buf, 0x28)
    e_shentsize, e_shnum, e_shstrndx = struct.unpack_from("<HHH", buf, 0x3A)
    raw = []
    for i in range(e_shnum):
        off = e_shoff + i * e_shentsize
        raw.append(struct.unpack_from("<IIQQQQIIQQ", buf, off))
    # section names live in shstrtab
    shstr = raw[e_shstrndx]
    strbase, strsize = shstr[4], shstr[5]
    out = []
    for (nameoff, stype, flags, addr, offset, size, link, _info, _align, entsize) in raw:
        end = buf.find(b"\x00", strbase + nameoff, strbase + strsize)
        name = buf[strbase + nameoff:end].decode("utf-8", errors="replace")
        out.append((name, stype, flags, addr, offset, size, link, entsize))
    return out


def va_map(secs, buflen):
    """[(addr, size, offset)] for allocated sections that have file content.

    NOBITS sections (.bss) carry an sh_offset past EOF and must be skipped,
    otherwise a symbol that lives there maps to an unreadable file offset.
    """
    out = []
    for name, _t, flags, addr, offset, size, _l, _e in secs:
        if not (flags & SHF_ALLOC) or not size:
            continue
        if offset + size > buflen:
            continue
        out.append((addr, size, offset))
    return out


def va_to_off(vmap, va, size=1):
    for addr, sec_size, offset in vmap:
        if addr <= va and va + size <= addr + sec_size:
            return offset + (va - addr)
    return None


def cstr(buf, vmap, va, maxlen=512):
    off = va_to_off(vmap, va)
    if off is None:
        return None
    end = buf.find(b"\x00", off, off + maxlen)
    if end < 0:
        end = off + maxlen
    return buf[off:end].decode("utf-8", errors="replace")


def dynsyms(buf, secs):
    out = []
    for name, stype, _flags, _addr, offset, size, link, entsize in secs:
        if stype != SHT_DYNSYM or not entsize:
            continue
        strbase, strsize = secs[link][4], secs[link][5]
        for i in range(size // entsize):
            off = offset + i * entsize
            st_name, _st_info, _other, _shndx, st_value, _st_size = \
                struct.unpack_from("<IBBHQQ", buf, off)
            if st_name == 0:
                continue
            end = buf.find(b"\x00", strbase + st_name, strbase + strsize)
            out.append((st_value, buf[strbase + st_name:end].decode("utf-8", "replace")))
    return out


def main():
    path = sys.argv[1]
    filters = sys.argv[2:] or ["Sfs2X"]
    buf = load(path)
    secs = sections(buf)
    vmap = va_map(secs, len(buf))
    syms = dynsyms(buf, secs)

    rows = []
    for value, name in syms:
        if not any(f in name for f in filters):
            continue
        if value == 0:
            continue
        ptr_off = va_to_off(vmap, value, 8)
        if ptr_off is None:
            continue
        target, = struct.unpack_from("<Q", buf, ptr_off)
        if target == 0:
            continue
        s = cstr(buf, vmap, target)
        if not s or len(s) > 200:
            continue
        if not all(32 <= ord(c) < 127 for c in s):
            continue
        rows.append((name, value, s))

    rows.sort()
    print("# SFS2X 常量符号 → 字符串值 (libgame.so, %d 项)" % len(rows))
    print("# 格式: <符号>  @VA = \"<值>\"")
    print()
    for name, value, s in rows:
        print("%s\n    @0x%x = %r" % (name, value, s))


if __name__ == "__main__":
    main()
