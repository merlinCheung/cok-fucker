#!/usr/bin/env python3
"""探查登录 init 响应里的背包(storage)结构 —— 2026-11-10。

背包数据不一定有独立的"拉背包"命令(实测 `cemetery.get.info` /
`show.status.item` / `itemcollection.data` 都不返回 items),
客户端的道具表来自**登录 init 的 storage**。
这里把 init 的 storage / storageTotal 解开看看能不能拿到
`{itemId: {uuid, count, ...}}`。

用法: python3 probe_init_storage.py <gameUid>
"""
import os
import sys
import tempfile
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ['COK_ACCOUNT_LOCK_FILE'] = os.path.join(
    tempfile.gettempdir(), 'cok-probe-init-%d.lock' % os.getpid())

from cok_client import CokClient, account_lock, apply_account_types  # noqa: E402
from cok_sfs import decode_params, parse_packet                       # noqa: E402
import cok_accounts as cas                                           # noqa: E402

uid = sys.argv[1] if len(sys.argv) > 1 else "<uid-other>"
acc = apply_account_types(dict(cas.get_account(uid)))
cl = CokClient(timeout=25, account=acc)

with account_lock(timeout=5, purpose="probe", key=uid):
    cl.connect()
    cl.bin_handshake()
    cl.login()
    # 吃掉 init 推送
    cl.sock.settimeout(8)
    buf = b""
    try:
        while True:
            ch = cl.sock.recv(65536)
            if not ch:
                break
            buf += ch
    except Exception:  # noqa: BLE001
        pass
    i = 0
    init = None
    while i + 3 <= len(buf):
        flags = buf[i]
        ln = (buf[i + 1] << 8) | buf[i + 2]
        if not (flags & 0x80) or ln == 0 or i + 3 + ln > len(buf):
            break
        try:
            fl, pl, obj, cons = parse_packet(buf[i:i + 3 + ln])
        except Exception:  # noqa: BLE001
            break
        pp = cl._resp_params(obj)
        rcmd = cl._resp_cmd(obj)
        if rcmd == "init":
            for k, v in pp.items():
                if isinstance(v, str) and len(v) > 60 and k != "qqq":
                    try:
                        o2, m2, raw = decode_params(bytes.fromhex(v), cl.key)
                        init = o2
                        print("init 来自字段 %s (len=%d)" % (k, len(v)), flush=True)
                    except Exception as e:  # noqa: BLE001
                        print("  字段 %s 解不开: %s" % (k, str(e)[:80]), flush=True)
        i += 3 + ln
    if not init:
        print("!! 没拿到 init", flush=True)
    else:
        print("init 顶层键:", sorted(init.keys())[:60], flush=True)
        for key in ("storage", "storageTotal", "tool", "tools", "items", "bag"):
            if key not in init:
                continue
            v = init[key]
            print("\n--- init[%s] type=%s" % (key, type(v).__name__), flush=True)
            if isinstance(v, dict):
                print("    键数 %d, 前 12 个:" % len(v), flush=True)
                for k2, v2 in list(v.items())[:12]:
                    s = json.dumps(v2, ensure_ascii=False)[:220]
                    print("      %s = %s" % (k2, s), flush=True)
            elif isinstance(v, list):
                print("    长度 %d, 前 6 个:" % len(v), flush=True)
                for v2 in v[:6]:
                    print("      %s" % json.dumps(v2, ensure_ascii=False)[:220], flush=True)
            else:
                print("    %s" % str(v)[:400], flush=True)
        # 找所有带 item/uuid 的键
        print("\n=== 含 uuid / itemId 的 init 字段 ===", flush=True)
        for k, v in init.items():
            s = json.dumps(v, ensure_ascii=False)
            if "uuid" in s and ("itemId" in s or "item_id" in s):
                print("  %s -> %s" % (k, s[:300]), flush=True)
cl.close()
