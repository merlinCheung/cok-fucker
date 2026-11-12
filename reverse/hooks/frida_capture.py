#!/usr/bin/env python3
"""
Frida 驱动: 给 COK 游戏主进程注入 cok_hook.js, 抓 AES 密钥 / 明文命令流。

用法:
  python3 frida_capture.py --pkg com.hcg.cok.nearme.gamecenter --seconds 120
  python3 frida_capture.py --pid 12345 --seconds 60
"""
import argparse
import json
import os
import sys
import threading
import time

import frida


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pkg", default="com.hcg.cok.nearme.gamecenter")
    ap.add_argument("--pid", type=int, default=0)
    ap.add_argument("--seconds", type=int, default=120)
    ap.add_argument("--out", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "cok-capture.jsonl"))
    ap.add_argument("--script", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "cok_hook.js"))
    ap.add_argument("--device", default="usb")
    args = ap.parse_args()

    if args.device == "usb":
        dev = frida.get_usb_device(timeout=20)
    else:
        dev = frida.get_device(args.device, timeout=20)
    print("[*] device:", dev.id, dev.name, dev.type, flush=True)

    src = open(args.script, "r", encoding="utf-8").read()

    session = None
    spawned = False
    if args.pid:
        pid = args.pid
        print("[*] attaching to pid", pid, flush=True)
        session = dev.attach(pid)
    else:
        print("[*] spawning", args.pkg, flush=True)
        try:
            pid = dev.spawn([args.pkg])
            spawned = True
            session = dev.attach(pid)
            print("[*] spawned pid", pid, flush=True)
        except Exception as e:  # noqa: BLE001
            print("[!] spawn failed:", e, flush=True)
            print("[!] attach to running process instead", flush=True)
            return 2

    counter = {"n": 0}
    lock = threading.Lock()
    fh = open(args.out, "w", encoding="utf-8")

    def on_message(message, data):
        with lock:
            counter["n"] += 1
            rec = {"ts": time.time(), "msg": message}
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
            fh.flush()
            if message.get("type") == "send":
                p = message.get("payload")
                t = p.get("t") if isinstance(p, dict) else None
                if t in ("cipher_init", "encrypter", "ext_request_init", "crypto_key",
                         "handshake_request", "header_encrypted", "module", "installed",
                         "login_request_init", "header_to_string",
                         "connect", "send", "sendto", "recv", "recvfrom"):
                    print("[hook]", json.dumps(p, ensure_ascii=False)[:600], flush=True)
            elif message.get("type") == "error":
                print("[err]", message.get("description"), flush=True)

    script = session.create_script(src)
    script.on("message", on_message)
    script.load()

    if spawned:
        dev.resume(pid)
        print("[*] resumed", flush=True)

    print("[*] capturing for %ds -> %s" % (args.seconds, args.out), flush=True)
    try:
        time.sleep(args.seconds)
    except KeyboardInterrupt:
        print("\n[*] interrupted", flush=True)

    try:
        script.unload()
    except Exception:  # noqa: BLE001
        pass
    try:
        session.detach()
    except Exception:  # noqa: BLE001
        pass
    fh.close()
    print("[*] done, messages:", counter["n"], flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
