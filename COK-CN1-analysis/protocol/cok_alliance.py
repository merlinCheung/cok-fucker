#!/usr/bin/env python3
"""COK 联盟功能直连封装(2026-10-30 实测)。

覆盖联盟面板里**能直连**的部分:
  * 联盟科技树(在研/进度/星级)
  * 科技捐献面板(三档: 低/中/高 —— 消耗/贡献/进度)
  * 联盟任务板(可接 / 已发布 / 详情 / 接取 / 领奖)
  * 联盟使命 + 5 天一轮的联盟签到
  * 捐献排行(总/今日/本周)
  * 联盟资源池(可捐资源与道具)
  * 联盟商店(联盟积分 + 商品)
  * 联盟求助(请求帮助 / 帮助全体 / 查看求助)

命令与参数(实测口径, 详见 ALLIANCE.md):
  读  al.rank                (无参 或 allianceId)
      al.task.record         (无参)
      al.task.get.available  (无参)
      al.task.get.published  (无参)
      al.task.get.detail     {taskUid}
      al.mission.show        (无参)
      al.donate.rank.all/today/week
      al.donate.res.info     (无参)
      al.shop.show           (无参)
      science.data.init      (无参) -> allianceScience[] 联盟科技树
      al.science.fresh       {scienceId} -> 捐献面板
      al.showhelp            (无参)
  写  al.task.accept         {taskUid}                    ✅ 实测成功
      al.task.award          {taskUid}                    ✅ 命令通(未完成时业务拦)
      al.callhelp            {queueId, qType}             ✅ 实测成功
      al.helpall             (无参)                       ✅ 实测成功
      al.science.donate      {scienceId, option}          🧩 参数已定(无可捐目标)
      al.task.publish        {publishName, finishTime, acceptReward, ...}

⚠ 写操作都是**真副作用**: 捐献消耗资源, 接任务占用任务位(上限 10),
   领奖消耗一次性奖励。所有写函数都返回 {ok, errorCode, error, ...},
   失败时把服务端错误码原样带出来(页面据此提示)。
"""

import time

# ---------------------------------------------------------------------------
# 联盟资源类型 id -> 中文名
# 服务端 al.donate.res.info / al.science.fresh 里的 res 用的是数字 id:
#   0/1/2/3 = 基础资源, 21~25 = 高级资源
# ⚠ 客户端配置表里**没有**资源 id -> 名称的权威映射(查过 database.local.xml),
#   只有 alliance_tree_v2_health_val_donate 把 21~24 标成"联盟生命值"道具
#   (health_val 1/10/15/20)。所以这里只给确定的, 其余显示成"资源#N",
#   宁可显示 id 也不给错名字。
# ---------------------------------------------------------------------------
RESOURCE_NAMES = {
    "21": "联盟生命值·一档",
    "22": "联盟生命值·二档",
    "23": "联盟生命值·三档",
    "24": "联盟生命值·四档",
    "25": "联盟生命值·五档",
}

#: 捐献档位 -> (面板字段前缀, 中文名, option 候选值)
#:
#: 客户端 native 里 `al.science.donate` 的参数是 `{scienceId:INT, option:INT}`,
#: option 来自 UI 选中的档位。0-based 与 1-based 两种基准下同一档位分别是:
#:   低档 0 / 1      中档 1 / 2      高档 2 / 3
#: ⚠ **候选值会跨档位**(0-based 时 option=1 是中档), 所以换候选**只能**在
#:    服务端回 `E000000`(参数无效)时进行; 其它错误码(冷却 E100160 /
#:    已满 E100126 / 权限不足)必须原样停下, 否则会捐错档位。
DONATE_TIERS = (
    ("low", "低档", (0, 1)),
    ("mid", "中档", (1, 2)),
    ("high", "高档", (2, 3)),
)

#: 捐献相关的服务端错误码 -> (是否"已达上限", 中文说明)
DONATE_STOP = {
    "E100126": (True, "该科技已进入可研究状态, 进度已满(达到本次捐献上限)"),
    "E100160": (False, "捐献冷却中, 等冷却结束再捐"),
    "E100125": (False, "加入联盟 4 小时内无法捐献"),
    "E100124": (True, "该联盟科技已到最大等级"),
}

