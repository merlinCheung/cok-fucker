#!/usr/bin/env python3
"""从 database.local.xml 生成保护罩(战争守护)规格表。

关键字段(实测):
  * goods 组里 `city_buff="1"` 且 `type2="1"` 的道具 = 保护罩本体
  * `display_quantity="1|28800"` 的第二段 = **持续秒数**(1|3600=1小时, 1|28800=8小时)
  * `cd_time="1"` = 有冷却
  * 道具中文名从 id-names.json 取(名字里自带时长, 如"战争守护8小时")

用法: python3 gen_shield_specs.py [database.local.xml] [id-names.json] [out.json]
"""
import json
import os
import re
import sys

XML = sys.argv[1] if len(sys.argv) > 1 else "/tmp/database.local.xml"
NAMES = sys.argv[2] if len(sys.argv) > 2 else os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "id-names.json")
OUT = sys.argv[3] if len(sys.argv) > 3 else os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "shield-specs.json")

data = open(XML, encoding="utf-8", errors="replace").read()
m = re.search(r'<Group id="goods">(.*?)</Group>', data, re.S)
if not m:
    print("找不到 goods 组")
    sys.exit(1)
body = m.group(1)

try:
    names = json.load(open(NAMES, encoding="utf-8"))
    item_names = names.get("item_names") or {}
except Exception:
    item_names = {}


def clean(raw):
    if not raw:
        return ""
    s = str(raw).strip()
    if s.startswith("{{") and s.endswith("}}"):
        s = s[2:-2]
    if "|" in s:
        s = s.split("|", 1)[0]
    return s.replace("{", "").replace("}", "").strip()


specs = []
for mm in re.finditer(r'<ItemSpec\b([^/>]*)/>', body):
    d = dict(re.findall(r'(\w+)="([^"]*)"', mm.group(1)))
    if d.get("city_buff") != "1":
        continue
    if d.get("type2") != "1":
        continue
    dq = d.get("display_quantity") or ""
    secs = None
    if "|" in dq:
        parts = dq.split("|")
        if len(parts) > 1 and parts[1].isdigit():
            secs = int(parts[1])
    iid = d.get("id")
    label = clean(item_names.get(iid) or item_names.get(d.get("name")))
    if secs is None:
        # 没有 display_quantity 时从名字推断("7天" / "30天" / "3天")
        mm2 = re.search(r'(\d+)\s*天', label or "")
        if mm2:
            secs = int(mm2.group(1)) * 86400
        else:
            mm2 = re.search(r'(\d+)\s*小时', label or "")
            if mm2:
                secs = int(mm2.group(1)) * 3600
            else:
                mm2 = re.search(r'(\d+)\s*分钟', label or "")
                if mm2:
                    secs = int(mm2.group(1)) * 60
    specs.append({
        "id": iid,
        "name": label or ("道具 " + str(iid)),
        "seconds": secs,
        "duration": ("%d 小时" % (secs // 3600)) if secs and secs % 3600 == 0
                    else (("%d 分钟" % (secs // 60)) if secs and secs % 60 == 0
                          else (("%d 秒" % secs) if secs else None)),
        "lv": d.get("lv"),
        "cd_time": d.get("cd_time"),
    })

specs.sort(key=lambda x: (x["seconds"] is None, x["seconds"] or 0))
out = {
    "source": "database.local.xml goods 组(city_buff=1 & type2=1) + id-names.json",
    "note": ("onekeybuff.use 只传槽位号(type); 槽位内容由 onekeybuff.save 写入"
             "(statusList = '道具id;道具id')。持续秒数取 display_quantity 的第二段。"),
    "specs": specs,
}
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print("保护罩规格 %d 条 -> %s" % (len(specs), OUT))
for s in specs:
    print("   %-9s %-22s %-10s lv=%-4s cd=%s" % (
        s["id"], s["name"], s["duration"] or "-", s["lv"], s["cd_time"]))
