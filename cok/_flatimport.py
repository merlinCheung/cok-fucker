"""让 ``cok.core`` / ``cok.tools`` 里的模块名保持历史写法。

这些模块彼此之间是**平铺 import**::

    import cok_client
    from cok_sfs import TypedInt, SFS_INT

平铺写法有三个好处, 一个都不能丢:

1. **安卓端不用改** —— Chaquopy 把 ``cok_*.py`` 解到 app 私有目录,
   ``sys.path`` 上就是那一层; 平铺名字直接可导入。
2. **工具脚本能独立跑** —— ``python3 cok/tools/scan_world.py`` 自己把
   ``cok/core`` 插进 ``sys.path`` 就能 import 到兄弟模块。
3. **历史文档不用改** —— 报告里几百处 ``python3 cok_web.py`` 仍然成立。

所以这里把 ``cok/core`` 与 ``cok/tools`` **注册成导入根**: 注册之后
``import cok_client`` 与 ``import cok.core.cok_client`` 拿到同一个模块对象。
用别名(而不是真把文件挪进包目录)是因为安卓端必须拿到**平铺的真实文件**。
"""

import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)

#: 需要注册成导入根的目录(顺序即优先级)
_SEARCH_PATHS = (
    os.path.join(_ROOT, "core"),
    os.path.join(_ROOT, "tools"),
)


def bootstrap():
    """把 core/ 与 tools/ 加进 ``sys.path``, 并同步 ``sys.modules`` 别名。

    幂等: 重复调用没有副作用。
    """
    for path in _SEARCH_PATHS:
        if os.path.isdir(path) and path not in sys.path:
            sys.path.insert(0, path)

    # 已经作为 cok.core.xxx / cok.tools.xxx 导入过的模块, 补一个平铺别名
    for pkg_name, pkg_dir in (("cok.core", "core"), ("cok.tools", "tools")):
        for name, mod in list(sys.modules.items()):
            if not name.startswith(pkg_name + "."):
                continue
            leaf = name.rsplit(".", 1)[1]
            if leaf in sys.modules:
                continue
            sys.modules[leaf] = mod


bootstrap()