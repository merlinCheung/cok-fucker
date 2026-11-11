#!/usr/bin/env python3
"""探针2: 服务端**校不校验 marchKey**? 以及混编队伍的行军明细长什么样。

要回答:
  1. 故意写错 marchKey, 服务端还收不收?
     -> 收 = 不校验(混编顺序可以随便拼, 不用还原客户端散列表顺序)
     -> 不收 = 校验(必须还原顺序, 上一个探针的"顺序A"能过说明顺序猜对了)
  2. 混编队伍回来前, `world.user.march` 的 `m` 明细里 army[] 是什么结构?
     (判回和"在外人数"都依赖这个结构)

用法: python3 probe_multitroop2.py [gameUid]
"""
import hashlib
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import cok_hunt as H                                    # noqa: E402
from cok_client import CokClient, account_lock, apply_account_types  # noqa: E402
import cok_accounts as cas                              # noqa: E402
from cok_sfs import TypedInt, SFS_INT                   # noqa: E402

uid = sys.argv[1] if len(sys.argv) > 1 else "<uid-other>"
acc = apply_account_types(dict(cas.get_account(uid)))
cl = CokClient(timeout=25, account=acc)


def multi_march_key(index, army, march_type=H.MARCH_TYPE_FIELDMONSTER):
    parts = [str(int(index)), "1021", str((int(march_type) + 1) * 1000)]
    for aid, (speed, load, num) in army.items():
        parts += [str(int(aid)), str(speed), str(load), str(int(num))]
    parts.append(H.MARCH_KEY_SALT)
    return hashlib.md5("".join(parts).encode()).hexdigest()


def march(label, soldiers, key, idx):
    params = {"point": int(idx), "type": H.MARCH_TYPE_FIELDMONSTER,
              "soldiers": soldiers, "generalId": "", "petDragonUid": "",
              "aormationId": "", "autoQueue": 0, "marchKey": key}
    try:
        r = cl.call("world.march", params)
    except Exception as e:  # noqa: BLE001
        print("  [%s] 异常: %s" % (label, str(e)[:120]))
        return None
    p = r.get("__params__") or {}
    log = p.get("$_monitor_log_$") or {}
    print("  [%s] errorCode=%s uuid=%s"
          % (label, p.get("errorCode"), str(log.get("uuid") or "")[:10]))
    return {"ok": not p.get("errorCode"), "params": p}


def main():
    with account_lock(timeout=5, purpose="probe", key=uid):
        cl.connect()
        cl.bin_handshake()
        cl.login()
        mk = H.read_march(cl)
        std = [a for a in H.usable_army(mk["army"])
               if len(a["id"]) == 6 and a["id"].startswith("10")]
        a1, a2 = std[0], std[1]
        n1, n2 = min(2, int(a1["free"])), min(2, int(a2["free"]))
        print("用兵种:", a1["id"], n1, "+", a2["id"], n2)

        f = H.find_monster(cl, 1)
        idx = H.point_index(f["x"], f["y"])
        print("目标怪 index=%s" % idx)

        # --- 1) marchKey 故意写错 ---
        print("\n[1] 混编 + **写错的 marchKey**:")
        soldiers = {str(a1["id"]): TypedInt(n1, SFS_INT),
                    str(a2["id"]): TypedInt(n2, SFS_INT)}
        r = march("错key", soldiers, "deadbeef" * 4, idx)

        # --- 2) 混编队伍的行军明细结构 ---
        print("\n[2] 派出的队伍明细(等 2 秒读 m):")
        time.sleep(2)
        mk2 = H.read_march(cl)
        for u, e in list(mk2["marches"].items())[:4]:
            print("  uuid=%s st=%s et=%s army=%s"
                  % (u[:10], e.get("st"), e.get("et"),
                     json.dumps(e.get("army"), ensure_ascii=False)[:300]))
        print("  _march_troops 解析:",
              [H._march_troops(e) for e in mk2["marches"].values()][:4])

        # --- 3) 同兵种连续出征: 同一兵种再派一次 ---
        print("\n[3] **同兵种连续出征**(再派一次 %s):" % a1["id"])
        f2 = H.find_monster(cl, 1)
        idx2 = H.point_index(f2["x"], f2["y"])
        s1 = {str(a1["id"]): TypedInt(n1, SFS_INT)}
        army1 = {str(a1["id"]): (a1.get("speed"), a1.get("load"), n1)}
        march("同兵种", s1, multi_march_key(idx2, army1), idx2)
        time.sleep(2)
        mk3 = H.read_march(cl)
        print("  在外队伍数:", len(mk3["marches"]))
        for u, e in list(mk3["marches"].items())[:4]:
            print("  uuid=%s army=%s"
                  % (u[:10], json.dumps(e.get("army"), ensure_ascii=False)[:200]))
        print("  army[].march:",
              [(a["id"], a["march"], a["free"]) for a in mk3["all"]][:8])


if __name__ == "__main__":
    try:
        main()
    finally:
        try:
            cl.close()
        except Exception:  # noqa: BLE001
            pass
