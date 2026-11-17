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
# --- 包自举: 直接 `python3 cok/core/xxx.py` 时把 cok/ 加进 sys.path ---
import os as _os
import sys as _sys

_PKG_ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
if _os.path.isdir(_PKG_ROOT) and _PKG_ROOT not in _sys.path:
    _sys.path.insert(0, _PKG_ROOT)
_CORE = _os.path.join(_PKG_ROOT, "core")
if _os.path.isdir(_CORE) and _CORE not in _sys.path:
    _sys.path.insert(0, _CORE)

import cok_paths  # noqa: E402
import cok_store as _store  # noqa: E402   # 业务状态入库（配置/运行态/索引）
from cok_paths import resource as _res  # noqa: E402
from cok_paths import data_dir as _pkg_data_dir  # noqa: E402
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
import traceback
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

#: 渠道档案表(多渠道: 果盘 guopan / 小七 x7sy ...)。
#: 渠道本身是"配置 + 协议模块"的组合, 见 cok/core/cok_channels.py。
try:
    import cok_channels  # noqa: E402
except Exception as _chan_cfg_exc:  # noqa: BLE001
    cok_channels = None
    CHANNEL_IMPORT_ERROR += "\ncok_channels: %s" % _chan_cfg_exc

#: 平台层(SQLite: 用户/会话/邀请/审计/限流)。
#:
#: 为什么单独一个模块: 这些数据和"游戏账号"完全无关, 是**平台**自己的状态。
#: 早期它是 users.json / sessions.json 两个 JSON 文件 —— 两个人同时登录时
#: "读-改-写"没有锁, 后写的会把先写的整个覆盖掉(会话莫名其妙失效)。
#: 现在统一进 SQLite(WAL), 见 cok/core/cok_platform.py。
try:
    import cok_platform as platform  # noqa: E402
except Exception as _plat_exc:  # noqa: BLE001
    platform = None
    PLATFORM_IMPORT_ERROR = traceback.format_exc()
else:
    PLATFORM_IMPORT_ERROR = ""

#: 口令 hash / 会话 TTL 的唯一实现(cok_users)。
#: 平台层的用户表在 SQLite(见 cok_platform), 但**口令派生**仍复用这里 ——
#: 一套算法、一套参数(scrypt 优先, 没有就 PBKDF2), 不在两个地方各写一份,
#: 否则将来改强度时会漏掉一边。
try:
    import cok_users  # noqa: E402
except Exception:  # noqa: BLE001
    cok_users = None


TOKEN_FILE = os.path.join(_pkg_data_dir(), ".cok-web-token")
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
    # 后台轮询: 一次把"当前所有托管账号"都刷一遍。
    # ⚠️ 不能复用引擎级的 `refresh-now` —— 那个只作用于**当前查看**的那一个号,
    #    所以安卓后台守护/网页「全部刷新」看起来在跑, 实际只有 1 个号被轮询,
    #    其余后台账号永远停在旧数据上("后台运行不生效")。
    "refresh-all",
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


#: 资源文件的内存缓存(启动后读一次, 之后命中内存)。
#:
#: 为什么: `/` 和 `/login` 每次都要把 183KB 的 HTML 从磁盘读一遍 ——
#: 10 个人各开一个页面就是 10 次磁盘 IO + 10 次解析, 而文件内容在进程
#: 生命周期里根本不会变。缓存后每次只是内存切片。
#:
#: 但缓存内容会跟着文件 mtime 走: 改了 cok_webui.html 之后刷新页面,
#: 旧版会一直显示(看起来像"改了没生效"), 调前端时非常误导人。
#: 所以每次命中时多比一次 mtime(一次 stat, 纳秒级), 变了才重新读。
_RES_CACHE = {}
_RES_MTIME = {}

# /api/state 短 TTL 缓存(仅用于"读操作, 刚写过就别读旧"):
# 10 个用户每人每 5 秒一次 = 每秒 2 次完整序列化 + 视图引擎。
# 加 3 秒 TTL 内存缓存后, 命中时**不重建引擎/不序列化**, 只是 bytes 回放。
# 为什么是 3 秒: 轮询间隔 5 秒, 正好把用户级写操作后**一次**轮询吃掉,
# 数据延迟在轮询周期内, 业务层感知不到。 key = 用户 uid + 当前查看账号。
_STATE_CACHE = {}
_STATE_TTL = 6.0  # 秒 (> 前端 5s 轮询, 命中率高)


# 允许从磁盘读的前端资源白名单(路径穿越防护用)。
# ⚠ 只有列在这里的文件名能被 `_resource()` 取到 —— 直接拿 URL 里的
#   字符串去拼路径会让 `../../etc/passwd` 这类请求读到仓库外的文件。
_RES_FILES = ("cok_webui.html", "cok_admin.html", "cok_login.html")


def _resource(name):
    """把 URL 里的资源名解析成本地文件路径(不在白名单里 -> None)。"""
    name = str(name or "").strip().lstrip("/")
    if name not in _RES_FILES:
        return None
    path = _res(name)
    return path if os.path.exists(path) else None


def _login_required_page():
    """给「没有登录页的宿主」(安卓 App)用的提示页。

    为什么要单独一个: 这类宿主(WebView 内嵌控制台)压根没有登录页,
    被 403/跳 `/login` 的结果就是白屏 —— 用户只看到一片空白,
    既不知道发生了什么, 也没法自救。所以这里明确写清楚: 需要从控制台带令牌进入。
    """
    return """<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>COK 管理后台 · 需要访问令牌</title>
<style>
 body{margin:0;min-height:100vh;display:flex;align-items:center;
      justify-content:center;background:#0a0e16;color:#c9d1d9;
      font:15px/1.7 -apple-system,'PingFang SC','Microsoft YaHei',sans-serif}
 .box{max-width:420px;padding:26px 28px;border:1px solid #24304a;
      border-radius:14px;background:#111827}
 h1{margin:0 0 12px;font-size:17px;color:#ff8b8b}
 p{margin:6px 0;color:#9fb0c6}
 a{display:inline-block;margin-top:14px;padding:9px 16px;border-radius:9px;
   background:#2f6feb;color:#fff;text-decoration:none}
</style></head><body>
<div class="box">
  <h1>需要访问令牌</h1>
  <p>这个页面属于本机管理后台, 只有带着控制台令牌的请求能打开。</p>
  <p>请从控制台顶栏的「管理后台」进入, 令牌会一起带过去。</p>
  <p>如果一直卡在这里, 把应用完全退出再打开即可(令牌会重新生成)。</p>
  <a href="/">返回控制台</a>
</div></body></html>"""


def _resource_bytes(name):
    """读一个前端资源(带内存缓存, 文件改了会自动失效)。"""
    path = _res(name)
    try:
        mtime = os.path.getmtime(path)
    except OSError:
        return ("缺少 %s" % name).encode("utf-8")
    hit = _RES_CACHE.get(name)
    if hit is not None and _RES_MTIME.get(name) == mtime:
        return hit
    try:
        with open(path, "rb") as fh:
            data = fh.read()
    except OSError:
        return ("缺少 %s" % name).encode("utf-8")
    _RES_CACHE[name] = data
    _RES_MTIME[name] = mtime
    return data


def _scan_child_nice():
    """子进程里降 CPU 优先级(在 fork 之后、exec 之前跑)。

    为什么不用 ``nice`` 前缀: 命令数组会被日志直接打给用户看(``cmd`` 字段),
    加一层 ``nice`` 会让它变成用户看不懂的东西。preexec_fn 是"只影响这个
    子进程"的钩子, 语义更干净。

    ⚠️ 它只在 POSIX 有; Windows 没有 os.setpriority, 用 try 兜住。
    """
    try:
        os.nice(10)          # 默认 nice 0 -> 10, 大约让出 60% 的 CPU 时间
    except Exception:        # noqa: BLE001
        pass
    # 子进程最容易忽略 SIGPIPE(扫描中途被 kill 时), 明确恢复默认行为
    try:
        signal.signal(signal.SIGPIPE, signal.SIG_DFL)
    except Exception:        # noqa: BLE001
        pass



