"""P0069: execute actual ELF with explicitly mocked L433 peripherals, not hardware proof."""
import struct
import sys
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_CODE, UC_HOOK_MEM_READ, UC_HOOK_MEM_WRITE
from unicorn.arm_const import UC_ARM_REG_SP, UC_ARM_REG_PC

REQUEST = bytes.fromhex('01 04 00 00 00 01 31 ca')
UART, RCC, PD = 0x40004800, 0x40021000, 0x48000c00

def crc(data):
    value = 0xffff
    for byte in data:
        value ^= byte
        for _ in range(8):
            value = (value >> 1) ^ (0xa001 if value & 1 else 0)
    return value.to_bytes(2, 'little')

def run_case(path, name, request, expected, rx_error=False, stall_tx=False, baud_gap=1042, duration=90000):
    u = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
    for address, size in [(0x08000000,0x40000),(0x20000000,0x10000),
                          (0x40000000,0x30000),(0x48000000,0x2000),(0xe000e000,0x2000)]:
        u.mem_map(address,size)
    u.mem_write(0x20000000,b'\xa5'*0x10000)
    with path.open('rb') as f:
        elf=ELFFile(f)
        for seg in elf.iter_segments():
            if seg['p_type']=='PT_LOAD' and seg['p_filesz']:
                u.mem_write(seg['p_paddr'],seg.data())
        symbols={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
    sp,reset=struct.unpack('<II',u.mem_read(0x08008000,8))
    u.reg_write(UC_ARM_REG_SP,sp)
    def write32(a,v): u.mem_write(a,struct.pack('<I',v&0xffffffff))
    def read32(a): return struct.unpack('<I',u.mem_read(a,4))[0]
    write32(RCC+8, 0x3f0f) # inherited PLL selection and bus dividers
    write32(0xe000e010,7)
    state={'time':0,'index':0,'pending':None,'de':False,'tx_done':0,'tx':bytearray(),'de_high':0,'de_low':0,'led_edges':0}
    writes=set()
    def code(uc,address,size,data):
        state['time']+=1
        assert address != (symbols['Default_Handler']&~1), 'fault handler entered'
        if state['time']>=duration: uc.emu_stop()
    def mem_read(uc,access,address,size,value,data):
        now=state['time']
        if address==RCC:
            write32(address, read32(address) | (0x400 if read32(address)&0x100 else 0))
        elif address==RCC+8:
            v=read32(address);write32(address,(v&~12)|((v&3)<<2))
        elif address==0x40000024:
            write32(address,now)
        elif address==UART+0x1c:
            idx=state['index']
            if idx<len(request) and now>=10000+idx*baud_gap and state['pending'] is None and read32(UART+4)&0x8000:
                state['pending']=request[idx];state['index']+=1
            status=0 if stall_tx else (0xc0 if now>=state['tx_done'] else 0)
            if state['pending'] is not None and read32(UART)&4:
                status|=0x20
                if rx_error and state['index']==3: status|=2
            write32(address,status)
        elif address==UART+0x24:
            write32(address,state['pending'] or 0);state['pending']=None
    def mem_write(uc,access,address,size,value,data):
        if 0x20000000<=address<0x20010000: return
        permitted=(RCC<=address<RCC+0x100 or 0x40000000<=address<0x40000040 or
                   UART<=address<UART+0x30 or 0x48000800<=address<0x48000c30 or
                   address==0x40003000 or 0xe000e000<=address<0xe000f000)
        assert permitted, f'unexpected MMIO/flash write {address:#x}'
        writes.add(address)
        if address==0x48000814:
            if (read32(address)^value)&(1<<12): state['led_edges']+=1
        if address==PD+0x18:
            if value&4: state['de']=True;state['de_high']+=1
            if value&(1<<18):
                assert state['time']>=state['tx_done'], 'DE released before final stop bit'
                state['de']=False;state['de_low']+=1
        elif address==UART+0x28:
            assert read32(UART+4)&0x8000, 'board TX/RX pin swap missing'
            assert state['de'] and not(read32(UART)&4), 'TX direction/echo suppression incorrect'
            state['tx'].append(value&255);state['tx_done']=state['time']+1042
        elif address==UART+0x18 and value&8: state['pending']=None
    u.hook_add(UC_HOOK_CODE,code)
    u.hook_add(UC_HOOK_MEM_READ,mem_read)
    u.hook_add(UC_HOOK_MEM_WRITE,mem_write)
    u.emu_start(reset,0,count=duration+10000)
    assert state['time']>=duration, f'stopped unexpectedly PC={u.reg_read(UC_ARM_REG_PC):#x}'
    assert bytes(state['tx'])==expected,(name,state['tx'].hex(),expected.hex())
    assert not state['de'] and read32(UART)&4
    assert read32(UART+12)==1667 and read32(UART)==13
    assert read32(UART+4)==0x8000, 'board requires USART3 SWAP (PC10 RX / PC11 TX)'
    assert read32(0x48000824)&0xff00==0x7700
    assert read32(0x48000800)&0xf00000==0xa00000
    assert read32(PD)&0x30==0x10
    assert read32(RCC+8)&0x3fff==5
    assert read32(RCC+0x88)&0x30==0x20
    assert read32(0xe000ed08)==0x08008000 and read32(0xe000e010)==0
    assert read32(0x40000028)==15 and read32(0x40000000)==1
    assert read32(0x48000800)&(3<<24)==1<<24
    if duration>=1100000: assert state['led_edges']>=2, 'missing PC12 heartbeat'
    assert 0x40003000 in writes
    assert read32(0x40013800)==0, 'CN105 USART1 touched'
    print(f'PASS ARM {name}: TX={bytes(state["tx"]).hex(" ") or "silent"}; PD2 released; no CN105/flash writes')

if __name__=='__main__':
    path=Path(sys.argv[1]);reply=bytes.fromhex('01 04 02 03 78');reply+=crc(reply)
    run_case(path,'read input0=888',REQUEST,reply)
    run_case(path,'bad CRC',REQUEST[:-1]+b'\x00',b'')
    request=b'\x00'+REQUEST[1:6];run_case(path,'broadcast',request+crc(request),b'')
    request=bytes.fromhex('01 06 00 00 00 01');exception=bytes.fromhex('01 86 01')
    run_case(path,'write rejected',request+crc(request),exception+crc(exception))
    run_case(path,'UART framing error',REQUEST,b'',rx_error=True)
    run_case(path,'TX timeout recovery',REQUEST,b'',stall_tx=True)

    run_case(path,'PC12 heartbeat over 1.1 seconds',REQUEST,reply,duration=1100000)
