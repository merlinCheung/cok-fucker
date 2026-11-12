#!/usr/bin/env python3
"""找「能读出玩家背包 / 能买到体力药水」的命令 —— 2026-11-10(第二轮)。

第一轮结论:
  * `item.buy {id,num}` 成功且响应带 uuid, 但 200380/200381/200382 买不到(道具商店不卖)
  * 客户端 Lua 里有 `mall.data / mall.data2 / mall.buy / mall.reward / mall.getNewGoods`
  * native .rodata 里有 `mall.info / mall.info.type / mall.info.type.12 / mall.info.type.23`
    以及 `player.info / cmd.finishinit / overview_new.data / hot.item.v2.get / push.useritem`

本脚本:
  A. mall.info / mall.data(多个 mallId) / mall.data2 —— 看商城里有没有体力药水
  B. 一批「可能带背包」的只读命令 —— 看有没有 useritemlist / uuid
  C. 汇总: 任何含 32 位 hex uuid 的响应都打出来

只读为主; 唯一可能花钱的是 item.buy, 默认不跑(加 --buy 才跑)。
用法: python3 probe_bag_v2.py <gameUid> [--buy]
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
import tempfile
import time

_C = os.path.join(HERE, "..", "..", "core")
sys.path.insert(0, _C)
os.environ['COK_ACCOUNT_LOCK_FILE'] = os.path.join(
    tempfile.gettempdir(), 'cok-probe-b2-%d.lock' % os.getpid())

from cok_client import CokClient, account_lock, apply_account_types  # noqa: E402
import cok_accounts as cas                                            # noqa: E402

uid = sys.argv[1] if len(sys.argv) > 1 else "<uid-guopan>"
DO_BUY = "--buy" in sys.argv
acc = apply_account_types(dict(cas.get_account(uid)))
cl = CokClient(timeout=15, account=acc)

HEX32 = re.compile(r'[0-9a-f]{32}')
POTIONS = ("200380", "200381", "200382")
found_uuids = []


def show(cmd, params, label=""):
    t0 = time.time()
    try:
        r = cl.call(cmd, params, retries=1)
    except Exception as e:  # noqa: BLE001
        print("  %-24s %-24s ERR %s" % (cmd, label, str(e)[:60]), flush=True)
        return None
    p = r.get("__params__") or {}
    s = json.dumps(p, ensure_ascii=False)
    uu = HEX32.findall(s)
    hit = [x for x in POTIONS if x in s]
    tag = ""
    if uu:
        tag += "  ★uuid=%s" % uu[:3]
        found_uuids.append((cmd, label, uu))
    if hit:
        tag += "  ★药水=%s" % hit
    if "useritemlist" in s:
        tag += "  ★★useritemlist"
    print("  %-24s %-24s %5.2fs len=%-6d %s%s"
          % (cmd, label, time.time() - t0, len(s), s[:180], tag), flush=True)
    return p


with account_lock(timeout=5, purpose="probe", key=uid):
    cl.connect()
    cl.bin_handshake()
    cl.login()

    print("=== A. 商城 ===", flush=True)
    show("mall.info", {})
    show("mall.data2", {})
    for mid in ("1", "2", "3", "4", "5", "6", "7", "8", "9", "10",
                "11", "12", "13", "14", "15", "20", "23", "123", "128"):
        show("mall.data", {"mallId": mid}, "mallId=" + mid)

    print("\n=== B. 候选「读背包」命令 ===", flush=True)
    for cmd in ("player.info", "user.info", "user.data", "player.data",
                "cmd.finishinit", "overview_new.data",
                "hot.item.get", "hot.item.v2.get",
                "item.collection.data", "goods.data", "tools.data",
                "tool.data", "prop.data", "props.data",
                "push.useritem", "user.item", "user.items",
                "bag.data", "my.item", "own.item", "owned.item"):
        show(cmd, {})

    print("\n=== C. 带参数的候选 ===", flush=True)
    for cmd in ("item.info", "item.list", "item.get", "item.have",
                "item.query", "item.data"):
        show(cmd, {"id": "200381"})

    if DO_BUY:
        print("\n=== D. item.buy(花钱!) ===", flush=True)
        for iid in POTIONS:
            show("item.buy", {"id": iid, "num": 1})

    print("\n=== 汇总: 带 uuid 的响应 ===", flush=True)
    seen = set()
    for cmd, label, uu in found_uuids:
        k = (cmd, label, tuple(uu))
        if k in seen:
            continue
        seen.add(k)
        print("  %s %s -> %s" % (cmd, label, uu[:4]), flush=True)
cl.close()
