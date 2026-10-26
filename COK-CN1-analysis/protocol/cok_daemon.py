#!/usr/bin/env python3
"""COK 游戏服常驻监控器 —— 脱离 App 持续跟踪游戏状态。

能力:
  * 自动连接 / 自动重连(断了自动走 bin 握手 + 登录 + 派生密钥)
  * 周期性轮询, **只输出变化**(状态指纹对比)
  * 提取: 每日签到进度、周任务进度与可领奖励、领主任务可领奖励、
          主线任务可领奖励、联盟 boss 状态、建造队列
  * 可选自动领奖(--claim,默认关闭;会真实消耗奖励次数)
  * 人类可读输出 / --json 机器可读输出 / --log <file> 追加日志

用法:
  python3 cok_daemon.py                       # 默认轮询项, 每 5 分钟
  python3 cok_daemon.py --interval 60          # 60 秒一轮
  python3 cok_daemon.py --json                 # 机器可读
  python3 cok_daemon.py --claim                # 开启自动领奖(有副作用,慎用)
  python3 cok_daemon.py --once                 # 只跑一轮就退出
  python3 cok_daemon.py --watch dailySign dailyQuest lordTask
"""
import argparse
import json
import os
import signal
import sys
import time
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cok_client import CokClient  # noqa: E402

# 告警规则
RULE_SIGN = "sign"        # 每日签到完成
RULE_CLAIM = "claim"      # 领到奖励
RULE_TASK = "task"        # 出现新的可领奖励
RULE_BOSS = "boss"        # 联盟 boss 状态变化(刷新/消失)
RULE_ERROR = "error"      # 连接异常 / 重连
RULE_SHIELD = "shield"    # 保护罩相关(被攻击后自动开罩)

#: 规则 -> 中文名(页面上不该只显示代号)
RULE_NAMES = {
    RULE_SIGN: "签到",
    RULE_CLAIM: "领奖",
    RULE_TASK: "任务奖励",
    RULE_BOSS: "联盟Boss",
    RULE_ERROR: "连接异常",
    RULE_SHIELD: "保护罩",
}


def rule_name(rule):
    return RULE_NAMES.get(rule, rule)
ALL_RULES = [RULE_SIGN, RULE_CLAIM, RULE_TASK, RULE_BOSS, RULE_ERROR, RULE_SHIELD]


class Alert(object):
    """webhook 告警: 支持通用 JSON / 企业微信 / 钉钉三种载荷格式。"""

    def __init__(self, url=None, kind="generic", rules=None, timeout=10.0):
        self.url = url
        self.kind = kind
        self.rules = set(rules or [])
        self.timeout = timeout
        self.sent = 0
        self.last_error = None

    def enabled(self, rule):
        return bool(self.url) and rule in self.rules

    def _payload(self, title, lines, key, value):
        text = "\n".join(lines)
        if self.kind == "wechat":
            return {"msgtype": "text", "text": {"content": "%s\n%s" % (title, text)}}
        if self.kind == "dingtalk":
            return {"msgtype": "text", "text": {"content": "%s\n%s" % (title, text)}}
        return {"kind": key, "title": title, "text": text, "value": value,
                "ts": time.strftime("%Y-%m-%d %H:%M:%S")}

    def push(self, rule, title, lines, key=None, value=None):
        if not self.enabled(rule):
            return False
        payload = self._payload(title, lines, rule, value)
        try:
            req = urllib.request.Request(
                self.url, data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
                headers={"Content-Type": "application/json"})
            urllib.request.urlopen(req, timeout=self.timeout).read()
            self.sent += 1
            return True
        except Exception as e:  # noqa: BLE001
            self.last_error = str(e)[:150]
            self.emit_local("alert_error", {"rule": rule, "msg": self.last_error})
            return False

    def emit_local(self, kind, payload):
        print("[alert:%s] %s" % (kind, json.dumps(payload, ensure_ascii=False, default=str)),
              flush=True)

WATCHERS = {
    # 名称 -> (命令名, 提取函数)
    "dailySign": ("monthlySign.info", "daily_sign"),
    "dailyQuest": ("dailyQuest2025.data", "daily_quest"),
    "lordTask": ("lordTask.data", "lord_task"),
    "storyTask": ("story.task.info", "story_task"),
    "boss": ("allianceNewBoss.bossMainInfo", "boss"),
    "overview": ("overview_new.data", "overview"),
    "buildQueue": ("build.info", "build_queue"),
}


def _as_int(v, default=0):
    try:
        return int(v)
    except (TypeError, ValueError):
        return default


