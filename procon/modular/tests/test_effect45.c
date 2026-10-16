#include "effect_source_fixture.h"
#include "effect_feedback.h"
#include "control.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
_Static_assert(EFFECT_SUPPLY_LIMIT_CC==4500,"Test must use production45C policy");
_Static_assert(EFFECT_NATIVE_RESTART_CC==4450,"Native restart must retain45C priority");
static effect_measurement m;
static unsigned flow,last;
static void begin(int supply,unsigned initial){
 effect_init();effect_begin(6000,5500,0);effect_capture(initial,0);flow=initial;last=0;
 m=(effect_measurement){.instant_w=4000,.short_w=4000,.supply_cC=supply,.hz=40,.ready=1,.quality=EF_READY};
}
static void tick(unsigned t){
 effect_test_sources(&m,t);unsigned next=effect_decide(&m,flow,t);
 if(next){assert(next<=5500);if(next<flow){
  unsigned thermal=effect_read(315,&m,flow,t)&EFFECT_FLAG_THERMAL;
  assert(flow-next<=100u && t-last>=(thermal?30000u:60000u));last=t;}
 flow=next;effect_verified(next,t);}
}

/* Minimal FTC model for the live regression: the controller owns the real
   Mode/effect state machine while this harness only answers its GET/SETs. */