#: 客户端错误码文案(来自 assets/local/text_zh_CN.ini, 挑了联盟相关的)
ERROR_TEXT = {
    "E000000": "操作无效, 请再次尝试",
    "E100120": "您不是该联盟的成员",
    "E100121": "没找到联盟",
    "E100123": "未找到对应项目",
    "E100124": "联盟科技已到最大等级",
    "E100125": "加入联盟4小时内无法捐献",
    "E100126": "该科技已进入可研究状态, 无法继续捐献",
    "E100160": "冷却时间未到, 请稍后尝试",
    "E100167": "请求服务器失败, 请稍后尝试",
    "134042": "任务未完成, 暂时不能领奖",
}


def _now_ms():
    return int(time.time() * 1000)


def _err_text(code):
    code = str(code or "")
    if code in ERROR_TEXT:
        return ERROR_TEXT[code]
    return ""


def _call(client, cmd, params=None):
    """发一条命令, 返回 (ok, params, errorCode, errorText)。

    retries=2: 每条连接的第一条业务请求会被服务端丢弃(铁律四), 重试能兜住。
    """
    try:
        r = client.call(cmd, params, retries=2)
    except Exception as e:  # noqa: BLE001
        return False, {}, "TIMEOUT", str(e)[:160]
    p = r.get("__params__") or {}
    code = p.get("errorCode")
    if code:
        return False, p, str(code), _err_text(code)
    return True, p, None, ""


def _int(v, default=0):
    try:
        return int(v)
    except (TypeError, ValueError):
        return default


# ---------------------------------------------------------------------------
# 读
# ---------------------------------------------------------------------------

def read_science(client):
    """联盟科技树(science.data.init 的 allianceScience[])。

    返回 {ok, list[], researching, count}
      list[] 每项: scienceId, level, star, currentPro, needPro, totalPro,
                   startTime, finishTime, speedUp, researching, full, percent
      researching = 正在研究的科技 scienceId(没有则空)
    """
    ok, p, code, msg = _call(client, "science.data.init")
    if not ok:
        return {"ok": False, "errorCode": code, "error": msg, "list": []}
    now = _now_ms()
    out = []
    researching = ""
    for s in (p.get("allianceScience") or []):
        if not isinstance(s, dict):
            continue
        sid = s.get("scienceId")
        cur = _int(s.get("currentPro"))
        need = _int(s.get("needPro"))
        start = _int(s.get("startTime"))
        finish = _int(s.get("finishTime"))
        # 在研 = 有 startTime 且(没 finishTime 或还没到期)
        # ⚠ finishTime 可能还没填(服务端刚开研究), 那时不能判成"没在研"——
        #   漏判会让自动捐献整轮跳过, 白等一轮。
        inprog = bool(start) and (not finish or finish > now)
        if inprog:
            researching = str(sid)
        out.append({
            "scienceId": str(sid),
            "level": _int(s.get("level")),
            "star": _int(s.get("star")),
            "currentPro": cur,
            "needPro": need,
            "totalPro": _int(s.get("totalPro")),
            "startTime": start,
            "finishTime": finish,
            "speedUp": bool(s.get("speedUp")),
            "researching": inprog,
            # 进度已满 = 服务端认为"已进入可研究状态", 这时不能再捐献(E100126)
            "full": bool(need) and cur >= need,
            "percent": int(cur * 100 / need) if need else 0,
        })
    return {"ok": True, "list": out, "researching": researching, "count": len(out)}


