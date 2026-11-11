#!/usr/bin/env python3
"""解 init 响应的**每一个**加密字段并合并 —— 2026-11-10。

之前的探针只解了第一个"长 hex 字段"(其它字段被跳过), 如果 init 的 params
分成多个加密字段(比如 背包/建筑/队列 各占一个字段), 背包可能就藏在第二个字段里。

用法: python3 probe_init_allfields.py <gameUid>
"""
import os
import re
import sys
import tempfile
import time
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ['COK_ACCOUNT_LOCK_FILE'] = os.path.join(
    tempfile.gettempdir(), 'cok-probe-initall-%d.lock' % os.getpid())

from cok_client import CokClient, account_lock, apply_account_types  # noqa: E402
from cok_sfs import decode_params, parse_packet                       # noqa: E402
import cok_accounts as cas                                           # noqa: E402

uid = sys.argv[1] if len(sys.argv) > 1 else "<uid-other>"
acc = apply_account_types(dict(cas.get_account(uid)))
cl = CokClient(timeout=25, account=acc)

HEX32 = re.compile(r'^[0-9a-f]{32}$')
STAM = ("200380", "200381", "200382")


def walk(node, path, out):
    if isinstance(node, dict):
        for k, v in node.items():
            if isinstance(v, str) and (HEX32.match(v) or v in STAM):
                out.append((path + "." + str(k), v))
            walk(v, path + "." + str(k), out)
    elif isinstance(node, list):
        for i, v in enumerate(node[:80]):
            if isinstance(v, str) and (HEX32.match(v) or v in STAM):
                out.append(("%s[%d]" % (path, i), v))
            walk(v, "%s[%d]" % (path, i), out)


with account_lock(timeout=5, purpose="probe", key=uid):
    cl.connect()
    cl.bin_handshake()
    cl.login()
    cl.sock.settimeout(3.0)
    buf = b""
    t0 = time.time()
    fields = []
    while time.time() - t0 < 25 and not fields:
        try:
            ch = cl.sock.recv(65536)
        except Exception:  # noqa: BLE001
            continue
        if not ch:
            break
        buf += ch
        i = 0
        while i + 3 <= len(buf):
            flags = buf[i]
            ln = (buf[i + 1] << 8) | buf[i + 2]
            if not (flags & 0x80) or ln == 0 or i + 3 + ln > len(buf):
                break
            try:
                _, _, obj, _ = parse_packet(buf[i:i + 3 + ln])
            except Exception:  # noqa: BLE001
                break
            pp = cl._resp_params(obj)
            if cl._resp_cmd(obj) == "init":
                fields = [(k, v) for k, v in pp.items()]
                break
            i += 3 + ln
        buf = buf[i:]

    if not fields:
        print("!! 没拿到 init")
        sys.exit(1)

    print("init 共有 %d 个参数:" % len(fields), flush=True)
    for k, v in fields:
        print("  %-14s type=%s len=%s" % (k, type(v).__name__,
                                          len(v) if isinstance(v, str) else "-"), flush=True)

    merged = {}
    for k, v in fields:
        if not isinstance(v, str) or len(v) <= 60 or k == "qqq":
            continue
        try:
            o2, _, _ = decode_params(bytes.fromhex(v), cl.key)
        except Exception as e:  # noqa: BLE001
            print("  字段 %s 解不开: %s" % (k, str(e)[:60]), flush=True)
            continue
        print("\n>>> 字段 %s 解出 %d 个键: %s"
              % (k, len(o2), sorted(o2.keys())[:25]), flush=True)
        merged[k] = o2
        # 直接搜
        hits = []
        walk(o2, k, hits)
        if hits:
            print("    命中 %d:" % len(hits), flush=True)
            for p, val in hits[:30]:
                print("      %-60s = %s" % (p, val), flush=True)
        # 疑似背包
        for kk, vv in o2.items():
            if isinstance(vv, list) and vv and isinstance(vv[0], dict):
                keys = set(vv[0].keys())
                if {"itemId", "uuid"} & keys or "uuid" in keys:
                    print("    >>> 疑似道具列表 %s[%d]: %s"
                          % (kk, len(vv), json.dumps(vv[0], ensure_ascii=False)[:300]), flush=True)

    json.dump(merged, open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                        "init-fields-%s.json" % uid),
                           "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
    print("\n[*] 合并结果已落盘 init-fields-%s.json" % uid)
cl.close()
