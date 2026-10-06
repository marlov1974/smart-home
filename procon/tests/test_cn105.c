/* P0071 independent protocol fixtures and transaction-level regression. */
#include "cn105.h"
#include "service.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
static const uint8_t fast_codes[]={4,0x0c,0x14,0x0b,9,0x15,0x26};
static const uint8_t ack[]={0xfc,0x7a,2,0x7a,1,0,9};
static unsigned seal(uint8_t *b,unsigned n) {
    unsigned sum=0;for(unsigned i=0;i<n-1;++i)sum+=b[i];b[n-1]=(uint8_t)(0xfc-sum);return n;
}
static void response(uint8_t *b,unsigned query,unsigned code,unsigned status,int value) {
    memset(b,0,22);b[0]=0xfc;b[1]=0x62;b[2]=2;b[3]=0x7a;b[4]=16;b[5]=(uint8_t)query;
    if(query==4)b[6]=(uint8_t)value;
    else {b[7]=(uint8_t)code;b[8]=(uint8_t)status;b[9]=(uint8_t)value;b[10]=(uint8_t)((uint16_t)value>>8);}
    seal(b,22);
}
static void feed(const uint8_t *b,unsigned n,uint32_t t) {for(unsigned i=0;i<n;++i)cn_feed(b[i],t,0);}
static unsigned drain(uint8_t *b) {unsigned n=0;while(cn_tx_byte(b+n)){cn_tx_sent();assert(++n<=22);}return n;}
/* Modes:0 pending->complete,1 forever pending,2 drop services,3 bad checksum,
 *4 wrong echo,5 terminal status6,6 no replies at all,7 delayed late A3. */
