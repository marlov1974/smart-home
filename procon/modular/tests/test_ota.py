"""P0080 execute real resident OTA C with a bounded flash backend."""
import ctypes,json,struct,sys,os
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from ota import *
c=ctypes.CDLL(str(Path(os.environ.get('P80_OTA_LIB','build/ota-test.dylib')).resolve()))
c.ota_handle.argtypes=[ctypes.c_void_p,ctypes.c_size_t,ctypes.c_void_p,ctypes.c_size_t];c.ota_handle.restype=ctypes.c_size_t
old=os.environ.get('P80_OTA_OLD','build');new=os.environ.get('P80_OTA_NEW','build-next')
base=(Path(old)/'install.bin').read_bytes();p=plan(old,new);fs=list(transactions(p,[1,2,3]))
def reset():c.reset_image(base);c.ota_reset()
def call(f):
 out=ctypes.create_string_buffer(64);n=c.ota_handle(f,len(f),out,64);return out.raw[:n]
def invoke(f):return decode(call(f),f[2],struct.unpack('<H',f[4:6])[0])
reset();assert c.modules_valid()
assert invoke(frame(1,0))['status']==0
bad=bytearray(fs[0]);bad[-1]^=1;assert call(bytes(bad))==b'' and c.count_erase()==0
# Wrong UID/current-image/mask fail before any erase.
for off in [16,12,8]:
 reset();b=bytearray(fs[0]);b[off]^=0x80;b[-4:]=struct.pack('<I',crc(b[:-4]));assert invoke(bytes(b))['status'] and c.count_erase()==0
reset()
for f in fs:
 r=invoke(f);assert r['status']==0,(f[2],r)
 if f[2] in (2,3,4):
  w,e=c.count_write(),c.count_erase();assert invoke(f)==r;assert (c.count_write(),c.count_erase())==(w,e)
 if f[2] in (2,3):assert not c.modules_valid()
assert c.modules_valid() and c.ota_exit_ready();total=c.count_write()+c.count_erase()
# Every physical mutation cut, including each manifest doubleword. A reset must
# never admit a mixed image. Before the first erase the unchanged old image is valid.
for cut in range(total):
 reset();c.set_cut(cut)
 for f in fs:
  if invoke(f)['status']:break
 assert c.modules_valid()==(cut==0),(cut,total)
 c.ota_reset();assert c.modules_valid()==(cut==0)
# Lost ACK exact retry survives intervening status and rejected stale sequence.
reset();invoke(fs[0]);invoke(fs[1]);w=c.count_write();invoke(frame(5,0));bad=frame(3,999,b'0'*16);assert invoke(bad)['status'];assert invoke(fs[1])['status']==0 and c.count_write()==w
# Torn input lengths and corruption cause no writes.
reset()
for f in fs[:3]:
 for n in range(len(f)):
  assert call(f[:n])==b''
assert c.count_write()==c.count_erase()==0
print('PASS actual C OTA: success, duplicate/status/conflict, bounds, UID, base hash, %d mutation cuts'%total)
Path(os.environ.get('P80_OTA_RESULT','build/ota-results.json')).write_text(json.dumps({'passed':True,'mutation_cuts':total,'physical':False},indent=2)+'\n')
# Full-set repair after an interrupted/corrupt installation, not only one chunk.
broken=bytearray(base);broken[0xD000:0xD040]=b'\xff'*64
c.reset_image(bytes(broken));c.ota_reset();assert not c.modules_valid()
repair=dict(p,mask=127,slots=list(range(7)),expected_manifest_crc=0)
for f in transactions(repair,[1,2,3]):assert invoke(f)['status']==0
assert c.modules_valid()
# A frame with a valid packet CRC but wrong image content cannot commit.
reset()
for f in fs:
 if f[2]==6:break
 if f[2]==3 and struct.unpack('<I',f[12:16])[0]==0:
  b=bytearray(f);b[16]^=1;b[-4:]=struct.pack('<I',crc(b[:-4]));f=bytes(b)
 r=invoke(f)
 if f[2]==4:assert r['status']==6 and not c.modules_valid()
 else:assert r['status']==0
print('PASS actual C OTA: full-set repair and valid-frame/wrong-image commit rejection')
# P0080 protocol2 regression: an old wire request cannot mutate anything.
reset();legacy=bytearray(fs[0]);legacy[3]=1;legacy[-4:]=struct.pack('<I',crc(legacy[:-4]));assert call(bytes(legacy))==b'' and c.count_erase()==0
# Another internally valid manifest can have identical whole-buffer CRC yet a
# different prefix digest. Reject stale expected base before the first erase.
other=bytearray(base);start=0xd000;before=bytes(other[start:start+64]);other[start+48]^=1
other[start+56:start+60]=struct.pack('<I',crc(other[start:start+56]));after=bytes(other[start:start+64])
assert crc(before)==crc(after) and crc(before[:56])!=crc(after[:56])
c.reset_image(bytes(other));c.ota_reset();assert c.modules_valid()
assert invoke(fs[0])['status']==4 and c.count_erase()==0
print('PASS protocol2: legacy request rejected; different valid base with same whole-manifest residue rejected before erase')
