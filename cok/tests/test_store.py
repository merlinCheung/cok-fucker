#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""业务状态入库（cok_store）的测试。

重点不是"表建没建"，而是那几条容易写错、且错了会静默丢数据的规则：
  * 局部更新不能抹掉其它字段（`account_state_set(parallel=True)` 不许清掉扫描历史）
  * 空库/坏 JSON 要能兜住（迁移时读到半个文件不能让整个控制台起不来）
  * 幂等（重复迁移不产生重复行）
  * 库不可写时退回内存库而不是崩掉
"""

import json
import os
import sys
import tempfile
import time
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "core"))

_TMP = tempfile.mkdtemp(prefix="cok-store-")
os.environ["COK_DATA_ROOT"] = _TMP
os.environ["COK_PLATFORM_DB"] = os.path.join(_TMP, "platform.db")
os.environ["COK_ACCOUNTS_DIR"] = os.path.join(_TMP, "accounts")
os.environ["COK_RESOURCES_DIR"] = os.path.join(ROOT, "resources")
os.makedirs(os.environ["COK_ACCOUNTS_DIR"], exist_ok=True)

import cok_platform as PLAT          # noqa: E402
import cok_store as S                # noqa: E402
import cok_accounts as ACCS          # noqa: E402


class StoreBase(unittest.TestCase):
    def setUp(self):
        S.use_memory()
        PLAT._CONN_PATH = None
        try:
            PLAT.close()
        except Exception:
            pass
        self.addCleanup(S.use_memory)
        S.init()

    # -- 辅助 ---------------------------------------------------------
    def put_account(self, key, owner="u-1", **kw):
        # ⚠️ save_account 要求 gameUid（账号库用它当文件名）
        acc = {"key": key, "gameUid": key, "owner": owner, "name": key}
        acc.update(kw)
        ACCS.save_account(acc)


class TestKv(StoreBase):
    def test_get_set_del(self):
        S.kv_set("u-1", "view_key", "351542128002216")
        self.assertEqual(S.kv_get("u-1", "view_key"), "351542128002216")
        S.kv_set("u-1", "view_key", "99900002")
        self.assertEqual(S.kv_get("u-1", "view_key"), "99900002")
        S.kv_del("u-1", "view_key")
        self.assertEqual(S.kv_get("u-1", "view_key", "-"), "-")

    def test_json_roundtrip(self):
        S.kv_set_json("u-1", "priorities", {"a": ["x", "y"], "b": []})
        self.assertEqual(S.kv_json("u-1", "priorities"), {"a": ["x", "y"], "b": []})

    def test_owner_isolation(self):
        S.kv_set("u-1", "k", "one")
        S.kv_set("u-2", "k", "two")
        self.assertEqual(S.kv_get("u-1", "k"), "one")
        self.assertEqual(S.kv_get("u-2", "k"), "two")

    def test_json_bad_returns_default(self):
        S.kv_set("u-1", "k", "not-json")
        self.assertEqual(S.kv_json("u-1", "k", {"d": 1}), {"d": 1})


class TestAccountState(StoreBase):
    def test_partial_update_keeps_other_fields(self):
        """最关键的一条：只改 parallel 不能抹掉扫描历史/任务统计。"""
        S.account_state_set("351542128002216",
                            scan_history=[{"at": 1, "rows": 3}],
                            task_stats={"route": 4})
        S.account_state_set("351542128002216", parallel=True)
        st = S.account_state_get("351542128002216")
        self.assertEqual(len(st["scan_history"]), 1)
        self.assertEqual(st["task_stats"], {"route": 4})
        self.assertTrue(st["parallel"])

    def test_default_when_missing(self):
        st = S.account_state_get("nope")
        self.assertEqual(st["scan_history"], [])
        self.assertEqual(st["task_stats"], {})

    def test_all(self):
        S.account_state_set("a", task_stats={"x": 1})
        S.account_state_set("b", parallel=True)
        allst = S.account_state_all()
        self.assertEqual(sorted(allst), ["a", "b"])


class TestAccountSettings(StoreBase):
    def test_roundtrip_and_keys(self):
        S.account_settings_set("351542128002216", {"autoSign": True, "lvLow": 40})
        self.assertEqual(S.account_settings_get("351542128002216")["lvLow"], 40)
        self.assertIn("351542128002216", S.account_settings_keys())

    def test_overwrite(self):
        S.account_settings_set("k", {"a": 1})
        S.account_settings_set("k", {"b": 2})
        self.assertEqual(S.account_settings_get("k"), {"b": 2})


class TestScanIndex(StoreBase):
    def test_partial_and_owner(self):
        S.scan_index_set("u-1", "k", doc={"step": 8, "players": [1, 2]})
        S.scan_index_set("u-1", "k", progress=12)
        got = S.scan_index_get("u-1", "k")
        self.assertEqual(got["progress"], 12)
        self.assertEqual(len(got["doc"]["players"]), 2)
        # 另一个 owner 的同名账号不串
        self.assertIsNone(S.scan_index_get("u-2", "k"))

    def test_list_and_done(self):
        S.scan_index_set("u-1", "k", doc={"a": 1}, scanned=5)
        S.scan_index_mark_done("u-1", "k")
        rows = S.scan_index_list()
        self.assertEqual(len(rows), 1)
        self.assertTrue(rows[0]["done"])


class TestAccountRun(StoreBase):
    def test_running_transitions(self):
        S.account_run_set("351542128002216", owner="u-1")
        self.assertFalse(S.account_run_get("351542128002216")["running"])
        S.account_run_set("351542128002216", running=True)
        r = S.account_run_get("351542128002216")
        self.assertTrue(r["running"])
        self.assertGreater(r["since"], 0)
        first_since = r["since"]
        time.sleep(0.01)
        S.account_run_set("351542128002216", running=False, reason="被顶")
        r = S.account_run_get("351542128002216")
        self.assertFalse(r["running"])
        self.assertEqual(r["reason"], "被顶")
        # 起点保留（方便算"跑了多久"）
        self.assertEqual(r["since"], first_since)

    def test_restart_resets_since(self):
        S.account_run_set("k", running=True)
        first = S.account_run_get("k")["since"]
        time.sleep(0.01)
        S.account_run_set("k", running=False)
        S.account_run_set("k", running=True)
        self.assertGreater(S.account_run_get("k")["since"], first)

    def test_list_by_owner(self):
        S.account_run_set("a", owner="u-1", running=True)
        S.account_run_set("b", owner="u-2", running=True)
        self.assertEqual([x["key"] for x in S.account_run_list(owner="u-1")], ["a"])


class TestTaskRun(StoreBase):
    def test_upsert_and_get(self):
        S.task_upsert("t1", key="351542128002216", owner="u-1",
                      kind="route", label="46-3 挂机",
                      params={"stage": "46-3"}, progress={"cur": 2})
        got = S.task_get("t1")
        self.assertEqual(got["kind"], "route")
        self.assertEqual(got["params"], {"stage": "46-3"})
        self.assertEqual(got["progress"], {"cur": 2})
        self.assertFalse(got["done"])

    def test_progress_update_keeps_params(self):
        S.task_upsert("t1", key="k", kind="route", params={"stage": "46-3"})
        S.task_upsert("t1", progress={"cur": 5, "max": 10})
        got = S.task_get("t1")
        self.assertEqual(got["params"], {"stage": "46-3"})
        self.assertEqual(got["progress"]["cur"], 5)

    def test_finish_and_running_only(self):
        S.task_upsert("t1", key="k", kind="route")
        S.task_upsert("t2", key="k", kind="debug")
        S.task_finish("t1", "done")
        self.assertEqual(len(S.task_list(key="k", running_only=True)), 1)
        self.assertEqual(len(S.task_list(key="k")), 2)

    def test_running_keys(self):
        S.task_upsert("t1", key="a", kind="route")
        S.task_upsert("t2", key="b", kind="route")
        S.task_finish("t2", "done")
        self.assertEqual(S.task_running_keys(), ["a"])

    def test_cleanup_keeps_running(self):
        S.task_upsert("t1", key="a", kind="route")
        S.task_finish("t1", "done")
        S.task_cleanup(days=1)
        # done 的记录没到期（刚写的）不该被删
        self.assertIsNotNone(S.task_get("t1"))


class TestClientState(StoreBase):
    def test_roundtrip_and_drop(self):
        S.client_state_set("u-1", "351542128002216", "lake", {"levels": [1, 2]})
        S.client_state_set("u-1", "351542128002216", "hunt", {"running": True})
        got = S.client_state_list("u-1", "351542128002216")
        self.assertEqual(sorted(got), ["hunt", "lake"])
        self.assertEqual(got["lake"]["levels"], [1, 2])
        S.client_state_drop("u-1", "351542128002216", "hunt")
        self.assertEqual(sorted(S.client_state_list("u-1", "351542128002216")), ["lake"])
        S.client_state_drop("u-1", "351542128002216")
        self.assertEqual(S.client_state_list("u-1", "351542128002216"), {})


class TestImportFiles(StoreBase):
    def setUp(self):
        StoreBase.setUp(self)
        self.root = tempfile.mkdtemp(prefix="cok-import-")
        self.adir = os.path.join(self.root, "accounts")
        os.makedirs(self.adir, exist_ok=True)
        os.makedirs(os.path.join(self.root, "u", "u-1"), exist_ok=True)
        ACCS.ACCOUNTS_DIR = self.adir
        ACCS.DATA_ROOT = self.root
        self.addCleanup(self._restore)

    def _restore(self):
        ACCS.ACCOUNTS_DIR = os.environ["COK_ACCOUNTS_DIR"]
        ACCS.DATA_ROOT = _TMP

    def _write(self, path, doc):
        with open(path, "w", encoding="utf-8") as f:
            if isinstance(doc, str):
                f.write(doc)
            else:
                json.dump(doc, f, ensure_ascii=False)

    def test_import_full(self):
        self.put_account("351542128002216", owner="u-1")
        self.put_account("99900002", owner="")
        self._write(os.path.join(self.root, "u", "u-1", "web-settings.json"),
                    {"autoSign": True, "huntMax": 5})
        # 全局默认配置（单用户模式的那一份）
        self._write(os.path.join(self.root, "web-settings.json"),
                    {"autoSign": False, "huntMax": 9})
        d = ACCS.data_dir("351542128002216")
        os.makedirs(d, exist_ok=True)
        self._write(os.path.join(d, "automation-settings.json"), {"autoSign": False})
        self._write(os.path.join(d, "scan-history.json"), [{"at": 1}, {"at": 2}])
        self._write(os.path.join(d, "task-stats.json"), {"route": 3})
        self._write(os.path.join(d, "map-index.json"),
                    {"step": 8, "players": [{"x": 1}, {"x": 2}]})
        self._write(os.path.join(self.adir, ".parallel"), "351542128002216, 99900002")

        out = S.import_files(self.root, self.adir)

        self.assertEqual(out["user_settings"], 2)   # 每用户 1 + 全局默认 1
        self.assertEqual(out["account_settings"], 1)
        self.assertEqual(out["account_state"], 1)
        self.assertEqual(out["scan_index"], 1)
        # owner 有值的账号在**平台库** users 里补了行；owner 为空的跳过
        import cok_platform as PLAT
        self.assertTrue(PLAT.user_get("u-1"), "账号的 owner 没在 users 里登记")
        self.assertEqual(len(PLAT.list_users()), 1)
        self.assertEqual(S.user_settings_get("u-1")["huntMax"], 5)
        self.assertEqual(S.account_settings_get("351542128002216")["autoSign"], False)
        st = S.account_state_get("351542128002216")
        self.assertEqual(len(st["scan_history"]), 2)
        self.assertTrue(st["parallel"])
        # 全局默认配置落在 owner="" 上（单用户模式用）
        self.assertEqual(S.user_settings_get("").get("huntMax"), 9,
                         "全局默认配置没落库")

    def test_import_idempotent(self):
        self.put_account("351542128002216", owner="u-1")
        d = ACCS.data_dir("351542128002216")
        os.makedirs(d, exist_ok=True)
        self._write(os.path.join(d, "scan-history.json"), [{"at": 1}])
        S.import_files(self.root, self.adir)
        second = S.import_files(self.root, self.adir)
        self.assertEqual(len(S.account_state_all()), 1)
        self.assertEqual(second["account_state"], 1)

    def test_import_bad_json_does_not_crash(self):
        self.put_account("351542128002216", owner="u-1")
        d = ACCS.data_dir("351542128002216")
        os.makedirs(d, exist_ok=True)
        self._write(os.path.join(d, "scan-history.json"), "{ 坏掉的 json")
        out = S.import_files(self.root, self.adir)
        # 坏文件被跳过，但别的步骤照跑
        self.assertIsInstance(out, dict)
        self.assertEqual(S.account_state_get("351542128002216")["scan_history"], [])

    def test_import_no_accounts_dir(self):
        out = S.import_files(self.root, os.path.join(self.root, "nope"))
        self.assertEqual(out["users"], 0)

    def test_import_scan_history_is_list(self):
        """scan-history.json 是 {"runs":[...]} -> 库里要存成数组，不是 {"runs":...}。"""
        self.put_account("351542128002216", owner="u-1")
        d = ACCS.data_dir("351542128002216")
        os.makedirs(d, exist_ok=True)
        self._write(os.path.join(d, "scan-history.json"),
                    {"runs": [{"id": "a", "status": "completed"}]})
        S.import_files(self.root, self.adir)
        st = S.account_state_get("351542128002216")
        self.assertEqual(len(st["scan_history"]), 1)
        self.assertEqual(st["scan_history"][0]["id"], "a")


class TestArchive(StoreBase):
    def test_append_and_list(self):
        S.archive_add("automation", "351542128002216", "u-1",
                      {"kind": "route", "at": int(time.time())}, size=120)
        S.archive_add("automation", "351542128002216", "u-1", {"kind": "hunt"})
        rows = S.archive_list(kind="automation", key="351542128002216")
        self.assertEqual(len(rows), 2)
        # 按时间倒序：最后一条在前
        self.assertEqual(rows[0]["doc"]["kind"], "hunt")

    def test_filters(self):
        S.archive_add("a", "k1", "u-1", {"x": 1})
        S.archive_add("b", "k2", "u-1", {"x": 2})
        self.assertEqual(len(S.archive_list(kind="a")), 1)
        self.assertEqual(S.archive_count(), 2)
        self.assertEqual(S.archive_count("a"), 1)
        self.assertEqual(len(S.archive_list(owner="u-2")), 0)

    def test_cleanup_keeps_newest(self):
        for i in range(6):
            S.archive_add("a", "k", "u-1", {"i": i})
        removed = S.archive_cleanup(keep=4)
        self.assertEqual(removed, 2)
        rows = S.archive_list(kind="a")
        self.assertEqual(len(rows), 4)
        self.assertEqual(rows[-1]["doc"]["i"], 2)   # 最老的 0/1 被删


class TestSettingsKey(StoreBase):
    """配置键必须**调用方统一拼**，否则拼错就"改了没生效"。"""

    def test_owner_and_account_do_not_collide(self):
        S.settings_set("owner:u-1", {"lvLow": 40})
        S.settings_set("acct:351542128002216", {"lvLow": 50})
        self.assertEqual(S.settings_get("owner:u-1")["lvLow"], 40)
        self.assertEqual(S.settings_get("acct:351542128002216")["lvLow"], 50)

    def test_helpers(self):
        S.user_settings_put("u-1", {"huntMax": 3})
        self.assertEqual(S.user_settings_get("u-1")["huntMax"], 3)
        S.account_settings_db_set("351542128002216", {"huntMax": 7})
        self.assertEqual(S.account_settings_db_get("351542128002216")["huntMax"], 7)
        self.assertEqual(S.account_settings_db_get("nope"), {})

    def test_empty_does_not_shadow_file(self):
        """库里没写过 -> 返回 {}，让调用方知道该走文件兜底。"""
        self.assertEqual(S.settings_get("owner:nobody"), {})


class TestMissingTable(StoreBase):
    """库里还没有新表时(老库首次升级)，读取一律返回"空"而不是抛异常。

    真实场景：服务器上 platform.db 已经存在，代码先部署、迁移后跑。
    那几十秒里页面会调 /api/admin/overview -> store.status()。
    """

    def test_all_readers_survive_missing_tables(self):
        c = S.conn()
        for t in ("account_settings", "account_state", "scan_index",
                  "scan_doc", "account_run", "task_run", "client_state",
                  "archive"):
            c.execute("DROP TABLE IF EXISTS %s" % t)
        c.commit()
        self.assertEqual(S.kv_json("x", "settings", {}), {})
        self.assertEqual(S.settings_get("owner:u-1"), {})
        self.assertEqual(S.account_state_get("k"),
                         {"scan_history": [], "task_stats": {},
                          "parallel": False})
        self.assertIsNone(S.scan_index_get("", "k"))
        self.assertEqual(S.account_run_list(), [])
        self.assertEqual(S.task_list(key="k"), [])
        self.assertEqual(S.client_state_list("u-1", "k"), {})
        self.assertEqual(S.archive_list(), [])
        st = S.status()          # 管理页那条路径
        self.assertIn("tables", st)
        self.assertEqual(st["tables"]["account_state"], 0)

    def test_writers_recreate_tables(self):
        """写侧会补建表 —— 老库不用手动迁移也能边跑边补。"""
        c = S.conn()
        for t in ("account_settings", "account_state", "client_state"):
            c.execute("DROP TABLE IF EXISTS %s" % t)
        c.commit()
        S.account_state_set("k", scan_history=[{"r": 1}])
        self.assertEqual(S.account_state_get("k")["scan_history"], [{"r": 1}])
        S.client_state_set("u-1", "k", "ui", {"a": 1})
        self.assertEqual(S.client_state_get("u-1", "k", "ui"), {"a": 1})


class TestStats(StoreBase):
    def test_shape(self):
        st = S.stats()
        for k in ("kv", "account_state", "account_settings", "scan_index",
                  "account_run", "task_run", "client_state"):
            self.assertIn(k, st)


class TestParallelFile(StoreBase):
    """accounts/.parallel 有两种历史写法，解析必须都认。

    真实踩坑：老版本把文件内容按逗号硬 split，遇到 JSON 数组
    `["136063574002223",\n"44056610002223"]` 会拆出
    `'["136063574002223"'` / `'44056610002223"]'` 两条垃圾 key，
    写进 account_state 后**永远没人读**，还让并行集显示多两个不存在的号。
    """

    def test_json_array_one_per_line(self):
        raw = '[\n"136063574002223",\n"44056610002223"\n]'
        self.assertEqual(S._parallel_keys(raw),
                         ["136063574002223", "44056610002223"])

    def test_comma_single_line(self):
        self.assertEqual(S._parallel_keys("a,b,c"), ["a", "b", "c"])

    def test_empty(self):
        self.assertEqual(S._parallel_keys(""), [])
        self.assertEqual(S._parallel_keys("[]"), [])

    def test_no_junk_keys_enter_db(self):
        """导入 JSON 数组格式的 .parallel 后，库里只该有真的 key。"""
        self.assertEqual(S._parallel_keys('[\n"a",\n"b"\n]'), ["a", "b"])
        for k in S._parallel_keys('[\n"a",\n"b"\n]'):
            S.account_state_set(k, parallel=True)
        rows = S.account_state_all()
        self.assertEqual(sorted(rows), ["a", "b"])
        for bad in rows:
            self.assertNotIn("[", bad)
            self.assertNotIn('"', bad)
            self.assertNotIn("]", bad)


if __name__ == "__main__":
    unittest.main()