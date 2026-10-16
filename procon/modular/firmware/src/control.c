/* P0072 r3. Independently encoded reference-backed controls; hardware trial pending. */
#include "control.h"
#include "effect.h"
#include "effect_feedback.h"
enum { IDLE, QUEUED, SNAPSHOT, APPLY, ACTIVE, RESTORE, RESTORE_BLOCKED };
enum { POWER=1, MODE, FLOW, DHW_TARGET, BOOST, MODE_FLOW };
typedef struct { uint16_t power,mode,flow,dhw,boost; } settings;
typedef struct { uint8_t field; uint16_t value; } action;
/* Private state: one bounded reset, no exported layout. */
typedef struct {
    settings original,current;
    action actions[5];
    uint16_t command[8], accepted,applied,rejected,error,acks,readbacks,restores;
    uint8_t state,saved,touched,n_actions,index_action,phase,retries,snapshot_step,waiting;
    uint32_t now_ms,lease_at,lease_ms,retry_at;
    uint8_t inflight_type,inflight_query,settling,flow_prepared;
    uint32_t settle_at;
    uint8_t raw28[16],seen28,reject_byte,reject_value;
    uint16_t generation28,blocked28,relevant28;
    uint32_t age28,diag_tick;
    effect_measurement feedback;
    uint8_t effect_session,effect_prepared,effect_abort,effect_suspended;
    uint16_t effect_abort_reason;
/* P0080: direct target replacement preserves the first session snapshot. */
    uint8_t retarget,native_mode;
    uint16_t retarget_from;
    uint8_t effect_recover;
} control_state;
static control_state controller;
/* P0080: every EFFECT cap uses the same persistent session policy. */
static int soft_lower(void){return controller.effect_session && controller.index_action<controller.n_actions && controller.actions[controller.index_action].field==FLOW && controller.actions[controller.index_action].value<=EFFECT_NATIVE_RESTART_CC && controller.actions[controller.index_action].value<controller.current.flow;}
static void recover_wait(void){
    controller.waiting=controller.settling=controller.phase=controller.retries=controller.effect_prepared=controller.flow_prepared=controller.effect_suspended=0;
    controller.n_actions=controller.index_action=0;effect_discard_pending();controller.state=ACTIVE;controller.effect_recover=1;
    effect_wait(EF_WAIT_NATIVE,controller.now_ms);
}
static int effect_waiting(void){return controller.feedback.quality==EF_WAIT_NATIVE || controller.feedback.quality==EF_SETTLING;}
static int native_heat_or_pause(unsigned m){return m==0 || m==2 || m==7 || (controller.effect_session && (m==1 || m==6));}
static int effect_mode_matches(unsigned m){
    unsigned expected=(controller.touched&(1u<<MODE))?1:controller.original.mode;
    if(m==expected)return 1;
    return controller.applied!=controller.accepted && m==controller.original.mode &&
        (controller.effect_recover || (controller.state==APPLY && controller.index_action<controller.n_actions && controller.actions[controller.index_action].field==MODE_FLOW));
}
static int gate28(const uint8_t *p);
static int heating(unsigned mode){return mode==2 || mode==7;}
static int effect_feedback_ok(void){return controller.feedback.ready && controller.feedback.pairs>=3 && controller.feedback.span_ms>=20000u && controller.feedback.age_ms<60000u && heating(controller.feedback.mode);}
/* The sampler and native mode can update in the same scheduler millisecond.
   A cached READY report is not a hard fault when newer telemetry no longer
   qualifies it. Yield unsent work; preserve sent readback and native guards. */
