'use strict';
/*
 * 双向明文探针 —— 终局方案
 * ------------------------
 * XOR 引擎(device 版 0x9e02b8)签名已从反汇编解出:
 *     void xor_at(char* buf, int len, std::string* key, int offset)
 *     x0=buf  x1=len  x2=key  x3=offset
 * 它是**原地**异或: buf 既是输入也是输出。
 *   => onEnter  读 buf = 该方向调用前的数据
 *   => onLeave  读 buf = 该方向调用后的数据
 * 同一个函数被两个方向共用, 用首字节区分:
 *   首字节 0x78        -> zlib 流 = **响应**(服务端→客户端), onLeave 才是明文
 *   首字节 0x12(SFS_OBJECT) -> **请求**, onEnter 才是明文
 *
 * 输出: {t:'x', dir:'req'|'resp', len, hex}
 * 本地用 cok_sfs 解析(请求直接 parse, 响应先 zlib.decompress 再 parse)。
 */
const OFF = { XOR: 0x9e02b8 };
const MAX = 262144;

function emit(o) { try { send(o); } catch (e) {} }

function hexOf(buf) {
  const u8 = new Uint8Array(buf);
  let s = '';
  for (let i = 0; i < u8.length; i++) s += ('0' + u8[i].toString(16)).slice(-2);
  return s;
}

Process.attachModuleObserver({
  onAdded(module) {
    if (module.name !== 'libgame.so') return;
    setTimeout(function () {
      const p = module.base.add(OFF.XOR);
      try {
        Interceptor.attach(p, {
          onEnter(args) {
            this.len = args[1].toInt32();
            this.off = args[3].toInt32();
            this.buf = args[0];
            if (this.len <= 0 || this.len > MAX) { this.len = 0; return; }
            let b0 = -1;
            try { b0 = this.buf.add(this.off).readU8(); } catch (e) {}
            // 请求方向: 调用前 buf 就是 SFS 明文(首字节 0x12 = SFS_OBJECT)
            if (b0 === 0x12) {
              let hex = null;
              try { hex = hexOf(this.buf.add(this.off).readByteArray(this.len)); } catch (e) {}
              if (hex) emit({ t: 'x', dir: 'req', len: this.len, hex: hex });
            }
          this.dumped = false;
          },
          onLeave() {
            if (!this.len || this.dumped) return;
            // 响应方向: 调用后 buf 才是明文 = zlib(SFS), 首字节 0x78
            let b1 = -1;
            try { b1 = this.buf.add(this.off).readU8(); } catch (e) {}
            if (b1 !== 0x78) return;          // 请求方向的 onLeave 是密文, 丢弃
            let hex = null;
            try { hex = hexOf(this.buf.add(this.off).readByteArray(this.len)); } catch (e) {}
            if (hex) { this.dumped = true; emit({ t: 'x', dir: 'resp', len: this.len, hex: hex }); }
          }
        });
        emit({ t: 'hooked', name: 'xor', addr: p.toString() });
      } catch (e) { emit({ t: 'hook_err', name: 'xor', msg: String(e) }); }
      emit({ t: 'script_loaded', pid: Process.id });
    }, 500);
  }
});
