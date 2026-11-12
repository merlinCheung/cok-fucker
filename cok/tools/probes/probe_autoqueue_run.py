#!/usr/bin/env python3
"""服务端自动打怪队列能不能开 + 会不会自己喝体力药水 —— 2026-11-10。

背景: 客户端的「自动打怪」= 服务端队列(autoQueue), 它有 saveItems(要用的道具),
      服务端会在体力不足时自己喝。已验证 autoQueue.save 能存下 saveItems。
      这里验证: (1) status=1 能不能开 (2) 开了会不会真的自动喝药。

受控: lv="1;1"(1 级怪) autoCount=1, 测完立刻 status=0 关掉。

用法: python3 probe_autoqueue_run.py <gameUid>
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
import tempfile
import time
import json

_C = os.path.join(HERE, "..", "..", "core")
sys.path.insert(0, _C)
os.environ['COK_ACCOUNT_LOCK_FILE'] = os.path.join(
    tempfile.gettempdir(), 'cok-probe-aqr-%d.lock' % os.getpid())

from cok_client import CokClient, account_lock, apply_account_types  # noqa: E402
import cok_accounts as cas                                           # noqa: E402

uid = sys.argv[1] if len(sys.argv) > 1 else "<uid-other>"
acc = apply_account_types(dict(cas.get_account(uid)))
cl = CokClient(timeout=20, account=acc)


def probe(cmd, params=None, tag=""):
    t0 = time.time()
    try:
        r = cl.call(cmd, params or {}, retries=1)
        p = r.get("__params__") or {}
        print("  %-18s %-10s %6.2fs  %s" % (cmd, tag, time.time() - t0,
                                           json.dumps(p, ensure_ascii=False)[:280]), flush=True)
        return p
    except Exception as e:  # noqa: BLE001
        print("  %-18s %-10s %6.2fs  ERR %s" % (cmd, tag, time.time() - t0, str(e)[:90]), flush=True)
        return None


with account_lock(timeout=5, purpose="probe", key=uid):
    cl.connect()
    cl.bin_handshake()
    cl.login()

    print("=== 0. 基线 ===", flush=True)
    probe("autoQueue.status", {"status": 0}, "读体力")
    probe("autoQueue.data", {}, "before")

    print("\n=== 1. 保存配置: 1级怪 / 次数1 / 体力药水 ===", flush=True)
    probe("autoQueue.save", {"lv": "1;1", "autoCount": 1, "force": 1,
                             "saveItems": "200380;1|200381;2"}, "save")

    print("\n=== 2. 开启队列 ===", flush=True)
    probe("autoQueue.status", {"status": 1}, "开启")

    print("\n=== 3. 观察 40 秒 (服务端自己打怪/喝药) ===", flush=True)
    cl.sock.settimeout(2.0)
    buf = b""
    end = time.time() + 40
    seen = {}
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
                from cok_sfs import parse_packet
                _, _, obj, _ = parse_packet(buf[i:i + 3 + ln])
                rcmd = cl._resp_cmd(obj)
                pp = cl._resp_params(obj)
                s = json.dumps(pp, ensure_ascii=False)
                if rcmd not in seen:
                    seen[rcmd] = s[:220]
                    print("    <- %-34s %s" % (rcmd, s[:200]), flush=True)
                if "200380" in s or "200381" in s or "useItems" in s:
                    print("    ★ 道具相关: %s -> %s" % (rcmd, s[:300]), flush=True)
            except Exception:  # noqa: BLE001
                pass
            i += 3 + ln
        buf = buf[i:]

    print("\n=== 4. 关闭队列 + 回读 ===", flush=True)
    probe("autoQueue.status", {"status": 0}, "关闭")
    probe("autoQueue.data", {}, "after")
    probe("autoQueue.status", {"status": 0}, "读体力")
cl.close()
