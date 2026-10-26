#!/usr/bin/env python3
"""端到端验证: 直连 → 取 init 推送的队列 → 用加速道具加速。

道具实例 uuid 取自 App 侧实测(frida 探针):
  itemId 200201(通用5分钟, type2=1) -> uuid 4600cedc8e8a43aeaa5aefba97b7bfa7
  itemId 200247(造兵10分钟, type2=3) -> uuid 1de38e919ce743c1ad69fdebb45a11ba
  itemId 200208(造兵2小时,  type2=3) -> uuid 3757a02129df4a5ba8c25e59f3495678
造兵队列(进行中) uuid = 9f993a6425a64d6cb48d9289a628ecc5 (queue type=1)
"""
import argparse
import json
import sys
import time

PROTO = "/Users/a1234/workspace/me/cok/COK-CN1-analysis/protocol"
sys.path.insert(0, PROTO)
from cok_client import CokClient  # noqa: E402
from cok_sfs import decode_params, parse_packet  # noqa: E402
import cok_account  # noqa: E402

KNOWN = {
    "200201": ("通用5分钟", "4600cedc8e8a43aeaa5aefba97b7bfa7"),
    "200247": ("造兵10分钟", "1de38e919ce743c1ad69fdebb45a11ba"),
    "200208": ("造兵2小时", "3757a02129df4a5ba8c25e59f3495678"),
    "200215": ("城建5分钟", "982b49d9c0fb4e8295f3beaa9843f982"),
}


def grab_init(c, wait=25.0):
    """登录后收 init 推送, 解密出 queue 列表(收帧要耐心, 推送可能延后到)"""
    c.sock.settimeout(3.0)
    buf = b""
    t0 = time.time()
    while time.time() - t0 < wait:
        try:
            ch = c.sock.recv(65536)
        except Exception:
            continue          # 超时只是暂时没数据, 继续等
        if not ch:
            break
        buf += ch
        i = 0
        while i + 3 <= len(buf):
            flags = buf[i]
            ln = (buf[i + 1] << 8) | buf[i + 2]
            if not (flags & 0x80) or ln == 0 or i + 3 + ln > len(buf):
                break
            fr = buf[i:i + 3 + ln]
            try:
                _, _, obj, _ = parse_packet(fr)
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
    ap.add_argument("--item", default="200201", help="道具模板 id")
    ap.add_argument("--count", type=int, default=1)
    ap.add_argument("--queue-type", type=int, default=1, help="队列 type(1=造兵)")
    ap.add_argument("--uuid", help="直接指定队列 uuid(默认从 init 推送里找)")
    ap.add_argument("--dry", action="store_true", help="只看不发")
    args = ap.parse_args()

    acct = cok_account.load_account()
    c = CokClient(account=acct, timeout=60.0)
    c.connect()
    c.login()

    qu = args.uuid
    init = grab_init(c)
    if init:
        qs = init.get("queue") or []
        print("[+] init 推送: queue %d 条" % len(qs))
        for q in qs:
            if not isinstance(q, dict):
                continue
            t = q.get("totalTime") or 0
            s = q.get("startTime") or 0
            tag = "进行中" if (t > 0 and s > 0) else ("已完成" if q.get("endTime") else "空闲")
            print("    type=%-4s qid=%-3s total=%-10s %-6s uuid=%s"
                  % (q.get("type"), q.get("qid"), t, tag, q.get("uuid")))
        if not qu:
            for q in qs:
                if (q.get("totalTime") or 0) > 0 and (q.get("startTime") or 0) > 0 \
                        and q.get("type") == args.queue_type:
                    qu = q.get("uuid")
                    print("[+] 选中进行中的 type=%s 队列: %s" % (args.queue_type, qu))
                    break
    else:
        print("[!] 未收到 init 推送")

    name, inst = KNOWN.get(args.item, ("?", None))
    if inst is None:
        print("[!] 未知道具 %s" % args.item)
        return 1
    if not qu:
        print("[!] 没有进行中的队列可用")
        return 2

    params = {
        "qUUID": qu,
        "itemUUID": inst,
        "isGold": 0,
        "itemCount": args.count,
    }
    print("\n=== queue.ccd (道具加速) ===")
    print("  道具 %s (%s) 实例 uuid=%s  数量=%d" % (args.item, name, inst, args.count))
    print("  队列 uuid=%s" % qu)
    print("  params:", json.dumps(params, ensure_ascii=False))
    if args.dry:
        return 0
    try:
        r = c.call("queue.ccd", params, retries=1)
        p = r.get("__params__") or r
        print("  响应:", json.dumps(p, ensure_ascii=False)[:500])
        if p.get("finished"):
            print("  ✅ 加速成功(finished=true)")
        elif p.get("errorCode"):
            print("  ⚠️  业务错误:", p.get("errorCode"))
    except Exception as e:
        print("  ERR", str(e)[:160])
    return 0


if __name__ == "__main__":
    sys.exit(main())
