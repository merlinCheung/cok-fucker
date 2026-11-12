#!/usr/bin/env python3
"""联盟功能的单元测试(不连游戏服)。

覆盖:
  * science.data.init -> 联盟科技树解析(在研/满进度/百分比)
  * al.science.fresh  -> 捐献面板三档解析(小写字段名 lowRes/lowNum/...)
  * al.task.*         -> 任务板合并(record 上限 + available 实时计数)
  * al.mission.show   -> 使命阶段进度 + 联盟签到
  * al.donate.rank.today / al.donate.res.info / al.shop.show / al.showhelp
  * 写操作参数: al.task.accept {taskUid} / al.task.award {taskUid}
                al.callhelp {queueId, qType} / al.science.donate {scienceId, option}
  * summary(): 捐献前置条件(科技已攒满 -> 不能捐)、任务位余量
"""
import os
import sys
import tempfile

os.environ["COK_ACCOUNT_LOCK_FILE"] = os.path.join(
    tempfile.gettempdir(), "cok-test-alliance-%d.lock" % os.getpid())
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "core"))
sys.path.insert(0, os.path.join(HERE, "..", "tools"))

import cok_alliance  # noqa: E402

FAILED = []


def check(name, cond, detail=""):
    print("[%s] %s%s" % ("PASS" if cond else "FAIL", name,
                         ("  — " + detail) if detail else ""))
    if not cond:
        FAILED.append(name)
    return bool(cond)


class FakeClient(object):
    def __init__(self, replies=None):
        self.replies = replies or {}
        self.calls = []

    def call(self, cmd, params=None, retries=1):
        self.calls.append((cmd, params))
        r = self.replies.get(cmd)
        if r is None:
            return {"__params__": {"errorCode": "E000000"}}
        if isinstance(r, dict) and "errorCode" in r and len(r) == 1:
            return {"__params__": r}
        return {"__params__": r}


NOW = 1793370000000


def _now():
    return NOW


cok_alliance._now_ms = _now


# ---------------------------------------------------------------------------
# 科技树
# ---------------------------------------------------------------------------
SCIENCE_INIT = {
    "allianceScience": [
        {"scienceId": 251600, "level": 2, "star": 5, "currentPro": 128000,
         "needPro": 128000, "totalPro": 640000, "startTime": 1793360409594,
         "finishTime": 1793432591994, "speedUp": False},
        {"scienceId": 250000, "level": 4, "star": 1, "currentPro": 2440,
         "needPro": 24000, "totalPro": 2440, "startTime": 0, "finishTime": 0},
    ],
    "science": [],
}


def test_science():
    c = FakeClient({"science.data.init": SCIENCE_INIT})
    r = cok_alliance.read_science(c)
    check("科技树读取成功", r.get("ok") is True)
    check("科技树共 2 项", r.get("count") == 2, str(r.get("count")))
    check("在研科技 = 251600", r.get("researching") == "251600", str(r.get("researching")))
    by = {s["scienceId"]: s for s in r.get("list") or []}
    s1 = by.get("251600") or {}
    check("在研科技 researching=True", s1.get("researching") is True)
    check("在研科技 full=True(进度已满)", s1.get("full") is True)
    check("在研科技 percent=100", s1.get("percent") == 100, str(s1.get("percent")))
    s2 = by.get("250000") or {}
    check("未在研科技 researching=False", s2.get("researching") is False)
    check("未满进度 full=False", s2.get("full") is False)
    check("进度百分比 10%", s2.get("percent") == 10, str(s2.get("percent")))


# ---------------------------------------------------------------------------
# 捐献面板
# ---------------------------------------------------------------------------
FRESH = {
    "scienceId": 251600,
    "lowRes": 3, "lowNum": 3000, "lowContribute": 200, "lowProgress": 40,
    "lowResFlag": 0,
    "midRes": 5, "midNum": 10, "midContribute": 1000, "midProgress": 200,
    "midResFlag": 0, "midAvailable": 0,
    "highRes": 3, "highNum": 3000, "highContribute": 5000, "highProgress": 1000,
    "highResFlag": 0, "highAvailable": 0,
}


