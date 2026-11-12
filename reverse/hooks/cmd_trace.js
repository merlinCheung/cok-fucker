'use strict';
/*
 * Privacy-safe COK startup tracer.
 *
 * The game command is plaintext in the outer SFS envelope, while account and
 * session fields live in other values.  Emit only dotted command identifiers
 * and byte counts, never packet bytes or arbitrary strings.
 */
const seen = new Set();
let emitted = 0;
const MAX_EVENTS = 160;

function emit(value) {
  try { send(value); } catch (_) {}
}

function dottedCommands(buf, length) {
  const bytes = new Uint8Array(buf.readByteArray(Math.min(length, 4096)));
  let text = '';
  for (let i = 0; i < bytes.length; i++) {
    const ch = bytes[i];
    text += ch >= 0x20 && ch < 0x7f ? String.fromCharCode(ch) : ' ';
  }
  const matches = text.match(/[a-z][a-z0-9_]*(?:\.[a-z0-9_]+)+/g) || [];
  return matches.filter(function (cmd) {
    return cmd.length <= 80 && !cmd.startsWith('com.');
  });
}

function inspect(direction, fd, buf, length) {
  if (emitted >= MAX_EVENTS || length <= 0 || length > 1024 * 1024) return;
  let commands = [];
  try { commands = dottedCommands(buf, length); } catch (_) { return; }
  commands.forEach(function (cmd) {
    const key = direction + ':' + fd + ':' + cmd;
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
emit({ t: 'trace_ready', pid: Process.id });
