import json, sys
PROTO="/Users/a1234/workspace/me/cok/cok"
sys.path.insert(0,PROTO)
from cok_client import CokClient
import cok_account
acct=cok_account.load_account()
c=CokClient(account=acct, timeout=60.0)
c.connect()
res=c.login()
print("=== login() 返回类型 ===", type(res))
if isinstance(res,tuple):
    print("tuple len", len(res))
    for i,x in enumerate(res):
        if isinstance(x,(bytes,bytearray)):
            print("  [%d] bytes len=%d"%(i,len(x))); continue
        if isinstance(x,dict):
            print("  [%d] dict keys: %s"%(i, sorted(x.keys())))
            for k,v in x.items():
                sv=json.dumps(v,ensure_ascii=False,default=str)
                print("        %-26s %s"%(k, sv[:200]))
        else:
            print("  [%d] %s: %s"%(i, type(x).__name__, str(x)[:300]))
else:
    for k,v in res.items():
        print("  %-28s %s"%(k, json.dumps(v,ensure_ascii=False)[:200]))
