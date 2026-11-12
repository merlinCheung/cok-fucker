#!/usr/bin/env python3
"""COK（列王的纷争 中国服）游戏服直连客户端 —— 只读用法。

用法:
    python3 cok_client.py --cmd cmd.ping
    python3 cok_client.py --cmd daily.quest.ls
    python3 cok_client.py --account my_account.json --cmd get.user.info.multi --params '{"uids":[<gameUid>]}'
    python3 cok_client.py --dump-only          # 只做离线回环自检, 不连服务器

协议要点（全部经字节级实证，见 COK-游戏服协议实测报告.md）：
  * 线格式  : [flags:1][length:2 大端] + SFS 载荷
  * 登录握手: 全程明文
      ① → {p:{bin:true, cl:"Android", api:"1.8.0"}, a:0, c:0}
      ② ← {p:{ct,ms,tk}, a:0, c:0}
      ③ → {p:{p:{...登录参数...}, zn:"COK2223", pw:"", un:"<gameUid>"}, a:1, c:0}
      ④ ← {p:{p:{..., id:"<前缀>_<密钥ID>", ver:"<base64>"}}, a:1, c:0}   ← 关键
  * 会话密钥: key = md5_hex(id 中下划线之前的部分)，keyId = int(id 下划线之后)
  * 业务请求: params = XOR(key, SFS明文)
  * 业务响应: blob = XOR(key, zlib(SFS明文))，解码 = XOR → 去 2 字节 zlib 头 → inflate → SFS
"""
# --- 包自举: 直接 `python3 cok/core/xxx.py` 时把 cok/ 加进 sys.path ---
import os as _os
import sys as _sys

_PKG_ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
if _os.path.isdir(_PKG_ROOT) and _PKG_ROOT not in _sys.path:
    _sys.path.insert(0, _PKG_ROOT)
_CORE = _os.path.join(_PKG_ROOT, "core")
if _os.path.isdir(_CORE) and _CORE not in _sys.path:
    _sys.path.insert(0, _CORE)
import cok_paths  # noqa: E402
from cok_paths import resource as _res  # noqa: E402
from cok_paths import data_dir as _data_dir  # noqa: E402

import argparse
import binascii
import contextlib
import errno
import fcntl
import json
import os
import random
import re
import socket
import struct
import sys
import threading
import time
import uuid as uuidlib
import zlib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # noqa: E402

from cok_sfs import (  # noqa: E402
    encode_object, flatten, xor_buf, read_value, Reader,
    derive_session_key, derive_login_fields, sign_code_from_cert, parse_best,
    TypedInt, SFS_BYTE, SFS_SHORT, SFS_INT, SFS_LONG,
    restore_typed_fields,
)

DEFAULT_HOST = "42.192.152.154"   # 游戏服(2026-10-23 由设备侧 getpeername 确认)
DEFAULT_PORT = 32231
# 线上抓包里的游戏服域名(serverId 2223 对应 s<serverId>.cok.elexcok.com)。
# 该域名只在渠道 DNS 下有记录, 公网 DNS 无 A 记录, 所以默认仍用抓包时的 IP,
# 需要时用 --host s2223.cok.elexcok.com 覆盖。
SERVER_DOMAIN_FMT = "s{server_id}.cok.elexcok.com"

# 线上真实 bin 握手帧(用于帧级等价自检)
REAL_BIN_FRAME = (
    "800036120003000170120003000362696e01010002636c080007416e64726f6964"
    "0003617069080005312e382e300001610300000001630200"
)

# 账号凭据模板(从设备/渠道登录复原后填入，提交前请勿硬编码真值)。
# 必填字段: pfId / platformToken / gameUid / deviceId / uuid / signCode /
#   buildCode / baseActiveKey / parseRegisterId / host / port / pf / channelSign
ACCOUNT = {
    "pfId": "<渠道:平台身份, 如 nearme:g1372797742670953701>",
    "platformToken": "<平台 token>",
    "gameUid": "<游戏服唯一 uid>",
    "deviceId": "<设备 id>",
    "uuid": "<账号 uuid(游戏服下发)>",
    "buildCode": "<构建码(32 位 hex)>",
    "signCode": "<签名码(32 位 hex)>",
    "host": "txaia-cok.elexapp.com",
    "port": 32231,
    "baseActiveKey": "<baseActiveKey>",
    "packageName": "com.hcg.cok.nearme.gamecenter",
    "appVersion": "12.06.0",
    "luaVersion": "release_12.06.0_25",
    "serverId": "2223",
    "parseRegisterId": "<uuid4>",
    "pf": "cn_nearme",
    "channelSign": "bang",
    "isSmall": "kao",
    "isHDLogin": "0",
    "lang": "zh_CN",
    "region": "CN",
    "fromCountry": "CN",
    "subscriberId": "default",
    "phoneDevice": "default",
    "pfchild": "",
    "gaid": "",
    "gmUid": "",
    "gmLogin": TypedInt(0, SFS_INT),
    "afUID": "",
    "googlePlay": "",
    "pfSign": "",
    "linkname": "",
    "instantAppCookie": "",
    "zn": "COK2223",
    "pw": "",
    "device_info": {
        "operator_name": "CHN-CT",
        "screen_h": TypedInt(2577, SFS_INT),
        "screen_w": TypedInt(1240, SFS_INT),
        "os_build": "PHK110_16.0.5.1201(CN01)",
        "screen_density": TypedInt(560, SFS_INT),
        "operators": "UNKNOWN",
        "os_version": "9.9.9",
        "model": "PHK110",
        "os_serial": "unknown",
        "os_fgpt": "OnePlus/PHK110/OP5913L1:16/BP2A.250605.015/T.20e88f8_46f605_46f603:user/release-keys",
        "network_type": TypedInt(0, SFS_INT),
    },
}


def log(*a):
    print(*a, flush=True)


