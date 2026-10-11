"""P0080 Mac/Shelly RPC simulation against real C OTA engine, no network."""
import sys,ctypes,tempfile,struct,json,base64,os
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import shelly_ota as h
from ota import *
c=ctypes.CDLL(str(Path(os.environ.get('P80_OTA_LIB','build/ota-test.dylib')).resolve()));c.ota_handle.argtypes=[ctypes.c_void_p,ctypes.c_size_t,ctypes.c_void_p,ctypes.c_size_t];c.ota_handle.restype=ctypes.c_size_t
old=os.environ.get('P80_OTA_OLD','build');new=os.environ.get('P80_OTA_NEW','build-next')
base=(Path(old)/'install.bin').read_bytes();p=plan(old,new);clock=[0.0]
h.time.sleep=lambda seconds:clock.__setitem__(0,clock[0]+seconds)
class Device:
 def __init__(self,drop=False,wrong_uid=False):
  self.available_at=0.0;self.source='old';self.running=False;self.baud=115200;self.tx=b'';self.rx=b'';self.dropped=False;self.drop=drop;self.wrong_uid=wrong_uid;self.reboot=False;self.peer_wait=False;self.commands=[]
 def exchange(self,b):
  if b[:2]==b'P8':
   assert self.baud==115200 and self.peer_wait
   out=ctypes.create_string_buffer(64);n=c.ota_handle(b,len(b),out,64);r=out.raw[:n]
   if b[2]==3 and self.drop and not self.dropped:self.dropped=True;return b''
   if b[2]==6:self.reboot=True
   return r
  assert self.baud==9600
  if b[1]==4:
   uid=[1,2,3] if b[0]==1 else [4,5,6]
   if self.wrong_uid:uid=[1,2,3]
   m=crc(bytes.fromhex(p['manifest'])[:56]) if self.reboot else p['expected_manifest_crc']
   w=[0xb180,2,1,0,p['layout']>>16,p['layout']&65535,m>>16,m&65535]+[x for v in uid for x in [v>>16,v&65535]]+[1,1]
   r=bytes([b[0],4,32])+struct.pack('>16H',*w);return r+h.crc16(r)
  self.commands.append((b[0],int.from_bytes(b[9:11],'big')))
  if b[0]==2:self.peer_wait=True
  else:assert self.peer_wait
  r=b[:6];return r+h.crc16(r)
 def rpc(self,m,p):
  if m=='Shelly.GetDeviceInfo':return {'id':'shellypro2-test','model':'SPSW-202XE12UL'}
  if m=='Serial.GetConfig':return {'mode':'js_uart','serial':{'baud':115200,'format':'8N1'}}
  if m=='Script.List':return {'scripts':[{'id':8,'name':'P0075 write reference','enable':False,'running':self.running}]}
  if m=='Switch.GetStatus':return {'output':False}
  if m=='Script.GetCode':return {'data':self.source[p['offset']:p['offset']+p['len']],'left':max(0,len(self.source)-p['offset']-p['len'])}
  if m=='Script.PutCode':self.source=(self.source if p['append'] else '')+p['code'];return {}
  if m=='Script.Start':self.running=True;return {}
  if m=='Script.Stop':self.running=False;return {}
  if m=='Script.SetConfig':return {}
  if m=='Script.Eval':
   code=p['code']
   if code.startswith('baud('):self.baud=int(code[5:-1]);return {'result':'true'}
   if code.startswith('stage('):self.tx=base64.b64decode(json.loads(code[6:-1]));return {'result':str(len(self.tx))}
   if code=='send()':
    self.rx=self.exchange(self.tx);self.available_at=clock[0]+(.7 if self.tx[:3]==b'P8\x04' else 0);return {'result':str(len(self.tx))}
   if code=='result()':
    assert clock[0]>=self.available_at,'host closed receive window before delayed COMMIT ACK'
    return {'result':base64.b64encode(self.rx).decode()}
  raise AssertionError((m,p))
for drop in [False,True]:
 c.reset_image(base);c.ota_reset();d=Device(drop)
 with tempfile.TemporaryDirectory() as td:
  s=h.Sender('unused','shellypro2-test',Path(td)/'run',d.rpc)
  try:s.transfer(p,1,[2])
  finally:s.stop()
 assert c.modules_valid() and d.commands==[(2,254),(1,255)] and not d.running
c.reset_image(base);c.ota_reset();d=Device(wrong_uid=True)
with tempfile.TemporaryDirectory() as td:
 s=h.Sender('unused','shellypro2-test',Path(td)/'run',d.rpc)
 try:
  try:s.transfer(p,1,[2]);raise AssertionError('duplicate UID accepted')
  except RuntimeError as e:assert 'peer identity' in str(e)
 finally:s.stop()
assert not d.commands and c.count_erase()==0
print('PASS host through fake Shelly RPC into actual C: target/WAIT ordering, full chunk update, lost ACK duplicate, post-reset validation, duplicate UID rejected, cleanup')

# Old status protocol is rejected before sending ENTER/WAIT or touching flash.
c.reset_image(base);c.ota_reset();d=Device();original=d.exchange
def legacy_status(b):
 r=original(b)
 if b[1]==4 and b[:2]!=b'P8':
  r=bytearray(r);r[5:7]=b'\x00\x01';r[-2:]=h.crc16(r[:-2]);return bytes(r)
 return r
d.exchange=legacy_status
with tempfile.TemporaryDirectory() as td:
 s=h.Sender('unused','shellypro2-test',Path(td)/'run',d.rpc)
 try:
  try:s.transfer(p,1,[2]);raise RuntimeError('legacy protocol accepted')
  except AssertionError:pass
 finally:s.stop()
assert not d.commands and c.count_erase()==0
print('PASS host protocol2: old status rejected before handoff')
