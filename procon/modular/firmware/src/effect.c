/* P0080: bounded demand-rate control with separate startup feed-forward. */
#include "effect.h"
#include "effect_feedback.h"
#include "telemetry.h"
#include "service.h"
#include "effect_model.h"
#include "effect_math.h"
typedef struct { uint32_t at; int32_t value; } source_point;
typedef struct { source_point points[16],latest; uint16_t generation; uint8_t head,count,seen; } source_track;
typedef struct { source_point current,recent,older; uint32_t age; uint8_t fresh; } source_trend;
/* Private module state; layout is not part of the cross-module ABI. */
typedef struct {
    uint16_t phase,reason,target,cap,initial,verified,decisions,adjustments;
    uint16_t up_total,down_total,pending;
    int16_t last_delta;
    int32_t previous_w,derivative;
    uint32_t last_decision,last_adjustment,previous_at;
    uint8_t have_previous,pending_demand;
    source_track hz_history,supply_history;
    int32_t hz_goal,trim;
    uint32_t goal_at,hold_at,reverse_at,progress_at;
    uint16_t target_gen,last_hz_target;
    uint8_t target_seen,thermal,holding,held;
    int8_t direction;
    uint8_t lead_started;
    uint16_t response_hz; /* A3/17 at the last verified actuator change. */
} effect_state;
static effect_state reg;
static int32_t absolute(int32_t v){return v<0?-v:v;}
void effect_init(void){reg=(effect_state){0};effect_model_reset();}

void effect_begin(uint16_t target_w,uint16_t cap_cC,uint32_t t){
    reg=(effect_state){0};effect_model_break();reg.target=target_w;reg.cap=cap_cC;reg.phase=EFFECT_START;
    reg.last_decision=reg.last_adjustment=reg.goal_at=t;reg.hz_goal=effect_model_target(target_w);
}
void effect_retarget(uint16_t target,uint16_t cap,uint32_t t){
    int32_t old_goal=reg.hz_goal,new_goal=effect_model_target(target)+reg.trim;
    if(new_goal<2000)new_goal=2000;
    if(new_goal>10300)new_goal=10300;
    reg.target=target;reg.cap=cap;reg.hz_goal=new_goal;
    if(absolute(new_goal-old_goal)>400)reg.goal_at=t;
    reg.progress_at=reg.reverse_at=t;
    reg.holding=reg.held=0;reg.direction=0;
    /* A planned supervisory reversal is not plant hunting.  Preserve response
       memory only when the new goal continues the last actuator direction. */
    if((new_goal-old_goal)*(int32_t)reg.last_delta<=0){reg.last_delta=0;reg.response_hz=0;}
    /* Retarget alone is not evidence that the physical plateau ended.  The
       model's Hz/temperature/flow range gates break the window if it moves. */
}
void effect_capture(uint16_t flow,uint32_t t){reg.initial=reg.verified=flow;reg.last_adjustment=t;reg.last_decision=t-30000u;}
void effect_stop(unsigned why,int restoring){
    reg.reason=(uint16_t)why;reg.phase=restoring?EFFECT_RESTORING:EFFECT_INVALID_FEEDBACK;reg.pending=0;
}
void effect_restored(void){reg.phase=EFFECT_OFF;reg.pending=0;}
/* Existing cross-module snapshot ABI provides independent source provenance.
   Unchanged values with NEW generations are real observations; duplicate polls
   never become extra samples. All differences are wrap-safe unsigned times. */
