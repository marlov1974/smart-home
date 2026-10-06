/* P0070. Original code using documented ATW packet facts, no SET commands. */
#include "cn105.h"
static uint8_t rx[22], tx[22], used, tx_len, tx_pos;
static uint8_t linked, valid, ever, hz, last_type, last_query;
static uint32_t now, last_byte, last_good, last_send, last_tick, age_ms;
static uint16_t replies, rx_bytes, errors, sent, uart_errors, handshakes;
static int started;
static uint8_t checksum(const uint8_t *b, unsigned n) {
    uint8_t sum = 0;
    for (unsigned i=0; i<n; ++i) sum = (uint8_t)(sum + b[i]);
    return (uint8_t)(0xfcu - sum);
}
void cn_init(void) {
    used=tx_len=tx_pos=linked=valid=ever=hz=last_type=last_query=0;
    now=last_byte=last_good=last_send=last_tick=age_ms=0;
    replies=rx_bytes=errors=sent=uart_errors=handshakes=0;
    started=0;
}
void cn_feed(uint8_t byte, uint32_t t, int error) {
    ++rx_bytes;
    if (error) { ++uart_errors; used=0; return; }
    if (used && t-last_byte>100u) { ++errors; used=0; }
    last_byte=t;
    if (!used && byte!=0xfc) return;
    rx[used++]=byte;
    if ((used==3 && rx[2]!=2) || (used==4 && rx[3]!=0x7a) ||
        (used==5 && rx[4]>16)) {
        ++errors; used=0; return;
    }
    if (used<6 || used!=(unsigned)rx[4]+6u) return;
    unsigned n=used; used=0;
    if (checksum(rx,n-1)!=rx[n-1]) { ++errors; return; }
    last_type=rx[1]; last_query=rx[4]?rx[5]:0;
    if (rx[1]==0x7a && rx[4]==1 && rx[5]==0) {
        linked=1; last_good=t; ++handshakes;
    } else if (rx[1]==0x62 && rx[4]==16 && rx[5]==4 && linked) {
        hz=rx[6]; ever=valid=1; age_ms=0; last_good=t; ++replies;
    }
}
void cn_tick(uint32_t t) {
    uint32_t dt=t-last_tick; last_tick=t; now=t;
    if (ever) age_ms = dt>=65535000u-age_ms ? 65535000u : age_ms+dt;
    if (valid && age_ms>=10000u) valid=0;
    if (used && t-last_byte>100u) {used=0; ++errors;}
    if (linked && t-last_good>=10000u) { linked=0; valid=0; }
    if (tx_len) {
        /* Abort a stuck UART queue; retry on the normal cadence. */
        if (t-last_send>=1000u) {tx_len=tx_pos=0; ++uart_errors;}
        else return;
    }
    if (!started) { if(t<1000u) return; }
    else if (t-last_send < (linked?2000u:3000u)) return;
    started=1; last_send=t; tx_pos=0;
    tx[0]=0xfc;tx[1]=linked?0x42:0x5a;tx[2]=2;tx[3]=0x7a;
    tx[4]=linked?16:2;
    for (unsigned i=5;i<21;++i) tx[i]=0;
    if(linked) tx[5]=4;
    else {tx[5]=0xca;tx[6]=1;}
    tx_len=(uint8_t)(tx[4]+6);tx[tx_len-1]=checksum(tx,tx_len-1);
}
int cn_tx_byte(uint8_t *byte) {
    if (!tx_len) return 0;
    *byte=tx[tx_pos]; return 1;
}
void cn_tx_sent(void) {
    if (tx_len && ++tx_pos==tx_len) {tx_len=tx_pos=0;++sent;}
}
uint16_t cn_read(unsigned a) {
    switch(a) {
    case 0:return 888;
    case 1:return 70;
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
    default:return 0;
    }
}
