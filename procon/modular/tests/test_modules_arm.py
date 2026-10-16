"""P0080 actual independently linked images: ABI, init and native handoff gate."""
import json,struct,sys
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import *
from unicorn.arm_const import *
p=Path(sys.argv[1]);u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
for a,n in [(0x08000000,0x20000),(0x20000000,0x10000),(0x40000000,0x30000),(0xe000e000,0x2000),(0x1fff7000,0x1000)]:u.mem_map(a,n)
u.mem_write(0x1fff7590,struct.pack('<III',1,2,3))
u.mem_write(0x08008000,(p/'install.bin').read_bytes());symbols={};slots=json.loads((p/'sizes.json').read_text())['slots']
for slot in slots:
 with (p/(slot['name']+'.elf')).open('rb') as f:
  elf=ELFFile(f);symbols[slot['name']]={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols() if s['st_shndx'] not in ('SHN_ABS','SHN_UNDEF')}
def stop(uc,a,n,d):
 if a==0x2000f000:uc.emu_stop()
u.hook_add(UC_HOOK_CODE,stop)
def call(slot,name,*args):
 u.reg_write(UC_ARM_REG_SP,0x20004000);u.reg_write(UC_ARM_REG_LR,0x2000f001)
 for r,v in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],args):u.reg_write(r,v)
 u.emu_start(symbols[slot][name],0,count=10000000)
 assert u.reg_read(UC_ARM_REG_PC)==0x2000f000
 return u.reg_read(UC_ARM_REG_R0)
def put(slot,name,v,n=4):u.mem_write(symbols[slot][name],v.to_bytes(n,'little'))
assert call('bl2','modules_valid')==1
u.mem_write(0x20001000,b'\xa5'*10000);call('bl2','modules_load');call('common','cn_init')
# Real cross-slot functions return existing P76 identity and revision.
assert call('common','cn_read',0)==888 and call('common','cn_read',1)==76 and call('common','cn_read',68)==2
# Every export veneer resolves to the matching function, independently of movement.
for slot in slots:
 for i,name in enumerate(slot['exports']):
  a=slot['address']+(512 if slot['id']==0 else 64)+4*i
  hits=[]
  def hook(uc,pc,n,d):
   hits.append(pc)
   if len(hits)==2:uc.emu_stop()
  h=u.hook_add(UC_HOOK_CODE,hook);u.emu_start(a|1,0,count=2);u.hook_del(h)
  assert hits==[a,symbols[slot['name']][name]&~1],(slot['name'],name,hits)
# The adaptive model lives in Service to retain Mode's fixed 12KiB boundary.
# These internal veneers follow its ten public exports without changing the
# public export count or layout fingerprint.
if 'effect_model_op' in symbols['service']:
 for i,name in enumerate(('effect_model_op','effect_model_tick')):
  a=slots[5]['address']+64+4*(10+i);hits=[]
  def private_hook(uc,pc,n,d):
   hits.append(pc)
   if len(hits)==2:uc.emu_stop()
  h=u.hook_add(UC_HOOK_CODE,private_hook);u.emu_start(a|1,0,count=2);u.hook_del(h)
  assert hits==[a,symbols['service'][name]&~1],(name,hits)
# P0080 pump A3: actual cross-slot service, telemetry and Modbus diagnostics.
if bytes(u.mem_read(symbols['service']['codes'],4))==bytes([27,28,18,19]):
 call('service','svc_init')
 for code,value in [(27,4),(28,3),(18,7),(19,2500)]:
  call('service','svc_start_cycle');assert call('service','svc_due',0,0x2000e000)==1
  assert bytes(u.mem_read(0x2000e000,1))==bytes([code])
  call('service','svc_sent',0)
  u.mem_write(0x2000e000,bytes([0xa3,0,code,2,value&255,value>>8])+bytes(10))
  assert call('service','svc_reply',0x2000e000,1,1)==1
 assert call('common','cn_read',87)==7 and call('common','cn_read',93)==2500
 assert call('drift','tele_read',121)==1 and call('drift','tele_read',123)==7
 assert call('drift','tele_read',150)==1 and call('drift','tele_read',151)==1
 call('service','svc_link',0,2)
 assert call('drift','tele_read',150)==2 and call('drift','tele_read',151)==2
 print('PASS actual ARM pump A3: four codes, level/RPM diagnostics, derived running and link-loss invalidation')
 call('common','cn_init')
# P0080: compiled Common/Service contract for separate A3 frequency records.
if 'frequency' in p.name or 'delta-sweep' in p.name:
 call('service','svc_init')
 for code,value in [(27,4),(28,3),(18,7),(19,2500),(16,70),(17,92)]:
  call('service','svc_start_cycle');assert call('service','svc_due',0,0x2000e000)==1
  assert bytes(u.mem_read(0x2000e000,1))==bytes([code])
  call('service','svc_sent',0)
  u.mem_write(0x2000e000,bytes([0xa3,0,code,2,value&255,value>>8])+bytes(10))
  assert call('service','svc_reply',0x2000e000,1,1)==1
 assert [call('common','cn_read',a) for a in range(372,384)]==[70,1,0,2,1,1,92,1,0,2,1,1]
 call('service','svc_tick',60000,60001)
 assert call('common','cn_read',373)==0 and call('common','cn_read',379)==0
 assert call('common','cn_read',372)==70 and call('common','cn_read',378)==92
 call('common','cn_init')
 print('PASS compiled A3/16/17 distinct raw values, status, completion and TTL')
