/* P0072 r2 independent controller model and lease/failure tests. */
#include "control.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
static uint16_t cmd[8]={0xc072,1,2,3800,0,30,1,2};
static unsigned power,mode,flow,dhw,boost,sets,bad,dropack;
static unsigned mode_sets,power_sets;
static uint8_t flags28[16];
static uint32_t time_ms;
static void reset(void){memset(flags28,0,sizeof flags28);ctl_init();power=1;mode=2;flow=2950;dhw=5200;boost=sets=bad=dropack=mode_sets=power_sets=0;time_ms=0;cmd[1]=1;cmd[2]=2;cmd[3]=3800;cmd[4]=0;cmd[5]=30;cmd[6]=1;}
static void tick(void){
 uint8_t type,p[16],r[16]={0};ctl_tick(time_ms);
 if(ctl_next(&type,p,time_ms)){
  if(type==0x41){
   ++sets;assert(p[0]==0x32 || p[0]==0x34);
   if(!bad){
    if(p[0]==0x34){assert(p[1]==1);boost=p[3];}
    else switch(p[1]){
     case 1:++power_sets;power=p[3];break;case 8:++mode_sets;mode=p[6];break;
     case 0x80:assert(p[2]==0 && p[6]==mode && ((unsigned)(p[8]<<8)|p[9])==dhw);flow=(p[10]<<8)|p[11];break;
     case 0x20:dhw=(p[8]<<8)|p[9];break;default:assert(0);
    }
   }
   if(dropack)ctl_timeout(time_ms);else assert(ctl_reply(0x61,r,1,time_ms));
  }else{
   assert(type==0x42);r[0]=p[0];
   if(p[0]==0x26){r[3]=power;r[6]=mode;r[8]=dhw>>8;r[9]=dhw;}
   else if(p[0]==9){r[5]=flow>>8;r[6]=flow;}
   else {assert(p[0]==0x28);memcpy(r+4,flags28+4,12);r[3]=boost;}
   assert(ctl_reply(0x62,r,16,time_ms));
  }
 }
 time_ms+=100;
}
static void until(unsigned state,unsigned limit){for(unsigned i=0;i<limit && ctl_read(256)!=state;++i)tick();assert(ctl_read(256)==state);}
static void auto_restore(void){uint16_t a[8]={0xc072,(uint16_t)(ctl_read(257)+1),1,0,0,0,0,2};assert(!ctl_submit(a,time_ms));until(0,200);assert(mode==2 && flow==2950 && dhw==5200 && power==1 && boost==0 && !ctl_read(261));}
static void flag_matrix(void){
 for(unsigned intent=0;intent<6;++intent)for(unsigned byte=4;byte<=10;++byte)for(unsigned value=1;value<=2;++value){
  reset();
  if(intent==0){cmd[2]=0;cmd[3]=cmd[6]=0;}
  if(intent==2){cmd[2]=3;cmd[3]=cmd[6]=0;}
  if(intent==3){cmd[2]=4;cmd[3]=0;cmd[4]=5400;cmd[6]=2;}
  if(intent==4){cmd[2]=4;}
  if(intent==5){cmd[4]=5400;cmd[6]=3;}
  flags28[byte]=(uint8_t)value;
  unsigned mask=(1u<<4)|(1u<<10);
  if(intent==1 || intent==4 || intent==5)mask|=1u<<6;
  if(intent==2 || intent==3 || intent==5)mask|=1u<<5;
  unsigned blocked=value>1 || (mask&(1u<<byte));
  assert(!ctl_submit(cmd,0));tick();tick();tick();
  assert(ctl_read(283)==1 && ctl_read(285)==1 && ctl_read(287)==mask);
  if(blocked){
   assert(ctl_read(256)==0 && ctl_read(260)==3 && !sets && !ctl_read(261));
   assert(ctl_read(286)==(1u<<byte) && ctl_read(296)==0x28 && ctl_read(297)==byte && ctl_read(298)==value);
   uint8_t fresh[16]={0x28};ctl_observe(fresh,time_ms);
   assert(ctl_read(286)==(1u<<byte) && ctl_read(297)==byte); /* passive update retains reason */
  }else{until(4,200);assert(!ctl_read(286));auto_restore();}
 }
 reset();uint8_t raw[16]={0x28,0,0,0,0,1,0,1,1,1};ctl_observe(raw,0);ctl_tick(32000);
 assert(ctl_read(284)==32 && ctl_read(290)==256 && ctl_read(291)==256 && ctl_read(292)==257);
 ctl_tick(70000000);assert(ctl_read(284)==65535);
 reset();flags28[4]=flags28[6]=flags28[10]=1;assert(!ctl_submit(cmd,0));tick();tick();tick();
 assert(ctl_read(286)==((1u<<4)|(1u<<6)|(1u<<10)) && ctl_read(297)==4);
}
static void direct_targets(void){
 reset();assert(!ctl_submit(cmd,0));until(4,200);
 unsigned before=sets;
 cmd[1]=2;cmd[3]=3200;assert(!ctl_submit(cmd,time_ms));
 assert(ctl_read(257)==2 && ctl_read(258)==1 && ctl_read(261));
 uint16_t lease=ctl_read(264);assert(!ctl_submit(cmd,time_ms));assert(ctl_read(264)==lease);
 uint16_t next[8];memcpy(next,cmd,sizeof next);next[1]=3;next[3]=3400;
 assert(ctl_submit(next,time_ms)==6); /* do not overwrite a pending replacement */
 cmd[3]=3300;assert(ctl_submit(cmd,time_ms)==3);cmd[3]=3200;
 until(4,200);assert(flow==3200 && mode==1 && sets==before+1 && mode_sets==1 && power_sets==0);
 assert(ctl_read(258)==2 && ctl_read(269)==2 && ctl_read(270)==2950);
 assert(!ctl_submit(next,time_ms));until(4,200);assert(flow==3400 && mode_sets==1 && power_sets==0);
 auto_restore();assert(mode_sets==2 && power_sets==0);
 /* New target has its own lease, which restores the original curve/target. */
 reset();assert(!ctl_submit(cmd,0));until(4,200);cmd[1]=2;cmd[3]=3200;
 uint32_t accepted_at=time_ms;assert(!ctl_submit(cmd,time_ms));until(4,200);
 time_ms=accepted_at+30001;tick();until(0,200);assert(mode==2 && flow==2950 && ctl_read(260)==7);
 /* Revalidate flags before any replacement SET. */
 reset();assert(!ctl_submit(cmd,0));until(4,200);before=sets;flags28[6]=1;cmd[1]=2;cmd[3]=3200;
 assert(!ctl_submit(cmd,time_ms));tick();tick();tick();assert(ctl_read(256)==5 && sets==before);
 flags28[6]=0;until(0,200);assert(flow==2950 && mode==2);
 /* Native mode change between session and guard must not write replacement. */
 reset();assert(!ctl_submit(cmd,0));until(4,200);before=sets;mode=2;cmd[1]=2;cmd[3]=3200;
 assert(!ctl_submit(cmd,time_ms));tick();assert(ctl_read(256)==5 && sets==before);until(0,200);
 /* Changed external target is not silently adopted as our original. */
 reset();assert(!ctl_submit(cmd,0));until(4,200);before=sets;flow=3500;cmd[1]=2;cmd[3]=3200;
 assert(!ctl_submit(cmd,time_ms));tick();tick();assert(ctl_read(256)==5 && sets==before);until(0,200);assert(flow==2950);
 /* Missing ACK is resolved by target readback; failed SET restores original. */
 reset();assert(!ctl_submit(cmd,0));until(4,200);dropack=1;cmd[1]=2;cmd[3]=3200;
 assert(!ctl_submit(cmd,time_ms));until(4,200);assert(flow==3200 && ctl_read(258)==2);auto_restore();
 reset();assert(!ctl_submit(cmd,0));until(4,200);bad=1;cmd[1]=2;cmd[3]=3200;
 assert(!ctl_submit(cmd,time_ms));until(5,200);assert(ctl_read(258)==1 && ctl_read(270)==2950);
 bad=0;until(0,200);assert(mode==2 && flow==2950);
 puts("PASS P0080 direct targets: multiple targets, single FLOW writes, preserved original, pending/retry/lease/guards/readback/failure");
}
int main(void){
 direct_targets();
 flag_matrix();
 reset();uint16_t w[8];memcpy(w,cmd,sizeof w);w[3]=4501;assert(ctl_submit(w,0)==3 && !sets);w[3]=1999;assert(ctl_submit(w,0)==3);w[3]=3800;w[5]=1801;assert(ctl_submit(w,0)==3);
 w[5]=30;w[4]=3900;w[6]=3;assert(ctl_submit(w,0)==3);w[4]=6001;assert(ctl_submit(w,0)==3);w[4]=5200;w[2]=5;assert(ctl_submit(w,0)==3);
 reset();assert(!ctl_submit(cmd,0));until(4,200);assert(mode==1 && flow==3800 && ctl_read(258)==1 && sets==2 && ctl_read(265)==2);
 /* Exact retry doesn't extend lease; conflicting same sequence rejected. */
 uint16_t remaining=ctl_read(264);assert(!ctl_submit(cmd,time_ms));assert(ctl_read(264)==remaining);cmd[3]=3900;assert(ctl_submit(cmd,time_ms)==3);cmd[3]=3800;
 cmd[1]=2;assert(!ctl_submit(cmd,time_ms));assert(ctl_read(258)==2 && ctl_read(264)==30);auto_restore();assert(ctl_read(267)==1);
 reset();assert(!ctl_submit(cmd,0));until(4,200);time_ms=30001;tick();until(0,200);assert(mode==2 && flow==2950 && ctl_read(260)==7);
 reset();time_ms=0xfffff000u;assert(!ctl_submit(cmd,time_ms));until(4,200);time_ms=0xfffff000u+30001u;tick();until(0,200);assert(mode==2 && flow==2950);
 reset();dropack=1;assert(!ctl_submit(cmd,0));until(4,200);assert(ctl_read(265)==0 && ctl_read(258)==1);auto_restore();
 reset();bad=1;assert(!ctl_submit(cmd,0));for(unsigned i=0;i<200;++i)tick();assert(ctl_read(258)==0);bad=0;until(0,200);assert(mode==2 && flow==2950);
 reset();cmd[2]=0;cmd[3]=0;cmd[6]=0;assert(!ctl_submit(cmd,0));until(4,200);assert(!power);auto_restore();
 reset();cmd[2]=3;cmd[3]=0;cmd[4]=5500;cmd[6]=2;assert(!ctl_submit(cmd,0));until(4,200);assert(boost==1 && dhw==5500);auto_restore();
 reset();cmd[2]=4;cmd[3]=0;cmd[4]=5400;cmd[6]=2;assert(!ctl_submit(cmd,0));until(4,200);assert(dhw==5400 && mode==2);auto_restore();
 /* Bad initial native mode forbids all SETs. */
 reset();mode=4;assert(!ctl_submit(cmd,0));tick();tick();assert(sets==0 && ctl_read(256)==0 && ctl_read(260)==3);
 /* Missing preflight replies must not cause SET; retries bounded. */
 reset();assert(!ctl_submit(cmd,0));uint8_t type,p[16];for(unsigned i=0;i<3;++i){assert(ctl_next(&type,p,1000*i));assert(type==0x42);ctl_timeout(1000*i+800);}assert(ctl_read(256)==0 && !ctl_read(261));
 /* Ack alone is not applied, and wrong echo is not consumed. */
 reset();assert(!ctl_submit(cmd,0));for(unsigned i=0;i<4;++i)tick();assert(sets==1 && ctl_read(258)==0);time_ms+=1000;assert(ctl_next(&type,p,time_ms));uint8_t wrong[16]={9};assert(!ctl_reply(0x62,wrong,16,time_ms));ctl_timeout(time_ms+800);
 /* Failed compensation retains snapshot and retries instead of claiming AUTO. */
 reset();assert(!ctl_submit(cmd,0));until(4,200);bad=1;time_ms=30001;tick();until(6,200);
 assert(ctl_read(261)==1 && ctl_read(267)==0 && flow==3800);bad=0;until(0,300);assert(flow==2950 && mode==2);
 /* Reboot is intentionally read-only, with no false restoration claim. */
 ctl_init();assert(!ctl_busy() && !ctl_read(261) && ctl_read(282)==0);
 puts("PASS P0072 r3 controls + 84 flag cases: ranges, sequence/idempotence, renewal, snapshot, OFF/FIXED/DHW/targets, readback not ack, restoration, lease/wrap, missing replies and reboot limits");
}
