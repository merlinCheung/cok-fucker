#!/usr/bin/env python3
"""两个修复点的回归测试(不连游戏服, 零消耗)。

1. **安卓端"让出账号"**: 安卓设备上没有 adb, 桌面端 `adb shell am force-stop`
   永远失败 -> 游戏 App 继续占着账号 -> 同账号两条连接 -> 游戏服互踢 ->
   猎人的连接刚建立就被服务端关闭(2026-11-01 实测:
   hunt_start -> hunt_step(stamina) -> hunt_error("连接被服务端关闭(已收 0/3 字节)")),
   表现为"点自动打怪后立刻退出"。
   现在: 平台钩子(安卓端 ActivityManager.killBackgroundProcesses)优先,
   钩子不可用再退回 adb; 猎人连接被踢还会**自动重连**并给出可照做的提示。

2. **天空之境自动领奖记账**: 领奖成功后必须写 task-stats 事件账本,
   否则"今日/本周/本月"面板里永远看不到这一项。

跑法: python3 test_takeover_and_sky.py
"""
import json
import os
import sys
import tempfile
import threading
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "core"))
sys.path.insert(0, os.path.join(HERE, "..", "tools"))

_TMP = tempfile.mkdtemp(prefix="cok-takeover-test-")
os.environ["COK_ACCOUNTS_DIR"] = os.path.join(_TMP, "accounts")
os.environ["COK_DATA_ROOT"] = os.path.join(_TMP, "data")

import cok_hunt  # noqa: E402
import cok_sky  # noqa: E402
import cok_web  # noqa: E402

#: 抓真实的 Engine 类。test_engine_manager.py 会把 cok_web.Engine 换成假引擎
#: (而且不还原), 同进程里跑其它测试时 cok_web.Engine 已经不是原类了。
#: 这里在**导入期**抓一份, 之后只认它。
ENGINE = cok_web.Engine

PASS = 0
FAIL = 0


def check(cond, name, extra=""):
    global PASS, FAIL
    if cond:
        PASS += 1
    else:
        FAIL += 1
    print("%s %s%s" % ("[PASS]" if cond else "[FAIL]", name,
                       ("  — " + extra) if extra else ""))


def stub_engine(**over):
    """造一个最小引擎桩(不碰网络/磁盘)。"""
    eng = ENGINE.__new__(ENGINE)
    eng.settings = {"automationPaused": False, "automationMode": "execute"}
    eng.lock = threading.Lock()
    eng.op_lock = threading.RLock()
    eng.persistent = False
    eng.pinned_key = ""
    eng._settings_account_key = "<uid-guopan-intl>"
    eng.automation_state = {"rules": {}}
    eng.phase = ""
    eng.states = {}
    eng.hunt = {}
    eng.shield_state = {}
    eng.dock_state = {}
    eng.welfare_state = {}
    eng.score_state = {}
    eng.alliance_state = {}
    eng.assist_state = {}
    eng.disconnected = False
    eng.connected = False
    eng.last_error = None
    eng.account_error = ""
    eng.account_source = ""
    eng.account_key = "<uid-guopan-intl>"
    eng.account_label = "测试号"
    eng.account_isolated = False
    eng.hunter = None
    eng.hunter_client = None
    eng.hunter_thread = None
    eng._hunter_starting = False
    eng.app_yield = False
    eng._suspend_poll = False
    eng.names = {"items": {"1001": "钢"}}
    eng.sky_disabled = False
    eng.sky_state = {}
    eng.task_stats = {"events": []}
    eng.automation_state = {"rules": {}}
    eng.automation_history = []
    eng.last_poll = 0.0
    eng.args = type("A", (), {"interval": 300, "account": {}})()
    eng._save_task_stats = lambda: None
    eng._save_automation_history = lambda: None
    eng._automation_record = lambda *a, **k: None
    for k, v in over.items():
        setattr(eng, k, v)
    return eng


class FakeDaemon(object):
    def __init__(self, date="2026-11-01"):
        self._ctx = {"date": date}
        self.events = []

    def ctx(self):
        return dict(self._ctx)

    def emit(self, kind, payload):
        self.events.append((kind, payload))


# ---------------- 1. 停 App: 平台钩子优先, adb 兜底 ----------------

