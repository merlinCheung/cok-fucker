# -*- coding: utf-8 -*-
import io, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import harness

src = harness.read("cok/core/cok_web.py")
lines = src.splitlines(True)
bs = harness.blocks(src)

PICK = (list(range(53, 69)) + list(range(69, 77))
        + list(range(77, 94)) + list(range(94, 101))
        + list(range(101, 108)) + list(range(108, 113))
        + list(range(113, 117)) + list(range(117, 126))
        + list(range(126, 132)) + [132, 133, 134]
        + list(range(137, 151)) + list(range(153, 169))
        + list(range(169, 176)) + [176]
        + list(range(179, 183)) + list(range(183, 187))
        + [187, 188] + list(range(189, 198)) + [198]
        + list(range(199, 202)) + [202] + list(range(204, 214))
        + list(range(214, 219)) + list(range(221, 231)))

picked = set(PICK)
for s, e, t in bs:
    if s not in PICK:
        continue
    n = s - 1
    while n >= 1 and lines[n - 1].lstrip().startswith("#"):
        picked.add(n)
        n -= 1
picked -= set(range(1, 51))
lo, hi = 51, 230
assert all(lo <= n <= hi for n in picked)

moved = "".join(lines[n - 1] for n in sorted(picked))
rest = "".join(lines[n - 1] for n in range(1, len(lines) + 1) if n not in picked)
harness.write("cok/core/cok_web_shared.py", moved)
harness.write(".refactor/cok_web_after_strip.py", rest)

# 核对: 剩余文件里应该没有任何 import/常量定义(除了自举)
import ast
tree = ast.parse(rest)
bad = []
for node in tree.body:
    ln = node.lineno
    if ln <= 60:
        continue
    if isinstance(node, (ast.Import, ast.ImportFrom, ast.Assign, ast.FunctionDef)):
        bad.append((ln, type(node).__name__))
print("剩余文件里 60 行以后的顶层定义:", bad)