def _ints(v):
    out = []
    for x in str(v or "").split(";"):
        x = x.strip()
        if x.isdigit():
            out.append(int(x))
    return out


def daily_sign(p, ctx):
    """每日签到状态"""
    days = _ints(p.get("days"))
    today = ctx.get("today")
    signed = today in days
    month = ctx.get("month")
    # rewardObj 的键是 "月-日"; multiDays 指定每月哪几天发月卡(如 3;5)
    multi = _ints(p.get("multiDays"))
    reward_obj = p.get("rewardObj") or {}
    card_days = []
    for d in multi:
        k = "%d-%d" % (month, d)
        v = reward_obj.get(k)
        if isinstance(v, dict) and v.get("reward"):
            card_days.append(k)
    return {
        "今日已签": signed,
        "今日(第%s天)" % today: True,
        "已签日期": days,
        "剩余补签次数": _as_int(p.get("leftLostSignTimes")),
        "月卡档位": str(p.get("multiDays") or ""),
        "本月月卡发放日": card_days,
        "今天是月卡日": ("%d-%d" % (month, today)) in reward_obj,
        "每日奖励道具": p.get("day2ItemIdStr"),
    }


def daily_quest(p, ctx):
    """周任务 + 日常任务"""
    ready = []
    for q in (p.get("dailyQuest") or []):
        if not isinstance(q, dict):
            continue
        if _as_int(q.get("times")) > 0:
            ready.append({"id": q.get("id"),
                          "进度": "%s/%s" % (q.get("num"), q.get("totalTimes"))})
    claimable = [x for x in str(p.get("weekTaskRewardId2025") or "").split(";") if x]
    return {
        "周任务积分": _as_int(p.get("weekTaskScore")),
        "周任务可领奖励": claimable,
        "周结束时间": p.get("weekEndTime"),
        "可领日常任务": ready,
    }


def lord_task(p, ctx):
    """领主任务"""
    rewards = [x for x in str(p.get("rewards") or "").split(";") if x]
    got = set(_ints(p.get("awardIndex")))
    claimable = [r for i, r in enumerate(rewards) if i not in got]
    todo = []
    for t in (p.get("task_arr") or []):
        if isinstance(t, dict) and _as_int(t.get("state")) != 2:
            todo.append({"id": t.get("taskId"), "进度": t.get("process"), "state": t.get("state")})
    return {
        "当前进度": _as_int(p.get("curProgress")),
        "档位": str(p.get("stages") or ""),
        "已领档位数": len(got),
        "可领奖励": claimable,
        "未完成任务数": len(todo),
        "未完成": todo[:10],
    }


def story_task(p, ctx):
    """主线任务

    注意: state==1 表示"任务已完成", **不等于"可领"** —— 实测领完 254310 后
    state 仍是 1(多个任务可共用同一奖励 id)。所以这里只报"已完成任务的奖励",
    是否真的可领由领奖接口的返回值决定。
    """
    done = []
    tasks = []
    for t in (p.get("storyTaskList") or []):
        if not isinstance(t, dict):
            continue
        if _as_int(t.get("state")) == 1 and t.get("taskReward"):
            done.append(t["taskReward"])
        # 任务 id 就是 ItemSpec id(33101001 这种), 网页端按它翻译成中文
        tasks.append({
            "id": t.get("id"),
            "进度": "%s/%s" % (t.get("num"), t.get("targetNum")),
            "目标": _as_int(t.get("targetNum")),
            "state": t.get("state"),
            "奖励": t.get("taskReward"),
        })
    return {
        "章节": _as_int(p.get("section")),
        "已完成任务奖励": sorted(set(done)),
        "任务数": len(p.get("storyTaskList") or []),
        "任务": tasks,
    }


def boss(p, ctx):
    """联盟 boss"""
    out = []
    for b in (p.get("bossInfo") or []):
        if isinstance(b, dict):
            out.append({
                "pointId": b.get("pointId"),
                "在位": bool(b.get("onPlace")),
                "cdTime": b.get("cdTime"),
                "cd结束": b.get("cdTime"),
                "num": b.get("num"),
            })
    return {"boss": out}


def overview(p, ctx):
    """建造/队列概览"""
    ql = []
    for grp in (p.get("queueList") or []):
        if not isinstance(grp, list):
            continue
        for it in grp:
            if isinstance(it, dict):
                ql.append({"type": it.get("type"), "qindex": it.get("qindex"),
                           "进度": "%s/%s" % (it.get("curValue"), it.get("maxValue"))})
    return {"队列": ql, "未开启": p.get("noOpenList")}


