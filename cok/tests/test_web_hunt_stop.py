#!/usr/bin/env python3
"""「停止打怪」在打怪进行中必须能成功(2026-11-12 修的 bug)。

**bug**: 点「停止打怪」一直报「账号正被占用(同账号只允许一个连接)」, 停止按钮失灵。

**根因**: 打怪线程持有那把**跨进程账号锁**(flock); 而"停止"这个请求
在 `action()` 里**也要先抢同一把锁** —— 于是变成**自己等自己**:
  * `account_lock` 的可重入判定按 **thread id**, 停止请求是**另一个线程**
    ⇒ 不算 nested ⇒ 真去 flock ⇒ 同进程另一个 fd 也冲突(EAGAIN)
    ⇒ 抛 `AccountBusy` ⇒ 页面显示「账号正被占用」。

**修法**: 「停止打怪」必须**先于账号锁执行** ——
先把猎人停掉(它自己会把锁还回去), 再走正常流程。

跑法:
    python3 test_web_hunt_stop.py
"""

import argparse
import json
import os
import sys
import tempfile
import threading
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "core"))
sys.path.insert(0, os.path.join(HERE, "..", "tools"))

# 测试用**独立**的账号锁文件, 否则会跟正在运行的网页控制台抢同一个账号
os.environ['COK_ACCOUNT_LOCK_FILE'] = os.path.join(
    tempfile.gettempdir(), 'cok-test-huntstop-%d.lock' % os.getpid())
import cok_web  # noqa: E402
import cok_client  # noqa: E402

FAILED = []


def check(name, cond, detail=""):
    print("  [%s] %s%s" % ("ok" if cond else "FAIL", name,
                           ("  <- " + detail) if (detail and not cond) else ""))
    if not cond:
        FAILED.append(name)
    return cond


def make_args(**over):
    a = argparse.Namespace(
        host="127.0.0.1", port=8771, account_device=True, account=None,
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
    """假后台引擎: 只有 action() 收尾要用到的 client 属性。"""

    def __init__(self):
        self.client = None


class FakeHunter(object):
    """假猎人: 只提供 stop() 和 state。"""

    def __init__(self):
        self.state = {"running": True, "kills": 3}
        self.stopped = False

    def stop(self, note=""):
        self.stopped = True
        self.state["running"] = False
        self.state["note"] = note


def main():
    tmp = tempfile.mkdtemp(prefix="cokweb-huntstop-")
    try:
        cok_web.Engine.SETTINGS_FILE = os.path.join(tmp, "web-settings.json")
        eng = cok_web.Engine(make_args())
        eng.daemon = FakeDaemon()     # 不连游戏服
        eng._ensure_account = lambda: True
        eng.app_online = lambda: False
        eng._ensure_client = lambda: None
        eng._hunt_state = lambda: {"stamina": 100, "stamina_max": 1000}

        hunter = FakeHunter()
        eng.hunter = hunter
        eng.hunter_client = None

        # ⚠️ 模拟"打怪线程正持有那把跨进程账号锁"。
        # 生产里这把锁是**开始打怪**的请求线程拿的, 由打怪线程归还;
        # 这里用主线程持有, "停止"请求放到**另一个线程** ——
        # 和真实场景一样, 停止请求**不是** nested(可重入按 thread id 判定)。
        lock_ctx = cok_client.account_lock(timeout=3.0, purpose="auto-hunt",
                                            key=eng._lock_key())
        lock_ctx.__enter__()
        eng._hunter_lock = lock_ctx

        # 先确认: 另一个线程**真的**拿不到这把锁(否则这个测试没有意义)
        got = {}

        def try_lock():
            try:
                with cok_client.account_lock(timeout=0.3, purpose="other",
                                             key=eng._lock_key()):
                    got["ok"] = True
            except Exception as e:  # noqa: BLE001
                got["ok"] = False
                got["err"] = str(e)

        th = threading.Thread(target=try_lock)
        th.start()
        th.join(timeout=5)
        check("前提: 打怪持锁时, 别的线程拿不到锁",
              got.get("ok") is False, json.dumps(got, ensure_ascii=False))

        # ★ 被测点: 打怪进行中点「停止」
        res = {}

        def do_stop():
            res["r"] = eng.action({"action": "hunt", "op": "auto-stop"})

        th2 = threading.Thread(target=do_stop)
        th2.start()
        th2.join(timeout=15)
        r = res.get("r") or {}
        check("打怪中点停止: 不再报「账号正被占用」",
              "账号正被占用" not in (r.get("error") or ""),
              json.dumps(r, ensure_ascii=False))
        check("打怪中点停止: 返回 ok",
              r.get("ok") is True, json.dumps(r, ensure_ascii=False))
        check("打怪中点停止: 猎人真的停了",
              hunter.stopped and not hunter.state.get("running"))
        check("打怪中点停止: 账号锁已归还(可以再被别的操作拿到)",
              _lock_is_free(eng._lock_key()))

        # 停完之后, 普通操作应该能正常拿到锁
        got2 = {}

        def try_lock2():
            try:
                with cok_client.account_lock(timeout=1.0, purpose="after",
                                             key=eng._lock_key()):
                    got2["ok"] = True
            except Exception as e:  # noqa: BLE001
                got2["ok"] = False
                got2["err"] = str(e)

        th3 = threading.Thread(target=try_lock2)
        th3.start()
        th3.join(timeout=5)
        check("停止后普通操作能拿到锁", got2.get("ok") is True,
              json.dumps(got2, ensure_ascii=False))
    finally:
        try:
            eng._release_hunter_lock()
        except Exception:  # noqa: BLE001
            pass
    print()
    if FAILED:
        print("❌ 失败 %d 项: %s" % (len(FAILED), ", ".join(FAILED)))
        return 1
    print("✅ 全部通过")
    return 0


def _lock_is_free(key):
    fd = os.open(cok_client.lock_file_for(key), os.O_RDWR | os.O_CREAT, 0o644)
    try:
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            fcntl.flock(fd, fcntl.LOCK_UN)
            return True
        except OSError:
            return False
    finally:
        os.close(fd)


if __name__ == "__main__":
    import fcntl  # noqa: E402
    sys.exit(main())
