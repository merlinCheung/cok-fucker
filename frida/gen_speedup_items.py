#!/usr/bin/env python3
"""解析客户端服务端下发的道具配置, 生成加速道具速查表。

来源: /data/data/com.hcg.cok.nearme.gamecenter/files/database.local.xml
      (adb pull 权限拒绝, 用 `su -c cat` 读)

type=2  = ITEM_TYPE_SPD 加速道具
type2   = ItemSpdMenu_* (取自 apktool/assets/lua_static/game/utility/gameConst.lua)
时长    = para 第 3 段 (秒), 缺失时退回 display_quantity 第 2 段
"""
import json
import re
import sys
import datetime

# gameConst.lua: ItemSpdMenu = { ... }
# type2 -> 适用的队列类型(主城/联盟/科技等"队列"类加速)
#   queueType: 1=建造队列, 2=造兵队列; None=不走队列(行军/治疗等另有命令)
QUEUE_TYPE = {
    1: "1,2", 3: "2", 6: "1", 7: "1", 9: "1", 10: "1", 11: "1", 12: "1",
    13: "1", 14: "1", 19: "1", 21: "1", 22: "1", 23: "1", 4: "1", 5: "1", 0: "1",
    2: None, 8: None,
}

MENU = {
    0: ("BuildingRemove", "拆除加速"),
    1: ("ALL", "通用(城建/造兵/科技/陷阱/治疗 全适用)"),
    2: ("Troop", "行军加速"),
    3: ("Soldier", "造兵加速"),
    4: ("Heal", "伤兵治疗加速"),
    5: ("Trap", "造陷阱加速"),
    6: ("Science", "科技加速"),
    7: ("City", "城建(主城建造)加速"),
    8: ("DuanZao", "锻造加速"),
    9: ("Alliance", "联盟加速"),
    10: ("Mate", "造材料加速"),
    11: ("HighTech", "新科技加速"),
    12: ("JieLv", "戒律大厅加速"),
    13: ("Civ_City", "文明堡垒分城城建加速"),
    14: ("Tactical", "阵法研习加速"),
    19: ("RaceScience", "先祖之魂加速(与队列类型一致)"),
    20: ("Extension", "新建/扩建(不走队列, 仅占位)"),
    21: ("Armament", "军械库加速"),
    22: ("ArmyReform", "士兵改造加速"),
    23: ("ForeignCiviTech", "外来文明科技加速"),
}


def parse_seconds(d):
    """加速时长(秒): 优先 para 第 3 段, 其次 display_quantity 第 2 段。"""
    para = d.get("para")
    if para:
        parts = [p.strip() for p in para.split(";")]
        if len(parts) >= 3 and parts[2].isdigit():
            return int(parts[2])
    dq = d.get("display_quantity")
    if dq:
        parts = [p.strip() for p in dq.split("|")]
        if len(parts) >= 2 and parts[1].isdigit():
            return int(parts[1])
    return None


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else "/tmp/database.local.xml"
    out = sys.argv[2] if len(sys.argv) > 2 else \
        "/Users/a1234/workspace/me/cok/cok/speedup-items.json"

    data = open(src, encoding="utf-8", errors="replace").read()
    pat = re.compile(r'<(\w+)\s+([^>]*?type2="([^"]*)"[^>]*?)/>')
    groups = {}
    total = 0
    for m in pat.finditer(data):
        d = dict(re.findall(r'(\w+)="([^"]*)"', m.group(2)))
        if d.get("type") != "2":
            continue
        total += 1
        t2 = int(d.get("type2") or 0)
        sec = parse_seconds(d)
        label = MENU.get(t2, ("?", "未知(%d)" % t2))
        qt = QUEUE_TYPE.get(t2, "unknown")
        if qt is None:
            qt = "not-queue"
        groups.setdefault(t2, {"key": label[0], "label": label[1],
                               "queue_type": qt, "items": []})
        groups[t2]["items"].append({
            "id": int(d["id"]) if d.get("id", "").isdigit() else d.get("id"),
            "seconds": sec,
            "icon": d.get("icon"),
            "color": d.get("color"),
            "name": d.get("name"),
        })

    for g in groups.values():
        g["items"].sort(key=lambda x: (x["seconds"] is None, x["seconds"] or 0, x["id"]))

    doc = {
        "source": "/data/data/com.hcg.cok.nearme.gamecenter/files/database.local.xml"
                  " (服务端下发的道具配置, adb pull 权限拒绝, 需 su -c cat)",
        "menu_source": "apktool/assets/lua_static/game/utility/gameConst.lua :: ItemSpdMenu",
        "rule": "type=2 即 ITEM_TYPE_SPD 加速道具; type2=ItemSpdMenu_* 决定适用场景;"
                " 时长 = para 第 3 段(秒), 缺失时取 display_quantity 第 2 段",
        "important": "type2=1 (ItemSpdMenu_ALL) 是**通用**加速道具, 对城建/造兵/科技/陷阱/治疗都适用;"
                     " queue.ccd 的 queueType 只区分建造(1)/造兵(2), 具体功能由 qUUID 唯一确定;"
                     " 道具是否适用由服务端按道具 type2 校验",
        "how_to_choose": "主城建造队列(queueType=1) => type2 ∈ {7 城建专用, 1 通用};"
                         " 造兵队列(queueType=2) => type2 ∈ {3 造兵专用, 1 通用};"
                         " type2=1 通用道具在两类队列都可用, 是最省心的选择",
        "queue_type_legend": "1=建造队列, 2=造兵队列, not-queue=不走队列(行军加速等用别的命令),"
                             " unknown=ItemSpdMenu 未定义(非加速场景道具)",
        "generated_at": datetime.datetime.now().isoformat(timespec="seconds"),
        "total": total,
        "groups": {str(k): v for k, v in sorted(groups.items())},
    }
    json.dump(doc, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    print("加速道具总数: %d, 分组 %d 个 -> %s" % (total, len(groups), out))
    print()
    for t2, g in sorted(groups.items()):
        mark = " ★通用" if t2 == "1" else ""
        print("[%2s] %-24s %-46s %3d 个%s" % (t2, g["key"], g["label"], len(g["items"]), mark))
    print()
    print("=== 通用加速道具(type2=1)明细 ===")
    for it in groups[1]["items"]:
        s = it["seconds"]
        print("   id=%-8s %8s 秒  icon=%-10s color=%s"
              % (it["id"], s if s is not None else "?", it["icon"], it["color"]))


if __name__ == "__main__":
    main()
