#!/usr/bin/env python3
"""渠道档案(channels): 一个渠道 = 一份配置 + 一套协议实现。

为什么要有这一层
----------------
以前果盘(guopan)是**硬编码**在 cok_channel_login.py 里的:
``CHANNEL_TEMPLATE`` / ``PFID_PREFIX`` / pfId 前缀 / UI 文案全都写死"果盘"。
再加一个渠道(比如小七 x7sy)就得把几百行协议代码复制一份, 而且两边的
appid/key/前缀很容易改串。

现在拆成两层:

* **档案(profile)** —— 纯配置: pf / channel / 包名 / 主机 / pfId 前缀 …
  加渠道时改这里, 不碰协议代码。
* **协议实现(protocol module)** —— 负责"账号密码 -> 平台身份(pfId)",
  以及"pfId -> 账号库凭据"。每个渠道一个模块, 通过 :func:`resolve_protocol`
  **懒加载**(避免循环 import)。

档案字段
--------
=========  ==========================================================
id         内部标识(网页/安卓传这个, 如 "guopan" / "x7sy")
name       显示名(UI 用, 如 "果盘" / "小七")
pf         游戏服**会校验**的渠道字段(cn_xxx); 填错 -> E002
channel    渠道名(getserverlist.php 用)
packageName 渠道包名
host/port  游戏服地址
pfIdPrefix pfId 前缀("ewanqf:" -> pfId = ewanqf:<平台token>)
protocol   协议实现模块名(懒加载); None = 该渠道还没实现
=========  ==========================================================

⚠ pf / pfIdPrefix **不能靠包名猜**, 必须实测:
游戏服只认 (pfId, gameUid, uuid) 三元组 + pf, pf 填错直接 E002。
用 :func:`cok_accounts.probe_pf` 登录实测确定。
"""
# --- 包自举: 直接 `python3 cok/core/xxx.py` 时把 cok/ 加进 sys.path ---
import os as _os
import sys as _sys

_PKG_ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
if _os.path.isdir(_PKG_ROOT) and _PKG_ROOT not in _sys.path:
    _sys.path.insert(0, _PKG_ROOT)
_CORE = _os.path.join(_PKG_ROOT, "core")
if _os.path.isdir(_CORE) and _CORE not in _sys.path:
    _sys.path.insert(0, _CORE)

import importlib  # noqa: E402


class ChannelProfile(object):
    """一个渠道的静态档案(纯数据, 不含协议逻辑)。"""

    def __init__(self, id, name, pf, channel, packageName, host, port,
                 pfIdPrefix, protocol=None, note="", enabled=True):
        self.id = id
        self.name = name
        self.pf = pf
        self.channel = channel
        self.packageName = packageName
        self.host = host
        self.port = port
        self.pfIdPrefix = pfIdPrefix
        #: 协议实现模块名(懒加载)。None = 尚未实现
        self.protocol = protocol
        self.note = note
        self.enabled = enabled

    # ---- pfId <-> 平台 token ----
    def make_pf_id(self, platform_token):
        """平台 token -> pfId(游戏服认的平台身份)。"""
        if not platform_token:
            return ""
        if platform_token.startswith(self.pfIdPrefix):
            return platform_token
        return "%s%s" % (self.pfIdPrefix, platform_token)

    def split_pf_id(self, pf_id):
        """pfId -> (前缀, 平台 token)。前缀不符返回 ("", pf_id)。"""
        s = str(pf_id or "")
        if self.pfIdPrefix and s.startswith(self.pfIdPrefix):
            return self.pfIdPrefix, s[len(self.pfIdPrefix):]
        return "", s

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "pf": self.pf,
            "channel": self.channel,
            "packageName": self.packageName,
            "host": self.host,
            "port": self.port,
            "pfIdPrefix": self.pfIdPrefix,
            "protocol": self.protocol,
            "note": self.note,
            "enabled": self.enabled,
        }

    def __repr__(self):
        return "<ChannelProfile %s pf=%s pkg=%s>" % (self.id, self.pf,
                                                     self.packageName)


#: 全部渠道档案。**加渠道 = 在这里加一条 + 写一个 protocol 模块**。
PROFILES = {}


def _register(p):
    PROFILES[p.id] = p
    return p


# --- 果盘 / 66手游 (com.hcg.cok.ewanqf.guopan) ---
# 协议: XXTEA + GPXX protobuf, userapi.guopan.cn/gamesdk/<appid>
# 见 cok_channel_login.py (已实测跑通, --selftest 可离线自证)
_register(ChannelProfile(
    id="guopan",
    name="果盘",
    pf="cn_ewanqf",
    channel="cn_ewanqf",
    packageName="com.hcg.cok.ewanqf.guopan",
    host="txaia-cok.elexapp.com",
    port=32231,
    pfIdPrefix="ewanqf:",
    protocol="cok_channel_login",
    note="海尔果盘/66手游; XXTEA+GPXX, 账号密码直连",
))


# --- 小七 (com.hcg.cok.ewanqf.x7sy) ---
# 账号体系: 小七平台账号(x7_cs_member_*) -> SuperSDK 换 eWan 账号 ->
#           游戏 pfId = ewanqf:<eWan openid>  (所以 pf 仍是 cn_ewanqf)
# 协议实现: cok_channel_x7sy (见该模块)
_register(ChannelProfile(
    id="x7sy",
    name="小七",
    pf="cn_ewanqf",
    channel="cn_ewanqf",
    packageName="com.hcg.cok.ewanqf.x7sy",
    host="txaia-cok.elexapp.com",
    port=32231,
    pfIdPrefix="ewanqf:",
    protocol="cok_channel_x7sy",
    note="小七(x7game/x7sy)平台账号; 需先经小七平台换 eWan 账号",
))


def get_profile(channel_id):
    """按 id 取档案; 找不到返回 None。"""
    if not channel_id:
        return None
    return PROFILES.get(str(channel_id).strip().lower())


def list_profiles(enabled_only=False):
    """列出所有渠道档案(给 UI 下拉框用)。"""
    out = [p for p in PROFILES.values() if (p.enabled or not enabled_only)]
    out.sort(key=lambda p: p.id)
    return out


def resolve_protocol(profile):
    """懒加载某渠道的协议实现模块; 没实现/导入失败返回 None。

    返回的模块必须提供:
        login(account, password, verbose=False) -> dict
            {"ok": bool, "pfId": str, "pf": str, "platformToken": str,
             "identities": [{"pfId":..., "name":..., "hasCharacter":bool}, ...],
             "errmsg": str, ...}
        build_account(pf_id, platform_token="", gamesvc=None) -> (acc|None, gs)
    """
    if profile is None or not profile.protocol:
        return None
    try:
        return importlib.import_module(profile.protocol)
    except Exception:  # noqa: BLE001  渠道模块缺失不该拖垮其它渠道
        return None
