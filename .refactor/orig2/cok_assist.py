#!/usr/bin/env python3
"""COK 游戏内「一键完成」面板(CityAssist)的直连执行器。

## 游戏里那个按钮到底是什么

客户端 `game/city/CityAssistController.lua`:

```lua
function CityAssistController:doTask()
    -- 执行：可顺序执行的任务
    for i,v in ipairs(self.v_data or {}) do
        for _,vv in ipairs(v.items or {}) do
            if vv.exeOrder == nil and vv.isOpen == 1 and vv.pass == nil then
                ...
                if taskHandle[vv.type] then
                    taskHandle[vv.type].doTask(vv)
                end
                return i
```

⇒ **它不是一条协议命令, 而是客户端的一次编排**: 遍历面板所有项, 挑出
"已开启 + 没通过 + (进度未满 或 CD 已过)"的, 逐项调用该项自己的 `doTask`,
一项做完再接着下一项(靠 "CityAssistView:doTask" 这个观察者接力)。

所以直连的做法就是**照这个顺序逐项发各自的命令** —— 本模块就是这么做的
(`run_all`)。面板清单来自客户端配置表 `territory_assist`(服务端不下发)。

## 面板 13 项 / 3 组

    试炼  1=英雄试炼  2=龙塔试炼
    养成  6=普通研习  7=高级研习  8=普通招募  10=联盟宝藏  11=献祭  16=宝石挖掘
    收取  9=装卸货物  12=文明结晶  13=科研工坊  14=资源收取  15=一键增产

kind:
    free —— 无损(只把已产出的结算入库), 自动执行也会跑
    cost —— 要烧金币/道具/体力
    dock —— 由港口自动领取那条规则覆盖, 不重复
    none —— 客户端没有可直连的实现(或者服务端不收), 只在面板里显示
"""

# --- 包自举: 让本文件既能 `python3 cok/core/xxx.py` 直接跑, 也能被平铺 import ---
import os as _os
import sys as _sys

_PKG_ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
if _os.path.isdir(_PKG_ROOT) and _PKG_ROOT not in _sys.path:
    _sys.path.insert(0, _PKG_ROOT)
_CORE = _os.path.join(_PKG_ROOT, "core")
if _os.path.isdir(_CORE) and _CORE not in _sys.path:
    _sys.path.insert(0, _CORE)

import time

#: (type, 名称, 组, 代价, kind, 执行命令)
PANEL = (
    # kind=cost 但 spec=None 的项 = **参数已从客户端源码确认, 但在真服没能验证**
    #   (2026-10-31 实测: 这些命令一律回 E000000 —— 研习/招募消耗的是**自己**的
    #    道具金币照样被拒, 说明是**该账号功能未开通/权限不足**, 不是参数错;
    #    英雄试炼是两步流程且命令名没定位到; 联盟宝藏客户端根本没有 taskHandle)
    #   ⇒ 没验证过的参数**不发**, 免得盲烧钱。
    (1, "英雄试炼", 1, "道具 213575 + 金币", "cost", None),
    (2, "龙塔试炼", 1, "体力", "cost",
     ("dragontower.quickbattle", {"dealObject": "auto"})),   # ✅ 真服验证通过
    (6, "普通研习", 2, "道具", "cost", None),
    (7, "高级研习", 2, "道具", "cost", None),
    (8, "普通招募", 2, "金币", "cost", None),
    (10, "联盟宝藏", 2, "体力", "cost", None),
    (11, "献祭", 2, "联盟资源", "cost", None),
    (16, "宝石挖掘", 2, "免费次数内不消耗", "none",
     ("gem.dig", {"times": 1, "isAuto": True})),
    (9, "装卸货物", 3, "无(港口奖励)", "dock", None),
    (12, "文明结晶", 3, "无", "free",
     ("civilizationCastle.oneKeyCollect", {})),
    (13, "科研工坊", 3, "无", "free", ("sagatower.collect", None)),
    (14, "资源收取", 3, "无", "free", ("build.collect", None)),
    (15, "一键增产", 3, "未接入", "none", None),
)

GROUP_NAMES = {1: "试炼", 2: "养成", 3: "收取"}

