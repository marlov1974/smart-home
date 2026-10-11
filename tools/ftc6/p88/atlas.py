"""Build a conservative atlas from verified tables and targeted operand exports.
No firmware listing is copied into the report; unresolved semantics stay unresolved.
"""
import argparse,csv,hashlib,json,re
from pathlib import Path
from extract import Image,extract,SHA
from source_tx import descriptors
PROFILE='FTC6 supplied 20.01'
UNKNOWN='UNKNOWN'

def record(identifier,path,name,kind='unresolved',**kw):
    row=dict(id=identifier,firmware=PROFILE,image_sha256=SHA,path=path,
      physical_port='CN105' if path=='uart2' else UNKNOWN,
      physical_confidence='protocol/P81 corroboration; no new physical test' if path=='uart2' else 'unverified',
      wire={},rx_fields=[],tx_fields=[],functional_name=name,operation_class=kind,
      accepted_predicate=UNKNOWN,gates=UNKNOWN,handler=[],source_sink=UNKNOWN,
      shared_function=UNKNOWN,forward_boundary=UNKNOWN,completion=UNKNOWN,
      response_error=UNKNOWN,cadence=UNKNOWN,persistence=UNKNOWN,side_effects=UNKNOWN,
      retry='not qualified; never infer idempotence from GET',failure_exit=UNKNOWN,
      reachability='structural only',semantic_confidence='unresolved',physical_validation='NOT RUN in P88',
      baseline='unresolved',evidence=[],next_verification='finish named dataflow and gates offline before physical work')
    row.update(kw);return row

def field(position,name,source=UNKNOWN,**kw):
    f=dict(position=position,origin='payload0 (frame byte5 for FC)',length=1,endian='byte',signed=False,
      scale=UNKNOWN,unit=UNKNOWN,range=UNKNOWN,name=name,source_sink=source)
    f.update(kw);return f

