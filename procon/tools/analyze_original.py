"""P0069: reproducible reference identity, vector and selected instruction evidence."""
from pathlib import Path
import hashlib
import json
import re
import struct
import sys
import zipfile
from capstone import Cs, CS_ARCH_ARM, CS_MODE_THUMB, CS_MODE_MCLASS
from capstone.arm import ARM_OP_MEM, ARM_REG_PC

ROOT=Path(__file__).resolve().parents[1]
BASE=0x08008000
EXPECTED='2ae03b0cdc684bcccbf9f5281878175f5ca53b144e3e32cc223159fcc4654766'
# ST cmsis-device-l4 ca0bfa2b8b68dc2994b27fba0a10dfd28d086ee1 startup_stm32l433xx.s.
L433_RESERVED=[7,8,9,10,13,45,46,58,59,60,61,62,63,64,66,68,69,77,78,79,91,95]

def main():
    folder=ROOT/'reference/original'
    data=(folder/'A1M_R5_Release_08008000.bin').read_bytes()
    assert len(data)==96692 and hashlib.sha256(data).hexdigest()==EXPECTED
    with zipfile.ZipFile(folder/'Proon+Firmware+Update+Tool+(v3.1.05).zip') as z:
        assert z.testzip() is None
        assert z.read('A1M_R5_Release_08008000.bin')==data
    vectors=struct.unpack_from('<99I',data)
    assert vectors[:2]==(0x20010000,0x0800a341)
    reserved=[i for i,v in enumerate(vectors) if v==0]
    assert reserved==L433_RESERVED
    result={'reference_sha256':EXPECTED,'bytes':len(data),
            'vectors':[hex(v) for v in vectors],
            'reserved_indices':reserved,'model_confidence':'strong inference, not physical identification',
            'candidate_family':'STM32L433xx'}
    if len(sys.argv)>1:
        matches=[]
        for p in sorted(Path(sys.argv[1]).glob('startup*.s')):
            source=p.read_text().split('g_pfnVectors:',1)[1]
            entries=re.findall(r'^\s*\.word\s+(\w+)',source,re.M)
            diff=sum((e=='0')!=(v==0) for e,v in zip(entries,vectors))
            matches.append({'file':p.name,'reserved_mismatches':diff,'entries':len(entries)})
        result['startup_comparison']=matches
    out=ROOT/'analysis';out.mkdir(exist_ok=True)
    (out/'reference-analysis.json').write_text(json.dumps(result,indent=2)+'\n')
    md=Cs(CS_ARCH_ARM,CS_MODE_THUMB|CS_MODE_MCLASS);md.detail=True;md.skipdata=True
    lines=['P0069 original instruction evidence; literal pools may decode as instructions.',
           'References are base+offset, not symbols; semantic labels are analyst inferences.']
    spans=[(0x08009794,0x08009a6e),(0x08009f80,0x0800a0e4),
           (0x0800a230,0x0800a268),(0x0800a330,0x0800a390),
           (0x08010988,0x08010a04),(0x08010aa4,0x08010b9e)]
    for start,end in spans:
        lines.append(f'\nSpan {start:#010x}–{end:#010x}')
        for ins in md.disasm(data[start-BASE:end-BASE],start):
            extra=''
            if ins.id and ins.mnemonic.startswith('ldr') and len(ins.operands)>1:
                op=ins.operands[1]
                if op.type==ARM_OP_MEM and op.mem.base==ARM_REG_PC:
                    address=((ins.address+4)&~3)+op.mem.disp
                    if BASE<=address<BASE+len(data)-3:
                        extra=f' ; [{address:08x}]={struct.unpack_from("<I",data,address-BASE)[0]:08x}'
            lines.append(f'{ins.address:08x} {ins.mnemonic:8} {ins.op_str}{extra}'.rstrip())
    (out/'original-excerpts.txt').write_text('\n'.join(lines)+'\n')
    print('PASS original ZIP/BIN identity, vectors, L433 reserved pattern; evidence in procon/analysis')

if __name__=='__main__':main()
