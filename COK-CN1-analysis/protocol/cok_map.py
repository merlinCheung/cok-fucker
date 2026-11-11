#!/usr/bin/env python3
"""COK 世界地图扫描器: 批量抓取全服玩家坐标, 建本地索引。

⚠️ 关键协议(2026-10-25 实测, 抓客户端流量得到)
------------------------------------------------
游戏客户端滑动世界地图时, 用的是 **`world.get`**:

    world.get { x: INT, y: INT, type: INT, serverId: INT, timeStamp: INT }

→ 服务端返回**以 (x,y) 为中心的一整片区域**(约 24×24 格)的全部地块,
  其中**带玩家名和坐标**。

返回结构(实测):
    {
      timeStamp, x, y, section, serverId, moveCityTime,
      collectLine: [ 行军/采集线 ],
      m:          [ 地图对象 ],
      points:     [ "<JSON 字符串数组>" ]     <- 地块数组(是**字符串**, 要二次 json.loads)
    }

points 里每个地块:
    { i: 坐标index, uid: 玩家uid, o: 玩家名字, t: 地块类型, l: 等级, ... }
    地块类型(实测): 1=玩家城, 3=资源点, 9=?, 1003=?

**类型必须显式指定 INT**: Python 的 int 会被编码成 BYTE(0x02),
服务端要 INT(0x04) —— 传错类型会回 E000000。

成本实测:
    * 每次请求 **0.17 秒**, 返回 25~100 个地块
    * **完全不消耗道具/资源/体力**
    * 全图 1201×1201 用步长 12 覆盖 -> 约 100×100 = 10000 次请求 ≈ 30 分钟
      (对比逐格 world.get.detail: 144 万次 ≈ 57 小时, 快 100 倍以上)
"""

import json
import os
import time

from cok_sfs import TypedInt, SFS_INT

#: 世界尺寸(客户端 WorldController.lua: _tile_count_x/_tile_count_y = 1201)
WORLD_SIZE = 1201

#: world.get 单次覆盖半径(实测相对中心 x -12~+11, y -13~+11)
COVER_RADIUS = 12

#: 步进步长: 必须 <= 覆盖直径, 否则会漏格子
STEP = 12

_HERE = os.path.dirname(os.path.abspath(__file__))

#: 数据目录。多账号时每个账号一个子目录(坐标索引/扫描历史/pid 各存各的)。
#: 由环境变量 COK_DATA_DIR 驱动, 子进程(scan_world.py)靠继承 env 自动对齐;
#: 不设时就是脚本所在目录, 行为与多账号改造前完全一致。
DATA_DIR = os.environ.get("COK_DATA_DIR") or _HERE

#: 默认索引文件
DEFAULT_INDEX = os.path.join(DATA_DIR, "map-index.json")

#: 扫描历史文件(每次扫描一行记录, 按 id 去重更新)
HISTORY_FILE = os.path.join(DATA_DIR, "scan-history.json")

#: 扫描进程 pid 文件(网页据此判断"扫描还在跑", 网页重启也不丢)
PID_FILE = os.path.join(DATA_DIR, "scan.pid")


def set_data_dir(path):
    """把数据目录指到 path, 并同步更新三个派生路径与 COK_DATA_DIR 环境变量。

    环境变量也一并设置, 这样之后 Popen 出去的 scan_world.py 子进程会继承到
    同一目录, 无需额外传参。path 为空则回退到脚本所在目录(单账号行为)。
    """
    global DATA_DIR, DEFAULT_INDEX, HISTORY_FILE, PID_FILE
    DATA_DIR = path or _HERE
    try:
        os.makedirs(DATA_DIR, exist_ok=True)
    except OSError:
        pass
    DEFAULT_INDEX = os.path.join(DATA_DIR, "map-index.json")
    HISTORY_FILE = os.path.join(DATA_DIR, "scan-history.json")
    PID_FILE = os.path.join(DATA_DIR, "scan.pid")
    if path:
        os.environ["COK_DATA_DIR"] = DATA_DIR
    else:
        os.environ.pop("COK_DATA_DIR", None)
    return DATA_DIR


