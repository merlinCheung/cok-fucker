#!/usr/bin/env python3
"""「一键完成」(CityAssist) 执行器的单元测试(不连游戏服)。

覆盖:
  * 面板 13 项齐全, 分组/代价/类别(free/cost/dock/none)正确
  * run_all 默认(include_costly=False): 只跑**无损**项, 消耗项标"跳过"
  * run_all(include_costly=True): 连消耗项一起跑, 顺序照游戏面板来
  * 资源收取/科研工坊 的 uuid 分组正确
  * 没接消耗项的(英雄试炼/研习/招募/宝藏)不会被瞎发
  * 装卸货物归港口规则, 不重复跑
"""
import os
import sys
import tempfile

os.environ["COK_ACCOUNT_LOCK_FILE"] = os.path.join(
    tempfile.gettempdir(), "cok-test-assist-%d.lock" % os.getpid())
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import cok_assist  # noqa: E402

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
        return {"__params__": r}


BUILD_INFO = {
    "resource": {"food": 1000, "wood": 2000, "iron": 3000},
    "building": [
        {"uuid": "res-1", "building": "412000;20"},
        {"uuid": "res-2", "building": "415000;20"},
        {"uuid": "sci-1", "building": "437000;15"},
        {"uuid": "other", "building": "499000;9"},
    ],
}
GEM_VIEW = {"leftFreeTimes": 3, "maxRcvdTimes": 5}

FREE_REPLIES = {
    "build.info": BUILD_INFO,
    "gem.getDigView": GEM_VIEW,
    "build.collect": {"food": 9000, "wood": 9000},
    "sagatower.collect": {"refreshTime": 1793404800000},
    "civilizationCastle.oneKeyCollect": {
        "itemArray": [{"itemId": "212069", "itemNum": 30}]},
}


def test_panel():
    check("面板 13 项", len(cok_assist.PANEL) == 13, str(len(cok_assist.PANEL)))
    names = [x[1] for x in cok_assist.PANEL]
    for want in ("英雄试炼", "龙塔试炼", "普通研习", "高级研习", "普通招募",
                 "联盟宝藏", "献祭", "宝石挖掘", "装卸货物", "文明结晶",
                 "科研工坊", "资源收取", "一键增产"):
        check("面板含「%s」" % want, want in names)
    kinds = {x[1]: x[4] for x in cok_assist.PANEL}
    check("无损项 = 文明结晶/科研工坊/资源收取",
          all(kinds[k] == "free" for k in ("文明结晶", "科研工坊", "资源收取")),
          str({k: kinds[k] for k in ("文明结晶", "科研工坊", "资源收取")}))
    check("装卸货物归港口规则", kinds["装卸货物"] == "dock", kinds["装卸货物"])
    check("消耗项标成 cost",
          all(kinds[k] == "cost" for k in
              ("英雄试炼", "龙塔试炼", "普通研习", "高级研习", "普通招募",
               "联盟宝藏", "献祭")), str(kinds))


def test_run_free_only():
    c = FakeClient(dict(FREE_REPLIES))
    r = cok_assist.run_all(c)
    check("run_all 成功", r.get("ok") is True, str(r.get("error")))
    cmds = [x[0] for x in c.calls]
    check("发了 build.collect", "build.collect" in cmds)
    check("发了 sagatower.collect", "sagatower.collect" in cmds)
    check("发了 civilizationCastle.oneKeyCollect",
          "civilizationCastle.oneKeyCollect" in cmds)
    check("默认不跑消耗项(龙塔试炼)", "dragontower.quickbattle" not in cmds)
    check("默认不跑献祭", "alliancecivilization.sacrifice" not in cmds)
    bc = [x[1] for x in c.calls if x[0] == "build.collect"][0]
    check("资源收取只带资源建筑 uuid", bc.get("uuid") == "res-1;res-2", str(bc))
    st = [x[1] for x in c.calls if x[0] == "sagatower.collect"][0]
    check("科研工坊只带科研建筑 uuid", st.get("uuid") == "sci-1", str(st))
    names = {s.get("项"): s.get("结果") for s in (r.get("steps") or [])}
    check("三个无损项都完成",
          names.get("资源收取") == "完成" and names.get("科研工坊") == "完成"
          and names.get("文明结晶") == "完成", str(names))
    check("消耗项标成跳过并进 skipped",
          names.get("龙塔试炼") == "跳过" and "龙塔试炼" in (r.get("skipped") or []),
          str(r.get("skipped")))
    check("面板 13 项都返回", len(r.get("panel") or []) == 13)
    check("宝石挖掘标成未接入", names.get("宝石挖掘") == "未接入", str(names))
    check("装卸货物标成跳过(港口规则)",
          names.get("装卸货物") == "跳过", str(names))


