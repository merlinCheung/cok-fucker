/*
 * 小七渠道(x7sy)登录抓取
 *
 * 目标: 把"小七账号密码 -> tokenkey -> 游戏身份"这条链路的**明文**全部捞出来,
 *       用来在纯 PC 复刻(不需要手机/模拟器/root)。
 *
 * 抓点(按价值排序):
 *   1. com.smwl.x7enc.XNetDealer.decryptResult   -> 响应明文 JSON(最值钱: 直接看到 tokenkey)
 *   2. com.smwl.x7enc.XNetDealer.getEncryptParams -> 请求明文参数 -> 加密后参数
 *   3. com.smwl.x7enc.XNetDealer.getEncryptUrl    -> 明文路径 -> 加密后 URL
 *   4. javax.crypto.spec.SecretKeySpec / IvParameterSpec -> AES 的 key/IV
 *   5. javax.crypto.Cipher.init/doFinal          -> 密文/明文对照
 *   6. com.smwl.smsdk.* 登录回调                   -> SMUserInfo.tokenkey
 *
 * 用法:
 *   python3 frida/frida_capture.py --pkg com.hcg.cok.ewanqf.x7sy \
 *       --script frida/capture_x7_login.js --seconds 180 --out /tmp/x7/x7login.jsonl
 */
'use strict';

function emit(t, payload) {
    payload = payload || {};
    payload.t = t;
    send(payload);
}

function safeStr(v) {
    try {
        if (v === null || v === undefined) return null;
        if (typeof v === 'string') return v.length > 4000 ? v.slice(0, 4000) + '...[trunc]' : v;
        return String(v);
    } catch (e) { return '<toString failed>'; }
}

function mapToObj(m) {
    // java.util.Map -> 普通对象
    // ⚠ 插件 classloader 里的 Map: 直接 m.entrySet() 会抛
    //   "TypeError: e.getKey is not a function"(跨 classloader 的方法调用问题)。
    //   解法: Java.cast 到 boot classpath 的 java.util.Map 再调 —— 跨 loader 是通的。
    var out = {};
    try {
        var mm = m;
        try {
            var MapCls = Java.use('java.util.Map');
            mm = Java.cast(m, MapCls);
        } catch (e0) { /* cast 失败就用原对象 */ }
        var it = mm.entrySet().iterator();
        while (it.hasNext()) {
            var e = it.next();
            var k, v;
            try { k = safeStr(e.getKey()); } catch (e1) { k = '<?>'; }
            try { v = e.getValue(); } catch (e2) { v = null; }
            var vs = null;
            try {
                if (v !== null && v.getClass) {
                    var cn = safeStr(v.getClass().getName());
                    if (cn.indexOf('java.lang.String') === 0) {
                        vs = safeStr(v);
                    } else if (cn.indexOf('byte[]') >= 0) {
                        vs = '<bytes ' + v.length + '>';
                    } else {
                        vs = safeStr(v);
                    }
                } else { vs = safeStr(v); }
            } catch (e3) { vs = '<err>'; }
            out[k] = vs;
        }
    } catch (e) {
        try { out['__toString'] = safeStr(m.toString()); } catch (e4) {}
        out['__err'] = safeStr(e);
    }
    return out;
}

// ⚠ 插件 classloader 返回的 Map: entrySet() 迭代在跨 loader 时会失败
//   (mapToObj 只能拿到 {"<?>": null})。但 **Map.get(key)** 是接口方法, 跨 loader 可用。
//   所以对已知 key 直接 get —— 这正是我们要的 {r,c,s,t}。
function mapGet(m, keys) {
    var out = {};
    try {
        var MapCls = Java.use('java.util.Map');
        var mm = Java.cast(m, MapCls);
        for (var i = 0; i < keys.length; i++) {
            try {
                var v = mm.get(keys[i]);
                if (v !== null && v !== undefined) out[keys[i]] = safeStr(v);
            } catch (e) {}
        }
        if (Object.keys(out).length === 0) {
            // 兜底: 用 toArray 拿全部 entry
            try {
                var arr = mm.entrySet().toArray();
                for (var j = 0; j < arr.length; j++) {
                    var e = arr[j];
                    out[safeStr(e.getKey())] = safeStr(e.getValue());
                }
            } catch (e2) {}
        }
    } catch (e) { out['__err'] = safeStr(e); }
    return out;
}

