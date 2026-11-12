#!/usr/bin/env python3
"""用直连客户端批量验证只读命令(带 App 真实参数),输出可用命令清单。

用法:
  python3 probe_readonly.py [--catalog command-catalog.json] [--host IP] [--port N]
默认只跑"只读"命令; 名字里含 reward/trigger/save/login/cok.proto 等的写操作会被跳过。
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

_C = os.path.join(HERE, "..", "..", "core")
sys.path.insert(0, _C)
from cok_client import CokClient  # noqa: E402

# 明确排除的写操作/副作用命令
SKIP_PATTERNS = ("reward", "trigger", "save.", "login.", "cok.proto", "enter",
                 "getreward", "buy", "exchange", "use", "open")
# 明确只读、优先验证
PRIORITY = ["cmd.ping", "overview_new.data", "monthlySign.info", "allianceNewBoss.bossMainInfo",
            "al.rank", "kingdom.officers", "chat.get.system.mails", "daily.quest.ls",
            "achieve.ls", "act.ls", "itemcollection.data", "gem.getDigView", "stat.tt",
            "science.data.cond", "festivalview.data", "generalBP.data", "formationTrain.bag",
            "worldboss", "accountLock.getUnlockView", "mall.info", "get.clash.server.list"]


def is_readonly(cmd):
    c = cmd.lower()
    return not any(p in c for p in SKIP_PATTERNS)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--catalog", default="command-catalog.json")
    ap.add_argument("--host", default="42.192.152.154")
    ap.add_argument("--port", type=int, default=32231)
    ap.add_argument("--timeout", type=float, default=15.0)
    ap.add_argument("--out", default="readonly-commands.json")
    ap.add_argument("--all", action="store_true", help="跑全部只读命令(较慢)")
    args = ap.parse_args()

    with open(args.catalog, encoding="utf-8") as fh:
        cat = json.load(fh)

    cmds = [c for c in cat if is_readonly(c)]
    if not args.all:
        ordered = [c for c in PRIORITY if c in cat]
        ordered += [c for c in cmds if c not in ordered]
        cmds = ordered
    print("[*] 待验证只读命令 %d 条" % len(cmds))

    c = CokClient(args.host, args.port, args.timeout)
    c.connect()
    c.bin_handshake()
    c.login()
    try:
        c.call("cmd.ping")
    except Exception:
        pass

    results = {}
    for cmd in cmds:
        params = {k: v for k, v in cat.get(cmd, {}).items()}
        try:
            res = c.call(cmd, params)
            p = res.get("__params__") or {}
            err = p.get("errorCode") if isinstance(p, dict) else None
            keys = [k for k in p if k not in ("_cok_",)] if isinstance(p, dict) else []
            status = "ERR" if err else "OK"
            results[cmd] = {"status": status, "errorCode": err, "fields": keys[:24],
                            "params_sent": params}
            print("  %-3s %-32s %s%s" % (status, cmd, ",".join(keys[:4]),
                                         ("  errorCode=%s" % err) if err else ""))
        except Exception as e:  # noqa: BLE001
            results[cmd] = {"status": "TIMEOUT", "error": str(e)[:80],
                            "params_sent": params}
            print("  TO  %-32s %s" % (cmd, str(e)[:60]))
    c.close()

    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(results, fh, ensure_ascii=False, indent=1)
    ok = sum(1 for v in results.values() if v["status"] == "OK")
    err = sum(1 for v in results.values() if v["status"] == "ERR")
    to = sum(1 for v in results.values() if v["status"] == "TIMEOUT")
    print("\n汇总: 成功 %d / 业务错误 %d / 超时 %d  (共 %d)" % (ok, err, to, len(results)))
    print("结果已写 %s" % args.out)


if __name__ == "__main__":
    main()
