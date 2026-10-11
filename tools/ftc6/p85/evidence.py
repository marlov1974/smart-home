"""P0085 offline evidence; no device access and no full firmware export."""
import argparse
import hashlib
import json
from pathlib import Path
SHA = 'd828c2e18a013a6adea8a191448b5c5f7d52ac17b3bbc1182c977e190b60976a'
VECTORS = {0xffd3c: 0xa397c, 0xffd40: 0xa37a8, 0xffd44: 0x944b8,
           0xffd48: 0x942a0, 0xffd4c: 0x944c6, 0xffd50: 0x942ae,
           0xffd54: 0xc1456, 0xffd6c: 0x942e6}
# Reviewed operands, including start boundaries of the two D timer ISRs.
OPERANDS = {
 0xd555a:'LDC #0xf,INTBH', 0xd555e:'LDC #0xfd00,INTBL',
 0xc4c87:'MOV.b #0x65,0x0248', 0xc4c9b:'MOV.b #0xcf,0x0249',
 0xc4e50:'MOV.w 0x24e,A0', 0xc502f:'MOV.w R0,0x24a',
 0x942a7:'JSR.a 0x000c4dfc', 0x944bf:'JSR.a 0x000c5004',
 0x942b5:'TST.b #0x80,0x6d8', 0x942bc:'JSR.a 0x0008b200',
 0x942c1:'JSR.a 0x0009e66e', 0x944d4:'JSR.a 0x0008b3c2',
 0x944d9:'JSR.a 0x0009e87a', 0x8af89:'MOV.b #0x15,0x0258',
 0x9e64a:'MOV.b #0x65,0x0258', 0x9e656:'MOV.b #0xcf,0x0259',
 0x9e6c3:'CMP.b 0x4,0x3d5b', 0x9e6fa:'ADD.b 0x3d56[A0],0x3d5c',
 0x9e7b0:'MOV.b #0x1,0x3d4c', 0x9e7e2:'LDE.b 0x832be[A0],R0L',
 0x9e7f6:'JSR.w 0x0009e938', 0x9e99c:'MOV.b [A0],0x1348[A1]',
 0x9e835:'JSR.w 0x0009dac0', 0x9d897:'JSR.w 0x0009d8a0',
 0x9e8a2:'MOV.b 0x1346[A0],R0L', 0x9e8a7:'MOV.w R0,0x25a',
 0xc4ef4:'MOV.b 0x3fb4,-0x4[FB]', 0xc4ef9:'MOV.b 0x3fb5,-0x3[FB]',
 0xc4d3e:'MOV.b 0x3fb3[A0],0x4455[A1]',
 0xc4f28:'CMP.b -0x1[FB],0x3fb3[A0]',
 0xc9288:'LDE.b 0x8740c[A0],R0L',0xc94b6:'LDE.b 0x87a60[A0],R0L',
 0x94318:'JSR.a 0x0009e9ae',0x9431c:'JSR.a 0x0009f04c',
 0xc148d:'JSR.a 0x0009e9ae',0xc1491:'JSR.a 0x0009f04c',
 0xcf758:'MOV.b 0x2349,R0L',0xcf75c:'MOV.b 0x234a,R0L',
 0xcf760:'MOV.b 0x234b,R0L',0xcf726:'CMP.b 0x2,0x0900',
 0xcf888:'MOV.b #0x6,0x2373',0xcede1:'CMP.w #0xc8,0x3238',
}

def derive(binary, instructions):
    data = Path(binary).read_bytes()
    if hashlib.sha256(data).hexdigest() != SHA:
        raise ValueError('Unqualified image')
    idx = {int(p[0].split(':')[1],16):p[1] for line in Path(instructions).read_text().splitlines()
           if len(p := line.split('\t')) >= 2}
    for address, expected in OPERANDS.items():
        if idx.get(address) != expected:
            raise ValueError(f'Missing/changed operand {address:x}: {idx.get(address)!r}')
    vectors = {a:int.from_bytes(data[a-0x80000:a-0x80000+4], 'little') & 0xfffff for a in VECTORS}
    if vectors != VECTORS:
        raise ValueError('Changed vectors')
    return {'package':'P0085','image_sha256':SHA,'version':'static20.01 candidate; not physical21.00',
            'vectors':{hex(a):hex(v) for a,v in vectors.items()},
            'operands':{hex(a):v for a,v in OPERANDS.items()},
            'diagnostic_read_length_table':list(data[0x32be:0x32ce]),
            'instructions_sha256':hashlib.sha256(Path(instructions).read_bytes()).hexdigest(),
            'physical_connector_assignment':{'UART0':'UNKNOWN','UART1':'UNKNOWN','UART2':'CN105 supported by P81/P84','D':'UNKNOWN'},
            'live_requests':0}

if __name__ == '__main__':
    p=argparse.ArgumentParser();p.add_argument('binary',type=Path);p.add_argument('instructions',type=Path);p.add_argument('output',type=Path)
    a=p.parse_args();a.output.write_text(json.dumps(derive(a.binary,a.instructions),indent=2)+'\n')
