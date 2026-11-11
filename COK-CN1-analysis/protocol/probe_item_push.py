#!/usr/bin/env python3
"""触发一次「背包变化」, 看服务端会不会推 `push.item.having`(带道具 uuid) —— 2026-11-10。

背景:
  * 客户端的道具实例 uuid 在 native `ToolController` 里;
    native 的日志 "SendItemPush - get a item(%d) from(%s)" 说明
    **`push.item.having` 会带道具信息**(itemId + 可能 uuid)。
  * 我们从没收到过这个 push —— 因为**从没让服务端的背包变过**。
  * 触发背包变化最便宜的办法 = **在商店买一个便宜道具**(200204 = 250 金币)。

本脚本: 试各种购买命令/参数, 每次买完立刻监听 8 秒的 push,
        看有没有 push.item.having / push.item.add 带 32 位 hex。

用法: python3 probe_item_push.py <gameUid>
"""
import os
import re
import sys
import tempfile
import time
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ['COK_ACCOUNT_LOCK_FILE'] = os.path.join(
    tempfile.gettempdir(), 'cok-probe-ipp-%d.lock' % os.getpid())

from cok_client import CokClient, account_lock, apply_account_types  # noqa: E402
from cok_sfs import TypedInt, SFS_INT, parse_packet                    # noqa: E402
import cok_accounts as cas                                            # noqa: E402

uid = sys.argv[1] if len(sys.argv) > 1 else "<uid-guopan>"
acc = apply_account_types(dict(cas.get_account(uid)))
cl = CokClient(timeout=15, account=acc)

HEX32 = re.compile(r'^[0-9a-f]{32}$')


def find_uuids(obj, path, out, depth=0):
    if depth > 8:
        return
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, str) and HEX32.match(v):
                out.append((path + "." + str(k), v))
            find_uuids(v, path + "." + str(k), out, depth + 1)
    elif isinstance(obj, list):
        for i, v in enumerate(obj[:200]):
            if isinstance(v, str) and HEX32.match(v):
                out.append(("%s[%d]" % (path, i), v))
            find_uuids(v, "%s[%d]" % (path, i), out, depth + 1)


def drain(seconds=8.0, tag=""):
    """把 socket 里收到的 push 全部读出来, 找带道具/uuid 的。"""
    cl.sock.settimeout(1.0)
    buf = b""
    end = time.time() + seconds
    found = []
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
                _, _, obj, _ = parse_packet(buf[i:i + 3 + ln])
                rcmd = cl._resp_cmd(obj)
                pp = cl._resp_params(obj)
                s = json.dumps(pp, ensure_ascii=False)
                if rcmd not in seen:
                    seen[rcmd] = s[:160]
                hits = []
                find_uuids(pp, "", hits)
                if hits or "item" in rcmd.lower():
                    found.append((rcmd, s[:600], hits))
                    print("    ★ %s -> %s" % (rcmd, s[:400]), flush=True)
                    if hits:
                        print("       uuid: %s" % hits[:6], flush=True)
            except Exception:  # noqa: BLE001
                pass
            i += 3 + ln
        buf = buf[i:]
    if not found:
        print("    (%s 没看到道具相关 push; 收到的命令: %s)"
              % (tag, list(seen.keys())[:8]), flush=True)
    return found


BUYS = [
    ("hot.item.v2.buy", {"itemId": "200204", "num": 1}),
    ("hot.item.v2.buy", {"itemId": "200204", "num": TypedInt(1, SFS_INT)}),
    ("hot.item.v2.buy", {"id": "200204", "count": 1}),
    ("hot.item.buy", {"itemId": "200204", "num": 1}),
    ("hot.item.buy", {"itemId": "200204", "count": 1}),
    ("item.buy", {"itemId": "200204", "num": 1}),
    ("item.buy", {"itemId": "200204", "count": 1}),
    ("item.buy", {"itemId": "200204", "num": TypedInt(1, SFS_INT)}),
    ("item.buy", {"id": "200204", "num": 1}),
]

with account_lock(timeout=5, purpose="probe", key=uid):
    cl.connect()
    cl.bin_handshake()
    cl.login()
    print("=== 先看基线 push ===", flush=True)
    drain(4, "基线")

    for cmd, params in BUYS:
        print("\n--- %s %s" % (cmd, json.dumps(params, ensure_ascii=False, default=str)), flush=True)
        try:
            r = cl.call(cmd, params, retries=1)
            p = r.get("__params__") or {}
            print("    响应: %s" % json.dumps(p, ensure_ascii=False)[:260], flush=True)
            if p.get("errorCode"):
                continue
        except Exception as e:  # noqa: BLE001
            print("    ERR %s" % str(e)[:90], flush=True)
            continue
        hits = drain(8, cmd)
        if hits:
            print("  ★★★ 命中! 停止尝试", flush=True)
            break
cl.close()
