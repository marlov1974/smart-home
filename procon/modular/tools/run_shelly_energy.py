#!/usr/bin/env python3
"""Install and supervise the P0080 Shelly pair-energy field trial.

The executor consumes a four-quarter plan from ``vp.energy.plan``.  This host
tool validates and publishes that plan before Script 7 is allowed to validate
or execute, and verifies the exact KVS value by reading it back.
"""
from __future__ import annotations
import argparse, json, time, urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
SOURCE=ROOT/'procon/modular/shelly/energy_pair_v1.js'
OUT=ROOT/'requirements/package-runs/P0080/evidence/shelly-energy-20261015'
HOST='http://192.168.86.85/rpc'
EXPECTED={1:(888,76,1),2:(888,76,1)}
PLAN_KEY='vp.energy.plan'
STATUS_KEY='vp.energy.status'
SCRIPT_ID=7
SERIAL_ID=100
PRODUCTION_BANNER='/* P0080 pair energy executor 1.5.1.'
PLAN_VERSION=1
QUARTER_SECONDS=900
PLAN_QUARTERS=4
MIN_QUARTER_WH=1500
MAX_QUARTER_WH=6000
DEFAULT_QUARTERS=(1500,2000,2500,4000)
RESTORE_GRACE_SECONDS=360
VALIDATION_TIMEOUT_SECONDS=75

def _strict_int(name,value):
    if type(value) is not int:
        raise ValueError(f'{name} must be an integer')
    return value

def aligned_plan_start(now=None):
    """Return the start of the current wall-clock 15-minute quarter."""
    if now is None:
        now=time.time()
    if isinstance(now,bool) or not isinstance(now,(int,float)):
        raise ValueError('current time must be numeric')
    if now<1600000000 or now>4294967295:
        raise ValueError('current time is outside the executor Unix range')
    return int(now)//QUARTER_SECONDS*QUARTER_SECONDS

def encode_plan(revision,start,quarters):
    """Encode one strict, versioned four-quarter Shelly KVS plan."""
    revision=_strict_int('revision',revision)
    start=_strict_int('start',start)
    if revision<1 or revision>2147483647:
        raise ValueError('revision must be in 1..2147483647')
    if start<1600000000 or start>4294967295 or start%QUARTER_SECONDS:
        raise ValueError('start must be a wall-clock aligned Unix quarter')
    if not isinstance(quarters,(list,tuple)) or len(quarters)!=PLAN_QUARTERS:
        raise ValueError('exactly four quarter targets are required')
    values=[]
    for index,value in enumerate(quarters):
        value=_strict_int(f'q{index}',value)
        if value<MIN_QUARTER_WH or value>MAX_QUARTER_WH:
            raise ValueError(
                f'q{index} must be in {MIN_QUARTER_WH}..{MAX_QUARTER_WH} Wh'
            )
        values.append(value)
    return (
        f'v={PLAN_VERSION}|rev={revision}|start={start}'
        f'|q0={values[0]}|q1={values[1]}|q2={values[2]}|q3={values[3]}'
    )

def trial_timeout_seconds():
    """Bound the four-quarter run while leaving time for native restoration."""
    return PLAN_QUARTERS*QUARTER_SECONDS+RESTORE_GRACE_SECONDS

def stamp(): return datetime.now(timezone.utc).isoformat()
def rpc(method,params=None,retries=5):
    body=json.dumps({'id':1,'src':'p0080-energy','method':method,'params':params or {}}).encode()
    error=None
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(urllib.request.Request(HOST,data=body,headers={'Content-Type':'application/json'}),timeout=12) as r:
                answer=json.load(r)
            if 'error' in answer: raise RuntimeError(answer['error'])
            return answer.get('result',{})
        except Exception as exc:
            error=exc
            if attempt+1<retries: time.sleep(2)
    raise error
def read(sid,addr,qty):
    if qty>16:
        first=read(sid,addr,16)
        return first+read(sid,addr+16,qty-16)
    return rpc('MbRtuClient.ReadInputRegisters',{'id':100,'sid':sid,'addr':addr,'qty':qty})['values']
