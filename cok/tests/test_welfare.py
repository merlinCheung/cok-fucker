#!/usr/bin/env python3
"""福利中心(每日好礼 / 龙之馈赠)的单元测试(不连游戏服)。

覆盖:
  * everydayexchange.data / .reward 的解析与领取
  * userpayreward.newinfo 的解析(多个 exchangeId / rewardDays)
  * "谁能领"的判定(买过 or 活动开 / 今天领没领)
  * claim_dragon_gift 的参数(exchangeId + specialReward 都要传)
  * claimable_count 计数
"""
import json
import os
import sys
import tempfile

os.environ["COK_ACCOUNT_LOCK_FILE"] = os.path.join(
    tempfile.gettempdir(), "cok-test-welfare-%d.lock" % os.getpid())
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "core"))
sys.path.insert(0, os.path.join(HERE, "..", "tools"))

import cok_welfare  # noqa: E402


class FakeClient(object):
    """按命令名回预设响应的假客户端。"""

    def __init__(self, replies=None):
        self.replies = replies or {}
        self.calls = []

    def call(self, cmd, params=None, retries=1):
        self.calls.append((cmd, params))
        r = self.replies.get(cmd)
        if r is None:
            return {"__params__": {"errorCode": "E000000"}}
        return {"__params__": r}


def check(name, cond, detail=""):
    print("[%s] %s%s" % ("PASS" if cond else "FAIL", name,
                         ("  — " + detail) if detail else ""))
    return bool(cond)


DAILY_DATA = {
    "freeRewarded": True,
    "freeReward": "256844",
    "payRewarded": False,
    "payReward": "256845",
    "commonExchangeIds": "765880;765881",
}

DRAGON_INFO = {
    "currDay": 1,
    "configArray": [
        {"exchangeId": "760359", "rewardId": "255801", "day": 1,
         "rewards": [{"type": "7", "value": {"num": 30, "id": "36006801"}},
                     {"type": "7", "value": {"num": 2500, "id": "211316"}}],
         "specialRewards": []},
        {"exchangeId": "760359", "rewardId": "249764", "day": 0, "rewards": [],
         "specialRewards": []},
    ],
    "processConfigArray": [],
    "760359": {"isBuy": True, "rewardDays": "0;1", "specialRewardDays": "",
               "specialActivityOpen": False, "process": 10, "processStr": ""},
    "764116": {"isBuy": False, "rewardDays": "", "specialRewardDays": "",
               "specialActivityOpen": False, "process": 0, "processStr": ""},
}


