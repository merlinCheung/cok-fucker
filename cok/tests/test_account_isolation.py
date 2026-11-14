#!/usr/bin/env python3
"""多账号**独立存活**回归测试(不连游戏服、不连设备)。

背景: 用户报的两个 bug ——
  1) 多个账号隔离没做好, 没法独立存活;
  2) 后台运行不生效。
根因(全部在真机上/真代码里复现过):
  A. **锁退化成一把**: `cok_client.lock_file_for()` 曾经"只要环境变量
     `COK_ACCOUNT_LOCK_FILE` 设了就无条件返回它、忽略 key"。桌面端没事,
     **安卓端**(`android_entry.py` 会设这个变量)于是所有账号共用一把锁 ⇒
     五个号排队, 后台"同时在线"是假的。
  B. **cok_rally 注册表是进程级全局**: `_KNOWN` / `_CURSOR` / `REGISTRY_FILE`
     都是模块级变量, 并行引擎互相覆盖 ⇒ A 号扫到的怪写进 B 号的列表/文件。
  C. **cok_map 数据目录是进程级全局**: `_apply_account_meta()` 里调
     `cok_map.set_data_dir()`, 后解析的账号赢 ⇒ 索引文件互相覆盖。
  D. **autoPoll 读的是"账号还没定下来时的全局配置"**: `Engine.__init__` 里
     `self.settings = self._load_settings()` 跑在 `account_key` 赋值之前,
     读到的是全局 `web-settings.json`; 用户在 A 号关掉"后台轮询" ⇒ 全局变
     False ⇒ **其它账号**的引擎一起停摆(它们的独立配置里其实是 True)。
  E. **后台守护只覆盖"当前在看的账号"**: 安卓 `BackgroundMonitorService` /
     页面「立即刷新」都只发引擎级的 `refresh-now`。

本测试逐条锁死 A/B/C/D/E 的不变量, 全部离线。

跑法:
    python3 test_account_isolation.py
"""

import argparse
import json
import os
import shutil
import sys
import tempfile
import threading
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "core"))
sys.path.insert(0, os.path.join(HERE, "..", "tools"))

_TMP = tempfile.mkdtemp(prefix="cok-isolation-test-")
os.environ["COK_ACCOUNTS_DIR"] = os.path.join(_TMP, "accounts")
os.environ["COK_DATA_ROOT"] = os.path.join(_TMP, "data")
# ⚠️ 必须**先**清掉, 再让需要它的用例自己设(否则测不到"设了会怎样")。
os.environ.pop("COK_ACCOUNT_LOCK_FILE", None)

import cok_accounts as accounts  # noqa: E402
import cok_client  # noqa: E402
import cok_map  # noqa: E402
import cok_rally  # noqa: E402
import cok_web  # noqa: E402

PASS = 0
FAIL = 0


def check(cond, name, extra=""):
    global PASS, FAIL
    tag = "[PASS]" if cond else "[FAIL]"
    if cond:
        PASS += 1
    else:
        FAIL += 1
    print("%s %s%s" % (tag, name, ("  — " + extra) if extra else ""))


def _try_lock(key, timeout=0.0):
    """另一个线程里尝试抢某账号的锁, 返回是否抢到。"""
    got = {"ok": None}

    def run():
        try:
            with cok_client.account_lock(timeout=timeout, purpose="probe", key=key):
                got["ok"] = True
        except cok_client.AccountBusy:
            got["ok"] = False
    t = threading.Thread(target=run)
    t.start()
    t.join()
    return got["ok"]


