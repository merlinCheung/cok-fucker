'use strict';
/*
 * 终局探针: 命令名 + 双向明文
 * -----------------------------
 * 1) XOR 引擎 (device 版 0x9e02b8) 签名(反汇编得出):
 *        void xor_at(char* buf, int len, std::string* key, int offset)
 *    - 原地异或; x2 是 key 对象指针, key 数据在 *(x2), 长度在 *(x2)-0x18
 *    - 请求方向: onEnter 读 buf = **params 明文**(首字节 0x12 = SFS_OBJECT)
 *    - 响应方向: onLeave 读 buf = **params 明文**(首字节 0x78 = zlib)
 *    - 同时读出**会话密钥**, 用来解 wire 上的完整帧(帧里只有 params 被加密,
 *      命令名 p.c 是明文, 但 params 加密; 有 key 就能把帧解出来)
 * 2) libc write/send -> 完整帧 hex(只 dump <= 8KB 的业务请求帧)
 *
 * Python 端: 用 key 解帧 -> parse -> 得到 命令名 + 全部 params
 */
const OFF = { XOR: 0x9e02b8 };
const MAX = 262144;
const MAXWIRE = 262144;   // 大响应(全背包 64KB+)会被 8KB 上限丢掉

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
      const base = module.base;

      // ---- 1) XOR 引擎: 双向明文 + 会话密钥 ----
      try {
        Interceptor.attach(base.add(OFF.XOR), {
          onEnter(args) {
            this.len = args[1].toInt32();
            this.off = args[3].toInt32();
            this.buf = args[0];
            if (this.len <= 0 || this.len > MAX) { this.len = 0; return; }
            let b0 = -1;
            try { b0 = this.buf.add(this.off).readU8(); } catch (e) {}
            // 会话密钥: x2 -> keyObj; *(x2) = 数据指针; 长度在 -0x18
            try {
              const kp = args[2].readPointer();
              const klen = kp.sub(0x18).readU32();
              if (klen > 0 && klen <= 64) {
                const k = hexOf(kp.readByteArray(klen));
                if (k !== lastKey) { lastKey = k; emit({ t: 'key', key: k }); }
              }
            } catch (e) {}
            if (b0 === 0x12) {                    // 请求: 调用前就是明文
              let hex = null;
              try { hex = hexOf(this.buf.add(this.off).readByteArray(this.len)); } catch (e) {}
              if (hex) emit({ t: 'x', dir: 'req', len: this.len, hex: hex });
            }
          },
          onLeave() {
            if (!this.len) return;
            let b1 = -1;
            try { b1 = this.buf.add(this.off).readU8(); } catch (e) {}
            if (b1 !== 0x78) return;              // 响应: 调用后才是明文(zlib)
            let hex = null;
            try { hex = hexOf(this.buf.add(this.off).readByteArray(this.len)); } catch (e) {}
            if (hex) emit({ t: 'x', dir: 'resp', len: this.len, hex: hex });
          }
        });
        emit({ t: 'hooked', name: 'xor', addr: base.add(OFF.XOR).toString() });
      } catch (e) { emit({ t: 'hook_err', name: 'xor', msg: String(e) }); }

      // ---- 2) wire 帧 ----
      try {
        const libc = Process.getModuleByName('libc.so');
        function h(name) {
          let p = null;
          try { p = libc.getExportByName(name); } catch (e) { return; }
          Interceptor.attach(p, {
            onEnter(args) { this.buf = args[1]; this.len = args[2].toInt32(); },
            onLeave() {
              if (this.len <= 0 || this.len > MAXWIRE) return;
              let hex = null;
              try { hex = hexOf(this.buf.readByteArray(this.len)); } catch (e) {}
              if (hex) emit({ t: 'w', len: this.len, hex: hex });
            }
          });
        }
        h('write'); h('send');
        // 入站也要抓: 响应(尤其大响应)才是背包 items 的来源
        function hin(name) {
          let p = null;
          try { p = libc.getExportByName(name); } catch (e) { return; }
          Interceptor.attach(p, {
            onEnter(args) { this.buf = args[1]; this.len = args[2].toInt32(); },
            onLeave() {
              if (this.len <= 0 || this.len > MAXWIRE) return;
              let hex = null;
              try { hex = hexOf(this.buf.readByteArray(this.len)); } catch (e) {}
              if (hex) emit({ t: 'r', len: this.len, hex: hex });
            }
          });
        }
        hin('read'); hin('recv'); hin('recvfrom');
        emit({ t: 'hooked', name: 'wire' });
      } catch (e) { emit({ t: 'hook_err', name: 'wire', msg: String(e) }); }

      emit({ t: 'script_loaded', pid: Process.id });
    }, 600);
  }
});

let lastKey = null;