#: 建筑类型 -> 是否是"资源产出建筑"(可收取)
#: 来源: lua game/utility/gameConst.lua + 客户端配置 territory_assist 的 go 字段
#:   412000/413000/414000/415000 = 各类资源产出建筑(秘银矿场/伐木场/铁矿场/农田…)
#:   437000 = 科研工坊(产科研石)
ASSIST_RES_TYPES = (412000, 413000, 414000, 415000)
#: 科研工坊建筑 id
ASSIST_SCIENCE_TYPE = 437000


def _call(client, cmd, params=None):
    try:
        r = client.call(cmd, params, retries=2)
    except Exception as e:  # noqa: BLE001
        return None, "TIMEOUT", str(e)[:120]
    p = (r or {}).get("__params__") or {}
    if not isinstance(p, dict):
        p = {}
    code = p.get("errorCode") or p.get("errCode") or ""
    if code:
        return p, str(code), ""
    return p, None, ""


def _btype(b):
    """建筑类型 id: `building` 字段优先, 否则从 `star_building_new` 推。

    `building` 字段是 "<类型id>;<等级>"; 新城市系统的建筑 `building` 为空,
    类型藏在 `star_building_new`("<类型id*10+星级>,数量")。
    """
    raw = str(b.get("building") or "").split(";")[0]
    if raw.isdigit():
        return int(raw)
    star = str(b.get("star_building_new") or "").split(",")[0]
    if star.isdigit():
        return (int(star) // 10) * 10
    return 0


def read_buildings(client):
    """读建筑列表, 分成"可收取资源"与"科研工坊"两组 uuid。"""
    p, code, err = _call(client, "build.info")
    if p is None:
        return None, [], [], err or code or "读建筑列表失败"
    res_ids, sci_ids = [], []
    for b in (p.get("building") or []):
        if not isinstance(b, dict):
            continue
        uid = b.get("uuid")
        if not uid:
            continue
        t = _btype(b)
        if t in ASSIST_RES_TYPES:
            res_ids.append(uid)
        elif t == ASSIST_SCIENCE_TYPE:
            sci_ids.append(uid)
    return p, res_ids, sci_ids, ""


def read_gem(client):
    """宝石挖掘视图(gem.getDigView)。返回 (免费次数, 每日上限, 错误)。"""
    p, code, err = _call(client, "gem.getDigView", {"isLogin": 1})
    if p is None:
        return 0, 0, err or code or "读宝石视图失败"
    def _i(k):
        try:
            return int(p.get(k) or 0)
        except (TypeError, ValueError):
            return 0
    return _i("leftFreeTimes"), _i("maxRcvdTimes"), ""


def _step(item, result, detail="", params=None):
    out = {"项": item, "结果": result, "详情": detail}
    if params is not None:
        out["_params"] = params
    return out


def _gain_text(p, before):
    gain = []
    for k, label in (("food", "粮食"), ("wood", "木材"), ("iron", "铁矿"),
                     ("stone", "石头"), ("silver", "银币")):
        try:
            d = int(p.get(k) or 0) - int(before.get(k) or 0)
        except (TypeError, ValueError):
            d = 0
        if d > 0:
            gain.append("%s+%s" % (label, d))
    return " ".join(gain)


def run_all(client, include_costly=False, max_steps=12):
    """按游戏「一键完成」的逻辑**串行**跑一遍。

    include_costly:
        False(默认) —— 只跑 **无损** 项(free)。定时自动执行用这个,
                        免得无人值守时把金币道具烧掉。
        True        —— 连**消耗** 项一起跑, 和游戏里点按钮一样。
                        手动「一键完成」按钮用这个(用户主动点的, 和游戏一致)。

    返回 {ok, steps[], panel[], changed, skipped}
      steps[]  每项: {项, 结果(完成/无可收取/跳过/未接入/失败), 详情}
    """
    steps = []
    skipped = []
    before_p, res_ids, sci_ids, err = read_buildings(client)
    if before_p is None:
        return {"ok": False, "error": err, "steps": steps, "panel": [],
                "changed": False, "skipped": skipped}
    before = dict(before_p.get("resource") or {})
    left, gem_max, _gerr = read_gem(client)

    def _run(cmd, params, label):
        p, code, msg = _call(client, cmd, params)
        if p is None:
            return _step(label, "失败", msg or "连接异常")
        if code:
            return _step(label, "服务端拒绝", str(code))
        return _step(label, "完成", "", p)

    # ---- 无损三项: 顺序执行(和游戏一致) ----
    if res_ids:
        st = _run("build.collect", {"uuid": ";".join(res_ids)}, "资源收取")
        st["详情"] = _gain_text(st.pop("_params", {}) or {}, before)
        steps.append(st)
    else:
        steps.append(_step("资源收取", "无可收取", ""))

    if sci_ids:
        st = _run("sagatower.collect", {"uuid": ";".join(sci_ids)}, "科研工坊")
        st["详情"] = str(st.pop("_params", {}).get("refreshTime") or "")
        steps.append(st)
    else:
        steps.append(_step("科研工坊", "无可收取", ""))

    st = _run("civilizationCastle.oneKeyCollect", {}, "文明结晶")
    if st.get("结果") == "完成":
        got = []
        for it in ((st.pop("_params", {}) or {}).get("itemArray") or []):
            if isinstance(it, dict):
                got.append("%s×%s" % (it.get("itemId"), it.get("itemNum")))
        st["详情"] = " ".join(got)
    steps.append(st)

    # ---- 其余项: 按 kind 处理 ----
    for t, name, group, cost, kind, spec in PANEL:
        if name in ("资源收取", "科研工坊", "文明结晶"):
            continue                      # 上面已经跑过
        if kind == "dock":
            steps.append(_step(name, "跳过", "由港口自动领取处理"))
            continue
        if kind == "none":
            if t == 16:
                steps.append(_step(name, "未接入",
                                   "免费次数 %s/%s(服务端暂不接受自动挖掘)" % (left, gem_max)))
            else:
                steps.append(_step(name, "未接入", "客户端无可直连实现"))
            continue
        if kind == "cost" and not include_costly:
            steps.append(_step(name, "跳过", "需消耗(%s),未开启" % cost))
            skipped.append(name)
            continue
        if spec is None:
            steps.append(_step(name, "未接入", "参数未确认"))
            continue
        cmd, params = spec
        steps.append(_run(cmd, params, name))
        if len(steps) >= max_steps:
            break

    for s in steps:
        s.pop("_params", None)
    changed = any(s.get("结果") == "完成" for s in steps)
    return {"ok": True, "steps": steps, "panel": panel_view(steps),
            "changed": changed, "skipped": skipped,
            "note": "一键完成(%s)" % ("含消耗项" if include_costly else "仅无损项")}


def panel_view(steps=None):
    """面板 13 项的清单 + 当前状态。"""
    done = {}
    for s in (steps or []):
        done[s.get("项")] = s.get("结果")
    out = []
    for t, name, group, cost, kind, _spec in PANEL:
        out.append({
            "type": t,
            "name": name,
            "group": group,
            "groupName": GROUP_NAMES.get(group, ""),
            "cost": cost,
            "autoKind": kind,
            "state": done.get(name) or "未执行",
        })
    return out


def summary(client):
    """只读: 面板清单 + 各项当前可做状态(不执行任何写操作)。"""
    p, res_ids, sci_ids, err = read_buildings(client)
    if p is None:
        return {"ok": False, "error": err, "items": []}
    left, mx, gerr = read_gem(client)
    items = []
    for t, name, group, cost, kind, _spec in PANEL:
        if t == 14:
            state = "可收取" if res_ids else "无可收取"
        elif t == 13:
            state = "可收取" if sci_ids else "无可收取"
        elif t == 12:
            state = "可执行"
        elif t == 16:
            state = ("免费次数 %s/%s(暂未接入自动)" % (left, mx) if left > 0
                     else "免费次数已用完")
        elif t == 9:
            state = "由港口规则处理"
        elif t == 15:
            state = "未接入"
        elif kind == "cost":
            state = "需消耗资源"
        else:
            state = "未知"
        items.append({
            "type": t, "name": name, "group": group,
            "groupName": GROUP_NAMES.get(group, ""),
            "cost": cost, "autoKind": kind, "state": state,
        })
    return {"ok": True, "items": items, "error": gerr}
