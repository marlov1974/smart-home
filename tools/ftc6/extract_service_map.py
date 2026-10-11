"""P0082: derive address-only selector evidence from local P82Audit listings."""
import argparse,json,re
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('listing',type=Path);p.add_argument('output',type=Path);args=p.parse_args()
ins={int(line.split('\t')[0].split(':')[-1],16):line.split('\t')[1] for line in args.listing.read_text().splitlines()}
result=[]
for address,text in ins.items():
    if not 0x8c0b4<=address<0x8c4a4:continue
    match=re.fullmatch(r'CMP.w #0x([0-9a-f]+),R0',text)
    branch=re.fullmatch(r'JMP.w 0x([0-9a-f]+)',ins.get(address+6,''))
    if match and branch:result.append({'code':int(match[1],16),'compare':hex(address),'handler':hex(int(branch[1],16))})
args.output.write_text(json.dumps(result,indent=2)+'\n')
print(f'{len(result)} selector comparisons, image-specific candidates; not a wire-protocol map')
