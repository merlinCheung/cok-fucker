#!/usr/bin/env python3
"""账号凭据的 SFS 整数类型回归测试。

背景(2026-10-27 实测): `TypedInt` 是 int 的子类, **JSON 存盘会把它退化成
裸 int**。再读回来时 SFS 编码按值大小选类型:

    gmLogin=0      -> BYTE(0x02)   本该是 INT(0x04)
    screen_h=2577  -> SHORT(0x03)  本该是 INT(0x04)

服务端对登录参数类型敏感, 类型一错就**拒登**: 登录响应里 id 是**数字**
(不是 `<前缀>_<密钥ID>` 字符串), 紧接着一个 `init.error` 推送, 连接被关。

多账号功能把凭据存成 JSON 再读回来, 等于每个号都会中招 —— 所以这条路径
必须有测试兜住。

跑法: python3 test_account_types.py
"""
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

_TMP = tempfile.mkdtemp(prefix="cok-accttypes-test-")
os.environ["COK_ACCOUNTS_DIR"] = os.path.join(_TMP, "accounts")
os.environ["COK_DATA_ROOT"] = os.path.join(_TMP, "data")

import cok_accounts as A  # noqa: E402
import cok_client  # noqa: E402
from cok_sfs import (  # noqa: E402
    TypedInt, SFS_BYTE, SFS_SHORT, SFS_INT, encode_value, restore_typed_fields,
)

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


def test_json_roundtrip_loses_type():
    """先确认"病根"真的存在: JSON 往返会把 TypedInt 变成裸 int。"""
    acc = dict(cok_client.ACCOUNT)
    rt = json.loads(json.dumps(acc, ensure_ascii=False))
    check(isinstance(acc["gmLogin"], TypedInt), "原始 gmLogin 带 SFS 类型标注")
    check(not isinstance(rt["gmLogin"], TypedInt),
          "JSON 往返后 gmLogin 退化成裸 int(病根)")
    check(encode_value(acc["gmLogin"])[0] == SFS_INT,
          "原始 gmLogin 编码为 INT")
    check(encode_value(rt["gmLogin"])[0] == SFS_BYTE,
          "退化后 gmLogin 编码成 BYTE(服务端会拒登)",
          "0x%02x" % encode_value(rt["gmLogin"])[0])


def test_restore_typed_fields():
    """restore_typed_fields 能把类型贴回去(含嵌套的 device_info)。"""
    acc = json.loads(json.dumps(cok_client.ACCOUNT, ensure_ascii=False))
    restore_typed_fields(acc, cok_client.ACCOUNT)
    check(isinstance(acc["gmLogin"], TypedInt)
          and acc["gmLogin"].sfs_type == SFS_INT, "gmLogin 恢复成 INT")
    di = acc.get("device_info") or {}
    check(isinstance(di.get("screen_h"), TypedInt)
          and di["screen_h"].sfs_type == SFS_INT, "device_info.screen_h 恢复成 INT")
    check(encode_value(di["screen_h"])[0] == SFS_INT,
          "screen_h 编码回 INT")
    # 布尔不能被当成整数处理
    tmpl = {"flag": TypedInt(1, SFS_INT)}
    vals = {"flag": True}
    restore_typed_fields(vals, tmpl)
    check(vals["flag"] is True, "布尔字段不被改成 TypedInt")


def test_client_merges_types():
    """CokClient 构造时会把合并后的账号类型补回来(所有账号来源都过这里)。"""
    raw = json.loads(json.dumps(cok_client.ACCOUNT, ensure_ascii=False))
    c = cok_client.CokClient(account=raw)
    check(isinstance(c.account["gmLogin"], TypedInt)
          and c.account["gmLogin"].sfs_type == SFS_INT,
          "CokClient 合并后 gmLogin 是 INT")
    check(encode_value(c.account["gmLogin"])[0] == SFS_INT,
          "CokClient 合并后 gmLogin 编码为 INT")
    check(isinstance(c.account["device_info"].get("screen_h"), TypedInt),
          "CokClient 合并后 device_info.screen_h 带类型")


def test_registry_get_account_typed():
    """账号库读出来的凭据必须带类型(否则多账号一个都登不上)。"""
    key = A.save_account({"gameUid": "777700002223", "roleName": "类型测试号"})
    got = A.get_account(key)
    check(got is not None, "入库后可读回")
    check(isinstance(got.get("gmLogin"), TypedInt)
          and got["gmLogin"].sfs_type == SFS_INT,
          "账号库读出的 gmLogin 带 INT 类型")
    check(isinstance((got.get("device_info") or {}).get("screen_h"), TypedInt),
          "账号库读出的 device_info.screen_h 带类型")
    # 入库时自动垫上内置模板 -> 存的是完整凭据, 不依赖设备
    check(got.get("baseActiveKey") and got.get("appVersion"),
          "入库时自动补齐内置模板字段(不依赖设备)")


def test_login_request_encoding():
    """端到端看一眼登录请求的编码: 类型对了才是能登的前提。"""
    raw = json.loads(json.dumps(cok_client.ACCOUNT, ensure_ascii=False))
    c = cok_client.CokClient(account=raw)
    acc = c.account
    ok = (encode_value(acc["gmLogin"])[0] == SFS_INT
          and encode_value(acc["device_info"]["screen_h"])[0] == SFS_INT
          and encode_value(acc["device_info"]["network_type"])[0] == SFS_INT)
    check(ok, "登录请求里三个整数字段都按 INT 编码")


def main():
    test_json_roundtrip_loses_type()
    test_restore_typed_fields()
    test_client_merges_types()
    test_registry_get_account_typed()
    test_login_request_encoding()
    print()
    if FAIL:
        print("%d 通过, %d 失败" % (PASS, FAIL))
        return 1
    print("全部通过 (%d)" % PASS)
    return 0


if __name__ == "__main__":
    sys.exit(main())