def read_donate_panel(client, science_id):
    """科技捐献面板(al.science.fresh {scienceId})。

    返回 {ok, scienceId, tiers[{key,name,res,resName,num,contribute,progress,
                                available}], canDonate, reason}
      available: 该档位服务端是否开放(None = 服务端没这个字段, 低档默认开放)
      canDonate: 现在能不能捐
      reason: 不能捐的原因(中文)
    """
    ok, p, code, msg = _call(client, "al.science.fresh", {"scienceId": _int(science_id)})
    if not ok:
        return {"ok": False, "errorCode": code, "error": msg, "tiers": []}
    tiers = []
    for key, name, _opts in DONATE_TIERS:
        # 服务端字段是 lowRes / lowNum / lowContribute / lowProgress / lowResFlag
        # (小写前缀), 只给 mid/high 额外的 Available
        def _g(suffix):
            return p.get(key + suffix)
        tiers.append({
            "key": key,
            "name": name,
            "res": _g("Res"),
            "resName": RESOURCE_NAMES.get(str(_g("Res")), ""),
            "num": _g("Num"),
            "contribute": _g("Contribute"),
            "progress": _g("Progress"),
            "resFlag": _g("ResFlag"),
            # 服务端只给 mid/high 的 Available, 低档没这个字段 -> 视为开放
            "available": _g("Available"),
        })
    open_tiers = [t for t in tiers if t["available"] in (None, 1, True)]
    return {
        "ok": True,
        "scienceId": str(p.get("scienceId") or science_id),
        "tiers": tiers,
        "canDonate": bool(open_tiers),
        "reason": "" if open_tiers else "该科技当前没有开放的捐献档位",
    }


def read_task_board(client):
    """联盟任务板(可接 / 已发布 / 记录)。

    返回 {ok, record, available[], published[], leftRequestCount, myTasks[]}
      myTasks[] = 自己发布或已接的任务
    """
    ok, p, code, msg = _call(client, "al.task.get.published")
    if not ok:
        return {"ok": False, "errorCode": code, "error": msg,
                "available": [], "published": [], "myTasks": []}
    published = [t for t in (p.get("taskList") or []) if isinstance(t, dict)]
    left = _int(p.get("leftRequestCount"))

    ok2, p2, code2, msg2 = _call(client, "al.task.get.available")
    available = []
    record = {}
    if ok2:
        available = [t for t in (p2.get("taskList") or []) if isinstance(t, dict)]
        record = dict(p2.get("record") or {})

    # al.task.record 才有上限字段(maxAcceptCount / maxPublishCount / 金币价)
    ok3, p3, _c3, _m3 = _call(client, "al.task.record")
    if ok3:
        limits = {k: v for k, v in p3.items() if k != "_cok_"}
        limits.update(record)   # available 里的实时计数优先
        record = limits

    mine = []
    for t in published + available:
        if t.get("acceptUid") or t.get("publishUid") == _self_uid(record):
            mine.append(_task_view(t))

    return {
        "ok": True,
        "record": {
            "acceptCount": _int(record.get("acceptCount")),
            "maxAcceptCount": _int(record.get("maxAcceptCount")),
            "publishCount": _int(record.get("publishCount")),
            "maxPublishCount": _int(record.get("maxPublishCount")),
            "gold": _int(record.get("gold")),
            "nextGold": _int(record.get("nextGold")),
            "freequeue": _int(record.get("freequeue")),
            "refreshCount": _int(record.get("refreshCount")),
            "maxFreeRefreshCount": _int(record.get("maxFreeRefreshCount")),
            "conditionAcceptLevel": _int(record.get("conditionAcceptLevel")),
            "conditionPublishLevel": _int(record.get("conditionPublishLevel")),
        },
        "available": [_task_view(t) for t in available],
        "published": [_task_view(t) for t in published],
        "leftRequestCount": left,
        "myTasks": mine,
    }


def _self_uid(record):
    """任务板记录里没有自己的 uid, 这里返回空(调用方不依赖它)。"""
    return ""


def _task_view(t):
    return {
        "uid": str(t.get("uid") or ""),
        "taskId": str(t.get("taskId") or ""),
        "publishName": str(t.get("publishName") or ""),
        "publishUid": str(t.get("publishUid") or ""),
        "acceptName": str(t.get("acceptName") or ""),
        "acceptUid": str(t.get("acceptUid") or ""),
        "acceptStat": _int(t.get("acceptStat")),
        "publishStat": _int(t.get("publishStat")),
        "stat": _int(t.get("stat")),
        "requested": bool(t.get("requested")),
        "freequeue": _int(t.get("freequeue")),
        "startTime": _int(t.get("startTime")),
        "finishTime": _int(t.get("finishTime")),
        "publishTime": _int(t.get("publishTime")),
        "vanishTime": _int(t.get("vanishTime")),
        "pic": str(t.get("pic") or ""),
        "acceptReward": str(t.get("acceptReward") or ""),
        "baseReward": str(t.get("baseReward") or ""),
    }


