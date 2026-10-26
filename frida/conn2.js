'use strict';
/*
 * 关联游戏服连接: hook connect 记录 (fd, ip, port)，
 * 同时 hook write/read 记录哪个 fd 在传 SFS 帧。
 * 两者一关联即可确定"游戏服当前节点的 IP:port"。
 */
function emit(o) { try { send(o); } catch (e) {} }
function hexOf(buf) {
  const u8 = new Uint8Array(buf);
  let s = '';
  for (let i = 0; i < u8.length; i++) s += ('0' + u8[i].toString(16)).slice(-2);
  return s;
}
const fdInfo = {};   // fd -> {ip, port}

function hookLib(name) {
  let p = null;
  try { p = Process.getModuleByName('libc.so').getExportByName(name); } catch (e) { return; }
  Interceptor.attach(p, {
    onEnter(args) {
      try {
        const fam = args[1].readU16();
        if (fam !== 2) return;
        const port = (args[1].add(2).readU8() << 8) | args[1].add(3).readU8();
        const ip = [0, 1, 2, 3].map(i => args[1].add(4 + i).readU8()).join('.');
        const fd = args[0].toInt32();
        fdInfo[fd] = { ip: ip, port: port };
        emit({ t: 'connect', fd: fd, ip: ip, port: port });
      } catch (e) {}
    }
  });
}
hookLib('connect');

// write/read: 只在首字节 0x80(大端 SFS 帧)时记录
function hookIo(name, dir) {
  let p = null;
  try { p = Process.getModuleByName('libc.so').getExportByName(name); } catch (e) { return; }
  Interceptor.attach(p, {
    onEnter(args) { this.fd = args[0].toInt32(); this.buf = args[1]; this.len = args[2].toInt32(); },
    onLeave(ret) {
      const n = dir === 'read' ? ret.toInt32() : this.len;
      if (n < 4 || n > 262144) return;
      let b0 = 0;
      try { b0 = this.buf.readU8(); } catch (e) { return; }
      if (b0 !== 0x80) return;
      let hex = null;
      try { hex = hexOf(this.buf.readByteArray(Math.min(n, 32))); } catch (e) {}
      const info = fdInfo[this.fd] || {};
      emit({ t: 'sfs_io', dir: dir, fd: this.fd, len: n, ip: info.ip || null,
             port: info.port || null, head: hex });
    }
  });
}
hookIo('write', 'out');
hookIo('send', 'out');
hookIo('read', 'in');
hookIo('recv', 'in');

emit({ t: 'script_loaded', pid: Process.id });
