#!/usr/bin/env python3
"""港口(newBoat)解析与自动逻辑的单元测试(不连游戏服)。

覆盖:
  * 命令族自动探测: 优先 newBoat, 服务端拒绝则回退旧族(实测 dockTrade 回 102192)
  * 船只状态解析(0 未解锁 / 1 空闲 / 2 贸易中 / 3 可领奖)
  * type=0 **不是船**而是"码头宝箱"(港口活动奖励位) —— 与客户端
    NewNavigationCell:refreshCell 一致: 标成 activity, 状态显示"码头宝箱",
    不算可派遣/可领奖
  * 码头宝箱数据来自 init 推送的 cargo 字段(rewardInfo "goods,{itemId},{count}")
  * 汇总: 可领奖 / 空闲 / 贸易中
  * 一键领取的 rewards 明细(从 array[i].goodsObj 解)
  * 所有族都被拒时给出 errorCode, 而不是抛异常
"""
import json
import os
import sys
import tempfile

os.environ["COK_ACCOUNT_LOCK_FILE"] = os.path.join(
    tempfile.gettempdir(), "cok-test-dock-%d.lock" % os.getpid())
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "core"))
sys.path.insert(0, os.path.join(HERE, "..", "tools"))

import cok_dock  # noqa: E402


class FakeClient(object):
    """可配置的假客户端。

    enabled_families: 允许返回数据的族名集合(其余回 102192)。
    """

    def __init__(self, ships, enabled=("newBoat",), reward_array=None,
                 cargo_reply=None, init_params=None):
        self.ships = ships
        self.enabled = set(enabled)
        self.reward_array = reward_array
        self.calls = []
        self.cargo_reply = cargo_reply
        self.init_params = init_params if init_params is not None else {}

    def call(self, cmd, params=None, retries=1):
        self.calls.append((cmd, params))
        fam = cmd.split(".")[0]
        if fam == "nightCityDock":
            fam = "nightCityDock"
        if cmd == "cargo.reward":
            if self.cargo_reply is None:
                return {"__params__": {"errorCode": "E100148"}}
            return {"__params__": self.cargo_reply}
        if fam not in self.enabled:
            return {"__params__": {"errorCode": "102192"}}
        if cmd.endswith(".data"):
            return {"__params__": {"ships": self.ships, "shipLimit": 4,
                                   "speedTimes": 3}}
        if cmd.endswith(".oneKeyShipReward"):
            return {"__params__": {"array": self.reward_array or []}}
        if cmd.endswith(".oneKeySendShip"):
            return {"__params__": {"array": [{"uuid": "u1"}]}}
        raise AssertionError("未预期的命令 %s" % cmd)


def check(name, cond, detail=""):
    print("[%s] %s%s" % ("PASS" if cond else "FAIL", name,
                         ("  — " + detail) if detail else ""))
    return bool(cond)


