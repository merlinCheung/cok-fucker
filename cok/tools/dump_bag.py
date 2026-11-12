#!/usr/bin/env python3
"""采集 COK 账号的完整背包(道具实例 uuid + 数量)。

原理: 客户端的道具数据在 C++ `ToolController` 里
      * `getToolIdsByType(type)`   -> 该类型道具 id 列表(CCArray)
      * `getToolInfoByIdForLua(id)` -> {uuid, cnt}
      所以用 frida attach 到 App 并注入一段 Lua 就能读出来, 不需要猜协议命令。

用法:
  # 1) 先在手机上打开游戏(进主城即可, 不需要点背包)
  # 2) 跑:
  python3 dump_bag.py --out bag-items.json
  python3 dump_bag.py --out bag-items.json --speedup speedup-owned.json

注意: 同账号只允许一个连接, 运行期间网页控制台要停着(App 也会被顶掉)。
"""
import os as _os
import sys as _sys
_PKG_ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
if _os.path.isdir(_PKG_ROOT) and _PKG_ROOT not in _sys.path:
    _sys.path.insert(0, _PKG_ROOT)

import argparse
from cok_paths import resource as _res  # noqa: E402
import json
import os
import subprocess
import sys
import threading
import time

import frida

ADB = "/Users/a1234/Library/Android/sdk/platform-tools/adb"
PKG = os.environ.get("COK_PKG", "com.hcg.cok.nearme.gamecenter")
HERE = os.path.dirname(os.path.abspath(__file__))

# 注入的 Lua: 遍历多种 type 取道具 id, 逐个读 uuid/数量
LUA_CODE = (
    "local out={} "
    "for _,tp in ipairs({2,1,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,"
    "21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,"
    "46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,"
    "71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,95,96,"
    "97,98,99,100}) do "
    " local ok,arr=pcall(function() return ToolController:call('getToolIdsByType',tp) end) "
    " if ok and arr then local ids=arrayToLuaTable(arr) "
    "  if ids and #ids>0 then for i,v in ipairs(ids) do "
    "   local ok2,t=pcall(function() return ToolController:call('getToolInfoByIdForLua',tonumber(v)) end) "
    "   if ok2 and t then local u='' local c=0 "
    "    local ok3=pcall(function() u=tostring(t:getProperty('uuid')) end) "
    "    local ok4=pcall(function() c=t:getCNT() end) "
    "    out[#out+1]=tostring(v)..'\\t'..u..'\\t'..tostring(c)..'\\t'..tp end "
    "   end end end end end "
    "return table.concat(out,'\\n')"
)

AGENT_JS = """
'use strict';
const MODULE = 'libgame.so';
function emit(o) { try { send(o); } catch (e) {} }
function findExport(name) {
  try { const p = Module.findExportByName(MODULE, name); if (p) return p; } catch (e) {}
  try { const m = Process.findModuleByName(MODULE);
        const s = m.enumerateSymbols().filter(function (x) { return x.name === name; });
        if (s.length) return s[0].address; } catch (e) {}
  try { const p = Module.findGlobalExportByName(name); if (p) return p; } catch (e) {}
  try {
    const mods = Process.enumerateModules();
    for (let i = 0; i < mods.length; i++) {
      if (mods[i].name.indexOf('libgame') < 0) continue;
      try { const p = mods[i].getExportByName(name); if (p) return p; } catch (e) {}
    }
  } catch (e) {}
  return null;
}
function setup() {
  setTimeout(function () {
    const pLoad = findExport('luaL_loadstring');
    const pCall = findExport('lua_pcall');
    const pTolstr = findExport('lua_tolstring');
    if (!pLoad || !pCall || !pTolstr) { emit({t:'fatal', msg:'缺 Lua 导出'}); return; }
    const luaL_loadstring = new NativeFunction(pLoad, 'int', ['pointer','pointer']);
    const lua_pcall = new NativeFunction(pCall, 'int', ['pointer','int','int','int']);
    const lua_tolstring = new NativeFunction(pTolstr, 'pointer', ['pointer','int','pointer']);
    let L = null, done = false, tried = 0;
    function run() {
      if (done || !L) return;
      tried++;
      const code = __CODE__;
      let ok = 0;
      try { ok = luaL_loadstring(L, Memory.allocUtf8String(code)); } catch (e) {}
      if (ok !== 0) { emit({t: 'try', n:tried, load:'fail'}); return; }
      try { lua_pcall(L, 0, 1, 0); } catch (e) { emit({t: 'try', n:tried, pcall:String(e).slice(0,120)}); return; }
      let out = null;
      try { const ps = lua_tolstring(L, -1, NULL); if (ps) out = ps.readCString(); } catch (e) {}
      emit({t: 'bag', n:tried, out: out});
      if (out && out.indexOf('\t') >= 0) done = true;
    }
    // App 已进主城时 lua_pcall 可能不再触发: 额外挂几个会被周期性调用的
    // Lua API 抓 lua_State, 再用定时器持续重试注入。
    ['lua_gettop', 'lua_call', 'luaL_loadstring', 'lua_pushnil', 'lua_settop',
     'lua_getfield', 'lua_setfield', 'lua_pushstring', 'lua_pushvalue',
     'lua_rawgeti', 'lua_gettable', 'lua_settable', 'lua_createtable',
     'lua_newtable', 'lua_pushcclosure', 'lua_tolstring'].forEach(function (nm) {
      try {
        const p = findExport(nm);
        if (!p) return;
        Interceptor.attach(p, { onEnter(args) { if (!L) L = args[0]; } });
      } catch (e) {}
    });
    // 诊断: 把 lua 符号的查找结果发出来(找不到就是 so 没导出 lua API)
    try {
      const found = ['lua_gettop', 'lua_call', 'lua_pcall', 'luaL_loadstring']
        .map(function (n) { return n + '=' + (findExport(n) ? 'Y' : 'N'); }).join(' ');
      emit({t: 'diag', luaExports: found});
    } catch (e) {}
    const timer = setInterval(function () {
      if (done) { clearInterval(timer); return; }
      try { run(); } catch (e) { emit({t: 'err', msg: String(e).slice(0,160)}); }
    }, 2500);
    emit({t: 'hooked'});
  }, 800);
}

Process.attachModuleObserver({ onAdded(module) {
  if (module.name !== MODULE) return;
  setup();
}});

// attach 时 libgame.so 往往**已经加载完**(App 早就在跑), observer 不会再触发,
// 所以这里主动查一次并直接 setup。
setTimeout(function () {
  try {
    const m = Process.findModuleByName(MODULE);
    if (m) setup();
  } catch (e) { emit({t: 'err', msg: 'findModule: ' + String(e).slice(0,120)}); }
}, 400);
"""


