#!/usr/bin/env python3
"""体力药水：道具实例 uuid 的获取/缓存 + 使用 —— 2026-11-10。

## 协议结论(真机实测, 见 COK-CN1-analysis/protocol/COK-游戏服协议实测报告.md)

* 体力药水道具 id: **200380**(10 体力) / **200381**(50 体力) / **200382**(100 体力)
  (客户端 `data_config.auto_kill_monster.k1="200380;200381"`, 道具表 `para` 字段=体力值)
* 使用命令 = **`item.use`**, 参数 **`{uuid: <道具实例 uuid>, num: <数量>}`**
  - `uuid` 是**道具实例 id**(32 位 hex), 不是模板 id —— 传 "200381" → E000000
  - `num` **必须编码成 SFS INT**(`TypedInt(n, SFS_INT)`), 传普通 int → E000000
  - uuid 不存在 → **E100166**(没有该道具); 数量不够 → **E100165**(道具数量不足)
* 服务端也有**自动打怪队列**(`autoQueue.save {saveItems}`)能自己喝药, 但
  `autoQueue.status {status:1}` 需要「自动打怪周卡」(客户端 k2=766437),
  没周卡一律 E000000 —— 所以控制台走**自己发 `item.use`** 这条路。

## 道具实例 uuid 从哪来: **`login.init`**

实测(2026-11-10 真机): 背包**有**只读接口 —— 命令 **`login.init`**。

    login.init  ->  {"qqq": <keyId>, "rlQW45Y": "<30 万 hex>"}
    rlQW45Y     ->  XOR(会话密钥) -> zlib -> SFS 对象(133 个顶层键, 95 万字节)
    其中 items = [{"itemId":"200381","count":40,"uuid":"94e0...","para1":"107","para2":"50"}, ...]

* `items` 就是**玩家背包**: 每条带 `itemId` / `count` / `uuid`(道具实例 id) /
  `para2`(体力值) / `useDate` / `vanishTime`
* 同一个实例的 `uuid` 在 count 用完之前**稳定**, 药水是堆叠的(一个实例 count=N)
* ⚠️ 这个响应是**「裸 zlib 流」**: 服务端不发帧长度, 帧头 3 字节就是 zlib 流的开头。
  客户端 `_recv_frame` 必须解到 zlib 流自然结束, 否则后面所有帧错位。
  (见 cok_client._read_zlib_stream)
* ⚠️ 服务端会丢弃**新连接的首条业务请求**, 所以 login.init 第一次常常超时,
  重发一次才有响应。

⇒ 本模块的 uuid 来源(按可靠度排序):

1. **拉背包**(`fetch_bag`): 发 `login.init`, 从 `items` 里取出体力药水的 uuid —— 最直接
2. **被动学习**: 任何响应/推送里出现 `{itemId|id: "200381", uuid: "<32hex>"}`
   配对时自动记下(领奖、获得道具、掉落都会带上)
3. **手动填写**: 账号配置里写 `staminaItems: {"200381": "<uuid>"}`

学习到的 uuid 会**持久化**到 `accounts/<uid>.items.json`。
"""
import json
import os
import re
import time

HERE = os.path.dirname(os.path.abspath(__file__))

#: 体力药水道具 id → 恢复的体力点数(客户端道具表 goods.<id>.para)
STAMINA_ITEMS = {
    "200380": 10,
    "200381": 50,
    "200382": 100,
}

#: 道具实例 uuid 的形态: 32 位小写 hex
UUID_RE = re.compile(r"^[0-9a-f]{32}$")

#: 响应里可能出现的"道具 id"字段名
_ITEM_KEYS = ("itemId", "itemid", "item_id", "propId", "toolId", "goodsId", "id")


def _accounts_dir():
    d = os.path.join(HERE, "accounts")
    try:
        os.makedirs(d, exist_ok=True)
    except OSError:
        pass
    return d


def items_path(uid):
    """某个账号的道具实例缓存文件。"""
    return os.path.join(_accounts_dir(), "%s.items.json" % str(uid))


def load_items(uid):
    """读缓存: {itemId: {"uuid": str, "count": int, "at": ts}}"""
    try:
        with open(items_path(uid), encoding="utf-8") as f:
            data = json.load(f)
        items = data.get("items") if isinstance(data, dict) else None
        return items if isinstance(items, dict) else {}
    except (OSError, ValueError):
        return {}