def test_stop_app_hook():
    """安卓端: 没有 adb, 必须靠平台钩子把游戏 App 停掉。"""
    calls = []

    def hook(package):
        calls.append(package)
        return True

    cok_web.set_platform_stop_app(hook)
    try:
        eng = stub_engine()
        eng.args = type("A", (), {"account": {"packageName": "com.hcg.cok.ewanqf.guopan"}})()
        eng._app_stopped = False
        ok = eng.stop_app()
        check(ok is True, "平台钩子成功时 stop_app 返回 True")
        check(calls == ["com.hcg.cok.ewanqf.guopan"],
              "钩子拿到的是**账号自己的**包名(不是固定 nearme 包)", str(calls))
        check(eng._app_stopped is True, "成功后记下 _app_stopped")
    finally:
        cok_web.set_platform_stop_app(None)


def test_stop_app_hook_failure_falls_back():
    """钩子失败 -> 退回 adb(桌面端路径)。"""
    # 造一个假的 adb: 记录参数并返回 0
    fake = os.path.join(_TMP, "fake-adb")
    with open(fake, "w") as f:
        f.write("#!/bin/sh\necho \"$@\" >> %s\nexit 0\n" % os.path.join(_TMP, "adb.log"))
    os.chmod(fake, 0o755)

    def hook(package):
        return False

    old = cok_web.ADB_CANDIDATES
    cok_web.set_platform_stop_app(hook)
    cok_web.ADB_CANDIDATES = [fake]
    try:
        eng = stub_engine()
        eng.args = type("A", (), {"account": {"packageName": "com.hcg.cok.nearme.gamecenter"}})()
        eng._app_stopped = False
        ok = eng.stop_app()
        check(ok is True, "钩子失败时退回 adb 并成功")
        log = os.path.join(_TMP, "adb.log")
        body = open(log).read() if os.path.exists(log) else ""
        check("am force-stop com.hcg.cok.nearme.gamecenter" in body,
              "adb 收到的是 force-stop + 账号包名", body.strip())
    finally:
        cok_web.ADB_CANDIDATES = old
        cok_web.set_platform_stop_app(None)


def test_stop_app_nothing_available():
    """两条路都不可用 -> 明确 False(上层据此提示"可能被互踢")。"""
    old = cok_web.ADB_CANDIDATES
    cok_web.ADB_CANDIDATES = [os.path.join(_TMP, "does-not-exist")]
    try:
        eng = stub_engine()
        eng.args = type("A", (), {"account": {}})()
        eng._app_stopped = True
        ok = eng.stop_app()
        check(ok is False, "没有钩子也没有 adb 时返回 False")
        check(eng._app_stopped is False, "失败时清掉 _app_stopped 标记")
    finally:
        cok_web.ADB_CANDIDATES = old


# ---------------- 2. 猎人: 连接被踢后自动重连 ----------------

def test_hunter_reconnect_swaps_client():
    """连接被踢 -> 调 on_reconnect 重建连接并继续打怪。"""
    seen = []
    emitted = []
    new_client = object()

    def on_reconnect(old):
        seen.append(old)
        return new_client

    h = cok_hunt.AutoHunter(client=object(), on_reconnect=on_reconnect, max_reconnects=2)
    h.on_event = lambda kind, payload: emitted.append(kind)
    got = h._try_reconnect()
    check(got is new_client, "重连成功返回新 client")
    check(h.client is new_client, "猎人换上了新 client")
    check(h._reconnects == 1, "重连计数 +1")
    check(len(seen) == 1 and seen[0] is not new_client,
          "回调收到的是旧 client")
    check("reconnect" in emitted, "重连过程发事件", str(emitted))


def test_hunter_reconnect_bounded():
    """重连次数有上限, 且回调抛异常时按失败处理。"""
    def boom(old):
        raise RuntimeError("连不上")

    h = cok_hunt.AutoHunter(client=object(), on_reconnect=boom, max_reconnects=1)
    check(h._try_reconnect() is None, "回调抛异常 -> 救不回来")
    check(h._reconnects == 1, "失败也计入次数")

    h2 = cok_hunt.AutoHunter(client=object(), on_reconnect=lambda o: object(),
                              max_reconnects=2)
    h2._try_reconnect()
    h2._try_reconnect()
    check(h2._try_reconnect() is None, "超过上限后不再重连")
    check(h2._reconnects == 2, "次数封顶在 max_reconnects")


def test_hunter_no_reconnect_hook():
    """没配 on_reconnect -> 维持老行为(立刻停, 把账号还回去)。"""
    h = cok_hunt.AutoHunter(client=object())
    check(h._try_reconnect() is None, "没有 on_reconnect 时返回 None")


