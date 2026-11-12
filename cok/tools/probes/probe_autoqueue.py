#!/usr/bin/env python3
"""探测 autoQueue.* 系列命令的返回 —— 2026-11-10。

目的:
  1. `autoQueue.data` 可能返回服务端自动打怪队列的完整状态(含道具/周卡)。
  2. 若服务端队列自带"体力不足自动喝药"(saveItems), 那我们的自建循环可以
     直接让服务端队列代劳, 绕开"拿不到道具实例 uuid"这个死结。

用法: python3 probe_autoqueue.py <gameUid>
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
import tempfile
import time
import json

_C = os.path.join(HERE, "..", "..", "core")
sys.path.insert(0, _C)
os.environ['COK_ACCOUNT_LOCK_FILE'] = os.path.join(
    tempfile.gettempdir(), 'cok-probe-aq-%d.lock' % os.getpid())

from cok_client import CokClient, account_lock, apply_account_types  # noqa: E402
from cok_sfs import TypedInt, SFS_INT                                 # noqa: E402
import cok_accounts as cas                                           # noqa: E402

uid = sys.argv[1] if len(sys.argv) > 1 else "<uid-other>"
acc = apply_account_types(dict(cas.get_account(uid)))
cl = CokClient(timeout=15, account=acc)


def probe(cmd, params=None):
    t0 = time.time()
    try:
        r = cl.call(cmd, params or {}, retries=1)
        p = r.get("__params__") or {}
        dt = time.time() - t0
        print("\n### %s  %.2fs" % (cmd, dt), flush=True)
        print(json.dumps(p, ensure_ascii=False, indent=1)[:4000], flush=True)
        return p
    except Exception as e:  # noqa: BLE001
        print("\n### %s  %.2fs  ERR %s" % (cmd, time.time() - t0, str(e)[:120]), flush=True)
        return None


with account_lock(timeout=5, purpose="probe", key=uid):
    cl.connect()
    cl.bin_handshake()
    cl.login()
    print("=== autoQueue.data ===", flush=True)
    probe("autoQueue.data")
    print("\n=== autoQueue.status {status:0} ===", flush=True)
    probe("autoQueue.status", {"status": 0})
    print("\n=== autoQueue.levelMaxMonster ===", flush=True)
    probe("autoQueue.levelMaxMonster")
    print("\n=== autoQueue.levelMaxBoss ===", flush=True)
    probe("autoQueue.levelMaxBoss")
    print("\n=== autoQueue.search {autoQueue:0} ===", flush=True)
    probe("autoQueue.search", {"autoQueue": 0})
cl.close()
