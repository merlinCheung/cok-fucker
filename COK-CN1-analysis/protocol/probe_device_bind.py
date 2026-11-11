#!/usr/bin/env python3
"""探针: 直连游戏服问「这台设备绑定了哪些账号」。

背景(2026-10-28):
  客户端 lua `game/command/DeviceAccountInfoCmd.lua` 用命令 **`device.bind.info`**
  向服务端要「设备账号列表」; 响应里 `param.accounts[]` 每项含
  gameUid / buildcode / ip / port / zone / uuid。
  另有:
    device.bind.export  {opUid}  -> 导出某账号, 返回 {code, expireTime}(授权码)
    device.bind.import  {code}    -> 用授权码把账号导入本设备
    device.bind.hide    {opUid}  -> 隐藏某账号

用法:
    python3 probe_device_bind.py                     # 默认用当前选中账号
    python3 probe_device_bind.py --key <uid-guopan> # 指定账号
    python3 probe_device_bind.py --cmd device.bind.export --params '{"opUid":"..."}'

⚠️ 同账号只允许一个连接 —— 走 account_lock, 拿不到锁就跳过, 不跟网页控制台互踢。
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cok_client import CokClient, AccountBusy, account_lock, load_account  # noqa: E402
import cok_accounts  # noqa: E402


def _dump(title, obj):
    print("\n=== %s ===" % title)
    print(json.dumps(obj, ensure_ascii=False, indent=2, default=str))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--key", help="账号 id(gameUid); 默认用当前选中账号")
    ap.add_argument("--cmd", default="device.bind.info")
    ap.add_argument("--params", default="{}")
    ap.add_argument("--timeout", type=float, default=30.0)
    args = ap.parse_args()

    key = args.key or cok_accounts.get_active_key()
    if not key:
        print("[!] 没有可用账号")
        return 1
    acc = cok_accounts.get_account(key)
    if acc is None:
        print("[!] 账号未注册: %s" % key)
        return 1
    print("[*] 账号 %s (%s) pfId=%s" % (key, cok_accounts.account_label(acc),
                                        acc.get("pfId")))

    try:
        with account_lock(timeout=8, purpose="probe %s" % args.cmd, key=key):
            c = CokClient(timeout=args.timeout, account=acc)
            try:
                c.connect()
                c.bin_handshake()
                c.login()
                try:
                    c.call("cmd.ping")
                except Exception as e:  # noqa: BLE001
                    print("[!] ping 失败(继续): %s" % e)
                res = c.call(args.cmd, json.loads(args.params))
                _dump("%s 响应" % args.cmd, res)
            finally:
                c.close()
    except AccountBusy as e:
        print("[!] 账号正被占用, 跳过: %s" % e)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
