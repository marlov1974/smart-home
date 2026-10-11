"""P0080 independent fixed-slot build. No device access."""
import argparse,subprocess,json,struct,binascii,hashlib,re
from pathlib import Path
ROOT=Path(__file__).resolve().parent
# Export order is ABI. Append only; changed RAM/layout requires a new ABI/layout.
SLOTS=[('bl2',8,4096,['platform_init','uart_init','uart_receive','uart_send','micros','watchdog_refresh','heartbeat','cn_uart_init','cn_uart_receive','cn_uart_ready','cn_uart_write','platform_uid_word','platform_dip_read','identity_init_dip','modbus_address','identity_read','cn_service']),
 ('common',12,2048,['cn_init','cn_feed','cn_tick','cn_tx_byte','cn_tx_sent','cn_read','cn_command','maintenance_ready']),
 ('dispatcher',4,256,['modbus_reply']),
 ('mode',12,4096,['ctl_feedback','ctl_link_lost','ctl_init','ctl_observe','ctl_submit','ctl_tick','ctl_busy','ctl_next','ctl_reply','ctl_timeout','ctl_read','effect_feedback_init','effect_feedback_tick','effect_feedback_get','effect_feedback_hard_invalid']),
 ('drift',4,2048,['tele_snapshot','tele_init','tele_tick','tele_invalidate','tele_accept','tele_read']),
 ('service',4,1024,['svc_init','svc_start_cycle','svc_link','svc_tick','svc_due','svc_sent','svc_reply','svc_timeout','svc_bad_frame','svc_read']),
 ('debug_command',4,256,['debug_command']),('debug_telemetry',4,256,['feedback_read'])]
