#!/usr/bin/env python3
"""`use.stamina.tool` 参数格式探测(2026-11-10)。

背景:
  * 客户端 Lua `UseToolView` 里点"使用体力药水"走的是 native 的
    `ToolController:call("useTool", itemId, count, true)`, native 内部
    按道具类型选命令, 体力药水对应 **`use.stamina.tool`**。
  * native 的参数拼法看不到(没符号), 只能**真机试**。

试的几种参数形状(按候选顺序):
  1. {itemId, num}
  2. {itemId, count}
  3. {id, num}
  4. {itemId}
  5. {uuid, num}          ← uuid 从登录 init / 背包快照拿
  6. {itemId, num, type}  ← 有的游戏要带 type

⚠️ 成功的那一次会**真的消耗**体力药水。

用法: python3 probe_use_stamina.py <gameUid> [itemId]
"""
import os
import sys
import tempfile
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ['COK_ACCOUNT_LOCK_FILE'] = os.path.join(
    tempfile.gettempdir(), 'cok-probe-usestam-%d.lock' % os.getpid())

import cok_hunt as H                                       # noqa: E402
from cok_client import CokClient, account_lock, apply_account_types  # noqa: E402
from cok_sfs import TypedInt, SFS_INT                      # noqa: E402
import cok_accounts as cas                                 # noqa: E402

uid = sys.argv[1] if len(sys.argv) > 1 else "<uid-other>"
item_id = sys.argv[2] if len(sys.argv) > 2 else "200381"

acc = apply_account_types(dict(cas.get_account(uid)))
cl = CokClient(timeout=25, account=acc)


def snap():
    st = H.read_stamina(cl)
    return int(st.get("stamina") or 0), st


def try_params(params, tag):
    st0, _ = snap()
    try:
        r = cl.call("use.stamina.tool", params, retries=1)
    except Exception as e:  # noqa: BLE001
        print("  [%s] 异常 %s" % (tag, str(e)[:100]), flush=True)
        return None
    p = r.get("__params__") or {}
    err = p.get("errorCode")
    time.sleep(1.2)
    st1, raw = snap()
    delta = st1 - st0
    print("  [%s] errorCode=%s 体力 %s -> %s (Δ%s) 响应键=%s"
          % (tag, err, st0, st1, delta, [k for k in p.keys()][:8]), flush=True)
    if delta > 0:
        return delta
    return None


with account_lock(timeout=5, purpose="probe", key=uid):
    cl.connect()
    cl.bin_handshake()
    cl.login()
    print("道具 %s" % item_id, flush=True)

    cands = [
        ({"itemId": item_id, "num": TypedInt(1, SFS_INT)}, "itemId+num(INT)"),
        ({"itemId": item_id, "num": 1}, "itemId+num(plain)"),
        ({"itemId": item_id, "count": TypedInt(1, SFS_INT)}, "itemId+count(INT)"),
        ({"id": item_id, "num": TypedInt(1, SFS_INT)}, "id+num(INT)"),
        ({"itemId": item_id}, "itemId only"),
        ({"itemId": item_id, "num": TypedInt(1, SFS_INT), "type": 1},
         "itemId+num+type"),
        ({"itemId": item_id, "num": TypedInt(1, SFS_INT), "opFrom": "0"},
         "itemId+num+opFrom"),
    ]
    for params, tag in cands:
        d = try_params(params, tag)
        if d:
            print("\n✅ 命中: %s -> %s  体力 +%s" % (tag, params, d), flush=True)
            break
        print("    (未生效, 继续下一个)", flush=True)
    else:
        print("\n❌ 所有候选都没生效", flush=True)
cl.close()