# ---------------------------------------------------------------- A. 锁
def test_lock_isolation():
    print("[A] 账号锁: 不同账号必须各拿各的(含安卓端设了 COK_ACCOUNT_LOCK_FILE 的情况)")

    # A1) 不设环境变量: 两个账号两个文件
    a, b = "111100002223", "222200002223"
    pa, pb = cok_client.lock_file_for(a), cok_client.lock_file_for(b)
    check(pa != pb, "不同账号锁文件不同", "%s vs %s" % (pa, pb))
    check(pa.endswith(".cok-account-%s.lock" % a), "分键锁文件名带 uid", pa)

    with cok_client.account_lock(timeout=0.0, purpose="hold-A", key=a):
        check(_try_lock(a) is False, "同账号 A 被占时其它线程抢不到")
        check(_try_lock(b) is True, "不同账号 B 不受 A 占用影响(可并行)")

    # A2) **安卓端形态**: 设了 COK_ACCOUNT_LOCK_FILE。
    #     旧代码这里会让 a / b 拿到同一个文件 ⇒ 退化成单账号。
    lock_dir = os.path.join(_TMP, "lockdir")
    os.environ["COK_ACCOUNT_LOCK_FILE"] = lock_dir
    try:
        pa2, pb2 = cok_client.lock_file_for(a), cok_client.lock_file_for(b)
        check(pa2 != pb2, "设了 COK_ACCOUNT_LOCK_FILE 时仍按 uid 分文件",
              "%s vs %s" % (pa2, pb2))
        check(os.path.dirname(pa2) == lock_dir, "锁落在覆盖目录里", pa2)
        check(os.path.isdir(lock_dir), "锁目录不存在时会被自动创建", lock_dir)
        with cok_client.account_lock(timeout=0.0, purpose="hold-A", key=a):
            check(_try_lock(a) is False, "覆盖目录下: 同账号仍互斥")
            check(_try_lock(b) is True, "覆盖目录下: 不同账号仍并行")
        # 无 key 时仍然用覆盖的那个文件(测试隔离语义不变)
        check(cok_client.lock_file_for(None) == lock_dir,
              "无 key 时仍回退到覆盖的单文件", cok_client.lock_file_for(None))
    finally:
        os.environ.pop("COK_ACCOUNT_LOCK_FILE", None)

    # A3) 同一账号跨线程仍然互斥(不能为了并行把互斥也拆了)
    with cok_client.account_lock(timeout=0.0, purpose="hold-A", key=a):
        check(_try_lock(a) is False, "同账号(跨线程)依然互斥")


# ---------------------------------------------------------------- B. rally
class FakeClient(object):
    """假客户端: world.get 返回预设地块, 并记录调用。"""

    def __init__(self, tiles=None, rally_list=None):
        self.tiles = tiles or []
        self.rally_list = rally_list or []
        self.calls = []

    def call(self, cmd, params=None, retries=1):
        self.calls.append(cmd)
        if cmd == "world.get":
            return {"__params__": {"points": [
                json.dumps(t) for t in self.tiles]}}
        if cmd == "alliance.team.ls":
            return {"__params__": {"list": self.rally_list, "helplist": []}}
        if cmd == "login.dataconfig":
            return {"__params__": {"dataConfig": {"world_rally": {
                "k1": "5", "k2": "10", "k3": "30", "k4": "60"}}}}
        raise AssertionError("未预期的命令 %s" % cmd)


def boss_tile(index, monster="902113"):
    return {"t": 15, "i": index, "t1": monster, "mchp": 720000,
            "mmhp": 720000, "st": 1793573758, "rt": 1793660158}


