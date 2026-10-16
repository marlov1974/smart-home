/* P0076 independent native model. Never opens a transport. */
#include "control.h"
#include "effect_feedback.h"
#include "effect_model.h"
#define EFFECT_AUTO_SOURCES
#include "effect_source_fixture.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
static uint16_t cmd[8]={0xc076,1,5,6000,4000,900,1,3};
static effect_measurement fb;
static unsigned power,mode,flow,dhw,boost,actual_mode,sets,fail_set,drop_ack;
static unsigned expected_entry=2950;
static unsigned guard28,guard26,last_guard,flow_sets,mode_sets,hidden_fixed,combined_sets,combined26,combined09;
static uint8_t flags[16];
static uint32_t now,last_flow_at;
static void reset(void){
    expected_entry=2950;ctl_init();memset(flags,0,sizeof flags);power=1;mode=2;flow=2950;dhw=5200;boost=0;actual_mode=2;
    sets=fail_set=drop_ack=guard28=guard26=last_guard=flow_sets=mode_sets=combined_sets=combined26=combined09=0;hidden_fixed=4500;now=last_flow_at=0;
    fb=(effect_measurement){.supply_cC=2900,.instant_w=2000,.short_w=2000,.slow_w=2000,.age_ms=0,.span_ms=20000,.quality=EF_READY,.pairs=3,.mode=2,.hz=30,.ready=1};
    ctl_feedback(&fb);cmd[1]=1;cmd[2]=5;cmd[3]=6000;cmd[4]=4000;cmd[5]=900;cmd[6]=1;cmd[7]=3;
}
static void tick(void){
    uint8_t type,p[16],r[16]={0};effect_test_sources(&fb,now);ctl_feedback(&fb);ctl_tick(now);
    if(ctl_next(&type,p,now)){
        if(type==0x41){
            ++sets;
            if(ctl_read(256)==3){assert(guard28 && guard26 && last_guard==0x26);guard28=guard26=last_guard=0;}
            assert(p[0]==0x32);
            if(p[1]==8){++mode_sets;if(!fail_set){mode=p[6];if(mode==1)flow=hidden_fixed;}}
            else if(p[1]==0x88){
                ++combined_sets;assert(p[2]==0 && p[6]==1 && ((unsigned)(p[8]<<8)|p[9])==dhw);
                assert(((unsigned)(p[10]<<8)|p[11])==expected_entry);
                if(!fail_set){hidden_fixed=(p[10]<<8)|p[11];flow=hidden_fixed;mode=1;}
                assert(flow<=cmd[4]);
            }
            else {assert(p[1]==0x80 && p[6]==mode && ((unsigned)(p[8]<<8)|p[9])==dhw);
                if(ctl_read(256)==3){last_flow_at=now;++flow_sets;}
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
static void start(void){
    /* These fixtures isolate behavior AFTER entry. Start already at the power
       goal so the separate atomic-entry test owns startup-gas assertions. */
    effect_measurement before=fb;
    {
        if(actual_mode==0 || (fb.quality==EF_WAIT_NATIVE && !fb.hz)){
            expected_entry=(unsigned)(fb.supply_cC+50);if(expected_entry>3950)expected_entry=3950;if(expected_entry>cmd[4])expected_entry=cmd[4];
        }else fb.short_w=fb.instant_w=cmd[3];
        ctl_feedback(&fb);
    }
    assert(!ctl_submit(cmd,now));until(4);assert(mode==1 && flow==expected_entry && sets==1 && ctl_read(261));
    assert(combined_sets==1 && combined26==1 && combined09==1 && !mode_sets);assert((ctl_read(262)&12)==12);
    fb=before;ctl_feedback(&fb);
}

static void advance(void){now+=60000;tick();until(4);}
static void restore(void){uint16_t a[8]={0xc072,(uint16_t)(ctl_read(257)+1),1,0,0,0,0,2};assert(!ctl_submit(a,now));until(0);assert(mode==2 && flow==2950 && power==1 && dhw==5200 && !boost && !ctl_read(261));}
static void regulator_test(void){
    const unsigned caps[]={3000,3800,4000,5500};
    for(unsigned i=0;i<sizeof caps/sizeof *caps;++i){
        effect_measurement m={.short_w=2000,.instant_w=2000,.supply_cC=2900,.hz=30,
            .ready=1,.quality=EF_READY,.pairs=3,.span_ms=20000};
        effect_begin(6000,(uint16_t)caps[i],0);effect_capture(2950,0);
        unsigned target=effect_decide(&m,2950,0);
        assert(target>2950 && target<=caps[i]);
        assert(!effect_decide(&m,2950,1000)); /* pending write never repeats */
        effect_verified((uint16_t)target,1000);
        for(unsigned t=5000;t<=600000;t+=5000){
            unsigned n=effect_decide(&m,(uint16_t)target,t);
            if(n){assert(n<=caps[i] && n>=3000);target=n;effect_verified((uint16_t)n,t);}
            assert(effect_read(322,&m,(uint16_t)target,t)!=EFFECT_UNKNOWN_UNREACHABLE);
            assert(effect_read(322,&m,(uint16_t)target,t)!=EFFECT_CUMULATIVE_CAP);
            assert(!effect_read(346,&m,(uint16_t)target,t));
        }
        assert(effect_read(321,&m,(uint16_t)target,600000)!=EFFECT_INVALID_FEEDBACK);
        m.supply_cC=4000;unsigned lower=effect_decide(&m,(uint16_t)target,660000);
        if(target>3900)assert(lower==target-100);
        else assert(!lower); /* qualified thermal floor is actual-1C */
        assert(effect_read(321,&m,(uint16_t)target,660000)!=EFFECT_INVALID_FEEDBACK);
    }
}
/* P0080 fast demand safety and response, shared by every configured target ceiling. */
static void fast_test(void){
 effect_measurement m={.instant_w=4000,.short_w=4000,.supply_cC=3300,.hz=40,.ready=1,.quality=EF_READY};
 effect_begin(6000,5500,0);effect_capture(3050,0);
 unsigned request_flow=effect_decide(&m,3050,0);assert(request_flow==3800);effect_verified(request_flow,0);
 unsigned n=0;
 /* The two-loop controller tapers surplus delta before lagged heat power
    reaches target. Timing/bounds are invariant; exact response is tested in
    test_predictive_candidate.c against distinct A3 target observations. */
 for(unsigned t=5000;t<=240000;t+=5000){
  m.hz=t<30000?40:t<120000?50:58;m.short_w=t<120000?2800:5500;
  unsigned before=request_flow;
  n=effect_decide(&m,request_flow,t);
  if(n){assert(n>=before-50 && n<=before+50);request_flow=n;effect_verified(n,t);}
 }
 m.age_ms=15000;m.short_w=3000;assert(!effect_decide(&m,request_flow,270000));
 m.age_ms=59000;unsigned before=request_flow;n=effect_decide(&m,request_flow,300000);
 if(n){assert(n>=before-50 && n<=before+50);request_flow=n;effect_verified(n,300000);}
 assert(effect_read(322,&m,request_flow,300000)!=EFFECT_SOURCE_STALE);
 m.supply_cC=3900;n=effect_decide(&m,request_flow,330000);
 if(request_flow>3950)assert(n==request_flow-50 && n>=3950);
 assert(effect_read(321,&m,request_flow,330000)==EFFECT_LIMITED);
 reset();cmd[4]=5500;start();
 while(!flow_sets)tick();until(4);assert(flow==3900 && ctl_read(344)>500);
 fb.ready=0;fb.quality=EF_WAIT_NATIVE;fb.mode=actual_mode=0;fb.hz=0;
 tick();until(4);assert(flow==3900);restore();
 reset();cmd[4]=5500;fb.supply_cC=3300;start();while(!flow_sets)tick();until(4);
 unsigned hot_before=flow;fb.supply_cC=4000;tick();until(4);assert(flow==hot_before);
   now+=60000;tick();until(4);assert(mode==1 && flow<hot_before && hot_before-flow<=100 && flow>=3900 && ctl_read(261));
 assert(ctl_read(321)==EFFECT_LIMITED && ctl_read(322)==EFFECT_TEMPERATURE_CAP);
 hot_before=flow;fb.supply_cC=4050;now+=15000;tick();until(4);assert(flow==hot_before);
   now+=45000;tick();until(4);assert(mode==1 && flow<hot_before && hot_before-flow<=100 && flow>=3950 && ctl_read(261));restore();
 reset();cmd[4]=5500;start();while(!flow_sets)tick();until(4);
 fb.ready=0;fb.quality=EF_STALE;tick();until(4);assert(flow<=3950 && mode==1 && ctl_read(261));
 fb.ready=1;fb.quality=EF_READY;now+=15000;tick();until(4);restore();
 reset();cmd[4]=5500;start();actual_mode=fb.mode=1;fb.ready=0;fb.quality=EF_DHW;
 tick();assert(ctl_read(256)==4 && ctl_read(261));
 actual_mode=fb.mode=2;fb.ready=1;fb.quality=EF_READY;now+=15000;tick();until(4);restore();
 reset();cmd[4]=5500;start();ctl_link_lost(now);fb.ready=0;fb.quality=EF_LINKLOSS;
 tick();assert(ctl_read(256)==4 && ctl_read(261));
 fb.ready=1;fb.quality=EF_READY;tick();until(4);assert(ctl_read(270)==2950);restore();
 reset();cmd[4]=5500;fb.ready=0;fb.quality=EF_WAIT_NATIVE;fb.mode=actual_mode=0;fb.hz=0;fb.supply_cC=3400;start();
 for(unsigned i=0;i<6;++i)advance();assert(flow==3450 && !ctl_read(346));restore();
 puts("PASS fast EFFECT: frequency-distance startup, Hz-leading bounded acceleration feedback, persistent thermal regulation, stale/DHW/link recovery, old-data reduction, no5C latch, mild native-pause demand");
}
static void startup_pair(void){
    fb.ready=0;fb.quality=EF_SETTLING;fb.mode=actual_mode=2;fb.hz=26;
    fb.pairs=1;fb.span_ms=0;fb.age_ms=1000;fb.instant_w=fb.short_w=2000;
}
static void startup_wait(void){
    reset();cmd[4]=5500;fb.ready=0;fb.quality=EF_WAIT_NATIVE;fb.mode=actual_mode=0;fb.hz=0;
    fb.pairs=0;fb.span_ms=0;start();
}
static void startup_test(void){
    /* First coherent heating pair is enough for guarded startup demand. */
    startup_wait();startup_pair();uint32_t began=now;
    tick();assert(ctl_read(256)==3 && effect_pending_demand()==2);
    until(4);assert(flow==3900 && flow_sets==1 && now-began<10000u && fb.span_ms==0);
    assert(ctl_read(270)==2950 && ctl_read(261));restore();

    /* Incoherent, aged, invalid or non-heating startup data cannot raise. */
    for(unsigned bad=0;bad<9;++bad){
        startup_wait();startup_pair();
        switch(bad){
        case 0:fb.pairs=0;break;case 1:fb.age_ms=15000;break;
        case 2:fb.hz=0;break;case 3:fb.hz=255;break;
        case 4:fb.mode=actual_mode=1;fb.quality=EF_DHW;break;
        case 5:fb.quality=EF_INVALID;break;case 6:fb.supply_cC=-1;break;
        case 7:fb.supply_cC=10001;break;case 8:fb.instant_w=fb.short_w=7000;break;
        }
        for(unsigned i=0;i<40;++i)tick();
        assert(!flow_sets && flow==2950 && ctl_read(261));restore();
    }
    /* Qualification is checked again after the native guard reads. */
    startup_wait();startup_pair();tick();assert(ctl_read(256)==3 && !flow_sets);
    fb.age_ms=15000;tick();tick();
    assert(ctl_read(256)==4 && !flow_sets && !effect_pending_demand());restore();

    /* Crossing into qualified READY during the guard does not discard startup. */
    startup_wait();startup_pair();tick();
    fb.ready=1;fb.quality=EF_READY;fb.pairs=3;fb.span_ms=20000;
    until(4);assert(flow_sets==1 && flow==3900);restore();

    /* A sent startup command still completes readback after pair qualification fades. */
    startup_wait();startup_pair();while(!flow_sets)tick();
    assert(effect_pending_demand()==2 && ctl_read(256)==3);
    fb.pairs=0;until(4);assert(flow==3900 && ctl_read(343)==1 && !effect_pending_demand());
    fb.pairs=1;fb.supply_cC=3800;tick();until(4);assert(flow==3900);
    now+=60000;tick();until(4);assert(flow==3900);
    fb.supply_cC=3900;now+=30000;tick();until(4);assert(flow==3900);
    fb.supply_cC=3950;now+=30000;tick();until(4);assert(flow==3900 && ctl_read(261));restore();

    /* Early startup retains the same finite lease and original restoration. */
    startup_wait();startup_pair();tick();until(4);assert(flow==3900);
    now+=900001u;tick();until(0);
    assert(mode==2 && flow==2950 && !ctl_read(261) && ctl_read(260)==7);
    puts("PASS early startup: fresh first pair, SETTLING/READY guard races, invalid admission, sent readback, timed gradual thermal reduction, original AUTO/lease restoration");
}
static unsigned fine_prime(effect_measurement *m,unsigned *demand){
    *m=(effect_measurement){.short_w=5840,.instant_w=5840,.supply_cC=3300,.hz=50,.ready=1,.quality=EF_READY};
    effect_begin(6000,5500,0);effect_capture(4500,0);*demand=4500;
    for(unsigned t=0;t<=60000;t+=5000){
        unsigned n=effect_decide(m,*demand,t);
        if(n){*demand=n;effect_verified(n,t);}
    }
    return 60000;
}
static void fine_test(void){
    effect_measurement m;unsigned demand;
    fine_prime(&m,&demand);assert(demand==4450);
    /* Small water-power quantization errors no longer integrate actuator gas. */
    for(unsigned t=65000;t<=300000;t+=5000){
        m.short_w=t<150000?5840:6160;
        unsigned n=effect_decide(&m,demand,t);
        if(n){assert(n==demand-50);demand=n;effect_verified(n,t);}
    }
    assert(demand<4450 && demand>=3500);
    assert(effect_read(319,&m,demand,300000)==0);
    /* Persistent material error adjusts the frequency goal, at most1Hz/min. */
    m.short_w=5100;
    for(unsigned t=305000;t<=480000;t+=5000){
        unsigned n=effect_decide(&m,demand,t);
        if(n){assert(n>=demand-50 && n<=demand+50);demand=n;effect_verified(n,t);}
    }
    assert(effect_read(319,&m,demand,480000)>0 && effect_read(319,&m,demand,480000)<=300);
    int16_t trim=(int16_t)effect_read(319,&m,demand,480000);
    int32_t bias=effect_model_bias();uint16_t updates=effect_model_updates(0),slopes=effect_model_updates(1);
    assert(effect_model_seed_gain(1450));
    assert(effect_model_gain()==1450 && effect_model_bias()==bias &&
           effect_model_updates(0)==updates && effect_model_updates(1)==slopes);
    assert((int16_t)effect_read(319,&m,demand,480000)==trim && effect_read(346,&m,demand,480000)==1);
    puts("PASS two-loop fine correction: quantization deadband, bounded frequency trim, no integrated actuator gas");
}
static void renewal_test(void){
    uint8_t type,p[16],reply[16]={0};
    /* A guard read owns the wire while the already-applied mission renews. */
    reset();cmd[5]=90;start();now+=60000;
    assert(ctl_next(&type,p,now) && type==0x42 && p[0]==0x28);
    assert(ctl_read(256)==3 && ctl_read(258)==1 && !flow_sets);
    unsigned action=ctl_read(278),actions_count=ctl_read(279),wire_phase=ctl_read(280);
    now+=5000;cmd[1]=2;assert(!ctl_submit(cmd,now));
    assert(ctl_read(257)==2 && ctl_read(258)==2 && ctl_read(264)==90);
    assert(ctl_read(256)==3 && ctl_read(278)==action && ctl_read(279)==actions_count && ctl_read(280)==wire_phase);
    assert(ctl_read(270)==2950 && !ctl_next(&type,p,now));
    now+=1000;assert(!ctl_submit(cmd,now) && ctl_read(264)==89); /* retry never renews */
    cmd[1]=3;cmd[3]=7000;assert(ctl_submit(cmd,now)==6);cmd[1]=2;cmd[3]=6000;
    now=95000;ctl_tick(now);assert(ctl_read(256)==3 && ctl_read(264)>0);
    reply[0]=0x28;assert(ctl_reply(0x62,reply,16,now));
    /* The manually supplied guard is recorded by the independent pump model. */
    ++guard28;last_guard=0x28;
    until(4);assert(flow_sets==1 && flow==3900 && ctl_read(270)==2950);restore();

    /* Renewal after a SET cannot skip or duplicate its required readback. */
    reset();cmd[5]=90;start();now+=60000;while(!flow_sets)tick();
    now+=1000;assert(ctl_next(&type,p,now) && type==0x42 && p[0]==9);
    assert(ctl_read(256)==3 && ctl_read(347)==3900);
    action=ctl_read(278);actions_count=ctl_read(279);wire_phase=ctl_read(280);
    cmd[1]=2;assert(!ctl_submit(cmd,now));uint32_t renewed_at=now;
    assert(ctl_read(256)==3 && ctl_read(278)==action && ctl_read(279)==actions_count && ctl_read(280)==wire_phase);
    assert(ctl_read(347)==3900 && ctl_read(343)==0 && !ctl_next(&type,p,now));
    memset(reply,0,sizeof reply);reply[0]=9;reply[5]=(uint8_t)(flow>>8);reply[6]=(uint8_t)flow;
    assert(ctl_reply(0x62,reply,16,now));until(4);
    assert(flow_sets==1 && ctl_read(343)==1 && !ctl_read(347) && ctl_read(270)==2950);
    now=renewed_at+90001u;tick();until(0);
    assert(mode==2 && flow==2950 && !ctl_read(261) && ctl_read(260)==7);

    /* Collection suspends a later adjustment but not renewal of its mission. */
    reset();start();now+=60000;tick();fb.ready=0;fb.quality=EF_PENDING;
    tick();tick();assert(ctl_read(256)==4 && ctl_read(258)==1 && !flow_sets);
    cmd[1]=2;assert(!ctl_submit(cmd,now) && ctl_read(258)==2 && ctl_read(270)==2950);
    fb.ready=1;fb.quality=EF_READY;tick();until(4);assert(flow_sets==1);restore();
    puts("PASS P0080 EFFECT in-flight renewal: guard/SET/readback preserved, no early completion/duplicate SET, retry lease, suspended action, expiry restoration");
}
/* Cached sampler quality can lag a fresh native-mode observation within one
   scheduler millisecond. A sent initial MODE_FLOW must still be read back. */
static void entry_transition_test(void){
    reset();cmd[4]=5500;fb.short_w=fb.instant_w=6000;ctl_feedback(&fb);assert(!ctl_submit(cmd,now));
    while(!combined_sets)tick();
    assert(ctl_read(256)==3 && !ctl_read(258));
    fb.mode=actual_mode=0; /* READY cache, fresh native pause: reproduction. */
    for(unsigned i=0;i<30;++i)tick();
    assert(!ctl_read(260) && ctl_read(261) && ctl_read(258)==1);
    assert(mode==1 && flow==2950 && combined_sets==1 && combined26==1 && combined09==1);
    fb.ready=0;fb.quality=EF_WAIT_NATIVE;fb.hz=0;tick();restore();

    /* Exercise transitions before snapshot, between guards, before SET and
       during both combined-command readbacks. No cached state grants a SET. */
    for(unsigned stage=0;stage<6;++stage)for(unsigned transition=0;transition<10;++transition){
        reset();cmd[4]=5500;fb.short_w=fb.instant_w=6000;ctl_feedback(&fb);assert(!ctl_submit(cmd,now));
        if(stage>=1)while(ctl_read(256)!=3)tick();
        if(stage>=2)tick(); /* GET28 guard completed. */
        if(stage>=3)tick(); /* GET26 guard completed. */
        if(stage>=4)tick(); /* Combined SET sent and acknowledged. */
        if(stage>=5)while(!combined26)tick();
        fb.short_w=fb.instant_w=6000;
        switch(transition){
        case 0:fb.ready=0;fb.quality=EF_PENDING;break;
        case 1:fb.ready=0;fb.quality=EF_WARMUP;break;
        case 2:fb.ready=0;fb.quality=EF_WAIT_NATIVE;fb.mode=actual_mode=0;fb.hz=0;break;
        case 3:fb.ready=0;fb.quality=EF_SETTLING;fb.pairs=1;fb.span_ms=0;break;
        case 4:fb.mode=actual_mode=0;break;
        case 5:fb.ready=0;break;
        case 6:fb.pairs=0;break;
        case 7:fb.span_ms=0;break;
        case 8:fb.age_ms=60000;break;
        case 9:fb.mode=actual_mode=1;break; /* Native DHW, cached heating power. */
        }
        for(unsigned i=0;i<30;++i)tick();
        assert(!ctl_read(260) && ctl_read(261) && ctl_read(257)==1);
        assert(ctl_read(270)==2950 && !flow_sets && combined_sets<=1);
        /* Pending data blocks an unsent write; after SET both readbacks finish. */
        if(stage<4 && transition!=2 && transition!=3)assert(!combined_sets && !ctl_read(258));
        if(stage>=4)assert(combined26==1 && combined09==1 && ctl_read(258)==1);
        fb.ready=1;fb.quality=EF_READY;fb.mode=actual_mode=2;fb.hz=30;
        fb.pairs=3;fb.span_ms=20000;fb.age_ms=0;
        for(unsigned i=0;i<500 && (!ctl_read(258) || ctl_read(256)!=4);++i)tick();
        assert(ctl_read(258)==1 && ctl_read(256)==4 && !ctl_read(260));
        assert(mode==1 && flow==2950 && combined_sets==1 && combined26==1 && combined09==1);
        restore();
    }
    /* A suspended initial application cannot renew itself or escape its lease. */
    reset();cmd[4]=5500;fb.short_w=fb.instant_w=6000;ctl_feedback(&fb);cmd[5]=90;assert(!ctl_submit(cmd,now));
    while(ctl_read(256)!=3)tick();fb.mode=actual_mode=0;
    for(unsigned i=0;i<30;++i)tick();
    assert(ctl_read(256)==4 && !ctl_read(258) && ctl_read(261) && !sets);
    cmd[1]=2;assert(ctl_submit(cmd,now)==6);now=90001;tick();until(0);
    assert(ctl_read(260)==7 && !ctl_read(261) && !sets && mode==2 && flow==2950);

    /* The transient classification never relaxes fresh native ownership guards. */
    reset();cmd[4]=5500;fb.short_w=fb.instant_w=6000;ctl_feedback(&fb);assert(!ctl_submit(cmd,now));
    while(ctl_read(256)!=3)tick();tick();fb.mode=actual_mode=0;flags[6]=1;
    for(unsigned i=0;i<20;++i)tick();
    fb.ready=0;fb.quality=EF_WAIT_NATIVE;fb.hz=0;until(0);
    assert(!sets && ctl_read(322)==EFFECT_NATIVE_INHIBIT);
    reset();cmd[4]=5500;fb.short_w=fb.instant_w=6000;ctl_feedback(&fb);assert(!ctl_submit(cmd,now));while(!combined_sets)tick();
    fb.mode=actual_mode=0;power=0;until(0);
    assert(power==0 && mode==2 && flow==2950 && ctl_read(322)==EFFECT_MODE_CHANGED);
    reset();cmd[4]=5500;fb.short_w=fb.instant_w=6000;ctl_feedback(&fb);assert(!ctl_submit(cmd,now));
    while(ctl_read(256)!=3)tick();fb.mode=actual_mode=3;until(0);
    assert(!sets && ctl_read(260)==8);
    puts("PASS initial EFFECT transitions: READY cache/fresh mode race, guards/SET/readbacks, pending/warmup/wait/settling, finite initial lease, native inhibits/power/mode retained");
}
int main(void){
    entry_transition_test();regulator_test();fast_test();startup_test();fine_test();renewal_test();
    reset();for(unsigned i=0;i<8;++i){uint16_t w[8];memcpy(w,cmd,sizeof w);switch(i){case 0:w[3]=999;break;case 1:w[3]=18000;break;case 2:w[4]=2999;break;case 3:w[4]=5501;break;case 4:w[5]=89;break;case 5:w[5]=1801;break;case 6:w[6]=0;break;case 7:w[7]=2;break;}assert(ctl_submit(w,now)==3 && !sets);}
    reset();fb.ready=0;ctl_feedback(&fb);assert(ctl_submit(cmd,0)==6 && !sets);fb.ready=1;fb.pairs=2;ctl_feedback(&fb);assert(ctl_submit(cmd,0)==6);fb.pairs=3;fb.span_ms=19999;ctl_feedback(&fb);assert(ctl_submit(cmd,0)==6);
    reset();start();assert(!ctl_busy());unsigned old=ctl_read(264);assert(!ctl_submit(cmd,now) && ctl_read(264)==old);cmd[1]=2;assert(!ctl_submit(cmd,now) && sets==1);cmd[1]=3;cmd[3]=7000;assert(!ctl_submit(cmd,now));
    assert(ctl_read(323)==7000 && ctl_read(258)==3 && ctl_read(269)==2 && ctl_read(270)==2950 && sets==1);
    cmd[1]=4;cmd[3]=6000;assert(!ctl_submit(cmd,now));
    advance();assert(flow==3900 && ctl_read(270)==2950 && flow_sets==1);advance();assert(flow<=4000 && ctl_read(270)==2950);restore();assert(ctl_read(321)==EFFECT_OFF);
    reset();fb.age_ms=60000;ctl_feedback(&fb);assert(ctl_submit(cmd,now)==6);
    reset();start();fb.age_ms=59999;unsigned aged_before=flow;advance();
    assert(flow_sets==1 && flow>aged_before && flow-aged_before<=50);restore();
    reset();start();fb.ready=0;fb.quality=EF_WARMUP;
    for(unsigned i=0;i<400;++i)tick();
    assert(ctl_read(256)==4 && sets==1 && !ctl_read(260));
    fb.ready=1;fb.quality=EF_READY;advance();assert(flow_sets==1);restore();
    reset();start();drop_ack=1;advance();assert(flow==3900 && ctl_read(258)==1);restore();
    reset();start();flags[6]=1;now+=60000;tick();until(0);assert(flow_sets==0 && mode==2 && ctl_read(286)==(1u<<6));
    reset();start();actual_mode=fb.mode=1;fb.ready=0;fb.quality=EF_DHW;advance();assert(mode==1 && !flow_sets && ctl_read(261));restore();
    reset();start();fb.ready=0;fb.quality=EF_INVALID;advance();assert(!flow_sets && ctl_read(261));restore();
    reset();start();now=900001;tick();until(0);assert(mode==2 && ctl_read(260)==7 && ctl_read(322)==EFFECT_LEASE_EXPIRED);
    reset();start();fail_set=1;now+=60000;tick();until(6);assert(ctl_read(261));fail_set=0;now+=5000;tick();until(0);assert(mode==2 && flow==2950);
    reset();power=0;assert(!ctl_submit(cmd,0));until(0);assert(!sets);
    reset();flow=4100;assert(!ctl_submit(cmd,0));until(0);assert(!sets);
    reset();drop_ack=1;start();restore();
    /* A combined startup's mode readback alone never means applied. */
    reset();fb.short_w=fb.instant_w=6000;ctl_feedback(&fb);assert(!ctl_submit(cmd,now));while(!combined26)tick();
    assert(ctl_read(256)==3 && !ctl_read(258) && (ctl_read(262)&12)==12);
    {uint8_t ty,p[16],wrong[16]={9};wrong[5]=0x0f;wrong[6]=0xa0;
     for(unsigned i=0;i<3;++i){assert(ctl_next(&ty,p,now));assert(p[0]==9);assert(ctl_reply(0x62,wrong,16,now));now+=1000;}}
    assert(ctl_read(256)==5 && ctl_read(261));until(0);assert(mode==2 && flow==2950 && ctl_read(322)==EFFECT_READBACK_MISMATCH);
    /* Partial pairs yield the bus, then resume the same guarded adjustment. */
    reset();start();fb.ready=0;fb.quality=EF_PENDING;now+=60000;tick();assert(ctl_read(256)==4 && !ctl_busy() && !flow_sets);
    fb.ready=1;fb.quality=EF_READY;tick();assert(ctl_read(256)==3);
    fb.ready=0;fb.quality=EF_PENDING;tick();tick();assert(ctl_read(256)==4 && !ctl_busy() && !flow_sets);
    fb.ready=1;fb.quality=EF_READY;tick();until(4);assert(flow==3900 && flow_sets==1);restore();
    reset();fb.short_w=fb.instant_w=fb.slow_w=INT32_MIN;fb.age_ms=UINT32_MAX;ctl_feedback(&fb);
    assert(ctl_read(331)==0x8000 && ctl_read(332)==0 && ctl_read(336)==65535);
    reset();start();{uint8_t p[16]={0x28};p[4]=1;ctl_observe(p,now);}tick();until(0);assert(!flow_sets);
    reset();start();fb.instant_w=fb.short_w=fb.slow_w=0;fb.ready=0;fb.quality=EF_ZEROFLOW;advance();assert(!flow_sets && ctl_read(261));restore();
    reset();start();ctl_init();assert(!ctl_busy() && !ctl_read(261) && !ctl_read(282) && ctl_read(350)==1 && !ctl_read(351));
    /* A long native pause may renew, but cannot escape lease expiry. */
    reset();fb.ready=0;fb.quality=EF_WAIT_NATIVE;fb.mode=actual_mode=0;fb.hz=0;start();
    unsigned pause_sets=sets;
    for(unsigned i=0;i<13;++i){now+=100000;cmd[1]++;assert(!ctl_submit(cmd,now));tick();assert(ctl_read(256)==4 && sets==pause_sets && !ctl_read(346));}
    assert(ctl_read(270)==2950);now+=900001;tick();until(0);assert(ctl_read(322)==EFFECT_LEASE_EXPIRED);
    /* Discard unsent acceleration if the compressor stops mid-guard. */
    reset();start();now+=60000;tick();fb.ready=0;fb.quality=EF_WAIT_NATIVE;fb.mode=actual_mode=0;fb.hz=0;
    tick();tick();assert(ctl_read(256)==4 && !flow_sets && !ctl_read(347));
    fb.ready=1;fb.quality=EF_READY;fb.mode=actual_mode=2;fb.hz=30;tick();advance();assert(flow_sets==1);restore();
    /* A sent adjustment completes readback before waiting. */
    reset();start();now+=60000;while(!flow_sets)tick();
    fb.ready=0;fb.quality=EF_WAIT_NATIVE;fb.mode=actual_mode=0;fb.hz=0;until(4);
    assert(ctl_read(344)>500 && !ctl_read(347) && !ctl_read(346));restore();
    reset();fb.short_w=fb.instant_w=6000;ctl_feedback(&fb);assert(!ctl_submit(cmd,now));while(ctl_read(256)!=3)tick();
    fb.ready=0;fb.quality=EF_PENDING;tick();assert(ctl_read(256)==4 && !ctl_read(258));
    cmd[1]=2;assert(ctl_submit(cmd,now)==6);cmd[1]=1;
    fb.ready=1;fb.quality=EF_READY;tick();until(4);restore();
    reset();now=0xffff0000u;start();fb.ready=0;fb.quality=EF_WAIT_NATIVE;fb.mode=actual_mode=0;fb.hz=0;tick();
    now+=600000;tick();assert(ctl_read(256)==4 && !flow_sets);restore();
    /* Pause demand follows supply without the old cumulative +5C latch. */
    reset();fb.ready=0;fb.quality=EF_WAIT_NATIVE;fb.mode=actual_mode=0;fb.hz=0;fb.supply_cC=3300;start();assert(flow==3350);
    for(unsigned supply=3400;supply<=3700;supply+=100){fb.supply_cC=(int32_t)supply;advance();assert(flow==supply+50 && !ctl_read(346));}
    assert(ctl_read(344)>500 && ctl_read(322)!=EFFECT_CUMULATIVE_CAP);restore();
    reset();cmd[4]=3000;fb.ready=0;fb.quality=EF_WAIT_NATIVE;fb.mode=actual_mode=0;fb.hz=0;fb.supply_cC=3300;start();assert(flow==3000);advance();assert(flow==3000);restore();
    reset();start();fb.ready=0;fb.quality=EF_WAIT_NATIVE;fb.mode=actual_mode=0;tick();
    {uint8_t p[16]={0x26};p[3]=0;p[6]=1;ctl_observe(p,now);}tick();until(0);assert(ctl_read(322)==EFFECT_MODE_CHANGED);
    puts("PASS P0080 unified EFFECT: bounded startup at every cap, no cumulative latch, snapshot/guards/readback/renewal, persistent DHW/feedback/native pause, lease restoration and reboot uncertainty");
}
