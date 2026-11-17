#!/usr/bin/env python3
"""P1 重构的回归测试: 作用域容器(cok_scope)+ 账号身份层(cok_identity)。

这两个模块是"消除模块级可变全局"和"统一账号概念"的地基, 它们错了
上层全错, 所以单独锁死语义。

覆盖的不变量:
  [1] Scope: 子作用域覆盖不影响父/兄弟; 继承读得到父值
  [2] Scope: 空 uid 就是"自己"(不是建一个空名桶)
  [3] Scope: reset 回到父值; snapshot/explain 看得见来源
  [4] cok_map: 两个账号各自 set_data_dir 后, 索引/pid/历史互不覆盖
  [5] cok_map: 老名字 DEFAULT_INDEX/DATA_DIR 仍可读(兼容老脚本)
  [6] cok_rally: 默认桶的老写法 `_KNOWN[...]` 与 `_known_for()` 同一块内存
  [7] cok_rally: 账号桶与默认桶互不影响; set_data_dir(uid=) 只改自己
  [8] cok_identity: key_of 各种形态; resolve 查不到时退回 {gameUid}
  [9] cok_identity: for_client 用真值覆盖占位符, 身份字段不跨号继承
  [10] cok_identity: missing_fields 能同时抓"空"和"占位符"

全程离线(不连游戏服、不连设备), 可重复跑。
"""

import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "core"))
sys.path.insert(0, os.path.join(HERE, "..", "tools"))

_FAILED = []


def check(name, cond, extra=""):
    if cond:
        print("[PASS] %s%s" % (name, ("  — " + str(extra)) if extra else ""))
    else:
        print("[FAIL] %s%s" % (name, ("  — " + str(extra)) if extra else ""))
        _FAILED.append(name)


# ─────────────────────────── 1-3. Scope ───────────────────────────
def test_scope_basics():
    print("\n[1/2/3] cok_scope: 层级查找 / 空 uid / reset / snapshot")
    from cok_scope import Scope

    root = Scope(None, "root")
    root["DIR"] = "/default"

    a = root.child("111")
    a.set("DIR", "/acc111")
    check("子作用域覆盖自己", a.get("DIR") == "/acc111", a.get("DIR"))
    check("默认作用域不受影响", root.get("DIR") == "/default", root.get("DIR"))

    b = root.child("222")
    check("兄弟之间互不影响", b.get("DIR") == "/default", b.get("DIR"))

    # 继承: 子作用域没设过的键 -> 读父的
    root["SHARED"] = "公共"
    check("子作用域继承父值", a.get("SHARED") == "公共", a.get("SHARED"))

    # 空 uid 必须映射到"自己", 而不是一个空名桶
    check("空 uid 返回自己", root.child("") is root)
    check("None uid 返回自己", root.child(None) is root)
    root.set("VIA_EMPTY", 1, uid="")
    check("空 uid 写入自己", root.raw("VIA_EMPTY") == 1)
    check("空 uid 写入不产生空名桶", "" not in root.children(),
          list(root.children()))

    # uid 归一: 数字 1 和字符串 "1" 同一个桶
    root.set("NUM", "int", uid=1)
    root.set("NUM", "str", uid="1")
    check("数字/字符串 uid 同桶", root.child("1").raw("NUM") == "str",
          root.child("1").raw("NUM"))

    # reset 回到父值
    a.reset("DIR")
    check("reset 后回落到父值", a.get("DIR") == "/default", a.get("DIR"))

    # explain / snapshot
    val, src = a.explain("DIR")
    check("explain 报出来源", val == "/default" and src == "root",
          (val, src))
    snap = root.snapshot()
    check("snapshot 列得出各账号覆盖",
          snap.get("111", {}).get("DIR") is None, snap)

    # contains
    check("contains 走继承链", "DIR" in a and "NOPE" not in a)


