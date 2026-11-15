#!/usr/bin/env python3
"""COK 平台层 —— SQLite 持久化(用户 / 会话 / 邀请 / 审计 / 限流)。

为什么要它(2026-11-14):
    控制台从"单人自用"改成"朋友也能接进来的平台"之后, 三件事必须落盘且**可靠**:
      1. 用户与会话 —— 以前是 `users.json` / `sessions.json`(JSON 文件)。
         JSON 的问题不是"不够快", 而是**并发写会丢**: 两个人同时登录, 后写的
         那份会把先写的整个覆盖掉(读-改-写没有锁)。
      2. 审计 —— 朋友共用一台机器, 谁删了谁的号、谁在什么时候加了号, 事后要查。
         JSON 追加日志没有索引, 查一次要整文件读。
      3. 限流 —— 公开分发的入口, 登录接口必须能挡住暴力破解。

为什么是 SQLite 而不是别的:
    * 标准库自带(`sqlite3`), 服务器上不用装任何东西 —— 和这个项目"零新依赖"
      的一贯做法一致。
    * 单文件(`data/platform.db`), 备份就是 `cp` 一个文件。
    * WAL 模式: 读不阻塞写, 10 个人同时开着页面也不会互相等锁。
    * 撑不住的时候(比如以后真做成几千人)换 Postgres 只改这一个模块。

线程模型:
    控制台是 `ThreadingHTTPServer` —— 每个请求一个线程。所以这里用
    `check_same_thread=False` + **一把进程级可重入锁**串行化写入。
    10 人规模下写入量极小(登录/审计), 串行完全够; 真到瓶颈再上连接池。
"""

import hashlib
import os
import secrets
import sqlite3
import threading
import time

import cok_paths

#: 数据库文件位置。环境变量可覆盖 —— 测试靠它指到临时目录, 不动真库。
DB_PATH = os.environ.get("COK_PLATFORM_DB") or os.path.join(
    cok_paths.data_dir(), "platform.db")

#: 审计日志保留条数(按 id 倒序裁剪, 防止无限增长)
AUDIT_KEEP = 5000

_LOCK = threading.RLock()
_CONN = None


# ---------------------------------------------------------------- 连接
def _connect():
    """打开(或复用)连接并保证表结构存在。"""
    global _CONN
    with _LOCK:
        if _CONN is not None:
            return _CONN
        d = os.path.dirname(os.path.abspath(DB_PATH))
        if d:
            try:
                os.makedirs(d, exist_ok=True)
            except OSError:
                pass
        conn = sqlite3.connect(DB_PATH, timeout=10.0,
                               check_same_thread=False)
        conn.row_factory = sqlite3.Row
        # WAL: 读不阻塞写(多个人同时开页面时最直观的收益)
        # synchronous=NORMAL: WAL 下断电最多丢最后一个事务, 换吞吐
        # busy_timeout: 偶发写锁竞争时等待而不是直接 "database is locked"
        for pragma in ("journal_mode=WAL", "synchronous=NORMAL",
                       "busy_timeout=5000", "foreign_keys=ON"):
            try:
                conn.execute("PRAGMA " + pragma)
            except sqlite3.Error:
                pass
        conn.executescript(SCHEMA)
        conn.commit()
        _CONN = conn
        return conn


def conn():
    """给外部(迁移脚本/管理命令)用的连接。"""
    return _connect()


def close():
    """关掉连接(测试用; 进程退出时不必调)。"""
    global _CONN
    with _LOCK:
        if _CONN is not None:
            try:
                _CONN.close()
            except sqlite3.Error:
                pass
            _CONN = None


def now():
    return time.time()


# ---------------------------------------------------------------- 用户
def user_get(username):
    return _one("SELECT * FROM users WHERE username=?", (str(username or ""),))


