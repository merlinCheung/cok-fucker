#!/usr/bin/env python3
"""在 database.local.xml 全表里按**文本 id**反查道具(保护罩规格)。

ItemSpec 的 name="101400" 就是客户端文本库的 id。
所以 name="104295"(战争守护1小时) 对应的道具 id 能直接反查出来,
再顺着它的 status 字段查状态组拿时长。
"""
import json
import re
import sys

XML = sys.argv[1] if len(sys.argv) > 1 else "/tmp/database.local.xml"
specs = json.load(open("/Users/a1234/workspace/me/cok/cok/shield-specs.json"))
text_ids = specs.get("shield_text_ids") or {}
print("要查的文本 id:", text_ids)

data = open(XML, encoding="utf-8", errors="replace").read()

# 所有 ItemSpec, 按 name 反查
by_name = {}
for m in re.finditer(r'<ItemSpec\b([^/>]*)/>', data):
    d = dict(re.findall(r'(\w+)="([^"]*)"', m.group(1)))
    n = d.get("name")
    if n and n not in by_name:
        by_name[n] = d

print("\n=== 文本 id -> 道具 ===")
found = {}
for tid, label in text_ids.items():
    d = by_name.get(tid)
    if d:
        found[tid] = d
        print("  %-8s %-16s 道具id=%-9s status=%-10s type=%-5s desc=%s" % (
            tid, label, d.get("id"), d.get("status"), d.get("type"),
            d.get("description")))
    else:
        print("  %-8s %-16s (文本 id 不在 ItemSpec.name 里)" % (tid, label))

# 顺带查所有 name 含"守护"文本 id 的道具
print("\n=== 名字里带'守护'的道具(用 id-names 反查) ===")
try:
    names = json.load(open("/Users/a1234/workspace/me/cok/cok/id-names.json"))
    items = names.get("item_names") or {}
    for iid, label in items.items():
        if isinstance(label, str) and "守护" in label and "战场" not in label:
            d = by_name.get(str(iid))
            if d:
                print("  道具id=%-9s 名=%-20s status=%-10s type=%-5s" % (
                    iid, label[:20], d.get("status"), d.get("type")))
except Exception as e:
    print("  ", e)

# 查这些 status 在哪个组里, 带什么字段
if found:
    print("\n=== status 字段反查 ===")
    for tid, d in sorted(found.items()):
        st = d.get("status")
        if not st:
            continue
        mm = re.search(r'<ItemSpec\b([^/>]*)/>', data)
        # 直接搜 status="<st>"
        hits = []
        for mm2 in re.finditer(r'<ItemSpec\b([^/>]*)/>', data):
            dd = dict(re.findall(r'(\w+)="([^"]*)"', mm2.group(1)))
            if dd.get("id") == st:
                hits.append(dd)
        for dd in hits[:2]:
            print("  道具%s status=%s ->" % (d.get("id"), st),
                  " ".join("%s=%s" % (k, v) for k, v in sorted(dd.items())))