def test_donate_panel():
    c = FakeClient({"al.science.fresh": FRESH})
    r = cok_alliance.read_donate_panel(c, 251600)
    check("捐献面板读取成功", r.get("ok") is True)
    tiers = {t["key"]: t for t in (r.get("tiers") or [])}
    check("低档 num=3000", (tiers.get("low") or {}).get("num") == 3000)
    check("低档 contribute=200", (tiers.get("low") or {}).get("contribute") == 200)
    check("低档 available=None(服务端不给这个字段)",
          (tiers.get("low") or {}).get("available") is None)
    check("中档 available=0", (tiers.get("mid") or {}).get("available") == 0)
    check("高档 available=0", (tiers.get("high") or {}).get("available") == 0)
    # 参数里 scienceId 必须传对
    check("读取面板传了 scienceId",
          c.calls and c.calls[0][1] == {"scienceId": 251600}, str(c.calls))


# ---------------------------------------------------------------------------
# 任务板
# ---------------------------------------------------------------------------
TASK_RECORD = {
    "freequeueTime": 0, "refreshCount": 0, "itemPublishCount": 0,
    "refreshTime": 1793368914008, "conditionTime": 86400,
    "maxPublishRewardCount": 10, "maxPublishItemUseCount": 100000,
    "acceptCount": 1, "freequeue": 1, "maxPublishCount": 8,
    "itemPublishUseCount": 0, "maxAcceptRewardCount": 10, "gold": 0,
    "maxAcceptCount": 10, "conditionPublishLevel": 10, "nextGold": 50,
    "publishCount": 0, "conditionAcceptLevel": 10,
}
TASK_AVAILABLE = {
    "gold": 0, "nextGold": 50, "freequeueTime": 0,
    "record": {"refreshCount": 0, "itemPublishCount": 0,
               "refreshTime": 1793368914008, "acceptCount": 1,
               "publishCount": 0, "itemRefreshCount": 0,
               "itemPublishUseCount": 0},
    "taskList": [{"uid": "10462f0fc960476d8bbd8f46b24176f1", "stat": 0,
                  "finishTime": 3600000, "taskId": "2910007",
                  "baseReward": "exp,0,9408|goods,36006801,1",
                  "publishUid": "<uid-main>"}],
    "freequeue": 1,
}
TASK_PUBLISHED = {
    "leftRequestCount": 3,
    "taskList": [{"uid": "e79590911f504fba8331e518f9da0240",
                  "publishName": "MissVenom", "publishUid": "282941343002223",
                  "acceptStat": 0, "publishStat": 0, "requested": False,
                  "finishTime": 3600000, "acceptReward": "exp,0,9408",
                  "pic": "g015", "freequeue": 1, "taskId": "2910007"}],
}


def test_task_board():
    c = FakeClient({"al.task.record": TASK_RECORD,
                    "al.task.get.available": TASK_AVAILABLE,
                    "al.task.get.published": TASK_PUBLISHED})
    r = cok_alliance.read_task_board(c)
    check("任务板读取成功", r.get("ok") is True)
    rec = r.get("record") or {}
    check("上限字段来自 al.task.record(maxAcceptCount=10)",
          rec.get("maxAcceptCount") == 10, str(rec.get("maxAcceptCount")))
    check("实时计数来自 available(acceptCount=1)",
          rec.get("acceptCount") == 1, str(rec.get("acceptCount")))
    check("maxPublishCount=8", rec.get("maxPublishCount") == 8)
    check("已发布任务 1 条", len(r.get("published") or []) == 1)
    check("已发布任务带发布人",
          (r.get("published") or [{}])[0].get("publishName") == "MissVenom")
    check("leftRequestCount=3", r.get("leftRequestCount") == 3)


