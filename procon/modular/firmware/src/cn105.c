/* P0072: existing framing plus exclusive transaction arbitration. Bounded supervised SET path at service boundaries. */
#include "cn105.h"
#include "ota.h"
#include "service.h"
#include "telemetry.h"
#include "control.h"
#include "effect_feedback.h"
enum { NONE, CONNECT, NORMAL, SERVICE, CONTROL, DIAGNOSTIC };
static uint8_t rx[22], tx[22], used, tx_len, tx_pos, owner;
static uint8_t linked, valid, ever, hz, last_type, last_query, polled;
static uint32_t now, last_byte, last_good, last_send, last_tick, age_ms;
static uint32_t reply_at, released_at;
static uint16_t replies, rx_bytes, errors, sent, uart_errors, handshakes;
static int started;
static uint8_t native26[16],native28[16],seen26,seen28;
static uint32_t native26_at,native28_at;
static uint8_t fast_index, query, control_fast;
static const uint8_t fast_codes[]={4,0x0c,0x14,0x0b,9,0x15,0x26,0x28};
#define FAST_COUNT (sizeof fast_codes/sizeof fast_codes[0])

/* P0081: bounded read-only asynchronous diagnostics, no public ABI change. */
enum { D_IDLE,D_QUEUED,D_BUSY,D_DONE,D_TIMEOUT,D_UNSUPPORTED,D_BAD_RESPONSE,D_ERROR };
typedef struct {
    uint16_t words[8], generation, error;
    uint8_t state, attempts, length, raw[22], bad;
    uint32_t accepted_at, completed_at, attempt_at, quarantine;
} diagnostic_state;
static diagnostic_state diag;
static int diag_pending(void){return diag.state==D_QUEUED || diag.state==D_BUSY;}
static int diag_allowed(uint16_t code){
    static const uint16_t safe[]={0,1,2,3,4,5,9,10,12,13,14,16,17,18,19,22,25,26,27,28,48,51,52,53,54,55,70,71,90,91,100,101,102,103,104,105,106,107,108,109,110,111,112,113,115,116,117,118,119,120,121,122,125,129,130,154,156,157,158,162,163,164,165,166,175,176,177,190,191,504,505,506,507,508,509,510,511,512,513,514,515,534,535,540,550,551,552,553,554,555,556,557,558,559,560,561,562,563,564,565,567,568,569,571};
    for(unsigned i=0;i<sizeof safe/sizeof safe[0];i++)if(code==safe[i])return 1;
    return 0;
}
static void diag_finish(uint8_t state,uint16_t error,uint32_t t){
    if(diag.state==D_BUSY){fast_index=0;svc_start_cycle();}
    diag.state=state;diag.error=error;diag.completed_at=t;diag.quarantine=t;++diag.generation;
}
static uint8_t diag_submit(const uint16_t w[8]){
    if(w[1]!=1 || w[2]!=0xfd || !w[3] || w[4]<1 || w[4]>2 || w[6] || w[7] || (w[4]==1 && w[5]>255))return 3;
    if(diag.words[3]==w[3]){
        for(unsigned i=0;i<8;i++)if(diag.words[i]!=w[i])return 3;
        return 0;
    }
    if(diag_pending() || ctl_read(256) || ctl_busy())return 6;
    if(diag.words[3] && (int16_t)(w[3]-diag.words[3])<=0)return 3;
    if(!linked || now-last_good>10000u)return 4;
    if(diag.words[3] && now-diag.quarantine<1000u)return 6;
    for(unsigned i=0;i<8;i++)diag.words[i]=w[i];
    diag.state=D_QUEUED;diag.attempts=diag.length=diag.bad=0;diag.error=0;diag.accepted_at=now;
    for(unsigned i=0;i<22;i++)diag.raw[i]=0;
    ++diag.generation;
    if(w[4]==2 && !diag_allowed(w[5]))diag_finish(D_UNSUPPORTED,1,now);
    return 0;
}
static uint16_t diag_read(unsigned a){
    unsigned i=a-600;
    if(i>=16 && i<27)return (uint16_t)(diag.raw[(i-16)*2]|((uint16_t)diag.raw[(i-16)*2+1]<<8));
    uint32_t age=diag.state>=D_DONE?now-diag.completed_at:now-diag.accepted_at;
    switch(i){
    case 0:return 0x81d1;case 1:return 1;case 2:return 0xfc;
    case 3:return diag.words[3];case 4:return diag.words[4];case 5:return diag.words[5];
    case 6:return diag.state;case 7:return diag.length;case 8:return diag.error;
    case 9:return diag.state==D_DONE;case 10:return diag.generation;
    case 11:return age/1000u>65535?65535:(uint16_t)(age/1000u);
    case 12:return diag.attempts;case 13:return diag.bad;
    case 14:return diag.length>=6?diag.raw[4]:0;case 15:return 30;
    case 27:return diag.generation;case 28:return diag_pending();
    default:return 0;
    }
}
static void diag_retry(uint32_t t){
    if(diag.words[4]==1 || diag.attempts>=10)
        diag_finish(diag.bad?D_BAD_RESPONSE:D_TIMEOUT,diag.bad?2:3,t);
}

