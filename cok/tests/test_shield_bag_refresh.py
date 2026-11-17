#!/usr/bin/env python3
"""新逻辑的离线验证: 保护罩槽位库存标记 + 背包快照 + 喝药数量/落盘/再拉取。

不连游戏服、不写真实数据目录(全部走临时目录)。
跑法: python3 cok/tests/test_shield_bag_refresh.py
"""
import os
import sys
import tempfile
import types

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "core"))
sys.path.insert(0, os.path.join(HERE, "..", "tools"))

os.environ["COK_ACCOUNT_LOCK_FILE"] = os.path.join(
    tempfile.gettempdir(), "cok-test-shieldbag-%d.lock" % os.getpid())

import cok_engine        # noqa: E402
import cok_hunt          # noqa: E402
import cok_stamina       # noqa: E402

_ok = True


def check(name, cond, detail=""):
    global _ok
    print("[%s] %s%s" % ("PASS" if cond else "FAIL", name,
                         ("  — " + detail) if detail else ""))
    if not cond:
        _ok = False


class FakeDaemon(object):
    def __init__(self, args):
        self.args = args
        self.client = None
        self.shield_end_ms = 0
        self.emitted = []

    def ctx(self):
        return {"today": 1, "month": 1, "now": 0, "date": "2026-11-17"}

    def emit(self, kind, payload):
        self.emitted.append((kind, payload))


class FakeShieldClient(object):
    """回 onekeybuff.get / show.status.item / login.init 的假客户端。"""

    def __init__(self, slot_num=0, bag_items=None):
        self.slot_num = slot_num          # 槽位1里 200411 的库存数量
        self.bag_items = bag_items or []
        self.calls = []

    def call(self, cmd, params=None, retries=1, timeout=None):
        self.calls.append(cmd)
        if cmd == "onekeybuff.get":
            return {"__params__": {"backList": [
                {"type": 1, "name": "",
                 "statusList": [{"itemId": "200411", "num": self.slot_num}]},
                {"type": 2, "name": "", "statusList": []},
                {"type": 3, "name": "", "statusList": []}]}}
        if cmd == "show.status.item":
            return {"__params__": {"statusItems": []}}
        if cmd == "login.init":
            return {"__params__": {"items": self.bag_items}}
        raise AssertionError("未预期的命令 %s" % cmd)


def make_engine(tmp, slot_num=0, bag_items=None):
    eng = cok_engine.Engine.__new__(cok_engine.Engine)
    eng.daemon = FakeDaemon(argparse_ns())
    eng.daemon.client = FakeShieldClient(slot_num, bag_items)
    eng.account_key = "unit-shieldbag"
    eng.settings = {}
    eng.lock = __import__("threading").RLock()
    eng.bag_snapshot = None
    eng._bag_refreshing = False
    eng._shield_specs_cache = None
    eng.names = {"items": {}}
    return eng


def argparse_ns():
    return types.SimpleNamespace(account=None, shield_watch_interval=20)


