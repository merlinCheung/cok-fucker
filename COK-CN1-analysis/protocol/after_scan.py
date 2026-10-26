#!/usr/bin/env python3
"""等全图扫描跑完, 然后: 复核坐标 -> 重新导出 -> 恢复自动打怪。

用法: python3 after_scan.py
"""
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import cok_map  # noqa: E402


def sh(cmd, timeout=600):
    print("\n$ %s" % " ".join(cmd), flush=True)
    try:
        p = subprocess.run(cmd, capture_output=True, text=True,
                           timeout=timeout, cwd=HERE)
        out = (p.stdout or "") + (p.stderr or "")
        print(out[-3000:], flush=True)
        return p.returncode, out
    except subprocess.TimeoutExpired:
        print("  (超时)", flush=True)
        return 1, ""


def main():
    print("等扫描结束…", flush=True)
    while True:
        pid = cok_map.read_scan_pid()
        alive = False
        if pid:
            try:
                os.kill(pid, 0)
                alive = True
            except OSError:
                alive = False
        if not alive:
            break
        time.sleep(30)

    idx = cok_map.load_index()
    meta = idx.get("meta") or {}
    print("扫描结束: 请求 %s/%s 玩家 %s 错位 %s 越界 %s 失败 %s" % (
        meta.get("requests_done"), meta.get("requests_total"),
        len(idx.get("players") or {}), meta.get("mismatched_responses"),
        meta.get("dropped_out_of_range"), meta.get("errors")), flush=True)

    # 1) 抽样复核
    sh([sys.executable, os.path.join(HERE, "verify_points.py"), "30"],
       timeout=900)
    # 2) 重新导出
    sh([sys.executable, os.path.join(HERE, "export_excel.py"),
        "--out", "cok-players.xlsx", "--csv", "--top", "10"])
    sh([sys.executable, os.path.join(HERE, "export_excel.py"),
        "--out", "cok-players-real.xlsx", "--real-only"])
    # 3) 恢复自动打怪
    try:
        import json
        import urllib.request
        token = open(os.path.join(HERE, ".cok-web-token")).read().strip()
        body = json.dumps({
            "action": "hunt", "op": "auto-start", "level": 15, "num": 5000,
            "maxKills": 30000, "squads": 4,
            "squadSpec": [
                {"army_id": "107012", "num": 20000},
                {"army_id": "107111", "num": 29000},
                {"army_id": "107009", "num": 8900},
                {"army_id": "107110", "num": 30000}]}).encode()
        req = urllib.request.Request(
            "http://127.0.0.1:8770/api/action?t=" + token, data=body,
            headers={"Content-Type": "application/json"})
        print("自动打怪:", urllib.request.urlopen(req, timeout=60).read().decode(),
              flush=True)
    except Exception as e:  # noqa: BLE001
        print("自动打怪未启动: %s" % e, flush=True)
    print("\n全部完成", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
