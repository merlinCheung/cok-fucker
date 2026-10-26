#!/usr/bin/env python3
"""列出所有 "bl <注册函数>" 调用点附近引用的消息名字符串。

注册模式(从 libgame.so 里读出来的):
    adrp x2, #<handler页>
    add  x2, x2, #<handler偏移>      ; x2 = 处理函数
    mov  x1, x19                     ; x1 = 消息名
    str  x2, [x29, #0x90]
    bl   <register_fn>               ; 注册
    ...
    adrp x1, #<名字页>
    add  x1, x1, #<名字偏移>         ; 消息名字符串
    bl   <strcmp_fn>

用法: python3 list_msg_names.py <libgame.so> <0xregister_fn>
"""
import re
import struct
import sys

P = sys.argv[1]
REG = int(sys.argv[2], 16)

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

strs = {}
for s in secs:
    if s["sname"].startswith(".rodata") or s["sname"].startswith(".data"):
        for m in re.finditer(rb"[ -~]{2,80}\x00", d[s["off"]:s["off"] + s["size"]]):
            strs.setdefault(s["addr"] + m.start(), m.group()[:-1].decode())

text = [s for s in secs if s["sname"] == ".text"][0]
base = text["addr"]
buf = d[text["off"]:text["off"] + text["size"]]

# 找所有 bl REG
sites = []
for i in range(0, len(buf) - 4, 4):
    w = struct.unpack_from("<I", buf, i)[0]
    if (w >> 26) == 0x25:
        imm = w & 0x3FFFFFF
        if imm & (1 << 25):
            imm -= (1 << 26)
        if base + i + (imm << 2) == REG:
            sites.append(base + i)
print("bl 0x%x 的调用点: %d 个" % (REG, len(sites)))

kw = sys.argv[3] if len(sys.argv) > 3 else None
for site in sites:
    # 名字字符串在注册**之后**(紧接着的 strcmp 用它)
    found = None
    for fwd in range(1, 18):
        idx = site + 4 * fwd - base
        if idx < 0 or idx + 4 > len(buf):
            break
        w = struct.unpack_from("<I", buf, idx)[0]
        if (w & 0x9F000000) != 0x90000000:
            continue
        rd = w & 0x1F
        imm = ((w >> 29) & 0x3) | (((w >> 5) & 0x7FFFF) << 2)
        if imm & (1 << 20):
            imm -= (1 << 21)
        page = ((base + idx) & ~0xFFF) + (imm << 12)
        for f2 in range(1, 8):
            j = idx + 4 * f2
            if j + 4 > len(buf):
                break
            w2 = struct.unpack_from("<I", buf, j)[0]
            if (w2 & 0xFFC00000) != 0x91000000:
                continue
            imm2 = (w2 >> 10) & 0xFFF
            sh2 = (w2 >> 22) & 0x3F
            if sh2 == 1:
                imm2 <<= 12
            elif sh2 != 0:
                continue
            rn = (w2 >> 5) & 0x1F
            if rn != rd:
                continue
            a = page + imm2
            if a in strs:
                found = strs[a]
                break
        if found:
            break
    if found and (kw is None or kw.lower() in found.lower()):
        print("   0x%x  %s" % (site, found))
