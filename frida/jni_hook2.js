'use strict';
/*
 * nativeDataR 全链捕获:
 *   - JNI 探针: 读 GetVersion 校准函数表基址
 *   - nativeDataR: 入参(byte[] 密文 + int keyId) / 返回值(byte[] 明文)
 *   - XOR 引擎: 每次调用的密钥字符串
 */
function hexOf(buf) {
  const u8 = new Uint8Array(buf);
  let s = '';
  for (let i = 0; i < u8.length; i++) s += ('0' + u8[i].toString(16)).slice(-2);
  return s;
}
function emit(o) { try { send(o); } catch (e) {} }

const JNI = { getVersion: 4, getArrayLength: 216, getByteArrayElements: 226, releaseByteArrayElements: 227 };

function jbytes(env, arr) {
  try {
    const table = env.readPointer();
    const ver = new NativeFunction(table.add(JNI.getVersion * 8).readPointer(), 'int', ['pointer'])();
    const getLen = new NativeFunction(table.add(JNI.getArrayLength * 8).readPointer(), 'int', ['pointer', 'pointer']);
    const getElems = new NativeFunction(table.add(JNI.getByteArrayElements * 8).readPointer(), 'pointer', ['pointer', 'pointer', 'pointer']);
    const len = getLen(env, arr);
    if (len <= 0 || len > (1 << 20)) return { len: len, hex: null, ver: ver };
    const p = getElems(env, arr, ptr(0));
    if (p.isNull()) return { len: len, hex: null, ver: ver };
    const out = hexOf(p.readByteArray(len));
    try {
      const rel = new NativeFunction(table.add(JNI.releaseByteArrayElements * 8).readPointer(), 'void', ['pointer', 'pointer', 'pointer', 'int']);
      rel(env, arr, p, 0);
    } catch (e) {}
    return { len: len, hex: out, ver: ver };
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

      hook(0x18b91dc, 'jni_nativeDataR', {
        onEnter(args) {
          this.env = args[0];
          const r = jbytes(args[0], args[2]);
          emit({ t: 'R_in', id: args[3].toInt32(), len: r.len, hex: r.hex, ver: r.ver, err: r.err });
        },
        onLeave(ret) {
          const r = jbytes(this.env, ret);
          emit({ t: 'R_out', len: r.len, hex: r.hex, err: r.err });
        }
      });

      hook(0x9e02b8, 'xor_engine', {
        onEnter(args) {
          this.len = args[1].toInt32();
          this.buf = args[0];
          this.off = args[3].toInt32();
          this.key = null;
          try {
            const dp = args[2].readPointer();
            const klen = dp.sub(0x18).readU32();
            if (klen > 0 && klen < 4096) this.key = dp.readUtf8String(klen);
          } catch (e) {}
          let plain = null;
          try { plain = hexOf(args[0].add(this.off).readByteArray(Math.min(this.len, 4096))); } catch (e) {}
          this.plain = plain;
        },
        onLeave() {
          let cipher = null;
          try { cipher = hexOf(this.buf.add(this.off).readByteArray(Math.min(this.len, 4096))); } catch (e) {}
          emit({ t: 'xor_pair', len: this.len, key: this.key, plain_hex: this.plain, cipher_hex: cipher });
        }
      });
    }, 300);
  }
});

emit({ t: 'script_loaded', pid: Process.id });