# P0080 dense-frequency schedule executes compiled Service via existing ABI.
if 'dense' in p.name:
 settings={256:4,263:2,275:6000}
 def control_stub(uc,pc,n,d):
  if pc==(symbols['mode']['ctl_read']&~1):
   uc.reg_write(UC_ARM_REG_R0,settings.get(uc.reg_read(UC_ARM_REG_R0),0))
   uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
 h=u.hook_add(UC_HOOK_CODE,control_stub)
 try:
  call('service','svc_init')
  seq=[16,17,16,17,27,16,17,16,17,28,16,17,16,17,18,16,17,16,17,19]
  for i,code in enumerate(seq):
   t=i*2000
   call('service','svc_start_cycle');assert call('service','svc_due',t,0x2000e000)==1
   assert bytes(u.mem_read(0x2000e000,1))==bytes([code])
   call('service','svc_sent',t)
   u.mem_write(0x2000e000,bytes([0xa3,0,code,0])+bytes(12))
   assert call('service','svc_reply',0x2000e000,t+10,1)==1
   assert call('service','svc_due',t+999,0x2000e020)==0
   assert call('service','svc_due',t+1000,0x2000e020)==1
   assert bytes(u.mem_read(0x2000e020,1))==bytes([code])
   call('service','svc_sent',t+1000)
   u.mem_write(0x2000e000,bytes([0xa3,0,code,2,42,0])+bytes(10))
   assert call('service','svc_reply',0x2000e000,t+1010,1)==1
  settings[256]=0
  for code in [16,17,27,28,18,19]:
   call('service','svc_start_cycle');assert call('service','svc_due',50000,0x2000e000)==1
   assert bytes(u.mem_read(0x2000e000,1))==bytes([code])
   call('service','svc_sent',50000)
   u.mem_write(0x2000e000,bytes([0xa3,0,code,2,42,0])+bytes(10))
   assert call('service','svc_reply',0x2000e000,50010,1)==1
 finally:u.hook_del(h)
 call('common','cn_init')
 print('PASS compiled dense sequence, exclusive retries and return to normal queue')
# P0080 focused fixed60 profile: compiled Service preserves the ordinary cursor.
if 'frequency-focus' in p.name or 'delta-sweep' in p.name:
 settings={256:0,263:2,275:6000}
 def focus_control_stub(uc,pc,n,d):
  if pc==(symbols['mode']['ctl_read']&~1):
   uc.reg_write(UC_ARM_REG_R0,settings.get(uc.reg_read(UC_ARM_REG_R0),0))
   uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
 h=u.hook_add(UC_HOOK_CODE,focus_control_stub)
 try:
  def focus_complete(code,stamp,status=2):
   u.mem_write(0x2000e000,bytes([0xa3,0,code,status,42,0])+bytes(10))
   assert call('service','svc_reply',0x2000e000,stamp,1)==1
  def focus_due(code,stamp):
   assert call('service','svc_due',stamp,0x2000e020)==1
   assert bytes(u.mem_read(0x2000e020,1))==bytes([code])
  call('service','svc_init');call('service','svc_start_cycle');focus_due(27,0)
  call('service','svc_sent',0);focus_complete(27,10);settings[256]=4
  for i in range(12):
   stamp=2000+i*2000
   if 'delta-sweep' in p.name:settings.update({263:0 if i%3==0 else 2,275:2000+i*400})
   call('service','svc_start_cycle');focus_due(17,stamp);call('service','svc_sent',stamp)
   focus_complete(17,stamp+10,0)
   if i==5:settings[256]=0
   assert call('service','svc_due',stamp+999,0x2000e020)==0
   focus_due(17,stamp+1000);call('service','svc_sent',stamp+1000);focus_complete(17,stamp+1010)
   settings[256]=4
  assert call('service','svc_read',382)==12 and call('service','svc_read',376)==0
  settings[256]=0
  for code in [28,18,19,16,17,27]:
   call('service','svc_start_cycle');focus_due(code,40000)
   call('service','svc_sent',40000);focus_complete(code,40010)
  gates=[(0,2,6000),(3,2,6000),(4,5,6000),(5,2,6000)]
  gates += [(4,1,0),(4,3,0),(4,4,6500),(0,0,0),(3,0,0),(5,0,0)] if 'delta-sweep' in p.name else [(4,2,5999)]
  for state,mode,target in gates:
   settings.update({256:state,263:mode,275:target})
   call('service','svc_init');call('service','svc_start_cycle');focus_due(27,0)
 finally:u.hook_del(h)
 call('common','cn_init')
 print('PASS actual ARM focus: every operation17, retry ownership, profile gates and retained ordinary cursor')
