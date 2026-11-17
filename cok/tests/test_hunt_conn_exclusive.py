#!/usr/bin/env python3
"""同账号连接独占: 回归测试(2026-11-16 服务器打怪被踢的根因)。

**背景(服务器实测)**:
  游戏服同账号**只保留最新的一条连接**。实测: 同账号开第二条连接后,
  旧的那条立刻被服务端关闭("连接被服务端关闭(已收 0/3 字节)"),
  新连接毫发无损 —— 即"后登录的赢"。

  于是网页控制台只要在自动打怪期间**又连一次**同账号(轮询重连、页面点
  一下按钮、`_ensure_client()` 发现 client 是 None 就重连……),
  猎人那条连接就会被踢掉, 用户看到的是
  「连接断开, 已自动停止: 连接被服务端关闭(已收 0/3 字节)」。

**这里锁住的规则**:
  1. 进程内同账号**只允许一条活连接** —— 第二条直接拒绝(AccountBusy),
     绝不让服务端去踢我们自己的连接。
  2. 第一条关掉之后, 第二条才允许建。
  3. 引擎层: 账号被自动打怪/扫描占用时, `_ensure_client()` 不许建连接。
  4. 猎人被踢后: 退避重连(默认 6 次), 并带上诊断信息。
"""
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
for p in (os.path.join(ROOT, "core"), ROOT):
    if p not in sys.path:
        sys.path.insert(0, p)

import cok_client  # noqa: E402
import cok_hunt  # noqa: E402


class FakeSocket(object):
    """socketpair 的一端: select/peek 都能真跑。

    peer 保持打开 = 对端还活着; peer 关掉 = 服务端已发 FIN(EOF)。
    """

    def __init__(self):
        import socket as _socket
        self.sock, self.peer = _socket.socketpair()

    def kill_peer(self):
        """模拟"服务端把连接关了"。"""
        try:
            self.peer.close()
        except Exception:
            pass


def make_client(uid="999", host="h", port=1):
    c = cok_client.CokClient.__new__(cok_client.CokClient)
    c.account = {"gameUid": uid, "host": host, "port": port}
    c.host = host
    c.port = port
    fake = FakeSocket()
    c.sock = fake.sock
    c._fake = fake
    c.key = b"k"
    c.key_id = 1
    c.req_count = 0
    c.connected_at = 0.0
    c.conn_identity = cok_client.conn_identity(c.account, host, port)
    return c


class TestConnExclusive(unittest.TestCase):

    def setUp(self):
        with cok_client._LIVE_CONNS_MUTEX:
            cok_client._LIVE_CONNS.clear()

    def tearDown(self):
        with cok_client._LIVE_CONNS_MUTEX:
            cok_client._LIVE_CONNS.clear()

    def test_same_account_second_connection_refused(self):
        """同账号第二条活连接 -> 直接拒绝(不能建, 更不能去踢第一条)。"""
        a = make_client()
        cok_client.claim_connection(a.conn_identity, a)
        b = make_client()
        self.assertIsNotNone(cok_client.live_connection(a.conn_identity))
        self.assertIs(cok_client.live_connection(a.conn_identity), a)
        # b 想连 -> 被拒
        other = cok_client.live_connection(b.conn_identity)
        self.assertIs(other, a)
        # 身份算得出来
        self.assertEqual(a.conn_identity, b.conn_identity)

    def test_different_account_not_blocked(self):
        """不同账号互不影响。"""
        a = make_client(uid="111")
        b = make_client(uid="222")
        cok_client.claim_connection(a.conn_identity, a)
        self.assertIsNone(cok_client.live_connection(b.conn_identity))

    def test_release_allows_new_connection(self):
        """第一条关掉之后, 第二条才允许建。"""
        a = make_client()
        cok_client.claim_connection(a.conn_identity, a)
        a.close()
        self.assertIsNone(cok_client.live_connection(a.conn_identity))
        b = make_client()
        self.assertIsNone(cok_client.live_connection(b.conn_identity))

    def test_dead_socket_counts_as_free(self):
        """服务端已经关掉的连接(EOF)不算"活着" -> 允许重连。"""
        a = make_client()
        cok_client.claim_connection(a.conn_identity, a)
        a._fake.kill_peer()      # 对端关闭 -> 我们这侧读到 EOF
        self.assertTrue(a.sock_dead())
        self.assertIsNone(cok_client.live_connection(a.conn_identity))

    def test_conn_diag(self):
        """诊断信息: 存活时长 + 请求数(被踢时告诉用户)。"""
        a = make_client()
        a.connected_at = 100.0
        a.req_count = 42
        d = a.conn_diag()
        self.assertEqual(d["requests"], 42)
        self.assertIn("age", d)


