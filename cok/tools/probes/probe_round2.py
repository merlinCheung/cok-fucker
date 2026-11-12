#!/usr/bin/env python3
"""第二轮零消耗探测 —— 2026-11-10。

目标:
  A. `suggest.item.use` 的参数也许要**数组**(协议里常见 `itemIdArr` 之类)
  B. native 里的 `msg.*` 推送名也许其实是可请求的命令
  C. 补测几个漏掉的 native 独有命令

全部用不存在的道具 id / 假 uuid, 最坏只回错误码。

用法: python3 probe_round2.py <gameUid>
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
    tempfile.gettempdir(), 'cok-probe-r2-%d.lock' % os.getpid())

from cok_client import CokClient, account_lock, apply_account_types  # noqa: E402
from cok_sfs import TypedInt, SFS_INT                                 # noqa: E402
import cok_accounts as cas                                           # noqa: E402

uid = sys.argv[1] if len(sys.argv) > 1 else "<uid-other>"
acc = apply_account_types(dict(cas.get_account(uid)))
cl = CokClient(timeout=9, account=acc)

FAKE = "0" * 32
BAD = "999999"          # 不存在的道具


def probe(cmd, params=None, tag=""):
    t0 = time.time()
    try:
        r = cl.call(cmd, params or {}, retries=1)
        p = r.get("__params__") or {}
        body = json.dumps(p, ensure_ascii=False)[:200]
        print("  %-26s %-28s %5.2fs  %s" % (cmd, tag, time.time() - t0, body), flush=True)
        return p
    except Exception as e:  # noqa: BLE001
        dt = time.time() - t0
        msg = str(e)
        kind = "超时" if ("超时" in msg or "无响应" in msg) else "ERR"
        print("  %-26s %-28s %5.2fs  %s %s" % (cmd, tag, dt, kind, msg[:60]), flush=True)
        return None


with account_lock(timeout=5, purpose="probe", key=uid):
    cl.connect()
    cl.bin_handshake()
    cl.login()

    print("=== A. suggest.item.use 数组参数 ===", flush=True)
    for tag, prm in [
        ("itemIdArr+num", {"itemIdArr": [BAD], "num": 1}),
        ("itemIdArr+count", {"itemIdArr": [BAD], "count": 1}),
        ("itemIdArr+numArr", {"itemIdArr": [BAD], "numArr": [1]}),
        ("items+num", {"items": [BAD], "num": 1}),
        ("itemIds+num", {"itemIds": BAD, "num": 1}),
        ("uuidArr+num", {"uuidArr": [FAKE], "num": 1}),
        ("itemId+useAll", {"itemId": BAD, "num": 1, "useAll": 1}),
        ("itemId+all", {"itemId": BAD, "num": 1, "all": 1}),
        ("itemId+num+use", {"itemId": BAD, "num": 1, "use": 1}),
        ("itemId+num+source", {"itemId": BAD, "num": 1, "source": 1}),
        ("itemId+num+from", {"itemId": BAD, "num": 1, "from": 1}),
        ("itemId+num+type2", {"itemId": BAD, "num": 1, "type2": 13}),
        ("itemId+num+page", {"itemId": BAD, "num": 1, "page": 4}),
        ("itemId+num+isAll", {"itemId": BAD, "num": 1, "isAll": 1}),
        ("itemId+num+auto", {"itemId": BAD, "num": 1, "auto": 1}),
        ("itemId+num+flag", {"itemId": BAD, "num": 1, "flag": 1}),
        ("itemId+num+isAuto", {"itemId": BAD, "num": 1, "isAuto": 1}),
    ]:
        probe("suggest.item.use", prm, tag)

    print("\n=== B. msg.* 命令 ===", flush=True)
    for c in ("msg.tool.change", "msg.tool.hotget.return",
              "msg.userclassify.tools.arrive", "msg.tool.userclassifytype.change",
              "msg.play.equip.put"):
        probe(c, {}, "空参")

    print("\n=== C. 漏掉的 native 命令 ===", flush=True)
    for c in ("queue.tool", "tool.merchante.save.index", "use.tool.exp",
              "use.dragon.prestige.tool", "award.tree.item", "hot.item.get",
              "hot.item.refresh", "item.compose", "equire.get", "equire.info"):
        probe(c, {}, "空参")
cl.close()
