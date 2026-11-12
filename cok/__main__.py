#!/usr/bin/env python3
"""统一入口: ``python3 -m cok <子命令> [参数...]``

把散落在仓库里的"要 cd 到某个目录才能跑"的脚本收成一个入口。
每个子命令只是**转发**给对应实现, 不复制任何业务逻辑。

    python3 -m cok console            # 网页控制台(最常用)
    python3 -m cok scan               # 全图扫描(断点续扫)
    python3 -m cok export             # 导出 Excel
    python3 -m cok verify             # 坐标抽样复核
    python3 -m cok locate             # 按名字查坐标
    python3 -m cok daemon             # 守护进程
    python3 -m cok preview            # 离线预览前端
    python3 -m cok test               # 跑离线回归测试
    python3 -m cok probe <名字>        # 跑一个协议探针(见 cok/tools/probes)
    python3 -m cok list               # 列出所有可用子命令
"""

import os
import subprocess
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)

# 让 "cok_client" 这类平铺 import 在包内也成立(安卓端/脚本共用同一套模块)。
#
# 顺序很重要: core/ 要在**最前**, 这样 `import cok_paths` 命中
# core/cok_paths.py —— 那是唯一一份实现(见该文件头部的说明)。
for _p in (os.path.join(_ROOT, "core"), os.path.join(_ROOT, "tools"), _ROOT):
    if os.path.isdir(_p) and _p not in sys.path:
        sys.path.insert(0, _p)

#: 子命令 -> (说明, 实现文件, 传给实现的额外参数)
#: ⚠ 网页控制台/守护进程**要一直占着终端**, 在**本进程**里跑
#: HTTPServer.serve_forever() 永远回不来, Ctrl-C 也没人收得到 —— 所以
#: 前台常驻的子命令单独走 `_run_foreground`(exec 后由终端信号控制)。
COMMANDS = {
    "console": ("网页控制台(监控 + 操作)", "core/cok_web.py",
                ["--account-device", "--port", "8770"]),
    "daemon": ("守护进程(后台轮询 + 推送)", "core/cok_daemon.py", []),
    "scan": ("全图扫描(独立进程, 可断点续扫)", "tools/scan_world.py", []),
    "export": ("导出地图索引为 Excel", "tools/export_excel.py", []),
    "verify": ("坐标抽样复核", "tools/verify_points.py", []),
    "preview": ("前端离线预览(不连游戏服)", "tools/preview_web.py",
                ["--port", "8771"]),
    "speedup": ("建造/造兵队列加速", "core/cok_speedup.py", []),
    "sweep": ("扫背包", "tools/sweep_bag.py", []),
    "dump-bag": ("dump 背包", "tools/dump_bag.py", []),
    "seed-boss": ("把 boss-zone 灌进集结注册表", "tools/seed_boss_registry.py", []),
}

#: 前台常驻类子命令: 日志流式转发, Ctrl-C 一起停
FOREGROUND = ("console", "daemon", "preview")

#: 子命令里用户可能想覆盖的端口参数(放在实现的参数之前, 后面的覆盖前面的)
PASSTHROUGH = ("--port", "--host", "--token", "--no-token", "--mock-dock",
               "--mock-hunt", "--account", "--label")


def _usage(code=0):
    print(__doc__.strip())
    print("\n可用子命令:")
    for name in sorted(COMMANDS):
        desc, rel, _ = COMMANDS[name]
        print("  %-10s %s" % (name, desc))
    print("  %-10s %s" % ("locate", "按名字查坐标(需 Python 交互)"))
    print("  %-10s %s" % ("probe", "跑一个协议探针(cok/tools/probes)"))
    print("  %-10s %s" % ("test", "跑离线回归测试(cok/tests)"))
    print("  %-10s %s" % ("list", "列出本帮助"))
    return code


def _resource_dir():
    """包内资源目录: 与 `cok_paths` 的默认值保持一致。"""
    return os.path.join(_HERE, "resources")


def _data_root():
    return os.path.join(_HERE, "data")


