#!/usr/bin/env python3
"""「体力不足自动喝体力药水」开关的回归测试(零消耗, 不连游戏服)。

背景(2026-11-17 线上反馈: 打怪时开了自动喝药水, 猎人却从来不用):
  这个开关此前**只存在于前端**, 后端一路都没接住:
    1. `huntAutoStamina` 不在 `Engine.DEFAULT_SETTINGS` 里, hunter() 也不回写,
       ⇒ `settings.get("huntAutoStamina")` 恒为 None ⇒ `auto_stamina` 永远 False;
    2. `_hunter_start` 在体力低于 `huntMinStamina` 时**直接拒启** —— 开着
       自动喝药水的号根本起不来, 更谈不上去喝;
    3. `_fallback_web_hunt`(没周卡时降级成网页自己打)不把 autoStamina 透传给
       `_hunter_start` ⇒ 降级路径静默丢掉开关。

覆盖:
  * DEFAULT_SETTINGS 里有 `huntAutoStamina`(默认关) 与 `huntMix`(默认 1)
  * `set-setting` 落成真正的 bool("false"/0 不能被当成 True)
  * 体力低于阈值时: 开关开 + 有药水 => 放行; 开关开 + 没药水 => 说清原因;
    开关关 => 维持原来的拒绝
  * 启动时开关被回写进 settings(重启/安卓读状态都能看到)
  * 猎人真的收到 auto_stamina=True 和药水实例 uuid
  * `_fallback_web_hunt` 透传 autoStamina

跑法: python3 cok/tests/test_stamina_switch.py
"""

import argparse
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "core"))
sys.path.insert(0, os.path.join(HERE, "..", "tools"))

os.environ["COK_ACCOUNT_LOCK_FILE"] = os.path.join(
    tempfile.gettempdir(), "cok-test-stamina-switch-%d.lock" % os.getpid())

import cok_client      # noqa: E402
import cok_engine      # noqa: E402
import cok_hunt        # noqa: E402
import cok_stamina     # noqa: E402


def check(name, cond, detail=""):
    print("[%s] %s%s" % ("PASS" if cond else "FAIL", name,
                         ("  — " + detail) if detail else ""))
    return bool(cond)


class FakeDaemon(object):
    def __init__(self, args, client=None):
        self.args = args
        self.client = client
        self.emitted = []

    def ctx(self):
        return {"today": 1, "month": 1, "now": 0, "date": "2026-11-17"}

    def emit(self, kind, payload):
        self.emitted.append((kind, payload))


class FakeClient(object):
    """只回 army 清单的假客户端(够 _auto_squad_spec 用)。"""

    def __init__(self, army):
        self.army = army

    def call(self, cmd, params=None, retries=1):
        if cmd == "world.user.march":
            return {"__params__": {"army": [dict(a) for a in self.army], "m": []}}
        raise AssertionError("未预期的命令 %s" % cmd)


ARMY = [{"id": "107110", "free": 100000, "march": 0, "speed": 9, "load": 13,
         "power": 10.8, "attack": 1, "defen": 1}]


class StopBeforeConnect(Exception):
    """哨兵: 在"该建连了"的地方主动停下, 后面都是网络活。"""


def make_args():
    return argparse.Namespace(
        host="127.0.0.1", port=8771, account_device=False, account=None,
        interval=300, timeout=60.0, webhook=None, webhook_type="generic",
        alert_rules=[], autoshield=False, persistent=False, once=False,
        log=None, json=False,
    )


class FakeLock(object):
    """假账号锁: 直接拿到, 不碰真实锁文件/进程。"""

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def build_engine(tmp, uid, potions=None):
    eng = cok_engine.Engine(make_args())
    eng.daemon = FakeDaemon(eng.args, FakeClient(ARMY))
    eng.account_key = uid
    eng._data_dir = lambda: tmp          # 别碰真实数据
    eng.settings = dict(cok_engine.Engine.DEFAULT_SETTINGS)
    eng.settings_seq = {}
    eng.hunt = {"stamina": 10}           # 低于 huntMinStamina(18)
    eng.hunter = None
    eng.hunter_client = None
    eng._hunter_starting = False
    eng._hunter_lock = None
    eng._save_settings = lambda: None    # 不写盘
    eng.stop_app = lambda: False
    eng._ensure_account = lambda: True   # 别真的去连游戏服
    eng._drop_daemon_client = lambda: None
    eng._set_hunter_starting = lambda *a, **kw: None
    eng._release_hunter_lock = lambda *a, **kw: None
    eng._record_hunt_kills = lambda *a, **kw: None
    eng._close_hunter_client = lambda *a, **kw: None
    eng._lock_key = lambda: None
    eng._hunter_reconnect = lambda: None
    eng._dock_tick = lambda *a, **kw: None
    # 测试机上没有 adb / 没有游戏 App —— 当作"App 不在线"
    eng.app_online = lambda: False
    # 账号锁 / 建连都是真进程与真 TCP —— 换掉, 但**保留哨兵**在猎人构造处停下
    cok_client.account_lock_retry = lambda **kw: FakeLock()
    eng._hunter_open_client = lambda: FakeClient(ARMY)
    if potions:
        cok_stamina.save_items(uid, potions)
    return eng


