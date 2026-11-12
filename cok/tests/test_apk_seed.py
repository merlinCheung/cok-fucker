#!/usr/bin/env python3
"""回归测试: APK 内置种子(构建期烘焙的真值)能被运行时正确取到。

## 为什么要有这个种子

公开仓库里 ``cok_client.ACCOUNT`` 的 ``baseActiveKey`` 是**脱敏占位符**,
``signCode`` 是空串 —— 真值不能进 git 仓库(仓库是公开的)。

但别人**直接安装打包好的 APK** 时, 设备上:
  * 没有账号库(全新安装)
  * 没有手工塞进去的 ``data/public-fields.json`` / ``sign-codes.json``

于是:
  * signCode 空 -> 加号被判「凭据不完整(缺 signCode)」, 根本加不进去
  * baseActiveKey 空 -> 服务端丢弃所有加密指令 -> 「登录成功但界面全空」

所以 build.gradle 在**构建期**把本地 gitignored 缓存里的真值烘焙进 APK:
  * ``cok_client.py`` 的 ACCOUNT 里注入真 baseActiveKey
  * 新增 ``cok_seed.json``(public_fields + sign_codes), 运行时当兜底

真值只进**构建产物**, git 仓库里永远没有。

本文件锁住三件事:
  1. 运行时能从种子取到公共字段 / 渠道 signCode
  2. 种子**不会**盖掉账号库里更新的真值
  3. 种子文件不存在时(桌面端)一切照常, 不炸
另外: 若已构建出 APK, 直接检查 APK 里确实烘焙进去了(且不是占位符)。
"""
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "core"))
sys.path.insert(0, os.path.join(HERE, "..", "tools"))

_TMP = tempfile.mkdtemp(prefix="cok-apk-seed-test-")
os.environ["COK_ACCOUNTS_DIR"] = os.path.join(_TMP, "accounts")
os.environ["COK_DATA_ROOT"] = os.path.join(_TMP, "data")
os.makedirs(os.environ["COK_ACCOUNTS_DIR"], exist_ok=True)
os.makedirs(os.environ["COK_DATA_ROOT"], exist_ok=True)

import cok_accounts as accounts  # noqa: E402
import cok_channel_login as channel_login  # noqa: E402

#: 假的真值(测试用, 不是真凭据)
SEED_KEY = "SEEDBASEKEY00000000000000000000000000000000000000000000000"
SEED_SIGN = "seed1111111111111111111111111111"
REG_KEY = "REGBASEKEY00000000000000000000000000000000000000000000000000"
REG_SIGN = "reg11111111111111111111111111111"

_APK = os.path.join(os.path.dirname(os.path.dirname(HERE)), "android-app", "app",
                    "build", "outputs", "apk", "debug", "app-debug.apk")


def _write_seed(public_fields=None, sign_codes=None, path=None):
    """造一个种子文件, 并把 accounts.SEED_FILE 指过去。"""
    path = path or os.path.join(_TMP, "cok_seed.json")
    payload = {
        "public_fields": public_fields if public_fields is not None else {},
        "sign_codes": sign_codes if sign_codes is not None else {},
    }
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False)
    accounts.SEED_FILE = path
    return path


def _clear_registry():
    """清空账号库 + 本地缓存 + harvest 缓存 -> 只剩种子这一个来源。"""
    for fn in os.listdir(accounts.ACCOUNTS_DIR):
        try:
            os.remove(os.path.join(accounts.ACCOUNTS_DIR, fn))
        except OSError:
            pass
    for fn in ("public-fields.json", "sign-codes.json"):
        try:
            os.remove(os.path.join(accounts.DATA_ROOT, fn))
        except OSError:
            pass
    accounts._public_fields_cache["at"] = 0.0
    accounts._public_fields_cache["value"] = {}


def test_seed_provides_public_field():
    """只有种子时, 公共字段(含 baseActiveKey)也必须能取到真值。"""
    _clear_registry()
    _write_seed(public_fields={"baseActiveKey": SEED_KEY, "appVersion": "12.06.0"})
    fields = accounts.public_fields()
    assert fields.get("baseActiveKey") == SEED_KEY, fields
    tpl = accounts.template_account()
    assert tpl.get("baseActiveKey") == SEED_KEY, tpl.get("baseActiveKey")
    assert not accounts.is_placeholder(tpl.get("baseActiveKey"))
    print("[PASS] 公共字段能从 APK 种子取到真值")


