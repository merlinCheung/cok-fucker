# -*- coding: utf-8 -*-
"""P0-1: 抽出 cok_web_shared.py —— 模块级共享定义(常量/import/小工具)。

只搬移, 不改一行逻辑。cok_web.py 原位置改成 `from cok_web_shared import *`
加一份显式再导出, 保持 `cok_web.<名字>` 全部可用。
"""
import io
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import harness

SRC = "cok/core/cok_web.py"
OUT = "cok/core/cok_web_shared.py"

src = harness.read(SRC)
lines = src.splitlines(True)
bs = harness.blocks(src)

MOVE = (list(range(53, 231)))          # import + 常量 + 小工具函数
DROP = set(range(1, 51))               # 自举头留下
picked = set(MOVE) - DROP

# 注释块并入: 块起始行往上连续的 # 行
for s, e, t in bs:
    if s not in picked:
        continue
    n = s - 1
    while n >= 1 and lines[n - 1].lstrip().startswith("#"):
        picked.add(n)
        n -= 1
picked = {n for n in picked if 51 <= n <= 230}

moved = "".join(lines[n - 1] for n in sorted(picked))
rest = "".join(lines[n - 1] for n in range(1, len(lines) + 1) if n not in picked)

harness.write(OUT, moved)
harness.write(".refactor/cok_web_step1.py", rest)

# 头部必须补：shared 也需要 sys.path 自举 + 那几个 import
head = ("# -*- coding: utf-8 -*-\n"
        '"""COK 控制台共享定义(常量 / 模块别名 / 小工具)。\n\n'
        "从 ``cok_web.py`` 原样搬出 —— 见 ``cok/core/cok_web.py`` 的说明。\n"
        '"""\n'
        "import os as _os\n"
        "import sys as _sys\n"
        "\n"
        "_PKG_ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))\n"
        "if _os.path.isdir(_PKG_ROOT) and _PKG_ROOT not in _sys.path:\n"
        "    _sys.path.insert(0, _PKG_ROOT)\n"
        "_CORE = _os.path.join(_PKG_ROOT, \"core\")\n"
        "if _os.path.isdir(_CORE) and _CORE not in _sys.path:\n"
        "    _sys.path.insert(0, _CORE)\n"
        "\n"
        "import cok_paths  # noqa: E402\n"
        "import cok_store as _store  # noqa: E402   # 业务状态入库（配置/运行态/索引）\n"
        "from cok_paths import resource as _res  # noqa: E402\n"
        "from cok_paths import data_dir as _pkg_data_dir  # noqa: E402\n"
        "import argparse  # noqa: E402\n"
        "import copy  # noqa: E402\n"
        "import datetime  # noqa: E402\n"
        "import json  # noqa: E402\n"
        "import os  # noqa: E402\n"
        "import secrets  # noqa: E402\n"
        "import signal  # noqa: E402\n"
        "import sys  # noqa: E402\n"
        "import re  # noqa: E402\n"
        "import subprocess  # noqa: E402\n"
        "import threading  # noqa: E402\n"
        "import time  # noqa: E402\n"
        "import traceback  # noqa: E402\n"
        "import webbrowser  # noqa: E402\n"
        "from urllib.parse import parse_qs  # noqa: E402\n"
        "from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer  # noqa: E402\n"
        "\n"
        "HERE = os.path.dirname(os.path.abspath(__file__))\n"
        "sys.path.insert(0, HERE)\n"
        "\n")
with io.open(OUT, "w", encoding="utf-8") as f:
    f.write(head + moved)
print("shared 总行数:", (head + moved).count("\n"))
