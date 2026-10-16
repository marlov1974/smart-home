/* P0080: behavioral qualification of the thermal demand envelope.
 * Synthetic measured histories are not a physical heat-pump simulation. */
#include "effect_source_fixture.h"
#include "effect_feedback.h"
#include <assert.h>
#include <stdio.h>

static effect_measurement m;
static unsigned demand,limit;
static void begin(unsigned cap,unsigned initial,int supply){
    m=(effect_measurement){.instant_w=4000,.short_w=4000,.slow_w=4000,
        .supply_cC=supply,.span_ms=60000,.quality=EF_READY,.pairs=12,
        .mode=2,.hz=40,.ready=1};
    demand=initial;limit=cap;
    effect_begin(6000,(uint16_t)cap,0);effect_capture((uint16_t)initial,0);
    effect_test_source(3,(tele_sample){0});effect_test_source(8,(tele_sample){0});
}
static unsigned decide(unsigned t,unsigned water_age,unsigned pair_age,int samples){
    m.age_ms=pair_age;
    if(samples){
        uint16_t gen=samples==2?1:(uint16_t)(t/5000u+1);
        effect_test_source(3,(tele_sample){m.supply_cC,water_age,gen,TELE_VALID,0});
        effect_test_source(8,(tele_sample){m.hz,0,gen,TELE_VALID,0});
    }
    unsigned before=demand,next=effect_decide(&m,(uint16_t)demand,t);
    if(next){
        assert(next<=limit);
        demand=next;effect_verified((uint16_t)next,t);
    }
    return before;
}
static unsigned flat(unsigned cap){
    begin(cap,cap<4200?cap:4200,3800);
    for(unsigned t=0;t<=300000;t+=5000){
        unsigned before=decide(t,0,0,1);
        /* Releasing a thermal limit is an ordinary correction, not restart. */
        if(t && demand>before)assert(demand-before<=200);
    }
    return demand;
}
static unsigned rising(unsigned source_age){
    begin(5500,4200,3700);
    unsigned at_38=0;
    for(unsigned t=0;t<=90000;t+=5000){
        m.supply_cC=3700+(int)(t/500); /*1.2C/min, ends38.8C.*/
        unsigned before=decide(t,source_age,0,1);
        if(m.supply_cC>=3800){
            if(!at_38)at_38=before;
            assert(demand<=at_38); /* Enough rise to approach the ceiling. */
        }
    }
    return demand;
}
static unsigned age_sensitive_rise(unsigned age){
    begin(5500,4200,3700);m.instant_w=m.short_w=m.slow_w=5500;
    for(unsigned t=0;t<=300000;t+=5000){
        m.supply_cC=3700+(int)(t/1200); /*0.5C/min, ending39.5C.*/
        decide(t,age,0,1);
    }
    return demand;
}
static void insufficient_history(void){
    for(unsigned samples=0;samples<=2;samples+=2){
        begin(5500,4500,3800);
        for(unsigned t=0;t<=360000;t+=5000){
            unsigned before=decide(t,0,0,(int)samples);
            /* Unknown trend uses the fallback goal, reached gently. */
            assert(demand<=before && before-demand<=100);
            if(t>=360000)assert(demand<=4200);
        }
    }
}
static void hot_temperature(void){
    for(unsigned supply=3900;supply<=5000;supply+=50){
        begin(5500,5500,(int)supply);unsigned last_change=0;
        for(unsigned t=0;t<=2400000;t+=5000){
            unsigned before=decide(t,0,0,1);
            assert(demand>=supply-100 && demand<=before);
            if(demand<before){
                assert(before-demand<=100);
                if(t)assert(t-last_change>=30000);
                last_change=t;
            }
        }
        assert(demand==(supply<3950?7800-supply:supply-100)); /* Converges gently while bounded negative margin. */
    }
    /* The margin must not chase a hotter measurement upward. */
    begin(5500,4000,4050);
    for(unsigned t=0;t<=120000;t+=5000){decide(t,0,0,1);assert(demand<=4000 && demand>=3950);}
    begin(3900,3900,4000);
    for(unsigned t=0;t<=120000;t+=5000){decide(t,0,0,1);assert(demand==3900);}
}
static void cooling_release(void){
    begin(5500,4500,3950);
    for(unsigned t=0;t<=900000;t+=5000)decide(t,0,0,1);
    unsigned protective=demand;
    assert(protective==3850);
    m.supply_cC=3800;
    for(unsigned t=905000;t<=1500000;t+=5000){
        unsigned before=decide(t,0,0,1);
        if(demand>before)assert(demand-before<=200);
    }
    assert(demand>4200 && demand>protective);
}
static void warmup_cadence(void){
    begin(5500,3050,3300);m.hz=26;m.ready=0;m.quality=EF_SETTLING;
    effect_test_sources(&m,0);
    demand=effect_pause_demand(&m,3050,0);assert(demand==4300);
    effect_verified((uint16_t)demand,0);m.supply_cC=4000;
    unsigned last_change=0;
    for(unsigned t=1000;t<=150000;t+=1000){
        effect_test_sources(&m,t);
        unsigned next=effect_pause_demand(&m,(uint16_t)demand,t);
        if(next){
            assert(next<demand && demand-next<=50 && next>=4050);
            assert(t-last_change>=60000);last_change=t;
            demand=next;effect_verified((uint16_t)next,t);
        }
    }
    assert(demand<4300); /* Repeated first-pair feedback still tapers. */
}
static void stale_source_startup(void){
    for(unsigned mask=1;mask<=3;++mask){
        begin(5500,3050,3300);
        effect_test_source(3,(tele_sample){3300,mask&1?20000:0,1,TELE_VALID,0});
        effect_test_source(8,(tele_sample){40,mask&2?20000:0,1,TELE_VALID,0});
        /* Fresh calculated-power feedback cannot refresh an old source. */
        decide(0,0,0,0);assert(demand<=3050);
        /* The atomic entry and first-pair SETTLING paths use the same gate. */
        begin(5500,3050,3300);
        effect_test_source(3,(tele_sample){3300,mask&1?20000:0,1,TELE_VALID,0});
        effect_test_source(8,(tele_sample){40,mask&2?20000:0,1,TELE_VALID,0});
        assert(effect_entry_demand(&m,3050,2,0)<=3050);
        effect_discard_pending();m.ready=0;m.quality=EF_SETTLING;
        assert(effect_pause_demand(&m,3050,0)<=3050);
    }
}
static void aging_holds(void){
    for(unsigned age=15000;age<60000;age+=5000){
        begin(5500,4200,3800);
        for(unsigned t=0;t<=120000;t+=5000)decide(t,0,0,1);
        unsigned old=demand,last_up=0;
        for(unsigned t=125000;t<=240000;t+=5000){
            unsigned before=decide(t,0,age,1);
            if(demand>before){assert(demand-before<=50);assert(!last_up || t-last_up>=60000);last_up=t;}
        }
        assert(demand<=old+100); /* Usable to60s, but never on the quick path. */
    }
    /* Below the normal30C floor, aged feedback still moves only0.5C/minute. */
    begin(5500,2500,2900);
    unsigned last_up=0;
    for(unsigned t=0;t<=120000;t+=5000){unsigned before=decide(t,0,20000,1);
        if(demand>before){assert(demand-before<=50);assert(!last_up || t-last_up>=60000);last_up=t;}}
    assert(demand<=2600);
}
int main(void){
    unsigned steady=flat(5500);
    assert(steady>4200);
    unsigned fresh=rising(0),aged=rising(10000);
    /* Two-loop flat tracking now reduces surplus delta even below power goal.
       Compare rising response with its own4500 startup, not another mission. */
    assert(fresh<4500 && aged<=fresh);
    assert(age_sensitive_rise(10000)<=age_sensitive_rise(0));
    insufficient_history();hot_temperature();cooling_release();warmup_cadence();aging_holds();stale_source_startup();
    for(unsigned cap=2500;cap<=4500;cap+=500)assert(flat(cap)<=cap);
    printf("PASS adaptive thermal envelope: stable38C demand%u, rising demand%u, aged rising%u; conservative unknown, hot down-step/cadence and positive margin, bounded release, aging hold and configured caps\n",steady,fresh,aged);
    return 0;
}
