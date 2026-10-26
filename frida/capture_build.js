'use strict';
/*
 * 「点一次就能抓到」探针: 一把挂住所有可能承载 **协议请求发出** 的位置,
 * 只要 App 在界面上触发一次建造/加速/领奖, 这里就能记下真实命令名与参数。
 *
 * 挂点:
 *   1) XOR 加密引擎 0x9e02b8   —— 所有 Java 侧业务请求加密处
 *   2) native 请求发送 0x13af684 —— native 侧(FUN_014af684)的命令名入口
 *   3) native 事件派发 0x148ce40 —— 服务端响应 → 客户端事件(msg_*)
 *   4) libc write/send           —— 线路原始字节
 *
 * 用法: 挂上之后在 App 界面点一次目标操作, 然后看输出里的 native_cmd / sfs_io。
 */
const OFF = {
  XOR: 0x9e02b8,
  NATIVE_SEND: 0x13af684,
  NATIVE_EVENT: 0x148ce40,
};

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

      function hook(off, tag, handlers) {
        const p = base.add(off);
        try { Interceptor.attach(p, handlers); emit({ t: 'hooked', name: tag, addr: p.toString() }); }
        catch (e) { emit({ t: 'hook_err', name: tag, msg: String(e) }); }
      }

      // 1) XOR 引擎: args[2] = 密钥串, args[1] = 长度
      hook(OFF.XOR, 'xor', {
        onEnter(args) {
          const len = args[1].toInt32();
          let head = null;
          try { head = hexOf(args[0].readByteArray(Math.min(len, 48))); } catch (e) {}
          emit({ t: 'xor_encrypt', len: len, head: head });
        }
      });

      // 2) native 侧命令名入口
      hook(OFF.NATIVE_SEND, 'native_send', {
        onEnter(args) {
          let cmd = null;
          try { cmd = args[4].readCString(); } catch (e) {}
          if (cmd) emit({ t: 'native_cmd', cmd: cmd });
        }
      });

      // 3) native 事件派发(服务端响应 → 客户端)
      hook(OFF.NATIVE_EVENT, 'native_event', {
        onEnter(args) {
          let name = null;
          try { name = args[1].readCString(); } catch (e) {}
          if (name) emit({ t: 'native_event', name: name });
        }
      });

      // 4) 线路原始字节
      const libc = Process.getModuleByName('libc.so');
      function h(name, dir) {
        let p = null;
        try { p = libc.getExportByName(name); } catch (e) { return; }
        Interceptor.attach(p, {
          onEnter(args) { this.fd = args[0].toInt32(); this.buf = args[1]; this.len = args[2].toInt32(); },
          onLeave(ret) {
            const n = dir === 'read' ? ret.toInt32() : this.len;
            if (n <= 0 || n > 262144) return;
            let hex = null;
            try { hex = hexOf(this.buf.readByteArray(n)); } catch (e) {}
            emit({ t: 'wire', dir: dir, fd: this.fd, len: n, hex: hex });
          }
        });
      }
      h('write', 'write'); h('send', 'send'); h('read', 'read'); h('recv', 'recv');
      emit({ t: 'wire_hooked' });
    }, 300);
  }
});

emit({ t: 'script_loaded', pid: Process.id });
