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
sys.path.insert(0, os.path.join(HERE, "..", "core"))

import cok_client  # noqa: E402
import cok_map  # noqa: E402
import cok_accounts as accounts  # noqa: E402

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


class _Args:
    """run_scan 的轻量参数容器(等价于 argparse.Namespace)。"""

    def __init__(self, **kw):
        self.__dict__.update(kw)


def run_scan(args, stop_event=None, install_signals=True,
             stop_app_fn=None, log=print):
    """执行一次扫描。CLI(独立进程)和安卓(进程内线程)共用这一份实现。

    args: 带以下字段的对象(见 _Args / argparse.Namespace):
      out, account_key, radius, step, max_requests, resume, server,
      keep_app, reconnect_every, delay, fresh
    stop_event: 可选 threading.Event —— 置位后在下一个中心点抛 KeyboardInterrupt
      优雅收尾(断点已随 progress 落盘)。安卓端没有信号可用, 靠它停止。
    install_signals: 是否注册 SIGTERM/SIGINT(只有主线程能注册; 工作线程传 False)。
    stop_app_fn: 可选"停游戏 App"实现。安卓端没有 adb, 传平台钩子(ActivityManager);
      不传则退回模块级 stop_app()(adb, 桌面端)。
    log: 进度/状态输出函数(默认 print; 安卓端可改成写日志文件)。
    """
    # ⚠️ 账号必须在读索引/定 --out **之前**确定下来:
    #   * account_key 给了 -> 用账号库的凭据, 并把数据目录隔离到该账号子目录
    #   * 没给           -> 沿用环境里的 COK_DATA_DIR(父进程网页已设好)或默认目录
    account = None
    if getattr(args, "account_key", None):
        account = accounts.get_account(args.account_key)
        if not account:
            log("[!] 账号库里没有 %s" % args.account_key)
            return 2
        cok_map.set_data_dir(accounts.data_dir(args.account_key))
    if getattr(args, "out", None) is None:
        args.out = cok_map.DEFAULT_INDEX

    # ⚠️ 全图重扫必须从**空白索引**开始: 旧索引里的坐标属于**上一次地图布局**
    # (服务端会重排地图), 混进新扫描后, 旧坐标的票数可能反而更多 ——
    # 众数投票就会选中原地不动的旧坐标(实测复核正确率只有 16.7%)。
    if args.fresh and os.path.exists(args.out):
        bak = "%s.bak-%s" % (args.out, time.strftime("%Y%m%d-%H%M%S"))
        try:
            os.replace(args.out, bak)
            log("  旧索引已归档: %s" % os.path.basename(bak))
        except OSError as e:
            log("  [!] 归档旧索引失败(继续): %s" % e)

    index = cok_map.load_index(args.out)
    meta = index.get("meta") or {}

    # ---- 扫描身份: pid 文件 + 历史记录(网页据此显示"扫描中"和历史) ----
    run_id = time.strftime("%Y%m%d-%H%M%S")
    cok_map.write_scan_pid(os.getpid())

    if install_signals:
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
    if account:
        # 指定了账号库账号 -> 直接用它的 gameUid, 不去读设备(设备上可能是别的号)
        own_uid = str(account.get("gameUid") or own_uid)
    else:
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
            log("[!] 还没有自己的坐标, 先跑一次小范围扫描定位")
    else:
        x0 = y0 = 0
        x1 = y1 = cok_map.WORLD_SIZE - 1

    # 断点续扫
    resume_y = None
    if args.resume and meta.get("partial") and meta.get("next_x") is not None:
        x0 = int(meta["next_x"])
        # ⚠️ 只把**第一列**的起点抬到断点 y, 后面每一列仍从 y0(=0) 开始 ——
        # 早先这里把 y0 也设成了 next_y, 那样会漏掉 "x>断点列 且 y<断点y" 的整片区域,
        # 而那部分**还没扫过**(日志会显示成 "区域: x 204~1200 y 432~1200")。
        resume_y = int(meta.get("next_y") or 0)
        log("[*] 从断点继续: x=%d, 第一列从 y=%d 开始(后续列从 y=%d 起)" % (
            x0, resume_y, y0))

    # ⚠️ 区域可能是长方形(续扫时), 必须是 列数 × 行数, 不能用平方
    total = ((x1 - x0) // args.step + 1) * ((y1 - y0) // args.step + 1)
    log("=" * 68)
    log("  COK 全图扫描")
    log("  区域: x %d~%d  y %d~%d  步长 %d" % (x0, x1, y0, y1, args.step))
    log("  预计请求数: %d  (约 %s)" % (total, fmt_dur(total * 0.2)))
    log("  索引: %s" % args.out)
    log("=" * 68)

    t_start = time.time()
    last_print = [0.0]

    # ⚠️ 必须先把手机上的游戏 App 停掉: 同账号只允许一个连接, App 在线时
    # 扫描器这条连接会被服务端主动断开(表现为"连接被服务端关闭(已收 0/3 字节)")。
    if not args.keep_app:
        stopper = stop_app_fn or stop_app
        try:
            stopped = bool(stopper(account.get("packageName")
                                   if account else None)) \
                if stop_app_fn else bool(stopper())
        except TypeError:
            # 平台钩子可能是无参/有参两种签名, 容错一下
            stopped = bool(stop_app_fn()) if stop_app_fn else bool(stop_app())
        except Exception:  # noqa: BLE001
            stopped = False
        log("  停 App: %s" % ("已停止" if stopped else "没找到/没权限(继续试)"))
        time.sleep(1.5)

    def _should_stop():
        return bool(stop_event is not None and stop_event.is_set())

    def progress(px, py, st):
        now = time.time()
        # 实时落盘(扫描中也能查到已扫到的), 并记录断点
        meta2 = dict(index.get("meta") or {})
        meta2.update({"updated_at": int(time.time()), "partial": True,
                      "next_x": px, "next_y": py,
                      "scanning": True,
                      "requests_done": st["requests"],
                      "requests_total": total})
        index["meta"] = meta2
        cok_map.save_index(index, args.out)
        if now - last_print[0] >= 5.0 or st.get("done"):
            last_print[0] = now
            done = st["requests"]
            eta = (total - done) * 0.2
            log("  [%5d/%5d] 中心(%d,%d) 玩家 %d 新增 %d 索引 %d  剩余约 %s" % (
                done, total, px, py, st["players"], st["new"],
                len(index.get("players") or {}), fmt_dur(eta)))
        # ⚠️ 协作式停止: 安卓端没有信号, 靠这里抛 KeyboardInterrupt ——
        # scan_area 的 finally 会把断点+meta 收尾, 外层 except 记"中断"历史。
        if _should_stop():
            raise KeyboardInterrupt

    def make_conn():
        """建一条干净连接(登录 + 预热)。"""
        # ⚠️ 超时要**短**(20 秒): 服务端偶尔会让某条请求既不返回也不断连,
        # 60 秒 × 4 次重试 = 卡 4 分钟才放弃。正常响应只要 0.2~1 秒。
        cc = cok_client.CokClient(timeout=20.0, account=account).connect()
        cc.bin_handshake()
        cc.login()
        # ⚠️ 新连接的第一条业务请求会被服务端丢弃 -> 补发一条把连接"热"起来
        for _ in range(2):
            try:
                cc.call("cmd.ping")
            except Exception:
                pass
        return cc

    try:
        # 多账号: 锁 key 用账号 id, 不同账号互不阻塞; 没指定账号则默认全局锁。
        with cok_client.account_lock(timeout=120.0, purpose="scan-world",
                                     key=args.account_key):
            c = make_conn()
            try:
                st = cok_map.scan_area(
                    c, x0, y0, x1, y1, server_id=args.server, step=args.step,
                    index=index, path=args.out, progress=progress,
                    max_requests=args.max_requests or None, own_uid=own_uid,
                    resume_y=resume_y,
                    reconnect=make_conn, reconnect_every=args.reconnect_every,
                    delay=args.delay)
            finally:
                c.close()
    except KeyboardInterrupt:
        log("\n[!] 被中断 —— 断点已保存, 下次续扫可接着扫")
        _finish_history("interrupted")
        return 130
    except Exception as e:  # noqa: BLE001
        log("\n[!] 扫描出错: %s" % str(e)[:200])
        _finish_history("interrupted")
        return 1

    idx = cok_map.load_index(args.out)
    meta = idx.get("meta") or {}
    players = idx.get("players") or {}
    real_n = sum(1 for v in players.values()
                 if not _NPC_RE.search(str(v.get("name") or "")))
    # ---- 写扫描历史 ----
    _finish_history("interrupted" if meta.get("partial") else "completed")
    log("=" * 68)
    log("  扫描完成")
    log("  请求 %d 次, 耗时 %s" % (st["requests"], fmt_dur(st["elapsed"])))
    log("  地块 %d, 玩家条目 %d, 新增 %d" % (
        st["tiles"], st["players"], st["new"]))
    log("  索引总数: %d 名玩家(其中真实玩家 %d)" % (len(players), real_n))
    if st.get("mismatched"):
        log("  ⚠️ 响应与请求对不上(已丢弃重发): %d 次" % st["mismatched"])
    if meta.get("dropped_out_of_range"):
        log("  ⚠️ 剔除越界点(坐标不可信): %d 个" % meta["dropped_out_of_range"])
    if st.get("errors"):
        log("  失败请求: %d" % st["errors"])
    log("  索引文件: %s" % args.out)
    log("=" * 68)
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=None,
                    help="索引文件(默认用当前账号的数据目录下 map-index.json)")
    ap.add_argument("--account-key", default=None,
                    help="账号库里的账号 id(gameUid); 给了就用该账号连接并隔离数据目录")
    ap.add_argument("--radius", type=int, default=0,
                    help="只扫自己周围 N 格(0 = 全图)")
    ap.add_argument("--step", type=int, default=cok_map.STEP)
    ap.add_argument("--max-requests", type=int, default=0,
                    help="本次最多请求数(0 = 不限)")
    ap.add_argument("--resume", action="store_true", help="从索引记录的断点继续")
    ap.add_argument("--server", type=int, default=2223)
    ap.add_argument("--keep-app", action="store_true",
                    help="不要停掉手机上的游戏 App(同账号双连接会被服务端互踢)")
    ap.add_argument("--reconnect-every", type=int, default=200,
                    help="每 N 个中心重连一次(看门狗, 0 = 不重连)")
    ap.add_argument("--delay", type=float, default=0.0,
                    help="每个中心之间的额外停顿秒数(限速, 避免服务端降速)")
    ap.add_argument("--fresh", action="store_true",
                    help="全图重扫: 归档旧索引并从空白索引开始(旧数据属于"
                         "上一次地图布局, 混进来会让众数投票选错)")
    args = ap.parse_args()

    def _p(msg):
        print(msg, flush=True)

    # CLI(独立进程)直接走共享实现: 装信号处理器、用 adb 停 App。
    return run_scan(args, stop_event=None, install_signals=True,
                    stop_app_fn=None, log=_p)


if __name__ == "__main__":
    raise SystemExit(main())
