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
# P0080 actual ARM Hz-leading startup and thermal guard.
measure=0x2000e000
u.mem_write(measure,struct.pack('<4i2I4HB3x',2000,2000,2000,3000,0,20000,0,4,2,30,1))
call('mode','effect_begin',6000,5500,0);call('mode','effect_capture',3050,0)
assert call('mode','effect_decide',measure,3050,0)==4500
call('mode','effect_verified',4500,0)
u.mem_write(measure,struct.pack('<4i2I4HB3x',5500,4500,4000,4000,0,20000,0,4,2,40,1))
assert call('mode','effect_decide',measure,4500,15000)==3800
print('PASS actual ARM Hz-leading demand:45C startup and thermal-priority reduction')
# Early demand uses one coherent pair while the real averaging window settles.
def startup_measure(supply=2900,pairs=1,age=1000):
 u.mem_write(measure,struct.pack('<4i2I4HB3x',2000,2000,2000,supply,age,0,9,pairs,2,26,0))
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
assert call('mode','effect_pause_demand',measure,4500,1000)==4200
assert call('mode','effect_pending_demand')==2
call('mode','effect_verified',4200,1001)
startup_measure(supply=3950)
assert call('mode','effect_pause_demand',measure,4200,2000)==3850
call('mode','effect_verified',3850,2001)
assert call('mode','effect_pending_demand')==0
print('PASS actual ARM early startup: first SETTLING pair, kind2/readback, repeated thermal reduction, absent/aged pair rejection')
# Cached READY plus a newer native pause must yield in the actual ARM controller.
call('mode','ctl_init')
u.mem_write(measure,struct.pack('<4i2I4HB3x',2000,2000,2000,3000,0,20000,0,4,2,30,1))
call('mode','ctl_feedback',measure)
u.mem_write(0x2000e600,struct.pack('<8H',0xc076,1,5,6000,5500,180,1,3))
assert call('mode','ctl_submit',0x2000e600,0)==0
u.mem_write(measure,struct.pack('<4i2I4HB3x',2000,2000,2000,3000,0,20000,0,4,0,30,1))
call('mode','ctl_feedback',measure);call('mode','ctl_tick',0)
assert call('mode','ctl_read',256)==1 and call('mode','ctl_read',260)==0
# An unsupported native mode still aborts before a write.
u.mem_write(measure,struct.pack('<4i2I4HB3x',2000,2000,2000,3000,0,20000,0,4,3,30,1))
call('mode','ctl_feedback',measure);call('mode','ctl_tick',1)
assert call('mode','ctl_read',256)==0 and call('mode','ctl_read',260)==8
print('PASS actual ARM cached READY/native transition: allowed pause yields; invalid native mode aborts')
# Offline atomic-entry experiment: execute the actual combined transaction.
for supply,actual,expected in [(3200,2,4500),(3800,2,4200),(3950,2,3850),(4000,2,3800),(4050,2,3750),(10000,2,3000),(3200,0,3250)]:
 call('mode','ctl_init');native={'power':1,'mode':2,'flow':3050,'dhw':5200,'actual':actual};writes=[];tm=0
 u.mem_write(measure,struct.pack('<4i2I4HB3x',2000,2000,2000,supply,0,20000,0,4,2,30,1))
 call('mode','ctl_feedback',measure)
 u.mem_write(0x2000e600,struct.pack('<8H',0xc076,1,5,6000,5500,180,1,3))
 assert call('mode','ctl_submit',0x2000e600,0)==0
 until(4)
 assert native['mode']==1 and native['flow']==expected and writes==[0x88]
 assert call('mode','ctl_read',258)==1 and call('mode','ctl_read',270)==3050
 assert submit(2,1)==0;until(0)
 assert native['mode']==2 and native['flow']==3050 and writes[-2:]==[0x80,8]
call('mode','effect_begin',6000,5500,0);call('mode','effect_capture',3050,0)
u.mem_write(measure,struct.pack('<4i2I4HB3x',-2147483648,2000,2000,3200,0,0,9,1,2,26,0))
assert call('mode','effect_entry_demand',measure,3050,2,0)==0
assert call('mode','effect_pending_demand')==0
print('PASS actual ARM atomic entry: combined45C, shared thermal caps, fresh native pause overrides old Hz, dual readback and original AUTO, partial pair rejection')
# Predictive-law regressions executed from the final linked mode image.
call('mode','effect_begin',6000,5500,0);call('mode','effect_capture',4500,0)
for stamp in range(0,120001,5000):
 power=5700+stamp//400
 u.mem_write(measure,struct.pack('<4i2I4HB3x',power-150,power,power,3300,0,60000,0,4,2,42,1))
 assert call('mode','effect_decide',measure,4500,stamp)==0
