#!/usr/bin/env python3
"""生成 id -> 中文名 映射表, 供网页控制台把代号翻译成人话。

数据来源:
  * 队列类型  : apktool/assets/lua_static/game/utility/gameConst.lua 的 QueueType 注释
  * 概览类型  : .../game/CommonPopup/OverviewNew/OverviewTypeDefine.lua 的 Type 注释
                (注意: 概览页用的是**另一套**枚举, 与 QueueType 不同)
  * 道具/建筑 : 客户端配置 database.local.xml 的 ItemSpec.name -> 文本 id
  * luaxml 表 : apktool/assets/local/luaxml/*.lua 的 ["id"] = { ["name"] = 文本id }
                (领主任务 lord_task 就只在这里)
  * 文本      : 设备上的新版 text_zh_CN.ini (UTF-8) 优先, APK 内置旧版兜底

用法:
  python3 gen_id_names.py [输出 json] [--device-text <ini>] [--cfg <xml>]
"""
import json
import os
import re
import sys

BASE = "/Users/a1234/workspace/me/cok/reverse"
CFG = "/tmp/database.local.xml"
TXT = os.path.join(BASE, "apk-extract/assets/local/text_zh_CN.ini")
LUA = os.path.join(BASE, "apktool/assets/lua_static/game/utility/gameConst.lua")
OVERVIEW_LUA = os.path.join(BASE, "apktool/assets/lua_static/game/CommonPopup/"
                             "OverviewNew/OverviewTypeDefine.lua")
LUAXML_DIRS = [
    os.path.join(BASE, "apktool/assets/local/luaxml"),
    os.path.join(BASE, "apktool/assets/localGreen/luaxmlGreen"),
]

# 需要在输出里单独成表的 luaxml 表(其余表只在能解析出中文名时并入 luaxml_names)
NAMED_LUAXML = ["luaxml_lord_task"]


def load_text(path):
    """读 text ini(id=值)。自动兼容 UTF-8 / UTF-16LE / GB18030。"""
    d = {}
    try:
        raw = open(path, "rb").read()
    except OSError:
        return d
    txt = None
    for enc in ("utf-8-sig", "utf-8", "utf-16-le", "gb18030"):
        try:
            cand = raw.decode(enc)
        except (UnicodeDecodeError, LookupError):
            continue
        if "=" in cand:
            txt = cand
            break
    if txt is None:
        return d
    for line in txt.splitlines():
        line = line.strip("\r\n \ufeff")
        if "=" in line:
            k, v = line.split("=", 1)
            d[k.strip()] = v.strip()
    return d


def load_queue_types():
    """从 Lua 注释解析 QueueType: TYPE_XXX = 12, -- 中文说明"""
    out = {}
    try:
        src = open(LUA, encoding="utf-8", errors="replace").read()
    except OSError:
        return out
    m = re.search(r"QueueType\s*=\s*\{(.*?)\}", src, re.S)
    if not m:
        return out
    for line in m.group(1).splitlines():
        mm = re.match(r"\s*TYPE_(\w+)\s*=\s*(\d+)\s*,\s*(?:--\s*(.*))?$", line)
        if mm:
            key, val, comment = mm.group(1), int(mm.group(2)), (mm.group(3) or "").strip()
            comment = re.sub(r"\s*\d+\s*$", "", comment).strip()
            out[val] = comment or key
    return out


def load_overview_types():
    """解析 OverviewTypeDefine.Type = { Building = 1, -- 建筑建造 ... }"""
    out = {}
    try:
        src = open(OVERVIEW_LUA, encoding="utf-8", errors="replace").read()
    except OSError:
        return out
    m = re.search(r"OverviewTypeDefine\.Type\s*=\s*\{(.*?)\n\}", src, re.S)
    if not m:
        return out
    for line in m.group(1).splitlines():
        mm = re.match(r"\s*(\w+)\s*=\s*(\d+)\s*,\s*(?:--\s*(.*))?$", line)
        if mm:
            key, val, comment = mm.group(1), int(mm.group(2)), (mm.group(3) or "").strip()
            out[val] = comment or key
    return out


