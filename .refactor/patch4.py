# -*- coding: utf-8 -*-
"""关键修正: 共享名字必须**预先放进 __dict__**(供本模块读), 但 __setattr__ 里
要同步 __dict__ + shared —— 这样「读」拿到的是本模块 dict 里的最新值,
「写」两边都改。再配一个 shared -> 各引用模块的推送即可。"""
import io

p = ".refactor/split2.py"
b = io.open(p, encoding="utf-8").read()

# A) shared: SharedModule 用 __getattr__/__setattr__ 做「写回 + 读自身」
OLD_START = b.index("class SharedModule(_sys.modules[__name__].__class__):")
OLD_END = b.index("def bind_shared_module(module_name, shared_names):")
NEW_CLS = '''class SharedModule(_sys.modules[__name__].__class__):
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
                if mod is not self and mod.__dict__.get("_shared_names") \\
                        and name in mod.__dict__["_shared_names"]:
                    object.__setattr__(mod, name, value)


#: 所有「引用了共享符号」的模块(写共享名字时要广播)
_shared_alias_modules = []
'''
b = b[:OLD_START] + NEW_CLS + b[OLD_END:]

# B) bind_shared_module: 预置一份值到 __dict__
OLD_B = b.index("def bind_shared_module(module_name, shared_names):")
OLD_B_END = b.index("'''\nharness.write(\"cok/core/cok_web_shared.py\"")
NEW_B = '''def bind_shared_module(module_name, shared_names):
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
b = b[:OLD_B] + NEW_B + b[OLD_B_END:]

# C) fwd_block: 不再装 import 钩子; 改成在文件末尾调用 bind_shared_module
OLD_FWD_START = b.index("def fwd_block(role, extra_imports=\"\"):")
OLD_FWD_END = b.index("engine_head = '''# -*- coding: utf-8 -*-")
NEW_FWD = '''def fwd_block(role, extra_imports=""):
    return \'\'\'# ---------------------------------------------------------------------------
# 共享符号: 从 ``cok_web_shared`` 转发到本模块命名空间(%s)。
#
# ⚠ 为什么不能直接 `from cok_web_shared import channel, ...`:
#    那样拷的是**值的引用**。shared 里 ``channel`` / ``PLATFORM_STOP_APP`` 这类
#    模块级全局一旦被重新赋值(测试注入假实现、安卓端注入停 App 钩子),
#    拷贝出来的名字不会跟着变 —— 表现就是「钩子注入了但没生效」。
#
#    做法: 文件末尾调 ``bind_shared_module(__name__, _SHARED_FORWARD)``,
#    它做两件事:
#      1. 把本模块 __class__ 换成 SharedModule 子类(带 ``__setattr__``);
#      2. 把共享名字的**当前值**预置进本模块 __dict__(供模块体/函数直接读)。
#    写共享名字时会同步 shared 并广播给其它引用模块, 于是
#    ``cok_web.channel = fake`` / ``cok_engine.ADB_CANDIDATES = [...]``
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
from cok_web_shared import bind_shared_module  # noqa: E402

_SHARED_FORWARD = %s


def _set_shared(name, value):
    """显式写共享全局(与 ``<本模块>.<name> = v`` 等价)。"""
    setattr(_shared, name, value)
    setattr(sys.modules[__name__], name, value)

%s\'\'\' % (role, fwd_literal(), extra_imports)


'''
b = b[:OLD_FWD_START] + NEW_FWD + b[OLD_FWD_END:]

# D) 两个模块末尾调用 bind_shared_module
b = b.replace('''harness.write("cok/core/cok_engine.py",
              engine_head + fwd_block("引擎层") + engine_body)''',
'''harness.write("cok/core/cok_engine.py",
              engine_head + fwd_block("引擎层") + engine_body
              + "\\n\\nbind_shared_module(__name__, _SHARED_FORWARD)\\n")''')
b = b.replace('''harness.write("cok/core/cok_web.py",
              rest_head + fwd_block("门面层") + rest_body)''',
'''harness.write("cok/core/cok_web.py",
              rest_head + fwd_block("门面层") + rest_body
              + "\\n\\nbind_shared_module(__name__, _SHARED_FORWARD)\\n")''')

io.open(p, "w", encoding="utf-8").write(b)
print("patched")
