"""COK 直连工具 —— 协议 / 地图 / 自动化 / 控制台 / 安卓端共用的 Python 包。

分层:

* :mod:`cok.paths`   —— 唯一的路径解析入口(资源 / 数据 / 包根)
* :mod:`cok.core`    —— 协议与业务实现(不含任何 CLI)
* :mod:`cok.tools`   —— 命令行动手工具(扫描 / 导出 / 校验)
* :mod:`cok.tests`   —— 离线回归测试
* ``cok.tools.probes`` —— 协议逆向期的一次性探针(归档, 不在运行时路径上)

统一入口::

    python3 -m cok <子命令>      # run / scan / export / console / test

桌面端数据根目录默认 ``cok/data``, 可用 ``COK_DATA_ROOT`` 覆盖;
安卓端由 ``android_entry.py`` 注入 ``files/cok/data``。
"""

__version__ = "1.0.0"