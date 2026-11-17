#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""账号概念的**唯一真相层**(facade)。

## 为什么要这一层

系统里原来有三个"账号"的说法, 语义互相重叠:

| 出处 | 是什么 | 问题 |
|---|---|---|
| `cok_account.load_account()` | 从**设备**上读凭据 | 需要 root / adb, 服务端用不了 |
| `cok_accounts`(账号库) | 磁盘上的 `<uid>.json` + `data_dir(key)` | 是"持久化 + 目录"层, 不是"凭据"层 |
| `cok_client.ACCOUNT` | 协议字段模板 | 是"发出去的字段", 不是"哪个号" |

于是同一件事到处写法不同: "这个号是谁"有 `account_key(acc)` / `acc["gameUid"]` /
`args.account` 三种; "它的数据在哪"有 `accounts.data_dir(key)` / 手拼
`os.path.join(DATA_ROOT, key)`。

**本模块把这些收敛成一组语义明确的函数**, 上层只认这一组:

    resolve(x) / key_of(x) / label_of(x) / dir_of(x)
    registry(uid) / save() / delete() / list_all()
    for_client(x)   -> 能直接喂给 CokClient 的账号 dict
    is_complete(x) / missing_fields(x)

## 边界(不做什么)

- **不**改协议: 不碰 `cok_client.ACCOUNT` 的内容(安卓 build.gradle 靠正则
  替换那个块, 改了构建会静默失配)。
- **不**替账号库做决定: 存储格式、迁移、导入导出都在 `cok_accounts`。
- **不**假设 uid 一定存在: 传 None / 空串时返回"未指定"的语义,
  调用方不用到处判空。

## 一条铁律: 身份字段不继承

