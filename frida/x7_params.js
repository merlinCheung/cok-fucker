/*
 * 只 hook XNetDealer.getEncryptParams(Map) —— 请求参数明文直接可读
 * 不带自测、不带轮询, 避免插件类把脚本带崩
 */
'use strict';
function emit(p) { try { send(p); } catch (e) {} }
function safeStr(v) {
    try { if (v === null || v === undefined) return null; var s = String(v);
        return s.length > 4000 ? s.slice(0, 4000) + '...[trunc]' : s; }
    catch (e) { return '<err>'; }
}
function mapGet(m, keys) {
    var out = {};
    try {
        var mm = Java.cast(m, Java.use('java.util.Map'));
        for (var i = 0; i < keys.length; i++) {
            try { var v = mm.get(keys[i]); if (v !== null && v !== undefined) out[keys[i]] = safeStr(v); } catch (e) {}
        }
    } catch (e) { out.__err = safeStr(e); }
    return out;
}
Java.perform(function () {
    var done = {};
    Java.enumerateClassLoaders({
        onMatch: function (loader) {
            var name = loader.toString();
            if (done[name]) return;
            try {
                var XD = Java.ClassFactory.get(loader).use('com.smwl.x7enc.XNetDealer');
                var ep = XD.getEncryptParams.overload('java.util.Map');
                ep.implementation = function (m) {
                    var r = ep.call(this, m);
                    emit({ ev: 'encrypt_params',
                           plain: mapGet(m, ['url','originUrl','pf','channel','user_account','pfId','cache_key','r','c','s','t','sign']),
                           cipher: mapGet(r, ['url','originUrl','pf','channel','user_account','pfId','cache_key','r','c','s','t','sign']) });
                    return r;
                };
                done[name] = true;
                emit({ ev: 'hooked', loader: name.substring(0, 80) });
            } catch (e) { /* 没这个类 */ }
        },
        onComplete: function () { emit({ ev: 'sweep_done', n: Object.keys(done).length }); }
    });
});