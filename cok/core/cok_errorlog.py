#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""异常**留痕**(P2): 替代 `except: pass`。

## 为什么改

代码里有 158 处(核心 9 个模块)`except: pass` —— 异常被**静默吞掉**:

    try:
        self._save_settings_db()      # 落库
    except Exception:
        pass                          # ← 失败了没人知道

三个后果, 都真实发生过:
1. **查不了**: 用户报"扫描没反应", 翻日志 —— 空的, 因为什么都没记。
2. **定不了位**: 就算有人打了 print, 也只有 `str(e)`, 没有文件/行号/函数。
3. **分不清"预期"和"真 bug"**: 文件不存在(预期) 和 磁盘满了(不是)
   混在一起, 谁都吞掉, 于是真问题永远浮不上来。

## 做法

`quiet(exc, where)` —— 记一条, 不抛, 不改控制流。**降级, 不升级**:

    try:
        ...
    except Exception as e:
        quiet(e, "落库失败")      # ← 只多这一行

三个设计点:

- **分级别**: 预期内异常(OSError/KeyError/TypeError/ValueError/AttributeError)
  记 DEBUG, 其余记 WARNING。文件不存在不该半夜叫醒运维, 但 socket 挂了该记。
- **采样**: 同一位置 2 秒内重复 N 次只记第一条 + 累计次数。
  高频轮询里一次网络抖能刷几千行, 把真日志冲掉 —— 这是最容易踩的坑。
- **不记敏感值**: 异常串截断到 300 字符(host/uid 会出现在里面)。

`quiet()` 自己绝不抛 —— 它出错就安静返回(它是最后一道, 没地方可喊)。

## 不收编的部分(有意为之)

- **老 tools / probes 脚本**: 那些是一次性诊断脚本, 吞异常是故意的(探针要看到
  全部输出), 换了反而吵。
- **纯清理路径**: `try: os.remove(f) except: pass` —— 文件本来就不存在是
  正常状态, 记日志纯属噪音。这类保留 pass, 但**必须写清注释**说明为什么。

## 自检 / 清单

    python3 -m cok_errorlog <目录>       # 列出所有静默 pass 的位置和所属函数

