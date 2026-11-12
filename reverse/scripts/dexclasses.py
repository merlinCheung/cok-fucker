#!/usr/bin/env python3
"""Class inventory from DEX class_defs (exact, not string-pool heuristics).

Parses header -> type_ids -> class_defs -> string_ids to recover every
defined class descriptor, then aggregates by package.
"""
import glob
import struct
import sys
import collections


def uleb128(buf, off):
    result = 0
    shift = 0
    while True:
        b = buf[off]
        off += 1
        result |= (b & 0x7F) << shift
        if not (b & 0x80):
            break
        shift += 7
    return result, off


def dex_class_names(path):
    buf = open(path, "rb").read()
    if buf[:4] != b"dex\n":
        return []
    string_ids_size, string_ids_off = struct.unpack_from("<II", buf, 0x38)
    type_ids_size, type_ids_off = struct.unpack_from("<II", buf, 0x40)
    class_defs_size, class_defs_off = struct.unpack_from("<II", buf, 0x60)

    def string_at(idx):
        (data_off,) = struct.unpack_from("<I", buf, string_ids_off + 4 * idx)
        _, off = uleb128(buf, data_off)
        end = buf.find(b"\x00", off)
        return buf[off:end].decode("utf-8", errors="replace")

    names = []
    for i in range(class_defs_size):
        class_idx, = struct.unpack_from("<I", buf, class_defs_off + 32 * i)
        descriptor_idx, = struct.unpack_from("<I", buf, type_ids_off + 4 * class_idx)
        names.append(string_at(descriptor_idx))
    return names


def main():
    files = sorted(glob.glob(sys.argv[1] if len(sys.argv) > 1 else "/tmp/apkdex.*/classes*.dex"))
    all_classes = []
    for f in files:
        n = dex_class_names(f)
        print("### %s -> %d classes" % (f, len(n)), file=sys.stderr)
        all_classes.extend(n)

    print("定义类总数:", len(all_classes), "| 去重:", len(set(all_classes)))

    # 统计各顶层命名空间的类数量
    top = collections.Counter()
    for c in all_classes:
        if not c.startswith("L"):
            continue
        body = c[1:].rstrip(";")
        parts = body.split("/")
        if len(parts) >= 2:
            top[".".join(parts[:2])] += 1
        elif parts:
            top[parts[0]] += 1

    print("\n=== 命名空间类数量 (top 45) ===")
    for ns, n in top.most_common(45):
        print("  %-46s %5d" % (ns, n))

    # 应用自有包明细
    print("\n=== 应用自有包 (com.clash / com.hcg / org.hcg) 类清单 ===")
    own = sorted(c for c in set(all_classes)
                 if c.startswith(("Lcom/clash/", "Lcom/hcg/", "Lorg/hcg/")))
    for c in own:
        print("  ", c.replace("/", ".").rstrip(";"))
    print("  小计:", len(own))


if __name__ == "__main__":
    main()
