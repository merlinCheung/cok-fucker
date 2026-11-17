#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""COK 业务状态入库（运行态 / 配置 / 索引 / 审计）。

# 为什么要这一层

在此之前，web 端的数据分成三堆，谁都不完整：

  1. **JSON 文件**：web-settings.json、automation-history.json、task-stats.json、
     scan-history.json、map-index.json、accounts/*.json —— 单机单用户时代够用，
     但它们**没有归属、没有并发控制、进程一挂就只剩最后一份快照**。
  2. **纯内存**：`EngineManager.running` / `_tasks` / `self.states[key]`、
     用户的"当前查看哪个号"、PlatformManager 的 owner→引擎表 ——
     **重启即丢**。服务器上重启一次服务，网页上"哪些号在跑/跑到哪了"全部归零，
     而账号在游戏里其实还在被操作（连接没断），两边状态直接不一致。
  3. **根本没存**：谁在什么时候跑了什么任务、被谁停的、为什么停 —— 全查不到。

# 分层原则（重要，改代码前先读）

**JSON 文件仍是每类数据的"原始快照"，数据库是权威索引 + 跨进程可查的运行时。**

这样分工的理由很实在：
  * 安卓端要读 `map-index.json`（扫描子进程在 assets 目录里跑，拿不到 DB 句柄）；
  * 迁移必须能"一次导入、随时重扫"（DB 坏了可以从 JSON 重建）；
  * 反过来，DB 里的运行态**必须**能被另一个进程看到 —— 网页控制台和扫描器
    是两个进程，"在不在跑"这件事只有共享存储说得清。

所以：**凡是"进程 A 写、进程 B 要看"的，必须进 DB；凡是"单进程算完就能扔的
缓存"，留在内存或文件里就好。** 别把纯缓存也塞进来，那是给自己加同步负担。

# 表清单

  users               ← 补平台用户种子（账号库里的 owner 必须在 users 里有行）
  user_settings       ← 每用户配置（web-settings.json 的 DB 索引）
  account_settings    ← 每账号配置（automation-settings.json 的 DB 索引）
  account_state       ← 每账号运行态：扫描历史 / 任务统计 / 并行集合
  kv                  ← 杂项小状态（查看指针、自动化优先级）
  scan_index          ← 地图索引 + 断点进度（多进程可写）
  account_run         ← 账号级运行/停止 + 原因（跨进程可见）
  task_run            ← 任务级运行态（可恢复）
  client_state        ← 各模块的显示缓存（关卡/治理/狩猎…）
  audit               ← 关键动作审计（平台层已有，这里补业务事件）
"""

import json
import os
import sqlite3
import threading
import time
import traceback

import cok_platform as PLAT

# ---------------------------------------------------------------- 表结构

# kv 表由 cok_platform.init() 建（它是平台层最早建的表之一）；
# 这里**不重复定义**，否则万一两边定义漂移，同一个 (uid,k) 会长得不一样。
# 业务侧只用 kv_get / kv_set / kv_json / kv_set_json 走它。

SCHEMA = """
-- 每账号的运行态汇总：扫描历史 / 任务统计 / 并行集合。
-- 一个账号一行，key = gameUid（**不带 owner 前缀** —— 账号库里的 key 是纯 gameUid，
-- 归属看 accounts.json 的 owner 字段；这里跟着账号库走，避免两套命名）。
CREATE TABLE IF NOT EXISTS account_state (
    key            TEXT PRIMARY KEY,
    scan_history   TEXT NOT NULL DEFAULT '[]',   -- JSON 数组
    task_stats     TEXT NOT NULL DEFAULT '{}',   -- JSON 对象
    parallel       INTEGER NOT NULL DEFAULT 0,   -- 是否加入并行
    updated_at     REAL NOT NULL DEFAULT 0
);

-- 每账号的配置（automation-settings.json 的 DB 索引）。
-- value 存整份配置的 JSON 文本：配置项有几十个且会随版本增删，
-- 拆成列意味着每加一个开关就要改表；存 JSON 让 schema 保持稳定。
CREATE TABLE IF NOT EXISTS account_settings (
    key            TEXT PRIMARY KEY,
    value          TEXT NOT NULL DEFAULT '{}',
    updated_at     REAL NOT NULL DEFAULT 0
);

-- 地图索引**正文**（players 那份，可能几 MB）+ 断点进度分开存。
-- 为什么拆：扫描时每隔几十秒写一次进度，如果整份 players 一起重写，
-- 每次都要序列化 2~3 MB —— 扫描到一半就能把磁盘写满 IO。
CREATE TABLE IF NOT EXISTS scan_doc (
    owner          TEXT NOT NULL DEFAULT '',
    key            TEXT NOT NULL DEFAULT '',
    doc            TEXT NOT NULL DEFAULT '{}',
    updated_at     REAL NOT NULL DEFAULT 0,
    PRIMARY KEY (owner, key)
);

-- 地图索引的进度/断点（轻量，高频写）。
-- 拆成 (owner, key) 而不是只按 key：同一个 gameUid 理论上不会属于两个用户，
-- 但索引文件历史上是"一个账号一份"，带上 owner 能让平台模式下的路径推导保持唯一。
CREATE TABLE IF NOT EXISTS scan_index (
    owner          TEXT NOT NULL DEFAULT '',
    key            TEXT NOT NULL DEFAULT '',
    progress       INTEGER NOT NULL DEFAULT 0,   -- 已扫请求数（断点）
    scanned        INTEGER NOT NULL DEFAULT 0,   -- 已确认格数
    step           INTEGER NOT NULL DEFAULT 0,
    done           INTEGER NOT NULL DEFAULT 0,
    updated_at     REAL NOT NULL DEFAULT 0,
    PRIMARY KEY (owner, key)
);

-- 账号级运行态：谁在用、从什么时候开始、为什么停。
-- 这是**跨进程**的关键表：网页控制台问"这个号在跑吗"、扫描器问"我能连吗"，
-- 都看这一行，而不是各自的内存字典（那样两个进程会各说各话）。
CREATE TABLE IF NOT EXISTS account_run (
    key            TEXT PRIMARY KEY,
    owner          TEXT NOT NULL DEFAULT '',
    running        INTEGER NOT NULL DEFAULT 0,
    since          REAL NOT NULL DEFAULT 0,
    reason         TEXT NOT NULL DEFAULT '',    -- 停止原因（正常/被顶/异常…）
    pid            INTEGER NOT NULL DEFAULT 0,  -- 持有者进程
    updated_at     REAL NOT NULL DEFAULT 0
);

-- 任务级运行态：task_id -> 账号/任务/参数/进度。
-- 存在这里的意义是"重启后能恢复"：进程挂了，重开后能看到
-- "哪些任务在跑、跑到哪一步"，而不是全部消失。
CREATE TABLE IF NOT EXISTS task_run (
    task_id        TEXT PRIMARY KEY,
    key            TEXT NOT NULL DEFAULT '',
    owner          TEXT NOT NULL DEFAULT '',
    kind           TEXT NOT NULL DEFAULT '',    -- route / debug ...
    label          TEXT NOT NULL DEFAULT '',
    params         TEXT NOT NULL DEFAULT '{}',
    progress       TEXT NOT NULL DEFAULT '{}',
    done           INTEGER NOT NULL DEFAULT 0,
    message        TEXT NOT NULL DEFAULT '',
    started_at     REAL NOT NULL DEFAULT 0,
    updated_at     REAL NOT NULL DEFAULT 0
);

-- 各模块的显示缓存（关卡进度、治理、狩猎、码头…）。
-- Engine.states[key] 现在只活在内存里，重启即空 -> 网页上所有卡片回到"未加载"，
-- 用户以为功能坏了。落这一张表后重启能直接回填。
CREATE TABLE IF NOT EXISTS client_state (
    owner          TEXT NOT NULL DEFAULT '',
    key            TEXT NOT NULL DEFAULT '',
    kind           TEXT NOT NULL DEFAULT '',    -- lake / gov / hunt / dock / sky / show ...
    doc            TEXT NOT NULL DEFAULT '{}',
    updated_at     REAL NOT NULL DEFAULT 0,
    PRIMARY KEY (owner, key, kind)
);

-- 历史流水（automation-history 那种"只追加"的数据）。
-- 按行存而不是整份 JSON：见 archive_add() 的说明。
CREATE TABLE IF NOT EXISTS archive (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    kind           TEXT NOT NULL DEFAULT '',
    owner          TEXT NOT NULL DEFAULT '',
    key            TEXT NOT NULL DEFAULT '',
    doc            TEXT NOT NULL DEFAULT '{}',
    size           INTEGER NOT NULL DEFAULT 0,
    created_at     REAL NOT NULL DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_task_run_key ON task_run(key);
CREATE INDEX IF NOT EXISTS idx_archive_kind ON archive(kind, key, created_at);
CREATE INDEX IF NOT EXISTS idx_client_state ON client_state(owner, key);
CREATE INDEX IF NOT EXISTS idx_account_run_owner ON account_run(owner);
"""


def init():
    """建表（幂等）。平台层的表由 PLAT.init() 建，这里只补业务表。"""
    _ensure()


# ---------------------------------------------------------------- 连接

_LOCK = threading.RLock()
_CONNS = {}
_CONN_PATH = None
_INMEM = False


def _ensure(path=None):
    """确保 SCHEMA 建好 + 平台层的表也在（kv / users / audit）。

    平台层的表归 cok_platform 管，但业务层可能先被 import（比如扫描器只导
    cok_store），所以这里显式补一次 `PLAT.init()` —— 它自己是幂等的。
    """
    if path is None:
        PLAT.init()
    _connect()


def _mem_conn():
    """内存库（测试 / 只读场景用）。

    **连接必须复用**：:memory: 库是"每连接一个库"，每次新建连接就等于换了个空库 ——
    上一个连接写的行在新连接里查不到。所以这里跟文件库一样缓存连接，只是不落盘。
    """
    try:
        PLAT.init()
    except Exception:
        pass
    if "mem" in _CONNS:
        return _CONNS["mem"]
    c = sqlite3.connect(":memory:", timeout=15, check_same_thread=False)
    c.row_factory = sqlite3.Row
    try:
        # 复制平台层的建表语句（内存库里没有 PLAT 自己的连接）
        c.executescript(PLAT.SCHEMA)
    except Exception:
        pass
    c.executescript(SCHEMA)
    _CONNS["mem"] = c
    return c


def _connect():
    global _CONN_PATH, _INMEM
    path = PLAT.db_path()
    with _LOCK:
        if _INMEM:
            return _mem_conn()
        if _CONN_PATH != path or path not in _CONNS:
            try:
                if path != ":memory:":
                    d = os.path.dirname(path)
                    if d and not os.path.isdir(d):
                        os.makedirs(d, exist_ok=True)
                c = sqlite3.connect(path, timeout=15, check_same_thread=False)
                c.row_factory = sqlite3.Row
                c.execute("PRAGMA journal_mode=WAL")
                c.execute("PRAGMA synchronous=NORMAL")
                c.executescript(SCHEMA)
                _CONNS[path] = c
                _CONN_PATH = path
            except sqlite3.OperationalError:
                # 库文件不可建（只读 assets / 权限）时退回内存库：
                # 宁可这一份状态不持久，也别让整个控制台起不来。
                _INMEM = True
                return _mem_conn()
        return _CONNS[path]


def use_memory():
    """切到内存库（测试用；调用后所有读写都不落盘）。"""
    global _INMEM, _CONN_PATH
    with _LOCK:
        _INMEM = True
        _CONN_PATH = None
        for c in list(_CONNS.values()):
            try:
                c.close()
            except Exception:
                pass
        _CONNS.clear()
        _mem_conn()          # 立刻把内存库建出来（表结构就绪）


def use_file():
    global _INMEM, _CONN_PATH
    with _LOCK:
        _INMEM = False
        _CONN_PATH = None


def in_memory():
    return _INMEM


def conn():
    return _connect()


def now():
    return time.time()


def close():
    with _LOCK:
        for c in _CONNS.values():
            try:
                c.close()
            except Exception:
                pass
        _CONNS.clear()
        _CONN_PATH = None


# ---------------------------------------------------------------- 小工具

def _j(obj):
    """序列化；已经是字符串就原样返回（调用方经常传已 dump 好的文本）。"""
    if isinstance(obj, str):
        return obj
    try:
        return json.dumps(obj, ensure_ascii=False, separators=(",", ":"))
    except (TypeError, ValueError):
        return json.dumps(str(obj), ensure_ascii=False)


def _uj(text, default):
    try:
        v = json.loads(text or "")
    except (TypeError, ValueError):
        return default
    return default if v is None else v


def _row(cur):
    return cur.fetchone()


def _safe(fn, fallback=None):
    """跑一条读语句，表还没建（老库刚换上代码）时返回 fallback。

    为什么需要：部署顺序是「先换代码、后跑迁移」，中间那几十秒里
    服务器上的 platform.db 只有 users/kv，业务表还不存在。
    那会儿管理页正好会调 status()，一路抛 no-such-table 会 500。
    """
    try:
        return fn()
    except sqlite3.OperationalError:
        return fallback


def _table_exists(name):
    try:
        r = _row(_connect().execute(
            "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (name,)))
        return r is not None
    except sqlite3.OperationalError:
        return False


def _ensure_tables():
    """确保业务表都在（老库首次升级时按需补建）。"""
    c = _connect()
    try:
        c.executescript(SCHEMA)
        c.commit()
    except sqlite3.OperationalError:
        pass


# ---------------------------------------------------------------- kv（每用户杂项）

def kv_get(owner, k, default=""):
    _ensure_tables()
    c = _connect()
    r = _row(c.execute("SELECT v FROM kv WHERE uid=? AND k=?",
                       (str(owner or ""), str(k))))
    return r["v"] if r else default


def kv_set(owner, k, v):
    _ensure_tables()
    c = _connect()
    c.execute("INSERT INTO kv (uid, k, v) VALUES (?,?,?)"
              " ON CONFLICT(uid, k) DO UPDATE SET v=excluded.v",
              (str(owner or ""), str(k), "" if v is None else str(v)))
    c.commit()


def kv_del(owner, k):
    c = _connect()
    c.execute("DELETE FROM kv WHERE uid=? AND k=?", (str(owner or ""), str(k)))
    c.commit()


def kv_json(owner, k, default=None):
    _ensure_tables()
    return _uj(kv_get(owner, k, ""), default)


def kv_set_json(owner, k, obj):
    kv_set(owner, k, _j(obj))


# ---------------------------------------------------------------- 账号配置

def account_settings_get(key, default=None):
    _ensure_tables()
    c = _connect()
    r = _row(c.execute("SELECT value FROM account_settings WHERE key=?",
                       (str(key or ""),)))
    if not r:
        return default if default is not None else {}
    return _uj(r["value"], {} if default is None else default)


def account_settings_set(key, obj):
    _ensure_tables()
    c = _connect()
    c.execute("INSERT INTO account_settings (key, value, updated_at)"
              " VALUES (?,?,?) ON CONFLICT(key) DO UPDATE SET"
              " value=excluded.value, updated_at=excluded.updated_at",
              (str(key or ""), _j(obj), now()))
    c.commit()


def account_settings_keys():
    _ensure_tables()
    c = _connect()
    return [r["key"] for r in c.execute(
        "SELECT key FROM account_settings ORDER BY key")]


# ---------------------------------------------------------------- 账号运行态

def account_state_get(key, default=None):
    _ensure_tables()
    """取一份账号运行态；没有就返回 default（默认空结构）。"""
    c = _connect()
    r = _row(c.execute("SELECT * FROM account_state WHERE key=?",
                       (str(key or ""),)))
    if not r:
        return default if default is not None else {
            "scan_history": [], "task_stats": {}, "parallel": False}
    return {"scan_history": _uj(r["scan_history"], []),
            "task_stats": _uj(r["task_stats"], {}),
            "parallel": bool(r["parallel"]),
            "updated_at": r["updated_at"]}


def account_state_set(key, scan_history=None, task_stats=None, parallel=None):
    _ensure_tables()
    """局部更新：只改传进来的字段（None = 不动）。

    key 为空 = "还不知道是哪个号"（引擎刚起、账号没解析出来）。这时候写进去
    会留下一条**永远没人读**的垃圾行，还会把别的号的统计带偏 —— 直接跳过。
    """
    k = str(key or "").strip()
    if not k:
        return False
    c = _connect()
    cur = _row(c.execute("SELECT scan_history, task_stats, parallel"
                         " FROM account_state WHERE key=?", (k,)))
    sh = cur["scan_history"] if cur else "[]"
    ts = cur["task_stats"] if cur else "{}"
    par = int(cur["parallel"]) if cur else 0
    if scan_history is not None:
        sh = _j(scan_history)
    if task_stats is not None:
        ts = _j(task_stats)
    if parallel is not None:
        par = 1 if parallel else 0
    c.execute("INSERT INTO account_state (key, scan_history, task_stats,"
              " parallel, updated_at) VALUES (?,?,?,?,?)"
              " ON CONFLICT(key) DO UPDATE SET scan_history=excluded.scan_history,"
              " task_stats=excluded.task_stats, parallel=excluded.parallel,"
              " updated_at=excluded.updated_at",
              (k, sh, ts, par, now()))
    c.commit()
    return True


def account_state_all():
    _ensure_tables()
    c = _connect()
    out = {}
    for r in c.execute("SELECT * FROM account_state"):
        out[r["key"]] = {
            "scan_history": _uj(r["scan_history"], []),
            "task_stats": _uj(r["task_stats"], {}),
            "parallel": bool(r["parallel"]),
            "updated_at": r["updated_at"],
        }
    return out


# ---------------------------------------------------------------- 地图索引

def scan_owner_of(key, default=""):
    """按账号 key 查它归谁（账号库是权威）。

    扫描器（子进程）只拿到 gameUid，不知道 owner；用它把进度挂到正确的人名下。
    """
    try:
        import cok_accounts as _A
        return str(_A.owner_of(str(key or "")) or default)
    except Exception:
        return default


def scan_index_get(owner, key, default=None):
    _ensure_tables()
    """读索引进度 + 正文（正文在 scan_doc 里）。"""
    c = _connect()
    o, k = str(owner or ""), str(key or "")
    r = _row(c.execute("SELECT * FROM scan_index WHERE owner=? AND key=?", (o, k)))
    d = _row(c.execute("SELECT doc, updated_at FROM scan_doc"
                       " WHERE owner=? AND key=?", (o, k)))
    if not r and not d:
        return default
    return {"doc": _uj(d["doc"], {}) if d else {},
            "progress": int(r["progress"]) if r else 0,
            "scanned": int(r["scanned"]) if r else 0,
            "step": int(r["step"]) if r else 0,
            "done": bool(r["done"]) if r else False,
            "updated_at": (d["updated_at"] if d else 0)
            if not r else max(r["updated_at"], d["updated_at"] if d else 0)}


def scan_index_set(owner, key, doc=None, progress=None, scanned=None,
                   step=None, done=None, meta=None):
    _ensure_tables()
    """写索引进度；`doc` 走 scan_doc（正文），其余走 scan_index（轻量）。

    拆表的原因见 scan_doc 的注释：进度是高频写，正文是几 MB，
    混在一张表里每次进度更新都要重写正文。
    """
    k = str(key or "").strip()
    if not k:
        # 没账号就没索引可写（"全局索引"这个概念不存在：索引永远属于某个号）
        return False
    c = _connect()
    o = str(owner or "")
    if doc is not None or meta is not None:
        cur = _row(c.execute("SELECT doc, updated_at FROM scan_doc"
                             " WHERE owner=? AND key=?", (o, k)))
        d = cur["doc"] if cur else "{}"
        if meta is not None:
            try:
                cur_doc = json.loads(d) if d else {}
            except (TypeError, ValueError):
                cur_doc = {}
            if not isinstance(cur_doc, dict):
                cur_doc = {}
            m = dict(cur_doc.get("meta") or {})
            m.update(meta)
            cur_doc["meta"] = m
            d = _j(cur_doc)
        if doc is not None:
            d = _j(doc)
        c.execute("INSERT INTO scan_doc (owner, key, doc, updated_at)"
                  " VALUES (?,?,?,?) ON CONFLICT(owner, key) DO UPDATE SET"
                  " doc=excluded.doc, updated_at=excluded.updated_at",
                  (o, k, d, now()))
    cur = _row(c.execute("SELECT progress, scanned, step, done"
                         " FROM scan_index WHERE owner=? AND key=?", (o, k)))
    pr = int(cur["progress"]) if cur else 0
    sc = int(cur["scanned"]) if cur else 0
    st = int(cur["step"]) if cur else 0
    dn = int(cur["done"]) if cur else 0
    if progress is not None:
        pr = int(progress)
    if scanned is not None:
        sc = int(scanned)
    if step is not None:
        st = int(step)
    if done is not None:
        dn = 1 if done else 0
    c.execute("INSERT INTO scan_index (owner, key, progress, scanned, step,"
              " done, updated_at) VALUES (?,?,?,?,?,?,?)"
              " ON CONFLICT(owner, key) DO UPDATE SET"
              " progress=excluded.progress, scanned=excluded.scanned,"
              " step=excluded.step, done=excluded.done,"
              " updated_at=excluded.updated_at",
              (o, k, pr, sc, st, dn, now()))
    c.commit()


def scan_index_mark_done(owner, key):
    scan_index_set(owner, key, done=1)


def scan_index_list():
    _ensure_tables()
    c = _connect()
    return [{"owner": r["owner"], "key": r["key"], "progress": int(r["progress"]),
             "scanned": int(r["scanned"]), "step": int(r["step"]),
             "done": bool(r["done"]), "updated_at": r["updated_at"]}
            for r in c.execute("SELECT * FROM scan_index ORDER BY updated_at DESC")]


# ---------------------------------------------------------------- 账号运行态（跨进程）

def account_run_get(key):
    _ensure_tables()
    c = _connect()
    r = _row(c.execute("SELECT * FROM account_run WHERE key=?",
                       (str(key or ""),)))
    if not r:
        return {"key": str(key or ""), "owner": "", "running": False,
                "since": 0.0, "reason": "", "pid": 0, "updated_at": 0.0}
    return {"key": r["key"], "owner": r["owner"], "running": bool(r["running"]),
            "since": r["since"], "reason": r["reason"], "pid": int(r["pid"]),
            "updated_at": r["updated_at"]}


def account_run_set(key, running=None, owner=None, reason=None, pid=None):
    _ensure_tables()
    c = _connect()
    k = str(key or "")
    cur = _row(c.execute("SELECT owner, running, since, reason, pid"
                         " FROM account_run WHERE key=?", (k,)))
    ow = cur["owner"] if cur else ""
    rn = int(cur["running"]) if cur else 0
    si = float(cur["since"]) if cur else 0.0
    rs = cur["reason"] if cur else ""
    pd = int(cur["pid"]) if cur else 0
    if owner is not None:
        ow = str(owner)
    if pid is not None:
        pd = int(pid)
    if running is not None:
        rn = 1 if running else 0
        # 从"停"转"跑"时重置起点；从"跑"转"停"时保留起点（方便算跑了多久）
        if running and not cur:
            si = now()
        elif running and cur and not int(cur["running"]):
            si = now()
        if not running and reason is not None:
            rs = str(reason)
    elif reason is not None:
        rs = str(reason)
    c.execute("INSERT INTO account_run (key, owner, running, since, reason, pid,"
              " updated_at) VALUES (?,?,?,?,?,?,?)"
              " ON CONFLICT(key) DO UPDATE SET owner=excluded.owner,"
              " running=excluded.running, since=excluded.since, reason=excluded.reason,"
              " pid=excluded.pid, updated_at=excluded.updated_at",
              (k, ow, rn, si, rs, pd, now()))
    c.commit()


def account_run_list(owner=None):
    _ensure_tables()
    c = _connect()
    sql = "SELECT * FROM account_run"
    args = ()
    if owner is not None:
        sql += " WHERE owner=?"
        args = (str(owner),)
    sql += " ORDER BY updated_at DESC"
    out = []
    for r in c.execute(sql, args):
        out.append({"key": r["key"], "owner": r["owner"],
                    "running": bool(r["running"]), "since": r["since"],
                    "reason": r["reason"], "pid": int(r["pid"]),
                    "updated_at": r["updated_at"]})
    return out


# ---------------------------------------------------------------- 任务运行态

def task_upsert(task_id, **kw):
    _ensure_tables()
    """写/更新一条任务运行态（只更新传进来的字段）。"""
    c = _connect()
    tid = str(task_id or "")
    cols = ("key", "owner", "kind", "label", "params", "progress", "done",
            "message", "started_at", "updated_at")
    cur = _row(c.execute(
        "SELECT %s FROM task_run WHERE task_id=?" % ", ".join(cols), (tid,)))
    vals = {}
    for col in cols:
        vals[col] = cur[col] if cur else None
    if not cur:
        vals.update({"key": "", "owner": "", "kind": "", "label": "",
                     "params": "{}", "progress": "{}", "done": 0,
                     "message": "", "started_at": now()})
    for k, v in kw.items():
        if k in ("params", "progress") and v is not None and not isinstance(v, str):
            v = _j(v)
        if k in vals or k in ("params", "progress"):
            vals[k] = v
    vals["updated_at"] = now()
    c.execute("INSERT INTO task_run (task_id, key, owner, kind, label, params,"
              " progress, done, message, started_at, updated_at)"
              " VALUES (?,?,?,?,?,?,?,?,?,?,?)"
              " ON CONFLICT(task_id) DO UPDATE SET key=excluded.key,"
              " owner=excluded.owner, kind=excluded.kind, label=excluded.label,"
              " params=excluded.params, progress=excluded.progress,"
              " done=excluded.done, message=excluded.message,"
              " updated_at=excluded.updated_at",
              (tid, vals["key"], vals["owner"], vals["kind"], vals["label"],
               vals["params"] or "{}", vals["progress"] or "{}", 
               1 if vals["done"] else 0, vals["message"] or "",
               vals["started_at"] or now(), now()))
    c.commit()


def task_get(task_id):
    _ensure_tables()
    c = _connect()
    r = _row(c.execute("SELECT * FROM task_run WHERE task_id=?",
                       (str(task_id or ""),)))
    if not r:
        return None
    return {"task_id": r["task_id"], "key": r["key"], "owner": r["owner"],
            "kind": r["kind"], "label": r["label"],
            "params": _uj(r["params"], {}), "progress": _uj(r["progress"], {}),
            "done": bool(r["done"]), "message": r["message"],
            "started_at": r["started_at"], "updated_at": r["updated_at"]}


def task_list(key=None, owner=None, running_only=False):
    _ensure_tables()
    c = _connect()
    sql = "SELECT * FROM task_run WHERE 1=1"
    args = []
    if key:
        sql += " AND key=?"
        args.append(str(key))
    if owner is not None:
        sql += " AND owner=?"
        args.append(str(owner))
    sql += " ORDER BY updated_at DESC LIMIT 200"
    out = []
    for r in c.execute(sql, tuple(args)):
        if running_only and r["done"]:
            continue
        out.append({"task_id": r["task_id"], "key": r["key"], "owner": r["owner"],
                    "kind": r["kind"], "label": r["label"],
                    "params": _uj(r["params"], {}), "progress": _uj(r["progress"], {}),
                    "done": bool(r["done"]), "message": r["message"],
                    "started_at": r["started_at"], "updated_at": r["updated_at"]})
    return out


def task_finish(task_id, message="", done=True):
    task_upsert(task_id, done=1 if done else 0, message=str(message or ""))


def task_running_keys(owner=None):
    """还有未完成任务在跑的账号 key（去重）。"""
    return sorted({t["key"] for t in task_list(owner=owner, running_only=True)
                   if t.get("key")})


def task_cleanup(days=7, keep_running=True):
    """清理过期任务记录（默认 7 天）。"""
    c = _connect()
    cut = now() - max(1, int(days)) * 86400
    if keep_running:
        c.execute("DELETE FROM task_run WHERE updated_at < ? AND done=1", (cut,))
    else:
        c.execute("DELETE FROM task_run WHERE updated_at < ?", (cut,))
    c.commit()


# ---------------------------------------------------------------- 模块显示缓存

def client_state_get(owner, key, kind, default=None):
    _ensure_tables()
    c = _connect()
    r = _row(c.execute("SELECT doc FROM client_state WHERE owner=? AND key=? AND kind=?",
                       (str(owner or ""), str(key or ""), str(kind or ""))))
    if not r:
        return default
    return _uj(r["doc"], {} if default is None else default)


def client_state_set(owner, key, kind, doc):
    _ensure_tables()
    c = _connect()
    c.execute("INSERT INTO client_state (owner, key, kind, doc, updated_at)"
              " VALUES (?,?,?,?,?) ON CONFLICT(owner, key, kind) DO UPDATE SET"
              " doc=excluded.doc, updated_at=excluded.updated_at",
              (str(owner or ""), str(key or ""), str(kind or ""), _j(doc), now()))
    c.commit()


def client_state_list(owner, key):
    _ensure_tables()
    c = _connect()
    out = {}
    for r in c.execute("SELECT kind, doc, updated_at FROM client_state"
                       " WHERE owner=? AND key=?",
                       (str(owner or ""), str(key or ""))):
        out[r["kind"]] = _uj(r["doc"], {})
    return out


def client_state_drop(owner, key, kind=None):
    c = _connect()
    if kind:
        c.execute("DELETE FROM client_state WHERE owner=? AND key=? AND kind=?",
                  (str(owner or ""), str(key or ""), str(kind)))
    else:
        c.execute("DELETE FROM client_state WHERE owner=? AND key=?",
                  (str(owner or ""), str(key or "")))
    c.commit()


# ---------------------------------------------------------------- 业务审计

def audit(uid, action, target="", ok=True, detail="", ip=""):
    """业务事件审计（平台层的 audit 表，这里只做转发 + 失败不抛）。"""
    try:
        PLAT.audit(uid, action=action, target=target, ok=ok, detail=detail, ip=ip)
        return True
    except Exception:
        try:
            print("[store] 审计写入失败: %s" % traceback.format_exc())
        except Exception:
            pass
        return False


# ---------------------------------------------------------------- 迁移

def import_files(data_root=None, accounts_dir=None, log=None):
    """把现有 JSON 文件导进库（幂等：重复跑只会刷新时间戳）。

    返回统计字典。扫描器/安卓端读的是文件，所以**这里只读不删** ——
    文件仍然是快照，等运行态全部走 DB 之后再考虑下线。
    """
    import cok_accounts as ACCS

    root = data_root or ACCS.DATA_ROOT
    adir = accounts_dir or ACCS.ACCOUNTS_DIR
    out = {"users": 0, "user_settings": 0, "account_settings": 0,
           "account_state": 0, "kv": 0, "scan_index": 0}

    def say(msg):
        if log:
            log(msg)
        else:
            print(msg)

    # 1) 每个账号的 owner 在 users 表里补一行（没有口令，纯归属）
    try:
        for a in ACCS.list_accounts():
            uid = str(a.get("owner") or "").strip()
            if not uid:
                continue
            row = PLAT.user_get_by_uid(uid)
            if row:
                continue
            # 无口令用户：pwd/salt 留空，纯做"归属登记"（账号库里的 owner
            # 必须在 users 里有行，否则跨用户隔离和审计都会指向一个不存在的用户）
            PLAT.user_upsert(uid, uid, pwd="", salt="", role="user")
            out["users"] += 1
            say("  users: 补 %s" % uid)
    except Exception:
        say("  users 导入失败: %s" % traceback.format_exc())

    # 2) 每用户配置：data/u/<owner>/web-settings.json -> user_settings
    #    ⚠️ 遍历用**账号库里的 owner**（u-1 / local-admin / ...），不是 `u/` 下的目录名 ——
    #    目录名会被 safe_key() 改写（大写变小写等），直接用它会写到一个"看起来对
    #    但永远查不到"的 owner 上。
    owners = []
    for a in _safe_accounts(ACCS):
        o = str(a.get("owner") or "").strip()
        if o and o not in owners:
            owners.append(o)
    udir = os.path.join(root, "u")
    if os.path.isdir(udir) and not owners:
        # 账号库里没有 owner（老格式 / 没导入过账号）时退回按目录名扫
        owners = [n for n in sorted(os.listdir(udir))
                  if os.path.isdir(os.path.join(udir, n))]
    for name in owners:
        if True:
            p = _user_settings_path(name, root)
            if not p or not os.path.isfile(p):
                continue
            try:
                with open(p, "r", encoding="utf-8") as f:
                    doc = json.load(f)
            except (OSError, ValueError):
                continue
            settings_set("owner:%s" % name, doc)
            out["user_settings"] += 1
            say("  user_settings: %s (%d 项)" % (name, len(doc or {})))

    # 3) 全局默认配置 -> 兜底用户 ""（单用户模式用）
    p = os.path.join(root, "web-settings.json")
    if os.path.isfile(p):
        try:
            with open(p, "r", encoding="utf-8") as f:
                doc = json.load(f)
            settings_set("owner:", doc)
            out["user_settings"] += 1
            say("  user_settings: (全局默认) %d 项" % len(doc or {}))
        except (OSError, ValueError):
            pass

    # 4) 每账号：配置 / 扫描历史 / 任务统计 / 并行标记 / 地图索引
    for a in _safe_accounts(ACCS):
        key = a.get("key")
        if not key:
            continue
        d = ACCS.data_dir(key)
        cfg = os.path.join(d, "automation-settings.json")
        if os.path.isfile(cfg):
            try:
                with open(cfg, "r", encoding="utf-8") as f:
                    doc = json.load(f)
                account_settings_set(key, doc)
                out["account_settings"] += 1
                say("  account_settings: %s" % key)
            except (OSError, ValueError):
                pass
        st = {}
        sh = os.path.join(d, "scan-history.json")
        if os.path.isfile(sh):
            try:
                with open(sh, "r", encoding="utf-8") as f:
                    hist = json.load(f)
                # 文件是 {"runs":[...]}（load_history 的格式）。
                # 直接存整份会让库里那一列变成 `{"runs":[...]}`，而读取侧
                # (`Engine._scan_history`) 期待的是**数组** —— 于是"看着导进去了、
                # 页面上却是 0 条"。这里必须拆出 runs。
                if isinstance(hist, dict):
                    hist = hist.get("runs") or []
                if isinstance(hist, list):
                    st["scan_history"] = hist
            except (OSError, ValueError):
                pass
        ts = os.path.join(d, "task-stats.json")
        if os.path.isfile(ts):
            try:
                with open(ts, "r", encoding="utf-8") as f:
                    st["task_stats"] = json.load(f)
            except (OSError, ValueError):
                pass
        if st:
            account_state_set(key, **st)
            out["account_state"] += 1
            say("  account_state: %s" % key)
        idx = os.path.join(d, "map-index.json")
        if os.path.isfile(idx):
            try:
                with open(idx, "r", encoding="utf-8") as f:
                    doc = json.load(f)
                scanned = len(doc.get("players") or doc.get("points") or []) \
                    if isinstance(doc, dict) else 0
                scan_index_set(str(a.get("owner") or ""), key, doc=doc,
                               scanned=scanned, step=int(doc.get("step") or 0)
                               if isinstance(doc, dict) else 0,
                               done=1 if isinstance(doc, dict)
                               and doc.get("done") else 0)
                out["scan_index"] += 1
                say("  scan_index: %s (%d 条)" % (key, scanned))
            except (OSError, ValueError):
                pass

    # 4.5) 清掉"没有归属"的孤儿行：早期版本/扫描器在账号未解析时会写一条空 key 行，
    #      它永远没人读，还会让统计数字看着比实际多。
    dropped = 0
    try:
        c = _connect()
        dropped += c.execute("DELETE FROM scan_index WHERE key=''").rowcount
        dropped += c.execute("DELETE FROM scan_doc WHERE key=''").rowcount
        dropped += c.execute("DELETE FROM account_state WHERE key=''").rowcount
        dropped += c.execute("DELETE FROM client_state WHERE key=''").rowcount
        # 老版本把 `.parallel` 按逗号硬拆，拆出来的 key 长得像
        # `["136063574002223"` —— 这行永远没人读，纯属垃圾。
        # 用 char(34) 表示双引号，省得在 SQL 字符串里转义引号。
        dropped += c.execute(
            "DELETE FROM account_state WHERE key LIKE '[%'"
            " OR key LIKE '%' || char(34) || '%'"
            " OR key LIKE '%]'").rowcount
        if dropped:
            c.commit()
    except Exception:
        pass

    # 5) 并行集合：accounts/.parallel（单行文本，逗号分隔）→ 每行 account_state
    par = os.path.join(adir, ".parallel")
    if os.path.isfile(par):
        try:
            with open(par, "r", encoding="utf-8") as f:
                raw = f.read() or ""
            # 文件有两种格式：单行 "a,b,c"，或每行一个号的 JSON 数组
            # ("["a","b"]" 那种排版)。直接按逗号 split 会把 JSON 拆成
            # '["136063574002223"' 和 '"44056610002223"]' 这种垃圾 key，
            # 写进 account_state 后就是两条**永远没人读**的孤儿行。
            keys = _parallel_keys(raw)
            if keys:
                for k in keys:
                    account_state_set(k, parallel=True)
                    out["kv"] += 1
                say("  parallel: %s" % ",".join(keys))
            else:
                say("  parallel: (空)")
        except OSError:
            pass

    if dropped:
        say("  清理孤儿行: %d 条" % dropped)
    out["dropped"] = dropped
    return out


def _parallel_keys(raw):
    """把 accounts/.parallel 的内容解析成账号 key 列表。

    兼容两种历史写法：
      * 单行 `"a,b,c"`（老版，直接 split 逗号）
      * JSON 数组 `["a", "b"]`（新版，每号一行更好 diff）
    """
    txt = (raw or "").strip()
    if not txt:
        return []
    if txt[0] in "[{\"":
        try:
            got = json.loads(txt)
        except (TypeError, ValueError):
            got = None
        if isinstance(got, list):
            return [str(x).strip() for x in got if str(x).strip()]
        if isinstance(got, dict):
            return [str(k).strip() for k in got.keys() if str(k).strip()]
    out, seen = [], set()
    for x in txt.replace("\n", ",").split(","):
        k = x.strip()
        if k and k not in seen:
            seen.add(k)
            out.append(k)
    return out


def _user_settings_path(owner, root=None):
    """每用户配置文件的路径。

    ⚠️ 必须和 `Engine._settings_file()` **算法一致**（那边是
    `os.path.join(DATA_ROOT,"u",safe_key(owner),"web-settings.json")`）——
    两边不一致就会出现"写进去查不到"。
    """
    import cok_accounts as _A
    base = root or _A.DATA_ROOT
    return os.path.join(base, "u", _A.safe_key(str(owner or "")), "web-settings.json")


def _safe_accounts(ACCS):
    try:
        return ACCS.list_accounts()
    except Exception:
        return []


def _user_settings_put(owner, doc):
    """写每用户配置（走 kv 表，键固定 `settings`）。"""
    kv_set_json(str(owner or ""), "settings", doc or {})


def settings_get(key, default=None):
    """读一份配置（key 由调用方决定：`owner:<uid>` / `acct:<gameUid>`）。

    为什么不让调用方自己拼前缀：拼错就永远读不到自己写的那份，
    而这类 bug 的表现是"改了开关没生效"，极难查。
    """
    got = kv_json(str(key or ""), "settings", None)
    if isinstance(got, dict) and got:
        return got
    return {} if default is None else default


def settings_set(key, doc):
    kv_set_json(str(key or ""), "settings", doc or {})


def user_settings_get(owner, default=None):
    return settings_get("owner:%s" % str(owner or ""), default)


def user_settings_put(owner, doc):
    settings_set("owner:%s" % str(owner or ""), doc)


def account_settings_db_get(key, default=None):
    return settings_get("acct:%s" % str(key or ""), default)


def account_settings_db_set(key, doc):
    settings_set("acct:%s" % str(key or ""), doc)


# ---------------------------------------------------------------- 自检

def status():
    """入库概览（管理页用）。

    关键是**每一项都要给出"库里 vs 文件里"两个数**：
    只有库的数没法判断"迁移是不是漏了"（文件还在，看着像没变）。
    """
    import cok_accounts as _A

    out = {"memory": _INMEM, "path": _CONN_PATH or "", "tables": {}, "files": {}}
    c = _connect()
    for t in ("kv", "account_state", "account_settings", "scan_index",
              "scan_doc", "account_run", "task_run", "client_state", "archive"):
        try:
            out["tables"][t] = int(_row(c.execute(
                "SELECT COUNT(*) n FROM %s" % t))["n"])
        except sqlite3.Error:
            out["tables"][t] = -1
    # 文件那侧（存在但还没进库的，才是"待迁移"）
    def n_json(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                d = json.load(f)
            return len(d) if isinstance(d, (list, dict)) else 0
        except (OSError, ValueError):
            return -1

    # 名字 -> 累加。平台模式下配置有两处：DATA_ROOT 根下那份（单用户/全局默认）
    # 和 `u/<owner>/web-settings.json`（每用户）。只看根目录会让页面上永远显示
    # "0 项"，看着像没迁 —— 所以把该看的地方都加进来。
    files = {"web-settings": 0, "task-stats": 0, "automation-history": 0}

    def add(path, name):
        n = n_json(path)
        if n > 0:
            files[name] += n

    add(os.path.join(_A.DATA_ROOT, "web-settings.json"), "web-settings")
    add(os.path.join(_A.DATA_ROOT, "task-stats.json"), "task-stats")
    add(os.path.join(_A.DATA_ROOT, "automation-history.json"),
        "automation-history")
    # 每用户的配置目录（引擎的 `_settings_file()` 同款路径）
    udir = os.path.join(_A.DATA_ROOT, "u")
    if os.path.isdir(udir):
        for name in sorted(os.listdir(udir)):
            add(os.path.join(udir, name, "web-settings.json"), "web-settings")
    # 每个账号自己的数据目录（`_data_dir()` = DATA_ROOT/<account_key>）
    for a in _safe_accounts(_A):
        k = a.get("key") or ""
        if not k:
            continue
        d = os.path.join(_A.DATA_ROOT, k)
        add(os.path.join(d, "task-stats.json"), "task-stats")
        add(os.path.join(d, "automation-history.json"), "automation-history")
    out["files"].update(files)
    out["files"]["accounts"] = len(_safe_accounts(_A))
    return out


def stats():
    c = _connect()
    out = {"memory": _INMEM, "path": _CONN_PATH}
    for t in ("kv", "account_state", "account_settings", "scan_index",
              "account_run", "task_run", "client_state"):
        try:
            out[t] = int(_row(c.execute("SELECT COUNT(*) n FROM %s" % t))["n"])
        except sqlite3.Error:
            out[t] = -1
    return out

# ---------------------------------------------------------------- 归档（历史 / 统计）

def archive_add(kind, key, owner, doc, size=0):
    _ensure_tables()
    """追加一条归档记录（automation-history 之类的流水）。

    **按行存**，不像别的表整份 JSON 塞一列：历史是"只追加、偶尔查最近 N 条"，
    整份存会让每次写入都要重写全部历史（现在有 58KB，一年就是几十 MB）。
    """
    if not str(key or "").strip():
        # 没有账号归属的流水没有价值（谁也不会去查它）
        return None
    c = _connect()
    cur = c.execute("INSERT INTO archive (kind, owner, key, doc, size, created_at)"
                    " VALUES (?,?,?,?,?,?)",
                    (str(kind or ""), str(owner or ""), str(key or ""),
                     _j(doc), int(size or 0), now()))
    c.commit()
    return cur.lastrowid


def archive_list(kind=None, key=None, owner=None, limit=200):
    _ensure_tables()
    c = _connect()
    sql = "SELECT * FROM archive WHERE 1=1"
    args = []
    if kind:
        sql += " AND kind=?"
        args.append(str(kind))
    if key:
        sql += " AND key=?"
        args.append(str(key))
    if owner is not None:
        sql += " AND owner=?"
        args.append(str(owner))
    sql += " ORDER BY created_at DESC LIMIT ?"
    args.append(max(1, int(limit)))
    out = []
    for r in c.execute(sql, tuple(args)):
        out.append({"id": r["id"], "kind": r["kind"], "owner": r["owner"],
                    "key": r["key"], "doc": _uj(r["doc"], {}),
                    "size": int(r["size"]), "created_at": r["created_at"]})
    return out


def archive_count(kind=None):
    c = _connect()
    if kind:
        r = _row(c.execute("SELECT COUNT(*) n FROM archive WHERE kind=?",
                           (str(kind),)))
    else:
        r = _row(c.execute("SELECT COUNT(*) n FROM archive"))
    return int(r["n"])


def archive_cleanup(keep=5000):
    """只保留最近 keep 条（历史不能无限涨）。"""
    c = _connect()
    n = archive_count()
    if n <= keep:
        return 0
    cut = n - keep
    c.execute("DELETE FROM archive WHERE id IN"
              " (SELECT id FROM archive ORDER BY created_at ASC LIMIT ?)", (cut,))
    c.commit()
    return cut
