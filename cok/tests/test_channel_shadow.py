#!/usr/bin/env python3
"""回归测试: 模块里不能有"同名函数被后定义盖掉"的重复顶层定义。

2026-11-16 事故(网页端果盘渠道登录全挂):

    失败·渠道登录请求失败: list_identities() got an unexpected keyword argument 'with_role'

根因: ``cok_channel_login.py`` 里 ``list_identities`` **定义了两遍** ——
前面那个是完整版 ``(res, verbose=False, with_role=True)``(会顺带去游戏服
解析角色), 后面"多渠道统一入口"那节又写了一个精简版 ``(res, verbose=False)``。
Python 里后定义的**直接盖掉**先定义的, 而且:

  * import 时不报错、pyflakes 也不一定报(同名重复定义是合法语法)
  * 只在**跑到那条调用路径**时才炸 —— 而这条路径要真的连果盘服务器才走得到

于是 ``channel_login_list_small()`` 里的
``list_identities(res, verbose=verbose, with_role=with_role)``
永远 TypeError, 网页端只要点"渠道账号登录"就必然失败。

本文件锁两件事:
  1. **静态**: core/ 下每个模块都不许有重复的顶层函数/类定义(AST 扫)
  2. **行为**: 真的走一遍"登录 -> 列小号"流程(全程打桩, 不联网),
     断言每个小号都带上了游戏角色信息 —— 这条在 bug 存在时必然失败
"""
import ast
import collections
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
CORE = os.path.join(HERE, "..", "core")
sys.path.insert(0, CORE)
sys.path.insert(0, os.path.join(HERE, "..", "tools"))

_TMP = tempfile.mkdtemp(prefix="cok-channel-shadow-test-")
os.environ["COK_ACCOUNTS_DIR"] = os.path.join(_TMP, "accounts")
os.environ["COK_DATA_ROOT"] = os.path.join(_TMP, "data")
os.makedirs(os.environ["COK_ACCOUNTS_DIR"], exist_ok=True)

import cok_channel_login as channel  # noqa: E402


def _top_level_names(path):
    """模块顶层定义过的函数/类名(同名出现多次 = 后者盖前者)。"""
    with open(path, "rb") as fh:
        src = fh.read().decode("utf-8")
    tree = ast.parse(src, path)
    names = []
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            names.append(node.name)
    return names


def test_no_duplicate_top_level_defs():
    """core/ 下每个模块的顶层函数/类名不许重复。

    重复定义不会报错, 但会**静默盖掉**先定义的那个 ——
    表现出来就是"某个参数突然不认识了"(unexpected keyword argument)。
    """
    dups = []
    for fn in sorted(os.listdir(CORE)):
        if not fn.endswith(".py"):
            continue
        # `._xxx` 是 macOS tar 的 AppleDouble 伴随文件（二进制），不是源码。
        if fn.startswith("._"):
            continue
        path = os.path.join(CORE, fn)
        try:
            names = _top_level_names(path)
        except (SyntaxError, UnicodeDecodeError) as exc:
            dups.append("%s: 读取失败 %s" % (fn, str(exc)[:80]))
            continue
        for name, times in collections.Counter(names).items():
            if times > 1:
                dups.append("%s: %s 定义了 %d 次" % (fn, name, times))
    assert not dups, "同名顶层定义(后定义会盖掉先定义): " + "; ".join(dups)
    print("[PASS] core/ 下没有重复的顶层定义")


def test_list_identities_signature():
    """被多渠道约定调用的接口, 签名必须和调用方对得上。"""
    import inspect

    params = inspect.signature(channel.list_identities).parameters
    assert "with_role" in params, \
        "cok_channel_login.list_identities 少了 with_role 参数: %s" % list(params)
    params2 = inspect.signature(channel.channel_login_list_small).parameters
    assert "with_role" in params2, \
        "channel_login_list_small 少了 with_role 参数: %s" % list(params2)
    print("[PASS] list_identities / channel_login_list_small 签名正确")


def test_channel_login_list_small_returns_roles():
    """真走一遍"登录 -> 列小号"(全程打桩, 不联网)。

    这条在 bug 存在时必然 TypeError:
    调用方传 with_role=..., 而实际生效的是那个被盖掉的精简版。
    """
    saved = {
        "channel_login": channel.channel_login,
        "list_small_accounts": channel.list_small_accounts,
        "build_account_from_pf_id": channel.build_account_from_pf_id,
    }
    try:
        def fake_channel_login(account, password, verbose=False):
            return {"ok": True, "succeeded": True,
                    "authEnvelope": "Login_1_140514_key", "guopanUid": "GP123"}

        def fake_list_small_accounts(uid, env, verbose=False):
            assert uid == "GP123", uid
            return {"retcode": 0, "list": [
                {"perGameId": "PG001", "name": "小号一", "gameUin": "GU1"},
                {"perGameId": "PG002", "name": "小号二", "gameUin": "GU2"},
            ]}

        def fake_build_account_from_pf_id(pf_id, *args, **kwargs):
            # 第二个小号没角色(没开过号) -> 带 note, 但不能整条流程失败
            if pf_id.endswith("PG002"):
                return None, {"ok": False, "note": "无角色"}
            return ({"gameUid": "9999", "uuid": "uuid-1", "zn": "COK2223",
                     "buildCode": "bc", "roleName": "老兵"},
                    {"ok": True, "gameUserLevel": 55})

        channel.channel_login = fake_channel_login
        channel.list_small_accounts = fake_list_small_accounts
        channel.build_account_from_pf_id = fake_build_account_from_pf_id

        res = channel.channel_login_list_small("acct", "pwd", verbose=False)
        assert res.get("ok"), res
        items = res.get("smallAccounts") or []
        assert len(items) == 2, items
        # 角色信息(with_role=True)必须真的带上来 —— 说明生效的是完整版
        assert items[0].get("gameUid") == "9999", items[0]
        assert items[0].get("roleName") == "老兵", items[0]
        assert items[0].get("hasCharacter") is True, items[0]
        assert items[0].get("pfId") == "ewanqf:" + channel.PFID_PREFIX + "PG001", items[0]
        # 没角色的那个也要出现(只是标记没角色), 不能整条流程挂掉
        assert items[1].get("hasCharacter") is False, items[1]
        assert items[1].get("note") == "无角色", items[1]
        print("[PASS] 登录->列小号->带角色 整条流程走通")
    finally:
        for name, fn in saved.items():
            setattr(channel, name, fn)


def main():
    test_no_duplicate_top_level_defs()
    test_list_identities_signature()
    test_channel_login_list_small_returns_roles()


if __name__ == "__main__":
    main()
