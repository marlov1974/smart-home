"""P0081 bounded read-only CN105 mapping via addressed Shelly Modbus RPC.
No serial reconfiguration, firmware update or heating-control operation.
"""
import argparse
import csv
from datetime import datetime, timezone
import json
from pathlib import Path
import time
from urllib.request import Request, urlopen
from commission_units import decode_identity, normalize_uid

SAFE_A3 = (0,1,2,3,4,5,9,10,12,13,14,16,17,18,19,22,25,26,27,28,48,51,52,53,54,55,70,71,90,91,100,101,102,103,104,105,106,107,108,109,110,111,112,113,115,116,117,118,119,120,121,122,125,129,130,154,156,157,158,162,163,164,165,166,175,176,177,190,191,504,505,506,507,508,509,510,511,512,513,514,515,534,535,540,550,551,552,553,554,555,556,557,558,559,560,561,562,563,564,565,567,568,569,571)
EXCLUDED = (200,340,342,343,344)
BASELINE = [(1,7),(1,0xa1),(1,0xa2),(2,27),(2,28)]
PRIORITY = (17,18,19,25,26,27,28,52,190,191,511,506,540)
STATUS = ('IDLE','QUEUED','BUSY','DONE','TIMEOUT','UNSUPPORTED','BAD_RESPONSE','ERROR')
SERVICE_CATALOG = json.loads(Path(__file__).with_name('service_codes.json').read_text())
SERVICE_METADATA = {int(k):v for k,v in SERVICE_CATALOG['codes'].items()}
if set(SERVICE_METADATA)!=set(SAFE_A3) or set(map(int,SERVICE_CATALOG['excluded']))!=set(EXCLUDED):
    raise RuntimeError('Manual catalog differs from vetted allowlist')
LABELS = {k:v['label'] for k,v in SERVICE_METADATA.items()}
class Blocked(RuntimeError): pass

def envelope(request_id, kind, code):
    if not 1<=request_id<=65535 or kind not in (1,2) or not 0<=code<=(255 if kind==1 else 65535):
        raise ValueError('Invalid diagnostic request')
    if kind==2 and code not in SAFE_A3: raise ValueError('Service not on vetted read-only allowlist')
    return [0x81d1,1,0xfd,request_id,kind,code,0,0]

def plan(scope='baseline', passes=2):
    codes=BASELINE if scope=='baseline' else ([(1,c) for c in range(256)] if scope=='direct' else [(2,c) for c in PRIORITY+tuple(c for c in SAFE_A3 if c not in PRIORITY)])
    return [(p,k,c) for p in range(passes) for k,c in codes]

def decode(words):
    if len(words)!=32 or words[:3]!=[0x81d1,1,0xfc] or words[10]!=words[27]: raise Blocked('Incoherent/unsupported diagnostic snapshot')
    if words[6]>=len(STATUS) or words[7]>22: raise Blocked('Invalid diagnostic schema')
    raw=b''.join(w.to_bytes(2,'little') for w in words[16:27])[:words[7]]
    checksum=bool(len(raw)>=6 and raw[0]==252 and raw[2:4]==bytes([2,0x7a]) and len(raw)==raw[4]+6 and sum(raw)%256==252)
    valid=bool(words[9])
    if valid and (words[6]!=3 or not checksum): raise Blocked('Invalid DONE/checksum')
    return dict(request_id=words[3],kind=words[4],code=words[5],status=STATUS[words[6]],valid=valid,generation=words[10],age_s=words[11],attempts=words[12],bad_frame_seen=words[13],error=words[8],raw_rx=raw.hex(),response_length=len(raw),payload_length=words[14],checksum_valid=checksum)