def test_fatal_conn_error_recognized():
    """服务端关连接的错误串必须被认出来(否则不会走重连)。"""
    check(cok_hunt._is_fatal_conn_error("连接被服务端关闭（已收 0/3 字节）"),
          "认得出'连接被服务端关闭'")
    check(cok_hunt._is_fatal_conn_error("ConnectionReset by peer"),
          "认得出 ConnectionReset")
    check(not cok_hunt._is_fatal_conn_error("体力不足"),
          "普通业务错误不会被当成断连")


# ---------------- 3. 天空之境: 领奖要记账 ----------------

def test_sky_auto_reward_records_task():
    """自动领奖成功 -> 写 task-stats 事件账本(kind=sky_reward, source=auto)。"""
    orig_read, orig_get = cok_sky.read_sky, cok_sky.get_reward
    calls = {"get": 0}

    def fake_read(cli, family=None, **kw):
        return {"ok": True, "family": "newHeaven", "can_reward": True,
                "state": 1, "curPower": 999999}

    def fake_get(cli, family=None, **kw):
        calls["get"] += 1
        return {"ok": True, "count": 2,
                "rewards": [{"itemId": "1001", "count": 5000}]}

    cok_sky.read_sky = fake_read
    cok_sky.get_reward = fake_get
    try:
        eng = stub_engine()
        eng.settings["skyAutoReward"] = True
        eng.settings["skyAutoExplore"] = False
        eng.daemon = FakeDaemon()
        eng._sky_tick(client=object())
        events = eng.task_stats["events"]
        check(len(events) == 1, "自动领奖写了 1 条事件", json.dumps(events, ensure_ascii=False))
        if events:
            ev = events[0]
            check(ev["kind"] == "sky_reward", "事件 kind 是 sky_reward", ev["kind"])
            check(ev["count"] == 2, "数量取服务端给的 count", str(ev["count"]))
            check(ev["source"] == "auto", "来源标记为 auto", ev["source"])
            check("钢" in ev["detail"], "明细里带奖励中文名", ev["detail"])
            check(ev["day"] == "2026-11-01", "按服务器日期归档到 day", ev["day"])
            check(ev["month"] == "2026-11", "按服务器日期归档到 month", ev["month"])
    finally:
        cok_sky.read_sky, cok_sky.get_reward = orig_read, orig_get


def test_sky_manual_reward_records_task():
    """手动领奖成功 -> 同样要记账(source=manual)。"""
    orig_get, orig_read = cok_sky.get_reward, cok_sky.read_sky

    def fake_get(cli, family=None, **kw):
        return {"ok": True, "count": 1,
                "rewards": [{"itemId": "1001", "count": 100}]}

    def fake_read(cli, family=None, **kw):
        return {"ok": True, "family": "newHeaven", "state": 0}

    cok_sky.get_reward = fake_get
    cok_sky.read_sky = fake_read
    try:
        eng = stub_engine()
        eng.daemon = FakeDaemon()
        eng.daemon.client = object()
        body = {"action": "sky", "op": "reward"}   # 后端读的是 "op"(安卓端也发 "op")
        try:
            eng.action(body)
        except Exception as e:  # noqa: BLE001
            print("    [调试] action 抛异常: %r" % (e,))
        events = eng.task_stats["events"]
        check(len(events) == 1, "手动领奖写了 1 条事件", json.dumps(events, ensure_ascii=False))
        if events:
            check(events[0]["kind"] == "sky_reward", "手动领奖 kind 是 sky_reward")
            check(events[0]["source"] == "manual", "手动领奖来源是 manual",
                  events[0]["source"])
    finally:
        cok_sky.get_reward = orig_get
        cok_sky.read_sky = orig_read


def test_sky_reward_label():
    """统计面板要有中文名(否则安卓端显示的是原始 key)。"""
    eng = stub_engine()
    eng.daemon = FakeDaemon()
    eng.task_stats["events"] = [{
        "at": 0, "kind": "sky_reward", "count": 1, "detail": "天空之境 钢 ×1",
        "source": "auto", "day": "2026-11-01", "week": "2026-W44", "month": "2026-11",
    }]
    view = eng._task_stats_view()
    rows = view["periods"]["day"]["breakdown"]
    check(len(rows) == 1, "今日统计里出现 1 行", json.dumps(rows, ensure_ascii=False))
    if rows:
        check(rows[0]["label"] == "天空之境探索奖励",
              "行标题是中文名", rows[0]["label"])
        check(rows[0]["count"] == 1, "计数正确", str(rows[0]["count"]))
        check(view["periods"]["month"]["total"] == 1, "本月统计也记上了")
        check(view["periods"]["week"]["total"] == 1, "本周统计也记上了")


