#!/usr/bin/env python3
"""给巨型狮鹫注册表打底: 把已探到的 boss 写进 boss-registry.json, 再补一轮全图抽样。

用法: python3 seed_boss_registry.py [account] [抽样中心数]
"""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)


def main():
    from cok_accounts import get_account
    from cok_client import CokClient
    import cok_rally as R

    acc_id = sys.argv[1] if len(sys.argv) > 1 else "<uid-main>"
    want = int(sys.argv[2]) if len(sys.argv) > 2 else 120

    # 1) 先把之前探测到的密集区结果灌进注册表
    zp = os.path.join(HERE, "boss-zone.json")
    if os.path.exists(zp):
        data = json.load(open(zp))
        now = time.time()
        for k, v in (data.get("tiles") or {}).items():
            idx = int(k)
            R._KNOWN[idx] = {
                "index": idx,
                "monsterId": v.get("monsterId"),
                "level": R.BOSS_IDS.get(str(v.get("monsterId"))),
                "hp": v.get("hp"),
                "maxHp": v.get("maxHp"),
                "x": v.get("x"),
                "y": v.get("y"),
                "start": v.get("st"),
                "refresh": v.get("rt"),
                "seen_at": now,
            }
        print("从 boss-zone.json 灌入 %d 只, 累计 %d 只" % (len(data.get("tiles") or {}), len(R._KNOWN)))

    # 2) 补一轮全图抽样(把目标铺到地图各处)
    acc = get_account(acc_id)
    cl = CokClient(account=acc, timeout=25.0).connect()
    cl.bin_handshake()
    cl.login()
    for _ in range(2):
        try:
            cl.call("cmd.ping")
        except Exception:
            pass

    def _reconnect(old):
        nonlocal cl
        try:
            old.close()
        except Exception:
            pass
        cl = CokClient(account=acc, timeout=25.0).connect()
        cl.bin_handshake()
        cl.login()
        return cl

    centers = R.map_centers()
    print("全图采样点 %d 个, 本次扫 %d 个" % (len(centers), want))
    t0 = time.time()
    sc = R.scan_bosses(cl, full=False, slice_size=want, on_reconnect=_reconnect)
    print("本次扫 %d 格, 累计已知 %d 只 (%.0fs)"
          % (sc["scanned"], sc["known"], time.time() - t0))
    R.save_registry()
    cl.close()
    print("注册表:", R.REGISTRY_FILE)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
