# COK Console Android preview

This is an Android client for the existing local COK console. It embeds Python
with Chaquopy and provides a native mobile interface backed by the local console.

The Gradle task `preparePythonSources` copies only the runtime modules and required
resources, then replaces the desktop development account with an empty protocol
template. Installed apps keep accounts, settings, map data, and the local access
token under Android app-private storage.

Build a debug APK on macOS:

```sh
cd android-app
./gradlew assembleDebug
adb install -r app/build/outputs/apk/debug/app-debug.apk
```

The first build downloads the pinned Android Gradle and Chaquopy plugins.

> ⚠ 仓库里**没有** `gradlew` 包装脚本。用本机已下载的 gradle 直接跑:
> `~/.gradle/wrapper/dists/gradle-9.6.1-bin/gradle-9.6.1/bin/gradle :app:assembleDebug --offline`

## 打包安全自检(别绕过它)

`preparePythonSources` 会把桌面端 `cok_client.py` 里的**内置账号凭据**
(pfId / uuid / buildCode / deviceId)换成空模板,再打进 APK。

替换用的是正则,一旦失配就是**静默失败** —— 凭据会原样进 APK。所以:

* 正则必须带 MULTILINE: `(?sm)ACCOUNT = \{.*?^\}`
  (少了 `m` 的话 `^` 只匹配字符串开头, 匹配不到 ACCOUNT 块的结尾 —— 2026-10-31 踩过)
* 任务末尾有**自检**: ACCOUNT 没清空、或产物里出现源账号的凭据串 → **直接让 build 失败**
* 源码里也不能写死真凭据: `cok_client.py` 的离线自检改成从 `ACCOUNT` 读输入,
  APK 里 ACCOUNT 是空的 → 那一项显示 SKIP 而不是 FAIL

验证 APK 里没有残留:

```sh
unzip -p app/build/outputs/apk/debug/app-debug.apk assets/chaquopy/app.imy > /tmp/app.imy
unzip -p /tmp/app.imy cok_client.py | grep -E 'nearme:g[0-9]+|cokc38|buildCode.*"[0-9a-f]{32}'
```

## 安卓端已知的三个坑(2026-10-31 修)

1. **账号可能跑错号**: 账号库里 `platformToken` 为空是合法的(果盘/ewanqf 渠道),
   但它曾被算进"账号必需字段" → 引擎判定账号不完整 → **静默改用内置账号**,
   于是手机上看着是 A 号, 实际跑的是 B 号。现在 `platformToken` 不再是必需字段,
   而且**账号库里有号但不完整时会直接报错**, 不再偷偷换号。
2. **运行时文件不能写进 assets**: `_data_dir()` 原来回退到模块所在目录,
   在安卓端就是 Chaquopy 的 assets —— `automation-history.json` / `map-index.json`
   全写进了打包资源目录(重装即丢, 还污染 APK)。现在统一回退到
   `accounts.DATA_ROOT`(安卓端 = `files/cok/data`)。
3. **APK 里的账号凭据**: 见上面「打包安全自检」。

## 导出 Excel: WebView 里的 blob 下载**不会落盘**(2026-11-09 修)

* **症状**: 在「完整高级控制台」(内嵌 WebView) 里点「导出 Excel」, 页面提示
  "已导出 XXX KB", 但**手机里找不到任何文件**。
* **原因**: 网页端导出是 `fetch -> blob -> <a download>`。桌面浏览器这么干没问题,
  但 **WebView 不处理 blob 下载** —— 没有 DownloadListener, anchor 点击被忽略,
  字节只活在内存里。页面那句"已导出"是**假成功**。
* **修法**: 给 WebView 注册 JS 桥, 让网页把字节交给原生落盘:
  * `ui/ExportSaver.kt` —— `saveExportToDownloads()`(写 MediaStore `Download/COK`)
    + `ExportBridge`(`@JavascriptInterface saveExport(filename, base64)`);
  * `ui/ConsoleWebScreen.kt` —— `addJavascriptInterface(ExportBridge(context), "CokAndroid")`;
  * `protocol/cok_webui.html` —— 导出时若发现 `window.CokAndroid.saveExport` 存在,
    就把 blob 转 base64 交给原生; 否则走原来的 `a.download`(桌面浏览器不受影响)。