def test_task_write():
    # 接任务: 只传 taskUid
    c = FakeClient({"al.task.accept": {"publishName": "MissVenom",
                                       "acceptUid": "<uid-main>",
                                       "finishTime": 1793371809938,
                                       "record": {"acceptCount": 1}}})
    r = cok_alliance.accept_task(c, "e79590911f504fba8331e518f9da0240")
    check("接取任务成功", r.get("ok") is True)
    check("接任务只传 taskUid 一个参数",
          c.calls[0][1] == {"taskUid": "e79590911f504fba8331e518f9da0240"},
          str(c.calls[0]))
    check("接任务返回发布人", r.get("publishName") == "MissVenom")

    # 领奖: 未完成时服务端回 134042
    c2 = FakeClient({"al.task.award": {"errorCode": "134042"}})
    r2 = cok_alliance.award_task(c2, "abc")
    check("领奖失败时带出错误码", r2.get("ok") is False and
          r2.get("errorCode") == "134042", str(r2))
    check("134042 有中文说明",
          cok_alliance.ERROR_TEXT.get("134042") != "", "缺文案")

    # 缺 taskUid 时不该发命令
    c3 = FakeClient({})
    r3 = cok_alliance.award_task(c3, "")
    check("缺 taskUid 直接拒绝, 不发命令",
          r3.get("ok") is False and not c3.calls)


def test_accept_all():
    c = FakeClient({"al.task.record": TASK_RECORD,
                    "al.task.get.available": TASK_AVAILABLE,
                    "al.task.get.published": TASK_PUBLISHED,
                    "al.task.accept": {"publishName": "MissVenom"}})
    r = cok_alliance.accept_tasks(c)
    check("一键接任务成功", r.get("ok") is True)
    check("接了 1 个任务", len(r.get("acted") or []) == 1, str(r.get("acted")))
    check("接取后余 8 个位置(10 减已占 1 再减新接 1)",
          r.get("left") == 8, str(r.get("left")))


# ---------------------------------------------------------------------------
# 使命 / 签到
# ---------------------------------------------------------------------------
MISSION = {
    "random": [{"missionId": "4900005", "type": 2, "currentValue": 283,
                "conditionValue": "20|100|500", "rewardFlag": "1|1|0",
                "rewardRecord": "0|0|0", "refreshTime": 1793318412187,
                "reward": []}],
    "common": [{"missionId": "4900003", "type": 1, "currentValue": 2896014,
                "conditionValue": "100000|500000|800000",
                "rewardFlag": "1|1|1", "rewardRecord": "0|0|0",
                "refreshTime": 1793318412014, "reward": []}],
    "alliance_sign_in": {"signIn_reward": "251492", "signInReward_state": 0,
                         "signIn_days": 5},
}


def test_mission():
    c = FakeClient({"al.mission.show": MISSION})
    r = cok_alliance.read_mission(c)
    check("使命读取成功", r.get("ok") is True)
    check("签到 5 天一轮", (r.get("signIn") or {}).get("signIn_days") == 5)
    check("今天还没签", (r.get("signIn") or {}).get("signInReward_state") == 0)
    stages = (r.get("random") or [{}])[0].get("stages") or []
    check("random 使命 3 个阶段", len(stages) == 3, str(len(stages)))
    check("第 1 阶段(20)已达成",
          stages and stages[0].get("reached") is True)
    check("第 2 阶段(100)已达成(当前值 283)",
          len(stages) > 1 and stages[1].get("reached") is True)
    check("第 3 阶段(500)未达成",
          len(stages) > 2 and stages[2].get("reached") is False)
    check("第 1 阶段已领奖",
          stages and stages[0].get("claimed") is True)


