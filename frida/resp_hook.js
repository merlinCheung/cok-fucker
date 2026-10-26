'use strict';
/*
 * COK 响应解码链捕获:
 *   FUN_00d58b78  响应参数解码器(取 "rlQW45Y" -> XOR -> 解压)
 *   FUN_00ae02b8  XOR 引擎 (Ghidra 0x00ae02b8 -> 运行时 base+0x9e02b8)
 *   FUN_02d96ccc / FUN_02d96bc8  解压包装
 *   ByteArray::Uncompress / LZ4_uncompress / inflate  具体实现
 * 命中哪个就记录哪个的输入/输出。
 */
function hexOf(buf) {
  const u8 = new Uint8Array(buf);
  let s = '';
  for (let i = 0; i < u8.length; i++) s += ('0' + u8[i].toString(16)).slice(-2);
  return s;
}
function emit(o) { try { send(o); } catch (e) {} }

Process.attachModuleObserver({
  onAdded(module) {
    if (module.name !== 'libgame.so') return;
    setTimeout(function () {
      const base = module.base;

      function hook(off, tag, handlers) {
        const p = base.add(off);
        try {
          Interceptor.attach(p, handlers);
          emit({ t: 'hooked', name: tag, addr: p.toString() });
        } catch (e) { emit({ t: 'hook_err', name: tag, msg: String(e) }); }
      }

      // XOR 引擎
      hook(0x9e02b8, 'xor_engine', {
        onEnter(args) {
          this.len = args[1].toInt32();
          this.buf = args[0];
          this.off = args[3].toInt32();
          this.key = null;
          try {
            const dp = args[2].readPointer();
            const klen = dp.sub(0x18).readU32();
            if (klen > 0 && klen < 4096) this.key = dp.readUtf8String(klen);
          } catch (e) {}
          let plain = null;
          try { plain = hexOf(args[0].add(this.off).readByteArray(Math.min(this.len, 4096))); } catch (e) {}
          this.plain = plain;
        },
        onLeave() {
          let cipher = null;
          try { cipher = hexOf(this.buf.add(this.off).readByteArray(Math.min(this.len, 4096))); } catch (e) {}
          emit({ t: 'xor_pair', len: this.len, key: this.key, plain_hex: this.plain, cipher_hex: cipher });
        }
      });

      // 响应解码器本体
      hook(0x9d58b78, 'resp_decoder', {
        onEnter(args) { emit({ t: 'resp_decoder_enter', a0: args[0].toString(), a1: args[1].toString() }); }
      });

      // 解压候选
      hook(0x1d96ccc, 'uncompress_2d96ccc', {
        onEnter(args) {
          this.len = args[1].toInt32();
          this.outp = args[2];
          let c = null;
          try { c = hexOf(args[0].readByteArray(Math.min(this.len, 4096))); } catch (e) {}
          emit({ t: 'uncompress_in', who: '2d96ccc', len: this.len, cipher_hex: c });
        },
        onLeave() {
          let p = null;
          try {
            const q = this.outp.readPointer();
            const n = q.add(8).readU32();
            p = hexOf(q.readByteArray(Math.min(n, 4096)));
          } catch (e) {}
          emit({ t: 'uncompress_out', who: '2d96ccc', plain_hex: p });
        }
      });

      hook(0x1d96bc8, 'uncompress_2d96bc8', {
        onEnter(args) { this.a0 = args[0]; this.a1 = args[1]; this.a2 = args[2]; },
        onLeave(ret) { emit({ t: 'uncompress_2d96bc8_ret', ret: ret.toString() }); }
      });

      // ByteArray::Uncompress (Sfs2X) —— 0x29881dc -> base+0x18881dc
      hook(0x18881dc, 'bytearray_uncompress', {
        onEnter(args) { emit({ t: 'bytearray_uncompress_enter', a0: args[0].toString() }); }
      });

      // LZ4_uncompress (0x2c9a510 -> base+0x1c9a510) : (src, srcSize, dst, dstCapacity)
      hook(0x1c9a510, 'lz4_uncompress', {
        onEnter(args) {
          let s = null;
          try { s = hexOf(args[0].readByteArray(Math.min(args[1].toInt32(), 512))); } catch (e) {}
          emit({ t: 'lz4_in', src_len: args[1].toInt32(), src_hex: s, dst_cap: args[3].toInt32() });
        },
        onLeave(ret) { emit({ t: 'lz4_out', ret: ret.toInt32() }); }
      });

      // inflate (0x2dbd904 -> base+0x1cbd904) : z_stream*
      hook(0x1cbd904, 'inflate', {
        onEnter(args) { emit({ t: 'inflate_enter', z: args[0].toString() }); },
        onLeave(ret) { emit({ t: 'inflate_leave', ret: ret.toInt32() }); }
      });
    }, 300);
  }
});

emit({ t: 'script_loaded', pid: Process.id });
