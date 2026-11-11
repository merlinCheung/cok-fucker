#!/usr/bin/env python3
"""COK 多账号注册表。

把若干个账号的凭据(就是 cok_account.load_account() / cok_client.ACCOUNT 那种
dict)存成磁盘上的 JSON, 统一按 **gameUid** 作为账号 id 管理, 并给每个账号
一个独立的数据目录(坐标索引 / 扫描历史 / 导出表都各存各的, 互不覆盖)。

目录布局::

    protocol/
      accounts/
        <gameUid>.json          每个账号一份凭据(load_account 的产物 + label)
        .active                 当前选中的账号 id(纯文本一行)
      data/
        <gameUid>/              该账号的运行时数据
          map-index.json
          scan-history.json
          ...

凭据 JSON 里除了协议字段外, 额外约定两个元字段:
    label    友好名(页面显示用; 不填则回退到 roleName / gameUid)
    added    首次写入时间戳(ISO)

设计要点:
  * 账号 id 一律用 gameUid(服务端唯一), 不用 label —— label 可以重名/改名。
  * 读写都走原子替换(tmp + os.replace), 避免并发写坏文件。
  * 这个模块**只管存储与路径**, 不碰网络, 也不碰账号锁 —— 锁在 cok_client。
"""
import json
import os
import re
import time

HERE = os.path.dirname(os.path.abspath(__file__))

#: 账号注册表根目录(可用环境变量覆盖, 方便测试用临时目录)
ACCOUNTS_DIR = os.environ.get(
    "COK_ACCOUNTS_DIR", os.path.join(HERE, "accounts"))

#: 每账号运行时数据根目录
DATA_ROOT = os.environ.get(
    "COK_DATA_ROOT", os.path.join(HERE, "data"))

#: 记录"当前选中账号 id"的文件
ACTIVE_FILE = os.path.join(ACCOUNTS_DIR, ".active")

#: 账号 id(gameUid)应当是纯数字; 清洗成安全文件名, 兜底别的字符
_SAFE_RE = re.compile(r"[^0-9A-Za-z_-]")


def account_key(acc):
    """从账号 dict 里取出账号 id(gameUid)。"""
    if not isinstance(acc, dict):
        return ""
    return str(acc.get("gameUid") or "").strip()


def safe_key(key):
    """把账号 id 清洗成安全的文件名片段。"""
    return _SAFE_RE.sub("_", str(key or "").strip()) or "default"


def account_label(acc):
    """账号的友好显示名: label -> roleName -> gameUid。"""
    if not isinstance(acc, dict):
        return ""
    return str(acc.get("label") or acc.get("roleName")
               or acc.get("gameUid") or "").strip()


def _ensure_dir(path):
    try:
        os.makedirs(path, exist_ok=True)
    except OSError:
        pass


def _atomic_write_json(path, obj):
    _ensure_dir(os.path.dirname(path))
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, ensure_ascii=False, indent=1)
    os.replace(tmp, path)


def _account_path(key):
    return os.path.join(ACCOUNTS_DIR, "%s.json" % safe_key(key))


def data_dir(key):
    """返回某账号的运行时数据目录(按需创建)。"""
    d = os.path.join(DATA_ROOT, safe_key(key))
    _ensure_dir(d)
    return d


def data_path(key, name):
    """某账号数据目录下的某个文件路径(如 map-index.json)。"""
    return os.path.join(data_dir(key), name)


def list_accounts(owner=None):
    """列出已注册账号, 返回 [{key,label,roleName,gameUid,...}], 按 label 排序。

    owner 给了就**只返回该用户名下的账号**(多用户隔离)。
    """
    out = []
    try:
        names = sorted(os.listdir(ACCOUNTS_DIR))
    except OSError:
        return out
    for fn in names:
        if not fn.endswith(".json") or fn.startswith("."):
            continue
        try:
            with open(os.path.join(ACCOUNTS_DIR, fn), encoding="utf-8") as fh:
                acc = json.load(fh)
        except (OSError, ValueError):
            continue
        key = account_key(acc) or fn[:-5]
        if owner is not None and (acc.get("owner") or "") != (owner or ""):
            continue
        out.append({
            "key": key,
            "label": account_label(acc) or key,
            "roleName": acc.get("roleName", ""),
            "gameUid": acc.get("gameUid", ""),
            "host": acc.get("host", ""),
            "zn": acc.get("zn", ""),
            "added": acc.get("added", ""),
            "owner": acc.get("owner", ""),
        })
    out.sort(key=lambda a: (a["label"] or "").lower())
    return out


