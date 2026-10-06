/* P0072: independent numeric/protocol fixtures, no hardware I/O. */
#include "telemetry.h"
#include "service.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
static uint16_t status(unsigned i){return tele_read(140+i);}
static int32_t value(unsigned i){return (int32_t)(((uint32_t)tele_read(100+2*i)<<16)|tele_read(101+2*i));}
static void temps(unsigned flow,unsigned ret,unsigned dhw){
    uint8_t p[16]={0x0c};p[1]=flow>>8;p[2]=flow;p[4]=ret>>8;p[5]=ret;p[7]=dhw>>8;p[8]=dhw;tele_accept(p);
}
static void flow(unsigned v){uint8_t p[16]={0x14};p[12]=v;tele_accept(p);}
int main(void){
    svc_init();tele_init();
    for(unsigned i=0;i<20;++i){assert(value(i)==INT32_MIN);assert(status(i)==(i==10||i==11?4:0));}
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
    tele_tick(30000);assert(status(3)==2 && status(7)==2 && value(7)==INT32_MIN);
    tele_tick(UINT32_MAX);assert(tele_read(163)==65535 && status(3)==2);
    uint8_t p[16]={4,0};tele_accept(p);assert(value(8)==0 && value(9)==0 && status(9)==1);
    p[1]=48;tele_accept(p);assert(value(8)==48 && value(9)==1);
    tele_tick(10000);assert(status(8)==2 && status(9)==2);
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
    assert(status(10)==4 && status(11)==4);
    puts("PASS P0072 telemetry: all mapped queries, unavailable, raw bytes, signed/zero/boundary power, stale/skew/invalid propagation, pump codes, negative brine; ASan+UBSan");
}