static int effect_collecting(void){
    return controller.feedback.quality==EF_PENDING || controller.feedback.quality==EF_WARMUP ||
        (controller.effect_session && ((controller.feedback.quality>=EF_STALE && controller.feedback.quality<=EF_LINKLOSS) ||
         (controller.feedback.quality==EF_READY && native_heat_or_pause(controller.feedback.mode) && !effect_feedback_ok())));
}
static int pause_demand_ok(void){
    unsigned kind=effect_pending_demand();
    if(kind==1)return controller.feedback.quality==EF_WAIT_NATIVE && controller.feedback.hz<255;
    return kind==2 && controller.effect_session &&
        (controller.feedback.quality==EF_SETTLING || effect_feedback_ok()) &&
        controller.feedback.pairs>=1 && controller.feedback.age_ms<15000u && heating(controller.feedback.mode) &&
        controller.feedback.hz>0 && controller.feedback.hz<255 && controller.feedback.supply_cC>=0 && controller.feedback.supply_cC<=10000;
}
void ctl_feedback(const effect_measurement *m){controller.feedback=*m;}
void ctl_link_lost(uint32_t t){
    controller.now_ms=t;
    if(controller.effect_session && controller.saved && controller.state!=RESTORE && controller.state!=RESTORE_BLOCKED){recover_wait();return;}
    if(controller.effect_session){controller.effect_abort=1;controller.effect_abort_reason=EFFECT_LINK_LOST;}
}
void ctl_observe(const uint8_t p[16],uint32_t t){
    if(p[0]==0x26 && controller.effect_session && (controller.state==ACTIVE || controller.state==APPLY)){
        if(p[3]!=1 || !effect_mode_matches(p[6]) || !native_heat_or_pause(p[4])){
            controller.effect_abort=1;controller.effect_abort_reason=EFFECT_MODE_CHANGED;
        }
    }
    if(p[0]!=0x28)return;
    for(unsigned i=0;i<16;++i)controller.raw28[i]=p[i];
    controller.seen28=1;++controller.generation28;controller.age28=0;controller.diag_tick=t;
    if(controller.effect_session && controller.state!=RESTORE && controller.state!=RESTORE_BLOCKED &&
       (!gate28(p) || p[3]!=0)){controller.effect_abort=1;controller.effect_abort_reason=EFFECT_NATIVE_INHIBIT;}
}
static int gate28(const uint8_t *p){
    controller.relevant28=(1u<<4)|(1u<<10); /* holiday and external server ownership */
    if(controller.command[2]==2 || (controller.command[6]&1))controller.relevant28|=1u<<6;
    if(controller.command[2]==3 || (controller.command[6]&2))controller.relevant28|=1u<<5;
    controller.blocked28=0;controller.reject_byte=controller.reject_value=0;
    for(unsigned i=4;i<=10;++i){
        /* Unknown encodings remain a failure, including unrelated flags. */
        if(p[i]>1 || (p[i] && (controller.relevant28&(1u<<i)))){
            controller.blocked28|=(uint16_t)(1u<<i);
            if(!controller.reject_byte){controller.reject_byte=(uint8_t)i;controller.reject_value=p[i];}
        }
    }
    return !controller.blocked28;
}
static uint16_t be(const uint8_t *p){return (uint16_t)((p[0]<<8)|p[1]);}
static void word(uint8_t *p,uint16_t v){p[0]=(uint8_t)(v>>8);p[1]=(uint8_t)v;}
static int equal_intent(const uint16_t *w){return w[0]==controller.command[0] && w[7]==controller.command[7] && w[2]==controller.command[2] && w[3]==controller.command[3] && w[4]==controller.command[4] && w[6]==controller.command[6];}
static void add(unsigned f,unsigned v){controller.actions[controller.n_actions++]=(action){(uint8_t)f,(uint16_t)v};}
static void restore_plan(void){
    controller.retarget=0;controller.effect_recover=0;
    controller.n_actions=controller.index_action=controller.phase=controller.retries=controller.waiting=0;
    /* Restore target while fixed mode still applies, then native mode last. */
    if(controller.touched&(1u<<FLOW))add(FLOW,controller.original.flow);
    if(controller.touched&(1u<<DHW_TARGET))add(DHW_TARGET,controller.original.dhw);
    if(controller.touched&(1u<<BOOST))add(BOOST,controller.original.boost);
    if(controller.touched&(1u<<POWER))add(POWER,controller.original.power);
    if(controller.touched&(1u<<MODE))add(MODE,controller.original.mode);
    controller.state=RESTORE;controller.settling=controller.flow_prepared=controller.effect_prepared=controller.effect_suspended=0;
    if(controller.effect_session)effect_stop(controller.effect_abort_reason?controller.effect_abort_reason:EFFECT_ABORTED,1);
}
static void fail(uint16_t why){
    if(controller.effect_session && controller.saved && why==4 && controller.state!=RESTORE && controller.state!=RESTORE_BLOCKED){recover_wait();return;}
    controller.error=why;controller.waiting=0;
    if(controller.effect_session && !controller.effect_abort_reason)
        controller.effect_abort_reason=why==4?EFFECT_READ_TIMEOUT:why==5?EFFECT_READBACK_MISMATCH:EFFECT_NATIVE_INHIBIT;
    if(controller.state==RESTORE || controller.state==RESTORE_BLOCKED){controller.state=RESTORE_BLOCKED;controller.retry_at=controller.now_ms;return;}
    if(controller.saved && controller.touched)restore_plan();
    else {controller.state=IDLE;controller.saved=0;if(controller.effect_session)effect_stop(controller.effect_abort_reason?controller.effect_abort_reason:EFFECT_NATIVE_INHIBIT,0);controller.effect_session=0;}
}
void ctl_init(void){
    controller=(control_state){0};controller.age28=65535000u;effect_init();
}

