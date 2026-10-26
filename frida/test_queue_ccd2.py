#!/usr/bin/env python3
"""用真实 qid/queueType/goldcost 实测 queue.ccd(主城建造队列加速)。"""
import argparse
import itertools
import json
import sys

PROTO = "/Users/a1234/workspace/me/cok/COK-CN1-analysis/protocol"
sys.path.insert(0, PROTO)
from cok_client import CokClient  # noqa: E402
from cok_sfs import TypedInt, SFS_INT  # noqa: E402
import cok_account  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--uuid", default="f2bb9577d6e1409a9688b22ffbc2a6c0")
    ap.add_argument("--timeout", type=float, default=60.0)
    args = ap.parse_args()

    acct = cok_account.load_account()
    c = CokClient(account=acct, timeout=args.timeout)
    c.connect()
    c.login()
    c.call("cmd.ping", {}, retries=0)

    u = args.uuid
    trials = [
        ("qid=1 qt=1 gc=0 isGold=1 ic=1", "1", "1", "0", 1, 1),
        ("qid=1 qt=1 gc=1 isGold=1 ic=1", "1", "1", "1", 1, 1),
        ("qid=1 qt=0 gc=0 isGold=1 ic=1", "1", "0", "0", 1, 1),
        ("qid=1 qt=1 gc=0 isGold=0 ic=1", "1", "1", "0", 0, 1),
        ("qid=1 qt=1 gc=100 isGold=1 ic=1", "1", "1", "100", 1, 1),
        ("qid=1 qt=1 gc=0 isGold=1 ic=0", "1", "1", "0", 1, 0),
        ("qid=1 qt=2 gc=0 isGold=1 ic=1", "1", "2", "0", 1, 1),
        ("qid=0 qt=1 gc=0 isGold=1 ic=1", "0", "1", "0", 1, 1),
        ("qid=1 qt=1 gc=0 isGold=1 ic=1 (retry)", "1", "1", "0", 1, 1),
    ]

    for label, qid, qt, gc, isgold, ic in trials:
        params = {
            "qUUID": u,
            "itemUUID": "",
            "isGold": TypedInt(isgold, SFS_INT),
            "itemCount": TypedInt(ic, SFS_INT),
            "queueId": qid,
            "queueType": qt,
            "goldcost": gc,
        }
        print("\n===== %s =====" % label)
        print("  params:", json.dumps(params, ensure_ascii=False))
        try:
            res = c.call("queue.ccd", params, retries=1)
            print("  ->", json.dumps(res, ensure_ascii=False)[:700])
        except Exception as e:
            print("  ERR", type(e).__name__, str(e)[:200])


if __name__ == "__main__":
    main()
