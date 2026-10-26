'use strict';
/*
 * COK 会话密钥下发通道 · 最终取证探针
 *
 * 静态结论(libgame.so 反编译):
 *   响应 params 里的 "id" 字段 = "<前缀>_<密钥ID>"
 *     -> 密钥ID = atoi(下划线后的部分)
 *     -> XOR 密钥 = md5_hex(前缀)            32 位小写 hex
 *     -> 存入 map<int,string> (cfg+0x1a8), 节点 value 字符串在 node+0x28
 *     -> cfg+0x1d8 = 前缀
 *   nativeData  : 用全局当前 keyId 查表取密钥 -> XOR 请求
 *   nativeDataR : 用 Java 传入的 keyId 查表取密钥 -> XOR 响应
 *
 * 本探针抓:
 *   xor_use     : 每次 XOR 的 (密钥, 长度, 明文前 64 字节) —— 即每条请求/响应的明文
 *   key_id      : nativeDataR 的 keyId 参数(来自响应的 qqq)
 *   keymap      : 登录后 keymap 全量 (keyId -> md5hex)
 *   prefix      : cfg+0x1d8 的原始字节(= id 前缀)
 *   wire        : libc write/read 原始字节(离线重组 TCP 流)
 */
const OFF = {
  XOR: 0x9e02b8,          // FUN_00ae02b8  XOR 引擎
  NATIVE_DATA: 0x18b8f7c, // Java_..._nativeData   (请求侧)
  NATIVE_DATA_R: 0x18b91dc, // Java_..._nativeDataR (响应侧)
  MAP_INSERT: 0xa262c8,  // map<int,string>::_M_get_insert_hint_unique_pos
  CFG_PTR: 0x3b1a5f8,    // .bss: 指向 cfg 单例
  KEYID_PTR: 0x3ad4800,  // .bss: 指向当前 keyId
};

function emit(o) { try { send(o); } catch (e) {} }
function hexOf(buf) {
  const u8 = new Uint8Array(buf);
  let s = '';
  for (let i = 0; i < u8.length; i++) s += ('0' + u8[i].toString(16)).slice(-2);
  return s;
}
// libstdc++ 新 ABI std::string: {char* data@0, size_t size@8, char buf[16]@16}
// 兼容老 COW: 长度也可能在 data-0x18
function readStdString(p) {
  try {
    if (!p || p.isNull()) return null;
    const dataPtr = p.readPointer();
    if (dataPtr.isNull()) return { len: 0, text: '' };
    let len = 0, base = dataPtr;
    try { len = p.add(8).readU32(); } catch (e) {}
    if (len === 0 || len > 4096) {
      try { len = dataPtr.sub(0x18).readU32(); } catch (e) { len = 0; }
    }
    if (!(len > 0 && len < 4096)) return { len: len, text: null };
    try {
      if (dataPtr.equals(p.add(16))) base = p.add(16);
    } catch (e) {}
    return { len: len, text: base.readUtf8String(len) };
  } catch (e) { return { err: String(e) }; }
}

let BASE = null;
let cfgPtr = null;
let dumped = false;

function walkMap(mapAddr) {
  const out = [];
  try {
    // libstdc++ _Rb_tree: map+0x08 = header._M_parent(根), 节点: left@0x10 right@0x18 key@0x20 string@0x28
    const root = mapAddr.add(0x10).readPointer();
    const stack = [root]; const seen = new Set();
    while (stack.length) {
      const node = stack.pop();
      if (node.isNull()) continue;
      const k = node.toString();
      if (seen.has(k)) continue;
      seen.add(k);
      let key = null, val = null, raw = null;
      try {
        key = node.add(0x20).readS32();
        raw = hexOf(node.add(0x28).readByteArray(24));
        const s = readStdString(node.add(0x28));
        val = s ? s.text : null;
      } catch (e) { raw = 'err:' + e; }
      out.push({ key: key, value: val, raw: raw });
      try { stack.push(node.add(0x10).readPointer()); } catch (e) {}
      try { stack.push(node.add(0x18).readPointer()); } catch (e) {}
    }
    return out;
  } catch (e) { return [{ err: String(e) }]; }
}

function dumpKeyState(tag) {
  try {
    if (cfgPtr === null) {
      const p = BASE.add(OFF.CFG_PTR).readPointer();
      if (p.isNull()) { emit({ t: 'keymap', tag: tag, err: 'cfg singleton null' }); return; }
      cfgPtr = p;
    }
    const map = walkMap(cfgPtr.add(0x1a8));
    let prefix = null, prefixRaw = null, keyId = null;
    try { prefixRaw = hexOf(cfgPtr.add(0x1d8).readByteArray(24)); } catch (e) {}
    try { const s = readStdString(cfgPtr.add(0x1d8)); prefix = s ? s.text : null; } catch (e) {}
    try { keyId = BASE.add(OFF.KEYID_PTR).readPointer().readS32(); } catch (e) {}
    emit({ t: 'keymap', tag: tag, cfg: cfgPtr.toString(), current_key_id: keyId,
           prefix: prefix, prefix_raw: prefixRaw, map: map });
  } catch (e) { emit({ t: 'keymap', tag: tag, err: String(e) }); }
}

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

      // XOR 引擎: args[0]=数据, args[1]=长度, args[2]=密钥 std::string*
      hook(OFF.XOR, 'xor', {
        onEnter(args) {
          const len = args[1].toInt32();
          const s = readStdString(args[2]);
          let head = null;
          try { head = hexOf(args[0].readByteArray(Math.min(len, 64))); } catch (e) {}
          let bt = null;
          try {
            bt = Thread.backtrace(this.context, Backtracer.ACCURATE).slice(0, 5)
                    .map(DebugSymbol.fromAddress).map(String);
          } catch (e) {}
          emit({ t: 'xor_use', len: len, key: s ? s.text : null, head: head, bt: bt });
        }
      });

      // 响应侧: param_4 = keyId (来自响应的 qqq 字段)
      hook(OFF.NATIVE_DATA_R, 'native_data_r', {
        onEnter(args) { emit({ t: 'key_id', key_id: args[3].toInt32() }); }
      });
      hook(OFF.NATIVE_DATA, 'native_data', { onEnter() {} });

      // keymap 插入: 记录 (id, value)
      hook(OFF.MAP_INSERT, 'map_insert', {
        onEnter(args) {
          const pair = args[2];
          let id = null, val = null;
          try {
            id = pair.readS32();
            const s = readStdString(pair.add(8));
            val = s ? s.text : null;
          } catch (e) {}
          emit({ t: 'map_insert', id: id, value: val });
        }
      });

      // 登录后定期 dump 密钥表
      let n = 0;
      const timer = setInterval(function () {
        n++;
        if (!dumped) dumpKeyState('poll' + n);
        if (n >= 40) clearInterval(timer);
      }, 3000);
    }, 400);
  }
});

emit({ t: 'script_loaded', pid: Process.id });
