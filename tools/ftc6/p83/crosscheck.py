"""P0083: derive minimal historical observations, never contact a device."""
import hashlib,json,sys
from pathlib import Path
p=Path(sys.argv[1]);out=[]
for line in p.read_text().splitlines():
    d=json.loads(line)
    if d['code'] not in (7,0x15,0x65,0x79,0xa1,0xa2):continue
    b=bytes.fromhex(d['raw_rx']);pay=b[5:-1]
    if len(b)!=22 or b[:5]!=bytes.fromhex('fc62027a10') or sum(b[1:])%256 or pay[0]!=d['code']:
        raise ValueError('Historical frame validation failed')
    keep=dict(code=hex(d['code']),pass_index=d['pass'],timestamp=d['timestamp'],valid_checksum=True)
    if d['code']==0x15:keep['fields']={str(i):pay[i] for i in (1,2,3)}
    elif d['code'] in (0x65,0x79):keep['gate_byte']=pay[1]
    elif d['code']==7:keep['fields']={label:int.from_bytes(pay[i:i+2],'big') for label,i in [('power_word_p3_p4',3),('heat_word_p5_p6',5),('energy_word_p11_p12',11)]}
    else:
        keep['date_bytes']=list(pay[1:4]);keep['data_sha256']=hashlib.sha256(pay[4:13]).hexdigest()
    out.append(keep)
Path(sys.argv[2]).write_text(json.dumps(dict(source_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),source='P0081 mapping-20261010T205704Z/direct/readings.jsonl',new_live_reads=0,observations=out),indent=2)+'\n')
