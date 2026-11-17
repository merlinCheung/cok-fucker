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
import secrets
import sys
import threading
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
    # 多用户改造后 /api/state 走 `self._manager().view_engine()` —— 管理器为空
    # 会在 snapshot() 上抛 AttributeError, 离线预览就全空白了。这里塞一个
    # **只包着这一个引擎**的轻量管理器, 让预览继续走真实渲染路径。
    class _SoloManager(object):
        owner = ""
        view_key = ""
        engines = ()

        def all_engines(self):
            return ()

        def view_engine(self):
            return eng

        def engine_for(self, key=None):
            return eng

        def accounts_overview(self):
            return {}

        def start(self):
            pass

        def stop_all(self):
            pass

    cok_web.Handler.manager = _SoloManager()

    # 平台模式演示: 离线预览默认 `Handler.platform is None`, 于是 `/api/me`
    # 回的是"匿名本地用户(role=admin)" ⇒ 管理面板按钮在预览里根本不出现,
    # 改管理页时看不到效果。这里挂一个**假平台层**(只实现前端会用到的
    # list_users), 并且 `_current_user` 固定返回 admin —— 预览不联网、不碰
    # 真库, 所以随便"冒充"没有风险。
    class _MockPlatform(object):
        #: 预览里这些 uid 就是"有号的人"—— list_accounts 里没有 owner 的号
        #: 归到 boss 名下, 好让管理面板有行可显示。
        uid = "u-demo-boss"

        def __init__(self):
            self.lock = threading.Lock()
            self.users = {}

        def list_users(self, limit=200):
            """`online` 要真实: 概览页按它统计在线人数, 不标就永远是 0。

            两个号标成在线 —— 他们在假快照里有正在跑的引擎(见
            `_preview_admin_accounts`), 标不在线会和下面那张表对不上。
            """
            return [
                {"uid": "u-demo-boss", "username": "boss", "role": "admin",
                 "banned": 0, "online": True, "created_at": 0,
                 "last_login": time.time()},
                {"uid": "u-demo-alice", "username": "alice", "role": "user",
                 "banned": 0, "online": True, "created_at": 0,
                 "last_login": time.time() - 600},
                {"uid": "u-demo-bob", "username": "bob", "role": "user",
                 "banned": 0, "online": False, "created_at": 0,
                 "last_login": time.time() - 7200},
            ]

        def get(self, owner, touch=True):
            return None

        # ---- 邀请码: 管理页的「邀请码」面板全靠这个 -------------------
        def invites_list(self, limit=100):
            rows = list(getattr(self, "_invites", []) or [])
            rows.extend([
                {"code": "COK-DEMO0001", "created_by": "boss",
                 "created_at": int(time.time()) - 86400,
                 "used_by": "alice", "expires_at": 0, "note": "预览"},
                {"code": "COK-DEMO0002", "created_by": "boss",
                 "created_at": int(time.time()) - 3600,
                 "used_by": "", "expires_at": 0, "note": ""}])
            return rows

        def invite_new(self, created_by="", expires_at=0, note=""):
            # 用 secrets 而不是 random: random 是可预测的伪随机(这个文件同时
            # 被真实部署脚本 import 过, 别把"生成邀请码"的做法留成范例)。
            code = "COK-DEMO" + secrets.token_hex(2).upper()
            self._invites = getattr(self, "_invites", [])
            self._invites.insert(0, {
                "code": code, "created_by": created_by or "",
                "created_at": int(time.time()), "used_by": "",
                "expires_at": int(expires_at or 0), "note": note or ""})
            return code

        def user_get(self, name):
            for u in self.list_users():
                if u.get("username") == str(name):
                    return u
            return None

        def user_get_by_uid(self, uid):
            for u in self.list_users():
                if u.get("uid") == str(uid):
                    return u
            return None

        def user_set_banned(self, name, banned):
            return True

        def user_set_role(self, name, role):
            return True

        def user_delete(self, name):
            return True

        # ---- 审计日志: `/api/audit` 直接调 `platform.recent_audit` -----
        # 少这个方法会抛 AttributeError → 响应直接断连(ERR_EMPTY_RESPONSE),
        # 页面上只显示"查询失败: Failed to fetch", 完全看不出是哪一层炸的。
        def recent_audit(self, uid=None, limit=100):
            base = int(time.time())
            rows = [
                {"ts": base - 30, "uid": "u-demo-boss", "action": "login",
                 "target": "boss", "ok": 1, "detail": "登录成功"},
                {"ts": base - 600, "uid": "u-demo-bob", "action": "account-add",
                 "target": "44056610002223", "ok": 1, "detail": "添加账号"},
                {"ts": base - 1800, "uid": "u-demo-alice",
                 "action": "account-remove", "target": "1125641597002221",
                 "ok": 1, "detail": "移除账号"},
                {"ts": base - 7200, "uid": "u-demo-boss",
                 "action": "invite-new", "target": "COK-DEMO0002",
                 "ok": 1, "detail": "生成邀请码"},
            ]
            if uid:
                rows = [r for r in rows if r.get("uid") == uid]
            return rows[:int(limit or 100)]

        def session_drop_user(self, uid):
            return True

    _mock_pm = _MockPlatform()
    cok_web.Handler.platform = _mock_pm
    # 路由里有些判断用的是**模块级** `platform`(不是 Handler 上的):
    # `/api/admin/users`、`/api/admin/invites` 写的是 `if platform is None:
    # return {"ok": True, "users": []}` —— 只挂 Handler 的话页面一切正常,
    # 但用户表和邀请码永远是空数组。所以模块级也要指过去。
    cok_web.platform = _mock_pm
    cok_web.Handler._current_user = (
        lambda self: {"uid": "u-demo-boss", "username": "boss",
                      "role": "admin", "banned": False})

    def _preview_admin_accounts(handler, with_errors=False):
        """假的全平台账号状态: 用来把管理面板渲染出来, 不碰真账号库。

        状态刻意做全: 报错 / 掉线 / 陈旧 / 打怪 / 有罩 / 无主 —— 每种分支都
        要能在预览里看到, 否则改完样式只能等真机。
        """
        now = time.time()

        def row(key, label, uid, uname, owner_name, status, **kw):
            s = {"shield_ms": 0, "has_shield": False, "dock_rewardable": 0,
                 "welfare_claimable": False, "hunting": False, "hunt_kills": 0,
                 "error": "", "disconnected": False, "app_yield": False,
                 "last_ok_poll": now - 30, "stale": False}
            s.update(kw)
            running = status != "none"
            return {"key": key, "label": label, "role_name": label,
                    "game_uid": key, "added": "2026-11-0%d" % (1 + len(key) % 8),
                    "owner": uid, "username": uname, "user_banned": False,
                    "orphan": not uid, "running": running, "parallel": running,
                    "priority": 1 + len(key) % 3,
                    # ⚠ 前端按后端的 `error` / `offline` / `stale` 判状态,
                    #   假数据写成 "err"/"off" 会一条都匹配不上(筛"报错"永远 0)。
                    "status": {"err": "error", "off": "offline"}.get(status, status),
                    "summary": s if running else None, "owner_name": owner_name}

        rows = [
            row("136063574002223", "主号(元气少女李逵)", "u-demo-boss", "boss",
                "boss", "ok", shield_ms=5 * 3600_000, has_shield=True,
                dock_rewardable=2, welfare_claimable=True),
            row("44056610002223", "乙", "u-demo-bob", "bob", "bob", "run",
                hunting=True, hunt_kills=12, shield_ms=3 * 3600_000,
                has_shield=True),
            row("1125641597002221", "甲", "u-demo-alice", "alice", "alice",
                "err", error="登录失败: 服务端返回 500192(账号被顶)"),
            row("351542128002216", "66手游号", "", "无主", "无主", "none"),
            row("136063574002224", "乙的小号(掉线)", "u-demo-bob", "bob", "bob",
                "off", disconnected=True, last_ok_poll=now - 900),
            row("136063574002225", "乙的小号(陈旧)", "u-demo-bob", "bob", "bob",
                "idle", stale=True, last_ok_poll=now - 4000),
        ]
        return {"ok": True, "platform": True, "preview": True,
                "users": _MockPlatform().list_users(), "accounts": rows,
                "stats": {"users": 3, "users_online": 2, "accounts": 6,
                          "shown": 6, "running": 2, "parallel": 2, "hunting": 1,
                          "shielded": 2, "errors": 1, "offline": 1, "stale": 1,
                          "orphan": 1},
                "generated": int(now)}

    # 管理面板要有行可显示: 离线预览里没有真账号库, 这里直接喂一份假快照
    # (只影响 `/api/admin/accounts` 这一个路由, 其它接口照旧走假引擎)。
    # 关掉缓存 —— 预览进程里状态是静态的, 缓存只会让改完代码看不到变化。
    cok_web._ADMIN_STATE_TTL = 0.0
    cok_web._admin_accounts_snapshot = _preview_admin_accounts
    # 管理动作在预览里也是假的: 真实现会去账号库找 key, 而预览没有账号库,
    # 会一律回"账号库里没有这个账号"。这里回一个成功, 让前端路径走通。
    cok_web.admin_account_action = (
        lambda handler, body: {
            "ok": True, "on": bool((body or {}).get("on")),
            "key": str((body or {}).get("key") or ""), "owner": "bob",
            "preview": True,
            "note": "已操作(预览模式, 没有真的动账号)"})

    # ---- 独立管理后台 cok/admin.html ----------------------------------
    # 概览**不再单独造假**: 真机上的实现就是 `_admin_accounts_snapshot` 的
    # 加一层聚合(见 cok_web._admin_platform_overview), 口径必须和表一致。
    # 这里同样让它跑真实现 —— 假快照已经是上面那份 6 行数据, 聚合出来的
    # KPI 才是页面真正会看到的样子。各造一套的话, 预览里对得上、线上对不上。

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
