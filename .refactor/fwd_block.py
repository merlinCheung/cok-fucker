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
