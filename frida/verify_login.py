#!/usr/bin/env python3
"""端到端验证: 从 frida 抓包里同时取
   (a) 运行时 native MD5 的输入序列
   (b) 登录请求线上字段
然后用协议库回算 signCode/buildCode/SecurityCode/cc, 与线上逐项比对。

用法: python3 verify_login.py <frida.jsonl>
"""
import binascii
import collections
import hashlib
import json
import sys

sys.path.insert(0, "/Users/a1234/workspace/me/cok/COK-CN1-analysis/protocol")
from cok_sfs import parse_packet, flatten, derive_login_fields, sign_code_from_cert  # noqa: E402

CERT_DER = "/tmp/cert0.der"


def try_frame(buf, i):
    if i + 3 > len(buf):
        return None
    if not (buf[i] & 0x80):
        return None
    ln = (buf[i + 1] << 8) | buf[i + 2]
    if ln == 0 or i + 3 + ln > len(buf):
        return None
    fr = bytes(buf[i:i + 3 + ln])
    try:
        fl, payload, obj, cons = parse_packet(fr)
    except Exception:
        return None
    if cons != len(payload):
        return None
    return fr, obj


def extract_frames(buf):
    out, i = [], 0
    while i + 3 <= len(buf):
        r = try_frame(buf, i)
        if r is None:
            i += 1
            continue
        out.append(flatten(r[1]) or {})
        i += 3 + ((buf[i + 1] << 8) | buf[i + 2])
    return out


def main(path):
    streams = collections.defaultdict(bytearray)
    md5_inputs = []
    for ln in open(path, encoding="utf-8", errors="replace"):
        try:
            o = json.loads(ln)
        except Exception:
            continue
        p = o.get("msg", {}).get("payload")
        if not isinstance(p, dict):
            continue
        t = p.get("t")
        if t == "wire":
            streams[(p.get("fd"), p.get("dir"))].extend(binascii.unhexlify(p["hex"]))
        elif t == "md5_update":
            md5_inputs.append(p.get("text"))

    print("=== 运行时 native MD5 输入中与登录相关的 ===")
    for s in md5_inputs:
        if not s:
            continue
        if "e01684719c1bec876c10bb124a6d65aa" in s or "d6b63d01d640fb78c979912ec839a0de" in s:
            print("  %s" % s)
            print("      md5 =", hashlib.md5(s.encode()).hexdigest())

    # 找登录请求
    login = None
    for (fd, d), buf in streams.items():
        if d != "write":
            continue
        for f in extract_frames(bytes(buf)):
            if not f:
                continue
            if "p.p.signCode" in f:
                login = f
                break
        if login:
            break
    if not login:
        print("\n!! 没找到登录请求")
        return 1

    t = login.get("p.p.cmdBaseTime")
    uid = login.get("p.p.gameUid")
    av = login.get("p.p.appVersion")
    print("\n=== 登录请求线上字段 ===")
    for k in ("cmdBaseTime", "appVersion", "gameUid", "signCode", "buildCode", "SecurityCode", "cc"):
        print("  %-13s = %s" % (k, login.get("p.p." + k)))

    sc = None
    try:
        sc = sign_code_from_cert(open(CERT_DER, "rb").read())
    except Exception as e:
        print("  (证书不可用: %s)" % e)
    d = derive_login_fields(t, uid, av, sc, login.get("p.p.buildCode"))

    print("\n=== 用协议库回算并比对 ===")
    ok = True
    for k in ("signCode", "buildCode", "SecurityCode", "cc"):
        want = login.get("p.p." + k)
        got = d.get(k)
        same = (want == got)
        ok = ok and same
        print("  %-13s 线上=%s" % (k, want))
        print("  %-13s 回算=%s   %s" % ("", got, "一致 ✓" if same else "不一致 ✗"))
    print("\n总判定:", "全部一致 ✓" if ok else "存在不一致 ✗")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
