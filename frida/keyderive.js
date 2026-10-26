'use strict';
/*
 * 验证会话 XOR 密钥的下发通道:
 *   静态结论(来自 libgame.so 反编译):
 *     登录响应 params 里有字段 "id" = "<前缀>_<密钥ID>"
 *     -> 密钥ID = atoi(前缀之后的部分)
 *     -> XOR 密钥 = md5_hex(前缀)            (32 位小写 hex 字符串)
 *     -> 存入 map<int,string> (单例 + 0x1a8),  单例 + 0x1d8 = 前缀
 *
 * 本脚本抓:
 *   md5_init   : MD5 输入(前缀)
 *   md5_final  : MD5 输出(hex 密钥)
 *   find_'_'   : "id" 原始字符串
 *   keymap     : 登录后 map<int,string> 全量内容
 *   xor_use    : 实际参与加解密的密钥
 */
const OFF = {
  MD5_INIT: 0x6aa7e8,     // FUN_017aa7e8  (MD5_Init, IV=67452301...)
  MD5_FINAL: 0x6aadec,    // FUN_017aadec  (MD5_Final + hex)
  FIND_US: 0x207b9b8,    // FUN_0307b9b8  (strchr '_')
  CFG_GET: 0x754444,     // FUN_01854444  (单例 getter)
  LOGIN_CMD: 0x1a260,    // FUN_0101a260  (解析 id -> 派生密钥)
  XOR: 0x9e02b8,         // FUN_00ae02b8  (XOR 引擎)
};

function emit(o) { try { send(o); } catch (e) {} }
function hexOf(buf) {
  const u8 = new Uint8Array(buf);
  let s = '';
  for (let i = 0; i < u8.length; i++) s += ('0' + u8[i].toString(16)).slice(-2);
  return s;
}
// 老 libstdc++ (COW) std::string: 数据指针在 +0, 长度在 data-0x18
function readStdString(p) {
  try {
    const dp = p.readPointer();
    if (dp.isNull()) return { len: 0, text: '' };
    const len = dp.sub(0x18).readU32();
    if (!(len > 0 && len < 4096)) return { len: len, text: null };
    return { len: len, text: dp.readUtf8String(len) };
  } catch (e) { return { err: String(e) }; }
}
function readStdStringAt(ptr) { return readStdString(ptr); }

let BASE = null;
let cfgPtr = null;

function hook(off, tag, handlers) {
  const p = BASE.add(off);
  try {
    Interceptor.attach(p, handlers);
    emit({ t: 'hooked', name: tag, addr: p.toString() });
  } catch (e) { emit({ t: 'hook_err', name: tag, msg: String(e) }); }
}

// libstdc++ map<int,string> 迭代: map+0 = header(color,parent,left,right), map+32 = 节点数
// 节点: base 32 字节(color,pad,parent,left,right) + value{ int@0, pad, char*@8, len@16 }
function dumpKeyMap(mapAddr) {
  const out = [];
  try {
    const root = mapAddr.add(8).readPointer();   // header._M_parent
    const count = mapAddr.add(32).readU64().toNumber();
    const stack = [root];
    const seen = new Set();
    while (stack.length) {
      const node = stack.pop();
      if (node.isNull()) continue;
      const k = node.toString();
      if (seen.has(k)) continue;
      seen.add(k);
      const key = node.add(32).readS32();
      const sp = node.add(40).readPointer();
      const len = node.add(48).readU64().toNumber();
      let text = null;
      if (!sp.isNull() && len > 0 && len < 4096) {
        try { text = sp.readUtf8String(len); } catch (e) { text = null; }
      }
      out.push({ key: key, len: len, value: text });
      stack.push(node.add(16).readPointer());  // _M_left
      stack.push(node.add(24).readPointer());  // _M_right
    }
    return { count: count, items: out };
  } catch (e) { return { err: String(e) }; }
}

