#!/usr/bin/env python3
"""主号联盟捐献 —— 轮询守候 + 试捐。

背景: 251600 的研究周期在 2026-10-31 15:54:26 结束, 但盟主还没开下一个科技,
      所以 15:58 那次重测读到的科技树全是 startTime=0(没有在研目标) —— 没法捐。

本脚本: 在同一条连接上轮询 science.data.init, 等盟主开下一个科技
      (startTime>0 且 currentPro<needPro), 一旦出现立刻:
        1) al.science.fresh 拿捐献面板
        2) al.science.donate {scienceId, option} 依次试 option = 0/1/2/3
           第一个被接受的就是本服该档位的编码
        3) 再读一次科技树核对进度

换候选编码**只在回 E000000(参数无效)** 时进行; 其它错误码原样停, 避免捐错档。

用法:
  python3 retest_donate_poll.py --minutes 40
"""
import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.join(HERE, "..", "core"))
sys.path.insert(0, os.path.join(HERE, "..", "tools"))
from cok_client import CokClient, load_account  # noqa: E402
from cok_alliance import DONATE_STOP, _call, read_science  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ACCOUNT_UID = "<uid-main>"
ACCOUNT = os.path.join(HERE, "accounts", "%s.json" % ACCOUNT_UID)
OPTION_CANDIDATES = (0, 1, 2, 3)


def log(msg):
    print("[%s] %s" % (time.strftime("%H:%M:%S"), msg))
    sys.stdout.flush()


def connect():
    acc = load_account(ACCOUNT)
    c = CokClient(account=acc)
    c.connect()
    c.bin_handshake()
    c.login()
    try:
        c.call("cmd.ping")
    except Exception:  # noqa: BLE001
        pass
    return c


def pick_target(sci):
    """挑「正在研究且进度未满」的科技。

    直接按原始字段判定: startTime>0 (在研) 且 currentPro<needPro (没满)。
    不依赖 read_science 的 researching 标志 —— 那个标志要求 finishTime>now,
    服务端刚开研究、finishTime 还没填的时候会漏判。
    """
    for s in sci.get("list") or []:
        if s.get("startTime") and not s.get("full"):
            return s
    return None


def identify_tier(panel_params, resp_params, progress_delta=None):
    """反推"这次捐的是哪一档" -> 推出 option 编码基准。

    三级判定, 越往后越弱:
      1) 服务端响应里带 contribute/progress —— 直接跟面板该档的值对上
      2) 捐献前后科技进度增量 —— 跟面板该档的 progress 对上
      3) 面板里只有一档开放 —— 那必然就是它
    返回 (档位序号, 档位 key); 判不出来返回 (None, "")。
    """
    keys = ("low", "mid", "high")
    resp_params = resp_params or {}

    # 1) 响应里直接带档位数值
    for idx, key in enumerate(keys):
        for field in ("contribute", "progress"):
            want = panel_params.get(key + field.capitalize())
            got = resp_params.get(field)
            if want is not None and got is not None and int(want) == int(got):
                return idx, key

    # 2) 进度增量
    if progress_delta:
        for idx, key in enumerate(keys):
            want = panel_params.get(key + "Progress")
            if want is not None and int(want) == int(progress_delta):
                return idx, key

    # 3) 面板里只有一档开放
    open_keys = []
    for key in keys:
        av = panel_params.get(key + "Available")
        if av is None or av == 1 or av is True:
            open_keys.append(key)
    if len(open_keys) == 1:
        return keys.index(open_keys[0]), open_keys[0]
    return None, ""


def try_donate(c, sid):
    """依次试 option=0/1/2/3, 返回 (accepted_option, tries)。

    换候选编码**只在 E000000(参数无效)** 时进行。
    E100160(冷却/状态不允许)是**可恢复**的 -> 等一会儿重试同一个 option,
    不换候选(换了也不会过, 还可能跨档位)。
    """
    tries = []
    for opt in OPTION_CANDIDATES:
        cd_retry = 0
        while True:
            ok, p, code, msg = _call(c, "al.science.donate",
                                     {"scienceId": int(sid), "option": opt})
            rec = {"option": opt, "ok": ok, "errorCode": code, "error": msg}
            if ok:
                rec["params"] = {k: v for k, v in p.items() if not k.startswith("_cok_")}
            tries.append(rec)
            log("  donate option=%-2s -> %s" % (opt, "✅ 接受" if ok else "拒绝 %s %s" % (code, msg)))
            if ok:
                return opt, tries
            if code == "E100160" and cd_retry < 3:
                # 冷却是可恢复的: 同档位等 60s 再试, 不换编码
                cd_retry += 1
                log("  (冷却 E100160, 60s 后重试同一档位, 第 %d 次)" % cd_retry)
                time.sleep(60)
                continue
            break
        if code != "E000000":
            log("  (非 E000000, 按规则停, 不换候选)")
            break
        time.sleep(0.4)
    return None, tries


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--minutes", type=float, default=40.0, help="最多守候分钟数")
    ap.add_argument("--interval", type=float, default=45.0, help="轮询间隔秒")
    args = ap.parse_args()

    # ⚠ 必须用**按账号**的锁(COK_ACCOUNT_LOCK_FILE 不要设), 这样网页控制台
    #   拿不到锁时会优雅跳过("账号正被占用"), 而不是跟本进程在游戏服上互踢。
    import cok_client
    try:
        with cok_client.account_lock(timeout=5.0, purpose="donate-poll",
                                     key=ACCOUNT_UID):
            run_watch(args)
    except cok_client.AccountBusy as e:
        log("账号正被占用, 本轮跳过: %s" % e)
        sys.exit(3)


