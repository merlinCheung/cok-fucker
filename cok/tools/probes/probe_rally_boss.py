#!/usr/bin/env python3
"""探测: 巨型狮鹫(活动怪) + 集结(rally) 相关协议。

只做**只读**探测, 不出征(出征会真扣体力/兵):
  1. login.dataconfig -> 看有没有 world_rally_k1..k4 / worldConfig
  2. res.tile.find type=7 level=12/21/30 -> 活动怪(巨型狮鹫)坐标
  3. world.get 附近地块 -> 找 boss 地块字段
  4. alliance.team.ls -> 联盟集结列表
  5. world.npcboss.march.check / world.march.check -> 参数探测
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import cok_accounts as accounts  # noqa: E402
from cok_client import CokClient  # noqa: E402


def show(title, obj, limit=1500):
    print("\n=== %s ===" % title)
    txt = json.dumps(obj, ensure_ascii=False, default=str)
    print(txt[:limit])


def main():
    key = sys.argv[1] if len(sys.argv) > 1 else "<uid-main>"
    acc = accounts.get_account(key)
    if not acc:
        print("[!] 没有账号 %s" % key)
        return 2
    c = CokClient(account=acc, timeout=25.0).connect()
    c.bin_handshake()
    c.login()
    for _ in range(2):
        try:
            c.call("cmd.ping")
        except Exception:
            pass

    # 1. dataconfig —— 集结时间配置在不在这里
    try:
        r = c.call("login.dataconfig")
        p = r.get("__params__") or {}
        show("login.dataconfig keys", sorted(p.keys())[:80])
        for k in ("worldConfig", "world_rally_k1", "world_rally_k2",
                  "world_rally_k3", "world_rally_k4", "boss_decr"):
            if k in p:
                print("  %s = %r" % (k, p[k]))
        wc = p.get("worldConfig")
        if isinstance(wc, dict):
            print("  worldConfig 子键:", sorted(wc.keys())[:60])
            for k in sorted(wc.keys()):
                if "rally" in k or "boss" in k or "stam" in k:
                    print("    %s = %r" % (k, wc[k]))
        # 也可能在嵌套 dict 里
        for k, v in p.items():
            if isinstance(v, dict) and "worldConfig" in v:
                show("nested worldConfig @ %s" % k, v["worldConfig"])
    except Exception as e:  # noqa: BLE001
        print("[!] login.dataconfig 失败: %s" % str(e)[:200])

    # 2. 活动怪搜索(type=7)
    for lv in (12, 21, 30, 35):
        try:
            r = c.call("res.tile.find", {"type": 7, "level": lv, "NoRecord": 1})
            p = r.get("__params__") or {}
            show("res.tile.find type=7 level=%d" % lv, p, 500)
        except Exception as e:  # noqa: BLE001
            print("[!] type=7 lv=%d 失败: %s" % (lv, str(e)[:160]))

    # 3. 联盟集结列表
    for cmd, params in (("alliance.team.ls", {"side": 1}),
                        ("team.war.ls", {}),
                        ("world.npcboss.march.check", {}),
                        ("world.march.check", {}),
                        ("worldboss", {"op": 0, "type": 16})):
        try:
            r = c.call(cmd, params)
            show(cmd, r.get("__params__") or {}, 800)
        except Exception as e:  # noqa: BLE001
            print("[!] %s 失败: %s" % (cmd, str(e)[:160]))

    c.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
