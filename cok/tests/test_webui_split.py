#!/usr/bin/env python3
"""前端拆分(前后端分离)的回归测试: cok_webui.html 不再是一个 4000 行单文件。

背景: 拆分前 `cok/resources/cok_webui.html` 有 4113 行 —— CSS 594 行 + HTML 530 行
+ JS 2976 行全挤在一个文件里。改一个按钮的样式要在里面翻半天, 而且
`cok_web._resource_bytes` 每次都把整个文件读进内存缓存。

拆成了三份:
    cok_webui.html  (只留结构 + 两个外链)
    cok_webui.css   (594 行样式)
    cok_webui.js    (2976 行逻辑)

锁死的不变量:
  [1] 三个文件都在资源目录里, 都非空
  [2] HTML 里是**外链**(<link>/<script src>), 没有内联 <style>/<script>
  [3] CSS/JS 的内容没被改动(按关键锚点抽查, 不逐字节比 —— 注释可改)
  [4] 服务端对 /webui.css 和 /webui.js **免 token** 返回(不然页面白屏)
  [5] 资源白名单只认固定文件名(路径穿越进不来)
  [6] 安卓打包清单(build.gradle)显式带了这两个文件 —— 否则手机上白屏

全程离线: 只起一个本地 HTTP server, 不连游戏服、不连设备。
"""

import os
import re
import sys
import threading
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "core"))
sys.path.insert(0, os.path.join(HERE, "..", "tools"))

RES = os.path.abspath(os.path.join(HERE, "..", "resources"))

_FAILED = []


def check(name, cond, extra=""):
    if cond:
        print("[PASS] %s%s" % (name, ("  — " + str(extra)) if extra else ""))
    else:
        print("[FAIL] %s%s" % (name, ("  — " + str(extra)) if extra else ""))
        _FAILED.append(name)


# ─────────────────────── 1-3. 文件与内容 ───────────────────────
def test_files():
    print("\n[1/2/3] 拆分后的三个文件与内容")
    paths = {n: os.path.join(RES, n) for n in
             ("cok_webui.html", "cok_webui.css", "cok_webui.js")}
    for n, p in paths.items():
        check("%s 存在" % n, os.path.isfile(p), p)
        if os.path.isfile(p):
            sz = os.path.getsize(p)
            check("%s 非空" % n, sz > 500, "%d bytes" % sz)

    html = open(paths["cok_webui.html"], encoding="utf-8").read()
    css = open(paths["cok_webui.css"], encoding="utf-8").read()
    js = open(paths["cok_webui.js"], encoding="utf-8").read()

    # 外链
    check("HTML 用 <link> 引 CSS",
          bool(re.search(r'<link[^>]+href="/webui\.css"', html)))
    check("HTML 用 <script src> 引 JS",
          bool(re.search(r'<script[^>]+src="/webui\.js"', html)))
    # 没有内联
    check("HTML 里没有内联 <style>", "<style" not in html)
    inline = re.findall(r"<script(?![^>]*\bsrc=)[^>]*>", html)
    check("HTML 里没有内联 <script>", not inline, inline[:2])

    # 内容抽查: 这些锚点在拆分前就存在, 拆完必须还在
    check("CSS 保留了主题变量", "--surface3" in css and "--bg" in css)
    check("CSS 保留了响应式断点", "@media" in css)
    check("JS 保留了 DOM 助手", "const $ = id =>" in js or "function $(" in js)
    check("JS 保留了启动入口", "scheduleRally()" in js)
    check("JS 没有变成空壳", js.count("\n") > 2000, js.count("\n"))
    check("HTML 保留了主要区块",
          all(k in html for k in ("sidebar", "banner")),
          len(html))