def main():
    tmp = tempfile.mkdtemp(prefix="cok-shieldbag-")
    os.environ["COK_DATA_ROOT"] = tmp
    import importlib
    importlib.reload(cok_stamina)

    # 1) 槽位库存标记: num=0 -> no_stock; num=3 -> 有库存
    eng = make_engine(tmp, slot_num=0)
    out = eng._shield_slots()
    slot1 = out["slots"][0]
    check("槽位内道具 num=0 -> no_stock",
          slot1["items"] and slot1["items"][0]["no_stock"] is True,
          str(slot1["items"])[:80])
    eng2 = make_engine(tmp, slot_num=3)
    out2 = eng2._shield_slots()
    check("槽位内道具 num=3 -> 有库存(no_stock=False)",
          out2["slots"][0]["items"][0]["no_stock"] is False)

    # 2) 背包快照: 有 200411x3 -> 下拉条目带数量
    bag = [{"itemId": "200411", "count": 3,
            "uuid": "a" * 32, "useDate": 0, "vanishTime": 0},
           {"itemId": "200410", "count": 0, "uuid": "b" * 32},
           {"itemId": "200381", "count": 5, "uuid": "c" * 32}]
    eng3 = make_engine(tmp, slot_num=3, bag_items=bag)
    with eng3.lock:
        eng3.bag_snapshot = {"at": 12345, "items": bag}
    items = eng3._shield_backpack_items()
    ids = {it["itemId"]: it for it in items}
    check("快照有 200411x3 -> 下拉列出且数量正确",
          ids.get("200411", {}).get("count") == 3,
          str(items)[:100])
    check("count=0 的道具不进下拉(200410)",
          "200410" not in ids, str(list(ids)))
    check("非保护罩道具不进下拉(200381 是药水)",
          "200381" not in ids, str(list(ids)))

    # 3) 猎人喝药: 服务端 count 权威 + 落盘
    uid = "unit-drink-%d" % os.getpid()
    potions = {"200381": {"uuid": "d" * 32, "count": 10}}
    cok_stamina.save_items(uid, potions)
    cl = FakeUseClient({"item.use": {"count": 9}})
    h = cok_hunt.AutoHunter(cl, auto_stamina=True,
                            stamina_items=dict(potions), uid=uid)
    h.state["stamina"] = 5
    ok = h._use_stamina_if_needed()
    check("喝药成功", ok)
    check("数量按服务端 count=9(不是本地减一)",
          h.stamina_items["200381"]["count"] == 9,
          str(h.stamina_items.get("200381")))
    disk = cok_stamina.load_items(uid)
    check("数量已落盘(网页/安卓读同一份缓存)",
          isinstance(disk.get("200381"), dict)
          and disk["200381"].get("count") == 9,
          str(disk.get("200381")))
    try:
        os.unlink(cok_stamina.items_path(uid))
    except OSError:
        pass

    # 4) 喝药后 uuid 失效(E100166) + 冷却后再拉背包
    uid2 = "unit-refetch-%d" % os.getpid()
    cok_stamina.save_items(uid2, {"200381": {"uuid": "e" * 32, "count": 2}})
    cl2 = FakeUseClient({"item.use": {"errorCode": "E100166"},
                         "login.init": {"items": [
                             {"itemId": "200381", "count": 4,
                              "uuid": "f" * 32}]}})
    h2 = cok_hunt.AutoHunter(cl2, auto_stamina=True,
                             stamina_items=cok_stamina.load_items(uid2),
                             uid=uid2)
    h2.state["stamina"] = 5
    h2._use_stamina_if_needed()      # 失败, uuid 丢弃
    check("E100166 后 uuid 被丢弃",
          "uuid" not in h2.stamina_items.get("200381", {}),
          str(h2.stamina_items.get("200381")))
    # 模拟"上次拉取在很久以前" -> 允许再拉一次
    h2._stamina_bag_tried = True
    h2._stamina_bag_at = 0.0         # 很久以前
    # login.init 拿到的新实例 uuid = f*32, 用它再喝一次应当成功
    cl2.responses["item.use"] = {"itemId": "200381", "count": 3}
    ok2 = h2._use_stamina_if_needed()
    check("uuid 失效 + 超过拉取冷却 -> 重新拉背包并喝上(数量取新实例)",
          ok2 and h2.stamina_items.get("200381", {}).get("uuid") == "f" * 32
          and h2.stamina_items.get("200381", {}).get("count") == 3,
          str(h2.stamina_items.get("200381"))[:80])
    check("重新拉背包走了 login.init(第 2 条)",
          len([c for c in cl2.calls if c == "login.init"]) >= 1,
          str(cl2.calls))
    try:
        os.unlink(cok_stamina.items_path(uid2))
    except OSError:
        pass

    # 5) 整背包快照落盘/读回(按账号隔离)
    uid3 = "unit-bagsnap-%d" % os.getpid()
    full = [{"itemId": "200411", "count": 3, "uuid": "a" * 32},
            {"itemId": "200381", "count": 5, "uuid": "c" * 32},
            {"itemId": "999999", "count": 1}]
    check("save_bag 成功", cok_stamina.save_bag(uid3, full) is True)
    back = cok_stamina.load_bag(uid3)
    check("load_bag 读回 items 一致",
          back and len(back.get("items") or []) == 3
          and back["items"][0]["itemId"] == "200411",
          str(back)[:80])
    check("load_bag 带 at 时间戳", back and int(back.get("at") or 0) > 0)
    check("另一个账号读不到(隔离)",
          cok_stamina.load_bag("unit-bagsnap-other") is None)

    # 6) _load_bag_from_disk 把落盘快照加载进内存
    eng5 = make_engine(tmp)
    eng5.account_key = uid3
    eng5.bag_snapshot = None
    eng5._load_bag_from_disk()
    check("启动加载: bag_snapshot 从磁盘恢复",
          eng5.bag_snapshot and len(eng5.bag_snapshot.get("items") or []) == 3,
          str(eng5.bag_snapshot)[:60])

    # 7) _bag_view 分类视图: 保护罩 / 体力药水分开, 杂项只计 total
    eng5._bag_refreshing = False
    view = eng5._bag_view()
    check("_bag_view total 含全部道具", view.get("total") == 3, str(view.get("total")))
    check("_bag_view 挑出保护罩",
          any(s["itemId"] == "200411" for s in view.get("shields") or []),
          str(view.get("shields"))[:80])
    check("_bag_view 挑出体力药水",
          any(p["itemId"] == "200381" for p in view.get("potions") or []),
          str(view.get("potions"))[:80])
    check("_bag_view loaded=True", view.get("loaded") is True)
    try:
        os.unlink(cok_stamina.bag_path(uid3))
    except OSError:
        pass

    print()
    print("全部通过" if _ok else "有失败项")
    return 0 if _ok else 1


class FakeUseClient(object):
    def __init__(self, responses):
        self.responses = responses
        self.calls = []

    def call(self, cmd, params=None, retries=1, timeout=None):
        self.calls.append(cmd)
        r = self.responses.get(cmd)
        if r is None:
            raise AssertionError("未预期的命令 %s" % cmd)
        return {"__params__": dict(r)}


if __name__ == "__main__":
    sys.exit(main())