#!/usr/bin/env python3
"""探针6: 混编队伍的行军明细里, `armId` 索引对应哪个兵种?

已知(探针1/3/5):
  * 混编**成功**(标准+标准、活动+活动都行; 活动+普通 = E000000)
  * 服务端**校验 marchKey 内容**, 且多兵种的拼接顺序 =
    **soldiers 的 key 字典序升序**
    (证据: OPPO 号上发送顺序 57580618,57580218 但按 57580218,57580618
     拼 key 才成功 -> 服务端是按 key 升序自己遍历的)

还缺的: 标准兵种混编时, 明细是 list 形式
  [{"total":2,...,"armId":0},{"total":2,...,"armId":1}]
`armId` 是第几个兵种? 是**发送顺序**还是 **key 升序**?
这决定"在外人数"能不能按兵种对号。

做法: 故意让**发送顺序**与 **key 升序**不同, 看 armId 对应谁。
另外顺便验一下**三兵种**混编。

用法: python3 probe_multiproop_armid.py [gameUid]
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


def key_of(index, entries, march_type=H.MARCH_TYPE_FIELDMONSTER):
    """entries: [(id, speed, load, num)] —— 按 **key 升序** 拼(实测规则)。"""
    parts = [str(int(index)), "1021", str((int(march_type) + 1) * 1000)]
    for aid, speed, load, num in sorted(entries, key=lambda x: str(x[0])):
        parts += [str(int(aid)), str(speed), str(load), str(int(num))]
    parts.append(H.MARCH_KEY_SALT)
    return hashlib.md5("".join(parts).encode()).hexdigest()


def main():
    with account_lock(timeout=5, purpose="probe", key=uid):
        cl.connect()
        cl.bin_handshake()
        cl.login()
        mk = H.read_march(cl)
        std = [a for a in mk["all"]
               if len(a["id"]) == 6 and a["id"].startswith("10")
               and int(a.get("free") or 0) > 0]
        print("标准兵种:", [(a["id"], a["free"]) for a in std][:6])
        if len(std) < 3:
            print("不足 3 种标准兵种, 退出")
            return
        a1, a2, a3 = std[0], std[1], std[2]

        def ent(a, n):
            return (a["id"], a.get("speed"), a.get("load"), n)

        n1 = min(2, int(a1["free"]))
        n2 = min(2, int(a2["free"]))
        n3 = min(2, int(a3["free"]))

        # --- 1) 两兵种: 发送顺序与 key 升序不同 ---
        print("\n[1] 两兵种, **发送顺序 = %s, %s**(看 key 升序是 %s, %s)"
              % (a1["id"], a2["id"], *sorted([a1["id"], a2["id"]])))
        f = H.find_monster(cl, 1)
        idx = H.point_index(f["x"], f["y"])
        soldiers = {str(a1["id"]): TypedInt(n1, SFS_INT),
                    str(a2["id"]): TypedInt(n2, SFS_INT)}
        params = {"point": int(idx), "type": H.MARCH_TYPE_FIELDMONSTER,
                  "soldiers": soldiers, "generalId": "", "petDragonUid": "",
                  "aormationId": "", "autoQueue": 0,
                  "marchKey": key_of(idx, [ent(a1, n1), ent(a2, n2)])}
        r = cl.call("world.march", params)
        p = r.get("__params__") or {}
        print("  errorCode=%s uuid=%s" % (p.get("errorCode"),
              str((p.get("$_monitor_log_$") or {}).get("uuid") or "")[:10]))
        time.sleep(2)
        mk2 = H.read_march(cl)
        for u, e in mk2["marches"].items():
            print("  明细 =", json.dumps(e.get("army"), ensure_ascii=False))
            print("  _march_troops =", H._march_troops(e))

        # --- 2) 三兵种混编 ---
        print("\n[2] 三兵种混编 %s + %s + %s" % (a1["id"], a2["id"], a3["id"]))
        f2 = H.find_monster(cl, 1)
        idx2 = H.point_index(f2["x"], f2["y"])
        soldiers3 = {str(a1["id"]): TypedInt(n1, SFS_INT),
                     str(a2["id"]): TypedInt(n2, SFS_INT),
                     str(a3["id"]): TypedInt(n3, SFS_INT)}
        params3 = {"point": int(idx2), "type": H.MARCH_TYPE_FIELDMONSTER,
                   "soldiers": soldiers3, "generalId": "", "petDragonUid": "",
                   "aormationId": "", "autoQueue": 0,
                   "marchKey": key_of(idx2, [ent(a1, n1), ent(a2, n2), ent(a3, n3)])}
        try:
            r3 = cl.call("world.march", params3)
            p3 = r3.get("__params__") or {}
            print("  errorCode=%s uuid=%s"
                  % (p3.get("errorCode"),
                     str((p3.get("$_monitor_log_$") or {}).get("uuid") or "")[:10]))
        except Exception as e:  # noqa: BLE001
            print("  异常:", str(e)[:120])
        time.sleep(2)
        mk3 = H.read_march(cl)
        print("  在外队伍数:", len(mk3["marches"]))
        for u, e in mk3["marches"].items():
            print("  明细 =", json.dumps(e.get("army"), ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    finally:
        try:
            cl.close()
        except Exception:  # noqa: BLE001
            pass