# ─────────────────────────── 4-5. cok_map ───────────────────────────
def test_map_scopes():
    print("\n[4/5] cok_map: 按账号隔离 + 老名字兼容")
    import cok_map as M

    d1 = tempfile.mkdtemp(prefix="scope_map_a_")
    d2 = tempfile.mkdtemp(prefix="scope_map_b_")
    M.set_data_dir(d1, uid="111")
    M.set_data_dir(d2, uid="222")

    p1, p2 = M.index_path("111"), M.index_path("222")
    check("两个账号索引路径不同", p1 != p2 and d1 in p1 and d2 in p2,
          (p1, p2))

    M.save_index({"players": {"a": {"x": 1}}, "meta": {"who": "A"}}, uid="111")
    M.save_index({"players": {"b": {"x": 2}}, "meta": {"who": "B"}}, uid="222")
    check("A 读到自己的索引", M.load_index(uid="111")["meta"].get("who") == "A",
          M.load_index(uid="111")["meta"])
    check("B 读到自己的索引", M.load_index(uid="222")["meta"].get("who") == "B",
          M.load_index(uid="222")["meta"])
    check("默认桶没被账号桶污染",
          M.load_index()["meta"].get("who") != "A", M.load_index()["meta"])

    M.write_scan_pid(1001, uid="111")
    M.write_scan_pid(2002, uid="222")
    check("pid 按账号分开",
          (M.read_scan_pid(uid="111"), M.read_scan_pid(uid="222")) == (1001, 2002),
          (M.read_scan_pid(uid="111"), M.read_scan_pid(uid="222")))

    M.record_scan({"id": "r1", "who": "A"}, uid="111")
    M.record_scan({"id": "r2", "who": "B"}, uid="222")
    ha = [r.get("who") for r in M.load_history(uid="111")["runs"]]
    hb = [r.get("who") for r in M.load_history(uid="222")["runs"]]
    check("历史按账号分开", ha == ["A"] and hb == ["B"], (ha, hb))

    # 老名字: 老脚本 `cok_map.DEFAULT_INDEX` 仍可读
    check("老名字 DEFAULT_INDEX 可读", M.DEFAULT_INDEX.endswith("map-index.json"),
          M.DEFAULT_INDEX)
    check("老名字 DATA_DIR 可读", os.path.isdir(M.DATA_DIR), M.DATA_DIR)
    check("老名字 HISTORY_FILE 可读", M.HISTORY_FILE.endswith("scan-history.json"))
    check("老名字 PID_FILE 可读", M.PID_FILE.endswith("scan.pid"))

    # snapshot_dirs 能一眼看出谁指到哪
    snap = M.snapshot_dirs()
    check("snapshot_dirs 列出账号目录", "111" in snap or "222" in snap,
          sorted(snap))


# ─────────────────────────── 6-7. cok_rally ───────────────────────────
def test_rally_scopes():
    print("\n[6/7] cok_rally: 默认桶老写法 + 账号桶隔离")
    import cok_rally as R

    d1 = tempfile.mkdtemp(prefix="scope_rally_a_")
    d2 = tempfile.mkdtemp(prefix="scope_rally_b_")
    R.set_data_dir(d1, uid="111")
    R.set_data_dir(d2, uid="222")

    check("两个账号注册表目录不同", R._dir_for("111") != R._dir_for("222"),
          (R._dir_for("111"), R._dir_for("222")))
    check("注册表文件跟目录走",
          R._registry_file("111").startswith(d1)
          and R._registry_file("222").startswith(d2))

    # 老写法: 直接操作 _KNOWN, 必须和 _known_for("") 是同一块内存
    R._KNOWN.clear()
    same = R._known_for() is R._KNOWN
    R._KNOWN["legacy"] = {"x": 1}
    check("_KNOWN 与 _known_for() 同一块内存", same, same)
    check("老写法写进去, 读得到", R._known_for().get("legacy") == {"x": 1},
          list(R._known_for()))
    R._CURSOR = 7
    check("老写法 _CURSOR 生效", R._cursor_for() == 7, R._cursor_for())

    # 账号桶与默认桶互不影响
    R._known_for("111")["a"] = {"x": 1}
    R._known_for("222")["b"] = {"x": 2}
    check("账号桶互不干扰",
          "a" in R._known_for("111") and "b" not in R._known_for("111")
          and "b" in R._known_for("222"),
          (list(R._known_for("111")), list(R._known_for("222"))))
    check("账号桶不污染默认桶",
          "legacy" in R._known_for() and "a" not in R._known_for(),
          list(R._known_for()))

    # set_data_dir(uid=) 只改自己
    before_b = R._dir_for("222")
    d3 = tempfile.mkdtemp(prefix="scope_rally_c_")
    R.set_data_dir(d3, uid="111")
    check("改 111 不动 222", R._dir_for("111") == d3 and R._dir_for("222") == before_b,
          (R._dir_for("111"), R._dir_for("222")))


