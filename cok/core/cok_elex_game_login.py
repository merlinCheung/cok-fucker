#!/usr/bin/env python3
"""最后一步: 用 elex 账号(手机号+密码)在 PC 上直接登录游戏服。

链路(2026-10-28 静态逆出 + 实测):
    手机号+密码
      → POST https://accountapi1.elexapp.com/services/v1/user/login/10001001
         (签名/密码哈希见 cok_elex_account.py)
      → 拿到 elex uid + token
      → 游戏服登录参数: pfId="elextech:<uid>"  platformToken=<token>
      → bin 握手 → 登录 → 派生会话密钥

为什么 pfId 是 "elextech:<uid>":
    com.clash.of.kings.COK_CN1$1.onLoginSuccess(userId)
        → Native.nativeSetPlatformUID("elextech:" + userId)

本脚本**不写任何账号库**, 只做只读探测(登录 + 立刻断开), 不会动已有账号。
⚠️ 如果 elex 账号已绑定游戏角色, 首次登录会把该角色拉上线(会顶掉手机 App 的连接)。

用法:
    python3 cok_elex_game_login.py <手机号> <密码>
    python3 cok_elex_game_login.py <手机号> <密码> --pf cn_cn1,cn1,elextech
"""
# --- 包自举: 让本文件既能 `python3 cok/core/xxx.py` 直接跑, 也能被平铺 import ---
import os as _os
import sys as _sys

_PKG_ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
if _os.path.isdir(_PKG_ROOT) and _PKG_ROOT not in _sys.path:
    _sys.path.insert(0, _PKG_ROOT)
_CORE = _os.path.join(_PKG_ROOT, "core")
if _os.path.isdir(_CORE) and _CORE not in _sys.path:
    _sys.path.insert(0, _CORE)

import argparse
import json
import os
import sys
import time
import uuid

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # noqa: E402
from cok_client import CokClient, CokError, ACCOUNT  # noqa: E402
from cok_sfs import TypedInt, SFS_INT  # noqa: E402
import cok_elex_account as elex  # noqa: E402

#: com.hcg.cok.cn1 官方包证书派生(openssl pkcs7 → cert.der → sign_code_from_cert)
CN1_SIGN_CODE = "df0b8b7ab5a75e84f8f7cfccd0a5d165"
CN1_PACKAGE = "com.hcg.cok.cn1"

#: pf 候选: PublishImpl.getPublishChannel() == "cn1", 而 nearme/ewanqf 实测是 "cn_<渠道>"
PF_CANDIDATES = ("cn_cn1", "cn1", "elextech", "cn_elextech")


def try_game_login(pf_id, platform_token, pf, game_uid="", sign_code=CN1_SIGN_CODE,
                   package=CN1_PACKAGE, timeout=25.0):
    """用 elex 身份试登录游戏服, 返回 (结果描述, 详情)。"""
    acc = dict(ACCOUNT)
    acc.update({
        "pfId": pf_id,
        "platformToken": platform_token,
        "pf": pf,
        "packageName": package,
        "signCode": sign_code,
        "gameUid": str(game_uid or ""),
        "deviceId": uuid.uuid4().hex[:16],
        "uuid": "cok" + uuid.uuid4().hex,
        "device_info": dict(ACCOUNT["device_info"]),
        "gmLogin": TypedInt(0, SFS_INT),
    })
    c = CokClient(timeout=timeout, account=acc)
    try:
        c.connect()
        c.bin_handshake()
        c.login()
        return "登录成功", {"key_id": c.key_id}
    except CokError as e:
        msg = str(e)
        if "连接被服务端关闭" in msg:
            return "断连(可能被踢/同账号在线)", msg[:200]
        return "失败", msg[:300]
    except Exception as e:  # noqa: BLE001
        return "异常", str(e)[:200]
    finally:
        c.close()


def elex_login_and_token(phone, password):
    """elex 登录 -> 换会话, 返回 (uid, token, 全部原始响应)。

    客户端流程(PhoneLoginActivity$4.onResponse):
      1) POST /services/v1/user/login/10001001  -> body {uid, t, token}
      2) POST /services/v1/user/token/10001001  {accountType,mobile,countryCode,token,t,uid}
         -> body = 用户信息 + 正式 token
    """
    res1 = elex.phone_login(phone, password)
    out = {"login": res1}
    body = res1.get("body") if isinstance(res1, dict) else None
    if not isinstance(body, dict):
        return None, None, out
    uid = body.get("uid")
    t = body.get("t")
    tok = body.get("token")
    if uid and tok and t:
        res2 = elex.call(elex.PATH_TOKEN, {
            "accountType": 1, "mobile": phone, "countryCode": "86",
            "token": tok, "t": t, "uid": uid})
        out["token_exchange"] = res2
        b2 = res2.get("body") if isinstance(res2, dict) else None
        if isinstance(b2, dict):
            out["token_body"] = b2
            uid = b2.get("uid") or uid
            tok = b2.get("token") or tok
    return uid, tok, out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("phone")
    ap.add_argument("password")
    ap.add_argument("--pf", default=",".join(PF_CANDIDATES), help="pf 候选(逗号分隔)")
    ap.add_argument("--gameuid", default="", help="gameUid(留空=让服务端按 elex 身份找角色)")
    args = ap.parse_args()

    print("[1] elex 账号登录 ...")
    uid, token, raw = elex_login_and_token(args.phone, args.password)
    print(json.dumps(raw, ensure_ascii=False, indent=2)[:2000])
    if not uid or not token:
        print("[!] 没拿到 uid/token, elex 登录失败(见上)")
        return 1

    pf_id = "elextech:%s" % uid
    print("\n[2] uid=%r token=%r" % (uid, (token or "")[:12] + "..."))
    print("\n[3] 游戏服登录试探 (pfId=%s)" % pf_id)
    for pf in [p for p in args.pf.split(",") if p]:
        print("  --- pf=%s" % pf)
        desc, detail = try_game_login(pf_id, token, pf, game_uid=args.gameuid)
        print("      %s  %s" % (desc, detail))
        if desc == "登录成功":
            break
        time.sleep(0.5)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
