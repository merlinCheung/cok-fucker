#!/usr/bin/env python3
"""在 ELF64 arm64 二进制里找字符串的代码引用(ADRP+ADD), 并对比各字符串的引用簇。

用法: python3 elf_xref.py <libgame.so> <str1> [str2 ...]
"""
import struct
import sys
import pickle


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

    out = []
    for i in range(e_shnum):
        s = sh(i)
        s['sname'] = nm(s['name'])
        out.append(s)
    return out


def sext(v, bits):
    if v & (1 << (bits - 1)):
        v -= (1 << bits)
    return v


def find_string(d, secs, needle):
    b = needle.encode()
    # 优先精确 NUL 结尾的串, 避免匹配到更长名字的前缀
    # (如 "world.march" 误命中 "world.march.retreat")
    i = d.find(b + b"\x00")
    if i < 0:
        i = d.find(b)
    if i < 0:
        return None
    for s in secs:
        if s['sname'] == '.rodata' and s['off'] <= i < s['off'] + s['size']:
            return s['addr'] + (i - s['off'])
    return i  # rodata 之外就当作 addr==off


def scan_adrp(data, start, size, targets):
    """返回 {target_page: [(adrp_addr, rd)]}"""
    pages = {t & ~0xFFF for t in targets}
    hits = {}
    end = start + size
    # 只在 4 字节对齐处扫描
    for off in range(start, end - 4, 4):
        w = struct.unpack_from('<I', data, off)[0]
        if (w & 0x9F000000) != 0x90000000:
            continue
        immlo = (w >> 29) & 0x3
        immhi = (w >> 5) & 0x7FFFF
        imm = sext((immhi << 2) | immlo, 19) << 12
        page = (off & ~0xFFF) + imm
        if page in pages:
            hits.setdefault(page, []).append((off, w & 0x1F))
    return hits


def resolve_adds(data, adrps, target):
    """在 adrp 之后 12 条指令内找 add Xd, Xn, #lo12"""
    out = []
    lo = target & 0xFFF
    for off, rd in adrps:
        for k in range(1, 13):
            o = off + 4 * k
            w = struct.unpack_from('<I', data, o)[0]
            # ADD (immediate, 64-bit): 0x91000000 mask 0xFF000000
            if (w & 0xFF000000) == 0x91000000:
                imm12 = (w >> 10) & 0xFFF
                sh = (w >> 22) & 0x3
                rn = (w >> 5) & 0x1F
                if rn == rd and (imm12 << (12 if sh == 1 else 0)) == lo:
                    out.append(o)
                    break
    return out


def main():
    path = sys.argv[1]
    needles = sys.argv[2:]
    d = open(path, 'rb').read()
    secs = load_sections(d)
    text = [s for s in secs if s['sname'] == '.text'][0]

    targets = {}
    for n in needles:
        v = find_string(d, secs, n)
        targets[n] = v
        print('%-18s vaddr=%s' % (n, hex(v) if v is not None else 'NOT FOUND'))

    tv = [v for v in targets.values() if v is not None]
    print('\n扫描 .text (0x%x, %.1f MB) ...' % (text['addr'], text['size'] / 1048576.0))
    hits = scan_adrp(d, text['addr'], text['size'], tv)

    results = {}
    for n, v in targets.items():
        if v is None:
            results[n] = []
            continue
        page = v & ~0xFFF
        adrps = hits.get(page, [])
        adds = resolve_adds(d, adrps, v)
        results[n] = adds
        print('%-18s xref_add=%d  %s' % (n, len(adds), [hex(a) for a in adds[:8]]))

    # 聚类: 哪些字符串的引用落在同一个 4KB 窗口
    print('\n=== 引用簇(按 4KB 窗口) ===')
    buckets = {}
    for n, adds in results.items():
        for a in adds:
            buckets.setdefault(a & ~0xFFF, []).append((n, a))
    for win, items in sorted(buckets.items()):
        names = sorted(set(n for n, _ in items))
        if len(names) > 1:
            print('  win 0x%x : %s' % (win, names))
    pickle.dump(results, open('/tmp/xrefs.pkl', 'wb'))


if __name__ == '__main__':
    main()
