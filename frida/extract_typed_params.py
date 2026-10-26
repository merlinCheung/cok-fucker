#!/usr/bin/env python3
"""从 frida 抓包(wire 帧 + XOR 事件)复原每条命令的**带 SFS 类型**的真实参数。

原理: 客户端发送前先对 params 做 XOR, 所以在时间序上, 一个 out 帧之前紧邻的
      xor_use 事件就是它的 params 加密记录。XOR 回明文后按 SFS 解析即可拿到
      每个字段的**原始键序与类型**(类型是复刻参数的关键)。
"""
import binascii
import collections
import json
import struct
import sys

sys.path.insert(0, "/Users/a1234/workspace/me/cok/frida")
from sfs_types import parse_pairs  # noqa: E402

TYPES = {0x01: "BOOL", 0x02: "BYTE", 0x03: "SHORT", 0x04: "INT", 0x05: "LONG",
         0x08: "STRING", 0x0a: "BYTES", 0x10: "STR_ARRAY", 0x11: "ARRAY",
         0x12: "OBJECT", 0x13: "CLASS"}


def parse_packet(b):
    flags = b[0]
    ln = struct.unpack_from(">H", b, 1)[0]
    payload = b[3:3 + ln]
    return flags, payload


def find_params(payload):
    """在信封字节流里直接定位 "params" 键的 BYTE_ARRAY 值(原始 hex)。

    不能用 parse_pairs: 它会把 0x0a 的值转成 "<N bytes>" 描述串, 拿不到数据。
    这里按 SFS 编码直接扫: keyLen(2) + "params" + type(1=0x0a) + len(4) + data
    """
    pat = struct.pack(">H", 6) + b"params"
    idx = payload.find(pat)
    if idx < 0:
        return None
    i = idx + len(pat)
    if i >= len(payload) or payload[i] != 0x0A:
        return None
    n = struct.unpack_from(">I", payload, i + 1)[0]
    data = payload[i + 5:i + 5 + n]
    if len(data) != n:
        return None
    return data.hex()


def main(path, out="typed-params.json"):
    events = []
    for ln in open(path, encoding="utf-8", errors="replace"):
        try:
            o = json.loads(ln)
        except Exception:
            continue
        p = o.get("msg", {}).get("payload")
        if isinstance(p, dict) and p.get("t") in ("wire", "xor_use"):
            events.append((o.get("ts", 0), p))
    events.sort(key=lambda x: x[0])

    recent_xor = []          # 出现过的 (len, key)
    catalog = {}
    for ts, p in events:
        if p["t"] == "xor_use":
            if p.get("key"):
                recent_xor.append((p.get("len"), p["key"].encode()))
            continue
        # wire 帧
        if p.get("dir") != "write":
            continue
        try:
            raw = binascii.unhexlify(p["hex"])
        except Exception:
            continue
        if not raw or raw[0] != 0x80:
            continue
        try:
            flags, payload = parse_packet(raw)
        except Exception:
            continue
        blobhex = find_params(payload)
        if not blobhex:
            continue
        try:
            blob = binascii.unhexlify(blobhex)
        except Exception:
            continue
        # 遍历出现过的所有 key, 谁能解出合法 SFS 就用谁
        # (请求与响应的 XOR 长度可能撞车, 单纯按长度/时间配对不可靠)
        plain = None
        for cand_len, key in reversed(recent_xor):
            if cand_len != len(blob):
                continue
            trial = bytes(b ^ key[i % len(key)] for i, b in enumerate(blob))
            if trial[:1] != b"\x12":
                continue
            try:
                parse_pairs(trial, 0)
            except Exception:
                continue
            plain = trial
            break
        if plain is None:
            continue
        try:
            pairs, _ = parse_pairs(plain, 0)
        except Exception:
            continue
        params = []
        for k, t, v in pairs:
            if k in ("_cok_", "cmdBaseTime", "newbasekey"):
                continue
            params.append({"key": k, "type": TYPES.get(t, "0x%02x" % t), "value": v})
        # 命令名: 信封 = {p:{p:{params}, r, c:"<cmd>"}, a, c}
        #         命令名在 p 的**直接**子项里(第 2 层), 不是 p.p 里
        cmd = None
        try:
            top, _ = parse_pairs(payload, 0)
            for k, t, v in top:
                if k == "p" and t == 0x12 and isinstance(v, list):
                    for k2, t2, v2 in v:
                        if k2 == "c" and t2 == 0x08 and isinstance(v2, str):
                            cmd = v2
        except Exception:
            pass
        if cmd and cmd not in catalog:
            catalog[cmd] = params
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(catalog, fh, ensure_ascii=False, indent=1)
    print("提取到 %d 条命令的带类型参数 -> %s" % (len(catalog), out))
    for c in list(catalog)[:8]:
        print("  %-28s %s" % (c, catalog[c][:3]))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "keyproof.jsonl")