var PARAM_KEYS = ['r', 'c', 's', 't', 'url', 'originUrl', 'cache_key'];

Java.perform(function () {
    emit('installed', { note: 'java ready' });

    // ---------- 1) XNetDealer: 小七网络层 ----------
    try {
        var XND = Java.use('com.smwl.x7enc.XNetDealer');
        var dec = XND.decryptResult.overload('java.lang.String');
        dec.implementation = function (s) {
            var r = dec.call(this, s);
            emit('decrypt_result', {
                cipher: safeStr(s),
                plain: safeStr(r)
            });
            return r;
        };
        emit('hooked', { what: 'XNetDealer.decryptResult' });
    } catch (e) { emit('hook_fail', { what: 'decryptResult', err: safeStr(e) }); }

    try {
        var XND2 = Java.use('com.smwl.x7enc.XNetDealer');
        var geu = XND2.getEncryptUrl.overload('java.lang.String');
        geu.implementation = function (p) {
            var r = geu.call(this, p);
            emit('encrypt_url', { plain: safeStr(p), cipher: safeStr(r) });
            return r;
        };
        var geu2 = XND2.getEncryptUrl.overload('java.lang.String', 'java.lang.String');
        geu2.implementation = function (p, t) {
            var r = geu2.call(this, p, t);
            emit('encrypt_url_tag', { plain: safeStr(p), tag: safeStr(t), cipher: safeStr(r) });
            return r;
        };
        emit('hooked', { what: 'XNetDealer.getEncryptUrl' });
    } catch (e) { emit('hook_fail', { what: 'getEncryptUrl', err: safeStr(e) }); }

    try {
        var XND3 = Java.use('com.smwl.x7enc.XNetDealer');
        var gep = XND3.getEncryptParams.overload('java.util.Map');
        gep.implementation = function (m) {
            var r = gep.call(this, m);
            emit('encrypt_params', {
                plain: mapToObj(m),
                cipher: mapToObj(r)
            });
            return r;
        };
        emit('hooked', { what: 'XNetDealer.getEncryptParams' });
    } catch (e) { emit('hook_fail', { what: 'getEncryptParams', err: safeStr(e) }); }

    // ---------- 1b) XNetDealer 的 native 方法(Java bridge 可直接 hook native 方法) ----------
    // encryptNative / getUrlNative / getResultNative 是 JNI 动态注册的 native 方法,
    // 但 frida 的 Java bridge 能在 ART 层替换它们, 于是**明文**直接可读。
    try {
        var XNDn = Java.use('com.smwl.x7enc.XNetDealer');
        var encN = XNDn.encryptNative.overload('java.lang.String');
        encN.implementation = function (json) {
            var r = encN.call(this, json);
            emit('n_encryptNative', { plain: safeStr(json), cipher: safeStr(r) });
            return r;
        };
        var resN = XNDn.getResultNative.overload('java.lang.String');
        resN.implementation = function (s) {
            var r = resN.call(this, s);
            emit('n_getResultNative', { cipher: safeStr(s), plain: safeStr(r) });
            return r;
        };
        var urlN = XNDn.getUrlNative.overload('java.lang.String');
        urlN.implementation = function (p) {
            var r = urlN.call(this, p);
            emit('n_getUrlNative', { plain: safeStr(p), cipher: safeStr(r) });
            return r;
        };
        var tagN = XNDn.getUrlNativeTag.overload('java.lang.String', 'java.lang.String');
        tagN.implementation = function (p, t) {
            var r = tagN.call(this, p, t);
            emit('n_getUrlNativeTag', { plain: safeStr(p), tag: safeStr(t), cipher: safeStr(r) });
            return r;
        };
        var refN = XNDn.refreshNative.overload('java.lang.String');
        refN.implementation = function (s) {
            var r = refN.call(this, s);
            emit('n_refreshNative', { in: safeStr(s), out: safeStr(r) });
            return r;
        };
        emit('hooked', { what: 'XNetDealer native methods' });
    } catch (e) { emit('hook_fail', { what: 'XNetDealer native', err: safeStr(e) }); }

    // ---------- 1d) Md5Utils.encode: ★签名原文在这里 ----------
    // native 用 FindClass("com/smwl/x7enc/Md5Utils") 找这个类,
    // FindClass 用的是**加载 so 的那个 classloader**(游戏主 dex), 不是插件的。
    // 所以必须挂在默认 loader 上(插件那份由 classloader 轮询另行处理)。
    try {
        var MU = Java.use('com.smwl.x7enc.Md5Utils');
        var menc = MU.encode.overload('java.lang.String');
        menc.implementation = function (s) {
            var out = menc.call(this, s);
            emit('md5_input', { msg: safeStr(s), md5: safeStr(out) });
            return out;
        };
        emit('hooked', { what: 'Md5Utils.encode' });
    } catch (e) { emit('hook_fail', { what: 'Md5Utils', err: safeStr(e) }); }

    // ---------- 1c) 插件 classloader 里的 XNetDealer ----------
    // 小七 SDK 的登录逻辑在**动态下载的插件 dex** 里, 里面还有一份
    // com.smwl.x7enc.XNetDealer —— 真正被调用的是插件那份,
    // 只 hook 主 dex 的类拦不到(表现为 cipher_doFinal 有数据但 encrypt_url 没事件)。
    // 插件是**运行中才加载**的, 所以要周期性重扫, 把新出现的 classloader 也 hook 上。
    var hookedClasses = {};
    var hookedLoaders = {};
    function sweepLoaders(reason) {
        var loaders = {};
        try {
            Java.enumerateClassLoaders({
                onMatch: function (loader) { loaders[loader.toString()] = loader; },
                onComplete: function () {
                    var n = 0;
                    for (var key in loaders) {
                        var lk = key;
                        if (hookedClasses[lk]) continue;
                        var loader = loaders[lk];
                        try {
                            // ⚠ 插件 dex 里**自带一套 okhttp** —— 主 dex 的 okhttp3.Request$Builder
                            //   钩子拦不到插件发起的请求(表现为只抓到 parse.com)。
                            //   所以 okhttp 也要**按 classloader 逐个 hook**。
                            try {
                                var Bld = Java.ClassFactory.get(loader).use('okhttp3.Request$Builder');
                                var bld = Bld.build.overload();
                                bld.implementation = function () {
                                    var req = bld.call(this);
                                    try {
                                        emit('http_request', {
                                            method: safeStr(req.method()),
                                            url: safeStr(req.url().toString()),
                                            loader: lk
                                        });
                                    } catch (e) {}
                                    return req;
                                };
                            } catch (e) { /* 该 loader 没有 okhttp */ }
                            // ⚠ 表单的真实字段名/值在这里 —— 服务端 -210 就是字段不对。
                            //   FormBody.Builder.add(k,v) 是**明文**入口, 一次 hook 就能拿到。
                            try {
                                var FB = Java.ClassFactory.get(loader).use('okhttp3.FormBody$Builder');
                                var fadd = FB.add.overload('java.lang.String', 'java.lang.String');
                                fadd.implementation = function (k, v) {
                                    try {
                                        emit('form_add', { key: safeStr(k), value: safeStr(v), loader: lk });
                                    } catch (e) {}
                                    return fadd.call(this, k, v);
                                };
                            } catch (e) { /* 该 loader 没有 FormBody */ }
                            var XD = Java.ClassFactory.get(loader).use('com.smwl.x7enc.XNetDealer');
                            var eu = XD.getUrlNative.overload('java.lang.String');
                            eu.implementation = function (p) {
                                var r = eu.call(this, p);
                                emit('n_getUrlNative', { plain: safeStr(p), cipher: safeStr(r), loader: lk });
                                return r;
                            };
                            var eut = XD.getUrlNativeTag.overload('java.lang.String', 'java.lang.String');
                            eut.implementation = function (p, t) {
                                var r = eut.call(this, p, t);
                                emit('n_getUrlNativeTag', { plain: safeStr(p), tag: safeStr(t), cipher: safeStr(r), loader: lk });
                                return r;
                            };
                            var en = XD.encryptNative.overload('java.lang.String');
                            en.implementation = function (j) {
                                var r = en.call(this, j);
                                // 先发最原始的 toString —— 后面任何解析失败都不影响这条
                                try {
                                    emit('n_encryptNative_raw', { plain: safeStr(j), raw: String(r.toString()) });
                                } catch (e0) {}
                                emit('n_encryptNative', { plain: safeStr(j), cipher: mapGet(r, PARAM_KEYS), loader: lk });
                                return r;
                            };
                            // ★ 签名原文在这里: native 拼好签名串后调用 Md5Utils.encode(msg)
                            //   → msg 就是 MD5 的原文, 公式 = md5hex(msg)
                            try {
                                var MU = Java.ClassFactory.get(loader).use('com.smwl.x7enc.Md5Utils');
                                var menc = MU.encode.overload('java.lang.String');
                                menc.implementation = function (s) {
                                    var out = menc.call(this, s);
                                    emit('md5_input', { msg: safeStr(s), md5: safeStr(out), loader: lk });
                                    return out;
                                };
                            } catch (e) { /* 该 loader 没有 Md5Utils */ }
                            var gr = XD.getResultNative.overload('java.lang.String');
                            gr.implementation = function (s) {
                                var r = gr.call(this, s);
                                emit('n_getResultNative', { cipher: safeStr(s), plain: safeStr(r), loader: lk });
                                return r;
                            };
                            var eu2 = XD.getEncryptUrl.overload('java.lang.String');
                            eu2.implementation = function (p) {
                                var r = eu2.call(this, p);
                                emit('encrypt_url', { plain: safeStr(p), cipher: safeStr(r), loader: lk });
                                return r;
                            };
                            var ep = XD.getEncryptParams.overload('java.util.Map');
                            ep.implementation = function (m) {
                                var r = ep.call(this, m);
                                emit('encrypt_params', { plain: mapGet(m, PARAM_KEYS), cipher: mapGet(r, PARAM_KEYS), loader: lk });
                                return r;
                            };
                            var dr = XD.decryptResult.overload('java.lang.String');
                            dr.implementation = function (s) {
                                var r = dr.call(this, s);
                                emit('decrypt_result', { cipher: safeStr(s), plain: safeStr(r), loader: lk });
                                return r;
                            };
                            hookedClasses[lk] = true;
                            hookedLoaders[lk] = loader;
                            n++;
                        } catch (e) { /* 该 loader 没这个类 */ }
                    }
                    if (n > 0) emit('hooked', { what: 'XNetDealer in classloaders', n: n, reason: reason });
                }
            });
        } catch (e) { emit('hook_fail', { what: 'classloader sweep', err: safeStr(e) }); }
    }
    sweepLoaders('initial');
    setInterval(function () { sweepLoaders('poll'); }, 5000);

    // ---------- 自测: 主动调用 native encryptNative ----------
    // 目的: 不依赖游戏真实请求, 也能拿到 {r,c,s,t} 与 Md5Utils 的签名原文,
    //       这样就能在 PC 上直接反推签名公式。
    var selftestDone = false;
    function selfTest() {
        if (selftestDone) return;
        var keys = [];
        for (var k in hookedLoaders) keys.push(k);
        emit('selftest_start', { loaders: keys.length });
        // ⚠ BootClassLoader 里没有 com.smwl.x7enc.XNetDealer, 而且它的 static
        //   初始化会 System.loadLibrary → 在 boot loader 里必然 UnsatisfiedLinkError,
        //   会把整个脚本带崩。所以只挑真正加载插件的那个 loader。
        var order = [];
        for (var k1 in hookedLoaders) {
            if (k1.indexOf('PluginClassLoader') >= 0) order.push(k1);
        }
        for (var k2 in hookedLoaders) {
            if (order.indexOf(k2) < 0 && k2.indexOf('PathClassLoader') >= 0 &&
                k2.indexOf('com.hcg.cok') >= 0) order.push(k2);
        }
        for (var k3 in hookedLoaders) {
            if (order.indexOf(k3) < 0) order.push(k3);
        }
        for (var idx = 0; idx < order.length; idx++) {
            var lk = order[idx];
            try {
                emit('selftest_try', { loader: lk.substring(0, 70) });
                var XD = Java.ClassFactory.get(hookedLoaders[lk]).use('com.smwl.x7enc.XNetDealer');
                // 直接调静态 native, 绕开 getInstance()(<clinit> 里 System.loadLibrary)
                var json = '{"mid":"21921411","appkey":"e76922b1c512b2f1dc6035a6d38a0ff2"}';
                var res = XD.encryptNative(json);
                var raw = '';
                try { raw = String(res.toString()); } catch (e1) { raw = '<toString failed>'; }
                emit('selftest_raw', { raw: raw, loader: lk.substring(0, 70) });
                selftestDone = true;
                return;
            } catch (e) {
                emit('selftest_err', { err: safeStr(e), loader: lk.substring(0, 70) });
            }
        }
    }
    setTimeout(selfTest, 4000);
    setInterval(selfTest, 6000);

    // ---------- 2) AES key / IV ----------
    try {
        var SKS = Java.use('javax.crypto.spec.SecretKeySpec');
        var skInit = SKS.$init.overload('[B', 'java.lang.String');
        skInit.implementation = function (key, alg) {
            emit('aes_key', { alg: safeStr(alg), key_hex: bytesToHex(key) });
            return skInit.call(this, key, alg);
        };
        emit('hooked', { what: 'SecretKeySpec' });
    } catch (e) { emit('hook_fail', { what: 'SecretKeySpec', err: safeStr(e) }); }

    try {
        var IVS = Java.use('javax.crypto.spec.IvParameterSpec');
        var ivInit = IVS.$init.overload('[B');
        ivInit.implementation = function (iv) {
            emit('aes_iv', { iv_hex: bytesToHex(iv) });
            return ivInit.call(this, iv);
        };
        emit('hooked', { what: 'IvParameterSpec' });
    } catch (e) { emit('hook_fail', { what: 'IvParameterSpec', err: safeStr(e) }); }

    try {
        var CIP = Java.use('javax.crypto.Cipher');
        var cipInit = CIP.init.overload('int', 'java.security.Key', 'java.security.spec.AlgorithmParameterSpec');
        cipInit.implementation = function (mode, key, spec) {
            var extra = {};
            try {
                if (spec) {
                    extra.iv_hex = bytesToHex(spec.getIV());
                    extra.specClass = safeStr(spec.getClass().getName());
                }
                if (key) {
                    extra.keyClass = safeStr(key.getClass().getName());
                    extra.keyFormat = safeStr(key.getFormat());
                    try { extra.key_enc = safeStr(key.getEncoded()); } catch (e3) {}
                }
            } catch (e2) {}
            emit('cipher_init', { mode: mode, extra: extra });
            return cipInit.call(this, mode, key, spec);
        };
        var df = CIP.doFinal.overload('[B');
        df.implementation = function (b) {
            var r = df.call(this, b);
            emit('cipher_doFinal', { in_hex: bytesToHex(b), out_hex: bytesToHex(r) });
            return r;
        };
        emit('hooked', { what: 'Cipher' });
    } catch (e) { emit('hook_fail', { what: 'Cipher', err: safeStr(e) }); }

    // ---------- 3) 登录回调: tokenkey ----------
    try {
        var SML = Java.use('com.smwl.smsdk.abstrat.SMLoginListener');
        emit('hooked', { what: 'SMLoginListener(class present)' });
    } catch (e) { emit('hook_fail', { what: 'SMLoginListener', err: safeStr(e) }); }

    try {
        var SMU = Java.use('com.smwl.smsdk.bean.SMUserInfo');
        var gTk = SMU.getTokenkey.overload();
        gTk.implementation = function () {
            var v = gTk.call(this);
            emit('tokenkey', { tokenkey: safeStr(v) });
            return v;
        };
        emit('hooked', { what: 'SMUserInfo.getTokenkey' });
    } catch (e) { emit('hook_fail', { what: 'SMUserInfo', err: safeStr(e) }); }

    try {
        var SMU2 = Java.use('com.smwl.smsdk.appHostLib.SMUserInfo_appHostLib');
        var gTk2 = SMU2.getTokenkey.overload();
        gTk2.implementation = function () {
            var v = gTk2.call(this);
            emit('tokenkey_hostlib', { tokenkey: safeStr(v) });
            return v;
        };
        emit('hooked', { what: 'SMUserInfo_appHostLib.getTokenkey' });
    } catch (e) { emit('hook_fail', { what: 'SMUserInfo_appHostLib', err: safeStr(e) }); }

    // ---------- 3b) 密码哈希: MessageDigest ----------
    // 渠道 SDK 常把密码先 MD5/SHA 再加密. 这里抓 "被哈希的原文"(可能是明文密码)
    // 和算法名, 这样纯 PC 复刻时能原样照抄.
    //
    // ⚠ 签名(MD5)的输入是**分块** update 的, 且多个请求并发 —— 只看单块会拼错。
    //   所以按 digest 实例累积所有 update 的字节, 在 digest() 时一次性输出。
    var mdBuf = {};
    try {
        var MD = Java.use('java.security.MessageDigest');
        ['MD5', 'SHA-1', 'SHA-256'].forEach(function (alg) {
            try {
                var d = MD.getInstance.overload('java.lang.String');
                d.implementation = function (a) {
                    emit('digest_instance', { alg: safeStr(a) });
                    return d.call(this, a);
                };
            } catch (e) {}
        });
        var acc = function (key, b) {
            try {
                if (!mdBuf[key]) mdBuf[key] = [];
                mdBuf[key].push(b);
            } catch (e) {}
        };
        var upd = MD.update.overload('[B');
        upd.implementation = function (b) {
            try {
                var h = '';
                for (var i = 0; i < b.length; i++) h += ('0' + (b[i] & 0xff).toString(16)).slice(-2);
                emit('digest_update', { len: b.length, text: b.length < 300 ? h : h.slice(0, 300) + '...', hex: h });
                acc(String(this.hashCode()), b);
            } catch (e) {}
            return upd.call(this, b);
        };
        try {
            var upd2 = MD.update.overload('[B', 'int', 'int');
            upd2.implementation = function (b, off, len) {
                try {
                    var h = '';
                    for (var i = 0; i < b.length; i++) h += ('0' + (b[i] & 0xff).toString(16)).slice(-2);
                    acc(String(this.hashCode()), b);
                } catch (e) {}
                return upd2.call(this, b, off, len);
            };
        } catch (e) {}
        var dg = MD.digest.overload();
        dg.implementation = function () {
            var r = dg.call(this);
            try {
                var key = String(this.hashCode());
                var chunks = mdBuf[key] || [];
                var all = '';
                for (var i = 0; i < chunks.length; i++) {
                    var bb = chunks[i];
                    for (var j = 0; j < bb.length; j++) all += ('0' + (bb[j] & 0xff).toString(16)).slice(-2);
                }
                var oh = '';
                for (var k = 0; k < r.length; k++) oh += ('0' + (r[k] & 0xff).toString(16)).slice(-2);
                emit('digest_done', { out_hex: oh, in_hex: all, len: all.length / 2 });
                delete mdBuf[key];
            } catch (e) {}
            return r;
        };
        try {
            var dgb = MD.digest.overload('[B');
            dgb.implementation = function (b) {
                var r = dgb.call(this, b);
                try {
                    var oh = '';
                    for (var k = 0; k < r.length; k++) oh += ('0' + (r[k] & 0xff).toString(16)).slice(-2);
                    var h = '';
                    for (var i = 0; i < b.length; i++) h += ('0' + (b[i] & 0xff).toString(16)).slice(-2);
                    emit('digest_done', { out_hex: oh, in_hex: h, len: b.length });
                } catch (e) {}
                return r;
            };
        } catch (e) {}
        emit('hooked', { what: 'MessageDigest' });
    } catch (e) { emit('hook_fail', { what: 'MessageDigest', err: safeStr(e) }); }

    // ---------- 3c) SuperSDK 登录方法(方法体在加固壳里, 但 Java 层可 hook) ----------
    try {
        var V = Java.use('cn.ewan.supersdk.a.v');
        var vnames = V.class.getDeclaredMethods();
        var hooked = 0;
        for (var i = 0; i < vnames.length; i++) {
            (function (m) {
                var mn = m.getName();
                var ov = m.getParameterTypes();
                var sig = ov.map(function (t) { return t.getName(); }).join(',');
                try {
                    var ovl = V[mn].overload.apply(V[mn], ov);
                    ovl.implementation = function () {
                        var args = [];
                        for (var k = 0; k < arguments.length; k++) {
                            var a = arguments[k];
                            var t = 'null';
                            if (a !== null && a !== undefined) {
                                try { t = safeStr(a); } catch (e2) { t = '<err>'; }
                            }
                            args.push(t);
                        }
                        emit('supersdk_call', { method: mn, sig: sig, args: args });
                        return ovl.apply(this, arguments);
                    };
                    hooked++;
                } catch (e) {}
            })(vnames[i]);
        }
        emit('hooked', { what: 'cn.ewan.supersdk.a.v', n: hooked });
    } catch (e) { emit('hook_fail', { what: 'supersdk.v', err: safeStr(e) }); }

    try {
        var SL = Java.use('cn.ewan.supersdk.open.SuperLogin');
        ['getOpenId', 'getToken', 'getSign', 'getUsername', 'getUn', 'isAuthenticated', 'isNewUser'].forEach(function (n) {
            try {
                var m = SL[n].overload('int');
                m.implementation = function (i) {
                    var v = m.call(this, i);
                    emit('superlogin', { field: n, value: safeStr(v) });
                    return v;
                };
                var m0 = SL[n].overload();
                m0.implementation = function () {
                    var v = m0.call(this);
                    emit('superlogin', { field: n, value: safeStr(v) });
                    return v;
                };
            } catch (e) {}
        });
        emit('hooked', { what: 'SuperLogin getters' });
    } catch (e) { emit('hook_fail', { what: 'SuperLogin', err: safeStr(e) }); }

    // ---------- 4) HTTP 请求(拿到真实 URL + 表单体) ----------
    try {
        var B = Java.use('okhttp3.Request$Builder');
        var build = B.build.overload();
        build.implementation = function () {
            var req = build.call(this);
            try {
                emit('http_request', {
                    method: safeStr(req.method()),
                    url: safeStr(req.url().toString())
                });
            } catch (e) {}
            return req;
        };
        emit('hooked', { what: 'okhttp Request.Builder.build' });
    } catch (e) { emit('hook_fail', { what: 'okhttp', err: safeStr(e) }); }

    // ---------- 4b) HttpURLConnection: 拿真实 URL / method / header ----------
    // 小七平台 SDK 的网络层不走 okhttp(抓包只看到 parse.com),
    // 走的是 HttpURLConnection。IV 极可能放在 query 或 header 里, 必须拿到。
    try {
        var HUC = Java.use('java.net.HttpURLConnection');
        var gOS = HUC.getOutputStream.overload();
        gOS.implementation = function () {
            try {
                var hdrs = {};
                try {
                    var it = this.getRequestProperties().entrySet().iterator();
                    while (it.hasNext()) {
                        var e = it.next();
                        hdrs[safeStr(e.getKey())] = safeStr(e.getValue());
                    }
                } catch (e2) {}
                emit('http_conn', {
                    url: safeStr(this.getURL().toString()),
                    method: safeStr(this.getRequestMethod()),
                    headers: hdrs
                });
            } catch (e) {}
            return gOS.call(this);
        };
        // setRequestProperty: 单独记一遍(有些 header 在 connect 前设)
        try {
            var sRP = HUC.setRequestProperty.overload('java.lang.String', 'java.lang.String');
            sRP.implementation = function (k, v) {
                try {
                    emit('http_header', {
                        url: safeStr(this.getURL().toString()),
                        key: safeStr(k),
                        value: safeStr(v)
                    });
                } catch (e) {}
                return sRP.call(this, k, v);
            };
        } catch (e2) {}
        emit('hooked', { what: 'HttpURLConnection' });
    } catch (e) { emit('hook_fail', { what: 'HttpURLConnection', err: safeStr(e) }); }

    // ---------- 4c) java.net.URL.openConnection: 拿 base url ----------
    try {
        var JU = Java.use('java.net.URL');
        var oc = JU.openConnection.overload();
        oc.implementation = function () {
            try {
                emit('url_open', { url: safeStr(this.toString()) });
            } catch (e) {}
            return oc.call(this);
        };
        emit('hooked', { what: 'java.net.URL.openConnection' });
    } catch (e) { emit('hook_fail', { what: 'URL.openConnection', err: safeStr(e) }); }

    // ---------- 4d) 请求体: OutputStream.write ----------
    // 兜底: 平台 SDK 若用 OutputStream 写 body, 这里能看到发出去的字节
    try {
        var DOS = Java.use('java.io.DataOutputStream');
        var wr = DOS.write.overload('[B');
        wr.implementation = function (b) {
            try {
                var s = '';
                for (var i = 0; i < b.length && i < 4096; i++) s += String.fromCharCode(b[i] & 0xff);
                if (s && /[A-Za-z]{3,}/.test(s)) {
                    emit('stream_write', { len: b.length, text: s.slice(0, 2000) });
                }
            } catch (e) {}
            return wr.call(this, b);
        };
        emit('hooked', { what: 'DataOutputStream.write' });
    } catch (e) { emit('hook_fail', { what: 'DataOutputStream', err: safeStr(e) }); }

    // ---------- 5) 角色信息(游戏侧回填) ----------
    try {
        var RI = Java.use('com.smwl.smsdk.bean.RoleInfo');
        var names = ['getGame_guid', 'getGame_role_id', 'getGame_role_name',
                     'getGame_area', 'getGame_area_id', 'getRoleLevel'];
        names.forEach(function (n) {
            try {
                var m = RI[n].overload();
                m.implementation = function () {
                    var v = m.call(this);
                    emit('role_info', { field: n, value: safeStr(v) });
                    return v;
                };
            } catch (e) {}
        });
        emit('hooked', { what: 'RoleInfo getters' });
    } catch (e) { emit('hook_fail', { what: 'RoleInfo', err: safeStr(e) }); }

    emit('ready', { done: true });
});

function bytesToHex(b) {
    try {
        if (b === null || b === undefined) return null;
        var n = b.length;
        var out = '';
        for (var i = 0; i < n; i++) {
            var v = b[i] & 0xff;
            var h = v.toString(16);
            out += (h.length === 1 ? '0' : '') + h;
        }
        return out;
    } catch (e) { return null; }
}
