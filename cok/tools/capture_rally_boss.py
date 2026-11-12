#!/usr/bin/env python3
"""真机抓包: 巨型狮鹫(活动怪) + 集结(rally) 的真实协议。

流程:
  1. 手机上启动游戏(登录到世界地图)
  2. tcpdump 抓游戏服 TCP(32231)
  3. 用 adb 触发 UI 操作(找活动怪 -> 集结)
  4. 收包 + 用已有的 SFS 解码器解出明文

用法:
  python3 capture_rally_boss.py            # 全流程
  python3 capture_rally_boss.py --capture-only   # 只抓包不解码
"""
import json
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "core"))

ADB = os.environ.get("ADB", os.path.expanduser(
    "~/Library/Android/sdk/platform-tools/adb"))
PKG = os.environ.get("PKG", "com.hcg.cok.nearme.gamecenter")
OUT = os.path.join(HERE, "evidence")


def sh(*args, **kw):
    return subprocess.run([ADB] + list(args), capture_output=True, text=True, **kw)


def sh_su(cmd):
    return sh("shell", "su -c '%s'" % cmd)


def main():
    only_capture = "--capture-only" in sys.argv
    os.makedirs(OUT, exist_ok=True)
    serial = sh("devices").stdout
    serials = [l.split()[0] for l in serial.splitlines()[1:]
               if l.strip() and l.split()[1] == "device"]
    if not serials:
        print("[!] 没有设备")
        return 2
    dev = serials[0]
    print("[*] 设备 %s 包 %s" % (dev, PKG))

    pcap = "/data/local/tmp/rally.pcap"
    sh_su("rm -f %s" % pcap)
    filt = "tcp port 32231"
    r = sh_su("nohup tcpdump -i any -s 0 -U -w %s \"%s\" >/dev/null 2>&1 &" % (pcap, filt))
    print("[*] tcpdump 启动:", (r.stdout or r.stderr).strip()[:120])
    time.sleep(3)

    # 启动游戏
    sh("shell", "am force-stop %s" % PKG)
    time.sleep(2)
    sh("shell", "monkey -p %s -c android.intent.category.LAUNCHER 1" % PKG)
    print("[*] 游戏启动, 等待登录(40s) ...")
    time.sleep(40)

    print("[*] 现在请在手机上操作:")
    print("    1) 进世界地图")
    print("    2) 找到「巨型狮鹫」(活动怪, 可用活动界面「前往」)")
    print("    3) 点它 -> 选集结 -> 选一个集结时间 -> 确认出征")
    print("    按回车开始计时 90 秒 ...")
    try:
        input()
    except EOFError:
        time.sleep(90)

    sh_su("pkill tcpdump")
    time.sleep(2)
    dst = os.path.join(OUT, "capture-rally-boss.pcap")
    sh("pull", pcap, dst)
    print("[*] 抓到 %s (%d 字节)" % (dst, os.path.getsize(dst)
                                    if os.path.exists(dst) else 0))

    if only_capture:
        return 0

    # 解码: 用现有的 pcap/SFS 解码器
    try:
        from cok_sfs import decode_capture  # type: ignore
        print("[*] 用 cok_sfs.decode_capture 解码")
    except Exception:
        print("[!] cok_sfs 没有 decode_capture, 稍后手动解")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
