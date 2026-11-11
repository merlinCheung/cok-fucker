#!/usr/bin/env python3
"""一次连接搞定两件事 —— 2026-11-10。

阶段 1: 把 init 响应的**每一个**加密字段都解开(以前只解第一个), 搜道具。
阶段 2: 把 frida 抓到的「客户端登录时真实发出的命令」批量发一遍,
        找出哪个的响应里带道具(itemId/uuid/count)。

命令都挑的只读的; 缺参数最多回 E000000, 不会消耗资源。

用法: python3 probe_bag_sweep.py <gameUid>
"""
import os
import re
import sys
import tempfile
import time
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ['COK_ACCOUNT_LOCK_FILE'] = os.path.join(
    tempfile.gettempdir(), 'cok-probe-sweep-%d.lock' % os.getpid())

from cok_client import CokClient, account_lock, apply_account_types  # noqa: E402
from cok_sfs import decode_params, parse_packet                       # noqa: E402
import cok_accounts as cas                                           # noqa: E402

uid = sys.argv[1] if len(sys.argv) > 1 else "<uid-other>"
acc = apply_account_types(dict(cas.get_account(uid)))
cl = CokClient(timeout=12, account=acc)

HEX32 = re.compile(r'^[0-9a-f]{32}$')
STAM = ("200380", "200381", "200382")

# frida 抓到的「客户端登录时真实发出」的命令(去重保序)
REAL_CMDS = [
    "login.dataconfig", "login.other", "cmd.finishinit",
    "kingdomtask_new.data", "daily.quest.ls", "civilization.prestige.info",
    "hero.introduction", "cok.proto", "oad.data", "alquick.data",
    "buidlingextension.res", "strengthen.info", "treasuremap.info",
    "elp.info", "ock.get", "magic.effect", "science.data.init",
    "score.login", "al.rank", "userpayreward.newinfo", "branchcity.enter",
    "hange.data", "show.enter.view.popup.sign", "scanctuary.data",
    "oat.data", "stat.tt", "exchange.refresh", "science.data.cond",
    "auction.get", "resource.client.reward.getmulti", "exchangeshow.ready",
    "miraclestone.data", "itemcollection.data", "enter.all", "ar.info",
    "ar.preview", "festivalview.data", "reference.data", "obilization.data",
    "obilization.data2", "oss.boss", "wild_monster_festival.data",
    "ragon.data", "everydayexchange.data", "trigger.activity",
    "monthfund.rewardinfo", "ign.info", "uest2025.data", "ecord.set",
    "resource.client.reward.get", "invest.open.ui", "story.task.info",
    "astle.info", "userfeedback.info", "formation.get", "skin.introduction",
    "skill.state.get", "castle.data", "rain.bag", "adge.badge", "et.list",
    "ct.info", "relic.get", "get.clash.server.list", "tactics.get",
    "skin.effect_new", "magic_weapon.data", "ift.info", "pgrade.data",
    "ask.data", "overview_new.data", "act.ls", "crossthrone.time",
    "show.status.item", "achieve.ls",
]


def find_items(obj):
    """在响应里找带道具特征的路径"""
    hits = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, list) and v and isinstance(v[0], dict):
                ks = set(v[0].keys())
                if "uuid" in ks or "itemId" in ks:
                    hits.append((k, len(v), json.dumps(v[0], ensure_ascii=False)[:200]))
            if isinstance(v, str) and (HEX32.match(v) or v in STAM):
                hits.append((k, 1, v))
            hits += find_items(v)
    elif isinstance(obj, list):
        for v in obj[:50]:
            hits += find_items(v)
    return hits


with account_lock(timeout=5, purpose="probe", key=uid):
    cl.connect()
    cl.bin_handshake()
    cl.login()

    # ---------- 阶段 1: init 全部字段 ----------
    print("=== 阶段 1: init 全部加密字段 ===", flush=True)
    cl.sock.settimeout(3.0)
    buf = b""
    t0 = time.time()
    inits = []
    while time.time() - t0 < 20 and not inits:
        try:
            ch = cl.sock.recv(65536)
        except Exception:  # noqa: BLE001
            continue
        if not ch:
            break
        buf += ch
        i = 0
        while i + 3 <= len(buf):
            flags = buf[i]
            ln = (buf[i + 1] << 8) | buf[i + 2]
            if not (flags & 0x80) or ln == 0 or i + 3 + ln > len(buf):
                break
            try:
                _, _, obj, _ = parse_packet(buf[i:i + 3 + ln])
            except Exception:  # noqa: BLE001
                break
            pp = cl._resp_params(obj)
            if cl._resp_cmd(obj) == "init":
                inits = list(pp.items())
                break
            i += 3 + ln
        buf = buf[i:]

    if inits:
        print("init 参数 %d 个:" % len(inits), flush=True)
        for k, v in inits:
            print("  %-16s %s len=%s" % (k, type(v).__name__,
                                          len(v) if isinstance(v, str) else "-"), flush=True)
        for k, v in inits:
            if not isinstance(v, str) or len(v) <= 60 or k == "qqq":
                continue
            try:
                o2, _, _ = decode_params(bytes.fromhex(v), cl.key)
            except Exception as e:  # noqa: BLE001
                print("  字段 %s 解不开: %s" % (k, str(e)[:60]), flush=True)
                continue
            print("  字段 %s -> %d 键: %s" % (k, len(o2), sorted(o2.keys())[:30]), flush=True)
            hits = find_items(o2)
            if hits:
                print("    ★ 含道具: %s" % json.dumps(hits[:6], ensure_ascii=False), flush=True)
    else:
        print("!! 没拿到 init", flush=True)

    # ---------- 阶段 2: 扫客户端真实命令 ----------
    print("\n=== 阶段 2: 扫客户端真实发出的命令 (找带道具的) ===", flush=True)
    found = []
    for cmd in REAL_CMDS:
        t0 = time.time()
        try:
            r = cl.call(cmd, {}, retries=1)
            p = r.get("__params__") or {}
            dt = time.time() - t0
            hits = find_items(p)
            keys = list(p.keys())[:6]
            flag = " ★★ 含道具" if hits else ""
            print("  %-38s %6.2fs  键=%s%s" % (cmd, dt, keys, flag), flush=True)
            if hits:
                print("      %s" % json.dumps(hits[:4], ensure_ascii=False)[:400], flush=True)
                found.append((cmd, hits))
        except Exception as e:  # noqa: BLE001
            dt = time.time() - t0
            msg = str(e)
            kind = "超时" if ("超时" in msg or "无响应" in msg) else "ERR"
            print("  %-38s %6.2fs  %s" % (cmd, dt, kind), flush=True)

    print("\n=== 结论 ===", flush=True)
    if found:
        for cmd, hits in found:
            print("  %s -> %s" % (cmd, json.dumps(hits[:3], ensure_ascii=False)[:400]), flush=True)
    else:
        print("  没有命令返回道具", flush=True)
cl.close()
