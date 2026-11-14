#!/usr/bin/env python3
"""小七渠道(x7sy)账号密码登录 —— **纯 PC** 复刻, 不依赖手机/模拟器/root。

和果盘(guopan)是**同构**的: 渠道账号密码 -> 平台身份(pfId) -> 游戏服凭据。
区别只在于中间的协议:

* 果盘: XXTEA + GPXX protobuf, userapi.guopan.cn
* 小七: **AES-256-CBC/PKCS5**, URL 全密文, 表单 4 字段(r/c/s/t)

协议全貌(2026-11-13 实测, 逐字节复现通过)
------------------------------------------------
**加密层**(libx7NativeEncrypt.so 里硬编码的 key):

    key = 9510506338be6f69d5d1a3c47c554ab4      (32 字节 ASCII -> AES-256)
    iv  = 16 个随机字符, 取自 [0-9a-z]
    输出 = base64url( iv || AES-256-CBC(key, iv, PKCS5Padding(明文)) )

**URL**: 路径本身也被加密, 直接拼在网关后面::

    https://user.x7sy.com/ga.do/<base64url(iv||密文)>        普通接口
    https://market.x7sy.com/ga.do/public/<base64url(...)>    public 接口

**body**: form-urlencoded, 4 个字段::

    r = base64url(16 字节随机 nonce)
    c = base64url(iv||密文(json 明文))
    s = MD5 签名
    t = 毫秒时间戳

**登录接口**(插件 dex 里 `smwl/nk2.java` + `com/smwl/smsdk/asm.java` 实证)::

    POST /ga.do/<加密("/login_register/login")>
    明文 json = {"logindata": 账号, "loginpass": 密码,
                 "user_from": appkey, "is_simulator": "-1",
                 "isManualLogin": "0"}

**免密登录**(有缓存 token 时)::

    POST /ga.do/<加密("/user/auto_login")>
    明文 json = {"logindata": 账号, "jwtString": <jwt>,
                 "operate_type": "sdk", "user_from": appkey, "is_simulator": "-1"}

**响应**: 服务端返回的是**明文 JSON**(客户端解密后拿到的), 关键字段::

    {"errorno": 0, "jwt_string": "<JWT>", "tokenkey": "<32 hex>",
     "member_data": {"mid": "...", "username": "...", "phone": "..."},
     "smallaccount": {"guid": "...", "gid": "2327", "smallaccount_name": "..."}}

⚠ 本模块只负责**小七平台层**(账号密码 -> tokenkey/jwt)。
   tokenkey/jwt -> eWan openid -> pfId 这一步走 **SuperSDK**,
   见 :func:`supersdk_login` / `cok/core/cok_supersdk.py`。
"""
import base64
import hashlib
import json
import os
import random
import string
import time
import urllib.error
import urllib.parse
import urllib.request

# --- 包自举: 直接 `python3 cok/core/xxx.py` 时把 cok/ 加进 sys.path ---
import os as _os
import sys as _sys

_PKG_ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
if _os.path.isdir(_PKG_ROOT) and _PKG_ROOT not in _sys.path:
    _sys.path.insert(0, _PKG_ROOT)
_CORE = _os.path.join(_PKG_ROOT, "core")
if _os.path.isdir(_CORE) and _CORE not in _sys.path:
    _sys.path.insert(0, _CORE)


#: AES key —— libx7NativeEncrypt.so 里的硬编码常量(实测逐字节复现一致)
X7_AES_KEY = b"9510506338be6f69d5d1a3c47c554ab4"

#: 小七 SDK 的 appkey(渠道身份标识, 所有小七游戏通用)
X7_APPKEY = "e76922b1c512b2f1dc6035a6d38a0ff2"

#: 签名盐(so 里硬编码的 "prod#request#<b64>@2" 模板, 逐字节一致)
X7_SIGN_TAIL = ("prod#request#"
                 "MzM0M2Q1ZGJlMzBiNzgzZDgxMTIyYmY0ODI4Yzk0OTFmMWZkODVkN2RhOWQ4NjY1NzczOTRhZDc5M2IyYzVjMg"
                 "@2")

