'use strict';
/*
 * COK / Sfs2X runtime hook
 * 目标:
 *   1) EVP_CipherInit_ex -> 抓 AES-128-CBC 的 key / IV
 *   2) EVP_CipherUpdate   -> 抓明文(in=明文当加密, out=明文当解密)与密文
 *   3) DefaultPacketEncrypter::{Decrypt,Encrypt} -> 确认 SFS 层是否真的走 AES
 *   4) ExtensionRequest::Init -> 抓命令名 + IsEncrypted(+0x60) 布尔位
 *   5) PacketHeader::Encrypted / ToString -> 抓封包头标志位
 *   6) CryptoKey::Key / IV -> 抓握手下发的密钥对象
 */

const MAXDUMP = 512;
const counts = {};
const ctxEnc = new Map();
const seenBufs = new Set();
let dumpBudget = 4000;   // 限制总 dump 次数,避免刷屏
let payloadBudget = 6 * 1024 * 1024;

function hexOf(buf) {
  const u8 = new Uint8Array(buf);
  let s = '';
  for (let i = 0; i < u8.length; i++) s += ('0' + u8[i].toString(16)).slice(-2);
  return s;
}

function hexAt(p, n) {
  try {
    if (p === null || p === undefined || p.isNull()) return null;
    return hexOf(p.readByteArray(n));
  } catch (e) {
    return null;
  }
}

function asciiAt(p, n) {
  try {
    if (p === null || p === undefined || p.isNull()) return null;
    const u8 = new Uint8Array(p.readByteArray(n));
    let s = '';
    for (let i = 0; i < u8.length; i++) {
      const c = u8[i];
      s += (c >= 0x20 && c < 0x7f) ? String.fromCharCode(c) : '.';
    }
    return s;
  } catch (e) {
    return null;
  }
}

// libstdc++ std::string 读取: [0]=char* [8]=len [16]=SSO buffer
function readStdString(p) {
  try {
    if (!p || p.isNull()) return null;
    const dataPtr = p.readPointer();
    const len = p.add(8).readU32();
    if (len === 0 || len > 8192) return { len: len, text: null, note: 'len=' + len };
    const sso = dataPtr.equals(p.add(16));
    const base = sso ? p.add(16) : dataPtr;
    return { len: len, text: base.readUtf8String(len), sso: sso };
  } catch (e) {
    return null;
  }
}

function bump(tag) {
  counts[tag] = (counts[tag] || 0) + 1;
}

function emit(obj) {
  try { send(obj); } catch (e) {}
}

function hookExport(mod, name, handlers) {
  let p = null;
  try { p = mod.getExportByName(name); } catch (e) { p = null; }
  if (p === null) {
    emit({ t: 'hook_miss', name: name });
    return false;
  }
  try {
    Interceptor.attach(p, handlers);
    emit({ t: 'hooked', name: name, addr: p.toString() });
    return true;
  } catch (e) {
    emit({ t: 'hook_err', name: name, msg: String(e) });
    return false;
  }
}