返回按函数聚合的清单, 收编时可以按优先级来(核心路径先收)。
"""

import logging
import os
import sys
import threading
import time

__all__ = ["quiet", "warn", "audit_silent_pass", "reset_throttle", "install"]

_LOG = logging.getLogger("cok")

#: 采样窗口(秒): 同一位置在这个窗口内只记第一条, 之后只累加计数。
_WINDOW = float(os.environ.get("COK_ERRLOG_WINDOW", "2.0"))

#: 同一位置的连续命中次数超过这个数, 改成"每 N 次记一条"
_BURST = int(os.environ.get("COK_ERRLOG_BURST", "50"))

#: 单条消息最大长度(异常字符串可能非常长, 会带上 host/uid)
_MAXLEN = 300

_lock = threading.Lock()
#: 位置 -> [窗口起点, 窗口内计数]
_seen = {}

#: 预期内的异常类型: 记 DEBUG(磁盘上没文件、键不存在、类型不对都是常态)
_EXPECTED = (OSError, IOError, KeyError, IndexError, TypeError, ValueError,
             AttributeError)


def install(level=logging.INFO):
    """把 `cok` 这个 logger 接到 stderr(幂等)。

    服务端(systemd)会收 stderr 进 journal, 所以不用额外配 handler;
    Android(Chaquopy) 的 stderr 也进 logcat。
    """
    lg = logging.getLogger("cok")
    if not lg.handlers:
        h = logging.StreamHandler()
        h.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s",
                                         "%m-%d %H:%M:%S"))
        lg.addHandler(h)
        lg.setLevel(level)
        lg.propagate = False
    return lg


def _where(where, depth):
    """定位信息: 调用方给的 where 优先, 否则从栈里取 文件:行号 in 函数。"""
    if where:
        return where
    try:
        f = sys._getframe(depth)
        while f is not None:
            mod = (f.f_globals.get("__name__") or "")
            if not (mod == "cok_errorlog" or mod.startswith("cok_errorlog.")):
                break
            f = f.f_back
        if f is None:
            return "<unknown>"
        return "%s:%d in %s" % (os.path.basename(f.f_code.co_filename),
                                f.f_lineno, f.f_code.co_name)
    except Exception:  # noqa: BLE001
        return "<unknown>"


def _clip(v):
    s = str(v)
    return s if len(s) <= _MAXLEN else s[:_MAXLEN] + "..."


def quiet(exc, where="", level=None, **extra):
    """记一条异常, **绝不抛出**。

    这是替代 `except: pass` 的标准写法: 把"吞掉"换成"吞掉但留痕"。

    参数:
        exc:   异常对象(或任何可 str 的东西)
        where: 出错位置/动作, 如 "落库失败"。不给就自动从栈里取 文件:行号。
        level: 日志级别。不给时: 预期内异常记 DEBUG, 其余 WARNING。
        extra: 附加字段(k=v), 会拼进消息(值截断)。
    """
    try:
        lvl = level
        if lvl is None:
            lvl = logging.DEBUG if isinstance(exc, _EXPECTED) else logging.WARNING
        loc = _where(where, 3)

        now = time.time()
        with _lock:
            ent = _seen.get(loc)
            if ent is not None and (now - ent[0]) < _WINDOW:
                ent[1] += 1
                if ent[1] % _BURST:
                    return                       # 采样: 静默跳过
                note = " (同一位置 %d 次)" % ent[1]
            else:
                _seen[loc] = [now, 1]
                note = ""

        msg = "%s: %s%s" % (loc, _clip(exc), note)
        if extra:
            msg += " | " + " ".join("%s=%s" % (k, _clip(v))
                                    for k, v in sorted(extra.items()))
        # exc_info 只在 WARNING 及以上带栈 —— DEBUG 是"预期内", 带栈纯属噪音
        if lvl >= logging.WARNING:
            _LOG.warning(msg, exc_info=exc if isinstance(exc, BaseException) else None)
        else:
            _LOG.debug(msg)
    except Exception:  # noqa: BLE001
        # 日志自己坏了也不能拖垮业务。这是本模块唯一保留的静默 ——
        # 它已经没有别的地方可喊了, 再抛出去只会让"日志失败"变成"业务崩"。
        return


def warn(exc, where="", **kw):
    """quiet() 的显式 WARNING 版("不该发生但也不至于崩")。"""
    kw.setdefault("level", logging.WARNING)
    return quiet(exc, where, **kw)


def reset_throttle():
    """清空采样状态(测试用; 长跑服务想重新统计时用)。"""
    with _lock:
        _seen.clear()


# ─────────────────────── 收编清单 ───────────────────────
def audit_silent_pass(root, skip_dirs=("__pycache__", ".git", "build", "probes")):
    """扫出所有 `except: pass` 的位置, 按函数归类。

    返回 [{file, line, func, except_line}], 只读不改, 供"逐步收编"排期用。

    判据(宁可漏不可误): except 之后第一条**真语句**就是 `pass`;
    中间只能有空行和注释。中间只要有一条别的语句, 就不算纯静默。

    跑法:
        python3 -m cok_errorlog <目录>
    """
    import ast
    import re

    out = []
    for dirpath, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        for fn in sorted(files):
            if not fn.endswith(".py"):
                continue
            # macOS 的 tar 会把扩展属性/资源分支写成 `._xxx` 伴随文件，
            # 它们**不是** Python 源码（内容是二进制），解包到 Linux 后
            # 混在 *.py 里。不跳过的话这里读一次就 UnicodeDecodeError。
            if fn.startswith("._"):
                continue
            path = os.path.join(dirpath, fn)
            try:
                with open(path, "rb") as fh:
                    raw = fh.read()
                # 按字节读再显式解码：遇到坏文件**跳过**，别让一份清单
                # 把调用方整个搞崩（本函数的定位是"辅助排查"）。
                src = raw.decode("utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            try:
                tree = ast.parse(src)
            except SyntaxError:
                continue

            spans = []
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    spans.append((node.lineno, node.end_lineno or node.lineno,
                                  node.name))
            spans.sort(key=lambda x: x[1] - x[0])

            lines = src.splitlines()
            for i, ln in enumerate(lines):
                if not re.match(r"\s*except\b", ln):
                    continue
                for j in range(i + 1, min(i + 8, len(lines))):
                    s = lines[j].strip()
                    if not s or s.startswith("#"):
                        continue
                    if s == "pass":
                        func = "<module>"
                        for a, b, name in spans:
                            if a <= i + 1 <= b:
                                func = name
                                break
                        out.append({"file": path, "line": i + 1, "func": func,
                                    "except_line": ln.strip()})
                    break
    return out


def _main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    root = argv[0] if argv else os.path.dirname(os.path.dirname(
        os.path.abspath(__file__)))
    rows = audit_silent_pass(root)
    by = {}
    for r in rows:
        by.setdefault((os.path.relpath(r["file"], root), r["func"]), []).append(r)
    print("静默 except:pass 共 %d 处, %d 个函数" % (len(rows), len(by)))
    for (f, fn), items in sorted(by.items(), key=lambda kv: -len(kv[1])):
        print("\n%s :: %s  (%d)" % (f, fn, len(items)))
        for it in items[:10]:
            print("  L%-5d %s" % (it["line"], it["except_line"][:72]))
        if len(items) > 10:
            print("  ... 还有 %d 处" % (len(items) - 10))
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())