#!/usr/bin/env python3
"""从 database.local.xml 提取保护罩(战争守护)规格: 道具 id -> 文本名 + 时长。

保护罩道具在 <Group id="city_buff"> 里, type=1 的是保护罩本体;
每个道具的 status 字段指向一个状态 id, 状态里带生效时长。
"""
import re
import sys

XML = sys.argv[1] if len(sys.argv) > 1 else "/tmp/database.local.xml"

# 1) 切出 city_buff 组
data = open(XML, encoding="utf-8", errors="replace").read()
m = re.search(r'<Group id="city_buff">(.*?)</Group>', data, re.S)
if not m:
    print("找不到 city_buff 组")
    sys.exit(1)
group = m.group(1)
items = re.findall(r'<ItemSpec\b([^/>]*)/>', group)
print("city_buff 道具数:", len(items))

shields = []
for attrs in items:
    d = dict(re.findall(r'(\w+)="([^"]*)"', attrs))
    if d.get("type") == "1":
        shields.append(d)
print("其中 type=1 (保护罩本体):", len(shields))
for d in shields:
    print("   id=%-9s name(text)=%-9s status=%-9s desc=%-9s tips=%s" % (
        d.get("id"), d.get("name"), d.get("status"), d.get("description"),
        d.get("tips")))

# 2) 找 status 组里这些 status id 的时长
want = {d.get("status") for d in shields if d.get("status")}
want |= {d.get("name") for d in shields if d.get("name")}
print("\n查状态/文本 id:", sorted(x for x in want if x))

for gid in ("city_buff", "status", "buff", "effect", "goods"):
    mm = re.search(r'<Group id="%s">(.*?)</Group>' % gid, data, re.S)
    if not mm:
        continue
    body = mm.group(1)
    hits = []
    for attrs in re.findall(r'<ItemSpec\b([^/>]*)/>', body):
        d = dict(re.findall(r'(\w+)="([^"]*)"', attrs))
        if d.get("id") in want:
            hits.append(d)
    if hits:
        print("\n=== Group %s 命中 %d ===" % (gid, len(hits)))
        for d in hits[:40]:
            print("   ", json.dumps(d, ensure_ascii=False) if False else
                  "  ".join("%s=%s" % (k, v) for k, v in sorted(d.items())))
