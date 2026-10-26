#!/usr/bin/env python3
"""把地图索引导出成 Excel(命令行版, 不用开网页)。

用法:
  python3 export_excel.py                      # 导出到 cok-players.xlsx
  python3 export_excel.py --out players.xlsx   # 换文件名
  python3 export_excel.py --index map-index.json
  python3 export_excel.py --csv                # 顺便导一份 CSV(Excel 友好)
  python3 export_excel.py --top 20             # 顺便打印最热闹的 20 个区域
"""
import argparse
import csv
import io
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import cok_excel  # noqa: E402
import cok_map  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--index", default=cok_map.DEFAULT_INDEX)
    ap.add_argument("--out", default=os.path.join(HERE, "cok-players.xlsx"))
    ap.add_argument("--csv", action="store_true", help="同时导出一份 CSV")
    ap.add_argument("--top", type=int, default=0, help="打印最热闹的 N 个区域")
    ap.add_argument("--real-only", action="store_true",
                    help="只导真实玩家(排除 Empire…#2223 这类 NPC)")
    args = ap.parse_args()

    idx = cok_map.load_index(args.index)
    players = idx.get("players") or {}
    if not players:
        print("[!] 索引是空的(%s) —— 先跑 scan_world.py" % args.index)
        return 1
    meta = idx.get("meta") or {}

    path, stats = cok_excel.export_index(idx, args.out,
                                          players_only=args.real_only)
    print("[*] 已导出: %s" % path)
    print("    条目 %d 条(真实玩家 %d / NPC %d) · 区域 %d 个 · %.1f KB" % (
        stats["players"], stats["real_players"], stats["npc"],
        stats["blocks"], stats["bytes"] / 1024.0))
    if meta.get("updated_at"):
        print("    索引更新于 %s" % time.strftime(
            "%Y-%m-%d %H:%M:%S", time.localtime(meta["updated_at"])))
    if meta.get("scanning"):
        print("    ⚠️ 扫描仍在进行(部分数据)")
    upd = meta.get("updated_at")
    if upd:
        age_h = (time.time() - upd) / 3600.0
        if age_h > 6:
            print("    ⚠️ 数据已是 %.1f 小时前的快照 —— 服务端会定时重排地图," % age_h)
            print("       若游戏内坐标与表里对不上, 请重扫: python3 scan_world.py")
        else:
            print("    (数据为 %.1f 小时前的快照)" % age_h)
    sp = meta.get("self_point") or {}
    if sp:
        print("    自己(扫描时刻): X %s, Y %s" % (sp.get("x"), sp.get("y")))

    if args.csv:
        csv_path = os.path.splitext(args.out)[0] + ".csv"
        with open(csv_path, "w", encoding="utf-8-sig", newline="") as f:
            w = csv.writer(f)
            w.writerow(["UID", "名字", "类型", "X", "Y", "点位index",
                        "等级", "首次发现时间"])
            rows = []
            for uid, p in players.items():
                if args.real_only and cok_excel.is_npc(p.get("name")):
                    continue
                rows.append([
                    uid, p.get("name") or "",
                    "NPC" if cok_excel.is_npc(p.get("name")) else "玩家",
                    p.get("x"), p.get("y"),
                    p.get("index"), p.get("level"),
                    time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(p["seen_at"]))
                    if p.get("seen_at") else "",
                ])
            rows.sort(key=lambda r: (r[1] == "", r[1]))
            w.writerows(rows)
        print("[*] 已导出 CSV: %s" % csv_path)

    if args.top:
        blocks = {}
        for p in players.values():
            if p.get("x") is None:
                continue
            key = (p["x"] // cok_excel.AREA_BLOCK, p["y"] // cok_excel.AREA_BLOCK)
            blocks.setdefault(key, []).append(p)
        top = sorted(blocks.items(), key=lambda kv: -len(kv[1]))[:args.top]
        print("\n=== 最热闹的 %d 个区域(每格 %d×%d) ===" % (
            args.top, cok_excel.AREA_BLOCK, cok_excel.AREA_BLOCK))
        for (bx, by), ps in top:
            print("  区块(%4d,%4d) X %4d-%4d  Y %4d-%4d  %4d 人" % (
                bx, by,
                bx * cok_excel.AREA_BLOCK, bx * cok_excel.AREA_BLOCK + cok_excel.AREA_BLOCK - 1,
                by * cok_excel.AREA_BLOCK, by * cok_excel.AREA_BLOCK + cok_excel.AREA_BLOCK - 1,
                len(ps)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
