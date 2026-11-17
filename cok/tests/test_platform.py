#!/usr/bin/env python3
"""多用户平台层回归测试 —— 不联网, 起一个真的 HTTP 服务用 curl 打。

覆盖(每一条都对应一个真实的坑):
  A. 登录/会话      : 密码对才发 Cookie; Cookie 失效后 API 403
  B. 首用户=管理员  : 第一个注册的人免邀请码且是 admin
  C. 邀请制         : 没邀请码注册不了; 用过一次的邀请码不能重复用
  D. 账号隔离       : 甲看不到乙的账号; 越权传 key 等于"不存在"
  E. 越权改配置     : A 的设置不会写进 B 的目录
  F. 限流           : 连续登录失败到上限后返回 429
  G. 封禁           : banned 用户立刻登录不上, 已有会话也失效
  H. 审计           : 登录/注册/删号都留痕, admin 可查

跑法: python3 cok/tests/test_platform.py
"""
import json
import os
import shutil
import sys
import tempfile
import threading
import time
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "core"))
sys.path.insert(0, os.path.join(HERE, "..", "tools"))

_TMP = tempfile.mkdtemp(prefix="cok-platform-test-")
os.environ["COK_DATA_ROOT"] = os.path.join(_TMP, "data")
os.environ["COK_ACCOUNTS_DIR"] = os.path.join(_TMP, "data", "accounts")
os.environ["COK_PLATFORM_DB"] = os.path.join(_TMP, "data", "platform.db")
os.environ.pop("COK_ACCOUNT_LOCK_FILE", None)

import cok_accounts as accounts      # noqa: E402
import cok_platform as platform      # noqa: E402
import cok_users                     # noqa: E402
import cok_web                       # noqa: E402

PASS = 0
FAIL = 0


