'use strict';
/*
 * queue.ccd / 加速类命令 精准探针 v4
 * ------------------------------------
 * 三个问题在这一版修掉:
 *  1) 之前用 `b0 & 0x80` 判 libc++ std::string 短/长 —— **错**, 所以 key 读出来全是垃圾,
 *     被 KEYS 过滤光, 一个字段都没抓到。现在两种布局都试, 取能读出合理 ASCII 的那个。
 *  2) key 不再依赖读 std::string: 用 make_str(0x2f7a6fc) 记下**刚构造的字面量**,
 *     紧接着的 set_value 就用它当 key(构造顺序在反汇编里是确定的)。
 *  3) 补 hook set_str(0x8fb620 是 PLT 存根, 改从 GOT 读真实地址再挂),
 *     并把命令名(字面量里含 '.') 一起上报, 这样能看出到底是哪个命令。
 *
 * device 版 libgame.so 偏移(ELF 静态 xref + 反汇编, 报告 §6.13.2):
 *   0x2f7a6fc  make_str(out, "literal", out2)
 *   0x9e7dec   set_value(obj, key, SFSValue*)     qUUID/itemUUID/isGold/itemCount
 *   0x2ce70ec  get_string(std::string*)            字符串字段的值
 *   0x8fb620   set_str(obj, key, const char*)      queueId/queueType/goldcost  (PLT)
 */
const OFF = {
  MAKE_STR:  0x2f7a6fc,
  SET_VALUE: 0x9e7dec,
  GET_STR:   0x2ce70ec,
  SET_STR_PLT: 0x8fb620,
  GOT_SET_STR: 0x3acc9f0,   // __got entry of set_str
};

const KEYS = {
  'qUUID': 1, 'qUuid': 1, 'itemUUID': 1, 'itemUuid': 1, 'itemId': 1,
  'isGold': 1, 'itemCount': 1, 'mark': 1,
  'queueId': 1, 'queueType': 1, 'goldcost': 1,
  'buildingId': 1, 'level': 1, 'star': 1, 'process': 1,
  'position': 1, 'costTime': 1, 'gold': 1, 'isInstant': 1,
};

function emit(o) { try { send(o); } catch (e) {} }

function hexOf(buf) {
  const u8 = new Uint8Array(buf);
  let s = '';
  for (let i = 0; i < u8.length; i++) s += ('0' + u8[i].toString(16)).slice(-2);
  return s;
}

function printable(s) {
  if (!s || s.length === 0 || s.length > 200) return false;
  for (let i = 0; i < s.length; i++) {
    const c = s.charCodeAt(i);
    if (c < 32 || c > 126) return false;
  }
  return true;
}

// 暴力试多种 libc++ std::string 布局 / 偏移, 返回第一个读得出全 ASCII 的
function readStrTry(p) {
  const out = [];
  // (A) libc++ 64-bit: size_t 在 offset 0, bit0=1 表示 long
  try {
    const sz = p.readU64();
    const len = Number(sz >> 1n);
    if (len > 0 && len <= 200) {
      if ((sz & 1) === 0) out.push(p.add(1).readUtf8String(len));       // short: data@1
      const ptr = p.add(16).readPointer();                              // long: data@16
      if (ptr) out.push(ptr.readUtf8String(len));
    }
  } catch (e) {}
  // (B) size_t 在 offset 8
  try {
    const sz = p.add(8).readU64();
    const len = Number(sz >> 1n);
    if (len > 0 && len <= 200) {
      if ((sz & 1) === 0) out.push(p.add(1).readUtf8String(len));
      const ptr = p.add(16).readPointer();
      if (ptr) out.push(ptr.readUtf8String(len));
    }
  } catch (e) {}
  // (C) 裸指针在 offset 0/8/16/24, 内容长度靠 C 字符串
  for (const off of [0, 8, 16, 24]) {
    try {
      const ptr = p.add(off).readPointer();
      if (ptr) { const s = ptr.readCString(); if (s) out.push(s); }
    } catch (e) {}
  }
  // (D) inline 数据: offset 1/9/17/25 起始, 长度取前 8 字节的若干候选
  for (const lenOff of [0, 8]) {
    try {
      const raw = p.add(lenOff).readU64();
      for (const len of [Number(raw >> 1n), Number(raw & 0x7f), Number(raw)]) {
        if (len > 0 && len <= 200) {
          for (const dataOff of [1, 9, 17, 25]) {
            try { out.push(p.add(dataOff).readUtf8String(len)); } catch (e) {}
          }
        }
      }
    } catch (e) {}
  }
  for (const s of out) if (printable(s)) return s;
  return null;
}

let lastLiteral = null;   // make_str 刚构造的字面量
const litRing = [];       // 最近 6 个字面量
let pendingKey = null;    // set_value 即将用的 key

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

      // 1) 字面量: 命令名(带 '.')与字段名
      hook(OFF.MAKE_STR, 'make_str', {
        onEnter(args) {
          let s = null;
          try { s = args[1].readCString(); } catch (e) {}
          if (!s || s.length < 2 || s.length > 60) return;
          if (!/^[A-Za-z0-9_.]+$/.test(s)) return;
          lastLiteral = s;
          // 环形缓冲: 最近的 6 个字面量, 供字段事件回溯命令名
          litRing.push(s);
          if (litRing.length > 6) litRing.shift();
        }
      });

      // 2) set(obj, key, SFSValue*)
      hook(OFF.SET_VALUE, 'set_value', {
        onEnter(args) {
          const key = lastLiteral || readStrTry(args[1]);
          if (!key) return;
          pendingKey = key;
          let ival = null, raw = null, sval = null;
          try { ival = args[2].add(0x30).readS32(); } catch (e) {}
          if (KEYS[key] || key === 'type' || key === 'op') {
            try { raw = hexOf(args[2].readByteArray(64)); } catch (e) {}
            try { sval = readStrTry(args[2].add(0x8)); } catch (e) {}
            emit({ t: 'field', key: key, ival: ival, sval: sval, raw: raw,
                   lits: litRing.slice() });
          }
        }
      });

      // 3) get_string(std::string*) -> 字符串字段的值
      hook(OFF.GET_STR, 'get_str', {
        onEnter(args) {
          // 反汇编顺序: make_str(key) -> get_string(value) -> set_value(key, value)
          // 所以这里要用 lastLiteral(刚 make 出来的 key), 不能用 pendingKey
          const key = lastLiteral;
          if (!key || !KEYS[key]) return;
          const v = readStrTry(args[0]);
          if (!v) return;
          emit({ t: 'value', key: key, value: v, lits: litRing.slice() });
        }
      });

      // 4) set_str(obj, key, const char*) —— 0x8fb620 是 PLT, 从 GOT 取真实地址
      try {
        const real = base.add(OFF.GOT_SET_STR).readPointer();
        if (real && !real.isNull()) {
          Interceptor.attach(real, {
            onEnter(args) {
              const key = lastLiteral || readStrTry(args[1]);
              if (!key) return;
              let val = null;
              try { val = args[2].readCString(); } catch (e) {}
              if (!key) return;
              if (KEYS[key]) emit({ t: 'field_str', key: key, value: val, lits: litRing.slice() });
              else if (val && val.length) emit({ t: 'field_other', key: key, value: val, lits: litRing.slice() });
            }
          });
          emit({ t: 'hooked', name: 'set_str_real', addr: real.toString() });
        }
      } catch (e) { emit({ t: 'hook_err', name: 'set_str_real', msg: String(e) }); }

      emit({ t: 'script_loaded', pid: Process.id });
    }, 600);
  }
});
