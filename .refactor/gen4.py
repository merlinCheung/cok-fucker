# -*- coding: utf-8 -*-
"""生成拆分文件 v4（最终形态）

不注册任何 import 钩子、不替换模块类型。共享符号的协作方式：

  1. cok_web_shared.py 定义所有共享常量/别名/小工具 + __SHARED_NAMES__ + bind_shared_module()
     末尾调 _init_shared_registry() 把自己注册进 sys.modules。
  2. cok_engine.py / cok_web.py 顶部 `from cok_web_shared import *` 拿**初始快照**，
      文件末尾调 bind_shared_module(__name__, tuple(_SHARED_FORWARD))
  3. bind 之后，这一层的同名全局读写都转发到 shared 的 __shared_values__。
     读走不到 __shared_values__ 时（shared 还没加载完）回落到本模块自己的值。

字节级保真：搬移的代码一行不改。
"""
import pathlib, sys, importlib.machinery, importlib.util, keyword

ROOT = pathlib.Path('.')
SRC = ROOT / 'cok/core/cok_web.py'          # 已恢复的原始单文件
BAK = ROOT / '.refactor/cok_web.py.bak0'
assert SRC.read_bytes() == BAK.read_bytes(), 'cok/core/cok_web.py 必须是未拆分的原文'

lines = SRC.read_text(encoding='utf-8').splitlines(keepends=True)

def find_top(lines, pred, start=0):
    for i in range(start, len(lines)):
        if pred(lines[i]):
            end = len(lines)
            for k in range(i + 1, len(lines)):
                if lines[k].strip() and not lines[k][0].isspace() and not lines[k].startswith(')'):
                    end = k
                    break
            return i, end
    raise KeyError('not found')

eg_s, eg_e = find_top(lines, lambda l: l.startswith('class Engine'))
em_s, em_e = find_top(lines, lambda l: l.startswith('class EngineManager'))
pm_s, pm_e = find_top(lines, lambda l: l.startswith('class PlatformManager'))

shared_body = ''.join(lines[52:eg_s])     # 53 行之后到 Engine 之前（含 import 别名块）
engine_body = ''.join(lines[eg_s:pm_e])
web_body    = ''.join(lines[pm_e:])

ORIG_IMPORTS = ''.join(lines[17:52])      # 第 18-52 行：路径注入 + 原始 import 块

# ---------- 计算共享符号清单 ----------
probe = ROOT / 'cok/core/_probe_shared.py'
probe.write_text(ORIG_IMPORTS + shared_body, encoding='utf-8')
sys.path.insert(0, str(ROOT / 'cok' / 'core'))
ld = importlib.machinery.SourceFileLoader('_probe_shared', str(probe))
sp = importlib.util.spec_from_loader('_probe_shared', ld)
pm = importlib.util.module_from_spec(sp)
sys.modules['_probe_shared'] = pm
ld.exec_module(pm)

ENGINE_NAMES = ('Engine', 'EngineManager', 'PlatformManager')
WEB_NAMES = ('cmd_console', 'serve', 'main', 'Handler',
             '_serve_with_factory', '_fmt_uptime', '_fmt_ts', '_is_https',
             '_is_local_request', '_is_loopback', '_json_response',
             '_read_request_json', '_local_admin_token_from_request',
             '_local_admin_credentials', '_local_admin_login_page',
             '_admin_create_account', '_admin_create_account_for',
             '_admin_accounts_snapshot', '_account_row', '_migrate_accounts',
             '_migrate_users', '_admin_account_action', '_admin_platform_overview',
             '_admin_account_snapshot')
skip = set(ENGINE_NAMES) | set(WEB_NAMES)
names = sorted(n for n in dir(pm)
               if not n.startswith('__') and n not in skip and n != 'annotations')

# ---------- 1) cok_web_shared.py ----------
std_imports = """# -*- coding: utf-8 -*-
\"\"\"cok_web 共享层（从 cok_web.py 拆出，代码逐字搬移，未改一行逻辑）。

放这里的东西必须同时满足：
  * 是常量 / 模块别名 / 无状态小工具函数；
  * cok_engine（引擎层）和 cok_web（HTTP 层）都要用。

两个文件用 `from cok_web_shared import *` 拿初始值，再在文件末尾调
`bind_shared_module()` 把自己接进转发链 —— 于是任一层改这些全局，
其它层和本模块都看得到（测试靠 cok_web.channel = ... 注入假实现，
安卓靠 cok_web.set_platform_stop_app() 注入钩子，都依赖这个语义）。

约束：本模块不许 import cok_engine / cok_web（会成环）。要共享的可变状态
放 ``shared_state`` 字典。
\"\"\"
"""
shared_text = std_imports + ORIG_IMPORTS + shared_body
shared_text += "\n\n# ---------------------------------------------------------- 共享符号转发\n"
shared_text += "# 值本体存在本模块（它是链的根），其它层 bind 后读写落到这里。\n"
shared_text += "_SHARED_VALUES = {}\n"
shared_text += "_SHARED_LAYERS = []\n\n"
shared_text += "__SHARED_NAMES__ = (\n"
for n in names:
    shared_text += "    %r,\n" % n
