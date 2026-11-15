#!/usr/bin/env python3
"""「自动打怪启动后立刻被断开 → 自动停止」的回归测试(2026-11-14 修的 bug)。

## 现场

    hunt_start -> hunt_step(stamina) -> tx autoQueue.data seq=1  (16 秒无 rx)
    -> 另一条连接登录成功 -> hunt_error "连接被服务端关闭(已收 0/3 字节)"
    -> 重连 2 次用尽 -> hunt_stopped

`ss -tnp` 实测服务进程对同一个游戏服同时挂着两条 socket
(CLOSE-WAIT + ESTAB), 日志里多条 `seq=1` 的连接交错出现
⇒ **同一账号同时存在多条连接**, 服务端互踢。

## 根因

`Engine` 里同账号有**两条**连接:

  * `hunter_client` —— 猎人专用(`_hunter_open_client`)
  * `daemon.client` —— 网页轮询/推送监听的常驻连接

`_hunter_reconnect()` 只关了 `old_client`, **完全没关 `daemon.client`**,
于是重连出来的猎人连接一登录就和它互踢 —— 重连 2 次必然失败。

另外 `_hunter_open_client()` 用的是 `args.game_host/game_port`(启动参数),
账号入库后并不会回写 args ⇒ 不同区服(端口不同)会连到错误节点。

## 本测试锁住的行为

1. `_hunter_open_client` 的 (host, port) 必须**以账号库为准**, 不被 args 带偏
2. `_hunter_reconnect` 必须**先关 daemon.client 再关 old_client**, 两者都清干净
3. 重连失败时不能把半死连接留在 daemon 上(否则下一轮轮询会复用它)
4. 断开提示不再无条件甩锅给"游戏 App 可能仍在线"(服务器上根本没 adb)

跑法:
    python3 cok/tests/test_hunt_double_conn.py
"""

import argparse
import os
import sys
import tempfile
import threading

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "core"))
sys.path.insert(0, os.path.join(HERE, "..", "tools"))

_TMP = tempfile.mkdtemp(prefix="cok-hunt2conn-")
os.environ["COK_ACCOUNTS_DIR"] = os.path.join(_TMP, "accounts")
os.environ["COK_DATA_ROOT"] = os.path.join(_TMP, "data")
os.environ["COK_ACCOUNT_LOCK_FILE"] = os.path.join(_TMP, "locks")

import cok_accounts as accounts  # noqa: E402
import cok_client  # noqa: E402
import cok_web  # noqa: E402

FAILED = []


def check(name, cond, detail=""):
    print("  [%s] %s%s" % ("ok" if cond else "FAIL", name,
                           ("  <- " + detail) if (detail and not cond) else ""))
    if not cond:
        FAILED.append(name)
    return cond


class FakeClient(object):
    """只记录 close() 有没有被调用。"""

    def __init__(self, name="c", host="", port=0):
        self.name = name
        self.host = host
        self.port = port
        self.closed = False

    def close(self):
        self.closed = True


class FakeDaemon(object):
    def __init__(self, client=None):
        self.client = client
        self.events = []

    def emit(self, kind, payload):
        self.events.append((kind, payload))


def make_args(**over):
    a = argparse.Namespace(
        host="127.0.0.1", port=8791, account_device=True, account=None,
        interval=300, timeout=60.0, webhook=None, webhook_type="generic",
        alert_rules=[], autoshield=False, speedup_item="200201",
        speedup_count=1, speedup_queue_type=1, shield_slot=1,
        shield_cover_old=1, shield_cooldown=600.0, shield_trigger=[],
        shield_trigger_force=[], persistent=False, watch=[], once=False,
        retry_delay=10.0, claim=False, claim_limit=5, claim_max_total=20,
        auto_sign=False, speedup=False, speedup_gold=False, log=None,
        json=False,
        # ⚠️ 故意给**错误的**区服地址(模拟启动参数与账号库不一致)
        game_host="1.2.3.4", game_port=32231,
    )
    for k, v in over.items():
        setattr(a, k, v)
    return a


