"""P0082: offline S-record validation; reconstructed vendor bytes stay local."""
import argparse, collections, hashlib, json, re
from pathlib import Path

def parse_srec(raw):
    memory={}; counts=collections.Counter(); entries=[]; duplicate=0; declared=[]
    widths={0:2,1:2,2:3,3:4,5:2,6:3,7:4,8:3,9:2}
    for line_no,line in enumerate(raw.decode('ascii').splitlines(),1):
        if not line.strip(): continue
        if not re.fullmatch(r'S[0-9][0-9a-fA-F]+',line): raise ValueError(f'line {line_no}: syntax')
        kind=int(line[1]); data=bytes.fromhex(line[2:]); width=widths.get(kind)
        if width is None or len(data)<width+2: raise ValueError(f'line {line_no}: type/length')
        if data[0]!=len(data)-1: raise ValueError(f'line {line_no}: count')
        if sum(data)&255!=255: raise ValueError(f'line {line_no}: checksum')
        addr=int.from_bytes(data[1:1+width],'big'); payload=data[1+width:-1];counts[str(kind)]+=1
        if kind in (1,2,3):
            for i,b in enumerate(payload):
                a=addr+i
                if a in memory:
                    if memory[a]!=b: raise ValueError(f'line {line_no}: conflicting overlap {a:x}')
                    duplicate+=1
                memory[a]=b
        elif kind in (7,8,9):
            if payload: raise ValueError('entry payload')
            entries.append({'type':kind,'address':addr})
        elif kind in (5,6):
            if payload: raise ValueError('count payload')
            declared.append(addr)
    if not memory: raise ValueError('empty image')
    actual=sum(counts[str(k)] for k in (1,2,3))
    if any(n!=actual for n in declared): raise ValueError('record count mismatch')
    return memory,dict(counts),entries,duplicate

def inspect_image(raw):
    mem,counts,entries,duplicates=parse_srec(raw); keys=sorted(mem);lo=keys[0];hi=keys[-1]
    spans=[];start=prev=lo
    for a in keys[1:]:
        if a!=prev+1: spans.append([start,prev+1]);start=a
        prev=a
    spans.append([start,prev+1]); image=bytes(mem.get(a,255) for a in range(lo,hi+1))
    vectors=[]
    for a in range(0xfffdc,0x100000,4):
        if all(a+i in mem for i in range(4)):
            b=bytes(mem[a+i] for i in range(4));v=int.from_bytes(b[:3],'little')&0xfffff
            vectors.append({'address':hex(a),'bytes':b.hex(),'low20_target':hex(v),'fourth_byte':b[3],'target_present':v in mem})
    strings=[]
    for s,e in spans:
        b=bytes(mem[a] for a in range(s,e))
        for m in re.finditer(rb'[ -~]{6,}',b):
            if b'.DAT' in m[0] or b'SETTING' in m[0] or b'PACIC' in m[0]:strings.append({'address':hex(s+m.start()),'text':m[0].decode()})
    report={'input_sha256':hashlib.sha256(raw).hexdigest(),'record_counts':counts,'entry_records':entries,'identical_overlap_bytes':duplicates,'range':[hex(lo),hex(hi)],'populated_bytes':len(mem),'regions':[[hex(s),hex(e-1)] for s,e in spans],'holes':hi-lo+1-len(mem),'ff_bytes':sum(v==255 for v in mem.values()),'ff_filled_image_sha256':hashlib.sha256(image).hexdigest(),'vector_candidates':vectors,'setting_strings':strings}
    return report,image

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('input',type=Path);p.add_argument('--report',type=Path,required=True);p.add_argument('--local-image',type=Path);a=p.parse_args()
    r,b=inspect_image(a.input.read_bytes());a.report.write_text(json.dumps(r,indent=2)+'\n')
    if a.local_image:a.local_image.write_bytes(b)
    print(json.dumps(r,indent=2))