def run_start(eng, body):
    """跑 _hunter_start, 把构造 AutoHunter 的参数截下来。

    只跑到「构造猎人」为止 —— 用哨兵异常在 Spy.__init__ 里停下,
    后面的起线程/事件都是并发与网络活, 与这个开关无关。
    """
    captured = {}
    real = cok_hunt.AutoHunter

    class Spy(real):
        def __init__(self, client, **kw):
            captured.update(kw)
            raise StopBeforeConnect()

    cok_hunt.AutoHunter = Spy
    try:
        res = eng._hunter_start(body)
    except StopBeforeConnect:
        res = {}
    finally:
        cok_hunt.AutoHunter = real
    return res, captured


def main():
    ok = True
    tmp = tempfile.mkdtemp(prefix="cok-stamina-switch-")
    try:
        # 1) 默认值存在且是 bool —— 回归"这个键根本不存在"的根因
        d = cok_engine.Engine.DEFAULT_SETTINGS
        ok &= check("DEFAULT_SETTINGS 有 huntAutoStamina",
                    "huntAutoStamina" in d)
        ok &= check("huntAutoStamina 默认关",
                    d.get("huntAutoStamina") is False,
                    repr(d.get("huntAutoStamina")))
        ok &= check("DEFAULT_SETTINGS 有 huntMix(默认 1)",
                    d.get("huntMix") == 1, repr(d.get("huntMix")))

        # 2) set-setting 落成真正的 bool
        eng = build_engine(tmp, "uid-set")
        eng._set_setting({"key": "huntAutoStamina", "value": True})
        ok &= check("set-setting True -> True",
                    eng.settings.get("huntAutoStamina") is True,
                    repr(eng.settings.get("huntAutoStamina")))
        eng._set_setting({"key": "huntAutoStamina", "value": "false"})
        ok &= check("set-setting 'false' -> False(不是 bool('false')=True)",
                    eng.settings.get("huntAutoStamina") is False,
                    repr(eng.settings.get("huntAutoStamina")))
        eng._set_setting({"key": "huntAutoStamina", "value": 0})
        ok &= check("set-setting 0 -> False",
                    eng.settings.get("huntAutoStamina") is False,
                    repr(eng.settings.get("huntAutoStamina")))
        eng._set_setting({"key": "huntMix", "value": "3"})
        ok &= check("set-setting huntMix '3' -> 3",
                    eng.settings.get("huntMix") == 3,
                    repr(eng.settings.get("huntMix")))
        eng._set_setting({"key": "huntMix", "value": 9})
        ok &= check("set-setting huntMix 越界 9 -> 夹到 4",
                    eng.settings.get("huntMix") == 4,
                    repr(eng.settings.get("huntMix")))
        eng._set_setting({"key": "huntMix", "value": "abc"})
        ok &= check("set-setting huntMix 非数字 -> 不写入(保持原值)",
                    eng.settings.get("huntMix") == 4,
                    repr(eng.settings.get("huntMix")))

        # 3) 体力低于阈值 + 开关开 + 有药水 => 放行(旧行为直接拒启)
        uid = "unit-switch-%d" % os.getpid()
        p = {"200381": {"uuid": "f" * 32, "count": 3}}
        eng = build_engine(tmp, uid, p)
        try:
            r, cap = run_start(eng, {"level": 1, "num": 10, "autoStamina": True})
            ok &= check("体力10<18 + 开关开 + 有药水 => 没被体力拦",
                        "低于安全阈值" not in str(r.get("error") or ""),
                        str(r.get("error"))[:70])
            ok &= check("开关回写进 settings",
                        eng.settings.get("huntAutoStamina") is True,
                        repr(eng.settings.get("huntAutoStamina")))
            ok &= check("猎人收到 auto_stamina=True",
                        cap.get("auto_stamina") is True,
                        repr(cap.get("auto_stamina")))
            ok &= check("猎人收到药水实例 uuid",
                        (cap.get("stamina_items") or {})
                        .get("200381", {}).get("uuid") == "f" * 32,
                        str(cap.get("stamina_items"))[:70])
            ok &= check("min_stamina 用的是 huntMinStamina",
                        cap.get("min_stamina") == 18,
                        repr(cap.get("min_stamina")))
        finally:
            try:
                os.unlink(cok_stamina.items_path(uid))
            except OSError:
                pass

        # 3b) 游戏 App 还在线 + 开关关 => 直接拒启, 别建连互踢
        #     (这里体力设成 50, 高于阈值 18, 好让拒绝原因来自"App 在线"而不是体力)
        eng_on = build_engine(tmp, "uid-apponline-%d" % os.getpid())
        eng_on.hunt = {"stamina": 50}
        eng_on.app_online = lambda: True
        r_on, cap_on = run_start(eng_on, {"level": 1, "num": 10})
        ok &= check("App 在线 + 开关关 => 拒启并说明",
                    "游戏 App 还在线" in str(r_on.get("error") or ""),
                    str(r_on.get("error"))[:80])
        ok &= check("App 在线时不构造猎人",
                    not cap_on, str(list(cap_on))[:40])

        # 3c) 游戏 App 还在线 + 开关开 + 有药水 => 放行(这是自救路径)
        uid2 = "unit-switch2-%d" % os.getpid()
        eng_on2 = build_engine(tmp, uid2, {"200381": {"uuid": "a" * 32, "count": 1}})
        try:
            eng_on2.app_online = lambda: True
            _r_on2, cap_on2 = run_start(eng_on2, {"level": 1, "num": 10,
                                                  "autoStamina": True})
            ok &= check("App 在线 + 开关开 + 有药水 => 仍然放行",
                        cap_on2.get("auto_stamina") is True,
                        repr(cap_on2.get("auto_stamina")))
        finally:
            try:
                os.unlink(cok_stamina.items_path(uid2))
            except OSError:
                pass

        # 4) 体力低于阈值 + 开关开 + 背包没药水 => 说清原因
        eng2 = build_engine(tmp, "unit-nopotion-%d" % os.getpid())
        r2, _ = run_start(eng2, {"level": 1, "num": 10, "autoStamina": True})
        ok &= check("没药水时提示可读",
                    "体力药水" in str(r2.get("error") or ""),
                    str(r2.get("error"))[:80])

        # 5) 体力低于阈值 + 开关关 => 维持原来的拒绝
        eng3 = build_engine(tmp, uid, p)
        try:
            r3, _ = run_start(eng3, {"level": 1, "num": 10})
            ok &= check("开关关 + 体力不足 => 仍拒启",
                        "低于安全阈值" in str(r3.get("error") or ""),
                        str(r3.get("error"))[:70])
            ok &= check("开关关时不会把 settings 写成 True",
                        eng3.settings.get("huntAutoStamina") is False,
                        repr(eng3.settings.get("huntAutoStamina")))
        finally:
            try:
                os.unlink(cok_stamina.items_path(uid))
            except OSError:
                pass

        # 6) 降级路径透传: _fallback_web_hunt -> _hunter_start 带 autoStamina
        eng4 = build_engine(tmp, "uid-fallback")
        seen = {}

        def spy_hunter_start(body):
            seen.update(body or {})
            return {"ok": True, "note": "spy"}

        eng4._hunter_start = spy_hunter_start
        eng4._ensure_client = lambda: None
        eng4.daemon.client = FakeClient(ARMY)
        eng4.settings["huntAutoStamina"] = True
        eng4._fallback_web_hunt({"num": 1000, "squads": 1, "mix": 1}, "1", "E1")
        ok &= check("降级路径把 autoStamina 透传给 _hunter_start",
                    seen.get("autoStamina") is True,
                    repr(seen.get("autoStamina")))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print()
    if ok:
        print("全部通过")
        return 0
    print("有失败项")
    return 1


if __name__ == "__main__":
    sys.exit(main())