def _template_account():
    """内置凭据模板(cok_client.ACCOUNT) —— 公共字段的兜底。

    账号库里存的是**完整凭据**: 渠道包读到的字段覆盖模板, 模板补齐
    服务器地址 / 协议版本 / baseActiveKey / device_info 这些公共字段。
    """
    try:
        from cok_client import ACCOUNT
        return dict(ACCOUNT)
    except Exception:  # noqa: BLE001
        return {}


def _apply_types(acc):
    """把读出来的账号凭据贴回 SFS 整数类型。

    ⚠️ TypedInt 是 int 的子类, **JSON 存盘会把它退化成裸 int**。再读回来时
    SFS 编码按值大小选类型(gmLogin 0 -> BYTE, screen_h 2577 -> SHORT),
    服务端对登录参数类型敏感, 类型一错就拒登(响应 id 是数字 + init.error)。
    所以账号库里读出来的凭据必须重新贴类型, 否则存过的号一个都登不上。
    """
    if not isinstance(acc, dict):
        return acc
    try:
        from cok_client import ACCOUNT
        from cok_sfs import restore_typed_fields
        return restore_typed_fields(acc, ACCOUNT)
    except Exception:  # noqa: BLE001
        return acc


def get_account(key):
    """读取某账号的完整凭据 dict; 不存在返回 None。"""
    p = _account_path(key)
    try:
        with open(p, encoding="utf-8") as fh:
            return _apply_types(json.load(fh))
    except (OSError, ValueError):
        return None


def _adopt_legacy_data(key):
    """账号首次入库时, 把**协议根目录的历史数据**接管到它自己的数据目录。

    为什么需要: 多账号之前, 所有数据(map-index.json / scan-history.json)
    都写在 protocol/ 根目录 —— 那是"当前那个号"的数据。账号一旦入库就会被
    隔离到 data/<gameUid>/, 根目录那份就成了没人读的孤儿(之前扫了几小时的
    地图索引白白看不见了)。

    规则: 只在"**还没有任何账号接管过**"时才接管, 且目标账号的数据目录里
    还没有 map-index.json —— 避免覆盖别的账号的数据, 也避免重复接管。
    """
    try:
        target = data_dir(key)
        root_index = os.path.join(HERE, "map-index.json")
        if os.path.exists(os.path.join(target, "map-index.json")):
            return []                       # 已经有自己的索引了, 不动
        if not os.path.exists(root_index):
            return []
        # 别的账号已经接管过了 -> 根目录这份不是它的
        for a in list_accounts():
            if a.get("key") == key:
                continue
            other = data_dir(a["key"])
            if os.path.exists(os.path.join(other, "map-index.json")):
                return []
        moved = []
        for name in ("map-index.json", "scan-history.json"):
            src = os.path.join(HERE, name)
            dst = os.path.join(target, name)
            if os.path.exists(src) and not os.path.exists(dst):
                os.replace(src, dst)
                moved.append(name)
        return moved
    except Exception:  # noqa: BLE001
        return []