def test_rally_isolation():
    print("[B] 巨型狮鹫注册表: 按 uid 隔离(不再共用 _KNOWN / _CURSOR / 落盘文件)")

    dir_a = os.path.join(_TMP, "uidA")
    dir_b = os.path.join(_TMP, "uidB")
    cok_rally.set_data_dir(dir_a, uid="A")
    cok_rally.set_data_dir(dir_b, uid="B")

    # B1) 注册表分桶
    cok_rally.scan_bosses(FakeClient(tiles=[boss_tile(1001)]),
                          slice_size=1, save=True, uid="A")
    check(len(cok_rally._known_for("A")) >= 1, "A 的注册表有数据",
          str(len(cok_rally._known_for("A"))))
    check(len(cok_rally._known_for("B")) == 0, "B 的注册表不受 A 影响",
          str(len(cok_rally._known_for("B"))))

    # B2) 落盘文件各写各的
    check(os.path.exists(os.path.join(dir_a, "boss-registry.json")),
          "A 的注册表落盘到自己的目录")
    check(not os.path.exists(os.path.join(dir_b, "boss-registry.json")),
          "B 的目录没有被 A 写脏")

    # B3) 游标分桶
    cur_a = cok_rally._cursor_for("A")
    check(cok_rally._cursor_for("B") == 0, "B 的游标不受 A 影响",
          str(cok_rally._cursor_for("B")))
    check(cur_a != 0, "A 的游标确实推进了", str(cur_a))

    # B4) scan 结果只含本账号扫到的怪(A 扫 2001, B 扫 3001, 互不串)
    r_a = cok_rally.scan_bosses(FakeClient(tiles=[boss_tile(2001)]),
                                slice_size=1, save=False, uid="A")
    r_b = cok_rally.scan_bosses(FakeClient(tiles=[boss_tile(3001)]),
                                slice_size=1, save=False, uid="B")
    idx_a = {b["index"] for b in r_a["new_bosses"]}
    idx_b = {b["index"] for b in r_b["new_bosses"]}
    check(2001 in idx_a and 3001 not in idx_a, "A 只看到自己扫到的",
          str(idx_a))
    check(3001 in idx_b and 2001 not in idx_b, "B 只看到自己扫到的",
          str(idx_b))

    # B5) 集结时长档位缓存按区服分桶(不同区服不同档, 不能互相污染)
    s1 = cok_rally.read_rally_slots(FakeClient(), server_id=2223)
    s2 = cok_rally.read_rally_slots(FakeClient(), server_id=2218)
    check(s1 == s2 and s1[0]["minutes"] == 5,
          "档位缓存按区服分开(默认档仍能读出)", str(s1))

    # B6) 老接口仍然可用(默认桶 == 原来的 _KNOWN)
    cok_rally._KNOWN.clear()
    cok_rally._merge_tiles([boss_tile(9001)], time.time())
    check(9001 in cok_rally._KNOWN, "老代码直接读写 _KNOWN 仍然生效")

    # B7) 默认桶(A 的桶除外)不受 uid 桶影响
    check(9001 not in cok_rally._known_for("A"),
          "默认桶与账号桶互不影响")


# ---------------------------------------------------------------- C. cok_map
def test_map_isolation():
    print("[C] 扫描索引目录: 并行引擎不再改进程全局 cok_map")

    before = cok_map.DEFAULT_INDEX
    eng = cok_web.Engine.__new__(cok_web.Engine)
    eng.pinned_key = "999900002223"
    eng.args = argparse.Namespace(account=None)
    eng.account_key = ""
    eng.account_label = ""
    eng.account_source = ""
    eng.account_note = ""
    eng.account_isolated = False
    eng._settings_account_key = ""
    eng.settings = {}
    eng.automation_state = {"rules": {}}
    eng.automation_history = []
    eng.task_stats = {}
    accounts.save_account({
        "gameUid": "999900002223", "roleName": "隔离测试号",
        "pfId": "x", "platformToken": "x", "deviceId": "x", "uuid": "x",
        "buildCode": "x", "signCode": "x"}, label="隔离测试号")
    eng._apply_account_meta(accounts.get_account("999900002223"), "账号库")
    check(eng.account_key == "999900002223", "账号已 settle", eng.account_key)
    check(cok_map.DEFAULT_INDEX == before,
          "**并行引擎不再改 cok_map 全局目录**", "%s -> %s" % (before, cok_map.DEFAULT_INDEX))
    check(cok_map.DATA_DIR == before.rsplit("/", 1)[0] if before else True,
          "cok_map.DATA_DIR 也未被改", str(cok_map.DATA_DIR))
    # 该引擎自己的索引路径仍指向自己的账号目录
    check("999900002223" in eng._index_path(), "引擎读写自己的索引路径",
          eng._index_path())
    check("999900002223" in eng._history_path(), "引擎读写自己的历史路径",
          eng._history_path())
    check("999900002223" in eng._pid_path(), "引擎读写自己的 pid 路径",
          eng._pid_path())
    # 注册表目录则按 uid 落到该账号目录
    reg_dir = cok_rally._dir_for("999900002223")
    check("999900002223" in reg_dir, "狮鹫注册表落到该账号目录", reg_dir)


