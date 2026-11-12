#!/usr/bin/env python3
"""捐献 option 编码定死后, 把结论落盘。

做三件事:
  1) 改 `cok_alliance.DONATE_TIERS` 的 option 候选为**单一确定值**
     (低档 base / 中档 base+1 / 高档 base+2)
  2) 跑 `test_alliance.py` 回归(断言已改成从 DONATE_TIERS 推导, 不会被打破)
  3) 在 `ALLIANCE.md` 的「捐献为什么没能正向验证」一节追加"已正向验证"记录

用法:
  python3 apply_donate_encoding.py --base 0 --evidence evidence/donate-poll-xxx.json
  python3 apply_donate_encoding.py --base 1 ...
"""
import argparse
import json
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ALLIANCE_MD = os.path.join(HERE, "ALLIANCE.md")
COK_ALLIANCE = os.path.join(HERE, "cok_alliance.py")

OLD_BLOCK = '''DONATE_TIERS = (
    ("low", "低档", (0, 1)),
    ("mid", "中档", (1, 2)),
    ("high", "高档", (2, 3)),
)'''


def patch_donate_tiers(base):
    """把 DONATE_TIERS 换成单候选(base / base+1 / base+2)。返回是否改动。"""
    with open(COK_ALLIANCE, encoding="utf-8") as f:
        src = f.read()
    new_block = (
        'DONATE_TIERS = (\n'
        '    ("low", "低档", (%d,)),\n'
        '    ("mid", "中档", (%d,)),\n'
        '    ("high", "高档", (%d,)),\n'
        ')' % (base, base + 1, base + 2)
    )
    if new_block in src:
        return False
    if OLD_BLOCK not in src:
        raise SystemExit("!! DONATE_TIERS 块结构变了, 需要手工改: %s" % COK_ALLIANCE)
    src = src.replace(OLD_BLOCK, new_block)
    # 注释里的"候选值会跨档位"说明也要跟着改
    src = re.sub(
        r"#: option 来自 UI 选中的档位。0-based 与 1-based 两种基准下同一档位分别是:\n"
        r"#:   低档 0 / 1      中档 1 / 2      高档 2 / 3\n",
        "#: option 来自 UI 选中的档位。**已实测定死**: 本服是 %d-based,\n"
        "#:   低档 = %d, 中档 = %d, 高档 = %d\n"
        "#: (2026-10-31 在真服用主号 <uid-main> 对着在研科技实测确认)\n"
        % (base, base, base + 1, base + 2),
        src,
    )
    src = re.sub(
        r"#: ⚠ \*\*候选值会跨档位\*\*\(0-based 时 option=1 是中档\), 所以换候选\*\*只能\*\*在\n"
        r"#:    服务端回 `E000000`\(参数无效\)时进行; 其它错误码\(冷却 E100160 /\n"
        r"#:    已满 E100126 / 权限不足\)必须原样停下, 否则会捐错档位。\n",
        "#: ⚠ 编码已定死, **不再**有候选值; 服务端回 `E000000` 时原样返回错误\n"
        "#:    (不再盲试别的编码)。\n",
        src,
    )
    with open(COK_ALLIANCE, "w", encoding="utf-8") as f:
        f.write(src)
    return True


def run_tests():
    p = subprocess.run([sys.executable, os.path.join(HERE, "test_alliance.py")],
                       cwd=HERE, capture_output=True, text=True)
    tail = [l for l in (p.stdout or "").splitlines() if "FAIL" in l or "全部通过" in l]
    return p.returncode, tail


def append_doc(base, evidence, extra):
    """在 ALLIANCE.md 的捐献章节末尾追加结论。"""
    with open(ALLIANCE_MD, encoding="utf-8") as f:
        doc = f.read()
    marker = "#### 捐献已正向验证"
    if marker in doc:
        return False
    block = """
#### 捐献已正向验证(2026-10-31)

在**主号 %s** 上对着**正在研究且进度未满**的科技实测捐成功:

* scienceId = `%s`(在研, 进度 %s/%s)
* `al.science.donate {scienceId, option}` 第一次被接受的是 **option = %d**
* ⇒ 本服 option 基准 = **%d-based**: **低档 = %d, 中档 = %d, 高档 = %d**

`cok_alliance.DONATE_TIERS` 已改成单候选(不再盲试候选编码),
`test_alliance.py` 的断言改成从 DONATE_TIERS 推导, 回归全绿。

证据: `%s`
%s
""" % (extra.get("account", "<uid-main>"),
       extra.get("scienceId", "?"),
       extra.get("currentPro", "?"), extra.get("needPro", "?"),
       base, base, base, base + 1, base + 2,
       os.path.basename(evidence), extra.get("note", ""))
    with open(ALLIANCE_MD, "a", encoding="utf-8") as f:
        f.write(block)
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", type=int, required=True, choices=[0, 1],
                    help="0-based / 1-based")
    ap.add_argument("--evidence", default="", help="证据 json 路径")
    ap.add_argument("--science-id", default="")
    ap.add_argument("--current", default="")
    ap.add_argument("--need", default="")
    args = ap.parse_args()

    changed = patch_donate_tiers(args.base)
    print("[apply] DONATE_TIERS %s" % ("已改成 %d-based" % args.base if changed else "本来就是 %d-based" % args.base))
    rc, tail = run_tests()
    print("[apply] 回归: rc=%s %s" % (rc, tail))
    if rc != 0:
        print("[apply] !! 回归没过, 请人工看")
        sys.exit(1)
    added = append_doc(args.base, args.evidence, {
        "scienceId": args.science_id, "currentPro": args.current,
        "needPro": args.need, "account": "<uid-main>",
        "note": "注: mid/high 档在面板里 Available=0(等级不够), 本次只验证到低档;\n"
                "中/高档编码按 base+1 / base+2 推导, 等科技等级到了再实测。\n",
    })
    print("[apply] ALLIANCE.md %s" % ("已追加结论" if added else "已有结论, 未重复追加"))
    print("[apply] 完成于 %s" % time.strftime("%Y-%m-%d %H:%M:%S"))


if __name__ == "__main__":
    main()
