#!/usr/bin/env python3
"""COK 直连控制台 —— 本地网页(监控 + 操作)。

特点:
  * 零新依赖: 只用 Python 标准库(http.server)
  * 复用 cok_daemon.py 的 watcher / extractor / 写操作实现, 不重复造轮子
  * 默认只绑 127.0.0.1, 带 token 鉴权
  * 后台线程持续轮询 + 监听服务端 push(可自动开保护罩)

用法:
  python3 cok_web.py --account-device            # 启动(默认 127.0.0.1:8770)
  python3 cok_web.py --account-device --port 9000 --webhook <URL> --webhook-type wechat
  python3 cok_web.py --account-device --open    # 启动后用默认浏览器打开

页面: http://127.0.0.1:8770/?t=<token>
"""
import argparse
import json
import os
import secrets
import signal
import sys
import re
import subprocess
import threading
import time
import webbrowser
from urllib.parse import parse_qs  # noqa: E402
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import cok_daemon as D  # noqa: E402
import cok_hunt as cok_hunt  # noqa: E402
import cok_client  # noqa: E402
import cok_dock  # noqa: E402
import cok_locate  # noqa: E402
import cok_map  # noqa: E402
import cok_excel  # noqa: E402
from cok_account import load_account  # noqa: E402

TOKEN_FILE = os.path.join(HERE, ".cok-web-token")
MAX_EVENTS = 300
ADB_CANDIDATES = [
    "/Users/a1234/Library/Android/sdk/platform-tools/adb",
    "adb",
]
GAME_PKG = "com.hcg.cok.nearme.gamecenter"
# 登录必须来自设备的字段。缺任意一个都说明"设备没连上"或"App 没登录过",
# 这时去连游戏服只会得到误导性的"连接被服务端关闭"。
ACCOUNT_REQUIRED = ("pfId", "platformToken", "gameUid", "deviceId", "uuid",
                    "signCode", "host", "port")
# 需要连游戏服的操作(会占用账号连接)。set-setting / hook-test 是纯本地的,
# 不在这个名单里, 因此不会被慢轮询堵住。
#: 港口功能未开启的服务端错误码(文本 102192 = "功能未开启, 敬请期待")
#: 服务端可能把它当字符串返回, 比较前统一转 int
DOCK_DISABLED_CODE = 102192


def _is_dock_disabled(code):
    """errorCode == 102192? (服务端有时给字符串)"""
    try:
        return int(code) == DOCK_DISABLED_CODE
    except (TypeError, ValueError):
        return False

GAME_SERVER_ACTIONS = frozenset((
    "sign", "claim", "reconnect", "autoshield", "shield", "speedup",
    "queues", "shieldslots", "hunt", "refresh-now", "dock", "locate",
))


def read_or_make_token():
    try:
        with open(TOKEN_FILE, "r", encoding="utf-8") as f:
            t = f.read().strip()
            if t:
                return t
    except OSError:
        pass
    t = secrets.token_urlsafe(18)
    try:
        with open(TOKEN_FILE, "w", encoding="utf-8") as f:
            f.write(t)
        os.chmod(TOKEN_FILE, 0o600)
    except OSError:
        pass
    return t


