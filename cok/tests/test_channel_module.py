#!/usr/bin/env python3
"""回归测试: 渠道登录模块可导入 + 凭据占位符治理。

2026-11-12 事故(安卓端点「渠道账号登录」报"模块未加载"):
  公开仓库脱敏时把 cok_channel_login.py 里的 signCode 占位符写成了
  **没闭合的字符串**::

      "signCode": "<果盘渠道公共 signCode(32 位 hex)>,     # 少一个右引号

  → SyntaxError: EOL while scanning string literal
  → cok_web.py 的 ``except Exception: channel = None`` 把异常**静默吞掉**
  → PC 和安卓**一起**只看到一句"渠道登录模块未加载", 完全查不到是哪一行炸了。

同一批脱敏还把 cok_client.ACCOUNT 的 baseActiveKey / signCode 换成了占位符。
那不是"少了点东西", 而是**假值**: 拿它当凭据, 服务端会丢弃所有加密指令
(表现是"登录成功但界面全空"), 极难查。

本文件锁住四件事:
  1. protocol/ 下每个 .py 都能编译 + 关键模块都能 import (语法回归)
  2. 模板里不残留脱敏占位符, 公共字段从账号库取到真值
  3. 渠道 signCode 不写死, 按 packageName 取**最新**账号的真值
  4. 账号列表不再把背包缓存(<uid>.items.json)当成账号
"""
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "core"))
sys.path.insert(0, os.path.join(HERE, "..", "tools"))

_TMP = tempfile.mkdtemp(prefix="cok-channel-module-test-")
os.environ["COK_ACCOUNTS_DIR"] = os.path.join(_TMP, "accounts")
os.environ["COK_DATA_ROOT"] = os.path.join(_TMP, "data")
os.makedirs(os.environ["COK_ACCOUNTS_DIR"], exist_ok=True)

import cok_accounts as accounts  # noqa: E402
import cok_client  # noqa: E402
import cok_channel_login as channel_login  # noqa: E402
import cok_web  # noqa: E402

#: 假的公共字段真值(测试用, 不是真凭据)
REAL_BASE_KEY = "REALBASEKEY0000000000000000000000000000000000000000000000"
OLD_SIGN = "old0000000000000000000000000000"
NEW_SIGN = "new1111111111111111111111111111"


def _seed():
    """在临时账号库里放两个同渠道账号(入库时间不同) + 一个背包缓存。"""
    d = accounts.ACCOUNTS_DIR
    common = {
        "baseActiveKey": REAL_BASE_KEY,
        "packageName": "com.hcg.cok.ewanqf.guopan",
        "pf": "cn_ewanqf",
        "host": "txaia-cok.elexapp.com",
        "port": 32231,
        "appVersion": "12.06.0",
        "luaVersion": "release_12.06.0_25",
        "device_info": {"os_version": "12.06.0"},
    }
    old = dict(common, gameUid="1001", uuid="uuid-old", deviceId="dev-old",
               buildCode="bc-old", signCode=OLD_SIGN, added="2026-10-30T00:09:12")
    new = dict(common, gameUid="1002", uuid="uuid-new", deviceId="dev-new",
               buildCode="bc-new", signCode=NEW_SIGN, added="2026-11-09T09:17:58")
    for acc in (old, new):
        with open(os.path.join(d, "%s.json" % acc["gameUid"]), "w",
                  encoding="utf-8") as fh:
            json.dump(acc, fh, ensure_ascii=False)
    # 背包缓存: 不是账号, 不该出现在账号列表里
    with open(os.path.join(d, "1002.items.json"), "w", encoding="utf-8") as fh:
        json.dump({"items": []}, fh)


def test_all_modules_compile():
    """protocol/ 下每个 .py 都必须能编译 —— 语法错误会让整个模块消失。"""
    broken = []
    for fn in sorted(os.listdir(HERE)):
        if not fn.endswith(".py"):
            continue
        path = os.path.join(HERE, fn)
        try:
            with open(path, encoding="utf-8") as fh:
                compile(fh.read(), path, "exec")
        except SyntaxError as exc:
            broken.append("%s:%s %s" % (fn, exc.lineno, exc.msg))
    assert not broken, "语法错误: " + "; ".join(broken)
    print("[PASS] protocol/ 下所有 .py 都能编译")


