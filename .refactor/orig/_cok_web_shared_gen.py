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


