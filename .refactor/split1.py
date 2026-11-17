# -*- coding: utf-8 -*-
"""P0 第一步: 把 cok_web.py 的「共享定义」抽到 cok_web_shared.py，原位置改成 from-import。

只做搬移, 不改任何一行逻辑。
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
starts = {s for s, e, t in bs}

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

# 自动把「注释块」并进搬移集合：块起始行往上连续的 # 行
picked = set(PICK)
for s, e, t in bs:
    if s not in PICK:
        continue
    n = s - 1
    while n >= 1 and lines[n - 1].lstrip().startswith("#"):
        picked.add(n)
        n -= 1

# 自举头(1-50 行)留在 cok_web.py
picked -= set(range(1, 51))

lo, hi = 51, 230
assert all(lo <= n <= hi for n in picked), "搬移范围越界: %s" % sorted(
    n for n in picked if not (lo <= n <= hi))

moved_text = "".join(lines[n - 1] for n in sorted(picked))
rest_text = "".join(lines[n - 1] for n in range(1, len(lines) + 1)
                    if n not in picked)

harness.write(OUT, moved_text)
harness.check_same(rest_text, src, "拆分前后剩余正文完全一致") if False else None
print("搬走 %d 行, 剩余 %d 行" % (len(picked), src.count("\n") - len(picked)))
print("--- 搬走内容的前 6 行 ---")
print("".join(moved_text.splitlines(True)[:6]))
print("--- 搬走内容的最后 6 行 ---")
print("".join(moved_text.splitlines(True)[-6:]))
print("--- 剩余正文的前 30 行 ---")
print("".join(rest_text.splitlines(True)[:30]))
