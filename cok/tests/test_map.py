#!/usr/bin/env python3
"""地图扫描器(cok_map)的单元测试(不连游戏服)。"""
import json
import os
import sys
import tempfile

os.environ["COK_ACCOUNT_LOCK_FILE"] = os.path.join(
    tempfile.gettempdir(), "cok-test-map-%d.lock" % os.getpid())
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "core"))
sys.path.insert(0, os.path.join(HERE, "..", "tools"))

import cok_map  # noqa: E402
import cok_hunt  # noqa: E402


class FakeClient(object):
    """模拟 world.get: 以中心点返回固定半径内的地块。"""

    def __init__(self, tiles_by_center=None, error=None):
        self.calls = []
        self.tiles_by_center = tiles_by_center or {}
        self.error = error

    def call(self, cmd, params=None, retries=1):
        self.calls.append((cmd, dict(params or {})))
        if self.error:
            return {"__params__": {"errorCode": self.error}}
        if cmd != "world.get":
            raise AssertionError("未预期的命令 %s" % cmd)
        cx = params["x"]
        cy = params["y"]
        tiles = self.tiles_by_center.get((int(cx), int(cy)), [])
        # points 是**字符串数组**(服务端真实形状)
        payload = json.dumps(tiles, ensure_ascii=False)
        return {"__params__": {"x": int(cx), "y": int(cy),
                               "points": [payload], "section": 1}}


def check(name, cond, detail=""):
    print("[%s] %s%s" % ("PASS" if cond else "FAIL", name,
                         ("  — " + detail) if detail else ""))
    return bool(cond)


