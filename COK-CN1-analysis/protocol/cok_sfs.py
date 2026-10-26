#!/usr/bin/env python3
"""
COK（列王的纷争 / Clash of Kings 中国服）游戏服协议工具包
====================================================================
实测自设备上的 com.hcg.cok.nearme.gamecenter（海尔渠道包 12.06.0），
游戏服 42.0.152.154:32231，协议为 SmartFoxServer 2X (SFS) over TCP。

线格式
------
    [3 字节包头] [SFS 载荷]
    包头 : flags(1) | length(2, 大端)   flags bit0 = 大端
    载荷 : SFSObject 编码

    SFSObject : [0x12][count:2 大端] 之后 count 组
                 [keyLen:2 大端][key 字节][value]
    value     : [typeID:1][数据]

    typeID: 0x00 NULL  0x01 BOOL  0x02 BYTE  0x03 SHORT 0x04 INT
            0x05 LONG  0x06 FLOAT 0x07 DOUBLE 0x08 UTF_STRING
            0x09 BOOL_ARRAY 0x0a BYTE_ARRAY 0x0b SHORT_ARRAY
            0x0c INT_ARRAY 0x0d LONG_ARRAY 0x0e FLOAT_ARRAY
            0x0f DOUBLE_ARRAY 0x10 UTF_STRING_ARRAY 0x11 SFS_ARRAY
            0x12 SFS_OBJECT 0x13 CLASS 0x14 TEXT
    UTF_STRING 载荷 = [len:2 大端][UTF-8 字节]
    LONG 为 8 字节大端。

请求外层（线上明文，可直接读）
    { p: { p: { params: <字节数组>, r: -1, c: "<命令名>" },
          a: 13, c: 1 }
    即：p.p.c = 命令名，p.p.params = 加密后的参数体。

参数体加密
----------
    params 的内容 = SFS 序列化的参数对象，再用一把 **每会话** 的
    32 字节（ASCII）密钥做 **循环 XOR** 混淆。
    密钥由服务端在登录/配置流程中下发（客户端配置表 id=81）。
    会话内恒定；换会话会变。密钥长度 32 字节 ASCII（十六进制字符）。

    XOR 不改变长度，因此密文与明文等长。

用法
----
    python3 cok_sfs.py decode  <pcap-ish jsonl>   # 解析抓包并解出 params
    python3 cok_sfs.py xor     <hex> <key>        # 手工加/解密
    python3 cok_sfs.py build   <key> <cmd> <json> # 构造一条请求的 params
"""
import binascii
import json
import struct
import sys
import zlib

TYPES = {
    0x00: "NULL", 0x01: "BOOL", 0x02: "BYTE", 0x03: "SHORT", 0x04: "INT",
    0x05: "LONG", 0x06: "FLOAT", 0x07: "DOUBLE", 0x08: "UTF_STRING",
    0x09: "BOOL_ARRAY", 0x0a: "BYTE_ARRAY", 0x0b: "SHORT_ARRAY",
    0x0c: "INT_ARRAY", 0x0d: "LONG_ARRAY", 0x0e: "FLOAT_ARRAY",
    0x0f: "DOUBLE_ARRAY", 0x10: "UTF_STRING_ARRAY", 0x11: "SFS_ARRAY",
    0x12: "SFS_OBJECT", 0x13: "CLASS", 0x14: "TEXT",
}


class Reader:
    def __init__(self, b):
        self.b = b
        self.i = 0

    def u8(self):
        v = self.b[self.i]
        self.i += 1
        return v

    def u16(self):
        v = struct.unpack_from(">H", self.b, self.i)[0]
        self.i += 2
        return v

    def i16(self):
        v = struct.unpack_from(">h", self.b, self.i)[0]
        self.i += 2
        return v

    def u32(self):
        v = struct.unpack_from(">I", self.b, self.i)[0]
        self.i += 4
        return v

    def raw(self, n):
        v = self.b[self.i:self.i + n]
        self.i += n
        return v


ARRAY_MODES = ("val", "kv")   # SFS_ARRAY 元素编码候选


# 合法 SFS 类型标签(0x00-0x14)
VALID_SFS_TYPES = frozenset(range(0x00, 0x15))