#: 脱敏占位符形态(形如 "<baseActiveKey>" / "<签名码(32 位 hex)>")。
#: 它**不是凭据** —— 当真值发给服务端, 服务端会丢弃所有加密指令
#: (登录却成功, 表现是"连上了但界面全空", 极难查)。
#:
#: ⚠ 上面 ACCOUNT 字典的**内容**别乱动: android-app/app/build.gradle 靠正则
#:   `(?sm)^ACCOUNT = \{.*?^\}\n` 把整个块换成安卓版安全模板(脱敏),
#:   匹配到的是**第一个行首的 }**。所以: 字典内部不能出现行首的 `}`,
#:   也不能在 ACCOUNT 之前再放一个 ACCOUNT = { —— 匹配不到就静默失败,
#:   桌面端凭据会被原样打进 APK(构建自检会拦下来, 但别去踩)。
_PLACEHOLDER_RE = re.compile(r"^<.*>$", re.S)


def _is_placeholder(value):
    """判断一个值是不是脱敏占位符(形如 "<baseActiveKey>")。"""
    return isinstance(value, str) and bool(_PLACEHOLDER_RE.match(value.strip()))


def _public_defaults():
    """协议公共字段的默认值: 内置模板 + 本地缓存/账号库里的**真值**。

    模板(ACCOUNT)在公开仓库里是脱敏占位符, 真值优先。
    真值来源见 cok_accounts.public_fields() —— baseActiveKey 这类是
    **协议级**公共字段(实测所有账号同值), 账号库里存的是从真机登录
    复原出来的真值。
    """
    out = dict(ACCOUNT)
    try:
        import cok_accounts as _accounts
        for k, v in _accounts.public_fields().items():
            if v and not _is_placeholder(v):
                out[k] = v
    except Exception:  # noqa: BLE001
        pass
    return out


class CokError(Exception):
    pass


# --------------------------------------------------------------------------
# 账号互斥锁(进程间)
# --------------------------------------------------------------------------
# 游戏服**同账号只允许一个连接**。网页控制台、命令扫描脚本、frida 采集
# 如果同时用同一个账号, 服务端会主动把其中一条踢掉 —— 表现成
# "连接被服务端关闭", 很容易被误判成协议问题。
# 这里用 flock 做**跨进程**互斥: 谁先拿到锁谁连, 别人直接跳过。
_HERE = os.path.dirname(os.path.abspath(__file__))
#: 账号互斥锁文件。可用环境变量 COK_ACCOUNT_LOCK_FILE 覆盖 ——
#: 测试要用独立锁, 否则会跟正在运行的网页控制台抢同一个账号。

ACCOUNT_LOCK_FILE = os.environ.get(
    "COK_ACCOUNT_LOCK_FILE", os.path.join(_data_dir(), ".cok-account.lock"))

#: 账号 id -> 文件名的清洗(多账号时每个账号一把锁)。
_LOCK_KEY_RE = re.compile(r"[^0-9A-Za-z_-]")


def lock_file_for(key=None):
    """按账号 id 解析锁文件路径。

    * 环境变量 COK_ACCOUNT_LOCK_FILE 一旦设置, **永远**用它(测试隔离优先,
      忽略 key) —— 保持既有测试行为不变。
    * key 为空 -> 默认单文件 .cok-account.lock(与多账号改造前完全一致,
      所有老调用点无需改动)。
    * key 非空 -> 每账号一把 .cok-account-<key>.lock, 不同账号互不阻塞,
      同账号(含跨进程)仍然互斥。
    """
    env = os.environ.get("COK_ACCOUNT_LOCK_FILE")
    if env:
        return env
    key = str(key or "").strip()
    if not key:
        return os.path.join(_HERE, ".cok-account.lock")
    safe = _LOCK_KEY_RE.sub("_", key) or "default"
    return os.path.join(_HERE, ".cok-account-%s.lock" % safe)


class AccountBusy(CokError):
    """账号正被别的进程/线程占用(同账号只允许一个连接)。"""


#: 进程内持锁状态。flock 是**按 fd**生效的, 同一进程里另开一个 fd 去 flock
#: 同一个文件会和自己冲突 —— 所以同线程嵌套取锁必须走计数, 不能再 flock。
#:
#: ⚠️ 但「可重入」只能对**同一个线程**成立。计数是进程级的, 如果不分线程,
#: 另一个线程(poll 轮询 vs 打怪线程)会误以为自己拿到了独占权, 两个线程
#: 同时连游戏服 → 服务端互踢(表现为"连接被服务端关闭")。
#: 所以这里记住持有者的 thread id, 只有同线程才走计数。
#:
#: 多账号: 每把锁(每个账号一个锁文件)各记一份状态, 按锁文件路径索引。
_LOCK_MUTEX = threading.Lock()
_LOCK_STATES = {}


def _lock_state(path):
    """取某锁文件的进程内持锁状态(没有则初始化)。调用方须持 _LOCK_MUTEX。"""
    st = _LOCK_STATES.get(path)
    if st is None:
        st = {"fd": None, "depth": 0, "purpose": "", "tid": None}
        _LOCK_STATES[path] = st
    return st


def _release_lock_once(path):
    """把进程内持锁计数减一; 归零时真正解锁并关 fd。

    注意: 释放**不**校验线程 —— 打怪的锁是 action 线程拿的, 却由打怪线程
    通过 emit("done"/"stopped") 归还, 跨线程释放是设计内的。
    真正要防的是"另一个线程假装自己拿到了锁"(nested 判定), 那在
    account_lock 里按 thread id 判定。
    """
    fdd = None
    with _LOCK_MUTEX:
        st = _lock_state(path)
        st["depth"] = max(0, st["depth"] - 1)
        if st["depth"] == 0:
            fdd = st["fd"]
            st["fd"] = None
            st["purpose"] = ""
            st["tid"] = None
    if fdd is not None:
        try:
            # ⚠️ 必须在解锁**之前**清掉持有者信息 —— flock 释放了但文件里
            # 还留着 "pid purpose" 的话, 页面会显示一个根本不存在的占用者。
            # ftruncate 只改长度, 不动 fd 偏移量 —— 必须先 lseek 回 0,
            # 否则 write 会写进空洞, 文件里留下一堆 NUL。
            os.ftruncate(fdd, 0)
            os.lseek(fdd, 0, os.SEEK_SET)
            os.write(fdd, b"free\n")
        except OSError:
            pass
        try:
            fcntl.flock(fdd, fcntl.LOCK_UN)
        except OSError:
            pass
        try:
            os.close(fdd)
        except OSError:
            pass