static source_trend history(source_track *h,unsigned index,int32_t expected,uint32_t t){
    tele_sample sample;
    source_trend out={.current={t,expected},.recent={t,expected},.older={t,expected}};
    if(!tele_snapshot(index,&sample) || sample.status!=TELE_VALID || sample.link_lost ||
       sample.age_ms>=60000u || sample.value!=expected)return out;
    out.fresh=1;out.age=sample.age_ms;out.current=(source_point){t-sample.age_ms,sample.value};
    if(h->seen && sample.generation==h->generation){
        if(sample.value!=h->latest.value){out.fresh=0;return out;}
        out.current=h->latest;
    }else{h->latest=out.current;h->seen=1;}

    if(h->count){
        source_point last=h->points[(h->head+15u)%16u];
        if(out.current.at-last.at>=60000u){
            h->count=h->head=0;reg.response_hz=0;
        }
    }
    if(!h->count || sample.generation!=h->generation){
        h->generation=sample.generation;
        /* Do not let a fast native poll evict the useful sixty-second span. */
        if(!h->count || out.current.at-h->points[(h->head+15u)%16u].at>=5000u){
            h->points[h->head]=out.current;h->head=(uint8_t)((h->head+1u)%16u);
            if(h->count<16)++h->count;
        }
    }
    out.recent=out.older=out.current;
    uint32_t near=UINT32_MAX,old=UINT32_MAX;
    for(unsigned i=0;i<h->count;++i){
        uint32_t age=out.current.at-h->points[i].at;
        if(age>=90000u)continue;
        uint32_t d=age>35000u?age-35000u:35000u-age;
        if(d<near){near=d;out.recent=h->points[i];}
        d=age>60000u?age-60000u:60000u-age;
        if(d<old){old=d;out.older=h->points[i];}
    }
    return out;
}
static int32_t slope(const source_trend *s,const source_point *past,uint32_t min_span,int32_t scale){
    uint32_t span=s->current.at-past->at;
    return s->fresh && span>=min_span && span<90000u?
        (s->current.value-past->value)*scale/(int32_t)span:0;
}
static int32_t thermal_forecast(int32_t supply,int32_t rate,uint32_t age){
    /* Valid0..100C history over>=20s bounds rate<=30000cC/min; fresh age<15s
       keeps the product below450million. Split the whole60s term exactly. */
    return supply+(rate>0?rate+rate*(int32_t)age/60000:0);
}
static int32_t thermal_ceiling(int32_t supply,int32_t rate,const source_trend *water){
    /* Unknown history retains gain3; a qualified trend permits gain8.
       Both use the same conservative age-aware horizon, never negative slope. */
    int32_t gain=water->fresh && water->age<15000u && water->current.at-water->older.at>=40000u &&
        water->current.at-water->recent.at>=20000u?8:3;
    int32_t margin=EFFECT_THERMAL_APPROACH_CC-thermal_forecast(supply,rate,water->age);
    int32_t limit=EFFECT_THERMAL_APPROACH_CC+(margin>0?gain*margin:margin);
    if(limit<3000)limit=3000;
    return limit;
}
/* Qualified braking permits a small negative delta. Each verified cut starts
   a full minute of observation; temperature rise alone never adds gas. */
static int32_t bounded_demand(int32_t next,int32_t supply,uint16_t flow,int margin,
                              int32_t max_down,uint32_t down_wait,uint32_t t){
    int32_t floor=supply+margin;
    if(floor>flow)floor=flow;
    if(next<floor)next=floor;
    if(next<(int32_t)flow-max_down)next=(int32_t)flow-max_down;
    if(next<flow && t-reg.last_adjustment<down_wait)next=flow;
    return next;
}
static int response_waiting(int direction,unsigned hz,uint32_t t){
    if(!direction || !reg.response_hz || !reg.last_delta || t-reg.last_adjustment>=60000u)return 0;
    if(direction>0 && reg.last_delta>0)return hz<=reg.response_hz;
    if(direction<0 && reg.last_delta<0)return hz>=reg.response_hz;
    return 0;
}
/* Initial gas uses the same frequency distance as the running controller.
   GET04 is only a coarse startup estimate until independent A3 is available. */