def stub_engine(**over):
    eng = cok_web.Engine.__new__(cok_web.Engine)
    eng.args = make_args()
    eng.lock = threading.RLock()
    eng.op_lock = threading.RLock()
    eng.account_key = ""
    eng.hunter_client = None
    eng.connected = True
    eng.daemon = FakeDaemon()
    eng._app_stopped = False
    eng.stop_app = lambda: False          # 服务器上没有 adb, 必然失败
    for k, v in over.items():
        setattr(eng, k, v)
    return eng


def seed_account(key, host, port):
    """把账号写进账号库(测试用的临时目录)。"""
    acc = {
        "gameUid": key, "pfId": "1000001", "zn": "COK2218",
        "host": host, "port": int(port),
        "uuid": "u-1", "deviceId": "d-1", "signCode": "s-1",
        "buildCode": "b-1", "baseActiveKey": "k-1",
    }
    accounts.save_account(acc)
    return accounts.get_account(key)


# ---------------- 1. host/port 以账号库为准 ----------------

def test_host_port_from_account_db():
    """args 给错端口时, 猎人连接必须用账号库的 host/port。"""
    key = "900000000000001"
    seed_account(key, "txaia-cok.elexapp.com", 32181)
    eng = stub_engine()
    eng.account_key = key
    eng.args.account = accounts.get_account(key)

    host, port = eng._hunter_host_port()
    check("账号库端口优先于 args.game_port", port == 32181, "port=%r" % port)
    check("账号库 host 优先于 args.game_host",
          host == "txaia-cok.elexapp.com", "host=%r" % host)


def test_host_port_falls_back_to_args():
    """没有账号库记录时, 退回 args(保持老行为, 不破坏单账号用法)。"""
    eng = stub_engine()
    eng.account_key = ""
    eng.args.account = None
    host, port = eng._hunter_host_port()
    check("无账号库记录 -> 用 args 的 host", host == "1.2.3.4", host)
    check("无账号库记录 -> 用 args 的 port", port == 32231, repr(port))


def test_host_port_bad_args_type():
    """args 里端口是脏数据(字符串/None)时不能抛异常。"""
    eng = stub_engine()
    eng.account_key = ""
    eng.args.account = None
    eng.args.game_port = "not-a-port"
    host, port = eng._hunter_host_port()
    check("脏端口数据不抛异常, 回退默认端口",
          port == cok_client.DEFAULT_PORT, repr(port))


# ---------------- 2. 重连必须先放掉两条连接 ----------------

def test_reconnect_drops_daemon_client():
    """★ 核心回归: 重连必须关掉 daemon.client(否则同账号双连接互踢)。"""
    eng = stub_engine()
    daemon_cli = FakeClient("daemon")
    old_cli = FakeClient("hunter-old")
    eng.daemon = FakeDaemon(daemon_cli)
    eng.hunter_client = old_cli
    eng.connected = True

    new_cli = FakeClient("hunter-new")
    opened = []

    def fake_open():
        opened.append(daemon_cli.closed)      # 建**新**连接时, 旧的必须已经关了
        return new_cli

    eng._hunter_open_client = fake_open
    got = eng._hunter_reconnect(old_cli)

    check("重连返回新连接", got is new_cli)
    check("旧猎人连接已关闭", old_cli.closed)
    check("★ 网页常驻连接已关闭(根因修复点)", daemon_cli.closed)
    check("建连前两条旧连接都已关闭", opened == [True], repr(opened))
    check("hunter_client 换成新连接", eng.hunter_client is new_cli)
    check("daemon.client 已清空(不会被下一轮轮询复用)",
          eng.daemon.client is None)
    check("connected 标记已复位", eng.connected is False)