#: 各接口的 host
HOST_USER = "user.x7sy.com"
HOST_JAPI = "japi.x7sy.com"
HOST_MARKET = "market.x7sy.com"

#: IV 字符表(so 里 "0123456789abcdefghijklmnopqrstuvwxyz")
_IV_ALPHA = string.digits + string.ascii_lowercase

#: 签名消息里插入的 32 字符随机串取自的 62 字符集(so rodata 0x2fd45)
_RAND_ALPHA = ("qwertyuiopasdfghjklzxcvbnm"
               "QWERTYUIOPASDFGHJKLZXCVBNM"
               "1234567890")

_UA = "okhttp/4.9.3"


# --------------------------------------------------------------------------
# 加密层
# --------------------------------------------------------------------------
def _b64u(raw):
    """base64url, 不带 padding(和客户端一致)。"""
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def _b64u_decode(text):
    s = text.replace("-", "+").replace("_", "/")
    s += "=" * ((4 - len(s) % 4) % 4)
    return base64.b64decode(s)


def _rand_iv():
    """随机 16 字符 IV(客户端就是从 [0-9a-z] 里取 16 个)。"""
    return "".join(random.choice(_IV_ALPHA) for _ in range(16)).encode("ascii")


def encrypt(plain):
    """明文(bytes/str) -> base64url(iv || AES-256-CBC 密文)。"""
    if isinstance(plain, str):
        plain = plain.encode("utf-8")
    iv = _rand_iv()
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    from cryptography.hazmat.primitives import padding as _pad
    padder = _pad.PKCS7(128).padder()
    data = padder.update(plain) + padder.finalize()
    enc = Cipher(algorithms.AES(X7_AES_KEY), modes.CBC(iv)).encryptor()
    return _b64u(iv + enc.update(data) + enc.finalize())


def decrypt(text):
    """base64url(iv||密文) -> 明文 bytes; 失败返回 None。"""
    try:
        raw = _b64u_decode(text)
        if len(raw) < 32:
            return None
        from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
        from cryptography.hazmat.primitives import padding as _pad
        dec = Cipher(algorithms.AES(X7_AES_KEY), modes.CBC(raw[:16])).decryptor()
        data = dec.update(raw[16:]) + dec.finalize()
        unpad = _pad.PKCS7(128).unpadder()
        return unpad.update(data) + unpad.finalize()
    except Exception:  # noqa: BLE001
        return None


def _aes_encrypt(plain, iv):
    """AES-256-CBC/PKCS5 加密, 指定 iv 返回密文 bytes(不含 iv)。"""
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    from cryptography.hazmat.primitives import padding as _pad
    padder = _pad.PKCS7(128).padder()
    data = padder.update(plain) + padder.finalize()
    enc = Cipher(algorithms.AES(X7_AES_KEY), modes.CBC(iv)).encryptor()
    return enc.update(data) + enc.finalize()


def encrypt(plain):
    """明文(bytes/str) -> base64url(iv || AES-256-CBC 密文)。"""
    if isinstance(plain, str):
        plain = plain.encode("utf-8")
    iv = _rand_iv()
    return _b64u(iv + _aes_encrypt(plain, iv))


