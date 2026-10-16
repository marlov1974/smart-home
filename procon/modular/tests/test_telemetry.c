/* P0072: independent numeric/protocol fixtures, no hardware I/O. */
#include "telemetry.h"
#include "service.h"
#include "control.h"
#include <assert.h>
static uint16_t control_state,control_mode,control_target;
uint16_t ctl_read(unsigned a) {return a==256?control_state:a==263?control_mode:a==275?control_target:0;}
#include <stdio.h>
#include <string.h>
static uint16_t status(unsigned i){return tele_read(140+i);}
static int32_t value(unsigned i){return (int32_t)(((uint32_t)tele_read(100+2*i)<<16)|tele_read(101+2*i));}
static void temps(unsigned flow,unsigned ret,unsigned dhw){
    uint8_t p[16]={0x0c};p[1]=flow>>8;p[2]=flow;p[4]=ret>>8;p[5]=ret;p[7]=dhw>>8;p[8]=dhw;tele_accept(p);
}
static void flow(unsigned v){uint8_t p[16]={0x14};p[12]=v;tele_accept(p);}
static void focus_service(void){
    uint8_t p[16]={0xa3,0,27,2,4,0},code;
    svc_init();svc_start_cycle();svc_sent(0);assert(svc_reply(p,10,1)); /* Cursor now28. */
    control_state=4;control_mode=2;control_target=6000;
    for(unsigned i=0;i<12;i++){
        unsigned t=2000+i*2000;
#ifdef PROCON_DELTA_SWEEP
        control_mode=i%3==0?0:2;control_target=(uint16_t)(2000+i*400);
#else
        control_mode=2;control_target=6000;
#endif
        svc_start_cycle();assert(svc_due(t,&code) && code==17);
        svc_sent(t);p[2]=17;p[3]=0;assert(svc_reply(p,t+10,1));
        if(i==5)control_state=0; /* Leaving the mission cannot change an owned retry. */
        assert(!svc_due(t+999,&code));assert(svc_due(t+1000,&code) && code==17);
        svc_sent(t+1000);p[3]=2;p[4]=(uint8_t)i;assert(svc_reply(p,t+1010,1));
        control_state=4;
    }
    assert(svc_read(378)==11 && svc_read(382)==12 && svc_read(376)==0);
    /* Exhaustion retains the ordinary queue position too. */
    svc_start_cycle();p[3]=0;
    for(unsigned i=0;i<10;i++){unsigned t=30000+i*1000;assert(svc_due(t,&code) && code==17);svc_sent(t);assert(svc_reply(p,t+10,1));}
    assert(svc_read(38)==1 && svc_read(379)==0);
    control_state=0;
    const uint8_t normal[]={28,18,19,16,17,27};
    for(unsigned i=0;i<6;i++){
        svc_start_cycle();assert(svc_due(41000,&code) && code==normal[i]);svc_sent(41000);
        p[2]=code;p[3]=2;assert(svc_reply(p,41010,1));
    }
    const uint16_t gates[][3]={{0,2,6000},{3,2,6000},{4,5,6000},{4,1,6000},{4,3,6000},{4,4,6000},{5,2,6000},{0,0,0},{3,0,0},{5,0,0}};
    for(unsigned i=0;i<sizeof gates/sizeof gates[0];i++){
        control_state=gates[i][0];control_mode=gates[i][1];control_target=gates[i][2];
        svc_init();svc_start_cycle();assert(svc_due(0,&code) && code==27);
    }
#ifndef PROCON_DELTA_SWEEP
    for(unsigned i=0;i<2;++i){
        control_state=4;control_mode=i?2:0;control_target=i?5999:0;
        svc_init();svc_start_cycle();assert(svc_due(0,&code) && code==27);
    }
#endif
    control_state=control_mode=control_target=0;svc_init();
    puts("PASS focused Service: explicit profile gating, repeated17, retry/expiry bounds, retained ordinary cursor and automatic exit");
}
int main(void){
    focus_service();
    svc_init();tele_init();
    for(unsigned i=0;i<20;++i){assert(value(i)==INT32_MIN);assert(status(i)==0);}
    temps(3500,3000,5000);flow(20);
    assert(value(3)==3500 && value(4)==3000 && value(5)==500 && value(14)==5000);
    assert(value(6)==2000 && value(7)==6966 && status(7)==1);
    assert(tele_read(208)==0x0d0c && tele_read(209)==0x00ac); /* exact raw bytes low-first */
    temps(3000,3500,5000);assert(value(7)==-6966);
    temps(3500,3500,5000);assert(value(7)==0 && status(7)==1);
    flow(0);assert(value(7)==0 && status(7)==1);
    temps(10000,0,10000);flow(200);assert(value(7)==1393333); /* largest accepted inputs */
    temps(0,10000,0);assert(value(7)==-1393333);
    temps(65535,3000,5000);assert(status(3)==3 && status(5)==3 && status(7)==3);
    temps(3500,3000,5000);flow(201);assert(status(6)==3 && status(7)==3);
    flow(255);assert(status(6)==3);
    flow(20);tele_tick(2001);flow(20);assert(status(7)==2); /* fresh but asynchronous */
    temps(3500,3000,5000);assert(status(7)==1);
    tele_tick(60000);assert(status(3)==2 && status(7)==2 && value(7)==INT32_MIN);
    tele_tick(UINT32_MAX);assert(tele_read(163)==65535 && status(3)==2);
    uint8_t p[16]={4,0};tele_accept(p);assert(value(8)==0 && value(9)==0 && status(9)==1);
    p[1]=48;tele_accept(p);assert(value(8)==48 && value(9)==1);
    tele_tick(59999);assert(status(8)==1 && status(9)==1);
    tele_tick(1);assert(status(8)==2 && status(9)==2);
    memset(p,0,sizeof p);p[0]=0x0b;p[11]=0;tele_accept(p);assert(value(15)==-4000);
    p[11]=111;tele_accept(p);assert(value(15)==1500); /* do not invent half-degree precision */
    p[11]=255;tele_accept(p);assert(status(15)==3);
    memset(p,0,sizeof p);p[0]=9;p[5]=0x0d;p[6]=0xac;tele_accept(p);assert(value(16)==3500);
    p[0]=0x26;p[8]=0x14;p[9]=0x50;p[4]=1;tele_accept(p);assert(value(17)==5200 && value(18)==1);
    for(unsigned i=0;i<8;++i){p[4]=i;tele_accept(p);assert(value(18)==(int32_t)i);}
    p[4]=255;tele_accept(p);assert(status(18)==3);
    memset(p,0,sizeof p);p[0]=0x15;p[1]=1;
    uint8_t codes[]={0x64,0x34,0x29,0x1f,0x14,0};
    for(unsigned i=0;i<6;++i){p[2]=codes[i];tele_accept(p);assert(value(12)==1 && value(13)==(int32_t)i);}
    p[2]=42;tele_accept(p);assert(status(13)==3);
    p[1]=255;tele_accept(p);assert(status(12)==3);
    memset(p,0,sizeof p);p[0]=0x14;p[2]=p[3]=p[4]=p[5]=1;tele_accept(p);assert(value(19)==15);
    p[2]=2;tele_accept(p);assert(status(19)==3);
    p[0]=4;p[1]=20;tele_accept(p);tele_invalidate();assert(status(8)==2);
    /* Each completed service keeps raw -1 distinct from unavailable. */
    svc_link(1,0);svc_sent(0);uint8_t b[16]={0xa3,0,27,2,0xff,0xff};assert(svc_reply(b,10,1));
    svc_start_cycle();svc_sent(100);b[2]=28;b[4]=0xfb;assert(svc_reply(b,110,1));
    assert(value(0)==-100 && value(1)==-500 && value(2)==400);
    svc_tick(60000,60110);assert(status(0)==2 && status(2)==2);
    assert(status(10)==0 && status(11)==0);
    svc_start_cycle();uint8_t code;assert(svc_due(60111,&code)&&code==18);
    svc_sent(60111);b[2]=18;b[3]=2;b[4]=7;b[5]=0;assert(svc_reply(b,60112,1));
    assert(value(11)==7 && status(11)==1 && svc_read(87)==7);
    svc_start_cycle();assert(svc_due(60113,&code)&&code==19);svc_sent(60113);
    b[2]=19;b[4]=0xc4;b[5]=9;assert(svc_reply(b,60114,1));
    assert(value(10)==1 && svc_read(93)==2500 && svc_read(94)==1);
    svc_link(0,60115);assert(status(10)==2 && status(11)==2 && value(10)==INT32_MIN);
    for(unsigned pass=0;pass<2;++pass){
        for(unsigned j=0;j<6;++j){
            svc_start_cycle();assert(svc_due(61000,&code));svc_sent(61000);
            b[2]=code;b[3]=2;b[4]=pass?0xff:0;b[5]=pass?0xff:0;
            assert(svc_reply(b,61001,1));
        }
        if(!pass)assert(value(10)==0 && value(11)==0 && status(10)==1 && status(11)==1);
    }
    assert(status(10)==3 && status(11)==3 && value(10)==INT32_MIN);
    svc_tick(60000,121000);assert(status(10)==2 && status(11)==2);
    svc_init();assert(status(10)==0 && status(11)==0);
    puts("PASS P0072 telemetry: all mapped queries, unavailable, raw bytes, signed/zero/boundary power, stale/skew/invalid propagation, pump codes, negative brine; ASan+UBSan");
}