def _run_script(rel, argv):
    """在当前进程里跑一个脚本文件(等价于 python3 <脚本>)。"""
    path = os.path.join(_HERE, rel)
    if not os.path.exists(path):
        print("[!] 找不到实现: %s" % path)
        return 2
    sys.argv = [path] + list(argv)
    # 资源/数据目录由环境变量指着, 子进程(扫描器)才继承得到
    os.environ.setdefault("COK_RESOURCES_DIR", _resource_dir())
    os.environ.setdefault("COK_DATA_ROOT", _data_root())
    with open(path, "r", encoding="utf-8") as fh:
        src = fh.read()
    # 以 __main__ 身份执行, 脚本里的 if __name__ == "__main__" 才会触发
    exec(compile(src, path, "exec"), {"__name__": "__main__", "__file__": path})
    return 0


def _run_tests(argv):
    import subprocess
    # 统一走 cok/tests/run_all.py（它自己处理 --with-network / 离线默认跳过）
    runner = os.path.join(_HERE, "tests", "run_all.py")
    if not os.path.exists(runner):
        print("[!] 没有找到测试入口: %s" % runner)
        return 1
    rc = subprocess.call([sys.executable, runner] + list(argv))
    return rc


def _run_probe(argv):
    if not argv:
        print("用法: python3 -m cok probe <探针名>")
        print("可选探针:")
        for f in sorted(os.listdir(os.path.join(_HERE, "tools", "probes"))):
            if f.startswith("probe_") and f.endswith(".py"):
                print("  ", f[:-3])
        return 1
    name = argv[0]
    if not name.startswith("probe_"):
        name = "probe_" + name
    path = os.path.join(_HERE, "tools", "probes", name + ".py")
    if not os.path.exists(path):
        print("[!] 没有这个探针: %s" % name)
        return 2
    return _run_script(os.path.join("tools", "probes", name + ".py"), argv[1:])


def _merge_flags(argv):
    """把用户传的 --port / --token 等拼进实现参数，用户值覆盖默认值。"""
    out = []
    for flag in PASSTHROUGH:
        for i, tok in enumerate(argv):
            if tok == flag or tok.startswith(flag + "="):
                out.append(argv[i])
                if tok == flag and i + 1 < len(argv):
                    out.append(argv[i + 1])
                break
    return out + argv


def _run_foreground(rel, argv):
    """前台常驻子命令：exec 后跑，Ctrl-C 一起停。"""
    path = os.path.join(_HERE, rel)
    if not os.path.exists(path):
        print("[!] 找不到实现: %s" % path)
        return 2
    sys.argv = [path] + _merge_flags(argv)
    os.environ.setdefault("COK_RESOURCES_DIR", _resource_dir())
    os.environ.setdefault("COK_DATA_ROOT", _data_root())
    with open(path, "r", encoding="utf-8") as fh:
        src = fh.read()
    exec(compile(src, path, "exec"), {"__name__": "__main__", "__file__": path})
    return 0


def _run_subprocess(rel, argv):
    """脚本放进独立进程跑，日志原样转发到当前终端。"""
    path = os.path.join(_HERE, rel)
    if not os.path.exists(path):
        print("[!] 找不到实现: %s" % path)
        return 2
    env = dict(os.environ)
    env.setdefault("COK_RESOURCES_DIR", _resource_dir())
    env.setdefault("COK_DATA_ROOT", _data_root())
    return subprocess.call(
        [sys.executable, path] + list(argv), env=env)


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0] in ("-h", "--help", "help", "list"):
        return _usage()

    cmd, rest = argv[0], argv[1:]
    if cmd == "test":
        return _run_tests(rest)
    if cmd == "probe":
        return _run_probe(rest)

    entry = COMMANDS.get(cmd)
    if entry is None:
        print("[!] 未知子命令: %s\n" % cmd)
        return _usage(2)
    desc, rel, default_args = entry
    if cmd in FOREGROUND:
        return _run_foreground(rel, rest)
    return _run_subprocess(rel, default_args + _merge_flags(rest))


if __name__ == "__main__":
    sys.exit(main())