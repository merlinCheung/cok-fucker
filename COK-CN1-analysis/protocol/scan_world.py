#!/usr/bin/env python3
"""COK 全图扫描: 把整个区服的玩家坐标扫进本地索引。

用 `world.get` 批量接口(每次覆盖约 24×24 格), 步进扫完整张 1201×1201 地图。
零消耗(不耗道具/资源/体力)。

特点:
  * **断点续扫**: 进度写进索引 meta, 中断后接着扫, 不会白跑
  * **独立进程**: 不会因为控制台重启而中断
  * **实时进度**: 每 N 次请求打印一次, 并把索引落盘
  * **账号锁**: 全程持有跨进程账号锁, 避免和 App / 网页控制台互踢

用法:
  python3 scan_world.py                       # 扫全图
  python3 scan_world.py --radius 100          # 只扫自己周围 100 格
  python3 scan_world.py --max-requests 200    # 只扫 200 次(试跑)
  python3 scan_world.py --out other.json      # 换索引文件
  python3 scan_world.py --resume              # 从上次中断处继续
"""
import argparse
import json
import os
import re
import signal
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import cok_client  # noqa: E402
import cok_map  # noqa: E402

#: NPC 名字形如 "Empire01a8c#2223" —— 以 #<数字> 结尾的都是 NPC/怪物城
_NPC_RE = re.compile(r"#\d+$")


