/* P0071: existing framing plus exclusive transaction arbitration. No SET frames. */
#include "cn105.h"
#include "service.h"
enum { NONE, CONNECT, NORMAL, SERVICE };
static uint8_t rx[22], tx[22], used, tx_len, tx_pos, owner;
static uint8_t linked, valid, ever, hz, last_type, last_query, polled;
static uint32_t now, last_byte, last_good, last_send, last_tick, age_ms;
static uint32_t reply_at, released_at;
static uint16_t replies, rx_bytes, errors, sent, uart_errors, handshakes;
static int started;
static uint8_t checksum(const uint8_t *b, unsigned n) {
    uint8_t sum=0;
    for(unsigned i=0;i<n;++i)sum=(uint8_t)(sum+b[i]);
    return (uint8_t)(0xfcu-sum);
}
static void release(uint32_t t) {owner=NONE;released_at=t;}
static void disconnect(uint32_t t) {
    linked=valid=polled=0;used=tx_len=tx_pos=0;release(t);svc_link(0,t);
}
static void begin(uint8_t kind, uint8_t code, uint32_t t) {
    owner=kind;started=1;last_send=t;tx_pos=0;
    tx[0]=0xfc;tx[1]=kind==CONNECT?0x5a:0x42;tx[2]=2;tx[3]=0x7a;
    tx[4]=kind==CONNECT?2:16;
    for(unsigned i=5;i<21;++i)tx[i]=0;
    if(kind==CONNECT){tx[5]=0xca;tx[6]=1;}
    else if(kind==NORMAL){tx[5]=4;polled=1;svc_start_cycle();}
    else {tx[5]=0xa3;tx[7]=code;svc_sent(t);}
    tx_len=(uint8_t)(tx[4]+6);tx[tx_len-1]=checksum(tx,tx_len-1);
}
void cn_init(void) {
    used=tx_len=tx_pos=owner=linked=valid=ever=hz=last_type=last_query=polled=0;
    now=last_byte=last_good=last_send=last_tick=age_ms=reply_at=released_at=0;
    replies=rx_bytes=errors=sent=uart_errors=handshakes=0;started=0;
    svc_init();svc_link(0,0);
}
static void bad_frame(void) {++errors;if(owner==SERVICE)svc_bad_frame();}
void cn_feed(uint8_t byte, uint32_t t, int error) {
    ++rx_bytes;
    if(error){++uart_errors;if(owner==SERVICE)svc_bad_frame();used=0;return;}
    if(used && t-last_byte>100u){bad_frame();used=0;}
    last_byte=t;
    if(!used && byte!=0xfc)return;
    rx[used++]=byte;
    if((used==3 && rx[2]!=2)||(used==4 && rx[3]!=0x7a)||(used==5 && rx[4]>16)) {
        bad_frame();used=0;return;
    }
    if(used<6 || used!=(unsigned)rx[4]+6u)return;
    unsigned n=used;used=0;
    if(checksum(rx,n-1)!=rx[n-1]){bad_frame();return;}
    last_type=rx[1];last_query=rx[4]?rx[5]:0;
    if(rx[1]==0x62 && rx[4]==16 && rx[5]==0xa3) {
        if(svc_reply(rx+5,t,linked && owner==SERVICE && !tx_len)) {last_good=t;release(t);}
    } else if(rx[1]==0x7a && rx[4]==1 && rx[5]==0 && owner==CONNECT && !tx_len) {
        linked=1;last_good=t;++handshakes;polled=0;svc_link(1,t);release(t);
    } else if(rx[1]==0x62 && rx[4]==16 && rx[5]==4 && linked && owner==NORMAL && !tx_len) {
        hz=rx[6];ever=valid=1;age_ms=0;last_good=t;++replies;release(t);
    }
}
void cn_tick(uint32_t t) {
    uint32_t dt=t-last_tick;last_tick=t;now=t;
    if(ever)age_ms=dt>=65535000u-age_ms?65535000u:age_ms+dt;
    if(valid && age_ms>=10000u)valid=0;
    svc_tick(dt,t);
    if(used && t-last_byte>100u){used=0;bad_frame();}
    if(linked && !owner && svc_read(32)==4 && t-last_good>=10000u)disconnect(t);
    if(owner) {
        if(tx_len && t-last_send>=1000u) {
            ++uart_errors;if(owner==SERVICE)svc_timeout(t);
            tx_len=tx_pos=0;release(t);
        } else if(!tx_len && t-reply_at>=800u) {
            if(owner==SERVICE)svc_timeout(t);
            release(t);
        } else return;
    }
    /* Turnaround/recovery guard. Late replies never release an unrelated owner. */
    if(t-released_at<50u)return;
    if(!linked) {
        if((!started && t>=1000u)||(started && t-last_send>=3000u))begin(CONNECT,0,t);
        return;
    }
    if(!polled || svc_read(32)==4){begin(NORMAL,0,t);return;}
    uint8_t code;
    if(svc_due(t,&code))begin(SERVICE,code,t);
}
int cn_tx_byte(uint8_t *byte) {if(!tx_len)return 0;*byte=tx[tx_pos];return 1;}
void cn_tx_sent(void) {
    if(tx_len && ++tx_pos==tx_len){tx_len=tx_pos=0;reply_at=now;++sent;}
}
uint16_t cn_read(unsigned a) {
    switch(a) {
    case 0:return 888;
    case 1:return 71;
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
    case 68:return 2; /* P0071 r2: exclusive Hz ->27 ->28 sequence. */
    default:return svc_read(a);
    }
}
