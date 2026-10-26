'use strict';
/*
 * 游戏协议 wire 层探针 (v4)
 * -----------------------------------------------
 * 目标: 抓到 **命令名**。
 *
 * 之前抓不到命令名的原因:
 *   - xor 引擎只拿到 **params**(命令名在更外层的 envelope 里)
 *   - write()/send() 抓到的是 **TLS 密文**
 *
 * 现在用两层:
 *   1) libc write/send  -> 扫描其中 **首字节为 0x80 的 SFS 帧**
 *      (游戏协议走明文 TCP, 资源下载走 TLS —— 靠首字节区分)
 *   2) xor 引擎         -> 会话 XOR 密钥(用于解 params)
 *
 * 帧结构: [flags:1][len:2][SFS 载荷]
 *   载荷 = { p: { p: { params: <加密字节数组> }, r: -1, c: "<命令名>" },
 *           a: 13, c: 1 }
 *   → 命令名在 p.c, params 在 p.p.params
 */
const OFF = { XOR: 0x9e02b8 };
const MAX = 4 * 1024 * 1024;

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

      // ---- 1) XOR 引擎: 会话密钥 ----
      try {
        Interceptor.attach(base.add(OFF.XOR), {
          onEnter(args) {
            try {
              const kp = args[2].readPointer();
              const klen = kp.sub(0x18).readU32();
              if (klen > 0 && klen <= 64) {
                const k = hexOf(kp.readByteArray(klen));
                emit({ t: 'key', key: k });
              }
            } catch (e) {}
          }
        });
        emit({ t: 'hooked', name: 'xor', addr: base.add(OFF.XOR).toString() });
      } catch (e) { emit({ t: 'hook_err', name: 'xor', msg: String(e) }); }

      // ---- 2) wire 层: 抓明文 SFS 帧 ----
      try {
        const libc = Process.getModuleByName('libc.so');
        function h(name) {
          const p = libc.getExportByName(name);
          if (!p) return;
          Interceptor.attach(p, {
            onEnter(args) { this.buf = args[1]; this.len = args[2].toInt32(); },
            onLeave() {
              try {
                const n = this.len;
                if (!n || n < 4 || n > MAX) return;
                const b = this.buf.readByteArray(n);
                if (!b) return;
                const u8 = new Uint8Array(b);
                if (u8[0] !== 0x80) return;          // 只取 SFS 明文帧
                emit({ t: 'w', len: n, hex: hexOf(b) });
              } catch (e) {}
            }
          });
        }
        h('write'); h('send');
        emit({ t: 'hooked', name: 'wire' });
      } catch (e) { emit({ t: 'hook_err', name: 'wire', msg: String(e) }); }

      emit({ t: 'script_loaded', pid: Process.id });
    }, 800);
  }
});
