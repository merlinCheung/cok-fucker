#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""作用域容器: 把"模块级可变全局"收进一个可寻址的命名空间。

## 为什么要有这个

`cok_map` / `cok_rally` 原来把可变状态直接挂在**模块对象**上
(`DATA_DIR` / `DEFAULT_INDEX` / `HISTORY_FILE` / `PID_FILE` /
`_DIR_BY_UID` / `REGISTRY_FILE`)。

这在单账号时代没问题: 一个进程里只有一个账号, 改一次全局就完事。
但**服务端是多租户** —— 5 个账号 5 个引擎在同一个进程里, 每个都要独立的
账号数据目录。模块级全局是**进程级单例**, 谁最后写谁生效, 前面的全被覆盖。

## 做法

`Scope` 就是一个**带层级查找的 dict**:

    Scope(默认值)                       # 根: 进程级默认
    scope.child("351542128002216")      # 子: 账号级
    scope["DATA_DIR"] = "/x"            # 写到当前 scope
    scope.set("DATA_DIR", v, uid="...") # 写到指定账号的子 scope
    scope.get("DATA_DIR")               # 先找自己, 再找祖先

于是同一份模块代码**不需要知道"现在是谁在调用"**:
给子 scope 设的值只有那个子 scope 读得到, 默认值仍然存在。

## 和直接用 dict 的区别(为什么要包一层)

1. **有名字**: 顶层 key 就是状态名, 拼错立刻知道; 不用记 `scope[0]` 是啥。
2. **有继承**: 子 scope 没设过就读父的 —— 默认值只写一份, 不用在每个账号里复制。
3. **有快照**: `snapshot()` 一次列出所有账号的覆盖, 排查"这个号的目录为什么不对"一眼可见。
4. **测试可断言**: `Scope` 的 API 稳定, 断言 `scope.get(...)` 比断言模块属性可靠。

## 语义边界(重要)

- `Scope.set(k, v)` 只改**当前** scope; 想改子 scope 必须显式 `set(k, v, uid=...)`
  或 `child(uid).set(...)`。**不会**隐式扩散到别的账号。
- 删 key 用 `Scope.reset(k)`: 回到**父 scope 的值**(不是删掉, 是"取消覆盖")。
- 子 scope 是**惰性创建**的: 没访问过就没有, 不会凭空产生一堆空桶。
"""

import os
import threading

__all_scope__ = ["Scope"]


class Scope(object):
    """带层级查找的命名空间。

    参数:
        parent: 父 scope(可为 None)
        name:   给日志用的名字(默认自动生成)
    """

    _MISSING = object()          # "没找到" 的哨兵(区分「值是 None」和「没有这个键」)

    def __init__(self, parent=None, name=""):
        object.__setattr__(self, "_values", {})
        object.__setattr__(self, "_children", {})
        object.__setattr__(self, "_parent", parent)
        object.__setattr__(self, "_name", name)
        object.__setattr__(self, "_lock", threading.RLock())

    # ─────────────────────── 查找 ───────────────────────
    def get(self, key, default=None):
        """取值: 当前 scope 没有 → 往父级找 → 都没有返回 default。"""
        cur = self
        while cur is not None:
            with cur._lock:
                if key in cur._values:
                    return cur._values[key]
            cur = cur._parent
        return default

    def raw(self, key, default=None):
        """只查当前 scope(不往父级找)。"""
        with self._lock:
            return self._values.get(key, default)

    def has_own(self, key):
        """当前 scope 是否**自己**设过这个值(不是继承来的)。"""
        with self._lock:
            return key in self._values

    def setdefault(self, key, value):
        """当前 scope 没设过才设; 返回最终生效的值(可能是父级的)。"""
        if self.raw(key, Scope._MISSING) is Scope._MISSING:
            with self._lock:
                self._values[key] = value
        return self.get(key)

    # ─────────────────────── 写入 ───────────────────────
    def set(self, key, value, uid=None):
        """设值。uid 为空 → 写**自己**; 否则写该 uid 的子 scope。

        返回实际写入的 scope 对象(排查时有用)。
        """
        k = _uid_key(uid)
        target = self.child(k) if k else self
        with target._lock:
            target._values[key] = value
        return target

    def update(self, **kw):
        with self._lock:
            self._values.update(kw)
        return self

    def reset(self, key):
        """取消当前 scope 的覆盖, 回到父级的值。"""
        with self._lock:
            self._values.pop(key, None)
        return self

    def clear(self):
        """清空当前 scope(不动父级)。"""
        with self._lock:
            self._values.clear()

    # ─────────────────────── 子 scope ───────────────────────
    def child(self, uid, create=True):
        """取(或建)uid 对应的子 scope。

        uid 是**原始类型**(str/int 都行), 内部统一成 str 做 key,
        否则 `1` 和 `"1"` 会分到两个桶 —— 而账号 id 在 JSON 里是数字、
        在命令行里是字符串, 同一个账号被拆成两份是最难查的那类 bug。
        """
        k = _uid_key(uid)
        if not k:
            return self
        with self._lock:
            sub = self._children.get(k)
            if sub is None and create:
                sub = Scope(self, "%s/%s" % (self._name, k))
                self._children[k] = sub
            return sub

    def children(self):
        with self._lock:
            return dict(self._children)

    def drop_child(self, uid):
        """删掉某个 uid 的子 scope(它的一切覆盖都回默认)。"""
        with self._lock:
            return self._children.pop(_uid_key(uid), None)

    # ─────────────────────── 查看 ───────────────────────
    def snapshot(self):
        """把整棵树的覆盖列出来(不含父级)。排查用。

        返回: {uid 或 "": {key: value}}  —— 空字符串是当前 scope 自己的覆盖。
        """
        out = {"": dict(self._values)}
        for k, sub in self.children().items():
            out[k] = dict(sub._values)
        return out

    def explain(self, key):
        """这个键的值从哪来: 返回 (值, 来源描述)。"""
        cur = self
        while cur is not None:
            if cur.has_own(key):
                return cur.get(key), (cur._name or "<default>")
            cur = cur._parent
        return None, "<unset>"

    @property
    def name(self):
        return self._name

    @property
    def parent(self):
        return self._parent

    def __getitem__(self, key):
        v = self.get(key, Scope._MISSING)
        if v is Scope._MISSING:
            raise KeyError(key)
        return v

    def __setitem__(self, key, value):
        self.set(key, value)

    def __contains__(self, key):
        cur = self
        while cur is not None:
            if cur.has_own(key):
                return True
            cur = cur._parent
        return False

    def __repr__(self):
        return "<Scope %s own=%s children=%s>" % (
            self._name or "default", sorted(self._values),
            sorted(self._children))


# ───────────────────────── 工具 ─────────────────────────
def _uid_key(uid):
    """把 uid 归一成字符串。

    账号 id 在库里是数字(351542128002216)、在命令行/HTML 里是字符串,
    不归一就会分成两个桶。
    """
    if uid is None:
        return ""
    if isinstance(uid, str):
        return uid.strip()
    return str(uid)


# ───────────────────────── 进程级根 ─────────────────────────
# 每个需要"按账号隔离"的模块建一个自己的根 Scope, 名字带模块名方便排查。
ROOT = Scope(None, "root")