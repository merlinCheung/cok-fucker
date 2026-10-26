#!/usr/bin/env python3
"""发一条命令后**只收帧不配对**, 看服务端用推送回的是什么。

背景:
  之前 probe 试 `msg_refreash_tool_data` 超时, 但连接没断, 而且期间
  收到了 `world.effect.push` —— 说明服务端**推送**是独立于命令响应的。
  如果道具全量是用推送下发的, 那就必须"发完命令不配对, 一直收帧",
  而不是等一个同名响应。

用法:
    python3 probe_bag_push.py --cmd msg_refreash_tool_data --wait 20
"""

import argparse
import json
import os
import random
import socket
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import cok_client  # noqa: E402


def count_uuid_dicts(node, depth=0):
    if depth > 14:
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cmd", default="msg_refreash_tool_data")
    ap.add_argument("--params", default="{}")
    ap.add_argument("--wait", type=float, default=20.0)
    ap.add_argument("--out", default="bag-push.json")
    args = ap.parse_args()

    account = dict(cok_client.ACCOUNT)
    account.setdefault("host", cok_client.DEFAULT_HOST)
    account.setdefault("port", cok_client.DEFAULT_PORT)

    c = cok_client.CokClient(account["host"], account["port"], 30.0, account)
    c.connect()
    c.bin_handshake()
    c.login()
    print("[*] 登录成功")

    params = json.loads(args.params)
    # 用和 cok_client._call_once **完全一致**的帧格式发送, 但不等同名响应,
    # 只管收帧 —— 服务端可能用推送下发道具全量
    try:
        c.seq += 1
        t = int(time.time())
        p = {
            "_cok_": "%06d%06d" % (c.cok_prefix, c.seq),
            "cmdBaseTime": t,
            "newbasekey": "%032x" % random.getrandbits(128),
        }
        if params:
            p.update(params)
        from cok_sfs import (TypedInt, SFS_INT, SFS_SHORT, SFS_BYTE,
                              encode_object, xor_buf)
        plain = encode_object(p)
        cipher = xor_buf(plain, c.key)
        env = {
            "p": {"p": {"params": cipher}, "r": TypedInt(-1, SFS_INT), "c": args.cmd},
            "a": TypedInt(13, SFS_SHORT),
            "c": TypedInt(1, SFS_BYTE),
        }
        c._send_frame(env)
        print("[*] 已发送 %s (只收帧, 不等同名响应)" % args.cmd)
    except Exception as e:
        print("[!] 发送失败: %s" % str(e)[:150])
        return 1

    end = time.time() + args.wait
    frames = []
    c.sock.settimeout(2.0)
    while time.time() < end:
        try:
            flags, obj, _ = c._recv_frame()
        except socket.timeout:
            continue
        except Exception as e:
            print("[!] 收帧结束: %s" % str(e)[:100])
            break
        try:
            cmd = c._resp_cmd(obj)
        except Exception:
            cmd = "?"
        try:
            p = c._resp_params(obj)
        except Exception:
            p = {}
        n = count_uuid_dicts(p)
        frames.append({"cmd": cmd, "params": p})
        keys = sorted(p.keys()) if isinstance(p, dict) else []
        print("  帧 cmd=%-28s uuid条目=%-5d 键=%s" % (cmd, n, ",".join(keys[:8])))
        if n >= 20:
            print("  \033[1m★ 这一帧里有 %d 条带 uuid 的道具!\033[0m" % n)
            with open(args.out, "w", encoding="utf-8") as f:
                json.dump(frames, f, ensure_ascii=False, indent=1, default=str)
            print("  已存 %s" % args.out)
            return 0

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(frames, f, ensure_ascii=False, indent=1, default=str)
    print("[*] 共 %d 帧, 已存 %s" % (len(frames), args.out))
    try:
        c.close()
    except Exception:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
