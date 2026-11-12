#!/usr/bin/env python3
"""领奖 -> 抓道具实例 uuid —— 2026-11-10 (决定性实验)。

发现: `resource.client.reward.getmulti` 会列出**可领取**的奖励,
      66 手游号的奖励 43003369 里含 200381(50体力) x 6。
      领奖时服务端会下发道具实例(uuid), 这就是我们要的 uuid 来源。

这里: 领奖 -> 同时监听 push, 找带 uuid / itemId=200381 的推送。

用法: python3 probe_claim_uuid.py <gameUid> [rewardId]
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
    tempfile.gettempdir(), 'cok-probe-claim-%d.lock' % os.getpid())

from cok_client import CokClient, account_lock, apply_account_types  # noqa: E402
from cok_sfs import parse_packet                                      # noqa: E402
import cok_accounts as cas                                            # noqa: E402

uid = sys.argv[1] if len(sys.argv) > 1 else "<uid-other>"
reward_id = sys.argv[2] if len(sys.argv) > 2 else "43003369"

acc = apply_account_types(dict(cas.get_account(uid)))
cl = CokClient(timeout=20, account=acc)

HEX32 = re.compile(r'^[0-9a-f]{32}$')


def find_uuids(o, path, out, d=0):
    if d > 8:
        return
    if isinstance(o, dict):
        for k, v in o.items():
            if isinstance(v, str) and HEX32.match(v):
                out.append((path + "." + str(k), v))
            find_uuids(v, path + "." + str(k), out, d + 1)
    elif isinstance(o, list):
        for i, v in enumerate(o[:120]):
            if isinstance(v, str) and HEX32.match(v):
                out.append(("%s[%d]" % (path, i), v))
            find_uuids(v, "%s[%d]" % (path, i), out, d + 1)


with account_lock(timeout=5, purpose="probe", key=uid):
    cl.connect()
    cl.bin_handshake()
    cl.login()

    print("=== 1. 列可领奖励(含 200381 的) ===", flush=True)
    r = cl.call("resource.client.reward.getmulti", {}, retries=1)
    p = r.get("__params__") or {}
    ro = p.get("rewardsObj") or {}
    picks = []
    for rid, info in ro.items():
        item = ((info.get("reward_list") or {}).get("item") or "")
        nums = ((info.get("reward_list") or {}).get("num") or "")
        its = item.split("|")
        ns = nums.split("|")
        for i, it in enumerate(its):
            if it in ("200380", "200381", "200382"):
                n = ns[i] if i < len(ns) else "?"
                picks.append((rid, it, n))
                print("  rewardId=%s 含 %s x%s" % (rid, it, n), flush=True)
    if not picks:
        print("  (没有药水类奖励)", flush=True)
    else:
        rid, item, n = picks[0]
        print("\n=== 2. 领取 %s (含 %s x%s) ===" % (rid, item, n), flush=True)
        r2 = cl.call("resource.client.reward.get", {"rewardId": rid}, retries=1)
        p2 = r2.get("__params__") or {}
        print("  响应: %s" % json.dumps(p2, ensure_ascii=False)[:1500], flush=True)
        hits = []
        find_uuids(p2, "", hits)
        print("  响应内 uuid: %s" % hits[:10], flush=True)

    print("\n=== 3. 监听 20 秒 push, 找道具 uuid ===", flush=True)
    cl.sock.settimeout(2.0)
    buf = b""
    end = time.time() + 20
    while time.time() < end:
        try:
            ch = cl.sock.recv(65536)
            if not ch:
                break
            buf += ch
        except Exception:  # noqa: BLE001
            pass
        i = 0
        while i + 3 <= len(buf):
            flags = buf[i]
            ln = (buf[i + 1] << 8) | buf[i + 2]
            if i + 3 + ln > len(buf):
                break
            try:
                _, _, obj, _ = parse_packet(buf[i:i + 3 + ln])
                rcmd = cl._resp_cmd(obj)
                pp = cl._resp_params(obj)
                s = json.dumps(pp, ensure_ascii=False)
                if "200380" in s or "200381" in s or "uuid" in s.lower():
                    hits = []
                    find_uuids(pp, "", hits)
                    print("  <- %-28s %s" % (rcmd, s[:600]), flush=True)
                    if hits:
                        print("     ★★ uuid: %s" % hits[:10], flush=True)
            except Exception:  # noqa: BLE001
                pass
            i += 3 + ln
        buf = buf[i:]
cl.close()
