/* Offline predictive-law scenarios; no device or transport. */
#include "effect.h"
#include "effect_feedback.h"
#include <assert.h>
#include <stdio.h>
static effect_measurement m;
static unsigned demand;
static void reset(unsigned power,unsigned hz,unsigned flow){
    effect_init();effect_begin(6000,5500,0);effect_capture((uint16_t)flow,0);demand=flow;
    m=(effect_measurement){.instant_w=(int)power,.short_w=(int)power,.supply_cC=3300,.hz=(uint16_t)hz,.ready=1,.quality=EF_READY,.pairs=4,.span_ms=60000};
}
static unsigned step(unsigned t){
    unsigned before=demand,n=effect_decide(&m,(uint16_t)demand,t);
    if(n){assert(n>=3000 && n<=5500);assert(n<=before+((m.short_w<5250 && (int)before-m.supply_cC<200)?100:50) || !t);assert(n>=before-100);demand=n;effect_verified((uint16_t)n,t);}
    return n;
}
int main(void){
    /* A rise that projects near the goal holds demand; a modest rise far
       below goal must not indefinitely mask a real power deficit. */
    reset(5700,42,4500);
    for(unsigned t=0;t<=120000;t+=5000){m.short_w=5700+(int)t/400;m.instant_w=m.short_w-150;assert(!step(t));}
    assert(demand==4500);

    /* At52Hz a35s lead alone is5900W, but45s more acceleration forecasts
       overshoot. The allowed1C reduction must happen before that overshoot. */
    reset(4800,42,4500);
    for(unsigned t=0;t<=60000;t+=5000){m.hz=t<30000?42:52;unsigned n=step(t);if(t==60000)assert(n==4400);}
    assert(demand==4400);

    /* The recentHz decline wins over a still-positive older60s slope and
       its future forecast: do not continue braking a falling plant. */
    reset(5500,40,4450);assert(effect_decide(&m,4450,0)==4500);demand=4500;effect_verified(4500,20000);
    for(unsigned t=20000;t<=80000;t+=5000){
        m.hz=t<30000?40:t<70000?62:60;
        unsigned before=demand,n=step(t);if(t==80000)assert(!n && demand==before);
    }

    /* A largeHz step must not brake while CURRENT lead remains far belowgoal,
       even when its added forecast becomes much larger. */
    reset(2800,40,4500);
    for(unsigned t=0;t<=60000;t+=5000){m.hz=t<30000?40:50;unsigned before=demand;step(t);assert(demand>=before);}

    /* A true stationary small error can still use bounded fine correction. */
    reset(5800,50,4500);
    for(unsigned t=0;t<=180000;t+=5000)step(t);
    assert(demand>4500 && demand<4600);

    /* High power plus rapid fallingHz must never inherit the larger DOWN
       bound for an upward correction. Up remains at most0.5C. */
    reset(13000,80,4500);
    for(unsigned t=0;t<=60000;t+=5000){m.hz=t<30000?80:50;unsigned n=step(t);if(t==60000)assert(n==4550);}

    /* Flat high supply still applies negative feedback: a static39.5C
       request previously allowed a persistent offset to reach40.5C. */
    const int hot_supply[]={3900,3950,4000,4050,10000};
    const unsigned hot_target[]={3900,3850,3800,3750,3000};
    for(unsigned i=0;i<5;++i){
        reset(5800,50,4500);m.supply_cC=hot_supply[i];
        assert(effect_decide(&m,4500,0)==hot_target[i]);
        assert(effect_read(321,&m,4500,0)==EFFECT_LIMITED);
    }

    /* A rising30s forecast may only lower the signed ceiling. It must not
       overwrite an already-lower correction with a fixed39C request. */
    reset(5800,50,4500);m.supply_cC=3900;
    unsigned n=effect_decide(&m,4500,0);assert(n==3900);effect_verified((uint16_t)n,0);
    m.supply_cC=4000;n=effect_decide(&m,3900,30000);assert(n>3000 && n<3800);

    /* Cooling releases the cap, not stored actuator demand. Weak-demand recovery is at most1C per decision; other increases remain
       at most0.5C. Startup must not replay its45C feed-forward. */
    reset(3000,50,4500);m.supply_cC=3950;
    n=effect_decide(&m,4500,0);assert(n==3850);demand=n;effect_verified((uint16_t)n,0);
    m.supply_cC=3800;
    for(unsigned t=5000;t<=120000;t+=5000)step(t);
    assert(demand>3850 && demand<=4200);
    /* Recent acceleration survives the first flat-Hz decision. Old code
       added gas here once its instantaneous rate forecast went flat. */
    reset(5500,32,4500);
    unsigned at60=0;
    for(unsigned t=0;t<=90000;t+=5000){
        m.hz=t<30000?32:42;step(t);
        if(t==60000)at60=demand;
    }
    assert(demand<=at60);
    /* Memory decays; it must not keep braking a permanently flat plant. */
    unsigned at90=demand;
    for(unsigned t=95000;t<=300000;t+=5000)step(t);
    assert(demand>at90);

    /* After limiting, weak demand gets a bounded1C recovery step. A modest
       subsequent300..400W/min rise must not block correction while far low. */
    reset(6000,40,3900);m.supply_cC=3800;
    for(unsigned t=0;t<=60000;t+=5000){if(t>=30000)m.short_w=4800;step(t);}
    assert(demand==4000);
    unsigned low=demand;
    for(unsigned t=65000;t<=90000;t+=5000){m.short_w=5000;step(t);}
    assert(demand>low);
    /* No recovery on stale feedback and no stored request after clipping. */
    m.age_ms=20000;low=demand;
    for(unsigned t=95000;t<=150000;t+=5000)assert(!step(t));
    assert(demand==low);
    m.age_ms=0;m.supply_cC=4000;
    n=effect_decide(&m,(uint16_t)demand,155000);assert(n<=3800);
    /* A fresh mission does not inherit earlier acceleration. */
    reset(6000,42,3900);m.supply_cC=3800;
    for(unsigned t=0;t<=120000;t+=5000)assert(!step(t));

    puts("PASS predictive law: rising-power/flat-Hz hold, earlier bounded1C brake, current-lead falling/far-below guards, persistent fine correction, thermal priority");
}