def test_run_with_costly():
    c = FakeClient(dict(FREE_REPLIES, **{
        "dragontower.quickbattle": {"success": True},
    }))
    r = cok_assist.run_all(c, include_costly=True)
    cmds = [x[0] for x in c.calls]
    check("含消耗项时跑龙塔试炼(唯一验证过的消耗命令)",
          "dragontower.quickbattle" in cmds)
    check("献祭没在真服验证过 -> 不发",
          "alliancecivilization.sacrifice" not in cmds)
    check("龙塔试炼参数 dealObject=auto",
          [x[1] for x in c.calls if x[0] == "dragontower.quickbattle"][0]
          == {"dealObject": "auto"})
    names = {s.get("项"): s.get("结果") for s in (r.get("steps") or [])}
    check("龙塔试炼标完成", names.get("龙塔试炼") == "完成", str(names))
    check("没接入的消耗项标未接入(不瞎发)",
          names.get("英雄试炼") == "未接入"
          and names.get("普通招募") == "未接入"
          and names.get("献祭") == "未接入", str(names))
    check("没接入的项没有发命令",
          not [x for x in c.calls
               if x[0] in ("newgeneral.luckdraw", "newgeneral.recruit",
                            "magic.receive", "gem.dig")],
          str([x[0] for x in c.calls]))


def test_never_sends_unknown():
    """没接入的消耗项绝不能发命令(会烧钱且参数没确认)。"""
    banned = ("recruit", "luckdraw", "magic.receive", "gem.dig", "formation",
              "sacrifice")
    for costly in (False, True):
        c = FakeClient(dict(FREE_REPLIES))
        cok_assist.run_all(c, include_costly=costly)
        hit = [x[0] for x in c.calls if any(b in x[0].lower() for b in banned)]
        check("include_costly=%s 时没发未接入的命令" % costly, not hit, str(hit))


def test_gem_not_dug():
    c = FakeClient(dict(FREE_REPLIES))
    cok_assist.run_all(c, include_costly=True)
    check("宝石挖掘不发 gem.dig(服务端拒)",
          not [x for x in c.calls if x[0] == "gem.dig"])


def test_summary():
    c = FakeClient({"build.info": BUILD_INFO, "gem.getDigView": GEM_VIEW})
    st = cok_assist.summary(c)
    check("面板摘要成功", st.get("ok") is True)
    items = {i["name"]: i for i in (st.get("items") or [])}
    check("13 项", len(items) == 13, str(len(items)))
    check("资源收取标成可收取", items["资源收取"]["state"] == "可收取",
          items["资源收取"]["state"])
    check("宝石挖掘显示剩余免费次数",
          "3" in items["宝石挖掘"]["state"], items["宝石挖掘"]["state"])
    check("英雄试炼标成需消耗资源",
          "需消耗资源" in items["英雄试炼"]["state"], items["英雄试炼"]["state"])
    check("装卸货物标成由港口规则处理",
          "港口" in items["装卸货物"]["state"], items["装卸货物"]["state"])


def main():
    test_panel()
    test_run_free_only()
    test_run_with_costly()
    test_never_sends_unknown()
    test_gem_not_dug()
    test_summary()
    print("\n%s" % ("全部通过" if not FAILED else "失败: " + ", ".join(FAILED)))
    return 1 if FAILED else 0


if __name__ == "__main__":
    sys.exit(main())
