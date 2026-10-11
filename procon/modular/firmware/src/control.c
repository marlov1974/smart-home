/* P0072 r3. Independently encoded reference-backed controls; hardware trial pending. */
#include "control.h"
#include "effect.h"
#include "effect_feedback.h"
enum { IDLE, QUEUED, SNAPSHOT, APPLY, ACTIVE, RESTORE, RESTORE_BLOCKED };
enum { POWER=1, MODE, FLOW, DHW_TARGET, BOOST, MODE_FLOW };
typedef struct { uint16_t power,mode,flow,dhw,boost; } settings;
typedef struct { uint8_t field; uint16_t value; } action;
static settings original,current;
static action actions[5];
static uint16_t command[8], accepted,applied,rejected,error,acks,readbacks,restores;
static uint8_t state,saved,touched,n_actions,index_action,phase,retries,snapshot_step,waiting;
static uint32_t now_ms,lease_at,lease_ms,retry_at;
static uint8_t inflight_type,inflight_query,settling,flow_prepared;
static uint32_t settle_at;
static uint8_t raw28[16],seen28,reject_byte,reject_value;
static uint16_t generation28,blocked28,relevant28;
static uint32_t age28,diag_tick;
static effect_measurement feedback;
static uint8_t effect_session,effect_prepared,effect_abort,effect_suspended;
static uint16_t effect_abort_reason;
static uint8_t effect_paused;
/* P0080: direct target replacement preserves the first session snapshot. */
static uint8_t retarget,native_mode;
static uint16_t retarget_from;
static uint32_t effect_pause_at;
static uint8_t effect_recover;
static int fast_session(void){return effect_session && command[4]>4000;}
static int soft_lower(void){return fast_session() && index_action<n_actions && actions[index_action].field==FLOW && actions[index_action].value<=3950 && actions[index_action].value<current.flow;}
static void recover_wait(void){
    waiting=settling=phase=retries=effect_prepared=flow_prepared=effect_suspended=0;
    n_actions=index_action=0;effect_discard_pending();state=ACTIVE;effect_recover=1;
    effect_wait(EF_WAIT_NATIVE,now_ms);
}
static int effect_waiting(void){return feedback.quality==EF_WAIT_NATIVE || feedback.quality==EF_SETTLING;}
static int native_heat_or_pause(unsigned m){return m==0 || m==2 || m==7 || (fast_session() && (m==1 || m==6));}
static int gate28(const uint8_t *p);
static int heating(unsigned mode){return mode==2 || mode==7;}
static int effect_feedback_ok(void){return feedback.ready && feedback.pairs>=3 && feedback.span_ms>=20000u && feedback.age_ms<60000u && heating(feedback.mode);}
/* The sampler and native mode can update in the same scheduler millisecond.
   A cached READY report is not a hard fault when newer telemetry no longer
   qualifies it. Yield unsent work; preserve sent readback and native guards. */
