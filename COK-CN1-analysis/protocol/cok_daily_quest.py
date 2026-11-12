#!/usr/bin/env python3
"""COK 每日任务（dailyQuest2025）直连封装。

能力:
  * 拉取每日任务列表，逐项显示每个任务的类型/进度/目标/是否完成
  * 领取日活跃宝箱（dailyQuest2025.reward）
  * 领取周活跃宝箱（dailyQuest2025.weekReward）
  * 快速完成单个/全部任务（dailyQuest2025.immediateTask / immediateAllTask，消耗道具）

用法:
  python3 cok_daily_quest.py --read                    # 拉取并显示每个任务项
  python3 cok_daily_quest.py --claim-boxes             # 领取所有可领的活跃宝箱
  python3 cok_daily_quest.py --complete <taskId>       # 快速完成单个任务(需道具)
  python3 cok_daily_quest.py --complete-all            # 快速完成全部(需道具)

⚠ 领取宝箱/快速完成是真实写操作，会消耗奖励次数/道具。
"""

import argparse
import json
import os
import sys
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cok_client import CokClient  # noqa: E402

# 本地 APK 解包里的任务配置表，服务端不下发 gotype/go/point，需在此补全。
# 相对仓库根目录；也可放在 COK_CN1_XML 环�境变量指定的路径。
_XML_DEFAULT = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..", "apk-extract", "assets", "local", "database.local.xml",
)


def _load_quest_config(xml_path=None):
    """解析 database.local.xml 的 daily_quest_2025 表，按任务 id 建立映射。

    返回: { task_id: {"gotype": str, "go": str, "point": str, ...} }
    找不到文件或表时返回空 dict。
    """
    path = xml_path or os.environ.get("COK_CN1_XML") or _XML_DEFAULT
    path = os.path.abspath(path)
    if not os.path.exists(path):
        return {}
    try:
        tree = ET.parse(path)
    except ET.ParseError:
        return {}
    root = tree.getroot()
    conf = {}
    for g in root.iter("Group"):
        if g.get("id") != "daily_quest_2025":
            continue
        for item in g.iter("ItemSpec"):
            tid = item.get("id")
            if not tid:
                continue
            conf[tid] = {
                "gotype": item.get("gotype"),
                "go": item.get("go"),
                "point": item.get("point"),
                "costitem": item.get("costitem"),
                "target": item.get("target"),
                "name": item.get("name"),
                "desc": item.get("desc"),
                "range": item.get("range"),
            }
        break
    return conf


_QUEST_CONF = _load_quest_config()


def _as_int(v, default=0):
    try:
        return int(v)
    except (TypeError, ValueError):
        return default


