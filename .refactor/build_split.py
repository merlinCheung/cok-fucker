# -*- coding: utf-8 -*-
"""生成 cok_web.py 的拆分文件(纯搬移)。

划分:
  cok_web_shared.py   已生成
  cok_engine.py       Engine / EngineManager / PlatformManager  (行 358-6386)
  cok_web.py          其余: Handler / 管理域 / 本机管理员 / main
"""
import ast
import io
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import harness

SRC = "cok/core/cok_web.py"
src = harness.read(SRC)
lines = src.splitlines(True)

# ---- 1. 抽引擎层 ----------------------------------------------------
ENGINE_BODY = "".join(lines[357:6386])

ENGINE_HEAD = '''# -*- coding: utf-8 -*-
"""COK 控制台的引擎层 —— 轮询 / 快照 / 账号 / 设置 / 游戏操作。

从 ``cok_web.py`` 原样搬出(2026-11 架构整理), **逻辑一行未改**。
拆分原因: ``cok_web.py`` 单文件 8000+ 行, 改一个开关要在 6000 行里翻定位;
现在按职责分成:

  * ``cok_web_shared.py``  模块级常量 / 模块别名 / 小工具(无状态)
  * ``cok_engine.py``      Engine / EngineManager / PlatformManager(本文件)
  * ``cok_web.py``         HTTP 路由 + 鉴权 + main + 门面 re-export

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

import cok_web_shared as _S  # noqa: E402
from cok_web_shared import *  # noqa: F401,F403
from cok_web_shared import (  # noqa: F401  (显式再导出, 静态检查/IDE 用)
    _store, _res, _pkg_data_dir, D, cok_hunt, cok_stamina, cok_rally,
    cok_client, cok_dock, cok_sky, cok_welfare, cok_scoremall, cok_alliance,
    cok_assist, cok_daily_quest, cok_map, cok_excel, load_account, accounts,
    channel, cok_channels, platform, cok_users,
    CHANNEL_IMPORT_ERROR, CHANNEL_IMPORT_REASON, TOKEN_FILE, MAX_EVENTS,
    ADB_CANDIDATES, GAME_PKG, PLATFORM_STOP_APP, ACCOUNT_REQUIRED,
    DOCK_DISABLED_CODE, ASSIST_RES_TYPES, ASSIST_SCIENCE_TYPE,
    GAME_SERVER_ACTIONS, MANAGER_ACTIONS, _is_dock_disabled,
    _probe_app_online, app_online_cached, set_platform_stop_app,
)
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

'''
harness.write("cok/core/cok_engine.py", ENGINE_HEAD + ENGINE_BODY)

# ---- 2. cok_web.py 保留其余 ----------------------------------------
rest = "".join(lines[:357]) + "".join(lines[6386:])
harness.write(".refactor/cok_web_step2.py", rest)

# ---- 3. 校验: 剩余部分里不允许再出现 Engine 的定义 -----------------
tree = ast.parse(rest)
names = [n.name for n in tree.body if isinstance(n, ast.ClassDef)]
print("剩余文件的类:", names)
print("剩余行数:", rest.count("\n"))