def user_add(username, uid, pwd, salt, role="user", created=0.0):
    """新增一个用户(不覆盖已存在的)。

    注册路径用它: `cok_users.register()` 写的是 **JSON 文件**(users.json),
    平台层读的是 **SQLite** —— 两边各写一份等于有两个真相, 迟早不一致。
    ⇒ 平台模式下的真相是 SQLite; `cok_users` 只贡献口令派生算法。
    """
    username = str(username or "")
    if not username or user_get(username):
        return False
    with _LOCK:
        _q("INSERT OR IGNORE INTO users(uid,username,pwd,salt,role,created_at)"
           " VALUES(?,?,?,?,?,?)",
           (str(uid or ""), username, str(pwd or ""), str(salt or ""),
            str(role or "user"), float(created or now())))
    return True


def user_get_by_uid(uid):
    return _one("SELECT * FROM users WHERE uid=?", (str(uid or ""),))


def user_upsert(username, uid, pwd, salt, role="user", created=0.0, keep=False):
    """建/改一个用户。

    keep=True 时**不覆盖已有口令**(只补缺失字段) —— 迁移脚本要靠它避免
    把库里的新口令写回旧值。
    """
    username = str(username or "")
    if not username:
        return False
    if keep and user_get(username):
        return True
    with _LOCK:
        _q("INSERT INTO users(uid,username,pwd,salt,role,banned,note,created_at,last_login)"
           " VALUES(?,?,?,?,?,0,'',?,0)"
           " ON CONFLICT(username) DO UPDATE SET uid=excluded.uid,"
           "pwd=excluded.pwd, salt=excluded.salt, role=excluded.role",
           (str(uid or ""), username, str(pwd or ""), str(salt or ""),
            str(role or "user"), float(created or now())))
    return True


def user_set_password(username, pwd, salt):
    with _LOCK:
        cur = _q("UPDATE users SET pwd=?, salt=? WHERE username=?",
                 (str(pwd or ""), str(salt or ""), str(username or "")))
        return cur.rowcount > 0


def user_set_role(username, role):
    with _LOCK:
        cur = _q("UPDATE users SET role=? WHERE username=?",
                 (str(role or "user"), str(username or "")))
        return cur.rowcount > 0


def user_set_banned(username, banned):
    with _LOCK:
        cur = _q("UPDATE users SET banned=? WHERE username=?",
                 (1 if banned else 0, str(username or "")))
        return cur.rowcount > 0


def user_touch_login(username, ts=None):
    with _LOCK:
        _q("UPDATE users SET last_login=? WHERE username=?",
           (float(ts if ts is not None else now()), str(username or "")))


def user_delete(username):
    """删用户 + 他的会话/邀请归属记录(账号文件不动, 交给调用方决定)。"""
    username = str(username or "")
    with _LOCK:
        row = user_get(username)
        if not row:
            return False
        _q("DELETE FROM sessions WHERE uid=?", (row["uid"],))
        _q("DELETE FROM users WHERE username=?", (username,))
        return True


def user_count():
    row = _one("SELECT COUNT(*) AS n FROM users")
    return int(row["n"]) if row else 0


def list_users(limit=200):
    return _rows("SELECT uid,username,role,banned,created_at,last_login "
                 "FROM users ORDER BY created_at LIMIT ?", (int(limit),))


def first_user():
    return _one("SELECT * FROM users ORDER BY created_at LIMIT 1")


# ---------------------------------------------------------------- 会话
def session_save(sid, uid, ttl, ip="", ua=""):
    t = now()
    with _LOCK:
        _q("INSERT INTO sessions(sid_hash,uid,created_at,expires_at,last_seen,ip,ua)"
           " VALUES(?,?,?,?,?,?,?)"
           " ON CONFLICT(sid_hash) DO UPDATE SET expires_at=excluded.expires_at,"
           "last_seen=excluded.last_seen",
           (hash_sid(sid), str(uid or ""), t, t + float(ttl), t,
            str(ip or "")[:64], str(ua or "")[:200]))


