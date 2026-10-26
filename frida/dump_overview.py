import json, sys
PROTO="/Users/a1234/workspace/me/cok/COK-CN1-analysis/protocol"
sys.path.insert(0,PROTO)
from cok_client import CokClient
import cok_account
acct=cok_account.load_account()
c=CokClient(account=acct, timeout=60.0)
c.connect(); c.login()
r=c.call("overview_new.data", {}, retries=2)
p=r.get("__params__") or r
print("=== overview_new.data 顶层键 (%d) ==="%len(p))
for k in sorted(p.keys()):
    v=p[k]
    if isinstance(v,list): print("  %-24s list(%d)"%(k,len(v)))
    elif isinstance(v,dict): print("  %-24s dict(%d)"%(k,len(v)))
    else: print("  %-24s %r"%(k,str(v)[:50]))
