'use strict';
/*
 * 抓 COK 游戏服 BlowFish 参数加密:
 *   1) BF_set_key (libgame.so, OpenSSL BlowFish)  -> 直接拿到密钥字节
 *   2) org.cocos2dx.ext.Native.nativeData       -> 请求侧: 入参=明文 params, 出参=密文
 *   3) org.cocos2dx.ext.Native.BlowFishDecrypt  -> 响应侧: 入参=密文, 出参=明文
 *   4) org.hcg.IF.NetClient.send                -> 命令名 + 加密前 params
 */
function hexOf(buf) {
  const u8 = new Uint8Array(buf);
  let s = '';
  for (let i = 0; i < u8.length; i++) s += ('0' + u8[i].toString(16)).slice(-2);
  return s;
}
function emit(o) { try { send(o); } catch (e) {} }

// ---------- 1) native: BF_set_key -> 密钥 ----------
function hookNative(mod, name, handlers) {
  let p = null;
  try { p = mod.getExportByName(name); } catch (e) { p = null; }
  if (!p) { emit({ t: 'hook_miss', name: name, mod: mod.name }); return; }
  try { Interceptor.attach(p, handlers); emit({ t: 'hooked', name: name, mod: mod.name, addr: p.toString() }); }
  catch (e) { emit({ t: 'hook_err', name: name, msg: String(e) }); }
}

Process.attachModuleObserver({
  onAdded(module) {
    if (module.name !== 'libgame.so') return;
    setTimeout(function () {
      // BF_set_key(BF_KEY *key, int len, const unsigned char *data)
      hookNative(module, 'BF_set_key', {
        onEnter(args) {
          const len = args[1].toInt32();
          let hex = null, ascii = null;
          try {
            const b = args[2].readByteArray(Math.min(len, 128));
            hex = hexOf(b);
            const u8 = new Uint8Array(b);
            ascii = Array.from(u8).map(c => (c >= 0x20 && c < 0x7f) ? String.fromCharCode(c) : '.').join('');
          } catch (e) {}
          emit({ t: 'bf_set_key', len: len, key_hex: hex, key_ascii: ascii });
        }
      });
      hookNative(module, 'BF_encrypt', {
        onEnter(args) {
          // BF_encrypt(BF_KEY *key, uint32_t *data, int rounds)
          let hex = null;
          try { hex = hexOf(args[1].readPointer().readByteArray(8)); } catch (e) {}
          emit({ t: 'bf_encrypt', data_head: hex, rounds: args[2].toInt32() });
        }
      });
      hookNative(module, 'BF_decrypt', {
        onEnter(args) {
          let hex = null;
          try { hex = hexOf(args[1].readPointer().readByteArray(8)); } catch (e) {}
          emit({ t: 'bf_decrypt', data_head: hex, rounds: args[2].toInt32() });
        }
      });
    }, 0);
  }
});

// ---------- 2/3/4) Java 层 ----------
function jbytesToHex(b) {
  if (b === null || b === undefined) return null;
  try {
    const a = Java.array('byte', b);
    let s = '';
    for (let i = 0; i < a.length; i++) {
      const v = a[i] & 0xff;
      s += ('0' + v.toString(16)).slice(-2);
    }
    return s;
  } catch (e) { return null; }
}

try {
  Java.perform(function () {
    try {
      const Native = Java.use('org.cocos2dx.ext.Native');

      // 请求侧加密: nativeData(byte[]) -> byte[]
      if (Native.nativeData) {
        const orig = Native.nativeData;
        Native.nativeData.implementation = function (arr) {
          const inHex = jbytesToHex(arr);
          const out = orig.call(this, arr);
          emit({ t: 'nativeData', in_hex: inHex, out_hex: jbytesToHex(out) });
          return out;
        };
        emit({ t: 'hooked', name: 'org.cocos2dx.ext.Native.nativeData' });
      }

      // 响应侧解密: BlowFishDecrypt(byte[]) -> byte[]
      if (Native.BlowFishDecrypt) {
        const orig2 = Native.BlowFishDecrypt;
        Native.BlowFishDecrypt.implementation = function (arr) {
          const inHex = jbytesToHex(arr);
          const out = orig2.call(this, arr);
          emit({ t: 'blowfish_decrypt', in_hex: inHex, out_hex: jbytesToHex(out) });
          return out;
        };
        emit({ t: 'hooked', name: 'org.cocos2dx.ext.Native.BlowFishDecrypt' });
      }
    } catch (e) {
      emit({ t: 'java_hook_err', msg: String(e) });
    }

    // NetClient.send(cmd, params)
    try {
      const NetClient = Java.use('org.hcg.IF.NetClient');
      const send = NetClient.send.overload('java.lang.String', 'com.smartfoxserver.v2.entities.data.ISFSObject');
      send.implementation = function (cmd, params) {
        let plain = null, keys = null;
        try {
          plain = jbytesToHex(params.toBinary());
        } catch (e) {}
        try {
          const k = params.getKeys();
          const it = k.iterator();
          keys = [];
          while (it.hasNext()) keys.push(String(it.next()));
        } catch (e) {}
        emit({ t: 'net_send', cmd: String(cmd), keys: keys, params_plain_hex: plain });
        return send.call(this, cmd, params);
      };
      emit({ t: 'hooked', name: 'org.hcg.IF.NetClient.send' });
    } catch (e) {
      emit({ t: 'java_send_err', msg: String(e) });
    }
  });
} catch (e) {
  emit({ t: 'java_err', msg: String(e) });
}

emit({ t: 'script_loaded', pid: Process.id });
