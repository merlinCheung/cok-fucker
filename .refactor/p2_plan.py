# -*- coding: utf-8 -*-
"""列出 P2 要处理的静默 except 及其所在方法/最近的上层函数。"""
import ast, io
src = io.open("cok/core/cok_web.py", encoding="utf-8").read()
tree = ast.parse(src)
lines = src.splitlines()

# 建立「行 -> 所在函数名」映射
func_at = {}
def walk(node, prefix=""):
    for ch in ast.iter_child_nodes(node):
        if isinstance(ch, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for n in range(ch.lineno, (ch.end_lineno or ch.lineno) + 1):
                func_at[n] = prefix + ch.name
            walk(ch, prefix + ch.name + ".")
        elif isinstance(ch, ast.ClassDef):
            walk(ch, prefix + ch.name + ".")
        else:
            walk(ch, prefix)
walk(tree)

for h in ast.walk(tree):
    if not isinstance(h, ast.Try):
        continue
    for hd in h.handlers:
        if not (len(hd.body) == 1 and isinstance(hd.body[0], ast.Pass)):
            continue
        t = hd.type
        wide = (t is None or (isinstance(t, ast.Name) and t.id in ("Exception", "BaseException")))
        if not wide:
            continue
        print("%5d  %-46s %s" % (hd.lineno, func_at.get(hd.lineno, "?"), lines[hd.lineno-1].strip()[:60]))