def main():
    ok = True

    # ---- 1) 坐标换算与 cok_hunt 互逆 ----
    ok &= check("index_to_point 与 cok_hunt.point_index 互逆",
                cok_map.index_to_point(cok_hunt.point_index(531, 931)) == (531, 931),
                str(cok_map.index_to_point(cok_hunt.point_index(531, 931))))
    ok &= check("point_to_index 正确",
                cok_map.point_to_index(531, 931) == 1118663,
                str(cok_map.point_to_index(531, 931)))
    ok &= check("index 0 返回 None", cok_map.index_to_point(0) is None)

    # ---- 2) fetch_area 解析 ----
    tiles = [
        {"i": 1118663, "uid": "<uid-main>", "o": "元气少女李逵",
         "t": 1, "l": 30},
        {"i": 1116261, "uid": "151482316002223", "o": "种田小龙龙",
         "t": 1, "l": 30},
        {"i": 1111446, "t": 1003, "v": 552960, "l": 3},
    ]
    cl = FakeClient({(531, 931): tiles})
    res = cok_map.fetch_area(cl, 531, 931)
    ok &= check("fetch_area 成功", res["ok"] is True, str(res.get("error")))
    ok &= check("解析出 3 个地块", len(res["tiles"]) == 3, str(len(res["tiles"])))
    ok &= check("解析出 2 个玩家", len(res["players"]) == 2, str(len(res["players"])))
    p0 = res["players"][0]
    ok &= check("玩家带 uid/名字/坐标",
                p0["uid"] == "<uid-main>" and p0["name"] == "元气少女李逵"
                and p0["x"] == 531 and p0["y"] == 931,
                json.dumps(p0, ensure_ascii=False))
    ok &= check("参数类型是 INT(0x04)",
                cok_map._I(531).sfs_type == 0x04, hex(cok_map._I(531).sfs_type))
    ok &= check("命令名是 world.get", cl.calls[0][0] == "world.get")

    # ---- 3) 服务端错误码 ----
    cl2 = FakeClient(error="E000000")
    res2 = cok_map.fetch_area(cl2, 1, 1)
    ok &= check("错误码被透传",
                res2["ok"] is False and res2["errorCode"] == "E000000",
                str(res2.get("errorCode")))

    # ---- 4) 索引合并与去重 ----
    idx = {"players": {}, "meta": {}}
    added = cok_map.merge_players(idx, res["players"])
    ok &= check("首次并入 2 个玩家", added == 2, str(added))
    added2 = cok_map.merge_players(idx, res["players"])
    ok &= check("重复并入不重复计数", added2 == 0, str(added2))
    ok &= check("索引里有 2 个玩家", len(idx["players"]) == 2, str(len(idx["players"])))

    # ---- 5) 落盘 / 读回 ----
    tmp = os.path.join(tempfile.gettempdir(), "cok-test-map-%d.json" % os.getpid())
    cok_map.save_index(idx, tmp)
    back = cok_map.load_index(tmp)
    ok &= check("索引落盘后可读回",
                len(back["players"]) == 2, str(len(back.get("players") or {})))
    os.remove(tmp)

    # ---- 6) 按名字查找 ----
    hits = cok_map.find_players(idx, "李逵")
    ok &= check("按名字命中", len(hits) == 1 and hits[0]["uid"] == "<uid-main>",
                str([h["name"] for h in hits]))
    hits2 = cok_map.find_players(idx, "151482316")
    ok &= check("按 uid 片段命中", len(hits2) == 1, str(len(hits2)))
    ok &= check("空关键词返回空", cok_map.find_players(idx, "  ") == [])

    # ---- 7) 区域扫描: 步进覆盖 ----
    calls = []

    class ScanClient(FakeClient):
        def call(self, cmd, params=None, retries=1):
            calls.append((int(params["x"]), int(params["y"])))
            return FakeClient.call(self, cmd, params, retries)

    sc = ScanClient()
    tmp2 = os.path.join(tempfile.gettempdir(), "cok-test-map2-%d.json" % os.getpid())
    stats = cok_map.scan_area(sc, 0, 0, 23, 23, step=12, path=tmp2)
    ok &= check("扫描发了 4 次请求(0/12 x 0/12)", stats["requests"] == 4,
                str(stats["requests"]))
    ok &= check("步进点在 12 的倍数上",
                all(cx % 12 == 0 and cy % 12 == 0 for cx, cy in calls),
                str(calls))
    ok &= check("扫描落盘了索引", os.path.exists(tmp2))
    doc = cok_map.load_index(tmp2)
    ok &= check("扫描后 meta 标记完成", doc["meta"].get("partial") is False,
                json.dumps(doc["meta"], ensure_ascii=False))
    ok &= check("扫描结束后不再标记 scanning(页面不会一直显示扫描中)",
                doc["meta"].get("scanning") is False,
                json.dumps(doc["meta"], ensure_ascii=False))
    ok &= check("扫描结束后 requests 计数准确",
                doc["meta"].get("requests_done") == 4
                and doc["meta"].get("requests_total") == 4,
                json.dumps(doc["meta"], ensure_ascii=False))
    os.remove(tmp2)

    # ---- 8) 断点续扫: max_requests 截断 ----
    tmp3 = os.path.join(tempfile.gettempdir(), "cok-test-map3-%d.json" % os.getpid())
    st = cok_map.scan_area(ScanClient(), 0, 0, 100, 100, step=12, path=tmp3,
                           max_requests=3)
    ok &= check("max_requests 生效", st["requests"] == 3, str(st["requests"]))
    doc3 = cok_map.load_index(tmp3)
    ok &= check("截断时 meta 标记 partial", doc3["meta"].get("partial") is True,
                json.dumps(doc3["meta"], ensure_ascii=False))
    ok &= check("截断时记录续扫位置",
                "next_x" in doc3["meta"] and "next_y" in doc3["meta"],
                json.dumps(doc3["meta"], ensure_ascii=False))
    ok &= check("截断后也不标记 scanning", doc3["meta"].get("scanning") is False,
                json.dumps(doc3["meta"], ensure_ascii=False))
    os.remove(tmp3)

    # ---- 9) 坐标校正: 越界点剔除 + 众数观测 ----
    # 服务端偶尔把覆盖区外的地块混进同一个 points 数组, 那些点的 index
    # 会落到地图别处 —— 不剔除就会把玩家坐标写坏(实测 91% 的坐标是这样坏的)。
    idx9 = {"players": {}, "meta": {}}
    batch9 = [
        {"uid": "u1", "name": "A", "index": 1118663, "x": 531, "y": 931, "level": 30},
        {"uid": "u2", "name": "B", "index": 1176504, "x": 724, "y": 979, "level": 30},
    ]
    cok_map.merge_players(idx9, batch9, center=(531, 931))
    ok &= check("覆盖区外的点被剔除",
                "u2" not in idx9["players"], str(list(idx9["players"])))
    ok &= check("覆盖区内的点保留",
                "u1" in idx9["players"], str(list(idx9["players"])))
    ok &= check("被剔除的点数被记录",
                idx9["meta"].get("dropped_out_of_range") == 1,
                json.dumps(idx9["meta"], ensure_ascii=False))

    # 众数投票: 同一 uid 被多次看到, 取出现次数最多的那个 index
    idx9b = {"players": {}, "meta": {}}
    good = {"uid": "u1", "name": "A", "index": 1118663, "x": 531, "y": 931, "level": 30}
    bad = {"uid": "u1", "name": "A", "index": 1176504, "x": 724, "y": 979, "level": 30}
    cok_map.merge_players(idx9b, [good, good, bad])
    ok &= check("坐标取众数观测而不是最后一次",
                cok_map.resolve_point(idx9b["players"]["u1"]) == 1118663,
                str(cok_map.resolve_point(idx9b["players"]["u1"])))

    # load_index 时自动把坐标校正成众数
    tmp9 = os.path.join(tempfile.gettempdir(), "cok-test-map9-%d.json" % os.getpid())
    with open(tmp9, "w", encoding="utf-8") as f:
        json.dump({"players": {"u1": {"name": "A", "index": 1176504, "x": 724,
                                     "y": 979, "seen_at": 1,
                                     "obs": {"1176504": 1, "1118663": 3}}},
                   "meta": {}}, f, ensure_ascii=False)
    doc9 = cok_map.load_index(tmp9)
    r9 = doc9["players"]["u1"]
    ok &= check("load_index 时坐标被校正成众数",
                r9.get("index") == 1118663 and r9.get("x") == 531
                and r9.get("y") == 931, json.dumps(r9, ensure_ascii=False))
    os.remove(tmp9)

    print("\n%s" % ("全部通过" if ok else "存在失败项"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
