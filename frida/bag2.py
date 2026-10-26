import json, sys, time
PROTO="/Users/a1234/workspace/me/cok/COK-CN1-analysis/protocol"
sys.path.insert(0,PROTO)
from cok_client import CokClient
from cok_sfs import decode_params
import cok_account
acct=cok_account.load_account()
c=CokClient(account=acct, timeout=25.0)
c.connect(); c.login()
# 先把 init 推送吃掉
c.sock.settimeout(8); buf=b""
try:
    while True:
        ch=c.sock.recv(65536)
        if not ch: break
        buf+=ch
except Exception: pass
from cok_sfs import parse_packet
i=0; init=None
while i+3<=len(buf):
    flags=buf[i]; ln=(buf[i+1]<<8)|buf[i+2]
    if not (flags&0x80) or ln==0 or i+3+ln>len(buf): break
    try:
        fl,pl,obj,cons=parse_packet(buf[i:i+3+ln])
    except Exception: break
    pp=c._resp_params(obj); rcmd=c._resp_cmd(obj)
    if rcmd=='init':
        for k,v in pp.items():
            if isinstance(v,str) and len(v)>60 and k!='qqq':
                o2,m2,raw=decode_params(bytes.fromhex(v), c.key); init=o2
    i+=3+ln
if init:
    st=init.get('storage'); stt=init.get('storageTotal')
    print("init.storage type=%s len=%s"%(type(st).__name__, len(st) if hasattr(st,'__len__') else '-'))
    print("init.storageTotal =", json.dumps(stt,ensure_ascii=False)[:300])
    if isinstance(st,dict):
        ks=list(st.items())[:6]
        for k,v in ks: print("   storage[%s] = %r"%(k,v))
print()
print("[*] 先 ping 再请求 cemetery.get.info ...")
try:
    r=c.call("cmd.ping",{},retries=1); print("  ping OK")
except Exception as e: print("  ping ERR",str(e)[:80])
try:
    r=c.call("cemetery.get.info",{},retries=1)
    p=r.get("__params__") or r
    print("  cemetery.get.info OK, 顶层 %d 键"%len(p))
    items=p.get('items')
    print("  items =", len(items) if isinstance(items,list) else '-')
    if isinstance(items,list) and items:
        sp=json.load(open(PROTO+"/speedup-items.json"))
        byid={}
        for t2,g in sp['groups'].items():
            for it in g['items']:
                if it['id'] is not None: byid[str(it['id'])]=(t2,it['seconds'],g['label'])
        for it in items:
            iid=str(it.get('itemId'))
            if iid in byid and (it.get('count') or 0)>0:
                t2,sec,label=byid[iid]
                print("   itemId=%-8s type2=%-3s %-6s count=%-5s uuid=%s"%(iid,t2,("%ss"%sec) if sec else "?",it.get('count'),it.get('uuid')))
except Exception as e:
    print("  cemetery.get.info ERR", str(e)[:120])
