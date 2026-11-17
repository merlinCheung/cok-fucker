#!/usr/bin/env python3
"""「一个账号只有一条连接」的最后一道闸门: 回归测试(2026-11-16)。

**背景(服务器实测, 打怪被踢的真凶)**:
  游戏服同账号只保留一条连接。2026-11-16 15:18 的现场:

  ```
  15:17:19  网页自己的连接登录(端口 32181)   <- 无主运行时建出来的引擎
  15:18:00  自动打怪开始, 猎人自己的连接登录(端口 32181, 同一个账号)
  15:18:41  网页那条开始发请求(cmd.ping + 一堆 watcher)
  15:18:42  猎人那条被服务端关闭: 「连接被服务端关闭(已收 0/3 字节)」
  ```

  ⇒ 两条连接**同时存在**。原因有两个, 都要堵:
  1. `connect(force=True)` 原来只是**跳过**检查, 自己那条照样建 ——
     于是"无主运行时"的连接和猎人的连接并存;
  2. 平台模式下 `PlatformManager.get("")`(= 没人登录的请求)会建一个
     **无主**运行时, 它的账号锁不带 owner 前缀, 和真正用户的那个引擎
     **互相看不见** ⇒ 同一个号开出两条连接。

**这里锁住的规则**:
  1. `connect(force=True)` 会**真正关掉**同账号的另一个活连接(接管, 不是并存);
  2. `connect(force=False)` 仍然直接拒绝(AccountBusy);
  3. 平台模式下 `PlatformManager.get("")` 返回 None(不建无主运行时);
  4. 锁的持有者以 **flock 为准**: 锁空闲但文件里留着陈旧 holder 时,
     不许报"账号正被占用"。
"""
import os
import sys
import shutil
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
for p in (os.path.join(ROOT, "core"), ROOT):
    if p not in sys.path:
        sys.path.insert(0, p)

import cok_client  # noqa: E402

#: 账号锁文件落到**临时目录**, 不能污染真实 cok/data/(否则跑完测试
#: data/ 里会留下一堆 .cok-account-*.lock)。COK_ACCOUNT_LOCK_FILE 覆盖的是
#: 锁的**目录**(见 cok_client.lock_file_for)。
_LOCK_DIR = None


def setUpModule():
    global _LOCK_DIR
    _LOCK_DIR = tempfile.mkdtemp(prefix="cok-single-conn-")
    os.environ["COK_ACCOUNT_LOCK_FILE"] = _LOCK_DIR


def tearDownModule():
    os.environ.pop("COK_ACCOUNT_LOCK_FILE", None)
    if _LOCK_DIR:
        shutil.rmtree(_LOCK_DIR, ignore_errors=True)


class FakeSocket(object):
    def __init__(self):
        import socket as _socket
        self.sock, self.peer = _socket.socketpair()

    def close(self):
        try:
            self.sock.close()
        except Exception:
            pass


def make_client(uid="999", host="127.0.0.1", port=1):
    c = cok_client.CokClient.__new__(cok_client.CokClient)
    c.account = {"gameUid": uid, "host": host, "port": port}
    c.host = host
    c.port = port
    _fake = FakeSocket()
    c.sock = _fake.sock
    c._fake = _fake          # ⚠️ 留住 peer, 否则对端被 GC -> 看起来"已死"    c.key = b"k"
    c.key_id = 1
    c.req_count = 0
    c.connected_at = 0.0
    c.timeout = 5.0
    c.conn_identity = cok_client.conn_identity(c.account, host, port)
    return c


class TestForceTakesOver(unittest.TestCase):

    def setUp(self):
        with cok_client._LIVE_CONNS_MUTEX:
            cok_client._LIVE_CONNS.clear()

    def tearDown(self):
        with cok_client._LIVE_CONNS_MUTEX:
            cok_client._LIVE_CONNS.clear()

    def test_force_closes_the_other_connection(self):
        """force=True = 接管: 必须把同账号那条**真正关掉**, 不能并存。"""
        a = make_client()
        cok_client.claim_connection(a.conn_identity, a)
        b = make_client()
        # b 去连(真连不上没关系: 关掉 a 发生在建 socket **之前**)
        try:
            b.connect(force=True, retries=1)
        except Exception:
            pass
        self.assertIsNone(a.sock, "force=True 之后, 原来那条连接必须被关掉")

    def test_non_force_still_refuses(self):
        """force=False 仍然直接拒绝(不能踢别人那条)。"""
        a = make_client()
        cok_client.claim_connection(a.conn_identity, a)
        b = make_client()
        with self.assertRaises(cok_client.AccountBusy):
            b.connect(force=False, retries=1)
        self.assertIsNotNone(a.sock, "被拒时不能动别人那条连接")

    def test_holder_uses_flock_as_truth(self):
        """锁空闲但文件里留着陈旧 holder -> 不许报"被占用"。"""
        key = "__stale_holder__"
        path = cok_client.lock_file_for(key)
        # 模拟"进程被 kill, 文件内容没清"
        with open(path, "w", encoding="utf-8") as f:
            f.write("999999 web-poll\n")
        self.assertEqual(cok_client.account_holder(key), "",
                         "锁明明是空的, 不该报出持有者")
        # 真的被占着时, 要报出来
        with cok_client.account_lock(timeout=0.0, purpose="web-poll", key=key):
            holder = cok_client.account_holder(key)
            self.assertIn("web-poll", holder)
            self.assertTrue(cok_client.account_holder_info(key)["self"])
        # 释放后又不该报
        self.assertEqual(cok_client.account_holder(key), "")


class TestNoOwnerlessRuntime(unittest.TestCase):
    """平台模式: 没人登录时不许建"无主运行时"。"""

    def test_platform_get_empty_owner_returns_none(self):
        import cok_engine
        pm = cok_engine.PlatformManager.__new__(cok_engine.PlatformManager)
        import threading
        pm.lock = threading.RLock()
        pm.users = {}
        pm.seen = {}
        pm.args = None
        self.assertIsNone(pm.get(""),
                          "owner 为空(=没人登录)不该建运行时")
        self.assertEqual(pm.users, {}, "也不该留下任何管理器")


if __name__ == "__main__":
    unittest.main(verbosity=2)
