#!/usr/bin/env python3
"""解析 COK App 抓包(wire 层明文 SFS 帧), 输出命令名 + 解密后的 params。

为什么能拿到命令名:
  游戏协议帧 = [flags:1][len:2][SFS 载荷]
  载荷 = { p: { p: { params: <XOR 加密的字节数组> }, r: -1, c: "<命令名>" },
          a: 13, c: 1 }
  → 命令名在 **p.c**, params 在 **p.p.params**
  → 只要找到**游戏服的会话 XOR 密钥**就能解出 params

用法:
  python3 decode_capture.py <capture.jsonl> [--key HEXSTR]
"""
import argparse
import binascii
import collections
import json
import os
import sys

# cok_sfs 在 protocol/ 目录里
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.expanduser(
    "~/workspace/me/cok/COK-CN1-analysis/protocol"))
from cok_sfs import Reader, read_value, xor_buf  # noqa: E402


def frames(path):
    """产出 (dir, payload_bytes) —— 只取 SFS 明文帧(首字节 0x80)。"""
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                o = json.loads(line)
            except Exception:
                continue
            pl = (o.get("msg") or {}).get("payload") or {}
            if pl.get("t") != "w":
                continue
            try:
                b = binascii.unhexlify(pl["hex"])
            except Exception:
                continue
            if len(b) < 3 or b[0] != 0x80:
                continue
            ln = (b[1] << 8) | b[2]
            if 3 + ln > len(b):
                continue
            yield pl.get("dir"), b[3:3 + ln]


def parse_frame(payload):
    try:
        r = Reader(payload)
        return read_value(r)
    except Exception:
        return None


def collect(path):
    out = []
    for d, payload in frames(path):
        obj = parse_frame(payload)
        if not isinstance(obj, dict):
            continue
        p = obj.get("p")
        if not isinstance(p, dict):
            continue
        cmd = p.get("c")
        if not isinstance(cmd, str):
            continue
        pp = p.get("p")
        pb = pp.get("params") if isinstance(pp, dict) else None
        out.append((d, cmd, pb))
    return out


def find_game_key(path):
    """从抓包里找游戏服的 XOR 密钥。

    判据: 拿候选 key 去解某个**已知明文长度**的 params,
    解出来必须以 0x12(SFS_OBJECT)开头 —— 否则不是游戏服密钥。
    """
    cands = []
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                o = json.loads(line)
            except Exception:
                continue
            pl = (o.get("msg") or {}).get("payload") or {}
            if pl.get("t") == "key" and pl.get("key"):
                cands.append(pl["key"])
    return cands


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("capture")
    ap.add_argument("--key", help="游戏服会话 XOR 密钥(hex 或 ASCII)")
    ap.add_argument("--count", type=int, default=0, help="只统计前 N 个命令")
    ap.add_argument("--show", action="store_true", help="打印解密后的 params")
    ap.add_argument("--filter", help="只显示匹配的命令")
    args = ap.parse_args()

    rows = collect(args.capture)
    cmds = collections.Counter((d or "?") + ":" + c for d, c, _ in rows)
    print("=== 命令统计 (%d 帧) ===" % len(rows))
    for c, n in cmds.most_common():
        print("  %4d  %s" % (n, c))

    key = None
    if args.key:
        kb = binascii.unhexlify(args.key) if all(
            ch in "0123456789abcdefABCDEF" for ch in args.key) else args.key.encode()
        key = kb
    else:
        # 登录前后密钥会换 -> 逐个候选 key 试解, 取"解出最多帧"的那个
        cands = find_game_key(args.capture)
        best = (0, None, None)
        for cand in cands:
            kb = binascii.unhexlify(cand) if all(
                ch in "0123456789abcdefABCDEF" for ch in cand) else cand.encode()
            ok = 0
            for _d, _c, pb in rows:
                if not pb:
                    continue
                try:
                    blob = binascii.unhexlify(pb)
                    dec = xor_buf(blob, kb)
                    if dec and dec[0] == 0x12:
                        ok += 1
                except Exception:
                    continue
            if ok > best[0]:
                best = (ok, kb, cand)
        if best[1] is not None:
            key = best[1]
            print("\n[*] 命中游戏服 XOR 密钥: %s (可解 %d/%d 帧)" % (
                best[2], best[0], len(rows)))

    if args.show:
        print("\n=== params 明细 ===")
        shown = 0
        for d, c, pb in rows:
            if args.filter and args.filter not in c:
                continue
            print("--- %s (%s) ---" % (c, d))
            if not pb:
                print("    (无 params)")
                continue
            try:
                blob = binascii.unhexlify(pb)
            except Exception:
                print("    (非 hex)", str(pb)[:120])
                continue
            if key:
                try:
                    r = Reader(xor_buf(blob, key))
                    o = read_value(r)
                    print("   ", json.dumps(o, ensure_ascii=False)[:600])
                    continue
                except Exception as e:
                    print("    解密失败:", e)
            print("    hex:", pb[:120])
            shown += 1
            if args.count and shown >= args.count:
                break


if __name__ == "__main__":
    main()
