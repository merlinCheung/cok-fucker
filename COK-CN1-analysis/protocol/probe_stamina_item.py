#!/usr/bin/env python3
"""体力药水(200380/200381/200382)读取 + 使用的真机探针(2026-11-10)。

要查清三件事:
  1. **实时读背包**: 哪条命令能拿到 `{itemId, uuid, count}` 列表
     (候选: `cemetery.get.info` / `show.status.item` / `itemcollection.data`)
  2. **使用协议**: `item.use` 的参数格式 —— 客户端 Lua:
     `utils.requestServer('item.use', {{"uuid",CCString:create(uuid)},
                                      {"num",CCInteger:create(count)}}, ...)`
  3. **效果**: 用掉 1 个 200380(10 体力) 后体力是不是真的 +10

⚠️ 会真实消耗 1 个体力药水。

用法: python3 probe_stamina_item.py <gameUid> [itemId] [num]
"""
import os
import sys
import tempfile
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ['COK_ACCOUNT_LOCK_FILE'] = os.path.join(
    tempfile.gettempdir(), 'cok-probe-stam-%d.lock' % os.getpid())

import cok_hunt as H                                       # noqa: E402
from cok_client import CokClient, account_lock, apply_account_types  # noqa: E402
from cok_sfs import TypedInt, SFS_INT, SFS_SHORT            # noqa: E402
import cok_accounts as cas                                 # noqa: E402

uid = sys.argv[1] if len(sys.argv) > 1 else "<uid-other>"
want_id = sys.argv[2] if len(sys.argv) > 2 else "200380"
want_num = int(sys.argv[3]) if len(sys.argv) > 3 else 1

acc = apply_account_types(dict(cas.get_account(uid)))
cl = CokClient(timeout=25, account=acc)

STAM_IDS = ["200380", "200381", "200382"]


def dump_items(tag, items):
    print("[%s] 背包 %d 项, 体力药水相关:" % (tag, len(items or [])), flush=True)
    for it in (items or []):
        if str(it.get("itemId")) in STAM_IDS:
            print("    id=%s uuid=%s count=%s type=%s type2=%s"
                  % (it.get("itemId"), it.get("uuid"), it.get("count"),
                     it.get("type"), it.get("type2")), flush=True)


with account_lock(timeout=5, purpose="probe", key=uid):
    cl.connect()
    cl.bin_handshake()
    cl.login()

    # ---------- 1) 实时读背包 ----------
    items = None
    for cmd, params in (("cemetery.get.info", {}),
                        ("show.status.item", {"itemType": "1"}),
                        ("itemcollection.data", {"itemType": "1"})):
        try:
            r = cl.call(cmd, params, retries=1)
            p = r.get("__params__") or {}
            got = p.get("items")
            print(">>> %s -> %d 键, items=%s"
                  % (cmd, len(p), (len(got) if isinstance(got, list) else type(got).__name__)),
                  flush=True)
            if isinstance(got, list) and got:
                items = got
                print("    样例:", {k: got[0].get(k) for k in
                                     ("itemId", "uuid", "count", "type", "type2")},
                      flush=True)
                break
        except Exception as e:  # noqa: BLE001
            print(">>> %s 失败: %s" % (cmd, str(e)[:110]), flush=True)
    if not items:
        print("!! 没读到背包", flush=True)
        cl.close()
        sys.exit(1)
    dump_items("读取", items)

    # 找目标药水
    target = None
    for it in items:
        if str(it.get("itemId")) == want_id and (int(it.get("count") or 0) > 0):
            target = it
            break
    if not target:
        print("!! 没有 %s (count>0)" % want_id, flush=True)
        cl.close()
        sys.exit(2)

    # ---------- 2) 使用 ----------
    st0 = H.read_stamina(cl)
    print("使用前体力:", st0, flush=True)
    uu = str(target.get("uuid"))
    for sfs_type, tag in ((SFS_INT, "INT"), (SFS_SHORT, "SHORT")):
        try:
            r = cl.call("item.use",
                        {"uuid": uu, "num": TypedInt(want_num, sfs_type)},
                        retries=1)
            p = r.get("__params__") or {}
            print(">>> item.use(num=%s as %s) -> %s"
                  % (want_num, tag, {k: v for k, v in p.items()
                                     if k in ("errorCode", "msg", "stamina",
                                              "currentStamina", "items")}),
                  flush=True)
            if p.get("errorCode"):
                continue
            time.sleep(1.5)
            st1 = H.read_stamina(cl)
            print("使用后体力:", st1, flush=True)
            try:
                d = (int(st1.get("stamina") or 0)) - (int(st0.get("stamina") or 0))
            except Exception:  # noqa: BLE001
                d = None
            print("体力变化 =", d, flush=True)
            # 背包里数量有没有变
            try:
                r2 = cl.call("cemetery.get.info", {}, retries=1)
                it2 = (r2.get("__params__") or {}).get("items") or []
                dump_items("使用后", it2)
            except Exception as e:  # noqa: BLE001
                print("   (复查背包失败 %s)" % str(e)[:80], flush=True)
            break
        except Exception as e:  # noqa: BLE001
            print(">>> item.use(%s) 异常: %s" % (tag, str(e)[:120]), flush=True)
cl.close()
