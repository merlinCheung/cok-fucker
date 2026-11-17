# -*- coding: utf-8 -*-
"""一次性生成拆分后的 3 个文件(纯搬移, 不改一行逻辑)。

原始 cok_web.py 的行区间(1 起算):
    1-52      文件头 / 自举 / import / HERE
    53-357    模块常量 + 模块别名 + 无状态小工具       -> cok_web_shared.py
    358-6499  Engine / EngineManager / PlatformManager -> cok_engine.py
    6500-…    管理域 / _Null* / Handler / 本机管理员 / 迁移 / main -> cok_web.py

⚠ 关键: 共享定义用「模块对象 + 属性转发」暴露, 不能 `from ... import *`。
   Python 的 from-import 会**拷贝值的引用**, 之后原模块里改 `channel` /
   `PLATFORM_STOP_APP` 这类模块级全局, 导入方看不见 —— 测试正是靠改
   `cok_web.channel` 注入假实现的, 拷一份就静默失效了(2026-11 实测踩过)。
"""
import io
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import harness

SRC = "cok/core/cok_web.py"
src = harness.read(SRC)
lines = src.splitlines(True)

def at(n):
    return lines[n - 1].rstrip("\n")

assert at(52) == "", repr(at(52))
assert at(53).startswith("import cok_daemon"), repr(at(53))
assert at(357) == "", repr(at(357))
assert at(358).startswith("class Engine"), repr(at(358))
assert at(6499).strip() == "return m, True", repr(at(6499))

SHARED = (53, 357)
ENGINE = (358, 6499)

shared_body = "".join(lines[SHARED[0] - 1:SHARED[1]])
engine_body = "".join(lines[ENGINE[0] - 1:ENGINE[1]])
rest_body = "".join(lines[ENGINE[1]:])

# 需要「转发」的共享名字(引擎层 / 门面层各一份)
FORWARD = """("""
for _n in ("_store", "_res", "_pkg_data_dir", "D", "cok_hunt", "cok_stamina",
           "cok_rally", "cok_client", "cok_dock", "cok_sky", "cok_welfare",
           "cok_scoremall", "cok_alliance", "cok_assist", "cok_daily_quest",
           "cok_map", "cok_excel", "load_account", "accounts", "channel",
           "cok_channels", "platform", "cok_users",
           "CHANNEL_IMPORT_ERROR", "CHANNEL_IMPORT_REASON", "PLATFORM_IMPORT_ERROR",
           "TOKEN_FILE", "MAX_EVENTS", "ADB_CANDIDATES", "GAME_PKG",
           "PLATFORM_STOP_APP", "ACCOUNT_REQUIRED", "DOCK_DISABLED_CODE",
           "ASSIST_RES_TYPES", "ASSIST_SCIENCE_TYPE",
           "GAME_SERVER_ACTIONS", "MANAGER_ACTIONS",
           "_is_dock_disabled", "_probe_app_online", "app_online_cached",
           "set_platform_stop_app", "_scan_child_nice", "_resource",
           "_resource_bytes", "_login_required_page", "read_or_make_token",
           "_STATE_CACHE", "_STATE_TTL", "_RES_CACHE", "_RES_FILES", "_RES_MTIME"):
    FORWARD += '    "%s",\n' % _n
FORWARD += ")"

shared_head = '''# -*- coding: utf-8 -*-
"""COK 控制台 —— 共享定义层(常量 / 模块别名 / 无状态小工具)。

从 ``cok_web.py`` 原样搬出(2026-11 架构整理), **逻辑一行未改**。
搬出来的只有「无状态」的东西: 常量、模块别名、纯函数; 有状态的
(Engine / EngineManager / Handler)各自留在自己的文件里。

拆分后的分工:

  * ``cok_web_shared.py``  本文件 —— 常量 / 模块别名 / 小工具
  * ``cok_engine.py``      Engine / EngineManager / PlatformManager
  * ``cok_web.py``         HTTP 路由 + 鉴权 + main + 门面(re-export)

⚠ 改动纪律: 这里的东西被引擎层和 HTTP 层同时引用, 改一个常量要想到另外两处。
⚠ 模块级全局(`channel` / `PLATFORM_STOP_APP` / `_APP_ONLINE_CACHE` ...)只能在
   本文件里赋值 —— 别的模块拿到的是同一份, 所以改这里所有引用方立刻可见。
"""
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


'''
harness.write("cok/core/cok_web_shared.py", shared_head + shared_body)