def read_value(r, depth=0, array_mode="val"):
    t = r.u8()
    name = TYPES.get(t, "0x%02x?" % t)
    if t == 0x00:
        return None
    if t == 0x01:
        return bool(r.u8())
    if t == 0x02:
        return r.u8()
    if t == 0x03:
        return r.i16()
    if t == 0x04:
        v = struct.unpack_from(">i", r.b, r.i)[0]
        r.i += 4
        return v
    if t == 0x05:
        v = struct.unpack_from(">q", r.b, r.i)[0]
        r.i += 8
        return v
    if t == 0x06:
        v = struct.unpack_from(">f", r.b, r.i)[0]
        r.i += 4
        return v
    if t == 0x07:
        v = struct.unpack_from(">d", r.b, r.i)[0]
        r.i += 8
        return v
    if t == 0x08:
        return r.raw(r.u16()).decode("utf-8", "replace")
    if t == 0x09:
        return [bool(r.u8()) for _ in range(r.u32())]
    if t == 0x0a:
        return r.raw(r.u32()).hex()
    if t == 0x0b:
        return [r.i16() for _ in range(r.u32())]
    if t == 0x0c:
        out = []
        for _ in range(r.u32()):
            out.append(struct.unpack_from(">i", r.b, r.i)[0])
            r.i += 4
        return out
    if t == 0x0d:
        out = []
        for _ in range(r.u32()):
            out.append(struct.unpack_from(">q", r.b, r.i)[0])
            r.i += 8
        return out
    if t == 0x0e:
        out = []
        for _ in range(r.u32()):
            out.append(struct.unpack_from(">f", r.b, r.i)[0])
            r.i += 4
        return out
    if t == 0x0f:
        out = []
        for _ in range(r.u32()):
            out.append(struct.unpack_from(">d", r.b, r.i)[0])
            r.i += 8
        return out
    if t == 0x10:
        # SFS_STRING_ARRAY: **count 为 2 字节**(本游戏服务端非官方标准, 与 0x11 一致);
        # 每个元素是 [len:2][data]
        return [r.raw(r.u16()).decode("utf-8", "replace") for _ in range(r.u16())]
    if t == 0x11:
        # SFS_ARRAY: count 为 2 字节; 元素可能是纯值, 也可能是 (key,value) 对
        # **每个数组独立探测模式**: 合法 SFS 类型只有 0x00-0x14, 若数组首个字节
        # 不是合法类型, 说明这一层其实是 (key,value) 对(首字节是 key 长度)。
        # 同一份响应里可以同时存在 val 模式与 kv 模式的数组, 所以不能全局传模式。
        n = r.u16()
        out = []
        probe = r.b[r.i] if r.i < len(r.b) else -1
        if n > 0 and probe not in VALID_SFS_TYPES:
            for _ in range(n):
                kl = r.i16()
                key = r.raw(kl).decode("utf-8", "replace")
                out.append((key, read_value(r, depth + 1, "kv")))
            return out
        for _ in range(n):
            out.append(read_value(r, depth + 1, array_mode))
        return out
    if t == 0x12:
        n = r.u16()
        out = {}
        for _ in range(n):
            kl = r.i16()
            key = r.raw(kl).decode("utf-8", "replace")
            out[key] = read_value(r, depth + 1, array_mode)
        return out
    if t == 0x14:
        return r.raw(r.u16()).decode("utf-8", "replace")
    raise ValueError("unknown type 0x%02x at %d" % (t, r.i - 1))


class TypedInt(int):
    """带显式 SFS 整数类型的值。

    客户端(cocos2d-x / SFS2X 序列化器)对整数字段是**按字段语义选固定类型**，
    不是按值大小选最小类型。例如:
        "a"(扩展号)  恒为 SHORT(0x03)   —— 即使值是 0
        "c"(命令号)  恒为 BYTE(0x02)
        "r"(请求序号) 恒为 INT(0x04)     —— 值 -1
        gmLogin / device_info 里的数字  为 INT(0x04)
    其余登录字段(哪怕是数字)一律是 STRING(0x08)。
    """

    def __new__(cls, value, sfs_type):
        o = int.__new__(cls, value)
        o.sfs_type = sfs_type
        return o


# SFS 整数类型标签
SFS_BYTE = 0x02
SFS_SHORT = 0x03
SFS_INT = 0x04
SFS_LONG = 0x05


