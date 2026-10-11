/* P0076: independent protocol fixtures for genuine-generation feedback, no I/O. */
#include "effect_feedback.h"
#include "telemetry.h"
#include "service.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
static uint32_t now;
static const effect_feedback_state *s(void){return effect_feedback_get();}
static void at(uint32_t t){tele_tick(t-now);now=t;}
static void poll(void){effect_feedback_tick(now);}
static void reset(uint32_t start){svc_init();tele_init();effect_feedback_init();now=start;}
static void temps(unsigned supply,unsigned ret){
    uint8_t p[16]={0x0c};p[1]=(uint8_t)(supply>>8);p[2]=(uint8_t)supply;
    p[4]=(uint8_t)(ret>>8);p[5]=(uint8_t)ret;p[7]=0x13;p[8]=0x88;tele_accept(p);
}
static void flow(unsigned litres){uint8_t p[16]={0x14};p[12]=(uint8_t)litres;tele_accept(p);}
static void hz(unsigned value){uint8_t p[16]={4};p[1]=(uint8_t)value;tele_accept(p);}
static void mode(unsigned state){hz(30);uint8_t p[16]={0x26};p[4]=(uint8_t)state;tele_accept(p);}
static void cycle(uint32_t t,unsigned litres,unsigned supply,unsigned ret){at(t);temps(supply,ret);flow(litres);mode(2);poll();}
static void ready(void){reset(0);cycle(0,20,3500,3000);cycle(10000,20,3500,3000);cycle(20000,20,3500,3000);assert(s()->ready && s()->quality==EF_READY);}
static void assert_empty(unsigned quality){assert(s()->quality==quality && !s()->ready && !s()->short_count && !s()->slow_count && s()->short_w==INT32_MIN && s()->instant_w==INT32_MIN);}
int main(void){
    reset(0);poll();assert_empty(EF_WARMUP);assert(s()->last_age_ms==UINT32_MAX);
    tele_sample snapshot;assert(!tele_snapshot(20,&snapshot) && !tele_snapshot(0,0));
    cycle(1,20,3500,3000);assert(s()->accepted_count==1 && s()->short_count==1 && !s()->ready);
    assert(s()->instant_w==6966 && s()->short_w==6966 && s()->slow_w==6966);
    assert(tele_snapshot(7,&snapshot) && snapshot.value==6966 && snapshot.age_ms==0 && snapshot.status==TELE_VALID);
    for(unsigned n=0;n<100;++n){at(now+1);poll();}assert(s()->accepted_count==1); /* duplicate observations aren't samples */
    cycle(10001,20,3500,3000);assert(s()->short_count==2 && !s()->ready);
    cycle(20001,20,3500,3000);assert(s()->short_count==3 && s()->short_span_ms==20000 && s()->ready);
    assert(s()->derivative_w_per_min==0);

    /* Both source generations must advance: neither GET0C nor GET14 alone counts. */
    ready();uint32_t accepted=s()->accepted_count;uint16_t tg=s()->temp_gen,fg=s()->flow_gen;
    at(30000);temps(3600,3000);mode(2);poll();
    assert(s()->quality==EF_PENDING && !s()->ready && s()->short_count==3 && s()->accepted_count==accepted);
    assert(s()->temp_gen==tg && s()->flow_gen==fg);
    at(31000);flow(20);poll();assert(s()->quality==EF_PENDING); /* GET26 predates newest source */
    at(31001);mode(2);poll();assert(s()->quality==EF_READY && s()->accepted_count==accepted+1);
    accepted=s()->accepted_count;
    at(40000);flow(21);mode(2);poll();assert(s()->quality==EF_PENDING && s()->accepted_count==accepted);
    at(41000);temps(3600,3000);mode(2);poll();assert(s()->accepted_count==accepted+1);

    /* Sampling spacing is based on acquisition time, never aging a cached pair into new data. */
    reset(0);cycle(0,20,3500,3000);cycle(1000,20,3500,3000);assert(s()->accepted_count==1 && s()->quality==EF_PENDING);
    at(4000);poll();assert(s()->accepted_count==1);cycle(4001,20,3500,3000);assert(s()->accepted_count==2);

    /* Exact source-skew boundary; synchronous public seconds would miss the one-ms difference. */
    reset(0);temps(3500,3000);at(2000);flow(20);mode(2);poll();assert(s()->accepted_count==1 && s()->instant_w==6966);
    reset(0);temps(3500,3000);at(2001);flow(20);mode(2);poll();assert(s()->quality==EF_PENDING && !s()->accepted_count);
    ready();at(30000);temps(3500,3000);at(32001);flow(20);mode(2);poll();
    assert(s()->quality==EF_PENDING && s()->short_count==3); /* incomplete/asynchronous pair doesn't flush valid history */
    at(80000);poll();assert_empty(EF_STALE); /* finite wait; no retained valid-looking feedback */

    /* Measurements remain fresh through59999ms, expire at60000ms. */
    reset(0);cycle(0,20,3500,3000);at(59999);poll();
    assert(s()->quality==EF_WARMUP && s()->short_count==1);
    at(60000);poll();assert_empty(EF_STALE);assert(s()->last_age_ms==60000);
    cycle(60001,20,3500,3000);assert(s()->quality==EF_WARMUP && s()->short_count==1);

    /* Zero delta is valid zero heat; zero flow is unusable regulation feedback. */
    ready();cycle(30000,20,3000,3000);assert(s()->instant_w==0 && s()->short_count==4);
    cycle(40000,0,3500,3000);assert_empty(EF_ZEROFLOW);
    cycle(50000,20,2900,3000);assert_empty(EF_INVALID);
    cycle(60000,255,3500,3000);assert_empty(EF_INVALID);
    cycle(70000,20,65535,3000);assert_empty(EF_INVALID);
    cycle(80000,20,3500,3000);assert(s()->quality==EF_WARMUP && s()->short_count==1);

    /* A DHW transition cannot be hidden inside old averages or reused after heating returns. */
    ready();at(30000);temps(5500,4800);flow(20);hz(30);poll();assert(s()->quality==EF_PENDING && s()->short_count==3);
    at(30001);mode(1);poll();assert_empty(EF_DHW);accepted=s()->accepted_count;
    at(30002);mode(2);poll();assert(s()->quality==EF_WARMUP && !s()->short_count && s()->accepted_count==accepted);
    cycle(40000,20,3500,3000);assert(s()->short_count==1 && !s()->ready);
    at(40001);mode(6);poll();assert_empty(EF_DHW);
    at(40002);mode(3);poll();assert_empty(EF_INVALID);
    at(40003);mode(0);poll();assert_empty(EF_WAIT_NATIVE);

    /* Link loss is separately reported while legacy Modbus status remains STALE. */
    ready();tele_invalidate();at(20001);poll();assert_empty(EF_LINKLOSS);
    assert(tele_read(143)==TELE_STALE && tele_snapshot(3,&snapshot) && snapshot.link_lost);
    at(20002);mode(2);poll();assert_empty(EF_STALE);
    cycle(30000,20,3500,3000);assert(s()->short_count==1 && !s()->ready);

    /* Independent wrapping 16-bit source counters are compared as tokens, not summed arithmetic. */
    reset(0);for(unsigned i=0;i<65535u;++i){temps(3500,3000);flow(20);}mode(2);poll();
    assert(s()->temp_gen==65535 && s()->flow_gen==65535 && s()->accepted_count==1);
    cycle(10000,20,3500,3000);assert(s()->temp_gen==0 && s()->flow_gen==0 && s()->accepted_count==2);
    at(20000);temps(3500,3000);mode(2);poll();assert(s()->accepted_count==2 && s()->quality==EF_PENDING);
    at(20001);flow(20);mode(2);poll();assert(s()->temp_gen==1 && s()->flow_gen==1 && s()->accepted_count==3);

    /* Wall-clock wrap remains correct for freshness, minimum spacing and window spans. */
    reset(0xffffe000u);cycle(now,20,3500,3000);cycle(0xffffe000u+10000u,20,3500,3000);cycle(0xffffe000u+20000u,20,3500,3000);
    assert(s()->ready && s()->short_span_ms==20000 && s()->accepted_count==3);

    /* Exact finite windows, quantized values and fixed storage over long simulated runs. */
    reset(0);int64_t last_seven=0,last_nineteen=0;
    for(unsigned i=0;i<=100;++i){
        unsigned litres=i%2?19:20;cycle(i*10000u,litres,3500,3000);
        if(i>=94)last_seven+=(int32_t)((int64_t)litres*100*500*418/60000);
        if(i>=82)last_nineteen+=(int32_t)((int64_t)litres*100*500*418/60000);
    }
    assert(s()->accepted_count==101 && s()->short_count==7 && s()->slow_count==19);
    assert(s()->short_span_ms==60000 && s()->slow_span_ms==180000);
    assert(s()->short_w==last_seven/7 && s()->slow_w==last_nineteen/19 && s()->ready);
    at(now+1);poll();assert(s()->short_count==6 && s()->slow_count==18);
    assert(s()->short_span_ms==50000 && s()->slow_span_ms==170000);
    assert(!effect_feedback_hard_invalid(EF_READY) && !effect_feedback_hard_invalid(EF_WARMUP) && !effect_feedback_hard_invalid(EF_PENDING));
    for(unsigned q=EF_STALE;q<=EF_LINKLOSS;++q)assert(effect_feedback_hard_invalid(q));
    effect_feedback_init();assert_empty(EF_WARMUP);assert(!s()->accepted_count); /* reset never pretends to preserve control/history */
    /* A ten-minute native pause, including zero flow, clears history without
       blessing sensor failure. Startup must build fresh paired history for60s. */
    ready();at(30000);temps(3000,3050);flow(0);mode(0);hz(0);poll();assert_empty(EF_WAIT_NATIVE);
    for(unsigned i=1;i<=60;++i){at(30000+i*10000);temps(3000,3050);flow(0);mode(0);hz(0);poll();assert_empty(EF_WAIT_NATIVE);}
    accepted=s()->accepted_count;
    cycle(640000,20,3500,3000);assert(s()->quality==EF_SETTLING && !s()->ready && s()->short_count==1);
    for(unsigned i=1;i<6;++i){cycle(640000+i*10000,20,3500,3000);assert(s()->quality==EF_SETTLING && !s()->ready);}
    cycle(700000,20,3500,3000);assert(s()->ready && s()->quality==EF_READY && s()->accepted_count==accepted+7);
    /* A brief Hz pulse does not shorten the next recovery interval. */
    at(710000);temps(3000,3000);flow(0);mode(2);hz(0);poll();assert_empty(EF_WAIT_NATIVE);
    cycle(720000,20,3500,3000);assert(s()->quality==EF_SETTLING);
    at(730000);temps(3000,3000);flow(0);mode(2);hz(0);poll();assert_empty(EF_WAIT_NATIVE);
    cycle(740000,20,3500,3000);assert(s()->quality==EF_SETTLING && s()->short_count==1);
    /* Real FAST restart order: Hz first, old idle zero-flow must await new pair. */
    at(740100);temps(3000,3000);flow(0);mode(2);hz(0);poll();assert_empty(EF_WAIT_NATIVE);
    at(740200);hz(30);poll();assert(s()->quality==EF_SETTLING);
    at(744300);temps(3500,3000);poll();assert(s()->quality==EF_SETTLING);
    at(744400);flow(20);poll();assert(s()->quality==EF_SETTLING);
    at(744500);{uint8_t p[16]={0x26};p[4]=2;tele_accept(p);}poll();assert(s()->quality==EF_SETTLING && s()->short_count==1);
    /* Stale Hz, invalid sensors and DHW remain errors even during pause. */
    at(750000);temps(3000,3000);flow(0);mode(0);hz(0);poll();assert_empty(EF_WAIT_NATIVE);
    at(810000);temps(3000,3000);flow(0);poll();assert_empty(EF_STALE);
    at(810001);temps(65535,3000);mode(0);hz(0);poll();assert_empty(EF_INVALID);
    at(810002);temps(3000,3000);mode(1);hz(0);poll();assert_empty(EF_DHW);
    at(810003);mode(0);hz(255);poll();assert_empty(EF_INVALID);
    puts("PASS P0076 feedback: independent generations, trailing heating mode, zero/invalid/link guards, skew/age edges, bounded exact windows, quantization, wrap and clean reset");
}
