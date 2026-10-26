'use strict';
/*
 * COK 游戏服参数加解密 全套抓取:
 *   A) 配置单例内存直读: map<int,string> 密钥表 + BlowFish 密钥
 *   B) 请求侧加密函数 hook: 明文 params + 使用的密钥
 *   C) 解密函数 hook: 响应密文 -> 明文
 *   D) BlowFish BF_set_key
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
    if (len > 4096) return { len: len, text: null };
    const sso = dataPtr.equals(p.add(16));
    const base = sso ? p.add(16) : dataPtr;
    return { len: len, text: base.readUtf8String(len), sso: sso };
  } catch (e) { return { err: String(e) }; }
}

function dumpConfig(A) {
  try {
    const s = readStdString(A.add(0x1d8));
    emit({ t: 'blowfish_key', len: s ? s.len : null, text: s ? s.text : null });
  } catch (e) { emit({ t: 'bf_key_err', msg: String(e) }); }

  const mapAddr = A.add(0x1a8);
  let count = 0;
  try { count = mapAddr.add(0x20).readU32(); } catch (e) {}
  emit({ t: 'map_addr', addr: mapAddr.toString(), node_count: count });

  const seen = new Set();
  const out = [];
  function walk(node, depth) {
    if (node === null || depth > 64) return;
    const k = node.toString();
    if (seen.has(k)) return;
    seen.add(k);
    let left, right;
    try { left = node.add(0x10).readPointer(); right = node.add(0x18).readPointer(); } catch (e) { return; }
    walk(left, depth + 1);
    try {
      const ik = node.add(0x20).readS32();
      const sp = node.add(0x28);
      let v = readStdString(sp);
      let raw = null;
      try { raw = hexOf(sp.readByteArray(24)); } catch (e) {}
      out.push({ k: ik, len: v ? v.len : null, v: v ? v.text : null, raw: raw });
    } catch (e) {}
    walk(right, depth + 1);
  }
  try { walk(mapAddr.add(0x10).readPointer(), 0); } catch (e) { emit({ t: 'walk_err', msg: String(e) }); }
  emit({ t: 'map_entries', n: out.length, entries: out });
}

function installHooks(module) {
  const base = module.base;

  function hook(off, tag, handlers) {
    const p = base.add(off);
    try {
      Interceptor.attach(p, handlers);
      emit({ t: 'hooked', name: tag, addr: p.toString() });
    } catch (e) { emit({ t: 'hook_err', name: tag, msg: String(e) }); }
  }

  hook(0x9e02b8, 'enc_A', {
    onEnter(args) {
      const len = args[1].toInt32();
      const key = readStdString(args[2]);
      let plain = null;
      try { plain = hexOf(args[0].readByteArray(Math.min(len, 4096))); } catch (e) {}
      emit({ t: 'enc_plain', len: len, key: key ? key.text : null, plain_hex: plain });
    }
  });

  hook(0x9b7890, 'enc_B', {
    onEnter(args) {
      const len = args[2].toInt32();
      const key = readStdString(args[3]);
      let plain = null;
      try { plain = hexOf(args[1].readByteArray(Math.min(len, 4096))); } catch (e) {}
      emit({ t: 'enc_plain_B', len: len, key: key ? key.text : null, plain_hex: plain });
    }
  });

  hook(0x1c96ccc, 'dec', {
    onEnter(args) {
      this.len = args[1].toInt32();
      this.outp = args[2];
      let ct = null;
      try { ct = hexOf(args[0].readByteArray(Math.min(this.len, 4096))); } catch (e) {}
      emit({ t: 'dec_in', len: this.len, cipher_hex: ct });
    },
    onLeave() {
      let pt = null;
      try {
        const p = this.outp.readPointer();
        const n = p.add(8).readU32();
        pt = hexOf(p.readByteArray(Math.min(n, 4096)));
      } catch (e) {}
      emit({ t: 'dec_out', plain_hex: pt });
    }
  });

  try {
    const bf = module.getExportByName('BF_set_key');
    if (bf) {
      Interceptor.attach(bf, {
        onEnter(args) {
          const len = args[1].toInt32();
          let hex = null;
          try { hex = hexOf(args[2].readByteArray(Math.min(len, 128))); } catch (e) {}
          emit({ t: 'bf_set_key', len: len, key_hex: hex });
        }
      });
      emit({ t: 'hooked', name: 'BF_set_key' });
    }
  } catch (e) {}
}

Process.attachModuleObserver({
  onAdded(module) {
    if (module.name !== 'libgame.so') return;
    setTimeout(function () {
      emit({ t: 'module', base: module.base.toString(), size: module.size });
      installHooks(module);
      let A = null;
      try {
        A = module.base.add(0x3b1a5f8).readPointer();
        emit({ t: 'singleton', addr: A.toString() });
        if (A && !A.isNull()) dumpConfig(A);
      } catch (e) { emit({ t: 'singleton_err', msg: String(e) }); }

      // cfgB = DAT_03c19040 -> 偏移 0x3b19040; 开关 +0x11f4, 模式 +0x19d0
      try {
        const B = module.base.add(0x3b19040).readPointer();
        let f = null, mode = null;
        try { f = B.add(0x11f4).readS32(); } catch (e) {}
        try { mode = B.add(0x19d0).readS32(); } catch (e) {}
        emit({ t: 'cfgB', addr: B.toString(), encrypt_flag_11f4: f, mode_19d0: mode });
      } catch (e) { emit({ t: 'cfgB_err', msg: String(e) }); }

      // 单例懒创建: 轮询直到非空
      let dumped = false;
      const timer = setInterval(function () {
        if (dumped) { return; }
        try {
          const p = module.base.add(0x3b1a5f8).readPointer();
          if (p && !p.isNull()) {
            dumped = true;
            emit({ t: 'singleton_ready', addr: p.toString() });
            dumpConfig(p);
          }
        } catch (e) {}
      }, 3000);
      setTimeout(function () { try { clearInterval(timer); } catch (e) {} }, 180000);
    }, 300);
  }
});

emit({ t: 'script_loaded', pid: Process.id });
