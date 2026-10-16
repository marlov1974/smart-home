#include "effect_source_fixture.h"
#include "effect_feedback.h"
#include <assert.h>
#include <stdio.h>
static effect_measurement m;
static unsigned flow,last;
static void begin(unsigned target,unsigned hz,unsigned start){
 m=(effect_measurement){.instant_w=7000,.short_w=7000,.supply_cC=3300,.hz=hz,.ready=1,.quality=EF_READY};
 effect_begin(target,5500,0);effect_capture(start,0);flow=start;last=0;
}
static void tick(unsigned t,unsigned age){
 effect_test_sources(&m,t);effect_test_source(8,(tele_sample){m.hz,age,(uint16_t)(t/5000+1),TELE_VALID,0});
 unsigned n=effect_decide(&m,flow,t);
 if(n){if(n<flow){assert(flow-n<=100 && t-last>=60000);last=t;}
 flow=n;effect_verified(n,t);}
}
int main(void){
 begin(4000,60,3500);
 for(unsigned t=0;t<=1200000;t+=5000)tick(t,0);
 assert(flow==3200); /* far above goal: reaches actual-1C, no deeper */
 m.hz=38;m.instant_w=m.short_w=4000;unsigned before=flow;
 for(unsigned t=1205000;t<=1500000;t+=5000)tick(t,0);
 assert(flow>before && flow>=3350); /* catch goal, release braking */
 begin(2000,24,3250);
 for(unsigned t=0;t<=180000;t+=5000)tick(t,0);
 assert(flow<3350); /*24Hz is no longer an artificial minimum. */
 m.hz=20;before=flow;for(unsigned t=185000;t<=420000;t+=5000)tick(t,0);
 assert(flow==before && effect_read(322,&m,flow,420000)==EFFECT_MINIMUM_OUTPUT);
 /* Observed minimum output is a real limiter: do not add gas while measured
    power is already more than0.5kW above the requested output. */
 begin(4000,60,3400);
 for(unsigned t=0;t<=600000;t+=5000)tick(t,60000);
 assert(flow==3400); /* unusable Hz cannot authorize a negative delta */
 puts("PASS braking: -1C floor, 0.5/1C ordinary cuts, goal/minimum release and stale gating");
}