def load_history(path=None):
    """读扫描历史。返回 {runs: [...]} —— 最近的在前。"""
    p = path or HISTORY_FILE
    try:
        with open(p, encoding="utf-8") as f:
            doc = json.load(f)
    except (OSError, ValueError):
        return {"runs": []}
    runs = doc.get("runs")
    if not isinstance(runs, list):
        runs = []
    runs.sort(key=lambda r: r.get("started_at") or 0, reverse=True)
    return {"runs": runs}


def record_scan(entry, path=None):
    """写一条扫描历史。同 id 的记录**更新**而不是追加(一次扫描会多次写)。"""
    p = path or HISTORY_FILE
    doc = load_history(p)
    runs = doc["runs"]
    rid = str(entry.get("id") or "")
    for i, r in enumerate(runs):
        if rid and str(r.get("id")) == rid:
            merged = dict(r)
            merged.update({k: v for k, v in entry.items() if v is not None})
            runs[i] = merged
            break
    else:
        runs.insert(0, dict(entry))
    doc["runs"] = runs[:60]          # 只留最近 60 次
    try:
        tmp = p + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(doc, f, ensure_ascii=False, indent=1)
        os.replace(tmp, p)
    except OSError:
        return False
    return True


def read_scan_pid(path=None):
    """读扫描进程 pid(没有就返回 None)。"""
    p = path or PID_FILE
    try:
        with open(p, encoding="utf-8") as f:
            return int((f.read() or "0").strip() or 0) or None
    except (OSError, ValueError):
        return None


def write_scan_pid(pid, path=None):
    p = path or PID_FILE
    try:
        with open(p, "w", encoding="utf-8") as f:
            f.write(str(int(pid)))
    except OSError:
        return False
    return True


def clear_scan_pid(path=None):
    p = path or PID_FILE
    try:
        os.remove(p)
    except OSError:
        return False
    return True


def _I(v):
    """强制 INT 类型(服务端对类型敏感)。"""
    return TypedInt(int(v), SFS_INT)


