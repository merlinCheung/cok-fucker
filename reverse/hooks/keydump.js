'use strict';
/*
 * 直接从 libgame.so 内存读出加解密密钥:
 *   单例A = [Ghidra DAT_03c1a5f8] -> 运行时 base + 0x3b1a5f8
 *   A+0x1a8 : std::map<int, std::string>  (nativeData 用的 key 表)
 *   A+0x1d8 : std::string  (BlowFish 密钥)
 */
function hexOf(buf) {
  const u8 = new Uint8Array(buf);
  let s = '';
  for (let i = 0; i < u8.length; i++) s += ('0' + u8[i].toString(16)).slice(-2);
  return s;
}
function emit(o) { try { send(o); } catch (e) {} }

function readStdString(p) {
  try {
    if (!p || p.isNull()) return null;
    const dataPtr = p.readPointer();
    const len = p.add(8).readU32();
    if (len === 0) return { len: 0, text: '' };
    if (len > 4096) return { len: len, text: null, err: 'too long' };
    const sso = dataPtr.equals(p.add(16));
    const base = sso ? p.add(16) : dataPtr;
    return { len: len, text: base.readUtf8String(len), sso: sso };
  } catch (e) { return { err: String(e) }; }
}

Process.attachModuleObserver({
  onAdded(module) {
    if (module.name !== 'libgame.so') return;
    setTimeout(function () {
      const base = module.base;
      // DAT_03c1a5f8 -> Ghidra 0x3c1a5f8, image base 0x100000 -> offset 0x3b1a5f8
      let A = null;
      try {
        A = base.add(0x3b1a5f8).readPointer();
        emit({ t: 'singleton', addr: A.toString(), base: base.toString() });
      } catch (e) { emit({ t: 'singleton_err', msg: String(e) }); return; }

      // BlowFish key @ A+0x1d8
      try {
        const s = readStdString(A.add(0x1d8));
        emit({ t: 'blowfish_key', len: s ? s.len : null, text: s ? s.text : null });
      } catch (e) { emit({ t: 'bf_key_err', msg: String(e) }); }

      // map @ A+0x1a8 : {header(32B), size_t count}
      const mapAddr = A.add(0x1a8);
      let count = 0;
      try { count = mapAddr.add(0x20).readU32(); } catch (e) {}
      emit({ t: 'map_addr', addr: mapAddr.toString(), node_count: count });

      const seen = new Set();
      const out = [];
      function walk(node, depth) {
        if (node === null || depth > 64) return;
        const key = node.toString();
        if (seen.has(key)) return;
        seen.add(key);
        let left, right;
        try { left = node.add(0x10).readPointer(); right = node.add(0x18).readPointer(); } catch (e) { return; }
        walk(left, depth + 1);
        try {
          const k = node.add(0x20).readS32();
          const v = readStdString(node.add(0x28));
          out.push({ k: k, len: v ? v.len : null, v: v ? v.text : null });
        } catch (e) {}
        walk(right, depth + 1);
      }
      try {
        const left = mapAddr.add(0x10).readPointer();
        walk(left, 0);
      } catch (e) { emit({ t: 'walk_err', msg: String(e) }); }
      emit({ t: 'map_entries', n: out.length, entries: out });
    }, 200);
  }
});

emit({ t: 'script_loaded', pid: Process.id });