def main():
    ok = True

    # ---- 1) 基本解析(用真实抓到的 newBoat.data 结构) ----
    ships = [
        {"uuid": "b99e", "configId": "59887301", "count": 0, "cTime": 1792121558944,
         "endTime": 0, "state": 1, "speedLimit": 0, "type": 0,
         "uuid2": None, "speedTimes": 0, "itemId": ""},
        {"uuid": "331c", "configId": "59887302", "count": 3, "cTime": 1792121558945,
         "endTime": 1792924388312, "state": 2, "speedLimit": 2, "type": 1,
         "speedTimes": 0, "itemId": "36008371"},
        {"uuid": "2907", "configId": "59887303", "count": 2000, "cTime": 1792121558945,
         "endTime": 1792924388310, "state": 2, "speedLimit": 2, "type": 2,
         "speedTimes": 0, "itemId": "36011023"},
        {"uuid": "adc6", "configId": "59887304", "count": 15, "cTime": 1792121558946,
         "endTime": 1792924388311, "state": 2, "speedLimit": 2, "type": 3,
         "speedTimes": 0, "itemId": "36013516"},
    ]
    cl = FakeClient(ships)
    st = cok_dock.read_dock(cl)
    ok &= check("读到 4 条船", len(st["ships"]) == 4, str(len(st["ships"])))
    ok &= check("命令族 = newBoat", st.get("family") == "newBoat", str(st.get("family")))
    ok &= check("状态翻译正确(第一格是码头宝箱)",
                st["ships"][0]["state_text"] == "码头宝箱"
                and st["ships"][1]["state_text"] == "贸易中",
                ",".join(s["state_text"] for s in st["ships"]))
    ok &= check("type=0 标成 activity(不是船)",
                st["ships"][0]["kind"] == "activity"
                and st["ships"][1]["kind"] == "boat")
    ok &= check("type=0 码头宝箱不算可派遣",
                st["ships"][0]["dispatchable"] is False)
    ok &= check("汇总空闲 0 条(码头宝箱被排除)",
                len(st["idle"]) == 0, "idle=%d" % len(st["idle"]))
    ok &= check("汇总贸易中 3 条", len(st["trading"]) == 3)
    ok &= check("码头宝箱单独归类", len(st.get("activity") or []) == 1)
    ok &= check("shipLimit 透传", st.get("shipLimit") == 4)

    # ---- 2) 可领奖船要 type != 0 ----
    cl2 = FakeClient([
        {"uuid": "x1", "state": 3, "type": 1, "itemId": "36008371"},
        {"uuid": "x2", "state": 3, "type": 0},
    ])
    st2 = cok_dock.read_dock(cl2)
    ok &= check("可领奖只算 type!=0 的船",
                len(st2["rewardable"]) == 1 and st2["rewardable"][0]["uuid"] == "x1")

    # ---- 3) 旧族回退(实测 dockTrade 回 102192) ----
    cl3 = FakeClient(ships, enabled=("dockTrade",))
    st3 = cok_dock.read_dock(cl3)
    ok &= check("newBoat 被拒时回退到 dockTrade",
                st3.get("ok") and st3.get("family") == "dockTrade",
                str(st3.get("family")))

    # ---- 4) 所有族都被拒 ----
    cl4 = FakeClient(ships, enabled=())
    st4 = cok_dock.read_dock(cl4)
    ok &= check("全族被拒时给 errorCode 且 ok=False",
                st4.get("ok") is False and st4.get("errorCode") == "102192",
                json.dumps(st4, ensure_ascii=False)[:120])

    # ---- 5) 一键领取 ----
    cl5 = FakeClient(ships, reward_array=[
        {"goodsObj": {"itemId": "36008371", "addNum": 1200, "uuid": "u9"}},
    ])
    r = cok_dock.one_key_reward(cl5)
    ok &= check("一键领取成功", r.get("ok") is True)
    ok &= check("领取条数 = 1", r.get("count") == 1, str(r.get("count")))
    ok &= check("领取明细从 goodsObj 解出",
                r["rewards"][0]["itemId"] == "36008371"
                and r["rewards"][0]["addNum"] == 1200,
                json.dumps(r.get("rewards"), ensure_ascii=False)[:120])
    ok &= check("一键领取命令名正确",
                cl5.calls[-1][0] == "newBoat.oneKeyShipReward", cl5.calls[-1][0])

    # ---- 6) 一键分派 ----
    r2 = cok_dock.one_key_send(cl5)
    ok &= check("一键分派成功", r2.get("ok") is True)
    ok &= check("一键分派命令名正确",
                cl5.calls[-1][0] == "newBoat.oneKeySendShip", cl5.calls[-1][0])

    # ---- 7) 自动逻辑: 没可领的不该动 ----
    cl6 = FakeClient([{"uuid": "a", "state": 1, "type": 1}])
    st6 = cok_dock.read_dock(cl6)
    ok &= check("无可领奖船时 autoReward 不该动作", not st6["rewardable"])
    ok &= check("有空闲船(type!=0)时 autoSend 才动作", len(st6["idle"]) == 1)

    # ---- 8) 码头宝箱: 数据在 init 推送的 cargo 字段里 ----
    class CargoClient(FakeClient):
        def __init__(self, ships, init_params):
            FakeClient.__init__(self, ships)
            self.init_params = init_params

    cg = CargoClient(ships, {"cargo": {"rewardTime": 1792981663685, "times": 1,
                                        "rewardInfo": "goods,200343,50"}})
    rc = cok_dock.read_cargo(cg)
    ok &= check("宝箱读得到奖励物品", rc.get("ok") is True
                and rc.get("itemId") == "200343" and rc.get("count") == 50,
                json.dumps(rc, ensure_ascii=False)[:160])
    ok &= check("宝箱带刷新时间与次数",
                rc.get("rewardTime") == 1792981663685 and rc.get("times") == 1)

    cg2 = CargoClient(ships, {})
    rc2 = cok_dock.read_cargo(cg2)
    ok &= check("没有 init.cargo 时不抛异常, 给出错误",
                rc2.get("ok") is False and "cargo" in str(rc2.get("error")))

    cg3 = CargoClient(ships, {"cargo": {"rewardInfo": "", "rewardTime": 0}})
    rc3 = cok_dock.read_cargo(cg3)
    ok &= check("空 rewardInfo 不炸", rc3.get("ok") is True and not rc3.get("itemId"))

    # ---- 9) 宝箱能不能领: rewardTime <= now ----
    now = 1792998105501
    ok &= check("rewardTime 已过 -> 可领",
                cok_dock.cargo_claimable({"rewardTime": now - 1}, now) is True)
    ok &= check("rewardTime 未到 -> 不可领",
                cok_dock.cargo_claimable({"rewardTime": now + 60000}, now) is False)
    ok &= check("没有 rewardTime -> 不可领",
                cok_dock.cargo_claimable({}, now) is False)

    # ---- 10) 领取码头宝箱: cargo.reward 必须无参, 响应带回新状态 ----
    cg4 = CargoClient(ships, {"cargo": {"rewardTime": now - 1, "times": 1,
                                        "rewardInfo": "goods,200343,50"}})
    cg4.cargo_reply = {
        "reward": {"goods": [{"itemId": "200343", "count": 100, "uuid": "u-x",
                              "para1": "158", "para2": "5000"}]},
        "cargo": {"rewardTime": now + 600000, "times": 2,
                  "rewardInfo": "goods,213444,200"},
        "isDouble": 1,
    }
    cr = cok_dock.claim_cargo(cg4)
    ok &= check("宝箱领取成功", cr.get("ok") is True)
    ok &= check("领取明细解出物品",
                cr["rewards"][0]["itemId"] == "200343" and cr["rewards"][0]["count"] == 100,
                json.dumps(cr.get("rewards"), ensure_ascii=False)[:120])
    ok &= check("cargo.reward 是无参调用",
                cg4.calls[-1] == ("cargo.reward", {}), str(cg4.calls[-1]))
    ok &= check("领取后的新状态写回缓存",
                (cg4.init_params.get("cargo") or {}).get("rewardInfo") == "goods,213444,200"
                and (cg4.init_params.get("cargo") or {}).get("times") == 2,
                json.dumps(cg4.init_params.get("cargo"), ensure_ascii=False))
    ok &= check("领完就不再可领(进入倒计时)",
                cok_dock.cargo_claimable(cg4.init_params.get("cargo"), now) is False)

    # 被拒(E100148 = 还没到时间/次数用完)时也要把状态刷回来
    cg5 = CargoClient(ships, {"cargo": {"rewardTime": now - 1}})
    cg5.cargo_reply = {"errorCode": "E100148",
                       "cargo": {"rewardTime": now + 300000, "times": 3,
                                 "rewardInfo": "goods,213444,200"}}
    cr5 = cok_dock.claim_cargo(cg5)
    ok &= check("E100148 判为未满足条件", cr5.get("ok") is False
                and cr5.get("errorCode") == cok_dock.CARGO_NOT_READY)
    ok &= check("被拒时也刷新状态",
                (cg5.init_params.get("cargo") or {}).get("times") == 3)

    print("\n%s" % ("全部通过" if ok else "存在失败项"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
