#!/usr/bin/env python3
"""模拟器"发卡机": 在安卓模拟器上用**账号+密码**登录渠道游戏, 自动导出凭据。

为什么需要它(2026-10-29):
  渠道账号的密码登录协议是二进制加密的(nearme=gcsdk 原生 / 果盘=GPXX Proto +
  libEncryptorP.so), 在 PC 上复刻成本很高;
  但**登录成功后游戏会把平台身份写进自己的 prefs**:
      platformUid / game_uid / account_uuid / buildcode / theSignCode / account_zone
  → 我们在 PC 上直接读这些 prefs, 就得到一份**完整可用的凭据**, 之后 PC 独立使用。

所以: 手机/模拟器只当"发卡机"(输一次密码), PC 当"大脑"(长期使用)。
本脚本用**模拟器**当发卡机, 于是**不需要占用别人的真手机**。

流程(全自动):
    起模拟器 → 装渠道包 → 启动 → 过隐私/权限 → 打开密码登录页
    → 填账号密码 → 勾协议 → 点登录 → 等游戏进主城
    → 读模拟器 prefs → 探测 pf → 写进账号库 → 在 PC 上验一次登录

用法:
    python3 cok_emu_login.py --account <果盘号> --password <密码>
    python3 cok_emu_login.py --account <号> --password <密码> --pkg com.hcg.cok.nearme.gamecenter
    python3 cok_emu_login.py --export-only            # 只导出模拟器里已有的号

注意:
  * 模拟器必须能联网(要连渠道账号服务器);
  * 每个渠道包一个"发卡机"实例最好(避免渠道 SDK 的本地状态互相干扰);
  * 登录成功会**顶掉同一账号在别处的连接**(游戏服同账号只允许一个连接)。
"""
import argparse
import json
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

SDK = os.environ.get("ANDROID_SDK", os.path.expanduser(
    "~/Library/Android/sdk"))
ADB = os.path.join(SDK, "platform-tools", "adb")
EMULATOR = os.path.join(SDK, "emulator", "emulator")
AVD = os.environ.get("COK_AVD", "medium_phone")

#: 果盘 SDK 的登录页控件(resource-id 后缀)
RID_USER = "view_login_user_name"
RID_PWD = "view_login_password"
RID_CHECK = "view_protocol_checkbox"
RID_LOGIN = "view_login_btn_login"


def adb(*args, serial=None, timeout=60):
    cmd = [ADB]
    if serial:
        cmd += ["-s", serial]
    cmd += list(args)
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    return p.stdout.replace("\r", "")


def sh(cmd, serial, timeout=60):
    return adb("shell", cmd, serial=serial, timeout=timeout)


def find_emulator():
    """返回在线的模拟器 serial(优先 emulator-*)。"""
    out = adb("devices")
    for line in out.splitlines()[1:]:
        if line.startswith("emulator-"):
            return line.split()[0]
    return None


