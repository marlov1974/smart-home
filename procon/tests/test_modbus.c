/* P0069: host tests run under address/undefined sanitizers. */
#include "modbus.h"
#include "cn105.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
static const uint8_t read0[] = {1,4,0,0,0,1,0x31,0xca};
static void seal(uint8_t *r, size_t n) {
    uint16_t c=crc16(r,n-2); r[n-2]=(uint8_t)c; r[n-1]=(uint8_t)(c>>8);
}
static uint32_t feed(rtu_state *s, const uint8_t *r, size_t n, uint32_t now, int error) {
    for(size_t i=0;i<n;i++,now+=1042) rtu_feed(s,r[i],now,error);
    return now-1042;
}
int main(void) {
    cn_init();
    uint8_t out[260], r[260];
    assert(crc16(read0,6)==0xca31 && crc16(read0,8)==0);
    assert(modbus_reply(read0,8,out,sizeof out)==7);
    assert(memcmp(out,"\x01\x04\x02\x03\x78",5)==0 && crc16(out,7)==0);
    for(size_t cap=0;cap<7;cap++) {
        memset(out,0xa5,sizeof out);
        assert(modbus_reply(read0,8,out,cap)==0);
        for(size_t i=0;i<sizeof out;i++) assert(out[i]==0xa5);
    }
    for(size_t n=0;n<8;n++) assert(modbus_reply(read0,n,out,sizeof out)==0);
    for(unsigned bit=0;bit<64;bit++) {
        memcpy(r,read0,8); r[bit/8]^=(uint8_t)(1u<<(bit%8));
        assert(modbus_reply(r,8,out,sizeof out)==0);
    }
    for(unsigned unit=0;unit<256;unit++) {
        memcpy(r,read0,8);r[0]=(uint8_t)unit;seal(r,8);
        assert(modbus_reply(r,8,out,sizeof out)==(unit==1?7u:0u));
    }
    memcpy(r,read0,8);r[1]=16;seal(r,8);
    assert(modbus_reply(r,8,out,sizeof out)==5 && out[1]==0x90 && out[2]==1);
    r[1]=6;seal(r,8);
    assert(modbus_reply(r,8,out,sizeof out)==5 && out[1]==0x86 && out[2]==1 && crc16(out,5)==0);
    memcpy(r,read0,8);r[2]=REGISTER_COUNT>>8;r[3]=REGISTER_COUNT&255;seal(r,8);
    assert(modbus_reply(r,8,out,sizeof out)==5 && out[2]==2);
    memcpy(r,read0,8);r[3]=0;r[5]=REGISTER_READ_MAX+1;seal(r,8);
    assert(modbus_reply(r,8,out,sizeof out)==5 && out[2]==2);
    r[5]=0;seal(r,8);assert(modbus_reply(r,8,out,sizeof out)==5 && out[2]==3);
    r[5]=126;seal(r,8);assert(modbus_reply(r,8,out,sizeof out)==5 && out[2]==3);
    /* P0070 block reads, small output capacity and overflow-safe range. */
    memcpy(r,read0,8);r[5]=REGISTER_READ_MAX;seal(r,8);
    assert(modbus_reply(r,8,out,sizeof out)==37 && out[2]==32 && crc16(out,37)==0);
    assert(out[3]==3 && out[4]==120 && out[5]==0 && out[6]==72);
    assert(out[7]==255 && out[8]==255 && out[9]==0 && out[10]==0);
    memset(out,0xa5,sizeof out);assert(modbus_reply(r,8,out,36)==0);
    for(size_t i=0;i<sizeof out;i++)assert(out[i]==0xa5);
    r[3]=REGISTER_COUNT-1;r[5]=1;seal(r,8);assert(modbus_reply(r,8,out,sizeof out)==7);
    r[5]=2;seal(r,8);assert(modbus_reply(r,8,out,sizeof out)==5 && out[2]==2);
    r[2]=255;r[3]=255;seal(r,8);assert(modbus_reply(r,8,out,sizeof out)==5 && out[2]==2);
    rtu_state s={0}; uint32_t last=feed(&s,read0,8,10000,0);
    assert(rtu_poll(&s,last+3999,out,sizeof out)==0);
    assert(rtu_poll(&s,last+4000,out,sizeof out)==7);
    assert(rtu_poll(&s,last+8000,out,sizeof out)==0);
    memset(&s,0,sizeof s);last=feed(&s,read0,8,UINT32_MAX-4000,0);
    assert(rtu_poll(&s,last+4000,out,sizeof out)==7);
    memset(&s,0,sizeof s);last=feed(&s,read0,8,10000,1);
    assert(rtu_poll(&s,last+4000,out,sizeof out)==0);
    last=feed(&s,read0,8,last+8000,0);assert(rtu_poll(&s,last+4000,out,sizeof out)==7);
    memset(&s,0,sizeof s);last=feed(&s,read0,4,10000,0);
    last=feed(&s,read0+4,4,last+2000,0);assert(rtu_poll(&s,last+4000,out,sizeof out)==0);
    memset(&s,0,sizeof s);for(unsigned i=0;i<300;i++)rtu_feed(&s,1,10000+i*100,0);
    assert(s.length==256 && s.invalid);assert(rtu_poll(&s,50000,out,sizeof out)==0);
    last=feed(&s,read0,8,60000,0);assert(rtu_poll(&s,last+4000,out,sizeof out)==7);
    uint32_t rng=123456789;
    for(unsigned trial=0;trial<20000;trial++) {
        size_t n=trial%sizeof r;
        for(size_t i=0;i<n;i++){rng=rng*1664525u+1013904223u;r[i]=(uint8_t)(rng>>24);}
        size_t cap=trial%sizeof out;memset(out,0xa5,sizeof out);
        size_t count=modbus_reply(r,n,out,cap);assert(count<=cap);
        for(size_t i=cap;i<sizeof out;i++)assert(out[i]==0xa5);
    }
    puts("PASS host: CRC golden vector, 64 corruptions, 256 unit IDs, exceptions, capacities, RTU timing/overflow/error recovery/wrap, 20000 malformed packets (ASan/UBSan)");
}
