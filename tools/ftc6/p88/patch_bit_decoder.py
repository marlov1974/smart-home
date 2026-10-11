"""P0088 isolated language patch, qualified installed baseline only."""
import argparse, hashlib, shutil
from pathlib import Path
BASE_SHA='087e6afb29a7625e789b30467a12cad4ab2c2731e08a98c914969a308df3f46f'

def patch(source, destination):
    source,destination=Path(source),Path(destination)
    if destination.exists():raise ValueError('destination must be new')
    spec=source/'data/languages/m16c.slaspec'
    if hashlib.sha256(spec.read_bytes()).hexdigest()!=BASE_SHA:raise ValueError('unqualified baseline')
    s=spec.read_text()
    changes={
        'bitBase8     = (3,7)':'bitBase8     = (3,7)\n\tbitFBBase8   = (3,7) signed',
        'local addr = (dest8_11 + imm8)/8;':'local addr:2 = imm8 + (dest8_11 >> 3);',
        'local addr = (dest8_11 + imm16)/8;':'local addr:2 = imm16 + (dest8_11 >> 3);',
        's_bitV: bitNo8, bitBase8[FB] is FB & op8_11=11; bitNo8 & bitBase8     { local addr = FB + bitBase8;':'s_bitV: bitNo8, bitFBBase8[FB] is FB & op8_11=11; bitNo8 & bitFBBase8 { local addr:2 = FB + sext(bitFBBase8:1);',
        'local addr = FB + bitBase16;':'local addr:2 = SB + bitBase16;',
        '1<<(dest8_11 & 3)':'1<<(dest8_11 & 7)',
        '1<<(imm8 & 3)':'1<<(dest8_11 & 7)',
        '1<<(imm16 & 3)':'1<<(dest8_11 & 7)',
    }
    for old,new in changes.items():
        if s.count(old)!=1:raise ValueError('patch anchor mismatch: '+old)
        s=s.replace(old,new)
    shutil.copytree(source,destination)
    (destination/'data/languages/m16c.slaspec').write_text(s)
    (destination/'data/languages/m16c.sla').unlink(missing_ok=True)
    p=destination/'data/languages/m16c.ldefs';p.write_text(p.read_text().replace('variant="default"','variant="p88-bits"').replace('id="m16c:LE:16:default"','id="m16c:LE:16:p88-bits"'))
    p=destination/'extension.properties';p.write_text(p.read_text().replace('name=ghidra_m16c','name=ghidra_m16c_p88'))
    return hashlib.sha256(s.encode()).hexdigest()

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('source');p.add_argument('destination');a=p.parse_args();print(patch(a.source,a.destination))