`IDENTITY_FIELDS` 里的字段(pfId / signCode / gameUid / uuid ...)每个号都不一样,
从别的号继承过来会**登录成功但服务端丢弃所有指令**(连上了, 界面全空 —— 极难查)。
`for_client()` 只合并**公共字段**(baseActiveKey 这类实测所有账号同值)。
"""

import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

import cok_accounts as _accounts

__all__ = [
    "resolve", "key_of", "label_of", "dir_of", "data_path",
    "registry", "save", "delete", "list_all", "exists",
    "for_client", "public_fields", "is_complete", "missing_fields",
    "IDENTITY_FIELDS", "load_account",
]

#: 身份字段(从账号库透出, 上层判断"能不能跨号继承"时用它)
IDENTITY_FIELDS = _accounts.IDENTITY_FIELDS


def load_account(*a, **kw):
    """从**设备**上读凭据(保留旧名, 老调用点不动)。

    ⚠️ 只在"本机连着手机 / 安卓端"有意义; 服务端用 `resolve()`。
    """
    from cok_account import load_account as _la
    return _la(*a, **kw)


# ─────────────────────── 解析 ───────────────────────
def key_of(x):
    """取账号 id。

    接受: 账号 dict / uid 字符串 / 数字 / None。
    **不查库** —— 只做"从各种形态里抠出 id", 免得调用方到处写
    `acc.get("gameUid") if acc else args.account`。
    """
    if x is None:
        return ""
    if isinstance(x, dict):
        return _accounts.account_key(x)
    return str(x).strip()


def registry(uid):
    """读账号库里 uid 那条; 没有返回 None。"""
    k = key_of(uid)
    if not k:
        return None
    try:
        return _accounts.get_account(k)
    except Exception:  # noqa: BLE001
        return None


def resolve(x):
    """把 uid / 账号 dict 归一成**账号 dict**。

    - dict: 原样返回(调用方自己那份为准)
    - uid(库里找得到): 库里那条
    - uid(库里没有) / None: `{"gameUid": uid}`, 至少 id 可用

    ⚠️ 可能返回**空 dict**(x 是 None 且没默认账号), 调用方要判。
    """
    if isinstance(x, dict):
        return x
    k = key_of(x)
    if not k:
        return {}
    reg = registry(k)
    return reg if reg else {"gameUid": k}


def label_of(x):
    """账号的显示名: label -> roleName -> gameUid -> ""。"""
    acc = x if isinstance(x, dict) else registry(x)
    if not acc:
        return ""
    try:
        return _accounts.account_label(acc) or key_of(acc)
    except Exception:  # noqa: BLE001
        return key_of(acc)


# ─────────────────────── 数据目录 ───────────────────────
def dir_of(x):
    """账号的运行时数据目录(不存在会创建)。

    ⚠️ 这是"账号数据目录"的**唯一入口**。别再各处手拼
    `os.path.join(DATA_ROOT, key)` —— 那绕过 `safe_key()`,
    uid 里带斜杠时目录就跑到别处去。
    """
    k = key_of(x)
    if not k:
        return _accounts.DATA_ROOT
    try:
        return _accounts.data_dir(k)
    except Exception:  # noqa: BLE001
        return _accounts.DATA_ROOT


def data_path(x, name):
    """账号数据目录下的某个文件。"""
    return os.path.join(dir_of(x), name)


# ─────────────────────── 增删查 ───────────────────────
def list_all():
    """库里所有账号(新的在前)。"""
    try:
        return _accounts.list_accounts()
    except Exception:  # noqa: BLE001
        return []


def exists(x):
    return bool(key_of(x)) and registry(x) is not None


def save(uid, acc, **kw):
    """把账号写进库。返回库里的 key(可能被纠正过)。"""
    return _accounts.upsert(key_of(uid) or key_of(acc), acc, **kw)


def delete(uid):
    """从库里删掉 uid(数据目录**不删** —— 那是用户的扫描结果)。"""
    k = key_of(uid)
    if not k:
        return False
    try:
        return bool(_accounts.remove(k))
    except Exception:  # noqa: BLE001
        return False


# ─────────────────────── 喂给客户端 ───────────────────────
def public_fields():
    """协议公共字段(baseActiveKey 这类, 实测所有账号同值)。"""
    try:
        return _accounts.public_fields()
    except Exception:  # noqa: BLE001
        return {}


def for_client(x):
    """产出**能直接喂给 CokClient 的账号 dict**。

    合并顺序(后者覆盖前者):
      1. 协议模板 `cok_client.ACCOUNT`(公开仓库里是占位符)
      2. 公共字段真值(本地缓存 / 账号库)
      3. 账号自己的字段

    第 3 步只覆盖**这个号自己的**字段 —— 身份字段绝不从别处继承
    (见模块头那条铁律)。
    """
    import cok_client as _cl
    out = _cl._public_defaults()          # 模板 + 公共字段真值
    acc = resolve(x)
    for k, v in (acc or {}).items():
        if v in (None, ""):
            continue                       # 空值不覆盖已有(模板/公共字段)
        out[k] = v
    return out


def is_complete(x):
    """这个号能不能登录(关键身份字段齐了没, 且都不是占位符)。"""
    return not missing_fields(x)


def missing_fields(x):
    """缺哪些关键字段(空列表 = 齐的)。

    ⚠️ 这里只查**账号身份**; `parseRegisterId` 故意**不查** ——
    它是安装注册标记(不是凭据), `CokClient` 在登录前会自己生成一个 UUID,
    老导入包里没有是正常的(见 cok_client.py:670)。
    """
    acc = for_client(x)
    need = ("gameUid", "pfId", "pf", "buildCode", "host", "port", "zn")
    miss = [k for k in need if not acc.get(k)]
    # 真·身份字段(缺了会登录失败 / 换号串号)
    for k in ("signCode", "uuid", "deviceId", "platformToken"):
        v = acc.get(k)
        if not v or _accounts.is_placeholder(v):
            miss.append(k)
    # 其它字段只要是占位符也算缺(模板里的 "<...>" 不是真值)
    # ⚠️ `parseRegisterId` 例外: 它是安装注册标记, 不是凭据,
    #    CokClient 登录前会自己生成 UUID(cok_client.py:670), 老包没这字段很正常。
    for k, v in (acc or {}).items():
        if k in miss or k == "parseRegisterId":
            continue
        if _accounts.is_placeholder(v):
            miss.append(k)
    return sorted(set(miss))


# ─────────────────────── 自检 ───────────────────────
def _selftest():
    print("[1] key_of: 各种形态都抠出 id")
    for v in ({"gameUid": " 111 "}, "222", 333, None, {"x": 1}):
        print("     %-26r -> %r" % (v, key_of(v)))
    print("[2] resolve: 库里没有时退回 {gameUid: uid}")
    print("     resolve('999999999') =", resolve("999999999"))
    print("[3] label_of / dir_of")
    print("     label_of('999999999') =", repr(label_of("999999999")))
    print("     dir_of('999999999')   =", dir_of("999999999"))
    print("[4] for_client: 占位符不覆盖真值")
    c = for_client(None)
    print("     baseActiveKey 还是占位符:",
          _accounts.is_placeholder(c.get("baseActiveKey")))
    print("[5] missing_fields")
    print("     ", missing_fields(None))
    print("OK")


if __name__ == "__main__":
    _selftest()