static effect_measurement ctl_m;
static uint16_t ctl_command[8];
static uint32_t ctl_now;
static unsigned ctl_power,ctl_mode,ctl_operating,ctl_flow,ctl_sets,ctl_last_target;
static int ctl_saw_3950;
static void ctl_step_test(void){
 uint8_t type,p[16],r[16]={0};
 effect_test_sources(&ctl_m,ctl_now);ctl_feedback(&ctl_m);
 if(ctl_next(&type,p,ctl_now)){
  if(type==0x41){
   assert(p[0]==0x32);++ctl_sets;
   if(p[1]&8)ctl_mode=p[6];
   if(p[1]&0x80){
    ctl_last_target=(unsigned)(p[10]<<8)|p[11];ctl_flow=ctl_last_target;
    assert(ctl_last_target<=EFFECT_SUPPLY_LIMIT_CC);
    if(ctl_last_target==3950)ctl_saw_3950=1;
   }
   assert(ctl_reply(0x61,r,1,ctl_now));
  }else{
   assert(type==0x42);r[0]=p[0];
   if(p[0]==0x26){r[3]=(uint8_t)ctl_power;r[4]=(uint8_t)ctl_operating;r[6]=(uint8_t)ctl_mode;r[8]=0x14;r[9]=0x50;}
   else if(p[0]==9){r[5]=(uint8_t)(ctl_flow>>8);r[6]=(uint8_t)ctl_flow;}
   else assert(p[0]==0x28);
   assert(ctl_reply(0x62,r,16,ctl_now));
  }
 }
 ctl_now+=100;
}
static void ctl_until_state(unsigned wanted){
 for(unsigned i=0;i<500 && ctl_read(256)!=wanted;++i)ctl_step_test();
 assert(ctl_read(256)==wanted);
}
static void live_native_pause_regression(void){
 ctl_init();effect_test_a3_mirror();ctl_now=ctl_sets=ctl_saw_3950=0;
 ctl_power=1;ctl_mode=2;ctl_operating=2;ctl_flow=2950;ctl_last_target=0;
 ctl_m=(effect_measurement){.instant_w=4000,.short_w=4000,.slow_w=4000,
  .supply_cC=4050,.age_ms=0,.span_ms=60000,.pairs=4,.mode=2,.hz=52,
  .ready=1,.quality=EF_READY};
 const uint16_t start[]={0xc076,1,5,5000,5500,900,1,3};
 memcpy(ctl_command,start,sizeof ctl_command);ctl_feedback(&ctl_m);
 assert(!ctl_submit(ctl_command,ctl_now));ctl_until_state(4);
 assert(ctl_mode==1 && ctl_flow==4250 && ctl_sets==1 && ctl_read(261));

 /* The live supervisor reduced5000W to4500W while actual water was already
    47.3C.  The thermal envelope must remain the highest-priority constraint. */
 ctl_m.instant_w=ctl_m.short_w=ctl_m.slow_w=5986;ctl_step_test();
 assert(ctl_flow==4250 && ctl_sets==1);
 ctl_command[1]=2;ctl_command[3]=4500;
 assert(!ctl_submit(ctl_command,ctl_now));
 ctl_now+=30000;ctl_m.instant_w=ctl_m.short_w=6188;ctl_m.slow_w=6000;
 ctl_m.supply_cC=4730;ctl_m.hz=44;ctl_step_test();
 assert(ctl_read(321)==EFFECT_LIMITED && ctl_read(322)==EFFECT_TEMPERATURE_CAP);
 assert(ctl_flow==4250 && ctl_read(258)==2);

 /* 44Hz ->26Hz ->0Hz reproduced the native rundown.  WAIT_NATIVE must replace
    the stale39.5C hard lower with a bounded restart request while retaining the
    mission snapshot and lease. */
 ctl_now+=30000;ctl_operating=0;ctl_m.mode=0;ctl_m.hz=26;
 ctl_m.ready=0;ctl_m.quality=EF_WAIT_NATIVE;
 ctl_step_test();ctl_until_state(4);
 assert(ctl_flow==EFFECT_NATIVE_RESTART_CC && ctl_last_target==EFFECT_NATIVE_RESTART_CC);
 assert(!ctl_saw_3950 && ctl_sets==2);
 assert(ctl_read(256)==4 && ctl_read(261) && ctl_read(258)==2 && ctl_read(264)>0);

 ctl_m.hz=0;ctl_m.supply_cC=4400;
 unsigned before=ctl_sets;for(unsigned i=0;i<20;++i)ctl_step_test();
 assert(ctl_flow>(unsigned)ctl_m.supply_cC && ctl_flow<=EFFECT_SUPPLY_LIMIT_CC);
 assert(ctl_sets==before && !ctl_saw_3950);
 assert(ctl_read(256)==4 && ctl_read(261) && ctl_read(258)==2 && ctl_read(264)>0);

 /* A normal lease renewal remains accepted throughout the native pause. */
 ctl_command[1]=3;assert(!ctl_submit(ctl_command,ctl_now));
 assert(ctl_read(257)==3 && ctl_read(258)==3 && ctl_read(264)>0);
 const uint16_t stop[]={0xc072,4,1,0,0,0,0,2};
 assert(!ctl_submit(stop,ctl_now));ctl_until_state(0);
 assert(ctl_mode==2 && ctl_flow==2950 && !ctl_read(261));
}
int main(void){
 /* Sustained40..43C is no longer latched by the historical40C policy. */
 for(int temp=4000;temp<=4300;temp+=50){
  begin(temp,4500);m.hz=52;m.instant_w=m.short_w=6000;for(unsigned t=0;t<=240000;t+=5000){tick(t);assert(!(effect_read(315,&m,flow,t)&1));}
 }
 /* Anticipate1C before the45C goal; thermal priority may cut1C/30s. */
 begin(4450,5500);
 for(unsigned t=0;t<=1800000;t+=5000){tick(t);assert(flow>=4350);}
 assert(flow==4350 && (effect_read(315,&m,flow,1800000)&1));
 assert(effect_read(324,&m,flow,1800000)==5500);
 /* Release at43.5C without cooling to43C or waiting90s. */
 m.supply_cC=4350;
 for(unsigned t=1805000;t<=1860000;t+=5000)tick(t);
 assert(!(effect_read(315,&m,flow,1860000)&1) && flow>4350);
 begin(4450,4300);m.hz=0;m.quality=EF_WAIT_NATIVE;m.ready=0;
 effect_test_sources(&m,0);assert(effect_entry_demand(&m,4300,0,0)==4350);
 /* A mission cap below the restart policy remains authoritative even while
    hot water would otherwise select the44.5C native-pause target. */
 effect_init();effect_begin(6000,4200,0);effect_capture(4100,0);
 m.supply_cC=4700;m.hz=0;m.quality=EF_WAIT_NATIVE;m.ready=0;
 assert(effect_pause_demand(&m,4100,0)==4200);
 assert(effect_read(324,&m,4100,0)==4200);
 /* If the verified request starts above that lower cap, unwind by exactly
    0.5C per full minute and stop at the cap. */
 effect_init();effect_begin(6000,4200,0);effect_capture(4700,0);
 assert(effect_pause_demand(&m,4700,59999)==0);
 unsigned hot_flow=4700,t_hot=60000;
 while(hot_flow>4200){
  unsigned next=effect_pause_demand(&m,hot_flow,t_hot);
  assert(next==hot_flow-50);hot_flow=next;effect_verified(hot_flow,t_hot);t_hot+=60000;
 }
 assert(effect_pause_demand(&m,hot_flow,t_hot)==0);
 /* Hz braking remains active even above the thermal approach threshold:
    envelope alone would allow44C here, power loop must request less. */
 begin(4400,4400);m.hz=70;m.instant_w=m.short_w=8500;
 for(unsigned t=0;t<=180000;t+=5000)tick(t);
 assert(flow<4400);
 /* A direct large upward retarget gets2C steps after fresh A3 feedback. */
 begin(3300,3500);m.hz=30;m.instant_w=m.short_w=3000;
 effect_retarget(3000,5500,0);tick(0);effect_retarget(10000,5500,5000);unsigned before=flow;
 tick(30000);assert(flow==before+200);
 /* Falling23Hz releases negative demand early; stationary24Hz may brake. */
 begin(3300,3250);effect_retarget(2000,5500,0);m.hz=24;m.instant_w=m.short_w=3200;
 tick(0);m.hz=23;tick(30000);assert(flow==3300);
 live_native_pause_regression();
 puts("PASS production45C: thermal cap and44->26->0Hz native pause retain a bounded44.5C restart target, mission and lease");
}