def encode_value(v):
    """把 python 值编码成 SFS value（不含外层 key）"""
    if isinstance(v, TypedInt):
        t = v.sfs_type
        if t == SFS_BYTE:
            return b"\x02" + bytes([v & 0xFF])
        if t == SFS_SHORT:
            return b"\x03" + struct.pack(">h", v)
        if t == SFS_INT:
            return b"\x04" + struct.pack(">i", v)
        if t == SFS_LONG:
            return b"\x05" + struct.pack(">q", v)
        raise ValueError("unknown SFS int type 0x%02x" % t)
    if v is None:
        return b"\x00"
    if isinstance(v, bool):
        return b"\x01" + (b"\x01" if v else b"\x00")
    if isinstance(v, int):
        if 0 <= v <= 0xFF:
            return b"\x02" + bytes([v])
        if -0x8000 <= v <= 0x7FFF:
            return b"\x03" + struct.pack(">h", v)
        if -0x80000000 <= v <= 0x7FFFFFFF:
            return b"\x04" + struct.pack(">i", v)
        return b"\x05" + struct.pack(">q", v)
    if isinstance(v, float):
        return b"\x06" + struct.pack(">f", v)
    if isinstance(v, str):
        # "hex:<hex>" 约定: 表示字节数组(线上 params 就是 BYTE_ARRAY)
        if v.startswith("hex:"):
            return b"\x0a" + struct.pack(">I", len(binascii.unhexlify(v[4:]))) + binascii.unhexlify(v[4:])
        b = v.encode("utf-8")
        return b"\x08" + struct.pack(">H", len(b)) + b
    if isinstance(v, (bytes, bytearray)):
        return b"\x0a" + struct.pack(">I", len(v)) + bytes(v)
    if isinstance(v, list):
        def enc_list(x):
            if all(isinstance(i, str) for i in x):
                # SFS_STRING_ARRAY: count **2 字节**(与服务端 read_value 一致)
                body = struct.pack(">H", len(x))
                for i in x:
                    bb = i.encode("utf-8")
                    body += struct.pack(">H", len(bb)) + bb
                return b"\x10" + body
            # SFS_ARRAY: count **2 字节**(与服务端 read_value 一致)
            body = struct.pack(">H", len(x))
            for i in x:
                body += encode_value(i)
            return b"\x11" + body
        return enc_list(v)
    if isinstance(v, dict):
        body = b"\x12" + struct.pack(">H", len(v))
        for k, val in v.items():
            kb = k.encode("utf-8")
            body += struct.pack(">H", len(kb)) + kb + encode_value(val)
        return body
    raise TypeError("unsupported value %r" % (v,))


def encode_object(d):
    body = b"\x12" + struct.pack(">H", len(d))
    for k, val in d.items():
        kb = k.encode("utf-8")
        body += struct.pack(">H", len(kb)) + kb + encode_value(val)
    return body


def xor_buf(data, key):
    kl = len(key)
    return bytes(b ^ key[i % kl] for i, b in enumerate(data))


def parse_best(buf):
    """尝试所有 SFS_ARRAY 编码模式, 返回第一个能完整消费缓冲区的结果"""
    best = None
    for mode in ARRAY_MODES:
        try:
            r = Reader(buf)
            obj = read_value(r, 0, mode)
            if r.i == len(buf):
                return obj, mode
            if best is None:
                best = (obj, mode + "(partial)")
        except Exception:
            if best is None:
                best = ({}, mode + "(error)")
    return best if best else ({}, "none")


def decode_params(blob, key):
    """响应 params: XOR(会话密钥) -> zlib -> SFS 对象"""
    import zlib as _z
    x = bytes(b ^ key[i % len(key)] for i, b in enumerate(blob))
    if x[:2] == b"\x78\x9c":
        raw = _z.decompressobj(-15).decompress(x[2:])
    else:
        raw = _z.decompress(x)
    obj, mode = parse_best(raw)
    return obj, mode, raw


def parse_packet(b):
    """返回 (flags, payload, obj, consumed)

    包头 = [flags:1][length:2]。flags 位义(来自 sfs2x.client.core.SFSIOHandler):
        0x80 = 大端长度   0x40 = BlueBoxed   0x20 = 压缩(zlib)   0x10 = 加密
    压缩帧的 length 是**压缩后**长度, 解压后才得到 SFS 载荷。
    """
    flags = b[0]
    ln = struct.unpack_from(">H", b, 1)[0]
    payload = b[3:3 + ln]
    if flags & 0x20:
        payload = zlib.decompress(payload)
    r = Reader(payload)
    obj = read_value(r)
    return flags, payload, obj, r.i


