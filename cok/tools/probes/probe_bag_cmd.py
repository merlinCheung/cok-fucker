#!/usr/bin/env python3
"""直连游戏服, 逐条试候选命令, 看哪条能返回**带 uuid 的全背包**。

背景:
  客户端的 ToolController 存着全部道具实例(itemId/count/uuid/...),
  但一直不知道是哪条命令把它灌满的。静态分析在 libgame.so 里翻到
  几个高度可疑的名字: msg_refreash_tool_data / msg_havetool /
  msg_tool_init_end / itemcollection.data ...

判定标准(不看字段名, 看数据形状):
    响应里出现 **大量 dict, 且每条带 uuid + itemId**  ->  就是它

用法:
    python3 probe_bag_cmd.py
    python3 probe_bag_cmd.py --cmds a.b c.d
"""

import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import cok_client  # noqa: E402

DEFAULT_CMDS = [
    "msg_refreash_tool_data",
    "msg_havetool",
    "msg_tool_init_end",
    "msg.tool.change",
    "itemcollection.data",
    "show.status.item",
    "outland.item.list",
    "hot.item.refresh",
    "status.item.refresh",
    "push.item.having",
    "push.useritem",
    "queue.tool",
    "world.user.march",
    "cemetery.get.info",
]


def count_uuid_dicts(node, depth=0):
    """统计"带 uuid 字段的 dict"的数量 —— 背包的形状特征。"""
    if depth > 12:
        return 0
    n = 0
    if isinstance(node, dict):
        if "uuid" in node and ("itemId" in node or "count" in node):
            n += 1
        for v in node.values():
            n += count_uuid_dicts(v, depth + 1)
    elif isinstance(node, (list, tuple)):
        for v in node:
            n += count_uuid_dicts(v, depth + 1)
    return n


def big_arrays(node, path="", out=None, depth=0):
    """列出所有长度 >= 20 的数组及其路径。"""
    if out is None:
        out = []
    if depth > 12:
        return out
    if isinstance(node, dict):
        for k, v in node.items():
            big_arrays(v, "%s.%s" % (path, k) if path else str(k), out, depth + 1)
    elif isinstance(node, (list, tuple)):
        if len(node) >= 20:
            out.append((path, len(node)))
        for i, v in enumerate(list(node)[:50]):
            big_arrays(v, "%s[%d]" % (path, i), out, depth + 1)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cmds", nargs="*", default=DEFAULT_CMDS)
    ap.add_argument("--out", default="bag-probe.json")
    args = ap.parse_args()

    account = dict(cok_client.ACCOUNT)
    account.setdefault("host", cok_client.DEFAULT_HOST)
    account.setdefault("port", cok_client.DEFAULT_PORT)

    c = cok_client.CokClient(account["host"], account["port"], 30.0, account)
    c.connect()
    c.bin_handshake()
    c.login()
    print("[*] 登录成功\n")

    results = {}
    for cmd in args.cmds:
        try:
            r = c.call(cmd, {}, retries=1)
        except Exception as e:
            print("  %-28s ERR  %s" % (cmd, str(e)[:90]))
            results[cmd] = {"error": str(e)[:200]}
            continue
        p = r.get("__params__") or r
        n_uuid = count_uuid_dicts(p)
        arrs = big_arrays(p)
        keys = sorted(p.keys()) if isinstance(p, dict) else []
        print("  %-28s uuid条目=%-5d 键=%s" % (cmd, n_uuid, ",".join(keys[:8])))
        for path, ln in arrs[:6]:
            print("        数组 %-40s len=%d" % (path, ln))
        results[cmd] = {"uuid_dicts": n_uuid, "keys": keys,
                         "big_arrays": arrs[:20],
                         "sample": json.dumps(p, ensure_ascii=False, default=str)[:800]}
        if n_uuid >= 20:
            print("  \033[1m★ %s 就是它! uuid 条目 %d\033[0m" % (cmd, n_uuid))

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=1, default=str)
    print("\n[*] 已存 %s" % args.out)
    try:
        c.close()
    except Exception:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