class PlatformManager(object):
    """多用户平台: 用户目录 -> 各自的 EngineManager。

    为什么要有这一层: `EngineManager` 的状态(并行集 / 查看指针 / 引擎表)
    全是**对象属性**。10 个人共用一个实例, 等于 10 个人共用一套"谁在跑、
    在看哪个号"的状态 —— A 点开后台运行, B 的账号列表里也会多一个;
    A 切到小号, B 那边也跟着跳。所以每个登录用户一个独立实例。

    生命周期: 登录时按需创建, 登出后**不立即销毁**(下一次登录大概率还是他,
    重建引擎要重新连游戏服, 代价大), 交给 `_sweep()` 按空闲时间回收。
    """

    #: 用户运行时空闲多久回收(秒)。30 分钟没动作 = 没人看, 引擎停掉省内存。
    IDLE_TTL = 30 * 60

    def __init__(self, args):
        self.args = args
        self.lock = threading.RLock()
        self.users = {}          # owner -> EngineManager
        self.seen = {}           # owner -> 最后一次活跃时间戳

    def get(self, owner, touch=True):
        """取(或建)某用户的运行时。owner 为空表示单用户模式。"""
        owner = str(owner or "")
        with self.lock:
            m = self.users.get(owner)
            if m is None:
                m = EngineManager(self.args, owner=owner or None)
                try:
                    m.start()
                except Exception:  # noqa: BLE001
                    pass
                self.users[owner] = m
            if touch:
                self.seen[owner] = time.time()
            return m

    def touch(self, owner):
        with self.lock:
            self.seen[str(owner or "")] = time.time()

    def drop(self, owner):
        """立刻停掉并移除某用户的运行时(封禁 / 删用户时用)。"""
        owner = str(owner or "")
        with self.lock:
            m = self.users.pop(owner, None)
            self.seen.pop(owner, None)
        if m is not None:
            try:
                m.stop_all()
            except Exception:  # noqa: BLE001
                pass
        return m is not None

    def sweep(self):
        """回收长时间没人用的运行时。返回被回收的 owner 列表。"""
        now = time.time()
        dead = []
        with self.lock:
            for owner, m in list(self.users.items()):
                if owner == "":          # 单用户/本地模式永不回收
                    continue
                # 本机管理员 = 宿主 App 自己(安卓端没有"别人"), 回收掉
                # 等于把 App 的后台运行全停了 —— 它永远不回收。
                if owner == LOCAL_ADMIN_UID:
                    continue
                if now - self.seen.get(owner, now) > self.IDLE_TTL:
                    dead.append((owner, m))
                    self.users.pop(owner, None)
                    self.seen.pop(owner, None)
        for _owner, m in dead:
            try:
                m.stop_all()
            except Exception:  # noqa: BLE001
                pass
        return [o for o, _m in dead]

    def stop_all(self):
        with self.lock:
            ms = list(self.users.values())
            self.users.clear()
            self.seen.clear()
        for m in ms:
            try:
                m.stop_all()
            except Exception:  # noqa: BLE001
                pass

    def view_engine(self):
        """单用户模式下的"当前查看引擎"(本地/安卓端沿用)。"""
        return self.get("").view_engine()

    # ------------------------------------------------ 管理员: 跨用户只读视图
    def preview(self, uid):
        """只登记不建引擎(给"用户存在但从没登录过"的情况摸底)。

        为什么不能直接 `get()`: `PlatformManager.get` 会 `start()` 一个新的
        EngineManager —— 它会把该用户所有"后台运行"的账号**全部拉起来**。
        管理员只是点了一下「账号状态」, 不该产生这种副作用, 所以这里建完
        不 start、也不塞进 `self.users`(免得下次真用户登录时拿到一个没跑
        起来的实例)。
        """
        uid = str(uid or "")
        with self.lock:
            m = self.users.get(uid)
            if m is not None:
                return m, False
        try:
            m = EngineManager(self.args, owner=uid or None)
        except Exception:  # noqa: BLE001
            return None, False
        return m, True


#: 管理员"全平台账号状态"快照缓存(不是 /api/state 那种大快照, 这里只有摘要)
_ADMIN_STATE_CACHE = {}
_ADMIN_STATE_TTL = 5.0


def _owner_of_account(acc):
    """账号 owner 字段 -> uid。

    绝大多数号存的就是 uid; 万一存成了用户名(早期数据/手工改过), 这里
    换成 uid —— 前端要靠它把号和用户对上, 显示成 "alice" 是没法定位的。
    """
    raw = str((acc or {}).get("owner") or "")
    if not raw:
        return ""
    row = platform.user_get_by_uid(raw) if platform is not None else None
    if row:
        return raw
    row = platform.user_get(raw) if platform is not None else None
    return row["uid"] if row else raw


def _account_row(acc, mgr, eng, server_now_ms):
    """把"账号库条目 + 运行时引擎"压成一行状态(只读内存, 不连游戏服)。"""
    key = str(acc.get("key") or "")
    row = {
        "key": key,
        "label": acc.get("label") or key,
        "role_name": acc.get("roleName") or "",
        "game_uid": acc.get("gameUid") or "",
        "added": acc.get("added") or "",
        "owner": _owner_of_account(acc),
        "running": False,
        "parallel": False,
        "priority": 2,
        # ⚠ 默认值不能是 "idle": 那是**有引擎但没在后台跑**的意思。没引擎、
        #   没数据的号(还没被任何人看过)应该是 "none"(未托管) —— 默认写成
        #   idle 会让管理页"空闲"筛选把一堆压根没跑过的号也算进去。
        "status": "none",
        "summary": None,
    }
    if mgr is not None:
        with mgr.lock:
            row["running"] = key in mgr.engines
            row["parallel"] = key in mgr.parallel
            row["priority"] = mgr.priorities.get(key, 2)
            eng = eng if eng is not None else mgr.engines.get(key)
    if eng is None:
        # ⚠ 引擎存在但取不到实例(被回收 / 快照里没带)和"压根没引擎"是
        #   两回事, 但在这一层分不清 —— 用 running 判: 在 engines 里就是
        #   已托管(空闲), 否则未托管。
        row["status"] = "idle" if row["running"] else "none"
        return row
    # 有引擎实例: 拿不到摘要(刚建、还没轮询)时按"在跑=ok / 没跑=idle"兜底,
    # 不能留默认值 —— 否则 status 会停在 "none", 明明是托管着的号却显示未托管。
    try:
        row["summary"] = eng._overview_summary()
    except Exception:  # noqa: BLE001
        row["summary"] = None
    s = row["summary"]
    if s:
        if s.get("error"):
            row["status"] = "error"
        elif s.get("disconnected"):
            row["status"] = "offline"
        elif not row["running"]:
            row["status"] = "idle"      # 有引擎(在看)但没在后台跑
        elif s.get("stale"):
            row["status"] = "stale"
        else:
            row["status"] = "ok"
    else:
        row["status"] = "idle" if row["running"] else "none"
    return row


def _admin_platform_overview(handler):
    """全平台概览(独立管理页 `/admin` 的 KPI 与账号表)。

    ⚠ 复用 `_admin_accounts_snapshot`: 页面上那张表和 KPI 必须**同一个口径**
      —— 各算各的迟早对不上("表里 6 行、卡片说 2 个在跑")。
      缓存(30s)也一并生效: 打开页面不会每个请求都重算一遍。
    """
    snap = _admin_accounts_snapshot(handler)
    accs = snap.get("accounts") or []
    users = snap.get("users") or []
    out = dict(snap)
    out.update({
        "running": len([r for r in accs if r.get("running")]),
        "hunting": len([r for r in accs
                        if (r.get("summary") or {}).get("hunting")]),
        "shielded": len([r for r in accs
                         if (r.get("summary") or {}).get("has_shield")]),
        "errors": len([r for r in accs if r.get("status") == "error"]),
        "offline": len([r for r in accs if r.get("status") == "offline"]),
        "stale": len([r for r in accs if r.get("status") == "stale"]),
        "orphan": len([r for r in accs if r.get("orphan")]),
        "users_total": len(users),
        "users_online": len([1 for u in users if u.get("online")]),
        "accounts_total": len(accs),
    })
    acc = dict(snap.get("accounting") or {})
    acc.setdefault("queued", 0)
    acc.setdefault("in_flight", 0)
    acc.setdefault("web_runs", 0)
    acc.setdefault("web_run_seconds", 0)
    acc.setdefault("max_in_flight", 0)
    acc.setdefault("running", out["running"])
    out["accounting"] = acc
    out["engines"] = len(snap.get("owners") or [])
    # 每个引擎的队列长度: 看的是"有没有积压", 不是绝对条数。
    queues = []
    try:
        pm = handler.platform
        with pm.lock:
            live = list((pm.users or {}).items())
        for uid, mgr in live:
            if mgr is None:
                continue
            try:
                with mgr.lock:
                    for eng in list(mgr.engines.values()):
                        q = getattr(eng, "queue", None)
                        snapfn = getattr(q, "snapshot", None)
                        n = len(snapfn()) if callable(snapfn) else (
                            len(q) if q is not None else 0)
                        if n:
                            queues.append(
                                {"uid": uid, "key": getattr(eng, "key", ""),
                                 "queued": n})
            except Exception:  # noqa: BLE001
                continue
    except Exception:  # noqa: BLE001
        queues = []
    out["queues"] = queues
    out["busy"] = [q["key"] for q in queues]
    out["queued"] = sum(q["queued"] for q in queues)
    out["server_time"] = time.time()
    out["python"] = sys.version.split()[0]
    try:
        from cok_accounts import DATA_ROOT as _dr
    except Exception:  # noqa: BLE001
        try:
            from accounts import DATA_ROOT as _dr  # type: ignore
        except Exception:  # noqa: BLE001
            _dr = ""
    out["data_root"] = _dr or ""
    # 入库情况：让管理员一眼看到"哪些数据在库里、哪些还只在文件里"。
    # 没有这个，迁移完没法确认是否真的生效（文件还在，看起来"没变"）。
    try:
        out["store"] = _store.status()
    except Exception:  # noqa: BLE001
        out["store"] = {}
    return out