def save_items(uid, items):
    """写缓存。返回是否写成功。"""
    if not items:
        return False
    path = items_path(uid)
    tmp = path + ".tmp"
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump({"updated": int(time.time()), "items": items},
                      f, ensure_ascii=False, indent=1)
        os.replace(tmp, path)
        return True
    except OSError:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        return False


def _is_uuid(v):
    return isinstance(v, str) and bool(UUID_RE.match(v))


def learn_items(payload, into=None):
    """从一个响应/推送里学出 {itemId: uuid} 配对。

    识别的形态:
      * {"itemId": "200381", "uuid": "<32hex>"}
      * {"id": "200381", "uuid": "<32hex>"}          (reward.value 这种)
      * {"itemId": "200381", "itemObj": {"uuid": ...}}
    返回 (新学到的 dict, 是否新增)。
    """
    found = {}

    def walk(node, inherited=None, depth=0):
        """inherited = 上层已经确定的道具 id。

        服务端常见的形态是 **id 和 uuid 不在同一层**:
            {"itemId": "200380", "itemObj": {"uuid": "<32hex>"}}
            {"id": "200381", "reward": {"uuid": "<32hex>"}}
        所以往下走的时候要把 id 传下去。
        """
        if depth > 8:
            return
        if isinstance(node, dict):
            iid = inherited
            for k in _ITEM_KEYS:
                v = node.get(k)
                if isinstance(v, str) and v.strip():
                    iid = v.strip()
                    break
                if isinstance(v, int) and not isinstance(v, bool):
                    iid = str(v)
                    break
            for k, v in node.items():
                if isinstance(v, str) and _is_uuid(v):
                    if iid:
                        found[iid] = v
                    break
            for v in node.values():
                walk(v, iid, depth + 1)
        elif isinstance(node, list):
            for v in node[:200]:
                walk(v, inherited, depth + 1)

    walk(payload)
    if into is None:
        into = {}
    added = False
    for iid, u in found.items():
        if into.get(iid) != u:
            into[iid] = u
            added = True
    return found, added


def merge_learned(uid, payload):
    """学习 + 落盘。返回新学到的 {itemId: uuid}。"""
    items = load_items(uid)
    found, added = learn_items(payload, items)
    if added:
        for iid in found:
            items[iid] = {"uuid": found[iid], "at": int(time.time())}
        save_items(uid, items)
    return found if added else {}


def pick_stamina(items):
    """从缓存里挑一个体力药水。优先挑回体力多的(200382 > 200381 > 200380)。

    返回 (itemId, uuid) 或 (None, None)。
    """
    best = (None, None)
    for iid in sorted(STAMINA_ITEMS, key=lambda x: -STAMINA_ITEMS[x]):
        ent = items.get(iid)
        if isinstance(ent, str):          # 简写: 直接给 uuid
            if _is_uuid(ent):
                return iid, ent
            continue
        if not isinstance(ent, dict):
            continue
        u = ent.get("uuid")
        if not _is_uuid(u):
            continue
        cnt = ent.get("count")
        if isinstance(cnt, int) and cnt <= 0:
            continue
        return iid, u
    return best


def use_stamina_item(client, uuid, num=1):
    """用掉 num 瓶体力药水。

    命令 `item.use {uuid, num: TypedInt(n, SFS_INT)}`。
    返回 (ok: bool, info: dict) —— info 里带 errorCode / 新体力(如果服务端回了)。
    """
    from cok_sfs import TypedInt, SFS_INT   # 局部导入, 避免循环依赖
    try:
        r = client.call("item.use",
                        {"uuid": str(uuid), "num": TypedInt(int(num), SFS_INT)},
                        retries=1)
    except Exception as e:  # noqa: BLE001
        return False, {"error": str(e)[:160]}
    p = r.get("__params__") or {}
    if p.get("errorCode"):
        return False, {"errorCode": p.get("errorCode"), "error": _err_text(p.get("errorCode"))}
    return True, {"params": p}


def _err_text(code):
    return {
        "E100165": "道具数量不足",
        "E100166": "没有该道具(实例 uuid 已失效)",
        "E100047": "体力不足",
        "E000000": "参数错误(服务端不接受这个道具实例)",
    }.get(str(code), str(code))


def scan_potions(items):
    """从背包 items 数组里挑出体力药水。

    返回 {itemId: {"uuid": str, "count": int}} —— 只保留 count>0 的实例。
    """
    out = {}
    if not isinstance(items, list):
        return out
    for it in items:
        if not isinstance(it, dict):
            continue
        iid = str(it.get("itemId") or "").strip()
        if iid not in STAMINA_ITEMS:
            continue
        u = it.get("uuid")
        if not _is_uuid(u):
            continue
        try:
            cnt = int(it.get("count") or 0)
        except (TypeError, ValueError):
            cnt = 0
        if cnt <= 0:
            continue
        out[iid] = {"uuid": u, "count": cnt}
    return out