def index_to_point(index, w=WORLD_SIZE):
    """地图点位 index -> (x, y)。与 cok_hunt.point_index 严格互逆。"""
    try:
        i = int(index)
    except (TypeError, ValueError):
        return None
    if i <= 0:
        return None
    n = i - 1
    return (n % w, n // w)


def point_to_index(x, y, w=WORLD_SIZE):
    """(x, y) -> 地图点位 index。"""
    return int(x) + 1 + int(w * int(y))


def _parse_points(params):
    """把 world.get 的 points 字段拆成地块列表。

    points 是一个**字符串数组**, 每个元素是 JSON 文本(可能是分段的大 JSON)。
    """
    out = []
    raw = params.get("points")
    if raw is None:
        return out
    items = raw if isinstance(raw, list) else [raw]
    for it in items:
        if isinstance(it, dict):
            out.append(it)
            continue
        if not isinstance(it, str):
            continue
        try:
            got = json.loads(it)
        except (ValueError, TypeError):
            continue
        if isinstance(got, list):
            out.extend(x for x in got if isinstance(x, dict))
        elif isinstance(got, dict):
            out.append(got)
    return out


def fetch_area(client, x, y, server_id=2223, timestamp=None, attempts=4):
    """拉取以 (x, y) 为中心的一整片区域。

    返回 {ok, errorCode, error, tiles:[地块], players:[玩家], elapsed,
          mismatched: 响应与请求对不上的次数}

    ⚠️ **响应校验**(2026-10-25 加): 服务端会在响应里回显请求的 x/y。
    如果拿到的响应里 x/y 不是我们请求的中心, 说明**拿错了包** ——
    一个迟到的旧响应被当成了本次的响应(命令名相同, 无法区分)。
    这种情况下必须丢掉它、清空 socket、重发。
    不校验的话, 一次错位就会把**别的中心**的坐标写进索引
    (实测 91% 的玩家坐标是这样被写坏的)。
    """
    t0 = time.time()
    mismatched = 0
    p = None
    for attempt in range(max(1, attempts)):
        # ⚠️ **每次重试都要用新的 timeStamp**: 服务端会丢弃**每条连接的第一条**
        # world.get; 重试时如果还带原来的 timeStamp, 服务端会当成重复请求继续丢,
        # 于是每次重试都失败(实测会一直卡到超时)。
        ts = int(time.time()) if timestamp is None else int(timestamp)
        try:
            # ⚠️ **retries=0**: 不能让 call 内部自动重发。
            # call 超时后会自动重发同一条命令, 而**迟到的旧响应命令名相同**,
            # 会被重发的那次当成自己的响应认领 —— 于是这一次拿到的是**别的
            # 中心**的数据, 而真正的新响应滞留在缓冲区, 被下一个请求读走,
            # **错位就此开始并持续传染**(实测 91% 的玩家坐标是这样被写坏的)。
            # 自己控制重试, 每次重试前先 drain 干净。
            r = client.call("world.get", {
                "x": _I(x), "y": _I(y), "type": _I(0),
                "serverId": _I(server_id), "timeStamp": _I(ts),
            }, retries=0)
        except Exception as e:  # noqa: BLE001
            # 超时/断连: 连接状态已经可疑, 可能有迟到响应躺在缓冲区里
            try:
                client.drain()
            except Exception:  # noqa: BLE001
                pass
            if attempt + 1 < max(1, attempts):
                time.sleep(0.5)
                continue
            return {"ok": False, "error": str(e)[:160], "tiles": [], "players": [],
                    "elapsed": time.time() - t0, "mismatched": mismatched}
        p = r.get("__params__") or {}
        if p.get("errorCode"):
            return {"ok": False, "errorCode": p.get("errorCode"),
                    "error": "服务端拒绝(%s)" % p.get("errorCode"),
                    "tiles": [], "players": [], "elapsed": time.time() - t0,
                    "mismatched": mismatched}
        rx, ry = p.get("x"), p.get("y")
        if rx is not None and ry is not None:
            try:
                same = (int(rx) == int(x) and int(ry) == int(y))
            except (TypeError, ValueError):
                same = False
            if not same:
                # 拿错了包: 丢掉它, 清空 socket(迟到的正确响应也一并丢掉),
                # 然后重发 —— 保证索引里写进去的一定是本次中心的数据。
                mismatched += 1
                try:
                    client.drain()
                except Exception:  # noqa: BLE001
                    pass
                time.sleep(0.3)
                continue
        break
    tiles = _parse_points(p)
    players = []
    for t in tiles:
        if not t.get("uid"):
            continue
        pt = index_to_point(t.get("i"))
        if not pt:
            continue
        players.append({
            "uid": str(t.get("uid")),
            "name": t.get("o") or "",
            "index": int(t.get("i")),
            "x": pt[0],
            "y": pt[1],
            "level": t.get("l"),
            "type": t.get("t"),
        })
    return {"ok": True, "errorCode": None, "tiles": tiles, "players": players,
            "elapsed": time.time() - t0, "raw_keys": list(p.keys()),
            "mismatched": mismatched}


def load_index(path=None):
    """读本地索引。返回 {players: {uid: {...}}, meta: {...}}

    读出来时会把每个玩家的坐标**校正成众数观测点**(见 resolve_point),
    所以不管索引是刚写的还是老的, 消费方拿到的都是"最可信"的那个坐标。

    path=None 时用**当前**的 DEFAULT_INDEX(set_data_dir 之后能生效) ——
    不能把 DEFAULT_INDEX 写进默认参数, 那样会在定义时就绑死旧目录。
    """
    if path is None:
        path = DEFAULT_INDEX
    try:
        with open(path, encoding="utf-8") as f:
            doc = json.load(f)
    except (OSError, ValueError):
        return {"players": {}, "meta": {}}
    doc.setdefault("players", {})
    doc.setdefault("meta", {})
    # 校正: 众数观测优先于"最后一次覆盖"
    for rec in doc["players"].values():
        if not isinstance(rec, dict):
            continue
        idx = resolve_point(rec)
        if not idx or rec.get("index") == idx:
            continue
        pt = index_to_point(idx)
        if pt:
            rec["index"] = idx
            rec["x"], rec["y"] = pt
    return doc


def save_index(doc, path=None):
    if path is None:
        path = DEFAULT_INDEX
    # ⚠️ 临时文件名要**带 pid**: 多个进程同时写同一个索引时, 共用
    # "<path>.tmp" 会互相抢文件 —— os.replace 报 FileNotFoundError,
    # 扫描器因此崩掉、而且旧索引会把新索引覆盖回去。
    tmp = "%s.tmp.%d" % (path, os.getpid())
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=1)
    os.replace(tmp, path)
    return path


