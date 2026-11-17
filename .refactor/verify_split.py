# -*- coding: utf-8 -*-
"""拆分回归: 校验每个顶层类/函数体与原始 cok_web.py 逐字节一致。

用法: python3 .refactor/verify_split.py [--verbose]
"""
import ast, io, os, sys

BAK = ".refactor/cok_web.py.bak0"
NEW = {"cok_web": "cok/core/cok_web.py",
       "cok_engine": "cok/core/cok_engine.py",
       "cok_web_shared": "cok/core/cok_web_shared.py"}

def defs(path):
    src = io.open(path, encoding="utf-8").read()
    tree = ast.parse(src)
    lines = src.splitlines(True)
    out = {}
    def add(prefix, node):
        name = prefix + node.name
        out[name] = "".join(lines[node.lineno - 1:node.end_lineno])
        for ch in node.body:
            if isinstance(ch, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                add(name + ".", ch)
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            add("", node)
    return out

orig = defs(BAK)
new = {}
for m, p in NEW.items():
    for k, v in defs(p).items():
        new["%s:%s" % (m, k)] = v

missing, diff = [], []
for name, body in orig.items():
    hit = [k for k in new if k.endswith(":" + name)]
    if not hit:
        missing.append(name); continue
    if not any(new[k] == body for k in hit):
        diff.append((name, hit))

print("原始定义: %d 个" % len(orig))
print("拆分后:   %d 个" % len(new))
print("缺失: %d %s" % (len(missing), missing[:6]))
print("内容不同: %d" % len(diff))
for name, hit in diff[:10]:
    print("   ", name, "->", hit)
extra = [k for k in new if k.split(":", 1)[1] not in orig]
print("新增(文件头/转发块里的辅助): %s" % extra)
ok = not missing and not diff
print("结论:", "拆分未改任何定义体 ✅" if ok else "有定义体被改动 ❌")
sys.exit(0 if ok else 1)