static int effect_collecting(void){
    return feedback.quality==EF_PENDING || feedback.quality==EF_WARMUP ||
        (fast_session() && ((feedback.quality>=EF_STALE && feedback.quality<=EF_LINKLOSS) ||
         (feedback.quality==EF_READY && native_heat_or_pause(feedback.mode) && !effect_feedback_ok())));
}
static int pause_demand_ok(void){
    unsigned kind=effect_pending_demand();
    if(kind==1)return feedback.quality==EF_WAIT_NATIVE && feedback.hz==0;
    return kind==2 && fast_session() &&
        (feedback.quality==EF_SETTLING || effect_feedback_ok()) &&
        feedback.pairs>=1 && feedback.age_ms<15000u && heating(feedback.mode) &&
        feedback.hz>0 && feedback.hz<255 && feedback.supply_cC>=0 && feedback.supply_cC<=10000;
}
void ctl_feedback(const effect_measurement *m){feedback=*m;}
void ctl_link_lost(uint32_t t){
    now_ms=t;
    if(fast_session() && saved){recover_wait();return;}
    if(effect_session){effect_abort=1;effect_abort_reason=EFFECT_LINK_LOST;}
}
void ctl_observe(const uint8_t p[16],uint32_t t){
    if(p[0]==0x26 && effect_session && (state==ACTIVE || state==APPLY)){
        unsigned expected=(touched&(1u<<MODE))?1:original.mode;
        if(p[3]!=1 || p[6]!=expected || !native_heat_or_pause(p[4])){
            effect_abort=1;effect_abort_reason=EFFECT_MODE_CHANGED;
        }
    }
    if(p[0]!=0x28)return;
    for(unsigned i=0;i<16;++i)raw28[i]=p[i];
    seen28=1;++generation28;age28=0;diag_tick=t;
    if(effect_session && state!=RESTORE && state!=RESTORE_BLOCKED &&
       (!gate28(p) || p[3]!=0)){effect_abort=1;effect_abort_reason=EFFECT_NATIVE_INHIBIT;}
}
static int gate28(const uint8_t *p){
    relevant28=(1u<<4)|(1u<<10); /* holiday and external server ownership */
    if(command[2]==2 || (command[6]&1))relevant28|=1u<<6;
    if(command[2]==3 || (command[6]&2))relevant28|=1u<<5;
    blocked28=0;reject_byte=reject_value=0;
    for(unsigned i=4;i<=10;++i){
        /* Unknown encodings remain a failure, including unrelated flags. */
        if(p[i]>1 || (p[i] && (relevant28&(1u<<i)))){
            blocked28|=(uint16_t)(1u<<i);
            if(!reject_byte){reject_byte=(uint8_t)i;reject_value=p[i];}
        }
    }
    return !blocked28;
}
static uint16_t be(const uint8_t *p){return (uint16_t)((p[0]<<8)|p[1]);}
static void word(uint8_t *p,uint16_t v){p[0]=(uint8_t)(v>>8);p[1]=(uint8_t)v;}
static int equal_intent(const uint16_t *w){return w[0]==command[0] && w[7]==command[7] && w[2]==command[2] && w[3]==command[3] && w[4]==command[4] && w[6]==command[6];}
static void add(unsigned f,unsigned v){actions[n_actions++]=(action){(uint8_t)f,(uint16_t)v};}
static void restore_plan(void){
    retarget=0;effect_recover=0;
    n_actions=index_action=phase=retries=waiting=0;
    /* Restore target while fixed mode still applies, then native mode last. */
    if(touched&(1u<<FLOW))add(FLOW,original.flow);
    if(touched&(1u<<DHW_TARGET))add(DHW_TARGET,original.dhw);
    if(touched&(1u<<BOOST))add(BOOST,original.boost);
    if(touched&(1u<<POWER))add(POWER,original.power);
    if(touched&(1u<<MODE))add(MODE,original.mode);
    state=RESTORE;settling=flow_prepared=effect_prepared=effect_suspended=0;
    if(effect_session)effect_stop(effect_abort_reason?effect_abort_reason:EFFECT_ABORTED,1);
}
static void fail(uint16_t why){
    if(fast_session() && saved && why==4 && state!=RESTORE && state!=RESTORE_BLOCKED){recover_wait();return;}
    error=why;waiting=0;
    if(effect_session && !effect_abort_reason)
        effect_abort_reason=why==4?EFFECT_READ_TIMEOUT:why==5?EFFECT_READBACK_MISMATCH:EFFECT_NATIVE_INHIBIT;
    if(state==RESTORE || state==RESTORE_BLOCKED){state=RESTORE_BLOCKED;retry_at=now_ms;return;}
    if(saved && touched)restore_plan();
    else {state=IDLE;saved=0;if(effect_session)effect_stop(effect_abort_reason?effect_abort_reason:EFFECT_NATIVE_INHIBIT,0);effect_session=0;}
}
void ctl_init(void){
    retarget=0;native_mode=0;retarget_from=0;effect_recover=0;
    original=current=(settings){0};
    for(unsigned i=0;i<16;++i)raw28[i]=0;
    seen28=reject_byte=reject_value=0;generation28=blocked28=relevant28=0;age28=65535000u;diag_tick=0;
    for(unsigned i=0;i<8;++i)command[i]=0;
    accepted=applied=rejected=error=acks=readbacks=restores=0;
    state=saved=touched=n_actions=index_action=phase=retries=snapshot_step=waiting=0;
    now_ms=lease_at=lease_ms=retry_at=0;inflight_type=inflight_query=settling=flow_prepared=0;settle_at=0;
    effect_paused=0;effect_pause_at=0;feedback=(effect_measurement){0};effect_session=effect_prepared=effect_abort=effect_suspended=0;effect_abort_reason=0;effect_init();
}
uint8_t ctl_submit(const uint16_t w[8],uint32_t now){
    now_ms=now;
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
        if((w[6]&1)?(w[3]<2000 || w[3]>4500):w[3]!=0)goto invalid;
        if((w[6]&2)?(w[4]<4000 || w[4]>6000):w[4]!=0)goto invalid;
        if(w[2]==2 && !(w[6]&1))goto invalid;
        if(w[2]==4 && !w[6])goto invalid;
        if((w[2]==0 || w[2]==3) && (w[6]&1))goto invalid;
    }
    }
    if(w[1]==accepted){
        for(unsigned i=0;i<8;++i)if(w[i]!=command[i])goto invalid;
        return 0; /* retry of same accepted packet never extends lease */
    }
    if(w[1]!=(uint16_t)(accepted==65535?1:accepted+1))goto invalid;
    if(w[2]==1){
        if(!saved || waiting || (state!=ACTIVE && state!=RESTORE_BLOCKED))goto busy;
        for(unsigned i=0;i<8;++i)command[i]=w[i];
        accepted=w[1];error=0;effect_abort_reason=EFFECT_ABORTED;restore_plan();return 0;
    }
    /* An internal EFFECT adjustment does not revoke an applied mission.
       Renew its lease without disturbing the current SET/readback transaction.
       Initial application must still finish before it can be renewed. */
    if(((state==ACTIVE && (!effect_suspended || applied==accepted)) ||
        (state==APPLY && effect_session && saved && applied==accepted)) && equal_intent(w)){
        for(unsigned i=0;i<8;++i)command[i]=w[i];
        accepted=applied=w[1];lease_at=now;lease_ms=(uint32_t)w[5]*1000u;return 0;
    }
    if(state==ACTIVE && saved && !waiting && !effect_session && !v3 &&
       command[2]==2 && command[6]==1 && w[2]==2 && w[6]==1){
        retarget_from=command[3];retarget=1;
        for(unsigned i=0;i<8;++i)command[i]=w[i];
        accepted=w[1];error=0;lease_at=now;lease_ms=(uint32_t)w[5]*1000u;
        snapshot_step=n_actions=index_action=phase=retries=waiting=settling=flow_prepared=0;
        blocked28=relevant28=0;reject_byte=reject_value=0;state=SNAPSHOT;return 0;
    }
    if(state!=IDLE || saved)goto busy;
    if(v3 && !effect_feedback_ok() && !effect_waiting())goto busy;
    retarget=0;effect_recover=0;effect_paused=0;effect_session=(uint8_t)v3;effect_abort=effect_prepared=effect_suspended=0;effect_abort_reason=0;
    if(v3)effect_begin(w[3],w[4],now);
    for(unsigned i=0;i<8;++i)command[i]=w[i];
    accepted=w[1];error=0;lease_at=now;lease_ms=(uint32_t)w[5]*1000u;
    blocked28=relevant28=0;reject_byte=reject_value=0;
    touched=0;snapshot_step=retries=waiting=0;state=QUEUED;return 0;