# ---------------------------------------------------------------------------
# 排行 / 资源池 / 商店 / 求助
# ---------------------------------------------------------------------------
def test_misc_reads():
    c = FakeClient({
        "al.donate.rank.today": {
            "refreshTime": 1793404800000,
            "donateRank": [{"uid": "<uid-main>", "name": "元气少女李逵",
                            "donation": 0, "rank": 3, "power": 347283901,
                            "alliance_honor": 0, "donateTime": 0}]},
        "al.donate.res.info": {
            "res": {"0": 8946161, "21": 89549761},
            "resMax": {"0": 500000000, "21": 80000000},
            "item": [{"213576": 8275}]},
        "al.shop.show": {"alliancePoint": 0, "goods": []},
        "al.showhelp": {"helps": []},
    })
    r = cok_alliance.read_donate_rank(c)
    check("捐献排行读取成功", r.get("ok") is True and len(r.get("list") or []) == 1)
    check("排行项有 uid/名字",
          (r.get("list") or [{}])[0].get("name") == "元气少女李逵")
    res = cok_alliance.read_res(c)
    check("资源池读取成功", res.get("ok") is True)
    check("资源 21 名字带'联盟生命值'",
          (res.get("res") or {}).get("21", {}).get("name", "").find("联盟生命值") >= 0,
          str((res.get("res") or {}).get("21")))
    check("资源 0 没查到权威名字 -> 显示 id",
          (res.get("res") or {}).get("0", {}).get("name", "").startswith("资源#"))
    check("道具列表解析", (res.get("item") or [{}])[0].get("itemId") == "213576")
    shop = cok_alliance.read_shop(c)
    check("商店读取成功", shop.get("ok") is True)
    check("联盟积分为 0", shop.get("alliancePoint") == 0)
    help_ = cok_alliance.read_help(c)
    check("求助读取成功", help_.get("ok") is True)


# ---------------------------------------------------------------------------
# 求助 / 捐献 写操作
# ---------------------------------------------------------------------------
def test_help_and_donate_write():
    c = FakeClient({"al.callhelp": {"success": True}})
    r = cok_alliance.call_help(c, "766302170051128286", 0)
    check("请求帮助成功", r.get("ok") is True)
    check("求助参数 = queueId + qType",
          c.calls[0][1] == {"queueId": "766302170051128286", "qType": 0},
          str(c.calls[0]))
    c2 = FakeClient({"al.helpall": {"success": True}})
    check("帮助全体成功", cok_alliance.help_all(c2).get("ok") is True)

    # 捐献: 服务端拒 -> 按该档位的候选编码依次试
    # ⚠ 期望值从 DONATE_TIERS 推导 —— 编码定死后(单候选)这套断言依然成立
    low_opts = list(cok_alliance.DONATE_TIERS[0][2])
    c3 = FakeClient({"al.science.donate": {"errorCode": "E000000"}})
    r3 = cok_alliance.donate(c3, 251600, "low")
    check("捐献全档被拒时报错", r3.get("ok") is False)
    check("捐献试了该档位的全部 option 候选",
          [x[1]["option"] for x in c3.calls] == low_opts,
          "试了 %s, 期望 %s" % ([x[1]["option"] for x in c3.calls], low_opts))
    check("捐献参数含 scienceId 与 option",
          all(set(x[1].keys()) == {"scienceId", "option"} for x in c3.calls),
          str(c3.calls))
    check("失败时带出错误码 E000000", r3.get("errorCode") == "E000000")

    # 服务端接受第一个 option 时应立即停
    c4 = FakeClient({"al.science.donate": {"success": True}})
    r4 = cok_alliance.donate(c4, 251600, "low")
    check("捐献成功", r4.get("ok") is True)
    check("成功后只发一次", len(c4.calls) == 1, str(c4.calls))
    check("高档 option = 低档 option + 2",
          cok_alliance.DONATE_TIERS[2][2][0] == cok_alliance.DONATE_TIERS[0][2][0] + 2,
          "高档 %s, 低档 %s" % (cok_alliance.DONATE_TIERS[2][2], cok_alliance.DONATE_TIERS[0][2]))