def _make_signature(c, r, ts, tail=X7_SIGN_TAIL):
    """小七签名 s = MD5(body + tail)。

    算法(2026-11-13 逐字节复现通过, 12 组真机 form_add 全对齐):
      1. SOURCE = c + r + ts
         c = base64url(iv||AES密文)  (body 里的 c 字段)
         r = base64url(16 字节随机 nonce)  (body 里的 r 字段)
         ts = 毫秒时间戳字符串(13 位)
      2. n = max(2, ts & 0x3f), cs = len(SOURCE) // n,
         lastlen = len(SOURCE) - (n-1)*cs
      3. body = block_{n-1}(lastlen) + block_{n-2}(cs) + ... + block_0(cs)
             即 SOURCE 按 n 块**逆序**拼接
      4. s = MD5(body + tail) 十六进制(32 字符)

    返回 (s_hex, body_bytes)。
    """
    source = (c + r + ts).encode("latin-1")
    total = len(source)

    n = max(2, int(ts) & 0x3f)
    cs = total // n
    lastlen = total - (n - 1) * cs

    # body = block_{n-1}(lastlen) + block_{n-2}(cs) + ... + block_0(cs)
    # source = block_0 + block_1 + ... + block_{n-1}
    # block_i = source[i*cs : (i+1)*cs]  (i = 0..n-2), block_{n-1} = source[(n-1)*cs:]
    parts = [source[(n - 1) * cs :]]  # block_{n-1} 首
    for i in range(n - 2, -1, -1):  # block_{n-2} ... block_0
        parts.append(source[i * cs : (i + 1) * cs])
    body = b"".join(parts)

    s = hashlib.md5(body + tail.encode("latin-1")).hexdigest()
    return s, body


# --------------------------------------------------------------------------
# 请求层
# --------------------------------------------------------------------------
def _post(host, path, params, public=False, timeout=20):
    """POST 一个加密接口, 返回 (http_status, 响应明文 dict 或 None)。

    路径是明文(如 "/user/auto_login"), 这里加密后拼到 /ga.do/ 后面。

    小七签名完整链路:
      c = base64url(iv||AES256-CBC(json))
      s, body = _make_signature(c, iv, ts, rand32)
      POST /ga.do/<encrypt(path)>  form: {r, c, s, t}
    """
    url = "https://%s/ga.do/%s%s" % (
        host, "public/" if public else "", encrypt(path))

    iv = _rand_iv()
    json_str = json.dumps(params, separators=(",", ":"))
    c = _b64u(iv + _aes_encrypt(json_str.encode("utf-8"), iv))
    r = _b64u(os.urandom(24))  # 真机 r 为 32 字符 base64url(24 字节)
    ts = str(int(time.time() * 1000))
    s, _body = _make_signature(c, r, ts)

    body = urllib.parse.urlencode({"r": r, "c": c, "s": s, "t": ts}).encode("ascii")
    req = urllib.request.Request(url, data=body, headers={
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": _UA,
        "Accept": "*/*",
        "Connection": "Keep-Alive",
        "Accept-Encoding": "gzip, deflate",
    })
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", "replace")
            status = resp.status
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", "replace")
        status = exc.code
    except Exception as exc:  # noqa: BLE001
        return -1, {"errorno": -1, "errormsg": str(exc)[:200]}
    try:
        return status, json.loads(raw)
    except Exception:  # noqa: BLE001
        return status, {"errorno": -1, "errormsg": raw[:300]}


# --------------------------------------------------------------------------
# 协议实现(给 cok_channels.resolve_protocol 用)
# --------------------------------------------------------------------------
def login(account, password, channel=None, verbose=False):
    """小七账号密码 -> 平台身份。

    与 :func:`channel_login` 完全一致，为 cok_web.py 通用路径
    ``proto.login(account, password, channel=..., verbose=...)`` 提供别名。
    """
    return channel_login(account, password, channel=channel, verbose=verbose)


