'use strict';
/*
 * 地图命令探针 (v3)
 * ---------------------------------------------
 * 之前抓不到命令名, 因为:
 *   - xor 引擎只拿到 **params**(命令名 p.p.c 在更外层的 envelope 里)
 *   - write()/send() 抓到的是 **TLS 密文**
 *
 * 这里直接 hook 静态链接的 OpenSSL:
 *   SSL_write(0x2dd8094) -> 出站明文完整 SFS 帧(含 p.p.c 命令名)
 *   SSL_read (0x2dd7d70) -> 入站明文(解密后、zlib 前)
 *
 * 明文帧格式: [flags:1][len:2 大端][SFS 载荷]
 *   载荷 = { p: { p: { params: <字节数组>, r: -1, c: "<命令名>" } }, a: 13, c: 1 }
 *   注意 params 本身是**再 XOR 一次**的, 但命令名是明文 -> 够用了。
 */
const OFF = { SSL_write: 0x2dd8094, SSL_read: 0x2dd7d70 };
const MAX = 4 * 1024 * 1024;

function emit(o) { try { send(o); } catch (e) {} }

function hexOf(buf) {
  const u8 = new Uint8Array(buf);
  let s = '';
  for (let i = 0; i < u8.length; i++) s += ('0' + u8[i].toString(16)).slice(-2);
  return s;
}

// 从明文 SFS 帧里粗略抓命令名: 找 "p" -> "p" -> "c" 结构
// 直接用字节模式找命令名字符串更稳: 命令名是 UTF_STRING, 前导 0x08 + len
function findCmdName(buf) {
  // 扫描所有 0x08 <len:2> 形式的字符串, 取看起来像命令名的(含 '.' 且全是 [a-z._])
  const u8 = new Uint8Array(buf);
  const out = [];
  for (let i = 0; i + 3 < u8.length; i++) {
    if (u8[i] !== 0x08) continue;
    const len = (u8[i + 1] << 8) | u8[i + 2];
    if (len < 3 || len > 60 || i + 3 + len > u8.length) continue;
    let s = '';
    let ok = true;
    for (let k = 0; k < len; k++) {
      const c = u8[i + 3 + k];
      if (c < 0x20 || c > 0x7e) { ok = false; break; }
      s += String.fromCharCode(c);
    }
    if (!ok) continue;
    if (!/^[a-z][a-z0-9_]*(\.[a-z0-9_]+)+$/.test(s)) continue;
    out.push(s);
  }
  return out;
}

Process.attachModuleObserver({
  onAdded(module) {
    if (module.name !== 'libgame.so') return;
    setTimeout(function () {
      const base = module.base;
      try {
        Interceptor.attach(base.add(OFF.SSL_write), {
          onEnter(args) {
            try {
              const len = args[2].toInt32();
              if (len <= 0 || len > MAX) return;
              const hex = hexOf(args[1].readByteArray(len));
              const cmds = findCmdName(args[1].readByteArray(len));
              emit({ t: 'w', dir: 'req', len: len, hex: hex, cmds: cmds });
            } catch (e) {}
          }
        });
        emit({ t: 'hooked', name: 'SSL_write', addr: base.add(OFF.SSL_write).toString() });
      } catch (e) { emit({ t: 'hook_err', name: 'SSL_write', msg: String(e) }); }

      try {
        Interceptor.attach(base.add(OFF.SSL_read), {
          onEnter(args) {
            this.len = args[2].toInt32();
            this.buf = args[1];
          },
          onLeave(retval) {
            try {
              const n = retval.toInt32();
              if (!this.len || n <= 0 || n > MAX) return;
              const hex = hexOf(this.buf.readByteArray(n));
              const cmds = findCmdName(this.buf.readByteArray(n));
              emit({ t: 'w', dir: 'resp', len: n, hex: hex, cmds: cmds });
            } catch (e) {}
          }
        });
        emit({ t: 'hooked', name: 'SSL_read', addr: base.add(OFF.SSL_read).toString() });
      } catch (e) { emit({ t: 'hook_err', name: 'SSL_read', msg: String(e) }); }

      emit({ t: 'script_loaded', pid: Process.id });
    }, 800);
  }
});
