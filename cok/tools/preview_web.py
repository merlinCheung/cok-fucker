#!/usr/bin/env python3
"""网页控制台的**离线预览**服务(不连游戏服、不碰设备)。

用途:
  * 改版式时不用占用账号连接, 也能看到"已连接"状态下页面长什么样
  * 设备没插上时, 也能确认页面本身没有渲染问题
  * 给不熟悉这套协议的人演示界面

它复用真正的 cok_web.Engine + cok_webui.html, 只把 daemon 换成一个
**假数据源**, 因此前端渲染路径和线上完全一致。

跑法:
    python3 preview_web.py --port 8771
    打开 http://127.0.0.1:8771/?t=<token>
"""

import argparse
import json
import os
import random
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "core"))

import cok_web  # noqa: E402

GAME_PKG = cok_web.GAME_PKG


class MockClient(object):
    """假客户端: 只实现网页用到的两个调用。"""

    def __init__(self, daemon):
        self.daemon = daemon
        self._spy_done = False

    def call(self, cmd, params=None):
        if cmd == "onekeybuff.use":
            return {"__params__": {"shieldEndTime": self.daemon.shield_end_ms}}
        if cmd == "queue.ccd":
            return {"__params__": {}}
        if cmd == "onekeybuff.get":
            return {"__params__": {"backList": [
                {"type": 1, "name": "",
                 "statusList": [{"itemId": "200410", "num": 12}]},
                {"type": 2, "name": "", "statusList": []},
                {"type": 3, "name": "", "statusList": []}]}}
        if cmd == "show.status.item":
            return {"__params__": {"statusItems": [
                {"type2": 1, "startTime": int(time.time() * 1000) - 3600_000,
                 "endTime": int(time.time() * 1000) + 8 * 3600_000}]}}
        if cmd == "newBoat.data":
            return {"__params__": {"ships": [dict(s) for s in self.daemon.dock_ships],
                                  "shipLimit": 4, "speedTimes": 3}}
        if cmd == "newBoat.oneKeyShipReward":
            got = [s for s in self.daemon.dock_ships
                   if s.get("state") == 3 and s.get("type") not in (0, None)]
            for s in self.daemon.dock_ships:
                if s.get("state") == 3:
                    s["state"] = 1
            return {"__params__": {"array": [
                {"uuid": s.get("uuid"),
                 "goodsObj": {"itemId": "200201", "addNum": 1200,
                              "uuid": s.get("uuid")}}
                for s in got]}}
        if cmd == "newBoat.oneKeySendShip":
            n = 0
            for s in self.daemon.dock_ships:
                if s.get("state") == 1 and s.get("type") not in (0, None):
                    s["state"] = 2
                    n += 1
            return {"__params__": {"array": [{"uuid": s.get("uuid")}
                                             for s in self.daemon.dock_ships
                                             if s.get("state") == 2][:n]}}
        if cmd == "dockTrade.data":
            # 旧族: 服务端回 102192(功能未开启) —— 保留用于验证回退逻辑
            return {"__params__": {"errorCode": "102192"}}
        if cmd == "search.player.spy":
            # 玩家坐标查询 mock: 第一次回候选, 第二次回 location
            if not getattr(self, "_spy_done", False):
                self._spy_done = True
                return {"__params__": {"array": [
                    {"name": "示例领主", "uid": "u-demo-1"},
                    {"name": "示例领主", "uid": "u-demo-2"}]}}
            return {"__params__": {"location": 1128213, "time": 1}}
        return {"__params__": {}}

    def close(self):
        pass


