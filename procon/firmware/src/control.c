/* P0072 r3. Independently encoded reference-backed controls; hardware trial pending. */
#include "control.h"
enum { IDLE, QUEUED, SNAPSHOT, APPLY, ACTIVE, RESTORE, RESTORE_BLOCKED };
enum { POWER=1, MODE, FLOW, DHW_TARGET, BOOST };
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
void ctl_observe(const uint8_t p[16],uint32_t t){
    if(p[0]!=0x28)return;
    for(unsigned i=0;i<16;++i)raw28[i]=p[i];
    seen28=1;++generation28;age28=0;diag_tick=t;
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
static int equal_intent(const uint16_t *w){return w[2]==command[2] && w[3]==command[3] && w[4]==command[4] && w[6]==command[6];}
static void add(unsigned f,unsigned v){actions[n_actions++]=(action){(uint8_t)f,(uint16_t)v};}
static void restore_plan(void){
    n_actions=index_action=phase=retries=waiting=0;
    /* Restore target while fixed mode still applies, then native mode last. */
    if(touched&(1u<<FLOW))add(FLOW,original.flow);
    if(touched&(1u<<DHW_TARGET))add(DHW_TARGET,original.dhw);
    if(touched&(1u<<BOOST))add(BOOST,original.boost);
    if(touched&(1u<<POWER))add(POWER,original.power);
    if(touched&(1u<<MODE))add(MODE,original.mode);
    state=RESTORE;settling=flow_prepared=0;
}
static void fail(uint16_t why){
    error=why;waiting=0;
    if(state==RESTORE || state==RESTORE_BLOCKED){state=RESTORE_BLOCKED;retry_at=now_ms;return;}
    if(saved && touched)restore_plan();
    else {state=IDLE;saved=0;}
}
void ctl_init(void){
    original=current=(settings){0};
    for(unsigned i=0;i<16;++i)raw28[i]=0;
    seen28=reject_byte=reject_value=0;generation28=blocked28=relevant28=0;age28=65535000u;diag_tick=0;
    for(unsigned i=0;i<8;++i)command[i]=0;
    accepted=applied=rejected=error=acks=readbacks=restores=0;
    state=saved=touched=n_actions=index_action=phase=retries=snapshot_step=waiting=0;
    now_ms=lease_at=lease_ms=retry_at=0;inflight_type=inflight_query=settling=flow_prepared=0;settle_at=0;
}
uint8_t ctl_submit(const uint16_t w[8],uint32_t now){
    now_ms=now;
    if(w[0]!=0xc072 || w[7]!=2 || !w[1] || w[2]>4 || w[6]>3)goto invalid;
    if(w[2]==1){if(w[3]||w[4]||w[5]||w[6])goto invalid;}
    else {
        if(w[5]<30 || w[5]>1800)goto invalid;
        if((w[6]&1)?(w[3]<2000 || w[3]>4500):w[3]!=0)goto invalid;
        if((w[6]&2)?(w[4]<4000 || w[4]>6000):w[4]!=0)goto invalid;
        if(w[2]==2 && !(w[6]&1))goto invalid;
        if(w[2]==4 && !w[6])goto invalid;
        if((w[2]==0 || w[2]==3) && (w[6]&1))goto invalid;
    }
    if(w[1]==accepted){
        for(unsigned i=0;i<8;++i)if(w[i]!=command[i])goto invalid;
        return 0; /* retry of same accepted packet never extends lease */
    }
    if(w[1]!=(uint16_t)(accepted==65535?1:accepted+1))goto invalid;
    if(w[2]==1){
        if(!saved || waiting || (state!=ACTIVE && state!=RESTORE_BLOCKED))goto busy;
        for(unsigned i=0;i<8;++i)command[i]=w[i];
        accepted=w[1];error=0;restore_plan();return 0;
    }
    if(state==ACTIVE && equal_intent(w)){
        for(unsigned i=0;i<8;++i)command[i]=w[i];
        accepted=applied=w[1];lease_at=now;lease_ms=(uint32_t)w[5]*1000u;return 0;
    }
    if(state!=IDLE || saved)goto busy;
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
        if(!waiting){if(saved && touched){error=7;restore_plan();}else{state=IDLE;saved=0;error=7;}}
    }
    if(state==RESTORE_BLOCKED && !waiting && t-retry_at>=5000u)restore_plan();
}
int ctl_busy(void){return state==QUEUED || state==SNAPSHOT || state==APPLY || state==RESTORE || state==RESTORE_BLOCKED;}
static void apply_plan(void){
    n_actions=index_action=phase=retries=flow_prepared=0;
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
            if(state==RESTORE){++restores;saved=touched=0;state=IDLE;if(command[2]==1)applied=accepted;}
            else {state=ACTIVE;applied=accepted;}
            return 0;
        }
        action a=actions[index_action];
        if(a.field==FLOW && !flow_prepared && phase!=1){*type=0x42;p[0]=0x26;phase=2;}
        else if(phase){*type=0x42;p[0]=(uint8_t)query_for(a.field);}
        else {
            *type=0x41;p[0]=a.field==BOOST?0x34:0x32;
            switch(a.field){
            case POWER:p[1]=1;p[3]=(uint8_t)a.value;break;
            case MODE:p[1]=8;p[6]=(uint8_t)a.value;break;
            case FLOW:p[1]=0x80;p[2]=0;p[6]=(uint8_t)current.mode;word(p+8,current.dhw);word(p+10,a.value);break;
            case DHW_TARGET:p[1]=0x20;word(p+8,a.value);break;
            case BOOST:p[1]=1;p[3]=(uint8_t)a.value;break;
            }
            touched|=(uint8_t)(1u<<a.field); /* even an unacknowledged SET may apply */
        }
    }
    waiting=1;inflight_type=*type;inflight_query=p[0];return 1;
}
static int update(const uint8_t *p){
    switch(p[0]){
    case 0x26:
        if(p[3]>1 || p[6]>2 || be(p+8)<4000 || be(p+8)>6000)return 0;
        current.power=p[3];current.mode=p[6];current.dhw=be(p+8);break;
    case 9:if(be(p+5)<2000 || be(p+5)>4500)return 0;current.flow=be(p+5);break;
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
    if(state==SNAPSHOT){
        if(p[0]==0x28 && !gate28(p)){fail(3);return 1;}
        retries=0;
        if(++snapshot_step==3){original=current;saved=1;apply_plan();}
    }else if(phase==2){flow_prepared=1;phase=retries=0;}
    else if(actual(actions[index_action].field)==actions[index_action].value){++index_action;phase=retries=flow_prepared=0;}
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