def identity(sid):
    values=read(sid,72,15)
    return {
        'first':72,'last':86,'values':values,
        'registers':{f'I{address}':value for address,value in zip(range(72,87),values)},
    }
def model_diagnostics(sid):
    values=read(sid,308,12)
    seed=read(sid,346,1)
    return {
        'first':308,'last':319,'values':values,
        'registers':{
            **{f'I{address}':value for address,value in zip(range(308,320),values)},
            'I346':seed[0],
        },
        'seed_sequence_address':346,'seed_sequence':seed[0],
    }
def script_code(script_id):
    """Read the complete Shelly source; Script.GetCode replies are bounded."""
    code=''
    while True:
        part=rpc('Script.GetCode',{'id':script_id,'offset':len(code),'len':1024})
        data=part.get('data','')
        if not isinstance(data,str) or (part.get('left') and not data):
            raise RuntimeError('invalid or stalled Script.GetCode response')
        code+=data
        if not part.get('left'): return code
        if len(code)>32768: raise RuntimeError('script source exceeds bounded read')

def serial_config():
    """Read and validate the serial transport required by the production script."""
    config=rpc('Serial.GetConfig',{'id':SERIAL_ID})
    serial=config.get('serial',{})
    if config.get('mode')!='mb_client' or serial.get('baud')!=9600 or serial.get('format')!='8N1':
        raise RuntimeError(f'Serial {SERIAL_ID} is not mb_client 9600 8N1: {config!r}')
    return config

def script_snapshot(script_id=SCRIPT_ID):
    """Capture all restorable Script state before the first mutation."""
    return {
        'id':script_id,
        'code':script_code(script_id),
        'config':rpc('Script.GetConfig',{'id':script_id}),
        'status':rpc('Script.GetStatus',{'id':script_id}),
    }

def _script_config_payload(config):
    if not isinstance(config,dict):
        raise RuntimeError(f'invalid Script.GetConfig result: {config!r}')
    return {key:value for key,value in config.items() if key!='id'}

def write_evidence_once(name,value):
    """Create evidence without ever replacing an earlier field snapshot."""
    OUT.mkdir(parents=True,exist_ok=True)
    with (OUT/name).open('x') as handle:
        json.dump(value,handle,indent=2)
        handle.write('\n')

def assert_script_state(code,config,running,script_id=SCRIPT_ID):
    got_code=script_code(script_id)
    got_config=rpc('Script.GetConfig',{'id':script_id})
    got_status=rpc('Script.GetStatus',{'id':script_id})
    if got_code!=code:
        raise RuntimeError(f'Script {script_id} source readback mismatch')
    expected_config=_script_config_payload(config)
    actual_config=_script_config_payload(got_config)
    exact_config='id' in config
    config_matches=(
        actual_config==expected_config if exact_config else
        all(actual_config.get(key)==value for key,value in expected_config.items())
    )
    if not config_matches:
        raise RuntimeError(
            f'Script {script_id} config readback mismatch: '
            f'expected={expected_config!r} actual={actual_config!r}'
        )
    if bool(got_status.get('running'))!=bool(running):
        raise RuntimeError(
            f'Script {script_id} running-state mismatch: '
            f'expected={bool(running)} actual={got_status!r}'
        )
    return {'code_bytes':len(got_code),'config':got_config,'status':got_status}

def quiesce_script(script_id=SCRIPT_ID):
    """Stop and disable Script 7, then prove both conditions before mutation."""
    rpc('Script.Stop',{'id':script_id})
    rpc('Script.SetConfig',{'id':script_id,'config':{'enable':False}})
    config=rpc('Script.GetConfig',{'id':script_id})
    status=rpc('Script.GetStatus',{'id':script_id})
    if config.get('enable') is not False or status.get('running'):
        raise RuntimeError(f'Script {script_id} did not become stopped and disabled: {config!r} {status!r}')
    return {'config':config,'status':status}