class Engine(object):
    """后台引擎: 轮询监控 + 收集 push + 执行写操作。"""

    def __init__(self, args):
        self.args = args
        self.lock = threading.RLock()      # 状态锁: 只保护内存, 毫秒级持有
        self.op_lock = threading.RLock()   # 操作锁: 串行化对游戏服的操作(含网络 I/O)
        self.events = []
        self.states = {}
        self.hunt = {}
        self.hunter = None
        self.hunter_client = None
        self.hunter_thread = None
        self.gold = None
        self.connected = False
        self.last_error = None
        self.autoshield_enabled = args.autoshield
        self.persistent = bool(getattr(args, "persistent", False))
        self.last_poll = 0.0
        self.app_yield = False
        self._suspend_poll = False
        self._poll_suspend_until = 0.0
        self._app_online_flag = False
        self.names = self._load_names()
        self.settings = self._load_settings()
        self.account_error = ""
        self.account_source = ""
        self._hunter_lock = None
        self.shield_state = {}
        self.persistent_arg = self.persistent
        self.dock_state = {}
        self.dock_disabled = False
        # 每个设置键的写入序号: 前端连续输入会并发 POST, 用序号挡住乱序覆盖
        self.settings_seq = {}
        self.daemon = D.Daemon(args)
        # 接管 emit: 事件同时进内存流(供网页显示)
        orig_emit = self.daemon.emit

        def emit(kind, payload):
            orig_emit(kind, payload)
            with self.lock:
                self.events.append({
                    "ts": time.strftime("%H:%M:%S"),
                    "kind": kind,
                    "data": payload,
                })
                if len(self.events) > MAX_EVENTS:
                    del self.events[:-MAX_EVENTS]
        self.daemon.emit = emit
        self._stop = threading.Event()
        self._thread = None

    def _load_names(self):
        """id -> 中文名(道具/建筑/奖励/任务/队列类型/概览类型)。"""
        try:
            with open(os.path.join(HERE, "id-names.json"), encoding="utf-8") as f:
                d = json.load(f)
            return {
                "queue_types": d.get("queue_types") or {},
                "overview_types": d.get("overview_types") or {},
                "items": d.get("item_names") or {},
                "luaxml": d.get("luaxml_names") or {},
                "tasks": d.get("task_names") or {},
                "story_tasks": d.get("story_tasks") or {},
                "story_chapters": d.get("story_chapters") or {},
                "rewards": d.get("reward_names") or {},
            }
        except Exception:
            return {"queue_types": {}, "overview_types": {}, "items": {},
                    "luaxml": {}, "tasks": {}, "story_tasks": {},
                    "story_chapters": {}, "rewards": {}}

    def _ensure_account(self):
        """确保有可用账号。

        账号有两个来源, 按优先级:
          1. **设备 SharedPreferences** —— 最新最准, 设备在时优先用
          2. **内置 ACCOUNT**(cok_client.ACCOUNT) —— 从线上登录请求复原的凭据,
             pfId / gameUid / deviceId / uuid / signCode / buildCode 齐全。
             signCode 是从 APK 签名证书派生的静态值, 所以**不依赖设备也能登录**
             (2026-10-25 实测: 设备完全没连上, 直连登录依然成功)。

        设备临时掉线(USB/无线都扫不到)时, 控制台照常工作 ——
        读不到设备账号就退回内置凭据, 只在页面提示"当前用的是内置凭据"。
        """
        if getattr(self.args, "account", None):
            return True
        acc = {}
        try:
            acc = load_account()
        except Exception as e:  # noqa: BLE001
            self.account_error = "读不到设备账号: %s" % str(e)[:120]
        missing = [k for k in ACCOUNT_REQUIRED if not acc.get(k)]
        if not missing:
            self.args.account = acc
            self.account_error = ""
            self.account_source = "设备"
            return True
        # 设备不可用 -> 退回内置凭据
        builtin = dict(cok_client.ACCOUNT)
        # 游戏服地址: 内置凭据里没有 host/port, 用**游戏服**地址(不是网页监听地址)
        builtin.setdefault("host", getattr(self.args, "game_host", None)
                           or cok_client.DEFAULT_HOST)
        builtin.setdefault("port", int(getattr(self.args, "game_port", None)
                                        or cok_client.DEFAULT_PORT))
        b_missing = [k for k in ACCOUNT_REQUIRED if not builtin.get(k)]
        if b_missing:
            self.account_error = ("设备未连接或 App 未登录(账号缺 %s); "
                                  "请插好数据线/确认无线调试, 再点一次刷新"
                                  % ", ".join(missing))
            return False
        self.args.account = builtin
        self.account_error = ""
        self.account_source = "内置凭据(设备未连接)"
        print("[*] 设备账号不可用, 改用内置凭据: %s" % ", ".join(missing))
        return True

    def stop_app(self):
        """把 App 停掉, 把账号让出来。

        **必须做**: 游戏服同账号只允许一个连接, App 在线时网页连上去会被服务端
        主动踢掉(表现为"连接被服务端关闭"), 看起来像命令不被接受, 其实是被互踢。
        """
        for adb in ADB_CANDIDATES:
            try:
                subprocess.run([adb, "shell", "am", "force-stop", GAME_PKG],
                               capture_output=True, timeout=8)
                return True
            except Exception:
                continue
        return False

    # ---------- 设置持久化(跨刷新/跨浏览器) ----------
    SETTINGS_FILE = os.path.join(HERE, "web-settings.json")
    # 默认值: 保证页面回填时每一项都有值, 不会出现"上限空着、下限填了"的乱象
    DEFAULT_SETTINGS = {
        "autoSign": False, "autoShield": False, "cover": True,
        "autoPoll": True, "hookType": "generic", "hookURL": "",
        "lvLow": 1, "lvHigh": 1,
        "perType": 50, "squads": 4, "huntMax": 0,
        # 港口(码头航海贸易)自动: 默认都关, 由用户显式打开
        "dockAutoReward": False, "dockAutoSend": False,
    }

    def _load_settings(self):
        d = {}
        try:
            with open(self.SETTINGS_FILE, encoding="utf-8") as f:
                loaded = json.load(f)
            if isinstance(loaded, dict):
                d = loaded
        except Exception:
            pass
        merged = dict(self.DEFAULT_SETTINGS)
        merged.update(d)
        return merged

    def _save_settings(self):
        try:
            tmp = self.SETTINGS_FILE + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=1)
            os.replace(tmp, self.SETTINGS_FILE)
        except Exception:
            pass

    def app_online(self):
        """检测 App 是否在跑(游戏服同账号只允许一个连接, 必须互相让路)。"""
        for adb in ADB_CANDIDATES:
            try:
                out = subprocess.run([adb, "shell", "ps", "-A"], capture_output=True,
                                     text=True, timeout=6).stdout
            except Exception:
                continue
            for line in out.splitlines():
                parts = line.split()
                if len(parts) >= 2 and parts[1] == GAME_PKG:
                    self._app_online_flag = True
                    return True
            self._app_online_flag = False
        return False

    # ---------- 生命周期 ----------
    def start(self):
        self._thread = threading.Thread(target=self._loop, name="cok-web-engine", daemon=True)
        self._thread.start()

    def stop(self):
        self._stop.set()

    def _poll_once(self):
        """跑一轮轮询: 连上 -> 拉全部 watcher -> 断开(ondemand 模式)。

        返回 (ok, note)。App 在线时让路, 不抢账号。

        **锁的分工(不要合并)**:
          op_lock —— 串行化"对游戏服的操作", 网络 I/O 全程持有
          lock   —— 只保护内存状态, 持有时间必须毫秒级
        早先用同一把锁, 轮询/操作期间 /api/state 整个卡死(最长 60 秒),
        页面表现为"按钮点了没反应"。拆开后页面永远可读。

        另外还有**跨进程**的账号锁(cok_client.account_lock):
        游戏服同账号只允许一个连接, 网页控制台和命令扫描脚本同时用同一个账号
        会被服务端互踢(表现为"连接被服务端关闭")。拿不到锁就跳过本轮。
        """
        with self.op_lock:
            if self.hunter and self.hunter.state.get("running"):
                return False, "自动打怪占用连接, 已跳过本轮"
            if not self.persistent and self.daemon.client is None and self.app_online():
                with self.lock:
                    self.app_yield = True
                    self.connected = False
                return False, "App 在线, 已让出账号"
            with self.lock:
                self.app_yield = False
            if not self._ensure_account():
                with self.lock:
                    self.connected = False
                    self.last_error = self.account_error
                return False, "设备未连接, 请检查 USB/无线调试"
            try:
                with cok_client.account_lock(timeout=0.0, purpose="web-poll"):
                    return self._poll_locked()
            except cok_client.AccountBusy as e:
                # ⚠️ "账号正被占用" 不是故障(打怪时账号被独占是设计内的让路),
                # 别写进 last_error —— 否则顶灯会误报"连接异常"。
                with self.lock:
                    self.connected = False
                return False, "账号被其他工具占用, 本轮跳过(%s)" % str(e)[:60]
            except Exception as e:  # noqa: BLE001
                with self.lock:
                    self.connected = False
                    self.last_error = str(e)[:200]
                return False, "刷新失败: %s" % str(self.last_error)[:120]

    def _poll_locked(self):
        """已持有 op_lock 和跨进程账号锁, 真正去连游戏服拉数据。"""

        if not self.daemon.client:
            self.daemon.connect()
        self.daemon.poll_once()
        with self.lock:
            self.connected = True
            self.last_error = None
            self.last_poll = time.time()
            for name, st in self.daemon.last_state.items():
                self.states[name] = st
            bq = self.states.get("buildQueue") or {}
            if isinstance(bq, dict):
                self.gold = bq.get("金币")
            if not self.settings.get("autoShield", self.autoshield_enabled):
                self.autoshield_enabled = False
        # 自动签到 / 自动开罩 / webhook —— 全部以网页保存的设置为准
        if self.settings.get("autoSign", False):
            try:
                self.daemon.auto_sign(self.daemon.ctx())
            except Exception as e:  # noqa: BLE001
                with self.lock:
                    self.last_error = "自动签到失败: %s" % str(e)[:120]
        if self.settings.get("autoShield", self.autoshield_enabled):
            self.autoshield_enabled = True
            self.daemon.autoshield(self.daemon.ctx())
        hook_url = self.settings.get("hookURL")
        if hook_url:
            self.daemon.alert.url = hook_url
        hook_kind = self.settings.get("hookType")
        if hook_kind:
            self.daemon.alert.kind = hook_kind
        # 保护罩状态(槽位 + 当前到期时间) —— 复用本轮连接, 不额外占号。
        # 服务端**只在有罩时**才给 shieldEndTime, 所以这一项天然"有罩才有值"。
        try:
            sh = self._shield_slots()
            with self.lock:
                self.shield_state = sh
        except Exception as e:  # noqa: BLE001
            with self.lock:
                self.shield_state = {"error": str(e)[:120]}
        # 打野怪状态(体力/等级/自动打怪设置) —— 复用本轮连接, 不额外占号
        try:
            hunt = self._hunt_state()
        except Exception as e:  # noqa: BLE001
            hunt = {"error": str(e)[:160]}
        with self.lock:
            self.hunt = hunt
        # 港口(码头航海贸易): 顺带查一次, 并按设置做自动领取/自动分派
        self._dock_tick()
        return True, "已刷新"

    def _dock_tick(self, client=None):
        """港口定时检查: 读状态 -> 有可领的就一键领 -> 有空闲的就一键派。

        复用当前连接, 不额外占号。两步都是**真实写操作**:
          * oneKeyShipReward —— 领取奖励(本来就是该领的, 风险低)
          * oneKeySendShip   —— 派出船只(会消耗载货/资源)
        所以默认都**关**, 由用户在页面上显式打开。

        client 为空时用 daemon.client; 打怪运行时传打怪那条连接
        (见 _hunter_start 的 on_tick), 这样**不额外开连接**也不会互踢。
        """
        cli = client or self.daemon.client
        if cli is None:
            return
        # 功能未开启时(服务端 102192 = "功能未开启, 敬请期待")不要每轮都空转
        if self.dock_disabled and client is None:
            return
        auto_reward = bool(self.settings.get("dockAutoReward", False))
        auto_send = bool(self.settings.get("dockAutoSend", False))
        try:
            st = cok_dock.read_dock(cli)
        except Exception as e:  # noqa: BLE001
            with self.lock:
                self.dock_state = {"error": str(e)[:120]}
            return
        if _is_dock_disabled(st.get("errorCode")):
            with self.lock:
                self.dock_state = {"errorCode": DOCK_DISABLED_CODE,
                                   "disabled": True,
                                   "note": "港口功能未开启(服务端 %d = 功能未开启, 敬请期待)"
                                           % DOCK_DISABLED_CODE}
                self.dock_disabled = True
            return
        if not st.get("ok") and st.get("error"):
            with self.lock:
                self.dock_state = {"error": st.get("error"),
                                   "note": "港口读取失败: %s" % st.get("error")}
            return
        acted = []
        if auto_reward and st.get("rewardable"):
            try:
                rr = cok_dock.one_key_reward(cli)
                acted.append("自动领取 %d 船的奖励%s" % (
                    len(st.get("rewardable") or []),
                    "" if rr.get("ok") else "(失败 %s)" % rr.get("errorCode")))
                st = cok_dock.read_dock(cli)
            except Exception as e:  # noqa: BLE001
                acted.append("自动领取失败: %s" % str(e)[:80])
        if auto_send and st.get("idle"):
            try:
                rs = cok_dock.one_key_send(cli)
                acted.append("自动分派 %d 条空闲船%s" % (
                    len(st.get("idle") or []),
                    "" if rs.get("ok") else "(失败 %s)" % rs.get("errorCode")))
                st = cok_dock.read_dock(cli)
            except Exception as e:  # noqa: BLE001
                acted.append("自动分派失败: %s" % str(e)[:80])
        if acted:
            self.daemon.emit("dock_auto", {"note": "; ".join(acted)})
            with self.lock:
                st["last_auto"] = "; ".join(acted)
        self._set_dock_state(st)

    def _set_dock_state(self, st):
        """写入港口状态, 但**保留**"上次领取"明细。

        轮询/自动检查/刷新都会重读港口, 直接覆盖会把用户刚看到的
        "领了多少 / 哪些没领到"冲掉, 所以这里统一保留。
        """
        with self.lock:
            prev = (self.dock_state or {}).get("last_reward")
            if prev and not (st or {}).get("last_reward"):
                st = dict(st)
                st["last_reward"] = prev
            self.dock_state = st

    def refresh_now(self):
        """立即刷新一次(不等轮询间隔)。"""
        ok, note = self._poll_once()
        if not self.persistent:
            with self.op_lock:
                try:
                    if self.daemon.client:
                        self.daemon.client.close()
                except Exception:
                    pass
                self.daemon.client = None
                with self.lock:
                    self.connected = False
        return {"ok": ok, "note": note}

    def _loop(self):
        while not self._stop.is_set():
            try:
                # 全图扫描在跑时, 主动把账号让给扫描器(否则两边互抢锁)
                if getattr(self, "_suspend_poll", False):
                    scanning = self._scan_status().get("running")
                    if scanning or time.time() < getattr(self, "_poll_suspend_until", 0):
                        with self.lock:
                            self.connected = False
                        for _ in range(3):
                            if self._stop.is_set():
                                break
                            time.sleep(1.0)
                        continue
                    self._suspend_poll = False
                if not self.settings.get("autoPoll", True):
                    # 用户关掉了自动轮询: 不连游戏服, 只等用户手动点「立即刷新」
                    with self.lock:
                        self.connected = False
                    for _ in range(3):
                        if self._stop.is_set():
                            break
                        time.sleep(1.0)
                    continue
                ok, note = self._poll_once()
                if not ok and "让出账号" in note:
                    for _ in range(int(max(1, self.args.interval) / 1.0)):
                        if self._stop.is_set():
                            break
                        time.sleep(1.0)
                    continue
            except Exception as e:  # noqa: BLE001
                with self.lock:
                    self.connected = False
                    self.last_error = str(e)[:200]
            if not self.persistent:
                # 按需短连接: 轮完立刻断开, 把账号还给 App(同账号只允许一个连接)
                with self.op_lock:
                    try:
                        if self.daemon.client:
                            self.daemon.client.close()
                    except Exception:
                        pass
                    self.daemon.client = None
                    with self.lock:
                        self.connected = False
            for _ in range(int(max(1, self.args.interval) / 1.0)):
                if self._stop.is_set():
                    break
                time.sleep(1.0)

    # ---------- API ----------
    def snapshot(self):
        with self.lock:
            queues = []
            for q in (getattr(self.daemon, "queues", None) or []):
                if not isinstance(q, dict):
                    continue
                total = q.get("totalTime") or 0
                start = q.get("startTime") or 0
                bld = (q.get("itemObj") or {}).get("building") \
                    if isinstance(q.get("itemObj"), dict) else None
                queues.append({
                    "uuid": q.get("uuid"),
                    "qid": q.get("qid"),
                    "type": q.get("type"),
                    "type_name": self._tr_queue_type(q.get("type")),
                    "building": bld,
                    "building_name": self._tr_building(bld),
                    "totalTime": total,
                    "startTime": start,
                    "endTime": q.get("endTime") or 0,
                    "running": bool(total > 0 and start > 0),
                })
            return {
                "connected": self.connected,
                # ondemand 模式轮完就断开, connected 永远是 False ——
                # 顶栏灯要用"有没有拿到数据"来判断, 否则一直显示"空闲"
                "has_data": bool(self.last_poll and not self.last_error),
                "persistent": self.persistent,
                "app_yield": self.app_yield,
                "app_online": self._app_cached,
                "last_poll": self.last_poll,
                "error": self.last_error,
                "server_date": self.daemon.ctx().get("date"),
                "gold": self.gold,
                "states": self._translate_states(self.states),
                "hunt": self.hunt,
                "hunter": self._hunter_state(),
                "monster_levels": cok_hunt.load_levels(),
                "queues": queues,
                "shield": {
                    "end_ms": getattr(self.daemon, "shield_end_ms", 0),
                    "autoshield": self.autoshield_enabled,
                    "slots": (self.shield_state or {}).get("slots") or [],
                    "specs": (self.shield_state or {}).get("specs") or [],
                    "persistent": self.persistent,
                },
                "autoSign": bool(self.settings.get("autoSign", False)),
                "autoPoll": bool(self.settings.get("autoPoll", True)),
                "dock": {
                    "ships": self._dock_ships_view(),
                    "rewardable": len((self.dock_state or {}).get("rewardable") or []),
                    "idle": len((self.dock_state or {}).get("idle") or []),
                    "trading": len((self.dock_state or {}).get("trading") or []),
                    "family": (self.dock_state or {}).get("family"),
                    "shipLimit": (self.dock_state or {}).get("shipLimit"),
                    "error": (self.dock_state or {}).get("error"),
                    "disabled": bool((self.dock_state or {}).get("disabled")),
                    "errorCode": (self.dock_state or {}).get("errorCode"),
                    "note": (self.dock_state or {}).get("note"),
                    "last_reward": (self.dock_state or {}).get("last_reward"),
                    "autoReward": bool(self.settings.get("dockAutoReward", False)),
                    "autoSend": bool(self.settings.get("dockAutoSend", False)),
                },
                "map_index": self._map_index_summary(),
                "account_error": self.account_error,
                "account_source": self.account_source,
                # ⚠️ 只有「别人」占着账号才算 busy —— 本进程自己在跑 daemon 时
                # flock 探测必然失败, 那是自指, 不是外部占用。
                "account_busy": self._account_busy(),
                "account_holder": cok_client.account_holder(),
                "account_holder_self": self._account_holder_self(),
                "items": self._owned_items(),
                "bag_source": self._bag_source(),
                "events": self.events[-120:],
                "interval": self.args.interval,
                "webhook": bool(self.args.webhook),
                "webhook_type": self.args.webhook_type,
                "alert_rules": sorted(self.daemon.alert.rules),
                "alert_rule_names": [D.rule_name(r)
                                     for r in sorted(self.daemon.alert.rules)],
                # 前端兜底用的少量枚举(道具/奖励全表太大, 已在后端翻译好)
                "names": {
                    "queue_types": self.names.get("queue_types") or {},
                    "overview_types": self.names.get("overview_types") or {},
                },
                "settings": dict(self.settings),
            }

    def _owned_items(self):
        """背包里**有库存**的加速道具实例。

        数据源(按优先级):
          1. bag-items.json     —— dump_bag.py 用 frida 注入读 ToolController 得到的**实时**背包
          2. speedup-owned.json —— 旧的静态快照(没有实时数据时的兜底)
        元数据(seconds / type2 / label)来自 speedup-meta.json。
        """
        owned = {}
        try:
            with open(os.path.join(HERE, "bag-items.json"), encoding="utf-8") as f:
                doc = json.load(f)
            for it in (doc.get("items") or []):
                iid = str(it.get("itemId"))
                if iid and (it.get("count") or 0) > 0:
                    owned[iid] = it
        except Exception:
            owned = {}
        if not owned:
            try:
                with open(os.path.join(HERE, "speedup-owned.json"), encoding="utf-8") as f:
                    owned = json.load(f).get("items") or {}
            except Exception:
                owned = {}
        meta = {}
        try:
            with open(os.path.join(HERE, "speedup-meta.json"), encoding="utf-8") as f:
                meta = json.load(f).get("items") or {}
        except Exception:
            meta = {}
        out = []
        for iid, v in owned.items():
            m = meta.get(iid) or {}
            sec = v.get("seconds", m.get("seconds"))
            label = v.get("label", m.get("label"))
            cn = (self.names.get("items") or {}).get(iid)
            if cn:
                cn = cn.replace("{0}", self._dur_text(sec))
            out.append({
                "itemId": iid, "uuid": v.get("uuid"), "count": v.get("count"),
                "type2": v.get("type2", m.get("type2")), "seconds": sec,
                "label": label, "name": cn,
            })
        out.sort(key=lambda x: int(x["itemId"]))
        return out

    def _bag_source(self):
        """背包数据的来源与时间 —— 页面要能看出这是实时还是快照。"""
        for name, label in (("bag-items.json", "frida 实时读 ToolController"),
                            ("speedup-owned.json", "旧静态快照")):
            p = os.path.join(HERE, name)
            try:
                with open(p, encoding="utf-8") as f:
                    doc = json.load(f)
            except Exception:
                continue
            src = doc.get("source")
            if src:
                return {"file": name, "label": label, "detail": str(src)[:80]}
            try:
                import datetime
                mt = datetime.datetime.fromtimestamp(os.path.getmtime(p))
                return {"file": name, "label": label,
                        "detail": "文件时间 " + mt.strftime("%Y-%m-%d %H:%M")}
            except Exception:
                return {"file": name, "label": label, "detail": ""}
        return {"file": "", "label": "无", "detail": "背包数据不可用"}

    @staticmethod
    def _dur_text(sec):
        if not sec:
            return ""
        if sec < 60:
            return "%d秒" % sec
        if sec < 3600:
            return "%d分钟" % round(sec / 60)
        if sec < 86400:
            return "%d小时" % round(sec / 3600, 1)
        return "%d天" % round(sec / 86400, 1)

    @staticmethod
    def _clean(s):
        """占位符不要直接删 —— 删掉会拼出"城堡升到级"这种读不通的句子。

        没有可填充值时用 ? 保留占位语义(如 "攻打?次联盟BOSS")。
        """
        return re.sub(r"\{\d+\}", "?", s).strip() if s else None

    def _tr_item(self, iid):
        n = (self.names.get("items") or {}).get(str(iid))
        return self._clean(n) if n else None

    def _dock_ships_view(self):
        """港口船表: 把载货道具 id 换成中文名, 附带可派遣/可领奖标记。"""
        out = []
        for s in ((self.dock_state or {}).get("ships") or []):
            v = dict(s)
            iid = str(s.get("itemId") or "")
            v["item_name"] = self._tr_item(iid) if iid else ""
            v["cargo_text"] = ("%s ×%s" % (v["item_name"], s.get("count"))
                               if v["item_name"] and s.get("count") is not None
                               else (v["item_name"] or ("道具 " + iid if iid else "空载")))
            out.append(v)
        return out

    def _tr_reward(self, rid):
        n = (self.names.get("rewards") or {}).get(str(rid))
        return self._clean(n) if n else None

    def _tr_queue_type(self, v):
        return (self.names.get("queue_types") or {}).get(str(v))

    def _tr_overview_type(self, v):
        """概览页(overview_new.data)用的是 OverviewTypeDefine.Type, 与 QueueType 不是一套。"""
        return (self.names.get("overview_types") or {}).get(str(v))

    def _tr_task(self, tid):
        """任务名: 优先 luaxml 表(领主任务), 再退到道具表(主线/日常任务是 ItemSpec)。"""
        t = str(tid)
        n = (self.names.get("tasks") or {}).get(t)
        if n:
            return self._clean(n)
        n = (self.names.get("items") or {}).get(t)
        if n:
            return self._clean(n)
        n = (self.names.get("luaxml") or {}).get(t)
        return self._clean(n) if n else None

    def _tr_story_task(self, tid, target=None):
        """主线任务名: 模板里的 {0} 用 target(目标次数/等级) 填充。"""
        t = str(tid)
        tmpl = (self.names.get("story_tasks") or {}).get(t)
        if tmpl:
            if target is not None:
                tmpl = tmpl.replace("{0}", str(target))
            return self._clean(tmpl)
        return self._tr_task(tid)

    def _tr_chapter(self, section):
        return (self.names.get("story_chapters") or {}).get(str(section))

    def _tr_building(self, b):
        """'410000;26' -> '行军帐篷 位置26'"""
        if not b:
            return None
        parts = str(b).split(";")
        n = self._tr_item(parts[0])
        base = n or parts[0]
        return (base + " 位置" + parts[1]) if len(parts) > 1 else base

    def _tr_id_list(self, lst):
        """id 列表 -> [{'id':..,'name':..}]"""
        out = []
        for i in (lst or []):
            out.append({"id": i, "name": self._tr_item(i) or self._tr_reward(i)})
        return out

    def _translate_states(self, states):
        """把各监控项里的 id 列表翻译成人话"""
        st = json.loads(json.dumps(states, ensure_ascii=False, default=str))
        try:
            dq = st.get("dailyQuest")
            if dq and dq.get("周任务可领奖励") is not None:
                dq["周任务可领奖励"] = self._tr_id_list(dq["周任务可领奖励"])
            if dq and isinstance(dq.get("可领日常任务"), list):
                for t in dq["可领日常任务"]:
                    if isinstance(t, dict):
                        t["名称"] = self._tr_task(t.get("id"))
            lt = st.get("lordTask")
            if lt and lt.get("可领奖励") is not None:
                lt["可领奖励"] = self._tr_id_list(lt["可领奖励"])
            if lt and isinstance(lt.get("未完成"), list):
                for t in lt["未完成"]:
                    if isinstance(t, dict):
                        t["名称"] = self._tr_task(t.get("id"))
            sk = st.get("storyTask")
            if sk and sk.get("已完成任务奖励") is not None:
                sk["已完成任务奖励"] = self._tr_id_list(sk["已完成任务奖励"])
            if sk and isinstance(sk.get("任务"), list):
                for t in sk["任务"]:
                    if isinstance(t, dict):
                        t["名称"] = self._tr_story_task(t.get("id"), t.get("目标"))
            if sk and sk.get("章节") is not None:
                sk["章节名"] = self._tr_chapter(sk.get("章节"))
            ov = st.get("overview")
            if ov and isinstance(ov.get("队列"), list):
                for t in ov["队列"]:
                    if isinstance(t, dict):
                        t["类型"] = self._tr_overview_type(t.get("type"))
            bq = st.get("buildQueue")
            if bq and isinstance(bq.get("建造队列"), list):
                for t in bq["建造队列"]:
                    if isinstance(t, dict):
                        t["类型"] = self._tr_queue_type(t.get("type"))
        except Exception:
            pass
        return st

    def _err_text(self, code):
        """服务端错误码 -> 中文(用 id-names.json 的 reward_names 文本表)。"""
        if code in (None, "", 0, "0"):
            return ""
        try:
            c = int(code)
        except (TypeError, ValueError):
            c = str(code)
        t = (self.names.get("rewards") or {}).get(str(c))
        if t:
            return "%s(%s)" % (t, c)
        return "错误码 %s" % c

    def _shield_specs(self):
        """保护罩规格表(id -> 名称/时长秒)。由 gen_shield_specs.py 生成。"""
        if getattr(self, "_shield_specs_cache", None) is None:
            self._shield_specs_cache = {}
            try:
                with open(os.path.join(HERE, "shield-specs.json"), encoding="utf-8") as f:
                    d = json.load(f)
                for s in (d.get("specs") or []):
                    self._shield_specs_cache[str(s.get("id"))] = s
            except Exception:
                pass
        return self._shield_specs_cache

    def _shield_slots(self):
        """读保护罩: 槽位内容 + 当前罩到期时间 + 可选规格。

        * 槽位配置来自 `onekeybuff.get` 的 `backList`
        * **当前罩到期时间来自 `show.status.item`**(statusItems 里 type2=1 的
          endTime) —— `onekeybuff.get` 只回槽位, **不回** shieldEndTime,
          所以重启后想显示"还剩多久"必须查 show.status.item。
        """
        out = {"slots": [], "shield_end_ms": 0, "specs": []}
        specs = self._shield_specs()
        # 当前罩状态
        try:
            r0 = self.daemon.client.call("show.status.item")
            p0 = r0.get("__params__") or {}
            for it in (p0.get("statusItems") or []):
                if not isinstance(it, dict) or int(it.get("type2") or 0) != 1:
                    continue
                e = int(it.get("endTime") or 0)
                if e and e < (1 << 62):
                    out["shield_end_ms"] = e
                    self.daemon.shield_end_ms = e
                break
        except Exception as e:  # noqa: BLE001
            out["state_error"] = str(e)[:120]
        # 槽位
        try:
            r = self.daemon.client.call("onekeybuff.get")
            p = r.get("__params__") or {}
        except Exception as e:  # noqa: BLE001
            out["error"] = str(e)[:120]
            out["specs"] = [dict(s) for s in specs.values()]
            return out
        for b in (p.get("backList") or []):
            if not isinstance(b, dict):
                continue
            items = []
            for d in (b.get("statusList") or []):
                if not isinstance(d, dict) or not d.get("itemId"):
                    continue
                iid = str(d.get("itemId"))
                sp = specs.get(iid) or {}
                items.append({
                    "id": iid,
                    "name": sp.get("name") or self._tr_item(iid) or ("道具 " + iid),
                    "duration": sp.get("duration"),
                    "seconds": sp.get("seconds"),
                    "num": d.get("num"),
                })
            out["slots"].append({
                "type": b.get("type"),
                "name": b.get("name"),
                "items": items,
                # 槽位为空 -> 没法用 onekeybuff.use 开罩(服务端会静默失败)
                "empty": not items,
            })
        out["specs"] = [dict(s) for s in specs.values()]
        return out

    def _shield_set_slot(self, slot, spec_id):
        """把槽位写成指定道具(onekeybuff.save)。

        客户端的 statusList 格式是 "itemId1;itemId2"(分号分隔, **不带数量**),
        见 assets/lua_static/game/OneKeyBuff/OneKeyBuffSelectView.lua。
        """
        r = self.daemon.client.call("onekeybuff.save",
                                   {"type": int(slot), "statusList": str(spec_id)})
        p = r.get("__params__") or {}
        got = []
        for b in (p.get("backList") or []):
            if isinstance(b, dict) and str(b.get("type")) == str(slot):
                got = [str(d.get("itemId")) for d in (b.get("statusList") or [])
                       if isinstance(d, dict) and d.get("itemId")]
        return {"ok": str(spec_id) in got, "slot": slot, "itemIds": got,
                "errorCode": p.get("errorCode")}

    @property
    def _app_cached(self):
        return getattr(self, "_app_online_flag", False)

    def _ensure_client(self):
        """ondemand 模式下, 操作前确保有连接。"""
        if self.daemon.client is None:
            if not self._ensure_account():
                raise RuntimeError(self.account_error)
            self.daemon.connect()
            with self.lock:
                self.connected = True

    def _hunt_state(self):
        """打野怪状态: 体力 / 野怪等级 / 自动打怪设置(只读)。"""
        try:
            return cok_hunt.snapshot(self.daemon.client)
        except Exception as e:  # noqa: BLE001
            return {"error": str(e)[:160]}

    # ---------------- 自动打怪(常驻连接) ----------------
    def _hunter_start(self, body):
        """开启自动打怪循环。会用一条**常驻连接**(App 会被踢下线)。"""
        if self.hunter and self.hunter.state.get("running"):
            return {"ok": False, "error": "已经在跑了"}
        level = int(body.get("level") or 1)
        num = int(body.get("num") or 50)
        troop = body.get("troop") or None
        max_kills = int(body.get("maxKills") or 0)
        squads = int(body.get("squads") or 4)
        # 每队兵种分配: [{army_id, num}]。不给就按可用兵种自动挑。
        squad_spec = body.get("squadSpec") or None
        if isinstance(squad_spec, list):
            spec = []
            for s in squad_spec:
                if not isinstance(s, dict):
                    continue
                aid = str(s.get("army_id") or s.get("id") or "").strip()
                if not aid:
                    continue
                try:
                    n = int(s.get("num") or num)
                except (TypeError, ValueError):
                    n = num
                spec.append({"army_id": aid, "num": n})
            squad_spec = spec or None
        # 先把 App 停掉: 同账号只允许一个连接, 不停会被服务端互踢
        stopped = self.stop_app()
        time.sleep(1.5)
        if not self._ensure_account():
            return {"ok": False, "error": self.account_error}
        # 跨进程账号锁: 自动打怪是**长连接**, 必须整段持锁,
        # 否则别的进程(命令扫描/采集)一连就把这条常驻连接踢掉
        try:
            lock_ctx = cok_client.account_lock(timeout=3.0, purpose="auto-hunt")
            lock_ctx.__enter__()
        except cok_client.AccountBusy as e:
            return {"ok": False, "error": str(e)}
        self._hunter_lock = lock_ctx
        try:
            from cok_client import CokClient
            cl = CokClient(getattr(self.args, "game_host", None)
                           or cok_client.DEFAULT_HOST,
                           int(getattr(self.args, "game_port", None)
                               or cok_client.DEFAULT_PORT),
                           30.0, self.args.account)   # args.account 已是 dict
            cl.connect()
            cl.bin_handshake()
            cl.login()
        except Exception as e:  # noqa: BLE001
            self._release_hunter_lock()
            return {"ok": False, "error": "连接游戏服失败: %s" % str(e)[:160]}
        with self.lock:
            self.hunter_client = cl

        def emit(kind, payload):
            self.daemon.emit("hunt_" + kind, payload)
            # 打怪线程结束(正常停/致命断连)都要**把账号锁还回去**
            if kind in ("done", "stopped"):
                self._release_hunter_lock()

        hunter = cok_hunt.AutoHunter(cl, level=level, num=num, troop_id=troop,
                                     max_kills=max_kills, on_event=emit,
                                     squads=squads, squad_spec=squad_spec,
                                     # 港口定时检查**搭打怪的顺风车**:
                                     # 用打怪这条连接, 不额外开连接(也不会互踢)
                                     on_tick=self._dock_tick)
        with self.lock:
            self.hunter = hunter
            self.hunter_thread = threading.Thread(target=hunter.run, daemon=True)
            self.hunter_thread.start()
        return {"ok": True,
                "note": "已开启自动打怪(等级 %d, 每只 %d 兵)%s"
                        % (level, num, "" if stopped else " [未能停止 App, 可能被互踢]")}

    def _release_hunter_lock(self):
        """释放自动打怪持有的跨进程账号锁。"""
        lock = getattr(self, "_hunter_lock", None)
        self._hunter_lock = None
        if lock is None:
            return
        try:
            lock.__exit__(None, None, None)
        except Exception:
            pass

    def _hunter_stop(self):
        with self.lock:
            hunter = self.hunter
        if not hunter:
            self._release_hunter_lock()
            return {"ok": True, "note": "本来就没在跑"}
        hunter.stop("用户停止")
        try:
            with self.lock:
                if self.hunter_client:
                    self.hunter_client.close()
        except Exception:
            pass
        with self.lock:
            self.hunter_client = None
        self._release_hunter_lock()
        try:
            hunt = self._hunt_state()   # 停完立刻回读一次体力/设置
        except Exception:
            hunt = None
        if hunt is not None:
            with self.lock:
                self.hunt = hunt
        return {"ok": True, "note": "已停止"}

    def _hunter_state(self):
        with self.lock:
            hunter = self.hunter
        if not hunter:
            return {"running": False, "note": "未开启"}
        if isinstance(hunter, dict):
            # 预览/测试用: 直接给状态字典
            return dict(hunter)
        return dict(hunter.state)

    def _hunt_action_raw(self, body):
        """打野怪写操作: 等级范围 / 部队编成 / 开 / 停。"""
        op = body.get("op")
        cl = self.daemon.client
        if op == "set-level":
            lo = int(body.get("low") or 1)
            hi = int(body.get("high") or lo)
            p = cok_hunt.save_level(cl, lo, hi)
            return {"ok": not p.get("errorCode"), "lv": p.get("lv") or "%d;%d" % (lo, hi)}
        if op == "set-format":
            fmt = body.get("format")
            if not fmt:
                army = cok_hunt.list_army(cl)
                if not army:
                    return {"ok": False, "error": "没有可用兵种(全部在治疗中?)"}
                fmt = cok_hunt.build_format(army, int(body.get("perType") or 50))
            p = cok_hunt.save_format(cl, fmt)
            return {"ok": not p.get("errorCode"), "format": p.get("format") or fmt}
        if op == "on":
            r = cok_hunt.set_status(cl, True)
            self.daemon.emit("hunt_status", r)
            return r
        if op == "off":
            r = cok_hunt.set_status(cl, False)
            self.daemon.emit("hunt_status", r)
            return r
        if op == "army":
            # 带中文名的可选兵种(给页面的下拉用)
            return {"ok": True, "army": cok_hunt.army_choices(cl)}
        if op == "auto-start":
            return self._hunter_start(body)
        if op == "auto-stop":
            return self._hunter_stop()
        if op == "find":
            lv = int(body.get("level") or 1)
            r = cok_hunt.find_monster(cl, lv)
            if r.get("ok"):
                levels = cok_hunt.load_levels()
                r["name"] = cok_hunt.level_name(levels, lv)
            return r
        return {"ok": False, "error": "未知打野怪操作 %r" % op}

    def _hunt_action(self, body):
        """打野怪写操作: 等级范围 / 部队编成 / 开 / 停。"""
        r = self._hunt_action_raw(body)
        # 写完立刻回读一次, 让页面上的体力/编成/状态立刻生效
        try:
            hunt = self._hunt_state()
        except Exception:
            hunt = None
        if hunt is not None:
            with self.lock:
                self.hunt = hunt
        return r

    def _norm_levels(self, key, val):
        """把野怪等级范围归一化成一对合法值, 返回 (lvLow, lvHigh)。

        野怪等级范围在协议里是"下限;上限", 下限大于上限是**非法区间**。
        用户把下限调到 4 而上限还是 1 时, 这里自动把上限一起抬到 4 ——
        而不是把下限压回 1, 免得用户刚输入的值被"吃掉"(页面曾出现 [4]-[1])。
        """
        try:
            lo = int(self.settings.get("lvLow", 1))
            hi = int(self.settings.get("lvHigh", 1))
        except (TypeError, ValueError):
            lo, hi = 1, 1
        try:
            v = int(val)
        except (TypeError, ValueError):
            return lo, hi
        v = max(1, min(30, v))
        if key == "lvLow":
            lo = v
            if hi < lo:
                hi = lo
        else:
            hi = v
            if lo > hi:
                lo = hi
        return lo, hi

    def _set_setting(self, body):
        """保存一项设置(纯本地, 不碰游戏服, 不进操作锁)。"""
        key = str(body.get("key") or "")
        val = body.get("value")
        if not key:
            return {"ok": False, "error": "缺少 key"}
        # 序号守卫: 前端连续输入会并发 POST, 迟到的旧值不能覆盖新值
        seq = body.get("seq")
        if isinstance(seq, int):
            last = self.settings_seq.get(key, 0)
            if seq < last:
                return {"ok": True, "key": key, "value": self.settings.get(key),
                        "note": "忽略过期写入(seq %d < %d)" % (seq, last)}
            self.settings_seq[key] = seq
        if key in ("lvLow", "lvHigh"):
            lo, hi = self._norm_levels(key, val)
            self.settings["lvLow"] = lo
            self.settings["lvHigh"] = hi
            val = lo if key == "lvLow" else hi
        else:
            self.settings[key] = val
        self._save_settings()
        with self.lock:
            if key == "autoShield":
                self.autoshield_enabled = bool(val)
                # ⚠️ 自动开罩靠**服务端推送**(push.world.injured 等),
                # 而推送只在"等待命令响应"期间才会被收到。
                # 按需短连接模式下轮完就断开 → 永远收不到被攻击 → 自动开罩形同虚设。
                # 所以开启自动开罩时自动切到**常驻连接**。
                self.persistent = bool(val) or self.persistent_arg
        if key == "hookURL" and val:
            self.daemon.alert.url = str(val)
        elif key == "hookType" and val:
            self.daemon.alert.kind = str(val)
        return {"ok": True, "key": key, "value": val,
                "settings": {"lvLow": self.settings.get("lvLow"),
                             "lvHigh": self.settings.get("lvHigh")}}

    def _hook_test(self, body):
        """发一条测试 webhook(纯本地, 不碰游戏服)。"""
        url = str(body.get("url") or "").strip()
        kind = str(body.get("type") or "generic")
        if not url:
            return {"ok": False, "error": "先填 Webhook URL"}
        # 用独立实例, 不改 daemon 正在用的那个 —— 否则并发轮询时
        # 真实告警会被发到测试地址上
        al = D.Alert(url, kind, ["test"])
        al.push("test", "COK 控制台测试",
                ["这是一条来自 COK 直连控制台的测试消息",
                 "时间 " + time.strftime("%Y-%m-%d %H:%M:%S")])
        if al.last_error:
            return {"ok": False, "error": al.last_error}
        return {"ok": True, "note": "测试已发送到 " + kind}

    def action(self, body):
        act = (body or {}).get("action")
        # 纯本地动作: 不碰游戏服, **不进操作锁**。
        # 否则一轮慢轮询(最长 60 秒)会把"保存设置"也一起堵住。
        if act == "set-setting":
            return self._set_setting(body)
        if act == "hook-test":
            return self._hook_test(body)
        if act not in GAME_SERVER_ACTIONS:
            # 先判未知操作, 别让"设备没连上"把真正的问题盖住
            return {"ok": False, "error": "未知操作 %r" % act}
        # 操作锁: 串行化对游戏服的写操作; 状态锁只用来改内存字段。
        # 两者分开, 页面在操作进行中照样能读 /api/state。
        with self.op_lock:
            try:
                # 离线预览(假 daemon)不连游戏服, 不该抢真账号的锁
                if getattr(self, "offline_preview", False):
                    return self._action_locked(act, body)
                # 跨进程账号锁: 别的进程(命令扫描/采集)正在用这个账号就跳过
                with cok_client.account_lock(timeout=2.0, purpose="web-action"):
                    return self._action_locked(act, body)
            except cok_client.AccountBusy as e:
                holder = cok_client.account_holder()
                if "scan-world" in holder:
                    return {"ok": False,
                            "error": "全图扫描正在占用账号, 请先在「玩家坐标」卡点「停止扫描」"}
                return {"ok": False, "error": str(e)}
            except Exception as e:  # noqa: BLE001
                return {"ok": False, "error": str(e)[:200]}
            finally:
                if not self.persistent:
                    # 按需模式: 操作完立刻把账号还给 App
                    try:
                        if self.daemon.client:
                            self.daemon.client.close()
                    except Exception:
                        pass
                    self.daemon.client = None
                    with self.lock:
                        self.connected = False
        return {"ok": False, "error": "未知操作 %r" % act}

    def _action_locked(self, act, body):
        """已持有 op_lock 和跨进程账号锁, 真正去连游戏服执行操作。"""
        self._ensure_client()
        if act == "sign":
            self.daemon.auto_sign(self.daemon.ctx())
            return {"ok": True, "note": "已触发签到"}
        if act == "claim":
            self.daemon.claim(self.daemon.ctx())
            return {"ok": True, "note": "已触发领奖"}
        if act == "reconnect":
            self.daemon.connect()
            with self.lock:
                self.connected = True
            return {"ok": True, "note": "已重连"}
        if act == "autoshield":
            with self.lock:
                self.autoshield_enabled = bool(body.get("enabled"))
            return {"ok": True, "enabled": self.autoshield_enabled}
        if act == "shield":
            slot = int(body.get("slot") or 1)
            cover = int(body.get("coverOld", 1))
            spec = str(body.get("spec") or "").strip()
            notes = []
            # 指定了规格 -> 先把槽位写成该道具, 再 use
            # (槽位为空时 onekeybuff.use 会**静默失败**: 不报错也不生效)
            if spec:
                sr = self._shield_set_slot(slot, spec)
                if not sr.get("ok"):
                    return {"ok": False,
                            "error": "写保护罩槽位失败(道具 %s)" % spec}
                notes.append("槽位 %d 已设为 %s" % (slot, spec))
            r = self.daemon.client.call("onekeybuff.use",
                                        {"type": slot, "coverOld": cover})
            p = r.get("__params__") or {}
            end = p.get("shieldEndTime")
            if end:
                self.daemon.shield_end_ms = int(end)
            elif not self.daemon.shield_end_ms:
                # 既没有新的到期时间, 也没有旧状态 -> 说明根本没开成
                return {"ok": False,
                        "error": ("开罩失败: 槽位 %d 没有可用的保护罩道具"
                                  "(服务端不报错, 只是不生效)") % slot,
                        "slot": slot, "notes": notes}
            self.daemon.emit("shield_manual", {"slot": slot, "spec": spec,
                                              "result": p})
            return {"ok": True, "slot": slot,
                    "shieldEndTime": self.daemon.shield_end_ms,
                    "coverOld": cover, "notes": notes,
                    "result": p}
        if act == "speedup":
            return self._speedup(body)
        if act == "queues":
            return {"ok": True, "queues": self.snapshot()["queues"]}
        if act == "shieldslots":
            return dict(self._shield_slots(), ok=True)
        if act == "dock":
            # 港口(码头航海贸易)
            sub = body.get("op") or "read"
            if sub == "read":
                st = cok_dock.read_dock(self.daemon.client)
                self._set_dock_state(st)
                if _is_dock_disabled(st.get("errorCode")):
                    self.dock_disabled = True
                return dict(st, ok=st.get("ok", True))
            if sub == "reward":
                # 领取前先记下"哪些船本来可领", 领取后对比出"哪些没领到"
                try:
                    before = cok_dock.read_dock(self.daemon.client)
                except Exception:
                    before = {}
                pending = [s.get("uuid") for s in (before.get("rewardable") or [])]
                r = cok_dock.one_key_reward(self.daemon.client)
                st = cok_dock.read_dock(self.daemon.client)
                self._set_dock_state(st)
                self.daemon.emit("dock_reward", r)
                # 领到的明细(带中文名)
                rewards = []
                for g in (r.get("rewards") or []):
                    iid = g.get("itemId") or ""
                    rewards.append({
                        "itemId": iid,
                        "name": self._tr_item(iid) or ("道具 " + iid),
                        "addNum": g.get("addNum"),
                        "uuid": g.get("uuid"),
                    })
                # 没领到的: 领取后仍然是"可领奖"的船
                still = [s for s in (st.get("rewardable") or [])
                         if not pending or s.get("uuid") in pending]
                unclaimed = [{"uuid": s.get("uuid"),
                              "state_text": s.get("state_text"),
                              "itemId": s.get("itemId")} for s in still]
                # 记住这次领取结果, 刷新页面后仍能看到"领了多少 / 哪些没领到"
                st = dict(self.dock_state or st)
                st["last_reward"] = {
                    "at": int(time.time()),
                    "count": r.get("count"),
                    "pending": len(pending),
                    "rewards": rewards,
                    "unclaimed": unclaimed,
                }
                self._set_dock_state(st)
                return {
                    "ok": r.get("ok"),
                    "errorCode": r.get("errorCode"),
                    "errorText": self._err_text(r.get("errorCode")),
                    "error": r.get("error"),
                    "family": r.get("family") or st.get("family"),
                    "count": r.get("count"),
                    "rewards": rewards,
                    "pending": len(pending),
                    "unclaimed": unclaimed,
                    "ships": st.get("ships"),
                }
            if sub == "send":
                r = cok_dock.one_key_send(self.daemon.client)
                st = cok_dock.read_dock(self.daemon.client)
                self._set_dock_state(st)
                self.daemon.emit("dock_send", r)
                return {"ok": r.get("ok"), "errorCode": r.get("errorCode"),
                        "error": r.get("error"),
                        "family": r.get("family") or st.get("family"),
                        "count": r.get("count"),
                        "ships": st.get("ships")}
            return {"ok": False, "error": "未知港口操作 %r" % sub}
        if act == "hunt":
            return self._hunt_action(body)
        if act == "locate":
            return self._locate_action(body)
        if act == "refresh-now":
            return self.refresh_now()
        return {"ok": False, "error": "未知操作 %r" % act}

    def _locate_action(self, body):
        """按玩家名字查地图坐标。

        三条路径(按优先级):
          1. **本地索引**(map-index.json) —— 扫描器建好的, 零消耗零连接, 最快
             ⚠️ 索引是**扫描时刻的快照**: 服务端会定时重排整张地图, 玩家城整体
             迁移(实测 2026-10-25 19:39 扫的坐标, 当天 20:20 原位置已站着别人)。
             所以命中索引后会**再用一次 world.get 验证**(0.17 秒)该点是否还是他,
             是就采用服务端的最新值, 不是就说明坐标已过期。
          2. **现场扫描** —— 用 world.get 扫玩家周围一片区域建索引(也不消耗道具)
          3. **道具路径**(search.player.spy) —— 消耗「坐标侦查」道具, 最后兜底
        """
        name = str(body.get("name") or "").strip()
        uid = body.get("uid")
        sub = body.get("op") or "query"

        # 1) 本地索引
        idx = cok_map.load_index()
        hits = cok_map.find_players(idx, name, limit=20) if name else []
        if uid:
            hits = [h for h in hits if h.get("uid") == str(uid)] or hits
        expired = False
        if hits and sub != "scan":
            # 验证: 那个坐标现在还是不是他?(地图重排后原位置会换成别人)
            cand = hits[0]
            verified = None
            cx, cy = cand.get("x"), cand.get("y")
            if cx is not None and cy is not None and self.daemon.client:
                try:
                    res = cok_map.fetch_area(self.daemon.client, cx, cy)
                    still = [p for p in (res.get("players") or [])
                             if str(p.get("uid")) == str(cand.get("uid"))]
                    if still:
                        verified = still[0]
                except Exception:  # noqa: BLE001
                    verified = None
            if verified is not None:
                # 坐标还有效 -> 用服务端给的最新值(比索引新)
                out = [verified] + [h for h in hits[1:] if h.get("uid") != verified.get("uid")]
                return {"ok": True, "source": "index+verified", "count": len(out),
                        "players": out,
                        "index_total": len(idx.get("players") or {}),
                        "index_updated": (idx.get("meta") or {}).get("updated_at")}
            # 验证失败 -> 索引里的坐标已过期(服务端重排过地图), 旧的命中作废
            expired = True
            hits = []

        # 2) 现场扫描: 用 world.get 扫一片区域建索引(不消耗任何道具)
        if sub == "scan" or expired:
            radius = int(body.get("radius") or 60)
            cx = int(body.get("cx") or 0)
            cy = int(body.get("cy") or 0)
            if not cx or not cy:
                # 以**自己**的位置为中心(从队列/概览数据拿不到就认坐标)
                own = self._own_point()
                cx, cy = own
            st = cok_map.scan_area(self.daemon.client,
                                   cx - radius, cy - radius, cx + radius, cy + radius,
                                   step=cok_map.STEP,
                                   own_uid=(getattr(self.args, "account", None) or {}).get("gameUid"))
            self._last_scan_center = (cx, cy)
            idx = cok_map.load_index()
            hits = cok_map.find_players(idx, name, limit=20) if name else []
            return {"ok": True, "source": "scan",
                    "players": hits, "scan": st,
                    "center": {"x": cx, "y": cy},
                    "stale": expired,
                    "index_total": len(idx.get("players") or {})}

        if not name:
            return {"ok": False, "error": "请输入玩家名字"}

        # 3) 道具路径
        r = cok_locate.locate(self.daemon.client, name, uid=uid)
        if r.get("ok"):
            self.daemon.emit("locate_player", {"name": r.get("name"),
                                               "x": r.get("x"),
                                               "y": r.get("y")})
        else:
            r = dict(r)
            r["errorText"] = self._err_text(r.get("errorCode"))
        return dict(r, ok=bool(r.get("ok")), source="item")


    def _account_holder_self(self):
        """当前账号锁是不是本进程自己拿着。"""
        try:
            return bool(cok_client.account_holder_info().get("self"))
        except Exception:
            return False

    # ---------------- 全图扫描(独立进程) ----------------

    def _scan_status(self, idx=None):
        """全图扫描的状态: 在不在跑、进度、健康指标。

        扫描是**独立进程**, 网页重启也不影响它 —— 所以状态靠 pid 文件判断,
        不能只看索引里的 meta.scanning(进程被强杀时那个标志会一直挂着)。
        """
        pid = cok_map.read_scan_pid()
        alive = False
        if pid:
            try:
                os.kill(pid, 0)
                alive = True
            except OSError:
                alive = False
        if idx is None:
            idx = cok_map.load_index()
        meta = idx.get("meta") or {}
        # ⚠️ **不要在这里写索引**: 扫描器可能正在写同一个文件, 抢 .tmp 会让它崩。
        # "进程没了但 scanning 标志还挂着" 只影响显示(running 用 alive 判断),
        # 真正的清理由扫描器自己的 finally 负责。
        done = int(meta.get("requests_done") or 0)
        total = int(meta.get("requests_total") or 0)
        return {
            "running": bool(alive and meta.get("scanning")),
            "pid": pid if alive else None,
            "requests_done": done,
            "requests_total": total,
            "percent": round(100.0 * done / total, 1) if total else 0.0,
            "players": len(idx.get("players") or {}),
            "partial": bool(meta.get("partial")),
            "updated_at": meta.get("updated_at"),
            "self_point": meta.get("self_point") or {},
            "mismatched": int(meta.get("mismatched_responses") or 0),
            "dropped": int(meta.get("dropped_out_of_range") or 0),
            "errors": int(meta.get("errors") or 0),
        }

    def _scan_start(self, body):
        """一键启动全图扫描(独立进程, 支持断点续扫)。"""
        st = self._scan_status()
        if st.get("running"):
            return {"ok": False, "error": "扫描已经在跑了 (pid %s)" % st.get("pid")}
        # 自动打怪是常驻连接, 会一直占着账号 —— 扫描起不来
        if self.hunter and self.hunter.state.get("running"):
            return {"ok": False,
                    "error": "自动打怪正在占用账号连接, 请先停掉打怪再扫描"}
        body = body or {}
        cmd = [sys.executable, os.path.join(HERE, "scan_world.py"),
               "--out", cok_map.DEFAULT_INDEX]
        meta = (cok_map.load_index().get("meta") or {})
        # ⚠️ 先让网页**自己**把账号交出来: 扫描器和后台轮询会互相抢锁
        # (轮询每 5 秒一轮、每轮持锁 2~3 秒), 扫描器用 LOCK_NB 轮询
        # 可能整整 120 秒都抢不到空隙。暂停轮询后扫描器就能稳定拿到锁。
        self._suspend_poll = True
        self._poll_suspend_until = time.time() + 120.0
        # ⚠️ 只有「上次是**全图**扫描且被中断」才续扫 —— 小范围扫描的断点
        # 落在地图一角, 全图扫描接着它扫会把那一大片漏掉。
        runs = (cok_map.load_history().get("runs") or [])
        last_full = None
        for r in runs:
            if not int(r.get("radius") or 0):
                last_full = r
                break
        if (last_full and last_full.get("status") == "interrupted"
                and meta.get("partial") and meta.get("next_x") is not None):
            cmd.append("--resume")        # 从上次全图的断点接着扫
        step = int(body.get("step") or 12)
        cmd += ["--step", str(step)]
        radius = int(body.get("radius") or 0)
        if radius > 0:
            cmd += ["--radius", str(radius)]
        else:
            # 全图重扫: 必须从空白索引开始。旧索引的坐标属于上一次地图布局
            # (服务端会重排地图), 混进来会让众数投票选错(实测正确率 16.7%)。
            cmd.append("--fresh")
        maxreq = int(body.get("maxRequests") or 0)
        if maxreq > 0:
            cmd += ["--max-requests", str(maxreq)]
        # 限速: 服务端在请求过快时会降速, 匀速反而更快跑完
        dly = float(body.get("delay", 0.25))
        if dly > 0:
            cmd += ["--delay", str(dly)]
        # 扫描前备份现有索引 —— 扫描中途失败不至于毁掉已有数据
        bak = ""
        try:
            if (os.path.exists(cok_map.DEFAULT_INDEX)
                    and os.path.getsize(cok_map.DEFAULT_INDEX) > 1024):
                bak = os.path.join(
                    HERE, "map-index.backup-%s.json" % time.strftime("%Y%m%d-%H%M%S"))
                with open(cok_map.DEFAULT_INDEX, "rb") as fi, open(bak, "wb") as fo:
                    fo.write(fi.read())
                self._trim_scan_backups()
        except OSError:
            bak = ""
        logp = os.path.join(HERE, "scan.log")
        try:
            f = open(logp, "ab")
        except OSError:
            f = subprocess.DEVNULL
        try:
            p = subprocess.Popen(
                cmd, stdout=f, stderr=f, cwd=HERE,
                env=dict(os.environ, PYTHONUNBUFFERED="1"))
        except Exception as e:  # noqa: BLE001
            return {"ok": False, "error": "启动失败: %s" % str(e)[:140]}
        cok_map.write_scan_pid(p.pid)
        return {"ok": True, "pid": p.pid,
                "note": "扫描已启动(独立进程, 关掉网页也继续) · 日志 scan.log",
                "cmd": " ".join(cmd[1:]),
                "resumed": "--resume" in cmd,
                "backup": os.path.basename(bak) if bak else ""}

    @staticmethod
    def _trim_scan_backups(keep=3):
        """只保留最近 N 份索引备份。"""
        try:
            names = sorted(f for f in os.listdir(HERE)
                           if f.startswith("map-index.backup-")
                           and f.endswith(".json"))
            for f in names[:-keep] if len(names) > keep else []:
                try:
                    os.remove(os.path.join(HERE, f))
                except OSError:
                    pass
        except OSError:
            pass

    def _scan_stop(self):
        """停止扫描(扫描器会保存断点, 之后可续扫)。"""
        pid = cok_map.read_scan_pid()
        if not pid:
            return {"ok": False, "error": "没有正在跑的扫描"}
        try:
            os.kill(pid, signal.SIGTERM)
        except OSError as e:
            return {"ok": False, "error": "停止失败: %s" % str(e)[:100]}
        return {"ok": True, "note": "已发停止信号, 断点已保存(之后可续扫)"}

    def _scan_history(self):
        """扫描历史(最近的在前)。"""
        return cok_map.load_history()
    def _account_busy(self):
        """账号是不是被**别人**占着(本进程自己用不算)。"""
        try:
            if self._account_holder_self():
                return False
            return bool(cok_client.account_is_busy())
        except Exception:
            return False

    def _map_index_summary(self):
        """地图索引的概况(页面概览条 + 导出按钮用)。"""
        try:
            idx = cok_map.load_index()
        except Exception:
            return {"count": 0}
        sc = self._scan_status(idx)
        return {
            "count": sc["players"],
            "updated_at": sc["updated_at"],
            # 索引是**扫描时刻的快照**; 服务端会定时重排整张地图, 坐标会整体过期
            "age_h": round((time.time() - sc["updated_at"]) / 3600.0, 2)
            if sc["updated_at"] else None,
            "scanning": sc["running"],
            "partial": sc["partial"],
            "requests_done": sc["requests_done"],
            "requests_total": sc["requests_total"],
            "self_point": sc["self_point"],
            # 健康指标: 错位/越界大 = 数据不可信
            "mismatched": sc["mismatched"],
            "dropped": sc["dropped"],
            "errors": sc["errors"],
        }

    def _own_point(self):
        """自己城市的地图坐标 (x, y)。

        来源优先级:
          1. 索引里**自己那条**(load_index 已按众数观测校正过, 比 meta 可靠)
          2. 索引 meta.self_point —— 扫描时顺带定位到自己(不写死坐标, 迁城也准)
          3. 都没有 -> (0, 0), 扫描器会全图步进找自己
        """
        idx = cok_map.load_index()
        meta = idx.get("meta") or {}
        own_uid = str((getattr(self.args, "account", None) or {}).get("gameUid") or "")
        if own_uid:
            me = (idx.get("players") or {}).get(own_uid)
            if me and me.get("x") is not None:
                return (int(me["x"]), int(me["y"]))
        sp = meta.get("self_point") or {}
        if sp.get("x") is not None and sp.get("y") is not None:
            return (int(sp["x"]), int(sp["y"]))
        last = getattr(self, "_last_scan_center", None)
        if last and last != (0, 0):
            return last
        return (0, 0)

    def _speedup(self, body):
        """用道具(或金币)加速指定队列。"""
        qu = body.get("uuid")
        count = int(body.get("count") or 1)
        use_gold = bool(body.get("gold"))
        if use_gold:
            params = {"qUUID": qu, "itemUUID": "", "isGold": 1, "itemCount": 1,
                      "queueId": str(body.get("qid") or 1),
                      "queueType": str(body.get("qtype") or 1), "goldcost": "0"}
        else:
            item_uuid = body.get("itemUuid")
            if not item_uuid:
                return {"ok": False, "error": "缺少道具实例 uuid(itemUuid)"}
            params = {"qUUID": qu, "itemUUID": item_uuid, "isGold": 0,
                      "itemCount": count}
        r = self.daemon.client.call("queue.ccd", params)
        p = r.get("__params__") or {}
        self.daemon.emit("speedup_manual", {"params": params, "result": p})
        return {"ok": not p.get("errorCode"), "result": p}


