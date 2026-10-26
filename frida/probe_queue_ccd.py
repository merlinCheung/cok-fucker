#!/usr/bin/env python3
"""queue.ccd / queue.one.key 参数组合穷举(单次连接连续发)。

服务端对未知命令静默忽略、对已知命令参数错返回 E000000,
所以只要能拿到响应就说明"命令存在+参数结构可解析"。
"""
import argparse
import itertools
import json
import os
import sys

PROTO = "/Users/a1234/workspace/me/cok/COK-CN1-analysis/protocol"
sys.path.insert(0, PROTO)
from cok_client import CokClient  # noqa: E402
from cok_sfs import TypedInt, SFS_INT, SFS_BYTE, SFS_LONG  # noqa: E402
import cok_account  # noqa: E402


def build_variants(uuid):
    """产出 (标签, cmd, params) 组合。"""
    out = []
    uuid_keys = ["qUUID", "uuid", "qUuid"]
    item_keys = ["itemUUID", "itemUuid", "itemId"]
    gold_opts = [("isGold=BOOL(T)", True), ("isGold=INT(1)", TypedInt(1, SFS_INT)),
                 ("isGold=BYTE(1)", TypedInt(1, SFS_BYTE))]
    tail_opts = [
        ("itemCount=1", {"itemCount": TypedInt(1, SFS_INT)}),
        ("queueType=1", {"queueType": TypedInt(1, SFS_INT)}),
        ("goldcost=1", {"goldcost": TypedInt(1, SFS_INT)}),
        ("no-tail", {}),
        ("itemCount=0", {"itemCount": TypedInt(0, SFS_INT)}),
    ]
    for uk, ik, (gl, gv), (tl, tv) in itertools.product(uuid_keys, item_keys, gold_opts, tail_opts):
        p = {uk: uuid, ik: "", "isGold": gv}
        p.update(tv)
        out.append(("%s|%s|%s|%s" % (uk, ik, gl, tl), "queue.ccd", p))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--uuid", default="3276c0a362b54e0394027dd7518fc38d")
    ap.add_argument("--timeout", type=float, default=45.0)
    ap.add_argument("--limit", type=int, default=200)
    args = ap.parse_args()

    acct = cok_account.load_account()
    c = CokClient(account=acct, timeout=args.timeout)
    c.connect()
    c.login()
    c.call("cmd.ping", {}, retries=0)

    variants = build_variants(args.uuid)
    print("组合数: %d" % len(variants))
    hits = []
    for i, (label, cmd, params) in enumerate(variants[: args.limit]):
        try:
            res = c.call(cmd, params, retries=0)
            code = res.get("errorCode")
            print("[%3d] %-58s -> %s" % (i, label, code or json.dumps(res, ensure_ascii=False)[:200]))
            if not code:
                hits.append((label, params, res))
                print("      >>> 命中! params=%s" % json.dumps(params, ensure_ascii=False))
        except Exception as e:
            msg = str(e)
            print("[%3d] %-58s -> ERR %s" % (i, label, msg[:120]))
            # 连接被服务端关闭 => 需要重连
            try:
                c.connect()
                c.login()
                c.call("cmd.ping", {}, retries=0)
            except Exception as e2:
                print("      重连失败:", str(e2)[:120])
                break

    print("\n=== 命中 %d 组 ===" % len(hits))
    for label, params, res in hits:
        print(label, json.dumps(params, ensure_ascii=False))
        print("   ", json.dumps(res, ensure_ascii=False)[:600])


if __name__ == "__main__":
    main()