def probe_pf(acc, timeout=20):
    """用**真实登录**实测出这个账号可用的 pf。

    为什么需要: pf 是**每账号**的字段, 且服务端**会校验**它 ——
    2026-10-29 实测(鸭皇号 nearme:g1372…):
        pf=cn_nearme  -> 登录成功
        pf=nearme / cn_ewanqf / 乱填 -> E002
    所以"cn_<渠道段>"只是归纳, 不可当准 —— 让服务器自己告诉我们。

    返回 (ok: bool, pf: str|None)。
    ⚠️ 每试一个候选就是一次真实登录, 会顶掉该账号在手机/其它地方的连接;
      账号正被占用(AccountBusy)时直接放弃, 不抢。
    """
    from cok_client import CokClient, CokError, account_lock, apply_account_types
    cands = []
    for pf in list(acc.get("pfCandidates") or []) + [acc.get("pf")]:
        if pf and pf not in cands:
            cands.append(pf)
    key = str(acc.get("gameUid") or "")
    try:
        with account_lock(timeout=3, purpose="probe pf", key=key):
            for pf in cands:
                a = apply_account_types(dict(acc))
                a["pf"] = pf
                c = CokClient(timeout=timeout, account=a)
                try:
                    c.connect()
                    c.bin_handshake()
                    c.login()
                    return True, pf
                except Exception:  # noqa: BLE001
                    pass
                finally:
                    c.close()
    except Exception as e:  # noqa: BLE001
        if "占用" in str(e):
            raise
        return False, None
    return False, None