def build(image,catalog):
    inv=extract(image);rows=[]
    inv['source_tx_descriptors']=descriptors(image)
    source_names={0x9a336:('Selected target temperature','ceil(clamp(signed39EF,0,8000)/50)','0.5 C'),
      0x9a36a:('Primary return temperature','ceil(clamp(signed39F3,0,6000)/100)','1 C'),
      0x9a39e:('Selected feedback temperature','ceil(clamp(signed39F1,0,8000)/50)','0.5 C'),
      0x9a3d2:('Primary flow feedback','feature06D5.bit7; nonlinear encoding of39F5=322E','raw encoding'),
      0x997c6:('Virtual demand temperature','(clamp(signed39C7,800,3950)-800)//50 for profile10','0.5 C, offset8 C'),
      0x99846:('Secondary virtual temperature','(clamp(signed39C9,-3900,8850)+3900)//50 for profile10','0.5 C, offset-39 C')}
    for d in inv['source_tx_descriptors']:
        for i,f in enumerate(d['fields']):
            name,formula,unit=source_names.get(f['source'],('Unresolved source field',UNKNOWN,UNKNOWN)) if f['kind']=='callback' else ('Constant field' if f['kind']=='constant' else 'Staged memory field',UNKNOWN,UNKNOWN)
            rows.append(record(f"source.tx.{d['address']}.{i:02d}",'source-software',name,'forwarding',
              wire={'direction':'TX','descriptor':d['address'],'length':d['length'],'profile':16},
              tx_fields=[field(f['bit_offset']//8,name,source=f"{f['kind']}:{f['source']:x}",origin='logical source frame byte0',bit_offset=f['bit_offset']%8,bit_length=f['width'],length=(f['bit_offset']%8+f['width']+7)//8,endian='little-bit-order',scale=formula,unit=unit,range=f"masked to {f['width']} bits")],
              handler=['9c228','9c34a','9c40e'],source_sink=f"{f['kind']} {f['source']:x} →1318 →084B",
              accepted_predicate='Internal descriptor selected by9B9A8/9BC40 or helper; not an external CN105 opcode',
              gates='9D598 scheduler and personality; individual selection in source-outgoing.md',
              completion='Local staging; peer completion separate',persistence='No persistent write in packer',
              semantic_confidence='field formula proven' if formula!=UNKNOWN else 'constant proven' if f['kind']=='constant' else 'unresolved',
              baseline='newly itemized source descriptor',evidence=[f['operand'],'9C228','source-outgoing.md'],reachability='descriptor region; per-descriptor caller qualification separate'))
    for root in ['a4fe0','a53d6','c0550','c0748','c9278','c94a6']:
        p=catalog/(root+'.asm')
        if not p.is_file() or not p.read_text().strip():raise ValueError('Missing reference '+root)
    for table in inv['tables']:
        path=table['id'].split('.')[0]
        for r in table['rows']:
            callbacks=sorted(set(r['callbacks'].values()))
            rows.append(record(f"{table['id']}.{r['index']:03d}",path,
              f"{table['id']} descriptor {r['index']}",wire={'descriptor_header':r['header'],'direction':table['id'].split('.')[1]},
              handler=callbacks,evidence=[r['address'],table['bounds_evidence'],r['record_sha256']],
              disposition='default' if r['index']==0 else 'enumerated',table=table['id'],index=r['index']))
    for r in inv['cn105_routes']:
        mapped=r['disposition']=='mapped';code=int(r['opcode'],16)
        name='GET' if r['frame']=='42' else 'SET'
        session=0x50<=code<=0x7e or code==0xc8
        rows.append(record(f"uart2.{r['frame']}.{r['opcode']}",'uart2',f'{name} {r["opcode"]}',
          'setting/session' if session else ('read/status' if name=='GET' else 'live control') if mapped else 'default/rejected',
          wire=dict(frame='FC',type=r['frame'],opcode=r['opcode'],direction='RX→TX'),
          rx_fields=[field(0,'command',range=r['opcode'])],handler=[r['packer']],
          accepted_predicate='FC/02/7A; established 2342.bit0; lookup and descriptor range match' if mapped else 'No nonzero internal route in these two lookup families',
          gates='CFB18 category/session; see settings-session' if session else 'A508A and downstream role gates remain command-specific',
          reachability='mapped; downstream gates required' if mapped else 'default in bounded lookup',
          evidence=[r['rx_descriptor'] or 'no range',r['tx_descriptor'],f'lookup index {r["lookup_index"]}'],
          internal=r['internal'],disposition=r['disposition']))
    for c in inv['service_classes']:
        rows.append(record(f'service.class.{c["index"]:02d}','shared-service',f'Service class {c["class_id"]} interval {c["minimum"]}–{c["maximum"]}',
          'forwarding/classification',wire={'selector_range':[c['minimum'],c['maximum']]},
          accepted_predicate='8C04E unsigned16 upper-bound classification; not external eligibility',
          evidence=[c['address'],'8C04E'],handler=['8c04e'],class_id=c['class_id'],reachability='internal classifier',semantic_confidence='classification proven'))
    for s in inv['switches']:
        for r in s['rows']:
            alias=[x['index'] for x in s['rows'] if x['target']==r['target']]
            rows.append(record(f'{s["id"]}.{r["index"]:02d}',s['id'].split('.')[0],f'{s["id"]} branch {r["index"]}',
              handler=[r['target']],wire={'normalized_index':r['index']},aliases=alias,
              evidence=[s['branch'],s['base']],reachability='relative switch entry; upstream normalization separate'))
    # Every directly stored response byte; sources deliberately remain raw until traced.
    tx=next(t for t in inv['tables'] if t['id']=='uart2.tx')
    for t in tx['rows']:
        root=t['callbacks']['8'];p=catalog/(root+'.asm')
        if not p.exists():raise ValueError('Missing packer reference '+root)
        positions={}
        for line in p.read_text().splitlines():
            m=re.search(r'^(ram:[0-9a-f]+)\tMOV\.b (.*),0x(23[56][0-9a-f])$',line)
            if m and 0x235e<=int(m[3],16)<=0x236d:
                positions.setdefault(int(m[3],16)-0x235e,[]).append({'instruction':m[1],'operand_source':m[2]})
        for pos,proof in sorted(positions.items()):
            rows.append(record(f'uart2.tx.{t["index"]:03d}.p{pos:02d}','uart2',f'Response {t["index"]} payload byte {pos}',
              'raw field',tx_fields=[field(pos,'unresolved response byte')],handler=[root],
              evidence=proof,reachability='direct store in response packer; route gates separate'))
    # New UART6 room transport: semantic rows separate from the seven descriptors.
    for command in range(0x48,0x4d):
        internal=command-0x47
        rx=[field(0,'selector',range=hex(command-0x21))]
        if command<0x4c:
            for n in range(8):rx.append(field(n+(2 if command==0x49 else 1),f'room channel {n+1}',f'0648+2*{n}; 0820+{n}',scale='(clamp(raw,128,208)-128)*0.5',unit='C',range='FF invalid; other bytes clamp to 0..40 C'))
        action={0x48:'room reports',0x49:'room reports and target selection',0x4a:'room reports and DHW boost',0x4b:'room reports and holiday',0x4c:'receiver status masks'}[command]
        statuspos={1:(14,15),2:(16,17),3:(15,16),4:(16,17),5:(6,7)}[internal]
        # statuspos are frame indices; payload subtract5.
        rx += [field(statuspos[0]-5,'status mask','39E5'),field(statuspos[1]-5,'inverted status mask','39E6',scale='bitwise NOT8')]
        if command==0x49:rx += [field(1,'target','38DC/38E2/38EE/38F4',scale='(raw-128)*0.5',unit='C',range='128..248 else ignored'),field(10,'target mode selector','86BEA lookup'),field(14,'zone selector','86C02 lookup')]
        if command in (0x4a,0x4b):rx += [field(9,'boost' if command==0x4a else 'holiday','3919' if command==0x4a else '391B',range='86BF6 / 86BFA table')]
        rows.append(record(f'uart6.command.{command:02x}','uart6',action,'event/live control',
          wire={'frame':'FC','type':f'{command:02x}','reply_type':f'{command+0x20:02x}','header':'04 03','direction':'peer→FTC'},rx_fields=rx,
          accepted_predicate=f'FC/{command:02X}/04/03; payload0={command-0x21:02X}; sum(bytes1..end)=0; declared payload+6=length<=22',
          gates='3F28.bit0 connected; C06C4 selector; 3F26 consumed by control tasks',
          handler=[f'{x:x}' for x in [0xc0550,0xc04f2,0x8f75e]],
          source_sink='8 room channels; 39E5/39E6 status; command-specific native setters',
          shared_function='B95E0 boost / C0AD0 holiday also used by CN105',
          completion='reply is link-level status, not proof of persistence or heating effect',
          side_effects='updates reports and selected requested state',persistence='not established',
          reachability='complete descriptor→parser→consumer static chain',semantic_confidence='field dataflow proven; physical role inferred',
          baseline='newly found static command',evidence=['8966B','86C5A','C00D2','C006C','8F75E','B9930','B958C','C0A80'],
          next_verification='unpowered connector continuity then passive frame correlation under separately authorized work'))
    rows.append(record('uart6.connect','uart6','accessory connect','transient state',wire={'type':'5a','reply':'7a','payload0':'ca','header':'04 03'},
        rx_fields=[field(0,'connect marker',range='CA'),field(1,'connect value','86BFE lookup')],handler=['c065e','c0362','c099e'],
        accepted_predicate='C069A header valid; CA; C0362 not FF',gates='does not require prior connected flag',side_effects='updates 3F28.bit0',
        reachability='static parser→flag',semantic_confidence='proven link state',evidence=['C065E','C0362','86BFE'],baseline='newly found static command'))
    # UART0 filenames and operations. IDs are local transaction IDs, not one-byte wire opcodes.
    for t in next(t for t in inv['tables'] if t['id']=='uart0.tx')['rows']:
        h=t['header'];i=t['index'];fidx=h[4]
        filename=image.at(0x87620+64*fidx,64).split(b'\0')[0].decode('ascii') if fidx<17 else UNKNOWN
        name=('default' if i==0 else 'read file' if h[1]==0x52 else 'write file' if h[1]==0x57 else 'status/control')
        if i==5:filename='A:\\LOG\\YYYY\\MM\\DD\\HHMMSS.LOG'
        rows.append(record(f'uart0.transaction.{i:02d}','uart0',name+' '+filename,'bulk transfer',wire={'local_id':i,'operation_byte':h[1],'total_length':int.from_bytes(bytes(h[2:4]),'little'),'filename':filename,'direction':'FTC→peer'},
          handler=list(t['callbacks'].values()),accepted_predicate='scheduled transaction 4450; peer response matched to 4451; busy 48E6 gate',
          completion='26 hex accepted;27 mismatch/busy;28 negative response; application is separate',
          side_effects='read can import staged settings; write sends file/log; not a pure heat-control protocol',
          evidence=[t['address'],'C96E6','C94DC','C939E'],reachability='descriptor and filename selected; scheduler/full payload semantics partial',semantic_confidence='file direction/name proven',baseline='newly found static command'))
    # The local service compare chain has explicit operands, including >999.
    listing=(catalog/'8c0b4.asm').read_text().splitlines()
    branches=[]
    for k,line in enumerate(listing):
        m=re.search(r'^(ram:[0-9a-f]+)\tCMP.w #0x([0-9a-f]+),R0$',line)
        if m and int(m[1].split(':')[1],16)<0x8c4a4 and k+2<len(listing):
            jump=re.search(r'JMP.w 0x000([0-9a-f]{5})',listing[k+2])
            if jump:branches.append((int(m[2],16),jump[1],m[1]))
    for selector,target,operand in branches:
        cls=next(c['class_id'] for c in inv['service_classes'] if c['minimum']<=selector<=c['maximum'])
        kind='action' if selector in range(340,345) or selector in range(350,364) or selector==532 else 'read/status with unqualified side effects'
        effect='Unresolved beyond local handler'
        if selector in range(520,532):effect='Even queries fold pending counters, losing division remainders; odd results truncate digits (P86)'
        if selector==532:effect='Copies energy bank then clears original counters and saves date'
        if selector in range(340,345):effect='Sets manual/state flag in 3ADC..3AE0'
        if selector in range(350,364):effect='Manual output action, changes 3A76 and output request fields'
        rows.append(record(f'service.local.{selector}','shared-service',f'Local service {selector}',kind,
            wire={'selector':selector,'class':cls},handler=[target],accepted_predicate='Local equality branch; external A3 additionally requires class2 and CEDD6 eligibility',
            gates='CN105 rejects 200 and >=700; internal-only routes must not be inferred as CN105',
            side_effects=effect,reachability='local branch proven; external eligibility separate',evidence=[operand,'8C0B4'],baseline='newly found static command'))
    annotations=json.loads((Path(__file__).parent/'reviewed.json').read_text())
    index={r['id']:r for r in rows}
    for item in annotations:
        if item['id'] in index:index[item['id']].update(item)
        else:rows.append(record(item['id'],item['path'],item['functional_name'],**{k:v for k,v in item.items() if k not in ('id','path','functional_name')}))
    for r in rows:
        for key in ('rx_fields','tx_fields'):
            r[key]=[dict(field(f['position'],f['name']),**f) for f in r[key]]
    return inv,rows

def write(image,catalog,out):
    inv,rows=build(image,catalog);out.mkdir(parents=True,exist_ok=True)
    (out/'structural-inventory.json').write_text(json.dumps(inv,indent=2)+'\n')
    (out/'command-atlas.json').write_text(json.dumps({'schema_version':1,'status':'PARTIAL','rows':rows},indent=2)+'\n')
    with (out/'command-atlas.csv').open('w',newline='') as f:
        keys=list(dict.fromkeys(k for r in rows for k in r));w=csv.DictWriter(f,fieldnames=keys,lineterminator='\n');w.writeheader()
        for r in rows:w.writerow({k:json.dumps(r.get(k),ensure_ascii=False) if isinstance(r.get(k),(dict,list)) else r.get(k) for k in keys})
    lines=['# P0088 itemized structural and field ledger','','Every machine row is represented here. Raw field rows are **not semantic completion**. See function-matrix.md for reviewed actions.','','| ID | Function | Path | Handler / evidence | Confidence |','|---|---|---|---|---|']
    for r in rows:lines.append('| '+ ' | '.join([r['id'],r['functional_name'].replace('|','/'),r['path'],', '.join(r['handler']),r['semantic_confidence']])+' |')
    (out/'atlas-ledger.md').write_text('\n'.join(lines)+'\n')
    coverage={'status':'PARTIAL','structural':{'descriptor_rows':sum(t['count'] for t in inv['tables']),'source_tx_descriptors':len(inv['source_tx_descriptors']),'source_tx_fields':sum(len(d['fields']) for d in inv['source_tx_descriptors']),'lookup_slots':512,'class_intervals':26,'local_service_branches':sum(r['id'].startswith('service.local.') for r in rows),'switch_entries':sum(s['count'] for s in inv['switches']),'scope':'six bounded descriptor tables, source descriptor region, two byte lookups, one class table, five switches; not all firmware dispatches'},
      'semantic':{'named_reviewed_rows':sum(r['semantic_confidence']!='unresolved' for r in rows),'inventoried_rows':len(rows),'complete_field_denominator':None,'note':'Descriptor/classification/file names are not a full action/field denominator; nested handlers remain open.'},
      'physical':{'new_tests':0,'new_confirmed_connectors':0,'note':'CN105 uses historical P81 correlation; UART6/CNRF and UART0/storage are inferences'},
      'paths':{p:'PARTIAL' for p in ['uart0','uart1','uart2','uart6','d','source-software','uart5','uart7','sio3','sio4']}}
    (out/'coverage.json').write_text(json.dumps(coverage,indent=2)+'\n')
    return rows

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('image',type=Path);p.add_argument('catalog',type=Path);p.add_argument('output',type=Path);a=p.parse_args()
    write(Image(a.image.read_bytes()),a.catalog,a.output)