@contextlib.contextmanager
def account_lock(timeout=0.0, purpose="", key=None):
    """占用账号互斥锁(进程内可重入)。

    timeout=0 表示**不等待**, 拿不到就立刻抛 AccountBusy(调用方应当跳过本轮)。
    用法:
        with account_lock(timeout=5, purpose="web poll"):
            ...连游戏服...

    key 是账号 id(gameUid)。不传则用默认单账号锁(行为同改造前);
    传了则每个账号一把独立锁, 不同账号并发不互相阻塞。

    **可重入**: 同一**线程**里嵌套取锁不会自己把自己挡掉(只加计数)。
    这条必须有 —— 网页控制台的 action() 已经持锁, 里面的
    _hunter_start() 要把锁**继续持有**到打怪结束, 如果嵌套取锁失败,
    点「开始自动打怪」就会报"账号被占用"。

    ⚠️ **可重入只对同一个线程成立**。另一个线程(比如后台轮询)来取锁时,
    必须真的去 flock —— flock 按 fd 生效, 同进程不同 fd 也会冲突, 于是
    另一个线程会拿到 AccountBusy 而不是假装自己拿到了独占权。
    否则两个线程会同时连游戏服, 服务端把其中一个踢掉。
    """  # noqa: E501
    path = lock_file_for(key)
    with _LOCK_MUTEX:
        st = _lock_state(path)
        nested = (st["depth"] > 0
                  and st["tid"] == threading.get_ident())
    if nested:
        with _LOCK_MUTEX:
            _lock_state(path)["depth"] += 1
        try:
            yield
        finally:
            _release_lock_once(path)
        return

    fd = os.open(path, os.O_RDWR | os.O_CREAT, 0o644)
    deadline = time.time() + max(0.0, timeout)
    try:
        while True:
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except OSError as e:
                if e.errno not in (errno.EACCES, errno.EAGAIN):
                    raise
                if time.time() >= deadline:
                    raise AccountBusy(
                        "账号正被占用(同账号只允许一个连接)%s"
                        % (("; " + purpose) if purpose else ""))
                time.sleep(0.2)
        try:
            os.ftruncate(fd, 0)
            os.write(fd, ("%d %s\n" % (os.getpid(), purpose or "-")).encode())
        except OSError:
            pass
        with _LOCK_MUTEX:
            st = _lock_state(path)
            st["fd"] = fd
            st["depth"] = 1
            st["purpose"] = purpose
            st["tid"] = threading.get_ident()
        try:
            yield
        finally:
            _release_lock_once(path)
    except BaseException:
        # 还没成功拿到锁就退出了(flock 失败/抛异常) —— 别把 fd 泄漏掉
        with _LOCK_MUTEX:
            st = _lock_state(path)
            if st["fd"] == fd:
                st["fd"] = None
                st["depth"] = 0
                st["tid"] = None
        try:
            fcntl.flock(fd, fcntl.LOCK_UN)
        except OSError:
            pass
        try:
            os.close(fd)
        except OSError:
            pass
        raise


def account_holder(key=None):
    """当前锁文件里记的持有者(给页面显示用)。"""
    try:
        with open(lock_file_for(key), encoding="utf-8", errors="replace") as f:
            # 清掉 NUL / 空白 —— 文件可能被旧版本写过空洞
            raw = " ".join(f.read().split("\0")).strip()
            # "free" 是空闲占位, 不是持有者
            return "" if raw == "free" else raw
    except Exception:
        return ""


def account_is_busy(key=None):
    """锁现在是否被别人占着(不抢, 只看)。"""
    fd = os.open(lock_file_for(key), os.O_RDWR | os.O_CREAT, 0o644)
    try:
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            fcntl.flock(fd, fcntl.LOCK_UN)
            return False
        except OSError:
            return True
    finally:
        os.close(fd)


def account_holder_info(key=None):
    """锁持有者信息。

    flock 的锁绑在 open file description 上, **同进程用另一个 fd 再 flock 也会失败**,
    所以「本进程正在用账号」时 `account_is_busy()` 会返回 True —— 那是自指, 不是别人占用。
    这里把「是不是我自己」单独算出来, 免得页面拿自己占的锁报警。

    返回 {'holder': 原始字符串, 'pid': int|None, 'self': bool}
    """
    raw = account_holder(key)
    pid = None
    parts = raw.split()
    if parts and parts[0].isdigit():
        try:
            pid = int(parts[0])
        except ValueError:
            pid = None
    return {"holder": raw, "pid": pid,
            "self": pid is not None and pid == os.getpid()}


def apply_account_types(acc, template=None):
    """把账号 dict 里的整数字段恢复成正确的 SFS 类型(见 cok_sfs.restore_typed_fields)。

    JSON 存盘会把 TypedInt 退化成裸 int, 再读回来时 SFS 编码类型就变了
    (gmLogin 0 -> BYTE, screen_h 2577 -> SHORT), 服务端会直接拒登。
    """
    if not isinstance(acc, dict):
        return acc
    tmpl = template if template is not None else ACCOUNT
    return restore_typed_fields(acc, tmpl)


def load_account(source=None):
    """加载账号参数。

    source 可以是:
      None        -> 用内置默认值
      "<文件路径>"  -> 读 JSON 文件
      "device"     -> 直接从设备 SharedPreferences 读(需 root)
    """
    if source == "device":
        from cok_account import load_account as _la
        return _la()
    if source and os.path.isfile(source):
        with open(source, encoding="utf-8") as fh:
            return apply_account_types(json.load(fh))
    return {}


def load_typed_catalog(path=None):
    """载入带 SFS 类型的命令参数目录。

    服务端对参数类型敏感: 同一个字段用 STRING 传会返回 E000000, 用 INT 就正常。
    另外合并 `param-types-override.json`(静态反出但没抓到包的手工修正),
    手工条目可用 "auto": false 表示只纠正类型、不自动补默认值。
    """
    here = os.path.dirname(os.path.abspath(__file__))
    if path is None:
        path = _res("command-catalog-typed.json")
    cat = {}
    for p in (path, _res("param-types-override.json")):
        try:
            with open(p, encoding="utf-8") as fh:
                d = json.load(fh)
        except Exception:
            continue
        if not isinstance(d, dict):
            continue
        for cmd, specs in d.items():
            if cmd.startswith("_") or not isinstance(specs, list):
                continue
            cat.setdefault(cmd, [])
            have = {s.get("key") for s in cat[cmd]}
            for s in specs:
                if s.get("key") not in have:
                    cat[cmd].append(s)
    return cat