def install_script_code(code,script_id=SCRIPT_ID):
    """Install exact source while leaving the slot stopped and disabled."""
    if not isinstance(code,str):
        raise ValueError('script code must be text')
    quiesce_script(script_id)
    for offset in range(0,len(code),900):
        rpc('Script.PutCode',{
            'id':script_id,'code':code[offset:offset+900],'append':offset>0,
        })
    # Empty scripts still need one replacing call.
    if not code:
        rpc('Script.PutCode',{'id':script_id,'code':'','append':False})
    expected={'enable':False}
    proof=assert_script_state(code,expected,False,script_id)
    return proof

def restore_script(snapshot):
    """Restore exact source/config and the prior running state after failure."""
    script_id=snapshot['id']
    quiesce_script(script_id)
    code=snapshot['code']
    for offset in range(0,len(code),900):
        rpc('Script.PutCode',{
            'id':script_id,'code':code[offset:offset+900],'append':offset>0,
        })
    if not code:
        rpc('Script.PutCode',{'id':script_id,'code':'','append':False})
    config=_script_config_payload(snapshot['config'])
    rpc('Script.SetConfig',{'id':script_id,'config':config})
    running=bool(snapshot['status'].get('running'))
    if running:
        rpc('Script.Start',{'id':script_id})
    else:
        rpc('Script.Stop',{'id':script_id})
    return assert_script_state(code,snapshot['config'],running,script_id)
def control(sid):
    v=read(sid,256,10)
    return dict(zip(('state','accepted','applied','rejected','error','saved','touched','mode','lease_s','acks'),v))
def native(sid):
    def le(words): return bytes(b for word in words for b in (word&255,word>>8))
    p9=le(read(sid,232,8)); p26=le(read(sid,248,8)); diag=read(sid,283,13); p28=le(diag[5:])
    return {'power':p26[3],'mode':p26[6],'flow':int.from_bytes(p9[5:7],'big'),
            'dhw':int.from_bytes(p26[8:10],'big'),'boost':p28[3],
            'operating_mode':p26[4],'diagnostic_age_s':diag[1]}
def baseline(sid):
    base=read(sid,0,16); ctl=control(sid); n=native(sid)
    if tuple((base[0],base[1],base[11]))!=EXPECTED[sid]: raise RuntimeError(f'VP{sid} identity/link gate {base}')
    if ctl['state']!=0 or ctl['saved']!=0: raise RuntimeError(f'VP{sid} has existing control session {ctl}')
    if n['power']!=1 or n['mode']!=2 or n['boost']!=0 or n['diagnostic_age_s']>20:
        raise RuntimeError(f'VP{sid} not in fresh ordinary curve operation {n}')
    return {
        'base':base,'identity':identity(sid),'control':ctl,'native':n,
        'model':model_diagnostics(sid),'feedback':read(sid,320,32),
    }
def event(kind,data):
    OUT.mkdir(parents=True,exist_ok=True)
    with (OUT/'events.jsonl').open('a') as f: f.write(json.dumps({'time':stamp(),'kind':kind,'data':data})+'\n')
def kvs_snapshot(key):
    """Read a KVS value without mistaking transport failures for absence."""
    try:
        result=rpc('KVS.Get',{'key':key})
    except Exception as exc:
        if 'not found' not in str(exc).lower():
            raise
        return {'present':False}
    if 'value' not in result:
        raise RuntimeError(f'KVS.Get returned no value for {key}: {result}')
    return {'present':True,'value':result['value']}
def set_plan(plan):
    """Publish and byte-for-byte verify one already encoded plan."""
    if not isinstance(plan,str):
        raise ValueError('encoded plan must be a string')
    rpc('KVS.Set',{'key':PLAN_KEY,'value':plan})
    result=rpc('KVS.Get',{'key':PLAN_KEY})
    if result.get('value')!=plan:
        raise RuntimeError(f'plan KVS readback mismatch: {result!r}')
    return result