def _task_type_label(gotype, go):
    """根据 gotype/go 猜测任务类型标签（供显示用，参考 JumpHandler.lua）。

    gotype 决定跳转大类，go 是该大类内的子项。
    服务端 dailyQuest2025.data 不下发这两个字段，需从本地
    database.local.xml 的 daily_quest_2025 表补全。
    """
    try:
        gt = int(gotype)
    except (TypeError, ValueError):
        gt = None
    if gt == 1:
        return "主城建筑(go=%s)" % go
    if gt == 2:
        return "UI 组件(go=%s)" % go
    if gt == 3:
        return "世界地图(go=%s)" % go
    if gt == 4:
        return "特殊建筑(go=%s)" % go
    if gt == 7:
        labels = {
            "5": "月卡",
            "7": "打开背包(全部)",
            "10": "打开礼包界面",
            "11": "打开聊天界面",
            "12": "打开许愿池",
            "13": "前往日常奖励",
            "14": "前往英雄试炼",
            "16": "跳转到装扮界面",
            "18": "龙塔试炼",
            "19": "跳转到作坊界面",
            "20": "跳转到储藏箱",
            "21": "跳转到龙魂秘宝",
            "22": "跳转到龙之馈礼",
            "23": "跳转到旅行商人",
            "24": "跳转到周年打卡",
            "25": "跳转到英雄招募",
            "26": "跳转皇家角斗场",
            "27": "跳转到每日好礼",
            "28": "跳转到日常奖励-签到",
            "31": "兵种进阶",
            "32": "阵法",
            "33": "炼金工坊",
            "34": "铁匠铺锻造",
            "35": "先祖之魂",
            "36": "神器",
            "37": "声望捐献",
            "45": "每日任务快速完成",
            "54": "SVIP 界面",
            "65": "SVIP 界面",
            "117": "福利界面某一页",
            "125": "天空之境",
        }
        return labels.get(str(go), "功能跳转(go=%s)" % go)
    if gt == 15:
        return "跳转指定 pos(go=%s)" % go
    if gt == 16:
        labels = {
            "2": "粮食采集",
            "7": "巨型狮鹫",
            "8": "普通怪",
            "10": "奇迹宝藏",
            "11": "超级营地",
        }
        return labels.get(str(go), "大地图搜索栏(go=%s)" % go)
    if gt == 105:
        return "联盟帮助"
    if gt == 106:
        return "联盟 boss"
    if gt == 107:
        return "联盟宝藏"
    if gt == 109:
        return "联盟科技"
    if gt == 117:
        return "福利界面某一页"
    if gt == 125:
        return "天空之境"
    return "未知类型(gotype=%s, go=%s)" % (gotype, go)


def task_protocol_viable(gotype, go):
    """判断该任务是否能通过直连协议"完成"（非道具快速完成）。

    当前结论：直连协议**只能做两件事**：
      1) dailyQuest2025.data —— 只读，拉取每个任务的进度/完成状态
      2) dailyQuest2025.reward / weekReward —— 领取已完成任务对应的活跃宝箱
         （不消耗道具，前提是 activePoints/weeklyActivePoints 足够且未领过）

    其余 18 个未完成任务的"正常完成"（如建造、研究、签到、龙塔试炼等）
    需在游戏 App 内手动点页面跳转执行，直连工具**无法模拟 UI 点击**。
    immediateTask / immediateAllTask 虽可直连调用，但**消耗道具**，用户已排除。

    返回: (viable: bool, reason: str)
    """
    # 只有已完成的任务对应的宝箱，能通过协议"一键完成"（领奖，不算任务本身完成）
    # 任务完成本身（hasCom 从 false 变 true）不能通过协议触发（非道具路径）
    return False, "任务完成需在 App 内手动执行对应页面操作；直连仅支持读进度与领已完成任务的宝箱"


def analyze_tasks(result):
    """把 read_daily_quest() 的返回值逐项分析，给出每个任务的：
      - gotype/go 对应的具体操作（来自本地 XML 配置表 + JumpHandler.lua）
      - 是否可通过直连协议完成（非道具）
      - 可用的协议命令
    返回列表，每项：{id, name, type_label, complete, progress, viable, reason, cmd}
    """
    out = []
    for t in result.get("tasks", []):
        tid = t.get("id")
        gotype = t.get("gotype")
        go = t.get("go")
        viable, reason = task_protocol_viable(gotype, go)
        item = {
            "id": tid,
            "name": t.get("name") or "",
            "type_label": t.get("type_label") or _task_type_label(gotype, go),
            "progress": t.get("progress") or "",
            "complete": t.get("complete") or False,
            "viable": viable,
            "reason": reason,
            "point": t.get("point"),
        }
        if t.get("complete"):
            item["cmd"] = "dailyQuest2025.reward {id} / weekReward {id}  # 领对应活跃宝箱(不消耗道具)"
        else:
            item["cmd"] = "（无直连完成命令；需在 App 内手动执行 %s）" % item["type_label"]
        out.append(item)
    return out