_TYPE_MAP = {
    "BYTE": SFS_BYTE, "SHORT": SFS_SHORT, "INT": SFS_INT, "LONG": SFS_LONG,
}


def encode_param(value, type_name):
    """按目录里记录的类型把值转成可编码对象。"""
    if type_name in _TYPE_MAP:
        try:
            return TypedInt(int(value), _TYPE_MAP[type_name])
        except (TypeError, ValueError):
            return str(value)
    if type_name == "BOOL":
        return bool(int(value)) if str(value) not in ("true", "True") else True
    return value


class CokClient(object):
    def __init__(self, host=DEFAULT_HOST, port=DEFAULT_PORT, timeout=30.0, account=None):
        self.timeout = timeout
        self.account = dict(ACCOUNT)
        if account:
            self.account.update(account)
        # Imported accounts from early Android builds can contain explicit
        # empty values for protocol-wide defaults. ``dict.update`` would let
        # those blanks erase the packaged defaults: login still succeeds, but
        # the server silently discards every encrypted feature request. Only
        # restore fields which are shared protocol configuration, never an
        # account identity or channel token.
        #
        # ⚠ 2026-11-12: 默认值**不能是脱敏占位符**。公开仓库里 ACCOUNT 的
        #   baseActiveKey 是 "<baseActiveKey>" 这种形态, 把它当真值回填 =
        #   给服务端发一个假字段 —— 登录能过, 但服务端会丢弃所有加密指令
        #   (表现是"连上了但界面全空")。真值从本地缓存/账号库取
        #   (cok_accounts.public_fields), 那是协议级公共字段, 所有账号同值。
        defaults = _public_defaults()
        for key in ("baseActiveKey", "appVersion", "luaVersion", "channelSign",
                    "isSmall", "isHDLogin", "lang", "region", "fromCountry",
                    "subscriberId", "phoneDevice", "pfchild", "gaid", "gmUid",
                    "afUID", "googlePlay", "pfSign", "linkname",
                    "instantAppCookie"):
            cur = self.account.get(key)
            if cur and not _is_placeholder(cur):
                continue  # 已有真值, 保留
            dv = defaults.get(key)
            if dv and not _is_placeholder(dv):
                self.account[key] = dv
        if not self.account.get("parseRegisterId"):
            # This is an installation registration marker, not an account
            # credential. A locally generated UUID is valid for Android
            # imports which did not have one persisted yet.
            self.account["parseRegisterId"] = str(uuidlib.uuid4())
        if not isinstance(self.account.get("device_info"), dict) or not self.account["device_info"]:
            self.account["device_info"] = dict(ACCOUNT.get("device_info") or {})
        else:
            # The Android package used to persist the literal placeholder
            # ``Android`` as os_version. This field is a protocol client
            # marker (rather than the device's Android release); the official
            # client sends the fixed value from ACCOUNT. That placeholder
            # authenticates, yet makes the server drop every feature command.
            # Repair existing imports in memory so users needn't re-add roles.
            device_info = self.account["device_info"]
            if device_info.get("os_version") == "Android":
                device_info["os_version"] = (ACCOUNT.get("device_info") or {}).get(
                    "os_version", "9.9.9")
        # Compatibility migration for Guopan accounts imported by builds which
        # omitted platformToken. The server-facing token is the role part of
        # ``ewanqf:<token>``; deriving it locally repairs existing accounts
        # without exposing credentials or requiring a second password login.
        pf_id = str(self.account.get("pfId") or "")
        if pf_id.startswith("ewanqf:") and ":" in pf_id:
            # Account dictionaries are first overlaid onto a generic template.
            # A legacy import can therefore carry a *non-empty token from a
            # different channel*. For Guopan, pfId and platformToken identify
            # the same selected role, so the pfId suffix is authoritative.
            self.account["platformToken"] = pf_id.partition(":")[2]
        # ⚠️ 贴回 SFS 整数类型: 账号可能来自 JSON(多账号库 / --account 文件),
        #    JSON 会把 TypedInt(INT) 退化成裸 int, 编码时 gmLogin 变成 BYTE、
        #    device_info 里的数字变成 SHORT —— 服务端对登录参数类型敏感,
        #    类型一错就拒登(响应 id 是数字 + init.error 推送)。
        restore_typed_fields(self.account, ACCOUNT)
        # 账号里带的服务器地址优先(设备上的 account_ip/account_port)
        self.host = self.account.get("host") or host
        self.port = int(self.account.get("port") or port)
        self.sock = None
        self.key = None
        self.key_id = None
        self.cok_prefix = random.randint(100000, 999999)
        self.seq = 0
        self.catalog = load_typed_catalog()
        self.rbuf = b""
        # 服务端主动推送帧(与请求命令不匹配的响应)。原先被静默丢弃,
        # 现在收集起来, 供"被攻击自动开保护罩"这类事件触发使用。
        self.pushes = []
        #: 可选的响应观察者: on_response(cmd, decoded) —— 解码后的**每个**
        #: 响应和推送都会调一次。用来被动学习"服务端下发的道具实例 uuid"
        #: (玩家背包没有只读接口, 只能从下发事件里学)。
        self.on_response = None
        # 登录后服务端下发的 `init` 推送(全局状态)。**只在这里下发**的数据
        # 有: cargo(码头宝箱的奖励物品/刷新时间)、building、assets 等。
        # 不缓存下来的话, 这些数据就永远拿不到 —— 端口卡片第一行
        # (type=0 的"码头宝箱"位)就是这么显示不出来的。
        self.init_params = {}

    # ---------------- 底层 ----------------
    def connect(self, retries=3, backoff=5.0):
        last = None
        for attempt in range(retries):
            try:
                self.sock = socket.create_connection((self.host, self.port), timeout=self.timeout)
                self.sock.settimeout(self.timeout)
                log("[*] 已连接 %s:%d" % (self.host, self.port))
                return self
            except Exception as e:  # noqa: BLE001
                last = e
                log("[!] 连接失败(%d/%d): %s" % (attempt + 1, retries, e))
                if attempt + 1 < retries:
                    time.sleep(backoff)
        raise CokError("无法连接 %s:%d —— %s" % (self.host, self.port, last))

    def close(self):
        try:
            if self.sock:
                self.sock.close()
        except Exception:
            pass
        self.sock = None

    def _send_frame(self, obj):
        payload = encode_object(obj)
        frame = bytes([0x80]) + struct.pack(">H", len(payload)) + payload
        self.sock.sendall(frame)
        return frame

    def _recv_exact(self, n):
        while len(self.rbuf) < n:
            chunk = self.sock.recv(65536)
            if not chunk:
                raise CokError("连接被服务端关闭（已收 %d/%d 字节）" % (len(self.rbuf), n))
            self.rbuf += chunk
        out, self.rbuf = self.rbuf[:n], self.rbuf[n:]
        return out

    @staticmethod
    def _is_zlib_head(head):
        """判断 head 是不是 zlib 流的开头(CMF/FLG)。

        zlib 头 2 字节: CMF=0x78(deflate/32K窗口), FLG 使 (CMF<<8|FLG)%31==0。
        """
        return len(head) >= 2 and head[0] == 0x78 and ((head[0] << 8) | head[1]) % 31 == 0

    def _read_zlib_stream(self, seed=b""):
        """把 socket 里的字节当成**一整条 zlib 流**读到结束。

        服务端对超大响应(实测: login.init 的 95 万字节玩家全量数据)会**不带
        帧长度**直接发一条裸 zlib 流 —— 这时帧头的 3 个字节其实就是 zlib 流的
        头两个字节, 长度字段是假的(读出来只有 39936, 实际 13 万)。
        所以这里不能用长度, 只能解到 zlib 流自然结束。
        """
        d = zlib.decompressobj()
        out = []
        data = seed + self.rbuf
        self.rbuf = b""
        while True:
            try:
                out.append(d.decompress(data))
            except zlib.error:
                break
            if d.eof:
                # 多读出来的字节要退回缓冲, 否则后面的帧全错位
                if d.unused_data:
                    self.rbuf = d.unused_data + self.rbuf
                break
            chunk = self.sock.recv(65536)
            if not chunk:
                raise CokError("连接被服务端关闭（zlib 流未结束）")
            data = chunk
        return b"".join(out)

    def _recv_frame(self):
        while True:
            head = self._recv_exact(3)
            flags = head[0]
            length = (head[1] << 8) | head[2]
            # 「裸 zlib 流」帧: 帧头 3 字节就是 zlib 流的开头(0x78 0x9c ...),
            # 长度字段无效 —— 必须解到流自然结束, 否则后面所有帧都错位。
            if flags & 0x20 and self._is_zlib_head(head[:2]):
                payload = self._read_zlib_stream(head)
                obj = read_value(Reader(payload))
                return flags, obj, obj
            payload = self._recv_exact(length)
            if flags & 0x20:
                try:
                    payload = zlib.decompress(payload)
                except zlib.error:
                    # 服务端心跳帧: flags=0xa8, 载荷只有 2 字节 "Yv" —— 它带
                    # 0x20(压缩) 位但根本不是压缩数据。以前在这里直接抛
                    # zlib.error, 把整个命令判成失败。心跳没有内容, 丢掉继续读。
                    if length <= 16:
                        continue
                    raise
            break
        obj = read_value(Reader(payload))
        # 注意: 不要用 flatten() —— 响应里 "p.c" 既是命令名又是顶层数字 c,
        # flatten 会因键冲突覆盖, 导致按命令名匹配响应失效。用原始嵌套结构。
        return flags, obj, obj

    def drain(self):
        """丢掉 socket 里残留的字节(错位后可能有迟到的旧响应)。

        ⚠️ 响应错位是致命的: 一个**迟到**的旧响应会被下一个请求"认领"
        (命令名相同), 于是那个请求拿到的是**别的中心**的数据 —— 坐标整个
        写错。所以校验发现对不上时, 必须先把 socket 洗干净再重发。
        """
        if not self.sock:
            return 0
        total = 0
        try:
            self.sock.settimeout(0.05)
            while True:
                chunk = self.sock.recv(65536)
                if not chunk:
                    break
                total += len(chunk)
        except (socket.timeout, OSError):
            pass
        finally:
            try:
                self.sock.settimeout(self.timeout)
            except OSError:
                pass
        self.rbuf = b""
        return total

    @staticmethod
    def _resp_cmd(obj):
        """从原始响应对象取命令名。"""
        p = obj.get("p") if isinstance(obj, dict) else None
        if isinstance(p, dict):
            c = p.get("c")
            if isinstance(c, str):
                return c
        return None

    @staticmethod
    def _resp_params(obj):
        """从原始响应对象取 params 段。

        线上结构有两种:
          bin 响应   : {"p": {ct, ms, tk}, "a":0, "c":0}          -> p 本身就是 params
          登录/业务  : {"p": {"p": {...}, ...}, "a":.., "c":..}    -> p.p 才是 params
        """
        p = obj.get("p") if isinstance(obj, dict) else None
        if not isinstance(p, dict):
            return {}
        inner = p.get("p")
        if isinstance(inner, dict):
            return inner
        return p

    # ---------------- 握手与登录 ----------------
    def bin_handshake(self):
        """bin 握手: 换游戏服 token(tk)。全程明文。

        信封类型必须与客户端一致: a=SHORT(0x03), c=BYTE(0x02)
        """
        self._send_frame({
            "p": {"bin": True, "cl": "Android", "api": "1.8.0"},
            "a": TypedInt(0, SFS_SHORT),
            "c": TypedInt(0, SFS_BYTE),
        })
        flags, obj, f = self._recv_frame()
        tk = self._resp_params(obj).get("tk")
        if not tk:
            raise CokError("bin 握手失败: %s" % json.dumps(f, ensure_ascii=False, default=str)[:300])
        bp = self._resp_params(obj)
        log("[+] bin 握手成功 tk=%s ct=%s ms=%s" % (tk, bp.get("ct"), bp.get("ms")))
        self.tk = tk
        return tk

    def login(self):
        """登录: 发明文登录请求, 从响应里取 id 并派生会话密钥。"""
        acc = self.account
        t = int(time.time())
        # Real client login uses the bootstrap sequence number 000000.  The
        # first encrypted request must then be 000001; starting login at 1
        # still permits authentication but channel game servers can silently
        # discard every subsequent feature request in that session.
        derived = derive_login_fields(
            t, acc["gameUid"], acc["appVersion"], acc.get("signCode"), acc.get("buildCode")
        )
        params = {
            "appVersion": acc["appVersion"],
            "luaVersion": acc["luaVersion"],
            "pfId": acc["pfId"],
            "gaid": acc["gaid"],
            "isHDLogin": acc["isHDLogin"],
            "pfchild": acc["pfchild"],
            "signCode": derived["signCode"],
            "buildCode": derived["buildCode"],
            "deviceId": acc["deviceId"],
            "isSmall": acc["isSmall"],
            "uuid": acc["uuid"],
            "serverId": acc["serverId"],
            "phoneDevice": acc["phoneDevice"],
            "gmUid": acc["gmUid"],
            "packageName": acc["packageName"],
            "lang": acc["lang"],
            "SecurityCode": derived["SecurityCode"],
            "cc": derived["cc"],
            "fromCountry": acc["fromCountry"],
            "gmLogin": acc["gmLogin"],
            "cmdBaseTime": str(t),
            "subscriberId": acc["subscriberId"],
            "gameUid": str(acc["gameUid"]),
            "newbasekey": "%032x" % random.getrandbits(128),
            "afUID": acc["afUID"],
            "googlePlay": acc["googlePlay"],
            "pfSign": acc["pfSign"],
            "platformToken": acc["platformToken"],
            "device_info": acc["device_info"],
            "parseRegisterId": acc["parseRegisterId"],
            "_cok_": "%06d%06d" % (self.cok_prefix, self.seq),
            "pf": acc["pf"],
            "channelSign": acc["channelSign"],
            "baseActiveKey": acc["baseActiveKey"],
            "linkname": acc["linkname"],
            "region": acc["region"],
            "instantAppCookie": acc["instantAppCookie"],
        }
        env = {
            "p": {
                "p": params,
                "zn": acc["zn"],
                "pw": acc["pw"],
                "un": str(acc["gameUid"]),
            },
            "a": TypedInt(1, SFS_SHORT),
            "c": TypedInt(0, SFS_BYTE),
        }
        self._send_frame(env)
        flags, obj, f = self._recv_frame()
        lp = self._resp_params(obj)

        # 服务端拒绝登录时不会下发 id。先翻译常见错误，避免把根因误报成
        # “登录响应里没有 id 字段”。
        if lp.get("ep") or lp.get("ec"):
            ep = lp.get("ep")
            ec = lp.get("ec")
            codes = [str(code) for code in ep] if isinstance(ep, list) else []
            zone_error = next((code for code in codes
                               if code.startswith("E003_ZONE_")), "")
            if zone_error:
                err_msg = ("登录失败：账号区服不匹配（服务端要求 COK%s，错误码 %s）"
                           % (zone_error.rsplit("_", 1)[-1], zone_error))
            elif codes:
                err_msg = "登录失败：服务器拒绝登录（错误码 %s）" % ", ".join(codes)
            else:
                err_msg = "登录失败：服务器返回异常响应"
            if ec:
                err_msg += " ec=%s" % ec
            raise CokError(err_msg)

        id_str = lp.get("id")
        if not id_str:
            raise CokError("登录响应里没有 id 字段: %s"
                           % json.dumps(lp, ensure_ascii=False, default=str)[:400])
        self.key, self.key_id = derive_session_key(id_str)
        log("[+] 登录成功  id=%s" % id_str)
        log("[+] 会话密钥 = %s   密钥ID = %s" % (self.key.decode(), self.key_id))
        return self.key, self.key_id

    # ---------------- 业务命令 ----------------
    def call(self, cmd, params=None, retries=1, timeout=None):
        """发一条业务命令并返回解码后的 params 明文(读操作)。

        实测: 新连接登录后, 服务端会**丢弃第一条加密业务请求**(不返回任何东西),
        重发同一条即可正常响应。所以这里默认在超时后自动重发一次。
        """
        if self.key is None:
            raise CokError("尚未登录")
        sock = self.sock
        previous_timeout = None
        if timeout is not None and sock is not None:
            previous_timeout = sock.gettimeout()
            sock.settimeout(timeout)
        try:
            last = None
            for attempt in range(retries + 1):
                try:
                    return self._call_once(cmd, params)
                except socket.timeout as e:
                    last = e
                    if attempt < retries:
                        log("[!] %s 无响应,重发一次(服务端会丢弃新连接的首条业务请求)" % cmd)
                        continue
                    raise CokError("命令 %s 无响应" % cmd)
                except CokError as e:
                    if "连接被服务端关闭" in str(e):
                        raise
                    last = e
                    if attempt < retries:
                        log("[!] %s 失败(%s),重试一次" % (cmd, e))
                        continue
                    raise
            raise CokError("命令 %s 失败: %s" % (cmd, last))
        finally:
            if previous_timeout is not None and sock is not None:
                try:
                    sock.settimeout(previous_timeout)
                except OSError:
                    pass

    def _call_once(self, cmd, params=None):
        self.seq += 1
        t = int(time.time())
        p = {
            "_cok_": "%06d%06d" % (self.cok_prefix, self.seq),
            # The live client sends this as an SFS STRING, even though it is
            # a Unix timestamp.  Sending an INT authenticates successfully
            # but channel servers silently drop subsequent feature requests.
            "cmdBaseTime": str(t),
            "newbasekey": "%032x" % random.getrandbits(128),
        }
        if params:
            p.update(params)
        # 按带类型目录补齐/纠正参数类型(服务端对类型敏感)
        for spec in (self.catalog.get(cmd) or []):
            k = spec["key"]
            if k in p:
                p[k] = encode_param(p[k], spec["type"])
            elif spec.get("auto", True) and k not in ("_cok_", "cmdBaseTime", "newbasekey"):
                p[k] = encode_param(spec["value"], spec["type"])
        plain = encode_object(p)
        cipher = xor_buf(plain, self.key)
        env = {
            "p": {"p": {"params": cipher}, "r": TypedInt(-1, SFS_INT), "c": cmd},
            "a": TypedInt(13, SFS_SHORT),
            "c": TypedInt(1, SFS_BYTE),
        }
        self._send_frame(env)
        # Keep Android field diagnostics useful without writing account data,
        # session keys, request bodies, or random replay-prevention values.
        log("[protocol] tx cmd=%s seq=%d params_bytes=%d" %
            (cmd, self.seq, len(plain)))

        deadline = time.time() + self.timeout
        while True:
            flags, obj, f = self._recv_frame()
            rcmd = self._resp_cmd(obj)
            if rcmd == cmd:
                decoded = self._decode_response(obj, cmd)
                log("[protocol] rx cmd=%s flags=0x%02x" % (cmd, flags))
                # 响应里也可能带新状态(如 cargo.reward 回的新宝箱状态)
                self._maybe_merge_cargo(decoded)
                return decoded
            # 推送帧(服务端主动下发): 收集而不是丢弃, 再继续等本命令的响应
            if rcmd:
                try:
                    decoded = self._decode_response(obj, rcmd)
                    self.pushes.append(decoded)
                    self._maybe_merge_cargo(decoded)
                except Exception:  # noqa: BLE001
                    self.pushes.append({"__cmd__": rcmd})
                if len(self.pushes) > 300:
                    del self.pushes[:-300]
            if time.time() > deadline:
                raise CokError("等待命令 %s 的响应超时(最后收到 cmd=%s)" % (cmd, rcmd))

    def take_pushes(self):
        """取走并清空收到的服务端推送帧列表。

        每项形如 {"__cmd__": "push.world.injured", "__params__": {...}}
        """
        out = list(self.pushes)
        self.pushes = []
        return out

    def receive_pushes(self, wait=0.0):
        """Read unsolicited server frames without bypassing the frame buffer.

        Login can be followed by an encrypted ``init`` push.  Callers used to
        read the socket directly for it, which bypassed ``rbuf`` and could
        split a later response across two readers.  Keep every frame on the
        same decoder path instead.
        """
        if self.sock is None:
            return []
        previous_timeout = self.sock.gettimeout()
        deadline = time.monotonic() + max(0.0, float(wait or 0.0))
        received = []
        try:
            while True:
                remaining = deadline - time.monotonic()
                if wait and remaining <= 0:
                    break
                self.sock.settimeout(min(1.0, remaining) if wait else 0.05)
                try:
                    _, obj, _ = self._recv_frame()
                except socket.timeout:
                    if not wait:
                        break
                    continue
                rcmd = self._resp_cmd(obj)
                if not rcmd:
                    continue
                try:
                    decoded = self._decode_response(obj, rcmd)
                except Exception:  # noqa: BLE001
                    decoded = {"__cmd__": rcmd}
                self.pushes.append(decoded)
                self._maybe_merge_cargo(decoded)
                received.append(decoded)
                if len(self.pushes) > 300:
                    del self.pushes[:-300]
        finally:
            try:
                self.sock.settimeout(previous_timeout)
            except OSError:
                pass
        return received

    def _maybe_merge_cargo(self, decoded):
        """把"码头宝箱"状态合并进缓存。

        宝箱(cargo)状态会出现在三个地方, 都会带**最新**值:
          * `init` 推送(登录时) —— 整个 init 缓存一份
          * `cargo.reward` 的**响应**(领取后: 立刻变成新物品 + 新倒计时)
          * 带 cargo 的推送(push.adreward 等)

        不合并的话, 领完之后页面还显示旧物品/旧倒计时。
        """
        ip = decoded.get("__params__")
        if not isinstance(ip, dict) or not ip:
            return
        if (decoded.get("__cmd__") or "") == "init":
            self.init_params = ip
            return
        cg = ip.get("cargo")
        if not isinstance(cg, dict):
            # 有些帧把宝箱字段直接摊在顶层
            if "rewardInfo" in ip or "rewardTime" in ip:
                cg = {k: ip.get(k) for k in
                      ("rewardInfo", "rewardTime", "times") if k in ip}
        if isinstance(cg, dict) and cg and self.init_params:
            self.init_params["cargo"] = cg

    def _decode_response(self, obj, cmd):
        """解码响应。

        两种形态:
        1) 明文 params(登录响应、cmd.ping 等): 直接挂在 p.p 下, 没有 qqq
        2) 加密 params(业务命令): p.p.qqq = 密钥ID, 另一个"混淆键"的值是
           hex 串 = XOR(key, zlib(SFS明文))
        """
        pp = self._resp_params(obj)
        rcmd = self._resp_cmd(obj)
        if not pp:
            return self._notify(cmd, {"__raw__": obj})
        qqq = pp.get("qqq")
        if qqq is None:
            return self._notify(cmd, {"__qqq__": None, "__cmd__": rcmd or cmd,
                    "__params__": flatten(pp) if not isinstance(pp, dict) else {k: v for k, v in pp.items()}})
        # 加密 params: 找值为长 hex 串的字段
        blob_key = None
        for k, v in pp.items():
            if k == "qqq":
                continue
            if isinstance(v, str) and len(v) > 32 and all(c in "0123456789abcdefABCDEF" for c in v):
                blob_key = k
                break
        if blob_key is None:
            return self._notify(cmd, {"__qqq__": qqq, "__cmd__": rcmd or cmd, "__raw__": obj})
        raw_hex = pp[blob_key]
        blob = binascii.unhexlify(raw_hex)
        x = xor_buf(blob, self.key)
        if x[:1] == b"\x78":
            body = zlib.decompressobj(-15).decompress(x[2:])
        else:
            body = zlib.decompress(x)
        # 用 parse_best: 它会尝试所有 SFS_ARRAY 编码模式并要求完整消费缓冲区
        inner, mode = parse_best(body)
        return self._notify(cmd, {"__qqq__": qqq, "__cmd__": rcmd or cmd, "__mode__": mode,
                "__params__": flatten(inner) if not isinstance(inner, dict) else inner})

    def _notify(self, cmd, decoded):
        """把解码后的响应/推送交给可选的观察者。

        用途: 自动打怪要喝背包里的体力药水, 而**玩家背包没有只读接口** ——
        道具实例 uuid 只能从"服务端下发道具"的响应里学到(领奖/掉落/获得)。
        调用方挂一个 on_response 钩子即可被动学到。
        """
        hook = getattr(self, "on_response", None)
        if hook is not None:
            try:
                hook(cmd, decoded)
            except Exception:  # noqa: BLE001
                pass
        return decoded


