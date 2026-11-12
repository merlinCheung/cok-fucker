#!/usr/bin/env python3
"""探测 7: 用 world.get 定位巨型狮鹫 + 集结出征参数真服实证。

⭐ 关键发现: `world.get` 的地块里有
     t=15  (WorldCityType.ActBossTile, 活动怪boss)
     t1="902113"/"902114"/"902115"  (monsterId = 巨型狮鹫各等级)
     i=index, mchp/mmhp=当前/最大血量, st/rt=出现/刷新时间
   → **不用 res.tile.find**, 所以不受每日搜索次数限制。

⚠️ 集结出征有真实副作用(扣体力 20 + 兵, 并在联盟里建集结)。
   从最像客户端的变体开始, 成功就停。
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

#: 巨型狮鹫 ItemSpec id -> 等级
BOSS_IDS = {"902113": 12, "902114": 21, "902115": 30, "902150": 35}
#: WorldCityType.ActBossTile
ACT_BOSS_TILE = 15


def I(v):
    return TypedInt(int(v), SFS_INT)


def fetch_tiles(c, x, y):
    """拉一片地块, 返回解析后的 list。"""
    r = c.call("world.get", {"x": I(x), "y": I(y), "type": I(0), "serverId": I(2223),
                             "timeStamp": I(int(time.time()))}, retries=0)
    p = r.get("__params__") or {}
    if p.get("errorCode"):
        return []
    tiles = []
    for it in (p.get("points") or []):
        try:
            got = json.loads(it) if isinstance(it, str) else it
        except Exception:
            continue
        if isinstance(got, list):
            tiles += [g for g in got if isinstance(g, dict)]
        elif isinstance(got, dict):
            tiles.append(got)
    return tiles


def find_boss_tiles(c, levels=None):
    """在已知 boss 聚集区扫描, 找出所有巨型狮鹫地块。

    巨型狮鹫固定刷在世界某片区域(实测 978~1040 / 668~693),
    这里扫一片就够; 找不到再扩大。
    """
    want = set(BOSS_IDS) if not levels else {
        bid for bid, lv in BOSS_IDS.items() if lv in levels}
    found = {}
    centers = [(1002, 668), (978, 693), (1014, 689), (1019, 692),
               (1002, 668), (1010, 680), (990, 680)]
    seen = set()
    for cx, cy in centers:
        for t in fetch_tiles(c, cx, cy):
            if t.get("t") != ACT_BOSS_TILE:
                continue
            mid = str(t.get("t1") or "")
            if mid not in want:
                continue
            idx = t.get("i")
            if idx in seen:
                continue
            seen.add(idx)
            found[idx] = {
                "index": int(idx), "monsterId": mid,
                "level": BOSS_IDS.get(mid),
                "hp": t.get("mchp"), "maxHp": t.get("mmhp"),
                "start": t.get("st"), "refresh": t.get("rt"),
            }
    return list(found.values())


def main():
    key = sys.argv[1] if len(sys.argv) > 1 else "<uid-main>"
    level = int(sys.argv[2]) if len(sys.argv) > 2 else 12
    do_march = "--march" in sys.argv
    acc = accounts.get_account(key)
    c = CokClient(account=acc, timeout=25.0).connect()
    c.bin_handshake()
    c.login()
    for _ in range(2):
        try:
            c.call("cmd.ping")
        except Exception:
            pass

    st = cok_hunt.read_stamina(c)
    print("[*] 体力: %s/%s" % (st["stamina"], st["max"]))

    bosses = find_boss_tiles(c)
    print("[*] 扫到巨型狮鹫地块 %d 个:" % len(bosses))
    for b in bosses:
        print("    index=%s 等级=%s hp=%s/%s monsterId=%s"
              % (b["index"], b["level"], b["hp"], b["maxHp"], b["monsterId"]))
    target = None
    for b in bosses:
        if b["level"] == level:
            target = b
            break
    if not target:
        print("[!] 没找到等级 %d 的巨型狮鹫" % level)
        c.close()
        return 1
    print("[*] 目标: %r" % target)

    if not do_march:
        print("\n[*] 只读模式结束(加 --march 才会真的出征)")
        c.close()
        return 0

    army = cok_hunt.list_army(c)
    std = cok_hunt.standard_army(army)
    a = std[0]
    num = min(200, a["free"])
    idx = target["index"]
    mid = target["monsterId"]

    def mkkey(mtype):
        return cok_hunt.march_key(
            idx, {a["id"]: (a.get("speed"), a.get("load"), num)}, march_type=mtype)

    def base(mtype, **extra):
        p = {
            "point": I(idx),
            "type": I(mtype),
            "soldiers": {a["id"]: TypedInt(num, SFS_INT)},
            "generalId": "",
            "petDragonUid": "",
            "aormationId": "",
            "autoQueue": 0,
            "marchKey": mkkey(mtype),
        }
        p.update(extra)
        return p

    variants = [
        ("V1 type=4 wtIndex=1", base(4, wtIndex=I(1))),
        ("V2 V1+monsterId", base(4, wtIndex=I(1), monsterId=mid)),
        ("V3 V1+other=1", base(4, wtIndex=I(1), other="1")),
        ("V4 type=4 无 wtIndex", base(4)),
        ("V5 type=6 wtIndex=1", base(6, wtIndex=I(1))),
        ("V6 type=17 wtIndex=1", base(17, wtIndex=I(1))),
        ("V7 type=4 wtIndex=1 ownerFlag=1",
         base(4, wtIndex=I(1), ownerFlag=I(1))),
        ("V8 type=4 wtIndex=1 +ept", base(4, wtIndex=I(1), ept=0)),
    ]

    for name, params in variants:
        try:
            r = c.call("world.march", params)
            p = r.get("__params__") or {}
            ok = not p.get("errorCode")
            print("\n>>> %s" % name)
            print("    ->", json.dumps(p, ensure_ascii=False, default=str)[:500])
            if ok:
                print("\n[OK] 成功: %s" % name)
                st2 = cok_hunt.read_stamina(c)
                print("[*] 体力后: %s" % st2["stamina"])
                try:
                    r2 = c.call("alliance.team.ls", {"side": 1})
                    lst = (r2.get("__params__") or {}).get("list") or []
                    print("[*] 联盟集结列表 %d 条, 最新:" % len(lst))
                    for it in lst[:2]:
                        print("    ", json.dumps(it, ensure_ascii=False)[:500])
                except Exception as e:  # noqa: BLE001
                    print("[!] alliance.team.ls 失败:", str(e)[:120])
                break
        except Exception as e:  # noqa: BLE001
            print("\n>>> %s 异常: %s" % (name, str(e)[:200]))
        time.sleep(1.0)

    c.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
