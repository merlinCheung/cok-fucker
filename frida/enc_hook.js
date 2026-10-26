'use strict';
/*
 * 抓 COK 游戏服参数加密:
 *   FUN_00ae02b8(data, len, keyString*, flag)  -> 请求侧加密, data 是明文 params
 *   FUN_00eb7890(cfg, data, len, keyString*)   -> 另一条加密分支
 *   FUN_02d96ccc(data, len, &out)              -> 解密 (nativeDataR 用)
 *   BF_set_key(...)                            -> BlowFish 密钥
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
    if (len === 0 || len > 4096) return { len: len, text: null };
    const sso = dataPtr.equals(p.add(16));
    const base = sso ? p.add(16) : dataPtr;
    return { len: len, text: base.readUtf8String(len), sso: sso };
  } catch (e) { return null; }
}

Process.attachModuleObserver({
  onAdded(module) {
    if (module.name !== 'libgame.so') return;
    setTimeout(function () {
      const base = module.base;

      function hook(off, tag, handlers) {
        const p = base.add(off);
        try {
          Interceptor.attach(p, handlers);
          emit({ t: 'hooked', name: tag, addr: p.toString(), off: '0x' + off.toString(16) });
        } catch (e) { emit({ t: 'hook_err', name: tag, msg: String(e) }); }
      }

      // 加密分支 A: FUN_00ae02b8(data, len, keyStr*, 0)
      hook(0xae02b8, 'enc_A', {
        onEnter(args) {
          const len = args[1].toInt32();
          const key = readStdString(args[2]);
          let plain = null, ascii = null;
          try {
            const b = args[0].readByteArray(Math.min(len, 2048));
            plain = hexOf(b);
            const u8 = new Uint8Array(b);
            ascii = Array.from(u8).map(c => (c >= 0x20 && c < 0x7f) ? String.fromCharCode(c) : '.').join('');
          } catch (e) {}
          emit({ t: 'enc_plain', len: len, key: key ? key.text : null, key_len: key ? key.len : null, plain_hex: plain, plain_ascii: ascii });
        }
      });

      // 加密分支 B: FUN_00eb7890(cfg, data, len, keyStr*)
      hook(0xeb7890, 'enc_B', {
        onEnter(args) {
          const len = args[2].toInt32();
          const key = readStdString(args[3]);
          let plain = null;
          try { plain = hexOf(args[1].readByteArray(Math.min(len, 2048))); } catch (e) {}
          emit({ t: 'enc_plain_B', len: len, key: key ? key.text : null, plain_hex: plain });
        }
      });

      // 解密: FUN_02d96ccc(data, len, &out)
      hook(0x2d96ccc, 'dec', {
        onEnter(args) {
          this.len = args[1].toInt32();
          this.outp = args[2];
          let ct = null;
          try { ct = hexOf(args[0].readByteArray(Math.min(this.len, 2048))); } catch (e) {}
          emit({ t: 'dec_in', len: this.len, cipher_hex: ct });
        },
        onLeave(ret) {
          let pt = null;
          try {
            const p = this.outp.readPointer();
            const n = p.add(8).readU32();
            pt = hexOf(p.readByteArray(Math.min(n, 2048)));
          } catch (e) {}
          emit({ t: 'dec_out', plain_hex: pt });
        }
      });

      // BlowFish 密钥
      try {
        const bf = module.getExportByName('BF_set_key');
        if (bf) {
          Interceptor.attach(bf, {
            onEnter(args) {
              const len = args[1].toInt32();
              let hex = null;
              try { hex = hexOf(args[2].readByteArray(Math.min(len, 128))); } catch (e) {}
              emit({ t: 'bf_set_key', len: len, key_hex: hex });
            }
          });
          emit({ t: 'hooked', name: 'BF_set_key' });
        }
      } catch (e) {}
    }, 0);
  }
});

emit({ t: 'script_loaded', pid: Process.id });
