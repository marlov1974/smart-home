"""P0088 bounded, hash-gated static inventory. Local files only."""
import argparse,hashlib,json
from pathlib import Path
BASE=0x80000
SHA='d828c2e18a013a6adea8a191448b5c5f7d52ac17b3bbc1182c977e190b60976a'
class Image:
 def __init__(self,data):
  if len(data)!=0x80000 or hashlib.sha256(data).hexdigest()!=SHA:raise ValueError('Wrong image')
  self.data=data
 def at(self,a,n):
  if n<0 or a<BASE or a+n>0x100000:raise ValueError('Invalid bounds')
  return self.data[a-BASE:a-BASE+n]
 def ptr(self,a):
  v=int.from_bytes(self.at(a,4),'little')
  if not BASE<=v<0x100000:raise ValueError(f'Invalid pointer {a:x}: {v:x}')
  return v

def extract(image):
 tables=[];roots=set();routes=[]
 def table(name,base,count,stride,offsets,bounds):
  rows=[]
  for i in range(count):
   a=base+i*stride;r=image.at(a,stride);p={str(o):f'{image.ptr(a+o):05x}' for o in offsets}
   roots.update(int(v,16) for v in p.values())
   rows.append(dict(index=i,address=f'{a:05x}',header=list(r[:min(offsets)]),callbacks=p,record_sha256=hashlib.sha256(r).hexdigest()))
  t=dict(id=name,base=f'{base:05x}',count=count,stride=stride,bounds_evidence=bounds,rows=rows)
  tables.append(t);return t
 cnrx=table('uart2.rx',0x892a8,15,59,[5],'A4FE0: index<15; A4F68 copies59')
 cntx=table('uart2.tx',0x84d56,151,16,[4,8,12],'A53D6: index<151; A535E copies16')
 for i,r in enumerate(cntx['rows']):
  if r['header'][0]!=i:raise ValueError('TX identity discontinuity')
 for frame,lookup in [(0x41,0x84b56),(0x42,0x84c56)]:
  for opcode in range(256):
   candidates=[r for r in cnrx['rows'] if r['header'][0]==0xfc and r['header'][1]==frame and r['header'][2]<=opcode<=r['header'][3]]
   index=image.at(lookup+opcode,1)[0];internal=0;descriptor=None
   if candidates and index!=255:
    if len(candidates)!=1 or index>=50:raise ValueError('Ambiguous/out-of-range CN105 lookup')
    descriptor=candidates[0]['address'];internal=image.at(int(descriptor,16)+9+index,1)[0]
    if internal>=151:raise ValueError('Out-of-range internal command')
   routes.append(dict(frame=f'{frame:02x}',opcode=f'{opcode:02x}',lookup_index=index,rx_descriptor=descriptor,internal=internal,
      tx_descriptor=cntx['rows'][internal]['address'],packer=cntx['rows'][internal]['callbacks']['8'],disposition='mapped' if internal else 'default/rejected'))
 table('uart0.rx',0x8740c,38,14,[2,6,10],'C9278 compares38; C921C copies14')
 table('uart0.tx',0x87a60,38,21,[5,9,13,17],'C94A6 compares38; C943E copies21')
 table('uart6.rx',0x8966b,7,9,[2],'C0550 compares7; C04F2 copies9')
 table('uart6.tx',0x86c5a,7,16,[4,8,12],'C0748 compares7; C06F0 copies16')
 classes=[];lower=0
 for i in range(26):
  a=0x806ac+3*i;r=image.at(a,3);upper=int.from_bytes(r[:2],'little') if i<25 else 65535
  if upper<lower:raise ValueError('Nonmonotonic service class bounds')
  classes.append(dict(index=i,address=f'{a:05x}',minimum=lower,maximum=upper,class_id=r[2],default=i==25));lower=upper+1
 switches=[]
 for name,branch,base,count in [('d.dispatch',0x9f315,0x9f31a,25),('uart2.set',0xa910a,0xa910f,48),('settings.recognized',0xcf695,0xcf69a,48),('source.dispatch',0x9cd67,0x9cd6c,16),('source.outgoing',0x9bc57,0x9bc5c,23)]:
  rows=[]
  for i in range(count):
   target=branch+int.from_bytes(image.at(base+2*i,2),'little',signed=True)
   if not BASE<=target<0x100000:raise ValueError('Switch target outside image')
   rows.append(dict(index=i,target=f'{target:05x}'))
  switches.append(dict(id=name,branch=f'{branch:05x}',base=f'{base:05x}',count=count,rows=rows))
 vectors=[]
 for a in range(0xffd00,0xffdfc+1,4):
  v=int.from_bytes(image.at(a,4),'little')&0xfffff
  vectors.append(dict(address=f'{a:05x}',target=f'{v:05x}'))
  if BASE<=v<0x100000:roots.add(v)
 roots.update((0xa4fe0,0xa53d6,0xa50bc,0xa504c,0xa508a,0xa5204,0xa5218,0xa522a,0xa523c,0x8c04e,0x8c0b4,0x9f152,0x9f2ea,0xc921c,0xc9278,0xc943e,0xc94a6,0xc0550,0xc0748,0xbfd16,0xc04f2,0xc06f0))
 return dict(image_sha256=SHA,tables=tables,cn105_routes=routes,service_classes=classes,switches=switches,vectors=vectors,d_translation_rx=list(image.at(0x832fe,16)),d_translation_tx=list(image.at(0x832ee,16)),d_transition_matrix=[list(image.at(0x88f65+i*25,25)) for i in range(25)],source_translation_rx=list(image.at(0x8328e,32)),source_translation_tx=list(image.at(0x8326e,32)),uart6_value_maps={f'{a:05x}':[list(image.at(a+i*2,2)) for i in range(n)] for a,n in [(0x86be2,4),(0x86bea,6),(0x86bf6,2),(0x86bfa,2),(0x86bfe,2),(0x86c02,2)]},roots=[f'{v:x}' for v in sorted(roots)])

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('image',type=Path);p.add_argument('output',type=Path);p.add_argument('--roots',type=Path)
 a=p.parse_args();result=extract(Image(a.image.read_bytes()));a.output.write_text(json.dumps(result,indent=2)+'\n')
 if a.roots:a.roots.write_text(','.join(result['roots'])+'\n')
