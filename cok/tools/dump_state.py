#!/usr/bin/env python3
"""打印关键命令的完整返回结构, 用于设计常驻工具的状态字段。"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

sys.path.insert(0, os.path.join(HERE, "..", "core"))
sys.path.insert(0, os.path.join(HERE, "..", "tools"))
from cok_client import CokClient  # noqa: E402


def main():
    c = CokClient(timeout=15)
    c.connect()
    c.bin_handshake()
    c.login()
    try:
        c.call("cmd.ping")
    except Exception:
        pass
    for cmd in ["monthlySign.info", "dailyQuest2025.data", "allianceNewBoss.bossMainInfo",
                "lordTask.data", "overview_new.data", "story.task.info"]:
        try:
            r = c.call(cmd)
            p = r.get("__params__") or {}
            print("=== %s (mode=%s) ===" % (cmd, r.get("__mode__")))
            for k, v in p.items():
                if k == "_cok_":
                    continue
                s = json.dumps(v, ensure_ascii=False, default=str)
                print("  %-22s %s" % (k, s[:400]))
            print()
        except Exception as e:  # noqa: BLE001
            print("=== %s 失败: %s\n" % (cmd, str(e)[:80]))
    c.close()


if __name__ == "__main__":
    main()
