import sys,json,time,argparse
from pathlib import Path
from datetime import datetime,timezone
from urllib.request import Request,urlopen
sys.path.insert(0,'/Users/marcus/Documents/Codex/smart-home-procon/procon/tools')
from read_mvp import capture
from control_command import encode
p=argparse.ArgumentParser();p.add_argument('phase',choices=['short','expiry','long']);a=p.parse_args()
out=Path('procon-live')/('p72-r2-'+a.phase+'-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'.jsonl')
f=out.open('x')
def log(kind,data):
 r={'timestamp':datetime.now(timezone.utc).isoformat(),'kind':kind,'data':data};f.write(json.dumps(r)+'\n');f.flush()
def rpc(method,params):
 body={'id':1,'method':method,'params':params};log('rpc_request',body)
 try:
  with urlopen(Request('http://192.168.86.85/rpc',data=json.dumps(body).encode(),headers={'Content-Type':'application/json'}),timeout=10) as r: result=json.load(r)
 except Exception as e:log('rpc_failure',str(e));raise
 log('rpc_response',result)
 if 'error' in result:raise RuntimeError(result)
 return result['result']
def status():
 w=[]
 for addr,n in [(256,16),(272,11)]:w+=rpc('MbRtuClient.ReadInputRegisters',{'id':100,'sid':1,'addr':addr,'qty':n})['values']
 print('CONTROL',w,flush=True);return w
def snapshot():
 r=capture('192.168.86.85');log('telemetry',r);print('TELEMETRY',{k:v['value'] for k,v in r['samples'].items()},flush=True);return r
seq=None
r=snapshot();w=status()
assert r['identity'][:3]==[2,1,3] and w[0]==0 and not w[5]
assert all(r['samples'][k]['status']==1 for k in ['flow_cC','return_cC','flow_target_cC','dhw_target_cC'])
seq=1 if w[1]==65535 else w[1]+1
lease={'short':90,'expiry':45,'long':960}[a.phase]
def send(s,mode,lease=0):
 c=encode(s,mode,flow=38 if mode=='fixed-flow' else None,lease=lease);log('command',c)
 return rpc('MbRtuClient.WriteHoldingRegisters',{'id':100,'sid':1,'addr':300,'values':c['words']})
started=time.monotonic();active=None;sent=False;auto=False;failed=False;lasttele=started
try:
 sent=True;send(seq,'fixed-flow',lease)
 while time.monotonic()-started<lease+120:
  w=status();elapsed=time.monotonic()-started
  if w[4] not in [0,7]:failed=True
  if w[0]==4 and w[2]==seq and active is None:
   active=time.monotonic();log('applied',w);print('APPLIED',flush=True)
  if w[0]==4 and not auto and (a.phase=='short' or failed or (a.phase=='long' and time.monotonic()-active>=900)):
   send(1 if seq==65535 else seq+1,'auto');auto=True
  if elapsed>8 and w[0]==0:
   log('finished',{'control':w,'active_seen':active is not None,'auto':auto,'failed':failed});snapshot()
   if active is None or failed or w[11]<1:raise RuntimeError('command failed or restoration not established')
   print('PASS PHASE',a.phase,flush=True);break
  if time.monotonic()-lasttele>=15:snapshot();lasttele=time.monotonic()
  time.sleep(2)
 else:raise RuntimeError('control phase deadline exceeded')
finally:
 if sent:
  try:
   w=status()
   if w[0]==4:
    send(1 if w[1]==65535 else w[1]+1,'auto')
    for _ in range(45):
     time.sleep(2);w=status()
     if w[0]==0 and not w[5]:break
   log('final_control',w)
   print('FINAL',w,'LOG',str(out),flush=True)
  except Exception as e:log('cleanup_error',str(e));print('CLEANUP ERROR',e,flush=True)
 f.close()
