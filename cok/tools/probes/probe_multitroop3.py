#!/usr/bin/env python3
"""探针3: 混编的三个决定性细节。

  1. marchKey 的**拼接顺序**到底按什么?
     错 key -> E000000(探针2), 说明服务端**校验内容**。
     所以顺序错了整次出征白跑(不消耗, 但白花一次请求)。
     这里测: 反序(id 倒序)行不行? 行 -> 只校验格式/顺序不敏感;
              不行 -> 顺序敏感, 必须还原客户端顺序。
  2. 混编队伍的行军明细 `m[].army` **完整结构**是什么?
     (探针2 只看到第一个兵种的数量, 第二个兵种的数量没解析出来)
  3. 混编队伍**回来后** `army[].march` / `free` 是否正确归位?

用法: python3 probe_multitroop3.py [gameUid]
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


def key_of(index, order, march_type=H.MARCH_TYPE_FIELDMONSTER):
    """order: [(army_id, speed, load, num), ...] 按给定顺序拼接。"""
    parts = [str(int(index)), "1021", str((int(march_type) + 1) * 1000)]
    for aid, speed, load, num in order:
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
    ok = not p.get("errorCode")
    print("  [%s] errorCode=%s uuid=%s"
          % (label, p.get("errorCode"), str(log.get("uuid") or "")[:10]))
    return {"ok": ok, "params": p, "uuid": str(log.get("uuid") or "")}


def main():
    with account_lock(timeout=5, purpose="probe", key=uid):
        cl.connect()
        cl.bin_handshake()
        cl.login()
        mk = H.read_march(cl)
        std = [a for a in H.usable_army(mk["army"])
               if len(a["id"]) == 6 and a["id"].startswith("10")]
        for a in std[:6]:
            print("  兵种 %s free=%s power=%s speed=%s load=%s"
                  % (a["id"], a["free"], a.get("power"), a.get("speed"), a.get("load")))
        a1, a2 = std[0], std[1]
        n1, n2 = min(2, int(a1["free"])), min(2, int(a2["free"]))
        soldiers = {str(a1["id"]): TypedInt(n1, SFS_INT),
                    str(a2["id"]): TypedInt(n2, SFS_INT)}
        fwd = [(a1["id"], a1.get("speed"), a1.get("load"), n1),
               (a2["id"], a2.get("speed"), a2.get("load"), n2)]
        rev = list(reversed(fwd))

        # --- 1) 反序 key ---
        f = H.find_monster(cl, 1)
        idx = H.point_index(f["x"], f["y"])
        print("\n[1] 混编 + **反序** marchKey (id 倒序拼):")
        r_rev = march("反序", soldiers, key_of(idx, rev), idx)
        if r_rev and r_rev["ok"]:
            print("  => 反序也成功: 服务端**不校验顺序**(或两种顺序都认)")
        else:
            print("  => 反序失败: 顺序敏感(id 升序/战力降序才是对的)")

        # --- 2) 正序, 顺便看完整明细 ---
        f2 = H.find_monster(cl, 1)
        idx2 = H.point_index(f2["x"], f2["y"])
        print("\n[2] 混编 + 正序 marchKey:")
        r_fwd = march("正序", soldiers, key_of(idx2, fwd), idx2)
        time.sleep(2)
        mk2 = H.read_march(cl)
        print("  在外队伍数:", len(mk2["marches"]))
        for u, e in mk2["marches"].items():
            print("  uuid=%s" % u[:10])
            print("    army 明细 =", json.dumps(e.get("army"), ensure_ascii=False))
            print("    _march_troops =", H._march_troops(e))
        print("  army[].march:",
              [(a["id"], a["march"], a["free"]) for a in mk2["all"] if a["id"] in (a1["id"], a2["id"])])

        # --- 3) 等队伍回来, 看 march/free 是否归位 ---
        print("\n[3] 等队伍回来(最多 120 秒)...")
        for i in range(24):
            time.sleep(5)
            mk3 = H.read_march(cl)
            if not mk3["marches"]:
                print("  全部回来了 (%d 秒)" % ((i + 1) * 5))
                break
            print("  还在外: %d 支" % len(mk3["marches"]))
        print("  army[].march/free:",
              [(a["id"], a["march"], a["free"]) for a in mk3["all"] if a["id"] in (a1["id"], a2["id"])])
        print("  体力:", H.read_stamina(cl))


if __name__ == "__main__":
    try:
        main()
    finally:
        try:
            cl.close()
        except Exception:  # noqa: BLE001
            pass
