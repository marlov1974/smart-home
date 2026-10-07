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

def run_case(path, name, request, expected, rx_error=False, stall_tx=False, baud_gap=1042, duration=90000, cn_hz=None, cn_corrupt=False, request_start=10000, second_request=None, extra_requests=None, service_mode="complete", inspect=None, control_model=False):
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
    cn={'tx':bytearray(),'wire':bytearray(),'schedule':[], 'next_tx':0, 'rx':0, 'svc_counts':{27:0,28:0}, 'svc_times':{27:[],28:[]}, 'normal':0, 'overlap':0, 'phase':4, 'phase_attempts':0}
    model={'power':1,'mode':2,'flow':2950,'dhw':5200,'boost':0,'sets':0}
    cn['model']=model
    request_times=[request_start+i*baud_gap for i in range(len(request))]
    if second_request:
        second_time,second_bytes=second_request
        request_times += [second_time+i*baud_gap for i in range(len(second_bytes))]
        request += second_bytes
    for start,chunk in (extra_requests or []):
        request_times += [start+i*baud_gap for i in range(len(chunk))]
        request += chunk
    def cn_packet(kind,payload):
        b=bytes([0xfc,kind,2,0x7a,len(payload)])+payload
        return b+bytes([(0xfc-sum(b))&255])

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
            if idx<len(request) and now>=request_times[idx] and state['pending'] is None and read32(UART+4)&0x8000:
                state['pending']=request[idx];state['index']+=1
            status=0 if stall_tx else (0xc0 if now>=state['tx_done'] else 0)
            if state['pending'] is not None and read32(UART)&4:
                status|=0x20
                if rx_error and state['index']==3: status|=2
            write32(address,status)
        elif address==0x4001381c:
            status=0xc0 if now>=cn['next_tx'] else 0
            if cn['schedule'] and now>=cn['schedule'][0][0]:
                assert now-cn['schedule'][0][0]<4584, 'CN105 RX overrun during Modbus TX'
                status|=0x20
            write32(address,status)
        elif address==0x40013824:
            _,b=cn['schedule'].pop(0); write32(address,b);cn['rx']+=1
            if state['de']: cn['overlap']+=1
        elif address==UART+0x24:
            write32(address,state['pending'] or 0);state['pending']=None
    def mem_write(uc,access,address,size,value,data):
        if 0x20000000<=address<0x20010000: return
        permitted=(RCC<=address<RCC+0x100 or 0x40000000<=address<0x40000040 or
                   UART<=address<UART+0x30 or 0x40013800<=address<0x40013830 or 0x48000000<=address<0x48000030 or 0x48000800<=address<0x48000c30 or
                   address==0x40003000 or 0xe000e000<=address<0xe000f000)
        assert permitted, f'unexpected MMIO/flash write {address:#x}'
        writes.add(address)
        if address==0x40013828:
            assert read32(0x40013800)==0x140d and read32(0x40013804)==0
            assert read32(0x4001380c)==6667
            if not cn['tx']: cn['frame_started']=state['time']
            cn['next_tx']=state['time']+4584
            cn['tx'].append(value&255);cn['wire'].append(value&255)
            if len(cn['tx'])>=5 and len(cn['tx'])==cn['tx'][4]+6:
                packet=bytes(cn['tx']);cn['tx'].clear()
                assert (sum(packet)&255)==0xfc
                allowed=[bytes.fromhex('fc 5a 02 7a 02 ca 01 5d')]
                fast_codes=[4,0x0c,0x14,0x0b,9,0x15,0x26]
                allowed += [cn_packet(0x42,bytes([q])+bytes(15)) for q in fast_codes]
                allowed += [cn_packet(0x42,bytes([0xa3,0,c])+bytes(13)) for c in (27,28)]
                assert packet in allowed or (control_model and ((packet[1]==0x42 and packet[5]==0x28) or packet[1]==0x41)), 'forbidden CN105 command'
                assert not cn['schedule'], 'overlapping CN105 transactions'
                if cn_hz is not None:
                    if packet[1]==0x5a: response=cn_packet(0x7a,bytes([0]))
                    elif control_model and (packet[1]==0x41 or cn.get('control',False) or (packet[5]==0x26 and cn['phase']==4 and cn.get('fast',0)==0)) and packet[5]!=4:
                        assert cn['phase']==4, 'control interleaved inside service operation'
                        cn['control']=True
                        payload=bytearray(16);payload[0]=packet[5]
                        if packet[1]==0x41:
                            q=packet[5:21];model['sets']+=1
                            if q[0]==0x34:
                                assert q[1]==1;model['boost']=q[3]
                            else:
                                assert q[0]==0x32
                                if q[1]==1:model['power']=q[3]
                                elif q[1]==8:model['mode']=q[6]
                                elif q[1]==0x20:model['dhw']=int.from_bytes(q[8:10],'big')
                                elif q[1]==0x80:
                                    assert q[6]==model['mode'] and int.from_bytes(q[8:10],'big')==model['dhw']
                                    model['flow']=int.from_bytes(q[10:12],'big')
                                else:raise AssertionError('unknown SET mask')
                            response=cn_packet(0x61,bytes([0]))
                        else:
                            if packet[5]==0x26:
                                payload[3]=model['power'];payload[6]=model['mode'];payload[8:10]=model['dhw'].to_bytes(2,'big')
                            elif packet[5]==9:payload[5:7]=model['flow'].to_bytes(2,'big')
                            elif packet[5]==0x28:payload[3]=model['boost']
                            else:raise AssertionError('unexpected control read')
                            response=cn_packet(0x62,bytes(payload))
                    elif packet[5]!=0xa3:
                        cn['control']=False
                        assert cn['phase']==4, 'FAST interleaved inside service operation'
                        f=cn.get('fast',0)
                        assert packet[5]==fast_codes[f]
                        cn['fast']=(f+1)%7
                        if f==6: cn['phase']=cn.get('next',27);cn['phase_attempts']=0
                        if packet[5]==4: cn['normal']+=1
                        payload=bytearray(16);payload[0]=packet[5]
                        if packet[5]==4: payload[1]=cn_hz
                        if packet[5]==0x0c:
                            payload[1:3]=(3500).to_bytes(2,'big');payload[4:6]=(3000).to_bytes(2,'big');payload[7:9]=(5000).to_bytes(2,'big')
                        if packet[5]==0x14: payload[12]=20
                        response=cn_packet(0x62,bytes(payload))
                        if cn_corrupt and packet[5]==4: response=response[:-1]+bytes([response[-1]^1])
                    else:
                        c=packet[7];cn['svc_counts'][c]+=1
                        assert c==cn['phase'], 'service order violated'
                        cn['phase_attempts']+=1
                        previous=cn['svc_times'][c]
                        if cn['phase_attempts']>1: assert cn['frame_started']-previous[-1]>=999000, f'retry too fast c={c} now={state["time"]} previous={previous[-1]} delta={state["time"]-previous[-1]}'
                        previous.append(cn['frame_started'])
                        status=(1 if c==27 else 2) if cn['svc_counts'][c]%2==0 else 0
                        if service_mode=='pending': status=0
                        if status or cn['phase_attempts']==10:
                            cn['next']=28 if c==27 else 27;cn['phase']=4;cn['phase_attempts']=0
                        value=7 if c==27 else 65533
                        response=cn_packet(0x62,bytes([0xa3,0,c,status,value&255,value>>8])+bytes(10))
                    begin=state['time']+20000
                    cn['schedule'] += [(begin+i*4584,b) for i,b in enumerate(response)]
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
    if expected is not None: assert bytes(state['tx'])==expected,(name,state['tx'].hex(),expected.hex())
    if inspect: inspect(bytes(state['tx']),cn)
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
    assert read32(0x40013800)==0x140d
    assert read32(0x40013804)==0 and read32(0x4001380c)==6667
    assert read32(0x48000000)&0x3c0000==0x280000
    assert read32(0x48000024)&0xff0==0x770
    assert read32(RCC+0x88)&3==2
    if cn_hz is not None: assert cn['rx']>=29, 'CN105 ACK/GET not exercised'
    print(f'PASS ARM {name}: {len(state["tx"])} Modbus bytes, CN RX={cn["rx"]}, overlap={cn["overlap"]}, GET04={cn["normal"]}, services={cn["svc_counts"]}; PD2 released; whitelist/no flash writes')

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

    request=bytes.fromhex('01 04 00 02 00 02');request+=crc(request)
    for hz,corrupt in [(48,False),(0,False),(48,True)]:
        data=bytes.fromhex('01 04 04')+(65535 if corrupt else hz).to_bytes(2,'big')+bytes([0,0 if corrupt else 1])
        run_case(path,f'concurrent CN105 {hz}Hz corrupt={corrupt}',REQUEST,reply+data+crc(data),duration=3400000,cn_hz=hz,cn_corrupt=corrupt,request_start=3130000,second_request=(3300000,request))

    def req(a,n):
        p=bytes([1,4])+a.to_bytes(2,'big')+n.to_bytes(2,'big');return p+crc(p)
    def parse_replies(data):
        blocks=[]
        while data:
            size=data[2]+5;packet=data[:size];assert packet[-2:]==crc(packet[:-2])
            blocks.append([int.from_bytes(packet[i:i+2],'big') for i in range(3,size-2,2)])
            data=data[size:]
        return blocks
    def inspect_service(data,cn):
        baseline,pending,later,completed,raw=parse_replies(data)
        assert baseline[0:2]==[888,72] and baseline[3]==1
        assert pending[10]==0
        assert later[0:2]==[888,72] and later[3]==1
        assert completed[0:3]==[7,7,1] and completed[8:11]==[65533,65533,1]
        assert raw[0:3]==[0xa3,0x011b,7] and raw[8:11]==[0xa3,0x021c,65533]
        assert later[5]>baseline[5] and later[7]==later[12]==0
        assert cn['normal']>=2 and min(cn['svc_counts'].values())>=2
    run_case(path,'A3 pending and complete in exclusive sequence with Modbus',req(0,16),None,duration=8600000,cn_hz=48,request_start=1900000,extra_requests=[(2100000,req(16,16)),(7800000,req(0,16)),(8000000,req(16,16)),(8300000,req(52,16))],inspect=inspect_service)
    def inspect_pending(data,cn):
        first,second,service,diagnostic=parse_replies(data)
        assert first[0:2]==second[0:2]==[888,72]
        assert first[3]==second[3]==1 and second[5]==first[5]
        assert service[2]==service[10]==0 and diagnostic[0] in (2,3)
        assert diagnostic[3]>=2 and diagnostic[4]>=2
        assert cn['svc_counts'][27]>=3 and cn['normal']==1
    run_case(path,'A3 repeated pending with no interleaved Hz and responsive Modbus',req(0,16),None,duration=5700000,cn_hz=20,service_mode='pending',request_start=3300000,extra_requests=[(5100000,req(0,16)),(5300000,req(16,16)),(5500000,req(32,16))],inspect=inspect_pending)

    def inspect_mvp(data,cn):
        words,states=parse_replies(data)
        vals=[int.from_bytes(words[i].to_bytes(2,'big')+words[i+1].to_bytes(2,'big'),'big',signed=True) for i in range(0,16,2)]
        assert vals==[3500,3000,500,2000,6966,48,1,-2147483648], vals
        assert states[3:10]==[1]*7 and states[10:12]==[4,4]
        assert cn['normal']==1 and cn['svc_counts'][27]>0
    run_case(path,'MVP values and validity during exclusive service',req(106,16),None,duration=3600000,cn_hz=48,request_start=3130000,extra_requests=[(3400000,req(140,16))],inspect=inspect_mvp)

    def command(seq,mode,flow=0,lease=0,flags=0):
        values=[0xc072,seq,mode,flow,0,lease,flags,2]
        b=bytes.fromhex('01 10 01 2c 00 08 10')+b''.join(v.to_bytes(2,'big') for v in values)
        return b+crc(b)
    def inspect_control(data,cn):
        # Mixed FC16 acknowledgements and FC04 diagnostics.
        responses=[]
        while data:
            n=8 if data[1]==16 else data[2]+5
            b=data[:n];assert b[-2:]==crc(b[:-2]);responses.append(b);data=data[n:]
        assert [b[1] for b in responses]==[16,4,16,4]
        applied=[int.from_bytes(responses[1][i:i+2],'big') for i in range(3,35,2)]
        restored=[int.from_bytes(responses[3][i:i+2],'big') for i in range(3,35,2)]
        assert applied[:3]==[4,1,1],applied
        assert restored[:3]==[0,2,2] and restored[11]>=1,restored
        assert cn['model']['mode']==2 and cn['model']['flow']==2950 and cn['model']['sets']==4
        assert cn['normal']>1 and cn['svc_counts'][27]>=2 and cn['svc_counts'][28]>=2
    run_case(path,'P0072 r2 FC16 FIXED38 then AUTO readback with exclusive A3',command(1,2,3800,60,1),None,duration=24000000,cn_hz=20,request_start=3000000,extra_requests=[(11000000,req(256,16)),(12000000,command(2,1)),(22500000,req(256,16))],inspect=inspect_control,control_model=True)
