#!/usr/bin/env python3
"""一次性会话连续试 queue.ccd / build.ccd 的参数组合。

用法:
  python3 test_queue_ccd.py [--uuid <队列uuid>]
"""
import argparse
import json
import os
import sys

PROTO = "/Users/a1234/workspace/me/cok/COK-CN1-analysis/protocol"
sys.path.insert(0, PROTO)
from cok_client import CokClient  # noqa: E402
import cok_account  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--uuid", default="3276c0a362b54e0394027dd7518fc38d")
    ap.add_argument("--timeout", type=float, default=60.0)
    args = ap.parse_args()

    acct = cok_account.load_account()
    c = CokClient(account=acct, timeout=args.timeout)
    c.connect()
    c.login()
    c.call("cmd.ping", {}, retries=0)

    u = args.uuid
    trials = [
        ("queue.ccd qUUID+itemUUID+isGold(INT)+itemCount", "queue.ccd",
         {"qUUID": u, "itemUUID": "", "isGold": 1, "itemCount": 1}),
        ("queue.ccd isGold=0", "queue.ccd",
         {"qUUID": u, "itemUUID": "", "isGold": 0, "itemCount": 1}),
        ("queue.ccd 仅 qUUID", "queue.ccd", {"qUUID": u}),
        ("queue.ccd uuid 字段名", "queue.ccd",
         {"uuid": u, "itemUUID": "", "isGold": 1, "itemCount": 1}),
        ("build.ccd 同参", "build.ccd",
         {"qUUID": u, "itemUUID": "", "isGold": 1, "itemCount": 1}),
        ("queue.one.key 同参", "queue.one.key",
         {"qUUID": u, "itemUUID": "", "isGold": 1, "itemCount": 1}),
    ]

    for label, cmd, params in trials:
        print("\n===== %s =====" % label)
        try:
            res = c.call(cmd, params, retries=1)
            print("  OK ->", json.dumps(res, ensure_ascii=False)[:900])
        except Exception as e:
            print("  ERR ->", type(e).__name__, str(e)[:400])


if __name__ == "__main__":
    main()
