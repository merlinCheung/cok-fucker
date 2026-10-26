#!/usr/bin/env python3
"""对照实验: 确定"命令是否存在"的可判别信号。

三组:
  A. 已知存在 + 参数齐全   -> 应有数据
  B. 已知存在 + 缺必需参数 -> 预期: 不回包(超时)
  C. 明显不存在的命令名   -> 预期: 断连 或 超时
"""
import os
import sys
import time

sys.path.insert(0, "/Users/a1234/workspace/me/cok/COK-CN1-analysis/protocol")
from cok_client import CokClient  # noqa: E402

CASES = [
    ("A 存在+参数齐全", "cmd.ping", None),
    ("A 存在+参数齐全", "monthlySign.info", None),
    ("B 存在+缺参数", "daily.quest.ls", None),
    ("B 存在+缺参数", "hero.introduction", None),
    ("C 不存在", "zzz.definitely.not.a.cmd", None),
    ("C 不存在", "totallyFakeCmd", None),
    ("C 不存在", "build.zzznotreal", None),
]


def run(cmd, params, timeout=10.0):
    c = CokClient(timeout=timeout)
    t0 = time.time()
    try:
        c.connect(retries=1, backoff=1)
        c.bin_handshake()
        c.login()
        try:
            c.call("cmd.ping")
        except Exception:
            pass
        r = c.call(cmd, params, retries=0)
        p = r.get("__params__") or {}
        return "DATA", "%s | keys=%s" % (p.get("errorCode") or "", ",".join(list(p.keys())[:4])), time.time() - t0
    except Exception as e:  # noqa: BLE001
        msg = str(e)
        kind = "CLOSED" if ("关闭" in msg or "reset" in msg.lower()) else "TIMEOUT"
        return kind, msg[:50], time.time() - t0
    finally:
        try:
            c.close()
        except Exception:
            pass


def main():
    for label, cmd, params in CASES:
        st, detail, dt = run(cmd, params)
        print("  %-18s %-32s %-8s %5.1fs  %s" % (label, cmd, st, dt, detail))
        sys.stdout.flush()


if __name__ == "__main__":
    main()
