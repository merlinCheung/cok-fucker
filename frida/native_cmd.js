'use strict';
/*
 * 抓 App 通过 native 侧发出的**协议请求命令名**。
 *
 * FUN_014af684(param_1, param_2, callback, 0, "cmdName", param_6)
 *   —— libgame.so 里的 native 请求发送入口(分析版 0x14af684, 设备版 0x13af684)。
 *      内部把命令名做 FNV-1a hash 后放进发送队列。
 *
 * 建造/加速等 UI 逻辑在 native 侧, Lua 的 requestServer 覆盖不到, 只能靠这里抓。
 */
const REQ_SEND = 0x13af684;

function emit(o) { try { send(o); } catch (e) {} }
function hexOf(buf) {
  const u8 = new Uint8Array(buf);
  let s = '';
  for (let i = 0; i < u8.length; i++) s += ('0' + u8[i].toString(16)).slice(-2);
  return s;
}

Process.attachModuleObserver({
  onAdded(module) {
    if (module.name !== 'libgame.so') return;
    setTimeout(function () {
      const base = module.base;
      const p = base.add(REQ_SEND);
      try {
        Interceptor.attach(p, {
          onEnter(args) {
            let cmd = null;
            try { cmd = args[4].readCString(); } catch (e) {}
            if (!cmd) return;
            emit({ t: 'native_cmd', cmd: cmd, p2: args[1].toString() });
          }
        });
        emit({ t: 'hooked', name: 'native_req_send', addr: p.toString() });
      } catch (e) {
        emit({ t: 'hook_err', name: 'native_req_send', msg: String(e) });
      }
    }, 300);
  }
});

emit({ t: 'script_loaded', pid: Process.id });
