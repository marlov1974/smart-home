/* P0080 generalized from hardware-verified MVP3 flash-r3 RAM writer.
 * BL2/original loader and all option registers are excluded. */
#include "ota.h"
#include "layout.h"
#define R(a) (*(volatile uint32_t *)(uintptr_t)(a))
#define F 0x40022000u
#define SR R(F+16)
#define CR R(F+20)
#define ACR R(F)
#define RAM __attribute__((section(".ramfunc"),noinline))
const uint8_t *flash_at(uint32_t a){return (const uint8_t *)(uintptr_t)a;}
static int gate(uint32_t a,unsigned n){
 if(a<UPDATE_BASE||a>=UPDATE_END||n>UPDATE_END-a||!n)return 0;
 if((R(0xe0042000)&4095u)!=0x435u||*(volatile uint16_t *)0x1fff75e0u!=128)return 0;
 unsigned rdp=R(F+32)&255u;if(rdp!=0xaa&&rdp!=0xbb)return 0;
 if((R(0xe000edf0)&1u)||R(0xe000ed08)!=0x08008000u)return 0;
 unsigned first=(a-0x08000000u)/2048,last=(a+n-1-0x08000000u)/2048;
 for(unsigned o=44;o<=48;o+=4){unsigned v=R(F+o),s=v&127,e=(v>>16)&127;if(s<=e&&first<=e&&last>=s)return 0;}
 unsigned s=(R(F+36)&32767u)*8u,e=(R(F+40)&32767u)*8u+7u;
 if(s<=e&&a-0x08000000u<=e&&a+n-1-0x08000000u>=s)return 0;
 return !(SR&(1u<<16))&&!(CR&0x40007u);
}
static RAM void wait_done(void){
 uint32_t t=R(0x40000024);
 while(SR&(1u<<16)){
  R(0x40003000)=0xaaaa;
  if(R(0x40000024)-t>2000000u){R(0xe000ed0c)=0x05fa0004;__asm volatile("dsb\nisb":::"memory");for(;;)__asm volatile("nop");}
 }
}
static RAM int operation(uint32_t a,const uint8_t *p,unsigned n,int erase){
 uint32_t old,acr=ACR;int ok=0;
 __asm volatile("mrs %0,primask\ncpsid i":"=r"(old)::"memory");
 ACR=acr&~0x600u;__asm volatile("dsb\nisb":::"memory");
 if(CR&0x80000000u){R(F+8)=0x45670123;R(F+8)=0xcdef89ab;}
 if(CR&0x80000000u)goto done;
 SR=0xc3fb;
 if(erase){CR=(CR&~0x3fbu)|2u|(((a-0x08000000u)/2048)<<3);CR|=1u<<16;wait_done();CR&=~0x3fau;if(SR&0xc3fau)goto done;}
 else {
  for(unsigned i=0;i<n;i+=8){
   uint32_t lo=0,hi=0;for(unsigned j=0;j<4;++j){lo|=(uint32_t)p[i+j]<<(8*j);hi|=(uint32_t)p[i+4+j]<<(8*j);}
   SR=0xc3fb;CR|=1;R(a+i)=lo;__asm volatile("isb":::"memory");R(a+i+4)=hi;wait_done();CR&=~1u;
   if(SR&0xc3fau)goto done;
   R(0x40003000)=0xaaaa;
  }
 }
 ok=1;
done:
 CR|=0x80000000u;ACR=(acr&~0x600u)|0x1800u;ACR=acr&~0x600u;ACR=acr;
 __asm volatile("dsb\nisb\nmsr primask,%0"::"r"(old):"memory");return ok;
}
int flash_erase(unsigned a){if((a&2047u)||!gate(a,2048))return 0;return operation(a,0,0,1);}
int flash_write(uint32_t a,const uint8_t *p,unsigned n){
 if((a&7u)||(n&7u)||n>240||!gate(a,n))return 0;
 if(!operation(a,p,n,0))return 0;
 for(unsigned i=0;i<n;++i)if(flash_at(a)[i]!=p[i])return 0;
 return 1;
}
