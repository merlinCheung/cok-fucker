#!/usr/bin/env python3
"""use.item.on.target 是不是真的在用道具 —— 2026-11-10。

现象: `use.item.on.target {itemId, num}` 恒回 {"success": true}(连不存在的道具
      也回 true), 所以要么它是空壳, 要么它真的按 itemId 用了道具。
      判定方法: 发之前后各读一次体力(autoQueue.status {status:0}, 零副作用)。

用法: python3 probe_use_on_target.py <gameUid> [itemId]
"""
import os
import sys
import tempfile
import time
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ['COK_ACCOUNT_LOCK_FILE'] = os.path.join(
    tempfile.gettempdir(), 'cok-probe-uot-%d.lock' % os.getpid())

from cok_client import CokClient, account_lock, apply_account_types  # noqa: E402
from cok_sfs import TypedInt, SFS_INT                                 # noqa: E402
import cok_accounts as cas                                           # noqa: E402

uid = sys.argv[1] if len(sys.argv) > 1 else "<uid-other>"
item = sys.argv[2] if len(sys.argv) > 2 else "200381"

acc = apply_account_types(dict(cas.get_account(uid)))
cl = CokClient(timeout=15, account=acc)


def stam(tag):
    try:
        r = cl.call("autoQueue.status", {"status": 0}, retries=1)
        p = r.get("__params__") or {}
        print("    体力[%s] = %s" % (tag, p.get("stamina")), flush=True)
        return p.get("stamina")
    except Exception as e:  # noqa: BLE001
        print("    体力[%s] 读失败 %s" % (tag, str(e)[:60]), flush=True)
        return None


def fire(cmd, params, tag):
    t0 = time.time()
    try:
        r = cl.call(cmd, params, retries=1)
        p = r.get("__params__") or {}
        print("    %-20s %-26s %5.2fs  %s" % (cmd, tag, time.time() - t0,
                                               json.dumps(p, ensure_ascii=False)[:220]), flush=True)
        return p
    except Exception as e:  # noqa: BLE001
        print("    %-20s %-26s %5.2fs  ERR %s" % (cmd, tag, time.time() - t0, str(e)[:70]), flush=True)
        return None


VARIANTS = [
    ("itemId+num", {"itemId": item, "num": 1}),
    ("itemId+num(SFS)", {"itemId": item, "num": TypedInt(1, SFS_INT)}),
    ("itemId+count", {"itemId": item, "count": 1}),
    ("itemId+num+target", {"itemId": item, "num": 1, "target": 0}),
    ("itemId+num+targetId", {"itemId": item, "num": 1, "targetId": 0}),
    ("itemId+num+type", {"itemId": item, "num": 1, "type": 1}),
    ("id+num", {"id": item, "num": 1}),
    ("itemId+num+toUid", {"itemId": item, "num": 1, "toUid": str(uid)}),
]

with account_lock(timeout=5, purpose="probe", key=uid):
    cl.connect()
    cl.bin_handshake()
    cl.login()
    print("=== 基线 ===", flush=True)
    base = stam("before")
    for tag, prm in VARIANTS:
        print("  -> %s" % tag, flush=True)
        fire("use.item.on.target", prm, tag)
        s = stam("after")
        if base is not None and s is not None and s != base:
            print("    ★★★ 体力变了! %s -> %s  (差 %s)" % (base, s, s - base), flush=True)
            base = s
        time.sleep(1)
    print("\n=== 结束体力 ===", flush=True)
    stam("final")
cl.close()
