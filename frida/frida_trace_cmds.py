#!/usr/bin/env python3
"""用 frida spawn 抓真实客户端**登录全过程的协议请求命令名** —— 2026-11-10。

目的: 我们 PC 端登录后只发过 init 相关的请求, 但客户端背包(道具 uuid)在
      ToolController 里 —— 说明客户端**一定**发过某个我们没发的命令,
      或者服务端在别的时点推了道具列表。
      抓命令序列 = 直接看到「客户端登录时到底发了什么」。

用法:
    python3 frida_trace_cmds.py [package] [seconds]
    python3 frida_trace_cmds.py com.hcg.cok.ewanqf.guopan 90
"""
import json
import os
import sys
import threading
import time

import frida

ADB = "/Users/a1234/Library/Android/sdk/platform-tools/adb"
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)                      # .../cok
PROTO = os.path.join(ROOT, "COK-CN1-analysis", "protocol")

SOCKET_HOOK = os.path.join(PROTO, "frida", "cmd_trace_both.js")
NATIVE_HOOK = os.path.join(HERE, "native_cmd.js")


def main():
    pkg = sys.argv[1] if len(sys.argv) > 1 else "com.hcg.cok.ewanqf.guopan"
    secs = int(sys.argv[2]) if len(sys.argv) > 2 else 90

    dev = frida.get_usb_device(timeout=25)
    print("[*] spawn %s ..." % pkg, flush=True)
    pid = dev.spawn([pkg])
    session = dev.attach(pid)
    print("[*] attached pid=%d" % pid, flush=True)

    events = []
    lock = threading.Lock()

    def on_message(message, data):
        p = message.get("payload")
        if message.get("type") == "send" and isinstance(p, dict):
            with lock:
                events.append(p)

    for path in (SOCKET_HOOK, NATIVE_HOOK):
        if not os.path.exists(path):
            print("[!] 缺脚本 %s" % path)
            continue
        try:
            src = open(path, encoding="utf-8").read()
            sc = session.create_script(src)
            sc.on("message", on_message)
            sc.load()
            print("[*] loaded %s" % os.path.basename(path), flush=True)
        except Exception as e:  # noqa: BLE001
            print("[!] %s 加载失败: %s" % (path, e))

    dev.resume(pid)
    print("[*] resumed, 采集 %d 秒…" % secs, flush=True)

    end = time.time() + secs
    while time.time() < end:
        time.sleep(2)
        with lock:
            n = len(events)
        if n and n % 25 == 0:
            print("    已 %d 条事件" % n, flush=True)

    try:
        session.detach()
    except Exception:  # noqa: BLE001
        pass

    with lock:
        evs = list(events)

    sock_send, sock_recv, native_cmds = [], [], []
    for e in evs:
        t = e.get("t")
        if t == "game_command":
            (sock_send if e.get("direction") == "send" else sock_recv).append(
                (e.get("cmd"), e.get("bytes")))
        elif t == "native_cmd":
            native_cmds.append(e.get("cmd"))

    print("\n=== 客户端**发出**的命令 (socket send, 去重保序) ===", flush=True)
    seen = set()
    for cmd, n in sock_send:
        if cmd in seen:
            continue
        seen.add(cmd)
        print("  %-46s %s bytes" % (cmd, n), flush=True)

    print("\n=== native 请求入口 (FUN_..._send) 抓到的命令 ===", flush=True)
    seen = set()
    for c in native_cmds:
        if c in seen:
            continue
        seen.add(c)
        print("  %s" % c, flush=True)

    print("\n=== 收到方向出现的点号串 (可能是服务端下发的命令名) ===", flush=True)
    seen = set()
    for cmd, n in sock_recv:
        if cmd in seen:
            continue
        seen.add(cmd)
        print("  %-46s %s bytes" % (cmd, n), flush=True)

    out = os.path.join(ROOT, "frida", "trace-cmds-%s.json" % pkg.replace(".", "_"))
    json.dump({"send": sock_send, "recv": sock_recv, "native": native_cmds},
              open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("\n[*] 原始事件写入 %s" % out)


if __name__ == "__main__":
    main()