def flatten(obj, prefix=""):
    out = {}
    if isinstance(obj, dict):
        for k, v in obj.items():
            out.update(flatten(v, prefix + "." + k if prefix else k))
    else:
        out[prefix] = obj
    return out


def decode_capture(path, key=None):
    """解析 frida 抓到的 JSONL，输出命令与（若给 key）解出的参数"""
    rows = []
    seen = set()
    for ln in open(path, encoding="utf-8", errors="replace").read().splitlines():
        try:
            rec = json.loads(ln)
        except Exception:
            continue
        pl = rec.get("msg", {}).get("payload")
        if not isinstance(pl, dict):
            continue
        if pl.get("t") not in ("write", "send", "read", "recv", "wire"):
            continue
        h = pl.get("hex")
        if not h:
            continue
        b = binascii.unhexlify(h)
        if len(b) < 4 or b in seen:
            continue
        seen.add(b)
        try:
            flags, payload, obj, consumed = parse_packet(b)
        except Exception as e:
            rows.append({"dir": pl.get("t"), "len": len(b), "error": str(e)})
            continue
        f = flatten(obj)
        row = {
            "dir": pl.get("t"), "len": len(b), "ok": consumed == len(payload),
            "cmd": f.get("p.p.c"), "flat": f,
        }
        pb = f.get("p.p.params")
        if key and isinstance(pb, str):
            blob = binascii.unhexlify(pb)
            try:
                r = Reader(xor_buf(blob, key))
                row["params"] = read_value(r)
            except Exception as e:
                row["params_error"] = str(e)
        rows.append(row)
    return rows


def derive_session_key(id_str):
    """从登录响应的 "id" 字段派生会话 XOR 密钥。

    服务端在登录响应(明文)的 params 里下发  id = "<前缀>_<密钥ID>" ，
    客户端(libgame.so FUN_0101a260) 的做法是:
        密钥ID   = atoi(下划线之后的部分)
        XOR 密钥 = md5_hex(下划线之前的部分)      —— 32 位小写 hex 字符串
    并把 密钥ID -> 密钥 存进 map<int,string>(cfg+0x1a8)；
    业务请求用当前密钥ID, 业务响应用响应里的 "qqq" 字段作密钥ID 去查表。

    返回 (key: bytes, key_id: int)。
    """
    import hashlib as _h
    prefix, _, suffix = id_str.partition("_")
    if not prefix:
        raise ValueError("id 字段格式应为 <前缀>_<密钥ID>: %r" % (id_str,))
    key = _h.md5(prefix.encode("utf-8")).hexdigest().encode("utf-8")
    try:
        key_id = int(suffix)
    except ValueError:
        key_id = None
    return key, key_id


# ---------------------------------------------------------------- 登录请求参数
# 登录请求(明文)中四个本地计算字段的派生规则, 全部来自 libgame.so 反编译 + 双会话数值验证。
#
#   signCode   = md5( sprintf("%x", Arrays.hashCode(certDER)) + "." + hex_upper(certDER) )
#                 —— 由 APK 签名证书派生, 同一 APK 恒定
#   buildCode  = 渠道下发的固定值, 同一账号/渠道恒定
#   SecurityCode = md5( str(cmdBaseTime) + "e01684719c1bec876c10bb124a6d65aa" + game_uid )
#   cc         = md5( "d6b63d01d640fb78c979912ec839a0de" + appVersion
#                      + str(cmdBaseTime) + game_uid )
#
SECURITY_CODE_SALT = "e01684719c1bec876c10bb124a6d65aa"
CC_SALT = "d6b63d01d640fb78c979912ec839a0de"


def _md5_hex(s):
    import hashlib as _h
    return _h.md5(s.encode("utf-8")).hexdigest()


def java_arrays_hashcode(data):
    """Java java.util.Arrays.hashCode(byte[]) 的等价实现(有符号字节)。"""
    r = 1
    for e in data:
        if e > 127:
            e -= 256
        r = (31 * r + e) & 0xFFFFFFFF
    return r


