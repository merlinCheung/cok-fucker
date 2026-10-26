#!/usr/bin/env python3
"""在 ELF 的重定位表/数据段里找 {函数指针, 名字字符串} 这样的配对表。

用法: python3 find_handler_table.py <libgame.so> <0xFUNC_ADDR>
"""
import re
import struct
import sys

P = sys.argv[1]
TARGET = int(sys.argv[2], 16)

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


def vaddr_of(off):
    for s in secs:
        if s["off"] <= off < s["off"] + s["size"]:
            return s["addr"] + (off - s["off"]), s["sname"]
    return None, None


def str_at(v):
    for s in secs:
        if s["sname"].startswith(".rodata") or s["sname"].startswith(".dynstr"):
            if s["addr"] <= v < s["addr"] + s["size"]:
                so = s["off"] + (v - s["addr"])
                raw = d[so:so + 80].split(b"\x00")[0]
                if raw and all(32 <= c < 127 for c in raw):
                    return raw.decode()
    return None


# 1) 找所有指向 TARGET 的 8 字节字面量
pat = struct.pack("<Q", TARGET)
sites = [m.start() for m in re.finditer(re.escape(pat), d)]
print("字面量出现在文件偏移: %s" % [hex(s) for s in sites])

# 2) 找 .rela.dyn 里对该地址的重定位 -> 得到 GOT/数据槽
rela = [s for s in secs if s["sname"] == ".rela.dyn"]
if rela:
    r = rela[0]
    n = r["size"] // 24
    slots = []
    for i in range(n):
        o = r["off"] + i * 24
        r_offset, r_info, r_addend = struct.unpack_from("<QQq", d, o)
        if r_addend == TARGET:
            slots.append(r_offset)
    print("重定位槽(vaddr): %s" % [hex(s) for s in slots])
    for slot in slots:
        # 扫数据段里所有引用这个槽的 8 字节项
        needle = struct.pack("<Q", slot)
        for m in re.finditer(re.escape(needle), d):
            off = m.start()
            va, seg = vaddr_of(off)
            if va is None:
                continue
            if not (seg.startswith(".data") or seg.startswith(".rodata") or seg.startswith(".got")):
                continue
            print("  槽 0x%x 被 %s vaddr 0x%x 引用" % (slot, seg, va))
            for k in (-1, 1, 2):
                a = off + k * 8
                v = struct.unpack_from("<Q", d, a)[0]
                s = str_at(v)
                print("      [%+d] 0x%x  %s" % (k, v, s if s else ""))