def restore_plan(snapshot,installed_plan=None):
    if installed_plan is not None:
        current=kvs_snapshot(PLAN_KEY)
        if not current.get('present') or current.get('value')!=installed_plan:
            # L4 may have rolled the plan during the run. It owns that newer
            # value; cleanup must not replace it with the pre-trial snapshot.
            return {'restored':False,'external_value_preserved':current}
    if snapshot.get('present'):
        rpc('KVS.Set',{'key':PLAN_KEY,'value':snapshot['value']})
        result=rpc('KVS.Get',{'key':PLAN_KEY})
        if result.get('value')!=snapshot['value']:
            raise RuntimeError(f'plan KVS restoration mismatch: {result!r}')
        return {'restored':True,'state':'previous_value'}
    rpc('KVS.Delete',{'key':PLAN_KEY})
    if kvs_snapshot(PLAN_KEY).get('present'):
        raise RuntimeError('plan KVS deletion did not restore the absent state')
    return {'restored':True,'state':'absent'}

def restore_kvs(key,snapshot):
    """Restore a captured KVS key exactly, including its absent state."""
    if snapshot.get('present'):
        rpc('KVS.Set',{'key':key,'value':snapshot['value']})
        result=kvs_snapshot(key)
        if not result.get('present') or result.get('value')!=snapshot['value']:
            raise RuntimeError(f'{key} KVS restoration mismatch: {result!r}')
        return {'restored':True,'state':'previous_value'}
    if not kvs_snapshot(key).get('present'):
        return {'restored':True,'state':'already_absent'}
    rpc('KVS.Delete',{'key':key})
    result=kvs_snapshot(key)
    if result.get('present'):
        raise RuntimeError(f'{key} KVS deletion did not restore the absent state')
    return {'restored':True,'state':'absent'}

def upload(code=None):
    code=SOURCE.read_text() if code is None else code
    proof=install_script_code(code)
    event('installed',{'bytes':len(code),'source':str(SOURCE),'proof':proof})
    return proof
def validate_runtime():
    production=SOURCE.read_text()
    if not production.startswith(PRODUCTION_BANNER):
        raise RuntimeError('production source is not the reviewed 1.5.1 release')
    code=production.replace('var VALIDATEONLY = 0;','var VALIDATEONLY = 1;')
    if code==production: raise RuntimeError('validation switch missing')
    upload(code); rpc('Script.Start',{'id':SCRIPT_ID}); event('validation_started',{})
    # Script 7 retries an absent per-UID gain record for 30 seconds before its
    # no-seed path, then still has identity/diagnostic and planner RPCs to run.
    deadline=time.monotonic()+VALIDATION_TIMEOUT_SECONDS
    while time.monotonic()<deadline:
        status=rpc('Script.GetStatus',{'id':SCRIPT_ID})
        if not status.get('running'):
            value=rpc('KVS.Get',{'key':STATUS_KEY}).get('value','')
            if status.get('errors') or 'phase=validated' not in value:
                raise RuntimeError(f'runtime validation failed status={status} kvs={value}')
            devices={str(sid):baseline(sid) for sid in (1,2)}
            upload(production)
            installed=assert_script_state(production,{'enable':False},False)
            result={'status':status,'kvs':value,'devices':devices,'production':installed}
            event('validation_passed',result)
            return result
        time.sleep(.5)
    raise RuntimeError('runtime validation did not stop')