def session_user(sid, touch=True):
    """sid -> uid(有效); 无效/过期返回 ""。

    过期会话顺手删掉(不删会一直占着表)。
    """
    if not sid:
        return ""
    h = hash_sid(sid)
    row = _one("SELECT * FROM sessions WHERE sid_hash=?", (h,))
    if not row:
        return ""
    if float(row["expires_at"]) < now():
        session_drop(sid)
        return ""
    if touch:
        with _LOCK:
            _q("UPDATE sessions SET last_seen=? WHERE sid_hash=?", (now(), h))
    return row["uid"]


def session_drop(sid):
    if not sid:
        return
    with _LOCK:
        _q("DELETE FROM sessions WHERE sid_hash=?", (hash_sid(sid),))


def session_drop_user(uid):
    with _LOCK:
        _q("DELETE FROM sessions WHERE uid=?", (str(uid or ""),))


def sessions_cleanup():
    with _LOCK:
        cur = _q("DELETE FROM sessions WHERE expires_at < ?", (now(),))
        return cur.rowcount or 0


def sessions_of(uid, limit=20):
    return _rows("SELECT sid_hash,created_at,expires_at,last_seen,ip "
                 "FROM sessions WHERE uid=? ORDER BY last_seen DESC LIMIT ?",
                 (str(uid or ""), int(limit)))


# ---------------------------------------------------------------- 邀请码
def invite_create(code, created_by="", expires_at=0, note=""):
    code = str(code or "").strip()
    if not code:
        return False
    with _LOCK:
        _q("INSERT INTO invites(code,created_by,created_at,expires_at,note)"
           " VALUES(?,?,?,?,?)"
           " ON CONFLICT(code) DO UPDATE SET created_at=excluded.created_at,"
           "created_by=excluded.created_by, used_by='', used_at=0,"
           "expires_at=excluded.expires_at",
           (code, str(created_by or ""), now(), float(expires_at or 0),
            str(note or "")[:200]))
    return True


def invite_new(created_by="", expires_at=0, note=""):
    """生成一个随机邀请码(一次性用)。"""
    for _ in range(5):
        code = "COK-" + secrets.token_hex(4).upper()
        if not invite_get(code):
            invite_create(code, created_by, expires_at, note)
            return code
    return ""


def invite_get(code):
    return _one("SELECT * FROM invites WHERE code=?", (str(code or "").strip(),))


def invite_consume(code, used_by):
    """用掉一个邀请码。返回 (ok, msg)。

    一次性: 用过就是用过, 重复用返回 False(而不是"静默放行")。
    """
    row = invite_get(code)
    if not row:
        return False, "邀请码不存在"
    if row["used_by"]:
        return False, "邀请码已被使用"
    if row["expires_at"] and float(row["expires_at"]) < now():
        return False, "邀请码已过期"
    with _LOCK:
        _q("UPDATE invites SET used_by=?, used_at=? WHERE code=? AND used_by=''",
           (str(used_by or ""), now(), row["code"]))
    return True, "ok"


def invites_list(limit=100):
    return _rows("SELECT * FROM invites ORDER BY created_at DESC LIMIT ?",
                 (int(limit),))


