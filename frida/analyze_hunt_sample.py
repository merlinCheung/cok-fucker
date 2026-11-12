#!/usr/bin/env python3
"""从 frida 抓包里挖出「打怪出征」样本, 反推 x,y→point index 换算与 marchKey 算法。

样本来源(同一次 App 会话):
  * res.tile.find 的**响应** -> x, y (怪的世界坐标)
  * world.march 的**请求**   -> point(index), soldiers, marchKey, type

用法:
  python3 analyze_hunt_sample.py /tmp/hunt_capture2.jsonl
"""
import binascii
import hashlib
import json
import re
import sys

PROTO = "/Users/a1234/workspace/me/cok/cok"
sys.path.insert(0, PROTO)
import cok_sfs  # noqa: E402


def load(path):
    keys, wires = [], []
    for ln in open(path, encoding="utf-8", errors="replace"):
        ln = ln.strip()
        if not ln:
            continue
        try:
            o = json.loads(ln)
        except Exception:
            continue
        p = (o.get("msg") or {}).get("payload") or {}
        t = p.get("t")
        if t == "key" and p.get("key"):
            keys.append(bytes.fromhex(p["key"]))
        elif t == "w" and p.get("hex"):
            wires.append(p["hex"])
    return keys, wires


def frames(path, key):
    """产出 (cmd, params) —— 响应方向的 params 会再解一层 zlib。"""
    out = []
    seen = set()
    for hexs in load(path)[1]:
        try:
            raw = binascii.unhexlify(hexs)
        except Exception:
            continue
        if raw in seen:
            continue
        seen.add(raw)
        try:
            flags, payload, obj, consumed = cok_sfs.parse_packet(raw)
        except Exception:
            continue
        f = cok_sfs.flatten(obj)
        cmd = f.get("p.c")
        if not cmd:
            continue
        pb = f.get("p.p.params")
        params = None
        if isinstance(pb, str):
            try:
                x = cok_sfs.xor_buf(binascii.unhexlify(pb), key)
                if x[:2] == b"\x78\x9c":
                    x = cok_sfs.zlib.decompress(x)
                params, _ = cok_sfs.parse_best(x)
            except Exception:
                params = None
        out.append((cmd, params))
    return out


def find_tile_samples(fr):
    """res.tile.find 的响应 -> [(x, y, level, type)]"""
    out = []
    for cmd, p in fr:
        if cmd != "res.tile.find" or not isinstance(p, dict):
            continue
        if "x" in p and "y" in p:
            out.append((p.get("x"), p.get("y"), p.get("level"), p.get("type")))
    return out


def find_march_samples(fr):
    """world.march 的请求 -> [params]"""
    return [p for cmd, p in fr if cmd == "world.march" and isinstance(p, dict)
            and "point" in p]


def guess_index_formulas(x, y):
    return {
        "x*1200+y": x * 1200 + y,
        "y*1200+x": y * 1200 + x,
        "(x-1)*1200+(y-1)": (x - 1) * 1200 + (y - 1),
        "x*1201+y": x * 1201 + y,
        "y*1201+x": y * 1201 + x,
        "x*1200+y+1": x * 1200 + y + 1,
        "y*1200+x+1": y * 1200 + x + 1,
        "x*1200-y": x * 1200 - y,
        "x+y*1200": x + y * 1200,
    }


def marchkey_variants(idx, typ, army, order="given"):
    """marchKey 的几种可能拼法(客户端算法 + 不带兵版本)。"""
    out = {}
    out["no_army"] = hashlib.md5(
        ("%d1021%d" % (idx, (typ + 1) * 1000) + "wNSc5Mm8YwiOhAab").encode()).hexdigest()
    if army:
        parts = ["%d" % idx, "1021", "%d" % ((typ + 1) * 1000)]
        items = list(army.items())
        for aid, (speed, load, num) in items:
            parts += [str(aid), str(speed), str(load), str(num)]
        parts.append("wNSc5Mm8YwiOhAab")
        out["with_army"] = hashlib.md5("".join(parts).encode()).hexdigest()
        items2 = sorted(items, key=lambda kv: int(kv[0]))
        parts = ["%d" % idx, "1021", "%d" % ((typ + 1) * 1000)]
        for aid, (speed, load, num) in items2:
            parts += [str(aid), str(speed), str(load), str(num)]
        parts.append("wNSc5Mm8YwiOhAab")
        out["with_army_sorted"] = hashlib.md5("".join(parts).encode()).hexdigest()
    return out


def main():
    path = sys.argv[1]
    keys, _ = load(path)
    if not keys:
        print("[!] 没有会话密钥")
        return 1
    key = keys[-1]
    fr = frames(path, key)
    print("[*] 命令帧 %d, 会话密钥 %s" % (len(fr), key.decode()))

    tiles = find_tile_samples(fr)
    marches = find_march_samples(fr)
    print("[*] res.tile.find 响应样本: %d" % len(tiles))
    for t in tiles[:10]:
        print("    x=%s y=%s level=%s type=%s" % t)
    print("[*] world.march 请求样本: %d" % len(marches))
    for m in marches[:10]:
        print("    %s" % json.dumps(m, ensure_ascii=False, default=str)[:500])

    if not marches:
        print("\n[!] 还没有出征样本 —— 需要在 App 里搜索一只怪并点它攻击")
        return 2

    m = marches[0]
    idx = m.get("point")
    typ = m.get("type")
    mk = m.get("marchKey")
    soldiers = m.get("soldiers")
    print("\n=== 样本 ===")
    print("point=%s type=%s marchKey=%s" % (idx, typ, mk))
    print("soldiers=%s" % json.dumps(soldiers, ensure_ascii=False, default=str))

    # 用样本反推 index 公式: 拿 tile 坐标对照
    if tiles:
        x, y = tiles[-1][0], tiles[-1][1]
        print("\n=== 用坐标 (%s, %s) 反推 index 公式 ===" % (x, y))
        for name, cand in guess_index_formulas(x, y).items():
            if cand == idx:
                print("  ✅ 命中: %s = %s" % (name, cand))
            else:
                print("     %-22s = %s" % (name, cand))

    # 用样本反推 marchKey
    print("\n=== 反推 marchKey ===")
    variants = marchkey_variants(idx, typ or 6, None)
    for name, v in variants.items():
        print("  %-18s %s %s" % (name, v, "✅ 命中" if v == mk else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