def sign_code_from_cert(cert_der):
    """由 APK 签名证书(X.509 DER)算出 signCode。

    客户端(Java_org_cocos2dx_ext_Native_nativeAPKCode) 的做法:
        sig = PackageManager.getPackageInfo(pkg, GET_SIGNATURES).signatures[0]
        str = sprintf("%x.", sig.hashCode()) + sig.toCharsString()
        signCode = md5(str)
    其中 sig.hashCode() = Arrays.hashCode(certDER),
          sig.toCharsString() = **小写** hex(certDER)
          (Android 用 Integer.toHexString, 输出小写)。
    """
    h = java_arrays_hashcode(cert_der) & 0xFFFFFFFF
    return _md5_hex("%x." % h + cert_der.hex())


def derive_login_fields(cmd_base_time, game_uid, app_version="12.06.0",
                        sign_code=None, build_code=None):
    """构造登录请求里的四个本地字段。

    cmd_base_time : int/str, 请求里的 cmdBaseTime(秒级时间戳)
    game_uid      : str, 账号 gameUid(如 "136063574002223")
    app_version   : str, appVersion
    sign_code     : str, 缺省用 None(调用方需自备; 正常从证书派生)
    build_code    : str, 缺省用 None
    返回 dict，含 signCode / buildCode / SecurityCode / cc。
    """
    t = str(cmd_base_time)
    out = {
        "cmdBaseTime": t,
        "SecurityCode": _md5_hex(t + SECURITY_CODE_SALT + str(game_uid)),
        "cc": _md5_hex(CC_SALT + str(app_version) + t + str(game_uid)),
    }
    if sign_code is not None:
        out["signCode"] = sign_code
    if build_code is not None:
        out["buildCode"] = build_code
    return out


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 1
    cmd = argv[1]
    if cmd == "derive":
        id_str = argv[2]
        key, key_id = derive_session_key(id_str)
        print("id 串        = %s" % id_str)
        print("前缀         = %s" % id_str.partition("_")[0])
        print("密钥ID       = %s" % key_id)
        print("会话 XOR 密钥 = %s" % key.decode())
        return 0
    if cmd == "login-fields":
        # login-fields <cmdBaseTime> <gameUid> [appVersion] [signCode] [buildCode]
        t = argv[2]
        uid = argv[3]
        av = argv[4] if len(argv) > 4 else "12.06.0"
        sc = argv[5] if len(argv) > 5 else None
        bc = argv[6] if len(argv) > 6 else None
        d = derive_login_fields(t, uid, av, sc, bc)
        for k, v in d.items():
            print("%-14s = %s" % (k, v))
        return 0
    if cmd == "sign-code":
        # sign-code <证书DER文件>
        data = open(argv[2], "rb").read()
        print("signCode = %s" % sign_code_from_cert(data))
        return 0
    if cmd == "xor":
        data = binascii.unhexlify(argv[2])
        key = argv[3].encode("utf-8")
        print(xor_buf(data, key).hex())
        return 0
    if cmd == "decode":
        path = argv[2]
        key = argv[3].encode("utf-8") if len(argv) > 3 else None
        for row in decode_capture(path, key):
            print("[%s] len=%s ok=%s cmd=%s" % (row.get("dir"), row.get("len"),
                                               row.get("ok"), row.get("cmd")))
            for k, v in row.get("flat", {}).items():
                if k.endswith("params") or k.endswith("rlQW45Y"):
                    continue
                print("    %-26s = %s" % (k, str(v)[:100]))
            if "params" in row:
                print("    -- params 明文 --")
                for k, v in flatten(row["params"]).items():
                    print("       %-22s = %s" % (k, str(v)[:100]))
            if row.get("params_error"):
                print("    params 解密失败:", row["params_error"])
            print("-" * 60)
        return 0
    if cmd == "build":
        key = argv[2].encode("utf-8")
        cmdname = argv[3]
        params = json.loads(argv[4])
        # params 字段若是 hex 串, 按 "hex:" 约定转成字节数组
        plain = encode_object(params)
        cipher = xor_buf(plain, key)
        # 线上真实结构: {p:{p:{params:<BYTE_ARRAY>}, r:-1, c:"<cmd>"}, a:13, c:1}
        env = {"p": {"p": {"params": cipher}, "r": -1, "c": cmdname},
               "a": 13, "c": 1}
        pkt = encode_object(env)
        head = bytes([0x80]) + struct.pack(">H", len(pkt))
        print(json.dumps({
            "params_plain_hex": plain.hex(),
            "params_cipher_hex": cipher.hex(),
            "packet_hex": (head + pkt).hex(),
        }, ensure_ascii=False, indent=2))
        return 0
    print(__doc__)
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
