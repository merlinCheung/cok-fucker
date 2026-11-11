#!/usr/bin/env python3
"""编队预设**按账号隔离**的回归测试(不连游戏服, 零消耗)。

背景(2026-10-27 实测踩坑): 「读游戏设置」读的是 `autoQueue.data`
= 游戏「自动打怪」面板当前用的编成, 那是**每个账号各自**的。
原先编队预设存在**全局** web-settings.json 里, 于是:

  * A 号读来的编成, 切到 B 号还在显示 -> "数据不对"
  * 读回来的编成被贴上"编队1"的名字, 让人以为那就是游戏里的编队1

现在改成按 gameUid 分桶(squadPresetsAcc), 互不串号, 并且带来源标记。

跑法: python3 test_squad_isolation.py
"""
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

_TMP = tempfile.mkdtemp(prefix="cok-squadiso-test-")
os.environ["COK_ACCOUNTS_DIR"] = os.path.join(_TMP, "accounts")
os.environ["COK_DATA_ROOT"] = os.path.join(_TMP, "data")

import cok_web  # noqa: E402

PASS = 0
FAIL = 0


def check(cond, name, extra=""):
    global PASS, FAIL
    if cond:
        PASS += 1
    else:
        FAIL += 1
    print("%s %s%s" % ("[PASS]" if cond else "[FAIL]", name,
                       ("  — " + extra) if extra else ""))


def make_engine(key, label):
    """造一个只带 settings/account_key 的最小引擎桩。"""
    e = types_engine()
    e.account_key = key
    e.account_label = label
    e.settings["squadPresetsAcc"] = "{}"
    return e


def types_engine():
    import types
    eng = cok_web.Engine.__new__(cok_web.Engine)
    eng.settings = {}
    eng.account_key = ""
    eng.account_label = ""
    eng.SETTINGS_FILE = os.path.join(_TMP, "web-settings-%d.json" % os.getpid())
    eng._save_settings = lambda: None      # 不落盘, 测试里不碰真设置
    return eng


SPEC_A = [{"army_id": "107110", "num": 50},
          {"army_id": "107012", "num": 50}]
SPEC_B = [{"army_id": "107111", "num": 30}]


def test_format_kinds():
    """autoQueue.format 的三种形态(2026-10-27 实测)。"""
    import cok_hunt
    cases = [
        ("", "empty", [], []),
        ("1", "index", [1], []),
        ("1;2;3", "index", [1, 2, 3], []),
        ("107110,50|107012,50", "army", [],
         [{"army_id": "107110", "num": 50}, {"army_id": "107012", "num": 50}]),
    ]
    for fmt, kind, indices, squads in cases:
        idx = []
        if fmt:
            parts = [x.strip() for x in fmt.split(";")]
            if all(x.isdigit() for x in parts):
                idx = [int(x) for x in parts]
        k = "empty" if not fmt else ("index" if idx else "army")
        check(k == kind, "format %r 判定为 %s" % (fmt, kind), "实际 %s" % k)
        check(idx == indices, "format %r 的索引" % fmt, str(idx))
        parsed = [{"army_id": s.get("id"), "num": s.get("num")}
                  for s in cok_hunt.parse_format(fmt)]
        check(parsed == squads, "format %r 的编成解析" % fmt, str(parsed))


def main():
    # --- A 号存一份编成 ---
    a = make_engine("111100002223", "甲号")
    ok, key = a._squad_preset_save(1, SPEC_A, from_game=True, from_game_account="甲号")
    check(ok and key == "111100002223", "A 号存编成成功", key)
    p = a._squad_preset(1)
    check(bool(p) and len(p["spec"]) == 2, "A 号读回自己的编成")
    check(bool(p.get("fromGame")), "A 号的编成带 fromGame 标记")
    check(p.get("fromGameAccount") == "甲号", "记下了是从哪个账号读来的",
          p.get("fromGameAccount"))

    # --- B 号: 必须是空的, 不能看到 A 的 ---
    b = make_engine("222200002223", "乙号")
    # B 用**同一份 settings**(真实场景就是同一份 web-settings.json)
    b.settings = a.settings
    pb = b._squad_preset(1)
    check(pb is None or not pb.get("spec"),
          "B 号看不到 A 号的编成(不串号)",
          json.dumps(pb, ensure_ascii=False)[:120] if pb else "空")
    lst = b._squad_preset_list()
    check(lst[0].get("empty") is True, "B 号的编队1 列表项标记为空")

    # --- A 号再读: 仍在 ---
    a2 = make_engine("111100002223", "甲号")
    a2.settings = a.settings
    pa = a2._squad_preset(1)
    check(bool(pa) and len(pa["spec"]) == 2, "A 号仍能读回自己的编成")

    # --- B 号存自己的一份, 不影响 A ---
    okb, _ = b._squad_preset_save(1, SPEC_B, from_game=True, from_game_account="乙号")
    check(okb, "B 号存自己的编成")
    a3 = make_engine("111100002223", "甲号")
    a3.settings = a.settings
    pa3 = a3._squad_preset(1)
    check(len(pa3.get("spec") or []) == 2
          and pa3["spec"][0]["army_id"] == "107110",
          "B 号存完不影响 A 号的编成")

    # --- 还没有分桶时, 回退旧的全局设置(向后兼容) ---
    c = make_engine("333300002223", "丙号")
    c.settings["squadPresets"] = json.dumps({"1": {"name": "编队1", "spec": SPEC_A}},
                                             ensure_ascii=False)
    pc = c._squad_preset(1)
    check(bool(pc) and len(pc["spec"]) == 2,
          "没有任何分桶时回退旧的全局设置(向后兼容)")

    test_format_kinds()
    print()
    if FAIL:
        print("%d 通过, %d 失败" % (PASS, FAIL))
        return 1
    print("全部通过 (%d)" % PASS)
    return 0


if __name__ == "__main__":
    sys.exit(main())
