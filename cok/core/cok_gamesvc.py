#!/usr/bin/env python3
"""游戏服 HTTP gameservice 客户端: getserverlist.php(取 gameUid / uuid / 区服)。

逆向结论(2026-10-29 实测):
  * 接口: GET https://<host>/gameservice/getserverlist.php?uuid=..&pfId=..&loginFlag=1&..&sig=..
  * **sig 算法已破解**(4/4 真机样本逐字节一致):
        sig = md5(uuid + str(t) + "@z4LugUwrDN0MqOJtzmHPK7Ss-k4taAUOZh1M3Yu9")
    其中 uuid = 设备侧 16 位 hex(t 无关), t = 秒级时间戳, 常量在 libgame.so 里明文可见。
  * **loginFlag=1 才带角色信息**(gameUid/账号uuid/角色名/等级/buildCode); loginFlag=0 只列全服区服。
  * **角色是按 pfId 查的, 与请求里的 uuid 无关** —— 实测:
      - 同一个 pfId + 任意新 uuid -> 仍返回该角色原 gameUid/账号uuid
      - 编造 pfId -> 落到兜底绿服(10052), 且**不返回任何角色信息**
    => 拿到 pfId 就等于拿到该账号的全部登录凭据; 不需要手机/root/抓包。
  * host: p3cok.elexapp.com(国内可直连) / dsap3cok.elexapp.com(游戏客户端在用, 境外线路)

用法:
    python3 cok_gamesvc.py --pf-id ewanqf:1084D654F5A7FB599158 --pf cn_ewanqf \
            --package com.hcg.cok.ewanqf.guopan
"""
# --- 包自举: 让本文件既能 `python3 cok/core/xxx.py` 直接跑, 也能被平铺 import ---
import os as _os
import sys as _sys

_PKG_ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
if _os.path.isdir(_PKG_ROOT) and _PKG_ROOT not in _sys.path:
    _sys.path.insert(0, _PKG_ROOT)
_CORE = _os.path.join(_PKG_ROOT, "core")
if _os.path.isdir(_CORE) and _CORE not in _sys.path:
    _sys.path.insert(0, _CORE)

import hashlib
import json
import os
import ssl
import sys
import time
import urllib.parse
import urllib.request

SIG_SECRET = "@z4LugUwrDN0MqOJtzmHPK7Ss-k4taAUOZh1M3Yu9"
HOSTS = ["p3cok.elexapp.com", "dsap3cok.elexapp.com"]
PATH_LIST = "/gameservice/getserverlist.php"

DEFAULT_P = {
    "token": "CN",
    "country": "US",
    "version": "12.06.0",
    "versioncode": "1896",
    "flag": "ph",
    "lang": "zh_CN",
    "serverId": "COK2223",
}


def game_tcp_port(server_id):
    """从国服区服号推导游戏 TCP 端口。

    ``getserverlist.php`` 返回的是 HTTP 服务端口（通常为 80），不能直接
    用来建立 SmartFox TCP 会话。设备侧记录表明游戏端口遵循：
    ``32000 + (serverId % 100) * 10 + 1``，例如 2217 -> 32171、
    2218 -> 32181、2223 -> 32231。
    """
    try:
        return 32000 + (int(server_id) % 100) * 10 + 1
    except (TypeError, ValueError):
        return None


def sign(device_uuid, t):
    """sig = md5(uuid + t + 密钥)"""
    return hashlib.md5(("%s%s%s" % (device_uuid, int(t), SIG_SECRET)).encode()).hexdigest()


def build_url(pf_id, pf=None, channel=None, package=None, device_uuid=None,
              login_flag=1, t=None, host=None, extra=None):
    params = dict(DEFAULT_P)
    params.update({
        "uuid": device_uuid or os.urandom(8).hex(),
        "pfId": pf_id,
        "loginFlag": int(login_flag),
        "t": int(t if t is not None else time.time()),
    })
    if pf:
        params["pf"] = pf
    if channel:
        params["channel"] = channel
    if package:
        params["packageName"] = package
    if extra:
        params.update(extra)
    params["sig"] = sign(params["uuid"], params["t"])
    return "https://%s%s?%s" % (host or HOSTS[0], PATH_LIST, urllib.parse.urlencode(params))


