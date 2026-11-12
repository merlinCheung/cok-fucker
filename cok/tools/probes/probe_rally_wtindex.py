#!/usr/bin/env python3
"""探测 8: 验证 wtIndex 各档 -> 集结时长的对应关系。

客户端 AllianceMassTeamViewLua:setTimeList:
    time1..time4 = dataConfig.world_rally k1..k4  (实测 5/10/30/60 分钟)
    按钮 m_btn1..m_btn4 -> tag=1..4 -> openMarchDeploy(..., wtIndex=tag)
    → 客户端只发**档位序号** wtIndex, 服务端自己按档位换算时长。

所以要确认: 换 wtIndex 后, 服务端回的集结里"结束时间"是否不同。
用 alliance.team.ls 读自己那条集结的 startTime / endTime / arrivalTime 对比。

⚠️ 会真的建 4 个集结(每个扣 20 体力 + 200 兵)。
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

sys.path.insert(0, HERE)
from probe_rally_march2 import find_boss_tiles  # noqa: E402


def I(v):
    return TypedInt(int(v), SFS_INT)


def my_rallies(c):
    """联盟集结列表里属于本账号的条目。"""
    r = c.call("alliance.team.ls", {"side": 1})
    p = r.get("__params__") or {}
    out = []
    for it in (p.get("list") or []):
        if not isinstance(it, dict):
            continue
        mine = any(m.get("uid") == str(c.account.get("gameUid"))
                   for m in (it.get("member") or []) if isinstance(m, dict))
        if mine:
            out.append(it)
    return out


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

    st = cok_hunt.read_stamina(c)
    print("[*] 体力: %s" % st["stamina"])

    bosses = find_boss_tiles(c, levels=(12,))
    if not bosses:
        print("[!] 没找到 lv12 巨型狮鹫")
        return 1
    target = bosses[0]
    idx = target["index"]
    print("[*] 目标 index=%s monsterId=%s" % (idx, target["monsterId"]))

    army = cok_hunt.list_army(c)
    a = cok_hunt.standard_army(army)[0]
    num = min(100, a["free"])

    def mkkey(mtype):
        return cok_hunt.march_key(
            idx, {a["id"]: (a.get("speed"), a.get("load"), num)}, march_type=mtype)

    for wt in (1, 2, 3, 4):
        params = {
            "point": I(idx),
            "type": I(4),
            "soldiers": {a["id"]: TypedInt(num, SFS_INT)},
            "generalId": "",
            "petDragonUid": "",
            "aormationId": "",
            "autoQueue": 0,
            "marchKey": mkkey(4),
            "wtIndex": I(wt),
        }
        try:
            r = c.call("world.march", params)
            p = r.get("__params__") or {}
            if p.get("errorCode"):
                print(">>> wtIndex=%d 失败: %s" % (wt, p.get("errorCode")))
                continue
            abt = p.get("allianceBattleTeam") or {}
            print(">>> wtIndex=%d 成功  uuid=%s startTime=%s endTime=%s"
                  % (wt, abt.get("uuid"), abt.get("startTime"), abt.get("endTime")))
            print("    全字段:", json.dumps(abt, ensure_ascii=False, default=str)[:900])
        except Exception as e:  # noqa: BLE001
            print(">>> wtIndex=%d 异常: %s" % (wt, str(e)[:160]))
        time.sleep(1.2)

    print("\n=== 联盟里我的集结 ===")
    for it in my_rallies(c):
        print(json.dumps({k: it.get(k) for k in
                          ("uuid", "startTime", "endTime", "arrivalTime",
                           "monsterId", "type", "rallyTime", "wtIndex")},
                         ensure_ascii=False, default=str))

    c.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