def build_queue(p, ctx):
    """主城建造队列(build.info -> buildingQueue)

    字段说明(实测):
      uuid      = **队列** uuid(加速时用它做 qUUID; 不是 itemObj.uuid)
      qid       = 队列槽位号(queueId)
      type      = 队列类型(queueType: 1=建造队列, 2=造兵队列)
      totalTime = 剩余建造毫秒(0 = 已完成/空闲)
      startTime = 开始建造时间戳
    """
    out = []
    for q in (p.get("buildingQueue") or []):
        if not isinstance(q, dict):
            continue
        total = _as_int(q.get("totalTime"))
        start = _as_int(q.get("startTime"))
        out.append({
            "uuid": q.get("uuid"),
            "qid": q.get("qid"),
            "type": q.get("type"),
            "进行中": bool(total > 0 and start > 0),
            "剩余毫秒": total,
            "剩余分钟": round(total / 60000.0, 1) if total else 0,
            "建筑": (q.get("itemObj") or {}).get("building") if isinstance(q.get("itemObj"), dict) else None,
        })
    return {"建造队列": out, "金币": p.get("gold")}


EXTRACTORS = {
    "daily_sign": daily_sign,
    "daily_quest": daily_quest,
    "lord_task": lord_task,
    "story_task": story_task,
    "boss": boss,
    "overview": overview,
    "build_queue": build_queue,
}


