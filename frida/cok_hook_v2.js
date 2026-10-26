'use strict';
/*
 * COK 协议 v2 捕获:
 *  1) FUN_00ae02b8 (XOR 引擎): 入参明文 / 出参密文 / 第3参=密钥字符串
 *  2) FUN_02d96bc8 (解压引擎): 入参=压缩数据 / 出参=解压结果
 *  3) 配置单例 map<int,string> 全量 dump (含 id=81 请求密钥 / id=65 响应密钥)
 */
function hexOf(buf) {
  const u8 = new Uint8Array(buf);
  let s = '';
  for (let i = 0; i < u8.length; i++) s += ('0' + u8[i].toString(16)).slice(-2);
  return s;
}
function emit(o) { try { send(o); } catch (e) {} }

function rawStdString(p, n) {
  try {
    if (!p || p.isNull()) return null;
    return hexOf(p.readByteArray(n || 24));
  } catch (e) { return null; }
}

function parseStdStringAt(p) {
  // libstdc++ std::string: [0]=char* [8]=len [16]=SSO buf
  try {
    if (!p || p.isNull()) return null;
    const dp = p.readPointer();
    const len = p.add(8).readU32();
    if (len === 0) return { len: 0, text: '' };
    if (len > 8192) return { len: len, text: null };
    const sso = dp.equals(p.add(16));
    const base = sso ? p.add(16) : dp;
    return { len: len, text: base.readUtf8String(len), sso: sso };
  } catch (e) { return { err: String(e) }; }
}

let dumped = false;

Process.attachModuleObserver({
  onAdded(module) {
    if (module.name !== 'libgame.so') return;
    setTimeout(function () {
      const base = module.base;
      emit({ t: 'module', base: base.toString(), pid: Process.id });

      function hook(off, tag, handlers) {
        const p = base.add(off);
        try {
          Interceptor.attach(p, handlers);
          emit({ t: 'hooked', name: tag, addr: p.toString(), off: '0x' + off.toString(16) });
        } catch (e) { emit({ t: 'hook_err', name: tag, msg: String(e) }); }
      }

      // XOR 引擎: FUN_00ae02b8(data, len, keyStr*, offset)
      hook(0x9e02b8, 'xor_engine', {
        onEnter(args) {
          this.len = args[1].toInt32();
          this.buf = args[0];
          this.off = args[3].toInt32();
          this.keyRaw = rawStdString(args[2], 24);
          this.key = null;
          try {
            const dp = args[2].readPointer();          // std::string::_M_p -> 数据指针
            const klen = dp.sub(0x18).readU32();       // 老 ABI: 长度在数据指针 -0x18
            if (klen > 0 && klen < 4096) {
              this.key = { len: klen, text: dp.readUtf8String(klen) };
            }
          } catch (e) {}
          let plain = null;
          try { plain = hexOf(args[0].add(this.off).readByteArray(Math.min(this.len, 8192))); } catch (e) {}
          this.plain = plain;
        },
        onLeave() {
          let cipher = null;
          try { cipher = hexOf(this.buf.add(this.off).readByteArray(Math.min(this.len, 8192))); } catch (e) {}
          emit({
            t: 'xor_pair', len: this.len,
            key: this.key ? this.key.text : null,
            key_len: this.key ? this.key.len : null,
            key_raw: this.keyRaw,
            plain_hex: this.plain, cipher_hex: cipher
          });
        }
      });

      // 解压引擎: FUN_02d96bc8  (nativeDataR 里在 XOR 之后调用)
      hook(0x1d96bc8, 'uncompress', {
        onEnter(args) {
          this.data = args[0];
          this.len = args[1].toInt32();
          this.outp = args[2];
          let c = null;
          try { c = hexOf(this.data.readByteArray(Math.min(this.len, 8192))); } catch (e) {}
          emit({ t: 'uncompress_in', len: this.len, cipher_hex: c });
        },
        onLeave() {
          let p = null;
          try {
            const q = this.outp.readPointer();
            const n = q.add(8).readU32();
            p = hexOf(q.readByteArray(Math.min(n, 8192)));
          } catch (e) {}
          emit({ t: 'uncompress_out', plain_hex: p });
        }
      });

      // 配置表: 轮询直到非空, 然后全量 dump
      const timer = setInterval(function () {
        let A = null;
        try { A = base.add(0x3b1a5f8).readPointer(); } catch (e) { return; }
        if (!A || A.isNull()) return;
        emit({ t: 'cfg_ready', addr: A.toString() });
        const mapAddr = A.add(0x1a8);
        const seen = new Set();
        const entries = [];
        function walk(node, depth) {
          if (node === null || depth > 64) return;
          const k = node.toString();
          if (seen.has(k)) return;
          seen.add(k);
          let l, r;
          try { l = node.add(0x10).readPointer(); r = node.add(0x18).readPointer(); } catch (e) { return; }
          walk(l, depth + 1);
          try {
            const ik = node.add(0x20).readS32();
            const raw = hexOf(node.add(0x20).readByteArray(80));
            const cand = [];
            for (const off of [0x28, 0x30, 0x38, 0x40, 0x48]) {
              const s = parseStdStringAt(node.add(off));
              if (s && s.text) cand.push({ off: '0x' + off.toString(16), len: s.len, text: s.text });
            }
            emit({ t: 'cfg_entry', k: ik, raw: raw, cand: cand });
            entries.push(ik);
          } catch (e) {}
          walk(r, depth + 1);
        }
        try { walk(mapAddr.add(0x10).readPointer(), 0); } catch (e) { emit({ t: 'walk_err', msg: String(e) }); }
        // BlowFish 密钥槽
        try { emit({ t: 'bf_slot', raw: hexOf(A.add(0x1d8).readByteArray(32)) }); } catch (e) {}
        // 持续轮询: 条目数变化时再 dump 一次
        let lastCount = entries.length;
        setInterval(function () {
          const seen2 = new Set();
          const cur = [];
          function w2(node, depth) {
            if (node === null || depth > 64) return;
            const k = node.toString(); if (seen2.has(k)) return; seen2.add(k);
            let l, r; try { l = node.add(0x10).readPointer(); r = node.add(0x18).readPointer(); } catch (e) { return; }
            w2(l, depth + 1);
            try { cur.push(node.add(0x20).readS32()); } catch (e) {}
            w2(r, depth + 1);
          }
          try { w2(mapAddr.add(0x10).readPointer(), 0); } catch (e) { return; }
          if (cur.length !== lastCount) {
            lastCount = cur.length;
            emit({ t: 'cfg_changed', ids: cur });
          }
        }, 2000);
      }, 2000);
      setTimeout(function () { try { clearInterval(timer); } catch (e) {} }, 240000);
    }, 300);
  }
});

emit({ t: 'script_loaded', pid: Process.id });