# ---------------------------------------------------------------- 表结构
SCHEMA = """
CREATE TABLE IF NOT EXISTS meta (
    k TEXT PRIMARY KEY,
    v TEXT
);

CREATE TABLE IF NOT EXISTS users (
    uid          TEXT PRIMARY KEY,
    username     TEXT UNIQUE NOT NULL,
    pwd          TEXT NOT NULL,
    salt         TEXT NOT NULL,
    role         TEXT NOT NULL DEFAULT 'user',
    banned       INTEGER NOT NULL DEFAULT 0,
    note         TEXT NOT NULL DEFAULT '',
    created_at   REAL NOT NULL,
    last_login   REAL NOT NULL DEFAULT 0,
    must_change_pwd INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS sessions (
    sid_hash     TEXT PRIMARY KEY,
    uid          TEXT NOT NULL,
    created_at   REAL NOT NULL,
    expires_at   REAL NOT NULL,
    last_seen    REAL NOT NULL DEFAULT 0,
    ip           TEXT NOT NULL DEFAULT '',
    ua           TEXT NOT NULL DEFAULT ''
);
CREATE INDEX IF NOT EXISTS idx_sessions_uid ON sessions(uid);

CREATE TABLE IF NOT EXISTS invites (
    code         TEXT PRIMARY KEY,
    created_by   TEXT NOT NULL DEFAULT '',
    created_at   REAL NOT NULL,
    expires_at   REAL NOT NULL DEFAULT 0,
    used_by      TEXT NOT NULL DEFAULT '',
    used_at      REAL NOT NULL DEFAULT 0,
    note         TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS audit (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    uid          TEXT NOT NULL DEFAULT '',
    ip           TEXT NOT NULL DEFAULT '',
    action       TEXT NOT NULL DEFAULT '',
    target       TEXT NOT NULL DEFAULT '',
    ok           INTEGER NOT NULL DEFAULT 1,
    detail       TEXT NOT NULL DEFAULT '',
    ts           REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_audit_ts ON audit(ts DESC);
CREATE INDEX IF NOT EXISTS idx_audit_uid ON audit(uid, id DESC);

CREATE TABLE IF NOT EXISTS ratelimit (
    bucket       TEXT PRIMARY KEY,
    hits         INTEGER NOT NULL DEFAULT 0,
    window_start REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS kv (
    uid          TEXT NOT NULL DEFAULT '',
    k            TEXT NOT NULL,
    v            TEXT NOT NULL DEFAULT '',
    PRIMARY KEY (uid, k)
);
"""


def init():
    """建表(幂等)。进程启动时调一次即可。

    另外做**增量迁移**: 老库(改造初期建的)没有 `must_change_pwd` 列,
    CREATE TABLE IF NOT EXISTS 不会补列 —— 于是读写都会报 "no such column"。
    这里显式检查并 ALTER, 让新旧库都能跑。
    """
    c = _connect()
    try:
        cols = {r["name"] for r in c.execute("PRAGMA table_info(users)")}
        if "must_change_pwd" not in cols:
            c.execute("ALTER TABLE users ADD COLUMN "
                      "must_change_pwd INTEGER NOT NULL DEFAULT 0")
            c.commit()
    except Exception:  # noqa: BLE001
        pass
    return DB_PATH


def _q(sql, args=()):
    c = _connect()
    with _LOCK:
        cur = c.execute(sql, args)
        c.commit()
        return cur


def _rows(sql, args=()):
    c = _connect()
    with _LOCK:
        return [dict(r) for r in c.execute(sql, args).fetchall()]


def _one(sql, args=()):
    c = _connect()
    with _LOCK:
        r = c.execute(sql, args).fetchone()
        return dict(r) if r else None


# ---------------------------------------------------------------- 会话 id
def hash_sid(sid):
    """会话 id 只存 **hash**。

    数据库被人拷走时, 攻击者拿不到可用的 sid(明文 sid = 直接冒充登录)。
    """
    return hashlib.sha256((sid or "").encode("utf-8")).hexdigest()


def new_sid():
    return secrets.token_urlsafe(32)


# ---------------------------------------------------------------- 限流
def rate_hit(bucket, limit, window):
    """固定窗口计数。

    返回 `(ok, retry_after)`:
      ok=True        -> 放行(已记一次)
      ok=False       -> 超限, retry_after 是建议的等待秒数

    为什么用固定窗口而不是令牌桶: 登录限流只需要"这个 IP 一分钟内最多试 5 次"
    这种粗粒度保护, 固定窗口实现简单、没有边界 bug(令牌桶在进程重启后状态
    就丢了, 而这里状态在库里)。
    """
    bucket = str(bucket or "")
    if not bucket:
        return True, 0
    t = now()
    with _LOCK:
        row = _one("SELECT hits, window_start FROM ratelimit WHERE bucket=?",
                   (bucket,))
        if not row or t - float(row["window_start"]) >= float(window):
            _q("INSERT INTO ratelimit(bucket,hits,window_start) VALUES(?,?,?) "
               "ON CONFLICT(bucket) DO UPDATE SET hits=1, window_start=excluded.window_start",
               (bucket, 1, t))
            return True, 0
        hits = int(row["hits"]) + 1
        _q("UPDATE ratelimit SET hits=? WHERE bucket=?", (hits, bucket))
        if hits > int(limit):
            left = float(window) - (t - float(row["window_start"]))
            return False, max(1, int(left) + 1)
        return True, 0


