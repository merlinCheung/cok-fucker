#!/usr/bin/env python3
"""体力药水自动使用的单元测试 —— 2026-11-10。

覆盖:
  * `cok_stamina.learn_items` 从各种响应形态里学出 {itemId: uuid}
  * `pick_stamina` 的挑选优先级与失效处理
  * `use_stamina_item` 的参数(**num 必须是 SFS INT** —— 传普通 int 服务端回 E000000)
  * `AutoHunter._use_stamina_if_needed` 的成功/失败/实例失效三条路径
  * 体力不足时(run 循环里)确实会触发喝药

跑: python3 test_stamina.py
"""
import json
import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "core"))
sys.path.insert(0, os.path.join(HERE, "..", "tools"))

import cok_hunt          # noqa: E402
import cok_stamina      # noqa: E402


class FakeClient(object):
    """假客户端: 记录发出的命令, 按脚本回响应。"""

    def __init__(self, responses=None):
        self.responses = responses or {}
        self.calls = []

    def call(self, cmd, params=None, retries=1, timeout=None):
        self.calls.append((cmd, params))
        r = self.responses.get(cmd)
        if callable(r):
            return r(cmd, params)
        if r is None:
            return {"__params__": {"_cok_": "1"}}
        return {"__params__": r}


def _uuid(n):
    return ("%032x" % n)


def _rm_items(uid):
    """删掉测试留下的道具缓存文件(别在真实 accounts/ 里留垃圾)。"""
    try:
        os.unlink(cok_stamina.items_path(uid))
    except OSError:
        pass


class TestLearnItems(unittest.TestCase):
    def test_flat_pair(self):
        payload = {"itemId": "200381", "uuid": _uuid(1)}
        found, added = cok_stamina.learn_items(payload)
        self.assertEqual(found.get("200381"), _uuid(1))
        self.assertTrue(added)

    def test_reward_value_shape(self):
        # 协议注释里的形态: reward[].value = {id, num, uuid}
        payload = {"reward": [{"type": 7, "value": {"num": 6, "id": "200381",
                                                  "uuid": _uuid(2)}}]}
        found, _ = cok_stamina.learn_items(payload)
        self.assertEqual(found.get("200381"), _uuid(2))

    def test_nested_item_obj(self):
        payload = {"itemEffectObj": {"itemId": "200380",
                                     "itemObj": {"uuid": _uuid(3)}}}
        found, _ = cok_stamina.learn_items(payload)
        self.assertEqual(found.get("200380"), _uuid(3))

    def test_non_uuid_ignored(self):
        payload = {"itemId": "200381", "uuid": "not-a-uuid"}
        found, added = cok_stamina.learn_items(payload)
        self.assertEqual(found, {})
        self.assertFalse(added)

    def test_into_accumulates(self):
        into = {"200380": _uuid(9)}
        found, added = cok_stamina.learn_items({"itemId": "200381",
                                                 "uuid": _uuid(4)}, into)
        self.assertTrue(added)
        self.assertEqual(into.get("200380"), _uuid(9))
        self.assertEqual(into.get("200381"), _uuid(4))

    def test_same_uuid_not_added(self):
        into = {"200381": _uuid(5)}
        _found, added = cok_stamina.learn_items({"itemId": "200381",
                                                  "uuid": _uuid(5)}, into)
        self.assertFalse(added)


class TestPickStamina(unittest.TestCase):
    def test_prefers_bigger_gain(self):
        items = {"200380": {"uuid": _uuid(1)},
                 "200381": {"uuid": _uuid(2)},
                 "200382": {"uuid": _uuid(3)}}
        iid, uuid = cok_stamina.pick_stamina(items)
        self.assertEqual(iid, "200382")
        self.assertEqual(uuid, _uuid(3))

    def test_zero_count_skipped(self):
        items = {"200381": {"uuid": _uuid(2), "count": 0},
                 "200380": {"uuid": _uuid(1), "count": 3}}
        iid, uuid = cok_stamina.pick_stamina(items)
        self.assertEqual(iid, "200380")

    def test_plain_string_uuid(self):
        iid, uuid = cok_stamina.pick_stamina({"200381": _uuid(7)})
        self.assertEqual(iid, "200381")
        self.assertEqual(uuid, _uuid(7))

    def test_none(self):
        iid, uuid = cok_stamina.pick_stamina({})
        self.assertIsNone(iid)
        self.assertIsNone(uuid)


