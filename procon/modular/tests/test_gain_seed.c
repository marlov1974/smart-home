/* P0080 RAM-only, exact-UID-bound long-term gain import. No EEPROM/flash. */
#include "effect_model.h"
#include "identity.h"
#include "modbus.h"
#include "telemetry.h"
#include <assert.h>
#include <stdio.h>

uint8_t debug_command(const uint16_t words[8]);
static int quiescent=1;
static unsigned passthrough;
static tele_sample samples[20];
static uint16_t hz=50,hgen;

int maintenance_ready(void){return quiescent;}
uint8_t cn_command(const uint16_t words[8]){(void)words;++passthrough;return 4;}
uint16_t cn_read(unsigned address){(void)address;return 0;}
uint16_t tele_read(unsigned address){(void)address;return 0;}
int tele_snapshot(unsigned i,tele_sample *out){if(i>=20)return 0;*out=samples[i];return 1;}
uint16_t svc_read(unsigned a){
    switch(a){case 372:return hz;case 373:case 377:return 1;case 374:return 0;case 376:return hgen;default:return 0;}
}
static void packet(uint16_t out[8],uint16_t gain){
    out[0]=0xc077;out[1]=gain;
    for(unsigned i=0;i<6;++i)out[2+i]=identity_read(78+i);
}
static uint8_t modbus_seed(const uint16_t words[8],uint8_t slave,int corrupt){
    uint8_t request[25]={0},reply[16];request[0]=slave;request[1]=16;request[2]=1;request[3]=44;
    request[5]=8;request[6]=16;
    for(unsigned i=0;i<8;++i){request[7+2*i]=(uint8_t)(words[i]>>8);request[8+2*i]=(uint8_t)words[i];}
    uint16_t crc=crc16(request,23);request[23]=(uint8_t)crc;request[24]=(uint8_t)(crc>>8);
    if(corrupt)request[24]^=1;
    size_t n=modbus_reply(request,sizeof request,reply,sizeof reply);
    if(slave!=1 || corrupt){assert(!n);return 255;}
    assert((n==8 && reply[1]==16) || (n==5 && reply[1]==0x90));
    assert(crc16(reply,n)==0);return n==8?0:reply[2];
}
static void learn_bias(void){
    for(unsigned i=0;i<20;++i)samples[i]=(tele_sample){0,0,0,TELE_VALID,0};
    samples[0].value=400;samples[3].value=3500;samples[4].value=3000;
    samples[6].value=1900;samples[7].value=6660;samples[18].value=2;
    for(unsigned t=0;t<=120000;t+=10000){
        for(unsigned i=0;i<20;++i)++samples[i].generation;
        hgen=(uint16_t)(t/40000);effect_model_tick(t,1);
    }
}
int main(void){
    const uint32_t uid[3]={0x01234567u,0x89abcdefu,0x13579bdfu};
    identity_init_dip(uid,0x61,1);effect_model_reset();
    assert(effect_model_gain()==1350 && effect_model_bias()==-1090);
    assert(!effect_model_seeded() && !effect_model_seeded_gain());

    uint16_t w[8];packet(w,1420);quiescent=0;
    assert(modbus_seed(w,1,0)==6 && effect_model_gain()==1350 && !effect_model_seeded());
    quiescent=1;assert(modbus_seed(w,2,0)==255 && modbus_seed(w,1,1)==255);

    /* Every UID word is matched exactly before first acceptance. */
    for(unsigned i=0;i<6;++i){w[2+i]^=1;assert(debug_command(w)==3);w[2+i]^=1;}
    assert(!effect_model_seeded() && effect_model_gain()==1350);
    assert(!modbus_seed(w,1,0));
    assert(effect_model_gain()==1420 && effect_model_seeded() && effect_model_seeded_gain()==1420);

    /* Exact retry is idempotent even when busy. Any changed payload is locked
       out for the rest of this boot. */
    quiescent=0;assert(!debug_command(w));
    w[1]=1430;assert(debug_command(w)==3 && effect_model_gain()==1420);
    w[1]=1420;w[7]^=1;assert(debug_command(w)==3 && effect_model_gain()==1420);w[7]^=1;
    quiescent=1;w[1]=1430;assert(debug_command(w)==3 && effect_model_gain()==1420);

    /* Range rejection cannot consume the one seed slot. */
    effect_model_reset();packet(w,699);assert(debug_command(w)==3 && !effect_model_seeded());
    packet(w,2001);assert(debug_command(w)==3 && !effect_model_seeded());
    packet(w,700);assert(!debug_command(w) && effect_model_gain()==700);

    /* Acceptance changes gain only; learned offset/counters remain volatile
       and untouched. The actuator trim is checked in test_effect.c. */
    effect_model_reset();learn_bias();
    assert(effect_model_bias()==-990 && effect_model_updates(0)==1);
    uint16_t updates=effect_model_updates(0),slopes=effect_model_updates(1);
    packet(w,1500);assert(!debug_command(w));
    assert(effect_model_gain()==1500 && effect_model_bias()==-990 &&
           effect_model_updates(0)==updates && effect_model_updates(1)==slopes);
    assert(effect_model_seeded());

    /* Reset models a reboot: deterministic fallback and one fresh seed slot. */
    effect_model_reset();
    assert(effect_model_gain()==1350 && effect_model_bias()==-1090);
    assert(!effect_model_seeded() && !effect_model_seeded_gain());
    packet(w,2000);assert(!debug_command(w));
    assert(effect_model_gain()==2000 && effect_model_seeded());

    uint16_t ordinary[8]={0xc076};assert(debug_command(ordinary)==4 && passthrough==1);
    puts("PASS gain seed: exact96-bit UID, range, busy gate, one-per-boot/idempotent import, gain-only state and reboot fallback");
}
