#!/usr/bin/env python3
"""主号联盟捐献重测。

流程(严格照 cron 任务):
  1) science.data.init -> 找 **正在研究** 且 **进度未满** 的联盟科技
     (currentPro < needPro 且 startTime > 0)
  2) 找到 -> al.science.fresh 拿捐献面板
  3) al.science.donate {scienceId, option} 依次试 option = 0/1/2/3
     第一次被接受的就是本服该档位的编码
  4) 没找到 -> 只报告状态, 不做任何写操作

⚠ 换候选编码**只在服务端回 E000000(参数无效)** 时进行;
  其它错误码(冷却 E100160 / 已满 E100126 / 权限)原样停, 避免捐错档白花钱。
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.join(HERE, "..", "core"))
sys.path.insert(0, os.path.join(HERE, "..", "tools"))
from cok_client import CokClient, load_account  # noqa: E402
from cok_alliance import (  # noqa: E402
    DONATE_TIERS, DONATE_STOP, _call, _int, read_science,
)

HERE = os.path.dirname(os.path.abspath(__file__))
ACCOUNT = os.path.join(HERE, "accounts", "<uid-main>.json")
OPTION_CANDIDATES = (0, 1, 2, 3)


def main():
    acc = load_account(ACCOUNT)
    print("== 账号 gameUid=%s pfId=%s" % (acc.get("gameUid"), str(acc.get("pfId"))[:24]))

    c = CokClient(account=acc)
    c.connect()
    c.bin_handshake()
    c.login()
    try:
        c.call("cmd.ping")
    except Exception:  # noqa: BLE001
        pass

    out = {"account": acc.get("gameUid"), "startedAt": time.strftime("%Y-%m-%d %H:%M:%S"),
           "steps": []}

    # ---- 1) 科技状态 ----
    sci = read_science(c)
    if not sci.get("ok"):
        print("!! science.data.init 失败: %s %s" % (sci.get("errorCode"), sci.get("error")))
        out["steps"].append({"step": "science", "ok": False,
                              "errorCode": sci.get("errorCode"), "error": sci.get("error")})
        c.close()
        _dump(out)
        return
    print("\n== 联盟科技树 ==")
    for s in sci.get("list") or []:
        flag = ""
        if s.get("researching"):
            flag = "  <== 在研"
        if s.get("full"):
            flag += "  (满进度)"
        print("  %-8s lv%-3s star%-2s  %8s/%-8s start=%s finish=%s%s" % (
            s.get("scienceId"), s.get("level"), s.get("star"),
            s.get("currentPro"), s.get("needPro"),
            s.get("startTime"), s.get("finishTime"), flag))
    out["science"] = sci

    # ---- 2) 找"在研且未满"的目标 ----
    target = None
    for s in sci.get("list") or []:
        if s.get("researching") and not s.get("full"):
            target = s
            break
    if target is None:
        researching = [s for s in (sci.get("list") or []) if s.get("researching")]
        print("\n== 结论: 没有可捐目标 ==")
        if researching:
            s = researching[0]
            print("  在研科技 %s 进度 %s/%s(满) -> 服务端会回 E100126, 捐不了"
                  % (s.get("scienceId"), s.get("currentPro"), s.get("needPro")))
        else:
            print("  当前没有正在研究的联盟科技(盟主还没开下一个)")
        out["steps"].append({"step": "target", "ok": False,
                             "reason": "no donateable target",
                             "researching": [s.get("scienceId") for s in researching]})
        _dump(out)
        c.close()
        return

    sid = target["scienceId"]
    print("\n== 找到可捐目标: scienceId=%s 进度 %s/%s ==" % (
        sid, target.get("currentPro"), target.get("needPro")))

    # ---- 3) 捐献面板 ----
    ok, panel_p, code, msg = _call(c, "al.science.fresh", {"scienceId": int(sid)})
    print("\n== al.science.fresh (scienceId=%s) ok=%s %s ==" % (sid, ok, code or ""))
    if ok:
        keys = [k for k in panel_p.keys() if not k.startswith("_cok_")]
        for k in sorted(keys):
            print("   %-18s %s" % (k, panel_p.get(k)))
    else:
        print("   %s" % msg)
    out["panel"] = {"ok": ok, "errorCode": code, "error": msg,
                    "params": {k: v for k, v in panel_p.items() if not k.startswith("_cok_")}}

    # ---- 4) 依次试 option ----
    print("\n== al.science.donate 试 option = %s ==" % (list(OPTION_CANDIDATES),))
    tries = []
    accepted = None
    for opt in OPTION_CANDIDATES:
        ok2, p2, code2, msg2 = _call(c, "al.science.donate",
                                     {"scienceId": int(sid), "option": opt})
        rec = {"option": opt, "ok": ok2, "errorCode": code2, "error": msg2}
        if ok2:
            rec["params"] = {k: v for k, v in p2.items() if not k.startswith("_cok_")}
        tries.append(rec)
        print("  option=%-2s -> %s %s" % (opt, "✅ 接受" if ok2 else "拒绝",
                                         "" if ok2 else "%s %s" % (code2, msg2)))
        if ok2:
            accepted = opt
            break
        if code2 != "E000000":
            print("     (非 E000000, 按规则停下, 不换候选)")
            break
        time.sleep(0.4)

    out["tries"] = tries
    out["acceptedOption"] = accepted

    # ---- 5) 结论 ----
    if accepted is not None:
        tier_idx = {0: 0, 1: 1, 2: 2, 3: 2}
        base = accepted - tier_idx[accepted]
        print("\n== 结论 ==")
        print("  低档 option = %d" % accepted)
        print("  ⇒ 本服 option 基准 = %s" % ("0-based" if base == 0 else "1-based"))
        print("  ⇒ 低档=%d 中档=%d 高档=%d" % (accepted, accepted + 1, accepted + 2))
        # 复核: 读一次科技树看进度有没有涨
        sci2 = read_science(c)
        if sci2.get("ok"):
            for s in sci2.get("list") or []:
                if s.get("scienceId") == sid:
                    print("  捐献后进度: %s/%s (之前 %s/%s)" % (
                        s.get("currentPro"), s.get("needPro"),
                        target.get("currentPro"), target.get("needPro")))
                    out["after"] = s
    else:
        last = tries[-1] if tries else {}
        print("\n== 结论: 仍然没捐出去 ==")
        print("  最后一次: option=%s -> %s %s" % (
            last.get("option"), last.get("errorCode"), last.get("error")))
        stop = DONATE_STOP.get(str(last.get("errorCode") or ""), (False, ""))
        if stop[0]:
            print("  判定: 已达上限(%s)" % stop[1])
        out["stopReason"] = stop[1] if stop[0] else ""

    _dump(out)
    c.close()


def _dump(out):
    out["finishedAt"] = time.strftime("%Y-%m-%d %H:%M:%S")
    path = os.path.join(HERE, "evidence", "donate-retest-%s.json" %
                         time.strftime("%Y%m%d-%H%M%S"))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print("\n-> %s" % path)


if __name__ == "__main__":
    main()
