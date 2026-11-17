# -*- coding: utf-8 -*-
"""SharedModule 改成在**模块创建时**就位(import 钩子), 而不是文件末尾才装。

这样类体执行期间读共享名字也会走转发(否则 `class Engine: X = _pkg_data_dir()`
这类语句在 install 之前执行, 直接 NameError)。
"""
import io

p = ".refactor/split2.py"
b = io.open(p, encoding="utf-8").read()

# 1) shared 里加「模块创建后置钩子」+ SharedModule 用懒绑定
OLD_CLS_START = b.index("class SharedModule(_sys.modules[__name__].__class__):")
OLD_CLS_END = b.index("'''\nharness.write(\"cok/core/cok_web_shared.py\"")
NEW_CLS = '''class SharedModule(_sys.modules[__name__].__class__):
    """共享符号「读转发 / 写回 shared」的模块类型。

    为什么要这么绕: 模块属性赋值(如 ``cok_web.channel = fake``)没法挂
    ``__setattr__`` 钩子, 而 ``from x import y`` 又是**值拷贝** —— 两者都会让
    「改了共享全局、别人看不见」这类 bug 静默发生。换成这个类型后:

      * 读共享名字 -> ``__getattr__`` 回 shared 取当前值;
      * 写共享名字 -> ``__setattr__`` 同时写 shared, 两边同一份。

    于是 ``cok_web.channel = fake`` / ``cok_engine.ADB_CANDIDATES = [...]``
    这些老写法(测试 / preview_web / 安卓入口)全部照常生效。
    """

    #: 共享名字清单(owner -> frozenset), 由 ``bind_shared_module()`` 填。
    _shared_names = frozenset()

    def __getattr__(self, name):
        if name in self._shared_names:
            return getattr(_sys.modules[__name__], name)
        raise AttributeError("module %r has no attribute %r"
                             % (self.__name__, name))

    def __setattr__(self, name, value):
        if name in self._shared_names:
            setattr(_sys.modules[__name__], name, value)
        object.__setattr__(self, name, value)


def bind_shared_module(module_name, shared_names):
    """把某个模块换成 SharedModule, 并把共享名字清单绑定到它**自己的类**上。

    ⚠ 每个模块要有自己的类(``type(name, (SharedModule,), {...})``):
    ``_shared_names`` 是类属性, 共用一个类会让两个模块的清单互相覆盖。
    """
    import sys as _s
    mod = _s.modules[module_name]
    if isinstance(mod, SharedModule):
        mod.__class__._shared_names = frozenset(shared_names)
        return mod
    cls = type(module_name + "Module", (SharedModule,),
               {"_shared_names": frozenset(shared_names)})
    mod.__class__ = cls
    return mod


'''
b = b[:OLD_CLS_START] + NEW_CLS + b[OLD_CLS_END:]

