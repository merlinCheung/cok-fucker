'use strict';
/*
 * 追踪 native MD5 的每次 Update 输入与 Final 输出, 用于还原
 * signCode / buildCode / SecurityCode / cc 四个登录参数的生成算法。
 *
 * 设备版偏移(按字节特征在 libgame.so 中定位):
 *   MD5_Init   = base+0x16a99e0
 *   MD5_Update = base+0x16aa548   (ctx, data_ptr, len)
 *   MD5_Final  = base+0x16aadec   (out_string*, ctx)  -> 32 字符小写 hex
 */
const OFF = {
  MD5_INIT: 0x16a99e0,
  MD5_UPDATE: 0x16aa548,
  MD5_FINAL: 0x16aadec,
};

function emit(o) { try { send(o); } catch (e) {} }
function hexOf(buf) {
  const u8 = new Uint8Array(buf);
  let s = '';
  for (let i = 0; i < u8.length; i++) s += ('0' + u8[i].toString(16)).slice(-2);
  return s;
}
// 老 libstdc++ COW std::string: data ptr 在 +0, 长度在 data-0x18
function readStdString(p) {
  try {
    if (!p || p.isNull()) return null;
    const dp = p.readPointer();
    if (dp.isNull()) return { len: 0, text: '' };
    let len = 0;
    try { len = p.add(8).readU32(); } catch (e) {}
    if (!(len > 0 && len < 4096)) {
      try { len = dp.sub(0x18).readU32(); } catch (e) { len = 0; }
    }
    if (!(len > 0 && len < 4096)) return { len: len, text: null };
    let base = dp;
    try { if (dp.equals(p.add(16))) base = p.add(16); } catch (e) {}
    return { len: len, text: base.readUtf8String(len) };
  } catch (e) { return { err: String(e) }; }
}

let BASE = null;
let seq = 0;

Process.attachModuleObserver({
  onAdded(module) {
    if (module.name !== 'libgame.so') return;
    setTimeout(function () {
      BASE = module.base;
      emit({ t: 'base', v: BASE.toString() });

      function hook(off, tag, handlers) {
        const p = BASE.add(off);
        try { Interceptor.attach(p, handlers); emit({ t: 'hooked', name: tag, addr: p.toString() }); }
        catch (e) { emit({ t: 'hook_err', name: tag, msg: String(e) }); }
      }

      hook(OFF.MD5_INIT, 'md5_init', {
        onEnter(args) { this.ctx = args[0].toString(); this.buf = []; }
      });

      hook(OFF.MD5_UPDATE, 'md5_update', {
        onEnter(args) {
          const ctx = args[0].toString();
          const ptr = args[1];
          const len = args[2].toInt32();
          let hex = null, txt = null;
          try {
            if (len > 0 && len < 4096) {
              hex = hexOf(ptr.readByteArray(len));
              txt = ptr.readUtf8String(len);
            }
          } catch (e) {}
          emit({ t: 'md5_update', ctx: ctx, len: len, text: txt, hex: hex });
        }
      });

      hook(OFF.MD5_FINAL, 'md5_final', {
        onEnter(args) { this.outp = args[0]; this.ctx = args[1].toString(); },
        onLeave() {
          const s = readStdString(this.outp);
          emit({ t: 'md5_final', ctx: this.ctx, out: s ? s.text : null });
        }
      });
    }, 300);
  }
});

emit({ t: 'script_loaded', pid: Process.id });