static int32_t start_demand(const effect_measurement *m){
    int32_t error=reg.hz_goal-(int32_t)m->hz*100;
    return m->supply_cC+(error>1500?1000:error>600?500:error>300?300:200);
}
/* Setpoint is the actuator; actual supply has a separate ceiling. */
static uint16_t effect_fast(const effect_measurement *m,uint16_t flow,uint32_t t){
    int32_t supply=m->supply_cC;
    if(supply<0 || supply>10000 || m->short_w<0 || !m->hz || m->hz>=255)return 0;
    source_trend water=history(&reg.supply_history,3,supply,t);
    int32_t rate=water.age<15000u?slope(&water,&water.recent,20000u,60000):0;
    int32_t forecast=thermal_forecast(supply,rate,water.age);
    int32_t ceiling=thermal_ceiling(supply,rate,&water);
    tele_sample native;
    uint8_t usable=m->age_ms<60000u && water.fresh && tele_snapshot(8,&native) &&
        native.status==TELE_VALID && !native.link_lost && native.age_ms<60000u && native.value==m->hz;
    uint8_t quick=usable && m->age_ms<15000u && water.age<15000u && native.age_ms<15000u;
    unsigned hz=svc_read(378),generation=svc_read(382);
    int valid=svc_read(379) && svc_read(383) && svc_read(380)<60 && hz>0 && hz<121;
    if(t-reg.last_decision<30000u)return 0;
    reg.last_decision=t;++reg.decisions;
    if(reg.have_previous && t-reg.previous_at>=1000u)
        reg.derivative=minute_rate(m->short_w-reg.previous_w,t-reg.previous_at);
    reg.previous_w=m->short_w;reg.previous_at=t;reg.have_previous=1;
    /* Current constraint, not a latch: cooling immediately restores headroom.
       The Hz loop still runs underneath this higher-priority envelope. */
    reg.thermal=forecast>=EFFECT_THERMAL_APPROACH_CC;
    int falling=0,request_limited=0;
    int32_t next=flow;reg.phase=EFFECT_HOLD;reg.reason=EFFECT_OK;
    if(reg.holding && t-reg.hold_at>=120000u)reg.holding=0;
    int minimum=usable && valid && hz<=20 && m->short_w>(int32_t)reg.target+500;
    if(valid && usable && (!reg.target_seen || generation!=reg.target_gen)){
        int change=reg.target_seen?(int)hz-reg.last_hz_target:0;
        falling=change<0;
        if(!reg.target_seen || change)reg.progress_at=t;
        if(absolute(change)>=5){
            int sign=change>0?1:-1;
            if(reg.direction && sign!=reg.direction && t-reg.reverse_at<180000u &&
               (!reg.held || t-reg.hold_at>=300000u)){
                reg.holding=reg.held=1;reg.hold_at=t;
            }
            reg.direction=(int8_t)sign;reg.reverse_at=t;
        }
        reg.target_seen=1;reg.target_gen=(uint16_t)generation;reg.last_hz_target=(uint16_t)hz;
        int32_t base=effect_model_target(reg.target);
        if(t-reg.goal_at>=60000u){
            int32_t error=(int32_t)reg.target-m->short_w;
            /* Trim only after the inner loop caught up; no windup under limits. */
            if(!minimum && !reg.holding && (error<0 || (!reg.thermal && flow<ceiling)) &&
               svc_read(373) && svc_read(377) && svc_read(374)<60 &&
               absolute((int32_t)svc_read(372)-(int32_t)hz)<=2 &&
               absolute((int32_t)hz*100-reg.hz_goal)<=300 && absolute(error)>500){
                reg.trim+=error>0?100:-100;
                if(reg.trim>1500)reg.trim=1500;
                if(reg.trim< -1500)reg.trim=-1500;
            }
            reg.goal_at=t;
        }
        reg.hz_goal=base+reg.trim;
        if(reg.hz_goal<2000)reg.hz_goal=2000;
        if(reg.hz_goal>10300)reg.hz_goal=10300;
        int32_t error=reg.hz_goal-(int32_t)hz*100;
        int wanted=error>300?1:error< -200?-1:0;
        int awaiting=response_waiting(wanted,hz,t);
        if(!reg.holding && !minimum){
            if((error>=-300 || hz<=20 || (hz<24 && change<0)) && flow<supply+50){
                if(!awaiting){next=flow+50;if(next>supply+50)next=supply+50;}
            }else if(error>300){
                int delta=error>1500?1000:error>600?500:300;
                next=supply+delta;
                /* Never keep cutting while the native target is already falling. */
                if(change<0 && next<flow)next=flow;
                /* A fixed delta can settle below the Hz goal. Do not repeatedly
                   brake a slow approach while still >3Hz short. An independent
                   unchanged target for90s permits one bounded gas increment,
                   then another full observation interval before reconsidering. */
                if(change<5 && next<flow)next=flow;
                if(t-reg.progress_at>=90000u){next=(int32_t)flow+50;reg.progress_at=t;}
                int rise=quick?(error>1000?200:error>600?100:50):50;
                if(next>flow+rise)next=flow+rise;
                if(awaiting)next=flow;
            }else if(error< -200){
                /* Keep reducing through a falling native target while still
                   far above the goal; near the goal, observe that response. */
                if(!awaiting && (error< -1000 || change>=0))
                    next=(int32_t)flow-(error< -1000?100:50);
            }else if(change>=0 && flow>supply+200)next=(int32_t)flow-50;
            /* At the Hz goal, excess delta remains acceleration demand even
               through a native plateau. Taper it; a falling target pauses the
               taper, and a lone one-Hz fall never adds gas by itself. */
        }
        if(!quick && next>flow && t-reg.last_adjustment<60000u)next=flow;
        if(awaiting && next==flow){reg.phase=EFFECT_CAPTURE;reg.reason=EFFECT_RESPONSE_PENDING;}
    }
    if(!reg.lead_started && usable){
        reg.lead_started=1;reg.phase=EFFECT_START;next=flow;
        if(m->short_w<(int32_t)reg.target-300){
            if(quick)next=start_demand(m);
            else if(t-reg.last_adjustment>=60000u)next=(int32_t)flow+50;
        }
    }
    if(reg.holding){reg.phase=EFFECT_CAPTURE;effect_model_break();}
    if(reg.thermal || next>ceiling || (flow>=ceiling && ceiling<reg.cap)){
        reg.thermal=1;
        if(next>ceiling)next=ceiling;
        reg.phase=EFFECT_LIMITED;reg.reason=EFFECT_TEMPERATURE_CAP;effect_model_break();
    }
    if(next>reg.cap || flow>reg.cap ||
       (usable && valid && reg.hz_goal-(int32_t)hz*100>300 && flow>=reg.cap)){
        request_limited=1;if(next>reg.cap)next=reg.cap;
    }
    int margin=50;
    if(usable && valid && (reg.thermal || (hz>20 && !(hz<24 && falling) && reg.hz_goal-(int32_t)hz*100 < -300)))
        margin=reg.thermal || reg.hz_goal-(int32_t)hz*100 < -600 ? -100 : -50;
    if(next<2000)next=2000;
    int32_t hz_error=reg.hz_goal-(int32_t)hz*100;
    int32_t max_down=reg.thermal || hz_error< -1000?100:50;
    uint32_t down_wait=reg.thermal?30000u:60000u;
    next=bounded_demand(next,supply,flow,margin,max_down,down_wait,t);
    if(!usable && next>flow)next=flow;
    if(next==flow){
        if(reg.thermal){reg.phase=EFFECT_LIMITED;reg.reason=EFFECT_TEMPERATURE_CAP;}
        else if(request_limited){reg.phase=EFFECT_LIMITED;reg.reason=EFFECT_REQUEST_CAP;}
        else if(minimum){reg.phase=EFFECT_LIMITED;reg.reason=EFFECT_MINIMUM_OUTPUT;}
        else if(!usable){reg.phase=EFFECT_CAPTURE;reg.reason=EFFECT_SOURCE_STALE;}
        return 0;
    }
    if(!reg.thermal){reg.phase=request_limited||minimum?EFFECT_LIMITED:EFFECT_CAPTURE;
        reg.reason=request_limited?EFFECT_REQUEST_CAP:minimum?EFFECT_MINIMUM_OUTPUT:EFFECT_OK;}
    reg.pending=(uint16_t)next;return reg.pending;
}
uint16_t effect_decide(const effect_measurement *m,uint16_t flow,uint32_t t){
    effect_model_tick(t,m->ready && m->age_ms<60000u && reg.phase!=EFFECT_LIMITED &&
        reg.phase!=EFFECT_INVALID_FEEDBACK && reg.phase!=EFFECT_OFF && reg.phase!=EFFECT_RESTORING && !reg.holding && !reg.thermal);
    if(!m->ready){if(m->quality!=EF_PENDING && m->quality!=EF_WARMUP)effect_stop(EFFECT_BAD_FEEDBACK,0);return 0;}
    if(reg.phase==EFFECT_OFF || reg.phase==EFFECT_RESTORING || reg.phase==EFFECT_INVALID_FEEDBACK || reg.pending)return 0;
    return effect_fast(m,flow,t);
}
int effect_pending_demand(void){return reg.pending?reg.pending_demand:0;}
/* Shared bounded startup/pause selection; callers retain admission policy. */
static uint16_t startup_target(const effect_measurement *m,uint16_t flow,unsigned kind,uint32_t t){
    int32_t next=flow;
    source_trend water=history(&reg.supply_history,3,m->supply_cC,t);
    source_trend hz=history(&reg.hz_history,8,m->hz,t);
    uint8_t usable=water.fresh && hz.fresh && m->age_ms<60000u;
    uint8_t quick=usable && water.age<15000u && hz.age<15000u && m->age_ms<15000u;
    if(kind==1){next=m->supply_cC+50;if(next>EFFECT_NATIVE_RESTART_CC)next=EFFECT_NATIVE_RESTART_CC;if(next<2000)next=2000;}
    else if(!reg.lead_started && m->short_w>=0 && m->short_w<(int32_t)reg.target-150){
        if(quick)next=start_demand(m);
        else if(usable && t-reg.last_adjustment>=60000u)next=(int32_t)flow+50;
    }
    int32_t limit=thermal_ceiling(m->supply_cC,water.age<15000u?slope(&water,&water.recent,20000u,60000):0,&water);
    if(next>limit)next=limit;
    if(next>reg.cap)next=reg.cap;
    if(reg.lead_started && t-reg.last_adjustment<30000u)return flow;
    next=bounded_demand(next,m->supply_cC,flow,50,50,60000u,t);
    /* A request cap may be below the floor used to preserve compressor
       operation.  Never let that floor raise an already-compliant request;
       when flow is above the cap, retain the ordinary bounded down slew. */
    if(flow<=reg.cap && next>reg.cap)next=reg.cap;
    if(kind==2 && next>flow && !quick){
        if(!usable || t-reg.last_adjustment<60000u)next=flow;
        else if(next>(int32_t)flow+50)next=(int32_t)flow+50;
    }else if(next>flow && !usable)next=flow;
    if(next!=flow){reg.pending=(uint16_t)next;reg.pending_demand=(uint8_t)kind;}
    return (uint16_t)next;
}
uint16_t effect_entry_demand(const effect_measurement *m,uint16_t flow,unsigned native_mode,uint32_t t){
    reg.pending=reg.pending_demand=0;
    if(m->supply_cC<0 || m->supply_cC>10000)return 0;
    unsigned kind=2;
    if(native_mode==0 || (m->quality==EF_WAIT_NATIVE && m->hz==0)){
        kind=1;
    }else if((native_mode==2 || native_mode==7) && (m->mode==2 || m->mode==7) &&
             (m->quality==EF_READY || m->quality==EF_SETTLING) && m->pairs && m->age_ms<15000u &&
             m->hz>0 && m->hz<255 && m->instant_w>=0 && m->short_w>=0){
        /* Heating qualification above is independent of the power deficit. */
    }else return 0;
    return startup_target(m,flow,kind,t);
}
uint16_t effect_pause_demand(const effect_measurement *m,uint16_t flow,uint32_t t){
    /* One coherent heating pair permits startup demand, not power regulation.
       Re-evaluate temperature protection throughout the averaging warmup. */
    if(!reg.pending && m->quality==EF_SETTLING && m->pairs &&
       m->age_ms<15000u && (m->mode==2 || m->mode==7) && m->hz>0 && m->hz<255 &&
       m->supply_cC>=0 && m->supply_cC<=10000 &&
       reg.phase!=EFFECT_INVALID_FEEDBACK && reg.phase!=EFFECT_OFF && reg.phase!=EFFECT_RESTORING){
        uint16_t next=startup_target(m,flow,2,t);
        return next==flow?0:next;
    }
    /* A native rundown/pause needs positive restart margin, not another blind
       thermal cut.  Keep the request 0.5C above actual whenever that fits below
       the actual-water priority.  A hotter plant gets the highest sub-limit
       request, so this path can retain/recover demand without requesting >45C. */
    if(m->quality!=EF_WAIT_NATIVE || m->hz>=255 || reg.pending ||
       reg.phase==EFFECT_OFF || reg.phase==EFFECT_RESTORING || reg.phase==EFFECT_INVALID_FEEDBACK ||
       m->supply_cC<0 || m->supply_cC>10000)return 0;
    if(flow>reg.cap){
        if(t-reg.last_adjustment<60000u)return 0;
        uint16_t next=(uint16_t)(flow-50u<reg.cap?reg.cap:flow-50u);
        reg.pending=next;reg.pending_demand=1;reg.phase=EFFECT_LIMITED;reg.reason=EFFECT_REQUEST_CAP;return next;
    }
    int32_t desired=m->supply_cC+50; /*0.5C above fresh measured supply*/
    if(desired>EFFECT_NATIVE_RESTART_CC)desired=EFFECT_NATIVE_RESTART_CC;
    /* Do not chase a cool measurement down during a native pause.  A request
       above the 45C policy is the only prompt downward correction here. */
    if(flow>EFFECT_NATIVE_RESTART_CC)desired=EFFECT_NATIVE_RESTART_CC;
    if(desired>reg.cap)desired=reg.cap;
    if(desired<2000)desired=2000;
    if(flow<=EFFECT_NATIVE_RESTART_CC && desired<=flow){reg.reason=EFFECT_OK;return 0;}
    reg.pending=(uint16_t)desired;reg.pending_demand=1;
    if(m->supply_cC>=EFFECT_THERMAL_APPROACH_CC || flow>EFFECT_NATIVE_RESTART_CC){
        reg.phase=EFFECT_LIMITED;reg.reason=EFFECT_TEMPERATURE_CAP;
    }else reg.reason=EFFECT_OK;
    return reg.pending;
}
void effect_discard_pending(void){reg.pending=0;reg.pending_demand=0;}
void effect_wait(unsigned quality,uint32_t t){
    effect_model_break();
    if(reg.phase==EFFECT_OFF || reg.phase==EFFECT_RESTORING || reg.phase==EFFECT_INVALID_FEEDBACK)return;
    reg.phase=quality==EF_WAIT_NATIVE?EFFECT_WAIT_NATIVE:EFFECT_SETTLING;
    /* A native pause is not evidence that a running pump failed to respond. */
    if(quality==EF_WAIT_NATIVE){reg.have_previous=0;reg.derivative=0;reg.hz_history=(source_track){0};reg.supply_history=(source_track){0};reg.lead_started=0;reg.response_hz=0;reg.last_decision=t;}
}
void effect_verified(uint16_t flow,uint32_t t){
    if(reg.pending && flow==reg.pending){
        if(reg.pending_demand==2)reg.lead_started=1;
        reg.last_delta=(int16_t)((int32_t)flow-reg.verified);
        if(reg.last_delta>0){reg.up_total=(uint16_t)(reg.up_total+reg.last_delta);}
        else reg.down_total=(uint16_t)(reg.down_total-reg.last_delta);
        ++reg.adjustments;reg.last_adjustment=t;
        reg.response_hz=reg.target_seen?reg.last_hz_target:0;
        /* Measured minimum interval starts at completed readback. */
        reg.last_decision=t;reg.pending=reg.pending_demand=0;
    }
    reg.verified=flow;
}
uint16_t effect_read(unsigned a,const effect_measurement *m,uint16_t flow,uint32_t t){
    int32_t value=0;
    /* FC04 input provenance mirrors use the existing controller route.
       FC16 command300..307 is a separate register bank and unchanged. */
    if(a>=300 && a<=307){
        unsigned offset=(a-300)%4;
        return svc_read(373+(a-300)/4*6+offset+(offset>=2));
    }
    if(a>=308 && a<=319){
        switch(a){
        case 308:return 4;case 309:return (uint16_t)reg.hz_goal;
        case 310:return (uint16_t)effect_model_gain();
        case 311:return (uint16_t)((uint32_t)effect_model_bias()>>16);
        case 312:return (uint16_t)effect_model_bias();
        case 313:return effect_model_updates(0);case 314:return effect_model_updates(1);
        case 315:{
            unsigned hz=svc_read(378);
            int valid=svc_read(379) && svc_read(383) && svc_read(380)<60 && hz>0 && hz<121;
            int power_valid=m->short_w>=0;
            int32_t e=valid?reg.hz_goal-(int32_t)hz*100:0;
            uint16_t f=(reg.thermal?EFFECT_FLAG_THERMAL:0) |
                (reg.holding?EFFECT_FLAG_OSCILLATION:0) |
                (valid && e>300?EFFECT_FLAG_RAMP_UP:0) |
                (valid && e< -200?EFFECT_FLAG_RAMP_DOWN:0) |
                (valid && response_waiting(e>300?1:e< -200?-1:0,hz,t)?EFFECT_FLAG_RESPONSE_WAIT:0) |
                (valid && power_valid && m->age_ms<60000u && hz<=20 && m->short_w>(int32_t)reg.target+500?EFFECT_FLAG_MINIMUM_OUTPUT:0) |
                ((reg.phase==EFFECT_LIMITED && reg.reason==EFFECT_REQUEST_CAP) || (valid && e>300 && flow>=reg.cap)?EFFECT_FLAG_REQUEST_CAP:0);
            if(valid && power_valid && absolute(e)<=300 && absolute((int32_t)reg.target-m->short_w)<=500)f|=EFFECT_FLAG_TRACKING;
            return f;
        }
        case 316:return reg.holding && t-reg.hold_at<120000u?(uint16_t)((120000u-(t-reg.hold_at))/1000u):0;
        case 317:return svc_read(372);case 318:return svc_read(378);
        default:return (uint16_t)(int16_t)reg.trim;
        }
    }
    if(a>=325 && a<=332){
        value=a<327?m->instant_w:a<329?m->short_w:a<331?m->slow_w:
            m->short_w==INT32_MIN?INT32_MIN:(int32_t)reg.target-m->short_w;
        return a%2?(uint16_t)((uint32_t)value>>16):(uint16_t)value;
    }
    switch(a){
    case 320:return 1;case 321:return reg.phase;case 322:return reg.reason;
    case 323:return reg.target;case 324:return reg.cap;
    case 333:return m->quality;case 334:return m->ready;case 335:return m->pairs;
    case 336:return m->age_ms/1000u>65535u?65535:(uint16_t)(m->age_ms/1000u);case 337:return (uint16_t)(m->span_ms/1000u);
    case 338:return flow;case 339:return (uint16_t)reg.last_delta;
    case 340:return (t-reg.last_adjustment)/1000u>65535u?65535:(uint16_t)((t-reg.last_adjustment)/1000u);
    case 341:return m->hz;case 342:return reg.decisions;case 343:return reg.adjustments;
    case 344:return reg.up_total;case 345:return reg.down_total;case 346:return effect_model_seeded();
    case 347:return reg.pending;case 348:return (uint16_t)(int16_t)(reg.derivative>32767?32767:reg.derivative< -32768?-32768:reg.derivative);
    case 349:return reg.initial;case 350:return 1;case 351:return 0;
    default:return 0;
    }
}