def fetch_bag(client, uid=None):
    """拉玩家背包, 学出体力药水的道具实例 uuid。

    命令 `login.init`(服务端会丢弃新连接的首条业务请求, 所以 retries>=1)。
    返回 (ok, info):
      ok=False -> info={"error": "..."}
      ok=True  -> info={"potions": {itemId: {"uuid","count"}}, "total": 背包道具总数,
                        "search": {"max": 每日找怪次数上限, "used": 已用次数}}
    """
    try:
        r = client.call("login.init", {}, retries=1)
    except Exception as e:  # noqa: BLE001
        return False, {"error": "拉背包失败: %s" % str(e)[:160]}
    p = r.get("__params__") or {}
    items = p.get("items")
    if not isinstance(items, list):
        return False, {"error": "login.init 没有返回 items 字段(服务端版本不同?)"}
    potions = scan_potions(items)
    if uid:
        cache = load_items(uid)
        for iid, ent in potions.items():
            ent = dict(ent)
            ent["at"] = int(time.time())
            cache[iid] = ent
        if potions:
            save_items(uid, cache)
    # 顺带把「今日找怪次数」读出来(2026-11-11 实测: world.maxSearchCount /
    # world.resSearchCount)—— 自动打怪每派一队消耗一次, 用完服务端只回空坐标。
    search = {}
    world = p.get("world")
    if isinstance(world, dict):
        try:
            mx = int(world.get("maxSearchCount") or 0)
            us = int(world.get("resSearchCount") or 0)
        except (TypeError, ValueError):
            mx = us = 0
        if mx > 0:
            search = {"max": mx, "used": us, "left": max(0, mx - us)}
    return True, {"potions": potions, "total": len(items), "search": search}


def claim_stamina_reward(client, uid=None):
    """主动领一份含体力药水的可领奖励, 借机让服务端把道具实例(含 uuid)推下来。

    返回 (ok, info): info = {"itemId", "rewardId", "uuid"?, "note"}
    """
    try:
        r = client.call("resource.client.reward.getmulti", {}, retries=1)
    except Exception as e:  # noqa: BLE001
        return False, {"error": "读取可领奖励失败: %s" % str(e)[:120]}
    p = r.get("__params__") or {}
    rewards = p.get("rewardsObj") or {}
    hit = None
    for rid, info in rewards.items():
        if not isinstance(info, dict):
            continue
        rl = info.get("reward_list") or {}
        items = str(rl.get("item") or "").split("|")
        nums = str(rl.get("num") or "").split("|")
        for i, iid in enumerate(items):
            if iid in STAMINA_ITEMS:
                n = nums[i] if i < len(nums) else "?"
                hit = (rid, iid, n)
                break
        if hit:
            break
    if not hit:
        return False, {"error": "没有含体力药水的可领奖励(可先在游戏里领掉/攒一瓶)"}
    rid, iid, n = hit
    try:
        r2 = client.call("resource.client.reward.get", {"rewardId": str(rid)}, retries=1)
    except Exception as e:  # noqa: BLE001
        return False, {"error": "领取失败: %s" % str(e)[:120]}
    p2 = r2.get("__params__") or {}
    if p2.get("errorCode"):
        return False, {"errorCode": p2.get("errorCode"),
                       "error": "领取失败: %s" % p2.get("errorCode")}
    found, _ = learn_items(p2)
    uuid = found.get(iid)
    if uid and uuid:
        items = load_items(uid)
        items[iid] = {"uuid": uuid, "count": int(n or 1), "at": int(time.time())}
        save_items(uid, items)
    return True, {"itemId": iid, "rewardId": rid, "num": n, "uuid": uuid,
                  "note": "已领取 %s x%s" % (iid, n)}


def status(uid):
    """给 UI 看的简短状态。"""
    items = load_items(uid)
    iid, uuid = pick_stamina(items)
    return {
        "known": bool(uuid),
        "itemId": iid,
        "uuid": uuid or "",
        "gain": STAMINA_ITEMS.get(iid or "", 0),
        "items": {k: (v.get("uuid") if isinstance(v, dict) else v)
                  for k, v in items.items() if k in STAMINA_ITEMS},
        "counts": {k: (v.get("count") if isinstance(v, dict) else None)
                   for k, v in items.items() if k in STAMINA_ITEMS},
    }
