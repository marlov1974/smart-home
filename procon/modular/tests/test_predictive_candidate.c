/* Two-loop response scenarios replace the retired acceleration predictor. */
#include "effect.h"
#include "effect_feedback.h"
#include <assert.h>
#include <stdio.h>
#define EFFECT_AUTO_SOURCES
#include "effect_source_fixture.h"
static effect_measurement m;
static unsigned demand;
static void reset(unsigned power,unsigned hz,unsigned flow){
    effect_init();effect_begin(6000,5500,0);effect_capture((uint16_t)flow,0);demand=flow;
    m=(effect_measurement){.instant_w=(int)power,.short_w=(int)power,.supply_cC=3300,.hz=(uint16_t)hz,.ready=1,.quality=EF_READY,.pairs=4,.span_ms=60000};
}
static void step(unsigned t){
    unsigned before=demand,n=effect_decide(&m,(uint16_t)demand,t);
    if(n){assert(n>=3000 && n<=5500);assert(n<=before+200 || !t);assert(n>=before-100);demand=n;effect_verified((uint16_t)n,t);}
}
int main(void){
    reset(6000,52,4500);step(0);
    for(unsigned t=5000;t<=1500000;t+=5000){m.hz=t<30000?52:51;step(t);assert(demand<=4500 && demand>=3500);}
    assert(demand==3500);assert(effect_read(319,&m,demand,300000)==0); /* no compensation for a lone1Hz */

    reset(6000,52,4500);step(0);m.hz=66;step(60000);assert(demand==4400);
    m.hz=52;step(90000);assert(demand==4400 && (effect_read(315,&m,demand,90000)&2));
    assert(effect_read(316,&m,demand,90000)==120);
    step(110000);assert(demand==4400);
    m.supply_cC=4000;step(120000);assert(demand==4300); /* thermal priority beats freeze */
    assert(effect_read(321,&m,demand,120000)==EFFECT_LIMITED);
    assert(!effect_read(316,&m,demand,220000)); /* no unsigned timer underflow */

    reset(3000,30,3050);step(0);assert(demand==4300);
    m.hz=50;step(60000);assert(demand==4250); /* anticipate slow power response */
    m.hz=49;step(90000);assert(demand==4250); /* falling target doesn't cause gas */
    effect_retarget(5000,5500,95000);
    /* Retarget transfers the bounded per-device correction instead of erasing
       it every time a 30-second supervisor changes the watt request. */
    assert(effect_read(319,&m,demand,95000)==100);
    assert(effect_read(309,&m,demand,95000)==4611 && effect_read(323,&m,demand,95000)==5000);
    /* A hot, power-short plant is capability-limited.  It must not teach the
       outer loop an ever-higher goal while the temperature envelope is active. */
    int retained_trim=(int16_t)effect_read(319,&m,demand,95000);
    m.supply_cC=4000;m.instant_w=m.short_w=3000;
    for(unsigned t=125000;t<=245000;t+=30000)step(t);
    assert((int16_t)effect_read(319,&m,demand,245000)==retained_trim);

    reset(6000,52,4500);step(0);m.age_ms=59000;m.hz=70;
    step(60000);assert(demand==4400); /* usable<60s keeps bounded control */
    m.supply_cC=4000;step(110000);assert(demand==4300);
    assert(effect_read(321,&m,demand,90000)==EFFECT_LIMITED);
    /* A genuine unchanged target below goal cannot leave us permanently on
       the same insufficient delta. Retain gas and add only0.5C after90s. */
    reset(5000,42,3800);step(0);unsigned initial=demand;
    for(unsigned t=5000;t<=300000;t+=5000)step(t);
    assert(demand>initial && demand<=initial+150);
    /* All sources younger than60s remain usable, but only fresh<15s data gets
       the aggressive path. Old-but-usable data adds at most0.5C per minute. */
    reset(6000,30,3500);step(0);m.instant_w=m.short_w=3000;m.age_ms=20000;
    step(30000);assert(demand==3500);step(60000);assert(demand==3550);
    assert(effect_read(322,&m,demand,60000)!=EFFECT_SOURCE_STALE);
    m.age_ms=60000;step(90000);assert(demand==3550);
    assert(effect_read(322,&m,demand,90000)==EFFECT_SOURCE_STALE);

    /* A verified flow increase is not stacked while A3/17 is unchanged inside
       its native minute.  Expiry resumes best effort without a fault. */
    reset(6000,30,3500);step(0);m.instant_w=m.short_w=3000;step(30000);
    unsigned first=demand;assert(first>3500);
    step(60000);assert(demand==first);
    assert(effect_read(322,&m,demand,60000)==EFFECT_RESPONSE_PENDING);
    assert(effect_read(315,&m,demand,60000)&EFFECT_FLAG_RESPONSE_WAIT);
    step(90000);assert(demand>first);

    /* A falling native target is progress, but not a reason to stop a bounded
       reduction while it remains more than10Hz above our goal. */
    reset(8000,60,3500);effect_retarget(4000,5500,0);step(0);
    m.hz=58;step(60000);assert(demand==3400);
    m.hz=56;step(120000);assert(demand==3300);

    /* A supervisor-requested reversal starts a new direction and cannot be
       classified as the plant's rapid alternating oscillation. */
    reset(6000,40,3500);step(0);m.hz=50;step(60000);
    effect_retarget(3000,5500,65000);m.hz=40;step(90000);
    assert(!(effect_read(315,&m,demand,90000)&EFFECT_FLAG_OSCILLATION));

    /* A3/16 actual and A3/17 requested frequency have independent values and
       completion generations. Only a new target generation drives this loop. */
    reset(6000,50,3500);effect_test_a3(90,30,1,1);step(0);
    m.instant_w=m.short_w=3000;effect_test_a3(91,30,2,1);step(30000);assert(demand==3500);
    effect_test_a3(91,30,2,2);step(60000);assert(demand>3500);
    assert(effect_read(317,&m,demand,60000)==91 && effect_read(318,&m,demand,60000)==30);
    effect_test_a3_mirror();

    /* Requested-flow caps are distinct from the physical-temperature envelope
       and approach a newly lower cap with the ordinary bounded down slew. */
    reset(6000,52,5000);step(0);effect_retarget(6000,3000,1);
    step(30000);assert(demand==5000 && effect_read(322,&m,demand,30000)==EFFECT_REQUEST_CAP);
    assert(!(effect_read(315,&m,demand,30000)&EFFECT_FLAG_THERMAL));
    step(60000);assert(demand==4950 && effect_read(322,&m,demand,60000)==EFFECT_REQUEST_CAP);
    assert(effect_read(315,&m,demand,60000)&EFFECT_FLAG_REQUEST_CAP);
    step(90000);assert(demand==4950);step(120000);assert(demand==4900);
    reset(6000,52,5000);m.supply_cC=EFFECT_THERMAL_APPROACH_CC+50;step(0);step(30000);
    assert(demand==4900 && effect_read(322,&m,demand,30000)==EFFECT_TEMPERATURE_CAP);

    /* Startup and native-pause helpers obey the same request cap without an
       abrupt jump when an existing request is already above that cap. */
    effect_init();effect_begin(6000,3000,0);effect_capture(5000,0);
    m=(effect_measurement){.instant_w=3000,.short_w=3000,.supply_cC=3300,.hz=30,
        .ready=1,.quality=EF_READY,.mode=2,.pairs=4};
    effect_test_sources(&m,60000);unsigned cap_step=effect_entry_demand(&m,5000,2,60000);
    assert(cap_step==4950);effect_verified((uint16_t)cap_step,60000);
    effect_init();effect_begin(6000,3000,0);effect_capture(2900,0);
    effect_test_sources(&m,60000);cap_step=effect_entry_demand(&m,2900,2,60000);
    assert(cap_step>2900 && cap_step<=3000);
    effect_init();effect_begin(6000,3000,0);effect_capture(4000,0);
    m.quality=EF_WAIT_NATIVE;m.ready=0;m.hz=0;
    cap_step=effect_pause_demand(&m,4000,60000);assert(cap_step==3950);
    assert(effect_read(322,&m,4000,60000)==EFFECT_REQUEST_CAP);
    effect_verified((uint16_t)cap_step,60000);
    cap_step=effect_pause_demand(&m,3950,120000);assert(cap_step==3900);

    /* Reversible limiter diagnostics distinguish cap/minimum/tracking states. */
    reset(6000,30,5500);step(0);m.instant_w=m.short_w=3000;step(30000);
    assert(effect_read(321,&m,demand,30000)==EFFECT_LIMITED);
    assert(effect_read(322,&m,demand,30000)==EFFECT_REQUEST_CAP);
    assert(effect_read(315,&m,demand,30000)&EFFECT_FLAG_REQUEST_CAP);
    effect_init();effect_begin(2000,5500,0);effect_capture(3300,0);demand=3300;
    m=(effect_measurement){.instant_w=3500,.short_w=3500,.supply_cC=3300,.hz=20,.ready=1,.quality=EF_READY};
    for(unsigned t=0;t<=150000;t+=30000){step(t);assert(demand==3300);
        assert(effect_read(322,&m,demand,t)==EFFECT_MINIMUM_OUTPUT);
        assert(effect_read(315,&m,demand,t)&EFFECT_FLAG_MINIMUM_OUTPUT);}
    assert((int16_t)effect_read(319,&m,demand,150000)==0);
    m.instant_w=m.short_w=2400;step(180000);assert(demand==3350);
    assert(effect_read(322,&m,demand,180000)!=EFFECT_MINIMUM_OUTPUT);
    /* Invalid power sentinels are legal while diagnostics remain readable. */
    m.short_w=INT32_MIN;assert(!(effect_read(315,&m,demand,180000)&(EFFECT_FLAG_MINIMUM_OUTPUT|EFFECT_FLAG_TRACKING)));
    m.short_w=-1;assert(!(effect_read(315,&m,demand,180000)&(EFFECT_FLAG_MINIMUM_OUTPUT|EFFECT_FLAG_TRACKING)));
    reset(6000,52,3500);step(0);
    assert(effect_read(308,&m,demand,0)==4);
    assert(effect_read(315,&m,demand,0)&EFFECT_FLAG_TRACKING);
    puts("PASS two-loop v3: retained retarget trim, response dwell, asymmetric braking, planned reversal, reversible limiter/tracking diagnostics");
}
