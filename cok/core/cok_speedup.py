#!/usr/bin/env python3
"""COK 加速工具: 列出建造/训练队列, 并用加速道具(或金币)加速。

已实测(2026-10-23, 直连非 App):
  * 队列清单来自**登录后服务端的 `init` 推送**(混淆键里, 用会话密钥解密)
  * 加速命令 = `queue.ccd`
      道具模式: {qUUID, itemUUID, isGold:0, itemCount:N}   ← 4 字段
      金币模式: {qUUID, itemUUID:"", isGold:1, itemCount:1, queueId, queueType, goldcost}
  * `itemUUID` = 背包里该道具的**实例 uuid**(32 位 hex), 见 speedup-owned.json
  * 造兵队列用 type2=3(造兵)或 type2=1(通用)道具; 城建队列用 type2=7 或 type2=1

用法:
  python3 cok_speedup.py --list                       # 只列队列
  python3 cok_speedup.py --item 200201                # 用 1 个通用5分钟道具加速
  python3 cok_speedup.py --item 200201 --count 3      # 用 3 个
  python3 cok_speedup.py --queue-type 1 --item 200201 # 指定队列类型(1=造兵 0=城建)
  python3 cok_speedup.py --gold                       # 用金币(实扣)
"""
# --- 包自举: 直接 `python3 cok/core/xxx.py` 时把 cok/ 加进 sys.path ---
import os as _os
import sys as _sys

_PKG_ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
if _os.path.isdir(_PKG_ROOT) and _PKG_ROOT not in _sys.path:
    _sys.path.insert(0, _PKG_ROOT)
_CORE = _os.path.join(_PKG_ROOT, "core")
if _os.path.isdir(_CORE) and _CORE not in _sys.path:
    _sys.path.insert(0, _CORE)
import cok_paths  # noqa: E402
from cok_paths import resource as _res  # noqa: E402

import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from cok_client import CokClient  # noqa: E402
from cok_sfs import decode_params, parse_packet  # noqa: E402
import cok_account  # noqa: E402

QUEUE_TYPE_NAME = {
    0: "建造队列", 1: "造兵队列", 2: "行军", 3: "?", 6: "?", 8: "?", 9: "联盟",
    10: "?", 12: "?", 16: "?", 19: "?", 32: "?", 33: "?", 35: "?", 36: "?",
    38: "?", 39: "?", 42: "?", 43: "?", 44: "?",
}


def load_owned():
    p = _res("speedup-owned.json")
    try:
        return json.load(open(p, encoding="utf-8"))["items"]
    except Exception:
        return {}