def test_reconnect_failure_leaves_no_half_dead_client():
    """重连失败: 不能把半死连接留在 daemon 上(否则下一轮轮询复用它)。"""
    eng = stub_engine()
    daemon_cli = FakeClient("daemon")
    old_cli = FakeClient("hunter-old")
    eng.daemon = FakeDaemon(daemon_cli)
    eng.hunter_client = old_cli

    def boom():
        raise RuntimeError("连不上")

    eng._hunter_open_client = boom
    raised = ""
    try:
        eng._hunter_reconnect(old_cli)
    except Exception as e:  # noqa: BLE001
        raised = str(e)
    check("重连失败会抛异常给上层", "连不上" in raised, raised)
    check("失败后 daemon.client 仍是 None", eng.daemon.client is None)
    check("失败后旧连接已关", old_cli.closed and daemon_cli.closed)


def test_reconnect_with_no_old_client():
    """old_client 为 None(比如启动时就没连上)也要能正常重连。"""
    eng = stub_engine()
    daemon_cli = FakeClient("daemon")
    eng.daemon = FakeDaemon(daemon_cli)
    eng.hunter_client = None
    new_cli = FakeClient("hunter-new")
    eng._hunter_open_client = lambda: new_cli
    got = eng._hunter_reconnect(None)
    check("old_client=None 时也能重连", got is new_cli)
    check("old_client=None 时仍然关掉 daemon 那条", daemon_cli.closed)


# ---------------- 3. 断开提示不再甩锅 App ----------------

def test_stopped_note_not_blaming_app_on_server():
    """服务器上没有 adb, 提示不能再说"游戏 App 可能仍在线"。"""
    eng = stub_engine()
    eng._app_stopped = False
    eng.account_key = ""
    eng._hunt_kills_seen = 0
    eng._record_hunt_kills = lambda kills: None
    eng.daemon = FakeDaemon()

    body = {"level": 1, "num": 10}
    # 直接取 _hunter_start 里那个 emit 的行为不容易(它嵌在函数里),
    # 这里复刻同一条判定路径: 用 _hunter_start 的源码级不变量做断言。
    # ⇒ 改为直接检查 `_hunter_start` 的提示文案来源是否还依赖"App 在线"。
    import inspect
    src = inspect.getsource(cok_web.Engine._hunter_start)
    check("提示不再无条件说「游戏 App 可能仍在线」",
          "请先完全退出游戏 App 再开始打怪" not in src)
    check("提示给出真实排查方向(别的设备/控制台)",
          "别的设备" in src and "云端部署无法自动停止" in src)


def test_drop_daemon_client_idempotent():
    """没有连接时反复调用 _drop_daemon_client 不能出错。"""
    eng = stub_engine()
    eng.daemon = FakeDaemon(None)
    eng._drop_daemon_client()
    eng._drop_daemon_client()
    check("daemon.client 保持 None", eng.daemon.client is None)


def test_drop_daemon_client_swallows_close_error():
    """close() 抛异常时也要把指针清掉(否则半死连接永远挂着)。"""
    class BadClient(object):
        def close(self):
            raise RuntimeError("socket already closed")

    eng = stub_engine()
    eng.daemon = FakeDaemon(BadClient())
    eng._drop_daemon_client()
    check("close() 抛异常也清空了 daemon.client", eng.daemon.client is None)
    check("close() 抛异常也复位了 connected", eng.connected is False)


def main():
    print("== 1. 猎人连接的 host/port ==")
    test_host_port_from_account_db()
    test_host_port_falls_back_to_args()
    test_host_port_bad_args_type()
    print("== 2. 重连前放掉全部同账号连接 ==")
    test_reconnect_drops_daemon_client()
    test_reconnect_failure_leaves_no_half_dead_client()
    test_reconnect_with_no_old_client()
    print("== 3. 提示文案 / 收尾 ==")
    test_stopped_note_not_blaming_app_on_server()
    test_drop_daemon_client_idempotent()
    test_drop_daemon_client_swallows_close_error()
    print()
    if FAILED:
        print("❌ 失败 %d 项: %s" % (len(FAILED), ", ".join(FAILED)))
        return 1
    print("✅ 全部通过")
    return 0


if __name__ == "__main__":
    sys.exit(main())