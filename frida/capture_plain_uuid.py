#!/usr/bin/env python3
"""hook native 的 XOR 引擎, 抓**加密前**的明文 SFS —— 2026-11-10。

目的: 找出「服务端下发玩家背包(道具实例 uuid)」的那条命令。

思路:
  * 协议帧 = [flags][len][SFS 载荷]; 载荷里的 params 是 XOR(密钥, zlib(SFS明文))
  * native 的 XOR 引擎函数在**加密前**拿到明文字节 —— hook 它就能直接看到
    命令名 + 参数 + 道具 uuid, 不需要任何密钥。
  * 抓到所有明文后用 cok_sfs.parse_best 解码, 找出含 32 位 hex(uuid) 的那条。

用法:
    python3 capture_plain_uuid.py --pkg com.hcg.cok.nearme.gamecenter --seconds 100
"""
import argparse
import json
import os
import re
import sys
import threading
import time

import frida

PROTO = os.path.expanduser(
    "~/workspace/me/cok/cok")
sys.path.insert(0, PROTO)
from cok_sfs import parse_best  # noqa: E402

HEX32 = re.compile(rb"^[0-9a-f]{32}$")

HOOK_JS = """
'use strict';
const MODULE = 'libgame.so';
const OFF = { XOR: 0x9e02b8 };
function emit(o) { try { send(o); } catch (e) {} }
function hexOf(buf) {
  const u8 = new Uint8Array(buf);
  let s = '';
  for (let i = 0; i < u8.length; i++) s += ('0' + u8[i].toString(16)).slice(-2);
  return s;
}
function sample(p, len) {
  try {
    if (!p) return null;
    const n = Math.min(Math.max(len | 0, 0), 65536);
    if (n <= 0) return null;
    return hexOf(p.readByteArray(n));
  } catch (e) { return null; }
}
Process.attachModuleObserver({
  onAdded(module) {
    if (module.name !== MODULE) return;
    setTimeout(function () {
      const base = module.base;
      const p = base.add(OFF.XOR);
      try {
        Interceptor.attach(p, {
          onEnter(args) {
            const len = args[1].toInt32();
            if (len <= 0 || len > 200000) return;
            const rec = { t: 'xor', len: len };
            for (let i = 0; i < 5; i++) {
              try { rec['a' + i] = sample(args[i], len); } catch (e) {}
            }
            emit(rec);
          }
        });
        emit({ t: 'hooked', addr: p.toString() });
      } catch (e) { emit({ t: 'hook_err', msg: String(e).slice(0, 160) }); }
    }, 400);
  }
});
// 已经加载完的话直接 hook
setTimeout(function () {
  try {
    const m = Process.findModuleByName(MODULE);
    if (!m) return;
    const p = m.base.add(OFF.XOR);
    Interceptor.attach(p, {
      onEnter(args) {
        const len = args[1].toInt32();
        if (len <= 0 || len > 200000) return;
        const rec = { t: 'xor', len: len };
        for (let i = 0; i < 5; i++) {
          try { rec['a' + i] = sample(args[i], len); } catch (e) {}
        }
        emit(rec);
      }
    });
    emit({ t: 'hooked2', addr: p.toString() });
  } catch (e) { emit({ t: 'hook_err2', msg: String(e).slice(0, 160) }); }
}, 300);
"""


def decode_hex(h):
    """把 hex 串解成 SFS 明文对象, 失败返回 None。"""
    if not h:
        return None
    try:
        raw = bytes.fromhex(h)
    except ValueError:
        return None
    for body in (raw,):
        try:
            obj, mode = parse_best(body)
        except Exception:  # noqa: BLE001
            continue
        if isinstance(obj, dict) and obj:
            return obj
    return None


def find_uuids(obj, path, out, depth=0):
    if depth > 8:
        return
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, str) and HEX32.match(v.encode()):
                out.append((path + "." + str(k), v))
            find_uuids(v, path + "." + str(k), out, depth + 1)
    elif isinstance(obj, list):
        for i, v in enumerate(obj[:300]):
            if isinstance(v, str) and HEX32.match(v.encode()):
                out.append(("%s[%d]" % (path, i), v))
            find_uuids(v, "%s[%d]" % (path, i), out, depth + 1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pkg", default="com.hcg.cok.nearme.gamecenter")
    ap.add_argument("--seconds", type=int, default=100)
    ap.add_argument("--out", default="/tmp/plain-frames.jsonl")
    args = ap.parse_args()

    dev = frida.get_usb_device(timeout=25)
    print("[*] spawn %s" % args.pkg, flush=True)
    pid = dev.spawn([args.pkg])
    session = dev.attach(pid)
    print("[*] attached pid=%d" % pid, flush=True)

    frames = []
    lock = threading.Lock()

    def on_message(message, data):
        p = message.get("payload")
        if message.get("type") == "send" and isinstance(p, dict):
            if p.get("t") == "xor":
                with lock:
                    frames.append(p)
            else:
                print("[hook]", json.dumps(p, ensure_ascii=False)[:160], flush=True)
        elif message.get("type") == "error":
            print("[err]", message.get("description"), flush=True)

    script = session.create_script(HOOK_JS)
    script.on("message", on_message)
    script.load()
    dev.resume(pid)
    print("[*] resumed, 采集 %d 秒…" % args.seconds, flush=True)

    end = time.time() + args.seconds
    while time.time() < end:
        time.sleep(3)
        with lock:
            n = len(frames)
        print("    xor 事件 %d" % n, flush=True)

    try:
        script.unload()
        session.detach()
    except Exception:  # noqa: BLE001
        pass

    with lock:
        frames = list(frames)
    print("\n[*] 共 %d 个 xor 事件" % len(frames), flush=True)

    # 逐个解码, 找带 uuid 的
    seen_cmds = {}
    uuid_hits = []
    for rec in frames:
        for key in ("a0", "a1", "a2", "a3", "a4"):
            h = rec.get(key)
            if not h:
                continue
            obj = decode_hex(h)
            if not obj:
                continue
            cmd = None
            for ck in ("cmd", "c", "command"):
                if isinstance(obj.get(ck), str):
                    cmd = obj[ck]
                    break
            if cmd:
                seen_cmds.setdefault(cmd, obj)
            hits = []
            find_uuids(obj, "", hits)
            if hits:
                uuid_hits.append((key, cmd, hits, obj))
                print("\n★★★ %s 含 %d 个 uuid: %s" % (key, len(hits), hits[:5]), flush=True)
                print("    明文: %s" % json.dumps(obj, ensure_ascii=False)[:1200], flush=True)

    print("\n=== 解出来的命令名 (%d 个) ===" % len(seen_cmds), flush=True)
    for cmd in sorted(seen_cmds):
        print("  %s" % cmd, flush=True)

    with open(args.out, "w", encoding="utf-8") as f:
        for rec in frames:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print("\n[*] 原始 xor 事件写入 %s" % args.out, flush=True)
    print("[*] uuid 命中 %d 条" % len(uuid_hits), flush=True)


if __name__ == "__main__":
    main()