# ---------------------------------------------------------------- D. autoPoll
class FakeDaemon(object):
    def __init__(self):
        self.client = None
        self.polled = 0
        self.shield_end_ms = 0
        self.alert = None

    def poll_once(self, on_state=None):
        self.polled += 1
        return True

    def emit(self, kind, payload):
        pass

    def ctx(self):
        return {}


def make_args(**over):
    a = argparse.Namespace(
        host="127.0.0.1", port=8770, account_device=True, account=None,
        interval=300, timeout=60.0, webhook=None, webhook_type="generic",
        alert_rules=[], autoshield=False,
        speedup_item="200201", speedup_count=1, speedup_queue_type=1,
        shield_slot=1, shield_cover_old=1, shield_cooldown=600.0,
        shield_trigger=[], shield_trigger_force=[], persistent=False,
        watch=[], once=False, retry_delay=10.0, claim=False, claim_limit=5,
        claim_max_total=20, auto_sign=False, speedup=False, speedup_gold=False,
        log=None, json=False,
    )
    for k, v in over.items():
        setattr(a, k, v)
    return a


def _make_engine(pinned, settings_file):
    eng = cok_web.Engine(make_args(), pinned_key=pinned)
    # ⚠️ SETTINGS_FILE 是**类属性**, 必须挂在类上(`_settings_file()` 里读的是
    #    self.SETTINGS_FILE, 实例上挂一份也行, 但这里统一改类, 跑完还原)。
    cok_web.Engine.SETTINGS_FILE = settings_file
    eng.settings = eng._load_settings()
    eng._settings_account_key = ""
    eng.daemon = FakeDaemon()
    eng._ensure_account = lambda: True
    eng.app_online = lambda: False
    eng.account_key = pinned
    eng.account_isolated = True
    return eng


def test_autopoll_per_account():
    print("[D] 后台轮询: autoPoll 归**账号**, A 号关掉不能带停 B 号")

    settings_file = os.path.join(_TMP, "web-settings.json")
    with open(settings_file, "w", encoding="utf-8") as f:
        json.dump({"autoPoll": False}, f)   # 全局: 关

    # 全局关掉的情况下, 账号 B 自己开着 ⇒ 必须仍然轮询
    eng_b = _make_engine("888800002223", settings_file)
    eng_b.settings["autoPoll"] = True
    eng_b._save_settings = lambda: None
    eng_b._settings_file = lambda: accounts.data_path("888800002223",
                                                      "automation-settings.json")
    check(eng_b.settings.get("autoPoll") is True,
          "账号 B 的独立配置是开的", str(eng_b.settings.get("autoPoll")))
    check(eng_b._settings_file() != settings_file,
          "账号 B 读的是自己的配置文件(不是全局)", eng_b._settings_file())

    # 没有独立配置的账号 ⇒ 继承全局(与改造前一致; 用**未登记**的 uid,
    # 未登记时引擎会走历史全局配置文件)
    eng_c = _make_engine("767676762223", settings_file)
    eng_c.account_isolated = False
    eng_c.account_key = "767676762223"
    eng_c.settings = eng_c._load_settings()
    check(eng_c.settings.get("autoPoll") is False,
          "未登记账号仍继承全局配置(兼容老用法)",
          str(eng_c.settings.get("autoPoll")))
    check(eng_c._settings_file() == settings_file,
          "未登记账号读的就是全局文件", eng_c._settings_file())

    # 真正的回归点: 全局 False + 账号 True ⇒ 该账号必须能轮询
    # (旧代码在 __init__ 里就读了全局, 于是一进循环就 continue, 永远不轮询)
    gate = {"reached": False}

    def fake_ensure():
        gate["reached"] = True
        return True

    eng_b._ensure_account = fake_ensure
    # 只跑一轮: 让循环判定一次 autoPoll 就停
    eng_b._poll_once = lambda: (True, "ok")
    eng_b._stop = threading.Event()
    orig_sleep = time.sleep
    try:
        calls = {"n": 0}

        def stop_after_poll(_s):
            calls["n"] += 1
            if calls["n"] >= 1:
                eng_b._stop.set()
        time.sleep = stop_after_poll
        eng_b._loop()
    finally:
        time.sleep = orig_sleep
    check(gate["reached"], "循环里先解析账号(autoPoll 用账号自己的配置)",
          str(gate))