invalid:rejected=w[1];error=1;return 3;
busy:rejected=w[1];error=2;return 6;
}
void ctl_tick(uint32_t t){
    uint32_t dt=t-diag_tick;diag_tick=t;
    if(seen28)age28=dt>=65535000u-age28?65535000u:age28+dt;
    now_ms=t;
    if((state==QUEUED || state==SNAPSHOT || state==APPLY || state==ACTIVE) && t-lease_at>=lease_ms){
        /* Never interrupt a wire transaction; expiration is processed after it. */
        if(!waiting){if(saved && touched){error=7;effect_abort_reason=EFFECT_LEASE_EXPIRED;restore_plan();}else{state=IDLE;saved=0;error=7;if(effect_session)effect_stop(EFFECT_LEASE_EXPIRED,0);effect_session=0;}}
    }
    if(effect_session && (state==QUEUED || state==SNAPSHOT || state==APPLY || state==ACTIVE)){
        if(fast_session() && feedback.quality>=EF_STALE && feedback.quality<=EF_LINKLOSS)effect_wait(EF_WAIT_NATIVE,t);
        if(effect_waiting()){
            if(!effect_paused){effect_paused=1;effect_pause_at=t;}
            effect_wait(feedback.quality,t);
        }else if(effect_feedback_ok())effect_paused=0;
        if(!fast_session() && effect_paused && t-effect_pause_at>=1200000u){effect_abort=1;effect_abort_reason=EFFECT_WAIT_TIMEOUT;}
        if(!effect_feedback_ok() && !effect_collecting() && !effect_waiting()){effect_abort=1;if(!effect_abort_reason)effect_abort_reason=EFFECT_BAD_FEEDBACK;}
        if(effect_abort && !waiting)fail(8);
    }
    if(state==RESTORE_BLOCKED && !waiting && t-retry_at>=5000u)restore_plan();
    /* Ordinary partial FAST pairs must yield the bus, not starve GET14/26.
       Preserve the pending action but require fresh guards when it resumes. */
    if(effect_session && state==APPLY && index_action<n_actions && !waiting && phase==0){
        int discard=actions[index_action].field!=MODE_FLOW &&
            ((effect_waiting() && !pause_demand_ok()) || (effect_pending_demand() && !pause_demand_ok()));
        if(discard){
            n_actions=index_action=0;effect_suspended=effect_prepared=flow_prepared=0;
            effect_discard_pending();state=ACTIVE;
        }else if(effect_collecting() && !soft_lower()){
            effect_suspended=1;effect_prepared=flow_prepared=0;state=ACTIVE;
        }
    }
    if(effect_session && state==ACTIVE && effect_suspended && effect_waiting()){
        if(actions[index_action].field==MODE_FLOW){
            if(effect_entry_demand(&feedback,current.flow,native_mode,t)){effect_suspended=0;state=APPLY;}
        }else if(pause_demand_ok()){effect_suspended=0;state=APPLY;}
        else {n_actions=index_action=0;effect_suspended=0;effect_discard_pending();}
    }
    if(effect_session && state==ACTIVE && effect_suspended && effect_feedback_ok()){
        effect_suspended=0;state=APPLY;
    }
    if(fast_session() && state==ACTIVE && effect_recover && effect_feedback_ok()){
        snapshot_step=retries=waiting=0;state=SNAPSHOT;
    }
    /* Power can be unavailable while native heating guards are still readable.
       Only reduce an existing boost; never increase on invalid feedback. */
    if(fast_session() && state==ACTIVE && !waiting && effect_collecting() &&
       feedback.quality!=EF_DHW && feedback.quality!=EF_LINKLOSS &&
       feedback.quality>=EF_STALE &&
       heating(feedback.mode) && current.flow>3950){
        effect_discard_pending();effect_suspended=effect_prepared=flow_prepared=0;
        n_actions=index_action=phase=retries=0;add(FLOW,3950);state=APPLY;
    }
    if(effect_session && state==ACTIVE && !effect_abort && !effect_suspended && !effect_recover){
        uint16_t next=effect_feedback_ok()?effect_decide(&feedback,current.flow,t):
            effect_pause_demand(&feedback,current.flow,t);
        if(next){n_actions=index_action=phase=retries=effect_prepared=flow_prepared=0;add(FLOW,next);state=APPLY;}
    }
}
int ctl_busy(void){return state==QUEUED || state==SNAPSHOT || state==APPLY || state==RESTORE || state==RESTORE_BLOCKED;}
static void apply_plan(void){
    n_actions=index_action=phase=retries=flow_prepared=0;
    if(effect_session){
        effect_capture(current.flow,now_ms);
        if(current.mode!=1)add(MODE_FLOW,current.flow);
        /* Atomic native flags 0x08|0x80 prevent exposing a hidden fixed target.
           Verify both mode (GET26) and target (GET09) before ACTIVE. */
        state=APPLY;return;
    }
    if(command[2]==2 && current.mode!=1)add(MODE,1);
    if(command[6]&1)add(FLOW,command[3]);
    if(command[6]&2)add(DHW_TARGET,command[4]);
    if(command[2]==3)add(BOOST,1);
    if(command[2]==0)add(POWER,0);
    if((command[2]==2 || command[2]==3) && current.power!=1)add(POWER,1);
    state=APPLY;
}
static unsigned query_for(unsigned f){return f==FLOW?9:f==BOOST?0x28:0x26;}
int ctl_next(uint8_t *type,uint8_t p[16],uint32_t t){
    ctl_tick(t);
    if(settling){if(t-settle_at<1000u)return 0;settling=0;}
    if(waiting || state==RESTORE_BLOCKED || !ctl_busy())return 0;
    for(unsigned i=0;i<16;++i)p[i]=0;
    if(state==QUEUED)state=SNAPSHOT;
    if(state==SNAPSHOT){static const uint8_t q[]={0x26,9,0x28};*type=0x42;p[0]=q[snapshot_step];}
    else {
        if(index_action>=n_actions){
            if(state==RESTORE){++restores;saved=touched=0;state=IDLE;if(command[2]==1)applied=accepted;if(effect_session){effect_restored();effect_session=effect_abort=0;}}
            else {state=ACTIVE;applied=accepted;if(effect_session)effect_verified(current.flow,t);}
            return 0;
        }
        action a=actions[index_action];
        if(effect_session && state==APPLY && !effect_prepared && phase!=1 && phase!=4){
            *type=0x42;p[0]=phase==2?0x26:0x28;if(phase!=2)phase=3;
        }
        else if(a.field==FLOW && !flow_prepared && phase!=1){*type=0x42;p[0]=0x26;phase=2;}
        else if(phase){*type=0x42;p[0]=(uint8_t)(a.field==MODE_FLOW && phase==4?9:query_for(a.field));}
        else {
            if(effect_session && state==APPLY && !effect_feedback_ok() && !(a.field==MODE_FLOW && effect_waiting()) && !pause_demand_ok() && !soft_lower()){
                effect_abort_reason=EFFECT_BAD_FEEDBACK;fail(8);return 0;
            }
            if(effect_session && state==APPLY && a.field==MODE_FLOW){
                a.value=effect_entry_demand(&feedback,current.flow,native_mode,t);
                if(!a.value){effect_suspended=1;effect_prepared=flow_prepared=0;state=ACTIVE;return 0;}
                actions[index_action]=a; /* Freeze this exact target once sent. */
            }
            *type=0x41;p[0]=a.field==BOOST?0x34:0x32;
            switch(a.field){
            case POWER:p[1]=1;p[3]=(uint8_t)a.value;break;
            case MODE:p[1]=8;p[6]=(uint8_t)a.value;break;
            case MODE_FLOW:p[1]=0x88;p[2]=0;p[6]=1;word(p+8,current.dhw);word(p+10,a.value);break;
            case FLOW:p[1]=0x80;p[2]=0;p[6]=(uint8_t)current.mode;word(p+8,current.dhw);word(p+10,a.value);break;
            case DHW_TARGET:p[1]=0x20;word(p+8,a.value);break;
            case BOOST:p[1]=1;p[3]=(uint8_t)a.value;break;
            }
            /* Even an unacknowledged combined write may apply both dimensions. */
            touched|=a.field==MODE_FLOW?(uint8_t)((1u<<MODE)|(1u<<FLOW)):(uint8_t)(1u<<a.field);
        }
    }
    waiting=1;inflight_type=*type;inflight_query=p[0];return 1;
}
static int update(const uint8_t *p){
    switch(p[0]){
    case 0x26:
        if(p[3]>1 || p[6]>2 || be(p+8)<4000 || be(p+8)>6000)return 0;
        current.power=p[3];current.mode=p[6];current.dhw=be(p+8);native_mode=p[4];break;
    case 9:if(be(p+5)<2000 || be(p+5)>5500)return 0;current.flow=be(p+5);break;
    case 0x28:if(p[3]>1)return 0;current.boost=p[3];break;
    default:return 0;
    }
    return 1;
}
static uint16_t actual(unsigned field){
    switch(field){case POWER:return current.power;case MODE:return current.mode;case FLOW:return current.flow;case DHW_TARGET:return current.dhw;default:return current.boost;}
}
int ctl_reply(uint8_t type,const uint8_t *p,unsigned len,uint32_t t){
    now_ms=t;if(!waiting)return 0;
    if(inflight_type==0x41){
        if(type!=0x61)return 0;
        ++acks;waiting=0;phase=1;retries=0;settling=1;settle_at=t;return 1; /* generic hint only */
    }
    if(type!=0x62 || len!=16 || p[0]!=inflight_query)return 0;
    waiting=0;++readbacks;
    ctl_observe(p,t);
    if(!update(p)){fail(3);return 1;}
    if(effect_session && state==APPLY && p[0]==0x26 && (current.power!=1 || !native_heat_or_pause(p[4]))){
        effect_abort_reason=EFFECT_MODE_CHANGED;fail(8);return 1;
    }
    if(state==SNAPSHOT){
        if(retarget && ((p[0]==0x26 && (current.power!=1 || current.mode!=1 || !native_heat_or_pause(p[4]))) ||
                       (p[0]==9 && current.flow!=retarget_from) || (p[0]==0x28 && current.boost))){fail(3);return 1;}
        if(p[0]==0x28 && !gate28(p)){effect_abort_reason=EFFECT_NATIVE_INHIBIT;fail(3);return 1;}
        if(effect_session && ((p[0]==0x26 && (current.power!=1 || !native_heat_or_pause(p[4]))) ||
            (p[0]==9 && current.flow>command[4]) || (p[0]==0x28 && current.boost))){
            effect_abort_reason=EFFECT_MODE_CHANGED;fail(8);return 1;
        }
        retries=0;
        if(++snapshot_step==3){
            if(effect_recover){
                effect_recover=0;error=0;n_actions=index_action=phase=retries=0;
                state=ACTIVE;applied=accepted;effect_discard_pending();
            }else if(retarget){n_actions=index_action=phase=retries=flow_prepared=0;add(FLOW,command[3]);state=APPLY;}
            else {original=current;saved=1;apply_plan();}
        }
    }else if(effect_session && state==APPLY && phase==3){
        if(!gate28(p) || current.boost){effect_abort_reason=EFFECT_NATIVE_INHIBIT;fail(3);return 1;}
        phase=2;retries=0;
    }else if(phase==2){
        if(retarget && state==APPLY && (current.power!=1 || current.mode!=1 || !native_heat_or_pause(p[4]))){fail(3);return 1;}
        if(effect_session && state==APPLY){
            unsigned expected=(touched&(1u<<MODE))?1:original.mode;
            if(current.power!=1 || !native_heat_or_pause(p[4]) || current.mode!=expected || (!effect_feedback_ok() && !effect_collecting() && !effect_waiting())){
                effect_abort_reason=EFFECT_MODE_CHANGED;fail(8);return 1;
            }
            effect_prepared=1;
        }
        flow_prepared=1;phase=retries=0;
    }
    else if(actions[index_action].field==MODE_FLOW && phase==1 && current.mode==1){
        phase=4;retries=0; /* mode alone is insufficient proof of bounded flow */
    }
    else if((actions[index_action].field==MODE_FLOW && phase==4 && current.flow==actions[index_action].value) ||
            (actions[index_action].field!=MODE_FLOW && actual(actions[index_action].field)==actions[index_action].value)){++index_action;phase=retries=flow_prepared=effect_prepared=0;}
    else if(++retries>=3)fail(5);
    else {settling=1;settle_at=t;}
    return 1;
}
void ctl_timeout(uint32_t t){
    now_ms=t;if(!waiting)return;waiting=0;
    if(inflight_type==0x41){phase=1;retries=0;settling=1;settle_at=t;return;} /* verify possible applied write */
    if(++retries>=3)fail(4);
}
uint16_t ctl_read(unsigned a){
    if(a>=320 && a<=351)return effect_read(a,&feedback,current.flow,now_ms);
    if(a>=288 && a<=295){unsigned i=2*(a-288);return (uint16_t)(raw28[i]|(raw28[i+1]<<8));}
    switch(a){
    case 283:return seen28;case 284:return (uint16_t)(age28/1000u);case 285:return generation28;
    case 286:return blocked28;case 287:return relevant28;
    case 296:return blocked28?0x28:0;case 297:return reject_byte;case 298:return reject_value;
    case 256:return state;case 257:return accepted;case 258:return applied;case 259:return rejected;
    case 260:return error;case 261:return saved;case 262:return touched;case 263:return command[2];
    case 264:return (state==ACTIVE || state==APPLY || state==SNAPSHOT || state==QUEUED)?(now_ms-lease_at>=lease_ms?0:(uint16_t)((lease_ms-(now_ms-lease_at)+999u)/1000u)):0;
    case 265:return acks;case 266:return readbacks;case 267:return restores;
    case 268:return original.power;case 269:return original.mode;case 270:return original.flow;case 271:return original.dhw;case 272:return original.boost;
    case 273:return current.power;case 274:return current.mode;case 275:return current.flow;case 276:return current.dhw;case 277:return current.boost;
    case 278:return index_action;case 279:return n_actions;case 280:return phase;case 281:return retries;
    case 282:return 0; /* no persistent reboot recovery guarantee */
    default:return 0;
    }
}