engine_head = '''# -*- coding: utf-8 -*-
"""COK 控制台的引擎层 —— 轮询 / 快照 / 账号 / 设置 / 游戏操作。

从 ``cok_web.py`` 原样搬出(2026-11 架构整理), **逻辑一行未改**。

为什么拆: ``cok_web.py`` 一度 8200+ 行, 改一个开关要在 6000 行里翻定位。
现在按职责分:

  * ``cok_web_shared.py``  模块常量 / 模块别名 / 小工具(无状态)
  * ``cok_engine.py``      本文件 —— Engine / EngineManager / PlatformManager
  * ``cok_web.py``         HTTP 路由 + 鉴权 + main + 门面(re-export)

⚠ ``Engine`` 的方法**不再往外拆**: 160 个方法共享 200+ 个 self 属性,
拆成 mixin 只会把「这个 self 是哪来的」变成考古题。
"""
import os as _os
import sys as _sys

_PKG_ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
if _os.path.isdir(_PKG_ROOT) and _PKG_ROOT not in _sys.path:
    _sys.path.insert(0, _PKG_ROOT)
_CORE = _os.path.join(_PKG_ROOT, "core")
if _os.path.isdir(_CORE) and _CORE not in _sys.path:
    _sys.path.insert(0, _CORE)

import cok_web_shared as _shared  # noqa: E402

_SHARED_FORWARD = %s


def _fwd_shared():
    g = globals()
    for _n in _SHARED_FORWARD:
        if _n not in g:
            g[_n] = getattr(_shared, _n)
    return g


_fwd_shared()

# 共享名字的**赋值**一律写回 shared(模块属性), 否则 Engine 里改 channel /
# PLATFORM_STOP_APP 之后, cok_web 那边读到的还是旧值。
for _n in _SHARED_FORWARD:
    globals()[_n] = property(lambda self, _n=_n: getattr(_shared, _n),
                             lambda self, v, _n=_n: setattr(_shared, _n, v))


class _SharedProxy(object):
    """`cok_engine.X = v` 时写回 shared。"""

    def __init__(self, name):
        self._name = name

    def __get__(self, obj, objtype=None):
        return getattr(_shared, self._name)

    def __set__(self, obj, value):
        setattr(_shared, self._name, value)


# 模块级 `__getattr__`(PEP 562): 只兜底 shared 里有、本模块没定义的名字。
def __getattr__(name):
    if name in _SHARED_FORWARD:
        return getattr(_shared, name)
    raise AttributeError("module %%r has no attribute %%r" %% (__name__, name))

''' % FORWARD
harness.write("cok/core/cok_engine.py", engine_head + engine_body)

rest_head = '''#!/usr/bin/env python3
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

────────────────────────────────────────────────────────────────────────
架构(2026-11 整理): 本文件只留 **HTTP 层** —— 路由 / 鉴权 / 参数 / main。

  * ``cok_web_shared.py``  模块常量 / 模块别名 / 小工具(无状态)
  * ``cok_engine.py``      Engine / EngineManager / PlatformManager
  * ``cok_web.py``         本文件: Handler + 管理域 + 本机管理员 + 迁移 + main

⚠ 为什么文件名没变: 测试(30+ 处)、安卓 ``android_entry.py``、
   ``tools/preview_web.py``、systemd 单元都按 ``cok_web.py`` / ``cok_web.X`` 走。
   本文件末尾有一段**门面转发**, 保证这些老入口一行都不用改。
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

import cok_web_shared as _shared  # noqa: E402
from cok_engine import Engine, EngineManager, PlatformManager  # noqa: E402

_SHARED_FORWARD = %s


def _fwd_shared():
    g = globals()
    for _n in _SHARED_FORWARD:
        if _n not in g:
            g[_n] = getattr(_shared, _n)
    return g


_fwd_shared()


def __getattr__(name):
    """PEP 562: 共享名字一律回 shared 取当前值(测试/安卓靠改它注入实现)。"""
    if name in _SHARED_FORWARD:
        return getattr(_shared, name)
    raise AttributeError("module %%r has no attribute %%r" %% (__name__, name))

''' % FORWARD
harness.write("cok/core/cok_web.py", rest_head + rest_body)
print("ok")
