"""P0080 supervised chunk uploader. Offline plan by default; explicit live flag.
Existing installation must already run BL2. Does not install BL2 or change relays.
"""
import argparse,base64,json,time,struct,hashlib
from pathlib import Path
from urllib.request import Request,urlopen
from datetime import datetime,timezone
from ota import plan,transactions,frame,decode,crc
CORE='''let u=UART.get(0),rx='',waiting=false,tx='',stray=0;
if(!u)throw new Error('UART_UNAVAILABLE');
u.recv(function(d){if(waiting){rx+=d;if(rx.length>512)rx=rx.slice(0,513);}else{stray+=d.length;}});
function baud(b){if(b!==9600&&b!==115200)throw new Error('BAUD');u.configure({baud:b,format:'8N1'});return true;}
function stage(b){if(waiting)throw new Error('BUSY');tx=atob(b);if(tx.length>252)throw new Error('FRAME');return tx.length;}
function send(){if(waiting||stray)throw new Error('BUSY');rx='';waiting=true;return u.send(tx);}
function result(){waiting=false;return btoa(rx);}
Timer.set(3600000,false,function(){u.configure({baud:115200,format:'8N1'});Shelly.call('Script.Stop',{id:8});});
'''
def crc16(b):
 c=65535
 for v in b:
  c^=v
  for _ in range(8):c=(c>>1)^(0xa001 if c&1 else 0)
 return struct.pack('<H',c)
def system(sid,cmd,nonce,seconds=900):
 b=struct.pack('>BBHHB4H',sid,16,384,4,8,0xb180,cmd,nonce,seconds);return b+crc16(b)
def status_frame(sid):
 b=struct.pack('>BBHH',sid,4,384,16);return b+crc16(b)
