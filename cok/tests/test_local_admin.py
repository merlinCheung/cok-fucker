# -*- coding: utf-8 -*-
"""独立管理后台的平台模式鉴权（不依赖用户登录）。

安卓 App 里的控制台没有登录页：服务端跑在 127.0.0.1、带随机 token，并且以平台模式启动
（`--platform --local-admin <token>`）。管理后台要给这种部署留一条**免登录的本机管理员**
通道，否则 `/admin` 一律跳登录页 —— 而 App 里根本没有登录页，就是白屏。

鉴权规则（三个条件全满足才认）：

  1. 请求来自回环地址（`_client_ip()`）—— 服务被 `--host 0.0.0.0` 暴露也不放行；
  2. `--local-admin <token>` 开着，且 `X-Cok-Token` 头或 `?t=` 与它逐字节相等；
  3. 平台层能取到该管理员账号（库里没有就现建一个，口令随机）。

对应实现在 `cok_web.py`（`_local_admin_ok` / `_local_admin_ensure` /
`_local_admin_claim_orphans`），这里只测鉴权判定本身。
"""
from __future__ import annotations

import os
import shutil
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

# ⚠ 必须在 import cok_web 之前就位: cok_accounts / cok_platform 把账号库路径
# 读成**模块级常量**(ACCOUNTS_DIR / DB_PATH), import 之后再改环境变量不生效,
# 测试会去写用户真实的账号库 —— 那是最坏的结果(污染/覆盖真凭据)。
_TMP_ROOT = tempfile.mkdtemp(prefix="cok-admin-test-")
os.environ["COK_DATA_ROOT"] = os.path.join(_TMP_ROOT, "data")
os.environ["COK_PLATFORM_DB"] = os.path.join(_TMP_ROOT, "platform.db")
os.environ["COK_ACCOUNTS_DIR"] = os.path.join(_TMP_ROOT, "accounts")
os.environ["COK_RESOURCES_DIR"] = os.path.join(ROOT, "resources")
os.makedirs(os.environ["COK_DATA_ROOT"], exist_ok=True)
os.makedirs(os.environ["COK_ACCOUNTS_DIR"], exist_ok=True)

sys.path.insert(0, os.path.join(HERE, "..", "core"))
sys.path.insert(0, os.path.join(HERE, "..", "tools"))

import cok_web as WEB  # noqa: E402
import cok_accounts as ACCS  # noqa: E402
import cok_platform as PLAT  # noqa: E402

TOK = "test-local-token-0123456789"


class _FakeHandler(object):
    """只带鉴权要用到的字段（真 Handler 要 socket/rfile）。"""

    local_admin_token = TOK
    headers = {}
    path = "/api/admin/overview"
    ip = "127.0.0.1"

    def __init__(self, ip="127.0.0.1", token=TOK, path="/api/admin/overview"):
        self.ip = ip
        self.headers = {"X-Cok-Token": token} if token else {}
        self.path = path

    def _client_ip(self):
        return self.ip


class LocalAdminAuthTest(unittest.TestCase):

    def setUp(self):
        self._old = _FakeHandler.local_admin_token
        _FakeHandler.local_admin_token = TOK

    def tearDown(self):
        _FakeHandler.local_admin_token = self._old

    def _ok(self, **kw):
        return WEB.Handler._local_admin_ok(_FakeHandler(**kw))

    def test_loopback_with_header_is_accepted(self):
        self.assertTrue(self._ok())

    def test_loopback_with_query_token_is_accepted(self):
        # 页面跳转带着 ?t=<token>，这是主要路径
        self.assertTrue(self._ok(token=None, path="/admin?t=" + TOK))

    def test_non_loopback_is_refused(self):
        # 服务暴露到 0.0.0.0 时也必须拒绝
        self.assertFalse(self._ok(ip="192.168.1.7"))
        self.assertFalse(self._ok(ip="10.0.0.4"))

    def test_wrong_token_is_refused(self):
        self.assertFalse(self._ok(token="wrong"))
        self.assertFalse(self._ok(token=None, path="/admin?t=nope"))

    def test_empty_token_is_refused(self):
        self.assertFalse(self._ok(token=""))
        self.assertFalse(self._ok(token=None, path="/admin"))

    def test_disabled_when_no_local_admin(self):
        _FakeHandler.local_admin_token = None
        self.assertFalse(self._ok())

    def test_identity_constants(self):
        self.assertEqual(WEB.LOCAL_ADMIN_NAME, "本机管理员")
        self.assertEqual(WEB.LOCAL_ADMIN_UID, "local-admin")


class LocalAdminPlatformTest(unittest.TestCase):
    """平台层：无主账号会被挂到本机管理员名下（否则安卓端管理页看到的是空列表）。

    每个用例一套**独立**的账号库 + platform.db —— 类级别的 setUp 里删共享目录，
    会把上一个用例建好的账号一起删掉（测试之间会互相踩）。
    """

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="cok-admin-case-")
        ACCS.ACCOUNTS_DIR = os.path.join(self.tmp, "accounts")
        ACCS.ACTIVE_FILE = os.path.join(ACCS.ACCOUNTS_DIR, ".active")
        ACCS.DATA_ROOT = os.path.join(self.tmp, "data")
        os.makedirs(ACCS.ACCOUNTS_DIR, exist_ok=True)
        PLAT._CONN_PATH = None          # 强制按新 COK_PLATFORM_DB 重开
        os.environ["COK_PLATFORM_DB"] = os.path.join(self.tmp, "platform.db")
        PLAT.init()
        self.old_handler_token = WEB.Handler.local_admin_token

    def tearDown(self):
        WEB.Handler.local_admin_token = self.old_handler_token
        PLAT.close()
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_ensure_creates_local_admin(self):
        WEB.Handler.local_admin_token = TOK
        row = WEB._local_admin_ensure()
        self.assertIsNotNone(row)
        self.assertEqual(row["uid"], WEB.LOCAL_ADMIN_UID)
        self.assertEqual((row["username"], row["role"]),
                         (WEB.LOCAL_ADMIN_NAME, "admin"))
        # 幂等：再调一次还是那一行
        self.assertEqual(WEB._local_admin_ensure()["uid"], WEB.LOCAL_ADMIN_UID)

    def test_claim_orphans_then_list_visible(self):
        WEB.Handler.local_admin_token = TOK
        WEB._local_admin_ensure()
        ACCS.save_account({"gameUid": "99900001", "openid": "o1",
                           "token": "t1"})
        self.assertEqual(ACCS.list_accounts(owner=WEB.LOCAL_ADMIN_UID), [])
        self.assertEqual(WEB._local_admin_claim_orphans(), 1)
        self.assertEqual([a["key"] for a in
                          ACCS.list_accounts(owner=WEB.LOCAL_ADMIN_UID)],
                         ["99900001"])
        self.assertEqual(ACCS.owner_of("99900001"), WEB.LOCAL_ADMIN_UID)
        self.assertEqual(WEB._local_admin_claim_orphans(), 0)   # 幂等

    def test_no_claim_when_local_admin_disabled(self):
        # 服务器部署（没开 --local-admin）不能把无主号塞给任何人
        WEB.Handler.local_admin_token = None
        ACCS.save_account({"gameUid": "99900002", "openid": "o2"})
        self.assertEqual(WEB._local_admin_claim_orphans(), 0)
        self.assertEqual(ACCS.owner_of("99900002"), "")


if __name__ == "__main__":
    try:
        unittest.main()
    finally:
        shutil.rmtree(_TMP_ROOT, ignore_errors=True)