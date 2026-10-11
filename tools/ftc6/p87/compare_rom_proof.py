#!/usr/bin/env python3
"""Compare original-ROM emulator observations with the reconstructed model.

Accepts a completed P87RoutineProof Ghidra log. Does not call any live service.
A Ghidra process exit0 alone is NOT success: script failures may still exit0.
"""
import argparse
import json
from pathlib import Path
import re
from model import lookup, temperature_byte, TimerWord
from native_state import *

def expected_vectors():
    out={f'lookup/{e}':lookup(e) for e in (-201,-200,-199,0,1,250,251)}
    out.update({f'target/{x}':temperature_byte(x) for x in (-1,0,1,49,50,51,8000,9000)})
    h=History70()
    def h70(name,error,phase,enabled=True):
        out['history70/'+name]=h.evaluate(enabled=enabled,error=error,
            phase_3d07=phase,previous_phase_3e01=0)
    h70('equal200',200,2);h70('enter',199,2);h70('leave',199,0)
    out['history70/start']=h.timer.word
    h.timer.word=0x8000|599;h70('hold599',999,0)
    h.timer.word=0x8000|600;h70('expire600',999,0)
    h.state=2;h70('disable',0,0,False);out['history70/clear']=h.timer.word
    h=History50()
    def h50(name,error):
        out['history50/'+name]=h.evaluate(enabled=True,error=error,phase_3d07=0,
                   mode_4927=2,value_3da4=5,threshold_3944=6)
    h50('above200',201);h50('enter200',200);out['history50/start']=h.timer.word
    h.timer.word=0x8000|179;h50('latched179',999)
    h.timer.word=0x8000|180;h50('expire180',999);out['history50/clear']=h.timer.word
    out['limit/min']=out['limit/mirror']=final_limit(70,100,50)
    out.update({f'limit/encode/{x}':limit_code(x) for x in (0,10,30,50,70,100,255)})
    t=TimerWord(0x8000|599)
    for name,mask,fast in [('wrongmask',1,False),('normal',2,False),('accelerated',2,True)]:
        timer_event(t,HISTORY70,mask,fast);out['timer/'+name]=t.word
    t.word=0xfffe;timer_event(t,HISTORY70,2,True);out['timer/overflowguard']=t.word
    for profile in (0,1,2):
        f=FixedFlowLimits();args=dict(profile=profile,held_error=100)
        for name,phase in [('enter',2),('leave',0),('expire',0)]:
            if name=='expire':f.history70.timer.word=0x8000|600
            out[f'fixed/profile{profile}/{name}']=f.evaluate(3500,3400,phase=phase,**args)['native_limit']
    out["bitfb/original_exit_flag"]=128
    out["bitfb/no_positive_alias"]=0
    return out

def compare(text):
    if 'P87_ROM_PROOF_COMPLETE' not in text or 'ERROR' in text or 'Uninitialized' in text:
        raise ValueError('Incomplete, failed or uninitialized ROM execution')
    pairs=re.findall(r'P87_ROM_PASS ([^=\s]+)=(-?\d+)',text)
    observed={k:int(v) for k,v in pairs}
    if len(observed)!=len(pairs):raise ValueError('Duplicate observations')
    expected=expected_vectors()
    if observed!=expected:
        raise ValueError({k:(observed.get(k),expected.get(k)) for k in observed.keys()|expected.keys()
                          if observed.get(k)!=expected.get(k)})
    return dict(status='PASS',observations=len(observed),vectors=observed,
                scope='Synthetic RAM; original ROM instructions; explicit EXITD and signed bit-FB architecture shims; no physical Hz validation')

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('log',type=Path)
    p.add_argument('--output',type=Path);a=p.parse_args()
    report=json.dumps(compare(a.log.read_text()),indent=2)+'\n'
    if a.output:a.output.write_text(report)
    else:print(report,end='')
