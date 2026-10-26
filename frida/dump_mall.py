import json, sys, collections
PROTO="/Users/a1234/workspace/me/cok/COK-CN1-analysis/protocol"
sys.path.insert(0,PROTO)
from cok_client import CokClient
import cok_account
acct=cok_account.load_account()
c=CokClient(account=acct, timeout=60.0)
c.connect(); c.login()
res=c.call("mall.info", {}, retries=1)
p=res.get("__params__") or res
malls=p.get("shoppingMall") or []
print("商城条目:", len(malls))
if malls:
    print("=== 字段全集 ===", sorted(malls[0].keys()))
    print()
    ids=sorted({str(m.get("item_id")) for m in malls})
    print("item_id 数量:", len(ids))
    pref=collections.Counter(i[:4] for i in ids)
    print("前缀分布:", dict(pref.most_common()))
    print()
    print("=== 全部条目(精简) ===")
    for m in malls:
        print("  id=%-9s sale_type=%-4s display=%-3s" % (m.get("item_id"), m.get("sale_type"), m.get("display")),
              {k:v for k,v in m.items() if k not in ("item_id","sale_type","display")})
