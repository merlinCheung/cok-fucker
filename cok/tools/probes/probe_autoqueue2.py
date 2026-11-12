#!/usr/bin/env python3
"""打通服务端 autoQueue(自动打怪代喝体力药水) —— 2026-11-10。

客户端源码(assets/lua_static/game/autoQueue/)确认:
  * AutoQueueController 用 `autoQueue.save {saveItems:"200380;1|200381;2", lv, autoCount, force}`
    告诉服务端"体力不够时用这些药水" —— **服务端按道具 id 自己找实例, 不需要 uuid**
  * `autoQueue.status {status:1}` 开启 / {status:0} 关闭
  * `autoQueue.data` 读当前配置(回显 saveItems/useItems/status/stamina/lastStaminaTime)
  * `autoQueue.search {autoQueue:n}` 找目标
  * 体力药水 id = data_config.auto_kill_monster.k1 = "200380;200381"

已知: 某号 `autoQueue.status {status:1}` -> E000000(疑缺周卡 k2=766437)
本脚本逐号测试, 并且**分别用 STRING / SFS_INT 两种类型传 status**。

用法: python3 probe_autoqueue2.py [gameUid ...]
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
import tempfile

_C = os.path.join(HERE, "..", "..", "core")
sys.path.insert(0, _C)
os.environ['COK_ACCOUNT_LOCK_FILE'] = os.path.join(
    tempfile.gettempdir(), 'cok-probe-aq-%d.lock' % os.getpid())

from cok_client import CokClient, account_lock, apply_account_types  # noqa: E402
from cok_sfs import TypedInt, SFS_INT                                      # noqa: E402
import cok_accounts as cas                                               # noqa: E402

UIDS = sys.argv[1:] or ["<uid-guopan-intl>", "<uid-main>",
                         "<uid-other>", "<uid-guopan>"]


def show(cl, cmd, params, label=""):
    try:
        r = cl.call(cmd, params, retries=1)
        p = r.get("__params__") or {}
        s = json.dumps(p, ensure_ascii=False)
        print("    %-22s %-18s len=%-6d %s"
              % (cmd, label, len(s), s[:260]), flush=True)
        return p
    except Exception as e:  # noqa: BLE001
        print("    %-22s %-18s ERR %s" % (cmd, label, str(e)[:70]), flush=True)
        return None


for uid in UIDS:
    print("\n========== 账号 %s ==========" % uid, flush=True)
    try:
        acc = apply_account_types(dict(cas.get_account(uid)))
    except Exception as e:  # noqa: BLE001
        print("  取账号失败: %s" % e, flush=True)
        continue
    cl = CokClient(timeout=20, account=acc)
    try:
        with account_lock(timeout=8, purpose="probe", key=uid):
            cl.connect()
            cl.bin_handshake()
            cl.login()

            print("  -- autoQueue.data --", flush=True)
            d = show(cl, "autoQueue.data", {})
            if d:
                for k in ("status", "saveItems", "useItems", "stamina",
                          "lastStaminaTime", "lv", "autoCount", "force",
                          "format", "errorCode"):
                    if k in d:
                        print("       %-16s = %r" % (k, d[k]), flush=True)

            print("  -- autoQueue.status (两种类型) --", flush=True)
            show(cl, "autoQueue.status", {"status": 0}, "int0")
            show(cl, "autoQueue.status", {"status": TypedInt(1, SFS_INT)}, "SFS_INT 1")
            show(cl, "autoQueue.status", {"status": "1"}, "str 1")
            show(cl, "autoQueue.status", {"status": TypedInt(0, SFS_INT)}, "SFS_INT 0")

            print("  -- autoQueue 其他 --", flush=True)
            show(cl, "autoQueue.levelMaxMonster", {})
            show(cl, "autoQueue.search", {"autoQueue": TypedInt(1, SFS_INT)})
    except Exception as e:  # noqa: BLE001
        print("  异常: %s" % str(e)[:120], flush=True)
    finally:
        cl.close()
