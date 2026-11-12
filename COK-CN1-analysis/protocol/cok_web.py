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
import copy
import datetime
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
import cok_stamina as cok_stamina  # noqa: E402
import cok_rally as cok_rally  # noqa: E402
import cok_client  # noqa: E402
import cok_dock  # noqa: E402
import cok_sky  # noqa: E402
import cok_welfare  # noqa: E402
import cok_scoremall  # noqa: E402
import cok_alliance  # noqa: E402
import cok_assist  # noqa: E402
import cok_daily_quest  # noqa: E402
import cok_map  # noqa: E402
import cok_excel  # noqa: E402
from cok_account import load_account  # noqa: E402
import cok_accounts as accounts  # noqa: E402
#: 渠道登录模块的导入失败信息(给页面显示用)。
#:
#: ⚠ 这里**曾经**只写 `except Exception: channel = None`, 把真实异常静默吞掉,
#:   结果安卓端只看到一句"渠道登录模块未加载", 完全查不到是哪一行炸了。
#:   2026-11-12 终于定位: cok_channel_login.py 里有个**没闭合的字符串**
#:   (公开仓库脱敏时写坏的), SyntaxError 让整个模块 import 不了 ——
#:   PC 和安卓**一起**挂掉。
#: 现在把真实原因留住, 页面直接显示, 不用再猜。
CHANNEL_IMPORT_ERROR = ""
CHANNEL_IMPORT_REASON = ""
try:
    import cok_channel_login as channel  # noqa: E402  渠道账号密码登录(果盘)
except Exception as _chan_exc:  # noqa: BLE001  模块缺失不应拖垮整个网页服务
    channel = None
    import traceback
    CHANNEL_IMPORT_ERROR = traceback.format_exc()
    CHANNEL_IMPORT_REASON = "%s: %s" % (type(_chan_exc).__name__, _chan_exc)

TOKEN_FILE = os.path.join(HERE, ".cok-web-token")
MAX_EVENTS = 300
ADB_CANDIDATES = [
    "/Users/a1234/Library/Android/sdk/platform-tools/adb",
    "adb",
]
GAME_PKG = "com.hcg.cok.nearme.gamecenter"
#: adb 探测"游戏 App 是否在跑"的**进程内共享缓存**。
#:
#: 原来每个引擎每轮轮询都各自 `adb shell ps -A`(6 秒超时), 多账号时
#: N 个引擎对**同一台设备**探测 N 次, 既慢又可能把 op_lock 拖住。
#: 桌面端只有一台设备, 结果天然可共享 —— 这里用一个带 TTL 的全局缓存,
#: TTL 内所有引擎直接复用上一次结果, 不再各自 shell。
_APP_ONLINE_TTL = 4.0
_APP_ONLINE_LOCK = threading.Lock()
_APP_ONLINE_CACHE = {"at": 0.0, "value": False}


def _probe_app_online():
    """真正执行一次 adb 探测(不走缓存)。返回 bool。"""
    for adb in ADB_CANDIDATES:
        try:
            out = subprocess.run([adb, "shell", "ps", "-A"], capture_output=True,
                                 text=True, timeout=6).stdout
        except Exception:  # noqa: BLE001
            continue
        for line in out.splitlines():
            parts = line.split()
            if len(parts) >= 2 and parts[1] == GAME_PKG:
                return True
        return False
    return False


def app_online_cached(ttl=_APP_ONLINE_TTL):
    """带 TTL 的"游戏 App 是否在跑"探测, 多引擎共享一次 adb 调用。

    TTL 内直接返回上次结果; 过期才真正 shell 一次, 并把结果和时间戳写回
    共享缓存。探测本身在锁外执行, 避免一个慢 adb 把所有引擎都堵在锁上。
    """
    now = time.time()
    with _APP_ONLINE_LOCK:
        if (now - _APP_ONLINE_CACHE["at"]) < ttl:
            return _APP_ONLINE_CACHE["value"]
    value = _probe_app_online()
    with _APP_ONLINE_LOCK:
        # 可能有并发探测同时跑完, 用最新一次为准即可(幂等)。
        _APP_ONLINE_CACHE["at"] = time.time()
        _APP_ONLINE_CACHE["value"] = value
    return value
#: 平台钩子: "停止游戏 App"(把游戏服的账号位让出来), 由外部注入。
#:
#: 安卓设备上**没有 adb**, 桌面端那条 `adb shell am force-stop` 永远失败,
#: 于是游戏 App 继续占着账号 -> 同账号两条连接 -> 游戏服互踢 ->
#: 猎人的连接刚建立就被服务端关闭(2026-11-01 在安卓端实测:
#: hunt_start -> hunt_step(stamina) -> hunt_error("连接被服务端关闭(已收 0/3 字节)")。
#: 安卓端由 android_entry.py 注入基于 ActivityManager.killBackgroundProcesses 的实现。
PLATFORM_STOP_APP = None


def set_platform_stop_app(func):
    """注册平台相关的"停止游戏 App"实现(安卓端用)。传 None 恢复默认(走 adb)。"""
    global PLATFORM_STOP_APP
    PLATFORM_STOP_APP = func


# 登录必须来自设备的字段。缺任意一个都说明"设备没连上"或"App 没登录过",
# 这时去连游戏服只会得到误导性的"连接被服务端关闭"。
ACCOUNT_REQUIRED = ("pfId", "gameUid", "deviceId", "uuid",
                    "signCode", "host", "port")
# ⚠ **platformToken 不是必需字段**: 果盘/ewanqf 渠道的账号库里它是空的
#    (pfId 里已经带了渠道 token, 见 accounts/<uid-guopan-intl>.json),
#    硬要求它会让这类账号被判成"不完整" -> 引擎静默改用内置账号 ->
#    **跑的是另一个号**(2026-10-31 在安卓端踩过: 手机上明明选了国服号,
#    实际跑的是内置凭据里的主号)。
# 需要连游戏服的操作(会占用账号连接)。set-setting / hook-test 是纯本地的,
# 不在这个名单里, 因此不会被慢轮询堵住。
#: 港口功能未开启的服务端错误码(文本 102192 = "功能未开启, 敬请期待")
#: 服务端可能把它当字符串返回, 比较前统一转 int
DOCK_DISABLED_CODE = 102192

#: 领地辅助(CityAssist): 资源类建筑 id —— 石/木/铁/食物, 产出完毕可批量收取
#: (常量来自 lua game/NewInnerCity/NewInnerCityBuildNode.lua)
ASSIST_RES_TYPES = (412000, 413000, 414000, 415000)
#: 领地辅助: 科研工坊(科研石)建筑 id (lua game/utility/gameConst.lua)
ASSIST_SCIENCE_TYPE = 437000


def _is_dock_disabled(code):
    """errorCode == 102192? (服务端有时给字符串)"""
    try:
        return int(code) == DOCK_DISABLED_CODE
    except (TypeError, ValueError):
        return False

GAME_SERVER_ACTIONS = frozenset((
    "sign", "claim", "reconnect", "autoshield", "shield", "speedup",
    "queues", "shieldslots", "hunt", "refresh-now", "dock", "sky", "locate", "welfare",
    "score", "assist-onekey", "alliance",
))