def read_mission(client):
    """联盟使命 + 联盟签到(al.mission.show)。

    返回 {ok, common[], random[], signIn{signIn_reward, signInReward_state, signIn_days}}
    """
    ok, p, code, msg = _call(client, "al.mission.show")
    if not ok:
        return {"ok": False, "errorCode": code, "error": msg, "common": [], "random": []}

    def _missions(arr):
        out = []
        for m in (arr or []):
            if not isinstance(m, dict):
                continue
            conds = str(m.get("conditionValue") or "")
            flags = str(m.get("rewardFlag") or "")
            vals = conds.split("|") if conds else []
            fs = flags.split("|") if flags else []
            cur = m.get("currentValue")
            stages = []
            for i, c in enumerate(vals):
                try:
                    cv = int(c)
                except ValueError:
                    cv = 0
                try:
                    cval = int(cur)
                except (TypeError, ValueError):
                    cval = 0
                stages.append({
                    "target": cv,
                    "reached": cval >= cv,
                    "claimed": fs[i] == "1" if i < len(fs) else False,
                })
            out.append({
                "missionId": str(m.get("missionId") or ""),
                "type": _int(m.get("type")),
                "currentValue": cur,
                "conditionValue": conds,
                "rewardFlag": flags,
                "rewardRecord": str(m.get("rewardRecord") or ""),
                "refreshTime": _int(m.get("refreshTime")),
                "stages": stages,
                "done": all(s["reached"] and s["claimed"] for s in stages) if stages else False,
            })
        return out

    sign = p.get("alliance_sign_in") or {}
    return {
        "ok": True,
        "common": _missions(p.get("common")),
        "random": _missions(p.get("random")),
        "signIn": {
            "signIn_reward": str(sign.get("signIn_reward") or ""),
            "signInReward_state": _int(sign.get("signInReward_state")),
            "signIn_days": _int(sign.get("signIn_days")),
        },
    }


def read_donate_rank(client):
    """捐献排行(今日)。返回 {ok, list[], me}"""
    ok, p, code, msg = _call(client, "al.donate.rank.today")
    if not ok:
        return {"ok": False, "errorCode": code, "error": msg, "list": []}
    lst = []
    for t in (p.get("donateRank") or []):
        if not isinstance(t, dict):
            continue
        lst.append({
            "uid": str(t.get("uid") or ""),
            "name": str(t.get("name") or ""),
            "donation": _int(t.get("donation")),
            "rank": _int(t.get("rank")),
            "power": _int(t.get("power")),
            "alliance_honor": _int(t.get("alliance_honor")),
            "donateTime": _int(t.get("donateTime")),
        })
    return {"ok": True, "list": lst, "refreshTime": _int(p.get("refreshTime"))}


def read_res(client):
    """联盟资源池(al.donate.res.info)。返回 {ok, res{}, resMax{}, item[]}"""
    ok, p, code, msg = _call(client, "al.donate.res.info")
    if not ok:
        return {"ok": False, "errorCode": code, "error": msg}
    res = {}
    for k, v in (p.get("res") or {}).items():
        res[str(k)] = {
            "have": _int(v),
            "max": _int((p.get("resMax") or {}).get(k)),
            "name": RESOURCE_NAMES.get(str(k)) or ("资源#%s" % k),
        }
    items = []
    for it in (p.get("item") or []):
        if not isinstance(it, dict):
            continue
        for iid, num in it.items():
            items.append({"itemId": str(iid), "num": _int(num)})
    return {"ok": True, "res": res, "item": items}


def read_shop(client):
    """联盟商店(al.shop.show)。返回 {ok, alliancePoint, goods[]}"""
    ok, p, code, msg = _call(client, "al.shop.show")
    if not ok:
        return {"ok": False, "errorCode": code, "error": msg, "goods": []}
    goods = []
    for g in (p.get("goods") or []):
        if not isinstance(g, dict):
            continue
        goods.append({
            "id": str(g.get("id") or g.get("goodsId") or ""),
            "name": str(g.get("name") or ""),
            "num": _int(g.get("num")),
            "type": g.get("type"),
            "price": g.get("price") or g.get("value"),
        })
    return {"ok": True, "alliancePoint": _int(p.get("alliancePoint")), "goods": goods}