def load_cfg_items(path):
    """返回 {group: {item_id: (text_id, name_text)}}"""
    try:
        raw = open(path, encoding="utf-8", errors="replace").read()
    except OSError:
        return {}
    groups = {}
    for gm in re.finditer(r'<Group id="([^"]+)">(.*?)</Group>', raw, re.S):
        gname, body = gm.group(1), gm.group(2)
        items = {}
        for im in re.finditer(r'<(\w+)\s+([^>]*?)/>', body):
            d = dict(re.findall(r'(\w+)="([^"]*)"', im.group(2)))
            iid = d.get("id")
            if iid and iid.isdigit():
                items[iid] = d.get("name") or ""
        groups[gname] = items
    return groups


def load_luaxml(text):
    """解析 luaxml_*.lua: {"12345": {["name"] = 文本id, ["des"] = 文本id, ...}}

    返回 {表名: {id: {"name": 短名, "des": 说明}}}
    """
    tables = {}
    for d in LUAXML_DIRS:
        if not os.path.isdir(d):
            continue
        for fn in sorted(os.listdir(d)):
            if not fn.startswith("luaxml_") or not fn.endswith(".lua"):
                continue
            tname = fn[:-4]
            try:
                src = open(os.path.join(d, fn), encoding="utf-8", errors="replace").read()
            except OSError:
                continue
            m = re.search(r"local\s+%s\s*=\s*\{" % re.escape(tname), src)
            if not m:
                continue
            body = src[m.end():]
            out = {}
            for em in re.finditer(r'\["(\w+)"\]\s*=\s*\{(.*?)\n\t\}', body, re.S):
                eid, fields = em.group(1), em.group(2)
                fld = dict(re.findall(r'\["(\w+)"\]\s*=\s*"([^"]*)"', fields))

                def _txt(key):
                    tid = (fld.get(key) or "").split("|")[0].strip()
                    return text.get(tid) if tid.isdigit() else None

                cn = _txt("name")
                if not cn:
                    continue
                out.setdefault(eid, {"name": cn, "des": _txt("des")})
            if out:
                tables[tname] = out
    return tables


def merge_text(old, new):
    """合并两版文本。

    新版(设备)条目更全, 但部分条目把具体数值退化成了 {0} 占位符
    (如 200201: 旧版 "5分钟加速" -> 新版 "{0}加速")。
    规则: 占位符版本不覆盖具体版本。
    """
    merged = dict(old)
    for k, v in new.items():
        cur = merged.get(k)
        if cur is None or ("{0}" in cur and "{0}" not in v):
            merged[k] = v
    return merged


def resolve_name(text, tid):
    """ItemSpec.name 可能是复合的 "模板文本id|填充文本id|..."。

    例: 200201 的 name = "9200330|9200319"
        9200330 = "{0}加速", 9200319 = "5分钟"  ->  "5分钟加速"
    """
    parts = [p.strip() for p in str(tid).split("|") if p.strip()]
    if not parts:
        return None
    tmpl = text.get(parts[0]) if parts[0].isdigit() else None
    if not tmpl:
        return None
    if len(parts) == 1:
        return tmpl
    vals = [text.get(p) for p in parts[1:]]
    out = tmpl
    for i, v in enumerate(vals):
        if v:
            out = out.replace("{%d}" % i, v)
    return out


