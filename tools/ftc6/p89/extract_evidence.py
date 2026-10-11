"""P0089 private-input verifier. Publishes hashes/footprints, never full listings."""
import argparse,hashlib,json,re
from pathlib import Path
SHA='d828c2e18a013a6adea8a191448b5c5f7d52ac17b3bbc1182c977e190b60976a'
def image(data):
    if len(data)!=0x80000 or hashlib.sha256(data).hexdigest()!=SHA:raise ValueError('wrong reference image')
    return data

def extract(binary,private):
    b=image(Path(binary).read_bytes());private=Path(private)
    hashes={};footprint={}
    for folder in ('controls','controls-more','read-helpers'):
        files=sorted((private/folder).glob('*.asm'))
        if not files:raise ValueError('missing evidence '+folder)
        for p in files:
            other=private/'repeat'/p.name
            if not other.is_file() or p.read_bytes()!=other.read_bytes():raise ValueError('nonreproducing export '+p.stem)
            hashes[p.stem]=hashlib.sha256(p.read_bytes()).hexdigest()
    if len(hashes)!=45:raise ValueError('wrong root count')
    for root in ('bd296','bd780'):
        rows=[]
        for line in (private/'controls-more'/f'{root}.asm').read_text().splitlines():
            m=re.match(r'ram:([0-9a-f]+)\tMOV\.([bw]) .*?,0x([0-9a-f]+)$',line)
            if m and 0x700<=int(m[3],16)<0x900:
                rows.append(dict(proof=m[1],active=m[3].zfill(4),width=1 if m[2]=='b' else 2))
        footprint[root]=rows
    return dict(image_sha256=SHA,assembly_sha256=hashes,repeat_count=len(hashes),
        tables={f'{a:x}':list(b[a-0x80000:a-0x80000+n]) for a,n in [(0x8929d,11),(0x82406,22),(0x8241c,22),(0x860cc,72)]},
        category6_direct_writes=footprint,scope='Repeated corrected-project assembly, not independent decoder proof; direct MOV writes in two importers, not complete semantic closure')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('binary');p.add_argument('private');p.add_argument('output',type=Path);a=p.parse_args();a.output.write_text(json.dumps(extract(a.binary,a.private),indent=2)+'\n')
