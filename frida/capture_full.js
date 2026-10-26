'use strict';
/*
 * 升级版探针: 目标 = 拿到**请求明文**里的命令名与参数名/参数值。
 *
 * 相比 capture_build.js 的改动:
 *   1) XOR 引擎不再只截 48 字节, 且**记录全部 5 个参数指针**并分别采样,
 *      用于确定"哪个参数是明文 buffer"(in-place / (dst,len,key,src) 两种签名)。
 *   2) 额外 hook "命令名 -> map" 的插入点(map<int,string>::insert),
 *      直接拿到完整命令名字符串。
 *   3) wire 层保留, 用于对齐"哪一帧 = 哪条命令"。
 */
const OFF = {
  XOR: 0x9e02b8,          // 设备版 libgame.so 偏移
  NATIVE_SEND: 0x13af684,
  MAP_INSERT: 0xa262c8,   // std::map<int,string>::insert —— 命令名入表
};

function emit(o) { try { send(o); } catch (e) {} }

function hexOf(buf) {
  const u8 = new Uint8Array(buf);
  let s = '';
  for (let i = 0; i < u8.length; i++) s += ('0' + u8[i].toString(16)).slice(-2);
  return s;
}

function sample(p, len) {
  try {
    if (p === null || p === undefined) return null;
    const n = Math.min(Math.max(len | 0, 0), 96);
    if (n <= 0) return null;
    return hexOf(p.readByteArray(n));
  } catch (e) { return null; }
}

Process.attachModuleObserver({
  onAdded(module) {
    if (module.name !== 'libgame.so') return;
    setTimeout(function () {
      const base = module.base;

      function hook(off, tag, handlers) {
        const p = base.add(off);
        try { Interceptor.attach(p, handlers); emit({ t: 'hooked', name: tag, addr: p.toString() }); }
        catch (e) { emit({ t: 'hook_err', name: tag, msg: String(e) }); }
      }

      // 1) XOR 引擎: 记录 5 个参数 + 各自采样
      hook(OFF.XOR, 'xor', {
        onEnter(args) {
          const len = args[1].toInt32();
          const rec = { t: 'xor', len: len };
          for (let i = 0; i < 5; i++) {
            let s = null;
            try { s = sample(args[i], len); } catch (e) {}
            rec['a' + i] = s;
          }
          // args[2] 常是密钥串, 单独按 C 字符串读
          try { rec.key = args[2].readCString(); } catch (e) {}
          emit(rec);
        }
      });

      // 2) 命令名 -> map<int,string> 插入
      hook(OFF.MAP_INSERT, 'map_insert', {
        onEnter(args) {
          // std::_Rb_tree::_M_insert_unique(node*, key, ...): 形参取决于版本
          let s = null;
          try { s = args[1].readCString(); } catch (e) {}
          if (!s) { try { s = args[2].readCString(); } catch (e) {} }
          if (s) emit({ t: 'map_insert', str: s });
        }
      });

      // 3) native 命令名入口(内部事件名, 辅助)
      hook(OFF.NATIVE_SEND, 'native_send', {
        onEnter(args) {
          let cmd = null;
          try { cmd = args[4].readCString(); } catch (e) {}
          if (cmd) emit({ t: 'native_cmd', cmd: cmd });
        }
      });

      emit({ t: 'script_loaded', pid: Process.id });
    }, 400);
  }
});
