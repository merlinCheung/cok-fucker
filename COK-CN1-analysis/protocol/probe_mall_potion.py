#!/usr/bin/env python3
"""扫所有商城(mall.data), 找体力药水(200380/200381/200382) —— 2026-11-10。

已确认:
  * `mall.data {mallId:"15"}` -> {"goodsArray":[...]}  (28KB, 商城存在)
  * `mall.data {mallId:"7"}` -> E000004 (商城不存在)
  * `mall.data {mallId:"128"}` -> goodsArray (联盟商店)
  * `mall.buy {mallId, targetId, num}` —— 客户端 Lua 用法, 买完大概率带 uuid
  * `item.buy {id,num}` 也能带 uuid, 但道具商店不卖体力药水

本脚本:
  1) 扫 mallId 1..80, 列出所有存在的商城
  2) 在每个商城里找体力药水, 打印 targetId/价格/货币
  3) --buy 时买 1 瓶, 看响应里有没有 uuid

用法: python3 probe_mall_potion.py <gameUid> [--buy]
"""
import json
import os
import re
import sys
import tempfile
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ['COK_ACCOUNT_LOCK_FILE'] = os.path.join(
    tempfile.gettempdir(), 'cok-probe-mp-%d.lock' % os.getpid())

from cok_client import CokClient, account_lock, apply_account_types  # noqa: E402
import cok_accounts as cas                                            # noqa: E402

uid = sys.argv[1] if len(sys.argv) > 1 else "<uid-guopan>"
DO_BUY = "--buy" in sys.argv
acc = apply_account_types(dict(cas.get_account(uid)))
cl = CokClient(timeout=15, account=acc)

HEX32 = re.compile(r'[0-9a-f]{32}')
POTIONS = ("200380", "200381", "200382")


def call(cmd, params, retries=1):
    try:
        r = cl.call(cmd, params, retries=retries)
        return r.get("__params__") or {}
    except Exception as e:  # noqa: BLE001
        print("    ERR %s %s: %s" % (cmd, params, str(e)[:70]), flush=True)
        return None


with account_lock(timeout=5, purpose="probe", key=uid):
    cl.connect()
    cl.bin_handshake()
    cl.login()

    print("=== A. mall.info ===", flush=True)
    p = call("mall.info", {})
    if p:
        s = json.dumps(p, ensure_ascii=False)
        print("   len=%d %s" % (len(s), s[:1500]), flush=True)
        for iid in POTIONS:
            if iid in s:
                print("   ★ 体力药水 %s 出现在 mall.info" % iid, flush=True)

    print("\n=== B. 扫 mallId 1..80 ===", flush=True)
    shops = {}
    for mid in range(1, 81):
        p = call("mall.data", {"mallId": str(mid)})
        if not p:
            continue
        if p.get("errorCode"):
            continue
        ga = p.get("goodsArray")
        if not isinstance(ga, list):
            print("   mall %-3d 存在, 但无 goodsArray (keys=%s)"
                  % (mid, list(p.keys())[:8]), flush=True)
            continue
        shops[mid] = ga
        hits = [g for g in ga
                if str(g.get("itemId")) in POTIONS
                or str(g.get("targetId")) in POTIONS]
        print("   mall %-3d goods=%-4d %s" % (mid, len(ga),
                                              ("★含体力药水: %s" % json.dumps(hits, ensure_ascii=False)) if hits else ""),
              flush=True)

    print("\n=== C. 其它商城数据源 ===", flush=True)
    for cmd, pr in (("mall.data2", {}), ("mall.getNewGoods", {}),
                    ("mall.info", {"type": 12}), ("mall.info", {"type": 23})):
        p = call(cmd, pr)
        if not p:
            continue
        s = json.dumps(p, ensure_ascii=False)
        uu = HEX32.findall(s)
        print("   %-20s len=%-6d uuid=%s %s" % (cmd, len(s), uu[:2], s[:200]), flush=True)

    if DO_BUY:
        print("\n=== D. 买体力药水 ===", flush=True)
        for mid, ga in shops.items():
            for g in ga:
                if str(g.get("itemId")) in POTIONS:
                    tid = g.get("targetId")
                    print("   试 mall %s target %s (item %s)"
                          % (mid, tid, g.get("itemId")), flush=True)
                    p = call("mall.buy", {"mallId": str(mid), "targetId": str(tid), "num": 1})
                    if p:
                        s = json.dumps(p, ensure_ascii=False)
                        uu = HEX32.findall(s)
                        print("      -> len=%d uuid=%s %s" % (len(s), uu[:3], s[:400]), flush=True)
                        if uu:
                            print("      ★★★ 拿到 uuid=%s" % uu[0], flush=True)
cl.close()