def print_analysis(result):
    """打印每个任务的详细分析（gotype/go 操作、可否协议完成、协议命令）。"""
    if not result.get("ok"):
        print("读取失败:", result.get("error") or result.get("errorCode"))
        return
    print("=== 每日任务协议可行性分析 ===")
    print("活跃点: %s   周活跃点: %s" % (result.get("activePoints"), result.get("weeklyActivePoints")))
    print()
    for t in analyze_tasks(result):
        mark = "✓" if t["complete"] else " "
        viable = "可协议" if t["viable"] else "需手动"
        print("[%s] %s(id=%s) 进度:%s 类型:%s 状态:%s" % (
            mark, t["name"] or t["id"], t["id"], t["progress"], t["type_label"], viable))
        print("      协议: %s" % t["cmd"])
        print("      说明: %s" % t["reason"])
    print()
    print("结论：直连协议目前唯一可安全'一键完成'的操作是领取已完成任务对应的")
    print("活跃宝箱（dailyQuest2025.reward / weekReward，不消耗道具）。其余未完成任务")
    print("需在游戏 App 内手动点页面跳转执行，直连工具只能拉取进度展示。")


def _enrich_task(q):
    """把本地 XML 配置表里的 gotype/go/point 等字段补给任务项。

    服务端 dailyQuest2025.data 不下发这些配置字段，任务 id 是常量，
    可直接匹配 database.local.xml 的 daily_quest_2025 表。
    """
    tid = q.get("id")
    if not tid:
        return q
    conf = _QUEST_CONF.get(str(tid))
    if not conf:
        return q
    if q.get("gotype") is None and conf.get("gotype"):
        q["gotype"] = conf["gotype"]
    if q.get("go") is None and conf.get("go"):
        q["go"] = conf["go"]
    if q.get("point") is None and conf.get("point"):
        q["point"] = conf["point"]
    if q.get("costitem") is None and conf.get("costitem"):
        q["costitem"] = conf["costitem"]
    if not q.get("target") and conf.get("target"):
        q["target"] = conf["target"]
    if not q.get("name") and conf.get("name"):
        q["name"] = conf["name"]
    if not q.get("desc") and conf.get("desc"):
        q["desc"] = conf["desc"]
    return q


def read_daily_quest(client):
    """拉取每日任务主界面，返回结构化数据。

    返回:
        {
          "ok": bool,
          "errorCode": str|None,
          "tasks": [{"id","name","desc","target","totalTimes","times","num",
                     "totalNum","point","costitem","hasComplete","type_label",
                     "progress","complete"}],
          "boxes": [{"id","point","state"}],           # 日活跃宝箱
          "weekly_boxes": [{"id","point","state"}],     # 周活跃宝箱
          "activePoints": int,
          "weeklyActivePoints": int,
          "weekEndTime": int,
          "curReward": int,
          "dailyTaskId2025": str,   # 已领日宝箱 id，";" 分隔
          "weekTaskRewardId2025": str,  # 已领周宝箱 id，";" 分隔
        }
    """
    try:
        r = client.call("dailyQuest2025.data")
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "error": str(e)[:160]}
    p = r.get("__params__") or {}
    if p.get("errorCode"):
        return {"ok": False, "errorCode": p.get("errorCode"), "error": p.get("errorCode")}

    tasks = []
    for q in (p.get("dailyQuest") or []):
        if not isinstance(q, dict):
            continue
        q = _enrich_task(q)
        tid = q.get("id")
        times = _as_int(q.get("times"))
        total_times = _as_int(q.get("totalTimes"))
        has_complete = bool(q.get("hasCom")) or times >= total_times
        gotype = q.get("gotype")
        go = q.get("go")
        tasks.append({
            "id": tid,
            "name": q.get("name") or "",
            "desc": q.get("desc") or "",
            "target": q.get("target") or "",
            "totalTimes": total_times,
            "times": times,
            "num": q.get("num"),
            "totalNum": q.get("totalNum"),
            "point": q.get("point"),
            "costitem": q.get("costitem"),
            "hasComplete": has_complete,
            "type_label": _task_type_label(gotype, go),
            "progress": "%s/%s" % (q.get("num"), total_times) if total_times else "",
            "complete": has_complete,
        })

    # 已领宝箱 id 集合
    got_daily = set(str(x) for x in str(p.get("dailyTaskId2025") or "").split(";") if x)
    got_weekly = set(str(x) for x in str(p.get("weekTaskRewardId2025") or "").split(";") if x)

    boxes = []
    for b in (p.get("rewardList") or []):
        if not isinstance(b, dict):
            continue
        bid = str(b.get("id"))
        bpoint = _as_int(b.get("point"))
        state = b.get("state")
        if state is None:
            # 客户端侧按 activePoints 与已领记录推断 state
            state = "GET_REWARD" if bid in got_daily else "UNKNOWN"
        boxes.append({
            "id": bid,
            "point": bpoint,
            "state": state,
            "claimable": bid not in got_daily,
        })

    weekly_boxes = []
    for wb in (p.get("newWeekRewardList") or []):
        if not isinstance(wb, dict):
            continue
        wid = str(wb.get("id"))
        wpoint = _as_int(wb.get("point"))
        state = wb.get("state")
        if state is None:
            state = "GET_REWARD" if wid in got_weekly else "UNKNOWN"
        weekly_boxes.append({
            "id": wid,
            "point": wpoint,
            "state": state,
            "claimable": wid not in got_weekly,
        })

    return {
        "ok": True,
        "tasks": tasks,
        "boxes": boxes,
        "weekly_boxes": weekly_boxes,
        "activePoints": _as_int(p.get("curReward")),
        "weeklyActivePoints": _as_int(p.get("weekTaskScore")),
        "weekEndTime": p.get("weekEndTime"),
        "curReward": p.get("curReward"),
        "dailyTaskId2025": p.get("dailyTaskId2025") or "",
        "weekTaskRewardId2025": p.get("weekTaskRewardId2025") or "",
    }


