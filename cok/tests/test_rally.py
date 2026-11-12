#!/usr/bin/env python3
"""巨型狮鹫 + 联盟集结 的单元测试(不连游戏服, 零消耗)。

覆盖(每条都对应一个真服实测结论或一个踩过的坑):
  1. 集结时长档位: 从 login.dataconfig 的 dataConfig.world_rally 读 k1..k4,
     读不到才用兜底值(不同区服配置不同, 不能写死)
  2. world.get 的 points 解析: 字典形式和 **JSON 字符串**形式都要认
  3. 地块识别: 只认 t=15(ActBossTile) 且 t1 是巨型狮鹫 id 的
  4. index -> (x, y) 换算
  5. 采样网格: 全图覆盖 + 轮转游标推进
  6. 扫描: 断线后能靠 on_reconnect 重建连接继续(实测服务端连打约 70 次就断)
  7. 集结出征参数: type=4(MethodRally)、wtIndex 是 INT、soldiers 是 INT、
     marchKey 必须按 type=4 算(不是打野怪的 type=6)
  8. 错误码翻译(115212/115218/115219/113228)
  9. 集结列表: 时间戳是**毫秒**, waitTime-createTime = 服务端实际执行的档位时长
 10. 归属判定: attackId / member.uid / member.userId 三种都认
 11. busy 标记必须按 **targetId**(目标地块), 不能按 monsterId ——
     同一个等级有几十只 boss, 用 monsterId 会把整片都标成"已有集结"
 12. 注册表落盘/读回
"""

import json
import os
import shutil
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "core"))
sys.path.insert(0, os.path.join(HERE, "..", "tools"))

# 注册表落盘到临时目录, 别污染真实数据
_TMP = tempfile.mkdtemp(prefix="cok-rally-test-")
os.environ["COK_DATA_DIR"] = _TMP

import cok_rally  # noqa: E402
from cok_sfs import SFS_INT  # noqa: E402

FAILED = []
PASSED = []

#: 用**真实时间戳**, 否则会被 _prune_known 当成过期条目清掉
NOW = time.time()


def check(name, cond, detail=""):
    if cond:
        PASSED.append(name)
    else:
        FAILED.append("%s %s" % (name, detail))
        print("  [FAIL] %s %s" % (name, detail))


