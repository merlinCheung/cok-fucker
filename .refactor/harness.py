# -*- coding: utf-8 -*-
"""字节级等价重构工具。

规则(安全网):
  * 只允许「整段搬移」和「换模块前缀」两类改动。
  * 类体保持完整 —— 方法不搬出 Engine。
  * 每个新文件用 `pass  # --- 以下为从 cok_web.py 原样搬来的定义 ---` 之后的内容
    与源文件按 AST 块切出来的原文**逐字节比对**。
"""
import ast
import io
import os
import re
import sys

SRC = "cok/core/cok_web.py"


def read(p=SRC):
    with io.open(p, encoding="utf-8") as f:
        return f.read()


def blocks(src):
    """顶层块: [(start_line, end_line, text)]，1 起算。"""
    tree = ast.parse(src)
    lines = src.splitlines(True)
    out = []
    for node in tree.body:
        start = min([node.lineno] + [d.lineno for d in getattr(node, "decorator_list", [])])
        end = node.end_lineno
        out.append((start, end, "".join(lines[start - 1:end])))
    return out


def split_head(src, first_line):
    """返回 (head, tail)，tail 从 first_line(1 起算) 开始。"""
    lines = src.splitlines(True)
    return "".join(lines[:first_line - 1]), "".join(lines[first_line - 1:])


def write(path, text, expect_head=None):
    d = os.path.dirname(path)
    if d and not os.path.isdir(d):
        os.makedirs(d)
    if expect_head is not None:
        cur = read(path) if os.path.exists(path) else ""
        if cur and cur != expect_head:
            raise SystemExit("!! %s 与预期不一致，先人工检查" % path)
    with io.open(path, "w", encoding="utf-8") as f:
        f.write(text)
    print("wrote %s (%d 行)" % (path, text.count("\n")))


PREFIX_RE = [
    (re.compile(r"(?<![A-Za-z0-9_.])_store\."), "cok_store."),
    (re.compile(r"(?<![A-Za-z0-9_.])_res\("), "_res("),
]


def check_same(a, b, label):
    if a != b:
        # 找第一个不同的行
        al, bl = a.splitlines(), b.splitlines()
        for i in range(min(len(al), len(bl))):
            if al[i] != bl[i]:
                print("!! %s 第 %d 行不同:\n   A: %r\n   B: %r" % (label, i + 1, al[i], bl[i]))
                break
        else:
            print("!! %s 行数不同 %d vs %d" % (label, len(al), len(bl)))
        return False
    print("OK %s 逐字节一致 (%d 字节)" % (label, len(a)))
    return True
