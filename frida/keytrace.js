'use strict';
/*
 * 定位会话密钥的下发通道:
 *   hook map<int,string> 的 _M_get_insert_hint_unique_pos (vaddr 0x0a262c8)
 *   -> 打印新插入的 id / value / 调用回溯
 * 同时 hook XOR 引擎 (0x9e02b8) 记录实际用到的密钥。
 */
function hexOf(buf) {
  const u8 = new Uint8Array(buf);
  let s = '';
  for (let i = 0; i < u8.length; i++) s += ('0' + u8[i].toString(16)).slice(-2);
  return s;
}
function emit(o) { try { send(o); } catch (e) {} }

function readStdStringOld(p) {
  // 老 libstdc++: _M_p 指向数据, 长度在 p-0x18
  try {
    const dp = p.readPointer();
    const len = dp.sub(0x18).readU32();
    if (len === 0 || len > 4096) return { len: len, text: null };
    return { len: len, text: dp.readUtf8String(len) };
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

      // map<int,string>::_M_get_insert_hint_unique_pos(this, hint, pair*)
      hook(0xa262c8, 'map_insert', {
        onEnter(args) {
          const pair = args[2];
          let id = null, val = null, raw = null;
          try {
            id = pair.readS32();
            raw = hexOf(pair.readByteArray(40));
            const s = readStdStringOld(pair.add(8).readPointer());
            val = s ? s.text : null;
          } catch (e) { raw = 'err:' + e; }
          let bt = null;
          try {
            bt = Thread.backtrace(this.context, Backtracer.ACCURATE).slice(0, 10)
                    .map(DebugSymbol.fromAddress).map(String);
          } catch (e) {}
          emit({ t: 'map_insert', id: id, value: val, raw: raw, bt: bt });
        }
      });

      // XOR 引擎: 实际用到的密钥
      hook(0x9e02b8, 'xor_engine', {
        onEnter(args) {
          this.len = args[1].toInt32();
          this.key = null;
          try {
            const dp = args[2].readPointer();
            const klen = dp.sub(0x18).readU32();
            if (klen > 0 && klen < 4096) this.key = dp.readUtf8String(klen);
          } catch (e) {}
          emit({ t: 'xor_use', len: this.len, key: this.key });
        }
      });
    }, 300);
  }
});

emit({ t: 'script_loaded', pid: Process.id });
