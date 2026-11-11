#!/usr/bin/env python3
"""从设备本地读取 COK 账号与服务器参数, 供直连客户端使用。

数据来源(App 的 SharedPreferences, root 读取):
  /data/data/<包名>/shared_prefs/
      Cocos2dxPrefsFile.xml        → game_uid / device_uid / account_uuid /
                                     buildcode / theSignCode / account_ip /
                                     account_port / account_zone / **platformUid**
      com.nearme.gamecenter.open.xml → 渠道 roleid(= platformToken) + roleName
  另: COK_GAMEUID.xml               → 备用 gameUid

⚠️ 平台身份以 **Cocos2dxPrefsFile.xml 的 platformUid** 为准
   (形如 `nearme:g1372797742670953701` / `ewanqf:1084D654F5A7FB599158`)。
   open.xml 里的 `gcsdk_tag_local_role_info.roleid` 可能是**上一个角色的残留**
   —— 实测 nearme 包里它是某个**内置凭据账号**的 pfId(具体值见账号库),
   用它登录会被服务端拒(E002 / 数字 id + init.error)。

包名与渠道字段的对应关系(已由设备 libgame.so 字符串 + 实测登录验证):
    包名 com.hcg.cok.<渠道>.<渠道包>
      pf     = "cn_" + <渠道>
      pfId   = <渠道> + ":" + platformToken
    例: com.hcg.cok.nearme.gamecenter -> pf=cn_nearme, pfId=nearme:<token>
        com.hcg.cok.ewanqf.guopan     -> pf=cn_ewanqf, pfId=ewanqf:<token>

用法:
  python3 cok_account.py                 # 打印默认包的参数
  python3 cok_account.py --json          # JSON 输出
  python3 cok_account.py --list          # 列出设备上所有 COK 包
  python3 cok_account.py -p <包名>        # 指定包
  python3 cok_account.py --write out.json  # 写成客户端可直接用的账号文件
"""
import argparse
import json
import os
import re
import subprocess
import sys

PKG = "com.hcg.cok.nearme.gamecenter"
ADB = os.environ.get("ADB", "/Users/a1234/Library/Android/sdk/platform-tools/adb")

#: 设备上可能存在的 COK 渠道包(用于自动发现)
PKG_PATTERN = re.compile(r"^com\.hcg\.cok\.[a-z0-9_]+(\.[a-z0-9_]+)?$")


def adb_sh(cmd, su=True):
    """执行设备 shell 命令, 返回 stdout"""
    if su:
        cmd = "su -c %s" % json.dumps(cmd)
    p = subprocess.run([ADB, "shell", cmd], capture_output=True, text=True)
    return p.stdout


def read_prefs(pkg, name):
    return adb_sh("cat /data/data/%s/shared_prefs/%s" % (pkg, name))


def list_packages():
    """列出设备上已安装的 COK 渠道包(按已知顺序, 未知排后面)。"""
    out = adb_sh("pm list packages", su=False)
    found = []
    for line in out.splitlines():
        pkg = line.strip().split(":")[-1].strip()
        if pkg and PKG_PATTERN.match(pkg):
            found.append(pkg)
    known = [PKG, "com.hcg.cok.ewanqf.guopan"]
    found.sort(key=lambda p: (known.index(p) if p in known else 99, p))
    return found


def channel_of(pkg):
    """从包名推出渠道段: com.hcg.cok.<渠道>.<包> -> <渠道>

    com.hcg.cok.nearme.gamecenter -> nearme
    com.hcg.cok.ewanqf.guopan     -> ewanqf
    """
    parts = (pkg or "").split(".")
    if len(parts) >= 4 and parts[0] == "com" and parts[1] == "hcg":
        return parts[3]
    if len(parts) >= 3 and parts[0] == "com" and parts[1] == "hcg":
        return parts[2]
    return "nearme"


def pf_of(pkg):
    """pf = "cn_" + 渠道段"""
    return "cn_" + channel_of(pkg)


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


def pf_candidates(pkg):
    """给出该渠道包可能的 pf 取值(按可能性排序)。

    pf **服务端会校验**(2026-10-29 实测: 鸭皇号用 cn_nearme 能登,
    换成 nearme / cn_ewanqf / 乱填 都是 E002), 所以它是**每账号**的字段,
    不能只靠"cn_<渠道段>"的归纳 —— 用 cok_accounts.probe_pf() 登录实测来确定。

    候选来源: 包名里的渠道段(com.hcg.cok.<渠道>.<包>) 与 渠道包名段。
    """
    chan = channel_of(pkg)
    parts = (pkg or "").split(".")
    seg = parts[3] if len(parts) >= 4 else chan
    out = []
    for c in ("cn_%s" % chan, chan, "cn_%s" % seg, seg,
              "cn_%s" % (seg or ""), "cn1", "cn_cn1", "elextech", "cn_elextech"):
        if c and c not in out:
            out.append(c)
    return out


