#!/usr/bin/env python3
"""第二轮: native 独有道具命令 + item.use 的 uuid 语义 —— 2026-11-10。

候选:
  * `suggest.item.use` / `value.bag` / `value.keybag` / `value.shkeybag`
    —— native 独有命令, 从未探过
  * `item.use` 的 uuid 到底是不是 32hex 实例 id —— 也可能直接是 itemId 字符串
  * `use.item.on.target` 的参数形态

安全: 只用**假 uuid / 不存在的 itemId** 试探, 最多回 errorCode, 不会真消耗。

用法: python3 probe_item_use3.py <gameUid>
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
    tempfile.gettempdir(), 'cok-probe-iu3-%d.lock' % os.getpid())

from cok_client import CokClient, account_lock, apply_account_types  # noqa: E402
from cok_sfs import TypedInt, SFS_INT                                 # noqa: E402
import cok_accounts as cas                                           # noqa: E402

uid = sys.argv[1] if len(sys.argv) > 1 else "<uid-other>"
acc = apply_account_types(dict(cas.get_account(uid)))
cl = CokClient(timeout=10, account=acc)

FAKE = "0" * 32


def probe(cmd, params=None, tag=""):
    t0 = time.time()
    try:
        r = cl.call(cmd, params or {}, retries=1)
        p = r.get("__params__") or {}
        dt = time.time() - t0
        body = json.dumps(p, ensure_ascii=False)[:260]
        print("  %-24s %-20s %6.2fs  %s" % (cmd, tag, dt, body), flush=True)
        return ("ok", dt, p)
    except Exception as e:  # noqa: BLE001
        dt = time.time() - t0
        msg = str(e)
        kind = "超时" if ("超时" in msg or "无响应" in msg) else "异常"
        print("  %-24s %-20s %6.2fs  %s %s" % (cmd, tag, dt, kind, msg[:70]), flush=True)
        return (kind, dt, None)


with account_lock(timeout=5, purpose="probe", key=uid):
    cl.connect()
    cl.bin_handshake()
    cl.login()

    print("=== C. item.use 的 uuid 语义 (uuid=itemId 字符串?) ===", flush=True)
    probe("item.use", {"uuid": "200381", "num": TypedInt(1, SFS_INT)}, "uuid=itemId串")
    probe("item.use", {"uuid": "200381"}, "uuid=itemId串 无num")
    probe("item.use", {"uuid": "200380", "num": TypedInt(1, SFS_INT)}, "uuid=200380")

    print("\n=== D. native 独有道具命令 ===", flush=True)
    probe("suggest.item.use", {"itemId": "200381", "num": TypedInt(1, SFS_INT)}, "itemId")
    probe("suggest.item.use", {"uuid": FAKE, "num": TypedInt(1, SFS_INT)}, "假uuid")
    probe("suggest.item.use", {}, "空参")
    probe("value.bag", {}, "空参")
    probe("value.keybag", {}, "空参")
    probe("value.shkeybag", {}, "空参")
    probe("store.bag.show.des", {}, "空参")
    probe("change.bagtab.sel", {}, "空参")

    print("\n=== E. use.item.on.target 参数形态 ===", flush=True)
    for name, prm in [
        ("itemId+num", {"itemId": "200381", "num": TypedInt(1, SFS_INT)}),
        ("id+num", {"id": "200381", "num": TypedInt(1, SFS_INT)}),
        ("uuid+num", {"uuid": FAKE, "num": TypedInt(1, SFS_INT)}),
        ("uuid+itemId+num", {"uuid": FAKE, "itemId": "200381", "num": TypedInt(1, SFS_INT)}),
        ("type+itemId", {"type": 1, "itemId": "200381"}),
        ("target", {"target": 1, "itemId": "200381"}),
    ]:
        probe("use.item.on.target", prm, name)
cl.close()
