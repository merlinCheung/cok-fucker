#!/usr/bin/env python3
"""找"实时拉背包"的命令(2026-11-10)。

已知:
  * `item.use {uuid, num:INT}` 命令名有效(秒回 errorCode), 但要**当前有效**的道具实例 uuid;
  * `bag-items.json` 里的 uuid 是 2026-10-24 的 frida 快照, 已失效(E100166 没有该道具);
  * 客户端 native 里 `push.item.having` / `push.useritem` 是**背包推送**;
  * native 的命令分发表里有 `hot.item.get` / `havest.tool` / `create.tool` / `rm.tool` /
    `tool.queue.buy`。

这里逐个试这些命令, 并**同时监听推送**, 看哪条能让服务端把背包(带 uuid)推下来。

用法: python3 probe_bag_pull.py <gameUid>
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
    tempfile.gettempdir(), 'cok-probe-bagpull-%d.lock' % os.getpid())

from cok_client import CokClient, account_lock, apply_account_types  # noqa: E402
from cok_sfs import parse_packet                                    # noqa: E402
import cok_accounts as cas                                          # noqa: E402

uid = sys.argv[1] if len(sys.argv) > 1 else "<uid-guopan>"
acc = apply_account_types(dict(cas.get_account(uid)))
cl = CokClient(timeout=12, account=acc)

CANDS = [
    ("hot.item.get", {}),
    ("hot.item.get", {"itemId": "200381"}),
    ("hot.item.v2.get", {}),
    ("havest.tool", {"index": 0}),
    ("havest.tool", {}),
    ("create.tool", {}),
    ("tool.queue.buy", {"num": 1}),
    ("show.status.item", {}),
    ("item.send", {}),
    ("use.item.on.target", {}),
]


def drain(tag, seconds=4.0):
    """监听推送, 返回 (cmd -> params) 里带道具的。"""
    cl.sock.settimeout(0.6)
    buf = b""
    end = time.time() + seconds
    found = []
    cmds = []
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
                fl, pl, obj, cons = parse_packet(buf[i:i + 3 + ln])
                pp = cl._resp_params(obj)
                rcmd = cl._resp_cmd(obj)
                s = json.dumps(pp, ensure_ascii=False)
                cmds.append(rcmd)
                if "itemId" in s or "uuid" in s and "count" in s:
                    found.append((rcmd, s[:800]))
            except Exception:  # noqa: BLE001
                pass
            i += 3 + ln
        buf = buf[i:]
    if cmds:
        print("     收到推送: %s" % sorted(set(cmds)), flush=True)
    for c, s in found:
        print("     ★ %s -> %s" % (c, s), flush=True)
    return found


with account_lock(timeout=5, purpose="probe", key=uid):
    cl.connect()
    cl.bin_handshake()
    cl.login()
    print("账号 %s" % uid, flush=True)
    for cmd, params in CANDS:
        t0 = time.time()
        try:
            r = cl.call(cmd, params, retries=1)
            p = r.get("__params__") or {}
            print(">>> %s %s -> %.2fs errorCode=%s 键=%s"
                  % (cmd, json.dumps(params, ensure_ascii=False),
                     time.time() - t0, p.get("errorCode"), list(p.keys())[:6]),
                  flush=True)
            s = json.dumps(p, ensure_ascii=False)
            if "itemId" in s or ("uuid" in s and "count" in s):
                print("     ★ 响应里有道具: %s" % s[:800], flush=True)
        except Exception as e:  # noqa: BLE001
            print(">>> %s %s -> 异常 %s"
                  % (cmd, json.dumps(params, ensure_ascii=False), str(e)[:80]),
                  flush=True)
        drain(cmd)
cl.close()
