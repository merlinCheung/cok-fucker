#!/usr/bin/env python3
"""果盘(guopan / ewanqf, flamingo SDK)渠道账号密码 -> 游戏服登录凭据, 纯 PC 复刻.

逆向结论(2026-10-29 实测, 对原方案三处事实订正见文末):
  * /gamesdk/ 载荷加密 = XXTEA(标准, 小端, 长度字在尾), **key = appKey "WVI2EOLJIW5YEE1Z"**
    (不是 AES; libEncryptorP.so/ttEncrypt 是字节跳动埋点, 与登录无关)
  * /xxdatareport.php(数据上报)用另一把 key = 签名盐 "#%$*)&*M<><vance"
  * 载荷是 protobuf(GPXX Proto); 账号命令在 f3.f17{ f1=subcmd, f2=设备块, f3=账号, f4=密码哈希 }
  * 密码登录: subcmd 101 取 salt(密码空)-> 服务器回 salt(f18.f4)
             -> 登录哈希 = MD5(salt + 明文密码) -> subcmd 102 提交
    (来自 com.flamingo.sdk.dex1.request.a.m8434: k0.m9332(salt + password))

用法:
    python3 cok_channel_login.py <果盘账号> <密码>
    python3 cok_channel_login.py <果盘账号> <密码> --json out.json

验证:
    # 离线自证: 回放归档 pcap, XXTEA/protobuf 逐字节往返 + pfId 推导核对(无需网络/账号)
    python3 cok_channel_login.py --selftest
    # 在线假号: 应回业务错(1026 密码/账号不正确), 而非协议错, 证明协议正确
    python3 cok_channel_login.py gptest001 wrongpass

协议时序(真机 + 模拟器抓包交叉验证, 顶层 cmd 恒为 1205, 真子命令在 f3):
    101 取 salt -> 响应 f3.f18{ f1=101, f4=salt }         (retcode 1034)
    102 密码登录 -> 成功响应 f3.f18{ f1=102, f2=认证信封, f3=guopanUid, f5=perGameId }
                 失败回 f3.f1=1026 + f3.f29=错误消息
    (可选) f3.f40{ f1=appid, f2=guopanUid } + 信封 = LOGINBETWEENAPP, 独立再换 perGameId
    平台身份: pfId = "ewanqf:1084" + perGameId  (前缀 1084 与 SDK OpenId 前缀一致)

已知限制(重要):
    果盘 HTTP 只能换出 **pfId**(+ SDK openId/token)。
    **gameUid / uuid 不由果盘下发** —— 它们是游戏服凭 pfId 首次登录时分配、
    落在设备 Cocos2dxPrefsFile.xml(即发卡机 cok_emu_login.py 的读取来源)。
    因此"账号密码 -> 完整 (pfId, gameUid, uuid) 三元组"无法只靠果盘 HTTP 补齐:
    拿到 pfId 后仍需走一次游戏服登录(新号会自动建号并分配 gameUid/uuid)。
    另: 手头无真实果盘账号的明文密码(账号库里存的是游戏服凭据, 非果盘密码),
    且约定不得拿用户真号做会踢人的登录, 故成功分支未用真号端到端跑通;
    协议本身已由两份抓包逐字节自证(--selftest 全绿)。
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
import base64
import hashlib
import http.client
import json
import os as _os
import re
import sys

APPKEY = b"WVI2EOLJIW5YEE1Z"       # /gamesdk/ 载荷 XXTEA key
REPORT_KEY = b"#%$*)&*M<><vance"    # /xxdatareport.php XXTEA key(备用)
HOST = "userapi.guopan.cn"
PATH = "/gamesdk/140514"
APPID = 140514

# 从真机/模拟器抓包解出的 subcmd=101 取-salt 明文模板(设备指纹块 + 账号槽).
# 结构: top.f3.f17{ f1=subcmd, f2=设备块, f3=账号, f4=密码哈希 }. 只替换 f1/f3/f4.
TEMPLATE_SALT101_HEX = (
    '080012d20108b50910001a0020013ac6010a0010681a0b73646b5f352e352e342e3328e08f1e306638ec07420231364a0060006a0070007801a20100a801e2c908b2011b416e64726f69642053444b206275696c7420666f722061726d3634b80124d00100e20100ea01206363626638386137666632393433333738653534353138333139316634383264f2012067306162787535313739333232303033363630343030303030303030323130348002008a02009202009a021063613464323932303333356238343431a20200aa0207616e64726f69641ae0010801100f8a01d801086512c6010a0010681a0b73646b5f352e352e342e3328e08f1e306638ec07420231364a0060006a0070007801a20100a801e2c908b2011b416e64726f69642053444b206275696c7420666f722061726d3634b80124d00100e20100ea01206363626638386137666632393433333738653534353138333139316634383264f2012067306162787535313739333232303033363630343030303030303030323130348002008a02009202009a021063613464323932303333356238343431a20200aa0207616e64726f69641a096770746573743030312200'
)

# 从真机抓包解出的"列小号"明文模板(cmd=1205, 子命令块 f3.f40, top.f3.f2=37).
# 订正: 此命令实为 GETSMALLACCOUNTGAMEUIN(subcmd 37, jadx 确认, 见 RE 方案 §8.4/§8.8),
#       早前误标为 LOGINBETWEENAPP(那其实是 subcmd 25). 函数/常量名属历史遗留, 行为 = 列小号.
# 结构: top.f2{ f1=1205, f2=guopanUid, f3=认证信封, f7=设备块 } + top.f3.f40{ f1=appid, f2=guopanUid }.
# 认证信封 = "Login_<guopanUid>_<appid>_<loginToken>". 只替换 guopanUid / 信封 token.
# (真机值: guopanUid=305273801, perGameId=D654F5A7FB599158 -> pfId=ewanqf:1084D654F5A7FB599158)
TEMPLATE_LOGINBETWEEN_HEX = (
    '080012ff0208b50910c9b7c891011a374c6f67696e5f3330353237333830315f3134303531345f323538356538303539363566336235353133323363616463313438663838326420013ab8020a0010681a0b73646b5f352e352e342e3328e08f1e306638ec07420231364a0060006a076e69753232323370007802a20100a801e2c908b2010650484b313130b80124d00100e2014039384543323934414635364234364638413939303035323337433231464644373636336639653365623838313665383563653233313138623834306232313834ea01203736333239356337633065373461366161346564306365363965636234333935f20120616d306b767778313739323430313134393630363030303030303030323130398002008a0200920240303138343030313634423845343134333835333235363645363932394432433463323836613337306465306262336264306233303230303136383736396539389a021035626139356566646332306464383339a20200aa02076f6e65706c75731a1108011025c2020a08e2c90810c9b7c89101'
)

# ------------------------- XXTEA (faithful port of com.flamingo.sdk.ud.c) -------------------------
_M = 0xFFFFFFFF
_DN = -1640531527  # 0x9E3779B9 (signed); java: sum -= 1640531527 == +DELTA

def _s32(x):
    x &= _M
    return x - 0x100000000 if x & 0x80000000 else x

def _U(x):
    return x & _M

def _b2i(b):
    n = len(b)
    out = [0] * (((n + 3) & (-4)) >> 2)
    for i in range(n):
        out[i >> 2] |= (b[i] & 255) << ((i & 3) << 3)
    return [_s32(x) for x in out]

def _i2b(ints, length):
    full = len(ints) << 2
    L = min(full, length)
    out = bytearray(length)
    for i in range(L):
        out[i] = ((_U(ints[i >> 2]) >> ((i & 3) << 3)) + 256) & 0xFF
    return bytes(out)

def xxtea_encrypt(data, key):
    if not data or key is None or len(key) != 16:
        return None
    i = len(data)
    i2 = ((i + 3) & (-4)) + 4
    buf = bytearray(i2); buf[:i] = data
    v = _b2i(bytes(buf)); k = _b2i(key)
    n = i2 >> 2
    v[n - 1] = i
    i6 = (52 // n) + 6
    i7 = n - 1
    z = _s32(i)
    if i7 > 0:
        summ = 0
        while i6 > 0:
            i6 -= 1
            summ = _s32(summ - 1640531527)
            e = (_U(summ) >> 2) & 3
            p = 0
            while p < i7:
                y = v[p + 1]
                z = _s32(((((_U(z) >> 5) ^ _U(y << 2)) + ((_U(y) >> 3) ^ _U(z << 4))) ^
                        ((y ^ summ) + (z ^ k[(p & 3) ^ e]))) + v[p])
                v[p] = z; p += 1
            y = v[0]
            z = _s32(v[i7] + ((((_U(z) >> 5) ^ _U(y << 2)) + ((_U(y) >> 3) ^ _U(z << 4))) ^
                             ((y ^ summ) + (z ^ k[e ^ (p & 3)]))))
            v[i7] = z
    return _i2b(v, len(v) << 2)

def xxtea_decrypt(data, key):
    if not data or key is None or len(key) != 16 or (len(data) & 3) != 0:
        return None
    i = len(data)
    v = _b2i(data); k = _b2i(key)
    n = i >> 2
    y = _s32(v[0]); i4 = n - 1
    if i4 > 0:
        summ = _s32(((52 // n) + 6) * _DN)
        while summ != 0:
            e = (_U(summ) >> 2) & 3
            p = i4
            while p > 0:
                z = v[p - 1]
                y = _s32(v[p] - (((y ^ summ) + (z ^ k[(p & 3) ^ e])) ^
                                (((_U(z) >> 5) ^ _U(y << 2)) + ((_U(y) >> 3) ^ _U(z << 4)))))
                v[p] = y; p -= 1
            z = v[i4]
            y = _s32(v[0] - (((y ^ summ) + (k[e ^ (p & 3)] ^ z)) ^
                            (((_U(z) >> 5) ^ _U(y << 2)) + ((_U(y) >> 3) ^ _U(z << 4)))))
            v[0] = y
            summ = _s32(summ + 1640531527)
    out_len = v[i4]
    if not (0 < out_len <= (len(v) << 2)):
        out_len = (len(v) << 2)
    return _i2b(v, out_len)

# ------------------------- protobuf exact-roundtrip codec -------------------------
def _rv(b, i):
    s = 0; r = 0
    while True:
        x = b[i]; i += 1
        r |= (x & 0x7f) << s; s += 7
        if not x & 0x80:
            return r, i

def _wv(n):
    out = bytearray()
    while True:
        x = n & 0x7f; n >>= 7
        if n:
            out.append(x | 0x80)
        else:
            out.append(x); return bytes(out)

def pb_parse(b):
    i = 0; out = []
    while i < len(b):
        tag, i = _rv(b, i)
        f = tag >> 3; wt = tag & 7
        if wt == 0:
            val, i = _rv(b, i); out.append([f, 0, val])
        elif wt == 2:
            ln, i = _rv(b, i); out.append([f, 2, b[i:i+ln]]); i += ln
        elif wt == 5:
            out.append([f, 5, b[i:i+4]]); i += 4
        elif wt == 1:
            out.append([f, 1, b[i:i+8]]); i += 8
        else:
            raise ValueError("bad wiretype %d" % wt)
    return out

def pb_serialize(items):
    out = bytearray()
    for f, wt, v in items:
        out += _wv((f << 3) | wt)
        if wt == 0:
            out += _wv(v)
        elif wt == 2:
            out += _wv(len(v)); out += v
        elif wt in (5, 1):
            out += v
    return bytes(out)

def pb_get(items, field):
    for f, wt, v in items:
        if f == field:
            return (wt, v)
    return None

def pb_set(items, field, wt, value):
    for it in items:
        if it[0] == field:
            it[1] = wt; it[2] = value
            return items
    items.append([field, wt, value]); return items

def pb_del(items, field):
    items[:] = [it for it in items if it[0] != field]
    return items

# ------------------------- GPXX account request build / send -------------------------
def md5hex(s):
    return hashlib.md5(s.encode() if isinstance(s, str) else s).hexdigest()

def build_account_request(account, passhash, subcmd):
    top = pb_parse(bytes.fromhex(TEMPLATE_SALT101_HEX))
    inner = pb_parse(pb_get(top, 3)[1])
    sub = pb_parse(pb_get(inner, 17)[1])
    pb_set(sub, 1, 0, subcmd)
    pb_set(sub, 3, 2, account.encode())
    pb_set(sub, 4, 2, passhash.encode())
    pb_set(inner, 17, 2, pb_serialize(sub))
    pb_set(top, 3, 2, pb_serialize(inner))
    return pb_serialize(top)

def build_loginbetween_request(guopan_uid, envelope):
    """组装"列小号"请求 GETSMALLACCOUNTGAMEUIN(cmd=1205, f3.f40, subcmd 37), 拿 per-game id.

    (命名订正: 此前误标 LOGINBETWEENAPP; 真正的 LOGINBETWEENAPP 是 subcmd 25. 见 RE 方案 §8.4/§8.8.
     函数名属历史遗留, 不改以免牵动调用处; 行为 = 列出该果盘账号下小号及各自 game uin/perGameId.)

    忠实复刻真机抓包: 顶层 f2{f1=1205, f2=guopanUid, f3=认证信封}, 子命令 f3.f40{f1=appid, f2=guopanUid}.
    只替换 guopanUid(两处)与认证信封; 设备块沿用模板里的真机值。
    """
    return build_getsmall_request(guopan_uid, envelope)


# ================= 果盘小号命令族 (subcmd 21/25/37/39/41/43) =================
# 字段号来源(2026-10-29 jadx 反编译 com/GPXX/Proto/z.java):
#   * 类 t0(=top.f3 容器)的 mo11() 给出每个命令块在容器内的 tag
#   * 各命令块类的 mo10()/mo11() 给出块内字段 tag
#   * 交叉校验: a3=17、u=40 与真机抓包逐字节重建一致
#
# subcmd -> (容器字段号, 块类, 块内字段)
#   15 UNITYLOGIN              f17 a3 {f1=101取salt/102密码/104带token, f2=channel, f3=账号, f4=密码哈希}
#   21 GETRANDOMACCOUNTNAME    f23 q
#   25 LOGINBETWEENAPP         f27 g0 {f1=109}
#   37 GETSMALLACCOUNTGAMEUIN  f40 u  {f1=appId, f2=guopanUid}
#   39 CREATESMALLACCOUNT..    f42 j  {f1=appId, f2=guopanUid, f3=小号名}
#   41 MODIFYSMALLACCOUNT..    f44 o0 {f1=List<int>, f2=o}
#   43 LOGINSMALLACCOUNT       f46 k0 {f1=appId, f2=o}
#   45 CANCELDESTROYACCOUNT    f48 b
#   47 CHECKLOGINSTATUS        f50 f
# 响应侧: f41=w{f1:[o]} (小号列表) / f43=l{f1:o} (建号结果)
CMD_BLOCK_FIELD = {
    3: 5, 5: 8, 9: 11, 13: 15, 15: 17, 21: 23, 25: 27,
    37: 40, 39: 42, 41: 44, 43: 46, 45: 48, 47: 50,
}


def build_cmd_request(subcmd, guopan_uid, envelope, block=None, token=None):
    """基于真机模板拼一条 /gamesdk 请求: 改 subcmd + 换命令块。

    模板是抓包里的 subcmd 37 请求, 其顶层 = {f1:0, f2:cmd块(y0), f3:容器(t0)}。
    这里只替换: cmd块里的 guopanUid / 认证信封, 容器里的 subcmd / 命令块。
    """
    top = pb_parse(bytes.fromhex(TEMPLATE_LOGINBETWEEN_HEX))
    head = pb_parse(pb_get(top, 2)[1])
    pb_set(head, 2, 0, int(guopan_uid))
    pb_set(head, 3, 2, (token if token is not None else envelope).encode()
           if isinstance(token if token is not None else envelope, str)
           else (token if token is not None else envelope))
    pb_set(top, 2, 2, pb_serialize(head))
    inner = pb_parse(pb_get(top, 3)[1])
    pb_set(inner, 2, 0, int(subcmd))
    # 清掉模板自带的命令块(属于 subcmd 37), 再放本 subcmd 的块
    for fld in set(CMD_BLOCK_FIELD.values()):
        pb_del(inner, fld)
    if block is not None:
        pb_set(inner, CMD_BLOCK_FIELD[subcmd], 2, block)
    pb_set(top, 3, 2, pb_serialize(inner))
    return pb_serialize(top)


def _blk(pairs):
    """按 [(field, wiretype, value)] 拼一个 protobuf 子块。"""
    return pb_serialize([list(p) for p in pairs])


def build_getsmall_request(guopan_uid, envelope):
    """subcmd 37 GETSMALLACCOUNTGAMEUIN: 列该果盘账号下的小号。"""
    return build_cmd_request(37, guopan_uid, envelope,
                             _blk([(1, 0, APPID), (2, 0, int(guopan_uid))]))


def build_create_small_request(guopan_uid, envelope, name):
    """subcmd 39 CREATESMALLACCOUNTGAMEUIN: 建小号(果盘后端登记新的 perGameId)。"""
    return build_cmd_request(39, guopan_uid, envelope,
                             _blk([(1, 0, APPID), (2, 0, int(guopan_uid)),
                                   (3, 2, name.encode())]))


def build_login_small_request(guopan_uid, envelope, small_o):
    """subcmd 43 LOGINSMALLACCOUNT: 选中小号进游戏。

    small_o = 小号对象 o 的**原始字节**(直接从 subcmd 37 响应里原样回传, 最保真)。
    """
    return build_cmd_request(43, guopan_uid, envelope,
                             _blk([(1, 0, APPID), (2, 2, small_o)]))


def build_loginbetweenapp_request(guopan_uid, envelope, token):
    """subcmd 25 LOGINBETWEENAPP: 用第三方 App 的 token 换果盘会话(账号密码流程用不到)。"""
    return build_cmd_request(25, guopan_uid, envelope,
                             _blk([(1, 0, 109)]), token=token)


def parse_small_accounts(pt):
    """从响应里解出小号列表 / 单个小号对象。

    返回 {"retcode": int, "list": [ {appId,guopanUid,perGameId,gameUin,name,raw}, ... ],
           "single": {...} or None}
    """
    out = {"retcode": None, "list": [], "single": None}
    if not pt:
        return out
    top = pb_parse(pt)
    f3 = pb_get(top, 3)
    if not f3:
        return out
    inner = pb_parse(f3[1])
    rc = pb_get(inner, 1)
    out["retcode"] = rc[1] if rc else None
    emsg = pb_get(inner, 29)
    if emsg:
        try:
            out["errmsg"] = emsg[1].decode()
        except Exception:
            out["errmsg"] = emsg[1].hex()

    def _o(raw):
        o = pb_parse(raw)
        d = {"raw": raw}
        for f, wt, v in o:
            if wt == 2:
                try:
                    d["f%d" % f] = v.decode()
                except Exception:
                    d["f%d" % f] = v.hex()
            else:
                d["f%d" % f] = v
        return {
            "appId": d.get("f1"), "guopanUid": d.get("f2"),
            "perGameId": d.get("f3"), "gameUin": d.get("f4"),
            "name": d.get("f6"), "raw": raw,
        }

    # f41 = w{f1: [o,...]}  小号列表
    blk = pb_get(inner, 41)
    if blk:
        try:
            w = pb_parse(blk[1])
            for f, wt, v in w:
                if f == 1 and wt == 2:
                    try:
                        sub = pb_parse(v)
                        if sub and sub[0][0] == 1:      # o 的第一个字段是 f1
                            out["list"].append(_o(v))
                    except Exception:
                        pass
        except Exception:
            pass
    # f43 = l{f1: o}  单个小号(建号/改号结果)
    blk = pb_get(inner, 43)
    if blk:
        try:
            l = pb_parse(blk[1])
            for f, wt, v in l:
                if f == 1 and wt == 2:
                    out["single"] = _o(v)
        except Exception:
            pass
    return out


def list_small_accounts(guopan_uid, envelope, verbose=True):
    """已登录态下拉小号列表(subcmd 37)。"""
    st, pt = post(build_getsmall_request(guopan_uid, envelope))
    r = parse_small_accounts(pt)
    if verbose:
        print("[small  ] HTTP %d retcode=%s 小号数=%d" % (st, r.get("retcode"), len(r["list"])))
        for s in r["list"]:
            print("           perGameId=%s gameUin=%s 名字=%r"
                  % (s["perGameId"], s["gameUin"], s["name"]))
    r["http"] = st
    return r


def create_small_account(guopan_uid, envelope, name, verbose=True):
    """建小号(subcmd 39) -> 果盘后端登记新的 perGameId -> 新 pfId。"""
    st, pt = post(build_create_small_request(guopan_uid, envelope, name))
    r = parse_small_accounts(pt)
    if verbose:
        print("[create ] HTTP %d retcode=%s errmsg=%r"
              % (st, r.get("retcode"), r.get("errmsg")))
        if r.get("single"):
            s = r["single"]
            print("           新小号 perGameId=%s gameUin=%s 名字=%r"
                  % (s.get("perGameId"), s.get("gameUin"), s.get("name")))
    r["http"] = st
    return r


def login_small_account(guopan_uid, envelope, small_o, verbose=True):
    """选中小号进游戏(subcmd 43)。small_o = 小号对象原始字节。"""
    st, pt = post(build_login_small_request(guopan_uid, envelope, small_o))
    r = parse_small_accounts(pt)
    if verbose:
        print("[pick   ] HTTP %d retcode=%s errmsg=%r"
              % (st, r.get("retcode"), r.get("errmsg")))
        if r.get("single"):
            s = r["single"]
            print("           perGameId=%s gameUin=%s 名字=%r"
                  % (s.get("perGameId"), s.get("gameUin"), s.get("name")))
    r["http"] = st
    return r


def post(plaintext):
    ct = xxtea_encrypt(plaintext, APPKEY)
    body = base64.encodebytes(ct)   # MIME 76-col base64
    conn = http.client.HTTPConnection(HOST, 80, timeout=20)
    conn.request("POST", PATH, body=body, headers={
        "Host": HOST, "Content-Type": "application/x-www-form-urlencoded",
        "Content-Length": str(len(body)), "User-Agent": "okhttp/3.12.1"})
    r = conn.getresponse(); data = r.read(); conn.close()
    pt = None
    try:
        ct2 = base64.b64decode(re.sub(rb"\s+", b"", data.strip()))
        pt = xxtea_decrypt(ct2, APPKEY)
    except Exception:
        pass
    return r.status, pt

def parse_resp(pt):
    """-> dict: retcodes + response account block f18.* / f15.* / f40.* if present."""
    if not pt:
        return {}
    out = {"retcodes": []}
    top = pb_parse(pt)
    f3 = pb_get(top, 3)
    if not f3:
        return out
    inner = pb_parse(f3[1])
    for f, wt, v in inner:
        if wt == 0:
            out["retcodes"].append((f, v))
    # 顶层返回码: f3.f1 是主返回码(0=成功, 1034=ELogin_RequestSaltOK, 1026=账号/密码错).
    rc = pb_get(inner, 1)
    out["retcode"] = rc[1] if rc else None
    # 错误消息(失败时服务端放在 f3.f29, UTF-8).
    emsg = pb_get(inner, 29)
    if emsg:
        try:
            out["errmsg"] = emsg[1].decode()
        except Exception:
            out["errmsg"] = emsg[1].hex()
    for blk in (18, 15, 40, 16, 41):
        sub = pb_get(inner, blk)
        if sub:
            try:
                si = pb_parse(sub[1])
            except Exception:
                continue
            for f, wt, v in si:
                key = "f%d.f%d" % (blk, f)
                if wt == 2:
                    try:
                        out[key] = v.decode()
                    except Exception:
                        out[key] = v.hex()
                else:
                    out[key] = v
    return out

# 游戏侧平台身份派生: 实测 niu2223(== 账号库 <uid-guopan-intl>)得到
#   登录成功响应 f18.f5 = "D654F5A7FB599158"  -> platformToken = "1084" + f18.f5
#   pfId   = "ewanqf:" + platformToken
# "1084" 前缀与 SDK OpenId 前缀一致(见 RE 方案 §2.2); 目前仅一个真号确认, 视为推断。
PFID_PREFIX = "1084"

def derive_platform_identity(resp):
    """从登录成功响应里派生游戏服认的平台身份(pfId / platformToken)。

    返回 {} 表示响应里没有 per-game id(登录未成功 / 字段缺失)。
    """
    per_game = resp.get("f18.f5")
    if not isinstance(per_game, str) or not per_game:
        return {}
    platform_token = PFID_PREFIX + per_game
    return {
        "perGameId": per_game,
        "platformToken": platform_token,
        "pfId": "ewanqf:" + platform_token,
        "pf": "cn_ewanqf",
        "guopanUid": resp.get("f18.f3"),
        "authEnvelope": resp.get("f18.f2"),
    }

def loginbetween(guopan_uid, envelope, verbose=True):
    """已登录态下换游戏侧 per-game id(cmd=1205, f3.f40). 返回 parse_resp dict。

    真机抓包里 102 成功响应已直接带 f18.f5; 这一步是独立/兜底通道:
    当 102 响应未带 per-game id(某些渠道/版本分两步)时, 用 guopanUid + 认证信封再换一次。
    """
    st, pt = post(build_loginbetween_request(guopan_uid, envelope))
    r = parse_resp(pt)
    if verbose:
        print("[betwn] HTTP %d retcode=%s f18.f5=%r"
              % (st, r.get("retcode"), r.get("f18.f5")))
    return r

def channel_login(account, password, verbose=True):
    """果盘账号密码 -> 游戏服平台身份(pfId/platformToken + SDK openId/token)。

    流程(真机+模拟器抓包实证): 101 取 salt -> 102 密码登录 -> 成功响应 f18 直接带
    per-game id(f18.f5) / guopanUid(f18.f3) / 认证信封(f18.f2); 若未带 f5 则用
    guopanUid+信封走 LOGINBETWEENAPP(f40) 兜底。
    """
    # 1) subcmd 101: 取 salt(密码哈希留空)
    st1, pt1 = post(build_account_request(account, "", 101))
    r1 = parse_resp(pt1)
    salt = r1.get("f18.f4")   # salt 固定在 f18.f4
    if verbose:
        print("[salt ] HTTP %d retcode=%s salt=%r" % (st1, r1.get("retcode"), salt))
    if not (isinstance(salt, str) and salt):
        return {"ok": False, "stage": "salt", "retcode": r1.get("retcode"),
                "errmsg": r1.get("errmsg"), "resp": r1}
    # 2) subcmd 102: 密码哈希 = MD5(salt + 明文密码)
    passhash = md5hex(salt + password)
    st2, pt2 = post(build_account_request(account, passhash, 102))
    r2 = parse_resp(pt2)
    login_fields = {k: v for k, v in r2.items() if k not in ("retcodes",)}
    if verbose:
        print("[login] HTTP %d retcode=%s f18.f5=%r errmsg=%r"
              % (st2, r2.get("retcode"), r2.get("f18.f5"), r2.get("errmsg")))
    # 登录成功判定: 主返回码 f3.f1 == 0 且账号块回执 f18.f1 == 102.
    ok = (r2.get("retcode") == 0) and (r2.get("f18.f1") == 102)
    if not ok:
        return {"ok": False, "stage": "login", "account": account,
                "salt": salt, "passhash": passhash,
                "retcode": r2.get("retcode"), "errmsg": r2.get("errmsg"),
                "login_fields": login_fields,
                "note": "假号/错密 -> 业务错(1026=账号或密码不正确), 协议正确",
                "login_pt_hex": pt2.hex() if pt2 else None}
    # 3) 派生平台身份. 102 成功响应一般已带 f18.f5; 否则用 f40 兜底换一次.
    identity = derive_platform_identity(r2)
    used_loginbetween = False
    if not identity:
        guopan_uid = r2.get("f18.f3")
        envelope = r2.get("f18.f2")
        if guopan_uid and envelope:
            r3 = loginbetween(guopan_uid, envelope, verbose=verbose)
            identity = derive_platform_identity(r3)
            used_loginbetween = True
    result = {
        "ok": True, "account": account, "salt": salt, "passhash": passhash,
        "guopanUid": r2.get("f18.f3"), "authEnvelope": r2.get("f18.f2"),
        "sdkToken": r2.get("f18.f2"),
        "retcode": r2.get("retcode"),
        "login_retcodes": r2.get("retcodes") or [],
        "used_loginbetween": used_loginbetween,
        "login_fields": login_fields,
        "login_pt_hex": pt2.hex() if pt2 else None,
    }
    result.update(identity)   # perGameId / platformToken / pfId / pf ...
    if identity:
        result["note"] = ("果盘侧已换出平台身份(pfId). 注意: gameUid/uuid 由游戏服"
                          "凭 pfId 首登时分配, 不在果盘响应里, 需再走游戏服登录获取.")
    else:
        result["ok"] = False
        result["stage"] = "identity"
        result["note"] = "登录成功但响应里没解出 per-game id(字段位可能随版本变化)"
    return result

# ------------------------- offline selftest: replay archived pcaps -------------------------
import os as _os
import struct as _struct

_EVID = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)),
                      "evidence", "chanlogin")

def _pcap_packets(path):
    data = open(path, "rb").read()
    magic = data[:4]
    endian = "<" if magic == b"\xd4\xc3\xb2\xa1" else ">"
    linktype = _struct.unpack(endian + "IHHiIII", data[:24])[6]
    off = 24
    while off + 16 <= len(data):
        _, _, caplen, _ = _struct.unpack(endian + "IIII", data[off:off + 16])
        off += 16
        yield linktype, data[off:off + caplen]
        off += caplen

def _tcp_payload(linktype, pkt):
    if linktype == 276:        # LINUX_SLL2
        proto = _struct.unpack(">H", pkt[0:2])[0]; l3 = pkt[20:]
    elif linktype == 1:        # EN10MB
        proto = _struct.unpack(">H", pkt[12:14])[0]; l3 = pkt[14:]
    else:
        return None
    if proto != 0x0800 or len(l3) < 20 or l3[9] != 6:
        return None
    ihl = (l3[0] & 0x0f) * 4
    tcp = l3[ihl:]
    if len(tcp) < 20:
        return None
    sport, dport, seq = _struct.unpack(">HHI", tcp[0:8])
    doff = (tcp[12] >> 4) * 4
    return (sport, dport), seq, tcp[doff:]

def _pcap_http_bodies(path):
    streams = {}
    for lt, pkt in _pcap_packets(path):
        r = _tcp_payload(lt, pkt)
        if not r:
            continue
        key, seq, pl = r
        if pl:
            streams.setdefault(key, {})[seq] = pl
    for key, segs in streams.items():
        buf = b"".join(segs[s] for s in sorted(segs))
        i = 0
        while True:
            he = buf.find(b"\r\n\r\n", i)
            if he < 0:
                break
            head = buf[i:he]
            m = re.search(rb"[Cc]ontent-[Ll]ength:\s*(\d+)", head)
            clen = int(m.group(1)) if m else 0
            bs = he + 4
            # 响应行是 "HTTP/1.1 200 OK"(无路径), 无法靠路径区分请求/响应方向,
            # 故对每个 body 都产出, 由调用方用 XXTEA+protobuf 是否解成功来过滤
            # (xxdatareport 用另一把 key, 会解密失败而自动排除).
            if clen and not head.startswith(b"POST /xxdatareport"):
                yield head[:4], buf[bs:bs + clen]
            i = bs + clen
            if i >= len(buf):
                break

def selftest(verbose=True):
    """离线自证: 回放归档 pcap, 断言 XXTEA 往返 + protobuf 结构逐字节一致,
    并核对 salt / per-game id / pfId 推导与真机值一致。无需网络/设备。"""
    pcaps = [_os.path.join(_EVID, "capture_phone_gcsdk.pcap"),
             _os.path.join(_EVID, "capture_emulator_login.pcap")]
    checked = rt_ok = pb_ok = 0
    salts, pergames = set(), set()
    for path in pcaps:
        if not _os.path.exists(path):
            if verbose:
                print("[selftest] skip (missing): %s" % path)
            continue
        for _meth, body in _pcap_http_bodies(path):
            try:
                ct = base64.b64decode(re.sub(rb"\s+", b"", body.strip()))
                pt = xxtea_decrypt(ct, APPKEY)
            except Exception:
                continue
            if not pt:
                continue
            checked += 1
            if xxtea_encrypt(pt, APPKEY) == ct:
                rt_ok += 1
            top = pb_parse(pt)
            if pb_serialize(top) == pt:
                pb_ok += 1
            r = parse_resp(pt)
            if isinstance(r.get("f18.f4"), str) and r.get("f18.f1") == 101:
                salts.add(r["f18.f4"])
            if isinstance(r.get("f18.f5"), str) and r["f18.f5"]:
                pergames.add(r["f18.f5"])
    ok = checked > 0 and rt_ok == checked and pb_ok == checked
    if verbose:
        print("[selftest] /gamesdk 帧 %d | XXTEA 往返一致 %d | protobuf 往返一致 %d"
              % (checked, rt_ok, pb_ok))
        print("[selftest] 抓到 salt=%s" % sorted(salts))
        for pg in sorted(pergames):
            print("[selftest] per-game id=%s -> pfId=ewanqf:%s%s" % (pg, PFID_PREFIX, pg))
    # 已知真机值交叉校验(若该样本在场)
    if "D654F5A7FB599158" in pergames:
        want = "ewanqf:1084D654F5A7FB599158"
        got = "ewanqf:" + PFID_PREFIX + "D654F5A7FB599158"
        assert got == want, "pfId 推导不符: %s != %s" % (got, want)
        if verbose:
            print("[selftest] 真机 pfId 推导核对通过: %s" % got)
    # LOGINBETWEEN 模板往返
    tpl = bytes.fromhex(TEMPLATE_LOGINBETWEEN_HEX)
    assert build_loginbetween_request(305273801,
        "Login_305273801_140514_2585e805965f3b551323cadc148f882d") == tpl, \
        "LOGINBETWEEN 模板往返失败"
    if verbose:
        print("[selftest] LOGINBETWEEN(f40) 模板逐字节重建通过")
    # --- 小号命令族模板结构断言 (字段号来自 jadx 反编译, 与抓包交叉校验) ---
    env = "Login_305273801_140514_2585e805965f3b551323cadc148f882d"
    uid = 305273801

    def _inner(req):
        t = pb_parse(req)
        return pb_parse(pb_get(t, 3)[1])

    def _field(items, f):
        g = pb_get(items, f)
        return pb_parse(g[1]) if g else None

    i = _inner(build_getsmall_request(uid, env))
    assert pb_get(i, 2)[1] == 37 and _field(i, 40) is not None, "subcmd37 模板结构错"
    assert pb_get(_field(i, 40), 1)[1] == APPID and pb_get(_field(i, 40), 2)[1] == uid, \
        "subcmd37 块字段错"

    i = _inner(build_create_small_request(uid, env, "小号A"))
    assert pb_get(i, 2)[1] == 39, "subcmd39 subcmd 错"
    j = _field(i, 42)
    assert j and pb_get(j, 1)[1] == APPID and pb_get(j, 2)[1] == uid \
        and pb_get(j, 3)[1].decode() == "小号A", "subcmd39 块字段错"

    o_raw = bytes.fromhex("0800a801e2c908b2011a10443136353446354137464235394146")
    i = _inner(build_login_small_request(uid, env, o_raw))
    assert pb_get(i, 2)[1] == 43, "subcmd43 subcmd 错"
    k = _field(i, 46)
    assert k and pb_get(k, 1)[1] == APPID and pb_get(k, 2)[1] == o_raw, "subcmd43 块字段错"

    i = _inner(build_loginbetweenapp_request(uid, env, "TOKEN"))
    assert pb_get(i, 2)[1] == 25 and pb_get(_field(i, 27), 1)[1] == 109, "subcmd25 结构错"
    if verbose:
        print("[selftest] 小号命令族模板(subcmd 25/37/39/43)结构断言通过")
    # --- 抓包里的 subcmd 38 响应应能解出小号列表(端到端解析自证) ---
    found_small = False
    for path in pcaps:
        if not _os.path.exists(path):
            continue
        for _meth, body in _pcap_http_bodies(path):
            try:
                ct = base64.b64decode(re.sub(rb"\s+", b"", body.strip()))
                pt = xxtea_decrypt(ct, APPKEY)
            except Exception:
                continue
            if not pt:
                continue
            sr = parse_small_accounts(pt)
            if sr["list"]:
                s = sr["list"][0]
                found_small = True
                if verbose:
                    print("[selftest] 抓包小号: perGameId=%s gameUin=%s 名字=%r"
                          % (s["perGameId"], s["gameUin"], s["name"]))
                assert s["perGameId"] == "D654F5A7FB599158", "小号 perGameId 解析错"
                assert s["name"] == "小强", "小号名字解析错"
                assert s["gameUin"] == 1791267779, "小号 gameUin 解析错"
    if verbose:
        print("[selftest] 小号列表解析: %s" % ("PASS" if found_small else "未在抓包中找到"))
        print("[selftest] 结论: %s" % ("PASS" if ok else "FAIL"))
    return ok

# ================= 一键"账号密码 -> 可直连的游戏服凭据" =================
# 果盘渠道的公共参数(与包绑定, 不随账号变化)。区服相关字段必须以
# getserverlist.php 按 pfId 返回的结果为准，角色可能迁服。
#
# ⚠ signCode **不在这里写死**:
#   signCode = md5(hashCode(certDER) + "." + hex(certDER)), 只跟**渠道包的签名证书**有关,
#   而渠道包会换证书 —— 实测 66手游(com.hcg.cok.ewanqf.guopan)包 2026-11-10 更新后
#   证书就变了, signCode 从 76ea103d... 变成 84869a86...。
#   写死的值一过期就登不上, 所以运行时从账号库(存的是真机登录复原的真值)取,
#   见 _resolve_sign_code()。
CHANNEL_TEMPLATE = {
    "pf": "cn_ewanqf",
    "channel": "cn_ewanqf",
    "packageName": "com.hcg.cok.ewanqf.guopan",
    "signCode": "",
    "host": "txaia-cok.elexapp.com",
    "port": 32231,
}


def _signcode_cache_path():
    """signCode 的本地缓存(gitignored, 跟着 accounts.DATA_ROOT 走)。"""
    try:
        import cok_accounts as accounts
        return _os.path.join(accounts.DATA_ROOT, "sign-codes.json")
    except Exception:  # noqa: BLE001
        return ""


def _load_signcode_cache():
    path = _signcode_cache_path()
    if not path:
        return {}
    try:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
        return data if isinstance(data, dict) else {}
    except (OSError, ValueError):
        return {}


def _save_signcode_cache(data):
    path = _signcode_cache_path()
    if not path or not data:
        return
    try:
        _os.makedirs(_os.path.dirname(path), exist_ok=True)
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=False, indent=1)
        _os.replace(tmp, path)
    except OSError:
        pass


def _resolve_sign_code(package_name=None, fallback="", pf=None):
    """渠道包的 signCode —— 从账号库里取真值。

    为什么不在代码里写死: 渠道包更新会换签名证书, signCode 跟着变
    (见 CHANNEL_TEMPLATE 上面的注释)。账号库里存的是从真机登录复原的
    真值, 那是唯一可靠的来源。

    取值顺序(越靠前越准):
      1. **同 packageName** 的账号 —— 就是这个渠道包签发的
      2. **同 pf 渠道** 的账号(如 cn_ewanqf) —— 同一发行渠道
      3. **任意**账号的 signCode —— 服务端不严格校验, 有一个总比空强
         (空 signCode 会让账号被判"凭据不完整", 直接连不上)
      4. **本地缓存** sign-codes.json —— 账号库被清空/删号后仍然有
      5. **APK 内置种子** cok_seed.json —— 构建期烘焙, 别人直接装 APK 时
         设备上既没有账号库也没有缓存, 只剩这一份

    同一个 packageName 下可能有多个号(包换过证书, signCode 跟着变),
    按**入库时间取最新**的, 它最接近当前装的包。

    取到的真值会顺手按 packageName 写进本地缓存, 账号删了也不丢。

    返回 (signCode, 来源说明); 找不到返回 (fallback, "")。
    """
    try:
        import cok_accounts as accounts
    except Exception:  # noqa: BLE001
        return fallback, ""
    try:
        stored = accounts.stored_accounts()
    except Exception:  # noqa: BLE001
        stored = []

    by_pkg, by_pf, by_any = [], [], []
    for _key, acc in stored:
        if not isinstance(acc, dict):
            continue
        code = str(acc.get("signCode") or "").strip()
        if not code or accounts.is_placeholder(code):
            continue
        added = str(acc.get("added") or "")
        item = (added, code)
        by_any.append(item)
        if package_name and acc.get("packageName") == package_name:
            by_pkg.append(item)
        elif pf and acc.get("pf") == pf:
            by_pf.append(item)
    for bucket, src in ((by_pkg, "同包账号"), (by_pf, "同渠道账号"),
                        (by_any, "其它账号")):
        if not bucket:
            continue
        bucket.sort(key=lambda x: x[0], reverse=True)
        code = bucket[0][1]
        if package_name:
            _remember_sign_code(package_name, code)
        return code, src
    # 账号库里没有 -> 看本地缓存
    cache = _load_signcode_cache()
    if package_name:
        hit = str(cache.get(package_name) or "").strip()
        if hit:
            return hit, "本地缓存"
    # 再看 APK 内置种子(构建期烘焙) —— 别人直接装 APK 时, 设备上只有这一份
    if package_name:
        try:
            import cok_accounts as _accounts
            hit = str(_accounts.apk_seed_sign_codes().get(package_name) or "").strip()
        except Exception:  # noqa: BLE001
            hit = ""
        if hit:
            return hit, "APK 内置种子"
    return fallback, ""


def _remember_sign_code(package_name, code):
    """把某个包的 signCode 记进本地缓存(账号库空了也还有)。"""
    if not package_name or not code:
        return
    cache = _load_signcode_cache()
    if cache.get(package_name) == code:
        return
    cache[package_name] = code
    _save_signcode_cache(cache)


def _account_template():
    """账号模板(协议版本/baseActiveKey/device_info 等公共字段)。

    ⚠ 不能直接用 cok_client.ACCOUNT: 公开仓库里它是**脱敏占位符**
    ("<baseActiveKey>" 之类), 直接拿来当凭据, 服务端会丢弃所有加密指令
    (表现是"连上了但界面全空")。cok_accounts.template_account() 会把占位符
    清掉, 并从账号库里把公共字段的真值补回来。
    """
    try:
        import cok_accounts as accounts
        return accounts.template_account()
    except Exception:  # noqa: BLE001
        try:
            from cok_client import ACCOUNT
            return dict(ACCOUNT)
        except Exception:  # noqa: BLE001
            return {}


def build_account_from_pf_id(pf_id, platform_token="", device_id=None, gamesvc=None):
    """pfId -> 完整可直连的游戏服凭据(纯 HTTP, 不连游戏服)。

    核心原理(2026-10-29 实测): 游戏的 getserverlist.php **按 pfId 解析角色**,
    与请求里的设备 uuid 无关; 响应直接带 gameUid / 账号 uuid / 区服 / buildCode。

    返回 (acc_dict_or_None, gamesvc_result_dict)
    """
    import cok_gamesvc
    if gamesvc is None:
        gamesvc = cok_gamesvc.resolve_character(
            pf_id, pf=CHANNEL_TEMPLATE["pf"], channel=CHANNEL_TEMPLATE["channel"],
            package=CHANNEL_TEMPLATE["packageName"])
    if not gamesvc.get("ok"):
        return None, gamesvc
    acc = _account_template()
    sign_code, sign_src = _resolve_sign_code(
        CHANNEL_TEMPLATE["packageName"], CHANNEL_TEMPLATE["signCode"],
        CHANNEL_TEMPLATE["pf"])
    acc.update({
        "pfId": pf_id,
        "platformUid": pf_id,
        "platformToken": platform_token or "",
        "pf": CHANNEL_TEMPLATE["pf"],
        "gameUid": gamesvc["gameUid"],
        "uuid": gamesvc["uuid"],
        "buildCode": gamesvc.get("buildCode") or acc.get("buildCode", ""),
        "zn": gamesvc.get("zn") or acc.get("zn", ""),
        "serverId": gamesvc.get("serverId") or acc.get("serverId", ""),
        "host": CHANNEL_TEMPLATE["host"],
        # gamesvc["port"] is HTTP (normally 80), not the SmartFox game
        # socket. The TCP port varies per zone and follows serverId.
        "port": gamesvc.get("gamePort") or CHANNEL_TEMPLATE["port"],
        "packageName": CHANNEL_TEMPLATE["packageName"],
        "signCode": sign_code,
        # 记一笔 signCode 是从哪来的 —— 下次排查"这个号为什么登不上"时,
        # 一眼能看出它是不是"同包/同渠道/兜底"拿来的。
        "signCodeSource": sign_src,
        "deviceId": device_id or _os.urandom(8).hex(),
        "roleName": gamesvc.get("gameUserName") or "",
    })
    return acc, gamesvc


def channel_login_list_small(account, password, verbose=True, with_role=True):
    """果盘账号密码 -> 登录 + 列出该账号下的**游戏小号**(每个小号 = 一个游戏身份)。

    流程(与真机 App 的顺序一致):
      1. subcmd 101 取 salt -> subcmd 102 密码登录 -> 信封(envelope) + guopanUid
      2. subcmd 37 GETSMALLACCOUNTGAMEUIN -> 小号列表(perGameId / 果盘gameUin / 名字)
      3. 每个小号 -> pfId = "ewanqf:1084"+perGameId
         -> (可选)游戏服 getserverlist 解析出 COK 角色(gameUid / uuid / 区服 / 昵称)

    返回 dict: ok / smallAccounts[] / authEnvelope / guopanUid / account ...
    """
    res = channel_login(account, password, verbose=verbose)
    if not res.get("ok"):
        return res
    env = res.get("authEnvelope")
    uid = res.get("guopanUid")
    items = []
    if not env or not uid:
        res["smallAccounts"] = items
        res["note"] = res.get("note", "") + " (没拿到信封/guopanUid, 无法列小号)"
        return res
    try:
        lr = list_small_accounts(uid, env, verbose=False)
    except Exception as exc:  # noqa: BLE001
        res["ok"] = False
        res["stage"] = "small"
        res["note"] = "列小号失败: %s" % exc
        return res
    res["smallRetcode"] = lr.get("retcode")
    if lr.get("retcode") not in (0, None):
        res["smallAccounts"] = items
        res["note"] = ("登录成功, 但列小号失败(retcode=%s %s)"
                       % (lr.get("retcode"), lr.get("errmsg") or ""))
        return res
    for s in lr.get("list") or []:
        per = s.get("perGameId")
        if not per:
            continue
        pf_id = "ewanqf:" + PFID_PREFIX + per
        it = {
            "perGameId": per,
            "pfId": pf_id,
            "guopanGameUin": s.get("gameUin"),
            "name": s.get("name") or per[:8],
            "hasCharacter": False,
        }
        if with_role:
            # 游戏服按 pfId 解析角色(与设备无关); 没开过号的会返回"无角色"
            try:
                acc, gs = build_account_from_pf_id(pf_id)
            except Exception:  # noqa: BLE001
                acc, gs = None, {"ok": False, "note": "getserverlist 失败"}
            if acc is not None:
                it.update({
                    "hasCharacter": True,
                    "gameUid": acc.get("gameUid"),
                    "uuid": acc.get("uuid"),
                    "zn": acc.get("zn"),
                    "buildCode": acc.get("buildCode"),
                    "roleName": acc.get("roleName"),
                    "gameUserLevel": gs.get("gameUserLevel"),
                })
            else:
                it["note"] = gs.get("note", "")
        items.append(it)
    res["smallAccounts"] = items
    res["note"] = "登录成功, 该果盘账号下有 %d 个游戏小号" % len(items)
    return res


def make_account(account, password, label=None, owner=None, save=False,
                 device_id=None, verbose=True):
    """果盘账号密码 -> 完整可直连的游戏服凭据。

    流程(纯 PC, 不需要手机/root/模拟器):
      1. subcmd 101/102 密码登录 -> pfId (perGameId)
      2. GET gameservice/getserverlist.php?pfId=..&sig=md5(uuid+t+密钥)
         -> gameUid / 账号 uuid / 区服 / buildCode  (**按 pfId 查, 与设备无关**)
      3. 组装成账号库格式的凭据

    save=True 时写进账号库(cok_accounts.save_account)。
    """
    import cok_gamesvc
    res = channel_login(account, password, verbose=verbose)
    if not res.get("ok"):
        res["stage"] = res.get("stage", "login")
        return res
    pf_id = res.get("pfId")
    if not pf_id:
        res["ok"] = False
        res["note"] = "登录成功但没解出 pfId"
        return res
    # 2) gameservice 解析角色 + 组装凭据
    try:
        acc, gs = build_account_from_pf_id(pf_id, res.get("platformToken", ""),
                                            device_id=device_id)
    except Exception as exc:  # noqa: BLE001
        res["ok"] = False
        res["stage"] = "gamesvc"
        res["note"] = "getserverlist 失败: %s" % exc
        return res
    if acc is None:
        res["ok"] = False
        res["stage"] = "gamesvc"
        res["gamesvc"] = gs
        res["note"] = gs.get("note", "")
        return res
    acc["channelAccount"] = account
    res["account"] = acc
    res["gamesvc"] = gs
    res["note"] = ("已生成可直连的游戏服凭据(pfId + gameUid + uuid), "
                   "不依赖手机/root; deviceId 可随意)")
    if save:
        try:
            import cok_accounts
            key = cok_accounts.save_account(acc, label=label, owner=owner)
            res["accountKey"] = key
            res["saved"] = True
        except Exception as exc:  # noqa: BLE001
            res["saved"] = False
            res["note"] += " (入库失败: %s)" % exc
    if verbose:
        print("[gamesvc] gameUid=%s uuid=%s zone=%s buildCode=%s"
              % (gs["gameUid"], gs["uuid"], gs.get("zn"), gs.get("buildCode")))
    return res


def main():
    ap = argparse.ArgumentParser(description="guopan channel account login (pure PC)")
    ap.add_argument("account", nargs="?")
    ap.add_argument("password", nargs="?")
    ap.add_argument("--json", help="write result dict to this file")
    ap.add_argument("--selftest", action="store_true",
                    help="离线回放归档 pcap 自证协议(无需网络/账号)")
    ap.add_argument("--list-small", action="store_true",
                    help="列出果盘账号下的小号(需 --guopan-uid + --envelope)")
    ap.add_argument("--create-small", metavar="NAME",
                    help="建一个小号(需 --guopan-uid + --envelope)")
    ap.add_argument("--pick-small", metavar="PERGAMEID",
                    help="选中小号进游戏(需 --guopan-uid + --envelope)")
    ap.add_argument("--guopan-uid")
    ap.add_argument("--envelope", help="认证信封 Login_<uid>_<appid>_<key>")
    ap.add_argument("--make-account", action="store_true",
                    help="账号密码 -> 完整可直连的游戏服凭据(pfId+gameUid+uuid)")
    ap.add_argument("--save", action="store_true", help="配合 --make-account: 写进账号库")
    ap.add_argument("--label", help="配合 --save: 账号显示名")
    ap.add_argument("--owner", help="配合 --save: 归属用户名(多用户隔离)")
    ap.add_argument("-q", "--quiet", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        ok = selftest(verbose=not args.quiet)
        sys.exit(0 if ok else 1)
    if args.make_account:
        if not args.account or args.password is None:
            ap.error("--make-account 需要 <account> <password>")
        r = make_account(args.account, args.password, label=args.label,
                         owner=args.owner, save=args.save, verbose=not args.quiet)
        printable = {k: v for k, v in r.items()
                     if k not in ("login_pt_hex", "account", "gamesvc")}
        if r.get("account"):
            printable["account"] = r["account"]
        print(json.dumps(printable, ensure_ascii=False, indent=2))
        if args.json:
            with open(args.json, "w") as fh:
                json.dump(r.get("account") or r, fh, ensure_ascii=False, indent=2)
            print("written %s" % args.json)
        return
    if args.list_small or args.create_small or args.pick_small:
        if not (args.guopan_uid and args.envelope):
            ap.error("小号命令需要 --guopan-uid 与 --envelope")
        uid = int(args.guopan_uid)
        env = args.envelope
        if args.list_small:
            list_small_accounts(uid, env, verbose=not args.quiet)
        if args.create_small:
            r = create_small_account(uid, env, args.create_small, verbose=not args.quiet)
            print(json.dumps({k: v for k, v in r.items() if k != "list"}, ensure_ascii=False, indent=2))
        if args.pick_small:
            lr = list_small_accounts(uid, env, verbose=not args.quiet)
            hit = [s for s in lr["list"] if s["perGameId"] == args.pick_small]
            if not hit:
                ap.error("没找到 perGameId=%s 的小号" % args.pick_small)
            login_small_account(uid, env, hit[0]["raw"], verbose=not args.quiet)
        return
    if not args.account or args.password is None:
        ap.error("需要 <account> <password>, 或使用 --selftest")
    res = channel_login(args.account, args.password, verbose=not args.quiet)
    printable = {k: v for k, v in res.items() if k != "login_pt_hex"}
    print(json.dumps(printable, ensure_ascii=False, indent=2))
    if args.json:
        with open(args.json, "w") as fh:
            json.dump(res, fh, ensure_ascii=False, indent=2)
        print("written %s" % args.json)

if __name__ == "__main__":
    main()