# ─────────────────────── 4-6. 服务端行为 ───────────────────────
def test_server():
    print("\n[4/5/6] 服务端路由 / 白名单 / 安卓打包")
    import cok_web

    # 4) 资源白名单必须含新文件(否则 _resource_bytes 直接说"缺少")
    for n in ("cok_webui.css", "cok_webui.js"):
        check("资源白名单含 %s" % n, n in cok_web_shared_files(), n)

    # 资源能读出来
    for n in ("cok_webui.html", "cok_webui.css", "cok_webui.js"):
        b = cok_web._resource_bytes(n)
        check("_resource_bytes(%s) 有内容" % n, len(b) > 500, "%d bytes" % len(b))

    # 路由表: 免 token 的路径白名单
    assets = getattr(cok_web, "_WEBUI_ASSETS", None)
    check("有静态资源白名单 _WEBUI_ASSETS", isinstance(assets, dict) and bool(assets),
          sorted(assets or {})[:4])
    if assets:
        check("白名单含 /webui.css", "/webui.css" in assets)
        check("白名单含 /webui.js", "/webui.js" in assets)
        # 白名单只能映射到**固定文件名**(不能拼变量)
        for path, val in assets.items():
            name = val[0]
            check("白名单 %s 映射到固定资源名" % path,
                  name in ("cok_webui.css", "cok_webui.js"),
                  name)
            check("白名单 %s 不含路径穿越" % path,
                  ".." not in path and name == os.path.basename(name), name)

    # 真起一个服务, 实测取页面/CSS/JS
    srv = cok_web.ThreadingHTTPServer(("127.0.0.1", 0), cok_web.Handler)
    port = srv.server_address[1]
    cok_web.Handler.token = "webui-split-test"
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    time.sleep(0.5)
    base = "http://127.0.0.1:%d" % port
    try:
        st, ct, body = _get(base + "/?t=webui-split-test")
        check("页面 200", st == 200, st)
        check("页面是 HTML",
              "text/html" in (ct or ""), ct)
        page = body.decode("utf-8", "replace")
        check("页面里引了外部 CSS", "/webui.css" in page)

        for p in ("/webui.css", "/webui.js"):
            st, ct, body = _get(base + p)      # 故意不带 token
            check("%s 免 token 可取" % p, st == 200, st)
            check("%s 内容够大(没白屏)" % p, len(body) > 1000, len(body))
            check("%s Content-Type 对" % p,
                  ("css" in (ct or "")) if p.endswith(".css")
                  else ("javascript" in (ct or "")), ct)

        # 白名单外: 一律 404(不能拿 python 源码)
        for p in ("/cok_web.py", "/cok_client.py", "/../cok/core/cok_web.py"):
            st, _, _ = _get(base + p)
            check("白名单外 %s 取不到" % p, st == 404, st)
    finally:
        srv.shutdown()

    # 6) 安卓打包清单必须显式带这两个文件
    gradle = os.path.abspath(os.path.join(HERE, "..", "..",
                                          "android-app", "app", "build.gradle"))
    if os.path.isfile(gradle):
        txt = open(gradle, encoding="utf-8").read()
        for n in ("cok_webui.css", "cok_webui.js"):
            check("build.gradle 带 %s" % n, n in txt, n)
    else:
        print("  (跳过 build.gradle 检查: 找不到文件)")


def cok_web_shared_files():
    """资源白名单(在共享层, 门面层也转发了)。"""
    import cok_web
    return list(getattr(cok_web, "_RES_FILES", ()) or ())


def _get(url):
    try:
        with urllib.request.urlopen(url, timeout=5) as r:
            return r.status, r.headers.get("Content-Type"), r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.headers.get("Content-Type"), e.read()
    except Exception as e:  # noqa: BLE001
        return "ERR", str(e), b""


def main():
    test_files()
    test_server()
    print()
    if _FAILED:
        print("失败 %d 项:" % len(_FAILED))
        for n in _FAILED:
            print("  FAIL", n)
        return 1
    print("全部通过")
    return 0


if __name__ == "__main__":
    sys.exit(main())