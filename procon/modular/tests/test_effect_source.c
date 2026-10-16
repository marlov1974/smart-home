#include "effect_source_fixture.h"
#include "effect_feedback.h"
#include <assert.h>
#include <stdio.h>
static void source(unsigned i,int v,unsigned age,unsigned gen){effect_test_source(i,(tele_sample){v,age,(uint16_t)gen,TELE_VALID,0});}
static unsigned replay(unsigned poll,uint32_t base){
 effect_measurement m={.instant_w=4800,.short_w=4800,.supply_cC=3300,.hz=42,.ready=1,.quality=EF_READY};
 effect_begin(6000,5500,base);effect_capture(4500,base);unsigned demand=4500;
 for(unsigned t=0;t<=90000;t+=poll){
  unsigned ha=t/10000*10000,wa=t/15000*15000;m.hz=ha<30000?42:52;
  source(8,m.hz,t-ha,65533+ha/10000);source(3,3300,t-wa,wa/15000);
  unsigned n=effect_decide(&m,demand,base+t);if(n){demand=n;effect_verified(n,base+t);}
 }
 assert(demand<4500);return demand;
}
int main(void){
 unsigned slow=replay(5000,0),fast=replay(1000,0);assert(slow==fast);
 assert(replay(5000,UINT32_MAX-45000u)==slow);
 effect_measurement m={.instant_w=5840,.short_w=5840,.supply_cC=3300,.hz=50,.ready=1,.quality=EF_READY};
 effect_begin(6000,5500,0);effect_capture(4500,0);source(8,50,0,1);source(3,3300,0,1);
 /* Even a bogus age reset cannot make repeated generation1 into new history. */
 for(unsigned t=0;t<=180000;t+=5000)assert(!effect_decide(&m,4500,t));
 effect_begin(6000,5500,0);effect_capture(4500,0);
 unsigned old=4500,last=0;
 for(unsigned t=0;t<=120000;t+=5000){
  effect_test_sources(&m,t);source(8,50,20000,t/5000);unsigned n=effect_decide(&m,old,t);
  if(n){assert(n<=old && t-last>=60000);old=n;last=t;effect_verified(n,t);}
 }
 assert(old<4500); /*20s-old coherent sources remain usable, only conservatively*/
 /* A newly hot supply still causes gradual reduction, subject to the same30s
    thermal interval, independently of the prior old-source scenario. */
 effect_begin(6000,5500,120000);effect_capture(4500,120000);m.supply_cC=4000;effect_test_sources(&m,125000);
 assert(!effect_decide(&m,4500,125000));
    effect_test_sources(&m,155000);assert(effect_decide(&m,4500,155000)==4400);
    effect_verified(4400,155000);
    assert(effect_read(321,&m,4400,155000)!=EFFECT_INVALID_FEEDBACK);
 for(unsigned cap=2000;cap<=5500;cap+=500){
  effect_begin(6000,cap,0);effect_capture(cap,0);m.supply_cC=2900;m.short_w=2000;
  unsigned n=effect_decide(&m,cap,0);assert(!n || n<=cap);
 }
 /* New inner loop deliberately tapers excessive delta as the frequency goal
    approaches, even before the lagged heat estimate reaches6kW. */
 m=(effect_measurement){.instant_w=6000,.short_w=6000,.supply_cC=3750,.hz=40,.ready=1,.quality=EF_READY};
 effect_begin(6000,5500,0);effect_capture(4200,0);unsigned demand=4200;
 for(unsigned t=0;t<=120000;t+=5000){
  /* Keep power near target so the outer trim does not demand renewed gas. */
  m.hz=t<30000?40:50;effect_test_sources(&m,t);
  unsigned n=effect_decide(&m,demand,t);
  if(n){assert(n>=demand-100 && n<=demand+50);demand=n;effect_verified(n,t);}
 }
 assert(demand<4200 && effect_read(321,&m,demand,120000)!=EFFECT_INVALID_FEEDBACK);
 puts("PASS source-aware EFFECT: polling invariance, timestamp/generation wrap, asynchronous/stale Hz, duplicate rejection, early thermal braking, caps");
}