def complete_task(client, task_id):
    """快速完成单个每日任务（dailyQuest2025.immediateTask，消耗道具）。"""
    params = {"id": str(task_id)}
    try:
        r = client.call("dailyQuest2025.immediateTask", params)
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "error": str(e)[:160]}
    p = r.get("__params__") or {}
    if p.get("errorCode"):
        return {"ok": False, "errorCode": p.get("errorCode"), "error": p.get("errorCode")}
    return {"ok": True, "taskId": str(task_id), "raw": p}


def complete_all_tasks(client):
    """快速完成全部未完成每日任务（dailyQuest2025.immediateAllTask，消耗道具）。"""
    try:
        r = client.call("dailyQuest2025.immediateAllTask")
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "error": str(e)[:160]}
    p = r.get("__params__") or {}
    if p.get("errorCode"):
        return {"ok": False, "errorCode": p.get("errorCode"), "error": p.get("errorCode")}
    return {"ok": True, "raw": p}


def claim_daily_box(client, box_id):
    """领取日活跃宝箱奖励（dailyQuest2025.reward）。"""
    params = {"id": str(box_id)}
    try:
        r = client.call("dailyQuest2025.reward", params)
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "error": str(e)[:160]}
    p = r.get("__params__") or {}
    if p.get("errorCode"):
        return {"ok": False, "errorCode": p.get("errorCode"), "error": p.get("errorCode")}
    return {"ok": True, "boxId": str(box_id), "award": p.get("award") or [],
            "randomAward": p.get("randomAward") or []}


