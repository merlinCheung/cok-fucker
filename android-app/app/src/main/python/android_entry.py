"""Android bootstrap for the embedded, loopback-only COK web console."""
import os
import sys
import threading


_started = False
_url = None
_start_lock = threading.Lock()


def _android_context():
    """拿到 Application context。

    ⚠ Chaquopy 17 **没有** jnius 模块, 也没有 Python.getContext()。
    只能用新 API: `from com.chaquo.python import Python` 直接导入 Java 类,
    再 `Python.getInstance().getPlatform().getApplication()` 拿 Application。
    """
    try:
        from com.chaquo.python import Python
    except Exception as e:  # noqa: BLE001
        print("[!] 拿 context: 导入 com.chaquo.python 失败(%s)" % str(e)[:160])
        return None
    try:
        platform = Python.getInstance().getPlatform()
    except Exception as e:  # noqa: BLE001
        print("[!] 拿 context: getPlatform() 失败(%s)" % str(e)[:160])
        return None
    if platform is None:
        print("[!] 拿 context: platform 是 None")
        return None
    # AndroidPlatform.getApplication()
    try:
        fn = getattr(platform, "getApplication")
        ctx = fn()
        if ctx is not None:
            return ctx
    except Exception as e:  # noqa: BLE001
        print("[i] 拿 context: getApplication() 失败(%s)" % str(e)[:120])
    # 兜底: AndroidPlatform.mContext 是 public 字段
    try:
        ctx = getattr(platform, "mContext")
        if ctx is not None:
            return ctx
    except Exception:  # noqa: BLE001
        pass
    print("[!] 拿 context: 各种路子都没拿到")
    return None


def _stop_game_app(package):
    """强停游戏 App, 把游戏服的账号位让出来。

    **为什么安卓端必须自己实现**: 安卓设备上没有 adb, 桌面端那条
    `adb shell am force-stop` 在这里永远失败 -> 游戏 App 继续占着账号 ->
    同账号两条连接 -> 游戏服互踢 -> 猎人的连接刚建立就被关闭
    (2026-11-01 实测: hunt_step(stamina) -> hunt_error("连接被服务端关闭"))。

    普通 App 能结束**别的** App 进程的正规途径只有一个:
    `ActivityManager.killBackgroundProcesses()`, 需要普通权限
    `android.permission.KILL_BACKGROUND_PROCESSES`(已在 Manifest 声明)。
    它只能杀后台进程 —— 用户点打怪时控制台在前台, 游戏 App 必然在后台。

    ⚠ **包可见性**(Android 11+): 控制台默认看不到没交互过的游戏包。
    所以 Manifest 里用 <queries> 放开了这两个游戏包; 也不能拿
    "查得到这个包"当前提(查不到也要照样尝试结束进程)。

    返回 True 表示"已调用", False 表示这条路子不可用(调用方会退回别的方案)。
    """
    try:
        ctx = _android_context()
        if ctx is None:
            return False
        am = ctx.getSystemService("activity")
        if am is None:
            print("[!] 停游戏 App: 拿不到 ActivityManager")
            return False
        ok = am.killBackgroundProcesses(package)
        print("[*] 停游戏 App %s: killBackgroundProcesses=%s" % (package, ok))
        return True
    except Exception as e:  # noqa: BLE001
        print("[!] 停游戏 App 失败(%s): %s" % (package, str(e)[:200]))
        return False


