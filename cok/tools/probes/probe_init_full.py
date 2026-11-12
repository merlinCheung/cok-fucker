#!/usr/bin/env python3
"""全量 dump 登录 init 的结构, 递归找道具表 —— 2026-11-10。

之前 probe_init_storage 只看了 storage/storageTotal/tool/tools/items/bag 五个键,
可能漏了别的键名(如 props/userTools)。这里把 init 全部顶层键打出来,
再递归搜任何含 32 位 hex(道具实例 uuid)或 200380/200381 的路径。

用法: python3 probe_init_full.py <gameUid>
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
import tempfile
import time
import json

_C = os.path.join(HERE, "..", "..", "core")
sys.path.insert(0, _C)
os.environ['COK_ACCOUNT_LOCK_FILE'] = os.path.join(
    tempfile.gettempdir(), 'cok-probe-initfull-%d.lock' % os.getpid())

from cok_client import CokClient, account_lock, apply_account_types  # noqa: E402
from cok_sfs import decode_params, parse_packet                       # noqa: E402
import cok_accounts as cas                                           # noqa: E402

uid = sys.argv[1] if len(sys.argv) > 1 else "<uid-other>"
acc = apply_account_types(dict(cas.get_account(uid)))
cl = CokClient(timeout=25, account=acc)

HEX32 = re.compile(r'^[0-9a-f]{32}$')


def brief(v, depth=0):
    if isinstance(v, dict):
        return "dict(%d) %s" % (len(v), list(v.keys())[:8])
    if isinstance(v, list):
        if not v:
            return "list(0)"
        return "list(%d) e0=%s" % (len(v), json.dumps(v[0], ensure_ascii=False)[:120])
    s = str(v)
    return s[:120]


def walk(node, path, out):
    """递归找含 uuid / 体力药水的路径"""
    if isinstance(node, dict):
        for k, v in node.items():
            if isinstance(v, str) and (HEX32.match(v) or v in ("200380", "200381", "200382")):
                out.append((path + "." + str(k), v))
            walk(v, path + "." + str(k), out)
    elif isinstance(node, list):
        for i, v in enumerate(node[:50]):
            if isinstance(v, str) and (HEX32.match(v) or v in ("200380", "200381", "200382")):
                out.append(("%s[%d]" % (path, i), v))
            walk(v, "%s[%d]" % (path, i), out)


with account_lock(timeout=5, purpose="probe", key=uid):
    cl.connect()
    cl.bin_handshake()
    cl.login()
    cl.sock.settimeout(3.0)
    buf = b""
    t0 = time.time()
    init = None
    while time.time() - t0 < 20 and init is None:
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
                for k, v in pp.items():
                    if isinstance(v, str) and len(v) > 60 and k != "qqq":
                        try:
                            o2, _, _ = decode_params(bytes.fromhex(v), cl.key)
                            init = o2
                            print("init 来自字段 %s" % k, flush=True)
                        except Exception:  # noqa: BLE001
                            pass
            i += 3 + ln
        buf = buf[i:]

    if not init:
        print("!! 没拿到 init")
        sys.exit(1)

    print("\n=== init 全部 %d 个顶层键 ===" % len(init), flush=True)
    for k in sorted(init.keys()):
        print("  %-24s %s" % (k, brief(init[k])), flush=True)

    hits = []
    walk(init, "", hits)
    print("\n=== 递归命中 (32hex uuid / 体力药水 id) 共 %d 处 ===" % len(hits), flush=True)
    for p, v in hits[:60]:
        print("  %-70s = %s" % (p, v), flush=True)

    # 顺便找所有"看起来像背包"的 dict: 值是 dict 且键是 6 位数字
    print("\n=== 疑似背包 (dict 的键为数字 itemId) ===", flush=True)

    def find_bags(node, path):
        if isinstance(node, dict):
            keys = list(node.keys())
            if len(keys) >= 3 and sum(1 for k in keys if re.match(r'^\d{5,7}$', str(k))) >= 3:
                print("  %s  %d 项, 样例 %s"
                      % (path, len(keys),
                         json.dumps({k: node[k] for k in keys[:3]}, ensure_ascii=False)[:300]), flush=True)
            for k, v in node.items():
                find_bags(v, path + "." + str(k))
        elif isinstance(node, list):
            for i, v in enumerate(node[:20]):
                find_bags(v, "%s[%d]" % (path, i))

    find_bags(init, "")
cl.close()