def _admin_accounts_snapshot(handler, with_errors=False):
    """全平台账号状态快照(管理员专用)。

    只读: 每个号只取**内存里已有的**状态(`_overview_summary`), 不连游戏服、
    不读凭据 —— 管理页看的是"谁在跑、谁掉线、谁报错", 不是账号本身。

    为什么要缓存 5 秒: 管理页会自己轮询, 而每个号的摘要都要拿引擎锁;
    10 个号 × 每 2 秒一次 = 白烧 CPU。缓存让并发的管理页共享一次计算。
    """
    if platform is None:
        return {"ok": True, "platform": False, "users": [], "accounts": [],
                "stats": {}, "note": "单用户模式没有平台账号体系"}
    q = handler._query()
    try:
        limit = max(1, min(500, int((q.get("limit") or ["500"])[0] or 500)))
    except (TypeError, ValueError):
        limit = 500
    try:
        owner_filter = str((q.get("uid") or [""])[0] or "")
    except Exception:  # noqa: BLE001
        owner_filter = ""
    # 运行时装在 **Handler 上**(`Handler.platform`), 模块级 `platform` 只是
    # 模块本身 —— 拿模块判断"是不是平台模式"永远为真。
    if getattr(handler, "platform", None) is None:
        return {"ok": True, "platform": False, "users": [], "accounts": [],
                "stats": {}, "note": "单用户模式没有平台账号体系"}
    pm = handler.platform
    # 离线预览/演示会整个替换掉这个函数(见 preview_web.py), 那种情况下
    # `platform` 模块可能根本没导入 —— 直接 list_users() 会 NameError。
    if platform is None:
        return {"ok": True, "platform": False, "users": [], "accounts": [],
                "stats": {}, "note": "平台层未导入"}
    ck = (owner_filter, limit)
    hit = _ADMIN_STATE_CACHE.get(ck)
    if hit and time.time() - hit[0] < _ADMIN_STATE_TTL:
        return hit[1]
    users = []
    try:
        users = platform.list_users()
    except Exception:  # noqa: BLE001
        users = []
    # uid -> (用户行, EngineManager 或 None)
    _prep_errors = []      # preview() 阶段的错误(下面和读库错误合在一起返回)
    live = {}
    for u in users:
        uid = str(u.get("uid") or "")
        mgr = None
        try:
            with pm.lock:
                mgr = pm.users.get(uid)
        except Exception:  # noqa: BLE001
            mgr = None
        if mgr is None:
            # 从没登录过 / 已被空闲回收: 建一个**不启动**的只读实例,
            # 这样"装了 App 但从没打开"的用户也能看到他有几个号。
            try:
                mgr, _tmp = pm.preview(uid)
            except Exception as e:  # noqa: BLE001
                # ⚠ 这里**必须**兜住: preview() 只是"不启动", 但它内部要
                # 建 EngineManager / 读账号库, 任一步出错(账号库损坏、盘满)
                # 就会让整个接口 500 —— 管理员连"有哪些号"都看不到。
                # 退化成一个空管理器: 该用户的号仍然列出来, 只是全显示为
                # "没数据", 比整页崩了有用。
                mgr = _NULL_MANAGER
                # ⚠ `errors` 在下面才定义 —— 先 append 会 UnboundLocalError,
                #   把一个"某个用户预览失败"的小问题升级成整个接口 500。
                _prep_errors.append("准备 %s 的只读视图失败: %s" % (uid, e))
        live[uid] = (u, mgr)

    rows = []
    errors = list(_prep_errors)
    try:
        all_accounts = accounts.list_accounts()      # 不过滤 owner = 全平台
    except Exception as e:  # noqa: BLE001
        all_accounts, _err = [], str(e)
        errors.append("读取账号库失败: %s" % e)
    now_ms = 0
    for acc in all_accounts[:limit]:
        uid = _owner_of_account(acc)
        u, mgr = live.get(uid, (None, None))
        eng = None
        if mgr is not None:
            try:
                with mgr.lock:
                    eng = mgr.engines.get(str(acc.get("key") or ""))
            except Exception:  # noqa: BLE001
                eng = None
        if not now_ms:
            try:
                now_ms = int(time.time() * 1000)
            except Exception:  # noqa: BLE001
                now_ms = 0
        row = _account_row(acc, mgr, eng, now_ms)
        row["username"] = (u or {}).get("username") or ""
        row["user_banned"] = bool((u or {}).get("banned"))
        row["orphan"] = not uid or uid not in live
        rows.append(row)

    # `?uid=` 过滤: 放在**这里**而不是取账号时过滤 —— 统计要给的是"全平台"
    # 口径(账号总数/报错数都是全局才有意义), 只有返回的行按 uid 收窄。
    if owner_filter:
        rows = [r for r in rows if r.get("owner") == owner_filter]
    elif rows and all(not r.get("owner") for r in rows) \
            and Handler.local_admin_token:
        # 本机管理员宿主(安卓 App): 库里全是 owner 为空的老号 —— 上面按 uid
        # 过滤会把它们**全过滤掉**, 页面看起来像"账号库坏了"。
        # 一台设备一套库, 这些号就是本机管理员的, 直接认领并显示成他的。
        if _local_admin_claim_orphans():
            rows = [dict(r, owner=r.get("owner") or LOCAL_ADMIN_UID,
                         orphan=False) for r in rows]

    # 统计: 管理员最先想看的是"有几个号在跑 / 几个掉线 / 几个报错"
    st = {
        "users": len(users),
        "users_online": len([1 for _u, m in live.values()
                             if m is not None and getattr(m, "engines", None)]),
        "accounts": len(all_accounts),
        "shown": len(rows),
        "running": len([r for r in rows if r["running"]]),
        "parallel": len([r for r in rows if r["parallel"]]),
        "hunting": len([r for r in rows
                        if (r.get("summary") or {}).get("hunting")]),
        "shielded": len([r for r in rows
                         if (r.get("summary") or {}).get("has_shield")]),
        "errors": len([r for r in rows if r["status"] == "error"]),
        "offline": len([r for r in rows if r["status"] == "offline"]),
        "stale": len([r for r in rows if r["status"] == "stale"]),
        "orphan": len([r for r in rows if r["orphan"]]),
    }
    out = {"ok": True, "platform": True, "users": users, "accounts": rows,
           "stats": st, "generated": int(time.time())}
    if errors:
        out["errors"] = errors
    _ADMIN_STATE_CACHE[ck] = (time.time(), out)
    return out


def admin_account_action(handler, body):
    """管理员对**别人的账号**做的最小动作集(只开/关后台运行)。

    为什么只给这两个: 其余写操作(删号/切查看/改设置)都会**改写别人的
    数据或抢掉别人的连接** —— 管理员该做的是"看见并让卡住的号重新跑",
    不是"替人玩游戏"。停止=关后台并行(会真的停引擎), 启动=开并行。
    """
    user = handler._current_user()
    if user is None or user.get("role") != "admin":
        return {"ok": False, "error": "需要管理员权限"}
    if platform is None:
        return {"ok": False, "error": "平台层未启用"}
    body = body or {}
    key = str(body.get("key") or "").strip()
    on = bool(body.get("on"))
    # `uid` 是前端从表格行里带过来的(它已经知道这行属于谁); 只做**交叉校验**,
    # 不作为定位依据 —— 真正的归属永远从账号库读, 不信客户端。
    claimed = str(body.get("uid") or "").strip()
    if not key:
        return {"ok": False, "error": "缺少账号 key"}
    acc = accounts.get_account(key)
    if acc is None:
        return {"ok": False, "error": "账号库里没有这个账号: %s" % key}
    uid = _owner_of_account(acc)
    row = platform.user_get_by_uid(uid) if uid else None
    target = (row or {}).get("username") or "无主账号"
    if claimed and row and claimed != uid:
        return {"ok": False, "error": "账号归属对不上(页面数据可能过期, 刷新后再试)"}
    if row and row.get("banned"):
        return {"ok": False, "error": "该账号的主人已被封禁"}
    pm = getattr(handler, "platform", None)
    if pm is None:
        return {"ok": False, "error": "平台层未启用"}
    # 目标用户的运行时: 用真 get()(它可能会启动该用户的引擎 —— 这次是
    # **用户要求**让它跑, 所以启动是对的)。
    mgr = pm.get(uid)
    if mgr is None:
        return {"ok": False, "error": "拿不到该用户的运行时"}
    r = mgr.set_parallel(key, on)
    # 让两边管理页下一次拉到的都是新值
    try:
        _ADMIN_STATE_CACHE.clear()
        handler._invalidate_state_cache({"uid": uid})
    except Exception:  # noqa: BLE001
        pass
    handler._audit_action("admin-account-%s" % ("start" if on else "stop"),
                          key, bool(r.get("ok")),
                          ("账号属 %s" % target) if r.get("ok")
                          else str(r.get("error") or "")[:120])
    if not r.get("ok"):
        return r
    return {"ok": True, "on": bool(on), "key": key, "owner": target,
            "note": ("已让 %s 的账号「%s」在后台运行" % (target, key)) if on
                    else ("已停止 %s 的账号「%s」" % (target, key))}


class _NullLock(object):
    """给 _NullManager 用的空锁(支持 ``with``)。"""

    def __enter__(self):
        return self

    def __exit__(self, *_a):
        return False

    def acquire(self, *_a, **_k):
        return True

    def release(self):
        pass


