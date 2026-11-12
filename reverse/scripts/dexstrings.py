#!/usr/bin/env python3
"""Dump the DEX string pool from classes*.dex and mine API-related literals.

REA's Android bridge cannot disassemble <clinit>, so the constant values
(WS_SERVER_LIST_URL, APP_ID, protocol command names) are recovered directly
from the DEX string pool.
"""
import glob
import re
import struct
import sys


def read_uleb128(buf, off):
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


def dex_strings(path):
    with open(path, "rb") as fh:
        buf = fh.read()
    if buf[:4] != b"dex\n":
        return []
    size = len(buf)
    string_ids_size, string_ids_off = struct.unpack_from("<II", buf, 0x38)
    out = []
    for i in range(string_ids_size):
        (data_off,) = struct.unpack_from("<I", buf, string_ids_off + 4 * i)
        if data_off >= size:
            continue
        _, off = read_uleb128(buf, data_off)
        end = buf.find(b"\x00", off)
        if end < 0:
            continue
        raw = buf[off:end]
        try:
            out.append(raw.decode("utf-8", errors="replace"))
        except Exception:
            pass
    return out


def main():
    files = sorted(glob.glob(sys.argv[1] if len(sys.argv) > 1 else "/tmp/apkdex.*/classes*.dex"))
    all_strings = []
    for f in files:
        s = dex_strings(f)
        print("### %s -> %d strings" % (f, len(s)), file=sys.stderr)
        all_strings.extend(s)

    uniq = sorted(set(all_strings))

    print("=" * 70)
    print("=== URLs (http/https/ws/wss) ===")
    print("=" * 70)
    urls = set()
    for s in uniq:
        for m in re.finditer(r"(?:https?|wss?)://[^\s\"'<>\\\x00]{4,200}", s):
            urls.add(m.group(0))
    for u in sorted(urls):
        print("  ", u)

    print()
    print("=" * 70)
    print("=== host-like literals ===")
    print("=" * 70)
    hosts = set()
    for s in uniq:
        for m in re.finditer(r"\b(?:[a-zA-Z0-9-]+\.){1,4}(?:com|cn|net|org|io|co|cc|top|xyz|game|haier|hcg)\b", s):
            hosts.add(m.group(0))
    for h in sorted(hosts):
        print("  ", h)

    print()
    print("=" * 70)
    print("=== short path-like literals (possible API paths) ===")
    print("=" * 70)
    paths = set()
    for s in uniq:
        if 2 < len(s) < 90 and s.startswith("/") and " " not in s and "\\" not in s:
            if not s.startswith("//") and s.count("/") >= 1:
                paths.add(s)
    for p in sorted(paths):
        print("  ", p)


if __name__ == "__main__":
    main()
