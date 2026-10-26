#!/usr/bin/env python3
"""全量扫描客户端命令, 找出返回**带 uuid 的道具实例**的那条。

为什么以前扫不出来:
  服务端会**丢弃新连接的首条业务请求**(不返回任何东西), 必须重发一次才正常响应。
  如果扫描时用 retries=0, 每条命令都必然超时 → 结论"没有这种命令"是**无效的**。
  本脚本用 retries=1, 并且同时检查:
    1) 命令响应本身
    2) 等待期间收到的**推送**(c.take_pushes())
  判定: 出现 >= 10 个带 uuid 字段的 dict。

用法:
    python3 sweep_bag.py --catalog command-catalog-typed.json
    python3 sweep_bag.py --all            # 扫全部命令(慢)
    python3 sweep_bag.py --cmds a.b c.d
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

KEYWORDS = ("item", "tool", "prop", "goods", "bag", "user", "world",
            "mall", "shop", "store", "equip", "res", "war", "material")


def count_uuid_dicts(node, depth=0):
    if depth > 16:
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


def biggest_arrays(node, path="", out=None, depth=0):
    if out is None:
        out = []
    if depth > 16:
        return out
    if isinstance(node, dict):
        for k, v in node.items():
            biggest_arrays(v, "%s.%s" % (path, k) if path else str(k), out, depth + 1)
    elif isinstance(node, (list, tuple)):
        if len(node) >= 10:
            out.append((path, len(node)))
        for i, v in enumerate(list(node)[:60]):
            biggest_arrays(v, "%s[%d]" % (path, i), out, depth + 1)
    return out


def new_conn(timeout):
    account = dict(cok_client.ACCOUNT)
    account.setdefault("host", cok_client.DEFAULT_HOST)
    account.setdefault("port", cok_client.DEFAULT_PORT)
    c = cok_client.CokClient(account["host"], account["port"], timeout, account)
    c.connect()
    c.bin_handshake()
    c.login()
    return c


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--catalog", default=os.path.join(HERE, "command-catalog-typed.json"))
    ap.add_argument("--cmds", nargs="*")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--timeout", type=float, default=6.0)
    ap.add_argument("--out", default="bag-sweep.json")
    args = ap.parse_args()

    if args.cmds:
        cmds = list(args.cmds)
    else:
        with open(args.catalog, encoding="utf-8") as f:
            cat = json.load(f)
        allc = [k for k in cat if not k.startswith("_") and not k.startswith("requestServer")]
        if args.all:
            cmds = sorted(allc)
        else:
            cmds = sorted(k for k in allc
                          if any(w in k.lower() for w in KEYWORDS))

    # 跨进程账号锁: 游戏服同账号只允许一个连接。
    # 网页控制台/自动打怪正在用这个账号时, 直接退出, 不要去互踢。
    try:
        _lock = cok_client.account_lock(timeout=0.0, purpose="bag-sweep")
        _lock.__enter__()
    except cok_client.AccountBusy as e:
        print("[!] %s" % e)
        print("    (网页控制台或自动打怪正在用这个账号, 稍后再试)")
        return 2

    print("[*] 待扫 %d 条命令" % len(cmds))

    c = None
    results = {}
    best = (0, None)
    for i, cmd in enumerate(cmds):
        for attempt in range(2):
            try:
                if c is None:
                    c = new_conn(args.timeout)
                r = c.call(cmd, {}, retries=1)
                p = r.get("__params__") or r
                n = count_uuid_dicts(p)
                arrs = biggest_arrays(p)
                # 顺便看等待期间收到的推送
                pn = 0
                for pu in c.take_pushes():
                    pn += count_uuid_dicts(pu)
                if n >= 10 or pn >= 10:
                    print("  ★★ %-34s 响应uuid=%-4d 推送uuid=%-4d %s"
                          % (cmd, n, pn, arrs[:3]))
                elif n or pn:
                    print("     %-34s 响应uuid=%-3d 推送uuid=%-3d" % (cmd, n, pn))
                results[cmd] = {"uuid": n, "push_uuid": pn,
                                "keys": sorted(p.keys())[:12] if isinstance(p, dict) else [],
                                "arrays": arrs[:12]}
                if max(n, pn) > best[0]:
                    best = (max(n, pn), cmd)
                break
            except socket.timeout:
                results[cmd] = {"error": "timeout"}
                break
            except Exception as e:
                results[cmd] = {"error": str(e)[:120]}
                try:
                    if c:
                        c.close()
                except Exception:
                    pass
                c = None
                if attempt == 0:
                    time.sleep(0.2)
                    continue
                break
        if (i + 1) % 20 == 0:
            print("   ... %d/%d" % (i + 1, len(cmds)))
        with open(args.out, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=1, default=str)

    if c:
        try:
            c.close()
        except Exception:
            pass
    print("\n[*] 最好的一条: %s (uuid 条目 %s)" % (best[1], best[0]))
    print("[*] 已存 %s" % args.out)
    try:
        _lock.__exit__(None, None, None)
    except Exception:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