# ---------------------------------------------------------------------------
# summary
# ---------------------------------------------------------------------------
def test_summary():
    st = {
        "science": {"list": [{"scienceId": "251600", "researching": True,
                              "full": True, "percent": 100}],
                    "researching": "251600"},
        "donatePanel": {"ok": True, "canDonate": True, "tiers": []},
        "task": {"record": {"maxAcceptCount": 10, "acceptCount": 1,
                            "maxPublishCount": 8, "publishCount": 0}},
        "mission": {"signIn": {"signIn_days": 5, "signInReward_state": 0}},
        "shop": {"alliancePoint": 7},
    }
    s = cok_alliance.summary(st)
    check("summary: 在研科技", s.get("researching") == "251600")
    check("summary: 科技已满 -> 不能捐", s.get("donateReady") is False)
    check("summary: 给出不能捐的原因",
          "攒满" in (s.get("donateReason") or ""), s.get("donateReason"))
    check("summary: 任务位余量 9", s.get("taskAcceptLeft") == 9)
    check("summary: 发布位余量 8", s.get("taskPublishedLeft") == 8)
    check("summary: 签到 5 天", s.get("signInDays") == 5)
    check("summary: 联盟积分 7", s.get("alliancePoint") == 7)

    st2 = {
        "science": {"list": [{"scienceId": "251600", "researching": True,
                              "full": False, "percent": 40}],
                    "researching": "251600"},
        "donatePanel": {"ok": True, "canDonate": True, "tiers": [{"key": "low"}]},
        "task": {}, "mission": {}, "shop": {},
    }
    s2 = cok_alliance.summary(st2)
    check("summary: 未满进度 -> 可以捐", s2.get("donateReady") is True)


# ---------------------------------------------------------------------------
# 自动捐献
# ---------------------------------------------------------------------------
SCI_FULL = {
    "allianceScience": [
        {"scienceId": 251600, "level": 2, "star": 5, "currentPro": 128000,
         "needPro": 128000, "totalPro": 640000, "startTime": 1793360409594,
         "finishTime": 1793432591994, "speedUp": False},
    ],
}
SCI_HALF = {
    "allianceScience": [
        {"scienceId": 251600, "level": 2, "star": 5, "currentPro": 40000,
         "needPro": 128000, "totalPro": 640000, "startTime": 1793360409594,
         "finishTime": 1793432591994, "speedUp": False},
    ],
}


class SeqClient(object):
    """按调用次数依次回不同响应的假客户端(用来模拟"捐到满")。"""

    def __init__(self, script):
        self.script = script
        self.calls = []

    def call(self, cmd, params=None, retries=1):
        self.calls.append((cmd, params))
        r = self.script.get(cmd)
        if isinstance(r, list):
            return {"__params__": (r.pop(0) if r else {"errorCode": "E000000"})}
        if r is None:
            return {"__params__": {"errorCode": "E000000"}}
        return {"__params__": r}


def test_auto_donate_basic():
    # 1) 没有在研科技
    c = FakeClient({"science.data.init": {"allianceScience": [
        {"scienceId": 250000, "currentPro": 10, "needPro": 100,
         "startTime": 0, "finishTime": 0}]}})
    r = cok_alliance.auto_donate(c)
    check("auto: 没有在研科技就停",
          r.get("stop") == "当前没有正在研究的联盟科技", str(r.get("stop")))
    check("auto: 没有在研时不发任何命令",
          not [x for x in c.calls if x[0].startswith("al.science.donate")])

    # 2) 科技已满 -> 立即停, 不发捐献命令
    c2 = FakeClient({"science.data.init": SCI_FULL})
    r2 = cok_alliance.auto_donate(c2)
    check("auto: 科技已满 -> 达到上限",
          r2.get("capReached") is True, str(r2.get("stop")))
    check("auto: 科技已满时不再发捐献命令",
          not [x for x in c2.calls if x[0] == "al.science.donate"])