def channel_login(account, password, channel=None, verbose=False):
    """小七账号密码 -> 平台身份。

    参数 ``channel`` 由 cok_web.py 传入(渠道 id), 本模块不使用, 仅为保持
    与协议模块统一签名 ``login(account, password, channel=None, verbose=False)``。

    返回 dict:
        ok/succeeded   是否登录成功
        stage          失败阶段(network / login / parse)
        errmsg         小七给的中文错误
        tokenkey       小七平台会话 token
        jwtString      小七平台 JWT(免密登录用)
        mid / guid    小七的 mid 与小号 guid
        pfId           游戏服认的平台身份(经 SuperSDK 换 eWan openid 后才有)
    """
    account = str(account or "").strip()
    password = str(password or "")
    if not account or not password:
        return {"ok": False, "succeeded": False, "stage": "input",
                "errmsg": "请填写小七账号和密码"}

    params = {
        "logindata": account,
        "loginpass": password,
        "user_from": X7_APPKEY,
        "is_simulator": "-1",
        "isManualLogin": "0",
    }
    status, data = _post(HOST_USER, "/login_register/login", params)
    if verbose:
        print("[x7] login http=%s errorno=%s msg=%s"
              % (status, data.get("errorno"), data.get("errormsg")))
    if status != 200:
        return {"ok": False, "succeeded": False, "stage": "network",
                "errmsg": data.get("errormsg") or ("HTTP %s" % status),
                "httpStatus": status}
    if data.get("errorno") not in (0, "0", None):
        return {"ok": True, "succeeded": False, "stage": "login",
                "errorno": data.get("errorno"),
                "errmsg": data.get("errormsg") or data.get("show_errormsg")
                          or "账号或密码不正确",
                "account": account}

    member = data.get("member_data") or {}
    small = data.get("smallaccount") or {}
    out = {
        "ok": True,
        "succeeded": True,
        "stage": "login",
        "account": account,
        "errmsg": data.get("errormsg") or "",
        "tokenkey": data.get("tokenkey") or "",
        "jwtString": data.get("jwt_string") or "",
        "mid": member.get("mid") or "",
        "username": member.get("username") or account,
        "phone": member.get("phone") or "",
        "guid": small.get("guid") or "",
        "gid": small.get("gid") or "",
        "smallAccountName": small.get("smallaccount_name") or "",
        "isSvip": data.get("isSvip"),
    }
    return out


def channel_login_by_token(account, tokenkey, jwt_string="", verbose=False):
    """用已有的 tokenkey/jwt 走"免密登录"(对应客户端的 /user/auto_login)。

    用途: 手机上登过一次之后, 把 token 拿到 PC 上用, 不必再输密码。
    """
    account = str(account or "").strip()
    if not account or not jwt_string:
        return {"ok": False, "succeeded": False, "stage": "input",
                "errmsg": "缺少账号或 jwt"}
    params = {
        "logindata": account,
        "jwtString": jwt_string,
        "operate_type": "sdk",
        "user_from": X7_APPKEY,
        "is_simulator": "-1",
    }
    status, data = _post(HOST_USER, "/user/auto_login", params)
    if verbose:
        print("[x7] auto_login http=%s errorno=%s" % (status, data.get("errorno")))
    if status != 200:
        return {"ok": False, "succeeded": False, "stage": "network",
                "errmsg": data.get("errormsg") or ("HTTP %s" % status)}
    if data.get("errorno") not in (0, "0", None):
        return {"ok": True, "succeeded": False, "stage": "login",
                "errmsg": data.get("errormsg") or "token 已失效",
                "errorno": data.get("errorno")}
    member = data.get("member_data") or {}
    small = data.get("smallaccount") or {}
    return {
        "ok": True, "succeeded": True, "stage": "login", "account": account,
        "tokenkey": data.get("tokenkey") or "", "jwtString": data.get("jwt_string") or "",
        "mid": member.get("mid") or "", "username": member.get("username") or account,
        "phone": member.get("phone") or "", "guid": small.get("guid") or "",
        "gid": small.get("gid") or "", "smallAccountName": small.get("smallaccount_name") or "",
    }


def list_identities(res, verbose=False):
    """小七账号下的游戏身份列表。

    小七只有**一个**游戏身份(不像果盘有一堆小号), 但仍按统一格式返回列表,
    方便网页/安卓那套"勾选加入"的 UI 复用。
    """
    items = []
    res = res or {}
    guid = res.get("guid") or ""
    name = res.get("smallAccountName") or res.get("username") or res.get("account") or ""
    if not guid and not name:
        return items
    items.append({
        "perGameId": guid,
        "pfId": res.get("pfId") or "",
        "name": name or guid,
        "hasCharacter": bool(res.get("hasCharacter")),
        "serverId": res.get("serverId") or "",
        "gameUid": res.get("gameUid") or "",
    })
    return items