def boss_tile(index, monster="902113", hp=720000, maxhp=720000):
    n = index - 1
    return {"t": 15, "i": index, "t1": monster, "mchp": hp, "mmhp": maxhp,
            "st": 1793573758, "rt": 1793660158, "x": n % 1201, "y": n // 1201}


class FakeClient(object):
    """假客户端: 按命令返回预设结果, 并记录收到的参数。"""

    def __init__(self, tiles=None, dataconfig=None, rally_list=None):
        self.tiles = tiles if tiles is not None else []
        self.dataconfig = dataconfig
        self.rally_list = rally_list or []
        self.calls = []
        self.world_get = []
        self.fail_after = None       # 第 N 次 world.get 开始抛异常
        self.n_get = 0

    def call(self, cmd, params=None, retries=1):
        self.calls.append((cmd, params))
        if cmd == "login.dataconfig":
            if self.dataconfig is None:
                raise AssertionError("未预期的命令 %s" % cmd)
            return {"__params__": self.dataconfig}
        if cmd == "world.get":
            self.n_get += 1
            self.world_get.append(params)
            if self.fail_after is not None and self.n_get > self.fail_after:
                raise IOError("连接被服务端关闭（已收 0/3 字节）")
            return {"__params__": {"points": [
                json.dumps(boss_tile(1000 + i)) for i in range(len(self.tiles))]}}
        if cmd == "alliance.team.ls":
            return {"__params__": {"list": self.rally_list, "helplist": []}}
        if cmd == "world.march":
            return {"__params__": {"allianceBattleTeam": {
                "teamId": "team-1", "monsterId": "902113",
                "member": [{"uid": "1", "totalTroops": 200}]}}}
        raise AssertionError("未预期的命令 %s" % cmd)


# ---------------------------------------------------------------- 1. 档位

def test_slots():
    print("[1] 集结时长档位")
    dc = {"dataConfig": {"world_rally": {"k1": "5", "k2": "10", "k3": "30", "k4": "60"}}}
    cl = FakeClient(dataconfig=dc)
    got = cok_rally.read_rally_slots(cl, use_cache=False)
    check("读到 4 档", [g["minutes"] for g in got] == [5, 10, 30, 60], str(got))
    check("slot 从 1 开始", [g["slot"] for g in got] == [1, 2, 3, 4], str(got))

    # dataConfig 可能是**字符串**形式(实测有这���)
    cl2 = FakeClient(dataconfig={"dataConfig": json.dumps(
        {"world_rally": {"k1": "7", "k2": "15", "k3": "45", "k4": "90"}})})
    got2 = cok_rally.read_rally_slots(cl2, use_cache=False)
    check("dataConfig 是字符串也能解析",
          [g["minutes"] for g in got2] == [7, 15, 45, 90], str(got2))

    # 读不到 -> 用兜底值, 但档位数还是 4
    cl3 = FakeClient(dataconfig={"dataConfig": {}})
    got3 = cok_rally.read_rally_slots(cl3, use_cache=False)
    check("读不到时用兜底值",
          [g["minutes"] for g in got3] == list(cok_rally.RALLY_FALLBACK_MINUTES),
          str(got3))


# ---------------------------------------------------------------- 2/3. 地块解析

def test_tiles():
    print("[2/3] world.get 地块解析")
    p = {"points": [
        boss_tile(500),                                    # 字典形式
        json.dumps(boss_tile(600, "902114")),              # JSON 字符串形式
        json.dumps([boss_tile(700, "902115")]),            # 字符串数组
        {"t": 3, "i": 800, "t1": "100100"},                 # 普通资源点 -> 忽略
        {"t": 15, "i": 900, "t1": "999999"},                # 不是狮鹫 -> 忽略
    ]}
    tiles = cok_rally._parse_tiles(p)
    check("解析出全部 5 个地块(过滤在 _merge_tiles 做)", len(tiles) == 5, str(len(tiles)))
    idxs = sorted(t["i"] for t in tiles)
    check("index 正确", idxs == [500, 600, 700, 800, 900], str(idxs))

    cok_rally._KNOWN.clear()
    cok_rally._merge_tiles(tiles, NOW)
    check("注册表只收 3 只", len(cok_rally._KNOWN) == 3, str(len(cok_rally._KNOWN)))
    t500 = cok_rally._KNOWN[500]
    check("等级映射 902113->12", t500["level"] == 12, str(t500))
    check("坐标换算 index->(x,y)", (t500["x"], t500["y"]) == (499 % 1201, 499 // 1201),
          str((t500["x"], t500["y"])))
    # 同一 index 再来一次只更新不重复计数
    n = cok_rally._merge_tiles([boss_tile(500)], NOW + 100)
    check("重复地块不重复计数", n == 0 and len(cok_rally._KNOWN) == 3, str(n))


# ---------------------------------------------------------------- 4/5. 网格

def test_grid():
    print("[4/5] 全图采样网格")
    centers = cok_rally.map_centers()
    check("网格非空", len(centers) > 0, str(len(centers)))
    xs = sorted({c[0] for c in centers})
    ys = sorted({c[1] for c in centers})
    check("覆盖整个地图宽", min(xs) <= 12 and max(xs) >= 1201 - cok_rally.SCAN_STRIDE,
          str((min(xs), max(xs))))
    check("覆盖整个地图高", min(ys) <= 13 and max(ys) >= 1201 - cok_rally.SCAN_STRIDE,
          str((min(ys), max(ys))))
    check("网格点不重复", len(set(centers)) == len(centers), str(len(centers)))


# ---------------------------------------------------------------- 6. 扫描 + 重连

def test_scan():
    print("[6] 扫描与断线重连")
    cok_rally._KNOWN.clear()
    cok_rally._CURSOR = 0
    cl = FakeClient(tiles=[boss_tile(1000 + i) for i in range(3)])
    r = cok_rally.scan_bosses(cl, slice_size=2, save=False)
    check("扫了 2 格", r["scanned"] == 2, str(r))
    check("游标前进了", r["cursor"] == 2, str(r))
    check("扫到 3 只", len(r["bosses"]) == 3, str(len(r["bosses"])))

    # 再扫一次 -> 游标继续往后, 注册表累积
    r2 = cok_rally.scan_bosses(cl, slice_size=2, save=False)
    check("游标继续推进", r2["cursor"] == 4, str(r2))

    # 断线: 第 1 次 world.get 就失败 -> 靠 on_reconnect 重建
    cok_rally._KNOWN.clear()
    cl2 = FakeClient(tiles=[boss_tile(2000)])
    cl2.fail_after = 0
    new_cl = FakeClient(tiles=[boss_tile(2000)])

    def reconnect(old):
        return new_cl

    r3 = cok_rally.scan_bosses(cl2, slice_size=3, on_reconnect=reconnect, save=False)
    check("断线后重连续扫", r3["scanned"] >= 1, str(r3))
    check("重连后拿到数据", len(r3["bosses"]) >= 1, str(r3))

    # 没有重连回调时: 断线就停, 不能无限抛
    cok_rally._KNOWN.clear()
    cl3 = FakeClient(tiles=[boss_tile(3000)])
    cl3.fail_after = 0
    r4 = cok_rally.scan_bosses(cl3, slice_size=3, on_reconnect=None, save=False)
    check("无重连回调时安全停下", r4["scanned"] == 0, str(r4))


# ---------------------------------------------------------------- 7/8. 出征

def test_march():
    print("[7/8] 集结出征参数与错误码")
    cok_rally._KNOWN.clear()
    cl = FakeClient()
    r = cok_rally.rally_march(cl, 12345, "107110", 100, 200, 300, slot=3)
    check("出征成功", r["ok"] is True, str(r))
    cmd, params = cl.calls[-1]
    check("命令是 world.march", cmd == "world.march", cmd)
    check("type=4 (MethodRally)", int(params["type"]) == 4, str(params.get("type")))
    check("type 是 INT 类型", getattr(params["type"], "sfs_type", None) == SFS_INT,
          str(getattr(params["type"], "sfs_type", None)))
    check("wtIndex=3", int(params["wtIndex"]) == 3, str(params.get("wtIndex")))
    check("wtIndex 是 INT 类型",
          getattr(params["wtIndex"], "sfs_type", None) == SFS_INT,
          str(getattr(params["wtIndex"], "sfs_type", None)))
    check("point 是 INT 类型",
          getattr(params["point"], "sfs_type", None) == SFS_INT,
          str(getattr(params["point"], "sfs_type", None)))
    n = int(list(params["soldiers"].values())[0])
    check("soldiers 数量对", n == 300, str(params["soldiers"]))
    check("soldiers 数量是 INT",
          getattr(list(params["soldiers"].values())[0], "sfs_type", None) == SFS_INT,
          str(params["soldiers"]))

    # marchKey 必须按 type=4 算 —— 和打野怪(type=6)的 key 不同
    from cok_hunt import march_key
    army = {"107110": (100, 200, 300)}
    check("marchKey 按 type=4 计算",
          params["marchKey"] == march_key(12345, army, march_type=4),
          str(params.get("marchKey")))
    check("marchKey 不等于 type=6 的",
          params["marchKey"] != march_key(12345, army, march_type=6),
          str(params.get("marchKey")))

    # 档位越界要被夹到 1..4
    cok_rally.rally_march(cl, 1, "107110", 100, 200, 10, slot=99)
    check("档位越界被夹住", int(cl.calls[-1][1]["wtIndex"]) == 4,
          str(cl.calls[-1][1].get("wtIndex")))

    # 错误码翻译
    for code, kw in (("115212", "同一个目标"), ("115218", "联盟"),
                     ("115219", "出发"), ("113228", "次数")):
        note = cok_rally._rally_error_note(code)
        check("错误码 %s 有中文说明" % code, kw in note, note)


# ---------------------------------------------------------------- 9/10/11. 列表

def test_rally_list():
    print("[9/10/11] 集结列表解析")
    ct = 1793583136236
    lst = [{
        "teamId": "team-mine", "monsterId": "902113", "targetType": 15,
        "targetId": 4067, "attackId": "<uid-main>", "attackName": "me",
        "createTime": ct, "waitTime": ct + 600000, "marchTime": ct + 660000,
        "totalTroops": 200, "member": [{"uid": "<uid-main>"}],
    }, {
        "teamId": "team-other", "monsterId": "902113", "targetType": 15,
        "targetId": 9999, "attackId": "999", "attackName": "other",
        "createTime": ct, "waitTime": ct + 300000,
        "member": [{"userId": "888"}],
    }, {
        "teamId": "team-city", "targetType": 111, "targetId": 396704,
        "createTime": ct, "waitTime": ct + 120000, "member": [],
    }]
    cl = FakeClient(rally_list=lst)
    r = cok_rally.read_alliance_rallies(cl)
    check("读到 3 条", len(r["list"]) == 3, str(len(r["list"])))
    a = r["list"][0]
    check("毫秒时间戳被换算成秒", abs(a["createTime"] - ct / 1000.0) < 0.01, str(a["createTime"]))
    check("wait_minutes = 10 分钟(档位2)", a["wait_minutes"] == 10.0, str(a["wait_minutes"]))
    check("targetId 保留", a["targetId"] == 4067, str(a["targetId"]))

    # 归属判定: attackId / member.uid / member.userId
    mine = cok_rally.my_rallies(cl, game_uid="<uid-main>")
    check("按 attackId 认出自己的集结", len(mine) == 1 and mine[0]["teamId"] == "team-mine",
          str(len(mine)))
    mine2 = cok_rally.my_rallies(cl, game_uid="888")
    check("按 member.userId 认出自己的集结", len(mine2) == 1, str(len(mine2)))

    # busy 只算 boss 目标(targetType=15), 且按 targetId
    busy = cok_rally.busy_targets(cl)
    check("busy 只含 boss 目标", busy == {4067, 9999}, str(busy))

    # snapshot 的 busy 标记: 同一 monsterId 的另一只 boss **不能**被标 busy
    cok_rally._KNOWN.clear()
    cok_rally._merge_tiles([boss_tile(4067), boss_tile(7777)], NOW)
    snap = cok_rally.snapshot(cl, save=False, game_uid="<uid-main>")
    b = {x["index"]: x for x in snap["bosses"]}
    check("有集结的那只标 busy", b[4067]["busy"] is True, str(b.get(4067)))
    check("同等级的另一只不标 busy", b[7777]["busy"] is False, str(b.get(7777)))
    check("我的集结被认出来", len(snap["my_rallies"]) == 1, str(snap["my_rallies"]))


# ---------------------------------------------------------------- 12. 注册表

def test_registry():
    print("[12] 注册表落盘 / 读回")
    cok_rally._KNOWN.clear()
    cok_rally._merge_tiles([boss_tile(4242), boss_tile(4343)], NOW)
    check("落盘成功", cok_rally.save_registry() is True)
    check("文件存在", os.path.exists(cok_rally.REGISTRY_FILE), cok_rally.REGISTRY_FILE)
    cok_rally._KNOWN.clear()
    cok_rally.load_registry()
    check("读回 2 只", len(cok_rally._KNOWN) == 2, str(len(cok_rally._KNOWN)))
    check("读回后 index 还在", 4242 in cok_rally._KNOWN, str(sorted(cok_rally._KNOWN)[:5]))
    check("读回后等级还在", cok_rally._KNOWN[4242]["level"] == 12,
          str(cok_rally._KNOWN.get(4242)))

    # 过期的不读回来
    data = json.load(open(cok_rally.REGISTRY_FILE))
    for k in data["tiles"]:
        data["tiles"][k]["seen_at"] = 0.0
    with open(cok_rally.REGISTRY_FILE, "w") as f:
        json.dump(data, f)
    cok_rally._KNOWN.clear()
    cok_rally.load_registry()
    check("过期的条目被丢掉", len(cok_rally._KNOWN) == 0, str(len(cok_rally._KNOWN)))


def main():
    try:
        test_slots()
        test_tiles()
        test_grid()
        test_scan()
        test_march()
        test_rally_list()
        test_registry()
    finally:
        shutil.rmtree(_TMP, ignore_errors=True)
    print("\n通过 %d 项, 失败 %d 项" % (len(PASSED), len(FAILED)))
    if FAILED:
        for f in FAILED:
            print("  FAIL:", f)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
