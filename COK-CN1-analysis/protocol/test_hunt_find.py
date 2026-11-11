#!/usr/bin/env python3
"""找怪失败路径的单元测试(2026-11-11 修 `int(None)` 崩溃)。

背景:
  服务端 `res.tile.find` 有两种"没找到":
    * x/y 字段缺失(None)  -> 今日找怪次数用完(客户端提示 113228)
    * x == -1 / y == -1    -> 世界上没有这个等级的怪(客户端提示 113229)
  之前两种都当成功返回, 后面 `point_index(None, None)` 里 `int(None)` 直接抛
  TypeError -> 自动打怪每轮都崩 -> 连续 5 次异常 -> 自动停止。

本测试不连游戏服, 零消耗。
"""

import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

os.environ.setdefault(
    'COK_ACCOUNT_LOCK_FILE',
    os.path.join(tempfile.gettempdir(), 'cok-test-find-%d.lock' % os.getpid()))
import cok_hunt  # noqa: E402


class FakeClient(object):
    def __init__(self, params):
        self.params = params
        self.calls = []

    def call(self, cmd, params=None, retries=0):
        self.calls.append((cmd, params))
        if cmd == "res.tile.find":
            return {"__params__": dict(self.params)}
        raise AssertionError("unexpected cmd %r" % cmd)


class TestFindMonster(unittest.TestCase):
    def test_ok_returns_int_coords(self):
        cl = FakeClient({"x": 1005, "y": 673, "type": 6})
        r = cok_hunt.find_monster(cl, 23)
        self.assertTrue(r["ok"])
        self.assertEqual(r["x"], 1005)
        self.assertEqual(r["y"], 673)

    def test_missing_coords_is_search_limit(self):
        """x/y 缺失 = 今日找怪次数用完 —— 不能当成功。"""
        cl = FakeClient({"type": 6})
        r = cok_hunt.find_monster(cl, 23)
        self.assertFalse(r["ok"])
        self.assertEqual(r["errorCode"], "SEARCH_LIMIT")

    def test_none_coords_is_search_limit(self):
        cl = FakeClient({"x": None, "y": None, "type": 6})
        r = cok_hunt.find_monster(cl, 23)
        self.assertFalse(r["ok"])
        self.assertEqual(r["errorCode"], "SEARCH_LIMIT")

    def test_minus_one_is_no_target(self):
        """x == -1 = 世界上没有这种怪(和"次数用完"是两回事)。"""
        cl = FakeClient({"x": -1, "y": -1, "type": 6})
        r = cok_hunt.find_monster(cl, 23)
        self.assertFalse(r["ok"])
        self.assertEqual(r["errorCode"], "NO_TARGET")

    def test_error_code_passthrough(self):
        cl = FakeClient({"errorCode": "E000000"})
        r = cok_hunt.find_monster(cl, 23)
        self.assertFalse(r["ok"])
        self.assertEqual(r["errorCode"], "E000000")


class TestPointIndex(unittest.TestCase):
    def test_none_does_not_raise(self):
        """⚠️ 这是崩溃点: 之前 int(None) 抛 TypeError, 一次就带崩整个打怪循环。"""
        self.assertEqual(cok_hunt.point_index(None, None), 0)
        self.assertEqual(cok_hunt.point_index(None, 673), 0)
        self.assertEqual(cok_hunt.point_index(1005, None), 0)

    def test_garbage_does_not_raise(self):
        self.assertEqual(cok_hunt.point_index("abc", "def"), 0)

    def test_normal_still_works(self):
        idx = cok_hunt.point_index(1005, 673)
        self.assertGreater(idx, 0)


class TestLaunchSearchLimit(unittest.TestCase):
    """_launch 遇到"找怪次数用完"时: 不计入 fails, 也不崩。"""

    def _hunter(self):
        h = cok_hunt.AutoHunter.__new__(cok_hunt.AutoHunter)
        h.client = FakeClient({"type": 6})
        h.level = 23
        h.num = 100
        h.state = {"stamina": 500, "fails": 0, "kills": 0}
        h._squads = []
        h.squad_spec = None
        h.squad_max = 4
        h.mix = 1
        h.min_stamina = 9
        h._find_blocked_until = 0.0
        h._find_used = 0
        h._find_limit = 6
        h.stamina_items = {}
        h._stamina_bag_tried = False
        return h

    def test_search_limit_not_counted_as_fail(self):
        h = self._hunter()
        army = [{"id": "107012", "free": 1000, "march": 0, "speed": 1, "load": 1}]
        sq = {"army_id": "107012", "num": 100, "state": "idle",
              "troops": [{"army_id": "107012", "num": 100,
                          "speed": 1, "load": 1}], "fails": 0, "note": ""}
        ok, info = h._launch(sq, army)
        self.assertFalse(ok)
        self.assertEqual(info.get("errorCode"), "SEARCH_LIMIT")
        self.assertEqual(sq["fails"], 0)          # 不算失败
        self.assertEqual(h.state["fails"], 0)      # 不算失败


if __name__ == "__main__":
    unittest.main(verbosity=2)
