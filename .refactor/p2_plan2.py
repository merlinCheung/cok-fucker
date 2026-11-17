# -*- coding: utf-8 -*-
"""列出 cok_web.py 所有「非 pass 结尾」的宽 except，看哪些是真错误。"""
import ast, io
src = io.open("cok/core/cok_web.py", encoding="utf-8").read()
tree = ast.parse(src)
lines = src.splitlines()

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
        t = hd.type
        wide = (t is None or (isinstance(t, ast.Name) and t.id in ("Exception", "BaseException")))
        if not wide:
            continue
        body = hd.body
        if len(body) == 1 and isinstance(body[0], ast.Pass):
            continue          # 已单独列过
        # 是否真的「说了话」
        has_log = any(
            isinstance(s, (ast.Expr,)) and isinstance(s.value, ast.Call)
            and getattr(s.value.func, "attr", "") in ("warning", "error", "info")
            or isinstance(s, ast.Raise)
            for s in ast.walk(hd))
        names = [getattr(s, "id", "") for s in ast.walk(hd) if isinstance(s, ast.Name)]
        kind = "LOG" if has_log else ("ret" if "return" in names or "error" in names else "silent?")
        first = lines[hd.body[0].lineno - 1].strip()[:70]
        print("%5d %-8s %-40s %s" % (hd.lineno, kind, func_at.get(hd.lineno, "?"), first))
