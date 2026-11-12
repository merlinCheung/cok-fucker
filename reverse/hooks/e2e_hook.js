'use strict';
/*
 * 最终版: 抓 params 加密的明文 + 密文(原地加密) + 密钥表原始字节
 *   FUN_00ae02b8(data, len, keyStr*, flag): 原地加密, 返回后 data 已是密文
 */
function hexOf(buf) {
  const u8 = new Uint8Array(buf);
  let s = '';
  for (let i = 0; i < u8.length; i++) s += ('0' + u8[i].toString(16)).slice(-2);
  return s;
}
function emit(o) { try { send(o); } catch (e) {} }

function readStdString(p) {
  try {
    if (!p || p.isNull()) return null;
    const dataPtr = p.readPointer();
    const len = p.add(8).readU32();
    if (len === 0) return { len: 0, text: '' };
    if (len > 4096) return { len: len, text: null };
    const sso = dataPtr.equals(p.add(16));
    const base = sso ? p.add(16) : dataPtr;
    return { len: len, text: base.readUtf8String(len), sso: sso };
  } catch (e) { return { err: String(e) }; }
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

      // 加密 A: 原地
      hook(0x9e02b8, 'enc_A', {
        onEnter(args) {
          this.len = args[1].toInt32();
          this.buf = args[0];
          this.key = readStdString(args[2]);
          let plain = null;
          try { plain = hexOf(args[0].readByteArray(Math.min(this.len, 4096))); } catch (e) {}
          this.plain = plain;
        },
        onLeave() {
          let cipher = null;
          try { cipher = hexOf(this.buf.readByteArray(Math.min(this.len, 4096))); } catch (e) {}
          emit({
            t: 'enc_pair', len: this.len,
            key: this.key ? this.key.text : null,
            key_raw: this.key ? this.key.len : null,
            plain_hex: this.plain, cipher_hex: cipher
          });
        }
      });

      // 加密 B
      hook(0x9b7890, 'enc_B', {
        onEnter(args) {
          this.len = args[2].toInt32();
          this.buf = args[1];
          this.key = readStdString(args[3]);
          let plain = null;
          try { plain = hexOf(args[1].readByteArray(Math.min(this.len, 4096))); } catch (e) {}
          this.plain = plain;
        },
        onLeave() {
          let cipher = null;
          try { cipher = hexOf(this.buf.readByteArray(Math.min(this.len, 4096))); } catch (e) {}
          emit({ t: 'enc_pair_B', len: this.len, key: this.key ? this.key.text : null, plain_hex: this.plain, cipher_hex: cipher });
        }
      });

      // 密钥表原始字节
      const A = base.add(0x3b1a5f8).readPointer();
      if (A && !A.isNull()) {
        const mapAddr = A.add(0x1a8);
        const seen = new Set();
        function walk(node, depth) {
          if (node === null || depth > 64) return;
          const k = node.toString();
          if (seen.has(k)) return;
          seen.add(k);
          let left, right;
          try { left = node.add(0x10).readPointer(); right = node.add(0x18).readPointer(); } catch (e) { return; }
          walk(left, depth + 1);
          try {
            const ik = node.add(0x20).readS32();
            const raw = hexOf(node.add(0x28).readByteArray(24));
            const s = readStdString(node.add(0x28));
            emit({ t: 'map_entry', k: ik, raw: raw, len: s ? s.len : null, v: s ? s.text : null });
          } catch (e) {}
          walk(right, depth + 1);
        }
        try { walk(mapAddr.add(0x10).readPointer(), 0); } catch (e) { emit({ t: 'walk_err', msg: String(e) }); }
        // BlowFish key 原始字节
        try { emit({ t: 'bf_key_raw', raw: hexOf(A.add(0x1d8).readByteArray(24)) }); } catch (e) {}
      }
    }, 400);
  }
});


// ---- 同会话抓线上原始字节 (fd 212) ----
const libc = Process.getModuleByName('libc.so');
let TARGET_FD = -1;   // 由 connect() 自动识别
function hookLib(name, dir) {
  let p = null;
  try { p = libc.getExportByName(name); } catch (e) { return; }
  Interceptor.attach(p, {
    onEnter(args) { this.fd = args[0].toInt32(); this.buf = args[1]; this.len = args[2].toInt32(); },
    onLeave(ret) {
      const n = dir === 'read' ? ret.toInt32() : this.len;
      if (n <= 0) return;
      let hex = null;
      try { hex = hexOf(this.buf.readByteArray(Math.min(n, 4096))); } catch (e) {}
      emit({ t: 'wire', dir: dir, fd: this.fd, len: n, hex: hex });
    }
  });
}
// connect: 记录连到游戏服(42.0.152.154:32231) 的 fd
try {
  const sockmod = Process.findModuleByName('libsocket.so');
  const cp = (sockmod || libc).getExportByName('connect');
  Interceptor.attach(cp, {
    onEnter(args) {
      const fd = args[0].toInt32();
      try {
        const fam = args[1].readU16();
        const port = (args[1].add(2).readU8() << 8) | args[1].add(3).readU8();
        if (fam === 2) {
          const b = [0,1,2,3].map(i => args[1].add(4+i).readU8()).join('.');
          emit({ t: 'connect', fd: fd, ip: b, port: port });
          if (port === 32231) TARGET_FD = fd;
        }
      } catch (e) {}
    }
  });
  emit({ t: 'hooked', name: 'connect' });
} catch (e) {}

hookLib('write', 'write');
hookLib('send', 'send');
hookLib('read', 'read');
hookLib('recv', 'recv');

emit({ t: 'script_loaded', pid: Process.id });
