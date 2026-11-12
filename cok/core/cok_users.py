#!/usr/bin/env python3
"""COK 控制台**多用户**系统(2026-10-29, 架构③: 一台云主机多人共用)。

为什么要有:
    之前控制台是"单 token 全局鉴权 + 全局 .active 指针" —— 一个人用没问题,
    但一台云主机给 5-10 个人共用时:
      * 任何人都能看到/切到别人的账号(凭据 + 游戏数据全串了)
      * 谁的号在跑、谁的号被踢, 全都分不清
    所以引入**用户**: 每人一个账号, 登录后只能看到自己名下的账号。

设计:
    users.json     {用户名: {pwd: <scrypt 派生>, salt, created, role}}
    sessions.json  {sid: {user, exp, created}}      (内存里也留一份, 少一次 IO)
    账号归属: 账号 JSON 里加 "owner": <用户名>; 列表/切换/删除都按 owner 过滤
    每人的"当前账号/并行账号": accounts/.u/<用户名>/{active,parallel}

口令用 hashlib.scrypt(N=2**14, r=8, p=1) + 随机 16 字节 salt,
**不存明文**; 库文件权限 0600。
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
from cok_paths import data_dir as _data_dir  # noqa: E402

import hashlib
import json
import os
import re
import secrets
import time


#: 多用户注册表: 账号库旁边的 users.json / sessions.json / .u/
_UROOT = os.path.join(_data_dir(), "accounts")
USERS_FILE = os.path.join(_UROOT, "users.json")
SESSIONS_FILE = os.path.join(_UROOT, "sessions.json")
UDIR = os.path.join(_UROOT, ".u")

SESSION_TTL = 30 * 24 * 3600          # 30 天
#: 口令派生。优先 scrypt, 但 **macOS 自带 Python 的 OpenSSL 常没编 scrypt**
#: (实测 hashlib.scrypt 不存在) → 退到 PBKDF2-HMAC-SHA256。
_HAS_SCRYPT = hasattr(hashlib, "scrypt")
_PBKDF2_ROUNDS = 200000
_USER_RE = re.compile(r"^[A-Za-z0-9_.\-]{2,32}$")

#: 内存缓存(避免每个请求都读盘); 文件是真相, 缓存只加速
_users_cache = None
_sessions_cache = None


# ---------------------------------------------------------------- 原子读写
def _load(path, default):
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return default


def _save(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, ensure_ascii=False, indent=1)
    os.replace(tmp, path)
    try:
        os.chmod(path, 0o600)
    except OSError:
        pass


def _users():
    global _users_cache
    if _users_cache is None:
        _users_cache = _load(USERS_FILE, {})
    return _users_cache


def _sessions():
    global _sessions_cache
    if _sessions_cache is None:
        _sessions_cache = _load(SESSIONS_FILE, {})
    return _sessions_cache


def _persist_users():
    _save(USERS_FILE, _users())


def _persist_sessions():
    _save(SESSIONS_FILE, _sessions())


# ---------------------------------------------------------------- 口令
def hash_password(password, salt=None):
    """口令派生, 返回 (hash_hex, salt_hex)。

    scrypt 优先, 没有就 PBKDF2-HMAC-SHA256(20 万轮) —— 两者都是标准库。
    """
    salt = salt or secrets.token_hex(16)
    raw = bytes.fromhex(salt)
    if _HAS_SCRYPT:
        dk = hashlib.scrypt(password.encode("utf-8"), salt=raw,
                            n=2 ** 14, r=8, p=1, dklen=32)
    else:
        dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), raw,
                                 _PBKDF2_ROUNDS, dklen=32)
    return dk.hex(), salt


def verify_password(password, pwd_hex, salt_hex):
    try:
        calc, _ = hash_password(password, salt_hex)
    except Exception:  # noqa: BLE001
        return False
    return secrets.compare_digest(calc, pwd_hex)


# ---------------------------------------------------------------- 用户
def list_users():
    return sorted(_users().keys())


def user_exists(username):
    return username in _users()


def register(username, password, role="user"):
    """注册。返回 (ok, msg)。"""
    username = (username or "").strip()
    if not _USER_RE.match(username):
        return False, "用户名只允许 2-32 位字母数字 _ . -"
    if len(password or "") < 6:
        return False, "密码至少 6 位"
    if username in _users():
        return False, "用户名已存在"
    pwd, salt = hash_password(password)
    _users()[username] = {
        "pwd": pwd, "salt": salt, "role": role,
        "created": time.strftime("%Y-%m-%dT%H:%M:%S"),
    }
    _persist_users()
    os.makedirs(os.path.join(UDIR, username), exist_ok=True)
    return True, "注册成功"


def check_password(username, password):
    u = _users().get(username or "")
    if not u:
        return False
    return verify_password(password or "", u.get("pwd", ""), u.get("salt", ""))


def set_password(username, password):
    u = _users().get(username)
    if not u:
        return False
    pwd, salt = hash_password(password)
    u["pwd"], u["salt"] = pwd, salt
    _persist_users()
    return True


def remove_user(username):
    if username not in _users():
        return False
    del _users()[username]
    _persist_users()
    # 清掉该用户的会话
    for sid in [s for s, v in _sessions().items() if v.get("user") == username]:
        del _sessions()[sid]
    _persist_sessions()
    return True


# ---------------------------------------------------------------- 会话
def login(username, password, ttl=SESSION_TTL):
    """登录成功返回 sid, 失败返回 None。"""
    if not check_password(username, password):
        return None
    sid = secrets.token_urlsafe(32)
    _sessions()[sid] = {"user": username, "exp": time.time() + ttl,
                        "created": time.time()}
    _persist_sessions()
    return sid


def logout(sid):
    if sid and sid in _sessions():
        del _sessions()[sid]
        _persist_sessions()


def user_of(sid):
    """sid -> 用户名; 无效/过期返回 ""。"""
    s = _sessions().get(sid or "")
    if not s:
        return ""
    if s.get("exp", 0) < time.time():
        del _sessions()[sid]
        _persist_sessions()
        return ""
    return s.get("user", "")


def cleanup_sessions():
    now = time.time()
    dead = [s for s, v in _sessions().items() if v.get("exp", 0) < now]
    for s in dead:
        del _sessions()[s]
    if dead:
        _persist_sessions()
    return len(dead)


# ---------------------------------------------------------------- 每人的状态
def _udir(username):
    return os.path.join(UDIR, username or "_")


def user_file(username, name):
    return os.path.join(_udir(username), name)


def get_active(username):
    """某人的当前账号 key。"""
    try:
        with open(user_file(username, "active"), encoding="utf-8") as fh:
            return fh.read().strip()
    except OSError:
        return ""


def set_active(username, key):
    os.makedirs(_udir(username), exist_ok=True)
    p = user_file(username, "active")
    tmp = p + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        fh.write(str(key or "") + "\n")
    os.replace(tmp, p)


def get_parallel(username):
    """某人的并行账号集合。"""
    try:
        with open(user_file(username, "parallel"), encoding="utf-8") as fh:
            return set(json.load(fh))
    except (OSError, ValueError):
        return set()


def set_parallel(username, keys):
    os.makedirs(_udir(username), exist_ok=True)
    p = user_file(username, "parallel")
    tmp = p + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(sorted(keys or []), fh)
    os.replace(tmp, p)


def main():
    import argparse
    ap = argparse.ArgumentParser(description="COK 控制台多用户管理")
    sub = ap.add_subparsers(dest="cmd")
    p = sub.add_parser("add", help="加用户")
    p.add_argument("username")
    p.add_argument("password")
    p.add_argument("--role", default="user")
    p.add_argument("--passwd", help="从终端读密码(不给则用命令行参数)")
    p = sub.add_parser("rm", help="删用户")
    p.add_argument("username")
    p = sub.add_parser("ls", help="列用户")
    sub.add_parser("sessions", help="列会话")
    p = sub.add_parser("passwd", help="改密码")
    p.add_argument("username")
    p.add_argument("password")
    args = ap.parse_args()

    if args.cmd in ("add", "passwd"):
        pwd = args.password
        if getattr(args, "passwd", None):
            import getpass
            pwd = getpass.getpass("密码: ")
        if args.cmd == "add":
            ok, msg = register(args.username, pwd, args.role)
            print(msg)
            return 0 if ok else 1
        print("已改密" if set_password(args.username, pwd) else "用户不存在")
        return 0
    if args.cmd == "rm":
        print("已删除" if remove_user(args.username) else "用户不存在")
        return 0
    if args.cmd == "ls":
        for u in list_users():
            print("  %-20s %s" % (u, _users()[u].get("created", "")))
        return 0
    if args.cmd == "sessions":
        for sid, v in sorted(_sessions().items(), key=lambda kv: kv[1].get("created", 0)):
            print("  %-8s %-20s 到期 %s" % (sid[:8], v.get("user"),
                                           time.strftime(
                                               "%Y-%m-%d %H:%M",
                                               time.localtime(v.get("exp", 0)))))
        return 0
    ap.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
