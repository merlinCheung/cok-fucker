/*
 * 只 hook 插件 PluginClassLoader 的 UserHttpApi2(它 dex 在内存里)
 * 不做自测 / 不轮询, 避免崩
 */
'use strict';
function emit(p) { try { send(p); } catch (e) {} }
function safeStr(v) {
    try { if (v === null || v === undefined) return null; var s = String(v);
        return s.length > 4000 ? s.slice(0, 4000) + '...[trunc]' : s; }
    catch (e) { return '<err>'; }
}
Java.perform(function () {
    var done = {};
    Java.enumerateClassLoaders({
        onMatch: function (loader) {
            var name = loader.toString();
            if (name.indexOf('PluginClassLoader') < 0 && name.indexOf('DynamicRuntime') < 0) return;
            if (done[name]) return;
            try {
                var f = Java.ClassFactory.get(loader);
                var H = f.use('com.hcg.utils.UserHttpApi2');
                H.getApi2Body.overload('java.lang.String', 'java.lang.String', 'boolean',
                    'okhttp3.Callback', 'java.util.Map')
                    .implementation = function (url, j, post, cb, m) {
                        emit({ ev: 'api2', url: safeStr(url), post: post });
                        return this.getApi2Body(url, j, post, cb, m);
                    };
                // 顺手 hook FormBody.Builder.add —— 表单明文
                try {
                    var FB = f.use('okhttp3.FormBody$Builder');
                    var fadd = FB.add.overload('java.lang.String', 'java.lang.String');
                    fadd.implementation = function (k, v) {
                        emit({ ev: 'form', key: safeStr(k), value: safeStr(v) });
                        return fadd.call(this, k, v);
                    };
                } catch (e2) {}
                done[name] = true;
                emit({ ev: 'hooked', loader: name.substring(0, 90) });
            } catch (e) { /* 没这个类 */ }
        },
        onComplete: function () { emit({ ev: 'sweep_done' }); }
    });
});