def test_auto_donate_stops_at_cap():
    """连捐到服务端回 E100126(已可研究状态)就该停。"""
    script = {
        "science.data.init": SCI_HALF,
        "al.science.fresh": FRESH,
        "al.science.donate": [{"success": True}, {"errorCode": "E100126"}],
    }
    c = SeqClient(script)
    r = cok_alliance.auto_donate(c, tier_mode="low", max_iter=10)
    check("auto: 捐成功 1 次后遇到上限就停",
          len(r.get("acted") or []) == 1, str(r.get("acted")))
    check("auto: 达到上限标记", r.get("capReached") is True and r.get("done") is True)
    check("auto: 停止原因写清楚",
          "满" in (r.get("stop") or ""), r.get("stop"))
    check("auto: 捐了 2 次就停(第二次是上限那次)",
          len([x for x in c.calls if x[0] == "al.science.donate"]) == 2,
          str([x for x in c.calls if x[0] == "al.science.donate"]))


def test_auto_donate_cd_stops():
    """冷却中(E100160)必须停, 不能继续硬捐。"""
    script = {
        "science.data.init": SCI_HALF,
        "al.science.fresh": FRESH,
        "al.science.donate": {"errorCode": "E100160"},
    }
    c = SeqClient(script)
    r = cok_alliance.auto_donate(c, tier_mode="low", max_iter=10)
    check("auto: 冷却中就停", "冷却" in (r.get("stop") or ""), r.get("stop"))
    check("auto: 冷却中不算达到上限", r.get("capReached") is False)
    check("auto: 冷却时只发一次捐献命令",
          len([x for x in c.calls if x[0] == "al.science.donate"]) == 1)


def test_auto_donate_never_resets_gold():
    """⚠ 安全底线: 自动捐献**绝不能**触发金币重置/改捐献目标。"""
    script = {
        "science.data.init": SCI_HALF,
        "al.science.fresh": FRESH,
        "al.science.donate": {"success": True},
    }
    c = SeqClient(script)
    cok_alliance.auto_donate(c, tier_mode="low", max_iter=5)
    banned = ("al.science.research", "al.targetscience.set",
              "al.targetscience.set.new", "al.science.donate.new",
              "al.task.refresh", "al.task.auto.refresh")
    hit = [x for x in c.calls if x[0] in banned]
    check("auto: 没有触发任何金币重置/改目标的命令",
          not hit, "触发了: %s" % [x[0] for x in hit])
    # 再跑一次"捐到满"和"冷却"两种路径, 同样不能碰
    for script2 in ({"science.data.init": SCI_HALF,
                     "al.science.fresh": FRESH,
                     "al.science.donate": [{"success": True},
                                           {"errorCode": "E100126"}]},
                    {"science.data.init": SCI_HALF,
                     "al.science.fresh": FRESH,
                     "al.science.donate": {"errorCode": "E100160"}}):
        c2 = SeqClient(script2)
        cok_alliance.auto_donate(c2, tier_mode="random", max_iter=5)
        hit2 = [x for x in c2.calls if x[0] in banned]
        check("auto: %s 路径也不碰金币重置" % (script2["al.science.donate"].get("errorCode")
                                              if isinstance(script2["al.science.donate"], dict)
                                              else "捐到满"),
              not hit2, "触发了: %s" % [x[0] for x in hit2])


def test_donate_option_fallback_only_on_E000000():
    """换 option 编码只在 E000000(参数无效)时发生, 否则会捐错档位。"""
    low_opts = list(cok_alliance.DONATE_TIERS[0][2])
    c = FakeClient({"al.science.donate": {"errorCode": "E000000"}})
    r = cok_alliance.donate(c, 251600, "low")
    check("donate: 参数无效才换编码(试了该档位全部候选)",
          len(c.calls) == len(low_opts), str(len(c.calls)))
    check("donate: 每次都是同一档位的候选",
          [x[1]["option"] for x in c.calls] == low_opts,
          str([x[1] for x in c.calls]))

    c2 = FakeClient({"al.science.donate": {"errorCode": "E100160"}})
    cok_alliance.donate(c2, 251600, "low")
    check("donate: 冷却时间不换编码(只发一次, 免得跨到别的档位)",
          len(c2.calls) == 1, str(c2.calls))

    c3 = FakeClient({"al.science.donate": {"errorCode": "E100126"}})
    r3 = cok_alliance.donate(c3, 251600, "low")
    check("donate: 已满标记 reachedCap",
          r3.get("reachedCap") is True and r3.get("stop"), str(r3))


