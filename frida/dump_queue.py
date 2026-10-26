#!/usr/bin/env python3
"""打印 build.info 的完整 buildingQueue 字段(找 qid / uuid 等)。"""
import json
import os
import sys

PROTO = "/Users/a1234/workspace/me/cok/COK-CN1-analysis/protocol"
sys.path.insert(0, PROTO)
from cok_client import CokClient  # noqa: E402
import cok_account  # noqa: E402

acct = cok_account.load_account()
c = CokClient(account=acct, timeout=60.0)
c.connect()
c.login()
res = c.call("build.info", {}, retries=1)
params = res.get("__params__") or res
q = params.get("buildingQueue")
print("=== buildingQueue (%d 条) ===" % len(q or []))
for i, item in enumerate(q or []):
    print("--- [%d] ---" % i)
    for k, v in sorted(item.items()):
        if isinstance(v, dict):
            print("   %-22s = <obj> %s" % (k, json.dumps(v, ensure_ascii=False)[:180]))
        else:
            print("   %-22s = %r" % (k, v))
print()
print("=== 顶层键 ===", sorted(params.keys()))
