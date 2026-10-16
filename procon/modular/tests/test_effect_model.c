/* Synthetic identification data; these are numerical tests, not a plant model. */
#include "effect_model.h"
#include "telemetry.h"
#include <assert.h>
#include <stdio.h>
static tele_sample samples[20];
static unsigned hz=50,hgen,hage,now;
int tele_snapshot(unsigned i,tele_sample *out){if(i>=20)return 0;*out=samples[i];return 1;}
uint16_t svc_read(unsigned a){switch(a){case 372:return hz;case 373:case 377:return 1;case 374:return hage;case 376:return hgen;default:return 0;}}
static void setup(void){
 effect_model_reset();now=hage=hgen=0;hz=50;
 for(unsigned i=0;i<20;++i)samples[i]=(tele_sample){0,0,0,TELE_VALID,0};
 samples[0].value=400;samples[3].value=3500;samples[4].value=3000;
 samples[6].value=1900;samples[7].value=5660;samples[18].value=2;
}
static void window(unsigned watts,unsigned frequency,int enabled){
 hz=frequency;samples[7].value=(int)watts;
 for(unsigned i=0;i<13;++i){
  for(unsigned j=0;j<20;++j)++samples[j].generation;
  hgen=now/40000;effect_model_tick(now,enabled);now+=10000;
 }
}
int main(void){
 setup();assert(effect_model_target(6000)==5251 && effect_model_target(5000)==4511);
 assert(effect_model_target(0)==2000 && effect_model_target(20000)==10300);
 window(6660,50,1);assert(effect_model_bias()==-990 && effect_model_updates(0)==1);
 effect_model_break();assert(effect_model_bias()==-990);
 window(10000,50,0);assert(effect_model_updates(0)==1); /* inhibited */

 setup();window(6000,50,1);window(9000,70,1);assert(!effect_model_updates(1));
 window(6000,50,1);assert(effect_model_updates(1)==1);
 assert(effect_model_gain()==1357 && effect_model_bias()==-1007); /* pivot preserved */

 setup();window(6000,50,1);samples[0].value=650;window(9000,70,1);
 samples[0].value=400;window(6000,50,1);assert(!effect_model_updates(1));
 for(unsigned field=0;field<5;++field){
  setup();if(field==0)samples[19].value=1; /* heater */
  if(field==1)samples[18].value=1; /* DHW */
  if(field==2)hage=60;
  if(field==3)samples[3].age_ms=15000;
  if(field==4)samples[6].age_ms=3000; /* skew */
  window(9000,50,1);assert(!effect_model_updates(0));
 }
 setup();
 for(unsigned t=0;t<300000;t+=1000)effect_model_tick(t,1);
 assert(!effect_model_updates(0)); /* duplicate generations are not evidence */
 setup();hz=70;
 for(unsigned t=0;t<=120000;t+=10000){
  ++samples[7].generation;effect_model_tick(t,1);
 }
 assert(!effect_model_updates(0)); /* no independent A3 observations */
 setup();now=UINT32_MAX-60000u;window(6660,50,1);
 assert(effect_model_updates(0)==1 && effect_model_bias()==-990); /* timer wrap */
 setup();samples[7].value=6660;
 for(unsigned t=0;t<=120000;++t){
  ++samples[7].generation;hgen=t/40000;effect_model_tick(t,1);
 }
 assert(effect_model_updates(0)==1 && effect_model_bias()==-990); /* dense polls never overweight a window */
 setup();samples[7].value=6660;
 for(unsigned t=0;t<=120000;t+=10000){
  ++samples[7].generation;hgen=t/40000;effect_model_tick(t,1);
  samples[7].status=TELE_STALE; /* intermediate flow/temperature poll */
  effect_model_tick(t+100,1);samples[7].status=TELE_VALID;
  samples[6].age_ms=3000;effect_model_tick(t+200,1);samples[6].age_ms=0;
 }
 assert(effect_model_updates(0)==1 && effect_model_bias()==-990);
 setup();samples[7].value=6660;
 for(unsigned t=0;t<=60000;t+=10000){++samples[7].generation;hgen=t/40000;effect_model_tick(t,1);}
 for(unsigned t=130000;t<=190000;t+=10000){++samples[7].generation;hgen=t/40000;effect_model_tick(t,1);}
 assert(!effect_model_updates(0)); /* a gap cannot stitch two short plateaus */
 for(unsigned t=200000;t<=250000;t+=10000){++samples[7].generation;hgen=t/40000;effect_model_tick(t,1);}
 assert(effect_model_updates(0)==1);
 puts("PASS model: defaults/rails, bounded offset, inhibited and stale windows, independent observations, comparable repeated slopes, pivot compensation, confound rejection");
}
