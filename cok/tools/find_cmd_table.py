#!/usr/bin/env python3
"""在静态数据段里找「命令名 → 处理函数」表 —— 2026-11-10。

已知: 处理 'useritemlist' 的函数 F=0xfd9498 是**通过函数指针被调用**的(无 bl 调用者),
      说明它躺在命令分发表里。
做法: 扫 .data.rel.ro / .data / .rodata, 找 8 字节指针 == F 的位置,
      再看同一区域附近的**字符串指针**, 解引用出命令名。

用法: python3 find_cmd_table.py <libgame.so> <函数地址>
"""
import struct
import sys

RODATA_OFF = 0x2F8B690
RODATA_SIZE = 0x2358E5
# (name, off, size)
SECTIONS = [
    (".data.rel.ro", 0x3822440, 0x29F8A0),
    (".data", 0x3ADB000, 0x3A118),
    (".rodata", RODATA_OFF, RODATA_SIZE),
]


def cstr(data, off, maxlen=120):
    if off < 0 or off >= len(data):
        return None
    end = data.find(b"\x00", off, off + maxlen)
    if end < 0:
        return None
    s = data[off:end]
    try:
        t = s.decode("utf-8")
    except Exception:  # noqa: BLE001
        return None
    if not t or not all(32 <= ord(c) < 127 for c in t):
        return None
    return t


def main():
    binpath = sys.argv[1]
    func = int(sys.argv[2], 0)
    data = open(binpath, "rb").read()
    pat = struct.pack("<Q", func)
    print("找指针 %s ..." % hex(func))
    for name, off, size in SECTIONS:
        blob = data[off:off + size]
        pos = 0
        while True:
            i = blob.find(pat, pos)
            if i < 0:
                break
            at = off + i
            print("\n  %s @ file 0x%x (vaddr 0x%x)" % (name, at, at))
            # 往前后看 ±128 字节的 8 字节指针, 解引用成字符串
            seen = []
            for delta in range(-128, 136, 8):
                p = at + delta
                if p < 0 or p + 8 > len(data):
                    continue
                val = struct.unpack_from("<Q", data, p)[0]
                if RODATA_OFF <= val < RODATA_OFF + RODATA_SIZE:
                    s = cstr(data, val)
                    if s and len(s) > 2:
                        key = (delta, s)
                        if key not in seen:
                            seen.append(key)
            for delta, s in seen:
                mark = "  <<<" if delta == 0 else ""
                print("     %+5d  %s%s" % (delta, s, mark))
            pos = i + 1


if __name__ == "__main__":
    main()