class MockDaemon(object):
    """假 daemon: 返回一份结构与真实解析结果一致的样例数据。"""

    def __init__(self, args):
        self.args = args
        self.client = None
        self.queues = []
        self.shield_end_ms = int((time.time() + 3600) * 1000)
        self.dock_ships = []
        self.alert = cok_web.D.Alert(None, "generic", list(cok_web.D.ALL_RULES))
        self.server_now = int(time.time() * 1000)

    def ctx(self):
        lt = time.localtime(time.time() + 8 * 3600)
        return {"today": lt.tm_mday, "month": lt.tm_mon,
                "now": self.server_now, "date": time.strftime("%Y-%m-%d", lt)}

    def connect(self):
        self.client = MockClient(self)
        self.emit("connected", {"host": "preview.local", "port": 32231,
                                "key_id": 0, "note": "离线预览, 未连真实游戏服"})

    def poll_once(self):
        now = int(time.time() * 1000)
        self.last_state = {
            "dailySign": {
                "本月已签到": 12,
                "今天已签": True,
                "本月签到天数": 12,
                "剩余次数": 8,
            },
            "dailyQuest": {
                "周任务可领奖励": [57621751, 57621752, 57621760],
                "可领日常任务": [
                    {"id": 57621751, "次数": 1},
                    {"id": 57621752, "次数": 1},
                    {"id": 57621753, "次数": 0},
                ],
                "日常任务": [{"id": 57621755, "进度": 3, "目标": 5}],
            },
            "lordTask": {
                "可领奖励": [33101001, 33101002],
                "任务": [{"id": 33101001, "进度": 2, "目标": 2}],
            },
            "storyTask": {
                "章节": 7,
                "可领奖励": [254310, 254311],
                "任务": [{"id": 33102001, "进度": 1, "目标": 3}],
            },
            "boss": {
                "联盟": "第七天堂",
                "Boss": [{"id": 6001, "名称": "泰坦", "血量": 1200000, "已伤害": 380000}],
                "次数": 3,
            },
            "overview": {
                "建造中": [{"id": 1001, "剩余": 120}],
                "训练中": [{"id": 107012, "数量": 200, "剩余": 300}],
                "行军中": [],
                "联盟捐献": [{"id": 1002, "数量": 1}],
            },
            "buildQueue": {
                "金币": 37230,
                "队列": [
                    {"uuid": "q-1", "type": 1, "totalTime": 3600, "startTime": now - 600,
                     "itemObj": {"building": 1001}},
                    {"uuid": "q-2", "type": 5, "totalTime": 7200, "startTime": now - 1200,
                     "itemObj": {"building": 1002}},
                ],
            },
        }
        self.queues = [
            {"uuid": "q-1", "qid": 1, "type": 1, "totalTime": 3600,
             "startTime": now - 600, "endTime": now + 3000,
             "itemObj": {"building": 1001}},
            {"uuid": "q-2", "qid": 2, "type": 5, "totalTime": 7200,
             "startTime": now - 1200, "endTime": now + 6000,
             "itemObj": {"building": 1002}},
            {"uuid": "q-3", "qid": 3, "type": 9, "totalTime": 0, "startTime": 0,
             "endTime": 0, "itemObj": {}},
        ]
        self.shield_end_ms = int((time.time() + 3600) * 1000)

    def auto_sign(self, ctx):
        self.emit("sign", {"note": "预览: 已触发签到"})

    def claim(self, ctx):
        self.emit("claim", {"note": "预览: 已触发领奖"})

    def autoshield(self, ctx):
        pass

    def emit(self, kind, payload):
        pass


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8771)
    ap.add_argument("--token", help="访问 token(默认自动生成)")
    ap.add_argument("--no-token", action="store_true")
    ap.add_argument("--mock-dock", action="store_true",
                    help="模拟港口有船可领/在途/空闲")
    ap.add_argument("--mock-hunt", action="store_true",
                    help="模拟 4 队并行进行中(预览进度表界面)")
    args = ap.parse_args()

    engine_args = argparse.Namespace(
        host=args.host, port=args.port, account_device=False, account={},
        interval=300, timeout=5.0, webhook=None, webhook_type="generic",
        alert_rules=list(cok_web.D.ALL_RULES), autoshield=True,
        speedup_item="200201", speedup_count=1, speedup_queue_type=1,
        shield_slot=1, shield_cover_old=1, shield_cooldown=600.0,
        shield_trigger=[], shield_trigger_force=[], persistent=False,
        watch=list(cok_web.D.WATCHERS.keys()), once=False, retry_delay=10.0,
        claim=False, claim_limit=5, claim_max_total=20, auto_sign=False,
        speedup=False, speedup_gold=False, log=None, json=False,
    )
    eng = cok_web.Engine(engine_args)
    eng.daemon = MockDaemon(engine_args)
    eng._ensure_account = lambda: True
    eng.app_online = lambda: False
    # 离线预览不连真实游戏服, 不该抢真账号的跨进程锁
    eng.offline_preview = True

    # 造几条事件, 让事件流不是空的
    base = time.time() - 600
    for i, (kind, data) in enumerate([
        ("connected", {"host": "preview.local", "port": 32231}),
        ("sign", {"note": "预览: 已完成今日签到"}),
        ("claim", {"note": "预览: 领取了 2 个奖励"}),
        ("state", {"name": "dailySign", "value": "已签到"}),
        ("shield_manual", {"slot": 1, "result": {"shieldEndTime": eng.daemon.shield_end_ms}}),
    ]):
        eng.events.append({"ts": time.strftime("%H:%M:%S",
                                               time.localtime(base + i * 37)),
                           "kind": kind, "data": data})

    # 体力 / 野怪状态也用假数据
    eng.hunt = {
        "stamina": 82, "stamina_max": 100, "lv_low": 1, "lv_high": 3,
        "max_level": 30, "status": 0,
        "format": "107012,200", "recover_per_min": 0.46,
    }

    # 模拟"4 队并行进行中", 用来预览进度表界面(不消耗任何体力)
    if args.mock_hunt:
        eng.hunter = {
            "running": True, "kills": 7, "fails": 0, "level": 15, "num": 5000,
            "troop": "107110", "stamina": 42, "stamina_max": 100,
            "last": {"x": 473, "y": 939, "index": 1128213, "troop": "107110",
                     "num": 5000, "ok": True},
            "note": "等部队回来(还有 3 队在外)",
            "recover_per_min": 0.46, "troops_out": 15000,
            "wait_for": "等部队回来(还有 3 队在外)",
            "squad_max": 4,
            "squads": [
                {"slot": 1, "army_id": "107110", "name": "狮鹫突袭者", "num": 5000,
                 "state": "marching", "x": 473, "y": 939, "index": 1128213,
                 "kills": 3, "fails": 0, "out": 5000, "elapsed": 18, "base_march": 0},
                {"slot": 2, "army_id": "107012", "name": "蛮族督军", "num": 5000,
                 "state": "marching", "x": 501, "y": 927, "index": 1113028,
                 "kills": 2, "fails": 0, "out": 5000, "elapsed": 11, "base_march": 0},
                {"slot": 3, "army_id": "107111", "name": "天马骑士", "num": 5000,
                 "state": "marching", "x": 545, "y": 940, "index": 1128941,
                 "kills": 2, "fails": 0, "out": 5000, "elapsed": 6, "base_march": 0},
                {"slot": 4, "army_id": "107212", "name": "修罗射手", "num": 1000,
                 "state": "idle", "x": None, "y": None, "index": None,
                 "kills": 0, "fails": 0, "out": 0, "elapsed": 0, "base_march": None,
                 "note": "体力只够 3 队(等恢复)"},
            ],
        }

    # 模拟港口(码头航海贸易)状态 —— 命令族 newBoat(实测启用)
    if args.mock_dock:
        eng.daemon.dock_ships = [
            {"uuid": "s1", "configId": "59887301", "state": 3, "type": 1,
             "itemId": "36008371", "count": 3, "endTime": 0, "speedTimes": 0},
            {"uuid": "s2", "configId": "59887302", "state": 2, "type": 1,
             "itemId": "36011023", "count": 2000,
             "endTime": int(time.time() * 1000) + 3600_000, "speedTimes": 1},
            {"uuid": "s3", "configId": "59887303", "state": 1, "type": 2,
             "itemId": "36013516", "count": 15, "endTime": 0, "speedTimes": 0},
            {"uuid": "s4", "configId": "59887304", "state": 1, "type": 0,
             "itemId": "", "count": 0, "endTime": 0, "speedTimes": 0},
        ]
        eng.dock_state = {
            "ok": True,
            "family": "newBoat",
            "shipLimit": 4,
            "ships": [
                {"uuid": "s1", "configId": "59887301", "state": 3, "state_text": "可领奖",
                 "type": 1, "dispatchable": False, "rewardable": True,
                 "itemId": "36008371", "count": 3, "endTime": 0, "speedTimes": 0},
                {"uuid": "s2", "configId": "59887302", "state": 2, "state_text": "贸易中",
                 "type": 1, "dispatchable": False, "rewardable": False,
                 "itemId": "36011023", "count": 2000,
                 "endTime": int(time.time() * 1000) + 3600_000, "speedTimes": 1},
                {"uuid": "s3", "configId": "59887303", "state": 1, "state_text": "空闲",
                 "type": 2, "dispatchable": True, "rewardable": False,
                 "itemId": "36013516", "count": 15, "endTime": 0, "speedTimes": 0},
                {"uuid": "s4", "configId": "59887304", "state": 1, "state_text": "空闲",
                 "type": 0, "dispatchable": False, "rewardable": False,
                 "itemId": "", "count": 0, "endTime": 0, "speedTimes": None},
            ],
            "rewardable": [{"uuid": "s1"}], "idle": [{"uuid": "s3"}],
            "trading": [{"uuid": "s2"}], "locked": [],
            "speedTimes": 3,
        }

    token = None if args.no_token else (args.token or cok_web.read_or_make_token())
    cok_web.Handler.token = token
    cok_web.Handler.engine = eng

    # 填一份样例状态(预览服务不跑轮询)
    eng.daemon.poll_once()
    eng.connected = True
    eng.last_poll = time.time()
    eng.gold = (eng.daemon.last_state.get("buildQueue") or {}).get("金币")
    for name, st in eng.daemon.last_state.items():
        eng.states[name] = st

    import http.server
    srv = http.server.ThreadingHTTPServer((args.host, args.port), cok_web.Handler)
    url = "http://%s:%d/" % (args.host, args.port)
    if token:
        url += "?t=%s" % token
    print("=" * 60)
    print("  COK 控制台 · 离线预览(假数据, 不连游戏服)")
    print("  打开: %s" % url)
    print("=" * 60, flush=True)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        srv.server_close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