def test_seed_provides_sign_code():
    """只有种子时, 渠道 signCode 也必须能取到(否则加号被判"凭据不完整")。"""
    _clear_registry()
    _write_seed(sign_codes={"com.hcg.cok.ewanqf.guopan": SEED_SIGN})
    got, src = channel_login._resolve_sign_code("com.hcg.cok.ewanqf.guopan", "", "cn_ewanqf")
    assert got == SEED_SIGN, got
    assert src == "APK 内置种子", src
    print("[PASS] 渠道 signCode 能从 APK 种子取到")


def test_registry_wins_over_seed():
    """账号库里的真值比种子新(渠道包换过证书) -> 账号库优先。"""
    _clear_registry()
    _write_seed(public_fields={"baseActiveKey": SEED_KEY},
                sign_codes={"com.hcg.cok.ewanqf.guopan": SEED_SIGN})
    acc = {
        "gameUid": "7001", "uuid": "u-7001", "deviceId": "d-7001",
        "buildCode": "b-7001", "signCode": REG_SIGN,
        "baseActiveKey": REG_KEY,
        "packageName": "com.hcg.cok.ewanqf.guopan", "pf": "cn_ewanqf",
        "added": "2026-11-12T10:00:00",
    }
    with open(os.path.join(accounts.ACCOUNTS_DIR, "7001.json"), "w",
              encoding="utf-8") as fh:
        json.dump(acc, fh, ensure_ascii=False)
    accounts._public_fields_cache["at"] = 0.0
    accounts._public_fields_cache["value"] = {}

    got_code, got_src = channel_login._resolve_sign_code(
        "com.hcg.cok.ewanqf.guopan", "", "cn_ewanqf")
    assert got_code == REG_SIGN, got_code
    assert got_src == "同包账号", got_src
    got_key = accounts.public_fields().get("baseActiveKey")
    assert got_key == REG_KEY, got_key
    print("[PASS] 账号库真值优先于 APK 种子")


def test_missing_seed_is_harmless():
    """桌面端没有 cok_seed.json -> 一切照常, 不抛异常。"""
    _clear_registry()
    accounts.SEED_FILE = os.path.join(_TMP, "does-not-exist.json")
    assert accounts.apk_seed_fields() == {}
    assert accounts.apk_seed_sign_codes() == {}
    assert accounts.public_fields() == {}
    got, src = channel_login._resolve_sign_code("com.hcg.cok.ewanqf.guopan", "", "cn_ewanqf")
    assert got == "" and src == "", (got, src)
    print("[PASS] 没有种子文件时不炸")


def test_built_apk_carries_real_seed():
    """已构建的 APK 里必须真的烘焙进了真值(且不是占位符)。"""
    if not os.path.exists(_APK):
        print("[SKIP] 还没构建 APK: %s" % _APK)
        return
    import io
    import re
    import zipfile
    with zipfile.ZipFile(_APK) as z:
        inner = zipfile.ZipFile(io.BytesIO(z.read("assets/chaquopy/app.imy")))
        names = inner.namelist()
        assert "cok_seed.json" in names, "APK 里没有 cok_seed.json"
        seed = json.loads(inner.read("cok_seed.json").decode("utf-8"))
        src = inner.read("cok_client.py").decode("utf-8", "replace")
    key = (seed.get("public_fields") or {}).get("baseActiveKey")
    assert key and not key.startswith("<"), "种子里的 baseActiveKey 是空/占位符"
    assert len(key) >= 32, "baseActiveKey 长度不对: %d" % len(key)
    # ACCOUNT 块里也必须是真值, 不能留占位符
    block = re.search(r"(?sm)^ACCOUNT = \{.*?^\}", src).group(0)
    baked = re.search(r'"baseActiveKey"\s*:\s*"([^"]*)"', block).group(1)
    assert baked == key, "ACCOUNT 里的 baseActiveKey 与种子不一致"
    assert "<baseActiveKey>" not in block, "ACCOUNT 里还留着占位符"
    # 渠道 signCode 也要烘焙进去
    signs = seed.get("sign_codes") or {}
    assert signs, "种子里没有渠道 signCode"
    for pkg, code in signs.items():
        assert code and not code.startswith("<"), pkg
    print("[PASS] APK 里确实烘焙了真值(公共字段 + 渠道 signCode)")


def main():
    test_seed_provides_public_field()
    test_seed_provides_sign_code()
    test_registry_wins_over_seed()
    test_missing_seed_is_harmless()
    test_built_apk_carries_real_seed()
    shutil.rmtree(_TMP, ignore_errors=True)


if __name__ == "__main__":
    main()