# P0080: execute the new admission boundary in the actual linked Common image.
# Only initial link/round position is seeded; requests, scheduler, service jobs,
# TX framing, response parsing and diagnostic status use their compiled APIs.
if 'frequency-target' in p.name or 'frequency-focus' in p.name or 'delta-sweep' in p.name:
 def diagnostic_fixture(fast_index):
  call('common','cn_init');call('service','svc_link',1,10000)
  for name,value,size in [('linked',1,1),('now',10000,4),('last_tick',10000,4),('last_good',10000,4),('fast_index',fast_index,1)]:
   put('common',name,value,size)
  assert call('mode','ctl_read',256)==0 and call('mode','ctl_busy')==0
 def queue_target():
  u.mem_write(0x2000e000,struct.pack('<8H',0x81d1,1,0xfd,1,2,17,0,0))
  assert call('common','cn_command',0x2000e000)==0
  assert call('common','cn_read',606)==1
 def drain_common():
  frame=bytearray()
  while call('common','cn_tx_byte',0x2000e040):
   frame+=u.mem_read(0x2000e040,1);call('common','cn_tx_sent')
   assert len(frame)<=22
  if frame:assert len(frame)==22 and sum(frame)%256==252
  return bytes(frame)
 def common_reply(frame,stamp,status=0):
  payload=bytearray(16);payload[0]=frame[5]
  if frame[5]==0xa3:payload[1:4]=bytes([frame[6],frame[7],status])
  reply=bytearray([252,0x62,2,0x7a,16])+payload
  reply.append((252-sum(reply))&255)
  for byte in reply:call('common','cn_feed',byte,stamp,0)
 diagnostic_fixture(8);queue_target();call('common','cn_tick',10050)
 frame=drain_common()
 assert call('common','cn_read',39)==5 and frame[5:8]==bytes([0xa3,0,17])
 assert call('common','cn_read',606)==2 and call('common','cn_read',612)==1
 # A partly completed FAST round must finish in its established order.
 diagnostic_fixture(3);queue_target()
 for offset,query in enumerate([0x0b,9,0x15,0x26,0x28]):
  stamp=10050+offset*270;call('common','cn_tick',stamp);frame=drain_common()
  assert call('common','cn_read',39)==2 and frame[5]==query
  assert call('common','cn_read',606)==1
  common_reply(frame,stamp+220)
 call('common','cn_tick',11400);frame=drain_common()
 assert call('common','cn_read',39)==5 and frame[5:8]==bytes([0xa3,0,17])
 # Already-started SERVICE ownership survives queued diagnostic admission,
 # both while waiting for a response and throughout pending/timeout retries.
 diagnostic_fixture(8);call('common','cn_tick',10050);frame=drain_common()
 assert call('common','cn_read',39)==3 and frame[5:8]==bytes([0xa3,0,27])
 queue_target();call('common','cn_tick',10100)
 assert call('common','cn_read',39)==3 and drain_common()==b''
 common_reply(frame,10270,0)
 assert call('service','svc_read',32)==3
 call('common','cn_tick',11049)
 assert call('common','cn_read',39)==0 and drain_common()==b''
 call('common','cn_tick',11050);frame=drain_common()
 assert call('common','cn_read',39)==3 and frame[7]==27 and call('common','cn_read',606)==1
 call('common','cn_tick',11850) # No response: unchanged800ms timeout.
 assert call('service','svc_read',32)==3 and drain_common()==b''
 call('common','cn_tick',12049);assert drain_common()==b''
 call('common','cn_tick',12050);frame=drain_common()
 assert call('common','cn_read',39)==3 and frame[7]==27
 common_reply(frame,12270,2);assert call('service','svc_read',32)==4
 call('common','cn_tick',12320);frame=drain_common()
 assert call('common','cn_read',39)==5 and frame[7]==17 # Existing DONE admission.
 call('common','cn_init')
 print('PASS actual ARM diagnostic boundary: READY after FAST admits17, partial FAST completes, active service/pending/timeout owns retries, DONE admission retained')
 # Public mailbox must survive composition: an older Dispatcher can reject
 # these addresses even when direct Common calls above work correctly.
 diagnostic_fixture(8)
 u.mem_write(0x2000e080,struct.pack('<III',1,2,3))
 call('bl2','identity_init_dip',0x2000e080,0x61,1);put('bl2','valid',1)
 def mailbox_crc(b):
  c=65535
  for v in b:
   c^=v
   for _ in range(8):c=(c>>1)^(0xa001 if c&1 else 0)
  return struct.pack('<H',c)
 def public_mailbox(b):
  b+=mailbox_crc(b);u.mem_write(0x2000e080,b)
  n=call('bl2','normal',0x2000e080,len(b),0x2000e200)
  r=bytes(u.mem_read(0x2000e200,n))
  assert len(r)>=5 and r[-2:]==mailbox_crc(r[:-2]),r.hex()
  return r
 for addr in (600,616):
  r=public_mailbox(struct.pack('>BBHH',1,4,addr,16))
  assert r[:3]==bytes([1,4,32]),('Public mailbox missing',addr,r.hex())
 words=struct.pack('>8H',0x81d1,1,0xfd,1,2,17,0,0)
 r=public_mailbox(bytes([1,16,1,44,0,8,16])+words)
 assert r[1:3]==bytes([0x90,3]) and call('common','cn_read',606)==0
 request=bytes([1,16,2,88,0,8,16])+words
 assert public_mailbox(request)[:6]==request[:6]
 assert call('common','cn_read',606)==1
 call('common','cn_tick',10050);frame=drain_common()
 assert frame[5:8]==bytes([0xa3,0,17])
 common_reply(frame,10270,2)
 r=public_mailbox(bytes.fromhex('010402580010'));w=struct.unpack('>16H',r[3:-2])
 assert w[:7]==(0x81d1,1,0xfc,1,2,17,3) and w[9]==1 and w[12]==1,w
 r=public_mailbox(bytes.fromhex('010402680010'))
 raw=b''.join(struct.pack('<H',v) for v in struct.unpack('>16H',r[3:-2])[:11])
 assert raw[:9]==bytes([252,0x62,2,0x7a,16,0xa3,0,17,2]) and sum(raw)%256==252
 call('common','cn_init')
 print('PASS actual ARM public mailbox through BL2/Dispatcher: read600/616, write600, reject diagnostic at300, complete17 and raw response')
