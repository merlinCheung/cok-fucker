#!/usr/bin/env python3
"""自动开罩(被攻击触发)的单元测试(不连游戏服、不写任何文件)。

覆盖(2026-10-26 修的三个坑):
  * 收到 push.world.injured -> 真的发 onekeybuff.use
  * 罩还剩很多时间 -> 不重复开(别白烧 8 小时的道具)
  * 罩快到期 -> 允许续
  * 服务端静默不生效(无 shieldEndTime) -> 判失败并报出来, 不装作成功
  * 冷却期内不再开
"""
import os
import sys
import time
import tempfile
import types

os.environ["COK_ACCOUNT_LOCK_FILE"] = os.path.join(
    tempfile.gettempdir(), "cok-test-shield-%d.lock" % os.getpid())
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import cok_daemon as D  # noqa: E402


class FakeClient(object):
    """假客户端: 只实现自动开罩用到的那几个方法。"""

    def __init__(self, use_reply=None, status_end_ms=0):
        self.pushes = []
        self.calls = []
        self.use_reply = use_reply if use_reply is not None else {
            "shieldEndTime": 1793000000000, "deal": [{"itemId": "200410"}]}
        self.status_end_ms = status_end_ms

    def call(self, cmd, params=None, retries=1):
        self.calls.append((cmd, params))
        if cmd == "onekeybuff.use":
            return {"__params__": self.use_reply}
        if cmd == "show.status.item":
            items = []
            if self.status_end_ms:
                items.append({"type2": 1, "startTime": 1, "endTime": self.status_end_ms})
            return {"__params__": {"statusItems": items}}
        raise AssertionError("未预期的命令 %s" % cmd)

    def take_pushes(self):
        out = list(self.pushes)
        self.pushes = []
        return out

    def close(self):
        pass


def make_daemon(**over):
    args = types.SimpleNamespace(
        webhook=None, webhook_type="generic", alert_rules=[], log=None,
        shield_slot=1, shield_cover_old=1, shield_cooldown=600.0,
        shield_refresh_before=300,
        shield_trigger=["push.world.injured", "push.world.cannon.injured",
                        "push.world.march.fail"],
        shield_trigger_force=["push.world.injured"],
    )
    for k, v in over.items():
        setattr(args, k, v)
    d = D.Daemon(args)
    d.events = []
    d.emit = lambda kind, payload: d.events.append((kind, payload))
    d.alert.push = lambda *a, **k: False
    return d


def check(name, cond, detail=""):
    print("[%s] %s%s" % ("PASS" if cond else "FAIL", name,
                         ("  — " + detail) if detail else ""))
    return bool(cond)


NOW = 1793000000000


def main():
    ok = True

    # ---- 1) 被攻击 -> 真的开罩 ----
    d = make_daemon()
    c = FakeClient()
    d.client = c
    c.pushes.append({"__cmd__": "push.world.injured", "__params__": {}})
    d.autoshield({"now": NOW})
    used = [x for x in c.calls if x[0] == "onekeybuff.use"]
    ok &= check("被攻击会发 onekeybuff.use", len(used) == 1, str(used))
    ok &= check("参数带槽位和 coverOld",
                used and used[0][1] == {"type": 1, "coverOld": True},
                str(used[0][1]) if used else "")
    kinds = [e[0] for e in d.events]
    ok &= check("有 shield_trigger 事件", "shield_trigger" in kinds, str(kinds))
    ok &= check("结果判为成功",
                any(k == "shield_result" and e.get("ok") for k, e in d.events),
                str(d.events))

    # ---- 2) 罩还剩很久 -> 不重复开(别白烧道具) ----
    d2 = make_daemon()
    c2 = FakeClient()
    d2.client = c2
    d2.shield_end_ms = NOW + 8 * 3600 * 1000        # 还剩 8 小时
    c2.pushes.append({"__cmd__": "push.world.injured", "__params__": {}})
    d2.autoshield({"now": NOW})
    ok &= check("罩还在生效时不重复开",
                not [x for x in c2.calls if x[0] == "onekeybuff.use"],
                str(c2.calls))
    ok &= check("给出 shield_skip 事件",
                any(k == "shield_skip" for k, _ in d2.events), str(d2.events))

    # ---- 3) 罩快到期 -> 允许续 ----
    d3 = make_daemon()
    c3 = FakeClient()
    d3.client = c3
    d3.shield_end_ms = NOW + 60 * 1000              # 还剩 1 分钟
    c3.pushes.append({"__cmd__": "push.world.injured", "__params__": {}})
    d3.autoshield({"now": NOW})
    ok &= check("罩快到期时允许续开",
                len([x for x in c3.calls if x[0] == "onekeybuff.use"]) == 1,
                str(c3.calls))

    # ---- 4) 服务端静默不生效 -> 判失败, 不装作成功 ----
    d4 = make_daemon()
    c4 = FakeClient(use_reply={"deal": []}, status_end_ms=0)
    d4.client = c4
    c4.pushes.append({"__cmd__": "push.world.injured", "__params__": {}})
    d4.autoshield({"now": NOW})
    ok &= check("静默失败时判为失败",
                any(k == "shield_result" and not e.get("ok") for k, e in d4.events),
                str(d4.events))
    ok &= check("静默失败时给出 shield_fail",
                any(k == "shield_fail" for k, _ in d4.events), str(d4.events))

    # ---- 5) 冷却期内不再开 ----
    d5 = make_daemon()
    c5 = FakeClient()
    d5.client = c5
    d5.shield_last = time.time()   # 刚刚开过 -> 冷却中
    c5.pushes.append({"__cmd__": "push.world.injured", "__params__": {}})
    d5.autoshield({"now": NOW})
    ok &= check("冷却期内不再开",
                not [x for x in c5.calls if x[0] == "onekeybuff.use"], str(c5.calls))

    # ---- 6) 非触发推送不动 ----
    d6 = make_daemon()
    c6 = FakeClient()
    d6.client = c6
    c6.pushes.append({"__cmd__": "push.al.science", "__params__": {}})
    d6.autoshield({"now": NOW})
    ok &= check("无关推送不触发开罩", not c6.calls, str(c6.calls))

    print("\n%s" % ("全部通过" if ok else "存在失败项"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