def main():
    ok = True

    # ---- 1) 每日好礼: 读 ----
    cl = FakeClient({"everydayexchange.data": DAILY_DATA})
    dg = cok_welfare.read_daily_gift(cl)
    ok &= check("每日好礼读到", dg.get("ok") is True)
    ok &= check("freeRewarded 解析成 bool", dg.get("freeRewarded") is True)
    ok &= check("充值奖励单独透传(脚本不碰)",
                dg.get("payRewarded") is False and dg.get("payReward") == "256845")
    ok &= check("命令名对", cl.calls[-1][0] == "everydayexchange.data")

    # ---- 2) 每日好礼: 领 ----
    cl2 = FakeClient({"everydayexchange.reward": {
        "rewardArray": [{"type": "7", "value": {"num": 100, "id": "200200"}}]}})
    r = cok_welfare.claim_daily_gift(cl2)
    ok &= check("每日好礼领取成功", r.get("ok") is True and r.get("count") == 1)
    ok &= check("奖励明细解出",
                r["rewards"][0]["itemId"] == "200200" and r["rewards"][0]["num"] == 100)
    ok &= check("领取是无参调用", cl2.calls[-1] == ("everydayexchange.reward", {}))

    # 已被领过 -> 业务错误码
    cl3 = FakeClient({"everydayexchange.reward": {"errorCode": "101312"}})
    r3 = cok_welfare.claim_daily_gift(cl3)
    ok &= check("已领取时给 errorCode(不抛异常)",
                r3.get("ok") is False and r3.get("errorCode") == "101312")

    # ---- 3) 龙之馈赠: 读 ----
    cl4 = FakeClient({"userpayreward.newinfo": DRAGON_INFO})
    dr = cok_welfare.read_dragon_gift(cl4)
    ok &= check("龙之馈赠读到", dr.get("ok") is True)
    ok &= check("currDay 解析", dr.get("currDay") == 1)
    ok &= check("黑龙挑出来", dr.get("blackId") == "760359")
    dragons = dr.get("dragons") or {}
    ok &= check("两条龙都解析出来", set(dragons) == {"760359", "764116"})
    black = dragons.get("760359") or {}
    ok &= check("黑龙今天已领(rewardDays 含 1)",
                black.get("claimed_today") is True and black.get("claimable") is False)
    blue = dragons.get("764116") or {}
    ok &= check("蓝龙没买 -> 不可领",
                blue.get("isBuy") is False and blue.get("claimable") is False)
    today = dr.get("today") or []
    ok &= check("今天的奖励配置取出来了",
                len(today) == 1 and today[0]["exchangeId"] == "760359"
                and len(today[0]["rewards"]) == 2,
                json.dumps(today, ensure_ascii=False)[:160])

    # 今天没领 -> 可领
    info2 = json.loads(json.dumps(DRAGON_INFO))
    info2["760359"]["rewardDays"] = "0"
    cl5 = FakeClient({"userpayreward.newinfo": info2})
    dr2 = cok_welfare.read_dragon_gift(cl5)
    ok &= check("今天没领 -> 可领",
                (dr2["dragons"]["760359"] or {}).get("claimable") is True)

    # 活动开着 + 没买 -> 普通可领、尊享不可领
    info3 = json.loads(json.dumps(DRAGON_INFO))
    info3["currDay"] = 2
    info3["760359"]["rewardDays"] = "0;1"
    info3["760359"]["specialActivityOpen"] = True
    info3["764116"]["rewardDays"] = ""
    info3["764116"]["specialActivityOpen"] = True
    cl6 = FakeClient({"userpayreward.newinfo": info3})
    dr3 = cok_welfare.read_dragon_gift(cl6)
    b3 = dr3["dragons"]["760359"]
    ok &= check("买过+活动开 -> 普通和尊享都可领",
                b3.get("claimable") is True and b3.get("special_claimable") is True)
    b3b = dr3["dragons"]["764116"]
    ok &= check("活动开但没买 -> 只有普通",
                b3b.get("claimable") is True and b3b.get("special_claimable") is False)

    # ---- 4) 龙之馈赠: 领(参数必须齐全) ----
    cl7 = FakeClient({"userpayreward.newaccept": {
        "rewardArray": [{"type": "7", "value": {"num": 30, "id": "36006801"}}]}})
    r7 = cok_welfare.claim_dragon_gift(cl7, "760359", False)
    ok &= check("龙之馈赠领取成功", r7.get("ok") is True and r7.get("count") == 1)
    ok &= check("newaccept 带齐 exchangeId + specialReward",
                cl7.calls[-1] == ("userpayreward.newaccept",
                                  {"exchangeId": "760359", "specialReward": False}),
                str(cl7.calls[-1]))
    cl8 = FakeClient({"userpayreward.newaccept": {"errorCode": "E100171"}})
    r8 = cok_welfare.claim_dragon_gift(cl8, "760359", True)
    ok &= check("条件不满足时给 errorCode",
                r8.get("ok") is False and r8.get("errorCode") == "E100171")

    # ---- 5) 汇总与计数 ----
    cl9 = FakeClient({"everydayexchange.data": DAILY_DATA,
                      "userpayreward.newinfo": DRAGON_INFO})
    allst = cok_welfare.read_all(cl9)
    ok &= check("两个都读到", allst["daily_gift"].get("ok") and allst["dragon_gift"].get("ok"))
    ok &= check("今天都领过 -> 可领 0 项", cok_welfare.claimable_count(allst) == 0)
    info4 = json.loads(json.dumps(DRAGON_INFO))
    info4["760359"]["rewardDays"] = "0"
    info4["everydayexchange"] = {"freeRewarded": False}
    cl10 = FakeClient({"everydayexchange.data": {"freeRewarded": False,
                                                 "freeReward": "256844"},
                       "userpayreward.newinfo": info4})
    allst2 = cok_welfare.read_all(cl10)
    ok &= check("两项都能领时计数 = 2", cok_welfare.claimable_count(allst2) == 2,
                str(cok_welfare.claimable_count(allst2)))

    # 单个功能挂了不影响另一个
    cl11 = FakeClient({"userpayreward.newinfo": DRAGON_INFO})
    allst3 = cok_welfare.read_all(cl11)
    ok &= check("单个命令失败不影响另一个",
                allst3["daily_gift"].get("ok") is False
                and allst3["dragon_gift"].get("ok") is True)

    print("\n%s" % ("全部通过" if ok else "存在失败项"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