def test_channel_module_importable():
    """渠道登录模块必须能 import —— cok_web 靠它提供渠道账号密码登录。"""
    assert channel_login is not None
    assert cok_web.channel is not None, "cok_web.channel 为 None: " + \
        (cok_web.CHANNEL_IMPORT_REASON or "?")
    assert not cok_web.CHANNEL_IMPORT_ERROR
    print("[PASS] cok_channel_login 可导入, cok_web 已挂上")


def test_template_has_no_placeholder():
    """模板里不能残留脱敏占位符 —— 那是假值, 当凭据用会让服务端丢指令。"""
    tpl = accounts.template_account()
    bad = [k for k, v in tpl.items() if accounts.is_placeholder(v)]
    assert not bad, "模板里还有占位符: %s" % bad
    # 身份字段必须留空(不能是别的账号的值, 也不能是假值)
    for k in ("pfId", "gameUid", "uuid", "deviceId", "buildCode", "signCode"):
        assert not tpl.get(k), "%s 应留空, 实际 %r" % (k, tpl.get(k))
    print("[PASS] 模板无占位符, 身份字段留空")


def test_public_fields_come_from_registry():
    """公共字段必须从账号库取到真值(baseActiveKey 缺了是真会出事)。"""
    tpl = accounts.template_account()
    assert tpl.get("baseActiveKey") == REAL_BASE_KEY, tpl.get("baseActiveKey")
    assert accounts.is_placeholder(cok_client.ACCOUNT.get("baseActiveKey")), \
        "前提变了: 模板里的 baseActiveKey 不再是占位符, 本用例失去意义"
    print("[PASS] 公共字段从账号库回填真值")


def test_resolve_sign_code_picks_newest():
    """渠道包换过证书 -> signCode 会变, 取**最新**入库的那个。

    取值顺序: 同 packageName -> 同 pf 渠道 -> 任意账号(兜底)。
    空 signCode 会让账号被判"凭据不完整", 直接连不上, 所以兜底也要给。
    """
    got, src = channel_login._resolve_sign_code("com.hcg.cok.ewanqf.guopan")
    assert got == NEW_SIGN, got
    assert src == "同包账号", src
    # 同渠道(pf)但不同包 -> 走第二档
    got2, src2 = channel_login._resolve_sign_code("com.hcg.cok.另一个包", "", "cn_ewanqf")
    assert got2 == NEW_SIGN, got2
    assert src2 == "同渠道账号", src2
    # 完全对不上 -> 兜底用任意账号的(总比空强)
    got3, src3 = channel_login._resolve_sign_code("com.hcg.cok.nearme.gamecenter")
    assert got3 == NEW_SIGN, got3
    assert src3 == "其它账号", src3
    print("[PASS] 渠道 signCode 按同包/同渠道/兜底取真值")


def test_build_account_uses_real_public_fields():
    """渠道导入出来的账号必须带真 baseActiveKey + 非空 signCode。"""
    acc, _gs = channel_login.build_account_from_pf_id(
        "ewanqf:1084TESTTOKEN",
        platform_token="1084TESTTOKEN",
        gamesvc={"ok": True, "gameUid": "9999", "uuid": "uuid-x",
                 "zn": "COK2223", "serverId": "2223", "gamePort": 32231,
                 "buildCode": "bc", "gameUserName": "T"},
    )
    assert acc["baseActiveKey"] == REAL_BASE_KEY, acc.get("baseActiveKey")
    assert acc["signCode"] == NEW_SIGN, acc.get("signCode")
    assert not accounts.is_placeholder(acc["baseActiveKey"])
    print("[PASS] 渠道导入账号带真公共字段")


def test_list_accounts_skips_items_cache():
    """背包缓存 <uid>.items.json 不是账号, 不该出现在账号列表里。"""
    keys = [a["key"] for a in accounts.list_accounts()]
    assert "1002.items" not in keys, keys
    assert "1001" in keys and "1002" in keys, keys
    print("[PASS] 账号列表不再混入 .items 缓存")


