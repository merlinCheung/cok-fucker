#!/usr/bin/env python3
"""守候 world.get 配额恢复, 一旦进入"可连续请求"状态就启动慢速扫描。

背景: 2026-10-25 的全图扫描连续打了 10201 次 world.get, 把**账号级**配额
打爆了 —— 之后连打怪用的 res.tile.find 都会被服务端关连接。配额在慢慢恢复,
表现为"偶尔放行一次"。

本脚本:
  1. 每 60 秒试一次 world.get, 记录成功/失败
  2. 一旦**连续 3 次成功**, 说明进入可扫状态 -> 立刻启动慢速全图扫描
     (STEP=20 减少请求数, 每次请求都做响应回显校验 + drain, 不会写错坐标)
  3. 断点续扫: 中断后重跑本脚本会接着上次进度

用法:
  python3 wait_and_scan.py            # 守候 + 扫描
  python3 wait_and_scan.py --watch    # 只守候, 不扫描
"""
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import cok_client  # noqa: E402
import cok_map  # noqa: E402

I = cok_map._I
LOG = "/tmp/wait_and_scan.log"


def log(msg):
    line = "[%s] %s" % (time.strftime("%H:%M:%S"), msg)
    print(line, flush=True)
    try:
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except OSError:
        pass


def probe():
    """试一次 world.get。返回 True = 放行。"""
    try:
        c = cok_client.CokClient(timeout=20.0).connect()
        c.bin_handshake()
        c.login()
        for _ in range(2):
            try:
                c.call("cmd.ping")
            except Exception:
                pass
        try:
            r = c.call("world.get", {"x": I(531), "y": I(931), "type": I(0),
                                     "serverId": I(2223),
                                     "timeStamp": I(int(time.time()))})
            p = r.get("__params__") or {}
            n = len(cok_map._parse_points(p))
            return True, "地块 %d 回显(%s,%s)" % (n, p.get("x"), p.get("y"))
        finally:
            try:
                c.close()
            except Exception:
                pass
    except Exception as e:  # noqa: BLE001
        return False, str(e)[:60]


def main():
    watch_only = "--watch" in sys.argv
    log("=== 开始守候 world.get 配额 ===")
    streak = 0
    for i in range(240):
        ok, detail = probe()
        log("探测 %3d: %s  %s" % (i + 1, "放行" if ok else "被拒", detail))
        if ok:
            streak += 1
            if streak >= 3:
                log("连续 3 次放行 —— 配额已恢复")
                break
        else:
            streak = 0
        time.sleep(60)
    else:
        log("守候超时, 配额还没恢复")
        return 1
    if watch_only:
        return 0
    log("启动慢速全图扫描(STEP=20, 带响应校验)")
    # STEP=20: 覆盖区实测 x 中心-12~+8 (宽 21 格), 20 的步进几乎不漏也不重叠,
    # 请求数 3721, 比 STEP=12 的 10201 少 2.7 倍。
    cmd = [sys.executable, os.path.join(HERE, "scan_world.py"),
           "--out", cok_map.DEFAULT_INDEX, "--step", "20"]
    log("执行: %s" % " ".join(cmd))
    return subprocess.call(cmd)


if __name__ == "__main__":
    sys.exit(main())
