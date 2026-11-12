#!/usr/bin/env python3
"""跑全部离线回归测试(不连游戏服)。

分类规则写在 ``NETWORK_TESTS`` 里: 名字出现在里面的用例**需要真实账号联网**,
只在你显式传 ``--with-network`` 时才跑 —— 默认跑的是"没网也能验证"的那批,
这样改一行代码后几秒钟就能拿到反馈, 不用等一个账号登录。

用法::

    python3 cok/tests/run_all.py                 # 只跑离线用例
    python3 cok/tests/run_all.py --with-network  # 连游戏服的也跑
    python3 cok/tests/run_all.py test_map        # 只跑名字里含 test_map 的
"""

import glob
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

#: 需要真实账号联网的用例(会真的登录游戏服, 慢且依赖账号状态)
NETWORK_TESTS = {
    "test_sign.py",        # 实测每日签到
    "test_pfid_rebuild.py",  # 用 pfId 反查角色并登录
}


def main(argv):
    with_network = "--with-network" in argv
    only = next((a for a in argv if not a.startswith("-")), None)

    tests = sorted(glob.glob(os.path.join(HERE, "test_*.py")))
    if only:
        tests = [t for t in tests if only in os.path.basename(t)]

    ran, failed, skipped = [], [], []
    for path in tests:
        name = os.path.basename(path)
        if name in NETWORK_TESTS and not with_network:
            skipped.append(name)
            continue
        print("\n" + "=" * 60)
        print("RUN  %s" % name)
        print("=" * 60)
        rc = subprocess.call([sys.executable, path])
        ran.append(name)
        if rc != 0:
            failed.append((name, rc))

    print("\n" + "=" * 60)
    print("跑了 %d 个用例" % len(ran))
    if skipped:
        print("跳过 %d 个(需要联网, 加 --with-network 才跑): %s"
              % (len(skipped), ", ".join(skipped)))
    if failed:
        print("失败 %d 个:" % len(failed))
        for name, rc in failed:
            print("  FAIL %s (exit=%d)" % (name, rc))
        return 1
    print("全部通过")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))