'use strict';
/*
 * 直接 hook JNI 入口, 用 JNI 读出 byte[] 与 int:
 *   Java_org_cocos2dx_ext_Native_nativeData   (nm 0x18b8f7c -> base+0x18b8f7c)
 *   Java_org_cocos2dx_ext_Native_nativeDataR  (nm 0x18b91dc -> base+0x18b91dc)
 * JNI 函数表偏移: GetArrayLength=idx216->0x6C0, GetByteArrayElements=idx226->0x710,
 *                   ReleaseByteArrayElements=idx227->0x718
 */
function hexOf(buf) {
  const u8 = new Uint8Array(buf);
  let s = '';
  for (let i = 0; i < u8.length; i++) s += ('0' + u8[i].toString(16)).slice(-2);
  return s;
}
function emit(o) { try { send(o); } catch (e) {} }

function jbytes(env, arr) {
  try {
    const table = env.readPointer();
    const getLen = new NativeFunction(table.add(0x6C0).readPointer(), 'int', ['pointer', 'pointer']);
    const getElems = new NativeFunction(table.add(0x710).readPointer(), 'pointer', ['pointer', 'pointer', 'pointer']);
    const len = getLen(env, arr);
    if (len <= 0 || len > (1 << 20)) return { len: len, hex: null };
    const p = getElems(env, arr, ptr(0));
    if (p.isNull()) return { len: len, hex: null };
    const out = hexOf(p.readByteArray(len));
    const release = new NativeFunction(table.add(0x718).readPointer(), 'void', ['pointer', 'pointer', 'pointer', 'int']);
    release(env, arr, p, 0);
    return { len: len, hex: out };
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

      // nativeData(JNIEnv*, jclass, jbyteArray)
      hook(0x18b8f7c, 'jni_nativeData', {
        onEnter(args) {
          const r = jbytes(args[0], args[2]);
          emit({ t: 'jni_nativeData_in', len: r.len, hex: r.hex, err: r.err });
        },
        onLeave(ret) {
          const r = jbytes(args[0], ret);
          emit({ t: 'jni_nativeData_out', len: r.len, hex: r.hex, err: r.err });
        }
      });

      // nativeDataR(JNIEnv*, jclass, jbyteArray, int id)
      hook(0x18b91dc, 'jni_nativeDataR', {
        onEnter(args) {
          this.env = args[0];
          const r = jbytes(args[0], args[2]);
          emit({ t: 'jni_nativeDataR_in', id: args[3].toInt32(), len: r.len, hex: r.hex, err: r.err });
        },
        onLeave(ret) {
          const r = jbytes(this.env, ret);
          emit({ t: 'jni_nativeDataR_out', len: r.len, hex: r.hex, err: r.err });
        }
      });
    }, 300);
  }
});

emit({ t: 'script_loaded', pid: Process.id });