def start_emulator(serial=None):
    """启动模拟器并等 boot_completed。返回 serial。"""
    serial = serial or find_emulator()
    if serial:
        return serial
    subprocess.Popen(
        [EMULATOR, "-avd", AVD, "-no-window", "-no-audio", "-no-snapshot",
         "-gpu", "swiftshader_indirect", "-no-boot-anim"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for _ in range(60):
        time.sleep(5)
        serial = find_emulator()
        if serial and sh("getprop sys.boot_completed", serial).strip() == "1":
            return serial
    raise SystemExit("[!] 模拟器启动超时")


def install(serial, apk):
    if not os.path.isfile(apk):
        raise SystemExit("[!] 找不到 APK: %s" % apk)
    print("[*] 安装 %s ..." % os.path.basename(apk))
    out = adb("install", "-r", "-t", apk, serial=serial, timeout=900)
    if "Success" not in out:
        raise SystemExit("[!] 安装失败: %s" % out.strip()[-200:])
    sh("root", serial)
    time.sleep(2)


def dump_ui(serial):
    """uiautomator dump -> 返回 {resource_id_suffix: (text, clickable, cx, cy)}"""
    sh("uiautomator dump /sdcard/u.xml", serial)
    raw = sh("cat /sdcard/u.xml", serial)
    out = {}
    for m in re.finditer(r"<node[^>]*>", raw):
        n = m.group(0)
        rid = re.search(r'resource-id="([^"]*)"', n)
        txt = re.search(r'text="([^"]*)"', n)
        clk = re.search(r'clickable="([^"]*)"', n)
        b = re.search(r'bounds="([^"]*)"', n)
        if not b:
            continue
        x1, y1, x2, y2 = map(int, re.findall(r"-?\d+", b.group(1)))
        key = rid.group(1).split("/")[-1] if rid else ""
        out.setdefault(key, (txt.group(1) if txt else "",
                             clk.group(1) == "true" if clk else False,
                             (x1 + x2) // 2, (y1 + y2) // 2))
    return out


def tap(serial, x, y):
    sh("input tap %d %d" % (x, y), serial)


def consent_dialogs(serial, rounds=10):
    """把隐私弹窗 / 权限弹窗全点掉。"""
    for _ in range(rounds):
        ui = dump_ui(serial)
        hit = False
        for key in ("permission_allow_button", "btn_right", "allow_button"):
            if key in ui:
                _, _, x, y = ui[key]
                tap(serial, x, y)
                hit = True
                time.sleep(2)
                break
        if not hit:
            return
    time.sleep(2)


def open_login_page(serial, timeout=120):
    """启动游戏并进入渠道 SDK 的登录页。"""
    pkg = _pkg_of(serial)
    sh("am force-stop %s" % pkg, serial)
    sh("monkey -p %s -c android.intent.category.LAUNCHER 1" % pkg, serial)
    time.sleep(10)
    consent_dialogs(serial)
    deadline = time.time() + timeout
    while time.time() < deadline:
        ui = dump_ui(serial)
        if RID_USER in ui or RID_PWD in ui:
            return ui
        time.sleep(4)
    return None


def _pkg_of(serial):
    out = sh("pm list packages | grep hcg", serial)
    pkgs = [l.strip().split(":")[-1] for l in out.splitlines() if l.strip()]
    return pkgs[0] if pkgs else "com.hcg.cok.ewanqf.guopan"


def pick_password_tab(serial, ui):
    """切到「密码登录」页签(快捷/手机/密码/快速注册)。"""
    texts = dump_ui(serial)
    for key, (txt, _, x, y) in texts.items():
        if txt.strip() in ("密码登录", "帐号登录", "账号登录"):
            tap(serial, x, y)
            time.sleep(2)
            return True
    return False


def do_login(serial, account, password, timeout=90):
    """填账号密码 → 勾协议 → 点登录。返回是否点到登录按钮。"""
    ui = dump_ui(serial)
    if RID_USER not in ui or RID_PWD not in ui:
        return False
    _, _, ux, uy = ui[RID_USER]
    tap(serial, ux, uy)
    time.sleep(1)
    sh("input text '%s'" % account.replace("'", ""), serial)
    time.sleep(1)
    _, _, px, py = ui[RID_PWD]
    tap(serial, px, py)
    time.sleep(1)
    sh("input text '%s'" % password.replace("'", ""), serial)
    time.sleep(1)
    sh("input keyevent 111", serial)      # ESC: 收起输入法, 否则勾选框点不到
    time.sleep(1)
    ui = dump_ui(serial)
    if RID_CHECK in ui:
        _, _, cx, cy = ui[RID_CHECK]
        tap(serial, cx, cy)
        time.sleep(1)
    ui = dump_ui(serial)
    if RID_LOGIN in ui:
        _, _, lx, ly = ui[RID_LOGIN]
        tap(serial, lx, ly)
        print("[*] 已点登录, 等待服务端响应 ...")
        deadline = time.time() + timeout
        while time.time() < deadline:
            time.sleep(5)
            ui = dump_ui(serial)
            # 登录成功后登录页消失
            if RID_USER not in ui:
                return True
        return False
    return False


def wait_platform_uid(serial, timeout=180):
    """等游戏把 platformUid 写进 prefs。返回 platformUid 或 None。"""
    deadline = time.time() + timeout
    while time.time() < deadline:
        xml = sh("cat /data/data/%s/shared_prefs/Cocos2dxPrefsFile.xml "
                 "2>/dev/null" % _pkg_of(serial), serial)
        m = re.search(r'<string name="platformUid">(.*?)</string>', xml, re.S)
        if m and m.group(1).strip():
            return m.group(1).strip()
        time.sleep(5)
    return None


def export_credential(serial):
    """从模拟器读出完整凭据(dict)。"""
    pkg = _pkg_of(serial)
    xml = sh("cat /data/data/%s/shared_prefs/Cocos2dxPrefsFile.xml "
             "2>/dev/null" % pkg, serial)

    def g(key):
        m = re.search(r'<string name="%s">(.*?)</string>' % re.escape(key),
                      xml, re.S)
        return m.group(1).strip() if m else ""
    acc = {
        "packageName": pkg,
        "platformUid": g("platformUid"),
        "gameUid": g("game_uid"),
        "uuid": g("account_uuid"),
        "deviceId": g("device_uid"),
        "buildCode": g("buildcode"),
        "signCode": g("theSignCode"),
        "host": g("account_ip"),
        "zn": g("account_zone"),
    }
    m = re.search(r'<string name="account_port">(.*?)</string>', xml, re.S)
    if m:
        try:
            acc["port"] = int(m.group(1))
        except ValueError:
            pass
    if acc.get("platformUid") and ":" in acc["platformUid"]:
        acc["pfId"] = acc["platformUid"]
        acc["platformToken"] = acc["platformUid"].split(":", 1)[1]
    return acc


def main():
    ap = argparse.ArgumentParser(description="模拟器发卡机: 账号密码登录 → 导出凭据")
    ap.add_argument("--account", help="渠道账号(果盘号)")
    ap.add_argument("--password", help="渠道密码")
    ap.add_argument("--apk", default="/tmp/gp/ewanqf.apk", help="渠道包 APK")
    ap.add_argument("--serial", help="模拟器 serial(默认自动找)")
    ap.add_argument("--export-only", action="store_true",
                    help="不登录, 只把模拟器里已有的号导出")
    ap.add_argument("--no-install", action="store_true")
    ap.add_argument("--wait", type=int, default=180,
                    help="等游戏写入平台身份的超时秒数")
    args = ap.parse_args()

    serial = start_emulator(args.serial)
    print("[*] 模拟器: %s" % serial)
    if not args.no_install and os.path.isfile(args.apk):
        install(serial, args.apk)
    else:
        sh("root", serial)

    if not args.export_only:
        if not args.account or not args.password:
            raise SystemExit("[!] 需要 --account / --password(或用 --export-only)")
        print("[*] 打开登录页 ...")
        ui = open_login_page(serial)
        if not ui:
            print("[!] 没找到登录页(可能 SDK 自动登录了, 试试 --export-only)")
        else:
            pick_password_tab(serial, ui)
            ok = do_login(serial, args.account, args.password)
            print("[*] 登录页已提交: %s" % ok)

    print("[*] 等游戏写入平台身份 ...")
    pu = wait_platform_uid(serial, timeout=args.wait)
    print("[*] platformUid = %s" % pu)
    acc = export_credential(serial)
    acc = {k: v for k, v in acc.items() if v}
    print("\n=== 导出的凭据 ===")
    print(json.dumps(acc, ensure_ascii=False, indent=2))
    if not acc.get("gameUid"):
        print("[!] 没拿到 gameUid, 导出失败")
        return 1
    # 补 pf 候选并实测
    try:
        import cok_account as ca
        acc["pfCandidates"] = ca.pf_candidates(acc.get("packageName") or "")
    except Exception:  # noqa: BLE001
        acc.setdefault("pfCandidates", [])
    import cok_accounts
    try:
        ok, pf = cok_accounts.probe_pf(acc)
    except Exception as e:  # noqa: BLE001
        ok, pf = False, None
        print("[!] pf 探测跳过: %s" % str(e)[:80])
    if ok:
        acc["pf"] = pf
        acc["pfVerified"] = True
        print("[*] pf 实测确定: %s" % pf)
    else:
        acc["pfVerified"] = False
    key = cok_accounts.save_account(acc)
    print("[*] 已入库: %s (%s)" % (key, cok_accounts.account_label(
        cok_accounts.get_account(key))))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
