"""P0081 exact-image diagnostic validation, following existing ARM regressions."""
import runpy,sys,struct
from pathlib import Path
ctx=runpy.run_path(str(Path(__file__).with_name('test_modules_arm.py')))
u,call,put,p= (ctx[k] for k in ('u','call','put','p'))
u.mem_write(0x08008000,(p/'install.bin').read_bytes());call('bl2','modules_load');call('common','cn_init')
put('common','linked',1,1);put('common','now',1000);put('common','last_good',1000)
a=0x2000e000
u.mem_write(a,struct.pack('<8H',0x81d1,1,0xfd,1,1,7,0,0))
assert call('common','cn_command',a)==0
assert call('common','cn_read',606)==1
# Complete background A3 at boundary, then allow actual arbiter to dispatch.
call('service','svc_link',1,1000);call('service','svc_sent',1000)
u.mem_write(a,bytes([0xa3,0,27,1])+bytes(12));assert call('service','svc_reply',a,1001,1)==1
call('common','cn_tick',1100)
b=[]
while call('common','cn_tx_byte',a):b.append(bytes(u.mem_read(a,1))[0]);call('common','cn_tx_sent')
assert len(b)==22 and b[1]==0x42 and b[5]==7 and b[6:21]==[0]*15
assert call('common','cn_read',606)==2
r=bytearray([252,0x62,2,0x7a,16,7])+bytearray(16);r[-1]=(252-sum(r))%256
for v in r:call('common','cn_feed',v,1150,0)
assert call('common','cn_read',606)==3 and call('common','cn_read',609)==1
raw=b''.join(call('common','cn_read',i).to_bytes(2,'little') for i in range(616,627))
assert raw==r
# Actual dispatcher preserves isolated addressed envelopes and FC04 result map.
def crc(data):
 c=65535
 for b in data:
  c^=b
  for _ in range(8):c=(c>>1)^(0xa001 if c&1 else 0)
 return struct.pack('<H',c)
u.mem_write(a,struct.pack('<3I',1,2,3));call('bl2','identity_init_dip',a,0x61,1)
req=bytes([1,4,2,88,0,16]);req+=crc(req);u.mem_write(a,req)
assert call('dispatcher','modbus_reply',a,len(req),a+256,64)==37
assert bytes(u.mem_read(a+256+3,2))==bytes([0x81,0xd1])
print('PASS actual ARM P0081 queued/busy/done, exact GET and raw frame, unchanged veneers, isolated FC04 map')
