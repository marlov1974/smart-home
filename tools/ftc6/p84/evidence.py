"""P0084 offline, hash-qualified compact transport evidence. No device access."""
import argparse, hashlib, json
from pathlib import Path
SHA='d828c2e18a013a6adea8a191448b5c5f7d52ac17b3bbc1182c977e190b60976a'
BASE=0x80000

def derive(binary, instructions):
    b=binary.read_bytes()
    if hashlib.sha256(b).hexdigest()!=SHA: raise ValueError('Unqualified firmware image')
    def at(a,n):
        if not BASE<=a<=BASE+len(b)-n:raise ValueError('Outside image')
        return b[a-BASE:a-BASE+n]
    def ptr(a):return int.from_bytes(at(a,4),'little')
    routes=[]
    for typ,table,commands in [(0x41,0x84b56,[0x32,0x34,0x65,0x71,0x72,0x79,0xc8]),(0x42,0x84c56,[0x15,0x26,0x28,0x65,0x71,0x72,0x79,0xa1,0xa2,0xa3])]:
        for c in commands:
            ix=at(table+c,1)[0];found=[]
            for row in range(15):
                a=0x892a8+59*row;v=at(a,59)
                if v[:2]==bytes([252,typ]) and v[2]<=c<=v[3] and ix!=255:
                    if 9+ix>=59:raise ValueError('Descriptor index overflow')
                    internal=v[9+ix]
                    item=dict(type=hex(typ),command=hex(c),descriptor=hex(a),internal_id=hex(internal),reply_packer=hex(ptr(0x84d56+16*internal+8)))
                    if typ==0x41 and 5<=internal<=51:
                        tab=0xa910f+2*(internal-5);item['staging_branch']=hex(0xa910a+int.from_bytes(at(tab,2),'little',signed=True))
                    found.append(item)
            if len(found)!=1:raise ValueError('Route not unique')
            routes+=found
    vectors={hex(a):hex(ptr(a)&0xfffff) for a in (0xffd3c,0xffd40)}
    if vectors!={'0xffd3c':'0xa397c','0xffd40':'0xa37a8'}:raise ValueError('UART vectors changed')
    switches=[]
    for branch,table,count in [(0x9f315,0x9f31a,25),(0xcf695,0xcf69a,48),(0xa910a,0xa910f,48)]:
        ts=[branch+int.from_bytes(at(table+2*i,2),'little',signed=True) for i in range(count)]
        if any(x<BASE or x>=0x100000 for x in ts):raise ValueError('Switch target outside image')
        switches.append(dict(branch=hex(branch),table=hex(table),count=count,targets=[hex(x) for x in ts]))
    # Minimum operand excerpts supporting the new findings; not a full listing.
    selected=[0xa36e3,0xa36f7,0xa3797,0xa3963,0xa397c,0xa37a8,0x9e9d1,0x9f5d1,0xa0873,0xa0879,0xa087c,0xcede1,0xcedea,0xcedf0,0xaaccc,0xaba24,0xbd401,0xbd811,0xcf832,0xcf8de]
    index={int(x[0].split(':')[1],16):x[1] for l in instructions.read_text().splitlines() if len(x:=l.split('\t'))>=2}
    missing=[hex(a) for a in selected if a not in index]
    if missing:raise ValueError('Missing operand evidence '+','.join(missing))
    return dict(image_sha256=SHA,version='20.01 candidate; not installed21.00',routes=routes,uart2_vectors=vectors,relative_switches=switches,receive_nibble_map=list(at(0x832fe,16)),operand_excerpts={hex(a):index[a] for a in selected},instructions_sha256=hashlib.sha256(instructions.read_bytes()).hexdigest(),live_requests=0)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('binary',type=Path);p.add_argument('instructions',type=Path);p.add_argument('output',type=Path);a=p.parse_args()
    a.output.write_text(json.dumps(derive(a.binary,a.instructions),indent=2)+'\n')
