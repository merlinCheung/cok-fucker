#!/usr/bin/env python3
"""网页控制台并发回归测试(不连游戏服、不碰设备)。

覆盖两个真实踩过的坑:

1) **锁把页面堵死**
   早先 `_poll_once()` / `action()` 和 `snapshot()` 共用同一把锁, 而轮询/操作
   全程持锁做网络 I/O。于是只要有一轮轮询在跑, `/api/state` 就整个卡住
   (最长 60 秒), 页面表现为"按钮点了没反应"。
   现在锁分成两把:
     op_lock —— 串行化对游戏服的操作(含网络 I/O)
     lock   —— 只保护内存状态, 毫秒级持有
   本测试用**慢轮询**验证: 轮询进行中, snapshot()/set-setting 仍然秒回。

2) **设置写丢**
   设置必须落盘(web-settings.json), 且并发写入不能乱序覆盖
   (前端连续输入会并发 POST, 迟到的旧值不能盖掉新值)。

跑法:
    python3 test_web_concurrency.py
"""

import argparse
import json
import os
import shutil
import sys
import tempfile
import subprocess
import threading
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

# 测试用**独立**的账号锁文件, 否则会跟正在运行的网页控制台抢同一个账号
os.environ['COK_ACCOUNT_LOCK_FILE'] = os.path.join(
    tempfile.gettempdir(), 'cok-test-account-%d.lock' % os.getpid())
import cok_web  # noqa: E402
import cok_client  # noqa: E402
import cok_map  # noqa: E402


def make_args(**over):
    """造一份最小可用的 args(字段与 cok_web.main() 的默认值对齐)。"""
    a = argparse.Namespace(
        host="127.0.0.1", port=8770, account_device=True, account=None,
        interval=300, timeout=60.0, webhook=None, webhook_type="generic",
        alert_rules=list(cok_web.D.ALL_RULES), autoshield=False,
        speedup_item="200201", speedup_count=1, speedup_queue_type=1,
        shield_slot=1, shield_cover_old=1, shield_cooldown=600.0,
        shield_trigger=[], shield_trigger_force=[], persistent=False,
        watch=list(cok_web.D.WATCHERS.keys()), once=False, retry_delay=10.0,
        claim=False, claim_limit=5, claim_max_total=20, auto_sign=False,
        speedup=False, speedup_gold=False, log=None, json=False,
    )
    for k, v in over.items():
        setattr(a, k, v)
    return a


class FakeDaemon(object):
    """假 daemon: poll_once 故意慢, 用来模拟"网络 I/O 期间页面被堵"。"""

    def __init__(self, args, delay=3.0):
        self.args = args
        self.delay = delay
        self.client = None
        self.last_state = {"buildQueue": {"金币": 12345}}
        self.queues = []
        self.shield_end_ms = 0
        self.alert = cok_web.D.Alert(None, "generic", list(cok_web.D.ALL_RULES))
        self.polling = threading.Event()

    def ctx(self):
        return {"today": 1, "month": 1, "now": 0, "date": "2026-01-01"}

    def poll_once(self):
        self.polling.set()
        time.sleep(self.delay)

    def connect(self):
        self.client = object()

    def auto_sign(self, ctx):
        pass

    def autoshield(self, ctx):
        pass

    def emit(self, kind, payload):
        pass


def check(name, cond, detail=""):
    mark = "PASS" if cond else "FAIL"
    print("[%s] %s%s" % (mark, name, ("  — " + detail) if detail else ""))
    return bool(cond)


