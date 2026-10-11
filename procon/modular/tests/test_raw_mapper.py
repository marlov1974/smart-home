"""P0081 offline transport fixtures, no device access."""
import sys,unittest,tempfile,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import raw_mapper as m
class Fake:
 def __init__(self):self.rid=0;self.kind=1;self.code=0;self.requests=[];self.n=2;self.now=0
 def health(self):return {'ok':True}
 def snapshot(self):
  self.n+=1
  return dict(request_id=self.rid,kind=self.kind,code=self.code,status='BUSY' if self.n==1 else ('TIMEOUT' if self.code==255 else 'DONE'),valid=self.n>1 and self.code!=255,raw_rx=f'{self.code:02x}{self.rid:04x}',attempts=1,error=0,checksum_valid=True)
 def submit(self,w):self.requests.append(w);self.rid,self.kind,self.code=w[3:6];self.n=0
 def clock(self):return self.now
 def sleep(self,n):self.now+=n
class Tests(unittest.TestCase):
 def test_plans(self):
  self.assertEqual(len(m.plan('direct')),512)
  self.assertIn((0,2,540),m.plan('a3'))
  for code in m.EXCLUDED:
   self.assertNotIn((0,2,code),m.plan('a3'))
   with self.assertRaises(ValueError):m.envelope(1,2,code)
 def test_manual_catalog(self):
  self.assertEqual(set(m.SERVICE_METADATA),set(m.SAFE_A3))
  self.assertTrue(m.SERVICE_METADATA[113]['historical'])
  self.assertFalse(m.SERVICE_METADATA[27]['historical'])
  self.assertEqual(m.SERVICE_METADATA[540]['manual_display_unit'],'L/min')
  self.assertTrue(all(x['wire_scale']=='unverified' for x in m.SERVICE_METADATA.values()))
 def test_enumeration_resume(self):
  with tempfile.TemporaryDirectory() as d:
   f=Fake();p=Path(d)
   rows=m.scan(f,m.plan('direct'),p,max_runtime=4000,clock=f.clock,sleep=f.sleep)
   self.assertEqual(len(rows),512);self.assertEqual(len(f.requests),512)
   self.assertTrue(all(w[:3]==[0x81d1,1,0xfd] and w[4]==1 and w[6:]==[0,0] for w in f.requests))
   self.assertEqual(sum(r['status']=='TIMEOUT' for r in rows),2)
   m.scan(f,m.plan('direct'),p,max_runtime=4000,clock=f.clock,sleep=f.sleep)
   self.assertEqual(len(f.requests),512)
   self.assertIn('UNKNOWN/NO_RESPONSE',(p/'command-map.md').read_text())
 def test_cap_resume_stop(self):
  with tempfile.TemporaryDirectory() as d:
   f=Fake();p=Path(d)
   rows=m.scan(f,m.plan(),p,max_runtime=5,clock=f.clock,sleep=f.sleep)
   self.assertLess(len(rows),10)
   rows=m.scan(f,m.plan(),p,max_runtime=100,clock=f.clock,sleep=f.sleep)
   self.assertEqual(len(rows),10)
   stop=p/'STOP';stop.touch()
   self.assertEqual(m.scan(f,m.plan('direct'),p/'new',stop=stop),[])
 def test_health_error_retains_reply(self):
  with tempfile.TemporaryDirectory() as d:
   f=Fake();count=[0]
   def health():
    count[0]+=1
    if count[0]>1:raise m.Blocked('errors increased')
    return {'ok':True}
   f.health=health
   with self.assertRaises(m.Blocked):m.scan(f,[(0,1,7)],Path(d),clock=f.clock,sleep=f.sleep)
   row=json.loads((Path(d)/'readings.jsonl').read_text())
   self.assertEqual(row['status'],'DONE');self.assertIn('error',row['health_after'])
   self.assertTrue((Path(d)/'requests.jsonl').exists())
 def test_decode(self):
  w=[0]*32;w[:3]=[0x81d1,1,0xfc];w[6]=3;w[7]=7;w[9]=1;w[10]=w[27]=2
  raw=bytearray([252,0x62,2,0x7a,1,7,0]);raw[-1]=(252-sum(raw))%256
  for i,b in enumerate(raw):w[16+i//2]|=b<<(8*(i%2))
  self.assertEqual(m.decode(w)['raw_rx'],raw.hex())
  w[27]=3
  with self.assertRaises(m.Blocked):m.decode(w)
 def test_rpc_write_surface(self):
  c=m.Shelly('unused',1);calls=[];c.rpc=lambda method,params:calls.append((method,params))
  c.submit(m.envelope(1,2,540))
  self.assertEqual(calls[0][0],'MbRtuClient.WriteHoldingRegisters');self.assertEqual(calls[0][1]['addr'],600)
  w=m.envelope(2,1,7);w[6]=1
  with self.assertRaises(ValueError):c.submit(w)
if __name__=='__main__':unittest.main()