FILES={'bl2':['platform','identity','bl2','ota','flash'],'common':['cn105'],'dispatcher':['modbus'],'mode':['control','effect','effect_feedback'],'drift':['telemetry'],'service':['service'],'debug_command':['debug_command'],'debug_telemetry':['debug_telemetry']}
def run(args):subprocess.run([str(x) for x in args],cwd=ROOT,check=True)
def crc(b):return binascii.crc32(b)&0xffffffff
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--toolchain',default='/tmp/procon-export/.local/toolchain');ap.add_argument('--out',default='build');ap.add_argument('--revision',type=int,default=1);ap.add_argument('--change-slot',default='');ap.add_argument('--probe-slot',default='');a=ap.parse_args()
 out=ROOT/a.out;out.mkdir(parents=True,exist_ok=True);cross=Path(a.toolchain)/'bin/arm-none-eabi-'
 addr=0x08008000;ram=0x20000000;slots=[];symbols={}
 for i,(name,kb,rsize,exports) in enumerate(SLOTS):
  v={'id':i,'name':name,'address':addr,'size':kb*1024,'ram':ram,'ram_size':rsize,'exports':exports};slots.append(v)
  for j,fn in enumerate(exports):symbols[fn]=addr+(512 if i==0 else 64)+j*4+1
  addr+=kb*1024;ram+=rsize
 assert ram<=0x20003800 # leave at least2K stack
 manifest=addr;layout=crc(json.dumps(slots,sort_keys=True).encode())
 (out/'layout.h').write_text('#ifndef LAYOUT_H\n#define LAYOUT_H\n#define LAYOUT_ID %du\n#define MANIFEST_ADDR 0x%xu\n#define UPDATE_BASE 0x%xu\n#define UPDATE_END 0x%xu\n#define ABI_VERSION 1u\n#define SLOT_COUNT 7u\nstatic const unsigned slot_addr[7]={%s};\nstatic const unsigned slot_size[7]={%s};\nstatic const unsigned slot_ram[7]={%s};\nstatic const unsigned slot_ramsize[7]={%s};\nstatic const unsigned slot_exports[7]={%s};\n#endif\n'%(layout,manifest,slots[1]['address'],manifest+2048,','.join(hex(s['address']) for s in slots[1:]),','.join(str(s['size']) for s in slots[1:]),','.join(hex(s['ram']) for s in slots[1:]),','.join(str(s['ram_size']) for s in slots[1:]),','.join(str(len(s['exports'])) for s in slots[1:])))
 full=bytearray(b'\xff'*98304);results=[]
 for s in slots:
  name=s['name'];base=s['address'];ident=s['id'];rev=a.revision if name in a.change_slot.split(",") else 1
  asm='.syntax unified\n.cpu cortex-m4\n.thumb\n.section .header,"a"\n'
  if ident:asm+='.word 0x50384348,%d,1,%d,0x%x,%d, _data_load,_data_start,_data_size,_bss_start,_bss_size,%d,%d,0,0,0\n'%(ident,layout,base,s['size'],len(s['exports']),rev)
  asm+='.section .exports,"ax"\n'
  for fn in s['exports']:asm+='b.w '+fn+'\n'
  if name==a.probe_slot:asm+='.section .layout_probe,"ax"\n.space 32,0\n'
  (out/(name+'.S')).write_text(asm)
  ld='MEMORY { FLASH(rx): ORIGIN=0x%x,LENGTH=%d\n RAM(rwx): ORIGIN=0x%x,LENGTH=%d }\n'%(base,s['size'],s['ram'],s['ram_size'])
  ld+='SECTIONS {\n'
  if not ident:ld+='.isr_vector : { KEEP(*(.isr_vector)) } > FLASH\n. = ORIGIN(FLASH)+512;\n'
  else:ld+='.header : { KEEP(*(.header)) } > FLASH\n'
  ld+='.exports '+hex(base+(512 if ident==0 else 64))+' : { KEEP(*(.exports)) } > FLASH\n.text : { KEEP(*(.layout_probe)) *(.text*) *(.rodata*) . = ALIGN(8); } > FLASH\n.data : { _data_start = .; _ramfunc_start = .; *(.ramfunc*) _ramfunc_end = .; *(.data*) . = ALIGN(8); _data_end = .; } > RAM AT> FLASH\n_data_load = LOADADDR(.data);\n.bss (NOLOAD) : { _bss_start = .; *(.bss*) *(COMMON) . = ALIGN(8); _bss_end = .; } > RAM\n/DISCARD/ : { *(.comment*) *(.note*) *(.ARM.exidx*) }\n_data_size = _data_end - _data_start; _bss_size = _bss_end - _bss_start;\n_stack_top = 0x20004000;\nASSERT(_bss_end <= ORIGIN(RAM)+LENGTH(RAM),"RAM slot overflow")\n}\n'
  # GNU ld MEMORY syntax requires whitespace around assignments.
  ld=ld.replace('ORIGIN=','ORIGIN = ').replace('LENGTH=','LENGTH = ')
  for fn,value in symbols.items():
   if fn not in s['exports']:ld+='PROVIDE(%s = 0x%x);\n'%(fn,value)
  (out/(name+'.ld')).write_text(ld)
  src=[ROOT/'firmware/src'/ (f+'.c') for f in FILES[name]]+[ROOT/'firmware/src/runtime.c',out/(name+'.S')]
  if not ident:src+=[ROOT/'firmware/startup/startup.S']
  # P0080: keep mode within its fixed12KiB slot; other module flags stay unchanged.
  run([str(cross)+'gcc','-mcpu=cortex-m4','-mthumb','-mfloat-abi=soft','-std=c11','-Os',*(['-fno-inline-functions-called-once'] if name=='mode' else []),'-g3','-Wall','-Wextra','-Werror','-ffreestanding','-fno-builtin','-ffunction-sections','-fdata-sections','-fno-unwind-tables','-fno-asynchronous-unwind-tables','-ffile-prefix-map='+str(ROOT)+'=.','-Ifirmware/include','-I'+str(out),*src,'-nostdlib','-Wl,--gc-sections,--build-id=none,-Map,'+str(out/(name+'.map')),'-T'+str(out/(name+'.ld')),'-lgcc','-o',out/(name+'.elf')])
  run([str(cross)+'objcopy','-O','binary',out/(name+'.elf'),out/(name+'.raw.bin')])
  raw=(out/(name+'.raw.bin')).read_bytes();assert len(raw)<=s['size'];data=raw+b'\xff'*(s['size']-len(raw));(out/(name+'.bin')).write_bytes(data)
  full[base-0x08008000:base-0x08008000+s['size']]=data
  section_sizes=subprocess.check_output([str(cross)+'size','-A',str(out/(name+'.elf'))],text=True)
  ram_used=sum(int(line.split()[1]) for line in section_sizes.splitlines() if line.split() and line.split()[0] in ('.data','.bss'))
  results.append({**s,'ram_used':ram_used,'used':len(raw),'free':s['size']-len(raw),'crc32':crc(data),'sha256':hashlib.sha256(data).hexdigest()})
 vals=[0x50384d46,1,layout,1]+[r['crc32'] for r in results[1:]]+[0,0,0]
 prefix=struct.pack('<14I',*vals);m=prefix+struct.pack('<II',crc(prefix),0x434f4d54)
 full[manifest-0x08008000:manifest-0x08008000+64]=m
 (out/'manifest.bin').write_bytes(m);(out/'install.bin').write_bytes(full)
 (out/'install.json').write_text(json.dumps({'package':'P0080','status':'offline-verified-candidate','base':hex(0x08008000),'end_exclusive':hex(0x08020000),'raw_bytes':manifest-0x08008000+64,'padded_bytes':98304,'initial_sp':hex(struct.unpack_from('<I',full)[0]),'reset_vector':hex(struct.unpack_from('<I',full,4)[0]),'sha256':hashlib.sha256(full).hexdigest()},indent=2)+'\n')
 (out/'sizes.json').write_text(json.dumps({'ota_protocol':2,'layout':layout,'manifest_address':manifest,'slots':results,'ram_reserved':ram-0x20000000,'stack_reserved':0x20004000-ram},indent=2)+'\n')
 for s in results:print(s['name'],s['used'],'/',s['size'])
if __name__=='__main__':main()