def main():
    ok = True
    tmp = tempfile.mkdtemp(prefix="cokweb-test-")
    settings_file = os.path.join(tmp, "web-settings.json")
    try:
        # 让 Engine 把设置写进临时目录, 不污染真实配置
        cok_web.Engine.SETTINGS_FILE = settings_file

        args = make_args()
        eng = cok_web.Engine(args)
        eng.daemon = FakeDaemon(args, delay=3.0)
        # 隔离外部依赖: 本测试不连设备、不连游戏服
        eng._ensure_account = lambda: True
        eng.app_online = lambda: False

        # --- 1) 慢轮询期间 snapshot 必须秒回 ---
        t = threading.Thread(target=eng._poll_once)
        t.start()
        # 等轮询真的进入 sleep
        deadline = time.time() + 5
        while not eng.daemon.polling.is_set() and time.time() < deadline:
            time.sleep(0.02)
        ok &= check("轮询已进入网络阶段", eng.daemon.polling.is_set())

        t0 = time.time()
        snap = eng.snapshot()
        dt = time.time() - t0
        ok &= check("轮询期间 /api/state 不被堵死",
                    dt < 0.5 and snap is not None,
                    "耗时 %.3fs" % dt)

        # --- 2) 轮询期间设置写入仍然可用 ---
        t0 = time.time()
        r = eng.action({"action": "set-setting", "key": "lvLow", "value": 3,
                        "seq": 10})
        dt2 = time.time() - t0
        ok &= check("轮询期间保存设置不阻塞",
                    dt2 < 0.5 and r.get("ok") is True, "耗时 %.3fs" % dt2)

        # ⚠️ 必须先等第一条慢轮询结束: 它持有**跨进程账号锁**,
        # 后面第 8 项的慢轮询会拿不到锁直接跳过, 测不出互斥
        t.join(timeout=15)
        ok &= check("第一条慢轮询已结束", not t.is_alive())

        # --- 3) 设置落盘 ---
        with open(settings_file, encoding="utf-8") as f:
            saved = json.load(f)
        ok &= check("设置已落盘 web-settings.json",
                    saved.get("lvLow") == 3, json.dumps(saved, ensure_ascii=False))

        # --- 4) 序号守卫: 迟到的旧写入不能覆盖新值 ---
        eng.action({"action": "set-setting", "key": "lvLow", "value": 9, "seq": 20})
        r = eng.action({"action": "set-setting", "key": "lvLow", "value": 1, "seq": 15})
        ok &= check("乱序写入被序号挡住(旧值不覆盖新值)",
                    eng.settings.get("lvLow") == 9 and "忽略" in (r.get("note") or ""),
                    "现值=%r note=%r" % (eng.settings.get("lvLow"), r.get("note")))

        # --- 5) snapshot 带出 settings, 页面刷新后能回填 ---
        snap2 = eng.snapshot()
        ok &= check("snapshot 带出 settings(前端可回填)",
                    snap2.get("settings", {}).get("lvLow") == 9,
                    json.dumps(snap2.get("settings"), ensure_ascii=False))

        # --- 6) snapshot 里 autoSign/autoPoll 是顶层字段, 不是藏在 shield 里 ---
        ok &= check("autoSign/autoPoll 在 snapshot 顶层",
                    "autoSign" in snap2 and "autoPoll" in snap2
                    and "autoSign" not in (snap2.get("shield") or {}),
                    "shield=%r" % (snap2.get("shield"),))

        # --- 7) 账号缺失时给出明确原因, 而不是去连游戏服 ---
        eng2 = cok_web.Engine(make_args())
        eng2.daemon = FakeDaemon(make_args())
        eng2.app_online = lambda: False
        eng2._ensure_account = lambda: False   # 模拟"设备没连上"
        eng2.account_error = "设备未连接, 读不到账号"
        ok2, note = eng2._poll_once()
        ok &= check("设备未连接时不连游戏服且给出原因",
                    (not ok2) and "设备未连接" in note, note)

        # --- 9) 账号锁: 同进程嵌套可重入(网页 action() 持锁时, 里面的
        #            _hunter_start 要继续持有锁到打怪结束) ---
        with cok_client.account_lock(timeout=0.0, purpose="outer"):
            ok_nested = True
            try:
                with cok_client.account_lock(timeout=0.0, purpose="inner"):
                    pass
            except cok_client.AccountBusy:
                ok_nested = False
            ok &= check("同进程嵌套取锁不报占用", ok_nested)
            ok &= check("嵌套期间锁仍被持有",
                        cok_client.account_is_busy(), "account_is_busy")
        ok &= check("最外层退出后锁已释放",
                    not cok_client.account_is_busy(), "account_is_busy")

        # --- 9b) 账号锁: 可重入**只对同线程**成立 ---
        # 分线程判定是必须的: 计数是进程级的, 不分线程的话后台轮询线程
        # 会误以为自己拿到了独占权, 于是和打怪线程同时连游戏服 -> 服务端互踢。
        res = {}

        def _other_thread():
            try:
                with cok_client.account_lock(timeout=0.0, purpose="other"):
                    res["got"] = True
            except cok_client.AccountBusy:
                res["got"] = False

        with cok_client.account_lock(timeout=0.0, purpose="main-thread"):
            t = threading.Thread(target=_other_thread)
            t.start()
            t.join()
        ok &= check("另一线程在锁内取锁会被拒(不能假装独占)",
                    res.get("got") is False, json.dumps(res))
        res.clear()
        t = threading.Thread(target=_other_thread)
        t.start()
        t.join()
        ok &= check("锁释放后另一线程能取到锁",
                    res.get("got") is True, json.dumps(res))
        ok &= check("释放后锁文件不留占用者痕迹",
                    cok_client.account_holder() == "",
                    repr(cok_client.account_holder()))

        # --- 9c) 查玩家: 索引命中后要用一次 world.get 验证坐标是否还有效 ---
        # 服务端会重排地图/响应会错位, 索引里的坐标可能失效(原位置换成别人)。
        # 所以命中索引后必须验证一次, 否则会把过期坐标当成答案。
        fake_idx = {"players": {"u1": {"name": "元气少女李逵", "index": 553484,
                                        "x": 1023, "y": 460, "level": 30,
                                        "seen_at": int(time.time())}},
                    "meta": {"updated_at": int(time.time())}}
        orig = (cok_web.cok_map.load_index, cok_web.cok_map.fetch_area,
                cok_web.cok_map.scan_area)
        try:
            cok_web.cok_map.load_index = lambda *a, **k: fake_idx
            eng.daemon.client = object()      # 有连接才会去验证
            # 1) 验证通过 -> 采用服务端给的最新坐标
            cok_web.cok_map.fetch_area = lambda c, x, y, **k: {
                "ok": True, "tiles": [],
                "players": [{"uid": "u1", "name": "元气少女李逵",
                             "index": 1118663, "x": 531, "y": 931, "level": 30}]}
            r = eng._locate_action({"name": "元气少女李逵"})
            ok &= check("索引命中且坐标仍有效 -> 走 index+verified",
                        r.get("source") == "index+verified", str(r.get("source")))
            ok &= check("返回的是服务端给的最新坐标而不是索引里的旧值",
                        bool(r.get("players")) and r["players"][0].get("x") == 531
                        and r["players"][0].get("y") == 931,
                        json.dumps(r.get("players"), ensure_ascii=False)[:120])
            # 2) 验证失败(地图已被重排) -> 降级到现场扫描
            cok_web.cok_map.fetch_area = lambda c, x, y, **k: {
                "ok": True, "tiles": [], "players": []}
            cok_web.cok_map.scan_area = lambda *a, **k: {
                "requests": 1, "tiles": 0, "players": 0, "new": 0,
                "errors": 0, "elapsed": 0.0}
            r2 = eng._locate_action({"name": "元气少女李逵"})
            ok &= check("索引坐标已失效 -> 降级到现场扫描",
                        r2.get("source") == "scan", str(r2.get("source")))
            ok &= check("降级时带 stale 标记",
                        r2.get("stale") is True, str(r2.get("stale")))
        finally:
            (cok_web.cok_map.load_index, cok_web.cok_map.fetch_area,
             cok_web.cok_map.scan_area) = orig

        # --- 9d) 全图扫描: 状态 / 历史 / 一键启动 ---
        # ⚠️ 必须隔离: 真实环境里可能正有扫描在跑, 而且**绝不能写真实索引** ——
        # 之前这条测试直接调 save_index(真实路径), 和扫描器抢同一个 .tmp 文件,
        # 把扫描器写崩、还把新索引覆盖回旧版本。
        orig_pid = cok_web.cok_map.read_scan_pid
        orig_write_pid = cok_web.cok_map.write_scan_pid
        orig_clear_pid = cok_web.cok_map.clear_scan_pid
        orig_load = cok_map.load_index
        orig_save = cok_map.save_index
        orig_popen = subprocess.Popen
        fake_store = {"players": {"u1": {"name": "A", "x": 1, "y": 2}},
                      "meta": {"scanning": False, "updated_at": int(time.time())}}
        cok_web.cok_map.read_scan_pid = lambda *a, **k: None
        cok_web.cok_map.write_scan_pid = lambda *a, **k: True
        cok_web.cok_map.clear_scan_pid = lambda *a, **k: True
        cok_map.load_index = lambda *a, **k: json.loads(json.dumps(fake_store))
        cok_map.save_index = lambda doc, path=None: fake_store.update(
            {"players": doc.get("players", {}), "meta": doc.get("meta", {})})
        # ⚠️ 绝不能真的启动扫描进程(会抢账号、还会写真实索引)
        class _FakePopen(object):
            def __init__(self, *a, **k):
                self.pid = -1
            def wait(self, *a, **k):
                return 0
        subprocess.Popen = _FakePopen
        try:
            st = eng._scan_status()
            ok &= check("扫描状态字段齐全",
                        all(k in st for k in ("running", "requests_done",
                                              "requests_total", "players",
                                              "mismatched", "dropped", "errors")),
                        json.dumps(st, ensure_ascii=False)[:160])
            ok &= check("没扫描时 running=False", st.get("running") is False,
                        str(st.get("running")))
            # 历史: 记录 / 同 id 更新不追加 / 倒序
            hist_file = os.path.join(tmp, "scan-history.json")
            cok_map.record_scan({"id": "t1", "started_at": 1000, "status": "running"},
                                 path=hist_file)
            cok_map.record_scan({"id": "t1", "status": "completed", "players": 7},
                                 path=hist_file)
            cok_map.record_scan({"id": "t2", "started_at": 2000, "status": "completed"},
                                 path=hist_file)
            h = cok_map.load_history(hist_file)
            ok &= check("历史按时间倒序",
                        [r.get("id") for r in h["runs"]][:2] == ["t2", "t1"],
                        str([r.get("id") for r in h["runs"]]))
            ok &= check("同 id 是更新而不是追加",
                        len([r for r in h["runs"] if r.get("id") == "t1"]) == 1,
                        str(len(h["runs"])))
            ok &= check("更新后的字段生效",
                        h["runs"][1].get("status") == "completed"
                        and h["runs"][1].get("players") == 7,
                        json.dumps(h["runs"][1], ensure_ascii=False))
            # 已经在跑时不允许再启动
            cok_web.cok_map.read_scan_pid = lambda *a, **k: os.getpid()
            fake_store["meta"]["scanning"] = True
            r3 = eng._scan_start({})
            ok &= check("扫描已在跑时拒绝重复启动",
                        r3.get("ok") is False and "已经在跑" in str(r3.get("error")),
                        str(r3.get("error")))
            ok &= check("测试没有碰真实索引文件",
                        orig_load is not None and "u1" in fake_store["players"],
                        str(list(fake_store["players"])))
        finally:
            (cok_web.cok_map.read_scan_pid, cok_web.cok_map.write_scan_pid,
             cok_web.cok_map.clear_scan_pid) = (orig_pid, orig_write_pid, orig_clear_pid)
            cok_map.load_index = orig_load
            cok_map.save_index = orig_save
            subprocess.Popen = orig_popen

        # --- 10) 等级范围归一化: 下限不能大于上限 ---
        eng.action({"action": "set-setting", "key": "lvLow", "value": 4, "seq": 30})
        ok &= check("下限在上限之内时原样保存",
                    eng.settings.get("lvLow") == 4 and eng.settings.get("lvHigh") == 9,
                    json.dumps({k: eng.settings.get(k) for k in ("lvLow", "lvHigh")}))
        eng.action({"action": "set-setting", "key": "lvHigh", "value": 2, "seq": 31})
        ok &= check("上限压到下限以下时两者一起归一化",
                    eng.settings.get("lvLow") == 2 and eng.settings.get("lvHigh") == 2,
                    json.dumps({k: eng.settings.get(k) for k in ("lvLow", "lvHigh")}))

        # --- 8) 碰游戏服的动作仍然互斥(不能为了不阻塞就把互斥也拆了) ---
        eng3 = cok_web.Engine(make_args())
        eng3.daemon = FakeDaemon(make_args(), delay=2.0)
        eng3._ensure_account = lambda: True
        eng3.app_online = lambda: False
        slow = threading.Thread(target=eng3._poll_once)
        slow.start()
        deadline = time.time() + 5
        while not eng3.daemon.polling.is_set() and time.time() < deadline:
            time.sleep(0.02)
        t0 = time.time()
        eng3.action({"action": "sign"})
        waited = time.time() - t0
        ok &= check("游戏服写操作仍互斥(等慢轮询结束)",
                    waited >= 1.0, "等待 %.3fs" % waited)
        slow.join(timeout=10)

        t.join(timeout=10)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print("\n%s" % ("全部通过" if ok else "存在失败项"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
