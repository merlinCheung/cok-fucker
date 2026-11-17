#!/usr/bin/env python3
"""账号锁「自占用」退避重试: 回归测试(2026-11-16)。

**背景(线上反馈)**: "所有都已经断开了, 但是点击重连还是提示被占用"。

根因不是外部占用, 而是**网页控制台自己**:
  * flock 绑在 open file description 上 —— **同进程用另一个 fd 再 flock 也会失败**;
  * 网页后台轮询线程(`purpose="web-poll"`)做一轮同步时正拿着那把账号锁;
  * 用户此时点「重连」→ `action()` 去抢锁 → 抢不到 → 抛 AccountBusy
    → 页面显示「账号正被占用(同账号只允许一个连接)」。

持有者其实是**自己人**, 而且是**瞬时**的(轮询一轮就还)。
所以正确做法是**退避重试**, 不是直接失败。

**这里锁住的规则**:
  1. 持有者是本进程短时占用(web-poll) → 退避重试, 最终能拿到锁;
  2. 持有者是长时独占(auto-hunt / scan-world) → **立刻**失败, 不干等;
  3. 持有者是别的进程 → **立刻**失败(不能傻等);
  4. 锁空闲 → `holder_is_transient_self()` 返回 False(别去等一个不存在的占用)。
"""
import os
import subprocess
import sys
import shutil
import tempfile
import threading
import time
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
for p in (os.path.join(ROOT, "core"), ROOT):
    if p not in sys.path:
        sys.path.insert(0, p)

import cok_client  # noqa: E402

KEY = "__cok_lock_retry_test__"

#: 锁文件必须落到**临时目录**, 不能污染真实 cok/data/。
#: COK_ACCOUNT_LOCK_FILE 覆盖的是锁的**目录**(见 cok_client.lock_file_for),
#: 在父进程里设好, test_fails_fast_on_foreign_process 的 Popen 子进程会继承,
#: 两边才会争同一把锁。
_LOCK_DIR = None


def setUpModule():
    global _LOCK_DIR
    _LOCK_DIR = tempfile.mkdtemp(prefix="cok-lock-retry-")
    os.environ["COK_ACCOUNT_LOCK_FILE"] = _LOCK_DIR


def tearDownModule():
    os.environ.pop("COK_ACCOUNT_LOCK_FILE", None)
    if _LOCK_DIR:
        shutil.rmtree(_LOCK_DIR, ignore_errors=True)


class TestAccountLockRetry(unittest.TestCase):

    def test_free_lock_is_not_transient(self):
        """没人占着 -> 不该被当成"自占用"。"""
        self.assertFalse(cok_client.holder_is_transient_self(KEY))

    def test_holder_info_marks_self(self):
        """持有者信息里 self=True(同进程)。"""
        with cok_client.account_lock(timeout=0.0, purpose="web-poll", key=KEY):
            info = cok_client.account_holder_info(KEY)
            self.assertTrue(info["self"], info)
            self.assertEqual(info["pid"], os.getpid())
            self.assertTrue(cok_client.holder_is_transient_self(KEY))

    def test_long_hold_purpose_is_not_transient(self):
        """auto-hunt / scan-world 是长时独占 -> 不能当成瞬时占用去等。"""
        for purpose in ("auto-hunt", "scan-world"):
            with cok_client.account_lock(timeout=0.0, purpose=purpose, key=KEY):
                self.assertFalse(
                    cok_client.holder_is_transient_self(KEY),
                    "purpose=%s 不该被判为瞬时占用" % purpose)

    def test_waits_for_transient_self_holder(self):
        """本进程短时占用 -> 退避重试, 最终拿到锁。"""
        released = []

        def holder():
            with cok_client.account_lock(timeout=0.0, purpose="web-poll", key=KEY):
                time.sleep(1.0)
                released.append(True)

        th = threading.Thread(target=holder)
        th.start()
        time.sleep(0.2)
        t0 = time.time()
        with cok_client.account_lock_retry(timeout=8.0, purpose="web-action",
                                           key=KEY):
            waited = time.time() - t0
        th.join()
        self.assertTrue(released)
        self.assertGreater(waited, 0.5,
                           "应该等轮询线程还锁, 实际只等了 %.2fs" % waited)

    def test_fails_fast_on_long_hold(self):
        """长时独占 -> 立刻失败, 不干等。"""
        def holder():
            with cok_client.account_lock(timeout=0.0, purpose="auto-hunt", key=KEY):
                time.sleep(2.5)

        th = threading.Thread(target=holder)
        th.start()
        time.sleep(0.3)
        t0 = time.time()
        with self.assertRaises(cok_client.AccountBusy):
            with cok_client.account_lock_retry(timeout=10.0,
                                               purpose="web-action", key=KEY):
                pass
        dt = time.time() - t0
        th.join()
        self.assertLess(dt, 1.0, "长时独占不该干等, 实际等了 %.2fs" % dt)

    def test_fails_fast_on_foreign_process(self):
        """别的进程占着 -> 立刻失败。"""
        code = (
            "import sys,time;sys.path.insert(0,%r);"
            "import cok_client;"
            "c=cok_client.account_lock(timeout=0.0,purpose='scan-world',key=%r);"
            "c.__enter__();time.sleep(2.5);c.__exit__(None,None,None)"
            % (os.path.join(ROOT, "core"), KEY)
        )
        proc = subprocess.Popen([sys.executable, "-c", code])
        time.sleep(0.8)
        t0 = time.time()
        with self.assertRaises(cok_client.AccountBusy):
            with cok_client.account_lock_retry(timeout=10.0,
                                               purpose="web-action", key=KEY):
                pass
        dt = time.time() - t0
        proc.wait()
        self.assertLess(dt, 2.0, "跨进程占用不该干等, 实际等了 %.2fs" % dt)

    def test_lock_released_after_retry(self):
        """retry 拿到锁之后, 退出时必须把锁还回去(不能漏锁)。"""
        with cok_client.account_lock_retry(timeout=2.0, purpose="web-action",
                                           key=KEY):
            self.assertTrue(cok_client.account_is_busy(KEY))
        # 释放后再拿 -> 必须能拿到
        with cok_client.account_lock_retry(timeout=2.0, purpose="web-action",
                                           key=KEY):
            pass


if __name__ == "__main__":
    unittest.main(verbosity=2)
