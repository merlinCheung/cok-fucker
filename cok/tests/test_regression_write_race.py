#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""两个"静默丢数据"的回归测试。

1. `cok_store` 的共享连接 + 显式 commit() 竞态
   —— 连接是模块级共享的, 而 sqlite3 的**事务状态是连接级的**:
      线程 A 的 INSERT 隐式开了事务, 线程 B 的 commit 顺手把它提掉,
      A 再 commit 就抛 `cannot commit - no transaction is active`。
      异常被 quiet() 吞成一条栈, 流水却一条没落库 —— 控制台看起来一切正常。

2. `cok_stamina.learn_items` 的同型比较
   —— 缓存值是 `{"uuid":..,"at":..}`(dict), 拿来比的是裸 uuid 字符串,
      永远不相等 ⇒ 每次都判成"新增": 缓存文件反复重写, 前端反复收到重复通知。
"""

import json
import os
import sys
import tempfile
import threading
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "core"))

_TMP = tempfile.mkdtemp(prefix="cok-regress-")
os.environ["COK_DATA_ROOT"] = _TMP
os.environ["COK_PLATFORM_DB"] = os.path.join(_TMP, "platform.db")
os.environ["COK_ACCOUNTS_DIR"] = os.path.join(_TMP, "accounts")
os.environ["COK_RESOURCES_DIR"] = os.path.join(ROOT, "resources")
os.makedirs(os.environ["COK_ACCOUNTS_DIR"], exist_ok=True)

import cok_platform as PLAT          # noqa: E402
import cok_store as S                # noqa: E402
import cok_stamina as ST             # noqa: E402

_UUID = "0123456789abcdef0123456789abcdef"


class TestStoreCommitRace(unittest.TestCase):
    """多线程写同一个库, 不许出现 "cannot commit - no transaction is active"。"""

    def setUp(self):
        S.use_memory()
        PLAT._CONN_PATH = None
        try:
            PLAT.close()
        except Exception:
            pass
        self.addCleanup(S.use_memory)
        S.init()

    def test_concurrent_archive_add(self):
        errs = []
        n_threads, n_each = 8, 40

        def worker(tid):
            try:
                for i in range(n_each):
                    S.archive_add("automation", "key-%d" % tid, "owner",
                                  {"i": i, "tid": tid})
            except Exception as e:      # noqa: BLE001
                errs.append("%s: %s" % (type(e).__name__, e))

        ths = [threading.Thread(target=worker, args=(t,)) for t in range(n_threads)]
        for t in ths:
            t.start()
        for t in ths:
            t.join()

        self.assertEqual(errs, [], "并发写库报错: %s" % errs[:3])
        self.assertEqual(S.archive_count(), n_threads * n_each,
                         "并发写库有条目丢了(流水静默丢就是这个症状)")

    def test_concurrent_mixed_writes(self):
        """读改写 + 单语句写混着来, 同样不许炸。"""
        errs = []

        def w_kv(tid):
            try:
                for i in range(30):
                    S.kv_set("owner-%d" % tid, "k%d" % i, "v%d" % i)
                    S.kv_get("owner-%d" % tid, "k%d" % i)
            except Exception as e:      # noqa: BLE001
                errs.append("kv %s: %s" % (type(e).__name__, e))

        def w_state(tid):
            try:
                for i in range(30):
                    S.account_state_set("acct-%d" % tid, parallel=bool(i % 2))
                    S.account_run_set("acct-%d" % tid, running=True, owner="o")
                    S.task_upsert("task-%d-%d" % (tid, i), key="k", owner="o")
            except Exception as e:      # noqa: BLE001
                errs.append("state %s: %s" % (type(e).__name__, e))

        ths = []
        for t in range(4):
            ths.append(threading.Thread(target=w_kv, args=(t,)))
            ths.append(threading.Thread(target=w_state, args=(t,)))
        for t in ths:
            t.start()
        for t in ths:
            t.join()

        self.assertEqual(errs, [], "并发写库报错: %s" % errs[:3])


class TestStaminaLearnIdempotent(unittest.TestCase):
    """同一个 uuid 再 learn 一次, 不该判成"新增"。"""

    def test_dict_shaped_cache_not_added_again(self):
        into = {"200381": {"uuid": _UUID, "at": 1}}
        found, added = ST.learn_items({"itemId": "200381", "uuid": _UUID}, into)
        self.assertFalse(added, "缓存里已经有这个 uuid 了, 不该算新增")
        self.assertEqual(found.get("200381"), _UUID)

    def test_merge_learned_second_time_is_empty(self):
        uid = "regress-acct"
        payload = {"itemId": "200381", "uuid": _UUID}

        first = ST.merge_learned(uid, payload)
        self.assertEqual(first.get("200381"), _UUID, "第一次应该学到")

        second = ST.merge_learned(uid, payload)
        self.assertEqual(second, {}, "同一个 uuid 再来一次, 不该又报'新增'")

        # 缓存形状要保持 {"uuid":..,"at":..}, 且 at 不能被反复刷新
        items = ST.load_items(uid)
        self.assertIsInstance(items.get("200381"), dict)
        at1 = items["200381"]["at"]
        ST.merge_learned(uid, payload)
        self.assertEqual(ST.load_items(uid)["200381"]["at"], at1,
                         "没变化就不该重写缓存(否则每次响应都刷一遍文件)")

    def test_merge_learned_new_uuid_reports(self):
        uid = "regress-acct-2"
        ST.merge_learned(uid, {"itemId": "200381", "uuid": _UUID})
        other = "fedcba9876543210fedcba9876543210"
        got = ST.merge_learned(uid, {"itemId": "200381", "uuid": other})
        self.assertEqual(got.get("200381"), other, "换了 uuid 就要算新增")
        self.assertEqual(ST.load_items(uid)["200381"]["uuid"], other)


if __name__ == "__main__":
    unittest.main()
