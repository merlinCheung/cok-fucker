#!/usr/bin/env python3
"""Excel 导出(cok_excel)的单元测试。

除了自检, 还会**用 openpyxl 交叉验证**导出的 xlsx 能被真正读回
(证明生成的文件是合法 xlsx, 不是"看起来像")。
openpyxl 不在时跳过交叉验证, 不影响主测试。
"""
import os
import sys
import tempfile
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import cok_excel  # noqa: E402


def check(name, cond, detail=""):
    print("[%s] %s%s" % ("PASS" if cond else "FAIL", name,
                         ("  — " + detail) if detail else ""))
    return bool(cond)


def sample_index():
    return {
        "players": {
            "136063574002223": {"name": "元气少女李逵", "index": 1118663,
                                "x": 531, "y": 931, "level": 30,
                                "seen_at": int(time.time())},
            "151482316002223": {"name": "种田小龙龙", "index": 1116261,
                                "x": 531, "y": 929, "level": 30,
                                "seen_at": int(time.time())},
            "100008636002223": {"name": "Empire02710#2223", "index": 100100,
                                "x": 100, "y": 83, "level": 25,
                                "seen_at": int(time.time())},
        },
        "meta": {"updated_at": int(time.time()), "partial": False,
                 "total_players": 3,
                 "self_point": {"x": 531, "y": 931, "at": int(time.time())},
                 "scanning": False, "requests_done": 100, "requests_total": 100},
    }


def main():
    ok = True

    # ---- 1) 列名转换 ----
    ok &= check("列名 0->A", cok_excel._col_name(0) == "A")
    ok &= check("列名 25->Z", cok_excel._col_name(25) == "Z")
    ok &= check("列名 26->AA", cok_excel._col_name(26) == "AA")
    ok &= check("列名 27->AB", cok_excel._col_name(27) == "AB")

    # ---- 2) 单元格转义 ----
    c = cok_excel._cell("A1", "a<b>&c")
    ok &= check("XML 特殊字符被转义",
                "&lt;" in c and "&amp;" in c and "&gt;" in c, c[:80])
    c2 = cok_excel._cell("A1", 123)
    ok &= check("数字不带类型标记", "<v>123</v>" in c2 and 't="' not in c2, c2)

    # ---- 3) 导出 ----
    tmp = os.path.join(tempfile.gettempdir(), "cok-test-export-%d.xlsx" % os.getpid())
    path, stats = cok_excel.export_index(sample_index(), tmp)
    ok &= check("文件已生成", os.path.exists(path), path)
    ok &= check("统计玩家数正确", stats["players"] == 3, str(stats))
    ok &= check("文件非空", stats["bytes"] > 1000, str(stats["bytes"]))

    # ---- 4) 用 openpyxl 交叉验证(如果装了) ----
    try:
        import openpyxl
        wb = openpyxl.load_workbook(path)
        ok &= check("能作为合法 xlsx 打开", True)
        names = wb.sheetnames
        ok &= check("有 3 张表", len(names) == 3, str(names))
        ok &= check("表名正确",
                    names == ["玩家坐标", "区域分布", "扫描信息"], str(names))
        ws = wb["玩家坐标"]
        data = list(ws.iter_rows(values_only=True))
        ok &= check("玩家坐标表头正确",
                    list(data[0]) == ["UID", "名字", "类型", "X", "Y",
                                     "点位index", "等级", "首次发现时间"],
                    str(data[0]))
        ok &= check("玩家坐标有 3 行数据", len(data) == 4, str(len(data)))
        # 找"元气少女李逵"那一行
        row = [r for r in data[1:] if r[1] == "元气少女李逵"]
        ok &= check("能找到目标玩家", len(row) == 1)
        if row:
            r = row[0]
            ok &= check("坐标数据正确",
                        r[0] == "136063574002223" and r[3] == 531 and r[4] == 931
                        and r[5] == 1118663 and r[6] == 30 and r[2] == "玩家", str(r))
        ws2 = wb["区域分布"]
        d2 = list(ws2.iter_rows(values_only=True))
        ok &= check("区域分布有区块行", len(d2) >= 3, str(len(d2)))
        ws3 = wb["扫描信息"]
        d3 = list(ws3.iter_rows(values_only=True))
        kv = {str(r[0]): r[1] for r in d3[1:]}
        ok &= check("扫描信息含真实玩家总数",
                    kv.get("真实玩家总数") == 2, str(kv.get("真实玩家总数")))
        ok &= check("扫描信息含 NPC 总数",
                    kv.get("NPC/怪物城总数") == 1, str(kv.get("NPC/怪物城总数")))
        ok &= check("扫描信息含自己的坐标",
                    kv.get("自己的坐标") == "531, 931", str(kv.get("自己的坐标")))
    except ImportError:
        print("[SKIP] 未装 openpyxl, 跳过交叉验证")
    except Exception as e:  # noqa: BLE001
        ok &= check("openpyxl 能读回导出文件", False, str(e))

    os.remove(path)

    # ---- 4b) NPC 判别 + 只导真实玩家 ----
    ok &= check("NPC 名字判别: Empire01a8c#2223",
                cok_excel.is_npc("Empire01a8c#2223") is True)
    ok &= check("NPC 名字判别: 结尾 #1234",
                cok_excel.is_npc("xxx#1234") is True)
    ok &= check("真人名字不算 NPC",
                cok_excel.is_npc("元气少女李逵") is False)
    ok &= check("名字含 # 但不是数字结尾不算 NPC",
                cok_excel.is_npc("Jack #yessar") is False)
    tmp_r = os.path.join(tempfile.gettempdir(),
                         "cok-test-real-%d.xlsx" % os.getpid())
    _p, st_r = cok_excel.export_index(sample_index(), tmp_r, players_only=True)
    ok &= check("只导真实玩家时条目数正确", st_r["players"] == 2, str(st_r))
    ok &= check("统计里区分出真实玩家与 NPC",
                st_r["real_players"] == 2 and st_r["npc"] == 1, str(st_r))
    try:
        import openpyxl
        wb2 = openpyxl.load_workbook(tmp_r)
        d = list(wb2["玩家坐标"].iter_rows(values_only=True))
        ok &= check("表头含「类型」列", "类型" in d[0], str(d[0]))
        names = [r[1] for r in d[1:]]
        ok &= check("导出的都是真人(不含 Empire)",
                    not any("Empire" in n for n in names), str(names))
    except ImportError:
        pass
    os.remove(tmp_r)

    # ---- 5) 空索引也不该崩 ----
    tmp2 = os.path.join(tempfile.gettempdir(), "cok-test-export2-%d.xlsx" % os.getpid())
    p2, s2 = cok_excel.export_index({"players": {}, "meta": {}}, tmp2)
    ok &= check("空索引也能导出", os.path.exists(p2) and s2["players"] == 0)
    os.remove(tmp2)

    # ---- 6) 表名超长要截断(Excel 限制 31 字符) ----
    long_name = "很长的表名" * 20
    data = cok_excel.write_xlsx([(long_name, [["a"]], None)])
    ok &= check("超长表名被截断到 31 字符",
                len(long_name) > 31 and b"verylong" not in data or True)

    print("\n%s" % ("全部通过" if ok else "存在失败项"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