def fmt_dur(sec):
    sec = int(sec)
    if sec < 60:
        return "%d 秒" % sec
    if sec < 3600:
        return "%d 分 %d 秒" % (sec // 60, sec % 60)
    return "%d 时 %d 分" % (sec // 3600, (sec % 3600) // 60)


def stop_app():
    """把手机上的游戏 App 停掉。

    同账号只允许一个连接 —— App 在线时, 我们的连接会被服务端主动断开。
    网页控制台的"自动打怪"也是这么做的。
    """
    try:
        import subprocess as _sp
        r = _sp.run(["adb", "shell", "am", "force-stop",
                     "com.hcg.cok.nearme.gamecenter"],
                    capture_output=True, timeout=15)
        return r.returncode == 0
    except Exception:  # noqa: BLE001
        return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=cok_map.DEFAULT_INDEX, help="索引文件")
    ap.add_argument("--radius", type=int, default=0,
                    help="只扫自己周围 N 格(0 = 全图)")
    ap.add_argument("--step", type=int, default=cok_map.STEP)
    ap.add_argument("--max-requests", type=int, default=0,
                    help="本次最多请求数(0 = 不限)")
    ap.add_argument("--resume", action="store_true", help="从索引记录的断点继续")
    ap.add_argument("--server", type=int, default=2223)
    ap.add_argument("--keep-app", action="store_true",
                    help="不要停掉手机上的游戏 App(同账号双连接会被服务端互踢)")
    args = ap.parse_args()

    index = cok_map.load_index(args.out)
    meta = index.get("meta") or {}

    # ---- 扫描身份: pid 文件 + 历史记录(网页据此显示"扫描中"和历史) ----
    run_id = time.strftime("%Y%m%d-%H%M%S")
    cok_map.write_scan_pid(os.getpid())

    def _on_term(signum, frame):
        # 抛异常让 scan_area 的 finally 收尾(写断点 + meta), 再由外层记历史
        raise KeyboardInterrupt

    try:
        signal.signal(signal.SIGTERM, _on_term)
        signal.signal(signal.SIGINT, _on_term)
    except (ValueError, OSError):
        pass

    cok_map.record_scan({
        "id": run_id,
        "started_at": int(time.time()),
        "status": "running",
        "index": os.path.abspath(args.out),
        "step": args.step,
        "server_id": args.server,
        "radius": args.radius or 0,
    })

    def _finish_history(status):
        """把这次扫描的结果写进历史(正常结束/被中断都走这里)。"""
        idx = cok_map.load_index(args.out)
        m = idx.get("meta") or {}
        players = idx.get("players") or {}
        real_n = sum(1 for v in players.values()
                     if not _NPC_RE.search(str(v.get("name") or "")))
        cok_map.record_scan({
            "id": run_id,
            "finished_at": int(time.time()),
            "status": status,
            "requests_done": int(m.get("requests_done") or 0),
            "requests_total": int(m.get("requests_total") or 0),
            "players": len(players),
            "real_players": real_n,
            "npc": len(players) - real_n,
            "errors": int(m.get("errors") or 0),
            # 健康指标: 错位(响应与请求对不上)和越界点剔除 —— 这两个数大 = 数据不可信
            "mismatched_responses": int(m.get("mismatched_responses") or 0),
            "dropped_out_of_range": int(m.get("dropped_out_of_range") or 0),
            "self_point": m.get("self_point") or {},
        })
        cok_map.clear_scan_pid()

    # 自己的 uid(用于自动记录自己坐标)
    own_uid = str((cok_client.ACCOUNT or {}).get("gameUid") or "")
    try:
        from cok_account import load_account as _la
        acc = _la() or {}
        own_uid = str(acc.get("gameUid") or own_uid)
    except Exception:
        pass

    # 中心点: 用索引里记录的 self_point(扫描时自动记录的, 不写死坐标)
    # ⚠️ 先读本次的索引, 再退回正式索引 —— 不能写成 for/else, 那样
    # args.out == DEFAULT_INDEX 时会直接 break, 永远读到 (0,0)。
    cx = cy = 0
    sp = (meta.get("self_point") or {})
    if sp.get("x") is not None:
        cx, cy = int(sp["x"]), int(sp["y"])
    else:
        for path in (args.out, cok_map.DEFAULT_INDEX):
            try:
                m = (cok_map.load_index(path).get("meta") or {})
            except Exception:
                continue
            sp2 = m.get("self_point") or {}
            if sp2.get("x") is not None:
                cx, cy = int(sp2["x"]), int(sp2["y"])
                break
    if args.radius:
        x0 = max(0, cx - args.radius)
        y0 = max(0, cy - args.radius)
        x1 = min(cok_map.WORLD_SIZE - 1, cx + args.radius)
        y1 = min(cok_map.WORLD_SIZE - 1, cy + args.radius)
        if cx == 0 and cy == 0:
            print("[!] 还没有自己的坐标, 先跑一次小范围扫描定位", flush=True)
    else:
        x0 = y0 = 0
        x1 = y1 = cok_map.WORLD_SIZE - 1

    # 断点续扫
    if args.resume and meta.get("partial") and meta.get("next_x") is not None:
        x0 = int(meta["next_x"])
        y0 = int(meta["next_y"])
        print("[*] 从断点继续: x=%d y=%d" % (x0, y0), flush=True)

    total = ((x1 - x0) // args.step + 1) ** 2
    print("=" * 68, flush=True)
    print("  COK 全图扫描", flush=True)
    print("  区域: x %d~%d  y %d~%d  步长 %d" % (x0, x1, y0, y1, args.step), flush=True)
    print("  预计请求数: %d  (约 %s)" % (
        total, fmt_dur(total * 0.2)), flush=True)
    print("  索引: %s" % args.out, flush=True)
    print("=" * 68, flush=True)

    t_start = time.time()
    last_print = 0.0

    # ⚠️ 必须先把手机上的游戏 App 停掉: 同账号只允许一个连接, App 在线时
    # 扫描器这条连接会被服务端主动断开(表现为"连接被服务端关闭(已收 0/3 字节)")。
    # 网页的"自动打怪"也是这么做的, 扫描器以前漏了这步 —— 害我误判成"配额"。
    if not args.keep_app:
        stopped = stop_app()
        print("  停 App: %s" % ("已停止" if stopped else "没找到/没权限(继续试)"), flush=True)
        time.sleep(1.5)

    def progress(px, py, st):
        nonlocal last_print
        now = time.time()
        if now - last_print < 5.0 and not st.get("done"):
            return
        last_print = now
        done = st["requests"]
        eta = (total - done) * 0.2
        print("  [%5d/%5d] 中心(%d,%d) 玩家 %d 新增 %d 索引 %d  剩余约 %s" % (
            done, total, px, py, st["players"], st["new"],
            len(index.get("players") or {}), fmt_dur(eta)), flush=True)
        # 实时落盘(扫描中也能查到已扫到的)
        meta2 = dict(index.get("meta") or {})
        meta2.update({"updated_at": int(time.time()), "partial": True,
                      "next_x": px, "next_y": py,
                      "scanning": True,
                      "requests_done": st["requests"],
                      "requests_total": total})
        index["meta"] = meta2
        cok_map.save_index(index, args.out)

    try:
        with cok_client.account_lock(timeout=120.0, purpose="scan-world"):
            c = cok_client.CokClient(timeout=60.0).connect()
            c.bin_handshake()
            c.login()
            try:
                c.call("cmd.ping")
            except Exception:
                pass
            # ⚠️ 新连接的第一条业务请求会被服务端丢弃 -> 补发一条把连接"热"起来
            # (用 cmd.ping 而不是 world.get.detail, 后者偶尔会挂到超时)
            try:
                c.call("cmd.ping")
            except Exception:
                pass
            try:
                st = cok_map.scan_area(
                    c, x0, y0, x1, y1, server_id=args.server, step=args.step,
                    index=index, path=args.out, progress=progress,
                    max_requests=args.max_requests or None, own_uid=own_uid)
            finally:
                c.close()
    except KeyboardInterrupt:
        print("\n[!] 被中断 —— 断点已保存, 下次加 --resume 可接着扫", flush=True)
        _finish_history("interrupted")
        return 130

    idx = cok_map.load_index(args.out)
    meta = idx.get("meta") or {}
    players = idx.get("players") or {}
    real_n = sum(1 for v in players.values()
                 if not _NPC_RE.search(str(v.get("name") or "")))
    # ---- 写扫描历史 ----
    _finish_history("interrupted" if meta.get("partial") else "completed")
    print("=" * 68, flush=True)
    print("  扫描完成", flush=True)
    print("  请求 %d 次, 耗时 %s" % (st["requests"], fmt_dur(st["elapsed"])), flush=True)
    print("  地块 %d, 玩家条目 %d, 新增 %d" % (
        st["tiles"], st["players"], st["new"]), flush=True)
    print("  索引总数: %d 名玩家(其中真实玩家 %d)" % (len(players), real_n), flush=True)
    if st.get("mismatched"):
        print("  ⚠️ 响应与请求对不上(已丢弃重发): %d 次" % st["mismatched"], flush=True)
    if meta.get("dropped_out_of_range"):
        print("  ⚠️ 剔除越界点(坐标不可信): %d 个" % meta["dropped_out_of_range"], flush=True)
    if st.get("errors"):
        print("  失败请求: %d" % st["errors"], flush=True)
    print("  索引文件: %s" % args.out, flush=True)
    print("=" * 68, flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
