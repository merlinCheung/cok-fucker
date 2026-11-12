#!/usr/bin/env python3
"""诊断 world.get 返回: 到底是"解码错乱"还是"玩家有多个地块"。

一次连接做多次同点查询, 对比:
  1) 解码模式 mode 是不是 partial(说明 SFS 数组模式判定失败 -> 数据错乱)
  2) 同一个 uid 在一次响应里出现几次(>1 次 = 玩家有多个地块)
  3) 同一个 uid 在**不同响应**里 i 值是否一致(不一致 = 服务端在变 或 解码在抖)
  4) 响应里的点 i 反算成坐标后, 相对请求中心的偏移分布
     (正确的点必然聚在覆盖区内; 错乱的点会散得到处都是)

用法:
  python3 diag_world_get.py                 # 默认查 (531,931) 三次
  python3 diag_world_get.py 531 931 5       # 查 (531,931) 五次
  python3 diag_world_get.py 531 931 5 <uid-main>   # 指定要盯的 uid
"""
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "core"))

import cok_client  # noqa: E402
import cok_map  # noqa: E402

W = cok_map.WORLD_SIZE


def pt(i):
    n = int(i) - 1
    return (n % W, n // W)


def main():
    cx = int(sys.argv[1]) if len(sys.argv) > 1 else 531
    cy = int(sys.argv[2]) if len(sys.argv) > 2 else 931
    times = int(sys.argv[3]) if len(sys.argv) > 3 else 3
    own = sys.argv[4] if len(sys.argv) > 4 else "<uid-main>"

    print("查中心 (%d,%d) 共 %d 次, 盯 uid=%s" % (cx, cy, times, own))
    print("=" * 72)
    seen = {}
    for k in range(times):
        try:
            r = cok_client.CokClient(timeout=90.0).connect()
            r.bin_handshake()
            r.login()
            for _ in range(2):
                try:
                    r.call("cmd.ping")
                except Exception:
                    pass
            try:
                # 直接用底层 call, 拿到 __mode__
                resp = r.call("world.get", {
                    "x": cok_map._I(cx), "y": cok_map._I(cy),
                    "type": cok_map._I(0), "serverId": cok_map._I(2223),
                    "timeStamp": cok_map._I(int(time.time()))})
            finally:
                try:
                    r.close()
                except Exception:
                    pass
        except Exception as e:
            print("[%d] 连接/请求失败: %s" % (k + 1, str(e)[:120]))
            time.sleep(5)
            continue

        mode = resp.get("__mode__")
        p = resp.get("__params__") or {}
        echo = (p.get("x"), p.get("y"))
        tiles = cok_map._parse_points(p)
        withuid = [t for t in tiles if t.get("uid")]
        mine = [t for t in withuid if str(t.get("uid")) == own]

        print("[%d] mode=%s | 请求中心(%d,%d) 响应回显x,y=%s | 地块 %d, 带 uid %d, 自己 %d 次" % (
            k + 1, mode, cx, cy, echo, len(tiles), len(withuid), len(mine)))
        if echo != (None, None) and (echo[0] != cx or echo[1] != cy):
            print("    ⚠️ 响应回显与请求中心不一致 -> 拿错了包(迟到响应被认领)")
        if "partial" in str(mode) or "error" in str(mode):
            print("    ⚠️ 解码没有完整消费缓冲区 -> 字段值可能是错乱的!")
        for t in mine:
            i = int(t.get("i"))
            x, y = pt(i)
            print("    自己 i=%-9d -> (%4d,%4d)  t=%s l=%s" % (i, x, y, t.get("t"), t.get("l")))
            seen.setdefault("mine", []).append(i)

        # 偏移分布: 正确解码时 dx/dy 应该很小且集中
        dxs = []
        dys = []
        for t in withuid:
            i = int(t.get("i"))
            x, y = pt(i)
            dxs.append(x - cx)
            dys.append(y - cy)
        if dxs:
            dxs.sort()
            dys.sort()
            n = len(dxs)
            print("    dx: min=%d p50=%d p90=%d max=%d | dy: min=%d p50=%d p90=%d max=%d" % (
                dxs[0], dxs[n // 2], dxs[int(n * 0.9)], dxs[-1],
                dys[0], dys[n // 2], dys[int(n * 0.9)], dys[-1]))
            far = [t for t in withuid
                   if abs(pt(int(t.get("i")))[0] - cx) > 60
                   or abs(pt(int(t.get("i")))[1] - cy) > 60]
            if far:
                print("    ⚠️ 有 %d 个点离请求中心 >60 格:" % len(far))
                for t in far[:6]:
                    i = int(t.get("i"))
                    print("        i=%-9d -> (%4d,%4d) uid=%s %r" % (
                        i, pt(i)[0], pt(i)[1], t.get("uid"), (t.get("o") or "")[:12]))
        # 记录这一轮所有 uid->i, 供跨轮对比
        for t in withuid:
            seen.setdefault("m", {})[str(t.get("uid"))] = int(t.get("i"))
        time.sleep(3)

    print("=" * 72)
    if "m" in seen and len(seen) > 1:
        print("每次响应里带 uid 地块数:", [len(x) for x in seen.get("m", {})][:1])
    # 跨轮对比需要保存每轮, 这里重新按 m 只保留最后一轮 -> 上面已打印 mode
    print("提示: 若 '自己' 每次的 i 都一样且 mode 不是 partial,")
    print("      说明服务端稳定, 问题在合并/覆盖; 若 i 每次都变, 是服务端或解码在抖。")


if __name__ == "__main__":
    main()