static uint8_t checksum(const uint8_t *b, unsigned n) {
    uint8_t sum=0;
    for(unsigned i=0;i<n;++i)sum=(uint8_t)(sum+b[i]);
    return (uint8_t)(0xfcu-sum);
}
static void release(uint32_t t) {owner=NONE;released_at=t;}
static void disconnect(uint32_t t) {
    if(diag_pending())diag_finish(D_ERROR,4,t);
    linked=valid=polled=fast_index=control_fast=0;tele_invalidate();ctl_link_lost(t);used=tx_len=tx_pos=0;release(t);svc_link(0,t);
}
static void begin(uint8_t kind, uint8_t code, uint32_t t) {
    owner=kind;started=1;last_send=t;tx_pos=0;
    tx[0]=0xfc;tx[1]=kind==CONNECT?0x5a:0x42;tx[2]=2;tx[3]=0x7a;
    tx[4]=kind==CONNECT?2:16;
    for(unsigned i=5;i<21;++i)tx[i]=0;
    if(kind==CONNECT){tx[5]=0xca;tx[6]=1;}
    else if(kind==NORMAL){tx[5]=query=fast_codes[fast_index++];polled=1;}
    else if(kind==DIAGNOSTIC){
        tx[5]=diag.words[4]==1?(uint8_t)diag.words[5]:0xa3;
        if(diag.words[4]==2){tx[6]=(uint8_t)(diag.words[5]>>8);tx[7]=(uint8_t)diag.words[5];}
        if(diag.state!=D_BUSY)++diag.generation;
        diag.state=D_BUSY;diag.attempt_at=t;++diag.attempts;
    } else {tx[5]=0xa3;tx[7]=code;svc_sent(t);}
    tx_len=(uint8_t)(tx[4]+6);tx[tx_len-1]=checksum(tx,tx_len-1);
}
void cn_init(void) {
    diag=(diagnostic_state){0};
    used=tx_len=tx_pos=owner=linked=valid=ever=hz=last_type=last_query=polled=0;
    now=last_byte=last_good=last_send=last_tick=age_ms=reply_at=released_at=0;
    replies=rx_bytes=errors=sent=uart_errors=handshakes=0;started=0;
    seen26=seen28=control_fast=0;fast_index=query=0;tele_init();effect_feedback_init();ctl_init();svc_init();svc_link(0,0);
}
static void bad_frame(void) {if(owner==DIAGNOSTIC)diag.bad=1;++errors;if(owner==SERVICE)svc_bad_frame();}
void cn_feed(uint8_t byte, uint32_t t, int error) {
    ++rx_bytes;
    if(error){if(owner==DIAGNOSTIC)diag.bad=1;++uart_errors;if(owner==SERVICE)svc_bad_frame();used=0;return;}
    if(used && t-last_byte>100u){bad_frame();used=0;}
    last_byte=t;
    if(!used && byte!=0xfc)return;
    rx[used++]=byte;
    if((used==3 && rx[2]!=2)||(used==4 && rx[3]!=0x7a)||(used==5 && rx[4]>16)) {
        bad_frame();used=0;return;
    }
    if(used<6 || used!=(unsigned)rx[4]+6u)return;
    unsigned n=used;used=0;
    if(checksum(rx,n-1)!=rx[n-1]){
        if(owner==DIAGNOSTIC){diag.length=(uint8_t)n;for(unsigned i=0;i<n;i++)diag.raw[i]=rx[i];++diag.generation;}
        bad_frame();return;
    }
    last_type=rx[1];last_query=rx[4]?rx[5]:0;
    if(owner==DIAGNOSTIC && !tx_len){
        uint8_t expected=diag.words[4]==1?(uint8_t)diag.words[5]:0xa3;
        if(rx[1]!=0x62 || rx[4]<1 || rx[5]!=expected){diag.bad=1;return;}
        if(diag.words[4]==2 && (rx[4]!=16 || rx[6]!=(uint8_t)(diag.words[5]>>8) || rx[7]!=(uint8_t)diag.words[5])){diag.bad=1;return;}
        diag.length=(uint8_t)n;for(unsigned i=0;i<n;i++)diag.raw[i]=rx[i];++diag.generation;
        last_good=t;
        if(diag.words[4]==1 || rx[8]==1 || rx[8]==2)diag_finish(D_DONE,0,t);
        else if(rx[8])diag_finish(D_UNSUPPORTED,rx[8],t);
        else diag_retry(t);
        release(t);return;
    }
    if(owner==CONTROL && !tx_len && ctl_reply(rx[1],rx+5,rx[4],t)) {
        if(rx[1]==0x62 && rx[4]==16)tele_accept(rx+5);
        last_good=t;release(t);
    } else if(rx[1]==0x62 && rx[4]==16 && rx[5]==0xa3) {
        if(svc_reply(rx+5,t,linked && owner==SERVICE && !tx_len)) {last_good=t;release(t);}
    } else if(rx[1]==0x7a && rx[4]==1 && rx[5]==0 && owner==CONNECT && !tx_len) {
        linked=1;last_good=t;++handshakes;polled=fast_index=0;svc_link(1,t);release(t);
    } else if(rx[1]==0x62 && rx[4]==16 && rx[5]==query && linked && owner==NORMAL && !tx_len) {
        tele_accept(rx+5);ctl_observe(rx+5,t);
        if(query==0x26){for(unsigned i=0;i<16;++i)native26[i]=rx[5+i];seen26=1;native26_at=t;}
        if(query==0x28){for(unsigned i=0;i<16;++i)native28[i]=rx[5+i];seen28=1;native28_at=t;}
        if(query==4){hz=rx[6];ever=valid=1;age_ms=0;++replies;}
        last_good=t;release(t);
    }
}
void cn_tick(uint32_t t) {
    uint32_t dt=t-last_tick;last_tick=t;now=t;
    if(ever)age_ms=dt>=65535000u-age_ms?65535000u:age_ms+dt;
    if(valid && age_ms>=60000u)valid=0;
    svc_tick(dt,t);tele_tick(dt);effect_feedback_tick(t);
    const effect_feedback_state *f=effect_feedback_get();
    tele_sample mode_sample,hz_sample,supply_sample;
    tele_snapshot(3,&supply_sample);tele_snapshot(18,&mode_sample);tele_snapshot(8,&hz_sample);
    effect_measurement m={.supply_cC=supply_sample.status==TELE_VALID?supply_sample.value:INT32_MIN,.instant_w=f->instant_w,.short_w=f->short_w,.slow_w=f->slow_w,
        .age_ms=f->last_age_ms,.span_ms=f->short_span_ms,.quality=f->quality,
        .pairs=f->short_count,.mode=mode_sample.status==TELE_VALID?(uint16_t)mode_sample.value:65535u,
        .hz=hz_sample.status==TELE_VALID?(uint16_t)hz_sample.value:65535u,.ready=f->ready};
    ctl_feedback(&m);ctl_tick(t);
    if(used && t-last_byte>100u){used=0;bad_frame();}
    if(diag_pending() && t-diag.accepted_at>=30000u){
        diag_finish(D_TIMEOUT,5,t);
        if(owner==DIAGNOSTIC){tx_len=tx_pos=0;release(t);}
    }
    if(linked && !owner && svc_read(32)==4 && t-last_good>=10000u)disconnect(t);
    if(owner) {
        if(tx_len && t-last_send>=1000u) {
            ++uart_errors;if(owner==DIAGNOSTIC){diag.bad=1;diag_retry(t);}if(owner==SERVICE)svc_timeout(t);
            if(owner==CONTROL)ctl_timeout(t);
            tx_len=tx_pos=0;release(t);
        } else if(!tx_len && t-reply_at>=800u) {
            if(owner==DIAGNOSTIC)diag_retry(t);
            if(owner==SERVICE)svc_timeout(t);
            if(owner==CONTROL)ctl_timeout(t);
            release(t);
        } else return;
    }
    /* Turnaround/recovery guard. Late replies never release an unrelated owner. */
    if(t-released_at<50u)return;
    if(!linked) {
        if((!started && t>=1000u)||(started && t-last_send>=3000u))begin(CONNECT,0,t);
        return;
    }
    /* A partial pair may suspend APPLY while this refresh is in progress.
       Keep its boundary until the complete coherent round has finished;
       otherwise the normal path would start another A3 before the write. */
    if(control_fast){
        if(fast_index<FAST_COUNT){begin(NORMAL,0,t);return;}
        control_fast=0;
    }
    if(svc_read(32)==4 && ctl_busy()) {
        /* P0080: CONTROL must not age its own feedback out. A3 may have
           delayed normal telemetry before this boundary. Refresh proactively
           FAST between (never inside) control transactions, keeping enough
           margin for the next reply. Complete the round for coherent power. */
        /* RESTORE(5)/RESTORE_BLOCKED(6) must remain able to recover even
           when GET04 is genuinely unavailable. Their native guards apply. */
        if(ctl_read(256)<5 && fast_index>=FAST_COUNT && hz_sample.age_ms>=6000u){fast_index=0;control_fast=1;}
        if(fast_index<FAST_COUNT){begin(NORMAL,0,t);return;}
        uint8_t type,payload[16];
        if(ctl_next(&type,payload,t)){
            owner=CONTROL;started=1;last_send=t;tx_pos=0;
            tx[0]=0xfc;tx[1]=type;tx[2]=2;tx[3]=0x7a;tx[4]=16;
            for(unsigned i=0;i<16;++i)tx[5+i]=payload[i];
            tx[21]=checksum(tx,21);tx_len=22;
        }
        return;
    }
    /* P0081: diagnostic A3 owns the whole retry sequence; normal telemetry
       gets a complete FAST round before the next accepted diagnostic. */
    if(diag.state==D_BUSY){
        if(t-diag.attempt_at>=1000u)begin(DIAGNOSTIC,0,t);
        return;
    }
    if(diag.state==D_QUEUED && svc_read(32)==4){begin(DIAGNOSTIC,0,t);return;}
    if(svc_read(32)==4){fast_index=0;svc_start_cycle();}
    if(fast_index<FAST_COUNT){begin(NORMAL,0,t);return;}
    uint8_t code;
    if(svc_due(t,&code))begin(SERVICE,code,t);
}
int cn_tx_byte(uint8_t *byte) {if(!tx_len)return 0;*byte=tx[tx_pos];return 1;}
void cn_tx_sent(void) {
    if(tx_len && ++tx_pos==tx_len){tx_len=tx_pos=0;reply_at=now;++sent;}
}
uint16_t cn_read(unsigned a) {
    if(a>=600 && a<632)return diag_read(a);
    switch(a) {
    case 0:return 888;
    case 1:return 76;
    case 2:return valid?hz:65535;
    case 3:return valid;
    case 4:return ever?(uint16_t)(age_ms/1000u):65535;
    case 5:return replies;
    case 6:return rx_bytes;
    case 7:return errors;
    case 8:return sent;
    case 9:return (uint16_t)(now/1000u);
    case 11:return linked;
    case 12:return uart_errors;
    case 13:return last_type;
    case 14:return last_query;
    case 15:return handshakes;
    case 39:return owner;
    case 68:return 2; /* P0076 revision2: native pause handling. */
    case 69:return 1; /* MVP API version. */
    case 70:return 15; /* Telemetry/control/EFFECT/address identity. */
    case 71:return ctl_read(256); /* Revision2 control state. */
    default:if(a>=352)return feedback_read(a);if(a>=256)return ctl_read(a);return a>=100?tele_read(a):svc_read(a);
    }
}

uint8_t cn_command(const uint16_t words[8]) {
    if(words[0]==0x81d1)return diag_submit(words);
    if(diag_pending())return 6;
    return ctl_submit(words,now);
}

/* Fresh native curve mode and ordinary DHW authorization, no active session.
 * Maintenance never invents a restored snapshot or writes FTC settings. */
int maintenance_ready(void) {
    return linked && !diag_pending() && ctl_read(256)==0 && !owner && seen26 && seen28 &&
        now-native26_at<10000u && now-native28_at<10000u &&
        native26[6]==2 && native28[3]==0 && native28[5]==0 && native28[6]==0 &&
        native28[4]==0 && native28[10]==0;
}