class Handler(BaseHTTPRequestHandler):
    engine = None
    token = None
    server_version = "CokWeb/1.0"

    def log_message(self, fmt, *a):  # 静默默认访问日志
        pass

    def _auth(self):
        if not self.token:
            return True
        got = self.headers.get("X-Cok-Token") or ""
        if not got:
            q = self.path.split("?", 1)
            if len(q) > 1:
                for kv in q[1].split("&"):
                    if kv.startswith("t="):
                        got = kv[2:]
                        break
        return got == self.token

    def _send(self, code, body, ctype="application/json; charset=utf-8"):
        if isinstance(body, (dict, list)):
            body = json.dumps(body, ensure_ascii=False, default=str).encode("utf-8")
        elif isinstance(body, str):
            body = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        try:
            self.wfile.write(body)
        except (BrokenPipeError, ConnectionResetError):
            pass

    def do_GET(self):  # noqa: N802
        path = self.path.split("?", 1)[0]
        if path == "/favicon.ico":
            # 浏览器总会来要一次, 回 204 省得控制台里挂一条红色 404
            self.send_response(204)
            self.send_header("Cache-Control", "max-age=86400")
            self.end_headers()
            return
        if path in ("/", "/index.html"):
            if not self._auth():
                self._send(403, "无效 token, 请用 ?t=<token> 访问")
                return
            try:
                html = open(os.path.join(HERE, "cok_webui.html"), "rb").read()
            except OSError:
                self._send(500, "缺少 cok_webui.html")
                return
            self._send(200, html, "text/html; charset=utf-8")
            return
        if path == "/api/state":
            if not self._auth():
                self._send(403, {"error": "unauthorized"})
                return
            self._send(200, self.engine.snapshot())
            return
        if path == "/api/scan/status":
            if not self._auth():
                self._send(403, {"error": "unauthorized"})
                return
            self._send(200, self.engine._scan_status())
            return
        if path == "/api/scan/history":
            if not self._auth():
                self._send(403, {"error": "unauthorized"})
                return
            self._send(200, self.engine._scan_history())
            return
        if path == "/api/export":
            # 导出地图索引成 Excel(xlsx); ?players=1 只导真实玩家(排除 NPC)
            if not self._auth():
                self._send(403, {"error": "unauthorized"})
                return
            only = "players" in parse_qs(self.path.split("?", 1)[1] if "?" in self.path else "")
            try:
                idx = cok_map.load_index()
                if not (idx.get("players") or {}):
                    self._send(404, {"error": "索引里还没有玩家, 先跑一次扫描"})
                    return
                # path=None -> 直接返回 xlsx 字节
                buf = cok_excel.export_index(idx, None, players_only=only)[0]
                fname = "cok-players%s.xlsx" % ("-real" if only else "")
                self.send_response(200)
                self.send_header("Content-Type",
                                 "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
                self.send_header("Content-Disposition",
                                 'attachment; filename="%s"' % fname)
                self.send_header("Content-Length", str(len(buf)))
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
                try:
                    self.wfile.write(buf)
                except (BrokenPipeError, ConnectionResetError):
                    pass
            except Exception as e:  # noqa: BLE001
                self._send(500, {"error": "导出失败: %s" % str(e)[:160]})
            return
        self._send(404, {"error": "not found"})

    def do_POST(self):  # noqa: N802
        path = self.path.split("?", 1)[0]
        if not self._auth():
            self._send(403, {"error": "unauthorized"})
            return
        if path in ("/api/scan/start", "/api/scan/stop", "/api/scan/history"):
            n = int(self.headers.get("Content-Length") or 0)
            raw = self.rfile.read(n) if n else b"{}"
            try:
                body = json.loads(raw.decode("utf-8"))
            except Exception:
                body = {}
            if path == "/api/scan/start":
                self._send(200, self.engine._scan_start(body))
                return
            if path == "/api/scan/stop":
                self._send(200, self.engine._scan_stop())
                return
            self._send(200, self.engine._scan_history())
            return
        if path != "/api/action":
            self._send(404, {"error": "not found"})
            return
        n = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(n) if n else b"{}"
        try:
            body = json.loads(raw.decode("utf-8"))
        except Exception:
            body = {}
        self._send(200, self.engine.action(body))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="127.0.0.1", help="网页监听地址")
    ap.add_argument("--port", type=int, default=8770, help="网页监听端口")
    ap.add_argument("--game-host", default=cok_client.DEFAULT_HOST,
                    help="游戏服地址(默认 %s)" % cok_client.DEFAULT_HOST)
    ap.add_argument("--game-port", type=int, default=cok_client.DEFAULT_PORT,
                    help="游戏服端口(默认 %s)" % cok_client.DEFAULT_PORT)
    ap.add_argument("--account-device", action="store_true", default=True)
    ap.add_argument("--account", help="账号 JSON 文件(不给则自动: 设备 → 内置凭据)")
    ap.add_argument("--interval", type=int, default=300, help="轮询间隔秒(默认 5 分钟, 越短越频繁占用账号)")
    ap.add_argument("--timeout", type=float, default=60.0)
    ap.add_argument("--webhook", help="告警 webhook URL")
    ap.add_argument("--webhook-type", default="generic",
                    choices=["generic", "wechat", "dingtalk"])
    ap.add_argument("--alert-rules", nargs="+", default=D.ALL_RULES,
                    choices=D.ALL_RULES)
    ap.add_argument("--autoshield", action="store_true",
                    help="被攻击时自动开保护罩(默认关, 需在页面里开)")
    ap.add_argument("--speedup-item", default="200201")
    ap.add_argument("--speedup-count", type=int, default=1)
    ap.add_argument("--speedup-queue-type", type=int, default=1)
    ap.add_argument("--shield-slot", type=int, default=1)
    ap.add_argument("--shield-cover-old", type=int, default=1)
    ap.add_argument("--shield-cooldown", type=float, default=600.0)
    ap.add_argument("--shield-trigger", nargs="+",
                    default=["push.world.injured", "push.world.cannon.injured",
                             "push.world.march.fail"])
    ap.add_argument("--shield-trigger-force", nargs="+",
                    default=["push.world.injured"])
    ap.add_argument("--token", help="访问 token(默认自动生成)")
    ap.add_argument("--no-token", action="store_true", help="不启用鉴权(仅本机可用)")
    ap.add_argument("--persistent", action="store_true",
                    help="常驻连接(实时监控, 但会把 App 踢下线)")
    ap.add_argument("--open", action="store_true", help="启动后打开浏览器")
    ap.add_argument("--log", help="追加日志文件(与 daemon 同参数)")
    ap.add_argument("--json", action="store_true", help="日志用 JSON 行(与 daemon 同参数)")
    args = ap.parse_args()
    args.json = False   # 网页控制台走自己的事件流, 这里保持 daemon 的文本输出
    # 补齐 daemon 需要但网页不暴露的参数默认值
    for k, v in dict(
        watch=list(D.WATCHERS.keys()),
        once=False, retry_delay=10.0,
        claim=False, claim_limit=5, claim_max_total=20, auto_sign=False,
        speedup=False, speedup_gold=False,
        shield_slot=1, shield_cover_old=1, shield_cooldown=600.0,
    ).items():
        if not hasattr(args, k):
            setattr(args, k, v)

    if args.account_device:
        # 账号改成**懒加载**(Engine._ensure_account): 优先读设备,
        # 读不到就退回内置凭据 —— 所以这里不做预读, 也不因此拒绝启动
        print("[*] 账号来源: 优先设备 SharedPreferences, 读不到则用内置凭据")

    token = None if args.no_token else (args.token or read_or_make_token())
    Handler.token = token
    Handler.engine = Engine(args)
    Handler.engine.start()

    srv = ThreadingHTTPServer((args.host, args.port), Handler)
    url = "http://%s:%d/" % (args.host, args.port)
    if token:
        url += "?t=%s" % token
    print("=" * 60)
    print("  COK 直连控制台已启动")
    print("  打开: %s" % url)
    if not token:
        print("  (未启用 token —— 仅建议本机访问)")
    print("  Ctrl+C 停止")
    print("=" * 60, flush=True)
    if args.open:
        try:
            webbrowser.open(url)
        except Exception:
            pass
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\n[*] 停止中 ...")
    finally:
        Handler.engine.stop()
        srv.server_close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
