'use strict';
/*
 * COK 客户端**收发双向**的命令名追踪 (2026-11-10)。
 *
 * 命令名在 SFS 外层封装里是明文, 所以直接 hook socket 的 send/write/read/recv 即可。
 * 关键用途: 找出「客户端登录时额外收到的命令」—— PC 端只收到 init + push.server.action,
 * 客户端却拿到了完整背包, 所以必有一个我们没收到的响应带着道具。
 */
const seen = new Set();
let emitted = 0;
const MAX_EVENTS = 400;

function emit(value) {
  try { send(value); } catch (_) {}
}

function dottedCommands(buf, length) {
  const bytes = new Uint8Array(buf.readByteArray(Math.min(length, 8192)));
  let text = '';
  for (let i = 0; i < bytes.length; i++) {
    const ch = bytes[i];
    text += ch >= 0x20 && ch < 0x7f ? String.fromCharCode(ch) : ' ';
  }
  const matches = text.match(/[a-z][a-z0-9_]*(?:\.[a-z0-9_]+)+/g) || [];
  const out = [];
  for (const cmd of matches) {
    if (cmd.length > 80) continue;
    // 去掉域名之类的前缀: 保留所有 "x.y" 和 "x.y.z" 后缀组合
    const parts = cmd.split('.');
    for (let i = 0; i < parts.length - 1; i++) {
      const s2 = parts[i] + '.' + parts[i + 1];
      if (!out.includes(s2)) out.push(s2);
      if (parts.length - i >= 3) {
        const s3 = s2 + '.' + parts[i + 2];
        if (!out.includes(s3)) out.push(s3);
      }
    }
  }
  return out;
}

function inspect(direction, fd, buf, length) {
  if (emitted >= MAX_EVENTS || length <= 0 || length > 1024 * 1024) return;
  let commands = [];
  try { commands = dottedCommands(buf, length); } catch (_) { return; }
  commands.forEach(function (cmd) {
    if (/(^|\.)com$/.test(cmd) || cmd.indexOf('.com.') >= 0 || cmd.indexOf('.net') >= 0 ||
        cmd.indexOf('.org') >= 0 || cmd.indexOf('.io') >= 0 || cmd.indexOf('.cn') >= 0) return;
    const key = direction + ':' + cmd;
    if (seen.has(key) || emitted >= MAX_EVENTS) return;
    seen.add(key);
    emitted++;
    emit({ t: 'game_command', direction: direction, fd: fd, cmd: cmd, bytes: length });
  });
}

const libc = Process.getModuleByName('libc.so');
['send', 'write'].forEach(function (name) {
  const address = libc.findExportByName(name);
  if (!address) return;
  Interceptor.attach(address, {
    onEnter(args) {
      this.fd = args[0].toInt32();
      this.buf = args[1];
      this.length = args[2].toInt32();
    },
    onLeave(retval) {
      if (retval.toInt32() > 0) inspect('send', this.fd, this.buf, this.length);
    }
  });
});

['recv', 'read'].forEach(function (name) {
  const address = libc.findExportByName(name);
  if (!address) return;
  Interceptor.attach(address, {
    onEnter(args) {
      this.fd = args[0].toInt32();
      this.buf = args[1];
      this.length = args[2].toInt32();
    },
    onLeave(retval) {
      const n = retval.toInt32();
      if (n > 0) inspect('recv', this.fd, this.buf, n);
    }
  });
});
emit({ t: 'trace_ready', pid: Process.id });
