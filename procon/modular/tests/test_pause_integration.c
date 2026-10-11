/* P0076 r2: real sampler + controller, native pump model, no hardware I/O. */
#include "control.h"
#include "effect_feedback.h"
#include "telemetry.h"
#include "service.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
static uint32_t now;
static unsigned native_mode=2,native_target=2950,operating=0,hz=0,litres=0,sets;
static void accept(uint8_t p[16]){tele_accept(p);ctl_observe(p,now);}
static void sources(void){
    uint8_t p[16]={4};p[1]=(uint8_t)hz;accept(p);
    memset(p,0,16);p[0]=0x0c;p[1]=0x0b;p[2]=0x54; /*29C*/
    p[4]=0x0a;p[5]=0xf0; /*28C*/accept(p);
    memset(p,0,16);p[0]=0x14;p[12]=(uint8_t)litres;accept(p);
    memset(p,0,16);p[0]=0x26;p[3]=1;p[4]=(uint8_t)operating;p[6]=(uint8_t)native_mode;p[8]=0x14;p[9]=0x50;accept(p);
    memset(p,0,16);p[0]=0x28;ctl_observe(p,now);
}
static void feedback_tick(void){
    effect_feedback_tick(now);
    const effect_feedback_state *f=effect_feedback_get();
    tele_sample m,h;tele_snapshot(18,&m);tele_snapshot(8,&h);
    tele_sample supply;tele_snapshot(3,&supply);
    effect_measurement fb={.supply_cC=supply.value,.instant_w=f->instant_w,.short_w=f->short_w,.slow_w=f->slow_w,
        .age_ms=f->last_age_ms,.span_ms=f->short_span_ms,.quality=f->quality,.pairs=f->short_count,
        .mode=(uint16_t)m.value,.hz=(uint16_t)h.value,.ready=f->ready};
    ctl_feedback(&fb);ctl_tick(now);
}
static void step(void){
    tele_tick(100);now+=100;
    if(now%4000==0)sources();
    feedback_tick();
    uint8_t type,p[16],reply[16]={0};
    if(!ctl_next(&type,p,now))return;
    if(type==0x41){
        assert(p[0]==0x32);++sets;
        if(p[1]&8)native_mode=p[6];
        if(p[1]&0x80)native_target=(p[10]<<8)|p[11];
        assert(native_target<=3800);assert(ctl_reply(0x61,reply,1,now));
    }else{
        assert(type==0x42);reply[0]=p[0];
        if(p[0]==0x26){reply[3]=1;reply[4]=(uint8_t)operating;reply[6]=(uint8_t)native_mode;reply[8]=0x14;reply[9]=0x50;}
        else if(p[0]==9){reply[5]=(uint8_t)(native_target>>8);reply[6]=(uint8_t)native_target;}
        else assert(p[0]==0x28);
        assert(ctl_reply(0x62,reply,16,now));tele_accept(reply);
    }
}
static void until(uint32_t t){while(now<t)step();}
static void same_ms_transition(void){
    now=sets=0;native_mode=2;native_target=2950;operating=2;hz=30;litres=20;
    svc_init();tele_init();effect_feedback_init();ctl_init();sources();until(24000);
    assert(effect_feedback_get()->ready && effect_feedback_get()->quality==EF_READY);
    uint16_t cmd[8]={0xc076,1,5,6000,5500,180,1,3};assert(!ctl_submit(cmd,now));
    /* A CN105 GET26 arrives after the sampler ran in this same millisecond.
       cn_tick then sees a cached READY result and a newer native mode. */
    operating=0;
    uint8_t p[16]={0x26};p[3]=1;p[4]=0;p[6]=2;p[8]=0x14;p[9]=0x50;accept(p);
    feedback_tick();
    assert(effect_feedback_get()->ready && effect_feedback_get()->quality==EF_READY);
    assert(ctl_read(256)!=0 && ctl_read(260)!=8 && !sets);
    until(29000);assert(ctl_read(256)==4 && native_mode==1 && sets==1);
    uint16_t stop[8]={0xc072,2,1,0,0,0,0,2};assert(!ctl_submit(stop,now));until(34000);
    assert(ctl_read(256)==0 && native_mode==2 && native_target==2950 && !ctl_read(261));
    puts("PASS integrated sampler/control: same-ms cached READY/new native pause waits, applies and restores");
}
int main(void){
    svc_init();tele_init();effect_feedback_init();ctl_init();sources();until(100);
    uint16_t cmd[8]={0xc076,1,5,6000,3800,900,1,3};assert(!ctl_submit(cmd,now));
    until(5000);assert(ctl_read(256)==4 && native_mode==1 && native_target==2950 && sets==1);
    until(605000);assert(ctl_read(256)==4 && sets==1 && ctl_read(321)==EFFECT_WAIT_NATIVE && !ctl_read(346));
    cmd[1]=2;assert(!ctl_submit(cmd,now));
    operating=2;hz=30;litres=20;
    until(665000);assert(sets==1); /* Fresh60s plus the adjustment interval. */
    until(725000);assert(sets==1);
    until(735000);assert(sets==2 && native_target==3050 && ctl_read(344)==100 && !ctl_read(346));
    operating=0;hz=0;litres=0;until(740000);
    until(1340000);assert(sets==2 && ctl_read(256)==4 && ctl_read(344)==100 && !ctl_read(346));
    uint16_t stop[8]={0xc072,3,1,0,0,0,0,2};assert(!ctl_submit(stop,now));until(1350000);
    assert(ctl_read(256)==0 && native_mode==2 && native_target==2950 && ctl_read(267)==1);
    puts("PASS P0076 r2 integrated sampler/control: two10min pauses, zero flow, fresh restart, no prestart raises, budgets retained, AUTO restored");
    same_ms_transition();
}