class _NullManager(object):
    """"没有运行时"时的空管理器(平台层没实现 / 拿不到用户实例)。

    为什么要它: `_manager()` 的返回值在下游被直接 `.view_engine()` /
    `.accounts_overview()`, 返回 None 就会在半路炸成 AttributeError。
    空实现让"没有引擎"变成一句"没数据", 而不是一堆 traceback。
    """

    owner = ""
    view_key = ""
    engines = ()
    parallel = ()
    priorities = {}
    # ⚠ 下面这几个是**属性**而不是方法: 平台层的 EngineManager 里它们就是
    # 列表/字典, 下游(``_account_row`` / ``_admin_accounts_snapshot`` /
    # ``accounts_overview``)直接遍历, 写成方法会 ``TypeError: not iterable``。
    accounts = ()
    users = ()
    config = None
    has_pending = False
    pending = ()
    hunt_state = None
    hunter = None
    dock_runner = None
    # `_account_row()` 里 `with mgr.lock:` —— 空壳也给一把真锁,
    # 否则"没有运行时"会变成 AttributeError 而不是"没数据"。
    lock = _NullLock()

    def view_engine(self):
        return _NULL_ENGINE

    def engine_for(self, key=None):
        return _NULL_ENGINE

    def accounts_overview(self):
        return {"list": [], "active": "", "view": "", "parallel": [],
                "running": []}

    def state_dict(self, *_a, **_k):
        return {}

    def call(self, *_a, **_k):
        return None

    def resolve(self, *_a, **_k):
        return None

    def start(self):
        pass

    def stop_all(self):
        pass


class _NullEngine(object):
    """空引擎: 只回一个"什么都没连上"的快照。"""

    def snapshot(self):
        return {"connected": False, "online": False, "has_data": False,
                "error": "没有可用的运行时(平台层未初始化)",
                "accounts": {"list": []}, "states": {}, "queues": []}

    def __getattr__(self, name):
        # 任何没实现的调用都回空, 免得管理页一处没兜住就整页崩
        def _noop(*_a, **_kw):
            return {}
        return _noop


_NULL_ENGINE = _NullEngine()
_NULL_MANAGER = _NullManager()


