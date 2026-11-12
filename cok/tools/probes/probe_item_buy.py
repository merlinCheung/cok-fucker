#!/usr/bin/env python3
"""`item.buy {id, num}` 能拿到道具实例 uuid —— 顺着这个口子找"读背包" —— 2026-11-10。

决定性发现(2026-11-10 实测):
    item.buy {id: "200204", num: 1}
    -> {"item": {"itemId":"200204", "count":1742, "uuid":"c37ef0d4db954446b5fc7c6abcd1a58a", ...},
        "costGold": 280, "remainGold": 84912}
  * 参数名是 **`id`**(不是 itemId!) —— 传 itemId 一律 E000000
  * 响应里**直接带道具实例 uuid**
  ⇒ 「获得道具」的响应会带 uuid ⇒ 这是 uuid 的一个可靠来源

本脚本:
  1) 先试能不能**买体力药水** 200381/200380(商店是否卖)
  2) 再试一批同风格的**只读**命令(item.info / item.list / item.get ...),
     看有没有能直接读出玩家背包的

用法: python3 probe_item_buy.py <gameUid>
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
import tempfile
import time
import json

_C = os.path.join(HERE, "..", "..", "core")
sys.path.insert(0, _C)
os.environ['COK_ACCOUNT_LOCK_FILE'] = os.path.join(
    tempfile.gettempdir(), 'cok-probe-ib-%d.lock' % os.getpid())

from cok_client import CokClient, account_lock, apply_account_types  # noqa: E402
import cok_accounts as cas                                            # noqa: E402

uid = sys.argv[1] if len(sys.argv) > 1 else "<uid-guopan>"
acc = apply_account_types(dict(cas.get_account(uid)))
cl = CokClient(timeout=15, account=acc)

HEX32 = re.compile(r'^[0-9a-f]{32}$')


def show(cmd, params):
    t0 = time.time()
    try:
        r = cl.call(cmd, params, retries=1)
        p = r.get("__params__") or {}
        s = json.dumps(p, ensure_ascii=False)
        uu = re.findall(r'[0-9a-f]{32}', s)
        print("  %-22s %-28s %5.2fs %s%s" % (
            cmd, json.dumps(params, ensure_ascii=False)[:28], time.time() - t0,
            s[:300], ("   ★uuid=%s" % uu[:3]) if uu else ""), flush=True)
        return p
    except Exception as e:  # noqa: BLE001
        print("  %-22s %-28s %5.2fs ERR %s" % (
            cmd, json.dumps(params, ensure_ascii=False)[:28], time.time() - t0,
            str(e)[:70]), flush=True)
        return None


with account_lock(timeout=5, purpose="probe", key=uid):
    cl.connect()
    cl.bin_handshake()
    cl.login()

    print("=== A. 买体力药水(200381/200380/200382) ===", flush=True)
    for iid in ("200381", "200380", "200382"):
        p = show("item.buy", {"id": iid, "num": 1})
        if p and p.get("item") and p["item"].get("uuid"):
            print("  ★★★ 买到 %s, uuid=%s count=%s"
                  % (iid, p["item"]["uuid"], p["item"].get("count")), flush=True)

    print("\n=== B. 同风格的只读命令(试读背包) ===", flush=True)
    for cmd in ("item.info", "item.list", "item.get", "item.detail", "item.have",
                "item.query", "item.data", "item.all", "item.my", "item.owned",
                "item.count", "item.num", "item.goods"):
        show(cmd, {"id": "200381"})
    for cmd in ("item.info", "item.list", "item.get", "item.have"):
        show(cmd, {})

    print("\n=== C. 其它可能带背包的命令 ===", flush=True)
    for cmd in ("item.use.info", "item.info.list", "user.item.info",
                "user.items.list", "world.item.info"):
        show(cmd, {"id": "200381"})
cl.close()