def test_pick_tier():
    tiers = [
        {"key": "low", "name": "低档", "num": 3000},
        {"key": "mid", "name": "中档", "num": 10},
        {"key": "high", "name": "高档", "num": 20},
    ]
    check("pick: 固定档位", cok_alliance.pick_tier(tiers, "mid").get("key") == "mid")
    check("pick: 最省资源", cok_alliance.pick_tier(tiers, "cheapest").get("key") == "mid")
    got = {cok_alliance.pick_tier(tiers, "random").get("key") for _ in range(60)}
    check("pick: 随机能覆盖多档", len(got) >= 2, str(got))
    check("pick: 固定到不存在的档位返回 None",
          cok_alliance.pick_tier(tiers, "nope") is None)

    # 可捐档位判定: 低档没 available 字段 -> 可捐; mid/high 按 available
    panel = {"tiers": [
        {"key": "low", "available": None},
        {"key": "mid", "available": 0},
        {"key": "high", "available": 1},
    ]}
    keys = [t["key"] for t in cok_alliance.available_tiers(panel)]
    check("available: 低档默认可捐, mid 被服务端关掉, high 开放",
          keys == ["low", "high"], str(keys))


# ---------------------------------------------------------------------------
# 联盟签到
# ---------------------------------------------------------------------------
MISSION_SIGNED = {
    "random": [], "common": [],
    "alliance_sign_in": {"signIn_reward": "251494", "signInReward_state": 0,
                         "signIn_days": 23},
}
MISSION_ALREADY = {
    "random": [], "common": [],
    "alliance_sign_in": {"signIn_reward": "251494", "signInReward_state": 1,
                         "signIn_days": 23},
}


def test_alliance_signin():
    # 未签 -> 能读出状态
    c = FakeClient({"al.mission.show": MISSION_SIGNED})
    st = cok_alliance.read_sign_in(c)
    check("签到状态读取成功", st.get("ok") is True)
    check("今天还没签", st.get("signed") is False)
    check("连续签到天数 23", st.get("days") == 23, str(st.get("days")))

    # 已签
    c2 = FakeClient({"al.mission.show": MISSION_ALREADY})
    st2 = cok_alliance.read_sign_in(c2)
    check("已签时 signed=True", st2.get("signed") is True)

    # 领奖: alliance.signIn.reward **无参**
    c3 = FakeClient({"alliance.signIn.reward": {
        "reward": {"goods": [{"itemId": "209993", "count": 15},
                             {"itemId": "211997", "count": 591}]}}})
    r = cok_alliance.claim_sign_in(c3)
    check("联盟签到领奖成功", r.get("ok") is True)
    check("领到 2 项", r.get("count") == 2, str(r.get("count")))
    check("签到领奖命令无参数",
          c3.calls and c3.calls[0] == ("alliance.signIn.reward", None),
          str(c3.calls))
    check("领奖明细带道具 id",
          (r.get("goods") or [{}])[0].get("itemId") == "209993")

    # 领奖失败
    c4 = FakeClient({"alliance.signIn.reward": {"errorCode": "E100000"}})
    r4 = cok_alliance.claim_sign_in(c4)
    check("领奖失败带出错误码", r4.get("ok") is False
          and r4.get("errorCode") == "E100000", str(r4))


def main():
    test_science()
    test_donate_panel()
    test_task_board()
    test_task_write()
    test_accept_all()
    test_mission()
    test_misc_reads()
    test_help_and_donate_write()
    test_auto_donate_basic()
    test_auto_donate_stops_at_cap()
    test_auto_donate_cd_stops()
    test_auto_donate_never_resets_gold()
    test_donate_option_fallback_only_on_E000000()
    test_pick_tier()
    test_alliance_signin()
    test_summary()
    print("\n%s" % ("全部通过" if not FAILED else "失败: " + ", ".join(FAILED)))
    return 1 if FAILED else 0


if __name__ == "__main__":
    sys.exit(main())
