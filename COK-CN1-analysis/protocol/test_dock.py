#!/usr/bin/env python3
"""港口(newBoat)解析与自动逻辑的单元测试(不连游戏服)。

覆盖:
  * 命令族自动探测: 优先 newBoat, 服务端拒绝则回退旧族(实测 dockTrade 回 102192)
  * 船只状态解析(0 未解锁 / 1 空闲 / 2 贸易中 / 3 可领奖)
  * type=0 是空船(无货物), 不算可派遣/可领奖 —— 与客户端 NewNavigationCtl 一致
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
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import cok_dock  # noqa: E402


class FakeClient(object):
    """可配置的假客户端。

    enabled_families: 允许返回数据的族名集合(其余回 102192)。
    """

    def __init__(self, ships, enabled=("newBoat",), reward_array=None):
        self.ships = ships
        self.enabled = set(enabled)
        self.reward_array = reward_array
        self.calls = []

    def call(self, cmd, params=None, retries=1):
        self.calls.append((cmd, params))
        fam = cmd.split(".")[0]
        if fam == "nightCityDock":
            fam = "nightCityDock"
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
    ok &= check("状态翻译正确",
                st["ships"][0]["state_text"] == "空闲"
                and st["ships"][1]["state_text"] == "贸易中",
                ",".join(s["state_text"] for s in st["ships"]))
    ok &= check("type=0 空船不算可派遣",
                st["ships"][0]["dispatchable"] is False)
    ok &= check("汇总空闲 0 条(type=0 空船被排除)",
                len(st["idle"]) == 0, "idle=%d" % len(st["idle"]))
    ok &= check("汇总贸易中 3 条", len(st["trading"]) == 3)
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

    print("\n%s" % ("全部通过" if ok else "存在失败项"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
