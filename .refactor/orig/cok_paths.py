"""唯一的路径解析入口。

这个仓库有两类目录, 混淆它们是历史上大部分"文件找不到 / 写错地方"的根因:

**资源目录(只读, 随代码走)**
    ``cok/resources/`` —— 协议目录、道具表、前端页面等静态文件。
    安卓端这些文件被打进 APK 的 assets, 由 Chaquopy 解到 app 私有目录。

**数据目录(可写, 随账号/设备走)**
    ``cok/data/``(桌面端)或 ``files/cok/data``(安卓端)。
    账号库、地图索引、运行时 json 都落在这里。

解析顺序(前者优先):

* ``COK_RESOURCES_DIR`` → ``<仓库根>/resources`` → ``<包目录>/resources``
* ``COK_DATA_ROOT``     → ``<仓库根>/data``       → ``<包目录>/data``

安卓端由 ``android_entry.py`` 在启动时设置这两个环境变量。
桌面端不设也能跑 —— 默认值就是仓库里的 ``cok/resources`` 与 ``cok/data``。

⚠ 不要用 ``os.path.dirname(__file__)`` 去拼资源路径: 同一个模块在桌面端
位于 ``cok/core/``, 在安卓端却被解到 assets 根目录 —— 只有这里算得对。
"""

import os

#: 本文件所在目录 = ``cok/core``
_CORE_DIR = os.path.dirname(os.path.abspath(__file__))

#: 包目录 = ``cok``
PACKAGE_DIR = os.path.dirname(_CORE_DIR)

#: 仓库根目录
REPO_ROOT = os.path.dirname(PACKAGE_DIR)

#: 安卓端由 build.gradle 生成的运行时种子(桌面端不存在)
APK_SEED_FILE = os.path.join(PACKAGE_DIR, "cok_seed.json")


def _first_dir(env_key, *candidates):
    """按 env → 候选路径 的顺序挑第一个存在的目录。

    都不存在时返回第一个候选 —— 调用方几乎都要拿它拼文件名, 返回 None
    只会把问题推迟到更远的地方。
    """
    env = os.environ.get(env_key)
    if env:
        return env
    for path in candidates:
        if os.path.isdir(path):
            return path
    return candidates[0]


def _flat_dir():
    """安卓端 Chaquopy 把 assets 摊平到同一层, 资源与 .py 同目录。

    判定依据: 模块自身目录里就有 id-names.json 这种**只可能来自 resources** 的文件。
    找不到就返回 None —— 不猜。
    """
    for name in ("id-names.json", "cok_webui.html", "bag-items.json"):
        if os.path.isfile(os.path.join(_CORE_DIR, name)):
            return _CORE_DIR
    return None


def resources_dir():
    """只读资源目录(协议目录、道具表、前端页面)。"""
    flat = _flat_dir()
    candidates = [
        os.path.join(PACKAGE_DIR, "resources"),   # 桌面: cok/resources
        os.path.join(REPO_ROOT, "resources"),     # 桌面兜底
    ]
    if flat is not None:
        candidates.insert(0, flat)                # Chaquopy 摊平布局
    return _first_dir("COK_RESOURCES_DIR", *candidates)


def data_dir():
    """可写数据目录(账号库、地图索引、运行时 json)。"""
    return _first_dir(
        "COK_DATA_ROOT",
        os.path.join(PACKAGE_DIR, "data"),
        os.path.join(REPO_ROOT, "data"),
    )


def resource(*parts):
    """资源目录下的某个文件路径。"""
    return os.path.join(resources_dir(), *parts)


def under_data(*parts):
    """数据目录下的某个文件路径(不创建目录)。"""
    return os.path.join(data_dir(), *parts)


def ensure_data_dir():
    """确保数据目录存在并返回它。"""
    path = data_dir()
    try:
        os.makedirs(path, exist_ok=True)
    except OSError:
        pass
    return path