put('common','linked',1,1);put('common','seen26',1,1);put('common','seen28',1,1);put('common','now',5000);put('common','native26_at',5000);put('common','native28_at',5000)
p26=bytearray(16);p26[6]=2;u.mem_write(symbols['common']['native26'],bytes(p26));u.mem_write(symbols['common']['native28'],bytes(16))
assert call('common','maintenance_ready')==1
for name,v,n in [('linked',0,1),('owner',3,1),('now',15000,4)]:
 old=bytes(u.mem_read(symbols['common'][name],n));put('common',name,v,n);assert call('common','maintenance_ready')==0;u.mem_write(symbols['common'][name],old)
for i in [3,4,5,6,10]:
 u.mem_write(symbols['common']['native28']+i,b'\x01');assert call('common','maintenance_ready')==0;u.mem_write(symbols['common']['native28']+i,b'\x00')
p26[6]=1;u.mem_write(symbols['common']['native26'],bytes(p26));assert call('common','maintenance_ready')==0
# Actual resident system router. UART TX is intercepted at its entry; CRC and
# command gate execute as compiled, and baud change executes against MMIO RAM.
def crc16(b):
 c=65535
 for v in b:
  c^=v
  for _ in range(8):c=(c>>1)^(0xa001 if c&1 else 0)
 return struct.pack('<H',c)
u.mem_write(0x2000e000,struct.pack('<III',1,2,3));call('bl2','identity_init_dip',0x2000e000,0x61,1);put('bl2','valid',1)
def router(b):
 b+=crc16(b);u.mem_write(0x2000e000,b)
 n=call('bl2','normal',0x2000e000,len(b),0x2000e200)
 return bytes(u.mem_read(0x2000e200,n))
assert router(bytes.fromhex('000401800010'))==b''
r=router(bytes.fromhex('010401800010'));assert r[:3]==bytes([1,4,32]) and r[-2:]==crc16(r[:-2])
import binascii
w=struct.unpack('>16H',r[3:-2]);assert w[1]==2 and (w[6]<<16|w[7])==binascii.crc32((p/'manifest.bin').read_bytes()[:56])
b=bytes.fromhex('01100180000408b18000fe00800384')
r=router(b);assert r[1:3]==bytes([0x90,6]) # fixed-flow mode is not native handoff
p26[6]=2;u.mem_write(symbols['common']['native26'],bytes(p26))
sent=[]
def tx_hook(uc,pc,n,d):
 if pc==(symbols['bl2']['uart_send']&~1):
  sent.append(bytes(uc.mem_read(uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1))))
  uc.reg_write(UC_ARM_REG_R0,1);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
h=u.hook_add(UC_HOOK_CODE,tx_hook)
assert router(b)==b'' and int.from_bytes(u.mem_read(symbols['bl2']['mode'],4),'little')==1
assert sent[-1]==b[:6]+crc16(b[:6])
put('bl2','mode',0);b=bytes.fromhex('01100180000408b18000ff00800384');assert router(b)==b''
assert int.from_bytes(u.mem_read(symbols['bl2']['mode'],4),'little')==2 and int.from_bytes(u.mem_read(0x4000480c,4),'little')==139
u.hook_del(h)
# P0080 direct-target replacement executed in the actual linked ARM mode slot.
call('mode','ctl_init');native={'power':1,'mode':2,'flow':2950,'dhw':5200};writes=[];tm=0
def submit(seq,mode,flow=0,lease=30):
 words=[0xc072,seq,mode,flow,0,0 if mode==1 else lease,1 if flow else 0,2]
 u.mem_write(0x2000e600,struct.pack('<8H',*words))
 return call('mode','ctl_submit',0x2000e600,tm)