class Sender:
 def __init__(self,host,device_id,out,rpc=None):
  self.host,self.device_id,self.out=host,device_id,Path(out);self.out.mkdir(exist_ok=False)
  self.rpc_override=rpc;self.changed=False
 def log(self,v):
  with (self.out/'rpc.jsonl').open('a') as f:f.write(json.dumps({'time':datetime.now(timezone.utc).isoformat(),**v})+'\n')
 def rpc(self,m,p=None):
  p=p or {};self.log({'method':m,'params':p})
  if self.rpc_override:r=self.rpc_override(m,p)
  else:
   request=Request('http://'+self.host+'/rpc',data=json.dumps({'id':1,'method':m,'params':p}).encode(),headers={'Content-Type':'application/json'})
   with urlopen(request,timeout=10) as f:r=json.load(f)
   if 'error' in r:raise RuntimeError(r)
   r=r['result']
  self.log({'result':r});return r
 def ev(self,c):
  r=self.rpc('Script.Eval',{'id':8,'code':c})['result']
  if c.startswith(('baud(', 'send(', 'stage(')):return json.loads(r) if isinstance(r,str) else r
  return r
 def identity(self,running=False):
  d=self.rpc('Shelly.GetDeviceInfo');assert d['id']==self.device_id and d['model']=='SPSW-202XE12UL'
  c=self.rpc('Serial.GetConfig',{'id':100});assert c['mode']=='js_uart' and c['serial']=={'baud':115200,'format':'8N1'}
  scripts=self.rpc('Script.List')['scripts'];assert any(x['id']==8 and x['name']=='P0075 write reference' for x in scripts)
  assert all(not x['enable'] and x['running']==(running and x['id']==8) for x in scripts)
  assert all(self.rpc('Switch.GetStatus',{'id':i})['output'] is False for i in (0,1))
 def code(self):
  s=''
  while True:
   r=self.rpc('Script.GetCode',{'id':8,'offset':len(s),'len':1024});s+=r['data']
   if not r['left']:return s
   if not r['data'] or len(s)>18000:raise RuntimeError('source bound')
 def start(self):
  self.identity();(self.out/'prior.js').write_text(self.code());self.changed=True
  for i in range(0,len(CORE),1024):self.rpc('Script.PutCode',{'id':8,'code':CORE[i:i+1024],'append':i!=0})
  assert self.code()==CORE
  self.rpc('Script.Start',{'id':8});time.sleep(.3);self.identity(True);assert self.ev('baud(9600)') is True
 def exchange(self,b,wait=.5):
  self.log({'tx_hex':b.hex()});assert self.ev('stage('+json.dumps(base64.b64encode(b).decode())+')')==len(b)
  assert self.ev('send()')==len(b);time.sleep(wait)
  r=base64.b64decode(self.ev('result()'),validate=True);self.log({'rx_hex':r.hex()});return r
 def status(self,sid):
  r=self.exchange(status_frame(sid));assert len(r)==37 and r[:3]==bytes([sid,4,32]) and r[-2:]==crc16(r[:-2])
  w=struct.unpack('>16H',r[3:-2]);assert w[:2]==(0xb180,2)
  return {'valid':w[2],'mode':w[3],'layout':w[4]<<16|w[5],'manifest_crc':w[6]<<16|w[7],'uid':[w[8]<<16|w[9],w[10]<<16|w[11],w[12]<<16|w[13]],'ready':w[14]}
 def ready(self,sid):
  for _ in range(20):
   s=self.status(sid)
   if s['ready']:return s
   time.sleep(.25)
  raise RuntimeError('Native AUTO/DHW/idle handoff not verified')
 def enter(self,sid,cmd):
  # Gate can race a new CN105 transaction; retry only explicit BUSY rejection.
  b=system(sid,cmd,0x80)
  for _ in range(20):
   r=self.exchange(b)
   if r==b[:6]+crc16(b[:6]):return
   if r==bytes([sid,0x90,6])+crc16(bytes([sid,0x90,6])):time.sleep(.3);continue
   raise RuntimeError('Ambiguous system handoff; stop '+r.hex())
  raise RuntimeError('CN105 remained busy')
 def transfer(self,p,target,peers,repair=False):
  if not 1<=target<=30 or target in peers or len(set(peers))!=len(peers):raise ValueError('address inventory')
  if any(not 1<=i<=30 for i in peers):raise ValueError('peer address')
  self.start();s=self.ready(target)
  if s['uid'] in ([0,0,0],[0xffffffff]*3):raise RuntimeError('invalid target UID')
  if s['layout']!=p['layout']:raise RuntimeError('wrong layout')
  if not s['valid']:
   if not repair:raise RuntimeError('invalid current image; explicit repair handoff required')
   p=dict(p,expected_manifest_crc=s['manifest_crc'],mask=127,slots=list(range(7)))
  elif s['manifest_crc']!=p['expected_manifest_crc']:raise RuntimeError('base image differs')
  seen=[s['uid']]
  for peer in peers:
   q=self.ready(peer)
   if not q['valid'] or q['uid'] in seen:raise RuntimeError('peer identity/state')
   seen.append(q['uid'])
  for peer in peers:self.enter(peer,254)
  self.enter(target,255);assert self.ev('baud(115200)') is True
  h=decode(self.exchange(frame(1,0)),1,0)
  if [h['uid0'],h['uid1'],h['uid2']]!=s['uid']:raise RuntimeError('OTA UID mismatch')
  sent=0
  for b in transactions(p,s['uid']):
   cmd=b[2];seq=struct.unpack('<H',b[4:6])[0]
   for attempt in range(3):
    # COMMIT scans every module twice; EXIT also validates the full set.
    r=self.exchange(b,2.0 if cmd in (4,6) else (1.0 if cmd==2 else .3))
    if r:break
   if not r:raise RuntimeError('No ACK; reset/handoff required')
   a=decode(r,cmd,seq)
   if a['status'] or a['next_seq']!=seq+1:raise RuntimeError(a)
   if [a['uid0'],a['uid1'],a['uid2']]!=s['uid']:raise RuntimeError('unexpected bus participant')
   sent+=1
   if sent%10==0:print('Acknowledged frames',sent,flush=True)
  assert self.ev('baud(9600)') is True;time.sleep(3)
  final=self.status(target)
  if not final['valid'] or final['manifest_crc']!=crc(bytes.fromhex(p['manifest'])[:56]) or final['uid']!=s['uid']:raise RuntimeError('post-reset verification')
  (self.out/'outcome.json').write_text(json.dumps({'verified':True,'exact_version_identity_verified':True,'ota_protocol':2,'target':target,'frames':sent,'final':final,'peers_wait_seconds':900},indent=2)+'\n')
 def stop(self):
  if self.changed:
   try:self.ev('baud(115200)')
   finally:
    self.rpc('Script.Stop',{'id':8});self.rpc('Script.SetConfig',{'id':8,'config':{'enable':False}})
  self.identity();(self.out/'cleanup.json').write_text('{"verified":true}\n')
def main():
 a=argparse.ArgumentParser();a.add_argument('old');a.add_argument('new');a.add_argument('--host');a.add_argument('--device-id');a.add_argument('--target',type=int);g=a.add_mutually_exclusive_group();g.add_argument('--isolated',action='store_true');g.add_argument('--peers',type=int,nargs='+');a.add_argument('--live',action='store_true');a.add_argument('--repair-native-confirmed',action='store_true');a.add_argument('--out',required=True);v=a.parse_args();p=plan(v.old,v.new)
 if not v.live:Path(v.out).write_text(json.dumps(p,indent=2)+'\n');print('Offline plan only');return
 if not all([v.host,v.device_id,v.target,v.isolated or v.peers]):a.error('live needs host, device-id, target and explicit isolated/peers inventory')
 if v.repair_native_confirmed:p=dict(p,mask=127,slots=list(range(7)))
 if not p['mask']:a.error('No changes')
 s=Sender(v.host,v.device_id,v.out)
 try:s.transfer(p,v.target,v.peers or [],v.repair_native_confirmed)
 finally:s.stop()
if __name__=='__main__':main()
