/* P0080 stop-and-wait updater. No writes outside BL2-excluded fixed slots. */
#include "ota.h"
#include "platform.h"
#include "layout.h"
#include <stdint.h>
static uint8_t manifest[64],last_request[252],last_response[64];
static unsigned last_n,last_out,next_seq,active,mask,slot,offset,exit_ready;
static uint32_t get32(const uint8_t *p){return p[0]|((uint32_t)p[1]<<8)|((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);}
static void put32(uint8_t *p,uint32_t v){for(unsigned i=0;i<4;++i)p[i]=(uint8_t)(v>>(8*i));}
uint32_t crc32(const void *ptr,size_t n){const uint8_t *p=ptr;uint32_t c=~0u;while(n--){c^=*p++;for(unsigned i=0;i<8;++i)c=(c>>1)^((c&1)?0xedb88320u:0);}return ~c;}
static int meta(const uint8_t *m){return get32(m)==0x50384d46u && get32(m+4)==ABI_VERSION && get32(m+8)==LAYOUT_ID && get32(m+56)==crc32(m,56) && get32(m+60)==0x434f4d54u;}
static int header(unsigned i){
 const uint8_t *h=flash_at(slot_addr[i]);uint32_t dl=get32(h+24),ds=get32(h+28),dn=get32(h+32),bs=get32(h+36),bn=get32(h+40);
 if(get32(h)!=0x50384348u||get32(h+4)!=i+1||get32(h+8)!=ABI_VERSION||get32(h+12)!=LAYOUT_ID||get32(h+16)!=slot_addr[i]||get32(h+20)!=slot_size[i]||get32(h+44)!=slot_exports[i])return 0;
 if((dl|ds|dn|bs|bn)&3u)return 0;
 return dl>=slot_addr[i]+64 && dl<=slot_addr[i]+slot_size[i] && dn<=slot_addr[i]+slot_size[i]-dl && ds==slot_ram[i] && dn<=slot_ramsize[i] && bs==ds+dn && bn<=slot_ramsize[i]-dn;
}
static int matches(const uint8_t *m){if(!meta(m))return 0;for(unsigned i=0;i<7;++i){watchdog_refresh();if(!header(i)||crc32(flash_at(slot_addr[i]),slot_size[i])!=get32(m+16+4*i))return 0;}return 1;}
int modules_valid(void){return matches(flash_at(MANIFEST_ADDR));}
void modules_load(void){
 for(unsigned i=0;i<7;++i){const uint8_t *h=flash_at(slot_addr[i]);const uint8_t *src=flash_at(get32(h+24));uint8_t *d=(uint8_t *)(uintptr_t)get32(h+28);for(unsigned j=0;j<get32(h+32);++j)d[j]=src[j];d=(uint8_t *)(uintptr_t)get32(h+36);for(unsigned j=0;j<get32(h+40);++j)d[j]=0;}
}
void ota_reset(void){active=mask=slot=offset=last_n=last_out=exit_ready=0;next_seq=1;}
uint32_t ota_state(void){return active;}
int ota_exit_ready(void){return exit_ready;}
static unsigned advance(unsigned i){while(i<7 && !(mask&(1u<<i)))++i;return i;}
size_t ota_handle(const uint8_t *r,size_t n,uint8_t *out,size_t cap){
 if(n<12||n>252||cap<64||r[0]!='P'||r[1]!='8'||r[3]!=2)return 0;
 unsigned seq=r[4]|(r[5]<<8),len=r[6]|(r[7]<<8),cmd=r[2];
 if(len>240||n!=len+12||get32(r+n-4)!=crc32(r,n-4))return 0;
 if(last_n==n){unsigned same=1;for(unsigned i=0;i<n;++i)if(last_request[i]!=r[i])same=0;if(same){for(unsigned i=0;i<last_out;++i)out[i]=last_response[i];return last_out;}}
 uint8_t status=0;const uint8_t *p=r+8;
 if(cmd==1||cmd==5){if(len)status=1;}
 else if(seq!=next_seq||seq==0)status=2;
 else if(cmd==2){
  if(active||len!=84||!meta(p+20)||(get32(p)&~127u)||!get32(p))status=1;
  else {
   for(unsigned i=0;i<3;++i)if(get32(p+8+4*i)!=platform_uid_word(i))status=3;
   uint32_t current=modules_valid()?crc32(flash_at(MANIFEST_ADDR),56):0;
   if(get32(p+4)!=current)status=4;
   if(!status){
    mask=get32(p);for(unsigned i=0;i<64;++i)manifest[i]=p[20+i];
    /* Require every unselected slot to match the destination before invalidating. */
    for(unsigned i=0;i<7;++i)if(!(mask&(1u<<i))&&(!header(i)||crc32(flash_at(slot_addr[i]),slot_size[i])!=get32(manifest+16+4*i)))status=4;
    if(!status){active=2; /* fault-latched until reset if flash operation fails */
     if(!flash_erase(MANIFEST_ADDR))status=5;
     for(unsigned i=0;i<7&&!status;++i)if(mask&(1u<<i))for(unsigned a=slot_addr[i];a<slot_addr[i]+slot_size[i];a+=2048){if(!flash_erase(a)){status=5;break;}watchdog_refresh();}
     if(!status){active=1;slot=advance(0);offset=0;}
    }
   }
  }
 }else if(cmd==3){
  if(active!=1||slot>=7||len<16||len>240)status=1;
  else {unsigned i=get32(p),off=get32(p+4),count=len-8;
   if(i!=slot||off!=offset||(count&7u)||count>slot_size[slot]-offset)status=2;
   else if(!flash_write(slot_addr[slot]+offset,p+8,count)){active=2;status=5;}
   else {offset+=count;if(offset==slot_size[slot]){slot=advance(slot+1);offset=0;}}
  }
 }else if(cmd==4){
  if(active!=1||slot!=7||len)status=1;
  else if(!matches(manifest))status=6;
  else if(!flash_write(MANIFEST_ADDR,manifest,56)||!flash_write(MANIFEST_ADDR+56,manifest+56,8)){active=2;status=5;}
  else if(!modules_valid()){active=2;status=6;}else active=0;
 }else if(cmd==6){if(len||active||!modules_valid())status=1;else exit_ready=1;}
 else status=1;
 if(cmd!=1&&cmd!=5&&!status)++next_seq;
 out[0]='P';out[1]='8';out[2]=cmd|128;out[3]=2;out[4]=r[4];out[5]=r[5];out[6]=32;out[7]=0;
 put32(out+8,status);put32(out+12,active);put32(out+16,next_seq);put32(out+20,slot);put32(out+24,offset);
 for(unsigned i=0;i<3;++i)put32(out+28+4*i,platform_uid_word(i));
 put32(out+40,crc32(out,40));
 /* Only cache mutation replies; status must never hide a duplicate write ACK. */
 if(cmd!=1&&cmd!=5&&!status){for(unsigned i=0;i<n;++i)last_request[i]=r[i];last_n=n;for(unsigned i=0;i<44;++i)last_response[i]=out[i];last_out=44;}
 return 44;
}
