#!/usr/bin/env python3
"""登录后**原始字节流**全量落盘 + 命令名提取 —— 2026-11-10。

前面的探针都是"解析帧 → 看 cmd 名", 一旦解析抛异常就整帧丢掉。
这里改成: 登录后 N 秒内把 socket 收到的**原始字节**全存下来, 之后离线分析:
  * 用 strings 找所有明文点号串(= 收到的命令名, 包括没被解析的那些)
  * 直接搜 'useritemlist' / 'itemId' 等关键字

用法: python3 probe_raw_stream.py <gameUid> [seconds]
"""
import os
import re
import sys
import tempfile
import time

_C = os.path.join(HERE, "..", "..", "core")
sys.path.insert(0, _C)
os.environ['COK_ACCOUNT_LOCK_FILE'] = os.path.join(
    tempfile.gettempdir(), 'cok-probe-raw-%d.lock' % os.getpid())

from cok_client import CokClient, account_lock, apply_account_types  # noqa: E402
import cok_accounts as cas                                           # noqa: E402

uid = sys.argv[1] if len(sys.argv) > 1 else "<uid-other>"
secs = int(sys.argv[2]) if len(sys.argv) > 2 else 30

HERE = os.path.dirname(os.path.abspath(__file__))
out_path = os.path.join(HERE, "raw-stream-%s.bin" % uid)

acc = apply_account_types(dict(cas.get_account(uid)))
cl = CokClient(timeout=25, account=acc)

with account_lock(timeout=5, purpose="probe", key=uid):
    cl.connect()
    cl.bin_handshake()
    cl.login()
    print("登录完成, 抓 %d 秒原始流…" % secs, flush=True)
    cl.sock.settimeout(1.0)
    buf = b""
    end = time.time() + secs
    while time.time() < end:
        try:
            ch = cl.sock.recv(65536)
            if not ch:
                break
            buf += ch
        except Exception:  # noqa: BLE001
            pass
    open(out_path, "wb").write(buf)
    print("落盘 %s  (%d 字节)" % (out_path, len(buf)), flush=True)
cl.close()

# ---- 离线分析 ----
data = open(out_path, "rb").read()
print("\n=== 可打印串里的点号命令名 ===", flush=True)
text = "".join(chr(b) if 32 <= b < 127 else "\n" for b in data)
toks = [t for t in re.split(r"[^A-Za-z0-9_.]+", text) if "." in t]
cmds = []
for t in toks:
    parts = t.split(".")
    for i in range(len(parts)):
        for j in range(i + 2, min(i + 4, len(parts) + 1)):
            cand = ".".join(parts[i:j])
            if cand not in cmds:
                cmds.append(cand)
for c in cmds:
    print("  %s" % c, flush=True)

print("\n=== 关键字 ===", flush=True)
for kw in (b"useritemlist", b"itemId", b"useritem", b"push.item", b"push.useritem",
           b"tools", b"itemList"):
    idx = data.find(kw)
    print("  %-16s %s" % (kw.decode(), hex(idx) if idx >= 0 else "未出现"), flush=True)