// ---- 线路原始字节(只收 SFS 帧: 首字节 0x80 且长度自洽) ----
function hookWire() {
  const lib = Process.findModuleByName('libc.so');
  if (!lib) { emit({ t: 'wire_err', msg: 'no libc' }); return; }
  const w = lib.getExportByName('write');
  const r = lib.getExportByName('read');
  function looksSfs(p, len) {
    if (len < 3) return false;
    try {
      const b = p.readU8();
      if ((b & 0x80) === 0) return false;
      const l = p.add(1).readU16();
      return l + 3 === len;
    } catch (e) { return false; }
  }
  if (w) Interceptor.attach(w, {
    onEnter(args) {
      const len = args[2].toInt32();
      if (len > 0 && len < 262144 && looksSfs(args[1], len)) {
        try { emit({ t: 'wire', dir: 'out', fd: args[0].toInt32(), len: len, hex: hexOf(args[1].readByteArray(len)) }); } catch (e) {}
      }
    }
  });
  if (r) Interceptor.attach(r, {
    onEnter(args) {
      this.len = args[2].toInt32();
      this.buf = args[1];
      this.fd = args[0].toInt32();
    },
    onLeave(retval) {
      const n = retval.toInt32();
      if (n > 0 && n < 262144 && looksSfs(this.buf, n)) {
        try { emit({ t: 'wire', dir: 'in', fd: this.fd, len: n, hex: hexOf(this.buf.readByteArray(n)) }); } catch (e) {}
      }
    }
  });
  emit({ t: 'wire_hooked' });
}

Process.attachModuleObserver({
  onAdded(module) {
    if (module.name !== 'libgame.so') return;
    setTimeout(function () {
      BASE = module.base;
      emit({ t: 'base', v: BASE.toString() });
      hookWire();

      // MD5_Init(ctx, std::string* text)
      hook(OFF.MD5_INIT, 'md5_init', {
        onEnter(args) {
          const s = readStdStringAt(args[1]);
          emit({ t: 'md5_input', text: s.text, len: s.len });
        }
      });

      // MD5_Final(std::string* out, ctx)
      hook(OFF.MD5_FINAL, 'md5_final', {
        onEnter(args) { this.outp = args[0]; },
        onLeave() {
          const s = readStdStringAt(this.outp);
          emit({ t: 'md5_output', text: s.text, len: s.len });
        }
      });

      // strchr(std::string* s, '_')
      hook(OFF.FIND_US, 'find_us', {
        onEnter(args) {
          if (args[1].toInt32() !== 0x5f) return;
          const s = readStdStringAt(args[0]);
          emit({ t: 'id_string', text: s.text, len: s.len });
        }
      });

      // 单例 getter: 记录指针
      hook(OFF.CFG_GET, 'cfg_get', {
        onLeave(retval) { if (cfgPtr === null) cfgPtr = retval; }
      });

      // 解析 id 的函数: 返回后 dump 密钥表
      hook(OFF.LOGIN_CMD, 'login_cmd', {
        onEnter() { emit({ t: 'login_cmd_enter' }); },
        onLeave() {
          if (cfgPtr === null) { emit({ t: 'keymap', err: 'no cfg singleton yet' }); return; }
          const mapAddr = cfgPtr.add(0x1a8);
          const prefix = readStdStringAt(cfgPtr.add(0x1d8));
          emit({
            t: 'keymap',
            cfg: cfgPtr.toString(),
            prefix_field: prefix.text,
            map: dumpKeyMap(mapAddr),
          });
        }
      });

      // XOR 引擎: 实际使用的密钥 + 回溯
      hook(OFF.XOR, 'xor_use', {
        onEnter(args) {
          const len = args[1].toInt32();
          const s = readStdStringAt(args[2]);
          let bt = null;
          try {
            bt = Thread.backtrace(this.context, Backtracer.ACCURATE).slice(0, 8)
                    .map(DebugSymbol.fromAddress).map(String);
          } catch (e) {}
          emit({ t: 'xor_use', len: len, key: s.text, bt: bt });
        }
      });
    }, 300);
  }
});

emit({ t: 'script_loaded', pid: Process.id });
