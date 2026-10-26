#!/usr/bin/env python3
"""把地图索引导出成 Excel(.xlsx)。

⚠️ **零新依赖**: 只用 Python 标准库手写 xlsx(xlsx 就是 zip + XML)。
   环境里若装了 openpyxl/xlsxwriter 也**不使用** —— 保持"复制即跑"的特性。

xlsx 结构:
    [Content_Types].xml          内容类型声明
    _rels/.rels                  包级关系
    xl/workbook.xml              工作簿(表名列表)
    xl/_rels/workbook.xml.rels   工作簿关系
    xl/styles.xml                样式(表头加粗 + 列宽)
    xl/worksheets/sheetN.xml     各工作表

导出三张表:
    1. 玩家坐标 —— 全部玩家的 uid / 名字 / X / Y / index / 等级 / 发现时间
    2. 区域分布 —— 按 50×50 格聚类, 看玩家集中在哪些区域
    3. 扫描信息 —— 索引元数据(时间/总量/自己的位置等)
"""
import io
import os
import re
import time
import zipfile
from xml.sax.saxutils import escape

#: 区域聚类粒度(格)
AREA_BLOCK = 50

#: NPC 名字判别: 形如 "Empire01a8c#2223" —— 以 #<数字> 结尾的都是 NPC/怪物城
_NPC_RE = re.compile(r"#\d+$")


def is_npc(name):
    """这个名字是不是 NPC/怪物城(不是真人玩家)。"""
    return bool(_NPC_RE.search(str(name or "")))


# ---------------- xlsx 底层 ----------------

def _col_name(n):
    """0 -> A, 25 -> Z, 26 -> AA"""
    s = ""
    n += 1
    while n:
        n, r = divmod(n - 1, 26)
        s = chr(65 + r) + s
    return s


def _cell(ref, value, style=None):
    attrs = ' r="%s"' % ref
    if style:
        attrs += ' s="%d"' % style
    if value is None or value == "":
        return '<c%s/>' % attrs
    if isinstance(value, bool):
        return '<c%s t="b"><v>%d</v></c>' % (attrs, 1 if value else 0)
    if isinstance(value, (int, float)):
        return '<c%s><v>%s</v></c>' % (attrs, value)
    # inline string: 避免再维护一个 sharedStrings 表
    return '<c%s t="inlineStr"><is><t xml:space="preserve">%s</t></is></c>' % (
        attrs, escape(str(value)))


def _sheet_xml(rows, col_widths=None, header_style=1):
    """rows: 二维列表; 第一行按表头处理。col_widths: 各列宽度。"""
    out = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
           '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">']
    if col_widths:
        out.append("<cols>")
        for i, w in enumerate(col_widths):
            out.append('<col min="%d" max="%d" width="%s" customWidth="1"/>'
                       % (i + 1, i + 1, w))
        out.append("</cols>")
    out.append("<sheetData>")
    for r, row in enumerate(rows, 1):
        out.append('<row r="%d">' % r)
        style = header_style if r == 1 else 0
        for c, val in enumerate(row):
            out.append(_cell("%s%d" % (_col_name(c), r), val, style))
        out.append("</row>")
    out.append("</sheetData>")
    out.append("</worksheet>")
    return "".join(out)


