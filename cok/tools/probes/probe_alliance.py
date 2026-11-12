#!/usr/bin/env python3
"""联盟功能探针: 批量跑联盟相关命令, 打印真实响应结构。

用途: 摸清「联盟面板」里到底有哪些功能能直连(只读优先), 写操作默认不跑。

用法:
  python3 probe_alliance.py                 # 只跑只读命令
  python3 probe_alliance.py --writes        # 额外跑写命令(会真的提交, 慎用)
  python3 probe_alliance.py --cmd al.rank   # 只跑指定命令
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

_C = os.path.join(HERE, "..", "..", "core")
sys.path.insert(0, _C)
from cok_client import CokClient  # noqa: E402

# (命令, 参数, 说明) —— 只读
READONLY = [
    ("al.check", {}, "自身联盟状态"),
    ("al.attr", {}, "联盟属性"),
    ("al.rank", {}, "联盟排行"),
    ("al.task.record", {}, "联盟任务板记录"),
    ("al.task.get.available", {}, "可接的联盟任务"),
    ("al.task.get.published", {}, "已发布的联盟任务"),
    ("al.mission.show", {}, "联盟任务/使命"),
    ("al.donate.rank.all", {}, "捐献排行-总"),
    ("al.donate.rank.today", {}, "捐献排行-今日"),
    ("al.donate.rank.week", {}, "捐献排行-本周"),
    ("al.science.fresh", {}, "联盟科技状态"),
    ("al.shop.show", {}, "联盟商店"),
    ("al.point.find", {}, "联盟成员点位"),
    ("al.ref.cnt", {}, "联盟推荐"),
    ("al.ref.list", {}, "联盟推荐列表"),
    ("al.userapplylist", {}, "入盟申请列表"),
    ("al.commentview", {}, "联盟留言"),
    ("allianceNewBoss.bossMainInfo", {}, "联盟BOSS"),
    ("allianceBoss.enter", {}, "联盟BOSS入口"),
    ("alquick.data", {}, "联盟一键信息"),
    ("allianceTax.data", {}, "联盟税收"),
    ("allianceCiviSkill.getView", {}, "联盟文明技能"),
    ("allianceNewBuilding.data", {}, "联盟新建筑"),
    ("alliancebounty.openUI", {}, "联盟赏金"),
    ("alliance.recharge.getRank", {}, "联盟充值排行"),
    ("alliance.team.ls", {}, "联盟集结列表"),
    ("allianceMillitaryPower", {}, "联盟战力"),
    ("dragonBattle8.allianceInfo", {}, "龙战联盟信息"),
]

# 第二轮: 修正命令名 + 带上反出来的参数
ROUND2 = [
    ("territory.check", {}, "联盟领地(正确命令名)"),
    ("al.donate.res.info", {}, "资源捐献信息"),
    ("al.shop.show", {"type": 12}, "联盟商店(分类12)"),
    ("al.shop.show", {"type": 23}, "联盟商店(分类23)"),
    ("al.science.fresh", {"type": 1}, "联盟科技刷新(t=1)"),
    ("al.science.donate.cd", {"scienceId": 0}, "捐献CD(带scienceId)"),
    ("al.task.get.detail", {"taskUid": ""}, "任务详情(空uid看报错)"),
    ("al.mission.show", {"type": 1}, "联盟使命(t=1)"),
    ("alquick.data", {}, "一键信息"),
    ("mine.help.info", {}, "我的帮助信息"),
    ("al.commentview", {"allianceId": ""}, "联盟留言(带id)"),
    ("allianceScience.info", {}, "联盟科技信息"),
    ("science.data.init", {}, "科技初始化(含allianceScience)"),
    ("al.event", {}, "联盟事件"),
    ("al.fight.bulletin", {}, "联盟战报公告"),
    ("allianceChest.simpleInfo", {}, "联盟宝箱"),
    ("al.science.donate", {"scienceId": 0}, "科技捐献(占位, 勿真跑)"),
    ("al.task.get.available", {"id": 0}, "可接任务(带id)"),
    ("al.task.get.published", {"id": 0}, "已发布任务(带id)"),
    ("al.rank", {"allianceId": ""}, "联盟排行(带id)"),
    ("al.abbr", {}, "联盟缩写"),
    ("al.search", {"name": ""}, "搜索联盟"),
    ("al.comment", {}, "联盟留言板"),
    ("al.get.url", {}, "联盟跳转url"),
]

# 第三轮: 带真实 id 的定向探测
ROUND3 = [
    ("signIn.info", {}, "签到信息(疑似联盟签到)"),
    ("signIn.reward", {}, "签到领取(写, 谨慎)"),
    ("al.task.get.detail", {"taskUid": "e79590911f504fba8331e518f9da0240"}, "任务详情(真实uid)"),
    ("al.task.get.detail", {"taskUid": "10462f0fc960476d8bbd8f46b24176f1"}, "任务详情(自己的)"),
    ("al.science.fresh", {"scienceId": 251600}, "科技刷新(真实scienceId)"),
    ("al.science.donate.cd", {"scienceId": 251600}, "捐献CD(真实scienceId)"),
    ("al.donate.rank.today", {}, "今日捐献排行"),
    ("al.mission.show", {}, "联盟使命"),
    ("al.check", {"allianceId": "30e750abfa2745289e13e1f4377a0976"}, "联盟检查(带id)"),
    ("al.attr", {"allianceId": "30e750abfa2745289e13e1f4377a0976"}, "联盟属性(带id)"),
    ("al.rank", {"allianceId": "30e750abfa2745289e13e1f4377a0976"}, "联盟排行(真实id)"),
    ("al.commentview", {"allianceId": "30e750abfa2745289e13e1f4377a0976"}, "联盟留言(真实id)"),
    ("al.userapplylist", {"allianceId": "30e750abfa2745289e13e1f4377a0976"}, "入盟申请(真实id)"),
    ("al.science.fresh.new", {"scienceId": 251600}, "科技刷新(新版)"),
    ("al.ref.cnt", {"allianceId": "30e750abfa2745289e13e1f4377a0976"}, "联盟推荐数(真实id)"),
]

# (命令, 参数, 说明) —— 写操作
WRITES = [
    ("al.callhelp", {}, "请求联盟帮助"),
    ("al.helpall", {}, "帮助全体"),
    ("al.science.donate", {}, "捐献科技"),
    ("al.science.donate.new", {}, "捐献科技(新版)"),
    ("al.task.accept", {}, "接受联盟任务"),
    ("al.task.award", {}, "领取联盟任务奖励"),
    ("al.task.publish", {}, "发布联盟任务"),
    ("al.task.refresh", {}, "刷新联盟任务"),
    ("al.shop.buy.al", {}, "联盟商店购买"),
    ("al.shop.buy.usr", {}, "个人商店购买"),
    ("al.targetscience.set", {"isuse": 0, "scienceId": 0}, "设置捐献目标科技"),
    ("al.mission.reward", {}, "领取联盟使命奖励"),
]


def brief(value, depth=0):
    """把响应压成可读的结构摘要。"""
    if isinstance(value, dict):
        out = {}
        for k, v in value.items():
            if k.startswith("_cok_"):
                continue
            out[k] = brief(v, depth + 1) if depth < 3 else type(v).__name__
        return out
    if isinstance(value, list):
        return ["<%d items>" % len(value)] + (
            [brief(value[0], depth + 1)] if value and depth < 2 else [])
    if isinstance(value, str) and len(value) > 80:
        return value[:80] + "..."
    return value


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--writes", action="store_true", help="额外跑写操作")
    ap.add_argument("--round", default="1", choices=["1", "2", "3", "all"], help="命令批次")
    ap.add_argument("--cmd", action="append", help="只跑指定命令(可重复)")
    ap.add_argument("--full", action="store_true", help="打印完整响应")
    ap.add_argument("--timeout", type=float, default=8.0, help="单命令超时(秒)")
    args = ap.parse_args()

    cmds = {"2": ROUND2, "3": ROUND3}.get(args.round,
            READONLY + ROUND2 + ROUND3 if args.round == "all" else READONLY)
    if args.writes:
        cmds = cmds + list(WRITES)
    if args.cmd:
        want = set(args.cmd)
        cmds = [c for c in cmds if c[0] in want] or [
            (c, {}, "") for c in args.cmd]

    c = CokClient(timeout=args.timeout)
    c.connect()
    c.bin_handshake()
    c.login()
    try:
        c.call("cmd.ping")
    except Exception:  # noqa: BLE001
        pass

    results = {}
    for cmd, params, note in cmds:
        try:
            r = c.call(cmd, params or None)
            p = r.get("__params__") or {}
            err = p.get("errorCode") if isinstance(p, dict) else None
            results[cmd] = {"status": "ERR" if err else "OK",
                            "errorCode": err, "params": brief(p)}
            print("  %-3s %-32s %s" % ("ERR" if err else "OK", cmd, note))
            if args.full:
                print(json.dumps(results[cmd], ensure_ascii=False, indent=1)[:4000])
            else:
                s = json.dumps(brief(p), ensure_ascii=False)
                print("        " + s[:300])
        except Exception as e:  # noqa: BLE001
            results[cmd] = {"status": "TO", "error": str(e)[:200]}
            print("  TO  %-32s %s" % (cmd, str(e)[:100]))
        sys.stdout.flush()

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "evidence", "alliance-probe-r%s.json" % args.round)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=1)
    print("\n-> %s" % out)
    c.close()


if __name__ == "__main__":
    main()
