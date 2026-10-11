#!/usr/bin/env python3
"""P0086 pinned evidence checks. Full private exports never copied to public output."""
import argparse
import hashlib
import json
from pathlib import Path
from uart1 import IMAGE_SHA

OPERANDS = {
 '0009e99c':'MOV.b [A0],0x1348[A1]',
 '0009e997':'MOV.w R0,A0',
 '0009e994':'ADC.w -0x2[FB],R2',
 '0008ca47':'AND.b 0xf0,-0x7[FB]',
 '0008ca4a':'AND.b 0xf,-0x7[FB]',
 '0008ca9d':'AND.b 0xf0,-0x7[FB]',
 '0008caa0':'AND.b 0xf,-0x7[FB]',
 '0008caf3':'AND.b 0xf0,-0x7[FB]',
 '0008caf6':'AND.b 0xf,-0x7[FB]',
 '0008cb49':'AND.b 0xf0,-0x7[FB]',
 '0008cb4c':'AND.b 0xf,-0x7[FB]',
 '0008cb9f':'AND.b 0xf0,-0x7[FB]',
 '0008cba2':'AND.b 0xf,-0x7[FB]',
 '0008cbf5':'AND.b 0xf0,-0x7[FB]',
 '0008cbf8':'AND.b 0xf,-0x7[FB]',
 '0008e3d6':'LDE.b 0x888db,0x3879',
 '000a8f82':'JSR.a 0x000cf9c4',
 '000a8f86':'MOV.b R0L,0x235f',
 '000bd401':'MOV.b 0x197b,0x770',
 '000bd811':'MOV.b 0x1cb0,0x7e6',
}
def sha(b):return hashlib.sha256(b).hexdigest()
def derive(binary, instructions):
    if sha(binary) != IMAGE_SHA: raise ValueError('Input image mismatch')
    if binary[0x1e99c:0x1e9a0] != bytes.fromhex('726d4813'): raise ValueError('Load opcode mismatch')
    rows={r.split('\t')[0].split(':')[-1]:r.split('\t')[1] for r in instructions.splitlines()[1:] if '\t' in r}
    for address, text in OPERANDS.items():
        if rows.get(address)!=text:raise ValueError(f'Unsupported/changed operand {address}: {rows.get(address)}')
    return dict(image_sha256=IMAGE_SHA,load_opcode='726d4813',operands=OPERANDS,
                length_table=binary[0x32be:0x32ce].hex(),rom_override_signature=binary[0xff4:0xff6].hex(),
                physical_validation='NOT RUN')
def verify(binary, first, second, proof):
    names=sorted(p.name for p in first.iterdir() if p.is_file())
    if names!=sorted(p.name for p in second.iterdir() if p.is_file()): raise ValueError('Export file sets differ')
    hashes={}
    for name in names:
        a=(first/name).read_bytes();b=(second/name).read_bytes()
        if a!=b:raise ValueError('Nondeterministic export '+name)
        hashes[name]=sha(a)
    requests=[r.split('\t')[:2] for r in (first/'requested.tsv').read_text().splitlines()]
    targets=Path(__file__).with_name('targets.txt').read_text().strip().split(',')
    if sorted(r[0] for r in requests)!=sorted(targets) or any(a!=b for a,b in requests):
        raise ValueError('Missing or incorrectly rooted requested function')
    evidence=derive(binary.read_bytes(),(first/'instructions.tsv').read_text())
    if proof.read_text().count('P86_ADDRESS_PASS') != 8:raise ValueError('Expected eight instruction emulator cases')
    return dict(status='PASS',evidence=evidence,export_files=len(names),export_sha256=hashes,emulator_cases=8)
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for n in ('binary','first','second','proof','output'):p.add_argument(n,type=Path)
    a=p.parse_args();out=verify(a.binary,a.first,a.second,a.proof)
    a.output.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print(json.dumps({k:v for k,v in out.items() if k not in ('evidence','export_sha256')}))
