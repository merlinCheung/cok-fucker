"""找哪个只读命令返回 items(背包) 与 queue(队列)。"""
import json, sys
PROTO="/Users/a1234/workspace/me/cok/COK-CN1-analysis/protocol"
sys.path.insert(0,PROTO)
from cok_client import CokClient
import cok_account
acct=cok_account.load_account()
CMDS=["overview_new.data","stat.tt","build.info","accountLock.getUnlockView","allianceNewBoss.bossMainInfo"]
for cmd in CMDS:
    try:
        c=CokClient(account=acct, timeout=30.0)
        c.connect(); c.login(); c.call("cmd.ping",{},retries=0)
        r=c.call(cmd,{},retries=0)
        p=r.get("__params__") or r
        if not isinstance(p,dict):
            print("\n### %s -> 非 dict"%cmd); continue
        has=[]
        for k in ("items","queue","buildingQueue","queueList","toolList","equip"):
            if k in p:
                v=p[k]
                has.append("%s(%s)"%(k, len(v) if isinstance(v,list) else type(v).__name__))
        print("\n### %s -> keys=%d  关键字段: %s"%(cmd,len(p),", ".join(has) or "无"))
        if isinstance(p.get("items"),list) and p["items"]:
            print("    items[0] =", json.dumps(p["items"][0],ensure_ascii=False)[:200])
        if isinstance(p.get("queue"),list) and p["queue"]:
            print("    queue[0] =", json.dumps(p["queue"][0],ensure_ascii=False)[:200])
        try: c.close()
        except Exception: pass
    except Exception as e:
        print("\n### %s -> ERR %s"%(cmd,str(e)[:90]))
