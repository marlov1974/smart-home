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
accept(3500,3000);call('drift','tele_tick',40000)
assert read(426,6)==old
put('drift','snapshot_sequence',0xffffffff);assert read(400,8)[2:4]==[0,1]
assert read(426,6)[:3]==[0x8000,0,2]
# Read via actual compiled dispatcher, decoder and cross-slot veneers.
call('drift','tele_init');assert read(402,2)==[0,0]
print('PASS actual ARM snapshot: resident -> dispatcher -> Drift, frozen fields, stale refresh, sequence rollover, reset')