class TestHuntResilience(unittest.TestCase):

    def test_reconnect_budget_is_larger_than_before(self):
        """重连次数上限 >= 6(以前 2 次, 用户几乎必然看到自动停止)。"""
        c = make_client()
        h = cok_hunt.AutoHunter(c, level=1, num=1)
        self.assertGreaterEqual(h.max_reconnects, 6)

    def test_conn_diag_text(self):
        c = make_client()
        c.connected_at = 0.0
        c.req_count = 7
        h = cok_hunt.AutoHunter(c, level=1, num=1)
        txt = h._conn_diag()
        self.assertIn("活了", txt)
        self.assertIn("请求", txt)

    def test_no_target_backoff(self):
        """连续找不到怪 -> 退避(别空转刷搜索)。"""
        c = make_client()
        h = cok_hunt.AutoHunter(c, level=30, num=1)
        h._no_target_streak = 0
        self.assertAlmostEqual(h._no_target_sleep(), h.poll)
        h._no_target_streak = 1
        self.assertGreater(h._no_target_sleep(), h.poll)
        h._no_target_streak = 9
        self.assertLessEqual(h._no_target_sleep(), 30.0)


class TestEngineGuard(unittest.TestCase):
    """引擎层: 账号被猎人/扫描占用时, 不许再建第二条连接。"""

    def _engine(self):
        import cok_engine
        eng = cok_engine.Engine.__new__(cok_engine.Engine)
        eng.lock = __import__("threading").Lock()
        eng.hunter = None
        eng.hunter_client = None
        eng._hunter_starting = False
        eng.account_key = "12345"
        eng.owner = "u-x"
        eng.daemon = type("D", (), {"client": None})()
        return eng

    def test_guard_blocks_when_hunter_active(self):
        eng = self._engine()
        self.assertIsNone(eng._account_connection_owner())
        eng.hunter = {"running": True}
        self.assertEqual(eng._account_connection_owner(), "hunter")
        with self.assertRaises(cok_client.AccountBusy):
            eng._assert_account_free("本轮轮询")
        with self.assertRaises(cok_client.AccountBusy):
            eng._ensure_client()

    def test_guard_blocks_during_handoff(self):
        """交接期(正在起猎人)也算占用。"""
        eng = self._engine()
        eng._hunter_starting = True
        self.assertEqual(eng._account_connection_owner(), "hunter")
        with self.assertRaises(cok_client.AccountBusy):
            eng._ensure_client()

    def test_stale_hunter_client_is_closed(self):
        """猎人跑完但连接还挂着 -> 必须关掉, 否则网页「重连」被自己拦下。

        ⚠️ 2026-11-16 线上反馈: "所有连接都断开了, 点重连还是提示被占用"。
        根因就是猎人 done 时没关连接, socket 还活着 ->
        进程内登记表认为有人占着这个账号。
        """
        eng = self._engine()
        hc = make_client()
        cok_client.claim_connection(hc.conn_identity, hc)
        eng.hunter_client = hc
        eng.hunter = {"running": False}      # 猎人已经跑完
        eng._close_stale_hunter_client()
        self.assertIsNone(eng.hunter_client)          # 指针清空
        self.assertIsNone(hc.sock)                     # socket 关了
        self.assertIsNone(cok_client.live_connection(hc.conn_identity))

    def test_running_hunter_client_is_kept(self):
        """猎人还在跑时, 那条连接是它正在用的 —— 绝不能关。"""
        eng = self._engine()
        hc = make_client()
        eng.hunter_client = hc
        eng.hunter = {"running": True}
        eng._close_stale_hunter_client()
        self.assertIs(eng.hunter_client, hc)
        self.assertIsNotNone(hc.sock)


if __name__ == "__main__":
    unittest.main(verbosity=2)
