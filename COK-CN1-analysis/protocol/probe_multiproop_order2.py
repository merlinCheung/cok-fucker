#!/usr/bin/env python3
"""探针5: 活动限定兵种之间能不能混编? 以及 marchKey 的顺序规则到底是哪一种。

为什么要在 OPPO 号上测:
  这个号的 `world.user.march` 返回的 army **原始顺序**是
  57580618, 57580218, 57580518, 57580118, 57580418, 107310
  —— 和 "id 升序" **完全不同**, 所以能区分两种假设:
    H2 顺序 = 服务端返回的原始顺序
    H1 顺序 = 兵种 id 升序

要回答:
  1. 活动兵种 + 活动兵种 混编行不行?
     (之前只验过 活动+普通 = E000000; 活动+活动没验过。
      活动兵库存最大(几十万), 如果能混编, 混编的实用价值最大。)
  2. 哪种拼接顺序能通过服务端校验?

失败不消耗士兵/体力(出征没成立), 所以可以放心穷举候选。

用法: python3 probe_multiproop_order2.py [gameUid]
"""
import hashlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import cok_hunt as H                                    # noqa: E402
from cok_client import CokClient, account_lock, apply_account_types  # noqa: E402
import cok_accounts as cas                              # noqa: E402
from cok_sfs import TypedInt, SFS_INT                   # noqa: E402

uid = sys.argv[1] if len(sys.argv) > 1 else "<uid-guopan>"
acc = apply_account_types(dict(cas.get_account(uid)))
cl = CokClient(timeout=25, account=acc)


def key_of(index, order, march_type=H.MARCH_TYPE_FIELDMONSTER):
    parts = [str(int(index)), "1021", str((int(march_type) + 1) * 1000)]
    for aid, speed, load, num in order:
        parts += [str(int(aid)), str(speed), str(load), str(int(num))]
    parts.append(H.MARCH_KEY_SALT)
    return hashlib.md5("".join(parts).encode()).hexdigest()


def try_order(label, idx, a, b, na, nb):
    """a/b = army 条目; na/nb = 派兵数。"""
    order = [(a["id"], a.get("speed"), a.get("load"), na),
             (b["id"], b.get("speed"), b.get("load"), nb)]
    soldiers = {str(a["id"]): TypedInt(na, SFS_INT),
                str(b["id"]): TypedInt(nb, SFS_INT)}
    params = {"point": int(idx), "type": H.MARCH_TYPE_FIELDMONSTER,
              "soldiers": soldiers, "generalId": "", "petDragonUid": "",
              "aormationId": "", "autoQueue": 0,
              "marchKey": key_of(idx, order)}
    try:
        r = cl.call("world.march", params)
        p = r.get("__params__") or {}
        code = p.get("errorCode")
    except Exception as e:  # noqa: BLE001
        code = "EXC:%s" % str(e)[:60]
    print("  %-12s 顺序=%s -> errorCode=%s"
          % (label, [x[0] for x in order], code))
    return not code


def main():
    with account_lock(timeout=5, purpose="probe", key=uid):
        cl.connect()
        cl.bin_handshake()
        cl.login()
        mk = H.read_march(cl)
        raw = [a for a in mk["all"] if int(a.get("free") or 0) > 0]
        print("army 原始顺序(有兵):",
              [(a["id"], a["free"], a.get("power")) for a in raw][:8])
        act = [a for a in raw if not (len(a["id"]) == 6 and a["id"].startswith("10"))]
        std = [a for a in raw if len(a["id"]) == 6 and a["id"].startswith("10")]
        if len(act) >= 2:
            a, b = act[0], act[1]
            na, nb = min(2, int(a["free"])), min(2, int(b["free"]))
            print("\n[A] 活动兵种 %s + %s 混编:" % (a["id"], b["id"]))
            cands = {
                "原始顺序": [a, b],
                "原始倒序": [b, a],
                "id升序": sorted([a, b], key=lambda x: int(x["id"])),
                "id倒序": sorted([a, b], key=lambda x: int(x["id"]), reverse=True),
            }
            for label, (x, y) in cands.items():
                f = H.find_monster(cl, 1)
                idx = H.point_index(f["x"], f["y"])
                if try_order(label, idx, x, y, min(2, int(x["free"])),
                             min(2, int(y["free"]))):
                    print("  => **通过: %s**" % label)
                    break
        else:
            print("活动兵种不足 2 种, 跳过 [A]")

        if len(std) >= 2:
            a, b = std[0], std[1]
            print("\n[B] 标准兵种 %s + %s 混编:" % (a["id"], b["id"]))
            for label, (x, y) in {
                "原始顺序": [a, b],
                "原始倒序": [b, a],
                "id升序": sorted([a, b], key=lambda x: int(x["id"])),
                "id倒序": sorted([a, b], key=lambda x: int(x["id"]), reverse=True),
            }.items():
                f = H.find_monster(cl, 1)
                idx = H.point_index(f["x"], f["y"])
                if try_order(label, idx, x, y, min(2, int(x["free"])),
                             min(2, int(y["free"]))):
                    print("  => **通过: %s**" % label)
                    break
        else:
            print("标准兵种不足 2 种, 跳过 [B]")

        time_import = __import__("time")
        time_import.sleep(2)
        mk2 = H.read_march(cl)
        print("\n在外队伍:", len(mk2["marches"]))
        for u, e in mk2["marches"].items():
            print("  uuid=%s army=%s" % (u[:10], e.get("army")))


if __name__ == "__main__":
    try:
        main()
    finally:
        try:
            cl.close()
        except Exception:  # noqa: BLE001
            pass