def read_help(client):
    """我的求助(al.showhelp)。返回 {ok, helps[]}"""
    ok, p, code, msg = _call(client, "al.showhelp")
    if not ok:
        return {"ok": False, "errorCode": code, "error": msg, "helps": []}
    helps = []
    for h in (p.get("helps") or []):
        if not isinstance(h, dict):
            continue
        helps.append({k: v for k, v in h.items() if k != "_cok_"})
    return {"ok": True, "helps": helps}


def read_sign_in(client):
    """联盟签到状态(来自 `al.mission.show` 的 `alliance_sign_in`)。

    返回 {ok, signed, days, reward}
      signed = True 表示今天已经签过
      days   = 连续签到天数
      reward = 今天的奖励道具 id
    """
    m = read_mission(client)
    if not m.get("ok"):
        return {"ok": False, "error": m.get("error") or "联盟使命读取失败",
                "signed": False, "days": 0, "reward": ""}
    sign = m.get("signIn") or {}
    return {
        "ok": True,
        "signed": _int(sign.get("signInReward_state")) == 1,
        "days": _int(sign.get("signIn_days")),
        "reward": sign.get("signIn_reward") or "",
    }


def claim_sign_in(client):
    """领取联盟签到奖励(`alliance.signIn.reward`, **无参**)。

    ⚠ 真副作用: 每天一次, 领完 `signInReward_state` 变 1。

    命令名是 `alliance.signIn.reward` —— 不是 `signIn.reward`(那个会回 102192
    "功能未开启")。2026-10-31 实测: 领到 goods 若干(道具/资源), 状态 0 -> 1。
    """
    ok, p, code, msg = _call(client, "alliance.signIn.reward")
    if not ok:
        return {"ok": False, "errorCode": code, "error": msg or "签到失败"}
    reward = p.get("reward")
    goods = []
    if isinstance(reward, dict):
        for g in (reward.get("goods") or []):
            if isinstance(g, dict):
                goods.append({"itemId": str(g.get("itemId") or ""),
                              "count": _int(g.get("count"))})
    return {"ok": True, "count": len(goods), "goods": goods}


def read_all(client, science_id=None):
    """一次读齐联盟面板(单个失败不影响其它)。"""
    out = {"ok": True}
    for key, fn in (("science", read_science), ("task", read_task_board),
                    ("mission", read_mission), ("donateRank", read_donate_rank),
                    ("res", read_res), ("shop", read_shop), ("help", read_help)):
        try:
            out[key] = fn(client)
        except Exception as e:  # noqa: BLE001
            out[key] = {"ok": False, "error": str(e)[:160]}
    # 捐献面板跟着"在研的科技"走
    sid = science_id
    if not sid:
        sci = out.get("science") or {}
        sid = sci.get("researching") or ""
    if sid:
        try:
            out["donatePanel"] = read_donate_panel(client, sid)
        except Exception as e:  # noqa: BLE001
            out["donatePanel"] = {"ok": False, "error": str(e)[:160], "tiers": []}
    else:
        out["donatePanel"] = {"ok": False, "tiers": [], "canDonate": False,
                              "reason": "当前没有正在研究的联盟科技"}
    return out


# ---------------------------------------------------------------------------
# 写
# ---------------------------------------------------------------------------

def accept_task(client, task_uid):
    """接取联盟任务(al.task.accept {taskUid})。

    ⚠ 真副作用: 占用一个任务位(上限 al.task.record.maxAcceptCount)。
    """
    uid = str(task_uid or "").strip()
    if not uid:
        return {"ok": False, "error": "缺少 taskUid"}
    ok, p, code, msg = _call(client, "al.task.accept", {"taskUid": uid})
    if not ok:
        return {"ok": False, "errorCode": code, "error": msg or "接取失败"}
    return {
        "ok": True,
        "taskUid": uid,
        "publishName": str(p.get("publishName") or ""),
        "acceptName": str(p.get("acceptName") or ""),
        "acceptUid": str(p.get("acceptUid") or ""),
        "finishTime": _int(p.get("finishTime")),
        "record": p.get("record") or {},
    }


