"""Offline image, ROM-table, operand and deterministic extraction checks."""
import argparse
import hashlib
import json
import struct
from pathlib import Path
from model import HEAT_TABLE
IMAGE_SHA='d828c2e18a013a6adea8a191448b5c5f7d52ac17b3bbc1182c977e190b60976a'
OPERANDS={
'000a1fdb':'JSR.a 0x000a2be0','000a1fe4':'SUB.w R1,R0',
'000a2017':'LDE.w A1A0,R0','000a2027':'JLEU 0x000a202d',
'000a2033':'LDE.w 0x8355e[A0],-0x5[FB]',
'0009a349':'CMP.w #0x1f40,-0x2[FB]','0009a359':'ADD.w #0x31,R0',
'0009a35f':'DIV.w #0x32','00099f68':'ADD.w #0xfa0,R0',
'00099f6e':'DIV.w #0x32','000af490':'SUB.w -0x2[FB],R0',
'000af496':'CMP.w 0x2,-0x4[FB]','000a331b':'MOV.w #0x8000,[A0]',
'000a332f':'MOV.w #0x0,[A0]','000a334d':'OR.b 0x80,R0H',
'000a336d':'AND.w #0x7fff,[A0]','000a33c6':'JLTU/NC 0x000a33cc',
'000986f8':'ADD.w -0x2[FB],R0','000986fb':'MOV.w R0,0x662',
'0009871b':'MOV.w R0,0x664','000b9b56':'JSR.w 0x000b9bfe'}
def sha(data):return hashlib.sha256(data).hexdigest()
def derive(blob,text):
    if sha(blob)!=IMAGE_SHA:raise ValueError('wrong firmware image')
    rows={x.split('\t')[0].split(':')[-1]:x.split('\t')[1] for x in text.splitlines() if '\t' in x}
    for address,operand in OPERANDS.items():
        if rows.get(address)!=operand:raise ValueError(f'operand mismatch {address}')
    table=[struct.unpack_from('<hhh',blob,0x355a+i*6) for i in range(11)]
    if [(a,c) for a,b,c in table]!=list(HEAT_TABLE) or any(a!=b for a,b,c in table):raise ValueError('table mismatch')
    return dict(image_sha256=IMAGE_SHA,operands=OPERANDS,heating_table=table)
def verify(image,a,b):
    names=sorted(x.name for x in a.iterdir() if x.is_file())
    if names!=sorted(x.name for x in b.iterdir() if x.is_file()):raise ValueError('file sets differ')
    hashes={}
    for n in names:
        x=(a/n).read_bytes()
        if x!=(b/n).read_bytes():raise ValueError('nondeterministic '+n)
        hashes[n]=sha(x)
    wanted=Path(__file__).with_name('roots.txt').read_text().strip().split(',')
    actual=[x.split('\t')[:2] for x in (a/'requested.tsv').read_text().splitlines()]
    if sorted(wanted)!=sorted(x[0] for x in actual) or any(x!=y for x,y in actual):raise ValueError('root mismatch')
    evidence=derive(image.read_bytes(),(a/'instructions.tsv').read_text())
    return dict(status='PASS',roots=len(wanted),export_files=len(names),export_hashes=hashes,evidence=evidence,physical='NOT RUN')
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for n in ['image','first','second','output']:p.add_argument(n,type=Path)
    a=p.parse_args();r=verify(a.image,a.first,a.second);a.output.write_text(json.dumps(r,indent=2)+'\n');print('PASS',r['roots'],'roots',r['export_files'],'matching files')
