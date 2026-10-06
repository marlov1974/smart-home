/* P0070 protocol tests with independent wire fixtures. */
#include "cn105.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
static const uint8_t ack[]={0xfc,0x7a,2,0x7a,1,0,9};
static void feed(const uint8_t *p,unsigned n,uint32_t t) {
    cn_tick(t);
    for(unsigned i=0;i<n;++i)cn_feed(p[i],t,0);
}
static void frame(uint8_t *b,uint8_t hz) {
    memset(b,0,22);b[0]=0xfc;b[1]=0x62;b[2]=2;b[3]=0x7a;b[4]=16;b[5]=4;b[6]=hz;
    unsigned sum=0;for(unsigned i=0;i<21;++i)sum+=b[i];b[21]=(uint8_t)(0xfc-sum);
}
static unsigned drain(uint8_t *b) {
    unsigned n=0;while(cn_tx_byte(b+n)){cn_tx_sent();assert(++n<=22);}return n;
}
int main(void) {
    uint8_t b[22],tx[22];cn_init();
    assert(cn_read(0)==888 && cn_read(1)==70 && cn_read(2)==65535 && cn_read(4)==65535);
    cn_tick(999);assert(!cn_tx_byte(tx));cn_tick(1000);
    assert(drain(tx)==8 && memcmp(tx,"\xfc\x5a\x02\x7a\x02\xca\x01\x5d",8)==0);
    frame(b,48);feed(b,22,1100);assert(cn_read(3)==0); /* unsolicited response before handshake */
    feed(ack,7,1200);assert(cn_read(11)==1 && cn_read(15)==1);
    cn_tick(3000);assert(drain(tx)==22 && tx[1]==0x42 && tx[5]==4 && tx[21]==0x2e);
    feed(b,22,3200);assert(cn_read(2)==48 && cn_read(3)==1 && cn_read(5)==1);
    cn_tick(13200);assert(cn_read(2)==65535 && cn_read(3)==0 && cn_read(11)==0);
    assert(cn_read(4)==10);drain(tx);
    /* Old timestamp cannot resurrect valid after wrap. */
    cn_tick(3200);assert(cn_read(3)==0 && cn_read(4)==65535);drain(tx);
    for(unsigned hz=0;hz<=255;hz+= (hz==0?48:207)) {
        cn_init();feed(ack,7,1);frame(b,(uint8_t)hz);feed(b,22,5);
        assert(cn_read(2)==hz && cn_read(3)==1);
        if(hz==255)break;
    }
    cn_init();feed(ack,7,1);frame(b,48);b[21]^=1;feed(b,22,5);
    assert(cn_read(3)==0 && cn_read(7)==1);
    frame(b,48);for(unsigned i=0;i<11;++i)cn_feed(b[i],10,0);
    cn_tick(111);assert(cn_read(7)==2);feed(b,22,112);assert(cn_read(2)==48);
    cn_init();feed(ack,7,1);frame(b,48);
    for(unsigned i=0;i<22;++i)cn_feed(b[i],10,i==8);
    assert(cn_read(3)==0 && cn_read(12)==1);feed(b,22,120);assert(cn_read(3)==1);
    cn_init();feed(ack,7,0xfffffff0u);frame(b,48);feed(b,22,0xfffffff5u);
    cn_tick(20);assert(cn_read(3)==1);cn_tick(10020);assert(cn_read(3)==0);
    cn_init();cn_tick(1000);cn_tick(2000);assert(cn_read(12)==1 && !cn_tx_byte(tx));
    cn_tick(4000);assert(drain(tx)==8);
    /* Every single bit corruption must not become valid telemetry. */
    for(unsigned bit=0;bit<176;++bit){cn_init();feed(ack,7,1);frame(b,48);b[bit/8]^=1u<<(bit%8);feed(b,22,5);assert(cn_read(3)==0);}
    /* Malformed serial stream bounded under ASan/UBSan. */
    cn_init();uint32_t rng=23;for(unsigned i=0;i<200000;++i){rng=rng*1664525u+1013904223u;cn_tick(i);cn_feed(rng>>24,i,0);if(i%11==0)drain(tx);}
    assert(cn_read(3)==0);
    puts("PASS CN105: connect/GET fixtures, 0/48/255Hz, validity/stale/reconnect/wrap, checksum/gap/UART errors, stuck TX,176 bit corruptions,200000 malformed bytes");
}