def accept_tasks(client, limit=None):
    """接取所有可接的联盟任务(受 maxAcceptCount 限制)。

    返回 {ok, acted[], failed[], left}
    """
    board = read_task_board(client)
    if not board.get("ok"):
        return {"ok": False, "error": board.get("error") or "任务板读取失败",
                "acted": [], "failed": []}
    rec = board.get("record") or {}
    left = _int(rec.get("maxAcceptCount")) - _int(rec.get("acceptCount"))
    if left <= 0:
        return {"ok": True, "acted": [], "failed": [],
                "left": 0, "note": "任务位已满"}
    if limit:
        left = min(left, int(limit))
    acted = []
    failed = []
    for t in (board.get("published") or []):
        if len(acted) >= left:
            break
        if t.get("requested") or t.get("acceptUid"):
            continue
        r = accept_task(client, t.get("uid"))
        if r.get("ok"):
            acted.append(t.get("publishName") or t.get("uid"))
        else:
            failed.append("%s(%s)" % (t.get("publishName") or t.get("uid"),
                                      r.get("errorCode") or r.get("error") or "失败"))
    return {"ok": True, "acted": acted, "failed": failed, "left": left - len(acted)}


def award_task(client, task_uid):
    """领取联盟任务奖励(al.task.award {taskUid})。

    ⚠ 真副作用: 消耗一次性奖励。任务没完成时服务端回 134042。
    """
    uid = str(task_uid or "").strip()
    if not uid:
        return {"ok": False, "error": "缺少 taskUid"}
    ok, p, code, msg = _call(client, "al.task.award", {"taskUid": uid})
    if not ok:
        return {"ok": False, "errorCode": code, "error": msg or "领奖失败"}
    return {"ok": True, "taskUid": uid, "params": {k: v for k, v in p.items() if k != "_cok_"}}


def call_help(client, queue_id, qtype=0):
    """向联盟请求帮助(al.callhelp {queueId, qType})。

    ⚠ 真副作用: 会向联盟广播求助(玩家在游戏里点"请求帮助"是同一个动作)。
    """
    qid = str(queue_id or "").strip()
    if not qid:
        return {"ok": False, "error": "缺少 queueId"}
    ok, _p, code, msg = _call(client, "al.callhelp",
                              {"queueId": qid, "qType": _int(qtype)})
    if not ok:
        return {"ok": False, "errorCode": code, "error": msg or "求助失败"}
    return {"ok": True, "queueId": qid, "qType": _int(qtype)}


def help_all(client):
    """帮助联盟全体(al.helpall)。⚠ 真副作用。"""
    ok, _p, code, msg = _call(client, "al.helpall")
    if not ok:
        return {"ok": False, "errorCode": code, "error": msg or "操作失败"}
    return {"ok": True}


def donate(client, science_id, tier="low"):
    """捐献联盟科技(al.science.donate {scienceId, option})。

    tier: "low" / "mid" / "high"
    ⚠ 真副作用: 消耗资源, 换联盟贡献 + 科技进度。

    option 编码: 客户端 native 里 option 来自 UI 选中的档位, 0-based 还是
    1-based 未定死(见 DONATE_TIERS 注释)。本函数**只在服务端回 E000000
    (参数无效)** 时才换候选编码 —— 其它错误码(冷却/已满/权限)原样返回,
    避免换候选时跨到别的档位去(那会捐错档, 白花钱)。
    """
    sid = _int(science_id)
    if not sid:
        return {"ok": False, "error": "缺少 scienceId"}
    key = str(tier or "low").lower()
    spec = None
    for k, name, opts in DONATE_TIERS:
        if k == key:
            spec = (name, opts)
            break
    if not spec:
        return {"ok": False, "error": "档位只能是 low / mid / high"}
    name, opts = spec

    last = None
    for opt in opts:
        ok, _p, code, msg = _call(client, "al.science.donate",
                                  {"scienceId": sid, "option": opt})
        if ok:
            return {"ok": True, "scienceId": sid, "tier": key, "tierName": name,
                    "option": opt}
        last = {"errorCode": code, "error": msg}
        if code != "E000000":
            # 不是"参数无效", 换编码重试有可能跨档位 -> 直接停
            break
    done, why = DONATE_STOP.get(str((last or {}).get("errorCode") or ""), (False, ""))
    return {"ok": False, "scienceId": sid, "tier": key, "tierName": name,
            "errorCode": (last or {}).get("errorCode"),
            "error": (last or {}).get("error") or "捐献失败",
            "stop": why, "reachedCap": done}