# ─────────────────────────── 8-10. cok_identity ───────────────────────────
def test_identity():
    print("\n[8/9/10] cok_identity: 键名归一 / for_client / 完整性检查")
    import cok_identity as I

    check("key_of: dict 取 gameUid", I.key_of({"gameUid": " 111 "}) == "111",
          I.key_of({"gameUid": " 111 "}))
    check("key_of: 字符串去空格", I.key_of(" 222 ") == "222")
    check("key_of: 数字转字符串", I.key_of(333) == "333")
    check("key_of: None -> 空", I.key_of(None) == "")
    check("key_of: 没 gameUid 的 dict -> 空", I.key_of({"x": 1}) == "")

    check("resolve: 库里没有 -> {gameUid}", I.resolve("999999999") == {"gameUid": "999999999"},
          I.resolve("999999999"))
    check("resolve: dict 原样返回",
          I.resolve({"gameUid": "1", "pfId": "p"}) == {"gameUid": "1", "pfId": "p"})
    check("resolve: None -> {}", I.resolve(None) == {})

    check("label_of: 库里没有 -> 空", I.label_of("999999999") == "",
          repr(I.label_of("999999999")))
    d = I.dir_of("999999999")
    check("dir_of: 建出账号目录", os.path.isdir(d) and d.endswith("999999999"), d)

    # for_client: 模板 + 公共真值 + 账号自己
    cli = I.for_client(None)
    check("for_client: 返回 dict 且有协议字段",
          isinstance(cli, dict) and bool(cli.get("pf")), sorted(cli)[:5])
    # 占位符不能被当真值
    ph = [k for k, v in cli.items() if isinstance(v, str) and v.startswith("<")]
    check("for_client: 没把占位符当真值(至少 baseActiveKey 不是)",
          not (cli.get("baseActiveKey") or "").startswith("<"),
          cli.get("baseActiveKey"))

    # missing_fields 同时抓空值和占位符
    miss = I.missing_fields(None)
    check("missing_fields: 空账号缺一堆字段", len(miss) >= 5, miss)
    check("is_complete: 空账号不完整", I.is_complete(None) is False)

    # 把"库里的完整账号"该有的字段都填上, 才算"齐"
    full = {"gameUid": "123456", "pfId": "cn_x:t", "pf": "cn_x", "buildCode": "abc",
            "host": "h", "port": 1, "zn": "COK", "signCode": "s" * 32,
            "deviceId": "dev", "uuid": "u-1", "platformToken": "tok"}
    fake = I.for_client(full)
    check("missing_fields: 填齐了就没缺", I.missing_fields(fake) == [],
          I.missing_fields(fake))
    check("is_complete: 填齐了就算完整", I.is_complete(fake) is True)

    ph_acc = dict(fake, signCode="<占位>")
    check("missing_fields: 占位符也算缺",
          "signCode" in I.missing_fields(ph_acc), I.missing_fields(ph_acc))


# ─────────────────────── 11-12. cok_errorlog ───────────────────────
def test_errorlog():
    print("\n[11/12] cok_errorlog: 留痕不抛 / 分级 / 采样 / 清单")
    import logging
    import io
    import cok_errorlog as EL

    buf = io.StringIO()
    h = logging.StreamHandler(buf)
    h.setFormatter(logging.Formatter("%(levelname)s %(message)s"))
    lg = logging.getLogger("cok")
    old_level, old_prop = lg.level, lg.propagate
    lg.addHandler(h)
    lg.setLevel(logging.DEBUG)
    lg.propagate = False
    EL.reset_throttle()

    try:
        try:
            open("/不存在的文件")
        except Exception as e:
            EL.quiet(e, "读文件")
        try:
            raise RuntimeError("socket 挂了")
        except Exception as e:
            EL.quiet(e, "连游戏服")

        def _inner():
            try:
                int("abc")
            except Exception as e:
                EL.quiet(e)
        _inner()
        EL.quiet(None, "坏输入")        # 不能抛

        out = buf.getvalue()
        check("预期内异常记 DEBUG", "DEBUG 读文件" in out, out.strip()[:80])
        check("真异常记 WARNING", "WARNING 连游戏服" in out)
        check("WARNING 带栈", "Traceback" in out)
        check("自动定位到 文件:行号", "test_scope_and_identity.py:" in out,
              [l for l in out.splitlines() if "invalid literal" in l][:1])
    finally:
        lg.removeHandler(h)
        lg.setLevel(old_level)
        lg.propagate = old_prop

    EL.reset_throttle()
    for _ in range(5):
        try:
            raise ValueError("重复")
        except Exception as e:
            EL.quiet(e, "采样位置")
    ent = EL._seen.get("采样位置")
    check("采样计数累加", bool(ent) and ent[1] == 5, ent)

    rows = EL.audit_silent_pass(os.path.join(HERE, "..", "core"))
    check("审计器扫得到静默 pass", len(rows) > 0, len(rows))
    check("审计器条目结构正确",
          all({"file", "line", "func", "except_line"} <= set(r) for r in rows),
          sorted(rows[0]) if rows else None)


def main():
    test_scope_basics()
    test_map_scopes()
    test_rally_scopes()
    test_identity()
    test_errorlog()
    print()
    if _FAILED:
        print("失败 %d 项:" % len(_FAILED))
        for n in _FAILED:
            print("  FAIL", n)
        return 1
    print("全部通过")
    return 0


if __name__ == "__main__":
    sys.exit(main())