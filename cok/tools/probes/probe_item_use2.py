#!/usr/bin/env python3
"""item.use 参数形态 + 「拉背包」命令名 —— 2026-11-10。

阶段 A: item.use 是否接受 **itemId** 而不是实例 uuid
         (若接受, 整个"拿不到 uuid"的死结直接消失)
阶段 B: 扫一批可能的「拉背包」命令名(未知命令 = 超时, 已知 = 秒回)

用法: python3 probe_item_use2.py <gameUid>
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
    tempfile.gettempdir(), 'cok-probe-iu2-%d.lock' % os.getpid())

from cok_client import CokClient, account_lock, apply_account_types  # noqa: E402
from cok_sfs import TypedInt, SFS_INT                                 # noqa: E402
import cok_accounts as cas                                           # noqa: E402

uid = sys.argv[1] if len(sys.argv) > 1 else "<uid-other>"
acc = apply_account_types(dict(cas.get_account(uid)))
cl = CokClient(timeout=10, account=acc)

FAKE_UUID = "0" * 32


def probe(cmd, params=None, tag="", timeout_note=""):
    t0 = time.time()
    try:
        r = cl.call(cmd, params or {}, retries=1)
        p = r.get("__params__") or {}
        dt = time.time() - t0
        print("  %-24s %-18s %6.2fs  errorCode=%-10s 键=%s"
              % (cmd, tag, dt, p.get("errorCode"), list(p.keys())[:6]), flush=True)
        return ("ok", dt, p)
    except Exception as e:  # noqa: BLE001
        dt = time.time() - t0
        msg = str(e)
        kind = "超时" if ("超时" in msg or "无响应" in msg) else "异常"
        print("  %-24s %-18s %6.2fs  %s %s"
              % (cmd, tag, dt, kind, msg[:70]), flush=True)
        return (kind, dt, None)


with account_lock(timeout=5, purpose="probe", key=uid):
    cl.connect()
    cl.bin_handshake()
    cl.login()

    print("=== A. item.use 参数形态 (itemId vs uuid) ===", flush=True)
    probe("item.use", {"itemId": "200381", "num": TypedInt(1, SFS_INT)}, "itemId+SFSINT")
    probe("item.use", {"itemId": "200381", "num": 1}, "itemId+plainnum")
    probe("item.use", {"id": "200381", "num": TypedInt(1, SFS_INT)}, "id+SFSINT")
    probe("item.use", {"itemId": "200381", "count": TypedInt(1, SFS_INT)}, "itemId+count")
    probe("item.use", {"itemId": "200381"}, "itemId only")
    probe("item.use", {"uuid": FAKE_UUID, "num": TypedInt(1, SFS_INT)}, "假uuid")
    probe("item.use", {"type2": "1", "num": TypedInt(1, SFS_INT)}, "type2")

    print("\n=== A2. use.item.on.target 变体 ===", flush=True)
    probe("use.item.on.target", {"itemId": "200381", "num": TypedInt(1, SFS_INT)}, "itemId")
    probe("use.item.on.target", {"uuid": FAKE_UUID, "num": TypedInt(1, SFS_INT)}, "假uuid")

    print("\n=== B. 拉背包命令名扫描 ===", flush=True)
    cands = [
        "item.list", "item.all", "item.get", "item.info", "item.data", "item.query",
        "bag.get", "bag.list", "user.item.list", "user.item.get", "user.items",
        "tool.list", "tool.get", "tool.data", "tool.info", "tool.all",
        "props.get", "props.list", "user.props", "world.props",
        "world.item.list", "world.user.item", "world.user.props",
        "world.get.item", "world.get.props", "world.tool.list",
        "user.get.item", "user.get.props", "user.get.tools",
        "goods.list", "goods.get", "my.item.list",
    ]
    for c in cands:
        probe(c, {}, "试")
cl.close()