def grab_init(c, wait=25.0):
    """登录后收 init 推送并解密。收帧要耐心: 推送可能延后到, 超时不要 break。"""
    c.sock.settimeout(3.0)
    buf = b""
    t0 = time.time()
    while time.time() - t0 < wait:
        try:
            ch = c.sock.recv(65536)
        except Exception:
            continue
        if not ch:
            break
        buf += ch
        i = 0
        while i + 3 <= len(buf):
            flags = buf[i]
            ln = (buf[i + 1] << 8) | buf[i + 2]
            if not (flags & 0x80) or ln == 0 or i + 3 + ln > len(buf):
                break
            try:
                _, _, obj, _ = parse_packet(buf[i:i + 3 + ln])
            except Exception:
                break
            pp = c._resp_params(obj)
            if c._resp_cmd(obj) == "init":
                for k, v in pp.items():
                    if isinstance(v, str) and len(v) > 60 and k != "qqq":
                        try:
                            o2, _, _ = decode_params(bytes.fromhex(v), c.key)
                            return o2
                        except Exception:
                            pass
            i += 3 + ln
        buf = buf[i:]
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--account-device", action="store_true", default=True,
                    help="从设备 SharedPreferences 自动读账号(默认开)")
    ap.add_argument("--timeout", type=float, default=60.0)
    ap.add_argument("--list", action="store_true", help="只列出队列, 不加速")
    ap.add_argument("--item", help="道具**模板 id**, 如 200201(通用5分钟); "
                            "实例 uuid 从 speedup-owned.json 查")
    ap.add_argument("--count", type=int, default=1, help="使用的道具数量")
    ap.add_argument("--queue-type", type=int, default=1, help="目标队列 type(1=造兵 0=城建)")
    ap.add_argument("--uuid", help="直接指定队列 uuid")
    ap.add_argument("--gold", action="store_true", help="用金币加速(实扣金币)")
    ap.add_argument("--json", action="store_true", help="机器可读输出")
    args = ap.parse_args()

    acct = cok_account.load_account()
    c = CokClient(account=acct, timeout=args.timeout)
    c.connect()
    c.login()

    init = grab_init(c)
    queues = (init or {}).get("queue") or []
    if not queues:
        print("[!] 未收到 init 推送, 拿不到队列清单(可加 --uuid 手动指定)")
        if not args.uuid:
            return 2

    def qstat(q):
        t = q.get("totalTime") or 0
        s = q.get("startTime") or 0
        return "进行中" if (t > 0 and s > 0) else ("已完成" if q.get("endTime") else "空闲")

    rows = []
    for q in queues:
        if not isinstance(q, dict):
            continue
        rows.append({
            "type": q.get("type"), "qid": q.get("qid"), "uuid": q.get("uuid"),
            "totalTime": q.get("totalTime") or 0, "startTime": q.get("startTime") or 0,
            "状态": qstat(q),
            "名称": QUEUE_TYPE_NAME.get(q.get("type"), "?"),
        })
    if args.json:
        print(json.dumps({"queues": rows}, ensure_ascii=False))
    else:
        print("[+] 队列 %d 条 (来自 init 推送)" % len(rows))
        for r in rows:
            print("    type=%-4s %-6s %-6s total=%-10s %s"
                  % (r["type"], r["名称"], r["状态"], r["totalTime"], r["uuid"]))

    if args.list:
        return 0

    qu = args.uuid
    if not qu:
        for r in rows:
            if r["type"] == args.queue_type and r["totalTime"] > 0 and r["startTime"] > 0:
                qu = r["uuid"]
                break
    if not qu:
        print("[!] 没有进行中的 type=%s 队列可用" % args.queue_type)
        return 3

    if args.gold:
        params = {"qUUID": qu, "itemUUID": "", "isGold": 1, "itemCount": 1,
                  "queueId": "1", "queueType": str(args.queue_type), "goldcost": "0"}
        print("\n=== queue.ccd (金币加速) 队列=%s ===" % qu)
    else:
        if not args.item:
            print("[!] 需要 --item <道具模板 id>(见 speedup-owned.json); 或用 --gold")
            return 4
        owned = load_owned()
        ent = owned.get(str(args.item))
        if not ent:
            print("[!] speedup-owned.json 里没有道具 %s(该快照不含此道具或已用完)" % args.item)
            return 5
        params = {"qUUID": qu, "itemUUID": ent["uuid"],
                  "isGold": 0, "itemCount": int(args.count)}
        print("\n=== queue.ccd (道具加速) ===")
        print("  道具 %s (%s, type2=%s) 实例 uuid=%s  数量=%d"
              % (args.item, ent.get("label"), ent.get("type2"), ent["uuid"], args.count))
        print("  队列 uuid=%s" % qu)
    print("  params:", json.dumps(params, ensure_ascii=False))

    try:
        r = c.call("queue.ccd", params, retries=1)
        p = r.get("__params__") or r
        print("  响应:", json.dumps(p, ensure_ascii=False)[:500])
        if p.get("finished"):
            print("  ✅ 加速完成")
        elif p.get("errorCode"):
            print("  ⚠️  业务错误:", p.get("errorCode"))
    except Exception as e:
        print("  ERR", str(e)[:160])
    return 0


if __name__ == "__main__":
    sys.exit(main())
