import json, sys, random, time
PROTO="/Users/a1234/workspace/me/cok/COK-CN1-analysis/protocol"
sys.path.insert(0,PROTO)
import cok_client
from cok_client import CokClient, TypedInt
from cok_sfs import derive_login_fields
import cok_account

def patched(self):
    acc=self.account; t=int(time.time()); self.seq+=1
    d=derive_login_fields(t, acc["gameUid"], acc["appVersion"], acc.get("signCode"), acc.get("buildCode"))
    params={"appVersion":acc["appVersion"],"luaVersion":acc["luaVersion"],"pfId":acc["pfId"],
        "gaid":acc["gaid"],"isHDLogin":acc["isHDLogin"],"pfchild":acc["pfchild"],
        "signCode":d["signCode"],"buildCode":d["buildCode"],"deviceId":acc["deviceId"],
        "isSmall":acc["isSmall"],"uuid":acc["uuid"],"serverId":acc["serverId"],
        "phoneDevice":acc["phoneDevice"],"gmUid":acc["gmUid"],"packageName":acc["packageName"],
        "lang":acc["lang"],"SecurityCode":d["SecurityCode"],"cc":d["cc"],
        "fromCountry":acc["fromCountry"],"gmLogin":acc["gmLogin"],"cmdBaseTime":str(t),
        "subscriberId":acc["subscriberId"],"gameUid":str(acc["gameUid"]),
        "newbasekey":"%032x"%random.getrandbits(128),"afUID":acc["afUID"],
        "googlePlay":acc["googlePlay"],"pfSign":acc["pfSign"],"platformToken":acc["platformToken"],
        "device_info":acc["device_info"],"parseRegisterId":acc["parseRegisterId"],
        "_cok_":"%06d%06d"%(self.cok_prefix,self.seq),"pf":acc["pf"],"channelSign":acc["channelSign"],
        "baseActiveKey":acc["baseActiveKey"],"linkname":acc["linkname"],"region":acc["region"],
        "instantAppCookie":acc["instantAppCookie"]}
    env={"p":{"p":params,"zn":acc["zn"],"pw":acc["pw"],"un":str(acc["gameUid"])},
         "a":TypedInt(1,0x03),"c":TypedInt(0,0x02)}
    self._send_frame(env)
    flags,obj,f=self._recv_frame()
    lp=self._resp_params(obj)
    self.LP=lp
    self.key,self.key_id=cok_client.derive_session_key(lp["id"])
    return self.key,self.key_id
CokClient.login=patched
acct=cok_account.load_account()
c=CokClient(account=acct, timeout=60.0)
c.connect(); c.login()
lp=c.LP
print("=== 登录响应 %d 键 ==="%len(lp))
for k in sorted(lp.keys()):
    v=lp[k]
    if isinstance(v,list): print("  %-26s list(%d)"%(k,len(v)))
    elif isinstance(v,dict): print("  %-26s dict(%d)"%(k,len(v)))
    else: print("  %-26s %r"%(k,str(v)[:40]))
print()
for k in ('queue','items'):
    if isinstance(lp.get(k),list) and lp[k]:
        print("--- %s[0] ---"%k); print(json.dumps(lp[k][0],ensure_ascii=False)[:300])
