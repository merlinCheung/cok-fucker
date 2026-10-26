import json, sys
PROTO="/Users/a1234/workspace/me/cok/COK-CN1-analysis/protocol"
sys.path.insert(0,PROTO)
from cok_client import CokClient
import cok_account
acct=cok_account.load_account()
c=CokClient(account=acct, timeout=60.0)
c.connect(); c.login()
r=c.call("cemetery.get.info", {}, retries=2)
p=r.get("__params__") or r
print("=== cemetery.get.info 顶层 %d 键 ==="%len(p))
items=p.get("items")
print("items =", len(items) if isinstance(items,list) else p.get("items"))
if isinstance(items,list) and items:
    print("items[0] =", json.dumps(items[0],ensure_ascii=False))
    sp=json.load(open(PROTO+"/speedup-items.json"))
    byid={}
    for t2,g in sp['groups'].items():
        for it in g['items']:
            if it['id'] is not None: byid[str(it['id'])]=(t2,it['seconds'],g['label'])
    print("\n=== 背包里的加速道具 ===")
    n=0
    for it in items:
        iid=str(it.get('itemId'))
        if iid in byid and (it.get('count') or 0)>0:
            t2,sec,label=byid[iid]; n+=1
            print("  itemId=%-8s type2=%-3s %-6s count=%-5s uuid=%s"%(iid,t2,("%ss"%sec) if sec else "?",it.get('count'),it.get('uuid')))
    print("  可用加速道具条目:",n)
