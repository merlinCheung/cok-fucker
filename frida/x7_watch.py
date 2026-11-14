#!/usr/bin/env python3
"""小七登录抓包 —— 带进程重启自动重挂。

用法: python3 frida/x7_watch.py --pkg com.hcg.cok.ewanqf.x7sy --seconds 900 --out /tmp/x7watch.jsonl
"""
import argparse
import json
import subprocess
import sys
import time

import frida
from frida_capture import preload_bridge

SCRIPT = r"""
'use strict';
function emit(p) { try { send(p); } catch (e) {} }
function safeStr(v) {
    try { if (v === null || v === undefined) return null; var s = String(v);
        return s.length > 6000 ? s.slice(0, 6000) + '...[trunc]' : s; }
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
    emit({ ev: 'ready', note: 'java ready' });
    var done = {};
    Java.enumerateClassLoaders({
        onMatch: function (loader) {
            var nm = loader.toString();
            if (done[nm]) return;
            try {
                var f = Java.ClassFactory.get(loader);
                var XD = f.use('com.smwl.x7enc.XNetDealer');
                // 1) 请求参数明文(★ pfId / logindata 在这里)
                var ep = XD.getEncryptParams.overload('java.util.Map');
                ep.implementation = function (m) {
                    var r = ep.call(this, m);
                    emit({ ev: 'encrypt_params',
                           plain: mapGet(m, ['logindata','loginpass','user_from','is_simulator',
                                             'isManualLogin','originUrl','ngid','mid','pf','channel',
                                             'pfId','user_account','guid','appkey','url']),
                           cipher: mapGet(r, ['r','c','s','t','url','originUrl']) });
                    return r;
                };
                // 2) native 加密前的明文
                var en = XD.encryptNative.overload('java.lang.String');
                en.implementation = function (j) {
                    var r = en.call(this, j);
                    emit({ ev: 'encrypt_native', plain: safeStr(j), cipher: mapGet(r, ['r','c','s','t']) });
                    return r;
                };
                // 3) 响应明文
                var gr = XD.getResultNative.overload('java.lang.String');
                gr.implementation = function (s) {
                    var r = gr.call(this, s);
                    emit({ ev: 'result_native', cipher: safeStr(s), plain: safeStr(r) });
                    return r;
                };
                // 4) URL
                var eu = XD.getUrlNative.overload('java.lang.String');
                eu.implementation = function (p) {
                    var r = eu.call(this, p);
                    emit({ ev: 'url_native', plain: safeStr(p), cipher: safeStr(r) });
                    return r;
                };
                // 5) 表单明文
                try {
                    var FB = f.use('okhttp3.FormBody$Builder');
                    var fadd = FB.add.overload('java.lang.String', 'java.lang.String');
                    fadd.implementation = function (k, v) {
                        emit({ ev: 'form', key: safeStr(k), value: safeStr(v) });
                        return fadd.call(this, k, v);
                    };
                } catch (e2) {}
                done[nm] = true;
                emit({ ev: 'hooked', loader: nm.substring(0, 90) });
            } catch (e) { /* 没这个类 */ }
        },
        onComplete: function () { emit({ ev: 'sweep_done', n: Object.keys(done).length }); }
    });
});
"""


def adb(*args):
    return subprocess.run(["adb", *args], capture_output=True, text=True).stdout.strip()


def pid_of(pkg):
    out = adb("shell", "pidof", pkg)
    return int(out.split()[0]) if out else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pkg", default="com.hcg.cok.ewanqf.x7sy")
    ap.add_argument("--seconds", type=int, default=900)
    ap.add_argument("--out", default="/tmp/x7watch.jsonl")
    args = ap.parse_args()

    fh = open(args.out, "w", encoding="utf-8")

    def on_message(msg, _data):
        fh.write(json.dumps({"ts": time.time(), "msg": msg}, ensure_ascii=False) + "\n")
        fh.flush()

    deadline = time.time() + args.seconds
    session = None
    script = None
    last_attached = None

    while time.time() < deadline:
        pid = pid_of(args.pkg)
        if pid is None:
            if session:
                try: session.detach()
                except Exception: pass
                session = script = None
                last_attached = None
                print("[watch] app 不在运行", flush=True)
            time.sleep(2)
            continue

        if pid != last_attached:
            if session:
                try: session.detach()
                except Exception: pass
            try:
                session = frida.attach(pid)
                script = session.create_script(preload_bridge(SCRIPT, "java"))
                script.on("message", on_message)
                script.load()
                last_attached = pid
                print("[watch] attached pid=%d @ %s" % (pid, time.strftime("%H:%M:%S")), flush=True)
            except Exception as exc:
                print("[watch] attach 失败 pid=%d: %s" % (pid, str(exc)[:120]), flush=True)
                session = script = None
                last_attached = None
                time.sleep(1)
                continue

        time.sleep(1.5)

    if session:
        try: session.detach()
        except Exception: pass
    fh.close()
    print("[watch] done ->", args.out, flush=True)


if __name__ == "__main__":
    sys.exit(main() or 0)