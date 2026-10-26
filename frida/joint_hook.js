'use strict';
/*
 * 同会话联合抓取:
 *   - 所有 fd 的 write/read 原始字节 (事后筛 SFS 帧)
 *   - XOR 引擎实际使用的密钥
 *   - 配置 map 的插入 (id / value / 回溯)
 * 目的: 在解码后的服务器响应里直接搜出"下发密钥的那条命令"。
 */
function hexOf(buf) {
  const u8 = new Uint8Array(buf);
  let s = '';
  for (let i = 0; i < u8.length; i++) s += ('0' + u8[i].toString(16)).slice(-2);
  return s;
}
function emit(o) { try { send(o); } catch (e) {} }

function readStdStringOld(p) {
  try {
    const dp = p.readPointer();
    const len = dp.sub(0x18).readU32();
    if (len === 0 || len > 4096) return { len: len, text: null };
    return { len: len, text: dp.readUtf8String(len) };
  } catch (e) { return null; }
}

const libc = Process.getModuleByName('libc.so');
function hookLib(name, dir) {
  let p = null;
  try { p = libc.getExportByName(name); } catch (e) { return; }
  Interceptor.attach(p, {
    onEnter(args) { this.fd = args[0].toInt32(); this.buf = args[1]; this.len = args[2].toInt32(); },
    onLeave(ret) {
      const n = dir === 'read' ? ret.toInt32() : this.len;
      if (n <= 0 || n > 65536) return;
      let hex = null;
      try { hex = hexOf(this.buf.readByteArray(n)); } catch (e) {}
      emit({ t: 'wire', dir: dir, fd: this.fd, len: n, hex: hex });
    }
  });
}
hookLib('write', 'write');
hookLib('read', 'read');

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

      // map<int,string> 插入
      hook(0xa262c8, 'map_insert', {
        onEnter(args) {
          const pair = args[2];
          let id = null, val = null;
          try {
            id = pair.readS32();
            const sp = pair.add(8).readPointer();
            const s = readStdStringOld(sp);
            val = s ? s.text : null;
            if (val === null) {
              // 备选: 新 ABI, 长度在对象 +8
              const len2 = pair.add(16).readU32();
              if (len2 > 0 && len2 < 4096) val = sp.readUtf8String(len2);
            }
          } catch (e) {}
          let bt = null;
          try {
            bt = Thread.backtrace(this.context, Backtracer.ACCURATE).slice(0, 6)
                    .map(DebugSymbol.fromAddress).map(String);
          } catch (e) {}
          emit({ t: 'map_insert', id: id, value: val, bt: bt });
        }
      });
    }, 300);
  }
});

emit({ t: 'script_loaded', pid: Process.id });
