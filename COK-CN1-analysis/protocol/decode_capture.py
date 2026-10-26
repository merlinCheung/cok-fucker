#!/usr/bin/env python3
"""COK 游戏服抓包重组 + 解密: 从 frida JSONL 还原 SFS 帧并解出 params 明文。"""
import binascii
import collections
import json
import sys

sys.path.insert(0, "/Users/a1234/workspace/me/cok/COK-CN1-analysis/protocol")
from cok_sfs import parse_packet, flatten, xor_buf, Reader, read_value, parse_best, decode_params  # noqa: E402


def try_frame(buf, i):
    """若 i 处是一个完整合法 SFS 帧, 返回 (frame, obj, consumed); 否则 None"""
    if i + 3 > len(buf):
        return None
    if not (buf[i] & 0x80):          # 真实帧必有 0x80(大端长度)
        return None
    ln = (buf[i + 1] << 8) | buf[i + 2]
    if ln == 0 or i + 3 + ln > len(buf):
        return None
    fr = bytes(buf[i:i + 3 + ln])
    try:
        flags, payload, obj, consumed = parse_packet(fr)
    except Exception:
        return None
    if consumed != len(payload):
        return None
    return fr, obj, 3 + ln


def extract_frames(buf):
    """TCP 字节流 -> SFS 帧列表 (逐位置校验, 只有能完整解析的才算帧)"""
    frames = []
    i = 0
    n = len(buf)
    while i + 3 <= n:
        r = try_frame(buf, i)
        if r is None:
            i += 1
            continue
        fr, obj, size = r
        frames.append((fr, obj))
        i += size
    return frames


def main(path, key_hex=None):
    KEY = bytes.fromhex(key_hex) if key_hex else None
    pairs, wires = [], []
    for ln in open(path, encoding="utf-8", errors="replace").read().splitlines():
        try:
            rec = json.loads(ln)
        except Exception:
            continue
        pl = rec.get("msg", {}).get("payload")
        if not isinstance(pl, dict):
            continue
        if pl.get("t") in ("enc_pair", "enc_pair_B"):
            pairs.append(pl)
        elif pl.get("t") == "wire":
            wires.append(pl)

    if KEY is None:
        keys = collections.Counter()
        for x in pairs:
            ph, ch = x.get("plain_hex"), x.get("cipher_hex")
            if not ph or not ch or len(ph) != len(ch) or not ph.startswith("12"):
                continue
            p1, c1 = bytes.fromhex(ph), bytes.fromhex(ch)
            ks = bytes(a ^ b for a, b in zip(p1, c1))
            keys[ks[:32].hex()] += 1
        if not keys:
            print("无法从 enc_pair 推导密钥")
            return 1
        KEY = bytes.fromhex(keys.most_common(1)[0][0])
    print("会话 XOR 密钥 = %s" % KEY.decode("latin1"))

    streams = collections.defaultdict(lambda: collections.defaultdict(bytearray))
    for w in wires:
        streams[w.get("fd")][w.get("dir")].extend(binascii.unhexlify(w["hex"]))

    cmds = collections.Counter()
    rows = []
    ok = fail = 0
    for fd, d in streams.items():
        for dirn, buf in d.items():
            for fr, obj in extract_frames(bytes(buf)):
                f = flatten(obj)
                cmd = f.get("p.c") or f.get("p.p.c")
                pb = f.get("p.p.params")
                if cmd is None and pb is None:
                    continue
                cmds[(dirn, cmd)] += 1
                inner = None
                if isinstance(pb, str):
                    blob = binascii.unhexlify(pb)
                    try:
                        inner = read_value(Reader(xor_buf(blob, KEY)))
                        ok += 1
                    except Exception as e:  # noqa: BLE001
                        inner = {"__err__": str(e)}
                        fail += 1
                rows.append((dirn, len(fr), cmd, inner, f))
    print("解析帧 %d | params 解密成功 %d | 失败 %d" % (sum(cmds.values()), ok, fail))
    print("\n=== 命令统计 ===")
    for (dirn, c), n in cmds.most_common(40):
        print("  [%-5s] %-28s x%d" % (dirn, c, n))
    print("\n=== 样例 ===")
    seen = set()
    for dirn, l, cmd, inner, f in rows:
        k = (dirn, cmd)
        if k in seen:
            continue
        seen.add(k)
        print("--- %s len=%d cmd=%s" % (dirn, l, cmd))
        for kk, v in f.items():
            if kk.endswith("params"):
                print("      %-16s = <%d 字节密文>" % (kk, len(v) // 2))
            else:
                print("      %-16s = %s" % (kk, str(v)[:70]))
        if isinstance(inner, dict):
            for kk, v in flatten(inner).items():
                print("      >> %-13s = %s" % (kk, str(v)[:70]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None))
