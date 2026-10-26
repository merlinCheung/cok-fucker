'use strict';
/*
 * 只盯游戏服 socket (默认 fd 212 -> 42.0.152.154:32231) 的收发字节。
 * 目的: 判断线上 SFS 载荷是否已加密 —— 明文应以 4 字节包头 + SFS 类型标签(0x00..0x14) 开头。
 */
let TARGET_FD = 212;
let cap = 0;
const MAXCAP = 400;

function hexOf(buf) {
  const u8 = new Uint8Array(buf);
  let s = '';
  for (let i = 0; i < u8.length; i++) s += ('0' + u8[i].toString(16)).slice(-2);
  return s;
}
function hexAt(p, n) {
  try { if (!p || p.isNull()) return null; return hexOf(p.readByteArray(n)); } catch (e) { return null; }
}
function asciiAt(p, n) {
  try {
    if (!p || p.isNull()) return null;
    const u8 = new Uint8Array(p.readByteArray(n));
    let s = '';
    for (let i = 0; i < u8.length; i++) { const c = u8[i]; s += (c >= 0x20 && c < 0x7f) ? String.fromCharCode(c) : '.'; }
    return s;
  } catch (e) { return null; }
}
function emit(o) { try { send(o); } catch (e) {} }

function dump(dir, fd, buf, len) {
  if (fd !== TARGET_FD) return;
  if (cap >= MAXCAP) return;
  cap++;
  const n = Math.min(len, 128);
  emit({
    t: dir, fd: fd, len: len,
    hex: hexAt(buf, n),
    ascii: asciiAt(buf, n),
    head4: hexAt(buf, 4),
    tag: (function () { try { return buf.readU8(); } catch (e) { return null; } })()
  });
}

const libc = Process.getModuleByName('libc.so');

function hook(name, handlers) {
  let p = null;
  try { p = libc.getExportByName(name); } catch (e) { p = null; }
  if (!p) { emit({ t: 'hook_miss', name: name }); return; }
  try { Interceptor.attach(p, handlers); emit({ t: 'hooked', name: name, addr: p.toString() }); }
  catch (e) { emit({ t: 'hook_err', name: name, msg: String(e) }); }
}

hook('send', {
  onEnter(args) { this.fd = args[0].toInt32(); this.buf = args[1]; this.len = args[2].toInt32(); },
  onLeave() { dump('send', this.fd, this.buf, this.len); }
});
hook('sendto', {
  onEnter(args) { this.fd = args[0].toInt32(); this.buf = args[1]; this.len = args[2].toInt32(); },
  onLeave() { dump('sendto', this.fd, this.buf, this.len); }
});
hook('sendmsg', {
  onEnter(args) { this.fd = args[0].toInt32(); this.msg = args[1]; },
  onLeave() {
    try {
      const iov = this.msg.add(0x10).readPointer();      // struct msghdr.msg_iov
      const iovcnt = this.msg.add(0x18).readU32();      // struct msghdr.msg_iovlen
      if (iovcnt > 0) {
        const base = iov.readPointer();
        dump('sendmsg', this.fd, base, base.add(8).readU32());
      }
    } catch (e) {}
  }
});
hook('write', {
  onEnter(args) { this.fd = args[0].toInt32(); this.buf = args[1]; this.len = args[2].toInt32(); },
  onLeave() { dump('write', this.fd, this.buf, this.len); }
});
hook('writev', {
  onEnter(args) {
    this.fd = args[0].toInt32();
    this.iov = args[1]; this.cnt = args[2].toInt32();
  },
  onLeave() {
    try {
      if (this.cnt > 0) {
        const base = this.iov.readPointer();
        dump('writev', this.fd, base, base.add(8).readU32());
      }
    } catch (e) {}
  }
});
hook('recv', {
  onEnter(args) { this.fd = args[0].toInt32(); this.buf = args[1]; },
  onLeave(ret) { const n = ret.toInt32(); if (n > 0) dump('recv', this.fd, this.buf, n); }
});
hook('recvfrom', {
  onEnter(args) { this.fd = args[0].toInt32(); this.buf = args[1]; },
  onLeave(ret) { const n = ret.toInt32(); if (n > 0) dump('recvfrom', this.fd, this.buf, n); }
});
hook('read', {
  onEnter(args) { this.fd = args[0].toInt32(); this.buf = args[1]; },
  onLeave(ret) { const n = ret.toInt32(); if (n > 0) dump('read', this.fd, this.buf, n); }
});
hook('readv', {
  onEnter(args) { this.fd = args[0].toInt32(); this.iov = args[1]; this.cnt = args[2].toInt32(); },
  onLeave(ret) {
    const n = ret.toInt32();
    try { if (n > 0 && this.cnt > 0) { const base = this.iov.readPointer(); dump('readv', this.fd, base, Math.min(n, base.add(8).readU32())); } } catch (e) {}
  }
});

rpc.exports = {
  setfd: function (fd) { TARGET_FD = fd; emit({ t: 'target_fd', fd: fd }); }
};

emit({ t: 'script_loaded', pid: Process.id, target_fd: TARGET_FD });
