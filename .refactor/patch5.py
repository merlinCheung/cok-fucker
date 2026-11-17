# -*- coding: utf-8 -*-
"""最终方案: 共享名字在**模块体执行之前**就预置进 __dict__(exec_module 包装)。

`class Engine: X = _pkg_data_dir()` 这类语句在模块体里执行, 比文件末尾的
bind_shared_module 更早, 所以必须让替换发生在 exec_module **之前**——
用 PEP 302 的 loader 包装: 先 bind 再 exec。

⚠ 但 bind 需要模块对象存在(create_module 之后), 而预置的值来自 shared,
  与模块自身无关 —— 所以顺序是:
    create_module -> bind_shared_module(替换 __class__ + 预置值) -> exec_module
"""
import io

p = ".refactor/split2.py"
b = io.open(p, encoding="utf-8").read()

# 1) 删掉旧的 fwd_block 实现, 换成 loader 包装版
S = b.index('def fwd_block(role, extra_imports=""):')
E = b.index("engine_head = '''# -*- coding: utf-8 -*-")

NEW = '''def fwd_block(role, extra_imports=""):
    return \'\'\'# ---------------------------------------------------------------------------
# 共享符号: 从 ``cok_web_shared`` 转发到本模块命名空间(%s)。
#
# ⚠ 为什么不能直接 `from cok_web_shared import channel, ...`:
#    那样拷的是**值的引用**。shared 里 ``channel`` / ``PLATFORM_STOP_APP`` 这类
#    模块级全局一旦被重新赋值(测试注入假实现、安卓端注入停 App 钩子),
#    拷贝出来的名字不会跟着变 —— 表现就是「钩子注入了但没生效」。
#
#    做法: 本文件顶部装一个**一次性 import 钩子**。本模块被 import 时:
#      1. ``create_module`` 建好模块对象;
#      2. ``bind_shared_module`` 把 __class__ 换成 SharedModule 子类,
#         并把共享名字的当前值预置进 __dict__ —— **在 exec_module 之前**,
#         这样模块体里 ``class Engine: SETTINGS_FILE = _pkg_data_dir()``
#         这类语句也能读到(否则 NameError);
#      3. ``exec_module`` 执行模块体;
#      4. 摘掉钩子(只影响本模块, 不污染全局 import)。
#
#    写共享名字 -> ``SharedModule.__setattr__`` 同步 shared 并广播给其它
#    引用模块。于是 ``cok_web.channel = fake`` /
#    ``cok_engine.ADB_CANDIDATES = [...]`` 这些老写法全部照常生效。
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
    """显式写共享全局(等价于 ``<本模块>.<name> = v``)。"""
    setattr(_shared, name, value)
    setattr(sys.modules[__name__], name, value)


class _SharedLoader(object):
    """包装真正的 loader: 建模块 -> bind(替换 __class__ + 预置值) -> exec。"""

    def __init__(self, inner, names):
        self._inner = inner
        self._names = names

    def create_module(self, spec):
        if hasattr(self._inner, "create_module"):
            return self._inner.create_module(spec)
        return None

    def exec_module(self, module):
        # ⚠ 必须在 exec 之前 bind: 模块体里会读共享名字(类属性赋值等)。
        bind_shared_module(module.__name__, self._names)
        self._inner.exec_module(module)

    def __getattr__(self, name):
        return getattr(self._inner, name)


def _install_shared_import_hook():
    """一次性 finder: 只包装本模块, 用完立刻从 sys.meta_path 摘掉。"""
    import importlib.machinery as _m
    fullname = __name__
    for f in sys.meta_path:
        if getattr(f, "_cok_shared_for", None) == fullname:
            return

    class _Finder(_m.PathFinder):
        _cok_shared_for = fullname

        def find_spec(self, fullname_, path=None, target=None):
            if fullname_ != fullname:
                return None
            spec = super().find_spec(fullname_, path, target)
            # 只包装一次: 第二次进来说明已经是我们的 loader 了
            if spec is not None and spec.loader is not None \\
                    and not isinstance(spec.loader, _SharedLoader):
                spec.loader = _SharedLoader(spec.loader, _SHARED_FORWARD)
            return spec

    sys.meta_path.insert(0, _Finder())


_install_shared_import_hook()

%s\'\'\' % (role, fwd_literal(), extra_imports)


'''
b = b[:S] + NEW + b[E:]

# 2) 末尾不再需要 bind(已在 exec 前做掉), 但保留一次幂等调用做防御
b = b.replace('''              + "\\n\\nbind_shared_module(__name__, _SHARED_FORWARD)\\n")''',
              '''              + ''' + "'''" + '''\\n\\n# 防御: 若本模块是被 reload() 或 importlib 直接执行的, 钩子可能没跑到,
# 这里再幂等补一次(bind_shared_module 自身可重入)。
bind_shared_module(__name__, _SHARED_FORWARD)
\'\'\'" + "'''" + ''')''')

io.open(p, "w", encoding="utf-8").write(b)
print("patched")
