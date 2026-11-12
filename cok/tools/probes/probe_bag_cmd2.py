#!/usr/bin/env python3
"""逐条试候选命令, **每条都重新登录**(一条失败不会连累后面的)。

判定"这就是全背包"的标准(不看字段名, 看数据形状):
    响应里出现 >= 20 个带 uuid 字段的 dict  ->  命中

用法:
    python3 probe_bag_cmd2.py
    python3 probe_bag_cmd2.py --cmds hot.item.get hot.item.refresh
"""

import argparse
import json
import os
import socket
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import cok_client  # noqa: E402

DEFAULT_CMDS = [
    "hot.item.get",
    "hot.item.refresh",
    "hot.item.refreshV3",
    "hot.item.v2.get",
    "hot.item.v3.get",
    "get.user.info",
    "itemcollection.data",
    "pve_item.read",
    "pve_item.data",
    "outland.item.list",
    "nfight.bagShow",
    "formationTrain.bag",
    "mall.getNewGoods",
    "mall.data",
    "mall.data2",
    "user.info",
    "user.data",
    "tool.data",
    "tools.data",
    "item.list",
    "item.data",
]


def count_uuid_dicts(node, depth=0):
    if depth > 14:
        return 0
    n = 0
    if isinstance(node, dict):
        if "uuid" in node:
            n += 1
        for v in node.values():
            n += count_uuid_dicts(v, depth + 1)
    elif isinstance(node, (list, tuple)):
        for v in node:
            n += count_uuid_dicts(v, depth + 1)
    return n


def big_arrays(node, path="", out=None, depth=0):
    if out is None:
        out = []
    if depth > 14:
        return out
    if isinstance(node, dict):
        for k, v in node.items():
            big_arrays(v, "%s.%s" % (path, k) if path else str(k), out, depth + 1)
    elif isinstance(node, (list, tuple)):
        if len(node) >= 15:
            out.append((path, len(node)))
        for i, v in enumerate(list(node)[:40]):
            big_arrays(v, "%s[%d]" % (path, i), out, depth + 1)
    return out


def login():
    account = dict(cok_client.ACCOUNT)
    account.setdefault("host", cok_client.DEFAULT_HOST)
    account.setdefault("port", cok_client.DEFAULT_PORT)
    c = cok_client.CokClient(account["host"], account["port"], 12.0, account)
    c.connect()
    c.bin_handshake()
    c.login()
    return c


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cmds", nargs="*", default=DEFAULT_CMDS)
    ap.add_argument("--out", default="bag-probe2.json")
    ap.add_argument("--timeout", type=float, default=12.0)
    args = ap.parse_args()


    # 跨进程账号锁: 游戏服同账号只允许一个连接。
    # 网页控制台/自动打怪正在用这个账号时, 直接退出, 不要去互踢。
    try:
        _lock = cok_client.account_lock(timeout=0.0, purpose="bag-sweep")
        _lock.__enter__()
    except cok_client.AccountBusy as e:
        print("[!] %s" % e)
        print("    (网页控制台或自动打怪正在用这个账号, 稍后再试)")
        return 2

    results = {}
    for cmd in args.cmds:
        c = None
        try:
            c = login()
            c.timeout = args.timeout
            # retries=1: 服务端会丢弃新连接的首条业务请求, 必须重发一次
            r = c.call(cmd, {}, retries=1)
            p = r.get("__params__") or r
            n = count_uuid_dicts(p)
            arrs = big_arrays(p)
            keys = sorted(p.keys()) if isinstance(p, dict) else []
            flag = "  ★命中" if n >= 20 else ""
            print("  %-26s uuid=%-4d 键=%s%s" % (cmd, n, ",".join(keys[:8]), flag))
            for path, ln in arrs[:5]:
                print("        数组 %-38s len=%d" % (path, ln))
            results[cmd] = {"uuid_dicts": n, "keys": keys,
                            "big_arrays": arrs[:20],
                            "sample": json.dumps(p, ensure_ascii=False, default=str)[:1200]}
            if n >= 20:
                with open(args.out, "w", encoding="utf-8") as f:
                    json.dump(results, f, ensure_ascii=False, indent=1, default=str)
                print("\n★ %s 就是它 —— 已存 %s" % (cmd, args.out))
                return 0
        except socket.timeout:
            print("  %-26s 超时" % cmd)
            results[cmd] = {"error": "timeout"}
        except Exception as e:
            msg = str(e)[:90]
            print("  %-26s ERR  %s" % (cmd, msg))
            results[cmd] = {"error": msg}
        finally:
            if c:
                try:
                    c.close()
                except Exception:
                    pass
        time.sleep(0.3)

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=1, default=str)
    print("\n[*] 已存 %s" % args.out)
    try:
        _lock.__exit__(None, None, None)
    except Exception:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
