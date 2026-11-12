#!/usr/bin/env python3
"""Regression test for the Guopan account-import credential handoff."""
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

_TMP = tempfile.mkdtemp(prefix="cok-channel-import-test-")
os.environ["COK_ACCOUNTS_DIR"] = os.path.join(_TMP, "accounts")
os.environ["COK_DATA_ROOT"] = os.path.join(_TMP, "data")

import cok_accounts as accounts  # noqa: E402
import cok_client  # noqa: E402
import cok_channel_login as channel_login  # noqa: E402
import cok_daemon  # noqa: E402
import cok_web  # noqa: E402


class FakeChannel(object):
    def __init__(self):
        self.calls = []

    def build_account_from_pf_id(self, pf_id, platform_token=""):
        self.calls.append((pf_id, platform_token))
        return ({"pfId": pf_id, "platformToken": platform_token,
                 "gameUid": "100", "uuid": "role-uuid", "deviceId": "device",
                 "buildCode": "build", "signCode": "sign"}, {"ok": True})


class FakeGameClient(object):
    made = []

    def __init__(self, host, port, timeout, account):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.account = account
        self.key_id = 1
        self.init_params = {}
        FakeGameClient.made.append(self)

    def connect(self):
        pass

    def bin_handshake(self):
        pass

    def login(self):
        pass

    def call(self, *_args, **_kwargs):
        return {}

    def close(self):
        pass


