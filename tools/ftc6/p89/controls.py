"""P0089 pure, bounded FTC20.01 state models; NOT live controllers."""
LOOKUP=(10,1,2,3,4,5,6,7,8,9,0)
def byte(x):
    if not isinstance(x,int) or not 0<=x<=255:raise ValueError('byte required')
    return x

def ownership(owner,request=False,release=False,peer_release=False,system=1,override=0,watchdog=0):
    allowed=system not in (2,3) and override!=1 and watchdog==0
    if owner==0:return int(allowed and request)
    if owner==1:return int(not (release or peer_release or not allowed))
    return 0

def inhibit_status(owner,local,remote,previous):
    for x in (owner,local,remote,previous):byte(x)
    return local if owner==0 else remote if owner==1 else previous

def inhibit_write(remote,enable,values):
    byte(remote);byte(enable)
    if len(values)!=5:raise ValueError('five fields required')
    for i,v in enumerate(values):
        byte(v)
        if enable&(1<<(i+2)) and v in (0,1):remote=(remote&~(1<<i))|(v<<i)
    return remote

def counter_step(counter,state,enabled,value):
    byte(counter);byte(value)
    if enabled and value==1:return ((counter+1)&255,1)
    if enabled and value==0:return (0,0)
    return counter,state

def demand_selection(previous,enabled,value,override,native,peer):
    for x in (previous,value,native,peer):byte(x)
    stored=LOOKUP[value if value<=10 else 0]*10 if enabled else previous
    active=100 if override else stored
    selected=min(100,native,active,peer)
    return dict(stored=stored,active=active,selected=selected,get05_p5=LOOKUP[min(selected//10,10)])

def target35(payload,profile,prior):
    if len(payload)!=16 or payload[0]!=0x35:raise ValueError('SET35 payload required')
    result=dict(prior)
    if profile==2 or payload[3] not in (0,1):return result
    for zone,pos,mask in [(0,4,2),(1,6,8)]:
        value=int.from_bytes(payload[pos:pos+2],'big')
        if payload[1]&mask and value!=65535:result[(payload[3],zone)]=value
    return result

def scaled_temperature(raw):
    if not isinstance(raw,int) or not 0<=raw<=65535:raise ValueError('raw16 required')
    signed=raw if raw<32768 else raw-65536
    delta=signed+4000
    quotient=abs(delta)//50 * (-1 if delta<0 else 1)
    return max(0,min(255,quotient))

def target32(payload,profile,prior):
    """B9AD0/B9BFE target-store slice only; not all SET32 consumers."""
    if len(payload)!=16 or payload[0]!=0x32:raise ValueError('SET32 payload required')
    result=dict(prior)
    if profile==2:return result
    for zone,pos,flagpos,mask,modepos in [(0,10,1,128,6),(1,12,2,2,7)]:
        mode=payload[modepos]
        value=int.from_bytes(payload[pos:pos+2],'big')
        if payload[flagpos]&mask and mode in (0,1,3,4) and value!=65535:
            result[(mode,zone)]=value
    return result

def coupled_modes(zone,value,modes,feature,table):
    """BBE92 requested-mode slice; publication3916/3918 is separate."""
    if len(table)!=72 or zone not in (0,1) or feature not in (0,1):raise ValueError('mode context')
    if len(modes)!=2 or any(m not in range(6) for m in modes):raise ValueError('prior modes')
    result=list(modes)
    if value not in range(5):return tuple(result)
    result[zone]=value
    mapped=table[feature*36+result[0]*6+result[1]]
    if mapped!=255:result[1]=mapped
    return tuple(result)