class TestUseStaminaItem(unittest.TestCase):
    def test_num_is_sfs_int(self):
        cl = FakeClient({"item.use": {"count": 1}})
        ok, info = cok_stamina.use_stamina_item(cl, _uuid(1), 1)
        self.assertTrue(ok)
        cmd, params = cl.calls[0]
        self.assertEqual(cmd, "item.use")
        self.assertEqual(params["uuid"], _uuid(1))
        # 数量必须是 SFS INT(TypedInt 是 int 的子类, 靠 sfs_type 标注类型),
        # 服务端收到普通 int 会回 E000000
        from cok_sfs import TypedInt, SFS_INT
        self.assertIsInstance(params["num"], TypedInt)
        self.assertEqual(params["num"].sfs_type, SFS_INT)
        self.assertEqual(int(params["num"]), 1)

    def test_error_code_returned(self):
        cl = FakeClient({"item.use": {"errorCode": "E100166"}})
        ok, info = cok_stamina.use_stamina_item(cl, _uuid(1), 1)
        self.assertFalse(ok)
        self.assertEqual(info["errorCode"], "E100166")
        self.assertIn("失效", info["error"])


class TestAutoHunterStamina(unittest.TestCase):
    def _hunter(self, responses=None, **kw):
        cl = FakeClient(responses or {})
        h = cok_hunt.AutoHunter(cl, auto_stamina=True,
                                 stamina_items={"200381": {"uuid": _uuid(11),
                                                          "count": 3}}, **kw)
        return h, cl

    def test_success_adds_stamina_and_counts(self):
        h, cl = self._hunter({"item.use": {"count": 1}})
        h.state["stamina"] = 5
        ok = h._use_stamina_if_needed()
        self.assertTrue(ok)
        self.assertEqual(h.state["stamina"], 5 + 50)
        self.assertEqual(h.state["stamina_potions"], 1)
        self.assertEqual(h.state["stamina_potion_item"], "200381")
        # 缓存里的数量应该减一
        self.assertEqual(h.stamina_items["200381"]["count"], 2)

    def test_failure_does_not_count_as_fails(self):
        h, cl = self._hunter({"item.use": {"errorCode": "E100165"}})
        h.state["stamina"] = 5
        h.state["fails"] = 0
        ok = h._use_stamina_if_needed()
        self.assertFalse(ok)
        self.assertEqual(h.state["fails"], 0)     # 不算打怪失败
        self.assertEqual(h.state["stamina"], 5)  # 体力没变
        self.assertEqual(h.state["stamina_potions"], 0)

    def test_expired_uuid_is_dropped(self):
        h, cl = self._hunter({"item.use": {"errorCode": "E100166"}})
        ok = h._use_stamina_if_needed()
        self.assertFalse(ok)
        # 实例失效 -> 缓存里应该丢掉这个 uuid
        self.assertNotIn("uuid", h.stamina_items.get("200381", {}))

    def test_disabled_does_nothing(self):
        cl = FakeClient({"item.use": {}})
        h = cok_hunt.AutoHunter(cl, auto_stamina=False,
                                stamina_items={"200381": {"uuid": _uuid(11)}})
        self.assertFalse(h._use_stamina_if_needed())
        self.assertEqual(cl.calls, [])

    def test_no_uuid_note(self):
        # 没有实例 uuid 时: 第一次会尝试拉背包(login.init), 拉不到才提示
        cl = FakeClient()
        h = cok_hunt.AutoHunter(cl, auto_stamina=True, stamina_items={})
        self.assertFalse(h._use_stamina_if_needed())
        self.assertIn("背包", h.state["note"])
        # 拉过一次就不要再拉(一次要 40~50 秒)
        self.assertTrue(h._stamina_bag_tried)
        self.assertIn("login.init", [c[0] for c in cl.calls])
        # 第二次直接给结论, 不再发请求
        n = len(cl.calls)
        self.assertFalse(h._use_stamina_if_needed())
        self.assertEqual(len(cl.calls), n)

    def test_fetches_bag_when_missing_uuid(self):
        # 背包里明明有药水 -> 拉一次背包就能喝上
        cl = FakeClient({"login.init": {"items": [
            {"itemId": "200381", "count": 3, "uuid": _uuid(77)}]}})
        h = cok_hunt.AutoHunter(cl, auto_stamina=True, stamina_items={})
        h.state["stamina"] = 5
        ok = h._use_stamina_if_needed()
        self.assertTrue(ok)
        self.assertEqual(h.state["stamina_potions"], 1)
        self.assertEqual(h.state["stamina_potion_item"], "200381")
        self.assertEqual(h.state["stamina"], 5 + 50)

    def test_state_has_counter(self):
        h, _cl = self._hunter()
        self.assertIn("stamina_potions", h.state)
        self.assertIn("auto_stamina", h.state)
        self.assertTrue(h.state["auto_stamina"])