def claim_all_boxes(client, result=None):
    """一键领取所有可领的活跃宝箱（日 + 周，不消耗道具）。

    这是目前直连协议里**唯一可安全“一键完成”的部分**：
    服务端按活跃点/周活跃点下发宝箱，已完成任务对应的宝箱可直接领取，
    不触发 quick-complete 也不消耗任何道具。

    参数:
      result: read_daily_quest(client) 的返回值；为 None 时会先拉一次。

    返回:
        {"ok": bool, "claimed": [{"kind":"daily|weekly","id":..., "point":...}],
         "skipped": [...], "error": str|None, "activePoints":..., "weeklyActivePoints":...}
    """
    if result is None:
        result = read_daily_quest(client)
    if not result.get("ok"):
        return {"ok": False, "error": result.get("error") or result.get("errorCode"),
                "claimed": [], "skipped": []}

    active = _as_int(result.get("activePoints"))
    weekly = _as_int(result.get("weeklyActivePoints"))
    got_daily = set(str(x) for x in str(result.get("dailyTaskId2025") or "").split(";") if x)
    got_weekly = set(str(x) for x in str(result.get("weekTaskRewardId2025") or "").split(";") if x)

    claimed = []
    skipped = []

    for b in result.get("boxes", []):
        bid = str(b.get("id"))
        bpoint = _as_int(b.get("point"))
        if bid in got_daily:
            skipped.append({"kind": "daily", "id": bid, "point": bpoint, "reason": "已领"})
            continue
        if active < bpoint:
            skipped.append({"kind": "daily", "id": bid, "point": bpoint,
                            "reason": "活跃点不足(%d < %d)" % (active, bpoint)})
            continue
        res = claim_daily_box(client, bid)
        if res.get("ok"):
            claimed.append({"kind": "daily", "id": bid, "point": bpoint,
                            "award": res.get("award") or []})
            got_daily.add(bid)
        else:
            skipped.append({"kind": "daily", "id": bid, "point": bpoint,
                            "reason": res.get("error") or res.get("errorCode") or "失败"})

    for wb in result.get("weekly_boxes", []):
        wid = str(wb.get("id"))
        wpoint = _as_int(wb.get("point"))
        if wid in got_weekly:
            skipped.append({"kind": "weekly", "id": wid, "point": wpoint, "reason": "已领"})
            continue
        if weekly < wpoint:
            skipped.append({"kind": "weekly", "id": wid, "point": wpoint,
                            "reason": "周活跃点不足(%d < %d)" % (weekly, wpoint)})
            continue
        res = claim_weekly_box(client, wid)
        if res.get("ok"):
            claimed.append({"kind": "weekly", "id": wid, "point": wpoint,
                            "raw": res.get("raw")})
            got_weekly.add(wid)
        else:
            skipped.append({"kind": "weekly", "id": wid, "point": wpoint,
                            "reason": res.get("error") or res.get("errorCode") or "失败"})

    return {
        "ok": True,
        "claimed": claimed,
        "skipped": skipped,
        "activePoints": active,
        "weeklyActivePoints": weekly,
    }


def claim_weekly_box(client, weekly_box_id):
    """领取周活跃宝箱奖励（dailyQuest2025.weekReward）。"""
    params = {"id": str(weekly_box_id)}
    try:
        r = client.call("dailyQuest2025.weekReward", params)
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "error": str(e)[:160]}
    p = r.get("__params__") or {}
    if p.get("errorCode"):
        return {"ok": False, "errorCode": p.get("errorCode"), "error": p.get("errorCode")}
    return {"ok": True, "weeklyBoxId": str(weekly_box_id), "raw": p}


def _print_read(result):
    if not result.get("ok"):
        print("读取失败:", result.get("error") or result.get("errorCode"))
        return
    print("=== 每日任务 ===")
    print("活跃点: %s   周活跃点: %s" % (result.get("activePoints"), result.get("weeklyActivePoints")))
    print("已领日宝箱: %s" % result.get("dailyTaskId2025") or "无")
    print("已领周宝箱: %s" % result.get("weekTaskRewardId2025") or "无")
    print()
    print("--- 每日任务列表 ---")
    for t in result.get("tasks", []):
        mark = "✓" if t["complete"] else " "
        print("[%s] %s(id=%s) 进度:%s 类型:%s 点数:%s 代价道具:%s" % (
            mark, t["name"] or t["id"], t["id"], t["progress"], t["type_label"],
            t["point"], t["costitem"]))
    print()
    print("--- 日活跃宝箱 ---")
    for b in result.get("boxes", []):
        flag = " (已领)" if not b.get("claimable") else ""
        print("宝箱 id=%s 需点数:%s%s" % (b.get("id"), b.get("point"), flag))
    print()
    print("--- 周活跃宝箱 ---")
    for wb in result.get("weekly_boxes", []):
        flag = " (已领)" if not wb.get("claimable") else ""
        print("宝箱 id=%s 需点数:%s%s" % (wb.get("id"), wb.get("point"), flag))


