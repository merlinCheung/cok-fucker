#!/usr/bin/env python3
"""探测 4: 巨型狮鹫地块详情 + 集结出征(world.march type=4)参数。

**只读为主**: 集结出征会真扣体力/兵, 所以这里只:
  1. 用 world.get 拿地块原始字段(找 boss 地块 + monsterId)
  2. 用 world.get.detail / world.get.monster 查详情
  3. 打印算出好的集结参数(不发送), 供人工确认
"""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import cok_accounts as accounts  # noqa: E402
import cok_hunt  # noqa: E402
from cok_client import CokClient  # noqa: E402
from cok_sfs import TypedInt, SFS_INT  # noqa: E402

#: 巨型狮鹫的 ItemSpec id(数据库 field_monster 组, name=650066)
BOSS_IDS = {12: "902113", 21: "902114", 30: "902115", 35: "902150"}


def I(v):
    return TypedInt(int(v), SFS_INT)


def main():
    key = sys.argv[1] if len(sys.argv) > 1 else "<uid-main>"
    acc = accounts.get_account(key)
    c = CokClient(account=acc, timeout=25.0).connect()
    c.bin_handshake()
    c.login()
    for _ in range(2):
        try:
            c.call("cmd.ping")
        except Exception:
            pass

    # 1. 活动怪坐标 -> world.get 原始地块
    for lv in (12, 21, 30):
        rr = c.call("res.tile.find", {"type": 7, "level": lv, "NoRecord": 1})
        p = rr.get("__params__") or {}
        x, y = p.get("x"), p.get("y")
        if x in (None, -1):
            print("[!] lv=%d 没找到活动怪" % lv)
            continue
        idx = cok_hunt.point_index(x, y)
        print("\n===== 活动怪 lv=%d 坐标(%s,%s) index=%s" % (lv, x, y, idx))
        try:
            r = c.call("world.get", {"x": I(x), "y": I(y), "type": I(0),
                                     "serverId": I(2223), "timeStamp": I(int(time.time()))},
                       retries=0)
            pp = r.get("__params__") or {}
            if pp.get("errorCode"):
                print("  world.get 错误:", pp.get("errorCode"))
            pts = pp.get("points") or []
            tiles = []
            for it in pts:
                try:
                    got = json.loads(it) if isinstance(it, str) else it
                except Exception:
                    continue
                if isinstance(got, list):
                    tiles += [g for g in got if isinstance(g, dict)]
                elif isinstance(got, dict):
                    tiles.append(got)
            print("  地块数 %d" % len(tiles))
            for t in tiles[:12]:
                print("   ", json.dumps(t, ensure_ascii=False)[:300])
            # 找含 902113/902114/902115 的地块
            for t in tiles:
                s = json.dumps(t, ensure_ascii=False)
                for lv2, bid in BOSS_IDS.items():
                    if bid in s:
                        print("  ★ 命中 巨型狮鹫 lv=%d id=%s:" % (lv2, bid))
                        print("   ", s[:600])
                        break
        except Exception as e:  # noqa: BLE001
            print("  [!] world.get 失败: %s" % str(e)[:160])

    # 2. 集结参数预演(只算不发)
    print("\n===== 集结参数预演(type=4 MethodRally) =====")
    st = cok_hunt.read_stamina(c)
    print("  体力:", st)
    army = cok_hunt.list_army(c)
    std = cok_hunt.standard_army(army)
    print("  可用标准兵种:", [(a["id"], a["free"], a.get("power")) for a in std[:5]])
    if std:
        a = std[0]
        num = min(1000, a["free"])
        key_m = cok_hunt.march_key(
            cok_hunt.point_index(1002, 668),
            {a["id"]: (a.get("speed"), a.get("load"), num)},
            march_type=4)
        print("  marchKey(type=4, index=1002*668):", key_m)
        print("  对比 type=6:", cok_hunt.march_key(
            cok_hunt.point_index(1002, 668),
            {a["id"]: (a.get("speed"), a.get("load"), num)},
            march_type=6))

    c.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
