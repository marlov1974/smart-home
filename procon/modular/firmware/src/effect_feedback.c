/* P0076: no controls; accept independent, coherent heating observations only. */
#include "effect_feedback.h"
#include "telemetry.h"
#define RING_SIZE 64u
#define SAMPLE_MIN_MS 4000u
#define MAX_AGE_MS 60000u
#define SHORT_MS 60000u
#define SLOW_MS 180000u
#define MIN_SPAN_MS 20000u
typedef struct { int32_t watts; uint32_t at; } point;
static point ring[RING_SIZE];
static effect_feedback_state result;
static unsigned head,count;
static uint32_t last_sample_at,last_poll;
static uint16_t consumed_temp,consumed_flow;
static uint8_t consumed,ever_sample,polled,resuming,running;
static uint32_t running_since;

int effect_feedback_hard_invalid(unsigned q){
    return q==EF_STALE || q==EF_INVALID || q==EF_ZEROFLOW || q==EF_DHW || q==EF_LINKLOSS;
}
static void empty(void){
    head=count=0;
    result.instant_w=result.short_w=result.slow_w=INT32_MIN;
    result.derivative_w_per_min=0;
    result.short_count=result.slow_count=0;
    result.short_span_ms=result.slow_span_ms=0;
    result.ready=0;
}
void effect_feedback_init(void){
    result=(effect_feedback_state){0};
    empty();result.quality=EF_WARMUP;result.last_age_ms=UINT32_MAX;
    last_sample_at=last_poll=0;consumed_temp=consumed_flow=0;consumed=ever_sample=polled=resuming=running=0;running_since=0;
    for(unsigned i=0;i<RING_SIZE;++i)ring[i]=(point){0};
}
static void reject(unsigned quality,const tele_sample *temp,const tele_sample *flow){
    empty();result.quality=(uint8_t)quality;
    /* A recovered mode cannot reuse a pair observed while heat was invalid. */
    consumed_temp=temp->generation;consumed_flow=flow->generation;consumed=1;
}
static void windows(uint32_t now){
    int64_t short_sum=0,slow_sum=0;
    unsigned ns=0,nl=0;
    uint32_t short_old=0,short_new=UINT32_MAX,slow_old=0,slow_new=UINT32_MAX;
    int32_t oldest_w=0,newest_w=0;
    while(count && now-ring[head].at>SLOW_MS){head=(head+1u)%RING_SIZE;--count;}
    for(unsigned n=0;n<count;++n){
        point p=ring[(head+n)%RING_SIZE];uint32_t age=now-p.at;
        if(age>SLOW_MS)continue;
        slow_sum+=p.watts;++nl;
        if(age>slow_old)slow_old=age;
        if(age<slow_new)slow_new=age;
        if(age<=SHORT_MS){
            short_sum+=p.watts;++ns;
            if(age>=short_old){short_old=age;oldest_w=p.watts;}
            if(age<=short_new){short_new=age;newest_w=p.watts;}
        }
    }
    result.short_count=(uint16_t)ns;result.slow_count=(uint16_t)nl;
    result.short_span_ms=ns?short_old-short_new:0;
    result.slow_span_ms=nl?slow_old-slow_new:0;
    result.short_w=ns?(int32_t)(short_sum/(int64_t)ns):INT32_MIN;
    result.slow_w=nl?(int32_t)(slow_sum/(int64_t)nl):INT32_MIN;
    /* Diagnostic endpoint slope, not an extra control input or precision claim. */
    result.derivative_w_per_min=result.short_span_ms>=MIN_SPAN_MS?
        (int32_t)(((int64_t)newest_w-oldest_w)*60000/(int64_t)result.short_span_ms):0;
}
static void pending(void){result.quality=resuming?EF_SETTLING:EF_PENDING;result.ready=0;result.instant_w=INT32_MIN;}
void effect_feedback_tick(uint32_t now){
    /* Telemetry is serviced in the same foreground loop; never duplicate its ms. */
    if(polled && now==last_poll)return;
    last_poll=now;polled=1;
    tele_sample temp,ret,flow,power,mode,hz;
    (void)tele_snapshot(3,&temp);(void)tele_snapshot(4,&ret);
    (void)tele_snapshot(8,&hz);(void)tele_snapshot(6,&flow);(void)tele_snapshot(7,&power);(void)tele_snapshot(18,&mode);
    result.last_age_ms=ever_sample?now-last_sample_at:UINT32_MAX;
    windows(now);
    if(temp.link_lost){reject(EF_LINKLOSS,&temp,&flow);return;}
    const tele_sample *sources[]={&temp,&ret,&flow,&mode,&hz};
    for(unsigned i=0;i<5;++i){
        if(sources[i]->status==TELE_NEVER){
            empty();result.quality=EF_WARMUP;return;
        }
        if(sources[i]->status==TELE_STALE || sources[i]->age_ms>=MAX_AGE_MS){reject(EF_STALE,&temp,&flow);return;}
        if(sources[i]->status!=TELE_VALID){reject(EF_INVALID,&temp,&flow);return;}
    }
    if(hz.value==255){reject(EF_INVALID,&temp,&flow);return;}
    if(mode.value==0 || ((mode.value==2 || mode.value==7) && hz.value==0)){
        reject(EF_WAIT_NATIVE,&temp,&flow);resuming=1;running=0;return;
    }
    if(mode.value!=2 && mode.value!=7){
        reject(mode.value==1 || mode.value==6?EF_DHW:EF_INVALID,&temp,&flow);return;
    }
    if(resuming && !running){running=1;running_since=now;}
    /* GET04 may announce restart before GET0C/14/26 replace cached idle data.
       Wait for that fresh pair; do not diagnose old zero flow as a live fault. */
    uint32_t older=temp.age_ms>flow.age_ms?temp.age_ms:flow.age_ms;
    uint32_t newer=temp.age_ms<flow.age_ms?temp.age_ms:flow.age_ms;
    if(resuming && (flow.age_ms>hz.age_ms || temp.age_ms>hz.age_ms ||
                   mode.age_ms>newer || older-newer>2000u)){pending();return;}
    if(flow.value<=0){reject(EF_ZEROFLOW,&temp,&flow);return;}
    if(temp.value<ret.value || temp.generation!=ret.generation || temp.age_ms!=ret.age_ms){
        reject(EF_INVALID,&temp,&flow);return;
    }
    if(count && result.last_age_ms>=MAX_AGE_MS){reject(EF_STALE,&temp,&flow);return;}
    /* GET26 follows GET0C/14 in FAST. A prior heating mode cannot bless a new pair. */
    if(mode.age_ms>newer || older-newer>2000u){pending();return;}
    if(power.status!=TELE_VALID || power.value<0){reject(EF_INVALID,&temp,&flow);return;}
    uint8_t new_temp=!consumed || temp.generation!=consumed_temp;
    uint8_t new_flow=!consumed || flow.generation!=consumed_flow;
    if(new_temp!=new_flow){pending();return;}
    if(new_temp){
        uint32_t sampled_at=now-older;
        if(ever_sample && sampled_at-last_sample_at<SAMPLE_MIN_MS){pending();return;}
        if(count==RING_SIZE){head=(head+1u)%RING_SIZE;--count;}
        ring[(head+count)%RING_SIZE]=(point){power.value,sampled_at};++count;
        last_sample_at=sampled_at;ever_sample=consumed=1;
        result.temp_gen=temp.generation;result.flow_gen=flow.generation;
        consumed_temp=temp.generation;consumed_flow=flow.generation;
        ++result.accepted_count;result.last_age_ms=older;
        windows(now);
    }
    result.instant_w=power.value;
    result.ready=(uint8_t)(result.short_count>=3 && result.short_span_ms>=MIN_SPAN_MS && result.last_age_ms<MAX_AGE_MS);
    if(resuming){
        if(now-running_since<60000u || !result.ready){result.ready=0;result.quality=EF_SETTLING;return;}
        resuming=0;
    }
    result.quality=result.ready?EF_READY:EF_WARMUP;
}
const effect_feedback_state *effect_feedback_get(void){return &result;}
