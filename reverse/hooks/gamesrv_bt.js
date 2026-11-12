'use strict';
/*
 * fd 212 = 游戏服 TCP (42.0.152.154:32231)
 * 抓完整载荷 + 调用回溯, 定位真正实现协议发送的 native 函数。
 */
let TARGET_FD = 212;
let cap = 0;
const MAXCAP = 80;
const MAXLEN = 4096;

function hexOf(buf) {
  const u8 = new Uint8Array(buf);
  let s = '';
  for (let i = 0; i < u8.length; i++) s += ('0' + u8[i].toString(16)).slice(-2);
  return s;
}
function emit(o) { try { send(o); } catch (e) {} }

function bt(ctx) {
  try {
    return Thread.backtrace(ctx, Backtracer.ACCURATE).slice(0, 10).map(DebugSymbol.fromAddress).map(String);
  } catch (e) { return null; }
}

const libc = Process.getModuleByName('libc.so');
function hook(name, handlers) {
  let p = null;
  try { p = libc.getExportByName(name); } catch (e) { p = null; }
  if (!p) { emit({ t: 'hook_miss', name: name }); return; }
  try { Interceptor.attach(p, handlers); emit({ t: 'hooked', name: name }); }
  catch (e) { emit({ t: 'hook_err', name: name, msg: String(e) }); }
}

function capture(dir, fd, buf, len, ctx) {
  if (fd !== TARGET_FD) return;
  if (cap >= MAXCAP) return;
  cap++;
  let hex = null;
  try { hex = hexOf(buf.readByteArray(Math.min(len, MAXLEN))); } catch (e) {}
  emit({ t: dir, fd: fd, len: len, hex: hex, bt: bt(ctx) });
}

hook('write', {
  onEnter(args) { this.fd = args[0].toInt32(); this.buf = args[1]; this.len = args[2].toInt32(); this.ctx = this.context; },
  onLeave() { capture('write', this.fd, this.buf, this.len, this.ctx); }
});
hook('send', {
  onEnter(args) { this.fd = args[0].toInt32(); this.buf = args[1]; this.len = args[2].toInt32(); this.ctx = this.context; },
  onLeave() { capture('send', this.fd, this.buf, this.len, this.ctx); }
});
hook('read', {
  onEnter(args) { this.fd = args[0].toInt32(); this.buf = args[1]; this.ctx = this.context; },
  onLeave(ret) { const n = ret.toInt32(); if (n > 0) capture('read', this.fd, this.buf, n, this.ctx); }
});
hook('recv', {
  onEnter(args) { this.fd = args[0].toInt32(); this.buf = args[1]; this.ctx = this.context; },
  onLeave(ret) { const n = ret.toInt32(); if (n > 0) capture('recv', this.fd, this.buf, n, this.ctx); }
});

rpc.exports = {
  setfd: function (fd) { TARGET_FD = fd; emit({ t: 'target_fd', fd: fd }); }
};
emit({ t: 'script_loaded', pid: Process.id, target_fd: TARGET_FD });
