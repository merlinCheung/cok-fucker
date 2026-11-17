# -*- coding: utf-8 -*-
"""P0: cok_web.py 的机械拆分。

文件划分(每个都是纯搬移, 不改逻辑):
  cok/core/cok_web_shared.py   模块级常量 / 模块别名 / 小工具   [已完成]
  cok/core/cok_engine.py       Engine + EngineManager + PlatformManager
  cok/core/cok_web_admin.py    管理域(account 表格 / 概览 / 管理动作) + _Null*
  cok/core/cok_web_actions.py  Handler 里的 do_GET / do_POST / MANAGER_ACTIONS 路由
  cok/core/cok_web_server.py   Handler + 本机管理员 / 迁移 / main
  cok/core/cok_web.py          门面(re-export) —— 保持 `cok_web.X` 全部可用
"""
import io
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import harness

SRC = "cok/core/cok_web.py"
lines = harness.read(SRC).splitlines(True)
bs = harness.blocks(SRC)
starts = {s: (s, e, t) for s, e, t in bs}

def seg(a, b):
    """取 a..b 行(含)。"""
    return "".join(lines[a - 1:b])

# ---- 块边界 ----
ENGINE = (358, 6386)          # Engine / EngineManager / PlatformManager
ADMIN = (6503, 6937)          # 管理域: _ADMIN_STATE_* / _account_row / _Null*
HANDLER = (6939, 7742)        # Handler

# Handler 内部按方法切
handler_src = seg(*HANDLER)
hl = handler_src.splitlines(True)
# 用 AST 找 Handler 的方法行号(相对整文件)
import ast
tree = ast.parse(harness.read(SRC))
handler_node = [n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "Handler"][0]
hmeth = {}
for m in handler_node.body:
    if isinstance(m, ast.FunctionDef):
        hmeth[m.name] = (m.lineno, m.end_lineno)
for k in ("do_GET", "do_POST", "_manager_action", "_audit_action", "_auth", "_send", "_json"):
    print(k, hmeth.get(k))
