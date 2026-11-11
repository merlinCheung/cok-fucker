#!/usr/bin/env python3
"""`item.use` 参数格式 + 体力药水真机使用验证(2026-11-10)。

已确认(对照实验 2026-11-10):
  * 服务端对**未知命令**表现为**超时**(乱写的 `zzz.not.exist` 就是超时);
  * `item.use` **0.27 秒回 errorCode=E000000** ⇒ **命令名是有效的**, 只是参数不对;
  * `use.stamina.tool` 超时 ⇒ **不是**客户端可发的请求命令(native 内部字符串)。

客户端 Lua 的格式(GeneralTreasureBoxController / MysteryBoxController):
    utils.requestServer('item.use', {{"uuid",CCString:create(uuid)},
                                     {"num",CCInteger:create(count)}}, ...)
队列加速用的是 `queue.ccd {qUUID, itemUUID, type, count}` —— 也要道具**实例 uuid**。

这里用 `bag-items.json` 里 200381(50体力) 的**实例 uuid** 试各种参数组合,
看哪个能真的把体力加上。

⚠️ 成功的那一次会**真的消耗 1 个 50 体力药水**。

用法: python3 probe_item_use.py [itemId] [num]
"""
import json
import os
import sys
import tempfile
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ['COK_ACCOUNT_LOCK_FILE'] = os.path.join(
    tempfile.gettempdir(), 'cok-probe-itemuse-%d.lock' % os.getpid())

import cok_hunt as H                                       # noqa: E402
from cok_client import CokClient, account_lock, apply_account_types  # noqa: E402
from cok_sfs import TypedInt, SFS_INT                      # noqa: E402
import cok_accounts as cas                                 # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
item_id = sys.argv[1] if len(sys.argv) > 1 else "200381"
want_num = int(sys.argv[2]) if len(sys.argv) > 2 else 1

# 背包快照里的道具实例 uuid
bag = json.load(open(os.path.join(HERE, "bag-items.json"), encoding="utf-8"))
ent = None
for it in (bag.get("items") or []):
    if str(it.get("itemId")) == item_id:
        ent = it
        break
print("背包快照里 %s -> %s" % (item_id, json.dumps(ent, ensure_ascii=False)),
      flush=True)
uuid = str((ent or {}).get("uuid") or "")
count = int((ent or {}).get("count") or 0)

# 依次试账号
accts = []
for uid in ("<uid-other>", "<uid-guopan>", "<uid-main>",
            "<uid-guopan-intl>"):
    try:
        accts.append(uid)
    except Exception:  # noqa: BLE001
        pass


def run(uid, params, tag):
    acc = apply_account_types(dict(cas.get_account(uid)))
    cl = CokClient(timeout=20, account=acc)
    try:
        with account_lock(timeout=5, purpose="probe", key=uid):
            cl.connect()
            cl.bin_handshake()
            cl.login()
            st0 = int(H.read_stamina(cl).get("stamina") or 0)
            t0 = time.time()
            try:
                r = cl.call("item.use", params, retries=1)
                p = r.get("__params__") or {}
                dt = time.time() - t0
                time.sleep(1.5)
                st1 = int(H.read_stamina(cl).get("stamina") or 0)
                print("  [%s] %s %.2fs errorCode=%s 体力 %s->%s (Δ%s) 键=%s"
                      % (uid, tag, dt, p.get("errorCode"), st0, st1,
                         st1 - st0, list(p.keys())[:6]), flush=True)
                return (p.get("errorCode"), st1 - st0)
            except Exception as e:  # noqa: BLE001
                print("  [%s] %s 异常 %s" % (uid, tag, str(e)[:90]), flush=True)
                return ("ERR", 0)
    finally:
        try:
            cl.close()
        except Exception:  # noqa: BLE001
            pass


CANDS = [
    ({"uuid": uuid, "num": TypedInt(want_num, SFS_INT)}, "uuid+num(INT)"),
    ({"uuid": uuid, "num": want_num}, "uuid+num(plain)"),
    ({"itemId": item_id, "num": TypedInt(want_num, SFS_INT)}, "itemId+num(INT)"),
    ({"itemId": item_id}, "itemId only"),
    ({"itemId": item_id, "count": want_num}, "itemId+count"),
]

if not uuid:
    print("!! 背包快照里没有 %s" % item_id, flush=True)
    sys.exit(1)

for uid in accts:
    print("=== 账号 %s (快照 count=%s) ===" % (uid, count), flush=True)
    for params, tag in CANDS:
        code, d = run(uid, params, tag)
        if d and d > 0:
            print("\n✅ 命中! %s / %s -> 体力 +%s" % (uid, tag, d), flush=True)
            print("   参数: %s" % json.dumps(params, ensure_ascii=False), flush=True)
            sys.exit(0)
    print("  (该账号没试出有效参数)", flush=True)