def run_watch(args):
    deadline = time.time() + args.minutes * 60
    out = {"account": ACCOUNT_UID, "startedAt": time.strftime("%Y-%m-%d %H:%M:%S"),
           "poll": [], "tries": [], "acceptedOption": None, "target": None}

    c = connect()
    log("已连接, 开始守候 %.0f 分钟(每 %.0fs 查一次)" % (args.minutes, args.interval))

    last_state = None
    while time.time() < deadline:
        try:
            sci = read_science(c)
        except Exception as e:  # noqa: BLE001
            log("读科技失败(重连): %s" % str(e)[:120])
            try:
                c.close()
            except Exception:  # noqa: BLE001
                pass
            time.sleep(3)
            try:
                c = connect()
            except Exception as e2:  # noqa: BLE001
                log("重连也失败: %s" % str(e2)[:120])
                time.sleep(10)
                continue
            continue

        if not sci.get("ok"):
            log("science.data.init 返回错误 %s %s" % (sci.get("errorCode"), sci.get("error")))
            time.sleep(args.interval)
            continue

        target = pick_target(sci)
        researching = [s for s in (sci.get("list") or []) if s.get("startTime")]
        state = tuple(sorted((s["scienceId"], s["currentPro"], s["needPro"])
                             for s in researching))
        if state != last_state:
            desc = ", ".join("%s %s/%s%s" % (s["scienceId"], s["currentPro"], s["needPro"],
                                            "(满)" if s["full"] else "") for s in researching) or "无"
            log("在研状态: %s" % desc)
            last_state = state
        out["poll"].append({"t": time.strftime("%H:%M:%S"),
                            "researching": [s["scienceId"] for s in researching]})

        if target is None:
            time.sleep(args.interval)
            continue

        # ---- 有可捐目标 ----
        sid = target["scienceId"]
        log("★ 出现可捐目标 scienceId=%s 进度 %s/%s" % (sid, target["currentPro"], target["needPro"]))
        out["target"] = target

        ok, panel, code, msg = _call(c, "al.science.fresh", {"scienceId": int(sid)})
        out["panel"] = {"ok": ok, "errorCode": code, "error": msg,
                        "params": {k: v for k, v in panel.items() if not k.startswith("_cok_")}}
        log("面板: %s" % json.dumps(out["panel"]["params"], ensure_ascii=False)[:800])

        accepted, tries = try_donate(c, sid)
        out["tries"] = tries
        out["acceptedOption"] = accepted

        if accepted is not None:
            # 用响应里的贡献值/进度反推"这次捐的是哪一档" -> 推出 option 基准
            resp = {}
            for t in tries:
                if t.get("option") == accepted:
                    resp = t.get("params") or {}
            # 先读捐献后的进度(用来算增量 -> 反推档位)
            sci2 = read_science(c)
            after = None
            for s in (sci2.get("list") or []):
                if s["scienceId"] == sid:
                    after = s
                    out["after"] = s
                    log("  捐献后进度 %s/%s (之前 %s/%s)" % (
                        s["currentPro"], s["needPro"],
                        target["currentPro"], target["needPro"]))
            delta = None
            if after is not None:
                try:
                    delta = int(after["currentPro"]) - int(target["currentPro"])
                except (TypeError, ValueError):
                    delta = None
            tier_idx, tier_key = identify_tier(panel, resp, delta)
            out["tierIdentified"] = {"index": tier_idx, "key": tier_key,
                                     "progressDelta": delta}
            base = (accepted - tier_idx) if tier_idx is not None else None
            out["base"] = base
            log("★ 捐献成功 option=%d  进度增量=%s  命中档位=%s(第 %s 档)  ⇒ 基准=%s" % (
                accepted, delta, tier_key or "?", (tier_idx if tier_idx is not None else "?"),
                ("%d-based" % base) if base is not None else "未知"))
        else:
            last = tries[-1] if tries else {}
            stop = DONATE_STOP.get(str(last.get("errorCode") or ""), (False, ""))
            log("★ 仍然没捐出去: option=%s -> %s %s%s" % (
                last.get("option"), last.get("errorCode"), last.get("error"),
                (" (已达上限)" if stop[0] else "")))
            out["stopReason"] = stop[1] if stop[0] else ""
        break

    out["finishedAt"] = time.strftime("%Y-%m-%d %H:%M:%S")
    out["gaveUp"] = out["acceptedOption"] is None and not out["tries"]
    path = os.path.join(HERE, "evidence", "donate-poll-%s.json" % time.strftime("%Y%m%d-%H%M%S"))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    log("证据 -> %s" % path)

    # ---- 编码定死了 -> 自动落盘(DONATE_TIERS + ALLIANCE.md + 回归) ----
    base = out.get("base")
    if base in (0, 1) and out.get("target"):
        import subprocess
        cmd = [sys.executable, os.path.join(HERE, "apply_donate_encoding.py"),
               "--base", str(base), "--evidence", os.path.basename(path),
               "--science-id", str(out["target"].get("scienceId")),
               "--current", str(out["target"].get("currentPro")),
               "--need", str(out["target"].get("needPro"))]
        log("落盘: %s" % " ".join(cmd[1:]))
        try:
            p = subprocess.run(cmd, cwd=HERE, capture_output=True, text=True, timeout=180)
            log("落盘输出:\n%s" % ((p.stdout or "") + (p.stderr or ""))[:1500])
            out["applyRc"] = p.returncode
        except Exception as e:  # noqa: BLE001
            log("落盘失败: %s" % str(e)[:200])
            out["applyRc"] = -1

    try:
        c.close()
    except Exception:  # noqa: BLE001
        pass


if __name__ == "__main__":
    main()
