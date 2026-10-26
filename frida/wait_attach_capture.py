#!/usr/bin/env python3
"""等待 COK App 进程出现, 自动 attach 并抓包(入站+出站)。

用法:
  python3 wait_attach_capture.py --seconds 300 --out /tmp/bag.jsonl
  (然后在手机上打开游戏 -> 进主城 -> 点开背包/道具界面)
"""
import argparse
import os
import subprocess
import threading
import time

import frida

ADB = "/Users/a1234/Library/Android/sdk/platform-tools/adb"
PKG = "com.hcg.cok.nearme.gamecenter"
HERE = os.path.dirname(os.path.abspath(__file__))


def app_pid():
    try:
        out = subprocess.run([ADB, "shell", "pidof", PKG], capture_output=True,
                             text=True, timeout=6).stdout.strip()
        return int(out.split()[0]) if out else 0
    except Exception:
        return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seconds", type=int, default=300)
    ap.add_argument("--out", default="/tmp/bag.jsonl")
    ap.add_argument("--script", default=os.path.join(HERE, "capture_full2.js"))
    args = ap.parse_args()

    dev = frida.get_usb_device(timeout=20)
    print("[*] device:", dev.id, dev.name, flush=True)

    deadline = time.time() + args.seconds
    pid = 0
    while time.time() < deadline:
        pid = app_pid()
        if pid:
            print("[*] App pid =", pid, flush=True)
            break
        time.sleep(2)
    if not pid:
        print("[!] 超时: 没等到 App 进程")
        return 2

    src = open(args.script, "r", encoding="utf-8").read()
    session = dev.attach(pid)
    script = session.create_script(src)

    counter = {"n": 0}
    lock = threading.Lock()
    fh = open(args.out, "w", encoding="utf-8")

    def on_message(message, data):
        with lock:
            counter["n"] += 1
            fh.write(json.dumps({"ts": time.time(), "msg": message},
                                ensure_ascii=False) + "\n")
            fh.flush()
            p = message.get("payload")
            if message.get("type") == "send" and isinstance(p, dict) \
                    and p.get("t") in ("script_loaded", "hooked", "module"):
                print("[hook]", json.dumps(p, ensure_ascii=False)[:160], flush=True)

    import json  # noqa: E402  (放在闭包里用)
    script.on("message", on_message)
    script.load()
    print("[*] attached, capturing ->", args.out, flush=True)

    try:
        time.sleep(args.seconds)
    except KeyboardInterrupt:
        pass
    try:
        script.unload()
    except Exception:
        pass
    try:
        session.detach()
    except Exception:
        pass
    fh.close()
    print("[*] done, messages:", counter["n"], flush=True)
    return 0


if __name__ == "__main__":
    import json  # noqa: E402
    sys_exit = main()
    raise SystemExit(sys_exit)
