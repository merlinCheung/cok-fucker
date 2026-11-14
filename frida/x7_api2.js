/*
 * 极简抓包: 逐个 classloader 找 UserHttpApi2 并 hook getApi2Body。
 * 不做自测 / 不轮询(只扫一次), 避免插件类把脚本带崩。
 */
'use strict';

function emit(p) { try { send(p); } catch (e) {} }
function safeStr(v) {
    try { if (v === null || v === undefined) return null; var s = String(v);
        return s.length > 4000 ? s.slice(0, 4000) + '...[trunc]' : s; }
    catch (e) { return '<err>'; }
}

Java.perform(function () {
    emit({ ev: 'installed' });
    var seen = 0;
    Java.enumerateClassLoaders({
        onMatch: function (loader) {
            try {
                var f = Java.ClassFactory.get(loader);
                var H = f.use('com.hcg.utils.UserHttpApi2');
                seen++;
                H.getApi2Body.overload('java.lang.String', 'java.lang.String', 'boolean',
                    'okhttp3.Callback', 'java.util.Map')
                    .implementation = function (url, j, post, cb, m) {
                        emit({ ev: 'api2', url: safeStr(url), post: post,
                               loader: loader.toString().substring(0, 60) });
                        return this.getApi2Body(url, j, post, cb, m);
                    };
                emit({ ev: 'hooked', loader: loader.toString().substring(0, 80) });
            } catch (e) { /* 该 loader 没这个类 */ }
        },
        onComplete: function () { emit({ ev: 'sweep_done', hits: seen }); }
    });
});