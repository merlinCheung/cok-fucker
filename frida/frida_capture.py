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


def preload_bridge(src, name="java"):
    """把 frida-tools 的 bridge(Java/ObjC/Swift)预置进脚本。

    为什么需要: frida 的 Java bridge **不是** agent 自带的, 而是 frida-tools
    宿主侧按需回灌的 —— 脚本访问 `Java` 时发 {type:"frida:load-bridge"},
    宿主再把 bridges/java.js 的源码 post 回脚本里求值。
    自己用 Python API 驱动时没人回灌, 表现就是
    "ReferenceError: 'Java' is not defined"(frida CLI 默认能工作, 就是因为
    它实现了这个协议)。

    这里直接前置 bridge 源码 + 定义全局, 等价于宿主回灌一次。
    """
    if not name:
        return src
    try:
        import frida_tools
        from pathlib import Path
        p = Path(frida_tools.__file__).parent / "bridges" / ("%s.js" % name)
        if not p.exists():
            print("[!] bridge not found: %s" % p, flush=True)
            return src
        code = p.read_text(encoding="utf-8")
    except Exception as e:  # noqa: BLE001
        print("[!] bridge preload failed:", e, flush=True)
        return src
    return ("%s\nObject.defineProperty(globalThis, '%s', {value: bridge});\n%s"
            % (code, name.capitalize(), src))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pkg", default="com.hcg.cok.nearme.gamecenter")
    ap.add_argument("--pid", type=int, default=0)
    ap.add_argument("--seconds", type=int, default=120)
    ap.add_argument("--out", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "cok-capture.jsonl"))
    ap.add_argument("--script", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "cok_hook.js"))
    ap.add_argument("--device", default="usb")
    ap.add_argument("--bridge", default="java",
                    help="预置的 bridge: java/objc/swift/none(不预置)")
    args = ap.parse_args()

    if args.device == "usb":
        dev = frida.get_usb_device(timeout=20)
    else:
        dev = frida.get_device(args.device, timeout=20)
    print("[*] device:", dev.id, dev.name, dev.type, flush=True)

    src = open(args.script, "r", encoding="utf-8").read()
    src = preload_bridge(src, args.bridge)

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

    # ⚠ 必须用 V8 runtime: frida 的 Java bridge(javax.crypto / okhttp 等)
    #   在 QuickJS(frida 17 的 create_script 默认值)下**不存在**, 表现为
    #   "ReferenceError: 'Java' is not defined"。frida CLI 默认就是 V8。
    script = session.create_script(src, runtime="v8")
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
