#!/usr/bin/env python3
"""Backtest the scalar MPC and fitted pair model; performs no device I/O."""
from __future__ import annotations
import argparse, json
from datetime import datetime
from pathlib import Path
from statistics import mean, median

from energy_planner import (
    PairModel,
    bounded_mpc_command,
    project_pair_step,
    remaining_energy_command,
    round_step_half_up,
    scalar_mpc_command,
)

TARGETS=(1500,2000,2500,4000,2500,2000,1500)

def observed_rows(path: Path):
    rows=[]
    for line in path.read_text().splitlines():
        event=json.loads(line)
        if event.get('kind')!='sample': continue
        values=[]; commands=[]
        for device in event['data'].get('devices',{}).values():
            words=device.get('feedback')
            if not words: break
            power=(words[7]<<16)|words[8]
            if power&0x80000000: power-=2**32
            if power==-2**31: break
            values.append(power); commands.append(words[3])
        if len(values)==2:
            rows.append((datetime.fromisoformat(event['time']).timestamp(),sum(values),sum(commands)))
    return rows

def field_observations(path: Path):
    """Extract attempt11 facts that constrain any counterfactual replay."""
    samples=[];final_results=None
    for line in path.read_text().splitlines():
        event=json.loads(line)
        if event.get('kind')!='sample': continue
        devices=event['data'].get('devices',{})
        if not all(str(sid) in devices and devices[str(sid)].get('feedback') for sid in (1,2)):
            continue
        feedback=[devices[str(sid)]['feedback'] for sid in (1,2)]
        powers=[]
        for words in feedback:
            power=(words[7]<<16)|words[8]
            if power&0x80000000: power-=2**32
            powers.append(power)
        kvs={part.split('=',1)[0]:part.split('=',1)[1]
             for part in (event['data'].get('kvs') or '').split('|') if '=' in part}
        if 'results' in kvs: final_results=[int(x) for x in kvs['results'].split(',')]
        samples.append({'time':datetime.fromisoformat(event['time']).timestamp(),
                        'power':sum(powers),'limited':all(w[1:3]==[4,4] for w in feedback),
                        'sent':sum(w[3] for w in feedback),
                        'reported':int(kvs['cmd']) if 'cmd' in kvs else None})
    anchor=samples[0]['time'];quarters=[]
    for quarter in range(len(TARGETS)):
        rows=[r for r in samples if int((r['time']-anchor)//900)==quarter and r['power']>=0]
        limited=[r for r in rows if r['limited']]
        quarters.append({'quarter':quarter+1,'samples':len(rows),
                         'both_temperature_limited_samples':len(limited),
                         'limited_pair_power_mean_w':mean(r['power'] for r in limited) if limited else None,
                         'limited_pair_power_min_w':min((r['power'] for r in limited),default=None),
                         'limited_pair_power_max_w':max((r['power'] for r in limited),default=None)})
    mismatches=[r for r in samples if r['reported'] is not None and r['reported']!=r['sent']]
    return {'measured_quarter_wh':final_results,
            'nominal_vs_sent_rounding_mismatch_samples':len(mismatches),
            'maximum_rounding_mismatch_w':max((r['sent']-r['reported'] for r in mismatches),default=0),
            'quarter_limiter_observations':quarters}

def model_fit(rows, model):
    predicted=rows[0][1]; errors=[]
    for before,after in zip(rows,rows[1:]):
        dt=after[0]-before[0]
        fraction=model.response_fraction*(before[2]-predicted)
        change=max(-model.fall_w_per_s*dt,min(model.rise_w_per_s*dt,fraction))
        predicted=max(0,predicted+change);errors.append(abs(predicted-after[1]))
    return {'samples':len(errors),'mae_w':mean(errors),'median_ae_w':median(errors),'max_ae_w':max(errors)}

def old_command(elapsed,delivered,command):
    q=elapsed//900;into=elapsed-q*900;remain=900-into
    required=(sum(TARGETS[:q+1])-delivered)*3600/remain
    a=TARGETS[q]*4;b=TARGETS[q+1]*4 if q+1<len(TARGETS) else a
    rate=26.6667 if b>=a else 13.3333;ramp=abs(b-a)/rate
    nominal=a if ramp<1 or into<900-ramp else a+(b-a)*(into-(900-ramp))/ramp
    blend=max(.25,min(.85,into/450));wanted=nominal*(1-blend)+required*blend
    wanted=max(6000,min(24000,wanted));wanted=max(command-400,min(command+800,wanted))
    return round_step_half_up(wanted,500)

def _lerp(t,t0,a,b): return a+(b-a)*(t-t0)/300

def trajectory_command(elapsed,delivered):
    """Exact 1.3.1 constant-time trajectory used in attempt11."""
    t=elapsed
    if t<300: reference=6000
    elif t<600: reference=_lerp(t,300,6000,11000)
    elif t<900: reference=_lerp(t,600,11000,10000)
    elif t<1200: reference=10000
    elif t<1500: reference=_lerp(t,1200,10000,14000)
    elif t<1800: reference=_lerp(t,1500,14000,13000)
    elif t<2100: reference=_lerp(t,1800,13000,12000)
    elif t<2400: reference=12000
    elif t<2700: reference=_lerp(t,2400,12000,11500)
    elif t<3000: reference=11500
    elif t<3300: reference=_lerp(t,3000,11500,10500)
    elif t<3600: reference=_lerp(t,3300,10500,11000)
    elif t<3900: reference=_lerp(t,3600,11000,10000)
    elif t<4200: reference=_lerp(t,3900,10000,9000)
    elif t<4500: reference=_lerp(t,4200,9000,8500)
    elif t<4800: reference=_lerp(t,4500,8500,8000)
    elif t<5100: reference=_lerp(t,4800,8000,6000)
    else: reference=6000
    knots=((300,0),(600,263),(900,1020),(1200,1864),(1500,2844),
           (1800,3971),(2100,5068),(2400,6107),(2700,7112),(3000,8095),
           (3300,9056),(3600,9988),(3900,10875),(4200,11707),(4500,12485),
           (4800,13205),(5100,13870),(5400,14470),(5700,15002),
           (6000,15508),(6300,16010))
    if t<300: reference_wh=0
    elif t>=6300: reference_wh=16010
    else:
        reference_wh=0
        for (ta,a),(tb,b) in zip(knots,knots[1:]):
            if t<tb:
                reference_wh=a+(b-a)*(t-ta)/(tb-ta);break
    correction=max(-3000,min(3000,(reference_wh-delivered)*4))
    return max(6000,min(24000,round_step_half_up(reference+correction,500)))

def _metrics(delivered,boundaries,maximum):
    quarters=[boundaries[0],*(b-a for a,b in zip(boundaries,boundaries[1:]))]
    errors=[actual-target for actual,target in zip(quarters,TARGETS)]
    return {'delivered_wh':delivered,'error_wh':delivered-sum(TARGETS),
            'maximum_command_w':maximum,'cumulative_boundary_wh':[round(x,3) for x in boundaries],
            'quarter_wh':[round(x,3) for x in quarters],
            'quarter_error_wh':[round(x,3) for x in errors],
            'absolute_quarter_error_wh':sum(abs(x) for x in errors),
            'maximum_absolute_quarter_error_wh':max(abs(x) for x in errors)}

def simulate(mode, model):
    elapsed=0;delivered=0.;power=0.;command=6000;startup=330.;maximum=command;boundaries=[];last_retarget=-120
    while elapsed<len(TARGETS)*900:
        if mode=='remaining':
            proposed=remaining_energy_command(elapsed_s=elapsed,delivered_wh=delivered,
                power_w=power,current_command_w=command,quarter_targets_wh=TARGETS,
                command_changing=elapsed-last_retarget<300).command_w
            if proposed!=command and elapsed-last_retarget>=120:
                command=proposed;last_retarget=elapsed
        elif mode in ('trajectory','trajectory_nominal'):
            command=trajectory_command(elapsed,delivered)
            # Attempt11 rounded both halves up. Preserve a nominal replay as a
            # diagnostic, but make the attempt11 replay use the sum sent.
            if mode=='trajectory' and command%1000==500: command+=500
        elif mode:
            planner=bounded_mpc_command if mode=='bounded' else scalar_mpc_command
            command=planner(elapsed_s=elapsed,delivered_wh=delivered,power_w=power,
                current_command_w=command,startup_remaining_s=startup,quarter_targets_wh=TARGETS,
                model=model).command_w
        else: command=old_command(elapsed,delivered,command)
        maximum=max(maximum,command)
        new_power,startup=project_pair_step(power,command,startup,model)
        delivered+=(power+new_power)*.5*model.step_s/3600;power=new_power;elapsed+=model.step_s
        if elapsed%900==0:boundaries.append(round(delivered,3))
    return _metrics(delivered,boundaries,maximum)

def main():
    parser=argparse.ArgumentParser();parser.add_argument('events',type=Path);parser.add_argument('--output',type=Path)
    args=parser.parse_args();model=PairModel();rows=observed_rows(args.events)
    result={'targets_wh':TARGETS,'attempt11_observed':field_observations(args.events),
            'model':model.__dict__,'fit_to_field_log':model_fit(rows,model),
            'old_controller_model_replay':simulate(None,model),
            'attempt11_nominal_trajectory_model_replay':simulate('trajectory_nominal',model),
            'attempt11_trajectory_model_replay':simulate('trajectory',model),
            'remaining_energy_v2_model_replay':simulate('remaining',model),
            'full_grid_mpc_model_replay':simulate('full',model),
            'bounded_mpc_model_replay':simulate('bounded',model),
            'warning':'Counterfactual model replay is not a physical field result.'}
    text=json.dumps(result,indent=2)+'\n'
    if args.output:args.output.write_text(text)
    print(text,end='')
if __name__=='__main__':main()