class Handler(BaseHTTPRequestHandler):
    engine = None
    manager = None
    token = None
    #: 平台层: 非空 = 多用户模式(需要登录); None = 单用户/本地模式。
    platform = None
    #: 平台层会话 Cookie 名
    SESSION_COOKIE = "cok_sid"
    #: 「本机管理员」token(`--local-admin`)。非空时带它的请求跳过登录,
    #: 直接当 `LOCAL_ADMIN_UID` 这个账号看 —— 给没有登录页的宿主用
    #: (安卓 App 内嵌服务器)。**只在回环地址上认**, 外网访问一律走登录。
    local_admin_token = None
    server_version = "CokWeb/1.0"

    def log_message(self, fmt, *a):  # 静默默认访问日志
        pass

    def _query(self):
        q = self.path.split("?", 1)
        return parse_qs(q[1]) if len(q) > 1 else {}

    def _cookie(self, name):
        """从 Cookie 头里取一个值(不引第三方库)。"""
        raw = self.headers.get("Cookie") or ""
        for part in raw.split(";"):
            k, _, v = part.strip().partition("=")
            if k == name:
                return v.strip()
        return ""

    def _client_ip(self):
        """客户端 IP。

        ⚠ 反向代理(以后要上 HTTPS 就会用)下 `client_address` 全是 127.0.0.1,
        限流会全部算到代理身上 —— 所以优先读 `X-Forwarded-For` 的第一跳。
        """
        xff = self.headers.get("X-Forwarded-For") or ""
        if xff:
            return xff.split(",")[0].strip()[:64]
        try:
            return (self.client_address or [""])[0] or ""
        except Exception:  # noqa: BLE001
            return ""

    def _local_admin_ok(self):
        """这个请求是不是「本机管理员」(`--local-admin` 的 token)。

        ⚠ 只在**回环地址**上认: token 会出现在宿主的 URL / 请求头里, 一旦
        服务被 `--host 0.0.0.0` 暴露出去, 同样的 token 若还能用, 就等于给
        全网留了一个免密管理员。回环之外的请求即使 token 对也要求登录。
        """
        want = self.local_admin_token
        if not want:
            return False
        if self._client_ip() not in ("127.0.0.1", "::1", "localhost"):
            return False
        got = self.headers.get("X-Cok-Token") or ""
        if not got:
            q = self.path.split("?", 1)
            if len(q) > 1:
                for kv in q[1].split("&"):
                    if kv.startswith("t="):
                        got = kv[2:]
                        break
        return bool(got) and secrets.compare_digest(str(got), str(want))

    def _current_user(self):
        """当前登录用户 -> {uid, username, role, banned}; 未登录返回 None。

        平台关闭时(platform is None)返回一个"匿名本地用户"占位, 让所有
        下游的 owner 判定走同一条路径(空 owner = 单用户, 不隔离)。

        `--local-admin` 给了 token 就走**本机管理员**分支: 不查会话表、
        不需要登录, 直接返回平台库里 uid 为 `LOCAL_ADMIN_UID` 的那行。
        """
        if self.platform is None:
            return {"uid": "", "username": "", "role": "admin", "banned": False}
        if self._local_admin_ok():
            row = platform.user_get_by_uid(LOCAL_ADMIN_UID)
            if row is None:
                # 平台库被删/换成新库: 就地补一个, 免得宿主 App 直接不可用
                _local_admin_ensure(bootstrap=False)
                row = platform.user_get_by_uid(LOCAL_ADMIN_UID)
            if row is None:
                return None
            if row.get("banned"):
                return {"uid": LOCAL_ADMIN_UID, "username": row["username"],
                        "role": row.get("role") or "admin", "banned": True}
            return {"uid": LOCAL_ADMIN_UID, "username": row["username"],
                    "role": row.get("role") or "admin", "banned": False}
        sid = self._cookie(self.SESSION_COOKIE)
        if not sid:
            # 兼容: 也接受 X-Cok-Sid 头(脚本/curl 用), 但**不**接受 ?t= 里的 sid
            sid = self.headers.get("X-Cok-Sid") or ""
        if not sid or platform is None:
            return None
        uid = platform.session_user(sid)
        if not uid:
            return None
        row = platform.user_get_by_uid(uid)
        if not row:
            return None
        if row.get("banned"):
            return {"uid": uid, "username": row["username"],
                    "role": row.get("role") or "user", "banned": True}
        return {"uid": uid, "username": row["username"],
                "role": row.get("role") or "user", "banned": False}

    def _require_user(self):
        """要登录; 已登录返回 user dict, 否则回 None(并已写好响应)。"""
        user = self._current_user()
        if user is not None and user.get("banned"):
            self._send(403, {"error": "banned", "note": "账号已被禁用"})
            return None
        return user

    def _manager(self):
        """当前请求该用的 EngineManager(按登录用户分区)。

        ⚠ 平台模式下 `platform.get()` 可能返回 None(假平台层 / 未实现的
        平台实现) —— 调用方大多直接 `m.view_engine()`, 拿到 None 就是一
        串 AttributeError, 表现为"页面转圈 + 服务端一堆 traceback"。
        这里兜一个空动作管理器, 让所有下游走同一条安全路径。
        """
        user = self._current_user() or {}
        if self.platform is None:
            return self.manager or _NULL_MANAGER
        # 本机管理员(`--local-admin`): 他的运行时必须**保持存活**。
        # `PlatformManager.sweep()` 会跳过这个 owner, 所以正常不会被回收;
        # 但 `stop_all()`(退出时)之后 `_manager()` 仍会重建 —— 那是对的,
        # 进程还在就该能用。
        m = self.platform.get(user.get("uid") or "")
        return m if m is not None else _NULL_MANAGER

    def _eng(self):
        """按 ?account=<key> 路由到对应引擎; 没给就用当前查看引擎。

        没有管理器(理论上不会)时退回旧的单引擎 Handler.engine。
        """
        m = self._manager()
        if m is None:
            return self.engine
        key = (self._query().get("account") or [None])[0]
        return m.engine_for(key)

    def _auth(self):
        """鉴权: 平台模式看会话, 单用户模式看 token。

        两种模式都保留, 是为了不破坏现有部署(本地控制台 / 安卓端内嵌服务器
        都没有登录页, 用 `?t=<token>` 仍然对)。

        `--local-admin` 的 token 优先: 宿主 App 没有登录页, 这是它在平台模式
        下唯一的入口。它在**单用户模式**下也认 —— 安卓端以前就是单用户模式,
        万一 `--platform` 没生效, 页面不至于一起 403。
        """
        if self._local_admin_ok():
            # 记活跃时间(内存, 不写库 —— 每个请求都写 SQLite 太浪费)
            try:
                self.platform.touch(LOCAL_ADMIN_UID)
            except Exception:  # noqa: BLE001
                pass
            return True
        if self.platform is not None:
            user = self._current_user()
            if user is None:
                return False
            if user.get("banned"):
                return False
            # 顺手记一下活跃时间(空闲回收靠它)
            try:
                self.platform.touch(user.get("uid") or "")
            except Exception:  # noqa: BLE001
                pass
            return True
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
        # 独立管理页面: 和主控制台完全分开(不共用 DOM/CSS/JS),
        # 未登录 -> 登录页; 非管理员 -> 403(不进页面, 避免"打开空白"的错觉)。
        if path in ("/admin", "/admin.html", "/admin/"):
            if not self._auth():
                if self.platform is not None:
                    # ⚠ 宿主 App(安卓)没有登录页: 给它登录页 = 白屏死路。
                    #   这里带 `?t=<token>` 但 token 不对时也要给个**能看懂的
                    #   文字页**, 否则 WebView 里就是一片空白 —— 连"发生了什么"
                    #   都看不出来, 用户只能反复重启 App。
                    if self._client_ip() in ("127.0.0.1", "::1", "localhost"):
                        self._send(200, _login_required_page(),
                                   "text/html; charset=utf-8")
                    else:
                        self._send(200, _resource_bytes("cok_login.html"),
                                   "text/html; charset=utf-8")
                else:
                    self._send(403, "无效 token, 请用 ?t=<token> 访问")
                return
            if self.platform is None:
                self._send(404, "单用户模式没有管理后台")
                return
            u = self._current_user() or {}
            if u.get("role") != "admin":
                self._send(403, "需要管理员权限")
                return
            self._send(200, _resource_bytes("cok_admin.html"),
                       "text/html; charset=utf-8")
            return
        if platform is not None and path in ("/login", "/login.html"):
            if self._auth():
                self.send_response(302)
                self.send_header("Location", "/")
                self.end_headers()
                return
            self._send(200, _resource_bytes("cok_login.html"),
                       "text/html; charset=utf-8")
            return
        if path in ("/", "/index.html"):
            if not self._auth():
                if self.platform is not None:
                    # 未登录: 直接给登录页(比 403 友好 —— 浏览器地址栏就能登)
                    self._send(200, _resource_bytes("cok_login.html"),
                               "text/html; charset=utf-8")
                else:
                    self._send(403, "无效 token, 请用 ?t=<token> 访问")
                return
            self._send(200, _resource_bytes("cok_webui.html"),
                       "text/html; charset=utf-8")
            return
        if path == "/api/me":
            # 谁登录了 + 他能看到几个账号。前端启动时用它判断要不要显示登录页。
            user = self._current_user()
            if user is None or user.get("banned"):
                self._send(403, {"error": "unauthorized"})
                return
            m = self._manager()
            try:
                mine = accounts.list_accounts(owner=(user.get("uid") or None)
                                              if self.platform is not None else None)
            except Exception:  # noqa: BLE001
                mine = []
            row = platform.user_get_by_uid(user.get("uid") or "") if platform else None
            self._send(200, {"ok": True, "user": user["username"],
                             "role": user.get("role") or "user",
                             "uid": user.get("uid") or "",
                             "platform": self.platform is not None,
                             "accounts": len(mine),
                             # 本机管理员(`--local-admin`): 前端靠它把「退出登录」
                             # 藏掉 —— 这个身份没有会话, 退出只会把人踢到登录页。
                             "local_admin": bool(self._local_admin_ok()),
                             # 初始随机密码没改过 -> 前端提示去改
                             "must_change_pwd": bool(row and row.get("must_change_pwd")),
                             "idle": (m is not None and not m.engines)})
            return
        if path == "/api/state":
            if not self._auth():
                self._send(403, {"error": "unauthorized"})
                return
            m = self._manager()
            key = (getattr(m, "owner", "") or "") + "|" + (getattr(m, "view_key", "") or "")
            now = time.time()
            hit = _STATE_CACHE.get(key)
            if hit and now - hit[0] < _STATE_TTL:
                self._send(200, hit[1])
                return
            snap = m.view_engine().snapshot()
            # 用管理器的账号视图覆盖单引擎的(带 running / parallel 标记;
            # 平台模式下**只有自己名下的账号**)
            try:
                snap["accounts"] = m.accounts_overview()
            except Exception:  # noqa: BLE001
                pass
            _STATE_CACHE[key] = (now, snap)
            self._send(200, snap)
            return
        if path == "/api/overview":
            # 轻量总览: 只要"有哪些号 / 谁在跑 / 谁有罩"。
            #
            # 为什么要单独一个接口: `/api/state` 里塞了地图索引、技能表、
            # 联盟、码头、天空岛等几十个模块的状态, 序列化一次是 **几百 KB**
            # (单账号 180~200KB)。10 个人每人每 5 秒刷一次 = 每秒 400KB,
            # 而其中 90% 的字段这一屏根本用不到。
            # ⇒ 首页轮询走这个轻接口, 详情按需拉 `/api/state`。
            if not self._auth():
                self._send(403, {"error": "unauthorized"})
                return
            m = self._manager()
            out = {"ok": True, "accounts": []}
            try:
                out["accounts"] = m.accounts_overview()
            except Exception:  # noqa: BLE001
                pass
            self._send(200, out)
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
        if path == "/api/audit":
            # 审计日志(仅管理员)
            user = self._current_user()
            if user is None or user.get("role") != "admin":
                self._send(403, {"error": "forbidden"})
                return
            if platform is None:
                self._send(200, {"ok": True, "rows": []})
                return
            uid = (self._query().get("uid") or [None])[0]
            limit = int((self._query().get("limit") or ["100"])[0] or 100)
            self._send(200, {"ok": True,
                             "rows": platform.recent_audit(uid=uid, limit=limit)})
            return
        if path == "/api/admin/users":
            # 用户管理(仅管理员)
            user = self._current_user()
            if user is None or user.get("role") != "admin":
                self._send(403, {"error": "forbidden"})
                return
            if platform is None:
                self._send(200, {"ok": True, "users": []})
                return
            self._send(200, {"ok": True, "users": platform.list_users()})
            return
        if path == "/api/admin/accounts":
            # 全平台账号状态(仅管理员)。
            #
            # 为什么要单独一个接口, 而不是让管理员"切换用户"去看:
            # 账号是按 owner uid 分区的, 管理员的 EngineManager 只装得下自己
            # 名下的号 —— 别人的号在跑没跑、罩还剩多久、打怪有没有报错,
            # 在他自己的 /api/overview 里**根本不存在**。出故障时最需要看的
            # 恰恰是"别人的号怎么了", 所以这个缺口必须在这一层补。
            #
            # 只读: 不触发任何游戏服请求, 不看别人的凭据 —— 每个号只输出
            # 运行状态摘要(和 /api/overview 里字段同源), 不含 openid/token。
            user = self._current_user()
            if user is None or user.get("role") != "admin":
                self._send(403, {"error": "forbidden"})
                return
            self._send(200, _admin_accounts_snapshot(self))
            return
        if path == "/api/admin/overview":
            user = self._current_user()
            if user is None or user.get("role") != "admin":
                self._send(403, {"error": "forbidden"})
                return
            self._send(200, _admin_platform_overview(self))
            return
        if path == "/api/admin/invites":
            # 邀请码管理(仅管理员)
            user = self._current_user()
            if user is None or user.get("role") != "admin":
                self._send(403, {"error": "forbidden"})
                return
            if platform is None:
                self._send(200, {"ok": True, "invites": []})
                return
            self._send(200, {"ok": True, "invites": platform.invites_list()})
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

    def _read_body(self):
        n = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(n) if n else b"{}"
        try:
            body = json.loads(raw.decode("utf-8"))
        except Exception:
            body = {}
        return body if isinstance(body, dict) else {}

    def _send_cookie(self, sid, ttl):
        self.send_response(200)
        # HttpOnly: 前端 JS 读不到(降低 XSS 危害); SameSite=Lax: 跨站 POST 不带 Cookie
        self.send_header("Set-Cookie",
                         "%s=%s; Path=/; Max-Age=%d; HttpOnly; SameSite=Lax"
                         % (self.SESSION_COOKIE, sid, int(ttl)))
        body = b'{"ok":true}'
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        try:
            self.wfile.write(body)
        except (BrokenPipeError, ConnectionResetError):
            pass

    def _clear_cookie(self):
        self.send_response(200)
        self.send_header("Set-Cookie",
                         "%s=; Path=/; Max-Age=0; HttpOnly; SameSite=Lax"
                         % self.SESSION_COOKIE)
        body = b'{"ok":true}'
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        try:
            self.wfile.write(body)
        except (BrokenPipeError, ConnectionResetError):
            pass

    def _invalidate_state_cache(self, user):
        """写操作后把该用户的 state 缓存清掉。"""
        if self.platform is None:
            return
        uid = (user or {}).get("uid") or ""
        prefix = str(uid) + "|"
        for k in list(_STATE_CACHE.keys()):
            if k == "" or k.startswith(prefix):
                try:
                    del _STATE_CACHE[k]
                except KeyError:
                    pass

    def _audit_action(self, action, target, ok, detail=""):
        """记一条审计(平台模式下)。单用户模式是 no-op。"""
        if platform is None:
            return
        user = self._current_user() or {}
        try:
            platform.audit(user.get("uid") or "", action, target, ok,
                           detail, self._client_ip())
        except Exception:  # noqa: BLE001
            pass

    def do_POST(self):  # noqa: N802
        path = self.path.split("?", 1)[0]

        # ---- 改密码(任何登录用户) ----
        if path == "/api/password":
            # 改自己的密码(任何登录用户)
            user = self._current_user()
            if user is None:
                self._send(403, {"ok": False, "error": "unauthorized"})
                return
            if platform is None:
                self._send(404, {"ok": False, "error": "not found"})
                return
            body = self._read_body()
            old_pw = str(body.get("old") or "")
            new_pw = str(body.get("new") or "")
            if len(new_pw) < 6:
                self._send(400, {"ok": False, "error": "新密码至少 6 位"})
                return
            row = platform.user_get(user.get("username") or "")
            if not row or not cok_users.verify_password(old_pw, row["pwd"],
                                                        row["salt"]):
                self._audit_action("password", "", False, "原密码不正确")
                self._send(401, {"ok": False, "error": "原密码不正确"})
                return
            pwd, salt = cok_users.hash_password(new_pw)
            platform.user_set_password(row["username"], pwd, salt)
            try:
                platform.conn().execute(
                    "UPDATE users SET must_change_pwd=0 WHERE username=?",
                    (row["username"],))
                platform.conn().commit()
            except Exception:  # noqa: BLE001
                pass
            self._audit_action("password", row["username"], True)
            self._send(200, {"ok": True})
            return

        if path.startswith("/api/admin/"):
            body = self._read_body()
            self._handle_admin(path, body)
            return

        # ---- 平台层入口(不需要登录) ----
        if path in ("/api/login", "/api/register", "/api/logout"):
            if self.platform is None:
                self._send(404, {"error": "not found"})
                return
            body = self._read_body()
            if path == "/api/logout":
                sid = self._cookie(self.SESSION_COOKIE)
                uid = ""
                if sid:
                    try:
                        uid = platform.session_user(sid, touch=False)
                    except Exception:  # noqa: BLE001
                        uid = ""
                    try:
                        platform.session_drop(sid)
                    except Exception:  # noqa: BLE001
                        pass
                self._audit_action("logout", "", True)
                self._clear_cookie()
                return
            self._handle_auth(path, body)
            return

        if not self._auth():
            self._send(403, {"error": "unauthorized"})
            return
        if path in ("/api/scan/start", "/api/scan/stop", "/api/scan/history"):
            body = self._read_body()
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
        body = self._read_body()
        # 账号级操作交给管理器(影响注册表 / 运行集), 其余路由到对应引擎。
        act = (body or {}).get("action")
        if act in MANAGER_ACTIONS:
            self._send(200, self._manager_action(act, body))
            return
        r = self._eng().action(body)
        # 任何写动作(set-setting 等)都让该用户的 state 缓存失效
        if isinstance(r, dict) and r.get("ok"):
            self._invalidate_state_cache(self._current_user() or {})
        self._send(200, r)

    # ---------------------------------------------------------------- 管理(admin only)
    def _handle_admin(self, path, body):
        """管理员操作: 封禁/解封用户、改角色、删除用户、生成邀请码。"""
        user = self._current_user()
        if user is None or user.get("role") != "admin":
            self._send(403, {"ok": False, "error": "需要管理员权限"})
            return
        if platform is None:
            self._send(404, {"ok": False, "error": "平台层未启用"})
            return
        if path == "/api/admin/account-action":
            # 管理侧账号动作。放在最前面 —— 下面那个 `if not target` 是给
            # **用户管理**(ban/role/delete/invite)用的, 这个接口没有 username。
            body = body or {}
            self._send(200, admin_account_action(self, body))
            return
        if path in ("/api/admin/store-status", "/api/admin/store-import"):
            # 入库状态 / 一次性迁移：管理页上"数据入库"那一块用它。
            # 没有这个，"迁移完了没"只能靠猜（文件还在，看着像没变）。
            if path.endswith("store-import"):
                out = _store.import_files(log=None)
                self._audit_action("store-import", "", True,
                                   "导入 %d 项" % sum(
                                       v for v in out.values()
                                       if isinstance(v, int)))
                self._send(200, {"ok": True, "imported": out,
                                 "status": _store.status()})
            else:
                self._send(200, {"ok": True, "status": _store.status()})
            return
        target = str(body.get("username") or "").strip()
        if not target:
            self._send(400, {"ok": False, "error": "缺少 username"})
            return

        if path == "/api/admin/ban":
            banned = bool(body.get("banned"))
            # 不能封禁自己
            if target == user.get("username"):
                self._send(400, {"ok": False, "error": "不能封禁自己"})
                return
            ok = platform.user_set_banned(target, banned)
            if ok:
                self._audit_action("admin-ban" if banned else "admin-unban",
                                   target, True)
                # 封禁时踢掉该用户的所有会话
                if banned:
                    platform.session_drop_user(
                        (platform.user_get(target) or {}).get("uid", ""))
            self._send(200, {"ok": ok, "banned": banned})
            return

        if path == "/api/admin/role":
            role = str(body.get("role") or "").strip()
            if role not in ("user", "admin"):
                self._send(400, {"ok": False, "error": "role 必须是 user 或 admin"})
                return
            if target == user.get("username"):
                self._send(400, {"ok": False, "error": "不能改自己的角色"})
                return
            ok = platform.user_set_role(target, role)
            if ok:
                self._audit_action("admin-role", target, True, role)
            self._send(200, {"ok": ok, "role": role})
            return

        if path == "/api/admin/delete-user":
            if target == user.get("username"):
                self._send(400, {"ok": False, "error": "不能删除自己"})
                return
            ok = platform.user_delete(target)
            if ok:
                self._audit_action("admin-delete", target, True)
            self._send(200, {"ok": ok})
            return

        if path == "/api/admin/invite-new":
            code = platform.invite_new(target or user.get("username", ""))
            if code:
                self._audit_action("admin-invite", code, True, target)
            self._send(200, {"ok": bool(code), "code": code})
            return

        self._send(404, {"ok": False, "error": "not found"})

    # ---------------------------------------------------------------- 登录/注册
    def _handle_auth(self, path, body):
        """登录 / 注册。成功后下发会话 Cookie(不是把凭据塞 URL)。

        为什么不用 URL token: 它会进浏览器历史、Referer 头和访问日志 ——
        等于把长期有效的凭据写在日志里。
        """
        username = str(body.get("username") or "").strip()
        password = str(body.get("password") or "")
        ip = self._client_ip()
        bucket = "auth:%s" % ip
        ok, retry = platform.rate_hit(bucket, 20, 60)
        if not ok:
            self._send(429, {"ok": False,
                             "error": "尝试过于频繁, 请 %d 秒后再试" % retry})
            return
        if not username or not password:
            self._send(400, {"ok": False, "error": "请输入用户名和密码"})
            return
        if path == "/api/register":
            self._do_register(username, password, str(body.get("invite") or ""), ip)
            return
        self._do_login(username, password, ip)

    def _do_login(self, username, password, ip):
        row = platform.user_get(username)
        if not row:
            # 用户不存在: 不暴露"这个用户名存在与否"(防用户名枚举)
            self._audit_action("login", "", False, "用户不存在")
            self._send(401, {"ok": False, "error": "用户名或密码不正确"})
            return
        if row.get("banned"):
            # 先判断封禁再验密码 —— 否则被封禁用户能靠"密码对不对"推断
            # 自己的账号状态(安全上叫 oracle 攻击)
            self._audit_action("login", username, False, "账号已被禁用")
            self._send(403, {"ok": False, "error": "账号已被禁用, 请联系管理员"})
            return
        if not cok_users.verify_password(password, row["pwd"], row["salt"]):
            # 失败也记审计 —— 有人在试弱口令时, 时间线上能看出来
            self._audit_action("login", username, False, "密码不正确")
            # 不暴露"用户名是否存在"(防用户名枚举): 统一回"用户名或密码不正确"
            self._send(401, {"ok": False, "error": "用户名或密码不正确"})
            return
        sid = platform.new_sid()
        platform.session_save(sid, row["uid"], cok_users.SESSION_TTL, ip=ip,
                              ua=(self.headers.get("User-Agent") or "")[:200])
        platform.user_touch_login(username)
        platform.rate_reset("auth:%s" % ip)
        self._audit_action("login", "", True)
        self._send_cookie(sid, cok_users.SESSION_TTL)

    def _do_register(self, username, password, invite, ip):
        # 首个用户自动成为 admin 且免邀请码 —— 不然部署完没人能登进去。
        first = (platform.user_count() == 0)
        if not first:
            if not invite:
                self._send(400, {"ok": False, "error": "注册需要邀请码"})
                return
            ok, msg = platform.invite_consume(invite, username)
            if not ok:
                self._audit_action("register", username, False, msg)
                self._send(403, {"ok": False, "error": msg})
                return
        # 平台模式下**用户表就是 SQLite**: 口令派生复用 cok_users 的算法,
        # 但记录只写一处(以前先写 users.json 再同步过来, 等于两个真相)。
        if cok_users is None:
            self._send(500, {"ok": False, "error": "口令模块未加载"})
            return
        ok, msg = _platform_register_user(username, password,
                                          role="admin" if first else "user")
        if not ok:
            self._send(400, {"ok": False, "error": msg})
            return
        self._audit_action("register", username, True,
                           "首个用户(自动管理员)" if first else "邀请码注册")
        self._do_login(username, password, ip)

    def _manager_action(self, act, body):
        m = self._manager()
        key = str((body or {}).get("key") or "").strip()
        # 账号级写操作清掉该用户的 state 缓存(下次请求重算最新)
        self._invalidate_state_cache(self._current_user() or {})
        if act == "account-switch":
            return m.set_view(key)
        if act == "account-parallel":
            return m.set_parallel(key, bool((body or {}).get("on")))
        if act == "account-priority":
            return m.set_priority(key, (body or {}).get("priority"))
        if act == "account-parallel-batch":
            return m.set_parallel_batch((body or {}).get("keys"), bool((body or {}).get("on")))
        if act == "refresh-all":
            keys = (body or {}).get("keys")
            return m.refresh_all(keys if isinstance(keys, list) else None)
        if act == "account-remove":
            r = m.remove_account(key)
            self._audit_action("account-remove", key, bool(r.get("ok")),
                               str(r.get("error") or ""))
            return r
        if act == "account-add-device":
            # 入库仍走引擎(要读设备), 完成后按需拉起/刷新运行集
            r = m.view_engine()._account_add_device(body)
            if r.get("ok") and r.get("key"):
                with m.lock:
                    m._ensure(m.view_key)
                self._audit_action("account-add-device", str(r.get("key")), True)
            else:
                self._audit_action("account-add-device", "",
                                   False, str(r.get("error") or "")[:160])
            return r
        if act == "account-relabel":
            r = m.view_engine()._account_relabel(body)
            self._audit_action("account-relabel", key, bool(r.get("ok")))
            return r
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


