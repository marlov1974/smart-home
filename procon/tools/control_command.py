"""P0072 r2: encode an operator command offline; never sends device traffic."""
import argparse
import json
from decimal import Decimal
MODES = {'off':0, 'auto':1, 'fixed-flow':2, 'dhw':3, 'targets':4}
def encode(sequence, mode, flow=None, dhw=None, lease=0):
    def target(value, low, high):
        n=Decimal(str(value))*100
        if not n.is_finite(): raise ValueError('Target must be finite')
        if n!=int(n) or not low<=n<=high: raise ValueError('Target outside allowed range/precision')
        return int(n)
    if not 1<=sequence<=65535 or mode not in MODES: raise ValueError('Invalid sequence/mode')
    flags=(1 if flow is not None else 0)|(2 if dhw is not None else 0)
    f=target(flow,2000,4500) if flow is not None else 0
    d=target(dhw,4000,6000) if dhw is not None else 0
    if mode=='auto':
        if flags or lease: raise ValueError('AUTO accepts no targets/lease; restores saved session')
    elif not 30<=lease<=1800: raise ValueError('Lease must be 30–1800 seconds')
    if mode=='fixed-flow' and flow is None: raise ValueError('Fixed flow requires target')
    if mode=='targets' and not flags: raise ValueError('No targets')
    if mode in ('off','dhw') and flow is not None: raise ValueError('Flow not permitted in this mode')
    words=[0xc072,sequence,MODES[mode],f,d,lease,flags,2]
    frame=bytes.fromhex('01 10 01 2c 00 08 10')+b''.join(v.to_bytes(2,'big') for v in words)
    crc=65535
    for b in frame:
        crc^=b
        for _ in range(8): crc=(crc>>1)^(0xa001 if crc&1 else 0)
    return {'sent':False,'function':16,'address':300,'words':words,'rtu_hex':(frame+crc.to_bytes(2,'little')).hex(' '),'warning':'Supervised candidate. Read original snapshot/status, verify applied sequence, preserve recovery settings externally; no reboot restoration guarantee.'}
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--sequence',type=int,required=True);p.add_argument('--mode',choices=MODES,required=True);p.add_argument('--flow');p.add_argument('--dhw');p.add_argument('--lease',type=int,default=0)
    a=p.parse_args()
    try: print(json.dumps(encode(a.sequence,a.mode,a.flow,a.dhw,a.lease),indent=2))
    except ValueError as e:p.error(str(e))
