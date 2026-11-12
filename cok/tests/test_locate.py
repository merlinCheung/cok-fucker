#!/usr/bin/env python3
"""玩家坐标查询的单元测试(不连游戏服)。

覆盖:
  * index <-> 坐标 的互逆换算(index = x + 1 + int(1201*y))
  * 搜索返回解析(多种可能的响应形状)
  * 同名多候选时选 uid
  * 服务端错误码 / 无坐标时的失败分支
"""
import json
import os
import sys
import tempfile

os.environ["COK_ACCOUNT_LOCK_FILE"] = os.path.join(
    tempfile.gettempdir(), "cok-test-locate-%d.lock" % os.getpid())
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "core"))
sys.path.insert(0, os.path.join(HERE, "..", "tools"))

import cok_locate  # noqa: E402
import cok_hunt  # noqa: E402


class FakeClient(object):
    """按脚本回放命令。"""

    def __init__(self, script):
        self.script = script
        self.calls = []

    def call(self, cmd, params=None, retries=1):
        self.calls.append((cmd, dict(params or {})))
        r = self.script.get(cmd)
        if r is None:
            raise RuntimeError("命令 %s 无响应" % cmd)
        if isinstance(r, list):
            r = r[0] if len(self.calls) == 1 else r[1]
        return r


def check(name, cond, detail=""):
    print("[%s] %s%s" % ("PASS" if cond else "FAIL", name,
                         ("  — " + detail) if detail else ""))
    return bool(cond)


def main():
    ok = True

    # ---- 1) index <-> 坐标 互逆 ----
    ok &= check("index_to_point 往返正确",
                cok_locate.index_to_point(cok_hunt.point_index(500, 300)) == (500, 300),
                str(cok_locate.index_to_point(cok_hunt.point_index(500, 300))))
    ok &= check("index_to_point(0) 返回 None",
                cok_locate.index_to_point(0) is None)
    ok &= check("index_to_point(非法值) 返回 None",
                cok_locate.index_to_point("abc") is None)
    ok &= check("index_to_point(1) = (0,0)",
                cok_locate.index_to_point(1) == (0, 0),
                str(cok_locate.index_to_point(1)))
    # 与打怪用的换算必须一致
    idx = cok_hunt.point_index(473, 939)
    ok &= check("与 cok_hunt.point_index 一致",
                cok_locate.index_to_point(idx) == (473, 939),
                "index=%d -> %s" % (idx, cok_locate.index_to_point(idx)))

    # ---- 2) 搜索成功 ----
    script = {
        "search.player.spy": [
            {"__params__": {"array": [{"name": "张三", "uid": "u1"},
                                      {"name": "李四", "uid": "u2"}]}},
            {"__params__": {"location": 361203, "time": 1}},
        ],
    }
    cl = FakeClient(script)
    r = cok_locate.locate(cl, "张三")
    ok &= check("查询成功", r.get("ok") is True, json.dumps(r, ensure_ascii=False)[:120])
    # index 361203 -> x=(361203-1)%1201=902, y=(361203-1)//1201=300
    ok &= check("坐标换算正确", r.get("x") == 902 and r.get("y") == 300,
                "x=%s y=%s loc=%s" % (r.get("x"), r.get("y"), r.get("location")))
    ok &= check("命令名正确",
                cl.calls[0][0] == "search.player.spy", cl.calls[0][0])
    ok &= check("第一个请求带 userName",
                cl.calls[0][1].get("userName") == "张三", str(cl.calls[0][1]))
    ok &= check("第二个请求带 uid",
                cl.calls[1][1].get("uid") == "u1", str(cl.calls[1][1]))
    ok &= check("候选列表保留 2 个",
                len(r.get("candidates") or []) == 2, str(len(r.get("candidates") or [])))

    # ---- 3) 同名多候选, 指定 uid ----
    script2 = {
        "search.player.spy": [
            {"__params__": {"array": [{"name": "同名", "uid": "ua"},
                                      {"name": "同名", "uid": "ub"}]}},
            {"__params__": {"location": 361203}},
        ],
    }
    cl2 = FakeClient(script2)
    r2 = cok_locate.locate(cl2, "同名", uid="ub")
    ok &= check("指定 uid 时选中该候选",
                cl2.calls[1][1].get("uid") == "ub", str(cl2.calls[1][1]))

    # ---- 4) 找不到人 ----
    cl3 = FakeClient({"search.player.spy": [{"__params__": {"array": []}}]})
    r3 = cok_locate.locate(cl3, "不存在")
    ok &= check("找不到时 ok=False 且有中文提示",
                r3.get("ok") is False and "没有找到" in (r3.get("error") or ""),
                str(r3.get("error")))

    # ---- 5) 服务端错误码 ----
    cl4 = FakeClient({"search.player.spy": [{"__params__": {"errorCode": "E000000"}}]})
    r4 = cok_locate.locate(cl4, "某���")
    ok &= check("服务端错误码被透传",
                r4.get("ok") is False and r4.get("errorCode") == "E000000",
                str(r4.get("errorCode")))

    # ---- 6) 没有坐标 ----
    cl5 = FakeClient({"search.player.spy": [{"__params__": {"array": [{"name": "甲", "uid": "u9"}]}},
                                             {"__params__": {"time": 1}}]})
    r5 = cok_locate.locate(cl5, "甲")
    ok &= check("服务端没给坐标时给出明确原因",
                r5.get("ok") is False and "没有返回坐标" in (r5.get("error") or ""),
                str(r5.get("error")))

    # ---- 6b) 第一次就带 location: 不能再发第二次(会多扣道具) ----
    cl5b = FakeClient({"search.player.spy": [
        {"__params__": {"array": [{"name": "甲", "uid": "u9"}], "location": 1202}},
    ]})
    r5b = cok_locate.locate(cl5b, "甲")
    ok &= check("第一次就带坐标时直接返回",
                r5b.get("ok") is True and r5b.get("x") == 0 and r5b.get("y") == 1,
                "x=%s y=%s" % (r5b.get("x"), r5b.get("y")))
    ok &= check("第一次就带坐标时**只发一次请求**(省道具)",
                len(cl5b.calls) == 1, "发了 %d 次" % len(cl5b.calls))

    # ---- 6c) 错误码提示是人话 ----
    cl6b = FakeClient({"search.player.spy": [{"__params__": {"errorCode": "E100165"}}]})
    r6b = cok_locate.locate(cl6b, "某人")
    ok &= check("E100165 提示提到坐标侦查道具",
                "坐标侦查" in (r6b.get("error") or ""), str(r6b.get("error")))

    # ---- 7) 空名字 ----
    r6 = cok_locate.locate(FakeClient({}), "  ")
    ok &= check("空名字被拦下", r6.get("ok") is False, str(r6.get("error")))

    # ---- 8) 响应形状兼容性 ----
    for key in ("array", "list", "players"):
        s = {"search.player.spy": [{"__params__": {key: [{"name": "Z", "uid": "z1"}]}},
                                    {"__params__": {"location": 1202}}]}
        rr = cok_locate.locate(FakeClient(s), "Z")
        # index 1202 -> x=(1201)%1201=0, y=1201//1201=1
        ok &= check("响应形状 %s 也能解析" % key,
                    rr.get("ok") is True and rr.get("x") == 0 and rr.get("y") == 1,
                    "%s -> x=%s y=%s" % (key, rr.get("x"), rr.get("y")))

    print("\n%s" % ("全部通过" if ok else "存在失败项"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