def available_tiers(panel):
    """从捐献面板里挑出**当前可捐**的档位。

    服务端只给 mid/high 的 `Available` 字段, 低档没这个字段 -> 低档是默认档,
    视为可捐。`Available` = 1 表示开放, 0 表示不可捐。
    """
    out = []
    for t in ((panel or {}).get("tiers") or []):
        av = t.get("available")
        if av in (None, 1, True, "1"):
            out.append(t)
    return out


def pick_tier(tiers, mode="random", rng=None):
    """按模式挑一个档位。

    mode: "random" 随机挑 / "low" "mid" "high" 固定档 / "cheapest" 消耗最少
    """
    if not tiers:
        return None
    if mode == "cheapest":
        def _n(t):
            try:
                return int(t.get("num"))
            except (TypeError, ValueError):
                return 10 ** 9
        return sorted(tiers, key=_n)[0]
    if mode in ("low", "mid", "high"):
        for t in tiers:
            if t.get("key") == mode:
                return t
        return None
    if mode != "random":
        # ⚠ 模式写错**不能**静默退化成随机 —— 那会捐出用户没指定的档位。
        return None
    if rng is None:
        import random as _r
        rng = _r.Random()
    return rng.choice(tiers)


def auto_donate(client, tier_mode="random", max_iter=20, rng=None):
    """**自动捐献**: 挑一个可捐档位捐下去, 直到科技进度攒满(达到上限)为止。

    规则:
      * 目标 = **正在研究**的那个科技(同时只能研究一个, 客户端文案 115807)
      * 每次**随机**挑一个当前开放的档位
      * 进度满(currentPro >= needPro)或服务端回 E100126 -> **停**
      * 捐献冷却(E100160) -> 停, 等下一轮
      * 单轮最多 max_iter 次(防跑飞的安全兜底)

    ⚠ **绝不**调用 `al.science.research`(花金币开启/重置研究)和
      `al.targetscience.set`(改捐献目标, 要 R5 权限) —— 这两个会动金币。
    """
    out = {"ok": True, "acted": [], "stop": "", "done": False,
           "scienceId": "", "tier": "", "iterations": 0, "capReached": False}
    sci = read_science(client)
    if not sci.get("ok"):
        out["ok"] = False
        out["stop"] = sci.get("error") or "联盟科技读取失败"
        return out
    sid = sci.get("researching") or ""
    if not sid:
        out["stop"] = "当前没有正在研究的联盟科技"
        return out
    out["scienceId"] = sid

    for _ in range(max(1, int(max_iter or 1))):
        panel = read_donate_panel(client, sid)
        if not panel.get("ok"):
            out["stop"] = "捐献面板读取失败: %s" % (panel.get("error") or "")
            break
        tiers = available_tiers(panel)
        if not tiers:
            out["stop"] = "当前没有开放的捐献档位"
            break
        tier = pick_tier(tiers, tier_mode, rng)
        if tier is None:
            out["stop"] = "没有符合条件的档位(模式 %s)" % tier_mode
            break
        r = donate(client, sid, tier.get("key"))
        out["iterations"] += 1
        out["tier"] = tier.get("key")
        if r.get("ok"):
            out["acted"].append({
                "tier": tier.get("key"),
                "tierName": tier.get("name"),
                "option": r.get("option"),
                "contribute": tier.get("contribute"),
                "progress": tier.get("progress"),
                "res": tier.get("res"),
                "num": tier.get("num"),
            })
            continue
        code = str(r.get("errorCode") or "")
        out["stop"] = r.get("stop") or r.get("error") or "捐献失败"
        if r.get("reachedCap") or code == "E100126":
            out["done"] = True
            out["capReached"] = True
            break
        # 服务端对"进度已满"有时回的是笼统的 E000000(操作无效),
        # 所以再读一次进度, 确认到底是"满了"还是别的原因。
        try:
            probe = read_science(client)
            for s in (probe.get("list") or []):
                if str(s.get("scienceId")) == str(sid) and s.get("full"):
                    out["stop"] = "该科技进度已满(达到本次捐献上限)"
                    out["done"] = True
                    out["capReached"] = True
                    break
        except Exception:  # noqa: BLE001
            pass
        break
    else:
        out["stop"] = "达到单轮上限 %d 次, 已停止" % max_iter

    # 最后再读一次进度, 报告当前状态(顺便确认是否已满)
    try:
        sci2 = read_science(client)
        for s in (sci2.get("list") or []):
            if str(s.get("scienceId")) == str(sid):
                out["progress"] = "%s/%s" % (s.get("currentPro"), s.get("needPro"))
                out["full"] = bool(s.get("full"))
                if s.get("full") and not out["done"]:
                    out["done"] = True
                    out["capReached"] = True
                    out["stop"] = out["stop"] or "该科技进度已满(达到本次捐献上限)"
                break
    except Exception:  # noqa: BLE001
        pass
    return out


