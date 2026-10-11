"""P0083 local-only, hash-gated direct-flow repair. No upstream source distribution."""
import argparse,hashlib,re
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('original',type=Path);p.add_argument('installed',type=Path);a=p.parse_args()
s=a.original.read_text()
if hashlib.sha256(a.original.read_bytes()).hexdigest()!='1c1f46945fc47a6bb5f6c755578708a4709aca47cd1aac9721256cc0eec243b8':
 raise ValueError('Unqualified upstream module')
helpers='''p83_abs: abs20 is abs20 { export *:4 abs20; }
p83_rel8: target is dsp8 [ target=inst_start+1+dsp8; ] { export *:4 target; }
p83_rel16: target is dsp16 [ target=inst_start+1+dsp16; ] { export *:4 target; }
p83_short: target is op=0x0C & dsp0_2 [ target=inst_start+2+dsp0_2; ] { export *:4 target; }

'''
constructors={
'JMP.s':':JMP.s p83_short is p83_short { goto p83_short; }',
'JMP.b':':JMP.b p83_rel8 is ops0_7=0xFE; p83_rel8 { goto p83_rel8; }',
'JMP.w':':JMP.w p83_rel16 is ops0_7=0xF4; p83_rel16 { goto p83_rel16; }',
'JMP.A':':JMP.A p83_abs is ops0_7=0xFC; p83_abs { goto p83_abs; }',
'JSR.w':':JSR.w p83_rel16 is ops0_7=0xF5; p83_rel16 { SP=SP-3; *[near]:3 SP=inst_next; call p83_rel16; }',
'JSR.a':':JSR.a p83_abs is ops0_7=0xFD; p83_abs { SP=SP-3; *[near]:3 SP=inst_next; call p83_abs; }'}
for mnemonic,body in constructors.items():
 s,n=re.subn(r'^:'+re.escape(mnemonic)+r'\s.*?\n}',lambda _:body,s,count=1,flags=re.M|re.S);assert n==1,mnemonic
s=s.replace(':JMP.s p83_short',helpers+':JMP.s p83_short',1)
s += """
# P0083 word-immediate rotation, Renesas M16C/60 manual ROT.
:ROT.w sha_imm12_15, d_eaw is (op1_7=0x70 & size0=1 & sha_imm12_15 & bit15=0) ... & d_eaw {
 local old:2 = d_eaw;
 local shifted:2 = old >> (16-sha_imm12_15);
 Cflg = (shifted & 1) != 0;
 d_eaw = (old << sha_imm12_15) | shifted;
 Sflg = d_eaw s< 0;
 Zflg = d_eaw == 0;
}
:ROT.w sha_imm12_15, d_eaw is (op1_7=0x70 & size0=1 & sha_imm12_15 & bit15=1) ... & d_eaw {
 local old:2 = d_eaw;
 local shifted:2 = old >> (-sha_imm12_15-1);
 Cflg = (shifted & 1) != 0;
 d_eaw = (old >> (-sha_imm12_15)) | (old << (16+sha_imm12_15));
 Sflg = d_eaw s< 0;
 Zflg = d_eaw == 0;
}
"""
a.installed.write_text(s)
print(hashlib.sha256(a.installed.read_bytes()).hexdigest())