def load_account(pkg=None, host=None, port=None, zn=None, app_version=None,
                 lua_version=None):
    """读某个包当前的账号凭据。pkg=None 时用默认包。"""
    pkg = pkg or PKG
    chan = channel_of(pkg)
    acc = {
        "packageName": pkg,
        "pf": pf_of(pkg),
        "pfId": "%s:%s" % (chan, ""),   # 占位, 下面按 platformUid 修正
        "pfCandidates": pf_candidates(pkg),
    }
    # 1) 游戏自己写的 platformUid —— **平台身份的唯一权威来源**
    prefs = xml_strings(read_prefs(pkg, "Cocos2dxPrefsFile.xml"))
    platform_uid = (prefs.get("platformUid") or "").strip()
    if ":" in platform_uid:
        acc["pfId"] = platform_uid
        acc["platformToken"] = platform_uid.split(":", 1)[1]
    # 2) 渠道 open 配置(备用): roleid = platformToken
    openxml = read_prefs(pkg, "com.nearme.gamecenter.open.xml")
    role = {}
    for m in re.finditer(r'<string name="gcsdk_tag_local_role_info">(.*?)</string>',
                         openxml, re.S):
        try:
            role = json.loads(m.group(1).replace("&quot;", '"'))
        except Exception:
            pass
    if role.get("roleid") and not acc.get("platformToken"):
        acc["platformToken"] = role["roleid"]
        acc["pfId"] = "%s:%s" % (chan, role["roleid"])
    # 只有 roleid 与当前平台身份一致时, roleName 才属于这个角色
    if role.get("roleName") and role.get("roleid") == acc.get("platformToken"):
        acc["roleName"] = role["roleName"]
    # 3) cocos UserDefault 里的其余字段
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
    # 4) 备用 gameUid
    if "gameUid" not in acc:
        g = xml_strings(read_prefs(pkg, "COK_GAMEUID.xml"))
        for k, v in g.items():
            if v.isdigit():
                acc["gameUid"] = v
                break
    # 5) 允许调用方覆盖(不同渠道包的服务器地址/版本可能不同)
    if host:
        acc["host"] = host
    if port:
        acc["port"] = int(port)
    if zn:
        acc["zn"] = zn
    if app_version:
        acc["appVersion"] = app_version
    if lua_version:
        acc["luaVersion"] = lua_version
    return acc


def load_previous_account(pkg=None):
    """读某个包**上一个号**的凭据(游戏切号时会把旧号留在 prefs 里)。

    2026-10-29 实测: nearme 包的 Cocos2dxPrefsFile.xml 里还有
        original_account_game_uid / original_account_uuid / original_account_ip
        / original_account_zone
    —— 也就是**上一个角色的 gameUid 和 uuid**; 它的平台 token 可以从渠道 SDK
    的角色信息里取(nearme: gcsdk_tag_local_role_info.roleid)。

    → 凡是这台手机登过的号, **凭据都能捞回来, 不需要密码**。
    没有就返回 None。
    """
    pkg = pkg or PKG
    chan = channel_of(pkg)
    prefs = xml_strings(read_prefs(pkg, "Cocos2dxPrefsFile.xml"))
    game_uid = (prefs.get("original_account_game_uid") or "").strip()
    uuid = (prefs.get("original_account_uuid") or "").strip()
    if not game_uid:
        return None
    acc = {
        "packageName": pkg,
        "pf": pf_of(pkg),
        "pfCandidates": pf_candidates(pkg),
        "gameUid": game_uid,
        "uuid": uuid,
        "host": prefs.get("original_account_ip") or "",
        "zn": prefs.get("original_account_zone") or "",
        "isPrevious": True,
    }
    # 平台 token: 渠道 SDK 的角色信息(roleid)
    openxml = read_prefs(pkg, "com.nearme.gamecenter.open.xml")
    for m in re.finditer(r'<string name="gcsdk_tag_local_role_info">(.*?)</string>',
                         openxml, re.S):
        try:
            role = json.loads(m.group(1).replace("&quot;", '"'))
        except Exception:
            continue
        rid = (role.get("roleid") or "").strip()
        if rid and rid != (acc.get("platformToken") or ""):
            acc["platformToken"] = rid
            acc["pfId"] = "%s:%s" % (chan, rid)
            if role.get("roleName"):
                acc["roleName"] = role["roleName"]
    if not acc.get("pfId"):
        acc["pfId"] = "%s:" % chan
    # 设备字段跟当前号共用(同一台设备 / 同一个区服)
    if prefs.get("device_uid"):
        acc["deviceId"] = prefs["device_uid"]
    if prefs.get("buildcode"):
        acc["buildCode"] = prefs["buildcode"]
    if prefs.get("theSignCode"):
        acc["signCode"] = prefs["theSignCode"]
    # 端口: original_* 里没有, 但同一个区服端口一样 → 沿用当前号的
    if prefs.get("account_port"):
        try:
            acc["port"] = int(prefs["account_port"])
        except ValueError:
            pass
    if not acc.get("host") and prefs.get("account_ip"):
        acc["host"] = prefs["account_ip"]
    if not acc.get("zn") and prefs.get("account_zone"):
        acc["zn"] = prefs["account_zone"]
    return acc


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--write", help="写成 JSON 文件")
    ap.add_argument("-p", "--package", help="包名(默认 %s)" % PKG)
    ap.add_argument("--list", action="store_true", help="列出设备上的 COK 包")
    args = ap.parse_args()

    if args.list:
        pkgs = list_packages()
        for p in pkgs:
            print(p)
        return 0

    acc = load_account(args.package)
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