def main():
    ap = argparse.ArgumentParser(description="COK 每日任务直连工具")
    ap.add_argument("--host", default="42.192.152.154")
    ap.add_argument("--port", type=int, default=32231)
    ap.add_argument("--timeout", type=float, default=30.0)
    ap.add_argument("--account-device", action="store_true",
                    help="从设备 SharedPreferences 自动读取账号与服务器地址")
    ap.add_argument("--read", action="store_true", help="拉取并显示每个任务项")
    ap.add_argument("--analyze", action="store_true",
                    help="逐项分析每个任务的 gotype/go 操作、可否协议完成、协议命令")
    ap.add_argument("--claim-boxes", action="store_true",
                    help="领取所有可领的活跃宝箱(日+周)")
    ap.add_argument("--complete", metavar="TASK_ID",
                    help="快速完成单个任务(需消耗道具)")
    ap.add_argument("--complete-all", action="store_true",
                    help="快速完成全部未完成任务(需消耗道具)")
    ap.add_argument("--json", action="store_true", help="机器可读输出")
    args = ap.parse_args()

    account = {}
    if args.account_device:
        from cok_account import load_account as _la
        account = _la()

    client = CokClient(args.host, args.port, args.timeout, account)
    client.connect()
    client.bin_handshake()
    client.login()

    try:
        if args.read:
            result = read_daily_quest(client)
            if args.json:
                print(json.dumps(result, ensure_ascii=False, default=str))
            else:
                _print_read(result)
        elif args.analyze:
            result = read_daily_quest(client)
            if args.json:
                print(json.dumps({"tasks": analyze_tasks(result),
                                  "activePoints": result.get("activePoints"),
                                  "weeklyActivePoints": result.get("weeklyActivePoints")},
                                 ensure_ascii=False, default=str))
            else:
                print_analysis(result)
        elif args.claim_boxes:
            result = read_daily_quest(client)
            if not result.get("ok"):
                print(json.dumps(result, ensure_ascii=False))
                return 1
            _print_read(result)
            active = result.get("activePoints") or 0
            weekly = result.get("weeklyActivePoints") or 0
            # 这里需要重新拉取以获取准确的 activePoints 与已领记录，已在 read_daily_quest 里拿到
            got_daily = set(str(x) for x in str(result.get("dailyTaskId2025") or "").split(";") if x)
            got_weekly = set(str(x) for x in str(result.get("weekTaskRewardId2025") or "").split(";") if x)
            for b in result.get("boxes", []):
                bid = str(b.get("id"))
                bpoint = _as_int(b.get("point"))
                if bid not in got_daily and active >= bpoint:
                    res = claim_daily_box(client, bid)
                    print("[领日宝箱] id=%s -> %s" % (bid, res.get("ok") and "OK" or res.get("error")))
            for wb in result.get("weekly_boxes", []):
                wid = str(wb.get("id"))
                wpoint = _as_int(wb.get("point"))
                if wid not in got_weekly and weekly >= wpoint:
                    res = claim_weekly_box(client, wid)
                    print("[领周宝箱] id=%s -> %s" % (wid, res.get("ok") and "OK" or res.get("error")))
        elif args.complete:
            res = complete_task(client, args.complete)
            print(json.dumps(res, ensure_ascii=False, default=str))
        elif args.complete_all:
            res = complete_all_tasks(client)
            print(json.dumps(res, ensure_ascii=False, default=str))
        else:
            ap.print_help()
            return 1
    finally:
        client.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
