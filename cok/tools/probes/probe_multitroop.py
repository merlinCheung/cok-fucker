#!/usr/bin/env python3
"""探针: 服务端到底让不让我**一次出征带多个兵种**(混编)。

要回答三件事:
  1. `world.march` 的 `soldiers` 里放**两个标准兵种**, 服务端收不收?
     (错误码是什么; 成功的判据 = 响应里有 `$_monitor_log_$.uuid`)
  2. `marchKey` 服务端**校不校验**?
     -> 用一个明显错的 key 试一次: 成功 = 不校验(混编顺序随便拼)
     -> 失败 = 校验(必须还原客户端的散列表遍历顺序)
  3. **活动限定兵种**(8 位 id)能不能跟普通兵种混编?
     (之前只在"编成串"上撞过 E000000, 手动出征是另一条路, 要单独验)

⚠ 真的会出征(消耗士兵和体力), 所以:
  * 每次只派**少量兵**(每种 1~2 个), 1 级怪;
  * 只跑必要的组合, 不做大规模扫图。

用法: python3 probe_multitroop.py [gameUid]
"""
import hashlib
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import cok_hunt as H                                    # noqa: E402
from cok_client import CokClient, account_lock, apply_account_types  # noqa: E402
import cok_accounts as cas                              # noqa: E402

uid = sys.argv[1] if len(sys.argv) > 1 else "<uid-other>"
acc = apply_account_types(dict(cas.get_account(uid)))
cl = CokClient(timeout=25, account=acc)


def multi_march_key(index, army, march_type=H.MARCH_TYPE_FIELDMONSTER):
    """自己算多兵种 marchKey(绕过 cok_hunt.march_key 的单兵种限制)。

    客户端算法: md5(index + "1021" + (marchType+1)*1000 + [armyId,speed,load,num]* + 盐)
    多兵种时 army 的拼接顺序取决于客户端散列表遍历顺序 —— 这里两种顺序都试。
    """
    parts = [str(int(index)), "1021", str((int(march_type) + 1) * 1000)]
    for aid, (speed, load, num) in army.items():
        parts += [str(int(aid)), str(speed), str(load), str(int(num))]
    parts.append(H.MARCH_KEY_SALT)
    return hashlib.md5("".join(parts).encode()).hexdigest()


def try_march(label, soldiers, key, point_idx):
    """发一次 world.march, 打印结果。"""
    params = {
        "point": int(point_idx),
        "type": H.MARCH_TYPE_FIELDMONSTER,
        "soldiers": soldiers,
        "generalId": "",
        "petDragonUid": "",
        "aormationId": "",
        "autoQueue": 0,
        "marchKey": key,
    }
    try:
        r = cl.call("world.march", params)
    except Exception as e:  # noqa: BLE001
        print("  [%s] 调用异常: %s" % (label, str(e)[:120]))
        return None
    p = r.get("__params__") or {}
    code = p.get("errorCode")
    log = p.get("$_monitor_log_$") or {}
    uuid = str(log.get("uuid") or "")
    print("  [%s] errorCode=%s uuid=%s %s"
          % (label, code, uuid[:10], (json.dumps(log)[:160] if log else "")))
    return {"ok": not code, "uuid": uuid, "errorCode": code, "params": p}


import json  # noqa: E402


def main():
    with account_lock(timeout=5, purpose="probe", key=uid):
        cl.connect()
        cl.bin_handshake()
        cl.login()
        mk = H.read_march(cl)
        pool = H.usable_army(mk["army"])
        std = [a for a in pool if len(a["id"]) == 6 and a["id"].startswith("10")]
        act = [a for a in pool if not (len(a["id"]) == 6 and a["id"].startswith("10"))]
        print("标准兵种:", [(a["id"], a["free"]) for a in std][:6])
        print("活动兵种:", [(a["id"], a["free"]) for a in act][:6])
        if len(std) < 2:
            print("标准兵种不足 2 种, 探针跑不了")
            return
        st = H.read_stamina(cl)
        print("体力:", st)

        # 找一个 1 级怪当目标
        f = H.find_monster(cl, 1)
        if not f.get("ok"):
            print("找怪失败:", f)
            return
        idx = H.point_index(f["x"], f["y"])
        print("目标怪 (%s,%s) index=%s" % (f.get("x"), f.get("y"), idx))

        a1, a2 = std[0], std[1]
        # 每种只派 2 个兵, 尽量少消耗
        n1 = min(2, int(a1["free"]))
        n2 = min(2, int(a2["free"]))

        from cok_sfs import TypedInt, SFS_INT

        # --- 1) 两个标准兵种混编 ---
        # 客户端多兵种的拼接顺序未知 -> 两种顺序各试一次
        for order, label in (("A/B", "混编/顺序A"), ("B/A", "混编/顺序B")):
            if order == "A/B":
                army_ordered = {str(a1["id"]): (a1.get("speed"), a1.get("load"), n1),
                                str(a2["id"]): (a2.get("speed"), a2.get("load"), n2)}
            else:
                army_ordered = {str(a2["id"]): (a2.get("speed"), a2.get("load"), n2),
                                str(a1["id"]): (a1.get("speed"), a1.get("load"), n1)}
            key_guess = multi_march_key(idx, army_ordered, H.MARCH_TYPE_FIELDMONSTER)
            soldiers = {str(a1["id"]): TypedInt(n1, SFS_INT),
                        str(a2["id"]): TypedInt(n2, SFS_INT)}
            print("\n[1] 两个标准兵种混编(%s):" % label)
            r = try_march(label, soldiers, key_guess, idx)
            if r and r.get("ok"):
                r1 = r
                break
        else:
            r1 = None

        # --- 2) 混编 + 故意写错 marchKey(看服务端校不校验) ---
        if r1 is None:
            print("\n[2] marchKey 故意写错(看服务端校不校验):")
            soldiers2 = {str(a1["id"]): TypedInt(n1, SFS_INT),
                         str(a2["id"]): TypedInt(n2, SFS_INT)}
            try_march("混编/错key", soldiers2, "deadbeef" * 4, idx)
        else:
            print("\n[2] 混编已成功, 跳过错 key 测试(避免多余出征)")

        # --- 3) 活动限定兵种 + 普通兵种混编 ---
        if act:
            a3 = act[0]
            n3 = min(1, int(a3["free"]))
            soldiers3 = {str(a3["id"]): TypedInt(n3, SFS_INT),
                         str(a1["id"]): TypedInt(n1, SFS_INT)}
            army3 = {str(a3["id"]): (a3.get("speed"), a3.get("load"), n3),
                     str(a1["id"]): (a1.get("speed"), a1.get("load"), n1)}
            print("\n[3] 活动兵种 %s + 普通兵种 %s 混编:" % (a3["id"], a1["id"]))
            try_march("活动混编", soldiers3,
                      multi_march_key(idx, army3, H.MARCH_TYPE_FIELDMONSTER), idx)
        else:
            print("\n[3] 没有活动限定兵种, 跳过")

        time.sleep(2)
        mk2 = H.read_march(cl)
        print("\n出征后 army(march 数):",
              [(a["id"], a["march"], a["free"]) for a in mk2["all"]][:6])
        print("在外队伍数:", len(mk2["marches"]))


if __name__ == "__main__":
    try:
        main()
    finally:
        try:
            cl.close()
        except Exception:  # noqa: BLE001
            pass
