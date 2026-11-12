#!/usr/bin/env python3
"""探针7: 混编队伍的 `m[].army` **原始结构**到底长什么样。

为什么要专门查: 混编时 `army` 字段的形态和单兵种不一样(实测见过 list 和
dict 两种), `_march_troops` 解析错的话"在外人数"就一直是 0。

要拿到:
  * 标准兵种 2 种混编 -> army 是 list 还是 dict? 每项怎么对应兵种?
  * 活动兵种 2 种混编 -> 同上
  * 单兵种(对照)

用法: python3 probe_multiproop_struct.py <gameUid>
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
    parts = [str(int(index)), "1021", str((int(march_type) + 1) * 1000)]
    for aid, speed, load, num in sorted(entries, key=lambda x: str(x[0])):
        parts += [str(int(aid)), str(speed), str(load), str(int(num))]
    parts.append(H.MARCH_KEY_SALT)
    return hashlib.md5("".join(parts).encode()).hexdigest()


def show(label, entries, idx):
    soldiers = {str(aid): TypedInt(num, SFS_INT) for aid, _s, _l, num in entries}
    params = {"point": int(idx), "type": H.MARCH_TYPE_FIELDMONSTER,
              "soldiers": soldiers, "generalId": "", "petDragonUid": "",
              "aormationId": "", "autoQueue": 0,
              "marchKey": key_of(idx, entries)}
    try:
        r = cl.call("world.march", params)
        p = r.get("__params__") or {}
        code = p.get("errorCode")
    except Exception as e:  # noqa: BLE001
        print("  [%s] 异常 %s" % (label, str(e)[:100]))
        return
    print("  [%s] errorCode=%s" % (label, code))
    if code:
        return
    time.sleep(2)
    mk = H.read_march(cl)
    for u, e in mk["marches"].items():
        raw = e.get("army")
        print("    army 类型 =", type(raw).__name__)
        print("    army 原始 =", json.dumps(raw, ensure_ascii=False))
        print("    _march_troops =", H._march_troops(e))
        print("    整条 entry =", json.dumps(e, ensure_ascii=False)[:600])
        break


def main():
    with account_lock(timeout=5, purpose="probe", key=uid):
        cl.connect()
        cl.bin_handshake()
        cl.login()
        mk = H.read_march(cl)
        raw = [a for a in mk["all"] if int(a.get("free") or 0) > 0]
        std = [a for a in raw if len(a["id"]) == 6 and a["id"].startswith("10")]
        act = [a for a in raw if not (len(a["id"]) == 6 and a["id"].startswith("10"))]
        print("标准:", [(a["id"], a["free"]) for a in std][:4])
        print("活动:", [(a["id"], a["free"]) for a in act][:4])

        def ent(a, n):
            return (a["id"], a.get("speed"), a.get("load"), n)

        if len(std) >= 2:
            f = H.find_monster(cl, 1)
            idx = H.point_index(f["x"], f["y"])
            print("\n[标准 2 种混编]")
            show("std2", [ent(std[0], 2), ent(std[1], 2)], idx)
        if len(act) >= 2:
            f2 = H.find_monster(cl, 1)
            idx2 = H.point_index(f2["x"], f2["y"])
            print("\n[活动 2 种混编]")
            show("act2", [ent(act[0], 2), ent(act[1], 2)], idx2)
        if std:
            f3 = H.find_monster(cl, 1)
            idx3 = H.point_index(f3["x"], f3["y"])
            print("\n[标准单兵种 对照]")
            show("std1", [ent(std[0], 2)], idx3)


if __name__ == "__main__":
    try:
        main()
    finally:
        try:
            cl.close()
        except Exception:  # noqa: BLE001
            pass
