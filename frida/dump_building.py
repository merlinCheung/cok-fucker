import json, sys
PROTO="/Users/a1234/workspace/me/cok/cok"
sys.path.insert(0,PROTO)
from cok_client import CokClient
import cok_account
acct=cok_account.load_account()
c=CokClient(account=acct, timeout=60.0)
c.connect(); c.login()
r=c.call("build.info",{},retries=1)
p=r.get("__params__") or r
bs=p.get("building") or []
print("building 数量:",len(bs))
if bs:
    print("字段全集:", sorted(bs[0].keys()))
    print()
    for b in bs[:12]:
        print("  ", {k:v for k,v in b.items() if k in
              ('uuid','buildingId','level','star','process','position','costTime','gold','isInstant',
               'type','opType','para1','building')})
