'use strict';
/* 抓 App 实际 connect 的所有 (ip, port)，用于确认游戏服当前节点。 */
function emit(o) { try { send(o); } catch (e) {} }
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
        emit({ t: 'connect', fd: args[0].toInt32(), ip: ip, port: port });
      } catch (e) {}
    }
  });
}
hookLib('connect');
emit({ t: 'script_loaded', pid: Process.id });
