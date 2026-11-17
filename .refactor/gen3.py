# -*- coding: utf-8 -*-
"""生成拆分文件 v3：不做任何 import 钩子 / 不换模块类型。

共享符号靠两层协作：
  cok_web_shared.py 末尾把 _SHARED_FORWARD 存进 sys.modules；
  cok_engine.py / cok_web.py 用 `from cok_web_shared import *` 拿**初始值**，
  再在模块体末尾调 bind_shared_module() 把自己注册进转发链。
之后任一层读写同名全局，都落到 shared 的同一个值上。

约束：cok_web_shared 不许回头 import 引擎层/门面层（模块名固定）。
"""
import pathlib, sys, importlib.machinery, importlib.util

SRC = pathlib.Path('.refactor/cok_web.py.bak0').read_text(encoding='utf-8')
lines = SRC.splitlines(keepends=True)
ROOT = pathlib.Path('.')
OUT_SHARED = ROOT / 'cok/core/cok_web_shared.py'
OUT_ENGINE = ROOT / 'cok/core/cok_engine.py'
OUT_WEB    = ROOT / 'cok/core/cok_web.py'

def find_class(lines, name):
    for i, l in enumerate(lines):
        if l.startswith('class %s' % name):
            end = len(lines)
            for k in range(i+1, len(lines)):
                if lines[k].strip() and not lines[k][0].isspace():
                    end = k
                    break
            return i, end
    raise KeyError(name)

eg_s, eg_e = find_class(lines, 'Engine')
em_s, em_e = find_class(lines, 'EngineManager')
pm_s, pm_e = find_class(lines, 'PlatformManager')

shared_lines = lines[52:eg_s]   # 从 import cok_daemon 开始
engine_body  = lines[eg_s:pm_e]
web_body     = lines[pm_e:]

# ---- shared 里 collect 共享符号的元组 ----
tmp = ROOT / 'cok/core/_cok_web_shared_gen.py'
# 收集器需要标准库导入（真实 shared 模块头部由标准头 + 这段拼出来）
# 收集器用的 = 原文件第 18-52 行的原始导入块 + 共享段
ORIG_IMPORTS = ''.join(lines[17:52])
tmp = ROOT / 'cok/core/_cok_web_shared_gen.py'
# 收集器需要标准库导入（真实 shared 模块头部由标准头 + 这段拼出来）
STD_HEAD = ("import os\nimport sys\nimport json\nimport time\nimport shutil\n"
            "import threading\nimport subprocess\nimport urllib.request\n"
            "import urllib.error\nfrom pathlib import Path\n")
tmp.write_text(ORIG_IMPORTS + ''.join(shared_lines), encoding='utf-8')
sys.path.insert(0, str(tmp.parent))
loader = importlib.machinery.SourceFileLoader('_cok_web_shared_gen', str(tmp))
spec = importlib.util.spec_from_loader('_cok_web_shared_gen', loader)
mod = importlib.util.module_from_spec(spec)
sys.modules['_cok_web_shared_gen'] = mod
loader.exec_module(mod)

ENGINE_NAMES = ('Engine', 'EngineManager', 'PlatformManager')
WEB_NAMES = ('cmd_console', 'serve', '_local_admin_ensure', 'main', 'Handler',
             '_serve_with_factory', '_local_admin_ensure',
             '_fmt_uptime', '_fmt_ts', '_is_https', '_is_local_request', '_is_loopback',
             '_json_response', '_read_request_json', '_local_admin_token_from_request',
             '_local_admin_ensure', '_local_admin_credentials', '_local_admin_login_page',
             '_admin_create_account', '_admin_create_account_for', '_admin_accounts_snapshot',
             '_account_row', '_migrate_accounts', '_migrate_users', '_admin_account_action',
             '_admin_platform_overview', '_local_admin_ensure')
lookup = {n for n in dir(mod) if not n.startswith('__')}
# shared 自己也不许 import 引擎层/门面层
forbidden = {'Engine', 'EngineManager', 'PlatformManager', 'Handler', 'serve', 'main'}
for name in sorted(lookup):
    if name in forbidden:
        print('skip(forward): %s' % name)
        continue
    print(name)