class Daemon(object):
    def __init__(self, args):
        self.args = args
        self.client = None
        self.last = {}
        self.server_now = 0
        self.logfile = None
        self.claimed = set()      # 已领过的 rewardId, 避免重复领
        self.claim_total = 0      # 本次运行累计领奖次数(上限保护)
        self.signed_days = set()  # 已签到的日期(避免重复签到)
        self.last_state = {}     # 每个监控项最近一次的 state(dict)
        self.shield_last = 0.0   # 上次开罩时间戳(用于冷却限流)
        self.shield_end_ms = 0   # 当前保护罩到期时间(毫秒); 0 = 无罩
        self.alert = Alert(args.webhook, args.webhook_type, args.alert_rules)
        if args.log:
            self.logfile = open(args.log, "a", encoding="utf-8")
        self.stop = False

    # ---------- 输出 ----------
    def emit(self, kind, payload):
        ts = time.strftime("%Y-%m-%d %H:%M:%S")
        if self.args.json:
            line = json.dumps({"ts": ts, "kind": kind, "data": payload},
                             ensure_ascii=False, default=str)
        else:
            line = "[%s] %s %s" % (ts, kind, json.dumps(payload, ensure_ascii=False, default=str))
        print(line, flush=True)
        if self.logfile:
            self.logfile.write(line + "\n")
            self.logfile.flush()

    # ---------- 连接 ----------
    def connect(self):
        if self.client:
            try:
                self.client.close()
            except Exception:
                pass
        # 游戏服地址: 优先 --game-host/--game-port(网页控制台的 --host/--port
        # 是**网页监听地址**, 不是游戏服 —— 早期两者混用, 害得控制台连自己)
        gh = getattr(self.args, "game_host", None) or self.args.host
        gp = int(getattr(self.args, "game_port", None) or self.args.port)
        c = CokClient(gh, gp, self.args.timeout, self.args.account)
        c.connect()
        c.bin_handshake()
        c.login()
        try:
            c.call("cmd.ping")
        except Exception:
            pass
        self.client = c
        self.queues = []
        self.grab_init()
        self.emit("connected", {"host": c.host, "port": c.port, "key_id": c.key_id})

    def grab_init(self, wait=20.0):
        """登录后收服务端的 `init` 推送, 解出队列清单(含 uuid 与 type)。

        必须**紧跟登录**收: 之后发任何请求都可能被挤掉/超时。
        recv 超时要 continue 不要 break(推送可能延后到)。
        """
        out = []
        try:
            from cok_sfs import decode_params, parse_packet
            self.client.sock.settimeout(3.0)
            buf = b""
            t0 = time.time()
            while time.time() - t0 < wait:
                try:
                    ch = self.client.sock.recv(65536)
                except Exception:
                    continue
                if not ch:
                    break
                buf += ch
                i = 0
                while i + 3 <= len(buf):
                    fl = buf[i]
                    ln = (buf[i + 1] << 8) | buf[i + 2]
                    if not (fl & 0x80) or ln == 0 or i + 3 + ln > len(buf):
                        break
                    try:
                        _, _, obj, _ = parse_packet(buf[i:i + 3 + ln])
                    except Exception:
                        break
                    pp = self.client._resp_params(obj)
                    if self.client._resp_cmd(obj) == "init":
                        for k, v in pp.items():
                            if isinstance(v, str) and len(v) > 60 and k != "qqq":
                                try:
                                    o2, _, _ = decode_params(bytes.fromhex(v), self.client.key)
                                    out = o2.get("queue") or []
                                except Exception:
                                    pass
                    i += 3 + ln
                buf = buf[i:]
                if out:
                    break
        except Exception:
            pass
        self.queues = out
        return out

    def ctx(self):
        now = self.server_now or int(time.time() * 1000)
        # 国服按北京时间(UTC+8)判定"今天"
        lt = time.localtime(now / 1000 + 8 * 3600)
        return {"today": lt.tm_mday, "month": lt.tm_mon, "now": now,
                "date": time.strftime("%Y-%m-%d", lt)}

    def poll_once(self):
        ctx = self.ctx()
        for name in self.args.watch:
            cmd, ex = WATCHERS[name]
            try:
                r = self.client.call(cmd)
            except Exception as e:  # noqa: BLE001
                # 单个监控项失败**不中断整轮**: 有的命令在长连接上会把连接弄废
                # (实测 allianceNewBoss.bossMainInfo 单独连接 OK, 连续发时被踢),
                # 这里重连后继续下一个监控项, 已取到的状态保留不清空。
                self.emit("error", {"watch": name, "cmd": cmd, "msg": str(e)[:120]})
                try:
                    self.connect()
                except Exception as e2:  # noqa: BLE001
                    self.emit("fatal", {"msg": str(e2)[:200]})
                    raise
                continue
            p = r.get("__params__") or {}
            prev = self.last.get(name)
            try:
                state = EXTRACTORS[ex](p, ctx)
            except Exception as e:  # noqa: BLE001
                state = {"__extract_error__": str(e)[:120]}
            state["_server_date"] = ctx["date"]
            fp = json.dumps(state, sort_keys=True, default=str)
            if self.last.get(name) != fp:
                self.last[name] = fp
                self.last_state[name] = state
                self.emit("state", {"watch": name, "cmd": cmd, "state": state})
                self.alert_on_state(name, state, prev)

    def alert_on_state(self, name, state, prev):
        """按规则把有意义的状态变化推成告警"""
        if not self.alert.url:
            return
        if name == "dailySign":
            was = (prev or {}).get("今日已签")
            now = state.get("今日已签")
            if was is False and now is True:
                self.alert.push(RULE_SIGN, "每日签到完成",
                               ["服务器日期: %s" % state.get("_server_date"),
                                "已签日期: %s" % ",".join(str(x) for x in state.get("已签日期") or [])],
                               key="dailySign", value=state)
            elif was is None and now is False:
                self.alert.push(RULE_SIGN, "今日尚未签到",
                               ["服务器日期: %s" % state.get("_server_date"),
                                "剩余补签次数: %s" % state.get("剩余补签次数")],
                               key="dailySign", value=state)
        elif name == "dailyQuest":
            cur = state.get("周任务可领奖励") or []
            old = (prev or {}).get("周任务可领奖励") or []
            if cur and cur != old:
                self.alert.push(RULE_TASK, "有新的周任务奖励可领",
                               ["可领奖励: %s" % ",".join(cur),
                                "周任务积分: %s" % state.get("周任务积分")],
                               key="dailyQuest", value=state)
        elif name == "lordTask":
            cur = state.get("可领奖励") or []
            old = (prev or {}).get("可领奖励") or []
            if cur and cur != old:
                self.alert.push(RULE_TASK, "有新的领主任务奖励可领",
                               ["可领奖励: %s" % ",".join(cur)],
                               key="lordTask", value=state)
        elif name == "boss":
            if prev is not None and state.get("boss") != prev.get("boss"):
                self.alert.push(RULE_BOSS, "联盟 boss 状态变化",
                               [json.dumps(state.get("boss"), ensure_ascii=False, default=str)[:300]],
                               key="boss", value=state)

    def auto_sign(self, ctx):
        """自动每日签到(幂等: 今天已签则跳过)

        复用 poll_once 已取到的 monthlySign.info 状态, 不额外发请求。
        """
        today = ctx.get("today")
        st = self.last_state.get("dailySign")
        if st is not None:
            if st.get("今日已签"):
                self.emit("sign_skip", {"today": today, "reason": "今天已签"})
                return None
        else:
            try:
                r = self.client.call("monthlySign.info")
            except Exception as e:  # noqa: BLE001
                self.emit("sign_error", {"msg": str(e)[:120]})
                return None
            p = r.get("__params__") or {}
            if today in set(_ints(p.get("days"))):
                self.emit("sign_skip", {"today": today, "reason": "今天已签"})
                return None
        try:
            r2 = self.client.call("monthlySign.sign")
            p2 = r2.get("__params__") or {}
            reward = p2.get("reward")
            self.emit("sign", {"today": today, "reward": reward,
                               "errorCode": p2.get("errorCode")})
            self.alert.push(RULE_SIGN, "自动签到完成",
                           ["服务器日期: %s" % ctx.get("date"),
                            "奖励: %s" % json.dumps(reward, ensure_ascii=False, default=str)[:200]],
                           key="sign", value=p2)
            return reward
        except Exception as e:  # noqa: BLE001
            self.emit("sign_error", {"msg": str(e)[:120]})
            self.alert.push(RULE_ERROR, "自动签到失败", [str(e)[:150]], key="sign")
            return None

    def claim(self, ctx):
        """收集可领奖励并领奖(--claim 开启时)

        阶段奖励优先用**精确命令** `lordTask.reward.process {index}`
        (index = awardIndex 之后的那一档), 其余用通用
        `resource.client.reward.get {rewardId}`。
        """
        targets = []
        # 1) 领主任务阶段奖励: 用 index 精确领
        try:
            r = self.client.call("lordTask.data")
            p = r.get("__params__") or {}
            got = _ints(p.get("awardIndex"))
            rewards = [x for x in str(p.get("rewards") or "").split(";") if x]
            nxt = (max(got) + 1) if got else 0
            if nxt < len(rewards):
                rr = self.client.call("lordTask.reward.process", {"index": nxt})
                pp = rr.get("__params__") or {}
                award = pp.get("reward") or pp.get("award") or []
                if award:
                    self.claimed.add(rewards[nxt])
                    self.claim_total += 1
                self.emit("claim_result", {"cmd": "lordTask.reward.process", "index": nxt,
                                          "rewardId": rewards[nxt], "award": award,
                                          "errorCode": pp.get("errorCode")})
        except Exception as e:  # noqa: BLE001
            self.emit("claim_result", {"cmd": "lordTask.reward.process",
                                      "error": str(e)[:100]})
        # 2) 周任务奖励
        try:
            r = self.client.call("dailyQuest2025.data")
            p = r.get("__params__") or {}
            targets += [x for x in str(p.get("weekTaskRewardId2025") or "").split(";") if x]
        except Exception:
            pass
        # 3) 主线任务奖励(state==1 表示已完成)
        try:
            r = self.client.call("story.task.info")
            p = r.get("__params__") or {}
            for t in (p.get("storyTaskList") or []):
                if isinstance(t, dict) and _as_int(t.get("state")) == 1 and t.get("taskReward"):
                    targets.append(t["taskReward"])
        except Exception:
            pass
        room = self.args.claim_max_total - self.claim_total
        if room <= 0:
            self.emit("claim", {"note": "已达本次运行的领奖上限", "max": self.args.claim_max_total})
            return
        targets = [t for t in dict.fromkeys(targets) if t not in self.claimed][:room]
        if not targets:
            self.emit("claim", {"note": "没有可领奖励"})
            return
        self.emit("claim", {"note": "准备领奖", "rewardIds": targets})
        for rid in targets[:self.args.claim_limit]:
            try:
                r = self.client.call("resource.client.reward.get", {"rewardId": rid})
                p = r.get("__params__") or {}
                award = p.get("award") or []
                if award:
                    self.claimed.add(rid)      # 真的领到才记, 避免下次重复
                    self.claim_total += 1
                self.emit("claim_result", {"rewardId": rid,
                                          "award": award,
                                          "errorCode": p.get("errorCode")})
            except Exception as e:  # noqa: BLE001
                self.emit("claim_result", {"rewardId": rid, "error": str(e)[:100]})

    def refresh_shield_state(self):
        """拉取当前保护罩到期时间。

        ⚠️ **不能用 `onekeybuff.get`**(实测它只回 backList 槽位配置, 不回 shieldEndTime)。
        权威来源是 `show.status.item` -> statusItems 里 **type2=1** 的那一项
        (type2=1 = 保护罩本体, 见 database.local.xml goods 组 city_buff=1 & type2=1)。
        endTime 是毫秒时间戳; 9223372036854775807 (Long.MAX) 表示"永久/未过期", 要排除。
        """
        end = 0
        try:
            r = self.client.call("show.status.item")
            p = r.get("__params__") or {}
            for it in (p.get("statusItems") or []):
                if not isinstance(it, dict):
                    continue
                if int(it.get("type2") or 0) != 1:
                    continue
                e = int(it.get("endTime") or 0)
                if e and e < (1 << 62):
                    end = e
                    break
            if end:
                self.shield_end_ms = end
        except Exception as e:  # noqa: BLE001
            self.emit("shield_state", {"error": str(e)[:120]})
        return self.shield_end_ms

    def autoshield(self, ctx):
        """被攻击/被侦查时自动开保护罩(--autoshield 开启时)

        触发信号: 服务端主动推送(push)帧, 由客户端收集在 client.pushes。
          默认监听 `push.world.injured`(部队被攻击)等三个。

        **有罩就不重复开**: 维护当前罩的到期时间 `shieldEndTime`
        (来源: `onekeybuff.get` 响应; `push.protect.time` 会刷新它),
        只有在 **无罩 / 罩已过期** 时才发 `onekeybuff.use`。
        否则连续被攻击会把保护罩道具瞬间烧光。

        动作: `onekeybuff.use {type: 槽位号, coverOld: 是否覆盖旧罩}`。
        槽位是用户自建的"一键 buff 预设"(1/2/3), `onekeybuff.get` 可查各槽道具。

        ⚠️ 有真实副作用(消耗保护罩道具), 因此额外带冷却限流。
        """
        a = self.args
        now_ms = int(ctx.get("now") or 0)
        pushes = []
        try:
            pushes = self.client.take_pushes()
        except Exception:
            pushes = []

        # 罩时间变更推送 -> 刷新本地状态
        for p in pushes:
            if (p.get("__cmd__") or "") == "push.protect.time":
                self.refresh_shield_state()

        hit = None
        force = False
        for p in pushes:
            cmd = p.get("__cmd__") or ""
            if cmd in a.shield_trigger_force:
                hit = p
                force = True
                break
            if cmd in a.shield_trigger and hit is None:
                hit = p
        if hit is None:
            return

        # 状态未知时先拉一次
        if not self.shield_end_ms:
            self.refresh_shield_state()
        # 有罩且未过期: 只有"被攻击"才续(说明罩扛不住了), 其它触发(被侦查等)跳过
        if (not force) and now_ms and self.shield_end_ms and now_ms < self.shield_end_ms:
            self.emit("shield_skip", {
                "note": "保护罩仍在生效中, 不重复开启",
                "剩余毫秒": self.shield_end_ms - now_ms,
                "触发": hit.get("__cmd__"),
            })
            return
        if time.time() - self.shield_last < a.shield_cooldown:
            return

        self.shield_last = time.time()
        params = {"type": int(a.shield_slot), "coverOld": bool(a.shield_cover_old)}
        self.emit("shield_trigger", {
            "note": "命中触发信号%s" % ("(被攻击, 续罩)" if force else "(当前无罩)"),
            "push": hit.get("__cmd__"),
            "slot": a.shield_slot, "coverOld": bool(a.shield_cover_old),
            "params": params,
        })
        try:
            r = self.client.call("onekeybuff.use", params)
            p = r.get("__params__") or {}
            ok = not p.get("errorCode")
            end = p.get("shieldEndTime")
            if end:
                self.shield_end_ms = int(end)
            self.emit("shield_result", {
                "cmd": "onekeybuff.use", "ok": ok,
                "errorCode": p.get("errorCode"),
                "shieldEndTime": self.shield_end_ms or p.get("shieldEndTime"),
            })
            self.alert.push(RULE_SHIELD, "已自动开启保护罩",
                           ["触发: %s" % hit.get("__cmd__"),
                            "槽位: %s" % a.shield_slot,
                            "到期: %s" % (self.shield_end_ms or p.get("shieldEndTime"))],
                           key="shield", value=p)
        except Exception as e:  # noqa: BLE001
            self.emit("shield_result", {"cmd": "onekeybuff.use", "error": str(e)[:120]})

    def speedup(self, ctx):
        """用**加速道具**加速队列(--speedup 开启时)

        命令: queue.ccd
        道具模式(默认): {qUUID, itemUUID, isGold:0, itemCount:N}   ← 4 字段(实测跑通)
        金币模式:       {qUUID, itemUUID:"", isGold:1, itemCount:1, queueId, queueType, goldcost}
        队列清单来自登录后服务端的 `init` 推送(connect 时抓), 覆盖建造/造兵/联盟等。
        道具实例 uuid 取自 speedup-owned.json(背包快照)。
        """
        a = self.args
        queues = getattr(self, "queues", []) or []
        running = [q for q in queues
                   if isinstance(q, dict)
                   and _as_int(q.get("totalTime")) > 0
                   and _as_int(q.get("startTime")) > 0
                   and _as_int(q.get("type")) == a.speedup_queue_type]
        if not running:
            self.emit("speedup", {
                "note": "没有进行中的 type=%d 队列, 跳过" % a.speedup_queue_type,
                "queue_types": sorted(set(_as_int(q.get("type")) for q in queues
                                         if isinstance(q, dict))),
                "queues": len(queues)})
            return
        q = running[0]
        qid = q.get("qid")
        qtype = q.get("type")

        if a.speedup_gold:
            params = {"qUUID": q.get("uuid"), "itemUUID": "", "isGold": 1, "itemCount": 1,
                      "queueId": str(qid), "queueType": str(qtype), "goldcost": "0"}
        else:
            owned = {}
            try:
                here = os.path.dirname(os.path.abspath(__file__))
                owned = json.load(open(os.path.join(here, "speedup-owned.json"),
                                      encoding="utf-8"))["items"]
            except Exception:
                owned = {}
            ent = owned.get(str(a.speedup_item))
            if not ent:
                self.emit("speedup", {"note": "speedup-owned.json 里没有道具 %s" % a.speedup_item})
                return
            params = {"qUUID": q.get("uuid"), "itemUUID": ent["uuid"],
                      "isGold": 0, "itemCount": int(a.speedup_count)}

        self.emit("speedup", {
            "note": "准备加速队列",
            "mode": "gold" if a.speedup_gold else "item",
            "itemId": params["itemUUID"], "itemCount": params["itemCount"],
            "queueUuid": params["qUUID"], "qid": qid, "queueType": qtype,
            "剩余毫秒": _as_int(q.get("totalTime")),
        })
        try:
            r2 = self.client.call("queue.ccd", params)
            p2 = r2.get("__params__") or {}
            done = bool(p2.get("finished"))
            self.emit("speedup_result", {
                "cmd": "queue.ccd", "finished": done,
                "remainGold": p2.get("remainGold"), "count": p2.get("count"),
                "itemId": p2.get("itemId"), "errorCode": p2.get("errorCode"),
            })
            if done:
                self.alert.push(RULE_TASK, "队列已加速完成",
                               ["队列 uuid: %s" % params["qUUID"],
                                "方式: %s" % ("金币" if a.speedup_gold else
                                            "道具 %s x%s" % (a.speedup_item, params["itemCount"])),
                                "剩余金币: %s" % p2.get("remainGold")],
                               key="speedup", value=p2)
        except Exception as e:  # noqa: BLE001
            self.emit("speedup_result", {"cmd": "queue.ccd", "error": str(e)[:120]})

    # ---------- 主循环 ----------
    def run(self):
        try:
            self.connect()
        except Exception as e:  # noqa: BLE001
            self.emit("fatal", {"msg": str(e)[:200]})
            return 1
        if self.args.once:
            self.poll_once()
            if self.args.auto_sign:
                self.auto_sign(self.ctx())
            if self.args.claim:
                self.claim(self.ctx())
            if self.args.speedup:
                self.speedup(self.ctx())
            if self.args.autoshield:
                self.autoshield(self.ctx())
            return 0
        self.emit("started", {"interval": self.args.interval,
                              "watch": self.args.watch,
                              "claim": bool(self.args.claim),
                              "speedup": bool(self.args.speedup)})
        while not self.stop:
            t0 = time.time()
            try:
                # 保活 + 刷新服务端时间
                r = self.client.call("cmd.ping")
                st = r.get("__params__") or {}
                if st.get("serverNowTime"):
                    self.server_now = _as_int(st.get("serverNowTime"))
                self.poll_once()
                if self.args.auto_sign:
                    self.auto_sign(self.ctx())
                if self.args.claim:
                    self.claim(self.ctx())
                if self.args.speedup:
                    self.speedup(self.ctx())
                if self.args.autoshield:
                    self.autoshield(self.ctx())
            except Exception as e:  # noqa: BLE001
                self.emit("reconnect", {"msg": str(e)[:150]})
                self.alert.push(RULE_ERROR, "连接异常,正在重连", [str(e)[:150]], key="error")
                try:
                    self.connect()
                except Exception as e2:  # noqa: BLE001
                    self.emit("fatal", {"msg": str(e2)[:200]})
                    time.sleep(self.args.retry_delay)
            # 保持固定节奏
            dt = time.time() - t0
            for _ in range(int(max(0, self.args.interval - dt) / 0.5) + 1):
                if self.stop:
                    break
                time.sleep(0.5)
        self.emit("stopped", {})
        return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="42.192.152.154")
    ap.add_argument("--account-device", action="store_true",
                    help="从设备 SharedPreferences 自动读取账号与服务器地址")
    ap.add_argument("--port", type=int, default=32231)
    ap.add_argument("--interval", type=int, default=300, help="轮询间隔秒")
    ap.add_argument("--timeout", type=float, default=30.0)
    ap.add_argument("--watch", nargs="+", default=["dailySign", "dailyQuest", "lordTask",
                                                  "storyTask", "boss", "overview"],
                    choices=list(WATCHERS.keys()))
    ap.add_argument("--json", action="store_true", help="机器可读输出")
    ap.add_argument("--log", help="追加日志文件")
    ap.add_argument("--once", action="store_true", help="只跑一轮")
    ap.add_argument("--claim", action="store_true", help="自动领奖(有副作用)")
    ap.add_argument("--claim-limit", type=int, default=5, help="单轮最多领几个")
    ap.add_argument("--claim-max-total", type=int, default=20,
                    help="本次运行累计最多领几个(安全上限)")
    ap.add_argument("--retry-delay", type=float, default=10.0)
    ap.add_argument("--auto-sign", action="store_true", help="自动每日签到(幂等)")
    ap.add_argument("--speedup", action="store_true",
                    help="用加速道具加速主城建造队列(有副作用, 消耗道具)")
    ap.add_argument("--speedup-item", default="200201",
                    help="加速道具**模板 id**(默认 200201 = 通用 5 分钟); "
                         "实例 uuid 取自 speedup-owned.json")
    ap.add_argument("--speedup-count", type=int, default=1, help="使用的道具数量")
    ap.add_argument("--speedup-gold", action="store_true",
                    help="改用金币加速(默认用道具; 金币会实扣)")
    ap.add_argument("--speedup-queue-type", type=int, default=1,
                    help="目标队列 type(1=造兵 0=城建; 见 init 推送的 queue[].type)")
    ap.add_argument("--autoshield", action="store_true",
                    help="被攻击/被侦查时自动开保护罩(有副作用, 消耗道具)")
    ap.add_argument("--shield-trigger", nargs="+",
                    default=["push.world.injured", "push.world.cannon.injured",
                             "push.world.march.fail"],
                    help="触发开罩的服务端 push 名")
    ap.add_argument("--shield-trigger-force", nargs="+",
                    default=["push.world.injured"],
                    help="这些 push 表示罩扛不住了, **无视已有罩直接续罩**;"
                         " 其它 --shield-trigger 只在无罩时才开")
    ap.add_argument("--shield-slot", type=int, default=1,
                    help="onekeybuff 预设槽位号(1/2/3, 用 onekeybuff.get 可查各槽道具)")
    ap.add_argument("--shield-cover-old", type=int, default=1,
                    help="onekeybuff.use 的 coverOld(1=覆盖旧罩)")
    ap.add_argument("--shield-cooldown", type=float, default=600.0,
                    help="两次自动开罩的最小间隔秒(防连续烧道具)")
    ap.add_argument("--webhook", help="告警 webhook URL")
    ap.add_argument("--webhook-type", default="generic",
                    choices=["generic", "wechat", "dingtalk"], help="告警载荷格式")
    ap.add_argument("--alert-rules", nargs="+", default=ALL_RULES, choices=ALL_RULES,
                    help="启用的告警规则")
    args = ap.parse_args()

    if args.account_device:
        from cok_account import load_account as _la
        acc = _la()
        args.account = acc
        print("[+] 已从设备读取账号: %s" % json.dumps(
            {k: acc.get(k) for k in ("pfId", "gameUid", "host", "port")}, ensure_ascii=False))

    d = Daemon(args)

    def on_sig(signum, frame):  # noqa: ARG001
        d.stop = True

    signal.signal(signal.SIGINT, on_sig)
    signal.signal(signal.SIGTERM, on_sig)
    return d.run()


if __name__ == "__main__":
    sys.exit(main())