def build_account(pf_id, platform_token="", gamesvc=None, channel=None):
    """pfId -> 账号库凭据(和果盘一样, 复用游戏服 getserverlist 那套)。"""
    import cok_channel_login as gl
    return gl.build_account_from_pf_id(pf_id, platform_token=platform_token,
                                       gamesvc=gamesvc, channel=channel or "x7sy")


def _selftest(verbose=True):
    """离线自证: 加密层 + 签名层用真机抓包的数据做逐字节核对。

    加密层: g22 的 /user/auto_login 密文逐字节一致。
    签名层: 用 g22 的 iv/ct/ts 重算 s, 与抓包一致。
    """
    # --- 加密层自证 (来自真机 frida 抓包 g22) ---
    cases = [
        ("/user/auto_login", "ljqati4a2nxpxtyy",
         "bGpxYXRpNGEybnhweHR5eUXFtBAhvjkRVTSbeWFoKeFaQTO_DDkS2bNMFFVskGvd"),
    ]
    ok = True
    for plain, iv, expect in cases:
        from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
        from cryptography.hazmat.primitives import padding as _pad
        padder = _pad.PKCS7(128).padder()
        data = padder.update(plain.encode()) + padder.finalize()
        enc = Cipher(algorithms.AES(X7_AES_KEY), modes.CBC(iv.encode())).encryptor()
        got = _b64u(iv.encode() + enc.update(data) + enc.finalize())
        good = (got == expect)
        ok = ok and good
        if verbose:
            print("[x7-selftest] %-22s %s" % (plain, "OK" if good else "FAIL"))
            if not good:
                print("   expect %s\n   got    %s" % (expect, got))

    # --- 签名层自证 (来自真机 frida 抓包 game9.jsonl, 12 组 form_add 全对齐) ---
    import json as _json
    sig_cases = []
    with open(_os.path.join(_PKG_ROOT, "..", "reverse", "evidence", "x7sy", "game9.jsonl")) as _f:
        _events = []
        for _line in _f:
            _line = _line.strip()
            if not _line:
                continue
            try:
                _o = _json.loads(_line)
            except Exception:
                continue
            _p = _o.get("msg", {}).get("payload", {})
            _events.append((_p.get("t"), _p))
    # 收集连续的 r,c,s,t 成组
    _i = 0
    while _i < len(_events):
        _t, _p = _events[_i]
        if _t == "form_add" and _p.get("key") == "r":
            _r = _p["value"]
            _c = _s = _ts = None
            _j = _i + 1
            while _j < len(_events) and _j < _i + 5:
                _t2, _p2 = _events[_j]
                if _t2 == "form_add":
                    _k = _p2.get("key")
                    if _k == "c":
                        _c = _p2.get("value")
                    elif _k == "s":
                        _s = _p2.get("value")
                    elif _k == "t":
                        _ts = _p2.get("value")
                _j += 1
            if _c and _s and _ts:
                sig_cases.append((_c, _r, _ts, _s))
        _i += 1

    sig_ok = True
    for _c, _r, _ts, _s_exp in sig_cases:
        _s, _body = _make_signature(_c, _r, _ts)
        _good = (_s == _s_exp)
        sig_ok = sig_ok and _good
        if verbose:
            print("[x7-selftest] %-22s %s" % (("签名层 t=" + _ts), "OK" if _good else "FAIL"))
            if not _good:
                print("   s     =", _s)
                print("   expected =", _s_exp)
    ok = ok and sig_ok
    return ok


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="x7sy channel login (pure PC)")
    ap.add_argument("account", nargs="?")
    ap.add_argument("password", nargs="?")
    ap.add_argument("--token", action="store_true", help="用 tokenkey 免密登录")
    ap.add_argument("--jwt", default="", help="免密登录用的 JWT")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        sys_exit = 0 if _selftest() else 1
        raise SystemExit(sys_exit)
    if not args.account:
        ap.print_help()
        raise SystemExit(2)
    if args.token:
        res = channel_login_by_token(args.account, "", args.jwt, verbose=True)
    else:
        res = channel_login(args.account, args.password or "", verbose=True)
    print(json.dumps(res, ensure_ascii=False, indent=2))