def _now():
    return time.time()


#: 「本机管理员」在平台库里的固定 uid(`--local-admin` 用)。
#:
#: 为什么是**固定值**而不是随机生成: 安卓 App 的内嵌服务器每次启动都要
#: 找到同一个人 —— 账号库里的 owner 字段记的就是这个 uid。随机的话每次
#: 启动都换一个人, 上次的号全部变成"无主账号", 列表会突然空掉。
#: 它同时也是 owner 值, 不会和真用户名冲突(真用户是 u-<hex>)。
LOCAL_ADMIN_UID = "local-admin"

#: 本机管理员的用户名(平台库里也建一行, 这样审计/用户表/管理页都看得到)。
LOCAL_ADMIN_NAME = "本机管理员"


def _local_admin_ensure(bootstrap=True):
    """确保平台库里存在「本机管理员」这一行。返回用户行或 None。

    为什么要有它: 平台模式的 `/api/me`、账号过滤、管理页全都按
    `platform.user_get_by_uid()` 走。宿主(安卓 App)不带登录页, 但如果
    库里没有这个 uid, 所有分支都会当成"查无此人"→ 页面 403 → 白屏。

    口令是**随机丢弃**的: 本机管理员只能从回环 + token 进入, 给它设一个
    能登录的口令等于多开一扇门。`must_change_pwd` 不置位(没人会去改)。
    """
    if platform is None:
        return None
    row = platform.user_get_by_uid(LOCAL_ADMIN_UID)
    if row is not None:
        return row
    pwd, salt = cok_users.hash_password(secrets.token_urlsafe(24))
    ok = platform.user_add(LOCAL_ADMIN_NAME, LOCAL_ADMIN_UID, pwd, salt,
                           role="admin")
    if not ok:
        # 可能已被别人用同名占用 / 库被换成只读的 —— 再读一次, 有就认
        return platform.user_get_by_uid(LOCAL_ADMIN_UID)
    row = platform.user_get_by_uid(LOCAL_ADMIN_UID)
    if row is not None and bootstrap:
        try:
            platform.audit(LOCAL_ADMIN_UID, "local-admin", LOCAL_ADMIN_NAME,
                           True, "本机管理员(免登录)", "127.0.0.1")
        except Exception:  # noqa: BLE001
            pass
    return row