def main():
    cfg_path = CFG
    device_text = None
    out = None
    argv = sys.argv[1:]
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--device-text" and i + 1 < len(argv):
            device_text = argv[i + 1]
            i += 2
        elif a == "--cfg" and i + 1 < len(argv):
            cfg_path = argv[i + 1]
            i += 2
        elif not a.startswith("--"):
            out = a
            i += 1
        else:
            i += 1

    text = load_text(TXT)                      # APK 旧版
    if device_text:
        text = merge_text(text, load_text(device_text))   # 设备新版补充
    qtypes = load_queue_types()
    otypes = load_overview_types()
    groups = load_cfg_items(cfg_path)

    names = {}
    # 1) 道具 / 建筑 / buff: id -> 中文名
    for gname, items in groups.items():
        for iid, tid in items.items():
            if not tid:
                continue
            first = tid.split("|")[0].strip()
            if not first.isdigit():
                continue
            cn = resolve_name(text, tid)
            if cn:
                names.setdefault(iid, cn)

    # 2) luaxml 表: id -> 中文名(领主任务等)
    tables = load_luaxml(text)
    luaxml_names = {}
    for tname, tmap in tables.items():
        for iid, ent in tmap.items():
            luaxml_names.setdefault(iid, ent["name"])
    # 领主任务: 主显示用 des(完整一句话), 短名另存
    task_names = {}
    task_short = {}
    for iid, ent in (tables.get("luaxml_lord_task") or {}).items():
        task_names[iid] = ent.get("des") or ent["name"]
        task_short[iid] = ent["name"]

    # 2b) 主线任务: story_setting 组的 name 是带 {0} 的模板, {0} 由 target 填充
    #     (例: 33101001 -> "城堡升到{0}级", target=2 -> "城堡升到2级")
    story_tasks = {}
    for iid, tid in (groups.get("story_setting") or {}).items():
        if not tid:
            continue
        tmpl = text.get(tid.split("|")[0].strip())
        if tmpl:
            story_tasks[iid] = tmpl
    # 2c) 章节: story_group 组 -> "第一章 · 扫除魔军"
    story_chapters = {}
    raw_cfg = ""
    try:
        raw_cfg = open(cfg_path, encoding="utf-8", errors="replace").read()
    except OSError:
        pass
    gm = re.search(r'<Group id="story_group">(.*?)</Group>', raw_cfg, re.S)
    if gm:
        for im in re.finditer(r"<ItemSpec\s+([^>]*?)/>", gm.group(1)):
            at = dict(re.findall(r'(\w+)="([^"]*)"', im.group(1)))
            grp = at.get("group")
            if not grp:
                continue
            title = text.get(at.get("title") or "") or ""
            sub = text.get(at.get("pic_title_dialog") or "") or ""
            story_chapters[grp] = (title + " · " + sub).strip(" ·") or title

    # 3) 队列类型 / 概览类型
    queue_types = {str(k): v for k, v in qtypes.items()}
    overview_types = {str(k): v for k, v in otypes.items()}

    # 4) 任何纯数字文本 id 都可能是奖励/任务名
    rewards = {}
    for k, v in text.items():
        if k.isdigit() and len(k) >= 5 and len(v) <= 60:
            rewards[k] = v

    doc = {
        "source": "gameConst.lua QueueType + OverviewTypeDefine.Type + database.local.xml "
                  "ItemSpec + luaxml/*.lua + 设备 text_zh_CN.ini",
        "queue_types": queue_types,
        "overview_types": overview_types,
        "item_names": names,
        "luaxml_names": luaxml_names,
        "task_names": task_names,
        "task_short": task_short,
        "story_tasks": story_tasks,
        "story_chapters": story_chapters,
        "reward_names": rewards,
        "counts": {
            "queue_types": len(queue_types),
            "overview_types": len(overview_types),
            "item_names": len(names),
            "luaxml_names": len(luaxml_names),
            "task_names": len(task_names),
            "story_tasks": len(story_tasks),
            "story_chapters": len(story_chapters),
            "reward_names": len(rewards),
        },
    }
    out = out or os.path.join(BASE, "protocol/id-names.json")
    json.dump(doc, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("written %s" % out)
    print("  " + " ".join("%s=%d" % (k, v) for k, v in doc["counts"].items()))
    print("\n概览类型:")
    for k in sorted(overview_types, key=lambda x: int(x)):
        print("   %-4s %s" % (k, overview_types[k]))
    print("\n道具样例:")
    for iid in ("200201", "200216", "200229", "400000", "410000",
                "57621751", "33101001"):
        if iid in names:
            print("   %-8s %s" % (iid, names[iid]))
    print("\n领主任务样例:")
    for iid in ("53075400", "53083609", "53083601"):
        if iid in task_names:
            print("   %-9s %s" % (iid, task_names[iid]))


if __name__ == "__main__":
    main()