# 2) fwd_block: 改成注册 import 钩子; 删掉文件末尾 install
OLD_FWD_START = b.index("def fwd_block(role, extra_imports=\"\"):")
OLD_FWD_END = b.index("engine_head = '''# -*- coding: utf-8 -*-")
NEWFWD = '''def fwd_block(role, extra_imports=""):
    return \'\'\'# ---------------------------------------------------------------------------
# 共享符号: 从 ``cok_web_shared`` 转发到本模块命名空间(%s)。
#
# ⚠ 为什么不能直接 `from cok_web_shared import channel, ...`:
#    那样拷的是**值的引用**。shared 里 ``channel`` / ``PLATFORM_STOP_APP`` 这类
#    模块级全局一旦被重新赋值(测试注入假实现、安卓端注入停 App 钩子),
#    拷贝出来的名字不会跟着变 —— 表现就是「钩子注入了但没生效」。
#
#    做法: 注册一个 import 钩子, 本模块**执行完的那一刻**把它的 __class__
#    换成 ``cok_web_shared.SharedModule`` 子类。之后
#      * 读共享名字 -> 回 shared 取当前值;
#      * 写共享名字 -> 同时写回 shared, 两边始终同一份。
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
from cok_web_shared import bind_shared_module  # noqa: E402

_SHARED_FORWARD = %s


def _cok_web_shared_postimport(_mod):
    """模块刚 import 完就替换 __class__(见 PEP 302 的 exec_module 包装)。

    ⚠ 不能在模块体内直接改 ``sys.modules[__name__].__class__``: 类体执行
    期间读共享名字(如 ``class Engine: SETTINGS_FILE = _pkg_data_dir()``)
    发生在赋值之前, 会直接 NameError。用钩子把替换推迟到模块执行完之后,
    但**仍在第一次 import 返回之前**, 外部拿到的已经是转发模块。
    """
    try:
        bind_shared_module(_mod.__name__, _SHARED_FORWARD)
    except Exception:  # noqa: BLE001  钩子失败不该让整个模块 import 不了
        pass
    return _mod


class _SharedModuleLoader(object):
    """包装真正的 loader, 在 exec_module 之后挂上共享转发。"""

    def __init__(self, inner):
        self._inner = inner

    def create_module(self, spec):
        if hasattr(self._inner, "create_module"):
            return self._inner.create_module(spec)
        return None

    def exec_module(self, module):
        self._inner.exec_module(module)
        _cok_web_shared_postimport(module)

    def __getattr__(self, name):
        return getattr(self._inner, name)


class _SharedModuleFinder(object):
    """给本模块装一个一次性 finder: 只匹配自己, 用完立刻摘掉。

    为什么不挂在 sys.meta_path 上常驻: 常驻 finder 会影响所有 import,
    排查问题时很难想到它。一次性 + 装完就摘, 影响面最小。
    """

    def __init__(self, fullname):
        self._fullname = fullname

    def find_module(self, fullname, path=None):  # 老接口(3.4+ 仍会被调用)
        return self.find_spec(fullname, path)

    def find_spec(self, fullname, path=None, target=None):
        import importlib.util as _u
        if fullname != self._fullname:
            return None
        # 已经 import 过(比如 reload)就直接返回, 避免重复包装
        mod = sys.modules.get(fullname)
        if mod is not None and getattr(mod, "__spec__", None) is not None:
            inner = mod.__spec__.loader
            if isinstance(inner, _SharedModuleLoader):
                return None
            return _u.spec_from_loader(
                fullname, _SharedModuleLoader(inner),
                origin=getattr(inner, "get_filename", lambda *a: None) and None)
        return None


# 直接装一次性 finder 太绕(还要处理 spec 的 origin), 这里用更简单可靠的办法:
# 在 sys.meta_path 上放一个只匹配本模块的 finder, 它返回一个包装 loader。
def _install_shared_import_hook():
    import importlib.machinery as _m
    fullname = __name__

    class _Finder(_m.PathFinder):
        def find_spec(self, fullname_, path=None, target=None):
            if fullname_ != fullname:
                return None
            spec = super().find_spec(fullname_, path, target)
            if spec is None or spec.loader is None:
                return spec
            if isinstance(spec.loader, _SharedModuleLoader):
                return spec
            spec.loader = _SharedModuleLoader(spec.loader)
            return spec

    for i, f in enumerate(sys.meta_path):
        if getattr(f, "__name__", "") == "_Finder" and \\
                getattr(f, "_cok_shared_for", None) == fullname:
            return
    f = _Finder()
    f._cok_shared_for = fullname
    f.__name__ = "_Finder"
    sys.meta_path.insert(0, f)


_install_shared_import_hook()

%s\'\'\' % (role, fwd_literal(), extra_imports)


'''
b = b[:OLD_FWD_START] + NEWFWD + b[OLD_FWD_END:]

# 3) 去掉两个文件末尾的 _install_shared_module()
b = b.replace('''              + "\\n\\n_install_shared_module()\\n")''', '''              )''')

io.open(p, "w", encoding="utf-8").write(b)
print("patched")