static void simulation(unsigned mode,uint32_t base,unsigned duration) {
    cn_init();uint8_t tx[22],rx[22],late[22];unsigned rxlen=0,late_len=0;
    uint32_t due=0,late_due=0,last_service[2]={0};
    unsigned count[2]={0},normals=0,connected=0,phase=4,phase_attempts=0,fast=0,next=27;
    for(unsigned step=0;step<duration;++step) {
        uint32_t t=base+step;cn_tick(t);
        if(rxlen && (int32_t)(t-due)>=0){feed(rx,rxlen,t);rxlen=0;}
        if(late_len && (int32_t)(t-late_due)>=0){feed(late,late_len,t);late_len=0;}
        unsigned n=drain(tx);
        if(n) {
            assert(!rxlen); /* arbiter cannot transmit while normal reply is pending */
            unsigned sum=0;for(unsigned i=0;i<n;++i)sum+=tx[i];assert((sum&255)==252);
            if(tx[1]==0x5a){assert(n==8 && memcmp(tx,"\xfc\x5a\x02\x7a\x02\xca\x01\x5d",8)==0);memcpy(rx,ack,7);rxlen=7;++connected;}
            else {
                assert(tx[1]==0x42 && n==22 && tx[2]==2 && tx[3]==0x7a && tx[4]==16);
                if(tx[5]!=0xa3) {
                    assert(phase==4 && tx[5]==fast_codes[fast]);
                    if(!fast){++normals;}
                    if(++fast==7){fast=0;phase=next;phase_attempts=0;}
                    response(rx,tx[5],0,0,20+(int)(normals%30));rxlen=22;
                } else {
                    assert(tx[5]==0xa3 && tx[6]==0 && (tx[7]==27 || tx[7]==28));
                    for(unsigned i=8;i<21;++i)assert(tx[i]==0);
                    unsigned idx=tx[7]-27;assert(tx[21]==(idx?0x73:0x74));
                    assert(tx[7]==phase);++phase_attempts;assert(phase_attempts<=10);
                    if(phase_attempts>1)assert(t-last_service[idx]>=1000u);
                    last_service[idx]=t;++count[idx];
                    unsigned status=mode==0 && count[idx]%3==0?idx+1:0;
                    if(mode==5)status=6;
                    response(rx,0xa3,tx[7],status,idx?-3:7);rxlen=22;
                    if(mode==2)rxlen=0;
                    if(mode==3)rx[21]^=1;
                    if(mode==4){rx[7]=(uint8_t)(idx?27:28);seal(rx,22);}
                    if(mode==7){memcpy(late,rx,22);late_len=22;late_due=t+900;rxlen=0;}
                    if((mode==0 && status) || mode==5 || phase_attempts==10) {
                        next=phase==27?28:27;phase=4;phase_attempts=0;
                    }
                }
            }
            if(mode==6)rxlen=0;
            due=t+50;
        }
        if(cn_read(3))assert(cn_read(4)<10);
        else assert(cn_read(2)==65535);
    }
    assert(cn_read(0)==888 && cn_read(1)==72);
    if(mode==6){assert(cn_read(3)==0 && connected>=3);return;}
    assert(normals>=3 && cn_read(5)>=normals-1);
    assert(count[0] && count[1]);
    if(mode==0) {
        assert(cn_read(18)==1 && cn_read(26)==1 && cn_read(16)==7 && cn_read(24)==65533);
        assert(cn_read(42)>=2);
        assert(cn_read(52)==0x00a3 && cn_read(53)==0x011b && cn_read(54)==7);
        assert(cn_read(60)==0x00a3 && cn_read(61)==0x021c && cn_read(62)==65533);
        assert(cn_read(7)==0 && cn_read(12)==0 && cn_read(37)==0);
    } else {
        assert(cn_read(18)==0 && cn_read(26)==0);
        if(mode!=5)assert(cn_read(38)>=2);
        if(mode>=2)assert(cn_read(37)>0);
    }
    printf("PASS CN105 service simulation mode%u, base%u, normal%u, svc27=%u svc28=%u cycles%u\n",mode,base,normals,count[0],count[1],cn_read(42));
}
static void service_units(void) {
    uint8_t p[16]={0xa3,0,27,1,0xff,0xff},code;
    /* Exact finite retry bound, including minimum cadence and zero retry budget after10. */
    svc_init();svc_link(1,0);p[3]=0;
    for(unsigned i=0;i<10;++i) {
        uint32_t t=i*1000u;assert(svc_due(t,&code) && code==27);svc_sent(t);
        assert(svc_reply(p,t+10,1));
        if(i<9)assert(!svc_due(t+999,&code));
    }
    assert(svc_read(38)==1 && !svc_due(10000,&code));
    svc_start_cycle();assert(svc_due(10000,&code) && code==28);
    p[3]=1;
    svc_init();svc_link(1,0);assert(svc_due(0,&code) && code==27);svc_sent(0);
    assert(svc_reply(p,10,1) && svc_read(16)==65535 && svc_read(18)==1); /* -1 is real, not missing */
    assert(!svc_due(11,&code));svc_start_cycle();
    assert(svc_due(11,&code) && code==28);svc_sent(11);p[2]=28;p[3]=2;p[4]=0;p[5]=0;
    assert(svc_reply(p,20,1) && svc_read(24)==0 && svc_read(26)==1);
    svc_tick(60000,60020);assert(svc_read(18)==0 && svc_read(26)==0 && svc_read(22)==1);
    assert(svc_read(52)==0xa3 && svc_read(54)==65535); /* retained completion */
    svc_tick(0xffffffffu,500);assert(svc_read(19)==65535 && svc_read(18)==0);
    svc_link(0,500);assert(svc_read(32)==5 && svc_read(33)==0);
    svc_link(1,600);assert(svc_due(600,&code) && code==27);
    svc_sent(600);p[2]=28;assert(!svc_reply(p,650,1) && svc_read(32)==2);
    assert(!svc_reply(p,650,0));
}
static void parser_units(void) {
    uint8_t b[22],tx[22];cn_init();cn_tick(1000);assert(drain(tx)==8);feed(ack,7,1050);
    cn_tick(1100);assert(drain(tx)==22 && tx[5]==4);
    response(b,0x0c,0,0,48);feed(b,22,1140);assert(cn_read(3)==0 && cn_read(39)==2);
    response(b,4,0,0,0);feed(b,22,1150);assert(cn_read(2)==0 && cn_read(3)==1);
    for(unsigned i=1;i<7;++i){cn_tick(1150+i*100);assert(drain(tx)==22 && tx[5]==fast_codes[i]);
        response(b,tx[5],0,0,0);feed(b,22,1200+i*100);}
    cn_tick(1850);assert(drain(tx)==22 && tx[5]==0xa3);
    response(b,0xa3,27,1,7);b[21]^=1;feed(b,22,1900);assert(cn_read(18)==0 && cn_read(39)==3);
    response(b,0xa3,28,1,7);feed(b,22,1900);assert(cn_read(18)==0 && cn_read(39)==3);
    response(b,0xa3,27,1,7);feed(b,22,1900);assert(cn_read(18)==1 && cn_read(39)==0);
    for(unsigned bit=0;bit<176;++bit){
        cn_init();cn_tick(1000);drain(tx);feed(ack,7,1050);cn_tick(1100);drain(tx);
        response(b,4,0,0,48);b[bit/8]^=1u<<(bit%8);feed(b,22,1150);assert(cn_read(3)==0);
    }
    cn_init();cn_tick(1000);cn_tick(2000);assert(cn_read(12)==1); /* stuck TX */
    cn_init();cn_tick(1000);drain(tx);feed(ack,7,1050);cn_tick(1100);drain(tx);
    response(b,4,0,0,255);feed(b,11,1150);cn_tick(1251);assert(cn_read(7)==1);feed(b,22,1252);assert(cn_read(2)==255);
    cn_tick(11252);assert(cn_read(3)==0 && cn_read(2)==65535); /* Hz ages honestly while services own the operation. */
    cn_init();cn_tick(1000);drain(tx);feed(ack,7,1050);cn_tick(1100);drain(tx);
    response(b,4,0,0,48);for(unsigned i=0;i<22;++i)cn_feed(b[i],1150,i==8);
    assert(cn_read(12)==1 && cn_read(3)==0);feed(b,22,1250);assert(cn_read(2)==48);
    cn_init();uint32_t rng=23;
    for(unsigned i=0;i<200000;++i){rng=rng*1664525u+1013904223u;cn_tick(i);cn_feed(rng>>24,i,0);if(i%11==0)drain(tx);}
    assert(cn_read(3)==0);
}
int main(void) {
    service_units();parser_units();
    for(unsigned mode=0;mode<=7;++mode)simulation(mode,0,65000);
    simulation(0,0xfffff000u,65000);
    puts("PASS CN105 P0072: protocol/ownership/retry/exhaustion/retained raw/TTL/wrap/reconnect/exclusive FAST->27->FAST->28 sequence; ASan+UBSan");
}
