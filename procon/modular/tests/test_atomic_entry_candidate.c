/* P0076 independent native model. Never opens a transport. */
#include "control.h"
#include "effect_feedback.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
static uint16_t cmd[8]={0xc076,1,5,6000,4000,900,1,3};
static effect_measurement fb;
static unsigned power,mode,flow,dhw,boost,actual_mode,sets,fail_set,drop_ack;
static unsigned guard28,guard26,last_guard,flow_sets,mode_sets,hidden_fixed,combined_sets,combined26,combined09;
static uint8_t flags[16];
static uint32_t now,last_flow_at;
static void reset(void){
    ctl_init();memset(flags,0,sizeof flags);power=1;mode=2;flow=3050;dhw=5200;boost=0;actual_mode=2;
    sets=fail_set=drop_ack=guard28=guard26=last_guard=flow_sets=mode_sets=combined_sets=combined26=combined09=0;hidden_fixed=4500;now=last_flow_at=0;
    fb=(effect_measurement){.supply_cC=3200,.instant_w=2000,.short_w=2000,.slow_w=2000,.age_ms=0,.span_ms=20000,.quality=EF_READY,.pairs=3,.mode=2,.hz=30,.ready=1};
    ctl_feedback(&fb);cmd[1]=1;cmd[2]=5;cmd[3]=6000;cmd[4]=4000;cmd[5]=900;cmd[6]=1;cmd[7]=3;
}
static void tick(void){
    uint8_t type,p[16],r[16]={0};ctl_feedback(&fb);ctl_tick(now);
    if(ctl_next(&type,p,now)){
        if(type==0x41){
            ++sets;
            if(ctl_read(256)==3){assert(guard28 && guard26 && last_guard==0x26);guard28=guard26=last_guard=0;}
            assert(p[0]==0x32);
            if(p[1]==8){++mode_sets;if(!fail_set){mode=p[6];if(mode==1)flow=hidden_fixed;}}
            else if(p[1]==0x88){
                ++combined_sets;assert(p[2]==0 && p[6]==1 && ((unsigned)(p[8]<<8)|p[9])==dhw);
                assert(((unsigned)(p[10]<<8)|p[11])>=2000 && ((unsigned)(p[10]<<8)|p[11])<=cmd[4]);
                if(!fail_set){hidden_fixed=(p[10]<<8)|p[11];flow=hidden_fixed;mode=1;}
                assert(flow<=cmd[4]);
            }
            else {assert(p[1]==0x80 && p[6]==mode && ((unsigned)(p[8]<<8)|p[9])==dhw);
                if(ctl_read(256)==3){assert(cmd[4]>4000 || now-last_flow_at>=60000);last_flow_at=now;++flow_sets;}
                if(!fail_set)hidden_fixed=flow=(p[10]<<8)|p[11];
            }
            if(drop_ack)ctl_timeout(now);else assert(ctl_reply(0x61,r,1,now));
        }else{
            assert(type==0x42);r[0]=p[0];
            if(p[0]==0x26){r[3]=power;r[4]=actual_mode;r[6]=mode;r[8]=dhw>>8;r[9]=dhw;if(ctl_read(280)==2){++guard26;last_guard=0x26;}}
            else if(p[0]==9){r[5]=flow>>8;r[6]=flow;}
            else {assert(p[0]==0x28);memcpy(r,flags,16);r[0]=0x28;r[3]=boost;if(ctl_read(280)==3){++guard28;last_guard=0x28;}}
            if(ctl_read(256)==3 && combined_sets && p[0]==0x26 && ctl_read(280)==1){++combined26;assert(ctl_read(258)==0);}
            if(ctl_read(256)==3 && combined_sets && p[0]==9 && ctl_read(280)==4){++combined09;assert(ctl_read(258)==0);}
            assert(ctl_reply(0x62,r,16,now));
        }
    }
    now+=100;
}
static void until(unsigned state){for(unsigned i=0;i<500 && ctl_read(256)!=state;++i)tick();if(ctl_read(256)!=state)fprintf(stderr,"until wanted%u got%u time%u quality%u age%u err%u\n",state,ctl_read(256),now,fb.quality,fb.age_ms,ctl_read(260));assert(ctl_read(256)==state);}
static void restore(void){uint16_t a[8]={0xc072,(uint16_t)(ctl_read(257)+1),1,0,0,0,0,2};assert(!ctl_submit(a,now));until(0);assert(mode==2 && flow==3050 && power==1 && dhw==5200 && !boost && !ctl_read(261));}

