import json, sys, time
PROTO="/Users/a1234/workspace/me/cok/COK-CN1-analysis/protocol"
sys.path.insert(0,PROTO)
from cok_client import CokClient
import cok_account
acct=cok_account.load_account()
c=CokClient(account=acct, timeout=25.0)
c.connect(); c.login()
print("[*] 登录完成, 收听 20 秒推送 ...")
c.sock.settimeout(20)
buf=b""
t0=time.time()
while time.time()-t0 < 20:
    try:
        chunk=c.sock.recv(65536)
    except Exception as e:
        print("   recv stop:", type(e).__name__); break
    if not chunk: break
    buf+=chunk
    # 尝试拆帧
    from cok_sfs import parse_packet
    i=0
    while i+3<=len(buf):
        flags=buf[i]; ln=(buf[i+1]<<8)|buf[i+2]
        if not (flags & 0x80) or ln==0 or i+3+ln>len(buf): break
        fr=buf[i:i+3+ln]
        try:
            fl,payload,obj,consumed=parse_packet(fr)
        except Exception as e:
            print("   parse err",e); break
        pp=c._resp_params(obj)
        rcmd=c._resp_cmd(obj)
        keys=[k for k in ('queue','items') if k in pp]
        print("   push cmd=%-22s keys=%d  %s"%(rcmd,len(pp),keys))
        # 解密混淆键(rlQW45Y 之类)
        for kk,vv in list(pp.items()):
            if isinstance(vv,str) and len(vv)>60 and kk!='qqq':
                try:
                    from cok_sfs import decode_params
                    o2,m2,raw=decode_params(bytes.fromhex(vv), c.key)
                    print("      >>> 解密 %s: mode=%s  共%d键"%(kk,m2,len(o2)))
                    print("          全部键:", sorted(o2.keys()))
                    for _k in ('items','queue','tools','toolList','itemList'):
                        if isinstance(o2.get(_k),list):
                            print("          %s = list(%d)  首条=%s"%(_k,len(o2[_k]),json.dumps(o2[_k][0],ensure_ascii=False)[:200] if o2[_k] else ''))
                    if 'queue' in o2 and isinstance(o2['queue'],list) and o2['queue']:
                        print("          queue[0] =", json.dumps(o2['queue'][0],ensure_ascii=False)[:220])
                        print("          queue 条数 =", len(o2['queue']))
                    if 'items' in o2 and isinstance(o2['items'],list) and o2['items']:
                        print("          items[0] =", json.dumps(o2['items'][0],ensure_ascii=False)[:220])
                        print("          items 条数 =", len(o2['items']))
                    pp = o2
                except Exception as e:
                    print("      解密 %s 失败: %s"%(kk,str(e)[:80]))
        for kk in list(pp.keys())[:6]:
            vv=pp[kk]
            if isinstance(vv,list): print("      %-22s list(%d)  %s"%(kk,len(vv),json.dumps(vv[0],ensure_ascii=False)[:220] if vv else ''))
            elif isinstance(vv,dict): print("      %-22s dict(%d) keys=%s"%(kk,len(vv),list(vv)[:12]))
            else: print("      %-22s %r"%(kk,str(vv)[:120]))
        if 'queue' in pp and isinstance(pp['queue'],list) and pp['queue']:
            print("      queue[0] =", json.dumps(pp['queue'][0],ensure_ascii=False)[:200])
        if 'items' in pp and isinstance(pp['items'],list) and pp['items']:
            print("      items[0] =", json.dumps(pp['items'][0],ensure_ascii=False)[:200])
        i+=3+ln
    buf=buf[i:]