# ---------------------------------------------------------------- E. refresh-all
class RecordingEngine(object):
    def __init__(self, args, pinned_key=None):
        self.pinned_key = pinned_key
        self.key = pinned_key or ""
        self.refreshed = 0
        self.hunter = None

    def start(self):
        pass

    def stop(self):
        pass

    def action(self, body):
        if (body or {}).get("action") == "refresh-now":
            self.refreshed += 1
            time.sleep(0.2)
            return {"ok": True, "note": "ok-%s" % self.key}
        return {"ok": False, "error": "未知"}

    def _overview_summary(self):
        return {"stale": True}


def test_refresh_all():
    print("[E] 后台运行: refresh-all 必须覆盖所有托管账号, 不是只刷当前在看的")

    real_engine = cok_web.Engine
    cok_web.Engine = RecordingEngine
    try:
        cok_web.EngineManager.PARALLEL_FILE = os.path.join(accounts.ACCOUNTS_DIR,
                                                          ".parallel")
        full = {"pfId": "x", "platformToken": "x", "deviceId": "x", "uuid": "x",
                "buildCode": "x", "signCode": "x"}
        for uid in ("555500002223", "888800002223", "767676762223"):
            accounts.save_account(dict(full, gameUid=uid, roleName=uid),
                                  label=uid)
        accounts.set_active_key("555500002223")   # 查看账号
        m = cok_web.EngineManager(make_args())
        m.start()
        m.set_parallel("888800002223", True)
        m.set_parallel("767676762223", True)
        want = set(m._desired_keys())
        check(len(want) == 3, "三个账号都在托管集里(并行 2 + 查看 1)",
              str(sorted(want)))
        # 并行发起: 每个号各 0.2s, 串行要 0.6s; 用耗时证明真的并行
        t0 = time.time()
        r = m.refresh_all()
        dt = time.time() - t0
        check(r.get("total") == len(want) and want <= set(r.get("results") or {}),
              "refresh-all 覆盖全部托管账号(并行集 ∪ 查看)",
              "%s vs %s" % (sorted(want), sorted(r.get("results") or {})))
        check(all(v.get("ok") for v in (r.get("results") or {}).values()),
              "每个账号都刷成功了", str(r.get("results")))
        check(dt < 0.2 * len(want) - 0.1,
              "并行执行(%d 个 × 0.2s 实际用了 %.2fs)"
              % (len(want), dt), "%.3fs" % dt)
        # 只刷当前查看账号 = 旧行为(后台不生效的那个)
        v = m.view_engine()
        v.refreshed = 0
        v.action({"action": "refresh-now"})
        check(v.refreshed == 1, "单引擎 refresh-now 仍然可用(手动刷新)")
        # 指定 keys 时只刷这些号
        r2 = m.refresh_all(["888800002223"])
        check(set(r2.get("results") or {}) == {"888800002223"},
              "可指定只刷某几个号", str(sorted(r2.get("results") or {})))
    finally:
        cok_web.Engine = real_engine


def main():
    try:
        test_lock_isolation()
        test_rally_isolation()
        test_map_isolation()
        test_autopoll_per_account()
        test_refresh_all()
    finally:
        shutil.rmtree(_TMP, ignore_errors=True)
    print()
    if FAIL:
        print("%d 通过, %d 失败" % (PASS, FAIL))
        return 1
    print("全部通过 (%d)" % PASS)
    return 0


if __name__ == "__main__":
    sys.exit(main())