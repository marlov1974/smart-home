/* P0080: bounded demand-rate control with separate startup feed-forward. */
#include "effect.h"
#include "effect_feedback.h"
typedef struct { uint32_t at; int16_t supply; uint16_t hz; } lead_point;
/* Private module state; layout is not part of the cross-module ABI. */
typedef struct {
    uint16_t phase,reason,target,cap,initial,verified,decisions,adjustments;
    uint16_t up_total,down_total,unresponsive,pending,boot_unknown,limit_latched;
    int16_t last_delta;
    int32_t previous_w,last_up_w,derivative;
    uint32_t last_decision,last_adjustment,previous_at;
    uint8_t have_previous,assess_up,pending_demand;
    lead_point lead_history[16];
    uint8_t lead_head,lead_count,lead_started;
    uint32_t lead_sample_at;
    uint8_t temperature_limited;
    int16_t fine_carry;
    int32_t response_lead; /* W: bounded memory, never accumulated actuator demand. */
} effect_state;
static effect_state reg;
static int32_t absolute(int32_t v){return v<0?-v:v;}
void effect_init(void){reg=(effect_state){0};reg.boot_unknown=1;}

void effect_begin(uint16_t target_w,uint16_t cap_cC,uint32_t t){
    effect_init();reg.target=target_w;reg.cap=cap_cC;reg.phase=EFFECT_START;
    reg.last_decision=reg.last_adjustment=t;
}
void effect_capture(uint16_t flow,uint32_t t){reg.initial=reg.verified=flow;reg.last_adjustment=t;reg.last_decision=reg.cap>4000?t-30000u:t;}
void effect_stop(unsigned why,int restoring){
    reg.reason=(uint16_t)why;reg.phase=restoring?EFFECT_RESTORING:EFFECT_INVALID_FEEDBACK;reg.pending=0;
}
void effect_restored(void){reg.phase=EFFECT_OFF;reg.pending=0;}
static void history(const effect_measurement *m,uint32_t t,lead_point *past,lead_point *accel){
    /* No generation field is exported to this module. Record no faster than5s,
       require fresh paired feedback and abandon a history spanning a long gap. */
    if(reg.lead_count && t-reg.lead_sample_at>=60000u){reg.lead_count=reg.lead_head=0;reg.fine_carry=0;reg.response_lead=0;}
    if(m->age_ms<15000u && (!reg.lead_count || t-reg.lead_sample_at>=5000u)){
        reg.lead_history[reg.lead_head]=(lead_point){t,(int16_t)m->supply_cC,m->hz};
        reg.lead_head=(uint8_t)((reg.lead_head+1u)%16u);if(reg.lead_count<16)++reg.lead_count;
        reg.lead_sample_at=t;
    }
    *past=(lead_point){t,(int16_t)m->supply_cC,m->hz};*accel=*past;
    uint32_t distance=UINT32_MAX,accel_distance=UINT32_MAX;
    for(unsigned i=0;i<reg.lead_count;++i){
        uint32_t age=t-reg.lead_history[i].at;
        if(age>=90000u)continue;
        uint32_t d=age>35000u?age-35000u:35000u-age;
        if(d<distance){distance=d;*past=reg.lead_history[i];}
        d=age>60000u?age-60000u:60000u-age;
        if(d<accel_distance){accel_distance=d;*accel=reg.lead_history[i];}
    }
}
static int32_t thermal_ceiling(int32_t supply,int32_t rate){
    int32_t positive=rate>0?rate:0,margin=3900-supply-positive/6;
    int32_t limit=3900+(margin>0?3*margin:margin);
    if(supply+positive/2>=4000 && limit>3900)limit=3900;
    if(limit<3000)limit=3000;
    return limit<reg.cap?limit:reg.cap;
}
static int32_t supply_rate(int32_t supply,lead_point past,uint32_t t){
    return t-past.at>=20000u?(int32_t)(((int64_t)(supply-past.supply)*60000)/(t-past.at)):0;
}
/* Setpoint is the actuator; actual supply has a separate ceiling. */
static uint16_t effect_fast(const effect_measurement *m,uint16_t flow,uint32_t t){
    int32_t supply=m->supply_cC;
    if(supply<0 || supply>10000 || m->short_w<0 || m->hz==0 || m->hz==255)return 0;
    lead_point past,accel;history(m,t,&past,&accel);
    uint32_t span=t-past.at,accel_span=t-accel.at,dt=t-reg.last_decision;
    int32_t rate=0;
    if(span>=20000u){
        if(accel_span>=40000u)rate=(int32_t)(((int64_t)((int32_t)m->hz-accel.hz)*60000000)/accel_span); /*mHz/min*/
    }
    int32_t thermal_cap=thermal_ceiling(supply,supply_rate(supply,past,t));
    if(dt<30000u && flow<=thermal_cap)return 0;
    reg.last_decision=t;++reg.decisions;
    if(reg.have_previous && t-reg.previous_at>=1000u)
        reg.derivative=(int32_t)(((int64_t)(m->short_w-reg.previous_w)*60000)/(t-reg.previous_at));
    reg.previous_w=m->short_w;reg.previous_at=t;reg.have_previous=1;
    int32_t next=flow;reg.phase=EFFECT_HOLD;reg.reason=EFFECT_OK;
    /* Ordinary15..59s old data holds the actuator. Thermal prediction is still
       evaluated; hard-stale handling belongs to the existing control layer. */
    if(m->age_ms<15000u){
        if(!reg.lead_started){
            reg.lead_started=1;reg.phase=EFFECT_START;
            /* Match the current host identification trial's45C initial demand.
               Do not add startup gas if output is already at/above its goal. */
            if(m->short_w<(int32_t)reg.target-300)next=reg.cap<4500?reg.cap:4500;
        }else if(span>=20000u && accel_span>=40000u){
            int32_t predicted=m->short_w+110*((int32_t)m->hz-past.hz);
            int32_t lead=rate>0?rate*33/400:0; /*45s at110W/Hz*/
            if(lead>1500)lead=1500;
            /* A frequency plateau does not erase the last native acceleration.
               Forget promptly when the plant falls or demand is already mild. */
            reg.response_lead-= (int32_t)(dt/100u);
            if(reg.response_lead<lead)reg.response_lead=lead;
            if(rate<0 || m->hz<past.hz || (int32_t)flow-supply<200)reg.response_lead=0;
            int32_t future=predicted+reg.response_lead;
            int32_t desired=((int32_t)reg.target-future)*1000/220; /*mHz/min*/
            if(desired>12000)desired=12000;
            if(desired< -12000)desired=-12000;
            int32_t step=(int32_t)(((int64_t)(desired-rate)*(dt>45000u?45000u:dt))/3600000);
            int32_t bound=(predicted>(int32_t)reg.target+1200 ||
                (future>(int32_t)reg.target+300 && rate>0))?100:50;
            /* Quantized10Hz native steps must not brake far below the goal. */
            if(predicted<(int32_t)reg.target-1500 && step<0)step=0;
            /* Already falling near/below goal: NEVER continue earlier braking. */
            if((rate<0 || m->hz<past.hz) && predicted<=(int32_t)reg.target+300 && step<0)step=0;
            if(m->hz==past.hz && predicted<(int32_t)reg.target-300 && future<(int32_t)reg.target+150 && step<0)step=0;
            /* Rising power alone is not a reason to ignore a persistent deficit. */
            if(step>0 && reg.derivative>0 && m->short_w+reg.derivative/2>=(int32_t)reg.target-150)step=0;
            int32_t up=50;
            if(step>0 && m->short_w<(int32_t)reg.target-750 && future<(int32_t)reg.target-750 && (int32_t)flow-supply<200)step=up=100;
            if(absolute(predicted-(int32_t)reg.target)<=150 && absolute(rate)<3000){step=0;reg.fine_carry=0;}
            if(!step || (step<0 && reg.fine_carry>0) || (step>0 && reg.fine_carry<0))reg.fine_carry=0;
            step+=reg.fine_carry;reg.fine_carry=0;
            if(absolute(step)<10){reg.fine_carry=(int16_t)step;step=0;}
            if(step>up)step=up;
            if(step< -bound)step=-bound;
            next=(int32_t)flow+step;if(step)reg.phase=EFFECT_CAPTURE;
        }
    }
    reg.temperature_limited=(uint8_t)(next>thermal_cap || (flow>=thermal_cap && thermal_cap<reg.cap));
    if(next>=thermal_cap){next=thermal_cap;reg.response_lead=0;if(reg.fine_carry>0)reg.fine_carry=0;}
    if(reg.temperature_limited){reg.phase=EFFECT_LIMITED;reg.reason=EFFECT_TEMPERATURE_CAP;}
    if(next>reg.cap)next=reg.cap;
    if(next<=3000){next=3000;if(reg.fine_carry<0)reg.fine_carry=0;}
    if(next==flow)return 0;
    reg.pending=(uint16_t)next;reg.last_up_w=m->short_w;return reg.pending;
}
uint16_t effect_decide(const effect_measurement *m,uint16_t flow,uint32_t t){
    if(!m->ready){if(m->quality!=EF_PENDING && m->quality!=EF_WARMUP)effect_stop(EFFECT_BAD_FEEDBACK,0);return 0;}
    if(reg.phase==EFFECT_OFF || reg.phase==EFFECT_RESTORING || reg.phase==EFFECT_INVALID_FEEDBACK || reg.pending)return 0;
    if(reg.cap>4000)return effect_fast(m,flow,t);
    if(t-reg.last_decision<60000u)return 0;
    reg.last_decision=t;++reg.decisions;
    int32_t measured=m->short_w,error_w=(int32_t)reg.target-measured;
    reg.derivative=0;
    if(reg.have_previous && t-reg.previous_at>=1000u)
        reg.derivative=(int32_t)(((int64_t)(measured-reg.previous_w)*60000)/(t-reg.previous_at));
    reg.previous_w=measured;reg.previous_at=t;reg.have_previous=1;
    if(reg.assess_up){
        if(measured-reg.last_up_w<250){if(reg.unresponsive<3)++reg.unresponsive;}else reg.unresponsive=0;
        reg.assess_up=0;
    }
    /* LIMITED is latched against further increases, but overshoot may reduce. */
    if(reg.limit_latched && error_w>=-700){reg.phase=EFFECT_LIMITED;reg.reason=reg.limit_latched;return 0;}
    int32_t abs_error=absolute(error_w);
    if(abs_error<=500 || (reg.phase==EFFECT_HOLD && abs_error<700)){
        reg.phase=EFFECT_HOLD;reg.reason=EFFECT_OK;return 0;
    }
    if(error_w>0 && reg.unresponsive>=3){reg.phase=EFFECT_LIMITED;reg.reason=reg.limit_latched=EFFECT_UNKNOWN_UNREACHABLE;return 0;}
    if(error_w>0 && reg.up_total>=500){reg.phase=EFFECT_LIMITED;reg.reason=reg.limit_latched=EFFECT_CUMULATIVE_CAP;return 0;}
    int32_t projected=measured+reg.derivative/2;
    if(error_w>0 && reg.derivative>0 && projected>=(int32_t)reg.target-500){reg.phase=EFFECT_CAPTURE;return 0;}
    int32_t step;
    if(error_w>2000){reg.phase=EFFECT_START;step=100;}
    else if(error_w>1000){reg.phase=EFFECT_CAPTURE;step=50;}
    else if(error_w>0){reg.phase=EFFECT_CAPTURE;step=25;}
    else {reg.phase=EFFECT_CAPTURE;step=error_w< -2000?-100:error_w< -1000?-50:-25;}
    if(step>0 && step>500-(int32_t)reg.up_total)step=500-(int32_t)reg.up_total;
    int32_t next=(int32_t)flow+step;
    if(next>reg.cap)next=reg.cap;
    if(next<2000)next=2000;
    if(next==(int32_t)flow){reg.phase=EFFECT_LIMITED;reg.reason=step>0?EFFECT_TEMPERATURE_CAP:EFFECT_TEMPERATURE_FLOOR;if(step>0)reg.limit_latched=reg.reason;return 0;}
    reg.reason=EFFECT_OK;reg.pending=(uint16_t)next;reg.last_up_w=measured;
    return reg.pending;
}
int effect_pending_demand(void){return reg.pending?reg.pending_demand:0;}
/* Shared bounded startup/pause selection; callers retain admission policy. */
static uint16_t startup_target(const effect_measurement *m,uint16_t flow,unsigned kind,uint32_t t){
    int32_t next=flow;
    if(kind==1){next=m->supply_cC+50;if(next>3950)next=3950;if(next<2000)next=2000;}
    else if(!reg.lead_started && m->short_w>=0 && m->short_w<(int32_t)reg.target-150)next=4500;
    lead_point past,accel;history(m,t,&past,&accel);
    int32_t limit=thermal_ceiling(m->supply_cC,supply_rate(m->supply_cC,past,t));
    if(next>limit)next=limit;
    if(next!=flow){reg.pending=(uint16_t)next;reg.pending_demand=(uint8_t)kind;}
    return (uint16_t)next;
}
uint16_t effect_entry_demand(const effect_measurement *m,uint16_t flow,unsigned native_mode,uint32_t t){
    if(reg.cap<=4000)return flow;
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
    if(reg.cap>4000 && !reg.pending && m->quality==EF_SETTLING && m->pairs &&
       m->age_ms<15000u && (m->mode==2 || m->mode==7) && m->hz>0 && m->hz<255 &&
       m->supply_cC>=0 && m->supply_cC<=10000 &&
       reg.phase!=EFFECT_OFF && reg.phase!=EFFECT_RESTORING && reg.phase!=EFFECT_INVALID_FEEDBACK){
        uint16_t next=startup_target(m,flow,2,t);
        return next==flow?0:next;
    }
    /* Drop a boost promptly if the native compressor stops. */
    if(reg.cap>4000 && m->quality==EF_WAIT_NATIVE && m->hz==0 && flow>4000 &&
       !reg.pending && m->supply_cC>=0 && m->supply_cC<4000){
        int32_t mild=m->supply_cC+50;if(mild>3800)mild=3800;
        reg.pending=(uint16_t)(mild<2000?2000:mild);reg.pending_demand=1;return reg.pending;
    }
    /* Native start demand is not a power-error correction. Never force Hz/on. */
    if(m->quality!=EF_WAIT_NATIVE || m->hz!=0 || reg.pending || reg.limit_latched ||
       reg.phase==EFFECT_OFF || reg.phase==EFFECT_RESTORING || reg.phase==EFFECT_INVALID_FEEDBACK ||
       m->supply_cC<0 || m->supply_cC>10000 || t-reg.last_adjustment<60000u)return 0;
    int32_t desired=m->supply_cC+50; /*0.5C above fresh measured supply*/
    if(desired<=flow){reg.reason=EFFECT_OK;return 0;}
    if(flow>=reg.cap){reg.reason=reg.limit_latched=EFFECT_TEMPERATURE_CAP;return 0;}
    if(reg.cap<=4000 && reg.up_total>=500){reg.reason=reg.limit_latched=EFFECT_CUMULATIVE_CAP;return 0;}
    int32_t next=(int32_t)flow+100;
    if(next>desired)next=desired;
    if(next>reg.cap)next=reg.cap;
    if(reg.cap<=4000 && next>(int32_t)flow+500-reg.up_total)next=(int32_t)flow+500-reg.up_total;
    reg.pending=(uint16_t)next;reg.pending_demand=1;reg.reason=EFFECT_OK;return reg.pending;
}
void effect_discard_pending(void){reg.pending=0;reg.pending_demand=0;}
void effect_wait(unsigned quality,uint32_t t){
    if(reg.phase==EFFECT_OFF || reg.phase==EFFECT_RESTORING || reg.phase==EFFECT_INVALID_FEEDBACK)return;
    reg.phase=quality==EF_WAIT_NATIVE?EFFECT_WAIT_NATIVE:EFFECT_SETTLING;
    /* A native pause is not evidence that a running pump failed to respond. */
    reg.assess_up=0;
    if(reg.cap<=4000 || quality==EF_WAIT_NATIVE){reg.have_previous=0;reg.derivative=0;reg.lead_count=reg.lead_head=reg.lead_started=0;reg.fine_carry=0;reg.response_lead=0;reg.last_decision=t;}
}
void effect_verified(uint16_t flow,uint32_t t){
    if(reg.pending && flow==reg.pending){
        if(reg.pending_demand==2)reg.lead_started=1;
        reg.last_delta=(int16_t)((int32_t)flow-reg.verified);
        if(reg.last_delta>0){reg.up_total=(uint16_t)(reg.up_total+reg.last_delta);reg.assess_up=(uint8_t)!reg.pending_demand;}
        else reg.down_total=(uint16_t)(reg.down_total-reg.last_delta);
        ++reg.adjustments;reg.last_adjustment=t;
        /* Measured minimum interval starts at completed readback. */
        reg.last_decision=t;reg.pending=reg.pending_demand=0;
    }
    reg.verified=flow;
}
uint16_t effect_read(unsigned a,const effect_measurement *m,uint16_t flow,uint32_t t){
    int32_t value=0;
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
    case 344:return reg.up_total;case 345:return reg.down_total;case 346:return reg.unresponsive;
    case 347:return reg.pending;case 348:return (uint16_t)(int16_t)(reg.derivative>32767?32767:reg.derivative< -32768?-32768:reg.derivative);
    case 349:return reg.initial;case 350:return reg.boot_unknown;case 351:return 0;
    default:return 0;
    }
}