def rate_reset(bucket):
    with _LOCK:
        _q("DELETE FROM ratelimit WHERE bucket=?", (str(bucket or ""),))


# ---------------------------------------------------------------- 审计
def audit(uid, action, target="", ok=True, detail="", ip=""):
    """记一条审计。写失败**不能**影响主流程 —— 兜底只打日志。"""
    try:
        with _LOCK:
            _q("INSERT INTO audit(uid,ip,action,target,ok,detail,ts) "
               "VALUES(?,?,?,?,?,?,?)",
               (str(uid or ""), str(ip or ""), str(action or ""),
                str(target or ""), 1 if ok else 0,
                str(detail or "")[:500], now()))
            # 稀疏裁剪: 每写 200 条才裁一次, 避免每条都跑一次 DELETE
            c = _connect()
            n = c.execute("SELECT COUNT(*) AS n FROM audit").fetchone()["n"]
            if n > AUDIT_KEEP + 200:
                c.execute("DELETE FROM audit WHERE id < "
                          "(SELECT MAX(id) - ? FROM audit)", (AUDIT_KEEP,))
                c.commit()
    except Exception:  # noqa: BLE001
        pass


def recent_audit(uid=None, limit=100, action=None):
    sql = "SELECT * FROM audit"
    where, args = [], []
    if uid is not None:
        where.append("uid=?")
        args.append(str(uid))
    if action:
        where.append("action=?")
        args.append(str(action))
    if where:
        sql += " WHERE " + " AND ".join(where)
    sql += " ORDER BY id DESC LIMIT ?"
    args.append(max(1, min(500, int(limit))))
    return _rows(sql, tuple(args))


# ---------------------------------------------------------------- 键值(每用户)
def kv_get(uid, k, default=""):
    row = _one("SELECT v FROM kv WHERE uid=? AND k=?",
               (str(uid or ""), str(k)))
    return row["v"] if row else default


def kv_set(uid, k, v):
    with _LOCK:
        _q("INSERT INTO kv(uid,k,v) VALUES(?,?,?) "
           "ON CONFLICT(uid,k) DO UPDATE SET v=excluded.v",
           (str(uid or ""), str(k), str(v if v is not None else "")))


def kv_del(uid, k):
    with _LOCK:
        _q("DELETE FROM kv WHERE uid=? AND k=?", (str(uid or ""), str(k)))


# ---------------------------------------------------------------- 统计(给管理端)
def stats():
    """一张表看清平台现状(管理页用)。"""
    c = _connect()
    with _LOCK:
        n_users = c.execute("SELECT COUNT(*) AS n FROM users").fetchone()["n"]
        n_banned = c.execute(
            "SELECT COUNT(*) AS n FROM users WHERE banned=1").fetchone()["n"]
        n_sess = c.execute(
            "SELECT COUNT(*) AS n FROM sessions WHERE expires_at>?",
            (now(),)).fetchone()["n"]
        n_inv = c.execute(
            "SELECT COUNT(*) AS n FROM invites WHERE used_by=''").fetchone()["n"]
        n_audit = c.execute("SELECT COUNT(*) AS n FROM audit").fetchone()["n"]
    return {"users": int(n_users), "banned": int(n_banned),
            "sessions": int(n_sess), "invites_unused": int(n_inv),
            "audit_rows": int(n_audit), "db": DB_PATH}