def _cover_radius(players, center):
    """估计这次响应的覆盖半径(格)。

    正确的点必然聚在请求中心附近; 偶尔被混进来的越界点会散在地图各处。
    估计方法: 只用**偏移最小的一半**点来锚定"密集簇"(正确点),
    再乘 3 倍当容差 —— 这样少数越界点不会把半径拉爆(直接用中位数会被带偏)。
    下限取实测覆盖区(x ±12, y ±13)再留一点余量。
    """
    dxs = sorted(abs((p.get("x") or 0) - center[0]) for p in players)
    dys = sorted(abs((p.get("y") or 0) - center[1]) for p in players)

    def radius(vals, lo):
        if not vals:
            return lo
        k = max(1, len(vals) // 2)      # 最小的一半 = 密集簇
        core = vals[:k]
        med = core[len(core) // 2]
        return max(lo, int(med * 3) + 2)

    return radius(dxs, 13), radius(dys, 14)


def resolve_point(rec):
    """取该玩家**众数**观测点, 而不是最后一次覆盖的值。

    同一个玩家会被多个重叠的覆盖区看到好几次。服务端偶尔把覆盖区外的
    地块混进同一个 points 数组, 那些点的 index 会落到地图别处 —— 如果只
    保留"最后一次覆盖", 一次错乱就会把正确坐标顶掉(实测 91% 的玩家坐标
    是这样被写坏的)。用众数投票可以把少数错乱观测投掉。
    """
    obs = (rec or {}).get("obs") or {}
    if obs:
        best = max(obs.items(), key=lambda kv: (kv[1], -int(kv[0])))[0]
        try:
            return int(best)
        except (TypeError, ValueError):
            pass
    return (rec or {}).get("index")


def merge_players(index, players, center=None):
    """把一批玩家并进索引, 返回写入条数。

    center: (cx, cy) —— 这批数据对应的请求中心。给了就会**剔除越界点**:
    那些点不是本次覆盖区的真实地块, 写进索引就是错的坐标。
    """
    store = index.setdefault("players", {})
    added = 0
    if center is not None and players:
        rx, ry = _cover_radius(players, center)
        good = []
        dropped = 0
        for p in players:
            if (abs((p.get("x") or 0) - center[0]) > rx
                    or abs((p.get("y") or 0) - center[1]) > ry):
                dropped += 1
                continue
            good.append(p)
        if dropped:
            meta = index.setdefault("meta", {})
            meta["dropped_out_of_range"] = int(
                meta.get("dropped_out_of_range") or 0) + dropped
        players = good
    for p in players:
        uid = p.get("uid")
        if not uid:
            continue
        old = store.get(uid)
        if old is None:
            added += 1          # 新出现的 uid 数
        obs = dict((old or {}).get("obs") or {})
        key = str(p.get("index"))
        obs[key] = obs.get(key, 0) + 1
        store[uid] = {
            "name": p.get("name") or "",
            "index": p.get("index"),
            "x": p.get("x"), "y": p.get("y"),
            "level": p.get("level"),
            "seen_at": int(time.time()),
            "obs": obs,
        }
    return added


def scan_area(client, x0, y0, x1, y1, server_id=2223, step=STEP,
              index=None, path=None, progress=None,
              max_requests=None, own_uid=None, delay=0.0, resume_y=None,
              reconnect=None, reconnect_every=200):
    """扫描一个矩形区域, 把玩家写进本地索引。

    x0/y0/x1/y1 是**格子坐标**范围(闭区间)。返回统计 dict。
    own_uid: 自己的 uid —— 扫描时顺带记下自己的坐标(存在 index.meta.self_point),
             这样"扫描附近"永远以自己为中心, 不需要写死坐标。
    resume_y: 断点续扫时**第一列**的起始 y(第一列从这个 y 开始, 后续列仍从 y0 开始)。
              ⚠️ 早先用 y0=next_y 把**整个区域**的 y 起点都抬高了 ——
              那样会漏掉 x>断点列 且 y<断点y 的整片区域, 而那部分还没扫过。
    reconnect: 可选回调, 每 reconnect_every 个中心调一次(重建连接)。
              长连接偶尔会进入"既不返回也不断连"的半死状态, 表现为扫描
              长时间卡在同一个中心; 定期重连能把影响限制在少量请求内。
    """
    if path is None:
        path = DEFAULT_INDEX
    index = index if index is not None else load_index(path)
    stats = {"requests": 0, "tiles": 0, "players": 0, "new": 0,
             "errors": 0, "elapsed": 0.0}
    t0 = time.time()
    nx = (x1 - x0) // step + 1 if x1 >= x0 else 0
    ny = (y1 - y0) // step + 1 if y1 >= y0 else 0
    total = nx * ny
    stopped = False        # 因 max_requests 提前收工
    interrupted = True     # 异常中断(断点仍可用)
    next_x = next_y = None
    try:
        for cx in range(x0, x1 + 1, step):
            # 断点续扫: 只有**第一列**从断点 y 开始, 后面每一列都从 y0 重新开始
            start_y = y0
            if cx == x0 and resume_y is not None:
                start_y = max(y0, int(resume_y))
            for cy in range(start_y, y1 + 1, step):
                if (reconnect and reconnect_every
                        and stats["requests"] % reconnect_every == 0
                        and stats["requests"] > 0):
                    try:
                        client = reconnect() or client
                    except Exception:  # noqa: BLE001
                        pass
                if delay:
                    # ⚠️ 限速: 服务端在请求过快时会**降速**(每个请求要等好几秒)甚至
                    # 半死连接。匀速发反而更快跑完。
                    time.sleep(delay)
                if max_requests and stats["requests"] >= max_requests:
                    next_x, next_y = cx, cy
                    stopped = True
                    break
                res = fetch_area(client, cx, cy, server_id=server_id)
                stats["requests"] += 1
                if res.get("mismatched"):
                    stats["mismatched"] = stats.get("mismatched", 0) + res["mismatched"]
                if not res.get("ok"):
                    stats["errors"] += 1
                    continue
                stats["tiles"] += len(res.get("tiles") or [])
                stats["players"] += len(res.get("players") or [])
                stats["new"] += merge_players(index, res.get("players") or [],
                                               center=(cx, cy))
                # 顺带记下自己的坐标 —— 用**众数观测**, 不用"最后一次看到"的值
                # (后者会被混入的越界点顶掉)
                if own_uid:
                    rec = (index.get("players") or {}).get(str(own_uid))
                    pt = index_to_point(resolve_point(rec)) if rec else None
                    if pt:
                        index.setdefault("meta", {})["self_point"] = {
                            "x": pt[0], "y": pt[1],
                            "at": int(time.time()),
                        }
                if progress:
                    progress(cx, cy, stats)
            if stopped:
                break
        else:
            interrupted = False
    finally:
        # ⚠️ 收尾状态必须在这里写 —— 正常走完 / 提前收工 / 异常中断三条路径
        # 都要把"还在扫描吗"说清楚, 否则页面会一直显示"扫描中"。
        stats["elapsed"] = time.time() - t0
        meta = dict(index.get("meta") or {})
        meta.update({"updated_at": int(time.time()),
                     "partial": bool(interrupted or stopped),
                     "scanning": False,
                     "requests_done": stats["requests"],
                     "requests_total": total,
                     "mismatched_responses": int(stats.get("mismatched") or 0),
                     "errors": int(stats.get("errors") or 0),
                     "dropped_out_of_range": int(
                         (index.get("meta") or {}).get("dropped_out_of_range") or 0),
                     "total_players": len(index.get("players") or {})})
        if next_x is not None:
            meta["next_x"] = next_x
            meta["next_y"] = next_y
        index["meta"] = meta
        save_index(index, path)
    return stats


def scan_world(client, server_id=2223, step=STEP, index=None,
               path=None, progress=None, max_requests=None,
               size=WORLD_SIZE):
    """扫描整张世界地图(1201×1201)。"""
    if path is None:
        path = DEFAULT_INDEX
    return scan_area(client, 0, 0, size - 1, size - 1,
                     server_id=server_id, step=step, index=index,
                     path=path, progress=progress,
                     max_requests=max_requests)


def find_players(index, keyword, limit=50):
    """在本地索引里按名字/uid 模糊查找。"""
    kw = (keyword or "").strip().lower()
    if not kw:
        return []
    out = []
    for uid, p in (index.get("players") or {}).items():
        name = (p.get("name") or "").lower()
        if kw in name or kw in str(uid):
            out.append(dict(p, uid=uid))
    # 精确匹配优先, 其次按名字长度
    out.sort(key=lambda p: (0 if (p.get("name") or "").lower() == kw else 1,
                            len(p.get("name") or "")))
    return out[:limit]
