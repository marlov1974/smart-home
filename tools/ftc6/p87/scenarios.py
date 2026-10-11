"""Prescribed inputs; event indices are NOT native control ticks."""
import json
from pathlib import Path
from model import evaluate, pump_step, TimerWord, water_balance_delta, UNKNOWN

def scenarios():
    out=[]
    def add(n, name, rows, missing):
        out.append(dict(scenario=n, name=name, input_kind='synthetic prescribed trajectory',
                        result='PARTIAL', timeline=rows, unresolved=missing))
    add(1,'positive step and different histories',
        [dict(history=h,event=k,**evaluate(t,3000)) for h,ts in
         [('low',[3000,3100,3500]),('high',[5500,4000,3500])] for k,t in enumerate(ts)],
        'Identical final error gives identical local lookup; downstream history response UNKNOWN.')
    add(2,'constant, zero, reversed error',
        [dict(initial_downstream_demand=init,event=i,**evaluate(t,3500))
         for init in ['minimum','maximum'] for i,t in enumerate([4000]*3+[3500]*3+[3000]*3)],
        'Local lookup has no accumulator/windup; downstream initial demand is not modeled.')
    timer=[]
    for count in [179,180,181]:
        t=TimerWord(0x8000|count); timer.append(dict(raw_count=count,status=t.status(180)))
    t=TimerWord(0x8000|180);t.pause();timer.append(dict(event='pause',word=t.word,status=t.status(180)))
    t.resume();timer.append(dict(event='resume',word=t.word,status=t.status(180)))
    t.clear();timer.append(dict(event='clear',word=t.word,status=t.status(180)))
    add(3,'below/equal/above and helper boundaries',
        [dict(duration_label=d,**evaluate(3500,f)) for d in ['short','sustained'] for f in [3499,3500,3501,3699,3700,3701]]+timer,
        'Timer180 is helper test only, not a proven thermostat timer. Stop/restart UNKNOWN.')
    add(4,'fast versus slow target startup',
        [dict(trajectory=name,event=i,**evaluate(t,f)) for name,targets in
         [('fast',[5500,4500,3800,3600]),('slow',[3300,3350,3400,3450])]
         for i,(t,f) in enumerate(zip(targets,[3100,3250,3400,3550]))],
        'No thermal plant or Hz prediction. Whether either trajectory avoids the 6kW stop is UNKNOWN.')
    add(5,'repeated identical versus sparse commands',
        [dict(schedule=s,event=i,**evaluate(3500,3300)) for s,n in [('repeated',4),('sparse',1)] for i in range(n)],
        'Assignment and lookup idempotent; command acceptance cadence and other timer side effects UNKNOWN.')
    add(6,'pump/return variation',
        [dict(flow_L_min=q,return_C=r,assumed_delta_C=water_balance_delta(6000,q),
              implied_measured_flow_C=r+water_balance_delta(6000,q),commanded_target=UNKNOWN)
         for q in [10,15,20] for r in [28,34]]+
        [dict(correction=c,selected_step=pump_step(1,8,3,5,state_3ad2=2,correction_49c7=c)) for c in range(8)],
        '49C7 producer and Water flow control correspondence unresolved. Balance does not prescribe target.')
    add(7,'heating DHW heating natural restart',
        [dict(event=i,phase=p,pump_step=pump_step(1,p,3,5),**evaluate(3500,3300,phase=p)) for i,p in enumerate([8,9,8])],
        'DHW priority, valve travel, overrun, restart and state transfer UNKNOWN.')
    add(8,'external limits and invalid feedback',
        [evaluate(3500,3300,valid=False),evaluate(3500,3300,age_ms=60001),
         evaluate(3500,3300,profile_0900=2),evaluate(3500,3300)],
        'External controller limitation/minimum capacity/flow failures cannot be synthesized as Hz.')
    return out
if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('output',type=Path);a=p.parse_args()
    a.output.write_text(json.dumps(scenarios(),indent=2)+'\n')
