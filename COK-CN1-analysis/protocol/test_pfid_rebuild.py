#!/usr/bin/env python3
"""回归测试：游戏服凭据能否**只靠 pfId** 重建（不依赖任何设备）。

对账号库里每个号：
  pfId --getserverlist.php--> {gameUid, uuid, zn, buildCode} --> SFS 登录
另外用**全新随机 deviceId** 登录，验证 deviceId 不绑账号。

跑法：
    python3 protocol/test_pfid_rebuild.py
    python3 protocol/test_pfid_rebuild.py --skip-login     # 只测解析
"""
import json
import os
import sys
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import cok_gamesvc                      # noqa: E402
from cok_client import CokClient, account_lock, load_account   # noqa: E402

ACCOUNTS = os.path.join(HERE, "accounts")


def accounts():
    out = []
    for fn in sorted(os.listdir(ACCOUNTS)):
        if fn.endswith(".json") and fn not in ("sessions.json", "users.json"):
            try:
                with open(os.path.join(ACCOUNTS, fn), encoding="utf-8") as fh:
                    out.append((fn[:-5], json.load(fh)))
            except (OSError, ValueError):
                continue
    return out


def main():
    skip_login = "--skip-login" in sys.argv
    n_ok = n_fail = 0
    for key, acc in accounts():
        pf_id = acc.get("pfId") or acc.get("platformUid")
        pf = acc.get("pf", "cn_ewanqf")
        pkg = acc.get("packageName", "")
        ch = acc.get("channel") or (pf[3:] if pf.startswith("cn_") else pf)
        label = "%s (%s)" % (key, acc.get("gameUid"))
        print("=" * 68)
        print("### %s  pfId=%s" % (label, pf_id))
        try:
            r = cok_gamesvc.resolve_character(pf_id, pf=pf, channel=ch, package=pkg)
        except Exception as exc:                        # noqa: BLE001
            print("   ❌ gameservice 失败: %s" % exc)
            n_fail += 1
            continue
        if not r.get("ok"):
            print("   ❌ 没解析出角色: %s" % r.get("note"))
            n_fail += 1
            continue
        same = (r["gameUid"] == str(acc.get("gameUid")))
        print("   ✅ 解析: gameUid=%s uuid=%s zone=%s buildCode=%s"
              % (r["gameUid"], r["uuid"], r.get("zn"), r.get("buildCode")))
        print("      与账号库 gameUid 一致: %s" % ("是" if same else "否!"))
        if not same:
            n_fail += 1
            continue
        if skip_login:
            n_ok += 1
            continue
        a = dict(acc)
        a["gameUid"] = r["gameUid"]
        a["uuid"] = r["uuid"]
        a["deviceId"] = os.urandom(8).hex()          # 全新 deviceId
        if r.get("buildCode"):
            a["buildCode"] = r["buildCode"]
        try:
            with account_lock(timeout=12, purpose="pfid-rebuild-test",
                              key=str(a.get("gameUid"))):
                c = CokClient(timeout=25, account=a)
                c.connect()
                c.bin_handshake()
                c.login()
            print("   ✅ SFS 登录成功(全新 deviceId=%s)" % a["deviceId"])
            n_ok += 1
        except Exception as exc:                        # noqa: BLE001
            msg = str(exc)
            if "占用" in msg:
                print("   ⏭ 跳过(账号正被控制台占用): %s" % msg)
                n_ok += 1
            else:
                print("   ❌ SFS 登录失败: %s" % msg)
                n_fail += 1
                traceback.print_exc()
    print("=" * 68)
    print("结果: %d 成功 / %d 失败" % (n_ok, n_fail))
    return 0 if n_fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
