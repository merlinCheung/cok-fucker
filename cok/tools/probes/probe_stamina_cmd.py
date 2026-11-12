#!/usr/bin/env python3
"""对照实验: 分清「命令名不对」和「参数不对」(2026-11-10)。

服务端对**未知命令**的表现通常是**超时**(不回 errorCode),
对**已知命令 + 错参数**通常是**秒回 errorCode**。
所以只要先测一个乱写的命令名做基线, 就能判断后面哪个是命令名问题。

测的东西:
  A. 基线: `cmd.ping` (一定有效) / `zzz.not.exist` (一定无效)
  B. `use.stamina.tool` 的几种参数
  C. 其它候选命令名
  D. `item.use` (客户端 Lua 的格式: {uuid, num}) —— 用**假 uuid**,
     只看"秒回 errorCode"还是"超时"(不真消耗)

用法: python3 probe_stamina_cmd.py <gameUid>
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
import tempfile
import time

_C = os.path.join(HERE, "..", "..", "core")
sys.path.insert(0, _C)
os.environ['COK_ACCOUNT_LOCK_FILE'] = os.path.join(
    tempfile.gettempdir(), 'cok-probe-stamcmd-%d.lock' % os.getpid())

from cok_client import CokClient, account_lock, apply_account_types  # noqa: E402
from cok_sfs import TypedInt, SFS_INT                                 # noqa: E402
import cok_accounts as cas                                           # noqa: E402

uid = sys.argv[1] if len(sys.argv) > 1 else "<uid-other>"
acc = apply_account_types(dict(cas.get_account(uid)))
cl = CokClient(timeout=12, account=acc)


def probe(cmd, params=None, tag=""):
    t0 = time.time()
    try:
        r = cl.call(cmd, params or {}, retries=1)
        dt = time.time() - t0
        p = r.get("__params__") or {}
        print("  %-34s %-8s %.2fs  errorCode=%s  键=%s"
              % (cmd, tag, dt, p.get("errorCode"), list(p.keys())[:5]), flush=True)
        return ("ok", dt, p)
    except Exception as e:  # noqa: BLE001
        dt = time.time() - t0
        msg = str(e)
        kind = "超时" if "超时" in msg or "无响应" in msg else "异常"
        print("  %-34s %-8s %.2fs  %s: %s"
              % (cmd, tag, dt, kind, msg[:80]), flush=True)
        return (kind, dt, None)


with account_lock(timeout=5, purpose="probe", key=uid):
    cl.connect()
    cl.bin_handshake()
    cl.login()
    print("=== A. 基线 ===", flush=True)
    probe("cmd.ping", {}, "基线有效")
    probe("zzz.not.exist", {}, "乱写")
    probe("autoQueue.status", {"status": 0}, "已知命令")

    print("\n=== B. use.stamina.tool 参数 ===", flush=True)
    probe("use.stamina.tool", {"itemId": "200381", "num": TypedInt(1, SFS_INT)},
          "itemId+num")
    probe("use.stamina.tool", {"itemId": "200381", "num": 1}, "plain num")
    probe("use.stamina.tool", {"itemId": 200381, "count": 1}, "int+count")
    probe("use.stamina.tool", {"id": "200381", "num": 1}, "id+num")
    probe("use.stamina.tool", {"itemId": "200381"}, "itemId only")
    probe("use.stamina.tool", {"uuid": "0" * 32, "num": 1}, "假uuid+num")

    print("\n=== C. 其它候选命令名 ===", flush=True)
    for c in ("use.item", "tool.use", "use.tool", "use.stamina",
              "world.useTool", "item.use", "user.item.use",
              "use.tool.stamina", "world.user.item"):
        probe(c, {"itemId": "200381", "num": 1, "uuid": "0" * 32}, "试")
cl.close()