* **原生入口也统一**: 原生「导出已索引玩家 Excel」现在复用同一个
  `saveExportToDownloads()`, 两个入口产物都在 **下载/COK/**, 提示文案一致。
* **文件名带时间戳**: `cok-players-real_20261109-1223.xlsx`。
  否则反复导出会被系统改成 `cok-players-real (1).xlsx`, 根本认不出是哪一次扫描的结果。

## 巨型狮鹫 · 联盟集结(2026-11-02)

自动打怪之外新增了「巨型狮鹫 · 集结」: 选等级 -> 选目标 -> 选集结时间 -> 发起集结。
协议细节见 `cok/docs/WEB.md` 的「巨型狮鹫 · 联盟集结」一节。

* **两个入口**: 原生「操作」页(紧跟「自动打怪」卡下面) + 「完整高级控制台」
  (WebView, 同一套 `cok_webui.html`)。两边都能用。
* 原生侧在 `ui/OperationsScreen.kt:RallyCard`, 走
  `ConsoleViewModel.loadRally()` / `startRally()` -> `POST /api/action {action:"hunt", op:"rally-state"|"rally-start"}`。
* 集结状态**不进 `/api/state`**: 它要发 `world.get` 拉地块, 比主轮询慢得多。
  原生侧只在进「操作」页时读一次, 之后靠卡片上的「刷新」按钮手动更新,
  **不跟主轮询抢账号连接**。

### 派兵数量支持手动键入(2026-11-02)

原生「操作」页的「派兵」改成了可编辑数字框(`ui/OperationsScreen.kt:NumericField`):
点数字框直接敲(如 `3500`), 范围 1 ~ 20000, `−` / `+` 按钮仍然保留方便微调。

**踩坑记录(Compose 1.11 的 `BasicTextField`, 别再改回去)**:

* 内部 `TextFieldState` 才是真正的主。聚焦时它会把旧值**原样吐回来**,
  而点击落在数字中间会把光标插进去、选区被折叠 ——
  于是「值放在输入框里」时敲 `3500` 会变成 `20350000` 这种拼接串。
* 解法: **输入框里永远只装"用户正在敲的内容", 当前值用灰色占位提示显示**。
  光标只有 0 一个落点, 敲什么就是什么。
* 想让"再点一次 = 重新敲"也成立, 光靠 `onFocusChanged` 不够(聚焦中再点不会触发焦点变化),
  得用 `pointerInput(PointerEventPass.Initial)` 侦测按下, 再用**前后缀差分**
  (`insertedDigits`) 从新旧文本里摘出"新敲进去的那几个字符",
  旧值整段丢掉 —— 直接丢弃整次回调会吃掉第一个按键。
* 数值一律**夹取后**回写父级(父级永远是合法值, 确认弹窗显示的也是它)。

### ⚠️ 运行时文件不能写进 assets(安卓端必须落到 files/cok/data)

`cok_rally` 的巨型狮鹫注册表 `boss-registry.json` 是运行时文件。
模块在 Chaquopy 的 assets 里(只读), 写进去会重装即丢还污染 APK ——
所以它的默认目录是 `accounts.DATA_ROOT`(安卓端 = `files/cok/data`),
并且网页在切账号时会调 `cok_rally.set_data_dir(...)` 跟 `cok_map` 保持一致。
**新增带落盘文件的模块时记得照这个来。**

## Background risk monitoring

In **More**, enable **Background risk monitoring** to keep the local console
available after the app is backgrounded. Android shows a persistent notification;
use its **Stop** action or the in-app toggle to stop monitoring. The service checks
the console every five minutes and sends a high-priority notification when a newly
detected risk needs attention.

The monitor uses the console's standard refresh path. Any automation already
enabled in the advanced console continues to apply during these refreshes. Keeping
the persistent notification active consumes a small amount of additional battery.