def save_account(acc, label=None, owner=None):
    """把一份账号凭据写入注册表, 以 gameUid 为 id。返回账号 id。

    已存在同 id 时**合并**(新值覆盖旧值), 保留原有 added / label(除非显式传 label)。

    存进去的是**完整凭据**: 先垫上 cok_client.ACCOUNT 模板(服务器地址 / 协议
    版本 / baseActiveKey / device_info 等公共字段), 再覆盖渠道包读到的字段。
    这样账号库里存的号**不依赖设备**也能直接登录。

    owner: 归属的用户名(多用户隔离)。已存在的号若已有归属且这次没给 owner,
    则**保留原归属**(不因为重新采集就把别人的号抢走)。
    """
    key = account_key(acc)
    if not key:
        raise ValueError("账号缺少 gameUid, 无法入库")
    existing = get_account(key) or {}
    merged = _template_account()
    merged.update({k: v for k, v in existing.items() if v is not None})
    merged.update({k: v for k, v in acc.items() if v is not None})
    if label is not None:
        merged["label"] = label
    elif not merged.get("label"):
        merged["label"] = account_label(acc) or key
    if owner is not None:
        merged["owner"] = owner
    elif not merged.get("owner"):
        merged["owner"] = ""
    if not merged.get("added"):
        merged["added"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    _atomic_write_json(_account_path(key), merged)
    _adopt_legacy_data(key)
    return key


def owner_of(key):
    """某个账号的归属用户名(没有归属返回 "")。"""
    acc = get_account(key) or {}
    return acc.get("owner", "") or ""


def remove_account(key, owner=None):
    """从注册表删除一个账号(不动它的 data 目录)。返回是否删到。

    owner 给了就只允许删**该用户名下**的号(多用户隔离)。
    """
    if owner is not None and owner_of(key) != (owner or ""):
        return False
    p = _account_path(key)
    try:
        os.remove(p)
        return True
    except OSError:
        return False


def set_label(key, label):
    """改某账号的显示名。"""
    acc = get_account(key)
    if acc is None:
        return False
    acc["label"] = label
    _atomic_write_json(_account_path(key), acc)
    return True


def get_active_key(owner=None):
    """读当前选中账号 id; 没有则回退到注册表第一个; 再没有返回 ""。

    owner 给了就**按人**存/取(多用户隔离, 见 cok_users.get_active)。
    """
    if owner is not None:
        import cok_users
        k = cok_users.get_active(owner)
        if k and get_account(k) is not None:
            return k
        accs = list_accounts(owner=owner)
        return accs[0]["key"] if accs else ""
    try:
        with open(ACTIVE_FILE, encoding="utf-8") as fh:
            k = fh.read().strip()
        if k and get_account(k) is not None:
            return k
    except OSError:
        pass
    accs = list_accounts()
    return accs[0]["key"] if accs else ""


def set_active_key(key, owner=None):
    """把某账号设为当前选中(写入 .active)。key 必须已注册。"""
    if get_account(key) is None:
        raise ValueError("账号未注册: %s" % key)
    if owner is not None:
        import cok_users
        cok_users.set_active(owner, key)
        return key
    _ensure_dir(ACCOUNTS_DIR)
    tmp = ACTIVE_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        fh.write(str(key) + "\n")
    os.replace(tmp, ACTIVE_FILE)
    return key


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser(description="COK 多账号注册表")
    sub = ap.add_subparsers(dest="cmd")

    sub.add_parser("ls", help="列出已注册账号")

    p_add = sub.add_parser("add", help="从设备读取账号并入库")
    p_add.add_argument("--label", help="友好名")
    p_add.add_argument("--from", dest="src", default="device",
                       help="device(默认, 从设备读) 或 JSON 文件路径")
    p_add.add_argument("-p", "--package",
                       help="指定渠道包名(默认用 cok_account.PKG)")
    p_add.add_argument("--all", action="store_true",
                       help="把设备上**所有** COK 渠道包的账号都入库")
    p_add.add_argument("--no-probe", action="store_true",
                       help="不实测 pf(默认会登录实测确定 pf)")

    p_rm = sub.add_parser("rm", help="删除一个账号")
    p_rm.add_argument("key")

    p_use = sub.add_parser("use", help="设为当前账号")
    p_use.add_argument("key")

    p_lbl = sub.add_parser("label", help="改显示名")
    p_lbl.add_argument("key")
    p_lbl.add_argument("label")

    args = ap.parse_args(argv)

    if args.cmd == "ls" or args.cmd is None:
        active = get_active_key()
        for a in list_accounts():
            mark = "*" if a["key"] == active else " "
            print("%s %-18s %-16s %s" % (mark, a["key"], a["label"], a["host"]))
        return 0
    if args.cmd == "add":
        if args.src == "device":
            from cok_account import load_account as _la
            from cok_account import load_previous_account as _lp_prev
            from cok_account import list_packages as _lp
            pkgs = (_lp() if args.all else [args.package])
            if not pkgs:
                print("设备上没有找到 COK 包")
                return 1
            added = []
            for pkg in pkgs:
                cands = []
                try:
                    cands.append(_la(pkg))
                except Exception as e:  # noqa: BLE001
                    print("[!] %s 读取失败: %s" % (pkg, str(e)[:100]))
                try:
                    prev = _lp_prev(pkg)
                    if prev:
                        cands.append(prev)
                except Exception:  # noqa: BLE001
                    pass
                for acc in cands:
                    if not acc.get("gameUid"):
                        print("[!] %s 没读到 gameUid, 跳过(App 登录过?)" % pkg)
                        continue
                    tag = "上一个号" if acc.get("isPrevious") else "当前号"
                    # pf 服务端会校验, 用登录实测确定(失败也不影响入库)
                    if not args.no_probe:
                        try:
                            ok, pf = probe_pf(acc)
                        except Exception as e:  # noqa: BLE001
                            ok, pf = False, None
                            print("[!] %s pf 探测跳过: %s" % (pkg, str(e)[:80]))
                        if ok:
                            acc["pf"] = pf
                            acc["pfVerified"] = True
                            print("   pf 实测确定: %s" % pf)
                        else:
                            acc["pfVerified"] = False
                            print("   [!] pf 实测失败, 保留候选值 %s" % acc.get("pf"))
                    key = save_account(acc, label=args.label if len(pkgs) == 1 else None)
                added.append(key)
                print("已入库: %s (%s)  <- %s"
                      % (key, account_label(get_account(key)), pkg))
            if added and not get_active_key():
                set_active_key(added[0])
            return 0 if added else 1
        with open(args.src, encoding="utf-8") as fh:
            acc = json.load(fh)
        key = save_account(acc, label=args.label)
        if not get_active_key():
            set_active_key(key)
        print("已入库: %s (%s)" % (key, account_label(get_account(key))))
        return 0
    if args.cmd == "rm":
        print("已删除" if remove_account(args.key) else "没找到", args.key)
        return 0
    if args.cmd == "use":
        set_active_key(args.key)
        print("当前账号 ->", args.key)
        return 0
    if args.cmd == "label":
        print("已改名" if set_label(args.key, args.label) else "没找到", args.key)
        return 0
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
