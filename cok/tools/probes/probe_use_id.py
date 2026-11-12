#!/usr/bin/env python3
"""`item.use` 的参数到底是 uuid 还是 id? —— 2026-11-10 决定性实验。

背景: `item.buy` 的参数名是 **`id`**(不是 itemId!), 响应还直接带 `item.uuid`。
      如果 `item.use` 也是 `{id, num}`, 那**根本不需要道具实例 uuid** ——
      整个「拿不到背包 uuid」的死结就消失了。

本脚本: 记录喝药前后的体力, 验证 `item.use {id, num}` 是否真能用掉一瓶药水。
        会真实消耗 1 瓶体力药水(200381 = 50 体力)。

用法: python3 probe_use_id.py <gameUid> [itemId]
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
    tempfile.gettempdir(), 'cok-probe-ui-%d.lock' % os.getpid())

from cok_client import CokClient, account_lock, apply_account_types  # noqa: E402
from cok_sfs import TypedInt, SFS_INT                                 # noqa: E402
import cok_accounts as cas                                           # noqa: E402

uid = sys.argv[1] if len(sys.argv) > 1 else "<uid-guopan>"
item = sys.argv[2] if len(sys.argv) > 2 else "200381"

acc = apply_account_types(dict(cas.get_account(uid)))
cl = CokClient(timeout=15, account=acc)


def stam(tag):
    try:
        r = cl.call("autoQueue.status", {"status": 0}, retries=1)
        p = r.get("__params__") or {}
        v = p.get("stamina")
        print("    体力[%s] = %s" % (tag, v), flush=True)
        return v
    except Exception as e:  # noqa: BLE001
        print("    体力[%s] 读失败: %s" % (tag, str(e)[:70]), flush=True)
        return None


def try_use(params, tag):
    t0 = time.time()
    try:
        r = cl.call("item.use", params, retries=1)
        p = r.get("__params__") or {}
        print("    item.use %-30s %5.2fs -> %s"
              % (tag, time.time() - t0, json.dumps(p, ensure_ascii=False)[:300]), flush=True)
        return p
    except Exception as e:  # noqa: BLE001
        print("    item.use %-30s %5.2fs ERR %s" % (tag, time.time() - t0, str(e)[:90]), flush=True)
        return None


with account_lock(timeout=5, purpose="probe", key=uid):
    cl.connect()
    cl.bin_handshake()
    cl.login()
    print("=== 基线 ===", flush=True)
    base = stam("before")

    print("\n=== A. item.use {id, num} (id = 道具模板 id) ===", flush=True)
    p = try_use({"id": item, "num": TypedInt(1, SFS_INT)}, "id+SFS_INT")
    if p and not p.get("errorCode"):
        after = stam("after")
        if base is not None and after is not None and after > base:
            print("  ★★★ 成功! 体力 %s -> %s (+%s) —— item.use 用的是 id, 不是 uuid!"
                  % (base, after, after - base), flush=True)
    if p and p.get("errorCode"):
        print("    (错误码 %s —— id 不行, 再试别的形态)" % p.get("errorCode"), flush=True)

    print("\n=== B. 其它形态 ===", flush=True)
    for tag, prm in [
        ("id+plain num", {"id": item, "num": 1}),
        ("itemId+count", {"itemId": item, "count": TypedInt(1, SFS_INT)}),
        ("id+count", {"id": item, "count": TypedInt(1, SFS_INT)}),
    ]:
        p2 = try_use(prm, tag)
        if p2 and not p2.get("errorCode"):
            after = stam("after " + tag)
            if base is not None and after is not None and after > base:
                print("  ★★★ 成功! 体力 %s -> %s" % (base, after), flush=True)
                break
        if p2 and p2.get("errorCode") == "E000000":
            print("    (连接可能已断, 后续命令不可信)", flush=True)
            break

    print("\n=== 最终体力 ===", flush=True)
    stam("final")
cl.close()