def main():
    fake = FakeChannel()
    old_channel = cok_web.channel
    cok_web.channel = fake
    try:
        engine = cok_web.Engine.__new__(cok_web.Engine)
        engine._chan_sessions = {
            "session": {"items": {"ROLE": {"perGameId": "ROLE", "name": "Role",
                                               "hasCharacter": True,
                                               "pfId": "ewanqf:1084ROLE"}},
                        "account": "channel-user"}
        }
        engine._chan_sessions_prune = lambda: None
        result = engine._channel_add({"sessionId": "session", "perGameIds": ["ROLE"]})
        assert result["ok"], result
        assert fake.calls == [("ewanqf:1084ROLE", "1084ROLE")], fake.calls
        stored = accounts.get_account("100")
        assert stored and stored["platformToken"] == "1084ROLE", stored
        print("[PASS] 果盘小号令牌随选中角色写入账号库")

        legacy = cok_client.CokClient(account={"pfId": "ewanqf:1084LEGACY"})
        assert legacy.account["platformToken"] == "1084LEGACY", legacy.account
        print("[PASS] 旧果盘账号可从 pfId 恢复缺失令牌")

        # Early Android packages saved empty protocol-wide fields. They must
        # inherit safe package defaults rather than overwrite them with blanks,
        # otherwise login looks successful while every later command times out.
        #
        # ⚠ 2026-11-12: 默认值**不能是脱敏占位符**。公开仓库里
        #   cok_client.ACCOUNT["baseActiveKey"] 是 "<baseActiveKey>" ——
        #   把它当默认值回填 = 给服务端发一个假字段, 服务端会丢弃所有
        #   加密指令(表现是"连上了但界面全空")。真值只能来自
        #   本地缓存/账号库(见 cok_accounts.public_fields)。
        repaired = cok_client.CokClient(account={
            "pfId": "ewanqf:1084PROFILE", "baseActiveKey": "",
            "parseRegisterId": "", "device_info": {},
        })
        assert not accounts.is_placeholder(repaired.account["baseActiveKey"]), \
            repaired.account["baseActiveKey"]
        assert repaired.account["parseRegisterId"]
        assert repaired.account["device_info"]
        # 有真值来源时必须回填**真值**
        accounts._save_public_cache({"baseActiveKey": "SEEDED_PUBLIC_KEY"})
        try:
            seeded = cok_client.CokClient(account={
                "pfId": "ewanqf:1084PROFILE", "baseActiveKey": "",
            })
            assert seeded.account["baseActiveKey"] == "SEEDED_PUBLIC_KEY", \
                seeded.account["baseActiveKey"]
        finally:
            try:
                os.remove(accounts.PUBLIC_FIELDS_FILE)
            except OSError:
                pass
        print("[PASS] 空协议公共字段会回填真值，旧安卓导入可继续使用")

        legacy_android_profile = cok_client.CokClient(account={
            "pfId": "ewanqf:1084PROFILE",
            "device_info": {"os_version": "Android"},
        })
        assert legacy_android_profile.account["device_info"]["os_version"] == \
            cok_client.ACCOUNT["device_info"]["os_version"]
        print("[PASS] 旧安卓设备画像的协议版本标记会迁移")

        rebuilt, _ = channel_login.build_account_from_pf_id(
            "ewanqf:1084MOVED",
            gamesvc={
                "ok": True,
                "gameUid": "200",
                "uuid": "moved-uuid",
                "zn": "COK2218",
                "serverId": "2218",
                "gamePort": 32181,
                "buildCode": "moved-build",
                "gameUserName": "Moved role",
            },
        )
        assert rebuilt["zn"] == "COK2218", rebuilt
        assert rebuilt["serverId"] == "2218", rebuilt
        assert rebuilt["port"] == 32181, rebuilt
        print("[PASS] 新导入账号保存服务端返回的实际区服")

        accounts.save_account({
            "pfId": "ewanqf:1084ZONE",
            "gameUid": "300",
            "deviceId": "device",
            "uuid": "old-uuid",
            "buildCode": "old-build",
            "signCode": "sign",
            "pf": "cn_ewanqf",
            "packageName": "com.hcg.cok.ewanqf.guopan",
            "zn": "COK2217",
            "serverId": "2217",
        })
        engine = cok_web.Engine.__new__(cok_web.Engine)
        engine.account_key = "300"
        engine.account_source = "账号库:旧区服号"
        engine.args = type("Args", (), {"account": None})()
        engine._apply_account_meta = lambda account, source: setattr(
            engine.args, "account", account)
        old_resolve = __import__("cok_gamesvc").resolve_character
        try:
            __import__("cok_gamesvc").resolve_character = lambda *_args, **_kwargs: {
                "ok": True,
                "gameUid": "300",
                "uuid": "new-uuid",
                "buildCode": "new-build",
                "zn": "COK2218",
                "serverId": "2218",
            }
            assert engine._refresh_registered_account_zone(
                "登录失败：账号区服不匹配（错误码 E003_ZONE_2218）")
        finally:
            __import__("cok_gamesvc").resolve_character = old_resolve
        repaired_zone = accounts.get_account("300")
        assert repaired_zone["zn"] == "COK2218", repaired_zone
        assert repaired_zone["serverId"] == "2218", repaired_zone
        assert repaired_zone["port"] == 32181, repaired_zone
        assert repaired_zone["uuid"] == "new-uuid", repaired_zone
        print("[PASS] E003_ZONE 会重新解析并修复已保存账号")

        accounts.save_account({
            "pfId": "ewanqf:1084PORT",
            "gameUid": "400",
            "deviceId": "device",
            "uuid": "same-uuid",
            "buildCode": "same-build",
            "signCode": "sign",
            "pf": "cn_ewanqf",
            "packageName": "com.hcg.cok.ewanqf.guopan",
            "zn": "COK2218",
            "serverId": "2218",
            "port": 32171,
        })
        engine.account_key = "400"
        old_resolve = __import__("cok_gamesvc").resolve_character
        try:
            __import__("cok_gamesvc").resolve_character = lambda *_args, **_kwargs: {
                "ok": True,
                "gameUid": "400",
                "uuid": "same-uuid",
                "buildCode": "same-build",
                "zn": "COK2218",
                "serverId": "2218",
            }
            assert engine._refresh_registered_account_zone("登录失败：服务器拒绝登录（错误码 COK8）")
        finally:
            __import__("cok_gamesvc").resolve_character = old_resolve
        repaired_port = accounts.get_account("400")
        assert repaired_port["port"] == 32181, repaired_port
        print("[PASS] COK8 也会修复迁服后遗留的游戏端口")

        args = type("Args", (), {
            "account": {"host": "zone.example", "port": 32181},
            "game_host": "default.example",
            "game_port": 32231,
            "host": "web.example",
            "port": 8770,
            "timeout": 10,
            "webhook": None,
            "webhook_type": "generic",
            "alert_rules": [],
            "log": None,
        })()
        original_client = cok_daemon.CokClient
        try:
            FakeGameClient.made = []
            cok_daemon.CokClient = FakeGameClient
            daemon = cok_daemon.Daemon(args)
            daemon.grab_init = lambda wait=3.0: []
            daemon.emit = lambda *_args, **_kwargs: None
            daemon.connect()
            assert FakeGameClient.made[-1].host == "zone.example"
            assert FakeGameClient.made[-1].port == 32181
        finally:
            cok_daemon.CokClient = original_client
        print("[PASS] 多账号连接优先使用账号自己的区服端口")
    finally:
        cok_web.channel = old_channel


if __name__ == "__main__":
    main()
