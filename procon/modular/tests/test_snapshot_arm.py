"""P0080 actual modular ARM, including resident routing and sequence rollover."""
import runpy,struct,sys
from pathlib import Path
ns=runpy.run_path(str(Path(__file__).with_name('test_modules_arm.py')))
u,call,put,router=[ns[x] for x in ('u','call','put','router')]
u.mem_write(ns['a'],ns['old']);put('bl2','mode',0);call('drift','tele_init')
def read(a,n):
 r=router(struct.pack('>BBHH',1,4,a,n));assert r[:3]==bytes([1,4,2*n]) and len(r)==5+2*n
 return list(struct.unpack('>'+str(n)+'H',r[3:-2]))
def accept(f,r):
 p=bytearray(16);p[0]=12;p[1:3]=struct.pack('>H',f);p[4:6]=struct.pack('>H',r)
 u.mem_write(0x2000e500,bytes(p));call('drift','tele_accept',0x2000e500)
accept(3200,3050);assert read(400,8)[:4]==[0x5380,1,0,1]
old=read(426,6);assert old[:3]==[0,3200,1]
accept(3500,3000);call('drift','tele_tick',60000) # current telemetry TTL is60s
assert read(426,6)==old
put('drift','snapshot_sequence',0xffffffff);assert read(400,8)[2:4]==[0,1]
assert read(426,6)[:3]==[0x8000,0,2]
# Read via actual compiled dispatcher, decoder and cross-slot veneers.
call('drift','tele_init');assert read(402,2)==[0,0]
print('PASS actual ARM snapshot: resident -> dispatcher -> Drift, frozen fields, stale refresh, sequence rollover, reset')

# New diagnostics traverse resident Modbus and the preserved Dispatcher/Common.
diagnostic_version=call("mode","ctl_read",308)
if diagnostic_version>=2:
 assert read(308,12)[0]==diagnostic_version and read(310,1)==[1350]
 assert read(300,8)==[call("service","svc_read",i) for i in (373,374,376,377,379,380,382,383)]
 print("PASS actual ARM two-loop diagnostic public Modbus routing")

# The Shelly energy executor consumes this exact FC04 mailbox in one 16-word
# transaction.  Seed signed values so the public word order is qualified too.
if diagnostic_version>=3:
 measurement=struct.pack('<4i2I4HB3x',1234,-2345,3456,3210,7000,22000,3,7,2,48,1)
 u.mem_write(0x2000e600,measurement);call('mode','ctl_feedback',0x2000e600)
 mailbox=read(321,16)
 assert mailbox==[call('mode','ctl_read',i) for i in range(321,337)]
 assert mailbox[4:10]==[0,1234,0xffff,0xf6d7,0,3456]
 assert mailbox[12:16]==[3,1,7,7]
 print('PASS actual ARM energy mailbox: FC04 321x16, signed power word order and age')