#: 账号级操作: 由 EngineManager 处理(影响全局注册表 / 运行集), 不路由到单个引擎。
MANAGER_ACTIONS = frozenset((
    "account-switch", "account-parallel", "account-remove",
    "account-add-device", "account-relabel", "account-priority", "account-parallel-batch",
    "channel-add",
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

    def __init__(self, args, pinned_key=None):
        # pinned_key: 并行模型下, 这个引擎**只**服务这个账号(gameUid), 不跟
        # 全局 active 指针走。单引擎(切换模型)时为 None, 行为同 Phase 1。
        self.pinned_key = pinned_key
        # 每个引擎要有**自己**的 args, 否则多个引擎共享同一个 args.account
        # 会互相踩(A 解析完账号写进 args.account, B 看到就不再解析了)。
        self.args = copy.copy(args)
        if pinned_key:
            self.args.account = None
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
        # 用户**主动断开**: 置位后轮询循环停在离线态, 不再自动连游戏服,
        # 直到用户点「重连」/「立即刷新」才清除。与 autoPoll(持久偏好)分开:
        # 这个是"此刻我要离线", 一次性闸门。
        self.disconnected = False
        self.last_error = None
        self.autoshield_enabled = args.autoshield
        self.persistent = bool(getattr(args, "persistent", False))
        self.last_poll = 0.0
        self.app_yield = False
        self._suspend_poll = False
        self._poll_suspend_until = 0.0
        self._app_online_flag = False
        # 切换账号会触发 sync_in_background; 快速来回切会堆出多条线程抢 op_lock。
        # 这个闸门保证"同一时刻只有一条即时同步线程", 已在跑就不再起。
        self._sync_inflight = False
        # 最近一次**成功**轮询的时间戳(秒); 0 表示还没成功过。健康看门狗用它
        # 判断某个后台账号是不是静默卡住了(长时间没有成功轮询)。
        self.last_ok_poll = 0.0
        # 上一次 stop_app() 是否真的把游戏 App 停掉了(用来判断"被服务端踢掉"
        # 的真实原因, 好给用户一条能照做的提示)
        self._app_stopped = False
        self.names = self._load_names()
        self.settings = self._load_settings()
        self._settings_account_key = ""
        self.automation_state = {"rules": {}}
        self.automation_history = self._load_automation_history()
        # 任务达成统计按账号落盘。历史只从首次看到任务状态后开始累计，避免把
        # 安装前未知的已完成任务伪造成今天的成果。
        self.task_stats = self._load_task_stats()
        self.account_error = ""
        self.account_source = ""
        self.account_note = ""      # 凭据来源的补充说明(设备号登不上时写这里)
        # 渠道(果盘)登录会话缓存: sid -> {at, account, authEnvelope, guopanUid, items}
        # 只在内存里, 30 分钟过期; 凭据(信封)不经过前端。
        self._chan_sessions = {}
        # 多账号: 当前选中账号的 id(gameUid)与显示名; 空表示还没锁定具体账号
        self.account_key = ""
        self.account_label = ""
        self._hunter_lock = None
        # 打怪从停客户端到猎人线程真正标记 running 之间也必须独占账号。
        # 仅检查 hunter.state["running"] 会留下一个建连空窗，后台轮询可能
        # 在这段时间新开连接并被服务端互踢。
        self._hunter_starting = False
        self.shield_state = {}
        self.persistent_arg = self.persistent
        # ⚠⚠ 自动开罩靠的是**服务端推送**(push.world.injured), 而推送是在
        # "等命令响应"时从 socket 读出来的 —— **短连接根本收不到**
        # (轮完就断开, 被攻击那一下多半发生在轮询窗口之外)。
        # 以前只在页面里**勾选**开关的那一刻才切常驻, 于是:
        #   设置文件里已经开着 autoShield / 重启了控制台 → 开关还在,
        #   连接却退回短连接 → 自动开罩**静默失效**(完全不报错)。
        # 这里按设置补上, 让"开着开关"和"常驻连接"始终一致。
        if self.settings.get("autoShield"):
            self.persistent = True
        self.dock_state = {}
        self.dock_disabled = False
        # 天空之境(TheHeavens)探索/领奖状态
        self.sky_state = {}
        self.sky_disabled = False
        # 福利中心(每日好礼 / 龙之馈赠)的读取与领取状态
        self.welfare_state = {}
        # 积分商城(ScoreMall, mallId=125)积分任务奖励
        self.score_state = {}
        # 联盟(科技树/任务板/捐献/使命/商店)状态
        self.alliance_state = {}
        self.alliance_at = 0.0
        self.alliance_error = ""
        # 联盟自动捐献的最近一次结果(给页面显示)
        self.alliance_auto = {}
        # 领地自动收取: 上次执行时间(秒), 用来节流
        self.assist_at = 0.0
        # 「一键完成」面板清单(13 项)与上次状态
        self.assist_panel = []
        self.assist_panel_at = 0.0
        # 自动开罩的"推送监听"心跳次数(页面显示, 用来确认它确实在跑)
        self.shield_watch_ticks = 0
        # 当前卡在哪一步(排障用: 轮询各阶段 + 推送监听)
        self.phase = "启动中"
        self.shield_watch_interval = int(getattr(args, "shield_watch_interval", 20) or 20)
        # 每个设置键的写入序号: 前端连续输入会并发 POST, 用序号挡住乱序覆盖
        self.settings_seq = {}
        # ⚠️ 用引擎**自己**的 args(可能是副本): daemon 连接时读 args.account,
        # 并行模型下每个引擎的账号不同, 不能共用同一个 args。
        self.daemon = D.Daemon(self.args)
        # 接管 emit: 事件同时进内存流(供网页显示)
        orig_emit = self.daemon.emit

        def emit(kind, payload):
            orig_emit(kind, payload)
            # 真实领取 = 权威计数源。签到成功发 sign, 每领一笔发 claim_result,
            # 都从这里汇聚 —— 手动按钮和后台自动都走 daemon.emit, 口径统一。
            try:
                self._record_from_event(kind, payload)
            except Exception:  # noqa: BLE001  记账失败绝不能拖垮事件流
                pass
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

        账号来源按优先级:
          0. **账号库里显式选中的账号**(多账号) —— 用户在页面上切过账号就用它,
             凭据直接取自注册表, 不依赖设备在不在。
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
        # 0) 账号来源:
        #    - 并行模型: 引擎被钉在 pinned_key 上, 只认自己的账号;
        #    - 切换模型: 跟随账号库的 active 指针。
        if self.pinned_key:
            active = self.pinned_key
        else:
            try:
                active = accounts.get_active_key()
            except Exception:  # noqa: BLE001
                active = ""
        if active:
            reg = accounts.get_account(active) or {}
            reg_missing = [k for k in ACCOUNT_REQUIRED if not reg.get(k)]
            if reg and not reg_missing:
                reg = dict(reg)
                reg.setdefault("host", getattr(self.args, "game_host", None)
                               or cok_client.DEFAULT_HOST)
                reg.setdefault("port", int(getattr(self.args, "game_port", None)
                                           or cok_client.DEFAULT_PORT))
                self._apply_account_meta(
                    reg, "账号库:" + (accounts.account_label(reg) or active))
                self.account_error = ""
                return True
            if reg and reg_missing:
                # ⚠ 账号库里有这个号, 但凭据不全 —— **不能**静默改用别的号!
                #    静默换号 = 用户以为在操作 A 号, 实际动的是 B 号。
                #    宁可明说"这个号缺字段", 也不要替用户做决定。
                self.account_error = (
                    "账号 %s 的凭据不完整(缺 %s); 请在「账号」页重新添加该账号, "
                    "不要让它回退到别的账号"
                    % (accounts.account_label(reg) or active, ", ".join(reg_missing)))
                # 补一句"怎么补" —— 少了这一步用户只能干瞪眼:
                # signCode 来自渠道包的签名证书, 删掉这个号、用「果盘账号登录」
                # 重新添加(或从手机「本机导入」)就能自动带回。
                if "signCode" in reg_missing:
                    self.account_error += (
                        "; signCode 跟渠道包的签名证书有关, 删掉这个号再用"
                        "「果盘账号登录」重新添加即可自动补上")
                return False
        acc = {}
        try:
            acc = load_account()
        except Exception as e:  # noqa: BLE001
            self.account_error = "读不到设备账号: %s" % str(e)[:120]
        missing = [k for k in ACCOUNT_REQUIRED if not acc.get(k)]
        if not missing:
            self._apply_account_meta(acc, "设备")
            self.account_error = ""
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
        self._apply_account_meta(builtin, "内置凭据(设备未连接)")
        self.account_error = ""
        print("[*] 设备账号不可用, 改用内置凭据: %s" % ", ".join(missing))
        return True

    def _apply_account_meta(self, acc, source):
        """settle 一个账号: 记住凭据 / 来源 / id / 显示名, 并切换数据目录。

        数据目录只有在这个账号**已登记进账号库**时才隔离到各自子目录
        (多账号模式); 没登记时保持历史行为(数据落在 protocol 根目录,
        旧的 map-index.json 照常可用) —— 这样单账号老用法完全不受影响。
        """
        self.args.account = acc
        self.account_source = source
        key = accounts.account_key(acc)
        self.account_key = key
        reg = accounts.get_account(key) if key else None
        self.account_label = ((accounts.account_label(reg) if reg else None)
                              or accounts.account_label(acc) or key)
        # 只有登记进账号库的账号才隔离(独立数据目录 + 独立锁); 否则走历史行为。
        self.account_isolated = bool(reg)
        # 账号确认后切到其独立的自动化配置、规则状态与执行历史。
        # 未登记账号保持老版本的全局配置文件，兼容现有单账号使用方式。
        if self._settings_account_key != key:
            self._settings_account_key = key
            self.settings = self._load_settings()
            self.automation_state = {"rules": {}}
            self.automation_history = self._load_automation_history()
            self.task_stats = self._load_task_stats()
        try:
            cok_map.set_data_dir(accounts.data_dir(key) if reg else None)
        except Exception:  # noqa: BLE001
            pass
        # 巨型狮鹫注册表也跟账号隔离(安卓端落在 files/cok/data, 不写 assets)
        try:
            cok_rally.set_data_dir(accounts.data_dir(key) if reg else None)
        except Exception:  # noqa: BLE001
            pass

    def _lock_key(self):
        """当前账号用于账号锁的 key。

        只要已经解析出 gameUid，就必须按它分锁。未入库的旧默认引擎若继续
        使用全局锁，而新建的账号引擎使用 uid 锁，同一账号会绕过彼此的互斥，
        导致两条连接被服务端互踢。没有可用 uid 时才回退历史全局锁。
        """
        return self.account_key or None

    def _hunter_active(self):
        """自动打怪是否正在占用或交接账号连接。"""
        if getattr(self, "_hunter_starting", False):
            return True
        hunter = self.hunter
        state = hunter if isinstance(hunter, dict) else getattr(hunter, "state", None)
        return bool(state and state.get("running"))

    def _set_hunter_starting(self, value):
        with self.lock:
            self._hunter_starting = bool(value)

    # ---- 每账号的数据文件路径(并行模型的地基) ----
    # ⚠️ cok_map 的数据目录是**进程内全局**(DEFAULT_INDEX 等)。单引擎时靠
    # _ensure_account -> set_data_dir 把全局指到当前账号就够了; 但并行模型
    # (同进程多个引擎各跑各的轮询线程)会互相覆盖这个全局 —— A 可能读到 B 的
    # 索引。所以引擎读写索引一律走**显式路径**(下面三个), 不再依赖全局状态。
    def _data_dir(self):
        """本引擎账号的数据目录; 未隔离账号退回**可写的**数据根目录。

        ⚠ 原来这里回退到 `cok_map._HERE`(模块所在目录)。在安卓端模块在
        Chaquopy 的 assets 里, 于是 automation-history.json / map-index.json
        这些**运行时文件被写进只读的打包资源目录** —— 重装即丢, 还污染 APK。
        现在统一回退到 `accounts.DATA_ROOT`(安卓端 = files/cok/data)。
        """
        if getattr(self, "account_isolated", False) and self.account_key:
            try:
                return accounts.data_dir(self.account_key)
            except Exception:  # noqa: BLE001
                pass
        try:
            os.makedirs(accounts.DATA_ROOT, exist_ok=True)
            return accounts.DATA_ROOT
        except Exception:  # noqa: BLE001
            return cok_map._HERE

    def _index_path(self):
        return os.path.join(self._data_dir(), "map-index.json")

    def _history_path(self):
        return os.path.join(self._data_dir(), "scan-history.json")

    def _pid_path(self):
        return os.path.join(self._data_dir(), "scan.pid")

    def stop_app(self):
        """把 App 停掉, 把账号让出来。

        **必须做**: 游戏服同账号只允许一个连接, App 在线时网页连上去会被服务端
        主动踢掉(表现为"连接被服务端关闭"), 看起来像命令不被接受, 其实是被互踢。

        账号可来自多个渠道包。不能固定停止 nearme 国服包: 当前账号若是果盘等
        渠道包, 真正持有游戏连接的进程仍会在线，随后必然和自动打野连接互踢。

        安卓设备上没有 adb, 所以先走平台钩子(ActivityManager 杀进程);
        钩子不存在或失败再退回 adb(桌面端)。
        """
        account = getattr(self.args, "account", None) or {}
        package = str(account.get("packageName") or GAME_PKG).strip() or GAME_PKG
        hook = PLATFORM_STOP_APP
        if hook is not None:
            try:
                if hook(package):
                    self._app_stopped = True
                    return True
            except Exception:  # noqa: BLE001  钩子失败不算致命, 继续试 adb
                pass
        for adb in ADB_CANDIDATES:
            try:
                result = subprocess.run([adb, "shell", "am", "force-stop", package],
                               capture_output=True, timeout=8)
                if result.returncode == 0:
                    self._app_stopped = True
                    return True
            except Exception:
                continue
        self._app_stopped = False
        return False

    # ---------- 设置持久化(跨刷新/跨浏览器) ----------
    SETTINGS_FILE = os.path.join(HERE, "web-settings.json")
    # 默认值: 保证页面回填时每一项都有值, 不会出现"上限空着、下限填了"的乱象
    DEFAULT_SETTINGS = {
        "autoSign": False, "autoShield": False, "cover": True,
        "autoPoll": True, "hookType": "generic", "hookURL": "",
        "lvLow": 1, "lvHigh": 1,
        "perType": 50, "squads": 4, "huntMax": 0,
        # 福利中心(每日好礼/龙之馈赠)自动领取
        "autoWelfare": False,
        # 积分商城积分任务: 可领时自动领(领奖, 风险低), 默认关
        "scoreAutoClaim": False,
        # 港口(码头航海贸易)自动: 默认都关, 由用户显式打开
        "dockAutoReward": False, "dockAutoSend": False,
        # 天空之境(探索消耗战力/部队, 风险高): 默认都关, 由用户显式打开
        "skyAutoReward": False, "skyAutoExplore": False,
        # 自动化安全策略。所有会写入游戏的后台规则都在服务端检查这些值，
        # 不能仅靠手机 UI 约束。
        "automationPaused": False,
        "automationMode": "execute",  # execute | notify
        "automationMaxFailures": 3,
        "automationBackoffMinutes": 15,
        # 只有需要人处理的自动化异常才进入手机提醒。all = 每次失败，
        # failures = 达到连续失败阈值后提醒，off = 不提醒。
        "automationAlertLevel": "failures",
        "huntMinStamina": 18,
        "skyMinPower": 0,
        "dockMinResourceReserve": 0,
    }

    AUTOMATION_RULES = (
        ("autoSign", "每日签到"),
        ("autoShield", "被攻击自动保护"),
        ("autoWelfare", "福利自动领取"),
        ("scoreAutoClaim", "积分任务自动领取"),
        ("dockAutoReward", "港口自动领取"),
        ("dockAutoSend", "港口自动分派"),
        ("skyAutoReward", "天空之境自动领奖"),
        ("skyAutoExplore", "天空之境自动探索"),
        ("allianceDonate", "联盟自动捐献"),
        ("allianceSignIn", "联盟自动签到"),
        ("assistAuto", "一键完成自动执行"),
    )

    def _load_settings(self):
        d = {}
        try:
            with open(self._settings_file(), encoding="utf-8") as f:
                loaded = json.load(f)
            if isinstance(loaded, dict):
                d = loaded
        except Exception:
            # 首次把旧的全局配置平滑带入账号独立配置；之后不会再共享。
            if self._settings_file() != self.SETTINGS_FILE:
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
            path = self._settings_file()
            os.makedirs(os.path.dirname(path), exist_ok=True)
            tmp = path + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=1)
            os.replace(tmp, path)
        except Exception:
            pass

    def _settings_file(self):
        if getattr(self, "account_isolated", False) and self.account_key:
            return accounts.data_path(self.account_key, "automation-settings.json")
        return self.SETTINGS_FILE

    def _automation_history_path(self):
        return os.path.join(self._data_dir(), "automation-history.json")

    def _task_stats_path(self):
        return os.path.join(self._data_dir(), "task-stats.json")

    def _load_task_stats(self):
        """读取任务达成事件账本；损坏或旧格式时从干净基线重新开始。"""
        try:
            with open(self._task_stats_path(), encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict) and isinstance(data.get("events"), list):
                data.setdefault("version", 1)
                data.setdefault("started_at", int(time.time()))
                data.setdefault("baseline", {})
                data.setdefault("current", {})
                return data
        except Exception:
            pass
        return {"version": 1, "started_at": int(time.time()), "baseline": {},
                "current": {}, "events": []}

    def _save_task_stats(self):
        try:
            path = self._task_stats_path()
            os.makedirs(os.path.dirname(path), exist_ok=True)
            self.task_stats["events"] = (self.task_stats.get("events") or [])[-1000:]
            tmp = path + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(self.task_stats, f, ensure_ascii=False, separators=(",", ":"))
            os.replace(tmp, path)
        except Exception:
            pass

    @staticmethod
    def _task_periods(server_date):
        """将服务器日期归一为日 / ISO 周 / 月，时区不再由手机本地时间猜。"""
        try:
            day = datetime.date.fromisoformat(str(server_date)[:10])
        except (TypeError, ValueError):
            day = datetime.datetime.now().date()
        iso = day.isocalendar()
        return {"day": day.isoformat(), "week": "%04d-W%02d" % (iso[0], iso[1]),
                "month": day.strftime("%Y-%m")}

    @staticmethod
    def _task_snapshot(states):
        """从 watcher 的只读状态提取可稳定比较的任务键。"""
        states = states or {}
        daily = states.get("dailyQuest") or {}
        lord = states.get("lordTask") or {}
        story = states.get("storyTask") or {}
        sign = states.get("dailySign") or {}
        ready = sorted(str(x.get("id")) for x in (daily.get("可领日常任务") or [])
                       if isinstance(x, dict) and x.get("id") is not None)
        weekly = sorted(str(x) for x in (daily.get("周任务可领奖励") or []) if x is not None)
        finished_story = sorted(str(x.get("id")) for x in (story.get("任务") or [])
                               if isinstance(x, dict) and str(x.get("state")) == "1"
                               and x.get("id") is not None)
        return {
            "signed": sign.get("今日已签") is True,
            "daily_ready": ready,
            "weekly_ready": weekly,
            "week_end": str(daily.get("周结束时间") or ""),
            "lord_claimed": int(lord.get("已领档位数") or 0),
            "lord_remaining": int(lord.get("未完成任务数") or 0),
            "story_finished": finished_story,
            "story_total": int(story.get("任务数") or len(story.get("任务") or [])),
        }

    def _record_task_stat(self, kind, count, periods, detail="", source="sync"):
        """记录一条实际达成；detail 保留给移动端展示具体任务/奖励。"""
        count = int(count or 0)
        if count <= 0:
            return
        self.task_stats.setdefault("events", []).append({
            "at": int(time.time()), "kind": kind, "count": count,
            "detail": str(detail or ""), "source": source,
            "day": periods["day"], "week": periods["week"], "month": periods["month"],
        })

    def _record_task_completion(self, kind, count=1, detail="", source="manual"):
        """供真实成功操作调用，以服务端日期归档而不是设备本地日期。"""
        with self.lock:
            self._record_task_stat(kind, count, self._task_periods(self.daemon.ctx().get("date")),
                                   detail=detail, source=source)
            self._save_task_stats()

    def _record_hunt_kills(self, kills):
        """把自动打怪的**累计击杀数**记进"任务达成明细"(只记累计数, 不记明细)。

        用**增量**记账: 只有比上次多出来的部分才算新击杀,
        否则会把累计值反复累加(每轮 tick 都加一次 -> 数字暴涨)。

        返回本次记入的数量(0 = 没有新增击杀)。
        """
        try:
            n = int(kills or 0)
        except (TypeError, ValueError):
            return 0
        seen = int(getattr(self, "_hunt_kills_seen", 0) or 0)
        delta = n - seen
        if delta <= 0:
            return 0
        self._hunt_kills_seen = n
        try:
            # detail 留空 -> 面板上只显示"打怪击杀 N", 不展开明细
            self._record_task_completion("hunt_kills", delta, "", source="auto")
        except Exception:  # noqa: BLE001
            pass
        return delta

    def _record_from_event(self, kind, payload):
        """从 daemon 事件里提取**真实领取**并记账(权威计数源)。

        - sign         : 签到成功(有奖励且无错误码) -> 每服务器日至多一次
        - claim_result : 每领到一笔奖励(award 非空) -> 按 taskKind 归类
        港口 / 好礼 / 天空走各自的 _record_task_completion, 不在这里重复。
        """
        if not isinstance(payload, dict):
            return
        if kind == "sign":
            if payload.get("errorCode"):
                return
            # daemon 只在 monthlySign.sign **写成功**后才 emit "sign"(已签走
            # sign_skip, 失败走 sign_error), 所以"无错误码"即视为真实签到;
            # 不强求 reward 非空, 避免个别无奖励返回被漏记。
            day = self._task_periods(self.daemon.ctx().get("date"))["day"]
            with self.lock:
                for ev in (self.task_stats.get("events") or []):
                    if ev.get("kind") == "sign" and ev.get("day") == day:
                        return   # 当天已记过签到, 不重复
            self._record_task_completion("sign", 1, "每日签到", source="auto")
            return
        if kind == "claim_result":
            if payload.get("errorCode"):
                return
            award = payload.get("award")
            if not award:
                return   # 没真领到(award 为空)就不算达成
            task_kind = payload.get("taskKind") or "task_reward"
            detail = ""
            try:
                if isinstance(award, list):
                    detail = ", ".join(self._reward_text(award))
            except Exception:  # noqa: BLE001
                detail = ""
            if not detail:
                detail = {"lord_milestone": "领主任务阶段奖励",
                          "weekly_reward": "周任务奖励",
                          "story_task": "主线任务奖励"}.get(task_kind, "任务奖励")
            self._record_task_completion(task_kind, 1, detail, source="auto")
            return

    def _update_task_stats(self, states, server_date):
        """刷新"当前周期状态"展示用的快照 —— **不再用差分计数**。

        旧做法是对比上一轮快照里"可领"的任务来计数, 但"可领"≠"已领":
        一个任务只要可领却没领, 跨天/跨周会被反复记; 装控制台当天已完成的
        部分又会被首轮基线整段吞掉。真实的日/周/月计数现在改由
        `_record_from_event` 在**领取成功**时写入(见 emit 包装)。
        这里只维护 `current`, 给页面"当前状态"那行用。
        """
        current = self._task_snapshot(states)
        with self.lock:
            self.task_stats["current"] = current
            self.task_stats.setdefault("baseline", {})
            self._save_task_stats()

    def _task_stats_view(self):
        """返回看板所需的周期汇总和当前周期任务状态。"""
        doc = self.task_stats or {}
        events = doc.get("events") or []
        periods = self._task_periods(self.daemon.ctx().get("date"))
        labels = {"sign": "每日签到", "daily_task": "日常任务", "weekly_reward": "周任务奖励",
                  "lord_milestone": "领主任务阶段", "story_task": "主线任务",
                  "dock_reward": "港口领取", "dock_cargo_reward": "码头宝箱领取",
                  "welfare_daily": "每日好礼", "welfare_dragon": "龙之馈赠",
                  "sky_reward": "天空之境探索奖励",
                  "sky_explore": "天空之境探索",
                  # 打怪: 只记累计击杀数(不记明细)
                  "hunt_kills": "打怪击杀"}
        out = {"started_at": int(doc.get("started_at") or 0), "current": doc.get("current") or {},
               "periods": {}}
        for name, value in periods.items():
            breakdown = {}
            for item in events:
                if item.get(name) == value:
                    kind = item.get("kind")
                    row = breakdown.setdefault(kind, {"count": 0, "details": {}})
                    count = int(item.get("count") or 0)
                    row["count"] += count
                    detail = str(item.get("detail") or "")
                    if detail:
                        row["details"][detail] = row["details"].get(detail, 0) + count
            rows = []
            for key, row in sorted(breakdown.items()):
                rows.append({"key": key, "label": labels.get(key, key), "count": row["count"],
                             "details": [{"label": detail, "count": count}
                                         for detail, count in sorted(row["details"].items())]})
            out["periods"][name] = {"label": value, "total": sum(row["count"] for row in breakdown.values()),
                                    "breakdown": rows}
        return out

    def _load_automation_history(self):
        try:
            with open(self._automation_history_path(), encoding="utf-8") as f:
                data = json.load(f)
            return data[-300:] if isinstance(data, list) else []
        except Exception:
            return []

    def _save_automation_history(self):
        try:
            path = self._automation_history_path()
            os.makedirs(os.path.dirname(path), exist_ok=True)
            tmp = path + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(self.automation_history[-300:], f, ensure_ascii=False)
            os.replace(tmp, path)
        except Exception:
            pass

    def _automation_rule(self, key):
        rule = self.automation_state.setdefault("rules", {}).setdefault(key, {})
        rule.setdefault("last_at", 0)
        rule.setdefault("last_success_at", 0)
        rule.setdefault("last_result", "waiting")
        rule.setdefault("last_reason", "等待下一次检查")
        rule.setdefault("failures", 0)
        return rule

    def _automation_record(self, key, status, summary, reason="", source="auto", force=False):
        now = int(time.time())
        rule = self._automation_rule(key)
        # 正常等待是高频巡检的预期结果。状态和原因没有变化时不反复写历史，
        # 否则 8 条规则会很快冲掉用户真正需要查看的成功/失败记录。
        if (not force and status == "waiting" and rule.get("last_result") == status
                and rule.get("last_reason") == (reason or summary)
                and now - int(rule.get("last_at") or 0) < 3600):
            return
        rule.update({"last_at": now, "last_result": status,
                     "last_reason": reason or summary})
        if status == "success":
            rule["last_success_at"] = now
            rule["failures"] = 0
        elif status == "failed":
            rule["failures"] = int(rule.get("failures") or 0) + 1
        else:
            rule["failures"] = int(rule.get("failures") or 0)
        record = {"id": "%d-%s" % (now * 1000, key), "at": now,
                  "account_key": self.account_key, "source": source,
                  "rule": key, "status": status, "summary": summary,
                  "reason": reason, "attempt": int(rule.get("failures") or 0) + 1}
        self.automation_history.append(record)
        self.automation_history = self.automation_history[-300:]
        self._save_automation_history()

    def _automation_alerts(self):
        """当前真正需要人工关注的自动化异常，供原生端待办和通知共用。"""
        level = self.settings.get("automationAlertLevel", "failures")
        if level == "off":
            return []
        threshold = max(1, int(self.settings.get("automationMaxFailures") or 3))
        alerts = []
        for key, label in self.AUTOMATION_RULES:
            state = self._automation_rule(key)
            failures = int(state.get("failures") or 0)
            if state.get("last_result") != "failed":
                continue
            if level == "failures" and failures < threshold:
                continue
            alerts.append({"key": key, "label": label,
                           "reason": state.get("last_reason") or "自动化执行失败",
                           "failures": failures,
                           "last_at": int(state.get("last_at") or 0),
                           "backoff": failures >= threshold})
        return alerts

    def _automation_allowed(self, key):
        if self.settings.get("automationPaused"):
            return False, "已暂停全部自动化"
        if self.settings.get("automationMode") == "notify":
            return False, "仅提醒模式，不会写入游戏"
        rule = self._automation_rule(key)
        limit = max(1, int(self.settings.get("automationMaxFailures") or 3))
        backoff = max(1, int(self.settings.get("automationBackoffMinutes") or 15)) * 60
        if int(rule.get("failures") or 0) >= limit and time.time() - int(rule.get("last_at") or 0) < backoff:
            return False, "连续失败，正在退避 %d 分钟" % (backoff // 60)
        return True, ""

    def _automation_snapshot(self):
        rules = []
        for key, label in self.AUTOMATION_RULES:
            state = dict(self._automation_rule(key))
            enabled = bool(self.settings.get(key, False))
            if self.settings.get("automationPaused"):
                status, reason = "paused", "已暂停全部自动化"
            elif not enabled:
                status, reason = "disabled", "规则未开启"
            elif self.settings.get("automationMode") == "notify":
                status, reason = "notify", "仅提醒，不会写入游戏"
            else:
                status, reason = state.get("last_result", "waiting"), state.get("last_reason", "等待下一次检查")
            rules.append(dict(key=key, label=label, enabled=enabled, status=status,
                              reason=reason, last_at=state.get("last_at", 0),
                              last_success_at=state.get("last_success_at", 0),
                              failures=state.get("failures", 0),
                              next_check_at=int(self.last_poll or 0) + int(self.args.interval or 300)))
        return {"paused": bool(self.settings.get("automationPaused")),
                "mode": self.settings.get("automationMode", "execute"),
                "rules": rules, "history": list(reversed(self.automation_history[-80:])),
                "alerts": self._automation_alerts(),
                "policy": {k: self.settings.get(k) for k in (
                    "automationMaxFailures", "automationBackoffMinutes", "automationAlertLevel", "huntMinStamina",
                    "skyMinPower", "dockMinResourceReserve")}}

    def _record_manual_action(self, act, result):
        if act == "refresh-now":
            return
        labels = {"sign": "手动签到", "claim": "手动领取任务奖励",
                  "assist-onekey": "手动收取领地资源", "shield": "手动开启保护罩",
                  "speedup": "手动加速队列", "hunt": "手动打怪操作",
                  "dock": "手动港口操作", "sky": "手动天空之境操作",
                  "welfare": "手动领取福利", "score": "手动积分商城操作"}
        if act not in labels:
            return
        ok = bool((result or {}).get("ok", False))
        note = str((result or {}).get("errorText") or (result or {}).get("errorCode")
                   or (result or {}).get("hint") or (result or {}).get("note")
                   or (result or {}).get("error") or "已提交")
        self._automation_record(act, "success" if ok else "failed", labels[act], note, source="manual")

    def app_online(self):
        """检测 App 是否在跑(游戏服同账号只允许一个连接, 必须互相让路)。

        走**进程内共享缓存**: 多个引擎对同一台设备不再各自 shell adb,
        TTL 内复用同一次探测结果。
        """
        value = app_online_cached()
        self._app_online_flag = value
        return value

    # ---------- 生命周期 ----------
    def start(self):
        self._thread = threading.Thread(target=self._loop, name="cok-web-engine", daemon=True)
        self._thread.start()

    def stop(self):
        """停止后台引擎，并立即放弃它持有的游戏服连接。

        EngineManager 在账号导入/切换时会 prune 旧引擎。只置 stop 标志会让
        已建立的连接等到下一轮循环才释放，新引擎若连接同账号就会被服务端
        互踢。关闭 socket 是可重入的，故意不等待可能卡住的网络 I/O。
        """
        self._stop.set()
        try:
            self._hunter_stop()
        except Exception:  # noqa: BLE001
            pass
        cli = self.daemon.client
        self.daemon.client = None
        if cli is not None:
            try:
                cli.close()
            except Exception:  # noqa: BLE001
                pass
        with self.lock:
            self.connected = False
            self._hunter_starting = False

    def sync_in_background(self):
        """Request an immediate first snapshot without holding an API response open.

        A newly imported channel account may have auto-poll disabled from a prior
        account's settings.  In that case the normal loop intentionally stays
        idle, which left the mobile UI looking as if importing had done nothing.
        This one-shot read is explicit user intent and is serialized by op_lock.
        """
        with self.lock:
            # 去重: 已有一条即时同步线程在跑就不再起 —— 快速来回切账号时,
            # 多条线程会一起抢 op_lock, 反而让切换更慢更不连贯。
            if self._sync_inflight:
                return
            self._sync_inflight = True
            self.disconnected = False
            self.phase = "正在同步"

        def run():
            try:
                result = self.refresh_now()
                if not result.get("ok"):
                    with self.lock:
                        self.phase = "同步失败"
                        self.last_error = str(result.get("note") or "读取游戏数据失败")[:200]
            finally:
                with self.lock:
                    self._sync_inflight = False

        threading.Thread(target=run, name="cok-initial-sync", daemon=True).start()

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
            if self._hunter_active():
                # ⚠️ 必须带"让出账号"这个关键字: _loop 靠它判断"这轮别碰连接,
                #    睡到下轮"。少了它就会继续走「推送监听」分支, 戳一下连接 ->
                #    重连 -> 把 AutoHunter 的连接踢了(同账号只允许一个连接),
                #    表现就是"点打怪后 30 秒报连接被服务端关闭"。
                return False, "自动打怪占用连接, 已让出账号, 已跳过本轮"
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
                with cok_client.account_lock(timeout=0.0, purpose="web-poll",
                                             key=self._lock_key()):
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

    def _connect_game_server(self):
        """连接游戏服，并在服务端指出角色迁服时修复已保存的区服信息。

        为什么需要: 手机上可能同时装了多个渠道包(国服/渠道服), 它们的
        SharedPreferences 里各有一套账号 —— 其中一套可能没登录/被风控
        (服务端回 `{"ep":["E002"],"ec":28}`), 而我们真正在玩的是**内置凭据**
        那个号。以前是"设备账号字段齐就用设备账号", 一旦那套号登不上,
        控制台就整个连不上(页面只显示"连接异常 E002")。

        内置凭据是从线上登录请求复原的(signCode 来自 APK 签名), 不依赖设备。
        """
        try:
            self.daemon.connect()
            return
        except Exception as e:  # noqa: BLE001
            first = str(e)[:120]
        if self._refresh_registered_account_zone(first):
            try:
                self.daemon.connect()
                return
            except Exception as e:  # noqa: BLE001
                first = str(e)[:120]
        if self.account_source != "设备":
            raise RuntimeError(first)
        # 设备账号不行 -> 换内置凭据
        builtin = dict(cok_client.ACCOUNT)
        builtin.setdefault("host", getattr(self.args, "game_host", None)
                           or cok_client.DEFAULT_HOST)
        builtin.setdefault("port", int(getattr(self.args, "game_port", None)
                                       or cok_client.DEFAULT_PORT))
        self.args.account = builtin
        self.account_source = "内置"
        self.account_note = ("设备账号登不上(%s), 已改用内置凭据" % first)
        self.daemon.connect()

    def _refresh_registered_account_zone(self, login_error):
        """修复已入库角色过期的区服、端口和登录字段。

        角色迁服后，旧的 ``zn`` 或 ``serverId`` 会让登录服返回
        ``E003_ZONE_<实际区服>``，该响应没有会话 ``id``。从 pfId 重查
        getserverlist.php 可得到角色当前的 zone/uuid/buildCode；只在返回的
        gameUid 与当前账号一致时才写回，避免把账号 A 的凭据套给账号 B。
        """
        match = re.search(r"E003_ZONE_(\d+)", str(login_error or ""))
        if not self.account_key:
            return False
        current = accounts.get_account(self.account_key)
        if not current:
            return False
        pf_id = str(current.get("pfId") or current.get("platformUid") or "").strip()
        if not pf_id:
            return False
        try:
            import cok_gamesvc
            pf = str(current.get("pf") or "")
            channel_name = str(current.get("channel") or "")
            if not channel_name:
                channel_name = pf[3:] if pf.startswith("cn_") else pf
            resolved = cok_gamesvc.resolve_character(
                pf_id,
                pf=pf or None,
                channel=channel_name or None,
                package=current.get("packageName") or None,
            )
        except Exception:  # noqa: BLE001
            return False
        if not resolved.get("ok") or str(resolved.get("gameUid")) != self.account_key:
            return False
        actual_zone = str(resolved.get("zn") or "")
        expected_zone = "COK%s" % match.group(1) if match else ""
        if expected_zone and actual_zone != expected_zone:
            return False
        updated = dict(current)
        for field in ("uuid", "buildCode", "zn", "serverId"):
            value = resolved.get(field)
            if value:
                updated[field] = str(value)
        game_port = cok_gamesvc.game_tcp_port(resolved.get("serverId"))
        if game_port:
            updated["port"] = game_port
        if updated == current:
            return False
        accounts.save_account(updated)
        self._apply_account_meta(updated, self.account_source)
        self.account_note = "已将账号区服更新为 %s，正在重新连接" % actual_zone
        return True

    def _publish_watcher_state(self, name, state):
        """Expose each successful watcher result without waiting for full poll."""
        with self.lock:
            self.states[name] = state
            self.connected = True
            self.last_error = None
            self.last_poll = time.time()
            self.last_ok_poll = self.last_poll
            if name == "buildQueue" and isinstance(state, dict):
                self.gold = state.get("金币")

    def _poll_locked(self):
        """已持有 op_lock 和跨进程账号锁, 真正去连游戏服拉数据。"""

        if not self.daemon.client:
            # Handshake success is meaningful on its own. Some optional watcher
            # commands take a long time (or time out and reconnect) on channel
            # accounts, so do not make the mobile UI look idle until every one
            # of those reads finishes.
            self.phase = "正在同步"
            self._connect_game_server()
            with self.lock:
                self.connected = True
                self.last_error = None
        # Publish each successful result as it arrives.  The watcher list has
        # overview first, so an optional task endpoint cannot keep a newly
        # imported account on an unusable blank screen.
        self.daemon.poll_once(on_state=self._publish_watcher_state)
        with self.lock:
            self.connected = True
            self.last_error = None
            self.last_poll = time.time()
            self.last_ok_poll = self.last_poll
            for name, st in self.daemon.last_state.items():
                self.states[name] = st
            bq = self.states.get("buildQueue") or {}
            if isinstance(bq, dict):
                self.gold = bq.get("金币")
            if not self.settings.get("autoShield", self.autoshield_enabled):
                self.autoshield_enabled = False
            self._update_task_stats(self.states, self.daemon.ctx().get("date"))
        # 自动签到 / 自动开罩 / webhook —— 全部以网页保存的设置为准
        if self.settings.get("autoSign", False):
            allowed, reason = self._automation_allowed("autoSign")
            if not allowed:
                self._automation_record("autoSign", "skipped", "自动签到未执行", reason)
            else:
                try:
                    self.daemon.auto_sign(self.daemon.ctx())
                    self._automation_record("autoSign", "success", "已检查每日签到")
                except Exception as e:  # noqa: BLE001
                    msg = "自动签到失败: %s" % str(e)[:120]
                    self._automation_record("autoSign", "failed", msg, msg)
                    with self.lock:
                        self.last_error = msg
        if self.settings.get("autoShield", self.autoshield_enabled):
            allowed, reason = self._automation_allowed("autoShield")
            if not allowed:
                self._automation_record("autoShield", "skipped", "自动保护未执行", reason)
            else:
                self.autoshield_enabled = True
                try:
                    self.daemon.autoshield(self.daemon.ctx())
                    self._automation_record("autoShield", "success", "自动保护已检查")
                except Exception as e:  # noqa: BLE001
                    msg = "自动保护失败: %s" % str(e)[:120]
                    self._automation_record("autoShield", "failed", msg, msg)
        # 自动签到 / 自动开罩 / webhook —— 全部以网页保存的设置为准
        """legacy marker: automation is handled above with policy enforcement."""
        hook_url = self.settings.get("hookURL")
        if hook_url:
            self.daemon.alert.url = hook_url
        hook_kind = self.settings.get("hookType")
        if hook_kind:
            self.daemon.alert.kind = hook_kind
        # 保护罩状态(槽位 + 当前到期时间) —— 复用本轮连接, 不额外占号。
        # 服务端**只在有罩时**才给 shieldEndTime, 所以这一项天然"有罩才有值"。
        try:
            self.phase = "保护罩"
            sh = self._shield_slots()
            with self.lock:
                self.shield_state = sh
        except Exception as e:  # noqa: BLE001
            with self.lock:
                self.shield_state = {"error": str(e)[:120]}
        # 打野怪状态(体力/等级/自动打怪设置) —— 复用本轮连接, 不额外占号
        try:
            self.phase = "打野怪"
            hunt = self._hunt_state()
        except Exception as e:  # noqa: BLE001
            hunt = {"error": str(e)[:160]}
        with self.lock:
            self.hunt = hunt
        # 港口(码头航海贸易): 顺带查一次, 并按设置做自动领取/自动分派
        self.phase = "港口"
        self._safe_tick(self._dock_tick)
        # 天空之境(TheHeavens): 顺带查一次, 并按设置做自动领取/自动探索
        self.phase = "天空之境"
        self._safe_tick(self._sky_tick)
        # 福利中心(每日好礼 / 龙之馈赠): 每天可领, 按设置自动领
        self.phase = "福利中心"
        self._safe_tick(self._welfare_tick)
        # 积分商城: 积分任务奖励, 按设置自动领
        self.phase = "积分商城"
        self._safe_tick(self._score_tick)
        # 联盟: 科技树/任务板/捐献/使命/商店(只读, 写操作由页面显式触发)
        self._safe_tick(self._alliance_tick)
        # 领地自动收取(定时结算已产出的资源, 无损)
        self._safe_tick(self._assist_auto_tick)
        # 「一键完成」面板清单(只读), 5 分钟刷一次就够
        self._safe_tick(self._assist_panel_tick)
        self.phase = "空闲"
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
        # 码头宝箱(港口活动奖励位): 数据在**登录时的 init 推送**里,
        # 不在 newBoat.data 里 —— 所以必须单独读, 否则第一格永远"空载"。
        try:
            st["cargo"] = cok_dock.read_cargo(cli)
        except Exception:  # noqa: BLE001
            st["cargo"] = {"ok": False}
        acted = []
        reward_result = None
        explore_result = None
        reward_allowed, reward_reason = self._automation_allowed("dockAutoReward")
        send_allowed, send_reason = self._automation_allowed("dockAutoSend")
        if auto_reward and not reward_allowed:
            self._automation_record("dockAutoReward", "skipped", "港口自动领取未执行", reward_reason)
        if auto_send and not send_allowed:
            self._automation_record("dockAutoSend", "skipped", "港口自动分派未执行", send_reason)
        if auto_reward and reward_allowed and st.get("rewardable"):
            try:
                rewardable_count = len(st.get("rewardable") or [])
                rr = cok_dock.one_key_reward(cli)
                acted.append("自动领取 %d 船的奖励%s" % (
                    rewardable_count,
                    "" if rr.get("ok") else "(失败 %s)" % rr.get("errorCode")))
                if rr.get("ok"):
                    self._record_task_completion("dock_reward", rewardable_count,
                                                 "港口船只奖励", source="auto")
                st = cok_dock.read_dock(cli)
            except Exception as e:  # noqa: BLE001
                acted.append("自动领取失败: %s" % str(e)[:80])
        # 码头宝箱(第一格)也要自动领 —— 不然"可领时自动领"对第一格完全不生效,
        # 页面显示"可领取"却永远领不到。
        if auto_reward and reward_allowed:
            try:
                cg = st.get("cargo") or {}
                if cok_dock.cargo_claimable(cg, self._server_now_ms()):
                    cr = cok_dock.claim_cargo(cli)
                    if cr.get("ok"):
                        self._record_task_completion(
                            "dock_cargo_reward", 1,
                            "码头宝箱 " + (", ".join(self._reward_text(cr.get("rewards") or [])) or "奖励"),
                            source="auto")
                        acted.append("自动领取码头宝箱 %s" % (
                            ", ".join(self._reward_text(cr.get("rewards") or [])) or "奖励"))
                    elif cr.get("errorCode") != cok_dock.CARGO_NOT_READY:
                        # E100148 = 还没到时间/次数用完, 正常状态, 不算失败
                        acted.append("码头宝箱领取失败(%s)" % (cr.get("errorCode") or "未知"))
                    # 领取后状态变了(成功或被拒都会回新状态), 重读
                    st["cargo"] = cok_dock.read_cargo(cli)
            except Exception as e:  # noqa: BLE001
                acted.append("码头宝箱领取失败: %s" % str(e)[:80])
        if auto_send and send_allowed and st.get("idle"):
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
            statuses = ("failed" if "失败" in "; ".join(acted) else "success")
            if auto_reward:
                self._automation_record("dockAutoReward", statuses, "; ".join(acted))
            if auto_send:
                self._automation_record("dockAutoSend", statuses, "; ".join(acted))
        elif auto_reward and reward_allowed:
            self._automation_record("dockAutoReward", "waiting", "暂无可领取的港口奖励")
        elif auto_send and send_allowed:
            self._automation_record("dockAutoSend", "waiting", "暂无空闲船位")
        self._set_dock_state(st)

    def _record_sky_reward(self, rr, source="auto"):
        """天空之境领奖记账(自动/手动共用)。

        独立成一个方法, 是为了让"记账失败"和"领奖失败"彻底分开:
        **领奖成功就一定要在日/周/月统计里留一条**, 记账出错只记日志,
        不能反过来把领奖说成失败, 也不能整轮刷新一起崩。
        """
        rewards = rr.get("rewards") or []
        count = int(rr.get("count") or len(rewards) or 1)
        detail = "天空之境 " + (", ".join(self._reward_text(rewards)) or "探索奖励")
        try:
            self._record_task_completion("sky_reward", count, detail, source=source)
        except Exception as e:  # noqa: BLE001
            print("[!] 天空之境奖励记账失败(%s): %s" % (source, str(e)[:160]))

    def _safe_tick(self, fn, *args, **kw):
        """跑一个"顺风车"子任务(港口/天空之境/福利/积分/联盟/领地)。

        这些子任务以前是裸调的: 任何一个抛异常, 后面所有子任务和
        `_update_task_stats` 都不会执行 —— 天空之境里一个 UnboundLocalError
        就能让"每日签到"不再入账、让福利自动领取整个停摆(2026-11-01 实测)。

        现在失败只记日志, 不许把整轮刷新带崩。
        """
        name = getattr(fn, "__name__", "tick")
        try:
            return fn(*args, **kw)
        except Exception as e:  # noqa: BLE001
            print("[!] %s 失败: %s" % (name, str(e)[:160]))
            return None

    def _sky_tick(self, client=None):
        """天空之境定时检查: 读状态 -> 完成未领就领 -> 空闲且开自动探索就探索。

        复用当前连接, 不额外占号。两步都是**真实写操作**:
          * get_reward —— 领取探索奖励(本来就该领, 风险低)
          * explore    —— 开始探索(按服务端规则消耗战力/部队, 风险高)
        所以默认都**关**, 由用户在页面上显式打开。自动探索尤其危险, 独立开关。
        """
        cli = client or self.daemon.client
        if cli is None:
            return
        # 功能未开启(或读不出)时不要每轮空转
        if self.sky_disabled and client is None:
            return
        auto_reward = bool(self.settings.get("skyAutoReward", False))
        auto_explore = bool(self.settings.get("skyAutoExplore", False))
        # 两个自动都没开就只读一次状态给页面看, 不做写操作
        try:
            st = cok_sky.read_sky(cli)
        except Exception as e:  # noqa: BLE001
            with self.lock:
                self.sky_state = {"error": str(e)[:120]}
            return
        if not st.get("ok"):
            # 读不到(功能未开启/命令族不对): 标记后不再每轮空转
            with self.lock:
                self.sky_state = {"error": st.get("error"),
                                  "errorCode": st.get("errorCode"),
                                  "disabled": True,
                                  "note": "天空之境读取失败(%s)"
                                          % (st.get("errorCode") or st.get("error") or "未知")}
                if client is None:
                    self.sky_disabled = True
            return
        fam = st.get("family")
        acted = []
        # ⚠ 必须先初始化: 下面两个变量只在"对应分支真的跑过"时才有值。
        #    以前没初始化, 于是"只开自动领奖不开自动探索"(探索默认关)时,
        #    领完奖走到 `if explore_result:` 直接 UnboundLocalError,
        #    **整轮刷新被带崩**(后面的福利/积分/联盟/领地自动全都跑不到)。
        #    2026-11-01 用真实服务端复现: 领奖成功 -> UnboundLocalError。
        reward_result = None
        explore_result = None
        reward_allowed, reward_reason = self._automation_allowed("skyAutoReward")
        explore_allowed, explore_reason = self._automation_allowed("skyAutoExplore")
        if auto_reward and not reward_allowed:
            self._automation_record("skyAutoReward", "skipped", "天空自动领奖未执行", reward_reason)
        if auto_explore and not explore_allowed:
            self._automation_record("skyAutoExplore", "skipped", "天空自动探索未执行", explore_reason)
        if auto_reward and reward_allowed and st.get("can_reward"):
            rr = None
            try:
                rr = cok_sky.get_reward(cli, family=fam)
            except Exception as e:  # noqa: BLE001
                note = "领取失败: %s" % str(e)[:80]
                acted.append(note)
                reward_result = ("failed", note, note)
            if rr is not None:
                if rr.get("ok"):
                    note = "自动领取探索奖励 %s" % (
                        ", ".join(self._reward_text(rr.get("rewards") or [])) or "已领取")
                    reward_result = ("success", note, "")
                    # 领奖成功**立刻记账**。记账单独 try, 不许它的异常改写
                    # "领奖成功"这个结论 —— 之前记账和领奖挤在同一个 try 里,
                    # 记账一旦抛错就会被当成"领取失败", 天空之境的奖励就悄悄
                    # 不进日/周/月统计(2026-11-01 实测踩到)。
                    self._record_sky_reward(rr, source="auto")
                else:
                    note = "领取失败(%s)" % (rr.get("errorCode") or rr.get("error") or "未知")
                    reward_result = ("failed", note, note)
                acted.append(note)
                try:
                    st = cok_sky.read_sky(cli, family=fam)
                except Exception:  # noqa: BLE001
                    pass
        # 只用客观事实"空闲"当闸门(state==0), 其余前提交给服务端裁定 ——
        # 反编译猜测的 can_explore 可能误伤已配置好的账号。
        min_power = max(0, int(self.settings.get("skyMinPower") or 0))
        enough_power = int(st.get("curPower") or 0) >= min_power
        # 探索固定一次: 天空之境纯靠定时检查, 空闲就开始探索一次(最省且安全),
        # 不再有"探索次数"这个设置。
        if auto_explore and explore_allowed and min_power and not enough_power:
            self._automation_record("skyAutoExplore", "skipped", "天空自动探索未执行",
                                    "当前战力低于保留阈值 %d" % min_power)
        elif auto_explore and explore_allowed and st.get("ok") and st.get("state") == cok_sky.STATE_IDLE:
            try:
                ex = cok_sky.explore(cli, num=1, family=fam)
                if ex.get("ok"):
                    note = "自动探索一次"
                    explore_result = ("success", note, "")
                    self._record_task_completion(
                        "sky_explore", 1, "天空之境探索", source="auto")
                else:
                    note = "探索失败(%s)" % (ex.get("errorCode") or ex.get("error") or "未知")
                    explore_result = ("failed", note, note)
                acted.append(note)
                st = cok_sky.read_sky(cli, family=fam)
            except Exception as e:  # noqa: BLE001
                note = "探索失败: %s" % str(e)[:80]
                acted.append(note)
                explore_result = ("failed", note, note)
        if acted:
            self.daemon.emit("sky_auto", {"note": "; ".join(acted)})
            if isinstance(st, dict):
                st["last_auto"] = "; ".join(acted)
            if reward_result:
                self._automation_record("skyAutoReward", *reward_result)
            if explore_result:
                self._automation_record("skyAutoExplore", *explore_result)
        elif auto_reward and reward_allowed:
            self._automation_record("skyAutoReward", "waiting", "暂无可领取的天空奖励")
        elif auto_explore and explore_allowed:
            self._automation_record("skyAutoExplore", "waiting", "天空探索暂不满足条件")
        with self.lock:
            self.sky_state = st if isinstance(st, dict) else {}

    # ---------------- 积分商城(ScoreMall, 积分任务奖励) ----------------

    def _score_tick(self, client=None):
        """积分商城: 读积分任务 -> (按设置)把可领的逐个领了。复用当前连接。"""
        cli = client or self.daemon.client
        if cli is None:
            return
        try:
            st = cok_scoremall.read_score_mall(cli)
        except Exception as e:  # noqa: BLE001
            with self.lock:
                self.score_state = {"ok": False, "error": str(e)[:160]}
            return
        acted = []
        allowed, reason = self._automation_allowed("scoreAutoClaim")
        if self.settings.get("scoreAutoClaim") and not allowed:
            self._automation_record("scoreAutoClaim", "skipped", "积分任务自动领取未执行", reason)
        if st.get("ok") and self.settings.get("scoreAutoClaim") and allowed and st.get("claimable"):
            r = cok_scoremall.claim_all(cli, state=st)
            acted = self._score_acted(r)
            try:
                st = cok_scoremall.read_score_mall(cli)
            except Exception:  # noqa: BLE001
                pass
            if acted:
                self.daemon.emit("score_auto", {"note": "; ".join(acted)})
                self._automation_record("scoreAutoClaim",
                                        "failed" if "失败" in "; ".join(acted) else "success",
                                        "; ".join(acted))
        elif self.settings.get("scoreAutoClaim") and allowed:
            self._automation_record("scoreAutoClaim", "waiting", "暂无可领取的积分任务奖励")
        if isinstance(st, dict):
            st["last_auto"] = "; ".join(acted) if acted else (self.score_state or {}).get("last_auto", "")
        with self.lock:
            self.score_state = st if isinstance(st, dict) else {}

    def _score_acted(self, r):
        """claim_all 结果 -> 动作说明列表。"""
        out = []
        for x in (r or {}).get("results") or []:
            if x.get("ok"):
                out.append("积分任务 %s: %s" % (
                    x.get("taskId"), ", ".join(self._reward_text(x.get("rewards") or [])) or "已领取"))
            else:
                out.append("积分任务 %s 领取失败(%s)" % (
                    x.get("taskId"), x.get("errorCode") or x.get("error") or "未知"))
        return out

    def _score_view(self):
        st = self.score_state or {}
        tasks = st.get("tasks") or []
        return {
            "ok": bool(st.get("ok")),
            "monthIntegral": st.get("monthIntegral"),
            "curStar": st.get("curStar"),
            "tasks": [dict(t, name=(t.get("name") or ("任务 " + t.get("taskId", ""))))
                      for t in tasks],
            "claimable": len(st.get("claimable") or []),
            "claimed": sum(1 for t in tasks if t.get("claimed")),
            "total": len(tasks),
            "has_taskArr": bool(st.get("has_taskArr")),
            "keys": st.get("keys") or [],
            "error": st.get("error"),
            "errorCode": st.get("errorCode"),
            "last_auto": st.get("last_auto") or "",
            "last_claim": st.get("last_claim"),
            "autoClaim": bool(self.settings.get("scoreAutoClaim", False)),
        }

    # ---------------- 联盟(科技/任务板/捐献/使命/商店) ----------------

    #: 联盟状态最少隔多久重读一次(秒)。联盟一次要读 8 条命令,
    #: 每轮轮询都读会拖慢刷新, 所以按这个间隔节流。
    ALLIANCE_MIN_INTERVAL = 60.0

    def _alliance_tick(self, client=None, force=False):
        """读一次联盟面板(只读), 结果缓存起来给页面用。

        复用当前连接, 不额外占号。**默认不做任何写操作** —— 捐献/接任务/领奖
        都必须由用户在页面上显式点(那是真副作用); 只有用户**显式打开**
        「联盟自动捐献」开关时, 才会走自动捐献(见 _alliance_auto_donate)。
        """
        cli = client or self.daemon.client
        if cli is None:
            return
        now = time.time()
        if not force and (now - self.alliance_at) < self.ALLIANCE_MIN_INTERVAL:
            return
        self.alliance_at = now
        self.phase = "联盟"
        try:
            st = cok_alliance.read_all(cli)
        except Exception as e:  # noqa: BLE001
            with self.lock:
                self.alliance_error = str(e)[:160]
            return
        with self.lock:
            self.alliance_state = st if isinstance(st, dict) else {}
            self.alliance_error = ""
        # 自动捐献是写操作, 只在开关打开时跑
        self._alliance_auto_donate(cli)
        # 联盟自动签到: 读到的 alliance_sign_in.signInReward_state == 0 就领
        self._alliance_auto_signin(cli)

    def _alliance_auto_signin(self, cli):
        """联盟自动签到: 没签就领(`alliance.signIn.reward`, 无参)。

        ⚠ 真副作用: 每天一次。已签则直接跳过, 不会重复领。
        """
        if not bool(self.settings.get("allianceSignIn", False)):
            return
        allowed, reason = self._automation_allowed("allianceSignIn")
        if not allowed:
            self._automation_record("allianceSignIn", "skipped",
                                    "联盟自动签到未执行", reason)
            return
        st = cok_alliance.read_sign_in(cli)
        if not st.get("ok"):
            self._automation_record("allianceSignIn", "failed",
                                    "联盟签到状态读取失败", str(st.get("error") or ""))
            return
        if st.get("signed"):
            self._automation_record("allianceSignIn", "waiting",
                                    "联盟签到今日已签(连续 %s 天)" % st.get("days"))
            return
        try:
            r = cok_alliance.claim_sign_in(cli)
        except Exception as e:  # noqa: BLE001
            self._automation_record("allianceSignIn", "failed",
                                    "联盟签到失败: %s" % str(e)[:80])
            return
        if r.get("ok"):
            self._automation_record("allianceSignIn", "success",
                                    "联盟签到成功, 领到 %s 项奖励" % r.get("count"))
            self.daemon.emit("alliance_signin",
                             {"note": "联盟签到成功, 领到 %s 项奖励" % r.get("count")})
        else:
            self._automation_record("allianceSignIn", "failed",
                                    "联盟签到失败(%s)" % (r.get("errorCode") or r.get("error")))

    def _assist_panel_tick(self, client=None, force=False):
        """刷新「一键完成」面板清单(只读)。"""
        now = time.time()
        if not force and (now - self.assist_panel_at) < 300:
            return
        cli = client or self.daemon.client
        if cli is None:
            return
        self.assist_panel_at = now
        try:
            st = cok_assist.summary(cli)
        except Exception:  # noqa: BLE001
            return
        items = st.get("items") or []
        if items:
            with self.lock:
                self.assist_panel = items

    def _assist_auto_tick(self, client=None, force=False):
        """领地辅助「一键完成」: **每服务器日自动跑一次**。

        等同游戏里「领地辅助 → 一键完成」, 由 cok_assist.run_all() 照客户端
        编排逐项执行。收取是无损幂等的, 但按用户设置每天只跑一次就够:
        用持久化的 `assistAutoLastDay`(服务器日期)判重, 重启当天也不会重跑。
        """
        if not bool(self.settings.get("assistAuto", False)):
            return
        today = self._task_periods(self.daemon.ctx().get("date"))["day"]
        if not force and self.settings.get("assistAutoLastDay") == today:
            return
        allowed, reason = self._automation_allowed("assistAuto")
        if not allowed:
            self._automation_record("assistAuto", "skipped",
                                    "一键完成未执行", reason)
            return
        cli = client or self.daemon.client
        if cli is None:
            return
        costly = bool(self.settings.get("assistAutoCostly", False))
        try:
            r = self._assist_onekey(costly=costly)
        except Exception as e:  # noqa: BLE001
            self._automation_record("assistAuto", "failed",
                                    "一键完成失败: %s" % str(e)[:80])
            return
        if not r.get("ok"):
            # 连不上/读不到时不写"今天已执行", 下一轮还会再试
            self._automation_record("assistAuto", "failed",
                                    "一键完成失败: %s" % str(r.get("error") or "未知")[:80])
            return
        # 真跑过一遍了: 记下今天已执行(持久化, 重启不重跑)
        with self.lock:
            self.assist_at = time.time()
            self.settings["assistAutoLastDay"] = today
            self._save_settings()
        steps = r.get("steps") or []
        done = [s for s in steps if s.get("结果") == "完成"]
        bad = [s for s in steps if s.get("结果") not in ("完成", "无可收取")]
        # 一键完成后，顺手领取每日任务活跃宝箱（不消耗道具，安全）。
        try:
            box_res = cok_daily_quest.claim_all_boxes(cli)
            if box_res.get("ok"):
                claimed = box_res.get("claimed") or []
                if claimed:
                    box_ids = ",".join(b.get("id", "") for b in claimed)
                    note = "每日一键完成 · 已执行 %d 项 · 已领活跃宝箱 [%s]" % (len(done), box_ids)
                else:
                    note = "每日一键完成 · 已执行 %d 项 · 活跃宝箱无可领" % len(done)
            else:
                note = "每日一键完成 · 已执行 %d 项 · 活跃宝箱: %s" % (
                    len(done), box_res.get("error") or "未领取")
        except Exception as e:  # noqa: BLE001
            note = "每日一键完成 · 已执行 %d 项 · 活跃宝箱: 异常 %s" % (len(done), str(e)[:80])
        if costly:
            note += "(含消耗项)"
        if bad:
            note += "; " + ", ".join("%s(%s)" % (s.get("项"), s.get("详情") or s.get("结果"))
                                     for s in bad[:3])
        self._automation_record("assistAuto", "failed" if bad and not done else "success",
                                note)
        if done:
            self.daemon.emit("assist_auto", {"note": note})

    def _alliance_auto_donate(self, cli):
        """联盟自动捐献: 随机挑一个可捐档位捐下去, 进度满就停。

        ⚠ **绝不**碰 `al.science.research`(花金币开启/重置研究)和
        `al.targetscience.set`(改捐献目标) —— 那两个会动金币/权限。
        """
        if not bool(self.settings.get("allianceDonate", False)):
            return
        allowed, reason = self._automation_allowed("allianceDonate")
        if not allowed:
            self._automation_record("allianceDonate", "skipped",
                                    "联盟自动捐献未执行", reason)
            return
        # ⚠ 已知在研科技已满就**整轮跳过**, 一个命令都不发 ——
        #    免得反复去戳服务端(而且万一服务端把满进度当"重置"处理就麻烦了)
        for s in ((self.alliance_state or {}).get("science") or {}).get("list") or []:
            if s.get("researching") and s.get("full"):
                self._automation_record(
                    "allianceDonate", "waiting",
                    "在研科技 %s 进度已满, 跳过(不会花金币重置)" % s.get("scienceId"))
                return
        tier_mode = str(self.settings.get("allianceDonateTier") or "random")
        max_iter = int(self.settings.get("allianceDonateMax") or 20)
        try:
            r = cok_alliance.auto_donate(cli, tier_mode=tier_mode,
                                         max_iter=max_iter)
        except Exception as e:  # noqa: BLE001
            self._automation_record("allianceDonate", "failed",
                                    "联盟自动捐献异常: %s" % str(e)[:80])
            return
        acted = r.get("acted") or []
        note = r.get("stop") or ""
        if acted:
            note = ("捐了 %d 次(%s); %s" % (
                len(acted),
                "、".join(a.get("tierName") or a.get("tier") for a in acted),
                note)).strip("; ")
        status = "success" if acted else "waiting"
        if not acted and r.get("stop") and "失败" in str(r.get("stop")):
            status = "failed"
        self._automation_record("allianceDonate", status, note or "暂无可捐献的档位")
        with self.lock:
            self.alliance_auto = {
                "at": time.time(),
                "acted": acted,
                "stop": r.get("stop") or "",
                "done": bool(r.get("done")),
                "capReached": bool(r.get("capReached")),
                "iterations": r.get("iterations") or 0,
                "scienceId": r.get("scienceId") or "",
                "tier": r.get("tier") or "",
                "progress": r.get("progress") or "",
            }
        if acted:
            self.daemon.emit("alliance_auto", {"note": note})

    def _alliance_view(self):
        """联盟面板给页面用的视图。"""
        st = self.alliance_state or {}
        if not st:
            return {"loaded": False, "error": self.alliance_error or "",
                    "summary": {}, "science": [], "tiers": [],
                    "task": {}, "mission": {}, "donateRank": [],
                    "res": {}, "shop": {}, "help": []}
        summ = cok_alliance.summary(st)
        sci = st.get("science") or {}
        task = st.get("task") or {}
        mission = st.get("mission") or {}
        shop = st.get("shop") or {}
        res = st.get("res") or {}
        return {
            "loaded": True,
            "error": self.alliance_error or "",
            "summary": summ,
            # 科技树: 只回正在研究的 + 进度最高的若干项, 全量 65 项太占版面
            "researching": summ.get("researchingScience"),
            "science": [s for s in (sci.get("list") or [])
                        if s.get("researching") or s.get("percent") > 0][:12],
            "scienceCount": sci.get("count") or 0,
            "tiers": summ.get("donateTiers") or [],
            "donateReady": summ.get("donateReady"),
            "donateReason": summ.get("donateReason"),
            "task": {
                "record": task.get("record") or {},
                "available": task.get("available") or [],
                "published": task.get("published") or [],
                "leftRequestCount": task.get("leftRequestCount") or 0,
                "acceptLeft": summ.get("taskAcceptLeft") or 0,
                "publishLeft": summ.get("taskPublishedLeft") or 0,
            },
            "mission": {
                "common": mission.get("common") or [],
                "random": mission.get("random") or [],
                "signIn": mission.get("signIn") or {},
            },
            "donateRank": (st.get("donateRank") or {}).get("list") or [],
            "res": res.get("res") or {},
            "resItem": res.get("item") or [],
            "shop": {"alliancePoint": shop.get("alliancePoint") or 0,
                     "goods": shop.get("goods") or []},
            "help": (st.get("help") or {}).get("helps") or [],
            # 自动捐献: 上次结果 + 当前设置(档位模式 / 单轮上限)
            "auto": dict(self.alliance_auto or {}),
            "autoEnabled": bool(self.settings.get("allianceDonate", False)),
            "autoTier": str(self.settings.get("allianceDonateTier") or "random"),
            "autoMax": int(self.settings.get("allianceDonateMax") or 20),
            # 联盟签到: 已签 / 连续天数 / 自动开关
            "signIn": (mission.get("signIn") or {}),
            "signInDone": int((mission.get("signIn") or {}).get("signInReward_state") or 0) == 1,
            "autoSignIn": bool(self.settings.get("allianceSignIn", False)),
            "assistAuto": bool(self.settings.get("assistAuto", False)),
        }

    # ---------------- 福利中心(每日好礼 / 龙之馈赠) ----------------

    def _welfare_tick(self, client=None):
        """福利中心: 读状态 -> (按设置)把能领的领了。

        复用当前连接, 不额外占号。领取是**真实写操作**(每天一次),
        所以只在服务端明确说"可领"时才发命令。
        """
        cli = client or self.daemon.client
        if cli is None:
            return
        auto = bool(self.settings.get("autoWelfare", False))
        try:
            st = cok_welfare.read_all(cli)
        except Exception as e:  # noqa: BLE001
            with self.lock:
                self.welfare_state = {"error": str(e)[:160]}
            return
        acted = []
        allowed, reason = self._automation_allowed("autoWelfare")
        if auto and not allowed:
            self._automation_record("autoWelfare", "skipped", "自动领取福利未执行", reason)
        if auto and allowed:
            acted = self._welfare_claim(cli, st)
            if acted:
                # 领完状态变了, 重读一次
                try:
                    st = cok_welfare.read_all(cli)
                except Exception:  # noqa: BLE001
                    pass
        if auto and allowed:
            self._automation_record("autoWelfare",
                                    "failed" if "失败" in "; ".join(acted) else "success" if acted else "waiting",
                                    "; ".join(acted) if acted else "暂无可领取的福利")
        st["last_auto"] = "; ".join(acted) if acted else ""
        with self.lock:
            self.welfare_state = st

    def _welfare_claim(self, cli, st, tag="welfare_auto"):
        """把当前能领的福利领了。返回动作说明列表(给日志/页面)。"""
        acted = []

        # 1) 每日好礼的**免费**奖励(充值奖励不碰, 要花钱)
        dg = st.get("daily_gift") or {}
        if dg.get("ok") and not dg.get("freeRewarded"):
            try:
                r = cok_welfare.claim_daily_gift(cli)
                if r.get("ok"):
                    self._record_task_completion(
                        "welfare_daily", 1,
                        "每日好礼 " + (", ".join(self._reward_text(r.get("rewards") or [])) or "奖励"),
                        source="auto" if tag == "welfare_auto" else "manual")
                    acted.append("自动领取每日好礼 %s" % (
                        ", ".join(self._reward_text(r.get("rewards") or [])) or "奖励"))
                else:
                    acted.append("每日好礼领取失败(%s)" % (r.get("errorCode") or "未知"))
            except Exception as e:  # noqa: BLE001
                acted.append("每日好礼领取失败: %s" % str(e)[:80])

        # 2) 龙之馈赠(黑龙 / 蓝龙)
        dragons = ((st.get("dragon_gift") or {}).get("dragons") or {})
        for eid, d in dragons.items():
            if d.get("claimable"):
                try:
                    r = cok_welfare.claim_dragon_gift(cli, eid, False)
                    if r.get("ok"):
                        self._record_task_completion(
                            "welfare_dragon", 1,
                            "龙之馈赠(%s) %s" % (eid, ", ".join(
                                self._reward_text(r.get("rewards") or [])) or "奖励"),
                            source="auto" if tag == "welfare_auto" else "manual")
                        acted.append("自动领取龙之馈赠(%s) %s" % (
                            eid, ", ".join(self._reward_text(r.get("rewards") or [])) or "奖励"))
                    else:
                        acted.append("龙之馈赠(%s)领取失败(%s)" % (eid, r.get("errorCode") or "未知"))
                except Exception as e:  # noqa: BLE001
                    acted.append("龙之馈赠(%s)领取失败: %s" % (eid, str(e)[:80]))
            if d.get("special_claimable"):
                try:
                    r = cok_welfare.claim_dragon_gift(cli, eid, True)
                    if r.get("ok"):
                        self._record_task_completion(
                            "welfare_dragon", 1,
                            "龙之馈赠尊享(%s) %s" % (eid, ", ".join(
                                self._reward_text(r.get("rewards") or [])) or "奖励"),
                            source="auto" if tag == "welfare_auto" else "manual")
                        acted.append("自动领取龙之馈赠尊享(%s) %s" % (
                            eid, ", ".join(self._reward_text(r.get("rewards") or [])) or "奖励"))
                except Exception as e:  # noqa: BLE001
                    acted.append("龙之馈赠尊享(%s)领取失败: %s" % (eid, str(e)[:80]))
        if acted:
            self.daemon.emit(tag, {"note": "; ".join(acted)})
        return acted

    def _reward_view(self, rewards):
        """奖励明细 -> 带中文名的列表(页面显示用)。"""
        out = []
        for g in rewards or []:
            iid = str(g.get("itemId") or "")
            out.append({
                "itemId": iid,
                "name": self._tr_item(iid) or ("道具 " + iid if iid else "奖励"),
                "num": g.get("num"),
            })
        return out

    def _welfare_view(self):
        """福利中心给页面用的视图: 两行 + 可领计数。"""
        st = self.welfare_state or {}
        dg = st.get("daily_gift") or {}
        dr = (st.get("dragon_gift") or {})
        dragons = dr.get("dragons") or {}
        today = dr.get("today") or []
        rows = []
        # 每日好礼
        rows.append({
            "key": "daily_gift",
            "name": "每日好礼",
            "cmd": "everydayexchange.reward",
            "state": ("已领" if dg.get("freeRewarded") else "可领") if dg.get("ok") else "读取失败",
            "claimable": bool(dg.get("ok") and not dg.get("freeRewarded")),
            "rewards": [],
            "note": ("免费奖励每天一次" if dg.get("ok") else (dg.get("error") or "")),
        })
        # 龙之馈赠: 黑龙(默认) + 蓝龙
        for eid, d in sorted(dragons.items()):
            today_cfg = None
            for t in today:
                if t.get("exchangeId") == eid:
                    today_cfg = t
                    break
            name = "龙之馈赠·黑龙" if eid == dr.get("blackId") else ("龙之馈赠·蓝龙" if eid == "764116"
                                                                   else "龙之馈赠·%s" % eid)
            if d.get("claimable"):
                dstate = "可领"
            elif d.get("claimed_today"):
                dstate = "今日已领"
            else:
                dstate = "不可领"
            rows.append({
                "key": "dragon_%s" % eid,
                "name": name,
                "cmd": "userpayreward.newaccept",
                "state": dstate,
                "claimable": bool(d.get("claimable")),
                "rewards": self._reward_view(today_cfg.get("rewards") or []),
                "note": ("已购买" if d.get("isBuy") else "未购买")
                        + (" · 尊享可领" if d.get("special_claimable") else ""),
                "exchangeId": eid,
            })
        return {
            "loaded": bool(st),
            "rows": rows,
            "claimable": cok_welfare.claimable_count(st),
            "last_auto": st.get("last_auto") or "",
            "error": self._welfare_error(st),
        }

    @staticmethod
    def _welfare_error(st):
        """两个功能**都**失败时才报整体错误(单个失败不影响另一个)。"""
        if not st:
            return ""
        if st.get("error"):
            return str(st.get("error"))
        items = [st.get("daily_gift") or {}, st.get("dragon_gift") or {}]
        if items and all((not i.get("ok")) for i in items):
            for i in items:
                if i.get("error") or i.get("errorCode"):
                    return str(i.get("error") or i.get("errorCode"))
            return "福利中心读取失败"
        return ""

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
        # 手动刷新 = 明确要连 -> 解除"主动断开"闸门
        self.disconnected = False
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

    def disconnect(self):
        """主动断开与游戏服的连接, 并停在离线态(不自动重连)。

        做三件事:
          1. 若在自动打怪(常驻连接), 先停掉它并还回账号锁;
          2. 关掉后台轮询/操作用的连接;
          3. 置位 disconnected 闸门 —— 轮询循环看到它就停在离线,
             直到用户点「重连」/「立即刷新」。
        这样账号被彻底让出来(手机 App 可以上线), 不占连接也不占账号锁。
        """
        notes = []
        # 1) 打怪常驻连接
        if self.hunter and self.hunter.state.get("running"):
            try:
                self._hunter_stop()
                notes.append("已停自动打怪")
            except Exception:  # noqa: BLE001
                pass
        # 2) 关后台连接
        with self.op_lock:
            try:
                if self.daemon.client:
                    self.daemon.client.close()
            except Exception:  # noqa: BLE001
                pass
            self.daemon.client = None
            with self.lock:
                self.disconnected = True
                self.connected = False
                self.app_yield = False
        self.daemon.emit("disconnected", {"note": "用户主动断开连接"})
        tail = ("(" + " · ".join(notes) + ")") if notes else ""
        return {"ok": True, "note": "已断开连接, 账号已让出" + tail}

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
                if self.disconnected:
                    # 用户主动断开: 确保连接已关, 停在离线态, 不自动重连
                    if self.daemon.client is not None:
                        with self.op_lock:
                            try:
                                if self.daemon.client:
                                    self.daemon.client.close()
                            except Exception:  # noqa: BLE001
                                pass
                            self.daemon.client = None
                    with self.lock:
                        self.connected = False
                    for _ in range(3):
                        if self._stop.is_set():
                            break
                        time.sleep(1.0)
                    continue
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
            if self.persistent and self.settings.get("autoShield"):
                # 常驻 + 自动开罩: 睡眠期间定时戳一下连接, 把"被攻击"的推送读出来。
                # 否则推送要等到下一轮轮询(默认 5 分钟)才被发现, 兵早被打完了。
                self._sleep_with_push_watch()
            else:
                for _ in range(int(max(1, self.args.interval) / 1.0)):
                    if self._stop.is_set():
                        break
                    time.sleep(1.0)

    def _sleep_with_push_watch(self):
        """睡眠期间定时"戳一下"连接, 及时收到"被攻击"推送。

        推送帧是在**等命令响应**时从 socket 读出来的, 不发命令就收不到 ——
        也就是说常驻连接下, 被攻击了也要等到**下一轮轮询**(默认 5 分钟)
        才会被发现, 兵早被打完了。这里每隔 N 秒发一条 `cmd.ping`
        (只读、便宜)把 socket 里的推送读出来, 立刻交给自动开罩处理。
        """
        step = max(5, int(getattr(self.args, "shield_watch_interval", 20) or 20))
        end = time.time() + int(max(1, self.args.interval))
        while not self._stop.is_set() and time.time() < end:
            time.sleep(min(step, max(0.2, end - time.time())))
            if self._stop.is_set():
                break
            # ⚠️ 自动打怪(网页自建循环)占着账号连接时, 这里**绝对不能**碰连接 ——
            #    戳一下/重连都会把打怪那条连接踢掉(同账号只允许一个连接),
            #    表现就是"点打怪后 30 秒报连接被服务端关闭"。
            if self._hunter_active():
                with self.lock:
                    self.connected = False
                return
            try:
                # 与其它对游戏服的操作互斥(页面上的手动操作也走这把锁)
                with self.op_lock:
                    cli = self.daemon.client
                    if cli is None:
                        continue
                    self.phase = "推送监听"
                    cli.call("cmd.ping")
                    allowed, reason = self._automation_allowed("autoShield")
                    if allowed:
                        self.daemon.autoshield(self.daemon.ctx())
                    # 心跳只负责接收 push；无事发生时不写执行历史，避免每 20 秒
                    # 的检查覆盖真正的自动处理结果。
                    with self.lock:
                        self.shield_watch_ticks += 1
            except Exception as e:  # noqa: BLE001
                # 心跳失败(断连等)不影响主循环, 下一轮轮询会重连
                # ⚠ 这里**必须**留个痕迹: 否则"心跳没生效"会变成静默失败
                # (上一轮就是踩了这个坑: 异常被吞, 页面看着一切正常)
                self.daemon.emit("shield_watch_error", {
                    "note": "推送监听失败: %s" % str(e)[:160],
                })
                # 连接可能已经半死/错位 -> 直接丢掉, 下一轮轮询会重连一条干净的
                # ⚠️ 但**自动打怪在跑时不能重连** —— 重连会把打怪那条连接踢掉
                if self._hunter_active():
                    return
                try:
                    with self.op_lock:
                        if self.daemon.client:
                            self.daemon.client.close()
                        self.daemon.client = None
                        # 立刻重连: 等下一轮轮询要 5 分钟, 期间收不到推送(自动开罩等于瞎了)。
                        # 重连失败(比如账号被 App 抢走)就留给下一轮轮询处理。
                        try:
                            self.daemon.connect()
                        except Exception as e:  # noqa: BLE001
                            self.daemon.emit("shield_watch_error", {
                                "note": "重连失败: %s" % str(e)[:120],
                            })
                except Exception:  # noqa: BLE001
                    pass

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
                "phase": self.phase,
                # 用户主动断开: 前端据此把顶灯显示成"已断开"而非"连接异常"
                "disconnected": self.disconnected,
                # ondemand 模式轮完就断开, connected 永远是 False ——
                # 顶栏灯要用"有没有拿到数据"来判断, 否则一直显示"空闲"
                "has_data": bool(self.last_poll and not self.last_error),
                "persistent": self.persistent,
                "app_yield": self.app_yield,
                "app_online": self._app_cached,
                "last_poll": self.last_poll,
                "last_ok_poll": self.last_ok_poll,
                "error": self.last_error,
                "server_date": self.daemon.ctx().get("date"),
                "gold": self.gold,
                "states": self._translate_states(self.states),
                "task_stats": self._task_stats_view(),
                "hunt": self.hunt,
                "hunter": self._hunter_state(),
                # 体力药水实例(纯本地读缓存, 不占号)
                "stamina_items": cok_stamina.status(self.account_key),
                # 编队预设(11 个, 对齐游戏) + 当前选中的
                "squad_presets": self._squad_preset_list(),
                "squad_preset": self.settings.get("squadPreset") or "",
                "monster_levels": cok_hunt.load_levels(),
                "queues": queues,
                "shield": {
                    "end_ms": getattr(self.daemon, "shield_end_ms", 0),
                    "autoshield": self.autoshield_enabled,
                    "slots": (self.shield_state or {}).get("slots") or [],
                    "specs": (self.shield_state or {}).get("specs") or [],
                    "persistent": self.persistent,
                    # 自动开罩的推送监听心跳(证明它确实在跑)
                    "watch_ticks": self.shield_watch_ticks,
                    "watch_interval": self.shield_watch_interval,
                },
                "autoSign": bool(self.settings.get("autoSign", False)),
                "autoPoll": bool(self.settings.get("autoPoll", True)),
                "welfare": self._welfare_view(),
                # 联盟(科技树/任务板/捐献面板/使命/商店)
                "alliance": self._alliance_view(),
                # 「一键完成」面板(13 项清单 + 状态)
                "assist": self._assist_view(),
                # 积分商城(积分任务奖励)
                "score": self._score_view(),
                "autoWelfare": bool(self.settings.get("autoWelfare", False)),
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
                    # 最近一次自动领取/分派，供原生操作页确认规则确实执行过。
                    "last_auto": (self.dock_state or {}).get("last_auto"),
                    "cargo": (self.dock_state or {}).get("cargo"),
                    # 码头宝箱现在能不能领(按钮高亮/计数用)
                    "cargo_claimable": cok_dock.cargo_claimable(
                        (self.dock_state or {}).get("cargo") or {}, self._server_now_ms()),
                    "autoReward": bool(self.settings.get("dockAutoReward", False)),
                    "autoSend": bool(self.settings.get("dockAutoSend", False)),
                },
                "sky": {
                    "ok": bool((self.sky_state or {}).get("ok")),
                    "state": (self.sky_state or {}).get("state"),
                    "state_text": (self.sky_state or {}).get("state_text"),
                    "family": (self.sky_state or {}).get("family"),
                    "new": bool((self.sky_state or {}).get("new")),
                    "endTime": (self.sky_state or {}).get("endTime"),
                    "exploreLv": (self.sky_state or {}).get("exploreLv"),
                    "exploreNum": (self.sky_state or {}).get("exploreNum"),
                    "allowedExploreCounts": (self.sky_state or {}).get("allowedExploreCounts")
                    or list(cok_sky.DEFAULT_ALLOWED_EXPLORE_COUNTS),
                    "maxExploreCount": (self.sky_state or {}).get("maxExploreCount"),
                    "can_reward": bool((self.sky_state or {}).get("can_reward")),
                    "can_explore": bool((self.sky_state or {}).get("can_explore")),
                    "explore_reason": (self.sky_state or {}).get("explore_reason"),
                    "has_general": bool((self.sky_state or {}).get("has_general")),
                    "has_reward": bool((self.sky_state or {}).get("has_reward")),
                    "curPower": (self.sky_state or {}).get("curPower"),
                    "needPower": (self.sky_state or {}).get("needPower"),
                    "remain": cok_sky.remain_seconds(self.sky_state or {}, self._server_now_ms()),
                    "error": (self.sky_state or {}).get("error"),
                    "disabled": bool((self.sky_state or {}).get("disabled")),
                    "errorCode": (self.sky_state or {}).get("errorCode"),
                    "note": (self.sky_state or {}).get("note"),
                    "last_auto": (self.sky_state or {}).get("last_auto"),
                    "autoReward": bool(self.settings.get("skyAutoReward", False)),
                    "autoExplore": bool(self.settings.get("skyAutoExplore", False)),
                },
                "map_index": self._map_index_summary(),
                "account_error": self.account_error,
                "account_source": self.account_source,
                "account_note": self.account_note,
                # ⚠️ 只有「别人」占着账号才算 busy —— 本进程自己在跑 daemon 时
                # flock 探测必然失败, 那是自指, 不是外部占用。
                "account_busy": self._account_busy(),
                "account_holder": cok_client.account_holder(self._lock_key()),
                "account_holder_self": self._account_holder_self(),
                # 多账号: 账号库列表 + 当前选中(给页面下拉框)
                "accounts": self._accounts_summary(),
                "items": self._owned_items(),
                "bag_source": self._bag_source(),
                "events": self.events[-120:],
                "automation": self._automation_snapshot(),
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
                    # 兵种名(107xxx 系列 121 条, 4KB) —— 游戏预设编成里可能出现
                    # 玩家没有的兵种, 前端要能显示它的名字, 否则只能显示 id
                    "army": self._army_names(),
                },
                "settings": dict(self.settings),
            }

    def _army_names(self):
        """兵种中文名(107xxx 系列)。缓存 —— 每次快照重算太浪费。"""
        if getattr(self, "_army_names_cache", None) is None:
            out = {}
            for k, v in (self.names.get("items") or {}).items():
                if str(k).startswith("107"):
                    out[str(k)] = v
            self._army_names_cache = out
        return self._army_names_cache

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

    def _server_now_ms(self):
        """服务端当前时间(ms)。优先用 cmd.ping 回的 serverNowTime, 退回本地时间。"""
        try:
            sn = int(getattr(self.daemon, "server_now", 0) or 0)
        except (TypeError, ValueError):
            sn = 0
        return sn or int(time.time() * 1000)

    def _reward_text(self, rewards):
        """奖励明细 -> "5,000钢 ×100" 这样的中文串。

        数量字段两种都有: 福利中心用 num, 码头宝箱用 count。
        """
        out = []
        for g in rewards or []:
            iid = str(g.get("itemId") or "")
            name = self._tr_item(iid) or ("道具 " + iid if iid else "奖励")
            n = g.get("num")
            if n is None:
                n = g.get("count")
            out.append("%s ×%s" % (name, n) if n is not None else name)
        return out

    def _dock_ships_view(self):
        """港口船表: 把载货道具 id 换成中文名, 附带可派遣/可领奖标记。

        第一格(type=0)是**码头宝箱**(港口活动奖励位), 不是船:
        显示"当前奖励物品 + 下次刷新时间", 绝不显示"空载"。
        """
        out = []
        cargo = (self.dock_state or {}).get("cargo") or {}
        cargo_name = self._tr_item(cargo.get("itemId") or "") or ""
        for s in ((self.dock_state or {}).get("ships") or []):
            v = dict(s)
            iid = str(s.get("itemId") or "")
            v["item_name"] = self._tr_item(iid) if iid else ""
            if s.get("kind") == "activity":
                v["item_name"] = cargo_name
                v["cargo_text"] = ("%s ×%s" % (cargo_name, cargo.get("count"))
                                   if cargo_name and cargo.get("count") is not None
                                   else (cargo_name or cok_dock.ACTIVITY_NAME))
                v["rewardTime"] = cargo.get("rewardTime")
                v["times"] = cargo.get("times")
                v["is_activity"] = True
            else:
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

    # ---------------- 领地辅助: 一键完成 ----------------
    @staticmethod
    def _assist_step(cli, cmd, params, title):
        """跑一条领地辅助命令, 返回 {"项","结果","详情"}。任何异常都吞掉, 不影响其它步骤。"""
        try:
            r = cli.call(cmd, params)
        except Exception as e:  # noqa: BLE001
            return {"项": title, "结果": "失败", "详情": str(e)[:120]}
        p = (r or {}).get("__params__") or {}
        if not isinstance(p, dict):
            p = {}
        err = p.get("errorCode") or p.get("errCode") or ""
        if err:
            return {"项": title, "结果": "服务端拒绝", "详情": str(err)}
        gain = []
        for k, label in (("food", "粮食"), ("wood", "木材"), ("iron", "铁矿"),
                         ("stone", "石头"), ("scienceStone", "科研石"),
                         ("silver", "银币")):
            v = p.get(k)
            try:
                iv = int(v) if v not in (None, "") else 0
            except (TypeError, ValueError):
                iv = 0
            if iv:
                gain.append("%s+%s" % (label, iv))
        rw = p.get("reward") or p.get("rewards") or ""
        detail = " ".join(gain)
        if not detail and rw:
            detail = str(rw)[:80]
        return {"项": title, "结果": "完成", "详情": detail, "_params": p}

    def _assist_onekey(self, costly=False):
        """游戏内「一键完成」—— 照客户端 CityAssistController:doTask 的逻辑逐项跑。

        对应游戏内「领地辅助(CityAssist)」面板里的批量操作
        (静态分析: apk-extract/assets/lua_static/game/city/CityAssistController.lua):

          1) 收取资源   → build.collect      {uuid: "u1;u2;..."}  秘银矿场/伐木场/铁矿场/农田
          2) 收取科研石 → sagatower.collect  {uuid: "u1;u2"}       科研工坊
          3) 文明要塞一键采集 → civilizationCastle.oneKeyCollect   (无参)

        实现要点(2026-10-29 实测):
          * 建筑类型来自 build.info 的 `building` 数组: `building` 字段是 "<类型id>;<等级>",
            新城市系统的建筑 `building` 为空, 类型藏在 `star_building_new`("<类型id*10+星级>,数量")。
          * **uuid 用建筑实例 uuid**(实测 `sagatower.collect` 传建筑 uuid 成功返回 refreshTime)。
          * build.collect 对未知 uuid 是宽容的(只回资源快照, 不报错), 所以多发不会误伤。
          * 收取是"把已积累的结算入库", 不消耗道具, 未产完的不会被提前结算。
        """
        cli = getattr(self.daemon, "client", None)
        if cli is None:
            return {"ok": False, "error": "尚未连接游戏服"}
        # 一键完成的实现搬到 cok_assist.py(面板 13 项的清单 + 无损档执行);
        # 这里只保留壳, 保持前端/安卓端已有的 {ok, steps, note, changed} 结构。
        try:
            r = cok_assist.run_all(cli, include_costly=bool(costly))
        except Exception as e:  # noqa: BLE001
            return {"ok": False, "error": "一键完成失败: %s" % str(e)[:140]}
        if not r.get("ok"):
            return {"ok": False, "error": r.get("error") or "一键完成失败"}
        with self.lock:
            self.assist_panel = r.get("panel") or []
        # 一键完成后，顺手领取每日任务活跃宝箱（不消耗道具，安全）。
        # 失败不影响一键完成本身，只写进 note 提示。
        try:
            box_res = cok_daily_quest.claim_all_boxes(cli)
            if box_res.get("ok"):
                claimed = box_res.get("claimed") or []
                if claimed:
                    box_ids = ",".join(b.get("id", "") for b in claimed)
                    r["note"] = (r.get("note") or "一键完成") + " · 已领活跃宝箱 [%s]" % box_ids
            else:
                r["note"] = (r.get("note") or "一键完成") + " · 活跃宝箱: %s" % (
                    box_res.get("error") or "未领取")
        except Exception as e:  # noqa: BLE001
            r["note"] = (r.get("note") or "一键完成") + " · 活跃宝箱: 异常 %s" % str(e)[:80]
        return {"ok": True, "steps": r.get("steps") or [],
                "panel": r.get("panel") or [],
                "note": r.get("note") or "一键完成",
                "changed": bool(r.get("changed"))}

    def _assist_view(self):
        """「一键完成」面板给页面用的视图(清单 + 各项状态)。

        只读缓存 —— 面板清单由轮询里的 `_assist_panel_tick` 刷新,
        免得每次生成快照都同步发命令拖慢页面。
        """
        items = list(self.assist_panel or [])
        return {"items": items,
                "auto": bool(self.settings.get("assistAuto", False)),
                "costly": bool(self.settings.get("assistAutoCostly", False)),
                # 自动执行改为每服务器日一次; lastDay 为已执行过的那个日期
                "schedule": "daily",
                "lastDay": self.settings.get("assistAutoLastDay") or ""}

    def _assist_onekey_old(self):
        """(旧实现, 保留参考; 新实现见 cok_assist.run_free)"""
        cli = getattr(self.daemon, "client", None)
        if cli is None:
            return {"ok": False, "error": "尚未连接游戏服"}
        try:
            p = cli.call("build.info").get("__params__") or {}
        except Exception as e:  # noqa: BLE001
            return {"ok": False, "error": "读建造队列失败: %s" % str(e)[:140]}
        before = dict(p.get("resource") or {})

        def _btype(b):
            """建筑类型 id: building 字段优先, 否则从 star_building_new 推(类型id*10+星级)。"""
            raw = str(b.get("building") or "").split(";")[0]
            if raw.isdigit():
                return int(raw)
            star = str(b.get("star_building_new") or "").split(",")[0]
            if star.isdigit():
                return (int(star) // 10) * 10
            return 0

        res_ids, sci_ids = [], []
        for b in (p.get("building") or []):
            if not isinstance(b, dict):
                continue
            uid = b.get("uuid")
            if not uid:
                continue
            t = _btype(b)
            if t in ASSIST_RES_TYPES:
                res_ids.append(uid)
            elif t == ASSIST_SCIENCE_TYPE:
                sci_ids.append(uid)

        steps = []
        if res_ids:
            st = self._assist_step(cli, "build.collect",
                                   {"uuid": ";".join(res_ids)},
                                   "收取资源(%d 座)" % len(res_ids))
            after = st.pop("_params", {}) or {}
            gain = []
            for k, label in (("food", "粮食"), ("wood", "木材"), ("iron", "铁矿"),
                             ("stone", "石头"), ("silver", "银币")):
                try:
                    d = int(after.get(k) or 0) - int(before.get(k) or 0)
                except (TypeError, ValueError):
                    d = 0
                if d > 0:
                    gain.append("%s+%s" % (label, d))
            if gain:
                st["详情"] = (" ".join(gain) + (" " + st["详情"] if st.get("详情") else ""))
            steps.append(st)
        else:
            steps.append({"项": "收取资源", "结果": "无可收取", "详情": ""})
        if sci_ids:
            steps.append(self._assist_step(cli, "sagatower.collect",
                                           {"uuid": ";".join(sci_ids)},
                                           "收取科研石(%d 座)" % len(sci_ids)))
        else:
            steps.append({"项": "收取科研石", "结果": "无可收取", "详情": ""})
        steps.append(self._assist_step(cli, "civilizationCastle.oneKeyCollect", {},
                                       "文明要塞一键采集"))
        ok = any(s.get("结果") == "完成" for s in steps)
        for s in steps:                      # 内部字段不要外泄
            s.pop("_params", None)
        return {"ok": True, "steps": steps, "note": "领地辅助一键完成",
                "changed": ok}

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
        # AutoHunter 独占这条 socket 时，不能从 HTTP 线程再发 read_data/status：
        # CokClient 不是多路复用协议，并发 call 会读走彼此的响应。此时页面需要的
        # 体力和进度都已由猎人每轮维护在 state 里，合并到最后一次完整快照即可。
        if self.daemon.client is None and self._hunter_active():
            with self.lock:
                state = self._hunter_state()
                cached = dict(self.hunt or {})
            for key in ("stamina", "stamina_max", "last_stamina_time", "status"):
                if state.get(key) is not None:
                    cached[key] = state[key]
            return cached
        try:
            return cok_hunt.snapshot(self.daemon.client)
        except Exception as e:  # noqa: BLE001
            return {"error": str(e)[:160]}

    # ---------------- 自动打怪(常驻连接) ----------------
    def _hunter_open_client(self):
        """建一条**新的**猎人专用连接(TCP + bin 握手 + 登录)。

        单独抽出来是为了重连时能原样重建 —— 建连顺序和 `login()` 里的
        序列号要求绑在一起, 不能随便少一步。
        """
        from cok_client import CokClient
        cl = CokClient(getattr(self.args, "game_host", None)
                       or cok_client.DEFAULT_HOST,
                       int(getattr(self.args, "game_port", None)
                           or cok_client.DEFAULT_PORT),
                       30.0, self.args.account)   # args.account 已是 dict
        cl.connect()
        cl.bin_handshake()
        cl.login()
        # 被动学习"服务端下发的道具实例 uuid"(玩家背包没有只读接口,
        # 只能从领奖/掉落/获得道具的响应里学到 uuid)。
        self._attach_item_learner(cl)
        return cl

    def _attach_item_learner(self, cl):
        """给一条连接挂上"道具实例 uuid 学习器"。"""
        uid = self.account_key or None
        if not uid or cl is None:
            return
        def _hook(cmd, decoded):
            try:
                params = decoded.get("__params__") if isinstance(decoded, dict) else None
                if not isinstance(params, dict):
                    return
                found = cok_stamina.merge_learned(uid, params)
                if found:
                    self.daemon.emit("stamina_items", cok_stamina.status(uid))
            except Exception:  # noqa: BLE001
                pass
        try:
            cl.on_response = _hook
        except Exception:  # noqa: BLE001
            pass

    def _hunter_reconnect(self, old_client):
        """猎人连接被服务端踢掉之后重建连接。

        绝大多数情况是**同账号双连接**: 游戏 App 还在线, 游戏服只留一条,
        服务端会把后进来的那条直接关掉(表现为"连接被服务端关闭(已收 0/3 字节)")。
        所以这里先再让一次路(停游戏 App), 等一下, 再重新连。
        返回新的 client(失败抛异常, 由调用方按失败处理)。
        """
        try:
            old_client.close()
        except Exception:  # noqa: BLE001
            pass
        try:
            self.stop_app()
        except Exception:  # noqa: BLE001
            pass
        time.sleep(1.5)
        cl = self._hunter_open_client()
        with self.lock:
            self.hunter_client = cl
        return cl

    def _auto_squad_spec(self, num, squads, mix=1):
        """按**当前库存**自动搭配编成: 每队可含**多个兵种**(混编),
        同一种兵可以拆多队、也可以一支队回来后连续出征。

        返回 plan: {"spec": [{"troops": [{army_id, num}]}], "num": 实际每队人数,
                    "squads": 实际队数, "total": 总兵力, "short": 是否被摊薄,
                    "note": 说明}

        * 兵种池 = 所有**有空闲兵**的兵种(含活动限定兵种 8 位 id)。
        * `mix` = 每队最多用几种兵:
          - 1 = 每队一种兵(旧行为);
          - 2+ = **一次出征带多个兵种**(混编)。服务端接受**同类**混编
            (标准+标准 ✅ / 活动+活动 ✅, 实测 2026-11-09),
            但**跨类混编会被拒**(活动 57580718 + 普通 107012 -> E000000),
            所以混编只在同类里做(见 `cok_hunt._army_class`)。
        * 数量 = `min(每队兵数, 该兵可用量)`; 库存不够分满 N 队时**按库存摊薄**
          每队人数(见 `cok_hunt.plan_squads`), 让"设 5 队"真的开得出 5 队。
        * 同一兵种库存多时可以**拆成多队**(协议实测同兵种多支部队可同时在外,
          且 2026-11-09 用行军 uuid 精确确认了可同时在外)。
        * 按战力从高到低挑(先派强的)。
        """
        try:
            army = cok_hunt.read_march(self.daemon.client)["army"]
        except Exception:  # noqa: BLE001
            army = []
        plan = cok_hunt.plan_squads(army, num, squads, mix)
        plan["spec"] = [{"troops": [{"army_id": str(t["army_id"]),
                                     "num": int(t["num"])}
                                    for t in (s.get("troops") or [])]}
                        for s in plan["slots"]]
        return plan

    def _hunter_start(self, body):
        """开启自动打怪循环。会用一条**常驻连接**(App 会被踢下线)。"""
        if self._hunter_active():
            # ⚠️ 已经有猎人在跑时**先把它停掉**(而不是直接报错)——
            #    旧猎人线程如果还活着, 会出现**两个猎人同时打怪**,
            #    体力几分钟能掉几百点(实测烧掉 574 点 = 57 只怪)。
            try:
                self.hunter.stop("被新的打怪请求替换")
            except Exception:  # noqa: BLE001
                pass
            for _ in range(20):          # 等它真正退出(最多 4 秒)
                if not self.hunter.state.get("running"):
                    break
                time.sleep(0.2)
            try:
                self._release_hunter_lock()
            except Exception:  # noqa: BLE001
                pass
            with self.lock:
                self.hunter = None
                self.hunter_client = None
        level = int(body.get("level") or 1)
        num = int(body.get("num") or 50)
        troop = body.get("troop") or None
        max_kills = int(body.get("maxKills") or 0)
        squads = int(body.get("squads") or 4)
        min_stamina = max(0, int(self.settings.get("huntMinStamina") or 0))
        known_stamina = (self.hunt or {}).get("stamina")
        if known_stamina is not None and int(known_stamina) < min_stamina:
            return {"ok": False, "error": "当前体力低于安全阈值 %d，暂不启动自动打怪" % min_stamina}
        # 每队兵种分配: [{troops: [{army_id, num}]}] 或旧的 [{army_id, num}]。
        # 不给就按可用兵种自动挑。
        squad_spec = body.get("squadSpec") or None
        if isinstance(squad_spec, list):
            spec = []
            for s in squad_spec:
                if not isinstance(s, dict):
                    continue
                # 新格式: 一支队多个兵种(混编)
                raw = s.get("troops")
                if isinstance(raw, list) and raw:
                    troops = []
                    for t in raw:
                        if not isinstance(t, dict):
                            continue
                        aid = str(t.get("army_id") or t.get("id") or "").strip()
                        if not aid:
                            continue
                        try:
                            n = int(t.get("num") or num)
                        except (TypeError, ValueError):
                            n = num
                        troops.append({"army_id": aid, "num": n})
                    if troops:
                        spec.append({"troops": troops})
                    continue
                # 旧格式: 一支队一个兵种
                aid = str(s.get("army_id") or s.get("id") or "").strip()
                if not aid:
                    continue
                try:
                    n = int(s.get("num") or num)
                except (TypeError, ValueError):
                    n = num
                spec.append({"troops": [{"army_id": aid, "num": n}]})
            squad_spec = spec or None
        # 每队最多用几种兵(1=每队一种兵; 2+=一次出征带多个兵种=混编)
        try:
            mix = max(1, min(4, int(body.get("mix")
                                     or self.settings.get("huntMix") or 1)))
        except (TypeError, ValueError):
            mix = 1
        # 体力不足时自动喝背包里的体力药水
        auto_stamina = bool(body.get("autoStamina")
                            if body.get("autoStamina") is not None
                            else self.settings.get("huntAutoStamina"))
        # 道具实例 uuid(不是模板 id): 优先用账号缓存, 再用账号配置里手填的
        stamina_items = dict(cok_stamina.load_items(self.account_key))
        acc_cfg = (accounts.get_account(self.account_key)
                   if self.account_key else None) or {}
        manual = acc_cfg.get("staminaItems")
        if isinstance(manual, dict):
            for k, v in manual.items():
                stamina_items.setdefault(str(k), v)
        # 没给编成 -> **按库存自动搭配**: 每队可含多个兵种(同类),
        # 数量 = min(每队兵数, 该兵当前可用量); 库存不够就按库存摊薄每队人数。
        plan = None
        if not squad_spec:
            plan = self._auto_squad_spec(num, squads, mix)
            squad_spec = plan.get("spec")
            if not squad_spec:
                return {"ok": False,
                        "error": "没有有空闲兵的兵种(全在治疗中?), 或库存不足"}
        # 先声明账号交接，再停止 App/关闭网页连接。此时猎人尚未置 running，
        # 但后台轮询和推送监听必须已开始让路。
        self._set_hunter_starting(True)
        # 先把 App 停掉: 同账号只允许一个连接, 不停会被服务端互踢
        stopped = self.stop_app()
        time.sleep(1.5)
        if not self._ensure_account():
            self._set_hunter_starting(False)
            return {"ok": False, "error": self.account_error}
        # 跨进程账号锁: 自动打怪是**长连接**, 必须整段持锁,
        # 否则别的进程(命令扫描/采集)一连就把这条常驻连接踢掉
        try:
            lock_ctx = cok_client.account_lock(timeout=3.0, purpose="auto-hunt",
                                               key=self._lock_key())
            lock_ctx.__enter__()
        except cok_client.AccountBusy as e:
            self._set_hunter_starting(False)
            return {"ok": False, "error": str(e)}
        self._hunter_lock = lock_ctx
        # ⚠️ **先把网页自己的连接断掉**再连猎人的那条。
        # 同账号只允许一个连接, 两个并存时服务端会随机踢掉一个 ->
        # 表现为"点打怪后十几分钟没有任何动作, 最后报连接被服务端关闭"。
        # 先断再连 = 任何时刻这个账号只有一条连接。
        try:
            with self.op_lock:
                if self.daemon.client:
                    try:
                        self.daemon.client.close()
                    except Exception:  # noqa: BLE001
                        pass
                self.daemon.client = None
                with self.lock:
                    self.connected = False
        except Exception:  # noqa: BLE001
            pass
        try:
            cl = self._hunter_open_client()
        except Exception as e:  # noqa: BLE001
            self._release_hunter_lock()
            self._set_hunter_starting(False)
            return {"ok": False, "error": "连接游戏服失败: %s" % str(e)[:160]}
        with self.lock:
            self.hunter_client = cl

        # 打怪击杀数记进"任务达成明细"(只记累计击杀数, 不记明细)。
        # 用 state["kills"] 的**增量**记账: 每次事件都比上一次多出来的才算新击杀,
        # 避免把累计值反复累加。
        with self.lock:
            self._hunt_kills_seen = 0

        def emit(kind, payload):
            if kind == "stopped":
                # 被服务端踢掉几乎等于"同账号双连接"。给一条能照做的提示,
                # 别只丢一句"连接被服务端关闭"(安卓端用户看不出该做什么)。
                note = str(payload.get("note") or "")
                if "连接" in note:
                    if self._app_stopped:
                        payload["note"] = (note + "｜已尝试停止游戏 App 仍被断开, "
                                           "请检查是否有别的设备登录了同一账号")
                    else:
                        payload["note"] = (note + "｜游戏 App 可能仍在线, "
                                           "请先完全退出游戏 App 再开始打怪")
            # 击杀增量记账(明细为空 = 只显示累计数)
            self._record_hunt_kills(payload.get("kills"))
            self.daemon.emit("hunt_" + kind, payload)
            # 打怪线程结束(正常停/致命断连)都要**把账号锁还回去**
            if kind in ("done", "stopped"):
                self._release_hunter_lock()
                self._set_hunter_starting(False)

        hunter = cok_hunt.AutoHunter(cl, level=level, num=num, troop_id=troop,
                                     max_kills=max_kills, on_event=emit,
                                     squads=squads, squad_spec=squad_spec,
                                     min_stamina=min_stamina,
                                     # 每队最多几种兵(1=每队一种兵; 2+=一次出征带多兵种)
                                     mix=mix,
                                     # 体力不足时自动喝背包里的体力药水
                                     auto_stamina=auto_stamina,
                                     stamina_items=stamina_items,
                                     # 账号 id: 体力不足时会拉一次背包(login.init)
                                     # 找药水的道具实例 uuid, 并落盘缓存
                                     uid=self.account_key,
                                     # 连接被服务端踢掉时自己重连(多半是同账号双连接)
                                     on_reconnect=self._hunter_reconnect,
                                     # 港口定时检查**搭打怪的顺风车**:
                                     # 用打怪这条连接, 不额外开连接(也不会互踢)
                                     on_tick=self._dock_tick)
        with self.lock:
            self.hunter = hunter
            self.hunter_thread = threading.Thread(target=hunter.run, daemon=True)
            self.hunter_thread.start()
        real_squads = len(squad_spec or [])
        # 每队人数 = 该队**所有兵种**人数之和(混编队是多种兵, 不能只看一个 "num")
        real_per = 0
        for s in (squad_spec or []):
            troops = (s or {}).get("troops") or []
            if troops:
                real_per = max(real_per, sum(int(t.get("num") or 0)
                                             for t in troops))
            else:
                real_per = max(real_per, int(s.get("num") or 0))
        note = "已开启自动打怪(等级 %d, %d 队 × 每队 %d 人)" % (
            level, real_squads, real_per)
        if mix > 1:
            note += "｜每队最多 %d 种兵(混编)" % mix
        if auto_stamina:
            _iid, _uuid = cok_stamina.pick_stamina(stamina_items)
            if _uuid:
                note += "｜体力不足自动喝药水(%s)" % _iid
            else:
                note += "｜体力不足自动喝药水(体力不够时会自动拉背包找药水)"
        if plan and plan.get("short"):
            note += "｜库存只够这么多, 每队人数已按库存摊薄(你填的 %d 是上限)" % num
        if not stopped:
            note += " [未能停止 App, 可能被互踢]"
        return {"ok": True, "note": note,
                "squads": real_squads, "perSquad": real_per,
                "plan": {"squads": real_squads, "num": real_per,
                         "short": bool(plan and plan.get("short")),
                         "note": (plan or {}).get("note") or ""}}

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

    def _hunter_stop(self, refresh=True):
        """停止自动打怪。

        ⚠️⚠️ **本方法必须能在"没有账号锁"的情况下调用**(2026-11-12 修):
        打怪线程正持有那把**跨进程账号锁**, 如果"停止"这个请求也先去抢锁,
        就变成**自己等自己** —— 永远拿不到, 页面报
        「账号正被占用(同账号只允许一个连接)」, **停止按钮完全失灵**。

        所以这里的顺序必须是:
            停线程 → 关猎人连接 → **先把锁还回去** → 再(可选)回读体力。
        回读体力(`_hunt_state`)要连游戏服, 所以**放在释放锁之后**,
        否则又会卡在同一把锁上。
        """
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
        self._release_hunter_lock()      # ← 先把跨进程账号锁还回去
        self._set_hunter_starting(False)
        if refresh:
            try:
                hunt = self._hunt_state()   # 锁已释放, 这里才连得上
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

    def _overview_summary(self):
        """给多账号总览用的紧凑摘要: 一屏看清每个号的关键态。

        只读内存里已有的状态, 不额外连网/占号 —— 总览是"看一眼",
        不应该触发任何游戏服操作。
        """
        now_ms = self._server_now_ms()
        with self.lock:
            shield_end = int(getattr(self.daemon, "shield_end_ms", 0) or 0)
            dock = dict(self.dock_state or {})
            welfare = dict(self.welfare_state or {})
            last_error = self.last_error
            last_ok = self.last_ok_poll
            disconnected = self.disconnected
            account_error = self.account_error
            app_yield = self.app_yield
        hunter = self._hunter_state()
        shield_left = max(0, shield_end - now_ms)
        dock_rewardable = len((dock.get("rewardable") or []))
        welfare_claimable = bool(welfare.get("daily_gift")
                                 and (welfare.get("daily_gift") or {}).get("ok")
                                 and not (welfare.get("daily_gift") or {}).get("freeRewarded"))
        # 健康: 近 10 分钟内有过成功轮询才算"新鲜"
        stale = bool(last_ok) and (time.time() - last_ok) > 600
        return {
            "shield_ms": shield_left,
            "has_shield": shield_left > 0,
            "dock_rewardable": dock_rewardable,
            "welfare_claimable": welfare_claimable,
            "hunting": bool(hunter.get("running")),
            "hunt_kills": int(hunter.get("kills") or 0),
            "error": account_error or (last_error if not disconnected else ""),
            "disconnected": bool(disconnected),
            "app_yield": bool(app_yield),
            "last_ok_poll": last_ok,
            "stale": stale,
        }

    def _hunt_action_raw(self, body):
        """打野怪写操作: 等级范围 / 部队编成 / 开 / 停。"""
        op = body.get("op")
        cl = self.daemon.client
        # 被动学习"服务端下发的道具实例 uuid"(网页这条连接也要挂)
        self._attach_item_learner(cl)
        if op == "stamina-status":
            # 体力药水实例的当前状态(有没有抓到 uuid / 是哪一瓶)
            return {"ok": True, "stamina": cok_stamina.status(self.account_key)}
        if op == "stamina-sync":
            # 拉一次背包(`login.init`), 直接拿到体力药水的**道具实例 uuid**
            # (含数量)。不消耗玩家任何奖励。
            # 拉不到再退一步: 领一份含药水的奖励, 借服务端下发道具实例。
            if cl is None:
                return {"ok": False, "error": "还没连上游戏服"}
            ok, info = cok_stamina.fetch_bag(cl, self.account_key)
            if ok and info.get("potions"):
                st = cok_stamina.status(self.account_key)
                names = ", ".join("%s x%s" % (k, v.get("count"))
                                  for k, v in sorted(info["potions"].items()))
                return {"ok": True, "note": "已同步体力药水: %s" % names,
                        "stamina": st}
            ok2, info2 = cok_stamina.claim_stamina_reward(cl, self.account_key)
            st = cok_stamina.status(self.account_key)
            if not ok2:
                err = (info.get("error") if not ok else "") or info2.get("error") or "同步失败"
                return {"ok": False, "error": err, "stamina": st}
            return {"ok": True, "note": info2.get("note") or "已同步",
                    "stamina": st}
        if op == "set-level":
            lo = int(body.get("low") or 1)
            hi = int(body.get("high") or lo)
            p = cok_hunt.save_level(cl, lo, hi)
            return {"ok": not p.get("errorCode"), "lv": p.get("lv") or "%d;%d" % (lo, hi)}
        if op == "set-format":
            # ⚠️ 游戏里存的是**编队槽位索引**, 不是编成串!
            #    客户端 `AutoQueueController:updateFormat()` ->
            #    `autoQueueInfo.format = atoi(formats[index])`,
            #    服务端**原样存储**(实测: 写 "1" 读回来还是 "1")。
            #    写编成串("107110,50|…")会把游戏面板的设置写坏 ——
            #    客户端读回后 atoi("107110,50|…") = 107110, 超过编队数(11)
            #    -> 直接被丢弃, 游戏里「自动打怪」的编队显示成空。
            fmt = str(body.get("format") or "").strip()
            if not fmt:
                return {"ok": False,
                        "error": "请给编队槽位索引(如 1 或 1;2;3), 不要写编成串"}
            if not re.fullmatch(r"\d+(;\d+)*", fmt):
                return {"ok": False,
                        "error": "只能写编队槽位索引(如 1 或 1;2;3), 不能写编成串 —— "
                                 "写编成串会把游戏「自动打怪」面板的设置写坏"}
            p = cok_hunt.save_format(cl, fmt)
            return {"ok": not p.get("errorCode"), "format": p.get("format") or fmt,
                    "note": "已把游戏「自动打怪」的编队设成槽位 %s" % fmt}
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
        if op == "autoqueue":
            # 读**游戏里**「自动打怪」面板当前用的编成(不是"部队"界面的预设编队)
            r = cok_hunt.read_autoqueue(cl)
            if isinstance(r, dict):
                # ⚠️ 多账号时一定要标明是**谁的**设置, 否则很容易串号
                # (用户在手机上给 A 号设的编队, 网页连着 B 号, 读出来自然是 B 的)
                r["account"] = self.account_label or self.account_key
                r["accountKey"] = self.account_key
                r["source"] = "游戏「自动打怪」面板当前用的编成"
                kind = r.get("kind")
                if kind == "index":
                    idxs = r.get("indices") or []
                    names = "、".join("编队%d" % i for i in idxs)
                    r["note"] = ("游戏里用的是**槽位索引**(%s) —— 这是游戏客户端的正常形式, "
                                 "意思就是「用游戏里的这几个编队」。"
                                 "但**编队槽位里的具体兵种服务端不下发**, 网页读不到, "
                                 "所以读不到「编队1 是哪几个兵」。" % names)
                elif kind == "army":
                    r["note"] = ("⚠️ 游戏里存的是**编成串**而不是槽位索引 —— "
                                 "这是被本工具的旧版写坏的格式(游戏客户端读回后会当成 "
                                 "107110 这种越界索引直接丢弃, 面板会显示空)。"
                                 "要恢复, 把它改回索引即可。")
                else:
                    r["note"] = ("该账号在游戏里没设过「自动打怪」的编成。"
                                 "游戏「部队」界面里的 11 个预设编队服务端不下发, 网页读不到; "
                                 "要在游戏里用编队1 打怪, 得先在「自动打怪」面板里选中编队1 并保存")
            return r
        if op == "autoqueue-store":
            # 把编成存进**当前账号**的编队桶(游戏里每个号的编成各不相同)
            idx = body.get("index")
            if idx in (None, ""):
                idx = self.settings.get("squadPreset")
            spec = body.get("spec") or []
            # fromGame: 这份编成是不是**从游戏里读来的**。
            # 网页自己按可用兵自动编排的不算 —— 不能顶着"读自游戏"的标签。
            from_game = body.get("fromGame")
            if from_game is None:
                from_game = True
            src = self.account_label or self.account_key
            if not from_game:
                src = ""
            ok, key = self._squad_preset_save(
                idx, spec, name=("编队%s" % idx),
                from_game=bool(from_game), from_game_account=src)
            return {"ok": bool(ok), "index": str(idx or ""), "account": key}
        if op == "game-hunt-start":
            # 用**游戏里的编队**打怪: 把选中的编队号写回游戏(槽位索引),
            # 再开游戏自己的自动打怪队列 —— 出征由游戏来做, 用的是玩家
            # 在游戏里设好的编队1/编队2..., 网页不参与兵种和数量。
            return self._game_hunt_start(body)
        if op == "game-hunt-stop":
            return self._game_hunt_stop()
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
        if op == "rally-state":
            # 巨型狮鹫(活动怪首领) + 集结状态: 4 档集结时长 / 地图上的 boss / 我的集结
            return self._rally_state(force=bool(body.get("force")))
        if op == "rally-start":
            # 向巨型狮鹫发起集结(真实消耗体力+兵)
            return self._rally_start(body)
        return {"ok": False, "error": "未知打野怪操作 %r" % op}

    # ---------------- 巨型狮鹫 + 集结 ----------------

    def _rally_reconnect(self, old_client):
        """扫描途中连接被服务端掐断时重建连接。

        ⚠️ 实测(2026-11-02): 连续 world.get 约 70 次后游戏服会**主动断开连接**
        ("连接被服务端关闭(已收 0/3 字节)")。扫描是长任务, 必须能自己接上,
        否则每次扫到一半就前功尽弃。
        """
        try:
            old_client.close()
        except Exception:  # noqa: BLE001
            pass
        try:
            self.daemon.connect()
        except Exception:  # noqa: BLE001
            raise
        cl = self.daemon.client
        if cl is None:
            raise RuntimeError("重连失败")
        with self.lock:
            self.connected = True
        return cl

    def _rally_state(self, force=False):
        """巨型狮鹫 + 集结的只读快照。

        读:
          * 4 档集结时长(服务端 dataConfig.world_rally, 每次都读, 不同区服不同)
          * 已知的巨型狮鹫目标(含血量; 轮转扫描 + 注册表慢慢补全)
          * 联盟里当前的集结(尤其是我自己那条 —— 同一目标只能有一支)
        """
        cl = self.daemon.client
        try:
            snap = cok_rally.snapshot(
                cl, force=force, slice_size=6,
                on_reconnect=self._rally_reconnect,
                game_uid=self.account_key)
        except Exception as e:  # noqa: BLE001
            return {"ok": False, "error": str(e)[:160]}
        snap["ok"] = True
        # 体力: 集结首领怪要 20 点, 不够就别让用户点
        try:
            st = cok_hunt.read_stamina(cl) or {}
            snap["stamina"] = st.get("stamina")
            snap["stamina_max"] = st.get("max")
        except Exception:  # noqa: BLE001
            pass
        snap["account"] = self.account_label or self.account_key
        return snap

    def _rally_start(self, body):
        """向巨型狮鹫发起**集结**(真实副作用: 扣体力 + 兵, 联盟里建集结)。

        协议: world.march {point, type:4(MethodRally), soldiers, marchKey,
        wtIndex:<时长档位 1..4>} —— 真服实测通过。
        """
        body = body or {}
        cl = self.daemon.client
        slot = int(body.get("slot") or 1)
        level = body.get("level")
        level = int(level) if level not in (None, "") else None
        index = body.get("index")
        index = int(index) if index not in (None, "") else None
        if index is None:
            # 自动挑: 排除已经有集结的目标(同一目标只能一支, 会回 115212)
            try:
                busy = cok_rally.busy_targets(cl, game_uid=self.account_key)
            except Exception:  # noqa: BLE001
                busy = set()
            tile = cok_rally.pick_boss_tile(cl, level=level, exclude=busy)
            if not tile:
                return {"ok": False,
                        "error": "地图上没找到巨型狮鹫(可能已刷新掉, 或这个等级没刷)"}
        else:
            tile = {"index": index}
        army = cok_hunt.list_army(cl)
        std = cok_hunt.standard_army(army)
        if not std:
            return {"ok": False, "error": "没有可用的标准兵种"}
        # 兵数: 页面给的, 库存不够就按库存
        try:
            want = int(body.get("num") or 0)
        except (TypeError, ValueError):
            want = 0
        a = std[0]
        num = min(want, a["free"]) if want > 0 else min(1000, a["free"])
        if num <= 0:
            return {"ok": False, "error": "没有空闲兵"}
        try:
            r = cok_rally.rally_march(
                cl, tile["index"], a["id"], a.get("speed"), a.get("load"), num,
                slot=slot, monster_id=tile.get("monsterId") or "")
        except Exception as e:  # noqa: BLE001
            return {"ok": False, "error": str(e)[:160]}
        r["index"] = tile["index"]
        r["level"] = tile.get("level")
        r["army_id"] = a["id"]
        r["num"] = num
        if r.get("ok"):
            mins = ""
            try:
                for s in cok_rally.read_rally_slots(cl):
                    if int(s.get("slot")) == slot:
                        mins = " / 集结 %s 分钟" % s.get("minutes")
                        break
            except Exception:  # noqa: BLE001
                pass
            r["note"] = ("已发起集结(档位 %d%s): 派 %d 个 %s 去打巨型狮鹫"
                         % (slot, mins, num,
                            cok_hunt.army_name(a["id"]) or a["id"]))
        self.daemon.emit("hunt_rally", r)
        return r

    def _game_hunt_start(self, body):
        """用**游戏里的编队**开打: 写回编队索引 + 开游戏自己的自动打怪。

        出征由游戏做(用玩家在游戏里设好的编队), 网页只管开关和监控。
        开游戏队列需要「自动打怪周卡」; 没有周卡就**自动降级**为网页自己
        按可用兵打(用户不用在页面上指定兵种/数量)。
        """
        body = body or {}
        idx = str(body.get("index") or self.settings.get("squadPreset") or "1")
        cl = self.daemon.client
        try:
            self._ensure_client()
            cl = self.daemon.client
        except Exception as e:  # noqa: BLE001
            return {"ok": False, "error": "连不上游戏服: %s" % str(e)[:140]}
        # 1) 把编队号写回游戏(槽位索引, 客户端要的就是这个)
        try:
            pf = cok_hunt.save_format(cl, idx)
        except Exception as e:  # noqa: BLE001
            return {"ok": False, "error": "写回编队失败: %s" % str(e)[:140]}
        if pf.get("errorCode"):
            return {"ok": False, "error": "写回编队失败: %s" % pf.get("errorCode")}
        # 2) 开游戏自己的自动打怪
        try:
            r = cok_hunt.set_status(cl, True)
        except Exception as e:  # noqa: BLE001
            return {"ok": False, "error": "开启失败: %s" % str(e)[:140]}
        if r.get("errorCode"):
            # 没有周卡 -> 降级: 网页自己打(按可用兵自动编排)
            return self._fallback_web_hunt(body, idx, r.get("errorCode"))
        return {"ok": True, "index": idx, "mode": "game",
                "note": "已开启游戏里的自动打怪, 用 编队%s" % idx}

    def _fallback_web_hunt(self, body, idx, code):
        """没有「自动打怪周卡」时的降级: 网页自己出征(按可用兵自动编排)。

        页面**不暴露**兵种/数量的输入 —— 兵种由网页按可用量自动挑,
        数量 = min(每兵种派出上限, 该兵可用量)。
        """
        per = int(body.get("num") or self.settings.get("perType") or 5000)
        squads = max(1, min(8, int(body.get("squads") or self.settings.get("squads") or 4)))
        # 每队最多几种兵(1=每队一种兵; 2+=一次出征带多个兵种=混编)
        try:
            mix = max(1, min(4, int(body.get("mix")
                                     or self.settings.get("huntMix") or 1)))
        except (TypeError, ValueError):
            mix = 1
        try:
            cl = self.daemon.client
            army = cok_hunt.read_march(cl)["army"]
        except Exception:  # noqa: BLE001
            army = []
        # 兵种池: 所有有空闲兵的兵种(含活动限定兵种, 单兵种出征实测可行),
        # 同一种兵可以拆成多队 —— 按库存切, 队数上限 = 用户设的并行队伍数。
        # mix>=2 时每队可由**多个同类兵种**混编(标准+标准 ✅ / 活动+活动 ✅,
        # 跨类会被服务端拒, 见 cok_hunt._army_class)。
        plan = cok_hunt.plan_squads(army, per, squads, mix)
        spec = [{"troops": [{"army_id": str(t["army_id"]), "num": int(t["num"])}
                           for t in (s.get("troops") or [])]}
                for s in plan["slots"]]
        spec = [s for s in spec if s.get("troops")]
        if not spec:
            return {"ok": False,
                    "error": "没有可用兵种(全在治疗中?), 也开不了游戏队列(%s)" % code}
        level = int(body.get("level") or self.settings.get("lvLow") or 1)
        r = self._hunter_start({"level": level,
                                "num": per,
                                "maxKills": int(body.get("maxKills") or 0),
                                "squads": squads,
                                "mix": mix,
                                "squadSpec": spec})
        if r.get("ok"):
            r["mode"] = "web"
            r["fallback"] = True
            r["note"] = ("没有「自动打怪周卡」(%s), 已改为网页自己打(按可用兵自动编排 %d 队)"
                         % (code, len(spec)))
            if plan.get("short"):
                r["note"] += "｜库存只够这么多, 每队人数已按库存摊薄(你填的 %d 是上限)" % per
        return r

    def _game_hunt_stop(self):
        """停: 关掉游戏里的自动打怪; 网页自建循环在跑的话也一起停。"""
        out = {}
        try:
            self._ensure_client()
            r = cok_hunt.set_status(self.daemon.client, False)
            out["game"] = {"ok": not r.get("errorCode"),
                           "error": r.get("errorCode") or ""}
        except Exception as e:  # noqa: BLE001
            out["game"] = {"ok": False, "error": str(e)[:120]}
        # 网页自建循环(降级模式)也要停
        try:
            if self.hunter and self.hunter.state.get("running"):
                out["web"] = self._hunter_stop()
        except Exception as e:  # noqa: BLE001
            out["web"] = {"ok": False, "error": str(e)[:120]}
        out["ok"] = True
        out["note"] = "已停止"
        return out

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

    # ---------------- 编队预设(对齐游戏的 11 个预设编队) ----------------
    # 客户端 CommonLib/commonBaseFunc.lua GgetFormationCount():
    # 基础 5 个 + SVIP/特效加成, 上限 12; 本工具按 11 个槽位做。
    SQUAD_PRESET_COUNT = 11

    def _squad_presets(self, account_key=None):
        """编队预设(名字 + 编成)。**按账号分桶**存。

        为什么分桶: 游戏里的编成是**每个账号各自**的(服务端按账号存编成),
        A 号读来的编成不能给 B 号用 —— 否则多账号下"读游戏设置"读到的
        和当前号对不上, 正是"数据不对"的另一个来源。

        取值顺序: 当前账号的桶 -> 全局 squadPresets(老数据/未分桶时的回退)。
        """
        key = account_key if account_key is not None else getattr(self, "account_key", "")
        acc = self._squad_preset_store_all()
        if acc:
            # 已经有分桶数据 -> **只**按账号取, 绝不能回退全局
            # (回退会让 A 号的编成出现在 B 号名下, 正是"数据不对"的来源)
            return acc.get(str(key)) or {}
        # 还没有任何分桶(第一次用) -> 回退旧的全局设置
        g = self.settings.get("squadPresets")
        if isinstance(g, str):
            try:
                g = json.loads(g)
            except Exception:  # noqa: BLE001
                g = {}
        raw = g if isinstance(g, dict) else {}
        return raw

    def _squad_preset_store_all(self):
        """整个 squadPresetsAcc 映射(账号id -> 该账号的编队桶)。"""
        acc = self.settings.get("squadPresetsAcc")
        if isinstance(acc, str):
            try:
                acc = json.loads(acc)
            except Exception:  # noqa: BLE001
                acc = {}
        return acc if isinstance(acc, dict) else {}

    def _squad_preset_store(self, account_key=None):
        """当前账号的编队桶(可写)。"""
        key = account_key if account_key is not None else getattr(self, "account_key", "")
        if not key:
            return None
        acc = self._squad_preset_store_all()
        return acc.setdefault(str(key), {})
    def _squad_preset_save(self, idx, spec, name=None, from_game=False,
                           from_game_account=""):
        """把一份编成存进**当前账号**的编队桶。返回 (是否成功, 账号id)。"""
        key = getattr(self, "account_key", "") or ""
        if not key:
            return False, ""
        try:
            i = int(idx)
        except (TypeError, ValueError):
            return False, key
        acc = self._squad_preset_store_all()
        bucket = acc.setdefault(str(key), {})
        bucket[str(i)] = {
            "name": name or ("编队%d" % i),
            "spec": spec,
            "fromGame": bool(from_game),
            "fromGameAccount": from_game_account or "",
        }
        self.settings["squadPresetsAcc"] = json.dumps(acc, ensure_ascii=False)
        self._save_settings()
        return True, key

    def _squad_preset(self, idx):
        """取某个编队预设: {index, name, spec:[{army_id,num}]}"""
        try:
            i = int(idx)
        except (TypeError, ValueError):
            return None
        raw = self._squad_presets().get(str(i))
        if not isinstance(raw, dict):
            return None
        spec = []
        for s in (raw.get("spec") or []):
            if not isinstance(s, dict):
                continue
            aid = str(s.get("army_id") or "").strip()
            if not aid:
                continue
            try:
                n = int(s.get("num") or 0)
            except (TypeError, ValueError):
                n = 0
            if n > 0:
                spec.append({"army_id": aid, "num": n})
        return {"index": i, "name": raw.get("name") or ("编队%d" % i),
                "spec": spec,
                # fromGame: 这份编成是从游戏「自动打怪」面板读来的(而不是手填的)
                "fromGame": bool(raw.get("fromGame")),
                "fromGameAccount": raw.get("fromGameAccount") or ""}

    def _squad_preset_list(self):
        """给页面的编队下拉用。"""
        out = []
        for i in range(1, self.SQUAD_PRESET_COUNT + 1):
            p = self._squad_preset(i) or {}
            out.append({
                "index": i,
                "name": p.get("name") or ("编队%d" % i),
                "spec": p.get("spec") or [],
                "empty": not p.get("spec"),
                # 来源标记: 读自游戏的编成要能跟手填的区分开
                "fromGame": bool(p.get("fromGame")),
                "fromGameAccount": p.get("fromGameAccount") or "",
            })
        return out

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
        if key == "automationMode":
            val = str(val or "execute")
            if val not in ("execute", "notify"):
                return {"ok": False, "error": "自动化模式仅支持 execute 或 notify"}
        if key == "automationAlertLevel":
            val = str(val or "failures")
            if val not in ("all", "failures", "off"):
                return {"ok": False, "error": "提醒级别仅支持 all、failures 或 off"}
        if key in ("automationMaxFailures", "automationBackoffMinutes"):
            try:
                val = max(1, min(120, int(val)))
            except (TypeError, ValueError):
                return {"ok": False, "error": "该策略需要有效的数字"}
        if key in ("huntMinStamina", "skyMinPower", "dockMinResourceReserve"):
            try:
                val = max(0, int(val))
            except (TypeError, ValueError):
                return {"ok": False, "error": "该策略需要有效的数字"}
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
        if act == "automation-recheck":
            # 重新检查只解除某规则的失败退避。下一轮巡检仍会经由全部
            # 安全策略决定是否发起游戏写操作，不能把“重试”变成隐式消耗。
            key = str((body or {}).get("key") or "")
            labels = dict(self.AUTOMATION_RULES)
            if key not in labels:
                return {"ok": False, "error": "未知自动化规则"}
            # 此处只清除本地失败计数和退避，绝不立即执行规则。真正执行仍须
            # 等下一次巡检并经过全部服务端安全策略。
            self._automation_rule(key)["failures"] = 0
            self._automation_record(
                key, "waiting", "已请求重新检查",
                "将在下一次巡检按安全策略重新判断", source="manual", force=True)
            return {"ok": True, "key": key,
                    "note": "已解除失败退避，将在下一次巡检重新检查"}
        # 主动断开: 本地动作(只关连接 / 置离线闸门), **绝不能**走 _action_locked,
        # 否则里面的 _ensure_client 会立刻把连接又建回来。
        if act == "disconnect":
            return self.disconnect()
        # 多账号管理: 也都是本地动作(只读写账号库文件 / 清内存态), 不连游戏服。
        if act == "account-switch":
            return self._account_switch(body)
        if act == "account-add-device":
            return self._account_add_device(body)
        if act == "account-remove":
            return self._account_remove(body)
        if act == "account-relabel":
            return self._account_relabel(body)
        # 渠道账号密码登录(果盘): 纯本地动作, 只对渠道服务器发 HTTP, 不连游戏服。
        if act == "channel-login":
            return self._channel_login(body)
        # 渠道登录第二步: 把用户勾选的小号加入账号库
        if act == "channel-add":
            return self._channel_add(body)
        if act not in GAME_SERVER_ACTIONS:
            # 先判未知操作, 别让"设备没连上"把真正的问题盖住
            return {"ok": False, "error": "未知操作 %r" % act}
        if act == "reconnect" and self.daemon.client is not None:
            # 首轮同步持有 op_lock 时，连接已经完成、只是可选状态仍在读取。
            # 不能让用户的“重新连接”排队等整轮同步，否则移动端会误报超时。
            self.disconnected = False
            with self.lock:
                self.connected = True
            return {"ok": True, "note": "已连接，正在同步游戏状态"}
        # 操作锁: 串行化对游戏服的写操作; 状态锁只用来改内存字段。
        # 两者分开, 页面在操作进行中照样能读 /api/state。
        with self.op_lock:
            try:
                # 离线预览(假 daemon)不连游戏服, 不该抢真账号的锁
                if getattr(self, "offline_preview", False):
                    result = self._action_locked(act, body)
                    self._record_manual_action(act, result)
                    return result
                # 先把账号确定下来(多账号: 这步才知道该锁哪把账号锁)。
                # _action_locked 里还会再确保连接, 这里只为拿到 account_key。
                self._ensure_account()
                lk = self._lock_key()
                # ⚠️⚠️ **「停止打怪」必须先于账号锁执行**(2026-11-12 修):
                # 打怪线程正持有那把跨进程账号锁, 而"停止"请求如果也去抢锁,
                # 就是**自己等自己** —— 永远拿不到, 页面报
                # 「账号正被占用(同账号只允许一个连接)」, 停止按钮完全失灵。
                # 这里先把猎人停掉(它自己会把锁还回去), 再走正常流程。
                if act == "hunt" and str(body.get("op") or "") == "auto-stop":
                    result = self._hunter_stop(refresh=False)
                    self._record_manual_action(act, result)
                    # 猎人锁**已经还回去了**, 现在可以正常拿锁 ->
                    # 把网页的常驻连接接回来, 并回读一次体力/设置
                    # (失败不影响"已停止"这个结果本身)。
                    try:
                        with cok_client.account_lock(timeout=2.0, purpose="web-action",
                                                     key=lk):
                            self._ensure_client()
                            hunt = self._hunt_state()
                            if hunt and not hunt.get("error"):
                                with self.lock:
                                    self.hunt = hunt
                    except Exception:
                        pass
                    return result
                # 跨进程账号锁: 别的进程(命令扫描/采集)正在用这个账号就跳过
                with cok_client.account_lock(timeout=2.0, purpose="web-action",
                                             key=lk):
                    result = self._action_locked(act, body)
                    self._record_manual_action(act, result)
                    return result
            except cok_client.AccountBusy as e:
                holder = cok_client.account_holder(self._lock_key())
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
        if act == "assist-onekey":
            # costly=True = 和游戏里点按钮一样, 连要烧金币道具的项一起跑
            return self._assist_onekey(costly=bool(body.get("costly")))
        if act == "reconnect":
            # 重连 = 明确要连 -> 解除"主动断开"闸门, 否则循环会立刻又把它关掉
            self.disconnected = False
            # 必须经由当前引擎的账号解析路径连接。渠道账号入库后不能绕开
            # _ensure_account，否则会错误回退到设备账号或启动时的默认账号。
            self._ensure_account()
            self._connect_game_server()
            with self.lock:
                self.connected = True
            return {"ok": True, "note": "已重连"}
        if act == "autoshield":
            with self.lock:
                self.autoshield_enabled = bool(body.get("enabled"))
            return {"ok": True, "enabled": self.autoshield_enabled}
        if act == "shield":
            if body.get("op") == "test-trigger":
                # 调试: 伪造一条"被攻击"推送, 走一遍自动开罩的完整链路
                # (推送 → 判定 → onekeybuff.use → 复核 → 事件)。
                # 不用真被打就能验证; 罩不在的时候**会真的消耗一个保护罩道具**。
                cli = self.daemon.client
                if cli is None:
                    return {"ok": False, "error": "还没有连接游戏服"}
                cli.pushes.append({"__cmd__": "push.world.injured", "__params__": {}})
                self.daemon.autoshield(self.daemon.ctx())
                return {"ok": True, "shield_end_ms": self.daemon.shield_end_ms,
                        "note": "已注入 push.world.injured 并跑完自动开罩逻辑"}
            slot = int(body.get("slot") or 1)
            cover = int(body.get("coverOld", 1))
            spec = str(body.get("spec") or "").strip()
            # 自动开罩沿用**你手动开罩用的槽位**
            # (否则自动路径永远用 CLI 默认的 1 号槽, 你在页面换槽位它不知道)
            try:
                self.daemon.args.shield_slot = slot
            except Exception:  # noqa: BLE001
                pass
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
                # 码头宝箱: 数据在 init 推送里, 一起读出来(否则第一格还是"空载")
                try:
                    st["cargo"] = cok_dock.read_cargo(self.daemon.client)
                except Exception:  # noqa: BLE001
                    st["cargo"] = {"ok": False}
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
                if r.get("ok"):
                    self._record_task_completion(
                        "dock_reward", len(pending),
                        "港口船只奖励 " + (", ".join(self._reward_text(r.get("rewards") or [])) or "奖励"))
                # 码头宝箱(第一格)也要领 —— 它是"可领取的奖励"里最容易漏掉的一项
                cargo_res = None
                cargo_note = ""
                try:
                    cg = cok_dock.read_cargo(self.daemon.client)
                    if cok_dock.cargo_claimable(cg, self._server_now_ms()):
                        cargo_res = cok_dock.claim_cargo(self.daemon.client)
                        if cargo_res.get("ok"):
                            for g in (cargo_res.get("rewards") or []):
                                iid = str(g.get("itemId") or "")
                                rewards.append({
                                    "itemId": iid,
                                    "name": self._tr_item(iid) or ("道具 " + iid),
                                    "addNum": g.get("count"),
                                    "uuid": g.get("uuid"),
                                    "from": "码头宝箱",
                                })
                            cargo_note = "码头宝箱 " + (", ".join(
                                self._reward_text(cargo_res.get("rewards") or [])) or "已领取")
                            self._record_task_completion("dock_cargo_reward", 1, cargo_note)
                            self.daemon.emit("dock_cargo_reward", cargo_res)
                        else:
                            cargo_note = ("码头宝箱还没到时间"
                                          if cargo_res.get("errorCode") == cok_dock.CARGO_NOT_READY
                                          else "码头宝箱领取失败(%s)" % (
                                              cargo_res.get("errorCode") or cargo_res.get("error") or "未知"))
                    else:
                        cargo_note = "码头宝箱还在倒计时"
                except Exception as e:  # noqa: BLE001
                    cargo_note = "码头宝箱领取失败: %s" % str(e)[:80]
                try:
                    st["cargo"] = cok_dock.read_cargo(self.daemon.client)
                except Exception:  # noqa: BLE001
                    pass
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
                    "cargo": cargo_note,
                }
                self._set_dock_state(st)
                return {
                    "ok": r.get("ok") or bool(cargo_res and cargo_res.get("ok")),
                    "errorCode": r.get("errorCode"),
                    "errorText": self._err_text(r.get("errorCode")),
                    "error": r.get("error"),
                    "family": r.get("family") or st.get("family"),
                    "count": r.get("count"),
                    "rewards": rewards,
                    "pending": len(pending),
                    "unclaimed": unclaimed,
                    "cargo": cargo_note,
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
        if act == "sky":
            # 天空之境(TheHeavens): 一键探索 / 一键领取
            sub = body.get("op") or "read"
            fam = (self.sky_state or {}).get("family")
            if sub == "read":
                st = cok_sky.read_sky(self.daemon.client)
                with self.lock:
                    self.sky_state = st if isinstance(st, dict) else {}
                    if not st.get("ok"):
                        self.sky_disabled = True
                return dict(st, ok=st.get("ok", False))
            if sub == "reward":
                r = cok_sky.get_reward(self.daemon.client, family=fam)
                st = cok_sky.read_sky(self.daemon.client, family=fam)
                with self.lock:
                    self.sky_state = st if isinstance(st, dict) else {}
                self.daemon.emit("sky_reward", r)
                if r.get("ok"):
                    self._record_sky_reward(r, source="manual")
                rewards = []
                for g in (r.get("rewards") or []):
                    iid = str(g.get("itemId") or "")
                    rewards.append({
                        "itemId": iid,
                        "name": self._tr_item(iid) or ("道具 " + iid),
                        "count": g.get("count"),
                        "uuid": g.get("uuid"),
                    })
                return {
                    "ok": r.get("ok"),
                    "errorCode": r.get("errorCode"),
                    "errorText": self._err_text(r.get("errorCode")),
                    "error": r.get("error"),
                    "family": r.get("family") or fam,
                    "count": r.get("count"),
                    "rewards": rewards,
                }
            if sub == "explore":
                # 探索固定一次: 不再有"次数"设置, 点一下就探索一次。
                r = cok_sky.explore(self.daemon.client, num=1, family=fam)
                st = cok_sky.read_sky(self.daemon.client, family=fam)
                with self.lock:
                    self.sky_state = st if isinstance(st, dict) else {}
                self.daemon.emit("sky_explore", r)
                if r.get("ok"):
                    self._record_task_completion(
                        "sky_explore", 1, "天空之境探索")
                # 被拒时, 用刚读到的状态补充一条可能的原因(仅提示, 不是拦截)
                hint = ""
                if not r.get("ok") and isinstance(st, dict) and st.get("explore_reason"):
                    hint = st.get("explore_reason")
                return {
                    "ok": r.get("ok"),
                    "errorCode": r.get("errorCode"),
                    "errorText": self._err_text(r.get("errorCode")),
                    "error": r.get("error"),
                    "hint": hint,
                    "family": r.get("family") or fam,
                    "num": r.get("num"),
                    "state": (st or {}).get("state"),
                    "state_text": (st or {}).get("state_text"),
                }
            return {"ok": False, "error": "未知天空之境操作 %r" % sub}
        if act == "alliance":
            # 联盟: 科技树/任务板/捐献/使命/商店
            # 读是只读; 写(接任务/领奖/求助/捐献)都是**真副作用**,
            # 必须由用户在页面上显式点, 不做自动。
            cli = self.daemon.client
            if cli is None:
                return {"ok": False, "error": "还没有连接游戏服"}
            sub = body.get("op") or "read"
            try:
                if sub == "read":
                    self._alliance_tick(cli, force=True)
                    return {"ok": True, "view": self._alliance_view()}
                if sub == "accept":
                    r = cok_alliance.accept_task(cli, body.get("taskUid"))
                elif sub == "accept-all":
                    r = cok_alliance.accept_tasks(cli, body.get("limit"))
                elif sub == "award":
                    r = cok_alliance.award_task(cli, body.get("taskUid"))
                elif sub == "help":
                    r = cok_alliance.call_help(cli, body.get("queueId"),
                                               body.get("qType") or 0)
                elif sub == "help-all":
                    r = cok_alliance.help_all(cli)
                elif sub == "donate":
                    sid = body.get("scienceId")
                    if not sid:
                        summ = (self.alliance_state or {}).get("science") or {}
                        sid = summ.get("researching") or ""
                    # 前置条件自己先判一遍: 在研科技已攒满进度时,
                    # 服务端只会回 E000000(操作无效), 不如直接说清楚原因。
                    reason = ""
                    sci = (self.alliance_state or {}).get("science") or {}
                    for s in (sci.get("list") or []):
                        if str(s.get("scienceId")) == str(sid):
                            if s.get("full"):
                                reason = "该科技进度已攒满(已是可研究状态), 无法继续捐献"
                            break
                    if not sid:
                        reason = "当前没有正在研究的联盟科技"
                    if reason:
                        return {"ok": False, "error": reason,
                                "errorText": reason,
                                "view": self._alliance_view()}
                    tier = body.get("tier") or \
                        str(self.settings.get("allianceDonateTier") or "random")
                    if tier == "random":
                        # 随机挑一个当前开放的档位(和自动捐献同一套规则)
                        panel = cok_alliance.read_donate_panel(cli, sid)
                        tiers = cok_alliance.available_tiers(panel)
                        pick = cok_alliance.pick_tier(tiers, "random")
                        tier = (pick or {}).get("key") or "low"
                    r = cok_alliance.donate(cli, sid, tier)
                elif sub == "sign-in":
                    # 联盟签到(alliance.signIn.reward, 无参)
                    st = cok_alliance.read_sign_in(cli)
                    if st.get("signed"):
                        return {"ok": True, "error": "",
                                "result": {"count": 0, "already": True},
                                "note": "今天已经签过了(连续 %s 天)" % st.get("days"),
                                "view": self._alliance_view()}
                    r = cok_alliance.claim_sign_in(cli)
                elif sub == "donate-auto":
                    # 手动跑一次"随机档位 + 捐到满"的自动流程
                    # 前置检查: 在研科技已满就别发命令了(服务端只会回笼统的
                    # E000000, 不如直接说清楚原因)
                    sci_now = (self.alliance_state or {}).get("science") or {}
                    for s in (sci_now.get("list") or []):
                        if s.get("researching") and s.get("full"):
                            return {"ok": False,
                                    "error": "该科技进度已攒满(已是可研究状态), 无法继续捐献",
                                    "errorText": "该科技进度已攒满(已是可研究状态), 无法继续捐献",
                                    "result": {"acted": [], "done": True,
                                               "capReached": True,
                                               "stop": "该科技进度已满(达到本次捐献上限)"},
                                    "view": self._alliance_view()}
                    r = cok_alliance.auto_donate(
                        cli,
                        tier_mode=str(body.get("tier")
                                      or self.settings.get("allianceDonateTier")
                                      or "random"),
                        max_iter=int(body.get("limit")
                                     or self.settings.get("allianceDonateMax") or 20))
                    r = {"ok": bool(r.get("acted")) or bool(r.get("ok")),
                         "errorCode": None,
                         "error": r.get("stop") or "",
                         "acted": r.get("acted") or [],
                         "done": r.get("done"),
                         "capReached": r.get("capReached")}
                else:
                    return {"ok": False, "error": "未知联盟操作 %r" % sub}
            except Exception as e:  # noqa: BLE001
                return {"ok": False, "error": str(e)[:200]}
            # 写完立刻回读一次, 让页面显示最新状态
            self._alliance_tick(cli, force=True)
            view = self._alliance_view()
            code = r.get("errorCode")
            return {
                "ok": bool(r.get("ok")),
                "errorCode": code,
                "errorText": cok_alliance.ERROR_TEXT.get(str(code or ""), ""),
                "error": r.get("error") or "",
                "result": {k: v for k, v in r.items()
                           if k not in ("ok", "errorCode", "error")},
                "view": view,
            }
        if act == "welfare":
            # 福利中心(每日好礼 / 龙之馈赠)
            sub = body.get("op") or "read"
            if sub == "claim":
                cli = self.daemon.client
                if cli is None:
                    return {"ok": False, "error": "还没有连接游戏服"}
                try:
                    st = cok_welfare.read_all(cli)
                    acted = self._welfare_claim(cli, st, tag="welfare_claim")
                    try:
                        st = cok_welfare.read_all(cli)
                    except Exception:  # noqa: BLE001
                        pass
                    with self.lock:
                        self.welfare_state = st
                    return {"ok": True, "acted": acted, "view": self._welfare_view()}
                except Exception as e:  # noqa: BLE001
                    return {"ok": False, "error": str(e)[:200]}
            # read: 只读状态, 不领
            self._welfare_tick()
            return {"ok": True, "view": self._welfare_view()}
        if act == "hunt":
            return self._hunt_action(body)
        if act == "score":
            # 积分商城(右键菜单 -> 积分商城 -> 积分好礼): 积分任务奖励
            cli = self.daemon.client
            if cli is None:
                return {"ok": False, "error": "还没有连接游戏服"}
            sub = body.get("op") or "read"
            if sub == "read":
                st = cok_scoremall.read_score_mall(cli)
                if isinstance(st, dict) and self.score_state.get("last_claim"):
                    st["last_claim"] = self.score_state.get("last_claim")
                with self.lock:
                    self.score_state = st if isinstance(st, dict) else {}
                return dict(self._score_view(), ok=bool(st.get("ok")),
                            errorText=self._err_text(st.get("errorCode")))
            if sub in ("claim", "claim-all"):
                pre = cok_scoremall.read_score_mall(cli)
                if not pre.get("ok"):
                    with self.lock:
                        self.score_state = pre
                    return {"ok": False, "error": pre.get("error") or "积分商城读取失败",
                            "errorCode": pre.get("errorCode"),
                            "errorText": self._err_text(pre.get("errorCode")),
                            "keys": pre.get("keys")}
                if sub == "claim" and body.get("taskId"):
                    results = [cok_scoremall.claim_task(cli, body.get("taskId"))]
                    r = {"ok": True, "results": results,
                         "claimed": sum(1 for x in results if x.get("ok")),
                         "failed": sum(1 for x in results if not x.get("ok")),
                         "pending": 1}
                else:
                    r = cok_scoremall.claim_all(cli, state=pre)
                acted = self._score_acted(r)
                if acted:
                    self.daemon.emit("score_claim", {"note": "; ".join(acted)})
                st = cok_scoremall.read_score_mall(cli)
                rewards = []
                for x in r.get("results") or []:
                    for g in x.get("rewards") or []:
                        iid = str(g.get("itemId") or "")
                        rewards.append({"itemId": iid, "num": g.get("num"),
                                        "name": self._tr_item(iid) or ("道具 " + iid if iid else "奖励"),
                                        "taskId": x.get("taskId")})
                fails = [{"taskId": x.get("taskId"),
                          "errorCode": x.get("errorCode"),
                          "errorText": self._err_text(x.get("errorCode")),
                          "error": x.get("error")}
                         for x in r.get("results") or [] if not x.get("ok")]
                if isinstance(st, dict):
                    st["last_claim"] = {"at": int(time.time()), "pending": r.get("pending", 0),
                                        "claimed": r.get("claimed", 0), "rewards": rewards,
                                        "fails": fails}
                with self.lock:
                    self.score_state = st if isinstance(st, dict) else {}
                return {"ok": True, "pending": r.get("pending", 0),
                        "claimed": r.get("claimed", 0), "failed": r.get("failed", 0),
                        "rewards": rewards, "fails": fails, "acted": acted,
                        "view": self._score_view()}
            return {"ok": False, "error": "未知积分商城操作 %r" % sub}
        if act == "locate":
            return self._locate_action(body)
        if act == "refresh-now":
            return self.refresh_now()
        return {"ok": False, "error": "未知操作 %r" % act}

    def _locate_action(self, body):
        """按玩家名字查地图坐标。

        两条路径:
          1. **本地索引**(map-index.json) —— 全图扫描建好的, 零消耗零连接。
             「查询坐标」(op=query)**只走这一条**: 命中后可选用一次 world.get
             做实时校验(0.17 秒、不消耗道具), 校验通过就用服务端最新坐标
             (source=index+verified); 校验不通过说明服务端重排过地图、原位置
             已换人, 仍返回索引里的坐标但标记 stale=True 提示可能已迁移。
             索引里没有该玩家时直接返回空结果, 不再消耗「坐标侦查」道具兜底。
          2. **现场扫描**(「扫描附近」, op=scan) —— 用 world.get 扫自己周边一片
             区域建索引(也不消耗道具)。
        """
        name = str(body.get("name") or "").strip()
        uid = body.get("uid")
        sub = body.get("op") or "query"

        # 现场扫描: 用 world.get 扫一片区域建索引(不消耗任何道具)
        if sub == "scan":
            radius = int(body.get("radius") or 60)
            cx = int(body.get("cx") or 0)
            cy = int(body.get("cy") or 0)
            if not cx or not cy:
                # 以**自己**的位置为中心(从队列/概览数据拿不到就认坐标)
                own = self._own_point()
                cx, cy = own
            st = cok_map.scan_area(self.daemon.client,
                                   cx - radius, cy - radius, cx + radius, cy + radius,
                                   step=cok_map.STEP, path=self._index_path(),
                                   own_uid=(getattr(self.args, "account", None) or {}).get("gameUid"))
            self._last_scan_center = (cx, cy)
            idx = cok_map.load_index(self._index_path())
            hits = cok_map.find_players(idx, name, limit=20) if name else []
            return {"ok": True, "source": "scan",
                    "players": hits, "scan": st,
                    "center": {"x": cx, "y": cy},
                    "index_total": len(idx.get("players") or {})}

        # 查询坐标: 仅以全图扫描建立的本地索引为准
        if not name:
            return {"ok": False, "error": "请输入玩家名字"}

        idx = cok_map.load_index(self._index_path())
        hits = cok_map.find_players(idx, name, limit=20)
        if uid:
            hits = [h for h in hits if h.get("uid") == str(uid)] or hits
        index_total = len(idx.get("players") or {})
        index_updated = (idx.get("meta") or {}).get("updated_at")

        if not hits:
            # 索引里没有 -> 让用户先全图扫描, 不再消耗道具兜底
            msg = ("索引为空, 请先执行全图扫描" if index_total == 0
                   else "索引中没有匹配该名字的玩家(可先全图扫描或扫描附近)")
            return {"ok": True, "source": "index", "count": 0, "players": [],
                    "index_total": index_total, "index_updated": index_updated,
                    "message": msg}

        # 命中索引 -> 用一次 world.get 做实时校验(免费, 拿最新坐标)
        cand = hits[0]
        verified = None
        attempted = False
        cx, cy = cand.get("x"), cand.get("y")
        if cx is not None and cy is not None and self.daemon.client:
            attempted = True
            try:
                res = cok_map.fetch_area(self.daemon.client, cx, cy)
                still = [p for p in (res.get("players") or [])
                         if str(p.get("uid")) == str(cand.get("uid"))]
                if still:
                    verified = still[0]
            except Exception:  # noqa: BLE001
                verified = None
                attempted = False  # 网络异常, 没能真正校验

        if verified is not None:
            # 坐标还有效 -> 用服务端给的最新值(比索引新)
            out = [verified] + [h for h in hits[1:] if h.get("uid") != verified.get("uid")]
            return {"ok": True, "source": "index+verified", "count": len(out),
                    "players": out, "stale": False,
                    "index_total": index_total, "index_updated": index_updated}

        # 校验不通过(原位置已换人)或未校验 -> 仍返回索引坐标, 标记可能过期
        msg = ("坐标来自上次扫描, 原位置已换人, 该玩家可能已迁移" if attempted
               else "坐标来自上次扫描(未实时校验)")
        return {"ok": True, "source": "index", "count": len(hits),
                "players": hits, "stale": attempted,
                "index_total": index_total, "index_updated": index_updated,
                "message": msg}


    def _account_holder_self(self):
        """当前账号锁是不是本进程自己拿着。"""
        try:
            return bool(cok_client.account_holder_info(self._lock_key()).get("self"))
        except Exception:
            return False

    # ---------------- 多账号管理 ----------------
    def _accounts_summary(self):
        """账号库概况: 列表 + 当前选中 id(给页面下拉框用)。"""
        try:
            lst = accounts.list_accounts()
        except Exception:  # noqa: BLE001
            lst = []
        try:
            active = accounts.get_active_key()
        except Exception:  # noqa: BLE001
            active = ""
        return {
            "list": lst,
            "active": active,
            # 当前引擎实际在用的账号(可能还没被 active 覆盖, 比如首轮用的设备号)
            "current": self.account_key,
            "current_label": self.account_label,
        }

    def _account_switch(self, body):
        """切换当前账号: 写 active 指针, 清掉旧连接/账号态, 下一轮按新账号重连。"""
        key = str((body or {}).get("key") or "").strip()
        if not key:
            return {"ok": False, "error": "缺少账号 key"}
        if accounts.get_account(key) is None:
            return {"ok": False, "error": "账号库里没有这个账号: %s" % key}
        # 打怪是常驻连接且独占旧账号的锁, 切号会把它晾在半路 —— 先拦住。
        if self.hunter and self.hunter.state.get("running"):
            return {"ok": False, "error": "自动打怪进行中, 请先停掉打怪再切换账号"}
        if key == accounts.get_active_key() and key == self.account_key:
            return {"ok": True, "note": "已经是当前账号", "active": key}
        try:
            accounts.set_active_key(key)
        except Exception as e:  # noqa: BLE001
            return {"ok": False, "error": "切换失败: %s" % str(e)[:120]}
        # 清空当前连接与账号态, 让下一轮轮询(或下一次操作)按新账号重新解析。
        with self.op_lock:
            try:
                if self.daemon.client:
                    self.daemon.client.close()
            except Exception:  # noqa: BLE001
                pass
            self.daemon.client = None
            with self.lock:
                self.connected = False
                self.args.account = None
                self.account_key = ""
                self.account_label = ""
                self.account_source = ""
                self.account_error = ""
                self.account_note = ""
                # 换号后旧账号的内存快照要清掉, 不然页面会串台显示上一个号的数据
                self.states = {}
                self.hunt = {}
                self.gold = None
                self.dock_state = {}
                self.shield_state = {}
            # 重新解析账号(切数据目录 + 定 key); 失败也不致命, 下一轮还会再试
            try:
                self._ensure_account()
            except Exception:  # noqa: BLE001
                pass
        return {"ok": True, "active": key,
                "label": self.account_label or key,
                "note": "已切换账号, 正在用新账号重新连接"}

    def _account_add_device(self, body):
        """把**设备上的账号**读进账号库(需要 root 的 adb)。

        手机上可能装了**多个渠道包**(海尔果盘 / 果盘国服 ...), 每个包一个号。
        默认把设备上**所有** COK 包的账号都加进来; 也可以用 body.package 指定单个包。

        每个包会读**两个**角色:
          * 当前号(platformUid / game_uid)
          * **上一个号**(游戏切号时留在 prefs 的 original_account_* 里) ——
            它的平台 token 从渠道 SDK 的角色信息取, 所以**登过的号都能捞回来, 不用密码**。
        pf 是**每账号**字段且服务端会校验, 这里用**登录实测**确定(可 body.noProbe 关闭)。
        """
        body = body or {}
        want = str(body.get("package") or "").strip()
        pkgs = []
        if want:
            pkgs = [want]
        else:
            try:
                import cok_account as _ca
                pkgs = _ca.list_packages()
            except Exception as e:  # noqa: BLE001
                return {"ok": False, "error": "读设备包列表失败: %s" % str(e)[:140]}
            if not pkgs:
                pkgs = [cok_account.PKG]
        added, skipped = [], []
        for pkg in pkgs:
            cands = []
            try:
                cands.append(("当前号", load_account(pkg)))
            except Exception as e:  # noqa: BLE001
                skipped.append("%s: 读取失败(%s)" % (pkg, str(e)[:60]))
            try:
                import cok_account as _ca2
                prev = _ca2.load_previous_account(pkg)
                if prev:
                    cands.append(("上一个号", prev))
            except Exception:  # noqa: BLE001
                pass
            for tag, acc in cands:
                missing = [k for k in ACCOUNT_REQUIRED if not acc.get(k)]
                if missing:
                    skipped.append("%s[%s]: 账号不完整(缺 %s)"
                                   % (pkg, tag, ",".join(missing)))
                    continue
                pf_ok = False
                if not body.get("noProbe"):
                    try:
                        pf_ok, pf = accounts.probe_pf(acc)
                    except Exception as e:  # noqa: BLE001
                        pf_ok, pf = False, None
                        skipped.append("%s[%s]: pf 实测跳过(%s)"
                                       % (pkg, tag, str(e)[:60]))
                    if pf_ok:
                        acc["pf"] = pf
                        acc["pfVerified"] = True
                    else:
                        acc["pfVerified"] = False
                        skipped.append("%s[%s]: pf 实测失败(保留候选 %s)"
                                       % (pkg, tag, acc.get("pf")))
                try:
                    key = accounts.save_account(acc)
                except Exception as e:  # noqa: BLE001
                    skipped.append("%s[%s]: 入库失败(%s)" % (pkg, tag, str(e)[:60]))
                    continue
                added.append({"key": key,
                              "label": accounts.account_label(accounts.get_account(key)),
                              "package": pkg, "role": tag,
                              "pf": acc.get("pf"), "pfVerified": pf_ok})
        if not added:
            return {"ok": False,
                    "error": "设备上没读到可用账号",
                    "detail": skipped}
        label = str(body.get("label") or "").strip()
        if label and len(added) == 1:
            accounts.set_label(added[0]["key"], label)
        if not accounts.get_active_key():
            accounts.set_active_key(added[0]["key"])
        return {"ok": True, "key": added[0]["key"],
                "added": added, "skipped": skipped,
                "label": accounts.account_label(accounts.get_account(added[0]["key"])),
                "note": "已加入账号库: %s" % ", ".join(a["label"] or a["key"]
                                                    for a in added)}

    def _account_remove(self, body):
        """从账号库删除一个账号(不动它已扫到的数据目录)。"""
        key = str((body or {}).get("key") or "").strip()
        if not key:
            return {"ok": False, "error": "缺少账号 key"}
        if key == self.account_key and (self.hunter
                                        and self.hunter.state.get("running")):
            return {"ok": False, "error": "该账号正在打怪, 请先停掉再删除"}
        ok = accounts.remove_account(key)
        # 删的是当前 active, 把指针让给剩下的任意一个
        if ok and key == accounts.get_active_key():
            rest = accounts.list_accounts()
            if rest:
                accounts.set_active_key(rest[0]["key"])
        return {"ok": bool(ok),
                "error": "" if ok else "账号库里没有这个账号",
                "active": accounts.get_active_key()}

    def _account_relabel(self, body):
        """给账号改个显示名。"""
        key = str((body or {}).get("key") or "").strip()
        label = str((body or {}).get("label") or "").strip()
        if not key or not label:
            return {"ok": False, "error": "缺少 key 或 label"}
        ok = accounts.set_label(key, label)
        if ok and key == self.account_key:
            self.account_label = label
        return {"ok": bool(ok),
                "error": "" if ok else "账号库里没有这个账号"}

    def _channel_login(self, body):
        """渠道(果盘)账号密码登录: **纯 PC**, 不依赖设备/模拟器/root。

        三跳(2026-10-29 全部实测通过):
          1. 果盘 HTTP(XXTEA+protobuf): 取 salt -> MD5(salt+密码) -> 登录
             -> 响应带 per-game id(f18.f5) -> 派生 **pfId**(游戏服认的平台身份);
          2. 游戏服 HTTP `gameservice/getserverlist.php`(**按 pfId 解析角色**, 与设备 uuid 无关)
             -> **gameUid / 账号 uuid / 区服 / buildCode**;
          3. 组装凭据 -> 入账号库 -> 网页里切过去直接用。

        所以"用账号密码登录别人在别的设备玩过的号"是**可行的**:
        只要有 pfId, 剩下的凭据游戏服会自己发。
        """
        if channel is None:
            return {"ok": False,
                    "error": "渠道登录模块未加载(cok_channel_login.py 缺失或导入失败): %s"
                             % (CHANNEL_IMPORT_REASON or "未知原因"),
                    "detail": CHANNEL_IMPORT_ERROR}
        account = str((body or {}).get("account") or "").strip()
        password = str((body or {}).get("password") or "")
        if not account or not password:
            return {"ok": False, "error": "请填写渠道账号和密码"}
        try:
            res = channel.channel_login_list_small(account, password, verbose=False)
        except Exception as e:  # noqa: BLE001  网络/协议异常都兜住, 不要让网页 500
            return {"ok": False, "error": "渠道登录请求失败: %s" % str(e)[:160]}
        if not res.get("ok"):
            stage = res.get("stage", "salt")
            if stage == "salt":
                # 取 salt 就失败: 多半是渠道服务器不可达或账号格式不对
                return {"ok": False, "stage": stage,
                        "error": "取 salt 失败(渠道服务器不可达或账号异常)",
                        "resp": res.get("resp")}
            # stage == "login": **业务错**(账号/密码不对), 协议本身是通的 ->
            # 走下面的"协议正常但未通过"分支, 不要误报成"取 salt 失败"
            return {"ok": True, "succeeded": False, "account": account,
                    "stage": stage,
                    "bizCodes": ([res.get("retcode")] if res.get("retcode") is not None
                                 else []),
                    "errmsg": res.get("errmsg"),
                    "note": ("协议走通了(取 salt + 提交登录都成功发出), 但果盘判定登录未通过"
                             " —— %s" % (res.get("errmsg") or "多半是账号或密码不对"))}
        fields = res.get("login_fields") or {}
        retcodes = res.get("login_retcodes") or []
        # 果盘登录是否成功: 顶层业务码 f3.f1==0 为成功。
        # (retcodes 里字段号 1 的那个值就是主返回码; retcode 是它的快捷方式)
        biz_codes = [c for (f, c) in retcodes if f == 1]
        if res.get("retcode") is not None:
            biz_codes = [res.get("retcode")]
        succeeded = (0 in biz_codes)
        if not succeeded:
            return {"ok": True, "succeeded": False,
                    "account": account, "salt": res.get("salt"),
                    "bizCodes": biz_codes,
                    "note": ("协议走通了(取 salt + 提交登录都成功发出), 但果盘判定登录未通过"
                             "——多半是账号或密码不对。业务码: %s" % (biz_codes or "未知"))}
        ident = channel.derive_platform_identity(fields)
        # 小号列表(每个小号 = 一个游戏身份)。已入库的标记出来, 页面默认不勾选。
        items = res.get("smallAccounts") or []
        lib = {}
        try:
            for a in accounts.list_accounts():
                full = accounts.get_account(a.get("key")) or {}
                if full.get("pfId"):
                    lib[full["pfId"]] = {"key": a.get("key"),
                                         "label": a.get("label") or full.get("label"),
                                         "gameUid": full.get("gameUid")}
        except Exception:  # noqa: BLE001
            lib = {}
        for it in items:
            m = lib.get(it.get("pfId"))
            it["inLibrary"] = bool(m)
            it["libraryKey"] = (m or {}).get("key")
            it["libraryLabel"] = (m or {}).get("label")
        # 缓存本次会话(信封 + 小号清单), 供"添加选中"那一步用(凭据不经过前端)
        sid = secrets.token_urlsafe(9)
        self._chan_sessions[sid] = {
            "at": time.time(),
            "account": account,
            "authEnvelope": res.get("authEnvelope"),
            "guopanUid": res.get("guopanUid"),
            "items": {it.get("perGameId"): it for it in items},
        }
        self._chan_sessions_prune()
        note = ("果盘登录成功, 该账号下有 %d 个游戏小号。勾选想加入控制台的, 点「添加选中」。"
                % len(items))
        if not items:
            note = ("果盘登录成功, 但**没列出任何小号**(%s)。"
                    "可能是这个果盘号还没在游戏里开过号。"
                    % (res.get("note") or ""))
        return {"ok": True, "succeeded": True,
                "account": account, "salt": res.get("salt"),
                "bizCodes": biz_codes,
                "pfId": ident.get("pfId"), "pf": ident.get("pf"),
                "platformToken": ident.get("platformToken"),
                "perGameId": ident.get("perGameId"),
                "guopanUid": res.get("guopanUid"),
                "smallAccounts": items, "sessionId": sid,
                "note": note}

    def _chan_sessions_prune(self):
        """清掉过期的渠道登录会话(信封不该长期留在内存里)。"""
        now = time.time()
        for k in [k for k, v in self._chan_sessions.items()
                  if now - v.get("at", 0) > 1800]:
            self._chan_sessions.pop(k, None)

    def _channel_add(self, body):
        """把选中的小号加入账号库(用户挑过之后才写)。"""
        if channel is None:
            return {"ok": False,
                    "error": "渠道登录模块未加载: %s"
                             % (CHANNEL_IMPORT_REASON or "未知原因"),
                    "detail": CHANNEL_IMPORT_ERROR}
        body = body or {}
        sid = str(body.get("sessionId") or "").strip()
        want = [str(x) for x in (body.get("perGameIds") or []) if str(x).strip()]
        label = str(body.get("label") or "").strip()
        sess = self._chan_sessions.get(sid)
        if not sess:
            self._chan_sessions_prune()
            sess = self._chan_sessions.get(sid)
        if not sess:
            return {"ok": False, "error": "会话已过期, 请重新登录"}
        if not want:
            return {"ok": False, "error": "请先勾选要添加的游戏号"}
        added, skipped = [], []
        for per in want:
            it = (sess.get("items") or {}).get(per)
            if not it:
                skipped.append("%s: 不在本次登录列出的小号里" % per)
                continue
            if not it.get("hasCharacter"):
                skipped.append("%s(%s): 游戏服还没有角色, 先在游戏里开号"
                               % (it.get("name") or per, per))
                continue
            try:
                pf_id = str(it.get("pfId") or "")
                # Each selected Guopan game role has its own platform identity.
                # Rebuilding the account without this token produced a login
                # which passed the handshake but whose feature requests were
                # silently ignored by the game server.
                platform_token = pf_id.partition(":")[2]
                acc, _gs = channel.build_account_from_pf_id(
                    pf_id, platform_token=platform_token)
            except Exception as e:  # noqa: BLE001
                skipped.append("%s: 解析游戏服凭据失败(%s)" % (per, str(e)[:60]))
                continue
            if acc is None:
                skipped.append("%s: 游戏服没解析出角色" % per)
                continue
            acc["channelAccount"] = sess.get("account")
            # 入库前先看凭据齐不齐: 缺字段的号切过去时只会报
            # "凭据不完整(缺 xxx)" —— 那时用户根本不知道是哪一步缺的。
            # 这里提前记下来, 随添加结果一起回给界面。
            missing = [k for k in ACCOUNT_REQUIRED if not acc.get(k)]
            if missing:
                acc["incompleteFields"] = ",".join(missing)
            try:
                key = accounts.save_account(acc, label=label or None)
            except Exception as e:  # noqa: BLE001
                skipped.append("%s: 入库失败(%s)" % (per, str(e)[:60]))
                continue
            added.append({"key": key,
                          "label": accounts.account_label(accounts.get_account(key)),
                          "gameUid": acc.get("gameUid"),
                          "roleName": acc.get("roleName") or it.get("name"),
                          "zone": acc.get("zn"),
                          "missing": missing,
                          "signCodeSource": acc.get("signCodeSource") or ""})
        if not added:
            return {"ok": False, "error": "没有可添加的游戏号", "detail": skipped}
        if label and len(added) == 1:
            accounts.set_label(added[0]["key"], label)
        note = "已加入账号库: %s" % ", ".join(a["label"] or a["key"]
                                            for a in added)
        bad = [a for a in added if a.get("missing")]
        if bad:
            note += ("; 但 %s 的凭据不完整(缺 %s) —— 切到它会连不上, "
                     "请检查 signCode 是否取到" % (
                         ", ".join(a["label"] or a["key"] for a in bad),
                         ", ".join(sorted({m for a in bad for m in a["missing"]}))))
        return {"ok": True, "added": added, "skipped": skipped, "note": note}

    # ---------------- 全图扫描(独立进程) ----------------

    def _scan_status(self, idx=None):
        """全图扫描的状态: 在不在跑、进度、健康指标。

        扫描是**独立进程**, 网页重启也不影响它 —— 所以状态靠 pid 文件判断,
        不能只看索引里的 meta.scanning(进程被强杀时那个标志会一直挂着)。
        """
        pid = cok_map.read_scan_pid(self._pid_path())
        alive = False
        if pid:
            try:
                os.kill(pid, 0)
                alive = True
            except OSError:
                alive = False
        if idx is None:
            idx = cok_map.load_index(self._index_path())
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
        # 先把账号定下来: set_data_dir 会把 cok_map.DEFAULT_INDEX 切到该账号目录,
        # 下面的 --out / 备份 / 续扫判断才会落在正确的账号数据目录里。
        self._ensure_account()
        lk = self._lock_key()
        st = self._scan_status()
        if st.get("running"):
            return {"ok": False, "error": "扫描已经在跑了 (pid %s)" % st.get("pid")}
        # 自动打怪是常驻连接, 会一直占着账号 —— 扫描起不来
        if self.hunter and self.hunter.state.get("running"):
            return {"ok": False,
                    "error": "自动打怪正在占用账号连接, 请先停掉打怪再扫描"}
        body = body or {}
        index_path = self._index_path()
        meta = (cok_map.load_index(index_path).get("meta") or {})
        # ⚠️ 先让网页**自己**把账号交出来: 扫描器和后台轮询会互相抢锁
        # (轮询每 5 秒一轮、每轮持锁 2~3 秒), 扫描器用 LOCK_NB 轮询
        # 可能整整 120 秒都抢不到空隙。暂停轮询后扫描器就能稳定拿到锁。
        self._suspend_poll = True
        self._poll_suspend_until = time.time() + 120.0
        # ⚠️ 只有「上次是**全图**扫描且被中断」才续扫 —— 小范围扫描的断点
        # 落在地图一角, 全图扫描接着它扫会把那一大片漏掉。
        runs = (cok_map.load_history(self._history_path()).get("runs") or [])
        last_full = None
        for r in runs:
            if not int(r.get("radius") or 0):
                last_full = r
                break
        step = int(body.get("step") or 12)
        radius = int(body.get("radius") or 0)
        # ⚠️ fresh / resume / radius **三选一且互斥**:
        #   fresh  = 清空索引从头扫(全图重扫; 旧坐标属于上一次地图布局)
        #   resume = 接着上次的断点继续(索引里已有数据, 不能清)
        #   radius = 只扫自己周围 N 格
        # fresh+resume 一起用 = 清空后又从旧断点开始, 断点之前的区域永远漏掉。
        # 特例: 勾了续扫但断点不可用 -> 三个都不加, 即「不清空、扫全图」(沿用历史行为)。
        want_resume = bool(body.get("resume"))
        do_resume = False
        do_fresh = False
        use_radius = 0
        if want_resume:
            if (radius <= 0 and last_full
                    and last_full.get("status") == "interrupted"
                    and meta.get("partial") and meta.get("next_x") is not None):
                do_resume = True
        elif radius > 0:
            use_radius = radius
        else:
            do_fresh = True
        maxreq = int(body.get("maxRequests") or 0)
        # 限速: 服务端在请求过快时会降速, 匀速反而更快跑完
        dly = float(body.get("delay", 0.25))
        # 扫描前备份现有索引 —— 扫描中途失败不至于毁掉已有数据。
        # 多账号: 备份与日志也落在各自账号目录, 并行时不互相覆盖/穿插。
        data_dir = self._data_dir()
        bak = ""
        try:
            if (os.path.exists(index_path)
                    and os.path.getsize(index_path) > 1024):
                bak = os.path.join(
                    data_dir, "map-index.backup-%s.json" % time.strftime("%Y%m%d-%H%M%S"))
                with open(index_path, "rb") as fi, open(bak, "wb") as fo:
                    fo.write(fi.read())
                self._trim_scan_backups(data_dir)
        except OSError:
            bak = ""
        # 归一化的扫描参数; 桌面端拼成 scan_world.py 的命令行, 安卓端直接喂给 run_scan。
        params = {
            "out": index_path, "account_key": lk, "step": step,
            "resume": do_resume, "fresh": do_fresh, "radius": use_radius,
            "max_requests": maxreq, "delay": dly, "data_dir": data_dir,
        }
        # ⚠️ 启动方式是**可替换的接缝**: 桌面端 = 独立子进程(_spawn_scanner 默认实现);
        # 安卓端没有可执行的 python, 由 android_entry.py 注入"进程内线程"版本。
        return self._spawn_scanner(params, bak)

    def _spawn_scanner(self, params, bak):
        """默认(桌面)启动器: 用独立子进程跑 scan_world.py。

        安卓端在 android_entry.py 里覆盖本方法, 改成进程内后台线程 ——
        Chaquopy 没有可执行的 python 解释器, subprocess 那条路在手机上必然失败。
        """
        cmd = [sys.executable, os.path.join(HERE, "scan_world.py"),
               "--out", params["out"]]
        if params.get("account_key"):
            cmd += ["--account-key", params["account_key"]]
        cmd += ["--step", str(params["step"])]
        if params.get("resume"):
            cmd.append("--resume")
        elif int(params.get("radius") or 0) > 0:
            cmd += ["--radius", str(int(params["radius"]))]
        elif params.get("fresh"):
            cmd.append("--fresh")
        if int(params.get("max_requests") or 0) > 0:
            cmd += ["--max-requests", str(int(params["max_requests"]))]
        if float(params.get("delay") or 0) > 0:
            cmd += ["--delay", str(float(params["delay"]))]
        logp = os.path.join(params.get("data_dir") or HERE, "scan.log")
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
        cok_map.write_scan_pid(p.pid, self._pid_path())
        return {"ok": True, "pid": p.pid,
                "note": "扫描已启动(独立进程, 关掉网页也继续) · 日志 scan.log",
                "cmd": " ".join(cmd[1:]),
                "resumed": "--resume" in cmd,
                "backup": os.path.basename(bak) if bak else ""}

    @staticmethod
    def _trim_scan_backups(data_dir=None, keep=3):
        """只保留最近 N 份索引备份(在 data_dir 里; 默认脚本根目录)。"""
        d = data_dir or HERE
        try:
            names = sorted(f for f in os.listdir(d)
                           if f.startswith("map-index.backup-")
                           and f.endswith(".json"))
            for f in names[:-keep] if len(names) > keep else []:
                try:
                    os.remove(os.path.join(d, f))
                except OSError:
                    pass
        except OSError:
            pass

    def _scan_stop(self):
        """停止扫描(扫描器会保存断点, 之后可续扫)。"""
        pid = cok_map.read_scan_pid(self._pid_path())
        if not pid:
            return {"ok": False, "error": "没有正在跑的扫描"}
        try:
            os.kill(pid, signal.SIGTERM)
        except OSError as e:
            return {"ok": False, "error": "停止失败: %s" % str(e)[:100]}
        return {"ok": True, "note": "已发停止信号, 断点已保存(之后可续扫)"}

    def _scan_history(self):
        """扫描历史(最近的在前)。"""
        return cok_map.load_history(self._history_path())
    def _account_busy(self):
        """账号是不是被**别人**占着(本进程自己用不算)。"""
        try:
            if self._account_holder_self():
                return False
            return bool(cok_client.account_is_busy(self._lock_key()))
        except Exception:
            return False

    def _map_index_summary(self):
        """地图索引的概况(页面概览条 + 导出按钮用)。"""
        try:
            idx = cok_map.load_index(self._index_path())
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
        idx = cok_map.load_index(self._index_path())
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
        qu = str(body.get("uuid") or "")
        count = int(body.get("count") or 1)
        use_gold = bool(body.get("gold"))
        # The phone may hold an older snapshot. Validate everything that can
        # become stale before issuing a resource-consuming game command.
        running = [q for q in (getattr(self.daemon, "queues", None) or [])
                   if isinstance(q, dict)
                   and str(q.get("uuid") or "") == qu
                   and int(q.get("totalTime") or 0) > 0
                   and int(q.get("startTime") or 0) > 0]
        if not running:
            return {"ok": False, "error": "队列已完成、未找到或状态已过期，请刷新后重试"}
        queue = running[0]
        if use_gold:
            params = {"qUUID": qu, "itemUUID": "", "isGold": 1, "itemCount": 1,
                      "queueId": str(body.get("qid") or queue.get("qid") or 1),
                      "queueType": str(body.get("qtype") or 1), "goldcost": "0"}
        else:
            item_uuid = str(body.get("itemUuid") or "")
            if not item_uuid:
                return {"ok": False, "error": "缺少道具实例 uuid(itemUuid)"}
            owned = next((item for item in self._owned_items()
                          if str(item.get("uuid") or "") == item_uuid), None)
            if not owned or int(owned.get("type2") or 0) != 1:
                return {"ok": False, "error": "道具不可用或不是通用加速道具，请刷新背包后重试"}
            available = int(owned.get("count") or 0)
            if count < 1 or count > available:
                return {"ok": False, "error": "道具数量无效，当前库存为 %d" % available}
            params = {"qUUID": qu, "itemUUID": item_uuid, "isGold": 0,
                      "itemCount": count}
        r = self.daemon.client.call("queue.ccd", params)
        p = r.get("__params__") or {}
        self.daemon.emit("speedup_manual", {"params": params, "result": p})
        return {"ok": not p.get("errorCode"), "result": p}


class EngineManager(object):
    """多账号引擎管理器(并行模型)。

    不变量: **每个账号至多一个活跃引擎**。活跃引擎集合 =
        并行开启的账号(self.parallel) ∪ 当前查看账号(self.view_key)
    用账号 key 索引, 从根上杜绝两个引擎抢同一个账号。

    - 查看引擎(view_engine): 页面当前正在看的那个账号的引擎, /api/state 等走它。
    - 并行引擎: 即使没在看, 也在后台轮询/守护/打怪的账号。
    - 账号库是空的(未登记)时退化为单引擎(pinned_key=None), 行为同 Phase 1。
    """

    #: 并行账号集合的持久化文件(重启后自动恢复后台运行的账号)
    PARALLEL_FILE = os.path.join(accounts.ACCOUNTS_DIR, ".parallel")
    SCHEDULE_FILE = os.path.join(accounts.ACCOUNTS_DIR, ".automation-priorities")

    def __init__(self, args):
        self.args = args
        self.lock = threading.RLock()
        self.engines = {}            # key(str, "" 表示默认单引擎) -> Engine
        self.parallel = self._load_parallel()
        self.priorities = self._load_priorities()
        # 初始查看账号: 账号库 active 指针; 没有账号库就用默认引擎("")
        try:
            self.view_key = accounts.get_active_key() or ""
        except Exception:  # noqa: BLE001
            self.view_key = ""

    # ---- 并行集合持久化 ----
    def _load_parallel(self):
        try:
            with open(self.PARALLEL_FILE, encoding="utf-8") as fh:
                data = json.load(fh)
            return set(str(k) for k in data if k)
        except (OSError, ValueError):
            return set()

    def _save_parallel(self):
        try:
            os.makedirs(accounts.ACCOUNTS_DIR, exist_ok=True)
            tmp = self.PARALLEL_FILE + ".tmp"
            with open(tmp, "w", encoding="utf-8") as fh:
                json.dump(sorted(self.parallel), fh)
            os.replace(tmp, self.PARALLEL_FILE)
        except OSError:
            pass

    def _load_priorities(self):
        try:
            with open(self.SCHEDULE_FILE, encoding="utf-8") as fh:
                data = json.load(fh)
            return {str(k): max(1, min(3, int(v))) for k, v in data.items()}
        except (OSError, ValueError, TypeError):
            return {}

    def _save_priorities(self):
        try:
            os.makedirs(accounts.ACCOUNTS_DIR, exist_ok=True)
            tmp = self.SCHEDULE_FILE + ".tmp"
            with open(tmp, "w", encoding="utf-8") as fh:
                json.dump(self.priorities, fh)
            os.replace(tmp, self.SCHEDULE_FILE)
        except OSError:
            pass

    # ---- 引擎生命周期 ----
    def _make_engine(self, key):
        eng = Engine(self.args, pinned_key=(key or None))
        eng.start()
        return eng

    def _ensure(self, key):
        """确保 key 的引擎在跑, 返回它。调用方须持 self.lock。"""
        eng = self.engines.get(key)
        if eng is None:
            eng = self._make_engine(key)
            self.engines[key] = eng
        return eng

    def _desired_keys(self):
        """当前应当活跃的账号集合。"""
        keys = set(self.parallel)
        keys.add(self.view_key)
        return keys

    def _prune(self):
        """停掉不再需要的引擎(既不在并行集、也不是当前查看账号)。持 self.lock。"""
        want = self._desired_keys()
        for key in list(self.engines):
            if key not in want:
                eng = self.engines.pop(key)
                try:
                    eng.stop()
                except Exception:  # noqa: BLE001
                    pass

    def start(self):
        """启动: 把并行账号 + 查看账号的引擎都拉起来。"""
        with self.lock:
            # 优先级只影响启动/恢复的顺序；每个账号随后拥有独立引擎和锁，
            # 不会因为某个账号轮询较慢阻塞另一个账号。
            for key in sorted(self._desired_keys(), key=lambda k: self.priorities.get(k, 2)):
                self._ensure(key)

    def stop_all(self):
        with self.lock:
            for eng in self.engines.values():
                try:
                    eng.stop()
                except Exception:  # noqa: BLE001
                    pass
            self.engines.clear()

    def view_engine(self):
        """页面当前查看账号的引擎(没有就按需创建)。"""
        with self.lock:
            return self._ensure(self.view_key)

    def engine_for(self, key):
        """取某账号的引擎; key 为 None/"" 时回退到查看引擎。"""
        with self.lock:
            if key is None or key == "":
                return self._ensure(self.view_key)
            return self._ensure(key)

    # ---- 账号级操作(管理器层, 影响全局注册表 / 运行集) ----
    def set_view(self, key):
        """切换查看账号。key 必须已登记(或 "" 表示默认引擎)。"""
        if key and accounts.get_account(key) is None:
            return {"ok": False, "error": "账号库里没有这个账号: %s" % key}
        with self.lock:
            if key:
                try:
                    accounts.set_active_key(key)
                except Exception:  # noqa: BLE001
                    pass
            self.view_key = key or ""
            eng = self._ensure(self.view_key)
            self._prune()
        # 切过去的引擎多半正卡在上一轮的睡眠里(ondemand 轮完就断开, 默认睡
        # interval 秒), 顶灯会显示"离线"。这里立刻催它同步一次, 否则页面要
        # 等到下一轮轮询才看到"已连接", 来回切换就显得不连贯。
        try:
            eng.sync_in_background()
        except Exception:  # noqa: BLE001
            pass
        return {"ok": True, "view": self.view_key}

    def set_parallel(self, key, on):
        """开/关某账号的后台并行运行。"""
        if not key:
            return {"ok": False, "error": "缺少账号 key"}
        if accounts.get_account(key) is None:
            return {"ok": False, "error": "账号库里没有这个账号: %s" % key}
        with self.lock:
            if on:
                self.parallel.add(key)
                self._ensure(key)
            else:
                self.parallel.discard(key)
                self._prune()
            self._save_parallel()
        return {"ok": True, "parallel": sorted(self.parallel)}

    def set_priority(self, key, priority):
        if not key or accounts.get_account(key) is None:
            return {"ok": False, "error": "账号库里没有这个账号"}
        try:
            priority = max(1, min(3, int(priority)))
        except (TypeError, ValueError):
            return {"ok": False, "error": "优先级必须是 1 到 3"}
        with self.lock:
            self.priorities[key] = priority
            self._save_priorities()
        return {"ok": True, "key": key, "priority": priority}

    def set_parallel_batch(self, keys, on):
        """批量开关后台托管；无效账号不会影响本批其它账号。"""
        valid = []
        for raw in keys if isinstance(keys, list) else []:
            key = str(raw or "").strip()
            if key and key not in valid and accounts.get_account(key) is not None:
                valid.append(key)
        if not valid:
            return {"ok": False, "error": "没有可管理的账号"}
        with self.lock:
            if on:
                self.parallel.update(valid)
                for key in sorted(valid, key=lambda k: self.priorities.get(k, 2)):
                    self._ensure(key)
            else:
                self.parallel.difference_update(valid)
                self._prune()
            self._save_parallel()
        return {"ok": True, "keys": valid, "on": bool(on),
                "parallel": sorted(self.parallel)}

    def remove_account(self, key):
        """删账号: 先停它的引擎、撤出并行集, 再从注册表删。"""
        if not key:
            return {"ok": False, "error": "缺少账号 key"}
        with self.lock:
            eng = self.engines.get(key)
            if eng and eng.hunter and eng.hunter.state.get("running"):
                return {"ok": False, "error": "该账号正在打怪, 请先停掉再删除"}
            self.parallel.discard(key)
            self.priorities.pop(key, None)
            self._save_parallel()
            self._save_priorities()
            if key in self.engines:
                try:
                    self.engines.pop(key).stop()
                except Exception:  # noqa: BLE001
                    pass
            ok = accounts.remove_account(key)
            if ok and key == accounts.get_active_key():
                rest = accounts.list_accounts()
                accounts.set_active_key(rest[0]["key"] if rest else "")
            # 查看账号被删掉 -> 把视图挪到剩下的 active
            if key == self.view_key:
                self.view_key = accounts.get_active_key() or ""
                self._ensure(self.view_key)
                self._prune()
        return {"ok": bool(ok),
                "error": "" if ok else "账号库里没有这个账号",
                "view": self.view_key}

    def accounts_overview(self):
        """账号库 + 运行状态(给页面下拉框 + 并行开关)。"""
        try:
            lst = accounts.list_accounts()
        except Exception:  # noqa: BLE001
            lst = []
        with self.lock:
            running = set(self.engines)
            parallel = set(self.parallel)
            view = self.view_key
        for a in lst:
            a["running"] = a["key"] in running
            a["parallel"] = a["key"] in parallel
            a["priority"] = self.priorities.get(a["key"], 2)
            eng = self.engines.get(a["key"])
            if eng is not None and hasattr(eng, "_automation_snapshot"):
                try:
                    automation = eng._automation_snapshot()
                    enabled = sum(1 for r in automation["rules"] if r["enabled"])
                    latest = (automation.get("history") or [{}])[0]
                    a["automation"] = {"enabled": enabled,
                                       "paused": automation.get("paused", False),
                                       "last_status": latest.get("status", "waiting"),
                                       "last_summary": latest.get("summary", "尚未执行")}
                except Exception:  # noqa: BLE001
                    pass
            # 紧凑总览: 一屏看清每个在跑的号的关键态(有无罩/待领/报错/打怪/健康)。
            # 只有真正有引擎在跑的号才有摘要; 没跑的号前端显示"未托管"。
            if eng is not None and hasattr(eng, "_overview_summary"):
                try:
                    a["summary"] = eng._overview_summary()
                except Exception:  # noqa: BLE001
                    pass
        return {"list": lst, "active": view, "view": view,
                "parallel": sorted(parallel),
                "running": sorted(k for k in running if k)}


class Handler(BaseHTTPRequestHandler):
    engine = None
    manager = None
    token = None
    server_version = "CokWeb/1.0"

    def log_message(self, fmt, *a):  # 静默默认访问日志
        pass

    def _query(self):
        q = self.path.split("?", 1)
        return parse_qs(q[1]) if len(q) > 1 else {}

    def _eng(self):
        """按 ?account=<key> 路由到对应引擎; 没给就用当前查看引擎。

        没有管理器(理论上不会)时退回旧的单引擎 Handler.engine。
        """
        if self.manager is None:
            return self.engine
        key = (self._query().get("account") or [None])[0]
        return self.manager.engine_for(key)

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
            snap = self._eng().snapshot()
            # 用管理器的全局账号视图覆盖单引擎的(带 running / parallel 标记)
            if self.manager is not None:
                try:
                    snap["accounts"] = self.manager.accounts_overview()
                except Exception:  # noqa: BLE001
                    pass
            self._send(200, snap)
            return
        if path == "/api/scan/status":
            if not self._auth():
                self._send(403, {"error": "unauthorized"})
                return
            self._send(200, self._eng()._scan_status())
            return
        if path == "/api/scan/history":
            if not self._auth():
                self._send(403, {"error": "unauthorized"})
                return
            self._send(200, self._eng()._scan_history())
            return
        if path == "/api/export":
            # 导出地图索引成 Excel(xlsx); ?players=1 只导真实玩家(排除 NPC)
            if not self._auth():
                self._send(403, {"error": "unauthorized"})
                return
            only = "players" in parse_qs(self.path.split("?", 1)[1] if "?" in self.path else "")
            try:
                idx = cok_map.load_index(self._eng()._index_path())
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
                self._send(200, self._eng()._scan_start(body))
                return
            if path == "/api/scan/stop":
                self._send(200, self._eng()._scan_stop())
                return
            self._send(200, self._eng()._scan_history())
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
        # 账号级操作交给管理器(影响全局注册表 / 运行集), 其余路由到对应引擎。
        act = (body or {}).get("action")
        if self.manager is not None and act in MANAGER_ACTIONS:
            self._send(200, self._manager_action(act, body))
            return
        self._send(200, self._eng().action(body))

    def _manager_action(self, act, body):
        m = self.manager
        key = str((body or {}).get("key") or "").strip()
        if act == "account-switch":
            return m.set_view(key)
        if act == "account-parallel":
            return m.set_parallel(key, bool((body or {}).get("on")))
        if act == "account-priority":
            return m.set_priority(key, (body or {}).get("priority"))
        if act == "account-parallel-batch":
            return m.set_parallel_batch((body or {}).get("keys"), bool((body or {}).get("on")))
        if act == "account-remove":
            return m.remove_account(key)
        if act == "account-add-device":
            # 入库仍走引擎(要读设备), 完成后按需拉起/刷新运行集
            r = m.view_engine()._account_add_device(body)
            if r.get("ok") and r.get("key"):
                with m.lock:
                    m._ensure(m.view_key)
            return r
        if act == "account-relabel":
            return m.view_engine()._account_relabel(body)
        if act == "channel-add":
            # 渠道登录会话属于当前查看引擎；入库后必须同步切换管理器，
            # 否则状态/刷新仍会路由到启动时的默认空账号。
            r = m.view_engine()._channel_add(body)
            if r.get("ok") and r.get("added"):
                key = str(r["added"][0].get("key") or "").strip()
                if key:
                    switched = m.set_view(key)
                    if not switched.get("ok"):
                        return {"ok": False,
                                "error": "账号已导入，但切换当前账号失败: %s"
                                         % switched.get("error", "未知错误"),
                                "added": r.get("added")}
                    r["active"] = key
                    # Channel import must immediately establish a snapshot. Do
                    # this asynchronously so a slow game-server response never
                    # makes the account-import request itself time out.
                    m.view_engine().sync_in_background()
                    r["note"] = (r.get("note") or "已加入账号库并切换到新账号") \
                                + "，正在同步游戏状态"
            return r
        return {"ok": False, "error": "未知账号操作 %r" % act}


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
    ap.add_argument("--shield-watch-interval", type=int, default=20,
                    help="常驻连接下, 每隔多少秒戳一下连接以接收推送(被攻击的响应速度)")
    ap.add_argument("--shield-cover-old", type=int, default=1)
    ap.add_argument("--shield-cooldown", type=float, default=600.0)
    ap.add_argument("--shield-refresh-before", type=int, default=300,
                    help="罩还剩不到这么多秒时才续开(默认 5 分钟)")
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
        # Keep the proven lightweight task endpoints first.  Some channel
        # servers do not answer overview_new.data promptly, while dailySign and
        # dailyQuest do, so incremental publication can make the app usable
        # before a later optional module stalls.
        watch=["dailySign", "dailyQuest", "buildQueue", "overview",
               "lordTask", "storyTask", "boss"],
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
    # 多账号并行: 管理器为每个活跃账号持有一个引擎; 账号库为空时退化为单引擎。
    Handler.manager = EngineManager(args)
    Handler.manager.start()
    # 兼容: 留一个 engine 引用指向当前查看引擎(极少数不带 ?account 的旧调用兜底)
    Handler.engine = Handler.manager.view_engine()

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
        Handler.manager.stop_all()
        srv.server_close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
