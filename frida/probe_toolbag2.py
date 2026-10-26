"""每个命令之间重连, 找返回道具实例 uuid 的接口。"""
import json, re, sys
PROTO="/Users/a1234/workspace/me/cok/COK-CN1-analysis/protocol"
sys.path.insert(0,PROTO)
from cok_client import CokClient
import cok_account
HEX=re.compile(r'\b[0-9a-f]{32}\b')
acct=cok_account.load_account()
CMDS=["hot.item.get","hot.item.v2.get","item.compose","item.buyUse","create.tool",
      "outland.item.list","equip.bag.show.des","tool.queue.buy","queue.tool",
      "formationTrain.bag","item.buy","itemcollection.data"]
for cmd in CMDS:
    try:
        c=CokClient(account=acct, timeout=25.0)
        c.connect(); c.login(); c.call("cmd.ping",{},retries=0)
        r=c.call(cmd,{},retries=0)
        p=r.get("__params__") or r
        s=json.dumps(p,ensure_ascii=False,default=str)
        hexes=sorted(set(HEX.findall(s)))
        print("\n### %s"%cmd)
        print("    len=%d  32hex=%d %s"%(len(s), len(hexes), hexes[:6]))
        if hexes or len(s)>120:
            print("    ", s[:700])
        try: c.close()
        except Exception: pass
    except Exception as e:
        print("\n### %s -> ERR %s"%(cmd,str(e)[:90]))
