#!/usr/bin/env python3
"""EngineManager(并行模型)不变量测试 —— 不连网, 用假引擎。

核心不变量:
  * 每个账号至多一个活跃引擎
  * 活跃集合 = 并行账号 ∪ 当前查看账号
  * prune 会停掉既不并行、也不在看的引擎
跑法: python3 test_engine_manager.py
"""
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

_TMP = tempfile.mkdtemp(prefix="cok-mgr-test-")
os.environ["COK_ACCOUNTS_DIR"] = os.path.join(_TMP, "accounts")
os.environ["COK_DATA_ROOT"] = os.path.join(_TMP, "data")
os.environ.pop("COK_ACCOUNT_LOCK_FILE", None)

import cok_accounts as A  # noqa: E402
import cok_web  # noqa: E402

REAL_ENGINE = cok_web.Engine

PASS = 0
FAIL = 0


def check(cond, name, extra=""):
    global PASS, FAIL
    tag = "[PASS]" if cond else "[FAIL]"
    PASS += 1 if cond else 0
    FAIL += 0 if cond else 1
    print("%s %s%s" % (tag, name, ("  — " + extra) if extra else ""))


class FakeEngine(object):
    """假引擎: 只记 start/stop, 不连网不开线程。"""
    def __init__(self, args, pinned_key=None):
        self.pinned_key = pinned_key
        self.started = False
        self.stopped = False
        self.hunter = None

    def start(self):
        self.started = True

    def stop(self):
        self.stopped = True


class FakeArgs(object):
    pass


#: 注入假引擎会把 cok_web.Engine 换掉。测试跑完必须还原, 否则同进程里
#: 其它测试(比如 test_takeover_and_sky.py)拿到的就是假类了。
_REAL_ENGINE = cok_web.Engine


def _restore_engine():
    cok_web.Engine = _REAL_ENGINE


def _mgr():
    cok_web.Engine = FakeEngine          # 注入假引擎
    cok_web.EngineManager.PARALLEL_FILE = os.path.join(
        A.ACCOUNTS_DIR, ".parallel")
    return cok_web.EngineManager(FakeArgs())


def _seed_accounts():
    full = {"pfId": "x", "platformToken": "x", "deviceId": "x", "uuid": "x",
            "buildCode": "x", "signCode": "x"}
    for uid, label in (("100", "大号"), ("200", "小号"), ("300", "三号")):
        A.save_account(dict(full, gameUid=uid, roleName=label), label=label)
    A.set_active_key("100")


def test_manager():
    _seed_accounts()
    m = _mgr()
    m.start()
    # 初始: 只有查看账号(active=100)在跑
    check(set(k for k in m.engines if k) == {"100"}, "初始只拉起查看账号",
          str(set(m.engines)))
    # 开 200 并行 -> 100(看) + 200(并行) 两个引擎
    m.set_parallel("200", True)
    check(set(k for k in m.engines if k) == {"100", "200"},
          "开并行后两个引擎", str(set(m.engines)))
    # 切换查看到 300 -> 100 不再被看也不并行, 应被 prune; 200 仍并行保留
    m.set_view("300")
    live = set(k for k in m.engines if k)
    check(live == {"200", "300"}, "切视图后 = 并行∪查看", str(live))
    check(A.get_active_key() == "300", "active 指针跟随查看账号")
    # 每账号至多一个引擎(没有重复 key)
    check(len(m.engines) == len(set(m.engines)), "每账号至多一个引擎")
    # 关 200 并行, 且当前不在看它 -> 应被停掉
    eng200 = m.engines.get("200")
    m.set_parallel("200", False)
    check("200" not in m.engines, "关并行后引擎被 prune")
    check(eng200 and eng200.stopped, "被 prune 的引擎确实 stop 了")
    # 批量托管: 有效账号一次性加入运行集，且遵循原有单账号不变量。
    batch_on = m.set_parallel_batch(["100", "200", "不存在"], True)
    check(batch_on.get("ok") and set(batch_on.get("keys", [])) == {"100", "200"},
          "批量开启会忽略无效账号", str(batch_on))
    check(set(k for k in m.engines if k) == {"100", "200", "300"},
          "批量开启后运行集 = 并行∪查看", str(set(m.engines)))
    # 关闭批量托管后，当前查看账号必须继续运行。
    batch_off = m.set_parallel_batch(["100", "200"], False)
    check(batch_off.get("ok") and set(k for k in m.engines if k) == {"300"},
          "批量关闭后保留当前查看账号", str(set(m.engines)))
    # 并行集持久化: 新管理器实例应恢复
    m.set_parallel("300", True)
    m2 = _mgr()
    check("300" in m2.parallel, "并行集持久化后能恢复", str(m2.parallel))
    # 删除账号: 先停引擎 + 撤并行 + 从库删
    m.set_view("100")
    r = m.remove_account("300")
    check(r.get("ok") and A.get_account("300") is None, "删除账号")
    check("300" not in m.parallel and "300" not in m.engines,
          "删除后撤出并行集与引擎表")
    _restore_engine()

def test_automation_safety():
    """自动化本地状态机不需网络或真实游戏凭据。"""
    engine = REAL_ENGINE.__new__(REAL_ENGINE)
    engine.settings = dict(REAL_ENGINE.DEFAULT_SETTINGS)
    engine.automation_state = {"rules": {}}
    engine.automation_history = []
    engine.account_key = "100"
    engine._save_automation_history = lambda: None

    engine._automation_record("autoSign", "waiting", "等待下一次检查", force=True)
    before = len(engine.automation_history)
    engine._automation_record("autoSign", "waiting", "等待下一次检查")
    check(len(engine.automation_history) == before, "等待状态不会重复写入历史")

    engine._automation_record("autoSign", "failed", "签到失败", "网络错误")
    engine._automation_record("autoSign", "failed", "签到失败", "网络错误")
    engine.settings["automationMaxFailures"] = 2
    engine.settings["automationAlertLevel"] = "failures"
    check(len(engine._automation_alerts()) == 1, "达到阈值后出现自动化异常")

    result = engine.action({"action": "automation-recheck", "key": "autoSign"})
    rule = engine._automation_rule("autoSign")
    check(result.get("ok") and rule.get("failures") == 0 and rule.get("last_result") == "waiting",
          "重新检查解除退避但不直接执行游戏操作", str(result))
    check(not engine._automation_alerts(), "重新检查后异常提醒解除")
    _restore_engine()

def main():
    test_manager()
    test_automation_safety()
    print()
    if FAIL:
        print("%d 通过, %d 失败" % (PASS, FAIL))
        return 1
    print("全部通过 (%d)" % PASS)
    return 0


if __name__ == "__main__":
    sys.exit(main())