def test_sky_manual_explore_records_task():
    """手动探索成功 -> 记一条 sky_explore 事件(探索有资源成本, 记发起次数)。"""
    orig_explore, orig_read = cok_sky.explore, cok_sky.read_sky

    def fake_explore(cli, num=None, family=None, allowed_counts=None, **kw):
        return {"ok": True, "num": num or 1, "family": "newHeaven"}

    def fake_read(cli, family=None, **kw):
        return {"ok": True, "family": "newHeaven", "state": 1,
                "allowedExploreCounts": [1, 5]}

    cok_sky.explore = fake_explore
    cok_sky.read_sky = fake_read
    try:
        eng = stub_engine()
        eng.daemon = FakeDaemon()
        eng.daemon.client = object()
        eng.action({"action": "sky", "op": "explore", "num": 1})
        events = eng.task_stats["events"]
        check(len(events) == 1, "手动探索写了 1 条事件", json.dumps(events, ensure_ascii=False))
        if events:
            check(events[0]["kind"] == "sky_explore", "手动探索 kind 是 sky_explore",
                  events[0]["kind"])
            check(events[0]["source"] == "manual", "手动探索来源是 manual",
                  events[0]["source"])
    finally:
        cok_sky.explore = orig_explore
        cok_sky.read_sky = orig_read


def test_sky_explore_label():
    """探索统计也要有中文名(否则面板显示原始 key)。"""
    eng = stub_engine()
    eng.daemon = FakeDaemon()
    eng.task_stats["events"] = [{
        "at": 0, "kind": "sky_explore", "count": 3, "detail": "天空之境探索 3 次",
        "source": "manual", "day": "2026-11-01", "week": "2026-W44", "month": "2026-11",
    }]
    view = eng._task_stats_view()
    rows = view["periods"]["day"]["breakdown"]
    check(len(rows) == 1, "今日统计里出现 1 行", json.dumps(rows, ensure_ascii=False))
    if rows:
        check(rows[0]["label"] == "天空之境探索", "行标题是中文名", rows[0]["label"])
        check(rows[0]["count"] == 3, "计数正确", str(rows[0]["count"]))


def test_overview_summary_shapes():
    """多账号总览摘要: 只读内存, 字段齐全, 不触发任何网络操作。"""
    eng = stub_engine()
    eng.daemon = FakeDaemon()
    eng._server_now_ms = lambda: 1_000_000
    eng.last_ok_poll = 0.0   # 从没成功过 -> stale=False(用 bool(last_ok) 守卫)
    eng.daemon.shield_end_ms = 1_000_000 + 60_000   # 还有 60 秒罩
    eng.dock_state = {"rewardable": [{"a": 1}, {"a": 2}]}
    eng.welfare_state = {"daily_gift": {"ok": True, "freeRewarded": False}}
    s = eng._overview_summary()
    check(s["has_shield"] is True, "有罩时 has_shield=True")
    check(s["shield_ms"] == 60_000, "罩剩余毫秒正确", str(s["shield_ms"]))
    check(s["dock_rewardable"] == 2, "港口待领计数正确", str(s["dock_rewardable"]))
    check(s["welfare_claimable"] is True, "每日好礼可领时 welfare_claimable=True")
    check(s["hunting"] is False, "未打怪时 hunting=False")
    check(s["stale"] is False, "从没成功轮询时不误报 stale")
    # 久无响应: 有过成功轮询, 但已超过 10 分钟
    eng.last_ok_poll = time.time() - 700
    check(eng._overview_summary()["stale"] is True, "超过 10 分钟无成功轮询标记 stale")


def main():
    test_stop_app_hook()
    test_stop_app_hook_failure_falls_back()
    test_stop_app_nothing_available()
    test_hunter_reconnect_swaps_client()
    test_hunter_reconnect_bounded()
    test_hunter_no_reconnect_hook()
    test_fatal_conn_error_recognized()
    test_sky_auto_reward_records_task()
    test_sky_manual_reward_records_task()
    test_sky_reward_label()
    test_sky_manual_explore_records_task()
    test_sky_explore_label()
    test_overview_summary_shapes()
    print()
    if FAIL:
        print("%d 通过, %d 失败" % (PASS, FAIL))
        return 1
    print("全部通过 (%d)" % PASS)
    return 0


if __name__ == "__main__":
    sys.exit(main())
