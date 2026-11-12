#!/usr/bin/env python3
"""elex 账号服务客户端(纯静态逆出, 2026-10-28)。

目的: 在**没有手机**的机器上用「手机号/邮箱 + 密码」登录 elex 账号中心,
拿到 token / 角色列表, 用于登录别的游戏账号。

协议来源(APK 反编译, 见 cok/docs/COK-游戏服协议实测报告.md §8.1.6):
  * base: https://accountapi1.elexapp.com   (CN 顺序: accountapi3 -> accountapi1)
    debug 环境: http://169.53.247.133:81
  * URL  = base + 路径 + appId(**appId 是路径的一段, 不是 query**)
    登录 /services/v1/user/login/10001001
    换 token /services/v1/user/token/10001001
    注册 /services/v1/user/register/10001001
    改密 /services/v1/user/editpass/10001001
    验证码 /services/v1/verifycode/getcode/10001001
    防沉迷 /services/v1/user/addantiaddiction/10001001
  * 方法 POST, Content-Type: application/json, body = JSON
  * 公共参数(JsonHelper.fillCommonParams): ip / lang / country / time(ms) / sig
  * 密码(SignUtil.MD5PassWord):
        passmd5 = md5( md5(password) + "p392SYseXuu9wot9" ).lower()
  * 签名(SignUtil.createAccountSign):
        每个字段拼成 "key=value&" (嵌套 JSONObject 递归) -> 按大小写不敏感排序 -> 拼接
        sig = md5( 拼接结果 + "key=zOXjcEOc48UAj7fY" ).lower()
        (sig 本身不参与签名: 它在公共参数里最后 put)

用法:
    python3 cok_elex_account.py login 13800000000 '密码'
    python3 cok_elex_account.py getcode 13800000000
    python3 cok_elex_account.py token <uid> <token>
    python3 cok_elex_account.py raw login '{"email":"a@b.c","passmd5":"..."}'
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

import argparse
import hashlib
import json
import time
import urllib.error
import urllib.request

APPID = "10001001"
HOSTS = ("https://accountapi1.elexapp.com", "https://accountapi3.elexapp.com")

PATH_LOGIN = "/services/v1/user/login/"
PATH_TOKEN = "/services/v1/user/token/"
PATH_REGISTER = "/services/v1/user/register/"
PATH_EDITPASS = "/services/v1/user/editpass/"
PATH_VCODE = "/services/v1/verifycode/getcode/"
PATH_ANTIA = "/services/v1/user/addantiaddiction/"

#: 密码盐(SignUtil.MD5PassWord)
PWD_SALT = "p392SYseXuu9wot9"
#: 签名 key(SignUtil.createAccountSign)
SIGN_KEY = "key=zOXjcEOc48UAj7fY"


def md5(text):
    return hashlib.md5(text.encode("utf-8")).hexdigest()


def passmd5(password):
    """SignUtil.MD5PassWord: md5(md5(pwd) + salt).lower()"""
    return md5(md5(password) + PWD_SALT).lower()


def create_sign(obj):
    """SignUtil.createSign: 递归拼 "k=v&" -> 大小写不敏感排序 -> 拼接。"""
    parts = []
    for key in obj.keys():
        val = obj.get(key)
        if isinstance(val, dict):
            sub = create_sign(val)
            if sub:
                parts.append(sub)
            continue
        if val is None:
            continue
        s = val if isinstance(val, str) else str(val)
        if not s:
            continue
        parts.append("%s=%s&" % (key, s))
    if not parts:
        return ""
    parts.sort(key=lambda s: s.lower())
    return "".join(parts)


def account_sign(obj):
    """SignUtil.createAccountSign: md5(createSign(obj) + SIGN_KEY).lower()"""
    base = create_sign(obj)
    if not base:
        return ""
    return md5(base + SIGN_KEY).lower()


def fill_common_params(obj, ip="127.0.0.1", lang="zh", country="CN"):
    """JsonHelper.fillCommonParams: ip / lang / country / time / sig(最后算, 不含自身)。"""
    obj["ip"] = ip
    obj["lang"] = lang
    obj["country"] = country
    obj["time"] = str(int(time.time() * 1000))
    obj["sig"] = account_sign(obj)
    return obj


def call(path, body, host=None, timeout=20):
    """POST JSON 到 elex 账号服务, 返回解析后的 JSON。"""
    last = None
    hosts = (host,) if host else HOSTS
    for h in hosts:
        url = "%s%s%s" % (h, path, APPID)
        data = json.dumps(body, ensure_ascii=False).encode("utf-8")
        req = urllib.request.Request(
            url, data=data, method="POST",
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json; charset=utf-8",
                "User-Agent": ("Mozilla/5.0 (Linux; Android 12) AppleWebKit/537.36 "
                               "(KHTML, like Gecko) Chrome/107.0.0.0 Mobile Safari/537.36"),
            })
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                raw = resp.read().decode("utf-8", "replace")
            try:
                return json.loads(raw)
            except ValueError:
                return {"__raw__": raw, "__url__": url}
        except urllib.error.HTTPError as e:
            raw = e.read().decode("utf-8", "replace")
            last = {"__http__": e.code, "__raw__": raw[:400], "__url__": url}
        except Exception as e:  # noqa: BLE001
            last = {"__error__": str(e), "__url__": url}
    return last or {"__error__": "unknown"}


def login(account, password, ip="127.0.0.1"):
    """邮箱/账号登录: body = email + passmd5 + 公共参数。"""
    body = {"email": account, "passmd5": passmd5(password)}
    fill_common_params(body, ip=ip)
    return call(PATH_LOGIN, body)


def phone_login(phone, password, ip="127.0.0.1"):
    """手机号 + 密码登录(PhoneLoginActivity.requestLogin 的原始字段)。

    客户端原文: {"accountType": 1, "mobile": <手机号>, "countryCode": "86", "passmd5": <...>}
    accountType=1 实测有效(0 -> 500, 2/3 -> param error)。
    """
    body = {"accountType": 1, "mobile": phone, "countryCode": "86",
            "passmd5": passmd5(password)}
    fill_common_params(body, ip=ip)
    return call(PATH_LOGIN, body)


def get_vcode(phone, ip="127.0.0.1"):
    """发短信验证码(PhoneRegisterActivity.requestGetPhoneVcode 的原始字段)。

    body: {"moduleName":"game","accountType":1,"countryCode":"86","mobile":<手机号>}
    ⚠️ 服务端对**任意**号码都返回 success, 不能用它判断账号是否存在。
    """
    body = {"moduleName": "game", "accountType": 1, "countryCode": "86", "mobile": phone}
    fill_common_params(body, ip=ip)
    return call(PATH_VCODE, body)


def register(phone, code, password, ip="127.0.0.1"):
    """用短信验证码注册 elex 账号(PhoneRegisterActivity.requestRegister)。

    body: {"accountType":1,"countryCode":"86","mobile":<手机号>,"verifyCode":<验证码>,
           "pass":<明文密码>}
    → 成功: code=0, body 里带 uid/token
    → "手机号已注册": 说明该号码已有 elex 账号
    → 112101 verify code error: 验证码不对/过期
    """
    body = {"accountType": 1, "countryCode": "86", "mobile": phone,
            "verifyCode": code, "pass": password}
    fill_common_params(body, ip=ip)
    return call(PATH_REGISTER, body)


def token(uid, tok, ip="127.0.0.1"):
    body = {"uid": str(uid), "token": tok}
    fill_common_params(body, ip=ip)
    return call(PATH_TOKEN, body)


def main():
    ap = argparse.ArgumentParser(description="elex 账号服务客户端")
    sub = ap.add_subparsers(dest="cmd")
    p = sub.add_parser("login", help="账号/邮箱 + 密码登录")
    p.add_argument("account")
    p.add_argument("password")
    p = sub.add_parser("phone-login", help="手机号 + 密码登录")
    p.add_argument("phone")
    p.add_argument("password")
    p = sub.add_parser("getcode", help="发短信验证码")
    p.add_argument("phone")
    p = sub.add_parser("register", help="用短信验证码注册(会真的建号)")
    p.add_argument("phone")
    p.add_argument("code")
    p.add_argument("password")
    p = sub.add_parser("token", help="用 token 换会话")
    p.add_argument("uid")
    p.add_argument("token")
    p = sub.add_parser("raw", help="直接发一个路径+JSON body(自动补公共参数)")
    p.add_argument("path")
    p.add_argument("body")
    p.add_argument("--no-sign", action="store_true", help="不补 ip/lang/country/time/sig")
    args = ap.parse_args()

    if args.cmd == "login":
        res = login(args.account, args.password)
    elif args.cmd == "phone-login":
        res = phone_login(args.phone, args.password)
    elif args.cmd == "getcode":
        res = get_vcode(args.phone)
    elif args.cmd == "register":
        res = register(args.phone, args.code, args.password)
    elif args.cmd == "token":
        res = token(args.uid, args.token)
    elif args.cmd == "raw":
        body = json.loads(args.body)
        if not args.no_sign:
            fill_common_params(body)
        res = call(args.path, body)
    else:
        ap.print_help()
        return 1
    print(json.dumps(res, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