class Shelly:
    def __init__(self,host,sid,component=100): self.host,self.sid,self.component=host,sid,component
    def rpc(self,method,params):
        req=Request('http://'+self.host+'/rpc',json.dumps(dict(id=1,method=method,params=params)).encode(),{'Content-Type':'application/json'})
        with urlopen(req,timeout=8) as r: value=json.load(r)
        if 'error' in value: raise Blocked(str(value['error']))
        return value.get('result',value)
    def read(self,address,count):
        r=self.rpc('MbRtuClient.ReadInputRegisters',dict(id=self.component,sid=self.sid,addr=address,qty=count))
        v=r.get('values')
        if not isinstance(v,list) or len(v)!=count or any(type(x)!=int or not 0<=x<=65535 for x in v):raise Blocked('Bad Modbus reply')
        return v
    def submit(self,words):
        # This is the ONLY write operation. No generic register/payload argument.
        envelope(words[3],words[4],words[5])
        if words!=envelope(words[3],words[4],words[5]):raise ValueError('Invalid envelope')
        return self.rpc('MbRtuClient.WriteHoldingRegisters',dict(id=self.component,sid=self.sid,addr=600,values=words))
    def snapshot(self):
        for _ in range(3):
            a=self.read(600,16); b=self.read(616,16); z=self.read(610,1)[0]
            if a[10]==b[11]==z:return decode(a+b)
        raise Blocked('Snapshot changed during read')
    def preflight(self,uid,scheduler_paused):
        if not scheduler_paused:raise Blocked('External weekly scheduling pause not confirmed')
        conf=self.rpc('Serial.GetConfig',dict(id=self.component))
        if conf.get('mode') not in ('mb_client',):raise Blocked('Shelly not in native Modbus client mode; operator activation required')
        jobs=self.rpc('Schedule.List',{}).get('jobs',[])
        if any(j.get('enable') for j in jobs):raise Blocked('Active Shelly schedule')
        scripts=self.rpc('Script.List',{}).get('scripts',[])
        if any(s.get('running') for s in scripts):raise Blocked('Running Shelly script may conflict')
        ident=decode_identity(self.read(72,12),self.sid)
        if ident['uid96']!=normalize_uid(uid):raise Blocked('Wrong Procon UID')
        self.health(); self.snapshot()
        self.identity=ident
        return ident
    def health(self):
        base=self.read(0,16); control=self.read(256,16)
        if base[0]!=888 or base[11]!=1 or base[3]!=1 or base[4]>30:raise Blocked('CN105 link/telemetry degraded')
        if control[0] or control[4] or control[5]:raise Blocked('Control mission/error/saved state active')
        pump=self.read(240,8)
        pump_power=pump[1]>>8
        if pump_power in (74,75,76,84,85,86,89,90,91):raise Blocked('Primary pump warning/error candidate')
        if hasattr(self,'last_health') and (base[7]!=self.last_health[7] or base[12]!=self.last_health[12]):raise Blocked('CN105 errors increased')
        self.last_health=base
        return dict(base=base,control=control,pump_raw=pump)

def report(rows,out):
    fields=['pass','kind','code','request_id','status','valid','latency_s','attempts','error','raw_rx','checksum_valid','hypothesis','manual_display_unit','historical','wire_scale','provenance']
    with (out/'summary.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');w.writeheader();w.writerows(rows)
    groups={}
    for r in rows:groups.setdefault((r['kind'],r['code']),[]).append(r)
    lines=['# P0081 command map','','Hardware observations only; a response is not proof of interpretation. No reply means UNKNOWN/NO_RESPONSE. Service labels are manual candidates.','','|Kind/code|Samples|Outcomes|Unique raw replies|Interpretation|','|---|---:|---|---|---|']
    for (k,c),rr in sorted(groups.items()):
        outcomes=','.join(sorted(set(r['status'] for r in rr)));raws=sorted(set(r['raw_rx'] for r in rr if r['raw_rx']))
        lines.append(f'|{k}/{c}|{len(rr)}|{outcomes}|'+ '<br>'.join(raws)+f'|{LABELS.get(c,"unknown") if k==2 else "unknown bytes"}; unconfirmed|')
    (out/'command-map.md').write_text('\n'.join(lines)+'\n')

