'use strict';
/*
 * socket 层抓包: 不依赖 SFS 符号, 直接看游戏进程往网络上写了什么。
 * 用途: 判定游戏服连接目标 + 线上字节是否已加密 + 协议形态。
 */
let cap = 0;
const MAXCAP = 600;
const seen = new Set();

function hexOf(buf) {
  const u8 = new Uint8Array(buf);
  let s = '';
  for (let i = 0; i < u8.length; i++) s += ('0' + u8[i].toString(16)).slice(-2);
  return s;
}

function hexAt(p, n) {
  try {
    if (!p || p.isNull()) return null;
    return hexOf(p.readByteArray(n));
  } catch (e) { return null; }
}

function asciiAt(p, n) {
  try {
    if (!p || p.isNull()) return null;
    const u8 = new Uint8Array(p.readByteArray(n));
    let s = '';
    for (let i = 0; i < u8.length; i++) {
      const c = u8[i];
      s += (c >= 0x20 && c < 0x7f) ? String.fromCharCode(c) : '.';
    }
    return s;
  } catch (e) { return null; }
}

function sockaddrInfo(p) {
  try {
    const family = p.readU16();
    const port = (p.add(2).readU8() << 8) | p.add(3).readU8();
    if (family === 2) {
      const b = [0, 1, 2, 3].map(function (i) { return p.add(4 + i).readU8(); });
      return { family: 'AF_INET', ip: b.join('.'), port: port };
    }
    if (family === 10) {
      let s = '';
      for (let i = 0; i < 16; i += 2) {
        const w = p.add(8 + i).readU16();
        s += (((w >> 8) & 0xff).toString(16) + (w & 0xff).toString(16)) + (i < 14 ? ':' : '');
      }
      return { family: 'AF_INET6', ip: s, port: port };
    }
    return { family: 'family=' + family, port: port };
  } catch (e) { return null; }
}

function emit(o) { try { send(o); } catch (e) {} }

function hook(mod, name, handlers) {
  let p = null;
  try { p = mod.getExportByName(name); } catch (e) { p = null; }
  if (!p) { emit({ t: 'hook_miss', name: name, mod: mod.name }); return; }
  try { Interceptor.attach(p, handlers); emit({ t: 'hooked', name: name, mod: mod.name, addr: p.toString() }); }
  catch (e) { emit({ t: 'hook_err', name: name, msg: String(e) }); }
}

const libc = Process.getModuleByName('libc.so');

hook(libc, 'connect', {
  onEnter(args) {
    emit({
      t: 'connect', fd: args[0].toInt32(),
      peer: sockaddrInfo(args[1])
    });
  }
});

hook(libc, 'send', {
  onEnter(args) {
    this.fd = args[0].toInt32();
    this.len = args[2].toInt32();
    this.buf = args[1];
  },
  onLeave(ret) {
    if (cap >= MAXCAP) return;
    cap++;
    emit({
      t: 'send', fd: this.fd, len: this.len, ret: ret.toInt32(),
      hex: hexAt(this.buf, Math.min(this.len, 96)),
      ascii: asciiAt(this.buf, Math.min(this.len, 96))
    });
  }
});

hook(libc, 'sendto', {
  onEnter(args) {
    this.fd = args[0].toInt32();
    this.len = args[2].toInt32();
    this.buf = args[1];
    this.peer = sockaddrInfo(args[5]);
  },
  onLeave(ret) {
    if (cap >= MAXCAP) return;
    cap++;
    emit({
      t: 'sendto', fd: this.fd, len: this.len, ret: ret.toInt32(), peer: this.peer,
      hex: hexAt(this.buf, Math.min(this.len, 96)),
      ascii: asciiAt(this.buf, Math.min(this.len, 96))
    });
  }
});

hook(libc, 'recv', {
  onEnter(args) {
    this.fd = args[0].toInt32();
    this.buf = args[1];
  },
  onLeave(ret) {
    const n = ret.toInt32();
    if (n <= 0 || cap >= MAXCAP) return;
    cap++;
    emit({
      t: 'recv', fd: this.fd, len: n,
      hex: hexAt(this.buf, Math.min(n, 96)),
      ascii: asciiAt(this.buf, Math.min(n, 96))
    });
  }
});

hook(libc, 'recvfrom', {
  onEnter(args) {
    this.fd = args[0].toInt32();
    this.buf = args[1];
  },
  onLeave(ret) {
    const n = ret.toInt32();
    if (n <= 0 || cap >= MAXCAP) return;
    cap++;
    emit({
      t: 'recvfrom', fd: this.fd, len: n,
      hex: hexAt(this.buf, Math.min(n, 96)),
      ascii: asciiAt(this.buf, Math.min(n, 96))
    });
  }
});

// 记录非本机(非 loopback)连接的 fd,便于区分游戏服与其他流量
const remoteFds = new Set();
emit({ t: 'script_loaded', pid: Process.id });
