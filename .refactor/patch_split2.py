# -*- coding: utf-8 -*-
"""把 split2.py 的转发机制换成「模块 __class__ 替换」(读转发 + 写回 shared)。"""
import io

p = ".refactor/split2.py"
b = io.open(p, encoding="utf-8").read()

old_start = b.index('def fwd_block(role, extra_imports=""):')
old_end = b.index("engine_head = '''# -*- coding: utf-8 -*-")

NEW = '''def fwd_block(role, extra_imports=""):
    return \'\'\'# ---------------------------------------------------------------------------
# 共享符号: 从 ``cok_web_shared`` 转发到本模块命名空间(%s)。
#
# ⚠ 为什么不能直接 `from cok_web_shared import channel, ...`:
#    那样拷的是**值的引用**。shared 里 ``channel`` / ``PLATFORM_STOP_APP`` 这类
#    模块级全局一旦被重新赋值(测试注入假实现、安卓端注入停 App 钩子),
#    拷贝出来的名字不会跟着变 —— 表现就是「钩子注入了但没生效」。
#
#    这里把本模块的 __class__ 换成 ``cok_web_shared.SharedModule``:
#      * **读**共享名字 -> 回 shared 取当前值;
#      * **写**共享名字 -> 同时写回 shared, 两边始终同一份。
#    于是 ``cok_web.channel = fake`` / ``cok_engine.ADB_CANDIDATES = [...]``
#    这些老写法(测试 / preview_web / 安卓入口)全部照常生效。
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
from cok_web_shared import SharedModule  # noqa: E402

_SHARED_FORWARD = %s

for _n in _SHARED_FORWARD:
    try:
        object.__setattr__(sys.modules[__name__], _n, getattr(_shared, _n))
    except AttributeError:
        pass
del _n


def _install_shared_module():
    """把本模块换成会「读转发 / 写回 shared」的模块类型。

    ⚠ 必须在文件末尾调用 —— 那时本模块的所有定义都已就位。
    """
    self = sys.modules[__name__]
    if isinstance(self, SharedModule):
        return
    object.__setattr__(self, "_shared", _shared)
    object.__setattr__(self, "_shared_names", set(_SHARED_FORWARD))
    self.__class__ = SharedModule


def _set_shared(name, value):
    """显式写共享全局(读走转发, 写走这里或模块属性赋值)。"""
    setattr(_shared, name, value)

%s\'\'\' % (role, fwd_literal(), extra_imports)


'''
b = b[:old_start] + NEW + b[old_end:]

# 1) shared 模块里加 SharedModule 类
ANCHOR = '''HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)


\'\'\'
harness.write("cok/core/cok_web_shared.py", SHARED_HEAD + shared_body)'''

SHAREDCLS = '''HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)


class SharedModule(_sys.modules[__name__].__class__):
    """把「共享符号」的读写都留在本模块的模块类型。

    为什么要这么绕: 模块属性赋值(如 ``cok_web.channel = fake``)没法挂
    ``__setattr__`` 钩子, 而 ``from x import y`` 又是**值拷贝** —— 两者都会让
    「改了共享全局、别人看不见」这类 bug 静默发生。换成这个类型后:

      * 读共享名字 -> ``__getattr__`` 回 shared 取当前值;
      * 写共享名字 -> ``__setattr__`` 同时写 shared, 两边同一份。

    于是 ``cok_web.channel = fake`` / ``cok_engine.ADB_CANDIDATES = [...]``
    这些老写法(测试 / preview_web / 安卓入口)全部照常生效。
    """

    def __getattr__(self, name):
        names = self.__dict__.get("_shared_names") or ()
        if name in names:
            shared = self.__dict__.get("_shared")
            if shared is not None:
                return getattr(shared, name)
        raise AttributeError("module %r has no attribute %r"
                             % (self.__name__, name))

    def __setattr__(self, name, value):
        if name in (self.__dict__.get("_shared_names") or ()):
            shared = self.__dict__.get("_shared")
            if shared is not None:
                setattr(shared, name, value)
        object.__setattr__(self, name, value)


\'\'\'
harness.write("cok/core/cok_web_shared.py", SHARED_HEAD + shared_body)'''

assert ANCHOR in b, "shared 锚点没找到"
b = b.replace(ANCHOR, SHAREDCLS)

# 2) 两个模块末尾调用 _install_shared_module()
A1 = '''harness.write("cok/core/cok_engine.py",
              engine_head + fwd_block("引擎层") + engine_body)'''
A1_NEW = '''harness.write("cok/core/cok_engine.py",
              engine_head + fwd_block("引擎层") + engine_body
              + "\\n\\n_install_shared_module()\\n")'''
assert A1 in b
b = b.replace(A1, A1_NEW)

A2 = '''harness.write("cok/core/cok_web.py",
              rest_head + fwd_block("门面层") + rest_body)'''
A2_NEW = '''harness.write("cok/core/cok_web.py",
              rest_head + fwd_block("门面层") + rest_body
              + "\\n\\n_install_shared_module()\\n")'''
assert A2 in b
b = b.replace(A2, A2_NEW)

io.open(p, "w", encoding="utf-8").write(b)
print("patched")
