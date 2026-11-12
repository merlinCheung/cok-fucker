#!/usr/bin/env python3
"""实测每日签到: monthlySign.sign, 并对比签到前后 monthlySign.info。"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "core"))
sys.path.insert(0, os.path.join(HERE, "..", "tools"))
from cok_client import CokClient  # noqa: E402


def sign_info(c):
    r = c.call("monthlySign.info")
    return r.get("__params__") or {}


def main():
    c = CokClient(timeout=15)
    c.connect()
    c.bin_handshake()
    c.login()
    try:
        c.call("cmd.ping")
    except Exception:
        pass

    before = sign_info(c)
    print("=== 签到前 ===")
    print("  已签日期   :", before.get("days"))
    print("  剩余补签   :", before.get("leftLostSignTimes"))
    print("  月卡档位   :", before.get("multiDays"))

    print("\n=== 发送 monthlySign.sign ===")
    try:
        r = c.call("monthlySign.sign")
        p = r.get("__params__") or {}
        print("  响应:", json.dumps(p, ensure_ascii=False, default=str)[:400])
    except Exception as e:  # noqa: BLE001
        print("  失败:", str(e)[:150])

    after = sign_info(c)
    print("\n=== 签到后 ===")
    print("  已签日期   :", after.get("days"))
    print("  剩余补签   :", after.get("leftLostSignTimes"))
    same = str(before.get("days")) == str(after.get("days"))
    print("  签到状态   :", "**无变化**" if same else "**已变化(签到成功)**")
    c.close()


if __name__ == "__main__":
    main()
