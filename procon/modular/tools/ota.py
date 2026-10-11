"""P0080 chunk planning and framing. CRC protects integrity, not authenticity."""
import argparse,binascii,json,struct
from pathlib import Path

def crc(b):return binascii.crc32(b)&0xffffffff
def frame(cmd,seq,payload=b''):
 if len(payload)>240 or not 0<=seq<65536:raise ValueError('frame bound')
 h=struct.pack('<2sBBHH',b'P8',cmd,2,seq,len(payload))+payload
 return h+struct.pack('<I',crc(h))
def decode(b,cmd,seq):
 if len(b)!=44 or b[:4]!=bytes([80,56,cmd|128,2]) or b[4:8]!=struct.pack('<HH',seq,32) or struct.unpack('<I',b[-4:])[0]!=crc(b[:-4]):raise ValueError('invalid OTA reply')
 v=struct.unpack('<8I',b[8:40]);return dict(zip(['status','active','next_seq','slot','offset','uid0','uid1','uid2'],v))
def plan(old,new):
 old,new=Path(old),Path(new);a=json.loads((old/'sizes.json').read_text());b=json.loads((new/'sizes.json').read_text())
 if a.get('ota_protocol')!=2 or b.get('ota_protocol')!=2:raise ValueError('protocol2 requires original BL2 installation first')
 if a['layout']!=b['layout']:raise ValueError('layout changes require initial installation')
 if (old/'bl2.bin').read_bytes()!=(new/'bl2.bin').read_bytes():raise ValueError('BL2 cannot be OTA updated')
 changes=[]
 for i,(x,y) in enumerate(zip(a['slots'][1:],b['slots'][1:])):
  data=(new/(y['name']+'.bin')).read_bytes()
  if len(data)!=y['size'] or crc(data)!=y['crc32']:raise ValueError('artifact mismatch')
  if data!=(old/(x['name']+'.bin')).read_bytes():changes.append(i)
 m=(new/'manifest.bin').read_bytes()
 if len(m)!=64 or struct.unpack('<I',m[56:60])[0]!=crc(m[:56]):raise ValueError('manifest mismatch')
 return {'package':'P0080','layout':b['layout'],'expected_manifest_crc':crc((old/'manifest.bin').read_bytes()[:56]),'mask':sum(1<<i for i in changes),'slots':changes,'payload_data_max':232,'wire_max':252,'new':str(new.resolve()),'old':str(old.resolve()),'manifest':m.hex(),'sizes':b['slots'][1:]}
def transactions(p,uid):
 if not p['mask']:raise ValueError('No changed chunks')
 seq=1;m=bytes.fromhex(p['manifest'])
 yield frame(2,seq,struct.pack('<5I',p['mask'],p['expected_manifest_crc'],*uid)+m)
 seq+=1
 for i in p['slots']:
  data=(Path(p['new'])/(p['sizes'][i]['name']+'.bin')).read_bytes()
  for offset in range(0,len(data),232):
   yield frame(3,seq,struct.pack('<II',i,offset)+data[offset:offset+232]);seq+=1
 yield frame(4,seq);yield frame(6,seq+1)
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('old');a.add_argument('new');a.add_argument('--out',required=True);v=a.parse_args();p=plan(v.old,v.new);Path(v.out).write_text(json.dumps(p,indent=2)+'\n');print('Changed slots:',p['slots'])
