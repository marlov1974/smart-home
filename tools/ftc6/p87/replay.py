"""Read existing private capture JSONL; emit sanitized relative-time analysis only."""
import argparse
import hashlib
import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from model import evaluate, UNKNOWN

FIELDS=('flow_cC','return_cC','flow_cL_min','heat_W','compressor_Hz','flow_target_cC','operating_mode_raw')
def replay(path):
    blob=path.read_bytes(); groups=defaultdict(list); seen=set(); duplicates=0; excluded=0
    for line in blob.splitlines():
        event=json.loads(line); d=event.get('data',{}); snap=d.get('snapshot',{})
        if event.get('kind')!='capture' or not snap: continue
        s=snap.get('samples',{}); cap=d.get('snapshot_capture',{})
        if 'midpoint_t' not in cap and snap.get('captured_at_host'):
            cap={'midpoint_t':datetime.fromisoformat(snap['captured_at_host']).timestamp()}
        if any(k not in s for k in FIELDS) or 'midpoint_t' not in cap:
            excluded+=1; continue
        valid=not snap.get('link_lost',True) and all(s[k].get('status')==1 and
              isinstance(s[k].get('value'),(int,float)) and
              isinstance(s[k].get('age_ms'),(int,float)) and 0<=s[k]['age_ms']<=60000 for k in FIELDS)
        if not valid: excluded+=1;continue
        sid=d.get('sid'); signature=(sid,)+tuple(s[k].get('generation') for k in FIELDS)
        if signature in seen: duplicates+=1;continue
        seen.add(signature)
        estimated={k:cap['midpoint_t']-s[k]['age_ms']/1000 for k in FIELDS}
        row={k:s[k]['value'] for k in FIELDS}
        row.update(host_t=cap['midpoint_t'],source_t=estimated['flow_cC'],
                   source_skew_s=max(estimated.values())-min(estimated.values()),
                   generations={k:s[k].get('generation') for k in FIELDS},
                   native_mode=d.get('native',{}).get('mode',UNKNOWN))
        # Logged operating_mode is a protocol field, not internal3CB7. No implicit conversion.
        row['lookup_counterfactual']=evaluate(row['flow_target_cC'],row['flow_cC'])
        groups[sid].append(row)
    result=[]
    for index, rows in enumerate(groups.values()):
        start=rows[0]['host_t']
        for row in rows:
            row['host_relative_s']=round(row.pop('host_t')-start,3)
            row['flow_source_relative_s_estimate']=round(row.pop('source_t')-start,3)
        result.append(dict(circuit=f'circuit-{index+1}',samples=len(rows),
             ranges={k:[min(r[k] for r in rows),max(r[k] for r in rows)] for k in FIELDS},
             max_source_skew_s=max(r['source_skew_s'] for r in rows),
             native_modes=sorted(set(r['native_mode'] for r in rows),key=str),
             timeline=[r for i,r in enumerate(rows) if i==0 or any(r[k]!=rows[i-1][k] for k in ('compressor_Hz','flow_target_cC','operating_mode_raw','native_mode'))]))
    return dict(input_sha256=hashlib.sha256(blob).hexdigest(),groups=result,
                excluded_invalid=excluded,duplicate_generation_vectors=duplicates,
                source_time='host snapshot midpoint (or legacy captured_at_host) minus cached age; estimate, not simultaneous sampling; timeline keeps Hz/target/mode transitions',
                replay_policy_max_age_ms=60000,policy_is_native_timeout=False,
                prediction_validation=UNKNOWN,
                note='Counterfactual ordinary20.01 heating lookup, not observed native demand. No Hz model; latency/error/stop accuracy not identifiable without outbound request, gates and phase-aligned captures.')
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('input',type=Path);p.add_argument('output',type=Path);a=p.parse_args()
    a.output.write_text(json.dumps(replay(a.input),indent=2)+'\n')
