#!/usr/bin/env python3
"""快速验证若干命令(带类型目录 + parse_best 解码)。"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cok_client import CokClient  # noqa: E402

CMDS = sys.argv[1:] or [
    "skin.introduction", "kingdom.officers", "itemcollection.data", "gem.getDigView",
    "formationTrain.bag", "check.result", "worldboss", "daily.quest.ls",
    "hero.introduction", "dragon.battle.info", "chat.get.system.mails",
]


def main():
    c = CokClient(timeout=15)
    c.connect()
    c.bin_handshake()
    c.login()
    try:
        c.call("cmd.ping")
    except Exception:
        pass
    for t in CMDS:
        try:
            r = c.call(t)
            p = r.get("__params__") or {}
            err = p.get("errorCode") if isinstance(p, dict) else None
            keys = ",".join([k for k in p if k != "_cok_"][:4]) if isinstance(p, dict) else ""
            print("  %-3s %-24s mode=%-10s %s%s" % (
                "ERR" if err else "OK", t, r.get("__mode__"), keys,
                (" errorCode=%s" % err) if err else ""))
        except Exception as e:  # noqa: BLE001
            print("  TO  %-24s %s" % (t, str(e)[:70]))
    c.close()


if __name__ == "__main__":
    main()