def start(files_dir, port, token):
    """Start the existing control server once and return its loopback URL."""
    global _started, _url
    data_dir = os.path.join(str(files_dir), "cok")
    os.makedirs(data_dir, exist_ok=True)

    # These values are read while the original modules import. Keeping every
    # writable item under filesDir avoids writes to the packaged Python assets.
    #
    # ⚠ COK_DATA_ROOT 是**所有**可写文件的根: 账号库、地图索引、web-settings、
    #    token、账号锁全在它下面。以前这里指向 <files>/cok/data 而账号库另走
    #    COK_ACCOUNTS_DIR, 两个根各管一半 —— 现在统一成一个, 少一层心智负担。
    os.environ["COK_DATA_ROOT"] = data_dir
    os.environ["COK_ACCOUNTS_DIR"] = os.path.join(data_dir, "accounts")
    # 账号锁: 这里给的是**目录**(不是单个文件)。
    # ⚠️ 曾经是"一个文件" —— 而 `cok_client.lock_file_for()` 以前只要看到这个
    #   环境变量就**无条件**返回它、忽略 key ⇒ **手机上所有账号共用一把锁**,
    #   五个号的 3 分钟轮询被串成一条线, "后台同时在线"是假的(多账号没法独立存活)。
    #   现在改成目录: `<该目录>/<uid>.lock`, 每个账号一把, 互不阻塞。
    #   同账号仍然互斥(flock 按文件), 所以"同账号只允许一个连接"的保护没变。
    os.environ["COK_ACCOUNT_LOCK_FILE"] = os.path.join(data_dir, "locks")
    # 资源目录: Chaquopy 把 cok/resources 里的文件解到 assets 根, 与模块同级。
    # 显式指出来, 免得 cok_paths 去仓库里找(手机上不存在仓库)。
    _res_dir = os.path.dirname(os.path.abspath(__file__))
    # 桌面: <flat>/cok/resources 才是真资源目录。
    # Chaquopy 扁平布局: 资源文件与 .py 模块同级, 没有 resources 子目录。
    if os.path.isdir(os.path.join(_res_dir, "resources")):
        os.environ["COK_RESOURCES_DIR"] = os.path.join(_res_dir, "resources")
    elif os.path.isfile(os.path.join(_res_dir, "cok_webui.html")):
        os.environ["COK_RESOURCES_DIR"] = _res_dir

    with _start_lock:
        # Android may recreate MainActivity without killing the process. The
        # embedded server keeps its original token, so every later Activity
        # must reuse the original URL instead of issuing an unusable token.
        if _url:
            return _url

        _url = "http://127.0.0.1:%s/?t=%s" % (port, token)
        if _started:
            return _url
        _started = True

        def run():
            import cok_web
            import cok_map
            import scan_world
            cok_web.TOKEN_FILE = os.path.join(data_dir, ".cok-web-token")
            cok_web.Engine.SETTINGS_FILE = os.path.join(data_dir, "web-settings.json")

            # 安卓端没有 adb, 让 cok_web 用系统的 ActivityManager 停游戏 App
            cok_web.set_platform_stop_app(_stop_game_app)

            # ⚠️ 全图扫描: 桌面端 _scan_start 用 subprocess.Popen 起独立进程跑
            # scan_world.py。安卓端(Chaquopy)**没有可执行的 python 解释器**,
            # 那条路必然失败 —— 以前直接禁掉("暂不支持")。
            # 现在换成**进程内后台线程**: 复用 Engine._scan_start 的 fresh/resume/
            # 备份判断, 只替换两个接缝 ——
            #   _spawn_scanner: 起线程跑 scan_world.run_scan(install_signals=False)
            #   _scan_stop    : 置协作式停止标志(不能发信号: 给自己发 SIGTERM 会杀掉整个 App)
            _GAME_PKG = "com.hcg.cok.nearme.gamecenter"

            def _spawn_scanner_inproc(engine, params, bak):
                prev = getattr(engine, "_scan_thread", None)
                if prev is not None and prev.is_alive():
                    return {"ok": False, "error": "扫描已经在跑了"}
                stop_event = threading.Event()
                args = scan_world._Args(
                    out=params["out"],
                    account_key=params.get("account_key"),
                    radius=int(params.get("radius") or 0),
                    step=int(params.get("step") or cok_map.STEP),
                    max_requests=int(params.get("max_requests") or 0),
                    resume=bool(params.get("resume")),
                    fresh=bool(params.get("fresh")),
                    server=2223,
                    keep_app=False,
                    reconnect_every=200,
                    delay=float(params.get("delay") or 0.0),
                )
                logp = os.path.join(params.get("data_dir") or data_dir, "scan.log")

                def _log(msg):
                    try:
                        with open(logp, "ab") as fh:
                            fh.write(("%s\n" % msg).encode("utf-8", "replace"))
                    except OSError:
                        pass
                    print(msg)

                def _stop_app(package=None):
                    return _stop_game_app(package or _GAME_PKG)

                def _worker():
                    try:
                        scan_world.run_scan(
                            args, stop_event=stop_event, install_signals=False,
                            stop_app_fn=_stop_app, log=_log)
                    except Exception as e:  # noqa: BLE001
                        _log("[!] 扫描线程异常: %s" % str(e)[:200])
                    finally:
                        # 收尾兜底: run_scan 正常会清 pid, 线程异常退出时也清掉,
                        # 否则 _scan_status 会一直按"本进程存活"判定成扫描中。
                        try:
                            cok_map.clear_scan_pid(engine._pid_path())
                        except Exception:  # noqa: BLE001
                            pass

                # 先占上 pid(= 本进程), 让紧接着的一次状态查询就能看到"扫描中";
                # run_scan 内部也会再写一次(同一路径), 幂等。
                try:
                    cok_map.write_scan_pid(os.getpid(), engine._pid_path())
                except Exception:  # noqa: BLE001
                    pass
                t = threading.Thread(target=_worker, name="cok-scan", daemon=True)
                engine._scan_thread = t
                engine._scan_stop_event = stop_event
                t.start()
                return {"ok": True, "pid": os.getpid(),
                        "note": "扫描已启动(后台线程, 切后台也继续) · 日志 scan.log",
                        "resumed": bool(params.get("resume")),
                        "backup": os.path.basename(bak) if bak else ""}

            def _scan_stop_inproc(engine):
                ev = getattr(engine, "_scan_stop_event", None)
                t = getattr(engine, "_scan_thread", None)
                if ev is None or t is None or not t.is_alive():
                    return {"ok": False, "error": "没有正在跑的扫描"}
                ev.set()
                return {"ok": True, "note": "已请求停止, 断点已保存(之后可续扫)"}

            cok_web.Engine._spawn_scanner = _spawn_scanner_inproc
            cok_web.Engine._scan_stop = _scan_stop_inproc
            sys.argv = [
                "cok_web.py", "--host", "127.0.0.1", "--port", str(port),
                "--token", str(token),
            ]
            cok_web.main()

        threading.Thread(target=run, name="cok-web", daemon=True).start()
    return _url
