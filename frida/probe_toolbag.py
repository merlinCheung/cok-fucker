"""探测哪个命令返回玩家道具持有量。"""
import json, sys
PROTO="/Users/a1234/workspace/me/cok/COK-CN1-analysis/protocol"
sys.path.insert(0,PROTO)
from cok_client import CokClient
import cok_account
acct=cok_account.load_account()
c=CokClient(account=acct, timeout=45.0)
c.connect(); c.login(); c.call("cmd.ping",{},retries=0)
CMDS=["hot.item.get","hot.item.v2.get","item.buyUse","item.compose","tool.queue.buy",
      "queue.tool","formationTrain.bag","outland.item.list","equip.bag.show.des"]
for cmd in CMDS:
    try:
        r=c.call(cmd,{},retries=0)
        p=r.get("__params__") or r
        s=json.dumps(p,ensure_ascii=False,default=str)
        print("\n### %s -> %s"%(cmd, s[:500]))
    except Exception as e:
        print("\n### %s -> ERR %s"%(cmd,str(e)[:120]))
