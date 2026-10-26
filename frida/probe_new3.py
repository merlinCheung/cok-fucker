import json, sys
PROTO="/Users/a1234/workspace/me/cok/COK-CN1-analysis/protocol"
sys.path.insert(0,PROTO)
from cok_client import CokClient
import cok_account
acct=cok_account.load_account()
CMDS=["onekeybuff.get","world.get.march","world.march","march.cancel","world.march.retreat",
      "world.get.detail","show.status.item","soldierHelp.info"]
for cmd in CMDS:
    try:
        c=CokClient(account=acct, timeout=45.0)
        c.connect(); c.login(); c.call("cmd.ping",{},retries=1)
        r=c.call(cmd,{},retries=1)
        p=r.get("__params__") or r
        s=json.dumps(p,ensure_ascii=False,default=str)
        print("\n### %s -> %s"%(cmd, s[:420]))
        try: c.close()
        except Exception: pass
    except Exception as e:
        print("\n### %s -> ERR %s"%(cmd,str(e)[:100]))
