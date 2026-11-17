# -*- coding: utf-8 -*-
"""P0: cok_web.py → cok_web_shared.py + cok_engine.py + cok_web.py(HTTP 层)。

纯搬移, 不改一行逻辑。行区间(1 起算, 含端点):
    1-52      文件头 / 自举 / import / HERE
    53-357    模块常量 + 模块别名 + 无状态小工具       -> cok_web_shared.py
    358-6499  Engine / EngineManager / PlatformManager -> cok_engine.py
    6500-…    管理域 / _Null* / Handler / 本机管理员 / 迁移 / main -> cok_web.py

⚠ 共享符号用 **PEP 562 模块级 __getattr__** 转发, 不用 from-import:
  from-import 拷的是值的引用, shared 里 `channel` / `PLATFORM_STOP_APP`
  被重新赋值后, 引擎层 / 门面层看不见 —— 测试靠改 `cok_web.channel`
  注入假实现, 拷一份就静默失效(2026-11 实测踩过)。
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

shared_body = "".join(lines[52:357])
engine_body = "".join(lines[357:6499])
rest_body = "".join(lines[6499:])

NAMES = ["_store", "_res", "_pkg_data_dir", "D", "cok_hunt", "cok_stamina",
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
         "_STATE_CACHE", "_STATE_TTL", "_RES_CACHE", "_RES_FILES", "_RES_MTIME"]


def fwd_literal():
    out = "(\n"
    for n in NAMES:
        out += '    "%s",\n' % n
    out += ")"
    return out


SHARED_HEAD = '''# -*- coding: utf-8 -*-
"""COK 控制台 —— 共享定义层(常量 / 模块别名 / 无状态小工具)。

从 ``cok_web.py`` 原样搬出(2026-11 架构整理), **逻辑一行未改**。
搬出来的只有「无状态」的东西: 常量、模块别名、纯函数; 有状态的
(Engine / EngineManager / Handler)各自留在自己的文件里。

拆分后的分工:

  * ``cok_web_shared.py``  本文件 —— 常量 / 模块别名 / 小工具
  * ``cok_engine.py``      Engine / EngineManager / PlatformManager
  * ``cok_web.py``         HTTP 路由 + 鉴权 + main + 门面(转发)

⚠ 改动纪律:
  1. 这里的东西被引擎层和 HTTP 层同时引用, 改一个常量要想到另外两处;
  2. 模块级全局(``channel`` / ``PLATFORM_STOP_APP`` / ``_APP_ONLINE_CACHE`` ...)
     **只能在本文件里赋值** —— 别的模块读到的是同一份, 改这里全部立刻可见。
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


#: ``from cok_web_shared import *`` 的清单(引擎层/门面层各有一份快照)。
#: 不写这个, import * 会把 os/json/threading 等标准库名一起拉进来,
#: 让两个模块的命名空间跟 shared 的私有名纠缠在一起, 排查时非常痛苦。
__all__ = [
    "_store",
    "_res",
    "_pkg_data_dir",
    "D",
    "cok_hunt",
    "cok_stamina",
    "cok_rally",
    "cok_client",
    "cok_dock",
    "cok_sky",
    "cok_welfare",
    "cok_scoremall",
    "cok_alliance",
    "cok_assist",
    "cok_daily_quest",
    "cok_map",
    "cok_excel",
    "load_account",
    "accounts",
    "channel",
    "cok_channels",
    "platform",
    "cok_users",
    "CHANNEL_IMPORT_ERROR",
    "CHANNEL_IMPORT_REASON",
    "PLATFORM_IMPORT_ERROR",
    "TOKEN_FILE",
    "MAX_EVENTS",
    "ADB_CANDIDATES",
    "GAME_PKG",
    "PLATFORM_STOP_APP",
    "ACCOUNT_REQUIRED",
    "DOCK_DISABLED_CODE",
    "ASSIST_RES_TYPES",
    "ASSIST_SCIENCE_TYPE",
    "GAME_SERVER_ACTIONS",
    "MANAGER_ACTIONS",
    "_is_dock_disabled",
    "_probe_app_online",
    "app_online_cached",
    "set_platform_stop_app",
    "_scan_child_nice",
    "_resource",
    "_resource_bytes",
    "_login_required_page",
    "read_or_make_token",
    "_STATE_CACHE",
    "_STATE_TTL",
    "_RES_CACHE",
    "_RES_FILES",
    "_RES_MTIME",
]


class SharedModule(_sys.modules[__name__].__class__):
    """共享符号「读转发 / 写回 shared」的模块类型。

    为什么要这么绕: 模块属性赋值(如 ``cok_web.channel = fake``)没法挂
    ``__setattr__`` 钩子, 而 ``from x import y`` 又是**值拷贝** —— 两者都会让
    「改了共享全局、别人看不见」这类 bug 静默发生。换成这个类型后:

      * 读: 本模块 ``__dict__`` 里预置了一份(模块体内/函数里直接用);
      * 写: ``__setattr__`` 同时更新本模块 ``__dict__`` 与 shared,
            并且**广播**给所有引用模块(见 ``_shared_aliases``)。

    于是 ``cok_web.channel = fake`` / ``cok_engine.ADB_CANDIDATES = [...]``
    这些老写法(测试 / preview_web / 安卓入口)全部照常生效。
    """

    def __setattr__(self, name, value):
        object.__setattr__(self, name, value)
        if name in (self.__dict__.get("_shared_names") or ()):
            shared = self.__dict__.get("_shared")
            if shared is not None:
                object.__setattr__(shared, name, value)
            # 广播给其它引用本名字的模块, 免得它们读到旧值
            for mod in list(_shared_alias_modules):
                if mod is not self and mod.__dict__.get("_shared_names") \
                        and name in mod.__dict__["_shared_names"]:
                    object.__setattr__(mod, name, value)


