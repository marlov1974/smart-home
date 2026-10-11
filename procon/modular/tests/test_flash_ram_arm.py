"""P0080 executes actual candidate ELF with mocked FLASH controller, no hardware."""
import struct,sys,json
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import *
from unicorn.arm_const import *
F=0x40022000;TEST=0x0800a000
def crc(b):
 c=65535
 for v in b:
  c^=v
  for _ in range(8):c=(c>>1)^(0xa001 if c&1 else 0)
 return struct.pack('<H',c)
def frame(seq,v):
 b=bytes.fromhex('01 10 01 90 00 04 08 f1 80')+struct.pack('>HI',seq,v)
 return b+crc(b)
class Board:
 def __init__(self,path,scenario='ok'):
  self.u=u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
  for a,n in [(0x08000000,0x40000),(0x20000000,0x10000),(0x40000000,0x30000),(0xe000e000,0x2000),(0xe0042000,0x1000),(0x1fff7000,0x1000)]:u.mem_map(a,n)
  u.mem_write(0x08000000,b'\xff'*0x40000)
  with path.open('rb') as f:
   elf=ELFFile(f)
   for seg in elf.iter_segments():
    if seg['p_type']=='PT_LOAD' and seg['p_filesz']:
     u.mem_write(seg['p_paddr'],seg.data());u.mem_write(seg['p_vaddr'],seg.data())
   self.sym={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
  self.scenario=scenario;self.cr=0xc0000000;self.sr=0;self.acr=0x600;self.keys=[];self.erases=0;self.stores=[];self.busy=0;self.t=0;self.reset=False
  self.put(0xe0042000,0x435);u.mem_write(0x1fff75e0,struct.pack('<H',128))
  self.put(0xe000ed08,0x08008000);self.put(0xe000edf0,0);self.put(F+0x20,0xaa);self.put(F+0x24,0x7fff);self.put(F+0x28,0);self.put(F+0x2c,0x7f);self.put(F+0x30,0x7f)
  if scenario=='wrp':self.put(F+0x2c,(63<<16)|63)
  if scenario=='pcrop':self.put(F+0x24,0x3f00);self.put(F+0x28,0x3fff)
  if scenario=='rdp1':self.put(F+0x20,0xfbfff8bb)
  if scenario=='rdp2':self.put(F+0x20,0xcc)
  if scenario=='debug':self.put(0xe000edf0,1)
  if scenario=='vtor':self.put(0xe000ed08,0x20000000)
  if scenario=='rdp':self.put(F+0x20,0)
  if scenario=='cpu':self.put(0xe0042000,0)
  if scenario=='density':u.mem_write(0x1fff75e0,struct.pack('<H',64))
  if scenario=='busy':self.sr=1<<16;self.busy=100000
  u.hook_add(UC_HOOK_CODE,self.code);u.hook_add(UC_HOOK_MEM_READ,self.read);u.hook_add(UC_HOOK_MEM_WRITE,self.write)
 def put(self,a,v):self.u.mem_write(a,struct.pack('<I',v))
 def code(self,u,a,n,d):
  if a==0x20003f00:u.emu_stop();return
  if self.busy:assert 0x20000000<=a<self.sym['_ramfunc_end'],f'flash execution while busy {a:x}'
 def read(self,u,access,a,n,v,d):
  if self.busy and 0x08000000<=a<0x08040000:raise AssertionError('flash data dependency while busy')
  if a==F+0x14:self.put(a,self.cr)
  if a==F:self.put(a,self.acr)
  if a==F+0x10:
   if self.busy:
    if self.scenario!='timeout':self.busy-=1
    if not self.busy:self.sr=(16 if self.scenario=='erase-error' else 8 if self.scenario=='program-error' and self.stores else 1)
   self.put(a,self.sr)
  if a==0x40000024:self.t+=10000;self.put(a,self.t)
 def write(self,u,access,a,n,v,d):
  pc=u.reg_read(UC_ARM_REG_PC)
  if 0x20000000<=a<0x20010000:return
  if a==F+8:
   assert 0x20000000<=pc<self.sym['_ramfunc_end'];self.keys.append(v)
   if len(self.keys)%2==0:
    assert self.keys[-2:]==[0x45670123,0xcdef89ab]
    if self.scenario!='unlock':self.cr&=~(1<<31)
  elif a==F+0x10:self.sr&=~v
  elif a==F:
   if v&0x1800:assert not v&0x600
   self.acr=v
  elif a==F+0x14:
   assert not self.busy
   assert not v&((1<<17)|(1<<18)|(1<<27)|4),'option/fast/mass operation'
   self.cr=v&~(1<<16)
   if v&(1<<16):
    page=(v>>3)&127
    assert 20<=page<43 and v&2 and not v&1
    assert 0x20000000<=pc<self.sym['_ramfunc_end']
    self.erases+=1
    if self.scenario!='erase-error':u.mem_write(0x08000000+page*2048,b'\xff'*2048)
    self.busy=4;self.sr=1<<16
  elif TEST<=a<0x08015800:
   assert n==4 and self.cr&1 and not self.cr&(1<<31)
   assert 0x20000000<=pc<self.sym['_ramfunc_end']
   self.stores.append((a,v))
   if len(self.stores)%2==0:
    assert a==self.stores[-2][0]+4
    self.busy=4;self.sr=1<<16
  elif a==0x40003000:assert v==0xaaaa
  elif a==0xe000ed0c:self.reset=True;u.emu_stop()
  else:raise AssertionError(f'unexpected write {a:x}')
 def invoke(self,name,*args):
  u=self.u;u.reg_write(UC_ARM_REG_SP,0x20004000);u.reg_write(UC_ARM_REG_LR,0x20003f01)
  for r,v in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],args):u.reg_write(r,v)
  u.emu_start(self.sym[name],0,count=300000)
  return u.reg_read(UC_ARM_REG_R0)

def main():
 p=Path(sys.argv[1])
 for scenario in ['ok','rdp1','rdp2','debug','vtor','cpu','density','unlock','erase-error','program-error','timeout']:
  b=Board(p,scenario)
  result=b.invoke('flash_erase',TEST)
  if scenario in ['ok','rdp1','program-error']:
   assert result==1
   data=bytes(range(232));b.u.mem_write(0x20002000,data)
   result=b.invoke('flash_write',TEST,0x20002000,len(data))
   assert result==(scenario!='program-error')
   if result:assert bytes(b.u.mem_read(TEST,232))==data
  elif scenario=='timeout':assert b.reset
  else:assert result==0
  print('PASS RAM writer',scenario)
 for a,n in [(0x08000000,8),(0x08008000,8),(0x08009ff8,8),(0x08015800,8),(TEST+1,8),(TEST,7),(TEST,248)]:
  b=Board(p);b.u.mem_write(0x20002000,b'\x55'*248);assert b.invoke('flash_write',a,0x20002000,n)==0 and not b.erases and not b.stores
 print('PASS RAM writer immutable ranges/alignment/length gates')
if __name__=='__main__':main()
