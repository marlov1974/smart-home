/* P0072 r2 independent controller model and lease/failure tests. */
#include "control.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
static uint16_t cmd[8]={0xc072,1,2,3800,0,30,1,2};
static unsigned power,mode,flow,dhw,boost,sets,bad,dropack;
static uint32_t time_ms;
static void reset(void){ctl_init();power=1;mode=2;flow=2950;dhw=5200;boost=sets=bad=dropack=0;time_ms=0;cmd[1]=1;cmd[2]=2;cmd[3]=3800;cmd[4]=0;cmd[5]=30;cmd[6]=1;}
static void tick(void){
 uint8_t type,p[16],r[16]={0};ctl_tick(time_ms);
 if(ctl_next(&type,p,time_ms)){
  if(type==0x41){
   ++sets;assert(p[0]==0x32 || p[0]==0x34);
   if(!bad){
    if(p[0]==0x34){assert(p[1]==1);boost=p[3];}
    else switch(p[1]){
     case 1:power=p[3];break;case 8:mode=p[6];break;
     case 0x80:assert(p[2]==0 && p[6]==mode && ((unsigned)(p[8]<<8)|p[9])==dhw);flow=(p[10]<<8)|p[11];break;
     case 0x20:dhw=(p[8]<<8)|p[9];break;default:assert(0);
    }
   }
   if(dropack)ctl_timeout(time_ms);else assert(ctl_reply(0x61,r,1,time_ms));
  }else{
   assert(type==0x42);r[0]=p[0];
   if(p[0]==0x26){r[3]=power;r[6]=mode;r[8]=dhw>>8;r[9]=dhw;}
   else if(p[0]==9){r[5]=flow>>8;r[6]=flow;}
   else {assert(p[0]==0x28);r[3]=boost;}
   assert(ctl_reply(0x62,r,16,time_ms));
  }
 }
 time_ms+=100;
}
static void until(unsigned state,unsigned limit){for(unsigned i=0;i<limit && ctl_read(256)!=state;++i)tick();assert(ctl_read(256)==state);}
static void auto_restore(void){uint16_t a[8]={0xc072,(uint16_t)(ctl_read(257)+1),1,0,0,0,0,2};assert(!ctl_submit(a,time_ms));until(0,200);assert(mode==2 && flow==2950 && dhw==5200 && power==1 && boost==0 && !ctl_read(261));}
int main(void){
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
 puts("PASS P0072 r2 controls: ranges, sequence/idempotence, renewal, snapshot, OFF/FIXED/DHW/targets, readback not ack, restoration, lease/wrap, missing replies and reboot limits");
}