def check(cond, name, extra=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print("[PASS] %s%s" % (name, ("  — " + extra) if extra else ""))
    else:
        FAIL += 1
        print("[FAIL] %s%s" % (name, ("  — " + extra) if extra else ""))


# ---------------------------------------------------------------- HTTP 小客户端
class Client(object):
    """带 Cookie 的最小 HTTP 客户端(不引第三方库)。"""

    def __init__(self, base):
        self.base = base
        self.cookie = ""

    def req(self, path, body=None, method=None):
        url = self.base + path
        data = None
        headers = {}
        if body is not None:
            data = json.dumps(body).encode("utf-8")
            headers["Content-Type"] = "application/json"
        if self.cookie:
            headers["Cookie"] = self.cookie
        req = urllib.request.Request(url, data=data, headers=headers,
                                     method=method or ("POST" if body is not None else "GET"))
        try:
            with urllib.request.urlopen(req, timeout=15) as r:
                raw = r.read()
                sc = r.headers.get("Set-Cookie") or ""
                if sc.startswith("cok_sid="):
                    self.cookie = "cok_sid=" + sc.split(";", 1)[0].split("=", 1)[1]
                return r.status, self._json(raw)
        except urllib.error.HTTPError as e:
            return e.code, self._json(e.read())

    @staticmethod
    def _json(raw):
        try:
            return json.loads(raw.decode("utf-8"))
        except Exception:  # noqa: BLE001
            return {"_raw": raw[:120].decode("utf-8", "replace")}


def _get_raw(base, path):
    """不解析 JSON、不跟随重定向: 返回 (status, body_bytes)。

    端口是 `_run(base)` 才知道的, 所以 base 从调用方传进来 —— 早先写成读
    模块级 PORT 会直接 NameError(而它是 main() 的局部变量)。
    """
    req = urllib.request.Request(base + path, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()

class FakeEngine(object):
    """不联网的假引擎: 只满足平台层需要的最小接口。"""

    def __init__(self, args, pinned_key=None, owner=""):
        self.args = args
        self.pinned_key = pinned_key
        self.owner = str(owner or "")
        self.running = False
        self.settings = {}
        self.parallel = set()

    def start(self):
        self.running = True

    def stop(self):
        self.running = False

    def snapshot(self):
        return {"connected": False, "online": False, "owner": self.owner}

    def accounts_summary(self):
        return []

    def set_setting(self, key, value):
        """平台层把它当引擎方法来调; 用 dict 存, 好让测试断言落点。"""
        self.settings[key] = value
        return True

    def action(self, body):
        act = (body or {}).get("action")
        if act == "account-switch":
            key = (body or {}).get("key")
            if key in ("900000000001", "900000000002"):
                self.account_key = key
                return {"ok": True, "key": key}
            return {"ok": False, "error": "账号库里没有这个账号: %s" % key}
        if act == "account-remove":
            return {"ok": True, "removed": (body or {}).get("key")}
        if act == "set-setting":
            self.set_setting((body or {}).get("key"), (body or {}).get("value"))
            return {"ok": True}
        return {"ok": True, "action": act}


def _free_port():
    import socket
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


def _seed_accounts():
    """两个用户各一个账号(账号 owner 是 **uid**, 不是用户名)。

    这一步踩过的坑: 一开始写成 owner="alice", 而平台层的 owner 是
    `u-xxxxxxxx` 形式的 uid —— 于是"按 uid 过滤"一个也匹配不上,
    页面账号列表永远是空的。owner 必须是 uid, 名字只是给人看的。
    """
    full = {"pfId": "x", "platformToken": "x", "deviceId": "x", "uuid": "x",
            "buildCode": "x", "signCode": "x"}
    accounts.save_account(dict(full, gameUid="900000000001", roleName="甲的大号"),
                          label="甲的大号", owner=_uid("alice"))
    accounts.save_account(dict(full, gameUid="900000000002", roleName="乙的小号"),
                          label="乙的小号", owner=_uid("bob"))


def _uid(username):
    row = platform.user_get(username)
    return row["uid"] if row else ""



# ---------------------------------------------------------------- 迁移(P2)
def _test_migrate():
    """旧 JSON 用户/会话 -> SQLite, 以及存量账号认领。

    这里用**函数级临时目录**: 迁移函数直接读 ``cok_users.USERS_FILE``(模块
    级常量, 在 import 时就定了), 换目录只能重新 import —— 太绕。所以直接
    把真文件写进当前 ACCOUNTS_DIR, 测完再删。踩过的坑: 之前试图靠环境变量
    重定向, 结果迁移读到的还是真目录(0 个用户), 白折腾。
    """
    import subprocess
    root = accounts.ACCOUNTS_DIR
    os.makedirs(root, exist_ok=True)
    users_file = os.path.join(root, "users.json")
    sess_file = os.path.join(root, "sessions.json")
    # 别覆盖用户自己的真数据
    if os.path.exists(users_file):
        check(True, "跳过迁移测试(账号目录已有 users.json, 不动它)")
        return

    rec = {"pwd": "aa" * 32, "salt": "11" * 16, "role": "admin",
           "created": "2026-09-01T10:00:00"}
    with open(users_file, "w", encoding="utf-8") as fh:
        json.dump({"migboss": rec, "migfriend": dict(rec, role="user")}, fh)
    with open(sess_file, "w", encoding="utf-8") as fh:
        json.dump({"oldsid1": {"user": "migboss", "exp": time.time() + 3600,
                               "created": time.time()}}, fh)
    full = {"pfId": "x", "platformToken": "x", "deviceId": "x", "uuid": "x",
            "buildCode": "x", "signCode": "x"}
    k1 = accounts.save_account(dict(full, gameUid="700000000001"), label="老号一")
    k2 = accounts.save_account(dict(full, gameUid="700000000002"), label="老号二")
    try:
        st = cok_web._migrate_users()
        check(st["users"] == 2, "迁移出 2 个用户", str(st))
        row = platform.user_get("migboss")
        check(bool(row) and row["role"] == "admin", "迁移保留了角色")
        check(row and row["uid"] == "u-migboss", "老用户没有 uid -> 用 u-<名字>",
              row and row["uid"])
        check(bool(platform.session_user("oldsid1")), "旧会话能用(按 sha256 存)",
              platform.session_user("oldsid1"))
        check(os.path.exists(users_file + ".migrated"), "旧 users.json 改名留档")

        # ⚠ 第二次读**不到** users.json 了(第一次迁移已把它改名成 .migrated) ——
        # 这正是迁移该有的效果: 旧文件不在, 自然不会重复导。
        # 真正要验证的幂等是"文件还在时再跑", 所以这里把文件恢复回来。
        shutil.copyfile(users_file + ".migrated", users_file)
        st2 = cok_web._migrate_users()
        check(st2["users"] == 0 and st2["skipped"] == 2,
              "迁移是幂等的(用户已在库里 -> 跳过, 不覆盖)", str(st2))
        os.remove(users_file)

        st3 = cok_web._migrate_accounts("migboss")
        check(st3["claimed"] == 2, "无主账号被认领", str(st3))
        got = sorted(a["key"] for a in accounts.list_accounts(
            owner=platform.user_get("migboss")["uid"]))
        check(got == sorted([k1, k2]), "认领后按 owner 能查到", str(got))
        st4 = cok_web._migrate_accounts("migfriend")
        check(st4["claimed"] == 0, "认领不抢已归属的号", str(st4))
        st5 = cok_web._migrate_accounts("不存在的人")
        check(st5["claimed"] == 0, "指定不存在的人 -> 不瞎认领", str(st5))
    finally:
        for p in (users_file, sess_file, users_file + ".migrated",
                  sess_file + ".migrated", os.path.join(root, k1 + ".json"),
                  os.path.join(root, k2 + ".json")):
            try:
                os.remove(p)
            except OSError:
                pass
        # 平台库里这几个用户也要清掉, 否则影响后面的统计断言
        for name in ("migboss", "migfriend"):
            try:
                platform.user_delete(name)
            except Exception:  # noqa: BLE001
                pass


class _NullLockForTest(object):
    """给 _Mgr 用的空锁(支持 with)。"""

    def __enter__(self):
        return self

    def __exit__(self, *_a):
        return False


class _FakeHandler(object):
    """`_admin_accounts_snapshot()` 只要 `._query()` 和 `.platform`。"""

    def __init__(self, plat, query=None):
        self.platform = plat
        self._q = query or {}

    def _query(self):
        return self._q


# ---------------------------------------------------------------- 主流程
def main():
    platform.init()
    _test_migrate()

    PORT = _free_port()
    srv = cok_web.ThreadingHTTPServer(("127.0.0.1", PORT), cok_web.Handler)

    class Args(object):
        host = "127.0.0.1"
        port = PORT
        account_device = False
        account = None
        interval = 300
        timeout = 5.0
        webhook = None
        webhook_type = "generic"
        persistent = False
        autoshield = False
        web_port = 0
        token_file = ""

    args = Args()
    # 注入假引擎: 不联网也能验证"隔离/越权/限流"这些平台语义
    cok_web.EngineManager._make_engine = (
        lambda self, p: FakeEngine(self.args, p, owner=self.owner))
    cok_web.EngineManager._load_priorities = lambda self: {}
    cok_web.EngineManager._save_priorities = lambda self: None
    cok_web.Handler.token = "test-token"
    cok_web.Handler.platform = cok_web.PlatformManager(args)
    # 别在 serve 之前抢建引擎(那会拉真引擎); _manager() 按需创建即可
    cok_web.Handler.engine = None
    cok_web.Handler.manager = None

    t = threading.Thread(target=srv.serve_forever, daemon=True)
    t.start()
    base = "http://127.0.0.1:%d" % PORT
    try:
        _run(base)
    finally:
        try:
            cok_web.Handler.platform.stop_all()
        except Exception:  # noqa: BLE001
            pass
        srv.shutdown()
        srv.server_close()
        platform.close()

    print("\n%d 通过, %d 失败" % (PASS, FAIL))
    shutil.rmtree(_TMP, ignore_errors=True)
    return 0 if FAIL == 0 else 1


def _run(base):
    # ---- A. 首用户 = 管理员, 免邀请码 ----
    c = Client(base)
    st, j = c.req("/api/register", {"username": "alice", "password": "pw-alice-1"})
    check(st == 200 and j.get("ok"), "首个注册用户直接成功(免邀请码)", str(j)[:120])
    me = platform.user_get("alice")
    check(bool(me) and me.get("role") == "admin", "首个用户是管理员",
          str(me and me.get("role")))
    check(bool(c.cookie), "注册后直接下发会话 Cookie", c.cookie[:24] + "...")
    _seed_accounts()          # 有了 alice 才有 uid 可用

    # ---- B. 会话有效 ----
    st, j = c.req("/api/me")
    check(st == 200 and j.get("user") == "alice", "/api/me 返回当前用户", str(j)[:120])
    check(j.get("platform") is True, "/api/me 标注平台模式")

    # ---- C. 隔离: alice 只看得到自己的号 ----
    st, j = c.req("/api/state")
    # accounts_overview 直接返回 list, 不是 {"list": [...]}
    _a = j.get("accounts") or []
    lst = [a["key"] for a in (_a.get("list") if isinstance(_a, dict) else _a)]
    check(st == 200 and lst == ["900000000001"],
          "alice 只看到自己名下的账号", str(lst))

    # ---- D. 越权: 直接传 bob 的 key ----
    st, j = c.req("/api/action", {"action": "account-switch",
                                  "key": "900000000002"})
    check(st == 200 and not j.get("ok"), "切到别人的号被拒绝",
          str(j.get("error"))[:80])
    st, j = c.req("/api/action", {"action": "account-remove",
                                  "key": "900000000002"})
    check(st == 200 and not j.get("ok"), "删别人的号被拒绝", str(j.get("error"))[:80])
    check(accounts.get_account("900000000002") is not None,
          "bob 的号确实还在(没被删掉)")

    # ---- E. bob 注册(用邀请码) ----
    code = platform.invite_new("alice", note="给 bob")
    check(bool(code), "管理员生成邀请码", code)
    c2 = Client(base)
    st, j = c2.req("/api/register", {"username": "bob", "password": "pw-bob-12",
                                     "invite": code})
    check(st == 200 and j.get("ok"), "持邀请码注册成功", str(j)[:120])
    check(platform.user_get("bob").get("role") == "user", "第二个用户是普通用户")
    # bob 是在 seed 之后才注册的, 当时那个 900000000002 的 owner 是空字符串
    # ⇒ 注册后**认领**无主账号(真实部署里就是这样: 谁导入谁拥有)
    accounts.save_account({"gameUid": "900000000002"}, label="乙的小号",
                          owner=platform.user_get("bob")["uid"])
    st, j = c2.req("/api/register", {"username": "carol", "password": "pw-carol",
                                     "invite": code})
    check(st == 403 and not j.get("ok"), "同一邀请码不能重复使用",
          str(j.get("error"))[:80])
    st, j = c2.req("/api/register", {"username": "carol", "password": "pw-carol"})
    check(st == 400 and not j.get("ok"), "没有邀请码注册被拒",
          str(j.get("error"))[:80])
    st, j = c2.req("/api/register", {"username": "carol", "password": "pw-carol",
                                     "invite": "COK-000000"})
    check(st == 403 and not j.get("ok"), "不存在的邀请码被拒",
          str(j.get("error"))[:80])

    # ---- F. bob 看不到 alice 的号 ----
    st, j = c2.req("/api/state")
    _a2 = j.get("accounts") or []
    lst2 = [a["key"] for a in (_a2.get("list") if isinstance(_a2, dict) else _a2)]
    check(st == 200 and lst2 == ["900000000002"],
          "bob 只看到自己名下的账号", str(lst2))

    # ---- G. 未登录 ----
    anon = Client(base)
    st, j = anon.req("/api/me")
    check(st == 403, "未登录访问 /api/me 被拒", str(st))
    st, j = anon.req("/api/state")
    check(st == 403, "未登录访问 /api/state 被拒", str(st))
    st, j = anon.req("/api/action", {"action": "account-remove",
                                     "key": "900000000001"})
    check(st == 403, "未登录不能执行写操作", str(st))
    # 未登录访问首页: 后端直接回登录页 HTML(浏览器地址栏就能登)
    try:
        with urllib.request.urlopen(base + "/", timeout=10) as r:
            html = r.read().decode("utf-8", "replace")
            code_ = r.status
    except urllib.error.HTTPError as e:
        html, code_ = e.read().decode("utf-8", "replace"), e.code
    check(code_ == 200 and "登录控制台" in html, "未登录访问 / 得到登录页",
          "status=%s" % code_)

    # ---- H. 错密码 ----
    st, j = Client(base).req("/api/login", {"username": "alice",
                                            "password": "wrong-one"})
    check(st == 401 and not j.get("ok"), "密码错误登录被拒", str(st))

    # ---- I. 审计 ----
    rows = platform.recent_audit(limit=50)
    acts = [r["action"] for r in rows]
    check("login" in acts and "register" in acts, "审计里有 login/register", str(acts))
    admin_rows = Client(base)
    st, j = admin_rows.req("/api/login", {"username": "alice",
                                          "password": "pw-alice-1"})
    st, j = admin_rows.req("/api/audit?limit=50")
    check(st == 200 and j.get("ok") and j.get("rows"), "管理员可查审计",
          "%d 行" % len(j.get("rows") or []))
    st, j = c2.req("/api/audit?limit=5")
    check(st == 403, "普通用户查审计被拒", str(st))

    # ---- J. 设置按用户分开(越权写不到别人目录) ----
    st, j = admin_rows.req("/api/action", {"action": "set-setting",
                                           "key": "autoSign", "value": True})
    check(st == 200, "设置写入成功", str(j)[:100])
    ma = cok_web.Handler.platform.get(platform.user_get("alice")["uid"])
    ea = ma.view_engine()
    check(getattr(ea, "owner", "") == platform.user_get("alice")["uid"]
          and ea.settings.get("autoSign") is True,
          "设置写进 alice 自己的引擎实例(隔离)",
          "owner=%s" % getattr(ea, "owner", "?"))

    # ---- K. 每个用户有独立 EngineManager ----
    pa = cok_web.Handler.platform.get(platform.user_get("alice")["uid"])
    pb = cok_web.Handler.platform.get(platform.user_get("bob")["uid"])
    check(pa is not None and pb is not None and pa is not pb,
          "每个用户一个 EngineManager 实例")
    pa.parallel.add("900000000001")
    check("900000000001" in pa.parallel and "900000000001" not in pb.parallel,
          "A 开后台运行不影响 B 的并行集", "%s vs %s" % (sorted(pa.parallel),
                                                     sorted(pb.parallel)))
    pa._state_path(".parallel")

    # ---- L. 会话过期/失效 ----
    sid = platform.new_sid()
    platform.session_save(sid, platform.user_get("bob")["uid"], ttl=-1)
    check(platform.session_user(sid) == "", "过期会话立刻失效")

    # ---- M. 封禁 ----
    platform.user_set_banned("bob", True)
    st, j = Client(base).req("/api/login", {"username": "bob",
                                            "password": "pw-bob-12"})
    check(st == 403 and not j.get("ok"), "被封禁的用户登录被拒", str(j.get("error")))
    st, j = c2.req("/api/me")
    check(st == 403, "封禁后已有会话立即失效", str(st))
    platform.user_set_banned("bob", False)

    # ---- 改密码(要用已登录的会话) ----
    pw_cli = Client(base)
    pw_cli.req("/api/login", {"username": "alice", "password": "pw-alice-1"})
    st, j = pw_cli.req("/api/password", {"old": "pw-alice-1",
                                         "new": "pw-alice-2"})
    check(st == 200 and j.get("ok"), "改密码成功", str(j)[:100])
    st, j = Client(base).req("/api/login", {"username": "alice",
                                            "password": "pw-alice-1"})
    check(st == 401, "旧密码失效", str(st))
    st, j = Client(base).req("/api/login", {"username": "alice",
                                            "password": "pw-alice-2"})
    check(st == 200 and j.get("ok"), "新密码可登录", str(st))
    pw_cli2 = Client(base)
    pw_cli2.req("/api/login", {"username": "alice", "password": "pw-alice-2"})
    st, j = pw_cli2.req("/api/password", {"old": "wrong", "new": "x123456"})
    check(st == 401, "原密码错了不能改", str(st))
    st, j = pw_cli2.req("/api/password", {"old": "pw-alice-2", "new": "123"})
    check(st == 400, "新密码太短被拒", str(j.get("error"))[:60])
    # 改回去, 免得影响后面的限流测试
    pw_cli2.req("/api/password", {"old": "pw-alice-2", "new": "pw-alice-1"})

    # ---- N. 限流 ----
    platform.rate_reset("auth:9.9.9.9")
    codes = []
    for i in range(25):
        st, _j = Client(base).req("/api/login", {"username": "alice",
                                                 "password": "bad-%d" % i})
        codes.append(st)
    check(429 in codes, "连续失败触发限流(429)", str(codes[-3:]))

    # ---- O. 管理员看全平台账号状态 ----
    # 这几个用例专门盯"跨用户可见"这件事: 之前管理员只能看自己的 EngineManager,
    # 别人的号在不在跑、掉没掉线, 完全看不到。
    # ⚠ 先把 N 段限流那一桶清掉 —— 它连续打了 25 次失败登录, 桶是**按 IP**
    #   算的, 紧接着的正常登录/注册会被当成"尝试过于频繁"挡掉。
    platform.rate_reset("auth:127.0.0.1")
    adm = Client(base)
    st, _jl = adm.req("/api/login", {"username": "alice",
                                     "password": "pw-alice-1"})
    check(st == 200 and bool(adm.cookie), "管理员重新登录拿到会话", str(st))
    cok_web._ADMIN_STATE_CACHE.clear()      # 同上: 别拿旧快照断言
    st, j = adm.req("/api/admin/accounts")
    check(st == 200 and j.get("ok") and j.get("platform") is True,
          "管理员可拉全平台账号状态", str(j)[:120])
    rows = j.get("accounts") or []
    keys = sorted(r["key"] for r in rows)
    check(keys == ["900000000001", "900000000002"],
          "一次看到**所有人**的账号(甲 + 乙)", str(keys))
    owners = sorted(set((r.get("owner") or "") for r in rows))
    check(owners == sorted([_uid("alice"), _uid("bob")]),
          "每行带 owner uid(能对上用户)", str(owners))
    names = sorted(set((r.get("username") or "") for r in rows))
    check(names == ["alice", "bob"], "每行带用户名(前端不用二次查表)", str(names))
    # 只读: 不该有任何凭据字段漏出来
    leaked = [k for r in rows for k in r
              if k.lower() in ("platformtoken", "signcode", "uuid", "deviceid",
                               "pfid", "buildcode")]
    check(not leaked, "账号状态不带任何凭据字段", str(leaked[:5]))
    st_j = (j.get("stats") or {})
    check(st_j.get("users") == 2 and st_j.get("accounts") == 2,
          "统计里用户数/账号数对得上", str(st_j)[:120])
    check("running" in st_j and "errors" in st_j and "offline" in st_j,
          "统计含 running/errors/offline", str(sorted(st_j)))

    # 只按某个用户过滤(?uid=)
    st, j2 = adm.req("/api/admin/accounts?uid=" + _uid("bob"))
    only_bob = sorted(r["key"] for r in (j2.get("accounts") or []))
    check(st == 200 and only_bob == ["900000000002"],
          "可按 uid 只看某个用户的账号", str(only_bob))
    st, j3 = adm.req("/api/admin/accounts?uid=u-nobody-here")
    check(st == 200 and (j3.get("accounts") or []) == [],
          "不存在的 uid -> 空列表(不是全平台)", str(j3)[:100])

    # 普通用户看不到(横向越权最要紧的一条)
    st, j4 = c2.req("/api/admin/accounts")
    check(st == 403, "普通用户拉全平台账号被拒", str(st))

    # 管理侧动作: 开/关别人的后台运行
    st, j5 = adm.req("/api/admin/account-action",
                     {"key": "900000000002", "on": True})
    check(st == 200 and j5.get("ok") and j5.get("on") is True,
          "管理员能启动别人的账号后台", str(j5)[:120])
    mb = cok_web.Handler.platform.get(_uid("bob"))
    check("900000000002" in mb.parallel, "bob 的并行集里真的多了这个号",
          str(sorted(mb.parallel)))
    st, j6 = adm.req("/api/admin/account-action",
                     {"key": "900000000002", "on": False})
    check(st == 200 and j6.get("ok") and not j6.get("on"),
          "管理员能停掉别人的账号后台", str(j6)[:120])
    check("900000000002" not in mb.parallel, "bob 的并行集里真的少了这个号",
          str(sorted(mb.parallel)))
    st, j7 = adm.req("/api/admin/account-action", {"key": "nope-nope", "on": True})
    check(st == 200 and not j7.get("ok"), "不存在的账号 key 被拒",
          str(j7.get("error"))[:80])
    st, j8 = adm.req("/api/admin/account-action", {"on": True})
    check(st == 200 and not j8.get("ok"), "缺少 key 被拒", str(j8.get("error"))[:60])
    st, j9 = c2.req("/api/admin/account-action",
                    {"key": "900000000001", "on": True})
    check(st == 403 and not j9.get("ok"),
          "普通用户不能开关别人的账号",
          "%s / %s" % (st, str(j9.get("error"))[:60]))
    # ⚠ 不能断言"alice 的并行集是空的" —— K 段自己就往里加了 900000000001。
    #   越权的正确判据是"这个号没被**新加进去**"。
    ma2 = cok_web.Handler.platform.get(_uid("alice"))
    check("900000000002" not in ma2.parallel
          and sorted(ma2.parallel) == ["900000000001"],
          "越权动作没生效(bob 的号没进 alice 的并行集)",
          str(sorted(ma2.parallel)))

    # 封禁用户的主人 -> 不许动他的号
    platform.user_set_banned("bob", True)
    st, ja = adm.req("/api/admin/account-action",
                     {"key": "900000000002", "on": True})
    check(st == 200 and not ja.get("ok") and "封禁" in str(ja.get("error")),
          "主人被封禁的账号不允许启动", str(ja.get("error"))[:60])
    platform.user_set_banned("bob", False)

    # 只读预览: 从没登录过的用户也要能看到他有几个号(且不能建引擎)
    uid_carol = ""
    platform.rate_reset("auth:127.0.0.1")     # 上一段的登录失败还占着这个桶
    code2 = platform.invite_new("alice", note="给 carol 看只读预览")
    c3 = Client(base)
    st, jc = c3.req("/api/register", {"username": "carol",
                                      "password": "pw-carol-1",
                                      "invite": code2})
    check(st == 200 and jc.get("ok"), "carol 注册成功(用来验证未登录用户的预览)",
          str(jc)[:100])
    rowc = platform.user_get("carol")
    uid_carol = rowc["uid"] if rowc else ""
    full = {"pfId": "x", "platformToken": "x", "deviceId": "x", "uuid": "x",
            "buildCode": "x", "signCode": "x"}
    accounts.save_account(dict(full, gameUid="900000000003",
                               roleName="丙的号"),
                          label="丙的号", owner=uid_carol)
    try:
        st, jd = adm.req("/api/admin/accounts")
        mine = [r for r in (jd.get("accounts") or [])
                if r.get("username") == "carol"]
        check(st == 200 and len(mine) == 1 and mine[0]["running"] is False,
              "carol 从没登录也能看到他的号(只读预览, 不算运行)", str(mine)[:160])
        check(uid_carol not in cok_web.Handler.platform.users,
              "预览不把他塞进运行时表(不建引擎)", str(list(cok_web.Handler.platform.users)))
    finally:
        try:
            accounts.remove_account("900000000003", owner=uid_carol)
        except Exception:  # noqa: BLE001
            pass
        try:
            platform.user_delete("carol")
        except Exception:  # noqa: BLE001
            pass

    # 单用户模式(platform=None)不该炸
    # ⚠ 先清缓存: 这个接口有 5 秒缓存, 而上面几段用例改过账号库/封禁状态。
    #   不清的话拿到的是旧快照, 断言会"莫名其妙"地失败。
    cok_web._ADMIN_STATE_CACHE.clear()
    old_platform = cok_web.Handler.platform
    try:
        cok_web.Handler.platform = None
        st, je = adm.req("/api/admin/accounts")
        check(st == 200 and je.get("platform") is False,
              "单用户模式下这个接口自洽返回(不是 500)", str(je)[:120])
    finally:
        cok_web.Handler.platform = old_platform

    # ---- P. 没有运行时时的兜底(_NULL_MANAGER) ----
    # 平台层存在但**这个用户没有引擎实例**(从没登录 / 已被空闲回收)时,
    # `_manager()` 返回空壳而不是 None —— 之前返回 None, 下游
    # `.view_engine().snapshot()` 一串 AttributeError, 表现为接口 500 +
    # 页面转圈, 排查时很容易误判成前端 bug。
    uid_carol2 = ""
    platform.rate_reset("auth:127.0.0.1")
    code3 = platform.invite_new("alice", note="验证空壳兜底")
    c4 = Client(base)
    st, jc4 = c4.req("/api/register", {"username": "carol2",
                                       "password": "pw-carol-2",
                                       "invite": code3})
    check(st == 200 and jc4.get("ok"), "carol2 注册成功(验证空壳兜底)",
          str(jc4)[:100])
    rowc2 = platform.user_get("carol2")
    uid_carol2 = rowc2["uid"] if rowc2 else ""
    # ⚠ 必须先建一个**真会话**(登录过)才有 EngineManager 实例可以对照 ——
    #   这里 carol2 只是"注册了但没登录", 所以她的号本来就该走空壳路径,
    #   而账号库此刻也确实没有她的号(前一步 remove 掉了), 于是 rows 为空。
    accounts.save_account({"pfId": "x", "platformToken": "x", "deviceId": "x",
                           "uuid": "x", "buildCode": "x", "signCode": "x",
                           "gameUid": "900000000004", "roleName": "丁的号"},
                          label="丁的号", owner=uid_carol2)
    check(len(accounts.list_accounts(owner=uid_carol2)) == 1,
          "前置: 丁的号确实入库了(免得空列表被当成'兜住了')",
          str(accounts.list_accounts(owner=uid_carol2))[:100])
    try:
        # 直接对"有平台层、但该用户没有实例"的情形走一遍快照 ——
        # 这正是过去 500 的那条路径(_manager() 返回 None ⇒ .view_engine() 炸)。
        cok_web._ADMIN_STATE_TTL = 0.0
        rows = cok_web._admin_accounts_snapshot(
            _FakeHandler(cok_web.Handler.platform))
        mine2 = [r for r in rows.get("accounts") or []
                 if r.get("owner") == uid_carol2]
        check(len(mine2) == 1 and mine2[0]["running"] is False,
              "没有引擎实例的用户也能出状态行(空壳兜底)",
              str(mine2)[:160])
        # ⚠ 期望值是 "none"(未托管), 不是 "idle"。
        #   "idle" = 有引擎在看、但没在后台跑; "none" = 连引擎都没有,
        #   从来没人看过它。混成一个会让管理页"空闲"筛选把一堆没跑过的号
        #   也捞进来 —— 管理员看到 20 个"空闲", 实际一个都没跑过。
        check(mine2 and mine2[0]["status"] == "none",
              "没在跑的号状态是 none(未托管, 不是 idle)",
              str(mine2[0].get("status")) if mine2 else "-")
        # 有引擎但没在后台跑 = idle。这条不走账号库 —— 直接对一行构造好的
        # 数据调 _account_row, 免得为了造"有引擎"去启真引擎。
        class _Mgr(object):
            lock = _NullLockForTest()
            engines = {"k": object()}
            parallel = ()
            priorities = {}
        row_idle = cok_web._account_row(
            {"key": "k", "label": "空闲号", "owner": uid_carol2}, _Mgr(),
            None, 0)
        check(row_idle["status"] == "idle" and row_idle["running"] is True,
              "有引擎没在跑的号状态是 idle",
              "%s / running=%s" % (row_idle["status"], row_idle["running"]))
        row_none = cok_web._account_row(
            {"key": "k2", "label": "没跑过", "owner": uid_carol2}, None, None, 0)
        check(row_none["status"] == "none",
              "没引擎也没数据的号是 none(未托管)",
              str(row_none["status"]))

        # ---- /api/admin/overview: 独立管理页的 KPI 必须和表同一个口径 ----
        # 为什么单独守这条: 概览曾经自己算一遍"在跑/打怪/有罩", 表格用
        # _account_row 的状态 —— 两套算法迟早对不上("表里 6 行、卡片说 2 个在跑")。
        # 现在概览是快照的薄聚合层, 这条测试把它钉住。
        cok_web._ADMIN_STATE_TTL = 0.0
        st_ov, j_ov = adm.req("/api/admin/overview")
        check(st_ov == 200 and j_ov.get("ok"), "管理页概览接口 200",
              str(j_ov)[:120])
        accs = j_ov.get("accounts") or []
        check(j_ov.get("accounts_total") == len(accs),
              "概览的 accounts_total 就是表里的行数",
              "%s vs %s" % (j_ov.get("accounts_total"), len(accs)))
        check(j_ov.get("running") == len([r for r in accs if r.get("running")]),
              "概览 running = 表里 running 为真的行数",
              "%s vs %s" % (j_ov.get("running"),
                            len([r for r in accs if r.get("running")])))
        check(j_ov.get("errors") == len([r for r in accs
                                         if r.get("status") == "error"]),
              "概览 errors = 表里 status=error 的行数", str(j_ov.get("errors")))
        check(isinstance(j_ov.get("users"), list) and j_ov.get("users"),
              "概览带用户列表(系统与运维面板要用)", str(j_ov)[:120])
        check(isinstance(j_ov.get("server_time"), float) and j_ov["server_time"] > 0
              and isinstance(j_ov.get("python"), str) and j_ov["python"]
              and isinstance(j_ov.get("data_root"), str),
              "概览带运行时字段(时间/Python/数据目录)", str(j_ov)[:160])

        # ---- 独立管理页 /admin 的路由与鉴权 ----
        # 三个分支都要守: 未登录给登录页 / 非管理员 403 / 管理员拿到页面。
        # 少了中间那条, 普通用户会打开一个空壳页面然后所有接口 403。
        st_pg, body_pg = _get_raw(base, "/admin")
        check(st_pg == 200 and b"COK" in body_pg,
              "/admin 未登录时给登录页(不是 500 / 404)", str(st_pg))
        st_a, j_a = adm.req("/api/admin/overview")
        check(st_a == 200, "管理员能拉管理页概览", str(st_a))
        # 普通用户: 直接换一个非管理员会话打这两个入口
        platform.rate_reset("auth:127.0.0.1")
        code5 = platform.invite_new("alice", note="验证非管理员被拦")
        c5 = Client(base)
        st5, _j5 = c5.req("/api/register", {"username": "dave5",
                                            "password": "pw-dave-5",
                                            "invite": code5})
        check(st5 == 200, "dave5 注册成功(验证非管理员被拦)", str(st5)[:100])
        st_ov2, j_ov2 = c5.req("/api/admin/overview")
        check(st_ov2 == 403, "非管理员拉概览被 403", str(st_ov2))
        st_acc2, _j = c5.req("/api/admin/accounts")
        check(st_acc2 == 403, "非管理员拉全平台账号被 403", str(st_acc2))
        # 空壳本身的可迭代性: 遍历 / with lock / view_engine 都不能炸
        null = cok_web._NULL_MANAGER
        with null.lock:
            pass
        check(list(null.accounts) == [] and null.view_engine() is not None,
              "空壳管理器可遍历/可加锁/有 view_engine", type(null).__name__)
    finally:
        try:
            accounts.remove_account("900000000004", owner=uid_carol2)
        except Exception:  # noqa: BLE001
            pass
        try:
            platform.user_delete("carol2")
        except Exception:  # noqa: BLE001
            pass


if __name__ == "__main__":
    sys.exit(main())