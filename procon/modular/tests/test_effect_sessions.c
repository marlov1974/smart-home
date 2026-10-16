/* P0080: the EFFECT mission policy is independent of its target ceiling.
   Exercise native pause/DHW/link recovery and rollback with a simulated FTC. */
#include "control.h"
#include "effect_feedback.h"
#include "effect_source_fixture.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>

static effect_measurement feedback;
static uint16_t command[8];
static uint32_t now;
static unsigned power, mode, operating, flow, sets;
static uint8_t flags[16];

static void step(void){
    uint8_t type,p[16],r[16]={0};
    effect_test_sources(&feedback,now);ctl_feedback(&feedback);
    if(ctl_next(&type,p,now)){
        if(type==0x41){
            assert(p[0]==0x32);++sets;
            if(p[1]&8)mode=p[6];
            if(p[1]&0x80)flow=(p[10]<<8)|p[11];
            assert(ctl_reply(0x61,r,1,now));
        }else{
            assert(type==0x42);r[0]=p[0];
            if(p[0]==0x26){r[3]=(uint8_t)power;r[4]=(uint8_t)operating;r[6]=(uint8_t)mode;r[8]=0x14;r[9]=0x50;}
            else if(p[0]==9){r[5]=(uint8_t)(flow>>8);r[6]=(uint8_t)flow;}
            else {assert(p[0]==0x28);memcpy(r+1,flags+1,15);}
            assert(ctl_reply(0x62,r,16,now));
        }
    }
    now+=100;
}
static void until(unsigned wanted){
    for(unsigned i=0;i<500 && ctl_read(256)!=wanted;++i)step();
    assert(ctl_read(256)==wanted);
}
static void prepare(unsigned cap){
    ctl_init();now=sets=0;power=1;mode=2;operating=2;flow=2950;
    memset(flags,0,sizeof flags);
    feedback=(effect_measurement){.instant_w=6000,.short_w=6000,.slow_w=6000,
        .supply_cC=2900,.span_ms=60000,.pairs=4,.mode=2,.hz=50,.ready=1,.quality=EF_READY};
    const uint16_t c[]={0xc076,1,5,6000,(uint16_t)cap,1800,1,3};
    memcpy(command,c,sizeof command);ctl_feedback(&feedback);
    assert(!ctl_submit(command,now));
}
static void start(unsigned cap){
    prepare(cap);until(4);
    assert(mode==1 && flow<=cap && ctl_read(261));
}
static void stop(void){
    const uint16_t c[]={0xc072,(uint16_t)(ctl_read(257)+1),1,0,0,0,0,2};
    assert(!ctl_submit(c,now));
}
static void restored(void){
    until(0);assert(mode==2 && flow==2950 && !ctl_read(261) && ctl_read(267)==1);
}
static void pause_and_dhw(unsigned cap){
    start(cap);
    unsigned before=sets;
    for(unsigned m=1;m<=6;m+=5){
        operating=m;feedback.mode=(uint16_t)m;feedback.quality=EF_DHW;feedback.ready=0;
        uint8_t p[16]={0x26};p[3]=1;p[4]=(uint8_t)m;p[6]=1;ctl_observe(p,now);
        for(unsigned i=0;i<50;++i)step();
        assert(ctl_read(256)==4 && ctl_read(261) && !ctl_read(260) && sets==before);
    }
    operating=0;feedback.mode=0;feedback.hz=0;feedback.quality=EF_WAIT_NATIVE;
    step();now+=1200100;step(); /* more than the removed 20 minute abort */
    assert(ctl_read(261) && ctl_read(256)!=5 && ctl_read(256)!=6 && !ctl_read(260));
    until(4);stop();restored();
}
static void link_and_timeout(unsigned cap){
    start(cap);unsigned before=sets;
    feedback.ready=0;feedback.quality=EF_LINKLOSS;ctl_feedback(&feedback);ctl_link_lost(now);
    step();assert(ctl_read(256)==4 && ctl_read(261) && sets==before);
    feedback.ready=1;feedback.quality=EF_READY;ctl_feedback(&feedback);
    /* Revalidation read timeouts return to recovery, without forgetting snapshot. */
    uint8_t type,p[16];
    for(unsigned i=0;i<3;++i){
        assert(ctl_next(&type,p,now));assert(type==0x42);ctl_timeout(now+800);now+=1000;
    }
    assert(ctl_read(256)==4 && ctl_read(261) && !ctl_read(260) && sets==before);
    step();until(4);assert(sets==before);
    /* Link loss during requested restore must never turn the mission back on. */
    stop();assert(ctl_read(256)==5);ctl_link_lost(now);assert(ctl_read(256)==5);
    restored();
}
static void interrupted_entry(unsigned cap){
    for(unsigned sent=0;sent<3;++sent){
        prepare(cap);until(3);assert(!sets && !ctl_read(258));
        if(sent){while(!sets)step();assert(mode==1);}
        if(sent==2){mode=2;flow=2950;} /* sent SET was never applied */
        feedback.ready=0;feedback.quality=EF_LINKLOSS;ctl_feedback(&feedback);ctl_link_lost(now);
        step();assert(ctl_read(256)==4 && ctl_read(261) && !ctl_read(258));
        uint8_t p[16]={0x26};p[3]=1;p[4]=2;p[6]=(uint8_t)mode;ctl_observe(p,now);
        feedback.ready=1;feedback.quality=EF_READY;
        for(unsigned i=0;i<500 && (!ctl_read(258) || ctl_read(256)!=4);++i)step();
        assert(ctl_read(258)==1 && ctl_read(256)==4 && mode==1 && flow<=cap);
        assert(sets==(sent==2?2u:1u) && ctl_read(269)==2 && ctl_read(270)==2950);
        stop();restored();
    }
    /* Changing a previously applied mission's mode during outage is not entry. */
    start(cap);unsigned before=sets;ctl_link_lost(now);mode=2;
    step();assert(ctl_read(256)==5 && sets==before);restored();
    /* A different initial mode also cannot be adopted under cover of recovery. */
    prepare(cap);until(3);ctl_link_lost(now);mode=0;
    step();assert(ctl_read(256)==0 && !sets && !ctl_read(261));
}
static void guards_and_lease(unsigned cap){
    start(cap);power=0;
    uint8_t p[16]={0x26};p[3]=0;p[4]=2;p[6]=1;ctl_observe(p,now);
    step();assert(ctl_read(256)==5);restored();assert(power==0);
    start(cap);flags[6]=1;p[0]=0x28;memcpy(p+1,flags+1,15);ctl_observe(p,now);
    step();assert(ctl_read(256)==5);restored();
    start(cap);now=1800001;step();assert(ctl_read(256)==5 && ctl_read(260)==7);restored();
}
int main(void){
    const unsigned caps[]={3000,3800,4000,5500};
    for(unsigned i=0;i<sizeof caps/sizeof *caps;++i){
        pause_and_dhw(caps[i]);link_and_timeout(caps[i]);interrupted_entry(caps[i]);guards_and_lease(caps[i]);
    }
    puts("PASS P0080 EFFECT session policy at 30/38/40/55C: DHW/pause/link/read-timeout recovery, native guards, lease expiry and interrupted restoration");
}
