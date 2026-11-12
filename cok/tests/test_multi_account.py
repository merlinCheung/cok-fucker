#!/usr/bin/env python3
"""多账号改造的回归测试: 分键账号锁 + 账号注册表。

跑法: python3 test_multi_account.py
"""
import os
import sys
import tempfile
import threading

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "core"))
sys.path.insert(0, os.path.join(HERE, "..", "tools"))

# 用临时目录隔离注册表与锁, 别碰正在运行的控制台。
_TMP = tempfile.mkdtemp(prefix="cok-multiacct-test-")
os.environ["COK_ACCOUNTS_DIR"] = os.path.join(_TMP, "accounts")
os.environ["COK_DATA_ROOT"] = os.path.join(_TMP, "data")
# 分键锁测试必须**不**设 COK_ACCOUNT_LOCK_FILE —— 一旦设了, 所有 key 会
# 被强制指到同一把锁(那是测试隔离语义), 就测不出"不同账号不互斥"。
os.environ.pop("COK_ACCOUNT_LOCK_FILE", None)
import cok_client  # noqa: E402
# 把锁文件落到临时目录, 不污染工作区。
cok_client._HERE = _TMP

import cok_accounts as A  # noqa: E402

PASS = 0
FAIL = 0


def check(cond, name, extra=""):
    global PASS, FAIL
    tag = "[PASS]" if cond else "[FAIL]"
    if cond:
        PASS += 1
    else:
        FAIL += 1
    print("%s %s%s" % (tag, name, ("  — " + extra) if extra else ""))


def _try_lock(key):
    """另一个线程里尝试抢某账号的锁(不等待), 返回是否抢到。"""
    got = {"ok": None}

    def run():
        try:
            with cok_client.account_lock(timeout=0.0, purpose="probe", key=key):
                got["ok"] = True
        except cok_client.AccountBusy:
            got["ok"] = False
    t = threading.Thread(target=run)
    t.start()
    t.join()
    return got["ok"]


def test_keyed_lock():
    key_a = "111100002223"
    key_b = "222200002223"
    # 占住 A, 另一个线程再抢 A 应失败, 抢 B 应成功。
    with cok_client.account_lock(timeout=0.0, purpose="hold-A", key=key_a):
        check(_try_lock(key_a) is False, "同账号 A 被占时其它线程抢不到")
        check(_try_lock(key_b) is True, "不同账号 B 不受 A 占用影响(并发可用)")
    # A 释放后应能再抢到。
    check(_try_lock(key_a) is True, "A 释放后可再取")
    # 不同账号用不同锁文件。
    check(cok_client.lock_file_for(key_a) != cok_client.lock_file_for(key_b),
          "不同账号锁文件路径不同")


def test_default_key_unchanged():
    # key=None 时仍是单文件默认锁, 两个 None 互斥。
    with cok_client.account_lock(timeout=0.0, purpose="hold-default"):
        check(_try_lock(None) is False, "默认锁(无 key)仍然全局互斥")
    check(cok_client.lock_file_for(None).endswith(".cok-account.lock"),
          "默认锁文件名未变")


def test_registry_roundtrip():
    acc = {"gameUid": "999900002223", "roleName": "测试号", "signCode": "x"}
    key = A.save_account(acc, label="小号一")
    check(key == "999900002223", "入库返回 gameUid 作为 id", key)
    got = A.get_account(key)
    check(got and got.get("label") == "小号一", "读回带 label")
    check(got.get("added"), "自动盖了 added 时间戳", got.get("added"))
    # 合并写: 再写一次只更新部分字段, 保留 label/added。
    A.save_account({"gameUid": key, "host": "h.example.com"})
    got2 = A.get_account(key)
    check(got2.get("host") == "h.example.com" and got2.get("label") == "小号一",
          "二次写入合并且保留 label")
    # active 指针。
    A.set_active_key(key)
    check(A.get_active_key() == key, "active 指针可读回", A.get_active_key())
    # 列表。
    A.save_account({"gameUid": "888800002223", "roleName": "小号二"})
    keys = {a["key"] for a in A.list_accounts()}
    check({"999900002223", "888800002223"} <= keys, "列表含两个账号", str(keys))
    # 每账号独立数据目录。
    p1 = A.data_path("999900002223", "map-index.json")
    p2 = A.data_path("888800002223", "map-index.json")
    check(p1 != p2 and os.path.dirname(p1) != os.path.dirname(p2),
          "两账号的数据目录互相隔离")
    # 删除。
    check(A.remove_account("888800002223") is True, "删除账号")
    check(A.get_account("888800002223") is None, "删后读不到")


def main():
    test_keyed_lock()
    test_default_key_unchanged()
    test_registry_roundtrip()
    print()
    if FAIL:
        print("%d 通过, %d 失败" % (PASS, FAIL))
        return 1
    print("全部通过 (%d)" % PASS)
    return 0


if __name__ == "__main__":
    sys.exit(main())