def _local_admin_claim_orphans():
    """把「无主账号」挂到本机管理员名下。返回认领个数。

    为什么需要: 安卓端以前是**单用户模式**, 账号库里所有号的 owner 是空串。
    切到平台模式后 `list_accounts(owner=uid)` 会把它们全过滤掉 ——
    表现是"App 里明明有 5 个号, 管理页和账号列表突然空了"。

    ⚠ 只有**开了 `--local-admin` 的宿主**(安卓 App 那种一台设备一套库)才调。
    服务器上绝不调: 那里的空 owner 可能是"还没认领给某个用户的号",
    挂到本机管理员名下等于替部署者做了归属决定。

    ⚠ 判定条件是 `Handler.local_admin_token` 而**不是** `platform is not None`:
    服务器上 `platform` 也非空(平台模式常驻), 只看它会让"认领"在服务器上照跑 ——
    那正是本函数最不该发生的地方(把用户的号塞进一个死账号名下)。
    """
    if platform is None or not Handler.local_admin_token:
        return 0
    n = 0
    try:
        lst = accounts.list_accounts()
    except Exception:  # noqa: BLE001
        return 0
    for acc in lst:
        if str(acc.get("owner") or ""):
            continue
        key = acc.get("key")
        try:
            full = accounts.get_account(key) or {}
            full["owner"] = LOCAL_ADMIN_UID
            accounts.save_account(full, owner=LOCAL_ADMIN_UID)
            n += 1
        except Exception:  # noqa: BLE001
            pass
    return n


def _platform_register_user(username, password, role="user"):
    """在平台库里建一个用户。返回 (ok, msg)。

    口令校验规则集中在 `cok_users.register` 里(长度/字符集), 这里直接复用
    它的**校验**, 但**不写它的文件** —— 见 `platform.user_add` 的说明。
    """
    username = (username or "").strip()
    if not cok_users._USER_RE.match(username):
        return False, "用户名只允许 2-32 位字母数字 _ . -"
    if len(password or "") < 6:
        return False, "密码至少 6 位"
    if platform.user_get(username):
        return False, "用户名已存在"
    pwd, salt = cok_users.hash_password(password)
    uid = "u-" + secrets.token_hex(8)
    if not platform.user_add(username, uid, pwd, salt, role=role):
        return False, "写入用户失败(用户名可能已存在)"
    return True, "注册成功"


def _now():
    return time.time()


def _migrate_users():
    """把旧的 ``users.json`` / ``sessions.json`` 迁进 SQLite, 返回统计 dict。

    为什么要有这一步: 平台模式之前的版本把用户存在 JSON 文件里, 两边各有一份
    就是"两个真相"。迁移**不删原文件**(改名成 ``*.migrated`` 留个后路),
    所以做错了还能退回去。

    幂等: 已经迁过的用户按 **uid** 认出来就跳过, 再跑一次不会重复写。
    """
    import time as _t
    stats = {"users": 0, "sessions": 0, "skipped": 0, "errors": 0}
    raw = cok_users._load(cok_users.USERS_FILE, {}) or {}
    if not isinstance(raw, dict):
        print("  users.json 格式不对(不是对象), 跳过")
        return stats
    for username, rec in raw.items():
        if not isinstance(rec, dict):
            continue
        # 老格式没有 uid —— 用 "u-" + 用户名做稳定 id, 这样**重复迁移**时
        # 还能认出是同一个人(否则每次跑都当成新用户)。
        uid = str(rec.get("uid") or "").strip() or ("u-" + str(username))
        old = platform.user_get_by_uid(uid) or platform.user_get(username)
        if old:
            stats["skipped"] += 1
            continue
        created = rec.get("created") or ""
        ts = 0.0
        if isinstance(created, str) and created:
            try:
                ts = _t.mktime(_t.strptime(created[:19], "%Y-%m-%dT%H:%M:%S"))
            except (ValueError, OverflowError):
                ts = 0.0
        ok = platform.user_upsert(username, uid,
                                  rec.get("pwd") or "", rec.get("salt") or "",
                                  role=(rec.get("role") or "user"),
                                  created=ts or 0.0)
        if ok:
            stats["users"] += 1
        else:
            stats["errors"] += 1
    # 会话: sid 直接进库(库里存 sha256, 见 session_save)
    sess = cok_users._load(cok_users.SESSIONS_FILE, {}) or {}
    if isinstance(sess, dict):
        for sid, rec in sess.items():
            if not isinstance(rec, dict):
                continue
            row = platform.user_get(str(rec.get("user") or ""))
            if not row:
                continue
            exp = float(rec.get("exp") or 0)
            platform.session_save(str(sid), row["uid"],
                                  max(1.0, exp - _now()), ip="")
            stats["sessions"] += 1
    if stats["users"] or stats["sessions"]:
        try:
            os.replace(cok_users.USERS_FILE, cok_users.USERS_FILE + ".migrated")
            if os.path.exists(cok_users.SESSIONS_FILE):
                os.replace(cok_users.SESSIONS_FILE,
                           cok_users.SESSIONS_FILE + ".migrated")
        except OSError as e:
            print("  [!] 旧文件改名失败(不影响新库): %s" % e)
    return stats


def _migrate_accounts(owner_name):
    """给"还没有主人"的账号认领归属, 返回统计 dict。

    为什么要认领: 平台模式的账号过滤是按 ``owner == uid`` 做的。改造前导入的
    号 ``owner`` 是空的 —— 平台模式下**一个都看不见**, 表现是"我明明有号,
    登录后列表是空的"。这一步把无主号挂到指定用户名下。

    ``owner_name`` 可以是用户名或 uid; 找不到就**什么都不做**并提示, 绝不瞎猜
    一个归属(把号塞给错的人比空列表更糟)。
    """
    st = {"claimed": 0, "already": 0, "list": []}
    row = platform.user_get(owner_name) or platform.user_get_by_uid(owner_name)
    if not row:
        print("  [!] 找不到用户: %s (先注册/迁移用户再认领)" % owner_name)
        return st
    owner = row["uid"]
    for acc in accounts.list_accounts():
        k = acc.get("key")
        if (acc.get("owner") or ""):
            st["already"] += 1
            continue
        try:
            full = accounts.get_account(k) or {}
            full["owner"] = owner
            accounts.save_account(full, owner=owner)
            st["claimed"] += 1
            st["list"].append(k)
        except Exception as e:  # noqa: BLE001
            print("  [!] 认领失败 %s: %s" % (k, e))
    return st


