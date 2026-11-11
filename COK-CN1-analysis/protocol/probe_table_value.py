#!/usr/bin/env python3
"""扫 `get.table.value {type: N, params: ...}` —— 2026-11-10。

线索: native 里同一个函数同时引用了字符串 "params" / "useritemlist" / "itemId",
      而客户端 Lua 里 `get.table.value` 的用法正是:
          ret:initWithName("get.table.value")
          ret:putParam("type", CCInteger:create(1))
          ret:putParam("params", CCString:create(itemId))
      响应结构是 `params.<字段>`。
      => 某个 type 下, params 里可能就带 useritemlist(道具实例 uuid 列表)!

这里把 type 1..40 全扫一遍, 找返回里含 useritemlist / uuid 的。

用法: python3 probe_table_value.py <gameUid>
"""
import os
import re
import sys
import tempfile
import time
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ['COK_ACCOUNT_LOCK_FILE'] = os.path.join(
    tempfile.gettempdir(), 'cok-probe-gtv-%d.lock' % os.getpid())

from cok_client import CokClient, account_lock, apply_account_types  # noqa: E402
from cok_sfs import TypedInt, SFS_INT                                 # noqa: E402
import cok_accounts as cas                                           # noqa: E402

uid = sys.argv[1] if len(sys.argv) > 1 else "<uid-other>"
acc = apply_account_types(dict(cas.get_account(uid)))
cl = CokClient(timeout=12, account=acc)

HEX32 = re.compile(r'^[0-9a-f]{32}$')


def deep(obj, path, out, depth=0):
    if depth > 6:
        return
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, str) and HEX32.match(v):
                out.append((path + "." + str(k), v))
            deep(v, path + "." + str(k), out, depth + 1)
    elif isinstance(obj, list):
        for i, v in enumerate(obj[:50]):
            if isinstance(v, str) and HEX32.match(v):
                out.append(("%s[%d]" % (path, i), v))
            deep(v, "%s[%d]" % (path, i), out, depth + 1)


def probe(params, tag):
    t0 = time.time()
    try:
        r = cl.call("get.table.value", params, retries=1)
        p = r.get("__params__") or {}
        dt = time.time() - t0
        s = json.dumps(p, ensure_ascii=False)
        hits = []
        deep(p, "", hits)
        flag = ""
        if "useritemlist" in s:
            flag = " ★★★ 含 useritemlist"
        elif hits:
            flag = " ★ 含 uuid %d 处" % len(hits)
        print("  type=%-3s %-14s %5.2fs 键=%s%s" % (params.get("type"), tag, dt,
                                                      list(p.keys())[:5], flag), flush=True)
        if flag:
            print("      %s" % s[:900], flush=True)
        return p
    except Exception as e:  # noqa: BLE001
        dt = time.time() - t0
        msg = str(e)
        kind = "超时" if ("超时" in msg or "无响应" in msg) else "ERR"
        print("  type=%-3s %-14s %5.2fs %s" % (params.get("type"), tag, dt, kind), flush=True)
        return None


with account_lock(timeout=5, purpose="probe", key=uid):
    cl.connect()
    cl.bin_handshake()
    cl.login()

    print("=== A. type 1..40, params=200380 (体力药水 id) ===", flush=True)
    for t in range(1, 41):
        probe({"type": t, "params": "200380"}, "params=200380")

    print("\n=== B. type 1..40, 不带 params ===", flush=True)
    for t in range(1, 41):
        probe({"type": t}, "无params")
cl.close()