def validate_observe(plan):
    """Transactional runtime validation and production Script 7 installation."""
    OUT.mkdir(parents=True,exist_ok=True)
    # These are captured before any mutation and written with O_EXCL semantics.
    original_script=script_snapshot()
    original_serial=serial_config()
    previous_plan=kvs_snapshot(PLAN_KEY)
    previous_status=kvs_snapshot(STATUS_KEY)
    write_evidence_once('script7-original.json',{
        'captured_at':stamp(),'script':original_script,'serial':original_serial,
        'plan_kvs':previous_plan,'status_kvs':previous_status,
    })
    succeeded=False
    primary_error=None
    cleanup_errors=[]
    try:
        quiescent=quiesce_script()
        # The ordering is intentional: this proof precedes both KVS.Set(plan)
        # and every Script.PutCode call.
        serial_config()
        event('validation_preflight',{'script7':quiescent,'serial':original_serial})
        original={str(s):baseline(s) for s in (1,2)}
        write_evidence_once('original-settings.json',original)
        set_plan(plan)
        plan_evidence={'key':PLAN_KEY,'value':plan,'readback_verified':True,
                       'previous':previous_plan}
        write_evidence_once('plan.json',plan_evidence)
        event('plan_installed',plan_evidence)
        result=validate_runtime()
        write_evidence_once('runtime-validation-result.json',result)
        succeeded=True
    except Exception as exc:
        primary_error=exc
    finally:
        # Stop VALIDATEONLY before restoring either KVS key; otherwise a late
        # callback could overwrite the restored status after a failed run.
        try:
            quiesce_script()
        except Exception as exc:
            cleanup_errors.append(f'Script 7 quiesce: {exc!r}')
        # VALIDATEONLY publishes vp.energy.status. It is evidence, not durable
        # application state, so restore the exact previous value/absence.
        try:
            event('plan_restored',restore_plan(previous_plan,plan))
        except Exception as exc:
            cleanup_errors.append(f'plan restore: {exc!r}')
        try:
            event('status_restored',restore_kvs(STATUS_KEY,previous_status))
        except Exception as exc:
            cleanup_errors.append(f'status restore: {exc!r}')
        if succeeded and not cleanup_errors:
            try:
                production=SOURCE.read_text()
                assert_script_state(production,{'enable':False},False)
            except Exception as exc:
                cleanup_errors.append(f'production install verification: {exc!r}')
        try:
            after_serial=serial_config()
            if after_serial!=original_serial:
                raise RuntimeError(
                    f'serial config changed: before={original_serial!r} after={after_serial!r}'
                )
            event('serial_invariant',{'before':original_serial,'after':after_serial})
        except Exception as exc:
            cleanup_errors.append(f'serial invariant: {exc!r}')
        if not succeeded or cleanup_errors:
            try:
                proof=restore_script(original_script)
                event('script7_restored_after_failure',proof)
            except Exception as exc:
                cleanup_errors.append(f'Script 7 rollback: {exc!r}')
            try:
                after_rollback_serial=serial_config()
                if after_rollback_serial!=original_serial:
                    raise RuntimeError(
                        f'serial config changed after rollback: '
                        f'before={original_serial!r} after={after_rollback_serial!r}'
                    )
            except Exception as exc:
                cleanup_errors.append(f'post-rollback serial invariant: {exc!r}')
    if primary_error or cleanup_errors:
        details=[]
        if primary_error: details.append(f'validation: {primary_error!r}')
        details.extend(cleanup_errors)
        raise RuntimeError('; '.join(details)) from primary_error
    return result
def restore_host(sid):
    c=control(sid)
    if c['state']==0 and not c['saved']: return c
    if c['saved'] and c['state'] in (4,6):
        seq=1 if c['accepted']==65535 else c['accepted']+1
        rpc('MbRtuClient.WriteHoldingRegisters',{'id':100,'sid':sid,'addr':300,'values':[0xc072,seq,1,0,0,0,0,2]})
    end=time.monotonic()+240
    while time.monotonic()<end:
        c=control(sid)
        if c['state']==0 and not c['saved']: return c
        time.sleep(2)
    raise RuntimeError(f'VP{sid} restoration timeout {c}')