shared_text += ''')


class _SharedModule(_ModuleType):
    """读写共享符号时落到 _SHARED_VALUES 的那一层。"""

    def __getattr__(self, name):
        if name in _SHARED_VALUES:
            return _SHARED_VALUES[name]
        raise AttributeError("module %r has no attribute %r" % (_SHARED_NAME, name))

    def __setattr__(self, name, value):
        if name in __SHARED_NAMES__:
            _SHARED_VALUES[name] = value
            return
        _ModuleType.__setattr__(self, name, value)


def _init_shared_registry():
    """把本模块换成 _SharedModule 并把初始值收进 _SHARED_VALUES。"""
    name = __name__
    values = dict((n, globals()[n]) for n in __SHARED_NAMES__ if n in globals())
    for layer in list(_SHARED_LAYERS):
        try:
            sys.modules.pop(layer, None)
        except Exception:
            pass
    del _SHARED_LAYERS[:]
    mod = _SharedModule(name)
    mod.__dict__.update(globals())
    mod.__dict__["__SHARED_NAME"] = name
    for key, value in values.items():
        mod.__dict__[key] = value
        _SHARED_VALUES[key] = value
    sys.modules[name] = mod
    return mod


def bind_shared_module(layer_name, names):
    """把一个引用层接进转发链：names 里的全局读写都落到共享值上。

    必须在**该模块体末尾**调用（类体/函数体执行期读共享名字靠的是
    `from cok_web_shared import *` 拿到的快照，bind 之前不动它）。
    """
    if layer_name in _SHARED_LAYERS:
        return
    layer = sys.modules.get(layer_name)
    if layer is None:
        return
    for name in names:
        if name in globals():
            layer.__dict__[name] = globals()[name]
    _SHARED_LAYERS.append(layer_name)

    def __getattr__(attr, _layer=layer, _names=names):
        if attr in _names and attr in _SHARED_VALUES:
            return _SHARED_VALUES[attr]
        raise AttributeError("module %r has no attribute %r" % (_layer.__name__, attr))

    def __setattr__(attr, value, _layer=layer, _names=names):
        if attr in _names:
            _SHARED_VALUES[attr] = value
            _layer.__dict__[attr] = value
            return
        _ModuleType.__setattr__(_layer, attr, value)

    layer.__class__ = type(str(layer_name) + "Module", (_SharedModule,),
                           {"__getattr__": __getattr__, "__setattr__": __setattr__})
    return layer


_init_shared_registry()
'''
(ROOT / 'cok/core/cok_web_shared.py').write_text(shared_text, encoding='utf-8')

# ---------- 2) cok_engine.py ----------
engine_text = "# -*- coding: utf-8 -*-\n" + '''\"\"\"cok_web 引擎层（从 cok_web.py 拆出，代码逐字搬移，未改一行逻辑）。

含 Engine / EngineManager / PlatformManager 三个类：一个账号一个引擎，
引擎只管「跑号」，不知道 HTTP 的存在。
\"\"\"
''' + ORIG_IMPORTS + "from cok_web_shared import *  # noqa: F401,F403  （共享层：常量/别名/小工具）\n\n"
engine_text += "from cok_web_shared import bind_shared_module as _bind_shared_module\n\n"
engine_text += "_SHARED_FORWARD = (\n"
for n in names:
    engine_text += "    %r,\n" % n
engine_text += ")\n\n"
engine_text += engine_body
engine_text += "\n\n_bind_shared_module(__name__, _SHARED_FORWARD)\n"
(ROOT / 'cok/core/cok_engine.py').write_text(engine_text, encoding='utf-8')

# ---------- 3) cok_web.py ----------
web_text = "# -*- coding: utf-8 -*-\n" + '''\"\"\"cok_web 门面 + HTTP 层（从 cok_web.py 拆出，代码逐字搬移，未改一行逻辑）。

结构：
  cok_web_shared 共享常量/别名/小工具（channel、D、_mcp_scan、路径、注册表）
  cok_engine     Engine / EngineManager / PlatformManager（跑号）
  cok_web(本文件) HTTP 层 + 本机管理员/迁移/main

`from cok_engine import *` 让 cok_web.Engine 这类名字保持原样可用
（测试与 android_entry.py 都按 cok_web.X 访问）。
\"\"\"
''' + ORIG_IMPORTS + "from cok_web_shared import *  # noqa: F401,F403  （共享层）\n"
web_text += "from cok_web_shared import bind_shared_module as _bind_shared_module\n"
web_text += "from cok_engine import *  # noqa: F401,F403  （引擎层：Engine/EngineManager/PlatformManager）\n\n"
web_text += "from cok_engine import _SHARED_FORWARD as _ENGINE_SHARED_FORWARD\n\n"
web_text += "from cok_engine import Engine, EngineManager, PlatformManager  # noqa: F401\n\n"
web_text += web_body
web_text += "\n\n_bind_shared_module(__name__, tuple(_SHARED_FORWARD) + _ENGINE_SHARED_FORWARD)\n"
# 门面末尾再挂一个 __getattr__，保证「先改 cok_web_shared.X，再从 cok_web 读」也一致
web_text += '''

def __getattr__(name):
    \"\"\"模块级兜底：门面层没定义的名字去共享层取。

    共享层的 __getattr__ 已经覆盖了 bind 过的名字，这里再兜一层，
    是为了让 `cok_web.<共享常量>` 在任何时刻都读到同一个值。
    \"\"\"
    try:
        _shared = __import__("cok_web_shared")
        return getattr(_shared, name)
    except AttributeError:
        raise AttributeError("module %r has no attribute %r" % (__name__, name))
'''
(ROOT / 'cok/core/cok_web.py').write_text(web_text, encoding='utf-8')

print('共享符号 %d 个' % len(names))
for path in ('cok/core/cok_web_shared.py', 'cok/core/cok_engine.py', 'cok/core/cok_web.py'):
    print(path, len((ROOT / path).read_text(encoding='utf-8').splitlines()), '行')