def _platform_bootstrap(args):
    """平台模式启动引导: 建管理员 / 生成邀请码。

    为什么不在首次注册时"谁先来谁当管理员"就完事:
      那样部署完的第一个小时里, 任何人扫到端口都能抢到 admin。
      现在改成: 管理员由**部署者**用 `--admin` 指定(密码给了就用, 没给就
      随机生成并打印在控制台), 邀请制只在这个基础上叠加。
    """
    if platform is None:
        return
    if platform.user_count() > 0:
        return                      # 已经有用户了(管理员早就建过)
    username = (getattr(args, "admin", "") or "admin").strip()
    pwd = getattr(args, "admin_password", "") or secrets.token_urlsafe(9)
    ok, msg = _platform_register_user(username, pwd, role="admin")
    if not ok:
        print("[!] 初始管理员创建失败: %s" % msg)
        return
    row = platform.user_get(username)
    if row:
        # 标记"密码是系统生成的", 登录后前端会提示改掉
        try:
            platform.conn().execute(
                "UPDATE users SET must_change_pwd=1 WHERE username=?",
                (username,))
            platform.conn().commit()
        except Exception:  # noqa: BLE001
            pass
    platform.audit(row["uid"] if row else "", "bootstrap", username, True,
                   "初始管理员", "127.0.0.1")
    print("-" * 60)
    print("  初始管理员: %s" % username)
    print("  初始密码  : %s" % pwd)
    print("  (请登录后立刻用 `python3 -m cok users passwd %s` 改掉)" % username)
    print("-" * 60, flush=True)


def _migrate_store():
    """把 JSON 里的业务状态导进库（幂等；**不删原文件**）。

    为什么保留文件：安卓端的扫描子进程、以及老版本回退时都要读它。
    等所有读路径都走库之后再考虑下线（那时会有一个明确的切换点）。
    """
    _store.init()
    return _store.import_files()


def _run_migrate(args):
    """执行 --migrate, 打印结果, 返回退出码。**不启动服务**。

    用法::

        # 1) 迁移用户与会话
        python3 -m cok console --platform --migrate users

        # 2) 给"没有主人"的存量账号认领归属(不指定就只报告)
        python3 -m cok console --platform --migrate accounts \
                --migrate-owner boss

        # 3) 两步一起做
        python3 -m cok console --platform --migrate users accounts \
                --migrate-owner boss
    """
    if platform is None:
        print("[!] 平台层 cok_platform 导入失败, 无法迁移:")
        print(PLATFORM_IMPORT_ERROR or "  (未知原因)")
        return 2
    platform.init()
    want = list(args.migrate or [])
    if not want:
        # `--migrate` 不带值时 argparse 给空列表：直接报错退出，
        # 别静默什么都不做（那是"看着成功其实没跑"的典型）。
        print("[!] --migrate 要指定至少一项: users / accounts / store")
        return 2
    print("=" * 60)
    print("  平台库: %s" % platform.DB_PATH)
    print("=" * 60)

    if "users" in want:
        st = _migrate_users()
        print("  用户/会话迁移: 新增 %d 个用户, %d 条会话, 跳过 %d 个, 失败 %d 个"
              % (st["users"], st["sessions"], st["skipped"], st["errors"]))
    if "accounts" in want:
        if not (args.migrate_owner or "").strip():
            # 不猜归属: 没有 --migrate-owner 就只把"谁没主人"列出来
            orphans = [a["key"] for a in accounts.list_accounts()
                       if not (a.get("owner") or "")]
            print("  账号认领: 有 %d 个账号没有主人%s"
                  % (len(orphans), (": " + ", ".join(orphans)) if orphans else ""))
            if orphans:
                print("  → 加 --migrate-owner <用户名> 指定归谁")
        else:
            st = _migrate_accounts(args.migrate_owner)
            print("  账号认领: 新认领 %d 个, 已有归属 %d 个%s"
                  % (st["claimed"], st["already"],
                     ("(" + ", ".join(st["list"]) + ")") if st["list"] else ""))

    if "store" in want:
        st = _migrate_store()
        print("  业务状态迁移: " + ", ".join(
            "%s=%s" % (k, v) for k, v in sorted(st.items())))

    row = platform.first_user()
    print("-" * 60)
    print("  当前用户总数: %d%s" % (platform.user_count(),
                                  ("(最早: %s / %s)" % (row["username"], row["role"]))
                                  if row else ""))
    orphan_n = len([a for a in accounts.list_accounts()
                    if not (a.get("owner") or "")])
    print("  账号总数: %d (其中无主: %d)"
          % (len(accounts.list_accounts()), orphan_n))
    print("=" * 60)
    return 0


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
    ap.add_argument("--platform", action="store_true",
                    help="多用户平台模式: 登录页 + 会话 Cookie + 每用户独立账号空间")
    ap.add_argument("--admin", help="平台模式下指定初始管理员用户名(密码首次登录时设置)")
    ap.add_argument("--admin-password", help="初始管理员密码(不给则首次启动生成随机密码并打印)")
    ap.add_argument("--local-admin", dest="local_admin", metavar="TOKEN",
                    help="平台模式下把带该 token 的请求当成「本机管理员」:"
                         " 不登录、不建平台用户、账号库不过滤归属。"
                         " 给安卓内嵌服务器用(它没有登录页, 打开即用是硬要求)。"
                         " ⚠ token 只在 127.0.0.1 上有效, 外网访问一律要求登录")
    ap.add_argument("--migrate", nargs="*",
                    help="把旧数据迁进平台库后退出: users=用户/会话, "
                         "accounts=给无主账号指定归属(--migrate-owner), "
                         "store=业务状态(配置/运行态/扫描索引/历史)")
    ap.add_argument("--migrate-owner", default="",
                    help="配合 --migrate accounts: 把无主账号归到哪个用户")
    ap.add_argument("--migrate-yes", action="store_true",
                    help="跳过确认直接迁移")
    ap.add_argument("--persistent", action="store_true",
                    help="常驻连接(实时监控, 但会把 App 踢下线)")
    ap.add_argument("--open", action="store_true", help="启动后打开浏览器")
    ap.add_argument("--log", help="追加日志文件(与 daemon 同参数)")
    ap.add_argument("--json", action="store_true", help="日志用 JSON 行(与 daemon 同参数)")
    args = ap.parse_args()
    args.json = False   # 网页控制台走自己的事件流, 这里保持 daemon 的文本输出

    # ---- 一次性迁移(做完就退出; 不启服务) ----
    # 放这里而不是 main 开头: 要保证 platform.init() 已经建好库,
    # 否则迁移会往一个还没建表的地方写。
    if args.migrate is not None:
        return _run_migrate(args)
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
    if args.platform:
        # 平台模式: 每个登录用户一个独立 EngineManager(见 PlatformManager)。
        # 这里仍然建一个"匿名"运行时, 给未登录时的 /api/me 等路由兜底。
        if platform is None:
            print("[!] 平台层 cok_platform 导入失败, 无法启用多用户模式:")
            print(PLATFORM_IMPORT_ERROR or "  (未知原因)")
            return 2
        platform.init()
        # 顺序很重要: **先** bootstrap 再建运行时 —— 反过来会出现一个
        # "还没建管理员就被别人注册走 admin"的窗口期。
        _platform_bootstrap(args)
        # 本机管理员: 给没有登录页的宿主(安卓 App)用。放在 bootstrap 之后,
        # 这样服务器上正常部署时不会凭空多出一个用户。
        if args.local_admin:
            Handler.local_admin_token = str(args.local_admin)
            row = _local_admin_ensure()
            if row is None:
                print("[!] 本机管理员创建失败, --local-admin 不生效")
                Handler.local_admin_token = None
            else:
                claimed = _local_admin_claim_orphans()
                print("[*] 本机管理员: %s (仅 127.0.0.1 + token 可用)"
                      % LOCAL_ADMIN_NAME)
                if claimed:
                    print("    已认领 %d 个无主账号" % claimed)
        Handler.platform = PlatformManager(args)
        # 匿名运行时只给未登录时的 /api/me 兜底(读账号数为 0), 不建引擎
        # 也能正常回答; 真引擎等第一个登录用户来建。
        Handler.manager = None
        Handler.engine = None
    else:
        Handler.manager = EngineManager(args)
        Handler.manager.start()
        # 兼容: 留一个 engine 引用指向当前查看引擎(极少数不带 ?account 的旧调用兜底)
        Handler.engine = Handler.manager.view_engine()

    srv = ThreadingHTTPServer((args.host, args.port), Handler)
    url = "http://%s:%d/" % (args.host, args.port)
    print("=" * 60)
    if args.platform:
        print("  COK 直连控制台已启动 · 多用户平台模式")
        print("  打开: %s  (首次访问会要求登录)" % url)
        if Handler.local_admin_token:
            print("  本机管理员: 已启用(--local-admin, 仅 127.0.0.1 + token)")
        try:
            st = platform.stats()
            print("  用户 %d 个 · 有效会话 %d 个 · 未用邀请码 %d 个"
                  % (st["users"], st["sessions"], st["invites_unused"]))
        except Exception:  # noqa: BLE001
            pass
    else:
        print("  COK 直连控制台已启动")
        print("  打开: %s" % (url + ("?t=%s" % token if token else "")))
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
        if Handler.platform is not None:
            Handler.platform.stop_all()
        elif Handler.manager is not None:
            Handler.manager.stop_all()
        srv.server_close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
