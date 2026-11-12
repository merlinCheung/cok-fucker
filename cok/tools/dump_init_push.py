#!/usr/bin/env python3
"""直连游戏服, 抓登录后服务端下发的 init push, 找全背包(items)。

背景:
  App 登录后 1 秒内, 服务端会把**全背包**(499 条 itemId/count/uuid/...)随初始化
  数据一次性下发。之前没能定位到"拉背包"的命令名, 原因很可能是:
  **背包根本不是某条命令的响应, 而是 init push 里的一部分**。

这个脚本用 cok_client.ACCOUNT 里复原的凭据直连(**不依赖设备**),
登录后把 init push 里的每一层嵌套 SFS 对象都解出来,
逐层看有没有 items / itemList / tools 之类的背包数组。

帧格式(与 cok_daemon.grab_init 一致):
    fl(1) | ln(2, big-endian) | payload(ln)
    parse_packet(payload) -> (_, _, obj, _)

用法:
    python3 dump_init_push.py --out init-push.jsonl
    python3 dump_init_push.py --out init-push.jsonl --find-items
"""

import argparse
import json
import os
import socket
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "core"))

import cok_client  # noqa: E402
from cok_sfs import decode_params, parse_packet  # noqa: E402

BAG_KEYS = ("items", "itemList", "tools", "bagItems", "goods", "item",
            "toolList", "toolsList", "propList")


def walk(node, path="", hits=None, depth=0):
    """在解码后的结构里找所有背包数组。"""
    if hits is None:
        hits = []
    if depth > 14:
        return hits
    if isinstance(node, dict):
        for k, v in node.items():
            p = "%s.%s" % (path, k) if path else str(k)
            if str(k) in BAG_KEYS and isinstance(v, (list, dict)):
                hits.append((p, v))
            walk(v, p, hits, depth + 1)
    elif isinstance(node, (list, tuple)):
        for i, v in enumerate(list(node)[:500]):
            walk(v, "%s[%d]" % (path, i), hits, depth + 1)
    return hits


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="init-push.jsonl")
    ap.add_argument("--host", default=cok_client.DEFAULT_HOST)
    ap.add_argument("--port", type=int, default=cok_client.DEFAULT_PORT)
    ap.add_argument("--wait", type=float, default=15.0,
                    help="登录后等多久收 push(秒)")
    ap.add_argument("--find-items", action="store_true",
                    help="在收到的 push 里搜背包数组")
    ap.add_argument("--dump-nested", action="store_true",
                    help="把 hex 字段里的嵌套 SFS 对象也解出来存盘")
    ap.add_argument("--account", help="账号 JSON 文件(默认用内置 ACCOUNT)")
    args = ap.parse_args()

    account = dict(cok_client.ACCOUNT)
    if args.account:
        with open(args.account, encoding="utf-8") as f:
            account.update(json.load(f))
    account.setdefault("host", args.host)
    account.setdefault("port", args.port)

    print("[*] 连接 %s:%s" % (args.host, args.port))
    c = cok_client.CokClient(args.host, args.port, 30.0, account)
    c.connect()
    print("[*] bin 握手完成 key_id=%s" % c.key_id)
    c.login()
    print("[*] 登录成功, 开始收 push(%.0fs)..." % args.wait)

    end = time.time() + args.wait
    out = open(args.out, "w", encoding="utf-8")
    n = 0
    hits = []
    cmds = {}
    try:
        # ⚠️ 必须用客户端自己的 _recv_frame(): 它会先取 self.rbuf 里
        # **已经缓存好的字节**(登录响应和后面的推送常常在同一次 recv 里到齐)。
        # 直接从 socket 读会把这些帧整段漏掉 —— 之前查背包一直查不到就是这个原因。
        c.sock.settimeout(2.0)
        while time.time() < end:
            try:
                flags, obj, _ = c._recv_frame()
            except socket.timeout:
                continue
            except Exception as e:
                print("[!] 收帧出错: %s" % str(e)[:120])
                break
            n += 1
            cmd = ""
            try:
                cmd = c._resp_cmd(obj)
            except Exception:
                pass
            cmds[cmd] = cmds.get(cmd, 0) + 1
            try:
                pp = c._resp_params(obj)
            except Exception:
                pp = {}
            rec = {"cmd": cmd, "params": pp}
            # hex 字段里可能藏着嵌套的 SFS 对象(init push 就是这么发的)
            nested = {}
            for k, v in list(pp.items()):
                if isinstance(v, str) and len(v) > 60 and k != "qqq":
                    try:
                        o2, _, _ = decode_params(bytes.fromhex(v), c.key)
                        nested[k] = o2
                    except Exception:
                        pass
            if nested:
                rec["nested"] = nested
            try:
                out.write(json.dumps(rec, ensure_ascii=False, default=str) + "\n")
            except Exception:
                pass
            if args.find_items:
                for p, v in walk(rec):
                    hits.append((cmd, p, v))
    finally:
        out.close()
        try:
            c.close()
        except Exception:
            pass

    print("[*] 收到 %d 帧, 已存 %s" % (n, args.out))
    print("[*] 收到的命令: %s" % (", ".join("%s×%d" % (k or "?", v)
                                        for k, v in sorted(cmds.items()))))
    if hits:
        print("[!] 找到背包数组:")
        for cmd, p, v in hits:
            print("    cmd=%s  path=%s  长度=%s" % (cmd, p, len(v) if hasattr(v, "__len__") else "?"))
            try:
                sample = list(v.items())[:2] if isinstance(v, dict) else list(v)[:2]
                print("       样本: %s" % json.dumps(sample, ensure_ascii=False, default=str)[:400])
            except Exception:
                pass
    else:
        print("[*] 没找到背包数组")
    return 0


if __name__ == "__main__":
    sys.exit(main())