def step():
 global tm
 if call('mode','ctl_next',0x2000e700,0x2000e710,tm):
  ty=u.mem_read(0x2000e700,1)[0];req=bytes(u.mem_read(0x2000e710,16));reply=bytearray(16)
  if ty==0x41:
   writes.append(req[1])
   if req[1]==8:native['mode']=req[6]
   elif req[1]==0x80:native['flow']=int.from_bytes(req[10:12],'big')
   elif req[1]==0x88:native['mode']=req[6];native['flow']=int.from_bytes(req[10:12],'big')
   else:raise AssertionError(('unexpected SET',req))
   u.mem_write(0x2000e800,bytes(reply));assert call('mode','ctl_reply',0x61,0x2000e800,1,tm)
  else:
   assert ty==0x42;reply[0]=req[0]
   if req[0]==0x26:
    reply[3]=native['power'];reply[4]=native.get('actual',2);reply[6]=native['mode'];reply[8:10]=struct.pack('>H',native['dhw'])
   elif req[0]==9:reply[5:7]=struct.pack('>H',native['flow'])
   else:assert req[0]==0x28
   u.mem_write(0x2000e800,bytes(reply));assert call('mode','ctl_reply',0x62,0x2000e800,16,tm)
 tm+=100
def until(state):
 for _ in range(200):
  if call('mode','ctl_read',256)==state:return
  step()
 raise AssertionError('ARM control deadline')
assert submit(1,2,3250)==0;until(4);assert native['mode']==1 and native['flow']==3250
assert submit(2,2,3200)==0 and call('mode','ctl_read',258)==1
assert submit(3,2,3800)==6 # pending update cannot be replaced
until(4);assert native['flow']==3200 and call('mode','ctl_read',258)==2
assert submit(3,2,3800)==0;until(4)
assert native['flow']==3800 and writes==[8,0x80,0x80,0x80]
assert call('mode','ctl_read',269)==2 and call('mode','ctl_read',270)==2950
assert submit(4,1)==0;until(0)
assert native['mode']==2 and native['flow']==2950 and writes[-2:]==[0x80,8]
print('PASS actual ARM direct targets: FLOW-only replacements, pending BUSY, original snapshot and AUTO restoration')
# P0080 fixed60 candidate: exercise compiled admission, readback and restoration.
if p.name=='build-fixed60':
 assert submit(5,2,6001)==3
 assert submit(5,2,6000)==0;until(4);assert native['flow']==6000
 assert submit(6,1)==0;until(0);assert native['mode']==2 and native['flow']==2950
 print('PASS actual ARM fixed60:6001 rejected,6000 applied/read back,AUTO restored')
# P0080 delta sweep raises only the manual-flow envelope, preserving restoration.
if 'delta-sweep' in p.name:
 assert submit(5,2,6501)==3
 assert submit(5,2,6500)==0;until(4);assert native['flow']==6500
 assert call('mode','ctl_read',270)==2950 and call('mode','ctl_read',269)==2
 before=len(writes)
 assert submit(6,2,3500)==0;until(4)
 assert native['flow']==3500 and writes[before:]==[0x80]
 assert submit(7,2,6499)==0;until(4);assert native['flow']==6499
 assert call('mode','ctl_read',270)==2950
 assert submit(8,1)==0;until(0);assert native['mode']==2 and native['flow']==2950
 for words in ([0xc072,9,3,0,6001,180,2,2],[0xc076,9,5,6000,5501,180,1,3]):
  u.mem_write(0x2000e600,struct.pack('<8H',*words))
  assert call('mode','ctl_submit',0x2000e600,tm)==3
 assert submit(9,2,6500)==0;until(4);tm+=30001;until(0)
 assert native['mode']==2 and native['flow']==2950 and call('mode','ctl_read',260)==7
 print('PASS actual ARM delta sweep:6500 accepted/6501 rejected, direct retargets, original preserved, AUTO/lease restored, DHW/EFFECT ceilings unchanged')
# Private helper probes remain useful when the compiler preserves their ABI.
# LTO may erase/clone them; qualification then uses real exported ctl_* APIs.
private_helpers = {'effect_begin','effect_capture','effect_decide','effect_verified',
 'effect_pause_demand','effect_pending_demand','effect_entry_demand'}
