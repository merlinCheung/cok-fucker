#!/usr/bin/env python3
"""探测 5: 巨型狮鹫**集结出征**的真实参数组合(真服实证)。

⚠️ 有真实副作用: 成功会真的派出部队(扣体力 20 + 兵), 并在联盟里建一个集结。
   所以: 从最像客户端的变体开始, **成功就停**, 每次只试一个。

客户端路径(已逆向确认):
  MonsterTilePopView:doAttack -> AllianceManager:openAllianceMassView(index)
    -> AllianceMassTeamViewLua (选集结时间, 4 个按钮 tag=1..4)
    -> openMarchDeploy(pointId, haveOwner=1, ..., bType=MethodRally(4), wtIndex=tag)
    -> BattleView -> world.march {type:4, wtIndex:1..4, ...}
  集结时长由**服务端** dataConfig.world_rally k1..k4 决定(5/10/30/60 分钟),
  客户端只发**档位序号** wtIndex。

变体顺序:
  V1 type=4 + wtIndex=1        (最像客户端)
  V2 V1 + monsterId
  V3 type=4 + wtIndex=1 + other="1"
  V4 type=4 无 wtIndex
  V5 type=6 + wtIndex=1        (纯攻击)
  V6 type=17 + wtIndex=1       (MethodNpcWorldBoss)
  V7 type=4 + wtIndex=5        (把分钟当序号传, 看错误码差异)
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

#: 巨型狮鹫 ItemSpec id(按等级)
BOSS_IDS = {12: "902113", 21: "902114", 30: "902115", 35: "902150"}


def I(v):
    return TypedInt(int(v), SFS_INT)


def find_boss(c, level):
    r = c.call("res.tile.find", {"type": 7, "level": level, "NoRecord": 1})
    p = r.get("__params__") or {}
    x, y = p.get("x"), p.get("y")
    if x in (None, -1) or y in (None, -1):
        return None
    return x, y, cok_hunt.point_index(x, y)


def main():
    key = sys.argv[1] if len(sys.argv) > 1 else "<uid-main>"
    level = int(sys.argv[2]) if len(sys.argv) > 2 else 12
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
    print("[*] 体力:", st["stamina"], "/", st["max"])
    army = cok_hunt.list_army(c)
    std = cok_hunt.standard_army(army)
    if not std:
        print("[!] 没有可用标准兵种")
        return 1
    a = std[0]
    num = min(200, a["free"])
    print("[*] 用兵种 %s x%d (库存 %d)" % (a["id"], num, a["free"]))

    spot = find_boss(c, level)
    if not spot:
        print("[!] 没找到 lv=%d 的活动怪(搜索次数可能用完)" % level)
        return 1
    x, y, idx = spot
    print("[*] 巨型狮鹫 lv=%d @(%s,%s) index=%s monsterId=%s"
          % (level, x, y, idx, BOSS_IDS.get(level)))

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

    boss_id = BOSS_IDS.get(level, "")
    variants = [
        ("V1 type=4 wtIndex=1", base(4, wtIndex=I(1))),
        ("V2 V1+monsterId", base(4, wtIndex=I(1), monsterId=boss_id)),
        ("V3 V1+other=1", base(4, wtIndex=I(1), other="1")),
        ("V4 type=4 无 wtIndex", base(4)),
        ("V5 type=6 wtIndex=1", base(6, wtIndex=I(1))),
        ("V6 type=17 wtIndex=1", base(17, wtIndex=I(1))),
        ("V7 type=4 wtIndex=5(分钟当序号)", base(4, wtIndex=I(5))),
        ("V8 type=4 wtIndex=1 ownerFlag=1",
         base(4, wtIndex=I(1), ownerFlag=I(1))),
    ]

    for name, params in variants:
        try:
            r = c.call("world.march", params)
            p = r.get("__params__") or {}
            ok = not p.get("errorCode")
            print("\n>>> %s" % name)
            print("    ->", json.dumps(p, ensure_ascii=False, default=str)[:600])
            if ok:
                print("\n[OK] 成功: %s" % name)
                st2 = cok_hunt.read_stamina(c)
                print("[*] 体力后:", st2["stamina"])
                try:
                    r2 = c.call("alliance.team.ls", {"side": 1})
                    lst = (r2.get("__params__") or {}).get("list") or []
                    print("[*] 联盟集结列表条数:", len(lst))
                    for it in lst[:3]:
                        print("    ", json.dumps(it, ensure_ascii=False)[:400])
                except Exception as e:  # noqa: BLE001
                    print("[!] alliance.team.ls 失败:", str(e)[:120])
                break
        except Exception as e:  # noqa: BLE001
            print("\n>>> %s  异常: %s" % (name, str(e)[:200]))
        time.sleep(1.0)

    c.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