uint8_t ctl_submit(const uint16_t w[8],uint32_t now){
    controller.now_ms=now;
    int v3=w[0]==0xc076 && w[7]==3;
    if(!w[1])goto invalid;
    if(v3){
        if(w[2]!=5 || w[3]<1000 || w[3]>12000 || w[4]<3000 || w[4]>5500 ||
           w[5]<90 || w[5]>1800 || w[6]!=1)goto invalid;
    }else{
    if(w[0]!=0xc072 || w[7]!=2 || w[2]>4 || w[6]>3)goto invalid;
    if(w[2]==1){if(w[3]||w[4]||w[5]||w[6])goto invalid;}
    else {
        if(w[5]<30 || w[5]>1800)goto invalid;
        if((w[6]&1)?(w[3]<2000 || w[3]>MANUAL_FLOW_MAX_CC):w[3]!=0)goto invalid;
        if((w[6]&2)?(w[4]<4000 || w[4]>6000):w[4]!=0)goto invalid;
        if(w[2]==2 && !(w[6]&1))goto invalid;
        if(w[2]==4 && !w[6])goto invalid;
        if((w[2]==0 || w[2]==3) && (w[6]&1))goto invalid;
    }
    }
    if(w[1]==controller.accepted){
        for(unsigned i=0;i<8;++i)if(w[i]!=controller.command[i])goto invalid;
        return 0; /* retry of same controller.accepted packet never extends lease */
    }
    if(w[1]!=(uint16_t)(controller.accepted==65535?1:controller.accepted+1))goto invalid;
    if(w[2]==1){
        if(!controller.saved || controller.waiting || (controller.state!=ACTIVE && controller.state!=RESTORE_BLOCKED))goto busy;
        for(unsigned i=0;i<8;++i)controller.command[i]=w[i];
        controller.accepted=w[1];controller.error=0;controller.effect_abort_reason=EFFECT_ABORTED;restore_plan();return 0;
    }
    /* An internal EFFECT adjustment does not revoke an controller.applied mission.
       Renew its lease without disturbing the controller.current SET/readback transaction.
       Initial application must still finish before it can be renewed. */
    if(((controller.state==ACTIVE && (!controller.effect_suspended || controller.applied==controller.accepted)) ||
        (controller.state==APPLY && controller.effect_session && controller.saved && controller.applied==controller.accepted)) && equal_intent(w)){
        for(unsigned i=0;i<8;++i)controller.command[i]=w[i];
        controller.accepted=controller.applied=w[1];controller.lease_at=now;controller.lease_ms=(uint32_t)w[5]*1000u;return 0;
    }
    /* P0080: replace EFFECT goal without AUTO or losing the controller.original snapshot. */
    if(v3 && controller.effect_session && controller.state==ACTIVE && controller.saved && !controller.waiting && !controller.effect_suspended &&
       controller.applied==controller.accepted && !controller.effect_abort){
        for(unsigned i=0;i<8;++i)controller.command[i]=w[i];
        effect_retarget(w[3],w[4],now);
        controller.accepted=controller.applied=w[1];controller.error=0;controller.lease_at=now;controller.lease_ms=(uint32_t)w[5]*1000u;return 0;
    }
    if(controller.state==ACTIVE && controller.saved && !controller.waiting && !controller.effect_session && !v3 &&
       controller.command[2]==2 && controller.command[6]==1 && w[2]==2 && w[6]==1){
        controller.retarget_from=controller.command[3];controller.retarget=1;
        for(unsigned i=0;i<8;++i)controller.command[i]=w[i];
        controller.accepted=w[1];controller.error=0;controller.lease_at=now;controller.lease_ms=(uint32_t)w[5]*1000u;
        controller.snapshot_step=controller.n_actions=controller.index_action=controller.phase=controller.retries=controller.waiting=controller.settling=controller.flow_prepared=0;
        controller.blocked28=controller.relevant28=0;controller.reject_byte=controller.reject_value=0;controller.state=SNAPSHOT;return 0;
    }
    if(controller.state!=IDLE || controller.saved)goto busy;
    if(v3 && !effect_feedback_ok() && !effect_waiting())goto busy;
    controller.retarget=0;controller.effect_recover=0;controller.effect_session=(uint8_t)v3;controller.effect_abort=controller.effect_prepared=controller.effect_suspended=0;controller.effect_abort_reason=0;
    if(v3)effect_begin(w[3],w[4],now);
    for(unsigned i=0;i<8;++i)controller.command[i]=w[i];
    controller.accepted=w[1];controller.error=0;controller.lease_at=now;controller.lease_ms=(uint32_t)w[5]*1000u;
    controller.blocked28=controller.relevant28=0;controller.reject_byte=controller.reject_value=0;
    controller.touched=0;controller.snapshot_step=controller.retries=controller.waiting=0;controller.state=QUEUED;return 0;
invalid:controller.rejected=w[1];controller.error=1;return 3;
busy:controller.rejected=w[1];controller.error=2;return 6;
}
void ctl_tick(uint32_t t){
    uint32_t dt=t-controller.diag_tick;controller.diag_tick=t;
    if(controller.seen28)controller.age28=dt>=65535000u-controller.age28?65535000u:controller.age28+dt;
    controller.now_ms=t;
    if((controller.state==QUEUED || controller.state==SNAPSHOT || controller.state==APPLY || controller.state==ACTIVE) && t-controller.lease_at>=controller.lease_ms){
        /* Never interrupt a wire transaction; expiration is processed after it. */
        if(!controller.waiting){if(controller.saved && controller.touched){controller.error=7;controller.effect_abort_reason=EFFECT_LEASE_EXPIRED;restore_plan();}else{controller.state=IDLE;controller.saved=0;controller.error=7;if(controller.effect_session)effect_stop(EFFECT_LEASE_EXPIRED,0);controller.effect_session=0;}}
    }
    if(controller.effect_session && (controller.state==QUEUED || controller.state==SNAPSHOT || controller.state==APPLY || controller.state==ACTIVE)){
        if(controller.feedback.quality>=EF_STALE && controller.feedback.quality<=EF_LINKLOSS)effect_wait(EF_WAIT_NATIVE,t);
        if(effect_waiting())effect_wait(controller.feedback.quality,t);
        if(!effect_feedback_ok() && !effect_collecting() && !effect_waiting()){controller.effect_abort=1;if(!controller.effect_abort_reason)controller.effect_abort_reason=EFFECT_BAD_FEEDBACK;}
        if(controller.effect_abort && !controller.waiting)fail(8);
    }
    if(controller.state==RESTORE_BLOCKED && !controller.waiting && t-controller.retry_at>=5000u)restore_plan();
    /* Ordinary partial FAST pairs must yield the bus, not starve GET14/26.
       Preserve the pending action but require fresh guards when it resumes. */
    if(controller.effect_session && controller.state==APPLY && controller.index_action<controller.n_actions && !controller.waiting && controller.phase==0){
        int discard=controller.actions[controller.index_action].field!=MODE_FLOW &&
            ((effect_waiting() && !pause_demand_ok()) || (effect_pending_demand() && !pause_demand_ok()));
        if(discard){
            controller.n_actions=controller.index_action=0;controller.effect_suspended=controller.effect_prepared=controller.flow_prepared=0;
            effect_discard_pending();controller.state=ACTIVE;
        }else if(effect_collecting() && !soft_lower()){
            controller.effect_suspended=1;controller.effect_prepared=controller.flow_prepared=0;controller.state=ACTIVE;
        }
    }
    if(controller.effect_session && controller.state==ACTIVE && controller.effect_suspended && effect_waiting()){
        if(controller.actions[controller.index_action].field==MODE_FLOW){
            if(effect_entry_demand(&controller.feedback,controller.current.flow,controller.native_mode,t)){controller.effect_suspended=0;controller.state=APPLY;}
        }else if(pause_demand_ok()){controller.effect_suspended=0;controller.state=APPLY;}
        else {controller.n_actions=controller.index_action=0;controller.effect_suspended=0;effect_discard_pending();}
    }
    if(controller.effect_session && controller.state==ACTIVE && controller.effect_suspended && effect_feedback_ok()){
        controller.effect_suspended=0;controller.state=APPLY;
    }
    if(controller.effect_session && controller.state==ACTIVE && controller.effect_recover && effect_feedback_ok()){
        controller.snapshot_step=controller.retries=controller.waiting=0;controller.state=SNAPSHOT;
    }
    /* Power can be unavailable while native heating guards are still readable.
       Only reduce an existing boost; never increase on degraded feedback.
       WAIT_NATIVE and SETTLING have their own bounded demand policy below. */
    if(controller.effect_session && controller.state==ACTIVE && !controller.waiting && effect_collecting() &&
       controller.feedback.quality>=EF_STALE && controller.feedback.quality<=EF_ZEROFLOW &&
       heating(controller.feedback.mode) && controller.current.flow>EFFECT_NATIVE_RESTART_CC){
        effect_discard_pending();controller.effect_suspended=controller.effect_prepared=controller.flow_prepared=0;
        controller.n_actions=controller.index_action=controller.phase=controller.retries=0;add(FLOW,EFFECT_NATIVE_RESTART_CC);controller.state=APPLY;
    }
    if(controller.effect_session && controller.state==ACTIVE && !controller.effect_abort && !controller.effect_suspended && !controller.effect_recover){
        uint16_t next=effect_feedback_ok()?effect_decide(&controller.feedback,controller.current.flow,t):
            effect_pause_demand(&controller.feedback,controller.current.flow,t);
        if(next){controller.n_actions=controller.index_action=controller.phase=controller.retries=controller.effect_prepared=controller.flow_prepared=0;add(FLOW,next);controller.state=APPLY;}
    }
}
int ctl_busy(void){return controller.state==QUEUED || controller.state==SNAPSHOT || controller.state==APPLY || controller.state==RESTORE || controller.state==RESTORE_BLOCKED;}
static void apply_plan(void){
    controller.n_actions=controller.index_action=controller.phase=controller.retries=controller.flow_prepared=0;
    if(controller.effect_session){
        effect_capture(controller.current.flow,controller.now_ms);
        if(controller.current.mode!=1)add(MODE_FLOW,controller.current.flow);
        /* Atomic native flags 0x08|0x80 prevent exposing a hidden fixed target.
           Verify both mode (GET26) and target (GET09) before ACTIVE. */
        controller.state=APPLY;return;
    }
    if(controller.command[2]==2 && controller.current.mode!=1)add(MODE,1);
    if(controller.command[6]&1)add(FLOW,controller.command[3]);
    if(controller.command[6]&2)add(DHW_TARGET,controller.command[4]);
    if(controller.command[2]==3)add(BOOST,1);
    if(controller.command[2]==0)add(POWER,0);
    if((controller.command[2]==2 || controller.command[2]==3) && controller.current.power!=1)add(POWER,1);
    controller.state=APPLY;
}
static unsigned query_for(unsigned f){return f==FLOW?9:f==BOOST?0x28:0x26;}
int ctl_next(uint8_t *type,uint8_t p[16],uint32_t t){
    ctl_tick(t);
    if(controller.settling){if(t-controller.settle_at<1000u)return 0;controller.settling=0;}
    if(controller.waiting || controller.state==RESTORE_BLOCKED || !ctl_busy())return 0;
    for(unsigned i=0;i<16;++i)p[i]=0;
    if(controller.state==QUEUED)controller.state=SNAPSHOT;
    if(controller.state==SNAPSHOT){static const uint8_t q[]={0x26,9,0x28};*type=0x42;p[0]=q[controller.snapshot_step];}
    else {
        if(controller.index_action>=controller.n_actions){
            if(controller.state==RESTORE){++controller.restores;controller.saved=controller.touched=0;controller.state=IDLE;if(controller.command[2]==1)controller.applied=controller.accepted;if(controller.effect_session){effect_restored();controller.effect_session=controller.effect_abort=0;}}
            else {controller.state=ACTIVE;controller.applied=controller.accepted;if(controller.effect_session)effect_verified(controller.current.flow,t);}
            return 0;
        }
        action a=controller.actions[controller.index_action];
        if(controller.effect_session && controller.state==APPLY && !controller.effect_prepared && controller.phase!=1 && controller.phase!=4){
            *type=0x42;p[0]=controller.phase==2?0x26:0x28;if(controller.phase!=2)controller.phase=3;
        }
        else if(a.field==FLOW && !controller.flow_prepared && controller.phase!=1){*type=0x42;p[0]=0x26;controller.phase=2;}
        else if(controller.phase){*type=0x42;p[0]=(uint8_t)(a.field==MODE_FLOW && controller.phase==4?9:query_for(a.field));}
        else {
            if(controller.effect_session && controller.state==APPLY && !effect_feedback_ok() && !(a.field==MODE_FLOW && effect_waiting()) && !pause_demand_ok() && !soft_lower()){
                controller.effect_abort_reason=EFFECT_BAD_FEEDBACK;fail(8);return 0;
            }
            if(controller.effect_session && controller.state==APPLY && a.field==MODE_FLOW){
                a.value=effect_entry_demand(&controller.feedback,controller.current.flow,controller.native_mode,t);
                if(!a.value){controller.effect_suspended=1;controller.effect_prepared=controller.flow_prepared=0;controller.state=ACTIVE;return 0;}
                controller.actions[controller.index_action]=a; /* Freeze this exact target once sent. */
            }
            *type=0x41;p[0]=a.field==BOOST?0x34:0x32;
            switch(a.field){
            case POWER:p[1]=1;p[3]=(uint8_t)a.value;break;
            case MODE:p[1]=8;p[6]=(uint8_t)a.value;break;
            case MODE_FLOW:p[1]=0x88;p[2]=0;p[6]=1;word(p+8,controller.current.dhw);word(p+10,a.value);break;
            case FLOW:p[1]=0x80;p[2]=0;p[6]=(uint8_t)controller.current.mode;word(p+8,controller.current.dhw);word(p+10,a.value);break;
            case DHW_TARGET:p[1]=0x20;word(p+8,a.value);break;
            case BOOST:p[1]=1;p[3]=(uint8_t)a.value;break;
            }
            /* Even an unacknowledged combined write may apply both dimensions. */
            controller.touched|=a.field==MODE_FLOW?(uint8_t)((1u<<MODE)|(1u<<FLOW)):(uint8_t)(1u<<a.field);
        }
    }
    controller.waiting=1;controller.inflight_type=*type;controller.inflight_query=p[0];return 1;
}
static int update(const uint8_t *p){
    switch(p[0]){
    case 0x26:
        if(p[3]>1 || p[6]>2 || be(p+8)<4000 || be(p+8)>6000)return 0;
        controller.current.power=p[3];controller.current.mode=p[6];controller.current.dhw=be(p+8);controller.native_mode=p[4];break;
    case 9:if(be(p+5)<2000 || be(p+5)>MANUAL_FLOW_MAX_CC)return 0;controller.current.flow=be(p+5);break;
    case 0x28:if(p[3]>1)return 0;controller.current.boost=p[3];break;
    default:return 0;
    }
    return 1;
}
static uint16_t actual(unsigned field){
    switch(field){case POWER:return controller.current.power;case MODE:return controller.current.mode;case FLOW:return controller.current.flow;case DHW_TARGET:return controller.current.dhw;default:return controller.current.boost;}
}
int ctl_reply(uint8_t type,const uint8_t *p,unsigned len,uint32_t t){
    controller.now_ms=t;if(!controller.waiting)return 0;
    if(controller.inflight_type==0x41){
        if(type!=0x61)return 0;
        ++controller.acks;controller.waiting=0;controller.phase=1;controller.retries=0;controller.settling=1;controller.settle_at=t;return 1; /* generic hint only */
    }
    if(type!=0x62 || len!=16 || p[0]!=controller.inflight_query)return 0;
    controller.waiting=0;++controller.readbacks;
    ctl_observe(p,t);
    if(!update(p)){fail(3);return 1;}
    if(controller.effect_session && controller.state==APPLY && p[0]==0x26 && (controller.current.power!=1 || !native_heat_or_pause(p[4]))){
        controller.effect_abort_reason=EFFECT_MODE_CHANGED;fail(8);return 1;
    }
    if(controller.state==SNAPSHOT){
        if(controller.retarget && ((p[0]==0x26 && (controller.current.power!=1 || controller.current.mode!=1 || !native_heat_or_pause(p[4]))) ||
                       (p[0]==9 && controller.current.flow!=controller.retarget_from) || (p[0]==0x28 && controller.current.boost))){fail(3);return 1;}
        if(p[0]==0x28 && !gate28(p)){controller.effect_abort_reason=EFFECT_NATIVE_INHIBIT;fail(3);return 1;}
        if(controller.effect_session && ((p[0]==0x26 && (controller.current.power!=1 || !native_heat_or_pause(p[4]))) ||
            (p[0]==9 && controller.current.flow>controller.command[4]) || (p[0]==0x28 && controller.current.boost))){
            controller.effect_abort_reason=EFFECT_MODE_CHANGED;fail(8);return 1;
        }
        /* Recovery may repeat an interrupted initial combined entry, but must
           never silently reclaim an operator's mode change after activation. */
        if(controller.effect_recover && p[0]==0x26){
            int mode_ok=controller.applied==controller.accepted?controller.current.mode==1:
                (controller.current.mode==controller.original.mode || ((controller.touched&(1u<<MODE)) && controller.current.mode==1));
            if(!mode_ok){controller.effect_abort_reason=EFFECT_MODE_CHANGED;fail(8);return 1;}
        }
        controller.retries=0;
        if(++controller.snapshot_step==3){
            if(controller.effect_recover){
                controller.effect_recover=0;controller.error=0;controller.n_actions=controller.index_action=controller.phase=controller.retries=0;
                effect_discard_pending();
                if(controller.current.mode!=1){add(MODE_FLOW,controller.current.flow);controller.state=APPLY;}
                else {controller.state=ACTIVE;controller.applied=controller.accepted;effect_verified(controller.current.flow,t);}
            }else if(controller.retarget){controller.n_actions=controller.index_action=controller.phase=controller.retries=controller.flow_prepared=0;add(FLOW,controller.command[3]);controller.state=APPLY;}
            else {controller.original=controller.current;controller.saved=1;apply_plan();}
        }
    }else if(controller.effect_session && controller.state==APPLY && controller.phase==3){
        if(!gate28(p) || controller.current.boost){controller.effect_abort_reason=EFFECT_NATIVE_INHIBIT;fail(3);return 1;}
        controller.phase=2;controller.retries=0;
    }else if(controller.phase==2){
        if(controller.retarget && controller.state==APPLY && (controller.current.power!=1 || controller.current.mode!=1 || !native_heat_or_pause(p[4]))){fail(3);return 1;}
        if(controller.effect_session && controller.state==APPLY){
            if(controller.current.power!=1 || !native_heat_or_pause(p[4]) || !effect_mode_matches(controller.current.mode) || (!effect_feedback_ok() && !effect_collecting() && !effect_waiting())){
                controller.effect_abort_reason=EFFECT_MODE_CHANGED;fail(8);return 1;
            }
            controller.effect_prepared=1;
        }
        controller.flow_prepared=1;controller.phase=controller.retries=0;
    }
    else if(controller.actions[controller.index_action].field==MODE_FLOW && controller.phase==1 && controller.current.mode==1){
        controller.phase=4;controller.retries=0; /* mode alone is insufficient proof of bounded flow */
    }
    else if((controller.actions[controller.index_action].field==MODE_FLOW && controller.phase==4 && controller.current.flow==controller.actions[controller.index_action].value) ||
            (controller.actions[controller.index_action].field!=MODE_FLOW && actual(controller.actions[controller.index_action].field)==controller.actions[controller.index_action].value)){++controller.index_action;controller.phase=controller.retries=controller.flow_prepared=controller.effect_prepared=0;}
    else if(++controller.retries>=3)fail(5);
    else {controller.settling=1;controller.settle_at=t;}
    return 1;
}
void ctl_timeout(uint32_t t){
    controller.now_ms=t;if(!controller.waiting)return;controller.waiting=0;
    if(controller.inflight_type==0x41){controller.phase=1;controller.retries=0;controller.settling=1;controller.settle_at=t;return;} /* verify possible controller.applied write */
    if(++controller.retries>=3)fail(4);
}
uint16_t ctl_read(unsigned a){
    if((a>=300 && a<=319) || (a>=320 && a<=351))return effect_read(a,&controller.feedback,controller.current.flow,controller.now_ms);
    if(a>=288 && a<=295){unsigned i=2*(a-288);return (uint16_t)(controller.raw28[i]|(controller.raw28[i+1]<<8));}
    switch(a){
    case 283:return controller.seen28;case 284:return (uint16_t)(controller.age28/1000u);case 285:return controller.generation28;
    case 286:return controller.blocked28;case 287:return controller.relevant28;
    case 296:return controller.blocked28?0x28:0;case 297:return controller.reject_byte;case 298:return controller.reject_value;
    case 256:return controller.state;case 257:return controller.accepted;case 258:return controller.applied;case 259:return controller.rejected;
    case 260:return controller.error;case 261:return controller.saved;case 262:return controller.touched;case 263:return controller.command[2];
    case 264:return (controller.state==ACTIVE || controller.state==APPLY || controller.state==SNAPSHOT || controller.state==QUEUED)?(controller.now_ms-controller.lease_at>=controller.lease_ms?0:(uint16_t)((controller.lease_ms-(controller.now_ms-controller.lease_at)+999u)/1000u)):0;
    case 265:return controller.acks;case 266:return controller.readbacks;case 267:return controller.restores;
    case 268:return controller.original.power;case 269:return controller.original.mode;case 270:return controller.original.flow;case 271:return controller.original.dhw;case 272:return controller.original.boost;
    case 273:return controller.current.power;case 274:return controller.current.mode;case 275:return controller.current.flow;case 276:return controller.current.dhw;case 277:return controller.current.boost;
    case 278:return controller.index_action;case 279:return controller.n_actions;case 280:return controller.phase;case 281:return controller.retries;
    case 282:return 0; /* no persistent reboot recovery guarantee */
    default:return 0;
    }
}
