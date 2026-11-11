#!/usr/bin/env python3
"""扫登录后收到的**所有推送**, 找带道具(itemId/uuid/count)的 —— 2026-11-10。

背景: 背包(道具 uuid + count)在客户端是 native 的 ToolController 管的,
而 Lua 里**没有**"拉背包"的请求命令(实测 `cemetery.get.info` /
`show.status.item` / `itemcollection.data` 都不返回 items)。
所以背包数据要么在**登录推送**里, 要么在**后续 push** 里。

这里把登录后 N 秒内收到的每个 push 都 dump 一遍, 找出带道具的。

用法: python3 probe_push_bag.py <gameUid> [seconds]
"""
import os
import sys
import tempfile
import time
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ['COK_ACCOUNT_LOCK_FILE'] = os.path.join(
    tempfile.gettempdir(), 'cok-probe-pushbag-%d.lock' % os.getpid())

from cok_client import CokClient, account_lock, apply_account_types  # noqa: E402
from cok_sfs import parse_packet                                  # noqa: E402
import cok_accounts as cas                                        # noqa: E402

uid = sys.argv[1] if len(sys.argv) > 1 else "<uid-other>"
secs = int(sys.argv[2]) if len(sys.argv) > 2 else 25

acc = apply_account_types(dict(cas.get_account(uid)))
cl = CokClient(timeout=25, account=acc)

STAM = ("200380", "200381", "200382")

with account_lock(timeout=5, purpose="probe", key=uid):
    cl.connect()
    cl.bin_handshake()
    cl.login()
    print("登录完成, 监听 %d 秒的推送…" % secs, flush=True)
    cl.sock.settimeout(1.0)
    buf = b""
    end = time.time() + secs
    seen = set()
    hits = []
    while time.time() < end:
        try:
            ch = cl.sock.recv(65536)
            if not ch:
                break
            buf += ch
        except Exception:  # noqa: BLE001
            pass
        # 解析出完整帧
        i = 0
        rest = b""
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
                if rcmd not in seen:
                    seen.add(rcmd)
                    print("  push %-42s 键=%s%s"
                          % (rcmd, list(pp.keys())[:6],
                             ("  <<< 含道具!" if ("itemId" in s or '"uuid"' in s and "count" in s) else "")),
                          flush=True)
                if any(k in s for k in ("itemId", "200380", "200381")):
                    hits.append((rcmd, s))
            except Exception:  # noqa: BLE001
                pass
            i += 3 + ln
        buf = rest + buf[i:]
    print("\n=== 收到 %d 个不同命令 ===" % len(seen), flush=True)
    print(sorted(seen), flush=True)
    if hits:
        print("\n=== 含道具的响应 ===", flush=True)
        for cmd, s in hits[:20]:
            print("  %s -> %s" % (cmd, s[:600]), flush=True)
cl.close()