def observe(execute,validate,plan):
    if validate:
        return validate_observe(plan)
    OUT.mkdir(parents=True,exist_ok=True)
    original={str(s):baseline(s) for s in (1,2)}
    (OUT/'original-settings.json').write_text(json.dumps(original,indent=2))
    previous_plan=kvs_snapshot(PLAN_KEY)
    try:
        set_plan(plan)
        plan_evidence={'key':PLAN_KEY,'value':plan,'readback_verified':True,
                       'previous':previous_plan}
        (OUT/'plan.json').write_text(json.dumps(plan_evidence,indent=2))
        event('plan_installed',plan_evidence)
        upload()
        if not execute: return
        rpc('Script.Start',{'id':7}); event('started',{'plan':plan})
        deadline=time.monotonic()+trial_timeout_seconds()
        while time.monotonic()<deadline:
            ss=rpc('Script.GetStatus',{'id':7})
            row={'script':ss,'kvs':None,'devices':{}}
            try: row['kvs']=rpc('KVS.Get',{'key':'vp.energy.status'}).get('value')
            except Exception: pass
            for sid in (1,2):
                try:
                    row['devices'][str(sid)]={
                        'base':read(sid,0,16),'identity':identity(sid),
                        'control':control(sid),'native':native(sid),
                        'model':model_diagnostics(sid),'feedback':read(sid,320,32),
                    }
                except Exception as exc: row['devices'][str(sid)]={'error':repr(exc)}
            event('sample',row); print(stamp(),row['kvs'],flush=True)
            if not ss.get('running'):
                if row['kvs'] and 'phase=complete' in row['kvs']: break
                raise RuntimeError(f'Script stopped before completion: {ss}')
            time.sleep(30)
        else: raise RuntimeError('Trial deadline expired')
    finally:
        restored={}
        if execute:
            for sid in (1,2):
                try:
                    c=restore_host(sid); n=native(sid); before=original[str(sid)]['native']
                    if any(n[k]!=before[k] for k in ('power','mode','dhw','boost')):
                        raise RuntimeError(f'VP{sid} native restoration mismatch before={before} after={n}')
                    restored[str(sid)]={
                        'control':c,'native':n,'identity':identity(sid),
                        'model':model_diagnostics(sid),'verified':True,
                    }
                except Exception as exc: restored[str(sid)]={'error':repr(exc)}
            (OUT/'restoration.json').write_text(json.dumps(restored,indent=2)); event('restoration',restored)
        try:
            rpc('Script.Stop',{'id':7}); rpc('Script.SetConfig',{'id':7,'config':{'enable':False}})
        except Exception as exc:
            event('script_cleanup_error',{'error':repr(exc)})
        plan_restore_error=None
        try:
            outcome=restore_plan(previous_plan,plan); event('plan_restored',outcome)
        except Exception as exc:
            plan_restore_error=exc; event('plan_restoration_error',{'error':repr(exc)})
        if any('error' in x for x in restored.values()):
            raise RuntimeError(f'Restoration failed {restored}')
        if plan_restore_error:
            raise RuntimeError(f'Plan KVS restoration failed: {plan_restore_error!r}')

def main():
    global OUT
    p=argparse.ArgumentParser();p.add_argument('--execute',action='store_true')
    p.add_argument('--validate-runtime',action='store_true')
    p.add_argument('--quarter-wh',nargs=PLAN_QUARTERS,type=int,default=DEFAULT_QUARTERS,
                   metavar=('Q0','Q1','Q2','Q3'),
                   help='four quarter targets in Wh (default: 1500 2000 2500 4000)')
    p.add_argument('--plan-revision',type=int,
                   help='positive plan revision (default: current Unix second)')
    p.add_argument('--plan-start',type=int,
                   help='wall-clock aligned Unix start (default: current quarter)')
    p.add_argument('--evidence-name',default='shelly-energy-20261015');a=p.parse_args()
    if '/' in a.evidence_name or a.evidence_name in ('','.','..'):
        raise ValueError('evidence name must be one directory component')
    OUT=ROOT/'requirements/package-runs/P0080/evidence'/a.evidence_name
    plan=encode_plan(
        a.plan_revision if a.plan_revision is not None else int(time.time()),
        a.plan_start if a.plan_start is not None else aligned_plan_start(),
        a.quarter_wh,
    )
    observe(a.execute,a.validate_runtime,plan)
if __name__=='__main__': main()