class TestFetchBag(unittest.TestCase):
    """`login.init` 拉背包 —— 体力药水道具实例 uuid 的正规来源。"""

    def test_scan_potions_keeps_only_potions_with_stock(self):
        items = [
            {"itemId": "200002", "count": 7, "uuid": _uuid(1)},   # 不是药水
            {"itemId": "200381", "count": 0, "uuid": _uuid(2)},   # 空实例
            {"itemId": "200381", "count": 5, "uuid": _uuid(3)},   # 有货
            {"itemId": "200380", "count": 2, "uuid": "bad"},       # uuid 不合法
            {"itemId": "200380", "count": 2, "uuid": _uuid(4)},
        ]
        got = cok_stamina.scan_potions(items)
        self.assertEqual(sorted(got.keys()), ["200380", "200381"])
        self.assertEqual(got["200381"]["uuid"], _uuid(3))
        self.assertEqual(got["200381"]["count"], 5)
        self.assertEqual(got["200380"]["uuid"], _uuid(4))

    def test_scan_potions_bad_input(self):
        self.assertEqual(cok_stamina.scan_potions(None), {})
        self.assertEqual(cok_stamina.scan_potions("x"), {})

    def test_fetch_bag_learns_and_caches(self):
        uid = "unit-test-bag-%d" % os.getpid()
        # 缓存写在真实 accounts/ 目录里 —— 用完删掉, 别留垃圾
        self.addCleanup(_rm_items, uid)
        cl = FakeClient({"login.init": {"items": [
            {"itemId": "200204", "count": 9, "uuid": _uuid(5)},
            {"itemId": "200381", "count": 6, "uuid": _uuid(6)}]}})
        ok, info = cok_stamina.fetch_bag(cl, uid)
        self.assertTrue(ok)
        self.assertEqual(info["total"], 2)
        self.assertEqual(info["potions"]["200381"]["uuid"], _uuid(6))
        self.assertEqual(info["potions"]["200381"]["count"], 6)
        # 落盘了
        back = cok_stamina.load_items(uid)
        self.assertEqual(back["200381"]["uuid"], _uuid(6))

    def test_fetch_bag_without_items_field(self):
        cl = FakeClient({"login.init": {"_cok_": "1"}})
        ok, info = cok_stamina.fetch_bag(cl)
        self.assertFalse(ok)
        self.assertIn("items", info.get("error", ""))


class TestStaminaItemTable(unittest.TestCase):
    def test_ids_and_gains(self):
        self.assertEqual(cok_stamina.STAMINA_ITEMS["200380"], 10)
        self.assertEqual(cok_stamina.STAMINA_ITEMS["200381"], 50)
        self.assertEqual(cok_stamina.STAMINA_ITEMS["200382"], 100)

    def test_hunt_constant_includes_382(self):
        self.assertIn("200382", cok_hunt.STAMINA_ITEMS)


class TestCacheFile(unittest.TestCase):
    def test_save_load_roundtrip(self):
        uid = "unit-test-%d" % os.getpid()
        try:
            items = {"200381": {"uuid": _uuid(8), "count": 2}}
            self.assertTrue(cok_stamina.save_items(uid, items))
            back = cok_stamina.load_items(uid)
            self.assertEqual(back["200381"]["uuid"], _uuid(8))
            st = cok_stamina.status(uid)
            self.assertTrue(st["known"])
            self.assertEqual(st["itemId"], "200381")
        finally:
            p = cok_stamina.items_path(uid)
            if os.path.exists(p):
                os.unlink(p)


if __name__ == "__main__":
    unittest.main(verbosity=2)