#: 所有「引用了共享符号」的模块(写共享名字时要广播)
_shared_alias_modules = []
def bind_shared_module(module_name, shared_names):
    """把某个模块换成 SharedModule, 并把共享名字的**当前值**预置进它的 __dict__。

    ⚠ 每个模块要有自己的类(``type(name, (SharedModule,), {...})``):
    ``_shared_names`` 是类属性, 共用一个类会让两个模块的清单互相覆盖。
    """
    import sys as _s
    mod = _s.modules[module_name]
    names = frozenset(shared_names)
    if not isinstance(mod, SharedModule):
        cls = type(module_name + "Module", (SharedModule,),
                   {"_shared_names": names})
        mod.__class__ = cls
    else:
        mod.__class__._shared_names = names
    # 预置一份当前值: 模块体内/函数里读共享名字直接命中 __dict__, 不再走钩子
    for n in names:
        if n not in mod.__dict__:
            try:
                object.__setattr__(mod, n, getattr(_s.modules[__name__], n))
            except AttributeError:
                pass
    if mod not in _shared_alias_modules:
        _shared_alias_modules.append(mod)
    return mod


'''
harness.write("cok/core/cok_web_shared.py", SHARED_HEAD + shared_body)


def fwd_block(role, extra_imports=""):
    return '''# ---------------------------------------------------------------------------
# 共享符号: 从 ``cok_web_shared`` 转发到本模块命名空间(%s)。
#
# ⚠ 为什么不能直接 `from cok_web_shared import channel, ...`:
#    那样拷的是**值的引用**。shared 里 ``channel`` / ``PLATFORM_STOP_APP`` 这类
#    模块级全局一旦被重新赋值(测试注入假实现、安卓端注入停 App 钩子),
#    拷贝出来的名字不会跟着变 —— 表现就是「钩子注入了但没生效」。
#
# 做法(两步):
#   1. ``from cok_web_shared import *`` 拉一份**初始快照**进本模块命名空间。
#      保证模块体执行期间(``class Engine: SETTINGS_FILE = _pkg_data_dir()``)
#      这些名字都在; 清单由 shared 的 ``__all__`` 决定, 不会漏。
#   2. 本文件**末尾**调 ``bind_shared_module(__name__, _SHARED_FORWARD)``:
#      把 __class__ 换成 SharedModule 子类, 并登记为"共享名字的引用方"。
#      之后写共享名字会同步 shared 并广播给其它引用方(见 SharedModule.__setattr__)。
#
# ⚠ 顺序很重要: 必须是「shared 全部定义完 → 引用方 import → 引用方末尾 bind」。
#    所以 ``cok_web_shared`` 里 import 任何东西都不要回头 import 引擎层/门面层。
#
# 于是 ``cok_web.channel = fake`` / ``cok_engine.ADB_CANDIDATES = [...]``
# 这些老写法(测试 / preview_web / 安卓入口)全部照常生效。
# ---------------------------------------------------------------------------
import argparse  # noqa: E402
import copy  # noqa: E402
import datetime  # noqa: E402
import json  # noqa: E402
import os  # noqa: E402
import secrets  # noqa: E402
import signal  # noqa: E402
import sys  # noqa: E402
import re  # noqa: E402
import subprocess  # noqa: E402
import threading  # noqa: E402
import time  # noqa: E402
import traceback  # noqa: E402
import webbrowser  # noqa: E402
from urllib.parse import parse_qs  # noqa: E402
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer  # noqa: E402

import cok_web_shared as _shared  # noqa: E402
from cok_web_shared import *  # noqa: F401,F403,E402   # 共享名字的初始快照
from cok_web_shared import bind_shared_module  # noqa: E402

_SHARED_FORWARD = %s


def _set_shared(name, value):
    """显式写共享全局(等价于 ``<本模块>.<name> = v``)。"""
    setattr(_shared, name, value)
    setattr(sys.modules[__name__], name, value)

%s''' % (role, fwd_literal(), extra_imports)


engine_head = '''# -*- coding: utf-8 -*-
"""COK 控制台的引擎层 —— 轮询 / 快照 / 账号 / 设置 / 游戏操作。

从 ``cok_web.py`` 原样搬出(2026-11 架构整理), **逻辑一行未改**。

为什么拆: ``cok_web.py`` 一度 8200+ 行, 改一个开关要在 6000 行里翻定位。
现在按职责分:

  * ``cok_web_shared.py``  模块常量 / 模块别名 / 小工具(无状态)
  * ``cok_engine.py``      本文件 —— Engine / EngineManager / PlatformManager
  * ``cok_web.py``         HTTP 路由 + 鉴权 + main + 门面(转发)

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

'''
harness.write("cok/core/cok_engine.py",
              engine_head + fwd_block("引擎层") + engine_body
              + "\n\n# 登记为本模块的共享符号引用方(读转发 / 写回 shared)。\n"
                "bind_shared_module(__name__, _SHARED_FORWARD)\n")

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

⚠ 文件名没变是**故意的**: 测试(30+ 处)、安卓 ``android_entry.py``、
   ``tools/preview_web.py``、systemd 单元都按 ``cok_web.py`` / ``cok_web.X`` 走,
   下面的门面转发保证这些老入口一行都不用改。
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

from cok_engine import Engine, EngineManager, PlatformManager  # noqa: E402

'''
harness.write("cok/core/cok_web.py",
              rest_head + fwd_block("门面层") + rest_body
              + "\n\n# 登记为本模块的共享符号引用方(读转发 / 写回 shared)。\n"
                "bind_shared_module(__name__, _SHARED_FORWARD)\n")
print("生成完毕")
