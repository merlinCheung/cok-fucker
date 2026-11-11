#!/usr/bin/env python3
"""`suggest.item.use` 参数专项 —— 2026-11-10。

已知: 该命令**存在**且秒回 E100165(道具数量不足) —— 说明它按 itemId 定位到了道具,
但"数量"没传对(默认 0 → 不足)。这里枚举数量的字段名 / 类型。

注意: 一旦参数组合命中, 会**真的消耗一瓶药水**(200381 = 50 体力),
      这是预期内的验证。

用法: python3 probe_suggest_use.py <gameUid> [itemId]
"""
import os
import sys
import tempfile
import time
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ['COK_ACCOUNT_LOCK_FILE'] = os.path.join(
    tempfile.gettempdir(), 'cok-probe-sugg-%d.lock' % os.getpid())

from cok_client import CokClient, account_lock, apply_account_types  # noqa: E402
from cok_sfs import TypedInt, SFS_INT                                 # noqa: E402
import cok_accounts as cas                                           # noqa: E402

uid = sys.argv[1] if len(sys.argv) > 1 else "<uid-other>"
item = sys.argv[2] if len(sys.argv) > 2 else "200381"

acc = apply_account_types(dict(cas.get_account(uid)))
cl = CokClient(timeout=12, account=acc)

FIELDS = ["num", "count", "number", "itemNum", "useNum", "n", "amount",
          "useNum", "useCount", "num2", "quantity", "cnt", "times", "value"]


def probe(params, tag):
    t0 = time.time()
    try:
        r = cl.call("suggest.item.use", params, retries=1)
        p = r.get("__params__") or {}
        dt = time.time() - t0
        body = json.dumps(p, ensure_ascii=False)[:300]
        mark = "  <<<< 成功!" if not p.get("errorCode") else ""
        print("  %-40s %6.2fs  %s%s" % (tag, dt, body, mark), flush=True)
        return p
    except Exception as e:  # noqa: BLE001
        dt = time.time() - t0
        print("  %-40s %6.2fs  ERR %s" % (tag, dt, str(e)[:80]), flush=True)
        return None


with account_lock(timeout=5, purpose="probe", key=uid):
    cl.connect()
    cl.bin_handshake()
    cl.login()

    print("=== A. 数量字段名枚举 (itemId=%s) ===" % item, flush=True)
    for f in FIELDS:
        probe({"itemId": item, f: 1}, "itemId + %s=1(plain)" % f)

    print("\n=== B. 数量字段名枚举 (SFS INT 编码) ===", flush=True)
    for f in FIELDS:
        probe({"itemId": item, f: TypedInt(1, SFS_INT)}, "itemId + %s=1(SFS_INT)" % f)

    print("\n=== C. 字符串数字 / 其它 id 字段名 ===", flush=True)
    for f in FIELDS:
        probe({"itemId": item, f: "1"}, 'itemId + %s="1"' % f)
    for idk in ("id", "itemid", "propId", "toolId", "goodsId", "itemId"):
        probe({idk: item, "num": 1}, "%s + num=1" % idk)

    print("\n=== D. 带 type/type2 ===", flush=True)
    for extra in ({"type": 3}, {"type2": 13}, {"type": 3, "type2": 13},
                  {"page": 4}, {"lv": 1}):
        p = {"itemId": item, "num": 1}
        p.update(extra)
        probe(p, "num=1 + %s" % json.dumps(extra))
cl.close()