call('mode','effect_begin',6000,5500,0);call('mode','effect_capture',4500,0)
for stamp in range(0,60001,5000):
 hz=42 if stamp<30000 else 52
 u.mem_write(measure,struct.pack('<4i2I4HB3x',4800,4800,4800,3300,0,60000,0,4,2,hz,1))
 target=call('mode','effect_decide',measure,4500,stamp)
 assert target==(4400 if stamp==60000 else 0)
 if target:call('mode','effect_verified',target,stamp)
print('PASS actual ARM predictive law: flat42Hz/rising mean holds;52Hz future overshoot receives bounded100cC braking')
# Positive thermal forecast cannot lift a lower signed above-center cap.
call('mode','effect_begin',6000,5500,0);call('mode','effect_capture',4500,0)
u.mem_write(measure,struct.pack('<4i2I4HB3x',5800,5800,5800,3900,0,60000,0,4,2,50,1))
assert call('mode','effect_decide',measure,4500,0)==3900
call('mode','effect_verified',3900,0)
u.mem_write(measure,struct.pack('<4i2I4HB3x',5800,5800,5800,4000,0,60000,0,4,2,50,1))
assert 3000<call('mode','effect_decide',measure,3900,30000)<3800
# Cooling permits ordinary bounded increases, not another startup jump.
call('mode','effect_begin',6000,5500,0);call('mode','effect_capture',4500,0)
u.mem_write(measure,struct.pack('<4i2I4HB3x',3000,3000,3000,3950,0,60000,0,4,2,50,1))
assert call('mode','effect_decide',measure,4500,0)==3850
call('mode','effect_verified',3850,0);target=3850
for stamp in range(5000,120001,5000):
 u.mem_write(measure,struct.pack('<4i2I4HB3x',3000,3000,3000,3800,0,60000,0,4,2,50,1))
 next_target=call('mode','effect_decide',measure,target,stamp)
 if next_target:
  assert target<next_target<=min(target+(100 if target-3800<200 else 50),4200)
  target=next_target;call('mode','effect_verified',target,stamp)
assert target>3850
print('PASS actual ARM thermal feedback: signed steady offsets, bounded high input, forecast never raises lower cap, bounded cooling release')

# Retained response prevents new gas on the first frequency plateau.
call('mode','effect_begin',6000,5500,0);call('mode','effect_capture',4500,0)
target=4500;at60=0
for stamp in range(0,90001,5000):
 hz=32 if stamp<30000 else 42
 u.mem_write(measure,struct.pack('<4i2I4HB3x',5500,5500,5500,3300,0,60000,0,4,2,hz,1))
 nxt=call('mode','effect_decide',measure,target,stamp)
 if nxt:target=nxt;call('mode','effect_verified',target,stamp)
 if stamp==60000:at60=target
assert target<=at60
at90=target
for stamp in range(95000,300001,5000):
 nxt=call('mode','effect_decide',measure,target,stamp)
 if nxt:target=nxt;call('mode','effect_verified',target,stamp)
assert target>at90
# Weak, underpowered demand recovers1C, then still corrects during modest rise.
call('mode','effect_begin',6000,5500,0);call('mode','effect_capture',3900,0)
target=3900
for stamp in range(0,90001,5000):
 power=6000 if stamp<30000 else 4800 if stamp<=60000 else 5000
 u.mem_write(measure,struct.pack('<4i2I4HB3x',power,power,power,3800,0,60000,0,4,2,40,1))
 nxt=call('mode','effect_decide',measure,target,stamp)
 if nxt:target=nxt;call('mode','effect_verified',target,stamp)
 if stamp==60000:assert target==4000
assert target>4000
print('PASS actual ARM response memory: plateau hold, bounded decay,1C recovery and correction despite modest power rise')

# One damaged module must invalidate whole feature set while resident code still runs.
a=slots[5]['address']+128;old=bytes(u.mem_read(a,1));u.mem_write(a,bytes([old[0]^1]));assert call('bl2','modules_valid')==0
print('PASS actual ELF: all veneers, module initialization, P76 identity, native handoff gates, corrupt-slot rejection')