def scan(client,items,out,max_runtime=1800,delay=2,timeout=32,stop=None,clock=time.monotonic,sleep=time.sleep):
    out.mkdir(parents=True,exist_ok=True);path=out/'readings.jsonl'
    rows=[json.loads(x) for x in path.read_text().splitlines()] if path.exists() else []
    completed={(r['pass'],r['kind'],r['code']) for r in rows}
    start=clock(); deadline=start+max_runtime
    if rows and 'elapsed_s' in rows[-1]:deadline-=rows[-1]['elapsed_s']
    for p,k,c in items:
        if (p,k,c) in completed:continue
        if clock()>=deadline or (stop and stop.exists()):break
        health=client.health();snap=client.snapshot();rid=(snap['request_id']%65535)+1
        if snap['status'] in ('QUEUED','BUSY'):raise Blocked('Pending request from another run; wait for expiry')
        words=envelope(rid,k,c);began=clock();stamp=datetime.now(timezone.utc).isoformat()
        with (out/'requests.jsonl').open('a') as f:
            f.write(json.dumps({'timestamp':stamp,'pass':p,'request_id':rid,'kind':k,'code':c,'raw_tx_intent':words,'previous_result':snap})+'\n')
        client.submit(words)
        while True:
            snap=client.snapshot()
            if (snap['request_id'],snap['kind'],snap['code'])!=(rid,k,c):raise Blocked('Request/result mismatch')
            if snap['status'] not in ('QUEUED','BUSY','IDLE'):break
            if clock()-began>timeout:raise Blocked('Host timeout; firmware expires within30s, no further submit')
            if clock()>=deadline or (stop and stop.exists()):raise Blocked('Stopped; pending firmware request expires within30s')
            sleep(1)
        try:after=client.health();health_error=None
        except Exception as e:after={'error':str(e)};health_error=e
        snap.update({'device_identity':getattr(client,'identity',None),'elapsed_s':round(max_runtime-(deadline-clock()),3),'pass':p,'timestamp':stamp,'latency_s':round(clock()-began,3),'raw_tx_intent':words,'health_before':health,'health_after':after,'hypothesis':LABELS.get(c,'unknown') if k==2 else 'unknown bytes','provenance':'OCH722A pp30-32 candidate, physical CN105 reply' if k==2 else 'physical direct GET reply'})
        if k==2:
            snap.update(SERVICE_METADATA[c])
            snap['provenance']=f"OCH722A p{SERVICE_METADATA[c]['manual_page']} display metadata; CN105 scale unverified"
        rows.append(snap)
        with path.open('a') as f:f.write(json.dumps(snap)+'\n')
        (out/'checkpoint.json').write_text(json.dumps({'completed':len(rows),'last_request_id':rid}))
        report(rows,out)
        if health_error:raise health_error
        if snap['status'] in ('BAD_RESPONSE','ERROR'):raise Blocked('Protocol/transport quality degraded; scan stopped')
        sleep(delay)
    return rows

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--host');ap.add_argument('--sid',type=int,default=1);ap.add_argument('--uid');ap.add_argument('--scheduler-paused',action='store_true')
    ap.add_argument('--scope',choices=['baseline','direct','a3'],default='baseline');ap.add_argument('--out',type=Path,default=Path('mapping-results'));ap.add_argument('--execute',action='store_true')
    ap.add_argument('--max-runtime',type=int,default=1800);ap.add_argument('--delay',type=float,default=2);ap.add_argument('--stop-file',type=Path,default=Path('STOP-MAPPING'))
    a=ap.parse_args();items=plan(a.scope)
    if not a.execute:print(json.dumps({'scope':a.scope,'requests':items,'excluded_a3':EXCLUDED,'runtime_cap_s':a.max_runtime,'delay_s':a.delay},indent=2));return
    if not a.host or not a.uid or a.delay<1 or not 1<=a.max_runtime<=7200:ap.error('Require host/UID, delay>=1 and runtime cap1..7200s')
    c=Shelly(a.host,a.sid);identity=c.preflight(a.uid,a.scheduler_paused)
    a.out.mkdir(parents=True,exist_ok=True)
    identity_path=a.out/'identity.json'
    if identity_path.exists() and json.loads(identity_path.read_text())!=identity:raise Blocked('Resume identity differs')
    identity_path.write_text(json.dumps(identity,indent=2))
    try:
        # Every extended run first validates the same bounded subset, independently.
        overall_start=time.monotonic()
        if a.scope!='baseline':
            baseline=scan(c,plan(),a.out/'baseline',max_runtime=min(600,a.max_runtime),delay=a.delay,stop=a.stop_file)
            if len(baseline)!=10 or any(r['status'] not in ('DONE','TIMEOUT','UNSUPPORTED') for r in baseline) or any(not r['valid'] for r in baseline if r['kind']==2):raise Blocked('Baseline incomplete, degraded or known A3 unavailable; extended discovery blocked')
        rows=scan(c,items,a.out,max_runtime=max(0,a.max_runtime-(time.monotonic()-overall_start)),delay=a.delay,stop=a.stop_file)
        print(json.dumps({'observations':len(rows),'planned':len(items),'complete':len(rows)==len(items)}))
    finally:
        # No cancel writes. One already accepted request expires within30s.
        pass
if __name__=='__main__':main()