def test_save_account_keeps_public_field():
    """空公共字段不能覆盖已有真值(空 baseActiveKey -> 服务端丢所有加密指令)。"""
    accounts.save_account({
        "pfId": "ewanqf:1084NEW", "gameUid": "1001", "uuid": "u2",
        "deviceId": "d2", "buildCode": "b2", "signCode": "s2",
        "baseActiveKey": "",
    })
    stored = accounts.get_account("1001")
    assert stored["baseActiveKey"] == REAL_BASE_KEY, stored.get("baseActiveKey")
    print("[PASS] 空公共字段不会覆盖真值")


def test_empty_value_does_not_wipe_real_signcode():
    """空 signCode 不能把账号库里**已有**的真值抹掉。

    2026-11-12 真机事故: 渠道导入的账号带着模板里的空 signCode,
    save_account 合并时把同渠道号已有的真 signCode 覆盖成了空 ->
    后面再导入新号就再也取不到真值 -> 新号被判"凭据不完整(缺 signCode)"。
    """
    before = accounts.get_account("1002").get("signCode")
    assert before == NEW_SIGN, before
    accounts.save_account({"gameUid": "1002", "signCode": "", "zn": "COK2218"})
    after = accounts.get_account("1002")
    assert after["signCode"] == NEW_SIGN, after.get("signCode")
    assert after.get("zn") == "COK2218", after.get("zn")
    print("[PASS] 空 signCode 不会抹掉已有真值")


def test_signcode_survives_account_deletion():
    """signCode 要写进本地缓存 —— 账号库空了/删号了仍然有。

    2026-11-12 真机事故: 新号入库时 signCode 取不到(账号库里那一刻
    没有可用的真值) -> 账号被判"凭据不完整" -> 连不上。
    缓存这一档保证"学到的真值"不会因为删号而丢。
    """
    got, src = channel_login._resolve_sign_code("com.hcg.cok.ewanqf.guopan")
    assert got == NEW_SIGN, got
    cache_file = os.path.join(accounts.DATA_ROOT, "sign-codes.json")
    assert os.path.exists(cache_file), cache_file
    # 模拟账号库被清空 -> 仍能从缓存取到
    for key in ("1001", "1002"):
        try:
            os.remove(os.path.join(accounts.ACCOUNTS_DIR, "%s.json" % key))
        except OSError:
            pass
    accounts._public_fields_cache["at"] = 0.0
    got2, src2 = channel_login._resolve_sign_code("com.hcg.cok.ewanqf.guopan")
    assert got2 == NEW_SIGN, got2
    assert src2 == "本地缓存", src2
    print("[PASS] signCode 落本地缓存, 账号删了也还在")


def test_client_backfill_uses_real_public_field():
    """CokClient 回填协议公共字段时**不能用脱敏占位符**当真值。

    模板(ACCOUNT)里的 baseActiveKey 是 "<baseActiveKey>" —— 把它回填进去,
    等于给服务端发一个假字段: 登录能过, 但服务端会丢弃所有加密指令
    (表现是"连上了但界面全空")。
    """
    c = cok_client.CokClient(account={"pfId": "ewanqf:1084X",
                                       "baseActiveKey": ""})
    got = c.account.get("baseActiveKey")
    assert not accounts.is_placeholder(got), got
    assert got == REAL_BASE_KEY, got
    print("[PASS] CokClient 公共字段回填用真值而不是占位符")


def main():
    _seed()
    test_all_modules_compile()
    test_channel_module_importable()
    test_template_has_no_placeholder()
    test_public_fields_come_from_registry()
    test_resolve_sign_code_picks_newest()
    test_build_account_uses_real_public_fields()
    test_list_accounts_skips_items_cache()
    test_save_account_keeps_public_field()
    test_empty_value_does_not_wipe_real_signcode()
    test_signcode_survives_account_deletion()
    test_client_backfill_uses_real_public_field()
    shutil.rmtree(_TMP, ignore_errors=True)


if __name__ == "__main__":
    main()
