"""P0080 frozen telemetry. FC04 only; reading raw400 captures a new image.
Scheduler-owned cached samples; physical sensor measurements remain asynchronous.
"""
import argparse,json
from datetime import datetime,timezone
from read_mvp import NAMES,request_block,signed32

def read_snapshot(read,attempts=3):
    """read(address,count)->words. Detect replacement by another reader."""
    if not 1<=attempts<=10:raise ValueError('attempts 1..10')
    def block(a,n):
        w=read(a,n)
        if not isinstance(w,(list,tuple)) or len(w)!=n or any(type(x) is not int or not 0<=x<=65535 for x in w):raise ValueError('invalid register reply')
        return list(w)
    for _ in range(attempts):
        stamp=datetime.now(timezone.utc).isoformat();h=block(400,8);seq=h[2]<<16|h[3]
        if h[:2]!=[0x5380,1] or not seq or h[4] not in (0,1) or h[5:]!=[20,0,0]:raise ValueError('snapshot header unsupported')
        data=[]
        for a in range(408,528,16):data+=block(a,min(16,528-a))
        if block(402,2)!=h[2:4]:continue
        samples={}
        for i,name in enumerate(NAMES):
            w=data[6*i:6*i+6];v=signed32(w[0],w[1]);status=w[2]
            if status>4 or ((v==-(1<<31)) != (status!=1)):raise ValueError('inconsistent snapshot record')
            samples[name]={'value':v if status==1 else None,'status':status,'age_ms':w[3]<<16|w[4],'generation':w[5]}
        return {'captured_at_host':stamp,'sequence':seq,'link_lost':bool(h[4]),'samples':samples}
    raise RuntimeError('snapshot replaced by another reader; retry limit reached')
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--host',required=True);p.add_argument('--slave',type=int,default=1);a=p.parse_args()
    print(json.dumps(read_snapshot(lambda x,n:request_block(a.host,x,n,a.slave)['values']),indent=2))
