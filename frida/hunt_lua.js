'use strict';
/*
 * 在 App 进程里直接执行 Lua, 取回 getIndexByPoint(x,y) 的换算结果。
 *
 * 原理:
 *  * libgame.so 导出 lua_pcall / luaL_loadstring / lua_tolstring
 *  * hook lua_pcall 的 onLeave —— 此刻上一段 Lua 已执行完, 栈是干净的,
 *    而我们仍在游戏线程的 C 栈里, 所以再压一次 lua_pcall 是安全的嵌套调用
 *  * 注入的 Lua 片段返回字符串, 用 lua_tolstring 取回
 *
 * 目标: 拿到 (x,y) -> point index 的换算, 以及 marchKey 的输入顺序。
 */
const MODULE = 'libgame.so';

function emit(o) { try { send(o); } catch (e) {} }

function findExport(name) {
  try {
    const p = Module.findExportByName(MODULE, name);
    if (p) return p;
  } catch (e) {}
  try {
    const m = Process.findModuleByName(MODULE);
    const s = m.enumerateSymbols().filter(function (x) { return x.name === name; });
    if (s.length) return s[0].address;
  } catch (e) {}
  return null;
}

Process.attachModuleObserver({
  onAdded(module) {
    if (module.name !== MODULE) return;
    setTimeout(function () {
      const base = module.base;
      const pLoad = findExport('luaL_loadstring');
      const pCall = findExport('lua_pcall');
      const pTolstr = findExport('lua_tolstring');
      emit({ t: 'sym', load: pLoad ? pLoad.toString() : null,
             call: pCall ? pCall.toString() : null,
             tolstr: pTolstr ? pTolstr.toString() : null });
      if (!pLoad || !pCall || !pTolstr) { emit({ t: 'fatal', msg: '缺 Lua 导出' }); return; }
      // frida 里必须用 NativeFunction 包装裸地址, 直接调用会报 "not a function"
      const luaL_loadstring = new NativeFunction(pLoad, 'int', ['pointer', 'pointer']);
      const lua_pcall = new NativeFunction(pCall, 'int', ['pointer', 'int', 'int', 'int']);
      const lua_tolstring = new NativeFunction(pTolstr, 'pointer', ['pointer', 'int', 'pointer']);

      // 背包道具: ToolController:getToolIdsByType(type) 列出该类型道具 id,
      // getToolInfoByIdForLua(id) -> uuid / getCNT()=数量。
      // type 2 = ITEM_TYPE_SPD(加速道具), 其它 type 也一起扫一遍。
      const CODES = [
        // getToolIdsByType 返回 CCArray(userdata), 要用 arrayToLuaTable 转
        "local ok,r=pcall(function() local out={} for _,tp in ipairs({2,1,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,60,70,80,90,100}) do local arr=ToolController:call('getToolIdsByType',tp); if arr then local ids=arrayToLuaTable(arr) if ids and #ids>0 then for i,v in ipairs(ids) do local t=ToolController:call('getToolInfoByIdForLua',tonumber(v)); if t then out[#out+1]=tostring(v)..':'..tostring(t:getProperty('uuid'))..':'..tostring(t:call('getCNT'))..':t'..tp end end end end end return table.concat(out,'|') end); return 'SPDBAG='..tostring(ok)..':'..tostring(r)",
        // 兜底: 直接看 ToolController 上有哪些方法
        "local ok,r=pcall(function() local t={} for k,v in pairs(getmetatable(ToolController) or {}) do t[#t+1]=tostring(k) end return table.concat(t,',') end); return 'methods='..tostring(ok)..':'..tostring(r)",
        "local ok,r=pcall(function() return tostring(GlobalData:call('shared'):getProperty('MaxStamina')) end); return 'MaxStamina='..tostring(ok)..':'..tostring(r)",
        "local ok,r=pcall(function() return tostring(WorldController:call('getInstance'):getProperty('currentStamine')) end); return 'currentStamine='..tostring(ok)..':'..tostring(r)",
      ];

      let done = false;
      let L = null;
      let idx = 0;
      let round = 0;
      const ROUNDS = 14;

      function run(L) {
        if (done) return;
        if (idx >= CODES.length) {
          idx = 0; round++;
          emit({ t: 'round', round: round });
          if (round >= ROUNDS) { done = true; emit({ t: 'done' }); return; }
          setTimeout(function () { try { run(L); } catch (e) { emit({ t: 'err', msg: String(e) }); } }, 20000);
          return;
        }
        const code = CODES[idx++];
        let ok = 0;
        try {
          const pstr = Memory.allocUtf8String(code);
          ok = luaL_loadstring(L, pstr);
        } catch (e) { emit({ t: 'err', msg: 'load: ' + String(e) }); return; }
        if (ok !== 0) { emit({ t: 'probe', code: idx, load: 'fail' }); return; }
        try {
          lua_pcall(L, 0, 1, 0);
        } catch (e) { emit({ t: 'err', msg: 'pcall: ' + String(e) }); return; }
        let out = null;
        try {
          const ps = lua_tolstring(L, -1, NULL);
          if (ps) out = ps.readCString();
        } catch (e) {}
        emit({ t: 'probe', code: idx, result: out });
      }

      Interceptor.attach(pCall, {
        onEnter(args) { if (!L) L = args[0]; },
        onLeave() {
          if (done || !L) return;
          // 延后一小段, 避免在 pcall 返回瞬间重入
          setTimeout(function () { try { run(L); } catch (e) { emit({ t: 'err', msg: String(e) }); } }, 120);
        }
      });
      emit({ t: 'hooked' });
    }, 800);
  }
});