def _fetch(url, timeout=15):
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    req = urllib.request.Request(url, headers={"User-Agent": "okhttp/3.12.1"})
    with urllib.request.urlopen(req, timeout=timeout, context=ctx) as r:
        return r.read().decode("utf-8", "replace")


def get_server_list(pf_id, pf=None, channel=None, package=None, device_uuid=None,
                    login_flag=1, t=None, extra=None, timeout=15):
    """-> dict(服务端 JSON)。失败抛 RuntimeError。"""
    last = None
    for host in HOSTS:
        url = build_url(pf_id, pf=pf, channel=channel, package=package,
                        device_uuid=device_uuid, login_flag=login_flag, t=t,
                        host=host, extra=extra)
        try:
            txt = _fetch(url, timeout=timeout)
            return json.loads(txt)
        except Exception as exc:      # 网络不通/非 JSON
            last = "%s: %s" % (host, exc)
    raise RuntimeError("getserverlist 失败 (%s)" % last)


def resolve_character(pf_id, pf=None, channel=None, package=None, device_uuid=None,
                      extra=None, timeout=15):
    """按 pfId 解析出游戏角色凭据。

    -> {"ok": bool, "gameUid","uuid","zn","serverId","ip","port","buildCode",
        "gameUserName","gameUserLevel","greenServer", "note"}
    ok=False 表示该 pfId 在游戏服还没有角色(果盘侧还没玩过这个号)。
    """
    js = get_server_list(pf_id, pf=pf, channel=channel, package=package,
                         device_uuid=device_uuid, login_flag=1, extra=extra,
                         timeout=timeout)
    out = {"ok": False, "note": "", "lastLoggedServer": js.get("lastLoggedServer"),
           "raw": js}
    sl = js.get("serverList") or []
    out["serverList"] = sl
    # 带角色的那一条(有 gameUid)
    hit = None
    for s in sl:
        if s.get("gameUid"):
            hit = s
            break
    if hit is None:
        out["note"] = ("该 pfId 在游戏服**没有角色**(serverList 里无 gameUid); "
                       "要么该渠道身份未在果盘登记, 要么还没在游戏里开过号")
        if sl:
            out["zone_fallback"] = sl[0].get("zone")
            out["ip"] = sl[0].get("ip")
            out["port"] = sl[0].get("port")
            out["serverId"] = sl[0].get("id")
        return out
    out.update({
        "ok": True,
        "gameUid": str(hit.get("gameUid")),
        "uuid": hit.get("uuid"),
        "zn": hit.get("zone"),
        "serverId": str(hit.get("id")),
        "ip": hit.get("ip"),
        "port": str(hit.get("port")),
        "gamePort": game_tcp_port(hit.get("id")),
        "buildCode": hit.get("buildCode"),
        "gameUserName": hit.get("gameUserName"),
        "gameUserLevel": hit.get("gameUserLevel"),
        "greenServer": hit.get("greenServer"),
        "note": "已按 pfId 解析出角色凭据(设备无关)",
    })
    return out


def main():
    import argparse
    ap = argparse.ArgumentParser(description="getserverlist.php 客户端")
    ap.add_argument("--pf-id", required=True)
    ap.add_argument("--pf")
    ap.add_argument("--channel")
    ap.add_argument("--package")
    ap.add_argument("--uuid", dest="device_uuid")
    ap.add_argument("--raw", action="store_true", help="打印原始 JSON")
    args = ap.parse_args()
    if args.raw:
        js = get_server_list(args.pf_id, pf=args.pf, channel=args.channel,
                             package=args.package, device_uuid=args.device_uuid)
        print(json.dumps(js, ensure_ascii=False, indent=2))
        return
    r = resolve_character(args.pf_id, pf=args.pf, channel=args.channel,
                          package=args.package, device_uuid=args.device_uuid)
    r.pop("raw", None)
    print(json.dumps(r, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