def publish_task(client, publish_name, finish_time, accept_reward,
                 item_id=None, item_num=0, freequeue=1, pic="g015"):
    """发布联盟任务(al.task.publish)。

    参数(静态反出, 未在真服验证过):
      publishName  任务标题
      finishTime   有效时长(毫秒)
      acceptReward 奖励串, 格式 "exp,0,9408|goods,36006801,1"
      freequeue    是否占用免费队列位
      itemId/itemNum 消耗的道具(可选)
    ⚠ 真副作用: 占用一个发布位(上限 8), 首次发布可能扣金币。
    """
    name = str(publish_name or "").strip()
    if not name:
        return {"ok": False, "error": "缺少任务标题"}
    params = {
        "publishName": name,
        "finishTime": _int(finish_time),
        "acceptReward": str(accept_reward or ""),
        "freequeue": _int(freequeue),
        "pic": str(pic or ""),
    }
    if item_id:
        params["itemId"] = str(item_id)
        params["itemNum"] = _int(item_num)
    ok, p, code, msg = _call(client, "al.task.publish", params)
    if not ok:
        return {"ok": False, "errorCode": code, "error": msg or "发布失败"}
    return {"ok": True, "params": {k: v for k, v in p.items() if k != "_cok_"}}


# ---------------------------------------------------------------------------
# 给网页用的汇总
# ---------------------------------------------------------------------------

def summary(state):
    """从 read_all 的结果里算出页面要显示的计数/提示。"""
    st = state or {}
    sci = st.get("science") or {}
    task = st.get("task") or {}
    mission = st.get("mission") or {}
    panel = st.get("donatePanel") or {}

    researching = sci.get("researching") or ""
    researching_sci = None
    for s in (sci.get("list") or []):
        if s.get("scienceId") == researching:
            researching_sci = s
            break

    donate_ready = bool(panel.get("canDonate"))
    donate_reason = ""
    if not researching:
        donate_ready = False
        donate_reason = "当前没有正在研究的联盟科技"
    elif researching_sci and researching_sci.get("full"):
        donate_ready = False
        donate_reason = "该科技进度已攒满(已是可研究状态), 无法继续捐献"
    elif not donate_ready:
        donate_reason = panel.get("reason") or "当前没有开放的捐献档位"

    sign = mission.get("signIn") or {}
    sign_done = _int(sign.get("signInReward_state")) == 1

    can_accept = _int((task.get("record") or {}).get("maxAcceptCount")) - \
        _int((task.get("record") or {}).get("acceptCount"))

    return {
        "researching": researching,
        "researchingScience": researching_sci,
        "donateReady": donate_ready,
        "donateReason": donate_reason,
        "donateTiers": panel.get("tiers") or [],
        "taskAcceptLeft": can_accept,
        "taskPublishedLeft": _int((task.get("record") or {}).get("maxPublishCount")) -
        _int((task.get("record") or {}).get("publishCount")),
        "pendingTasks": len([t for t in (task.get("published") or []) if t.get("requested")]),
        "signInDays": _int(sign.get("signIn_days")),
        "signInDone": sign_done,
        "signInReward": sign.get("signIn_reward") or "",
        "alliancePoint": _int((st.get("shop") or {}).get("alliancePoint")),
    }
