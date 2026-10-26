#!/usr/bin/env python3
"""从设备本地读取 COK 账号与服务器参数, 供直连客户端使用。

数据来源(App 的 SharedPreferences, root 读取):
  /data/data/com.hcg.cok.nearme.gamecenter/shared_prefs/
      com.nearme.gamecenter.open.xml  → 渠道 roleid(= platformToken)
      Cocos2dxPrefsFile.xml           → game_uid / device_uid / account_uuid /
                                       buildcode / theSignCode / account_ip / account_port / account_zone
  另: COK_GAMEUID.xml               → 备用 gameUid

用法:
  python3 cok_account.py                 # 打印读到的参数
  python3 cok_account.py --json          # JSON 输出
  python3 cok_account.py --write out.json  # 写成客户端可直接用的账号文件
"""
import argparse
import json
import os
import re
import subprocess
import sys

PKG = "com.hcg.cok.nearme.gamecenter"
SP_DIR = "/data/data/%s/shared_prefs" % PKG
ADB = os.environ.get("ADB", "/Users/a1234/Library/Android/sdk/platform-tools/adb")


def adb_sh(cmd, su=True):
    """执行设备 shell 命令, 返回 stdout"""
    if su:
        cmd = "su -c %s" % json.dumps(cmd)
    p = subprocess.run([ADB, "shell", cmd], capture_output=True, text=True)
    return p.stdout


def read_prefs(name):
    return adb_sh("cat %s/%s" % (SP_DIR, name))


def xml_strings(text):
    """解析 Android SharedPreferences XML 里的 <string name="k">v</string>"""
    out = {}
    for m in re.finditer(r'<string name="([^"]+)">(.*?)</string>', text, re.S):
        k, v = m.group(1), m.group(2)
        v = (v.replace("&quot;", '"').replace("&amp;", "&")
              .replace("&lt;", "<").replace("&gt;", ">").replace("&apos;", "'")
              .replace("&#39;", "'"))
        out[k] = v
    for m in re.finditer(r'<int name="([^"]+)" value="([^"]*)"', text):
        out[m.group(1)] = m.group(2)
    return out


def load_account():
    acc = {}
    # 1) 渠道 open 配置: roleid = platformToken
    openxml = read_prefs("com.nearme.gamecenter.open.xml")
    role = {}
    for m in re.finditer(r'<string name="gcsdk_tag_local_role_info">(.*?)</string>', openxml, re.S):
        try:
            role = json.loads(m.group(1).replace("&quot;", '"'))
        except Exception:
            pass
    if role.get("roleid"):
        acc["platformToken"] = role["roleid"]
        acc["pfId"] = "nearme:" + role["roleid"]
        acc["roleName"] = role.get("roleName", "")
    # 2) cocos UserDefault
    prefs = xml_strings(read_prefs("Cocos2dxPrefsFile.xml"))
    if prefs.get("game_uid"):
        acc["gameUid"] = prefs["game_uid"]
    if prefs.get("device_uid"):
        acc["deviceId"] = prefs["device_uid"]
    if prefs.get("account_uuid"):
        acc["uuid"] = prefs["account_uuid"]
    if prefs.get("buildcode"):
        acc["buildCode"] = prefs["buildcode"]
    if prefs.get("theSignCode"):
        acc["signCode"] = prefs["theSignCode"]
    if prefs.get("account_ip"):
        acc["host"] = prefs["account_ip"]
    if prefs.get("account_port"):
        try:
            acc["port"] = int(prefs["account_port"])
        except ValueError:
            pass
    if prefs.get("account_zone"):
        acc["zn"] = prefs["account_zone"]
    # 3) 备用 gameUid
    if "gameUid" not in acc:
        g = xml_strings(read_prefs("COK_GAMEUID.xml"))
        for k, v in g.items():
            if v.isdigit():
                acc["gameUid"] = v
                break
    return acc


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--write", help="写成 JSON 文件")
    args = ap.parse_args()

    acc = load_account()
    if args.write:
        with open(args.write, "w", encoding="utf-8") as fh:
            json.dump(acc, fh, ensure_ascii=False, indent=1)
        print("已写 %s" % args.write)
        if not args.json:
            print(json.dumps(acc, ensure_ascii=False, indent=1))
        return 0
    if args.json:
        print(json.dumps(acc, ensure_ascii=False, indent=1))
    else:
        for k, v in acc.items():
            print("  %-14s = %s" % (k, v))
    missing = [k for k in ("platformToken", "pfId", "gameUid", "deviceId", "uuid",
                           "buildCode", "signCode", "host", "port", "zn") if k not in acc]
    if missing:
        print("[!] 缺失字段: %s" % ", ".join(missing), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