function install(mod) {
  emit({ t: 'module', name: mod.name, base: mod.base.toString(), size: mod.size });

  // ---- 1) AES key / IV ----
  hookExport(mod, 'EVP_CipherInit_ex', {
    onEnter(args) {
      bump('EVP_CipherInit_ex');
      const ctx = args[0];
      const type = args[1];
      const key = args[3];
      const iv = args[4];
      const enc = args[5].toInt32();
      ctxEnc.set(ctx.toString(), enc);
      let bt = null;
      try {
        bt = Thread.backtrace(this.context, Backtracer.ACCURATE)
          .slice(0, 8)
          .map(DebugSymbol.fromAddress)
          .map(String);
      } catch (e) { bt = null; }
      emit({
        t: 'cipher_init', enc: enc,
        key: hexAt(key, 32), iv: hexAt(iv, 32),
        key_ascii: asciiAt(key, 32), iv_ascii: asciiAt(iv, 32),
        ctx: ctx.toString(), arg2: args[2].toString(),
        cipher_name: (function () {
          try { return type.readPointer().readCString(); } catch (e) { return null; }
        })(),
        bt: bt
      });
    }
  });

  // ---- 2) 明文/密文流 ----
  hookExport(mod, 'EVP_CipherUpdate', {
    onEnter(args) {
      this.ctx = args[0].toString();
      this.out = args[1];
      this.outLenPtr = args[2];
      this.inp = args[3];
      this.inLen = args[4].toInt32();
    },
    onLeave(ret) {
      bump('EVP_CipherUpdate');
      const enc = ctxEnc.has(this.ctx) ? ctxEnc.get(this.ctx) : -1;
      let written = 0;
      try { written = this.outLenPtr.readU32(); } catch (e) { written = 0; }
      const show = dumpBudget > 0 && payloadBudget > 0;
      if (show) { dumpBudget--; payloadBudget -= (this.inLen + written); }
      if (!show) return;
      emit({
        t: 'cipher_update', enc: enc,
        in_len: this.inLen,
        in_hex: hexAt(this.inp, Math.min(this.inLen, MAXDUMP)),
        in_ascii: asciiAt(this.inp, Math.min(this.inLen, MAXDUMP)),
        out_len: written,
        out_hex: hexAt(this.out, Math.min(written, MAXDUMP)),
        out_ascii: asciiAt(this.out, Math.min(written, MAXDUMP))
      });
    }
  });

  hookExport(mod, 'EVP_CipherFinal', {
    onEnter(args) { this.out = args[1]; this.outLenPtr = args[2]; this.ctx = args[0].toString(); },
    onLeave(ret) {
      bump('EVP_CipherFinal');
      let written = 0;
      try { written = this.outLenPtr.readU32(); } catch (e) { written = 0; }
      if (dumpBudget <= 0) return;
      dumpBudget--;
      emit({
        t: 'cipher_final',
        enc: ctxEnc.has(this.ctx) ? ctxEnc.get(this.ctx) : -1,
        out_len: written,
        out_hex: hexAt(this.out, Math.min(written, MAXDUMP)),
        out_ascii: asciiAt(this.out, Math.min(written, MAXDUMP))
      });
    }
  });

  // ---- 3) SFS 层是否真的加密 ----
  const encDec = '_ZN5Sfs2X4Core22DefaultPacketEncrypter7DecryptEN5boost10shared_ptrINS_4Util9ByteArrayEEE';
  const encEnc = '_ZN5Sfs2X4Core22DefaultPacketEncrypter7EncryptEN5boost10shared_ptrINS_4Util9ByteArrayEEE';
  hookExport(mod, encDec, { onEnter() { bump('DefaultPacketEncrypter::Decrypt'); emit({ t: 'encrypter', op: 'Decrypt' }); } });
  hookExport(mod, encEnc, { onEnter() { bump('DefaultPacketEncrypter::Encrypt'); emit({ t: 'encrypter', op: 'Encrypt' }); } });

  // ---- 4) 命令名 + IsEncrypted 位 ----
  const extInit = '_ZN5Sfs2X8Requests16ExtensionRequest4InitESsN5boost10shared_ptrINS_8Entities4Data10ISFSObjectEEENS3_INS4_4RoomEEEb';
  hookExport(mod, extInit, {
    onEnter(args) {
      bump('ExtensionRequest::Init');
      const cmd = readStdString(args[1]);
      emit({
        t: 'ext_request_init',
        cmd: cmd ? cmd.text : null,
        cmd_len: cmd ? cmd.len : null,
        is_encrypted: args[4].toInt32() & 1,
        raw_cmd_ptr: args[1].toString(),
        raw_bytes: hexAt(args[1], 40)
      });
    }
  });

  const loginInit = '_ZN5Sfs2X8Requests12LoginRequest4InitESsSsSsN5boost10shared_ptrINS_8Entities4Data10ISFSObjectEEE';
  hookExport(mod, loginInit, {
    onEnter(args) {
      bump('LoginRequest::Init');
      const u = readStdString(args[1]);
      const pwd = readStdString(args[2]);
      const zone = readStdString(args[3]);
      emit({
        t: 'login_request_init',
        user: u ? u.text : null,
        zone: zone ? zone.text : null,
        has_password: !!(pwd && pwd.text && pwd.text.length)
      });
    }
  });

  // ---- 5) 封包头标志位 ----
  hookExport(mod, '_ZN5Sfs2X4Core12PacketHeader9EncryptedEv', {
    onEnter(args) { this.h = args[0]; },
    onLeave(ret) {
      bump('PacketHeader::Encrypted');
      emit({ t: 'header_encrypted', value: ret.toInt32() & 1, hdr: this.h.toString() });
    }
  });
  hookExport(mod, '_ZN5Sfs2X4Core12PacketHeader10ToStringEv', {
    onEnter(args) { this.sret = args[0]; this.h = args[1]; },
    onLeave(ret) {
      bump('PacketHeader::ToString');
      const s = readStdString(this.sret);
      emit({ t: 'header_to_string', text: s ? s.text : null, hdr: this.h.toString() });
    }
  });

  // ---- 6) 握手下发的密钥对象 ----
  hookExport(mod, '_ZN5Sfs2X4Util9CryptoKey3KeyEv', {
    onEnter(args) { this.sret = args[0]; this.self = args[1]; },
    onLeave(ret) {
      bump('CryptoKey::Key');
      let ba = null;
      try { ba = this.sret.readPointer(); } catch (e) {}
      emit({ t: 'crypto_key', which: 'key', bytearray: ba ? ba.toString() : null });
    }
  });
  hookExport(mod, '_ZN5Sfs2X4Util9CryptoKey2IVEv', {
    onEnter(args) { this.sret = args[0]; this.self = args[1]; },
    onLeave(ret) {
      bump('CryptoKey::IV');
      let ba = null;
      try { ba = this.sret.readPointer(); } catch (e) {}
      emit({ t: 'crypto_key', which: 'iv', bytearray: ba ? ba.toString() : null });
    }
  });

  // 握手请求构造(拿到 zq/平台串)
  hookExport(mod, '_ZN5Sfs2X8Requests16HandshakeRequestC1ESsSsSs', {
    onEnter(args) {
      bump('HandshakeRequest::ctor');
      const a = readStdString(args[1]);
      const b = readStdString(args[2]);
      const c = readStdString(args[3]);
      emit({ t: 'handshake_request', a: a ? a.text : null, b: b ? b.text : null, c: c ? c.text : null });
    }
  });

  // ---- 7) 线上原始字节 (WriteTCP) ----
  hookExport(mod, '_ZN5Sfs2X4Core12SFSIOHandler8WriteTCPEN5boost10shared_ptrINS_4Util9ByteArrayEEE', {
    onEnter(args) { bump('SFSIOHandler::WriteTCP'); this.sp = args[1]; },
    onLeave(ret) {
      if (dumpBudget <= 0) return;
      dumpBudget--;
      let ba = null;
      try { ba = this.sp.readPointer(); } catch (e) {}
      emit({ t: 'write_tcp', bytearray: ba ? ba.toString() : null });
    }
  });

  hookExport(mod, '_ZN5Sfs2X4Core16SFSProtocolCodec16PrepareTCPPacketEN5boost10shared_ptrINS_8Bitswarm8IMessageEEE', {
    onEnter() { bump('SFSProtocolCodec::PrepareTCPPacket'); }
  });
  hookExport(mod, '_ZN5Sfs2X4Core12SFSIOHandler16HandlePacketDataEN5boost10shared_ptrINS_4Util9ByteArrayEEE', {
    onEnter() { bump('SFSIOHandler::HandlePacketData'); }
  });
  hookExport(mod, '_ZN5Sfs2X4Core16SFSProtocolCodec12OnPacketReadEN5boost10shared_ptrINS_4Util9ByteArrayEEE', {
    onEnter() { bump('SFSProtocolCodec::OnPacketRead'); }
  });

  emit({ t: 'installed' });
}

Process.attachModuleObserver({
  onAdded(module) {
    if (module.name === 'libgame.so') {
      setTimeout(function () { install(module); }, 0);
    }
  }
});

emit({ t: 'script_loaded', pid: Process.id, arch: Process.arch });