if private_helpers <= set(symbols['mode']):
 # P0080 actual ARM Hz-leading startup and thermal guard.
 measure=0x2000e000
 source_clock=0
 def source_accept(hz=None,supply=None):
  # Exercise the real Drift parser/export; no fabricated tele_sample structs.
  if hz is not None:
   u.mem_write(0x2000e900,bytes([4,hz])+bytes(14));call('drift','tele_accept',0x2000e900)
  if supply is not None:
   b=bytearray(16);b[0]=0x0c;b[1:3]=struct.pack('>H',supply)
   u.mem_write(0x2000e900,bytes(b));call('drift','tele_accept',0x2000e900)
 def fresh_measure(payload):
  # Older isolated control fixtures represent a new real source observation.
  u.mem_write(measure,payload)
  values=struct.unpack('<4i2I4HB3x',payload)
  source_accept(hz=values[9],supply=values[3] if 0<=values[3]<=10000 else None)
 def fresh_decide(measure,flow,stamp):
  global source_clock
  call('drift','tele_tick',(stamp-source_clock)&0xffffffff);source_clock=stamp
  values=struct.unpack('<4i2I4HB3x',bytes(u.mem_read(measure,36)))
  source_accept(hz=values[9],supply=values[3])
  return call('mode','effect_decide',measure,flow,stamp)
 fresh_measure(struct.pack('<4i2I4HB3x',2000,2000,2000,3000,0,20000,0,4,2,30,1))
 call('mode','effect_begin',6000,5500,0);call('mode','effect_capture',3050,0)
 assert fresh_decide(measure,3050,0)==4500
 call('mode','effect_verified',4500,0)
 fresh_measure(struct.pack('<4i2I4HB3x',5500,4500,4000,4000,0,20000,0,4,2,40,1))
 assert fresh_decide(measure,4500,15000)==0
 assert fresh_decide(measure,4500,30000)==4450
 print('PASS actual ARM Hz-leading demand:45C startup and thermal-priority reduction')
 # Early demand uses one coherent pair while the real averaging window settles.
 def startup_measure(supply=2900,pairs=1,age=1000):
  fresh_measure(struct.pack('<4i2I4HB3x',2000,2000,2000,supply,age,0,9,pairs,2,26,0))
 for pairs,age in [(0,1000),(1,15000)]:
  call('mode','effect_begin',6000,5500,0);call('mode','effect_capture',3050,0)
  startup_measure(pairs=pairs,age=age)
  assert call('mode','effect_pause_demand',measure,3050,0)==0
  assert call('mode','effect_pending_demand')==0
 call('mode','effect_begin',6000,5500,0);call('mode','effect_capture',3050,0)
 startup_measure()
 assert call('mode','effect_pause_demand',measure,3050,0)==4500
 assert call('mode','effect_pending_demand')==2
 call('mode','effect_verified',4500,1)
 assert call('mode','effect_pending_demand')==0
 startup_measure(supply=3800)
 assert call('mode','effect_pause_demand',measure,4500,1000)==0
 assert call('mode','effect_pause_demand',measure,4500,30001)==4450
 assert call('mode','effect_pending_demand')==2
 call('mode','effect_verified',4450,30001)
 startup_measure(supply=3950)
 assert call('mode','effect_pause_demand',measure,4450,31000)==0
 assert call('mode','effect_pause_demand',measure,4450,60001)==4400
 call('mode','effect_verified',4400,60001)
 assert call('mode','effect_pending_demand')==0
 print('PASS actual ARM early startup: first SETTLING pair, kind2/readback, soft thermal taper with30s cadence, absent/aged pair rejection')
 # Cached READY plus a newer native pause must yield in the actual ARM controller.
 call('mode','ctl_init')
 fresh_measure(struct.pack('<4i2I4HB3x',2000,2000,2000,3000,0,20000,0,4,2,30,1))
 call('mode','ctl_feedback',measure)
 u.mem_write(0x2000e600,struct.pack('<8H',0xc076,1,5,6000,5500,180,1,3))
 assert call('mode','ctl_submit',0x2000e600,0)==0
 fresh_measure(struct.pack('<4i2I4HB3x',2000,2000,2000,3000,0,20000,0,4,0,30,1))
 call('mode','ctl_feedback',measure);call('mode','ctl_tick',0)
 assert call('mode','ctl_read',256)==1 and call('mode','ctl_read',260)==0
 # An unsupported native mode still aborts before a write.
 fresh_measure(struct.pack('<4i2I4HB3x',2000,2000,2000,3000,0,20000,0,4,3,30,1))
 call('mode','ctl_feedback',measure);call('mode','ctl_tick',1)
 assert call('mode','ctl_read',256)==0 and call('mode','ctl_read',260)==8
 print('PASS actual ARM cached READY/native transition: allowed pause yields; invalid native mode aborts')
 # Offline atomic-entry experiment: execute the actual combined transaction.
 for supply,actual,expected in [(3200,2,4500),(3800,2,4200),(3950,2,3850),(4000,2,3800),(4050,2,3750),(10000,2,3050),(3200,0,3250)]:
  call('mode','ctl_init');native={'power':1,'mode':2,'flow':3050,'dhw':5200,'actual':actual};writes=[];tm=0
  fresh_measure(struct.pack('<4i2I4HB3x',2000,2000,2000,supply,0,20000,0,4,2,30,1))
  call('mode','ctl_feedback',measure)
  u.mem_write(0x2000e600,struct.pack('<8H',0xc076,1,5,6000,5500,180,1,3))
  assert call('mode','ctl_submit',0x2000e600,0)==0
  until(4)
  assert native['mode']==1 and native['flow']==expected and writes==[0x88]
  assert call('mode','ctl_read',258)==1 and call('mode','ctl_read',270)==3050
  assert submit(2,1)==0;until(0)
  assert native['mode']==2 and native['flow']==3050
  assert writes[-1]==8 and (expected==3050 or writes[-2:]==[0x80,8])
 call('mode','effect_begin',6000,5500,0);call('mode','effect_capture',3050,0)
 fresh_measure(struct.pack('<4i2I4HB3x',-2147483648,2000,2000,3200,0,0,9,1,2,26,0))
 assert call('mode','effect_entry_demand',measure,3050,2,0)==0
 assert call('mode','effect_pending_demand')==0
 print('PASS actual ARM atomic entry: combined45C, shared thermal caps, fresh native pause overrides old Hz, dual readback and original AUTO, partial pair rejection')
 # Predictive-law regressions executed from the final linked mode image.
 call('mode','effect_begin',6000,5500,0);call('mode','effect_capture',4500,0)
 for stamp in range(0,120001,5000):
  power=5700+stamp//400
  fresh_measure(struct.pack('<4i2I4HB3x',power-150,power,power,3300,0,60000,0,4,2,42,1))
  assert fresh_decide(measure,4500,stamp)==0
 call('mode','effect_begin',6000,5500,0);call('mode','effect_capture',4500,0)
 for stamp in range(0,60001,5000):
  hz=42 if stamp<30000 else 52
  fresh_measure(struct.pack('<4i2I4HB3x',4800,4800,4800,3300,0,60000,0,4,2,hz,1))
  target=fresh_decide(measure,4500,stamp)
  assert target==(4400 if stamp==60000 else 0)
  if target:call('mode','effect_verified',target,stamp)
 print('PASS actual ARM predictive law: flat42Hz/rising mean holds;52Hz future overshoot receives bounded100cC braking')
 # Thermal correction converges gently, preserving a positive native margin.
 call('mode','effect_begin',6000,5500,0);call('mode','effect_capture',4500,0)
 target=4500;last_change=None
 for stamp in range(0,360001,1000):
  fresh_measure(struct.pack('<4i2I4HB3x',4000,4000,4000,3950,0,60000,0,12,2,40,1))
  nxt=fresh_decide(measure,target,stamp)
  if nxt:
   assert target-50<=nxt<=target and nxt>=4000
   if last_change is not None:assert stamp-last_change>=30000
   last_change=stamp;target=nxt;call('mode','effect_verified',nxt,stamp)
 assert target==4000
 for stamp in range(365000,720001,5000):
  fresh_measure(struct.pack('<4i2I4HB3x',4000,4000,4000,3800,0,60000,0,12,2,40,1))
  nxt=fresh_decide(measure,target,stamp)
  if nxt:
   assert target-50<=nxt<=target+100
   target=nxt;call('mode','effect_verified',nxt,stamp)
 assert target>4200
 print('PASS actual ARM thermal feedback: <=0.5C down/30s, positive actual+0.5C margin, gradual cooling recovery')

 # Retained response prevents new gas on the first frequency plateau.
 call('mode','effect_begin',6000,5500,0);call('mode','effect_capture',4500,0)
 target=4500;at60=0
 for stamp in range(0,90001,5000):
  hz=32 if stamp<30000 else 42
  fresh_measure(struct.pack('<4i2I4HB3x',5500,5500,5500,3300,0,60000,0,4,2,hz,1))
  nxt=fresh_decide(measure,target,stamp)
  if nxt:target=nxt;call('mode','effect_verified',target,stamp)
  if stamp==60000:at60=target
 assert target<=at60
 at90=target
 for stamp in range(95000,300001,5000):
  nxt=fresh_decide(measure,target,stamp)
  if nxt:target=nxt;call('mode','effect_verified',target,stamp)
 assert target>at90
 # Weak, underpowered demand recovers1C, then still corrects during modest rise.
 call('mode','effect_begin',6000,5500,0);call('mode','effect_capture',3900,0)
 target=3900
 for stamp in range(0,90001,5000):
  power=6000 if stamp<30000 else 4800 if stamp<=60000 else 5000
  fresh_measure(struct.pack('<4i2I4HB3x',power,power,power,3800,0,60000,0,4,2,40,1))
  nxt=fresh_decide(measure,target,stamp)
  if nxt:target=nxt;call('mode','effect_verified',target,stamp)
  if stamp==60000:assert target==4000
 assert target>4000
 print('PASS actual ARM response memory: plateau hold, bounded decay,1C recovery and correction despite modest power rise')

 # Genuine asynchronous generations across separately linked Drift and Mode.
 def source_replay(poll,base=0):
  call('drift','tele_init');call('mode','effect_begin',6000,5500,base)
  call('mode','effect_capture',4500,base);demand=4500
  hz=42
  for elapsed in range(0,90001,poll):
   if elapsed:call('drift','tele_tick',poll)
   if elapsed%10000==0:
    hz=42 if elapsed<30000 else 52;source_accept(hz=hz)
   if elapsed%15000==0:source_accept(supply=3300)
   u.mem_write(measure,struct.pack('<4i2I4HB3x',4800,4800,4800,3300,0,60000,0,4,2,hz,1))
   stamp=(base+elapsed)&0xffffffff
   nxt=call('mode','effect_decide',measure,demand,stamp)
   if nxt:demand=nxt;call('mode','effect_verified',nxt,stamp)
  assert demand<4500
  return demand
 assert source_replay(1000)==source_replay(5000)==source_replay(5000,0xffff5000)
 # Fast power samples must not turn one cached Hz value into a growing history.
 call('drift','tele_init');call('mode','effect_begin',6000,5500,0);call('mode','effect_capture',4500,0)
 source_accept(hz=50)
 for stamp in range(0,120001,5000):
  if stamp:call('drift','tele_tick',5000)
  source_accept(supply=3300)
  u.mem_write(measure,struct.pack('<4i2I4HB3x',5840,5840,5840,3300,0,60000,0,4,2,50,1))
  assert call('mode','effect_decide',measure,4500,stamp)==0
 # The independent actual-temperature guard still reduces demand on stale Hz.
 source_accept(supply=4000)
 u.mem_write(measure,struct.pack('<4i2I4HB3x',5840,5840,5840,4000,0,60000,0,4,2,50,1))
 # Fresh water jumps33->40C: its positive trend may lower the ceiling further.
 assert call('mode','effect_decide',measure,4500,125000)==0
 assert call('mode','effect_decide',measure,4500,150000)==4450
 print('PASS actual ARM source histories: Drift generation/time provenance, asynchronous cadence, polling invariance, timer wrap, stale Hz hold and thermal protection')

 # Predictive thermal release in real independently linked Drift/Mode images.
 def thermal_replay(rising=False):
  call('drift','tele_init');call('mode','effect_begin',6000,5500,0)
  call('mode','effect_capture',4200,0);demand=4200;at38=None;last_down=None
  end=90000 if rising else 300000
  for stamp in range(0,end+1,5000):
   if stamp:call('drift','tele_tick',5000)
   supply=3700+stamp//500 if rising else 3800
   source_accept(hz=40,supply=supply)
   u.mem_write(measure,struct.pack('<4i2I4HB3x',4000,4000,4000,supply,0,60000,0,12,2,40,1))
   before=demand;nxt=call('mode','effect_decide',measure,demand,stamp)
   if nxt:demand=nxt;call('mode','effect_verified',nxt,stamp)
   assert demand<=5500
   if stamp and demand>before:assert demand-before<=100
   if demand<before:
    assert before-demand<=50
    if last_down is not None:assert stamp-last_down>=30000
    last_down=stamp
   if rising and supply>=3800:
    if at38 is None:at38=before
    assert demand<=at38
  return demand
 steady=thermal_replay();rising=thermal_replay(True)
 assert steady>4200 and rising<steady
 # Actual40C remains a protective boundary after the qualified rising history.
 source_accept(hz=40,supply=4000)
 u.mem_write(measure,struct.pack('<4i2I4HB3x',4000,4000,4000,4000,0,60000,0,12,2,40,1))
 assert call('mode','effect_decide',measure,rising,95000)==0
 hot=call('mode','effect_decide',measure,rising,120000)
 assert rising-50<=hot<rising and hot>=4050
 # Fresh pair metadata must not conceal an aged independently read source.
 for stale in ('water','hz','both'):
  call('drift','tele_init');call('mode','effect_begin',6000,5500,0)
  call('mode','effect_capture',3050,0);source_accept(hz=40,supply=3300)
  call('drift','tele_tick',20000)
  if stale=='water':source_accept(hz=40)
  if stale=='hz':source_accept(supply=3300)
  u.mem_write(measure,struct.pack('<4i2I4HB3x',4000,4000,4000,3300,0,60000,0,12,2,40,1))
  assert call('mode','effect_entry_demand',measure,3050,2,20000)<=3050
 print('PASS actual ARM adaptive thermal envelope: stable38C releases above42C, bounded recovery, gradual rising/hot correction with positive margin and independent stale-source entry guard')

else:
 print('SKIP private ARM helper probes: optimized image has no stable private ABI; running public controller qualification instead')
import runpy
runpy.run_path(str(Path(__file__).with_name('test_public_effect_arm.py')))['qualify_public_effect'](u,call)

# One damaged module must invalidate whole feature set while resident code still runs.
a=slots[5]['address']+128;old=bytes(u.mem_read(a,1));u.mem_write(a,bytes([old[0]^1]));assert call('bl2','modules_valid')==0
print('PASS actual ELF: all veneers, module initialization, P76 identity, native handoff gates, corrupt-slot rejection')