#: 样式表: 0=普通, 1=表头(加粗+底色)
_STYLES = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
<fonts count="2">
<font><sz val="11"/><name val="Calibri"/></font>
<font><b/><sz val="11"/><color rgb="FFFFFFFF"/><name val="Calibri"/></font>
</fonts>
<fills count="3">
<fill><patternFill patternType="none"/></fill>
<fill><patternFill patternType="gray125"/></fill>
<fill><patternFill patternType="solid"><fgColor rgb="FF2F6FEB"/><bgColor indexed="64"/></patternFill></fill>
</fills>
<borders count="1"><border><left/><right/><top/><bottom/><diagonal/></border></borders>
<cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>
<cellXfs count="2">
<xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/>
<xf numFmtId="0" fontId="1" fillId="2" borderId="0" xfId="0" applyFont="1" applyFill="1"/>
</cellXfs>
<cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles>
</styleSheet>"""


def write_xlsx(sheets, path=None):
    """sheets: [(表名, rows, col_widths), ...] -> 写 xlsx 文件, 返回 path。"""
    if not sheets:
        raise ValueError("没有可导出的表")
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        # [Content_Types].xml
        ct = ['<?xml version="1.0" encoding="UTF-8"?>',
              '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">',
              '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>',
              '<Default Extension="xml" ContentType="application/xml"/>',
              '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>',
              '<Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>']
        for i in range(len(sheets)):
            ct.append('<Override PartName="/xl/worksheets/sheet%d.xml" '
                      'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>' % (i + 1))
        ct.append("</Types>")
        z.writestr("[Content_Types].xml", "".join(ct))

        # _rels/.rels
        z.writestr("_rels/.rels",
                   '<?xml version="1.0" encoding="UTF-8"?>'
                   '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                   '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" '
                   'Target="xl/workbook.xml"/></Relationships>')

        # xl/workbook.xml
        wb = ['<?xml version="1.0" encoding="UTF-8"?>',
              '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
              'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets>']
        for i, (name, _rows, _w) in enumerate(sheets):
            wb.append('<sheet name="%s" sheetId="%d" r:id="rId%d"/>'
                      % (escape(str(name)[:31]), i + 1, i + 1))
        wb.append("</sheets></workbook>")
        z.writestr("xl/workbook.xml", "".join(wb))

        # xl/_rels/workbook.xml.rels
        rels = ['<?xml version="1.0" encoding="UTF-8"?>',
                '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">']
        for i in range(len(sheets)):
            rels.append('<Relationship Id="rId%d" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" '
                        'Target="worksheets/sheet%d.xml"/>' % (i + 1, i + 1))
        rels.append('<Relationship Id="rId%d" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" '
                    'Target="styles.xml"/>' % (len(sheets) + 1))
        rels.append("</Relationships>")
        z.writestr("xl/_rels/workbook.xml.rels", "".join(rels))

        z.writestr("xl/styles.xml", _STYLES)

        for i, (_name, rows, widths) in enumerate(sheets):
            z.writestr("xl/worksheets/sheet%d.xml" % (i + 1),
                       _sheet_xml(rows, widths))

    data = buf.getvalue()
    if path:
        tmp = path + ".tmp"
        with open(tmp, "wb") as f:
            f.write(data)
        os.replace(tmp, path)
        return path
    return data


# ---------------- 业务导出 ----------------

def export_index(index, path=None, players_only=False):
    """把地图索引导出成 xlsx。返回 (path_or_bytes, 统计dict)。

    players_only=True -> 只导真实玩家(排除 NPC/怪物城)。
    """
    all_players = index.get("players") or {}
    meta = index.get("meta") or {}

    if players_only:
        players = {u: p for u, p in all_players.items()
                   if not is_npc(p.get("name"))}
    else:
        players = all_players
    npc_count = sum(1 for p in all_players.values() if is_npc(p.get("name")))

    # --- 表1: 玩家坐标 ---
    # ⚠️ 表头和数据要分开处理: 数据按名字排序, **表头不能参与排序**
    data1 = []
    for uid, p in players.items():
        data1.append([
            uid,
            p.get("name") or "",
            "NPC" if is_npc(p.get("name")) else "玩家",
            p.get("x"), p.get("y"), p.get("index"), p.get("level"),
            time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(p["seen_at"]))
            if p.get("seen_at") else "",
        ])
    # 按名字排序(空名在后), 方便人工查
    data1.sort(key=lambda r: (r[1] == "", r[1]))
    rows1 = [["UID", "名字", "类型", "X", "Y", "点位index", "等级", "首次发现时间"]]
    rows1.extend(data1)

    # --- 表2: 区域分布 ---
    blocks = {}
    for p in players.values():
        if p.get("x") is None or p.get("y") is None:
            continue
        key = (p["x"] // AREA_BLOCK, p["y"] // AREA_BLOCK)
        blocks.setdefault(key, []).append(p)
    rows2 = [["区块X", "区块Y", "X范围", "Y范围", "总数", "其中玩家",
              "最高等级玩家", "最高等级"]]
    for (bx, by), ps in sorted(blocks.items(), key=lambda kv: -len(kv[1])):
        real_ps = [p for p in ps if not is_npc(p.get("name"))]
        best = max(real_ps or ps, key=lambda p: (p.get("level") or 0))
        rows2.append([
            bx * AREA_BLOCK, by * AREA_BLOCK,
            "%d-%d" % (bx * AREA_BLOCK, bx * AREA_BLOCK + AREA_BLOCK - 1),
            "%d-%d" % (by * AREA_BLOCK, by * AREA_BLOCK + AREA_BLOCK - 1),
            len(ps), len(real_ps),
            best.get("name") or "", best.get("level") or 0,
        ])

    # --- 表3: 扫描信息 ---
    sp = meta.get("self_point") or {}
    real_total = sum(1 for p in all_players.values() if not is_npc(p.get("name")))
    upd = meta.get("updated_at")
    age_h = (time.time() - upd) / 3600.0 if upd else None
    rows3 = [
        ["项目", "值"],
        ["真实玩家总数", real_total],
        ["NPC/怪物城总数", len(all_players) - real_total],
        ["索引条目总数", len(all_players)],
        ["本次导出条数", len(players)],
        ["索引更新时间", time.strftime("%Y-%m-%d %H:%M:%S",
                                     time.localtime(upd)) if upd else ""],
        ["扫描状态", "扫描中" if meta.get("scanning") else
         ("未完成" if meta.get("partial") else "已完成")],
        ["已请求次数", meta.get("requests_done", "")],
        ["预计总请求", meta.get("requests_total", "")],
        ["断点 X", meta.get("next_x", "")],
        ["断点 Y", meta.get("next_y", "")],
        ["自己的坐标", ("%s, %s" % (sp.get("x"), sp.get("y"))) if sp else ""],
        ["区域聚类粒度", "%d x %d 格" % (AREA_BLOCK, AREA_BLOCK)],
        ["NPC 判别规则", "名字以 #<数字> 结尾 (如 Empire01a8c#2223)"],
        ["导出时间", time.strftime("%Y-%m-%d %H:%M:%S")],
    ]
    # ⚠️ 时效提示: 坐标是**扫描时刻的快照**。服务端会定时重排整张地图
    # (实测 2026-10-25 19:39 扫出来的坐标, 当天 20:20 已全部失效:
    #  原位置站着完全不同的玩家)。所以必须告诉用户"什么情况下坐标会过期"。
    if age_h is None:
        stale_note = "索引没有更新时间 —— 数据可能来自手工导入, 坐标请用页面「查玩家 · 现场扫描」核对"
    elif age_h > 6:
        stale_note = ("⚠️ 数据已 %.1f 小时前的快照。服务端会定时重排地图, "
                      "若游戏内坐标与本表对不上, 说明地图已重排 —— "
                      "请用页面「玩家坐标 · 现场扫描」或重跑 scan_world.py 刷新" % age_h)
    else:
        stale_note = ("数据为 %.1f 小时前的快照。服务端会定时重排地图, "
                      "若游戏内坐标对不上, 请重扫" % age_h)
    rows3.append(["⚠️ 数据时效", stale_note])
    rows3.append(["坐标性质", "扫描时刻的快照(不是实时位置); 玩家在地图重排后会整体迁移"])

    sheets = [
        ("玩家坐标", rows1, [18, 26, 8, 8, 8, 12, 8, 20]),
        ("区域分布", rows2, [10, 10, 14, 14, 8, 10, 26, 10]),
        ("扫描信息", rows3, [20, 40]),
    ]
    p = write_xlsx(sheets, path)
    stats = {"players": len(players), "real_players": real_total,
             "npc": len(all_players) - real_total,
             "blocks": len(blocks),
             "bytes": os.path.getsize(p) if p and os.path.exists(p) else 0}
    return p, stats
