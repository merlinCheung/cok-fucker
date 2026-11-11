#!/usr/bin/env python3
"""探针4: 多兵种 marchKey 的**拼接顺序**到底按什么规则。

已知(探针3):
  * 两个标准兵种混编 -> 服务端**接受**(uuid 正常返回)
  * marchKey 内容被服务端**校验**: 写错 -> E000000; **反序** -> E000000
  * 66手游号上, "id 升序" 的拼接能通过

要分清两种假设:
  H1 顺序 = 兵种 id 升序
  H2 顺序 = 服务端 `world.user.march` 返回的 army 原始顺序(不排序)
  H3 顺序 = 战力降序 / 升序
在**另一个账号**上验证(如果它的 army 原始顺序 != id 升序, 就能区分 H1/H2)。

做法: 对每种候选顺序各发一次, 记下**哪个成功**。
失败不消耗士兵/体力(出征根本没成立), 所以可以放心试。

用法: python3 probe_multiproop_order.py [gameUid]
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import cok_hunt as H                                    # noqa: E402
from cok_client import CokClient, account_lock, apply_account_types  # noqa: E402
import cok_accounts as cas                              # noqa: E402
from cok_sfs import TypedInt, SFS_INT                   # noqa: E402

uid = sys.argv[1] if len(sys.argv) > 1 else "<uid-main>"
acc = apply_account_types(dict(cas.get_account(uid)))
cl = CokClient(timeout=25, account=acc)


def key_of(index, order, march_type=H.MARCH_TYPE_FIELDMONSTER):
    parts = [str(int(index)), "1021", str((int(march_type) + 1) * 1000)]
    for aid, speed, load, num in order:
        parts += [str(int(aid)), str(speed), str(load), str(int(num))]
    parts.append(H.MARCH_KEY_SALT)
    return hashlib.md5("".join(parts).encode()).hexdigest()


def main():
    with account_lock(timeout=5, purpose="probe", key=uid):
        cl.connect()
        cl.bin_handshake()
        cl.login()
        mk = H.read_march(cl)
        raw = [a for a in mk["all"] if int(a.get("free") or 0) > 0]
        print("服务端 army 原始顺序(有兵):",
              [(a["id"], a["free"], a.get("power")) for a in raw][:8])
        std = [a for a in raw if len(a["id"]) == 6 and a["id"].startswith("10")]
        std = std[:3]
        if len(std) < 2:
            print("标准兵种不足, 退出")
            return
        a1, a2 = std[0], std[1]
        n1, n2 = min(2, int(a1["free"])), min(2, int(a2["free"]))
        print("\n用兵种:", a1["id"], "(idx0)", "+", a2["id"], "(idx1)")
        print("  id 升序? ", a1["id"] < a2["id"])
        print("  战力降序?", (a1.get("power") or 0) >= (a2.get("power") or 0))

        def entry(a, n):
            return (a["id"], a.get("speed"), a.get("load"), n)

        cands = {
            "id升序": sorted([entry(a1, n1), entry(a2, n2)],
                             key=lambda x: int(x[0])),
            "id倒序": sorted([entry(a1, n1), entry(a2, n2)],
                             key=lambda x: int(x[0]), reverse=True),
            "原始顺序": [entry(a1, n1), entry(a2, n2)],
            "原始倒序": [entry(a2, n2), entry(a1, n1)],
            "战力降序": sorted([entry(a1, n1), entry(a2, n2)],
                               key=lambda x: -(x[1] or 0)),
            "战力升序": sorted([entry(a1, n1), entry(a2, n2)],
                               key=lambda x: (x[1] or 0)),
        }
        soldiers = {str(a1["id"]): TypedInt(n1, SFS_INT),
                    str(a2["id"]): TypedInt(n2, SFS_INT)}
        winner = None
        for label, order in cands.items():
            f = H.find_monster(cl, 1)
            idx = H.point_index(f["x"], f["y"])
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
            print("  候选 %-8s 顺序=%s -> errorCode=%s"
                  % (label, [x[0] for x in order], code))
            if not code:
                winner = label
                break
        print("\n=> 通过的候选顺序:", winner)
        print("   soldiers 明细(参考):",
              json.dumps({str(a1["id"]): n1, str(a2["id"]): n2}))


if __name__ == "__main__":
    try:
        main()
    finally:
        try:
            cl.close()
        except Exception:  # noqa: BLE001
            pass
