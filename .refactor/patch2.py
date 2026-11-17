# -*- coding: utf-8 -*-
"""修正: 读共享名字必须**不落** __dict__ —— 否则模块 __getattr__ 永远不触发。"""
import io

p = ".refactor/split2.py"
b = io.open(p, encoding="utf-8").read()

OLD = '''for _n in _SHARED_FORWARD:
    try:
        object.__setattr__(sys.modules[__name__], _n, getattr(_shared, _n))
    except AttributeError:
        pass
del _n
'''
NEW = '''# ⚠ 这里**故意不**把共享名字拷进本模块 __dict__:
#    一旦拷了, 读的时候直接命中 __dict__, 模块级 ``__getattr__`` 永远不会触发,
#    之后 shared 里改了值(测试注入 / 安卓注入钩子)本模块就再也看不见了。
#    "看不见"是静默的 —— 2026-11 拆分时在这里踩过一次。
#    共享名字统一靠 ``SharedModule.__getattr__`` 回 shared 取当前值。
'''
assert OLD in b
b = b.replace(OLD, NEW)

# 文件末尾的安装调用挪到「所有定义之后」
OLD2 = '''harness.write("cok/core/cok_engine.py",
              engine_head + fwd_block("引擎层") + engine_body
              + "\\n\\n_install_shared_module()\\n")'''
NEW2 = '''harness.write("cok/core/cok_engine.py",
              engine_head + fwd_block("引擎层") + engine_body
              + "\\n\\n_install_shared_module()\\n")'''
assert OLD2 in b

io.open(p, "w", encoding="utf-8").write(b)
print("patched")