def app_pid():
    """游戏主进程的 pid。

    ⚠️ `pidof <pkg>` 会把 `:core` 之类的子进程也列出来, 而 **libgame.so 只在
    主进程里**(实测: ewanqf 的 :core 进程 maps 里没有 libgame.so)。
    attach 到错的进程就永远读不到 ToolController。
    """
    try:
        out = subprocess.run([ADB, "shell", "pidof", PKG], capture_output=True,
                             text=True, timeout=6).stdout.strip()
        pids = [int(x) for x in out.split() if x.strip().isdigit()]
    except Exception:
        return 0
    for pid in pids:
        try:
            maps = subprocess.run(
                [ADB, "shell", "su", "-c", "grep -c libgame.so /proc/%d/maps" % pid],
                capture_output=True, text=True, timeout=8).stdout.strip()
            if maps and int(maps.splitlines()[-1].strip() or 0) > 0:
                return pid
        except Exception:
            continue
    return pids[0] if pids else 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=_res("bag-items.json"))
    ap.add_argument("--speedup", help="同时写加速道具快照到这个文件")
    ap.add_argument("--seconds", type=int, default=180)
    ap.add_argument("--launch", action="store_true",
                    help="App 没开时自动拉起")
    args = ap.parse_args()

    pid = app_pid()
    if not pid and args.launch:
        print("[*] 拉起 App —— 还需要你在手机上点进主城(加载完才会发 lua_pcall)")
        try:
            subprocess.run([ADB, "shell", "monkey", "-p", PKG,
                            "-c", "android.intent.category.LAUNCHER", "1"],
                           capture_output=True, timeout=30)
        except Exception:
            pass
        for _ in range(25):
            time.sleep(2)
            pid = app_pid()
            if pid:
                break
    if not pid:
        print("[!] App 没在跑 —— 请先在手机上打开游戏(进主城即可), 或加 --launch")
        return 2
    print("[*] App pid =", pid, flush=True)

    dev = frida.get_usb_device(timeout=20)
    session = dev.attach(pid)
    src = AGENT_JS.replace("__CODE__", json.dumps(LUA_CODE))
    script = session.create_script(src)

    result = {}
    lock = threading.Lock()

    def on_message(message, data):
        p = message.get("payload")
        if message.get("type") == "send" and isinstance(p, dict):
            if p.get("t") == "bag" and p.get("out"):
                with lock:
                    out = p.get("out") or ""
                    result["n"] = p.get("n")
                    # 只有拿到真正的道具行(带 tab)才算成功, 否则说明 App 还没进主城
                    if chr(9) in out:
                        result.setdefault("out", out)
                    else:
                        result.setdefault("empty", p.get("n"))
            else:
                print("[hook]", json.dumps(p, ensure_ascii=False)[:200], flush=True)

    script.on("message", on_message)
    script.load()

    deadline = time.time() + args.seconds
    while time.time() < deadline:
        with lock:
            if "out" in result:
                break
        time.sleep(1)

    try:
        script.unload()
    except Exception:
        pass
    try:
        session.detach()
    except Exception:
        pass

    with lock:
        raw = result.get("out")
    if not raw:
        print("[!] 没读到背包数据(试第 %s 轮都没拿到; App 是否已进主城?)" % result.get("n"))
        return 3

    items = []
    for line in raw.split("\n"):
        if not line.strip():
            continue
        parts = line.split("\t")
        if len(parts) < 3:
            continue
        iid, uuid, cnt = parts[0], parts[1], parts[2]
        tp = parts[3] if len(parts) > 3 else ""
        try:
            cnt = int(cnt)
        except ValueError:
            cnt = 0
        items.append({"itemId": iid, "uuid": uuid, "count": cnt, "type": tp})
    owned = [x for x in items if x["count"] > 0]
    doc = {"source": "frida Lua 注入读 ToolController", "total": len(items),
           "owned": len(owned), "items": items}
    json.dump(doc, open(args.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("[*] 写入 %s: 共 %d 条, 有库存 %d 条" % (args.out, len(items), len(owned)))

    if args.speedup:
        # 加速道具: type=2 (ITEM_TYPE_SPD) 或 id 以 2002 开头
        sp = [x for x in owned if x.get("type") == "2" or str(x["itemId"]).startswith("2002")]
        json.dump({"source": "dump_bag.py (frida Lua)", "items": {x["itemId"]: x for x in sp}},
                  open(args.speedup, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print("[*] 加速道具快照 %d 种 -> %s" % (len(sp), args.speedup))
    return 0


if __name__ == "__main__":
    sys.exit(main())