# ---------------- 离线自检 ----------------
def frame_bytes(obj):
    payload = encode_object(obj)
    return bytes([0x80]) + struct.pack(">H", len(payload)) + payload


def selftest():
    """不连服务器: 验证 编包 → XOR → 解包 → 派生密钥 的回环正确性。"""
    log("=== 离线回环自检 ===")
    key = b"5c64b9a7217a78b2e96ae87d4beaa36b"
    plain = encode_object({"_cok_": "123456000001", "cmdBaseTime": "1792658351",
                           "newbasekey": "a" * 32})
    cipher = xor_buf(plain, key)
    back = flatten(read_value(Reader(xor_buf(cipher, key))))
    ok1 = back.get("_cok_") == "123456000001"

    blob = xor_buf(zlib.compress(plain), key)
    x = xor_buf(blob, key)
    body = zlib.decompressobj(-15).decompress(x[2:])
    back2 = flatten(read_value(Reader(body)))
    ok2 = back2.get("cmdBaseTime") == "1792658351"

    # 登录字段派生自检: 输入(accountId/signCode/buildCode)**从 ACCOUNT 读**,
    # 不写死在源码里 —— 写死的话这些真凭据会被打进安卓 APK。
    # 安卓包里 ACCOUNT 是空模板(见 android-app/app/build.gradle), 这一项跳过。
    _acct = ACCOUNT
    if _acct.get("gameUid") and _acct.get("signCode") and _acct.get("buildCode"):
        d = derive_login_fields(1792658351, _acct["gameUid"], "12.06.0",
                                _acct["signCode"], _acct["buildCode"])
        ok3 = (d["SecurityCode"] == "014707b6687e72c32caeb40200833222"
               and d["cc"] == "2a6cb8e03c0cac24492d589d1dede6fb")
    else:
        ok3 = None   # 没有凭据(安卓包) -> 跳过, 不算失败
    k, kid = derive_session_key("4c462c581c94244362f283cd83766e4b_85")
    ok4 = k == key and kid == 85

    # 帧级等价: 重建的 bin 帧必须与线上真实帧逐字节一致
    mine_bin = frame_bytes({
        "p": {"bin": True, "cl": "Android", "api": "1.8.0"},
        "a": TypedInt(0, SFS_SHORT),
        "c": TypedInt(0, SFS_BYTE),
    })
    ok5 = mine_bin.hex() == REAL_BIN_FRAME

    log("  请求 XOR 回环      : %s" % ("OK" if ok1 else "FAIL"))
    log("  响应 XOR+zlib 回环 : %s" % ("OK" if ok2 else "FAIL"))
    log("  登录字段派生       : %s" % ("SKIP(无凭据)" if ok3 is None
                                          else ("OK" if ok3 else "FAIL")))
    log("  会话密钥派生       : %s" % ("OK" if ok4 else "FAIL"))
    log("  bin 帧逐字节等价   : %s" % ("OK" if ok5 else "FAIL"))
    if not ok5:
        log("    线上: %s" % REAL_BIN_FRAME)
        log("    我方: %s" % mine_bin.hex())
    return all((ok1, ok2, ok3 is not False, ok4, ok5))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default=DEFAULT_HOST)
    ap.add_argument("--port", type=int, default=DEFAULT_PORT)
    ap.add_argument("--cmd", default="cmd.ping", help="要发送的命令名(只读命令)")
    ap.add_argument("--params", default="{}", help="命令参数 JSON")
    ap.add_argument("--account", help="账号参数 JSON 文件(覆盖默认值)")
    ap.add_argument("--account-device", action="store_true",
                    help="从设备 SharedPreferences 自动读取账号与服务器地址")
    ap.add_argument("--timeout", type=float, default=30.0)
    ap.add_argument("--dump-only", action="store_true", help="只做离线自检")
    ap.add_argument("--no-login", action="store_true", help="跳过登录")
    ap.add_argument("--no-ping", action="store_true", help="登录后不自动发 cmd.ping")
    args = ap.parse_args()

    if args.dump_only:
        return 0 if selftest() else 1

    account = None
    if args.account_device:
        account = load_account("device")
        log("[+] 已从设备读取账号: %s" % json.dumps(
            {k: account.get(k) for k in ("pfId", "gameUid", "host", "port")}, ensure_ascii=False))
    elif args.account:
        account = load_account(args.account)

    c = CokClient(args.host, args.port, args.timeout, account)
    try:
        c.connect()
        if not args.no_login:
            c.bin_handshake()
            c.login()
            if not args.no_ping:
                # 新连接先发一条 cmd.ping：实测服务端需要先收到这一条才会正常回业务命令
                try:
                    c.call("cmd.ping")
                    log("[+] 已完成握手 ping")
                except Exception as e:  # noqa: BLE001
                    log("[!] 握手 ping 失败(继续): %s" % e)
        res = c.call(args.cmd, json.loads(args.params))
        log("\n=== %s 响应 ===" % args.cmd)
        if "__params__" in res:
            log("  qqq(密钥ID) = %s   线上命令 = %s" % (res.get("__qqq__"), res.get("__cmd__")))
            for k, v in res["__params__"].items():
                log("  %-28s = %s" % (k, str(v)[:160]))
        else:
            log(json.dumps(res, ensure_ascii=False, indent=2))
    finally:
        c.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
