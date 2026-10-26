'use strict';
/*
 * 合并探针: 设备版 native MD5 全量追踪 + 登录请求构造器入口 + 游戏服线路字节。
 * 目的: 在登录发生的那一刻, 抓到 signCode/buildCode/SecurityCode/cc 的 md5 输入。
 *
 * 设备版 runtime 偏移 = 分析版 Ghidra 地址 - 0x100000
 *   MD5_Init   FUN_017a99e0 -> 0x16a99e0
 *   MD5_Update FUN_017aa548 -> 0x16aa548
 *   MD5_Final  FUN_017aadec -> 0x16aadec
 *   登录请求构造器 FUN_00c2ee8c -> 0xb2ee8c
 */
const OFF = {
  MD5_INIT: 0x16a99e0,
  MD5_UPDATE: 0x16aa548,
  MD5_FINAL: 0x16aadec,
  LOGIN_BUILD: 0xb2ee8c,
};

function emit(o) { try { send(o); } catch (e) {} }
function hexOf(buf) {
  const u8 = new Uint8Array(buf);
  let s = '';
  for (let i = 0; i < u8.length; i++) s += ('0' + u8[i].toString(16)).slice(-2);
  return s;
}
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

function hookWire() {
  const libc = Process.findModuleByName('libc.so');
  if (!libc) return;
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
}

Process.attachModuleObserver({
  onAdded(module) {
    if (module.name !== 'libgame.so') return;
    setTimeout(function () {
      BASE = module.base;
      emit({ t: 'base', v: BASE.toString() });
      hookWire();

      function hook(off, tag, handlers) {
        const p = BASE.add(off);
        try { Interceptor.attach(p, handlers); emit({ t: 'hooked', name: tag, addr: p.toString() }); }
        catch (e) { emit({ t: 'hook_err', name: tag, msg: String(e) }); }
      }

      hook(OFF.MD5_INIT, 'md5_init', { onEnter(args) { emit({ t: 'md5_init', ctx: args[0].toString() }); } });

      hook(OFF.MD5_UPDATE, 'md5_update', {
        onEnter(args) {
          const ptr = args[1];
          const len = args[2].toInt32();
          let hex = null, txt = null;
          try {
            if (len > 0 && len < 4096) {
              hex = hexOf(ptr.readByteArray(len));
              txt = ptr.readUtf8String(len);
            }
          } catch (e) {}
          emit({ t: 'md5_update', len: len, text: txt, hex: hex });
        }
      });

      hook(OFF.MD5_FINAL, 'md5_final', {
        onEnter(args) { this.outp = args[0]; },
        onLeave() {
          const s = readStdString(this.outp);
          let out = s ? s.text : null;
          if (out === null) {
            try {
              const dp = this.outp.readPointer();
              out = dp.readUtf8String(32);
            } catch (e) {}
          }
          emit({ t: 'md5_final', out: out });
        }
      });

      hook(OFF.LOGIN_BUILD, 'login_build', {
        onEnter() { emit({ t: 'login_build_enter' }); }
      });
    }, 300);
  }
});

emit({ t: 'script_loaded', pid: Process.id });
