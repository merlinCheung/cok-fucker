'use strict';
/*
 * 直接在传输 SFS 帧的 socket 上调用 getpeername, 拿到游戏服真实 IP:port。
 * (libcore 用 syscall 直连, hook libc connect 抓不到)
 */
function emit(o) { try { send(o); } catch (e) {} }
function hexOf(buf) {
  const u8 = new Uint8Array(buf);
  let s = '';
  for (let i = 0; i < u8.length; i++) s += ('0' + u8[i].toString(16)).slice(-2);
  return s;
}

const libc = Process.getModuleByName('libc.so');
const getpeername = new NativeFunction(libc.getExportByName('getpeername'), 'int', ['int', 'pointer', 'pointer']);
const done = {};

function peerOf(fd) {
  if (done[fd]) return done[fd];
  const buf = Memory.alloc(128);
  const lenp = Memory.alloc(8);
  lenp.writeU32(128);
  let res = null;
  try {
    if (getpeername(fd, buf, lenp) === 0) {
      const port = (buf.add(2).readU8() << 8) | buf.add(3).readU8();
      const ip = [0, 1, 2, 3].map(i => buf.add(4 + i).readU8()).join('.');
      res = { ip: ip, port: port };
    }
  } catch (e) { res = { err: String(e) }; }
  done[fd] = res;
  return res;
}

function hookIo(name, dir) {
  let p = null;
  try { p = libc.getExportByName(name); } catch (e) { return; }
  Interceptor.attach(p, {
    onEnter(args) { this.fd = args[0].toInt32(); this.buf = args[1]; this.len = args[2].toInt32(); },
    onLeave(ret) {
      const n = dir === 'read' ? ret.toInt32() : this.len;
      if (n < 4 || n > 262144) return;
      let b0 = 0;
      try { b0 = this.buf.readU8(); } catch (e) { return; }
      if (b0 !== 0x80) return;
      let head = null;
      try { head = hexOf(this.buf.readByteArray(Math.min(n, 24))); } catch (e) {}
      const peer = peerOf(this.fd);
      emit({ t: 'sfs_io', dir: dir, fd: this.fd, len: n, peer: peer, head: head });
    }
  });
}
hookIo('write', 'out');
hookIo('send', 'out');
hookIo('read', 'in');
hookIo('recv', 'in');

emit({ t: 'script_loaded', pid: Process.id });