static void begin_entry(void){reset();cmd[4]=5500;assert(!ctl_submit(cmd,now));}
static void guards(void){while(ctl_read(256)!=3)tick();tick();tick();assert(ctl_read(280)==0 && !combined_sets);}
static void applied_once(void){for(unsigned i=0;i<500 && !ctl_read(258);++i)tick();if(ctl_read(258)!=1 || ctl_read(256)!=4)fprintf(stderr,"atomic state=%u error=%u phase=%u mode=%u actual=%u flow=%u sets=%u quality=%u pairs=%u age=%u pending=%u nativekind=%u\n",ctl_read(256),ctl_read(260),ctl_read(280),mode,actual_mode,flow,sets,fb.quality,fb.pairs,fb.age_ms,ctl_read(347),effect_pending_demand());assert(ctl_read(258)==1 && ctl_read(256)==4);assert(combined_sets==1 && combined26==1 && combined09==1);assert(ctl_read(270)==3050 && ctl_read(261));}
int main(void){
    begin_entry();applied_once();assert(flow==4500 && ctl_read(343)==1);restore();
    begin_entry();fb.ready=0;fb.quality=EF_SETTLING;fb.pairs=1;fb.span_ms=0;applied_once();assert(flow==4500);restore();
    begin_entry();fb.supply_cC=3800;applied_once();assert(flow==4200);restore();
    const unsigned hot_supply[]={3950,4000,4050,10000},hot_target[]={3850,3800,3750,3000};
    for(unsigned i=0;i<4;++i){begin_entry();fb.supply_cC=(int)hot_supply[i];applied_once();assert(flow==hot_target[i]);restore();}
    begin_entry();cmd[4]=4200; /* Already accepted cap remains5500; separate exact cap test below. */
    fb.instant_w=fb.short_w=6000;applied_once();assert(flow==3050);restore();
    reset();cmd[4]=4200;assert(!ctl_submit(cmd,now));applied_once();assert(flow==4200);restore();

    /* Re-evaluate demand after fresh guards, not when the snapshot was taken. */
    begin_entry();guards();fb.supply_cC=3900;applied_once();assert(flow==3900);restore();
    for(unsigned bad=0;bad<5;++bad){
        begin_entry();guards();
        switch(bad){case 0:fb.age_ms=15000;break;case 1:fb.pairs=0;break;case 2:fb.instant_w=INT32_MIN;break;case 3:fb.hz=0;break;case 4:fb.supply_cC=INT32_MIN;break;}
        for(unsigned i=0;i<30;++i)tick();assert(!combined_sets && !ctl_read(258) && ctl_read(261) && !ctl_read(260));
        fb.age_ms=0;fb.pairs=3;fb.instant_w=2000;fb.hz=30;fb.supply_cC=3200;
        applied_once();assert(flow==4500);restore();
    }
    /* A real native-mode guard reporting0 overrides an older positive-Hz pair. */
    begin_entry();while(ctl_read(256)!=3)tick();tick();actual_mode=0;
    applied_once();assert(flow==3250);restore();
    begin_entry();guards();fb.ready=0;fb.quality=EF_WAIT_NATIVE;fb.mode=actual_mode=0;fb.hz=0;
    /* Native guard is re-read after a transient collection before wire emission. */
    fb.quality=EF_PENDING;tick();fb.quality=EF_WAIT_NATIVE;
    applied_once();assert(flow==3250);restore();

    /* Once sent, both readbacks use the original combined target despite pause. */
    begin_entry();while(!combined_sets)tick();assert(flow==4500 && !ctl_read(258));
    fb.ready=0;fb.quality=EF_WAIT_NATIVE;fb.mode=actual_mode=0;fb.hz=0;
    applied_once();assert(flow==4500);
    tick();until(4);assert(flow==3250 && combined_sets==1);restore();

    /* Incomplete SETTLING does not delete the initial action or renew its lease. */
    begin_entry();guards();fb.ready=0;fb.quality=EF_SETTLING;fb.pairs=0;
    for(unsigned i=0;i<30;++i)tick();assert(!combined_sets && ctl_read(261) && !ctl_read(258));
    cmd[1]=2;assert(ctl_submit(cmd,now)==6);now=900001;tick();until(0);assert(!sets && ctl_read(260)==7 && mode==2);
    begin_entry();while(ctl_read(256)!=3)tick();flags[6]=1;until(0);assert(!sets && ctl_read(322)==EFFECT_NATIVE_INHIBIT);
    begin_entry();while(ctl_read(256)!=3)tick();power=0;until(0);assert(!sets && ctl_read(322)==EFFECT_MODE_CHANGED);
    puts("PASS offline atomic entry: one MODE_FLOW45C, first pair, thermal/configured caps, no gas at goal, late requalification, native-pause mild target, frozen sent readbacks, snapshot/AUTO/lease/native guards");
}
