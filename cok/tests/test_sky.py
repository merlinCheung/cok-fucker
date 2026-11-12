#!/usr/bin/env python3
"""Regression checks for Sky exploration count validation (no device/server)."""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "core"))
sys.path.insert(0, os.path.join(HERE, "..", "tools"))

import cok_sky
from cok_sfs import TypedInt, SFS_INT


class FakeClient(object):
    def __init__(self, info=None):
        self.calls = []
        self.info = info or {
            "state": "0", "exploreLv": "92", "landId": "56014601",
            "chooseGeneral": [{"id": "1"}], "chooseRewards": [{"id": "2"}],
            "curPower": "459551700", "needPower": "350000000",
        }

    def call(self, command, params):
        self.calls.append((command, params))
        if command == "newHeaven.info":
            return {"__params__": self.info}
        if command == "newHeaven.explore":
            return {"__params__": {"state": "1"}}
        return {"__params__": {"errorCode": "unsupported"}}


def check(name, condition):
    print("[%s] %s" % ("PASS" if condition else "FAIL", name))
    return bool(condition)


def main():
    ok = True
    client = FakeClient()
    status = cok_sky.read_sky(client)
    ok &= check("read_sky exposes allowed 1..10 counts",
                status.get("allowedExploreCounts") == list(range(1, 11)))
    ok &= check("read_sky keeps configured exploration prerequisites",
                status.get("can_explore") is True)

    before = len(client.calls)
    rejected = cok_sky.explore(client, num=30)
    ok &= check("unsupported count is rejected before a game write",
                not rejected.get("ok") and len(client.calls) == before
                and "1、2、3" in rejected.get("error", ""))

    accepted = cok_sky.explore(client, num=10)
    sent = client.calls[-1] if client.calls else (None, {})
    value = sent[1].get("num")
    ok &= check("legal count is sent as SFS integer",
                accepted.get("ok") and sent[0] == "newHeaven.explore"
                and isinstance(value, TypedInt) and value.sfs_type == SFS_INT
                and int(value) == 10)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
