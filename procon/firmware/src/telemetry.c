/* P0072: fresh/valid is a protocol property, not hardware calibration. */
#include "telemetry.h"
#include "service.h"
#define AGE_MAX 65535000u
#define TTL 30000u
enum { NEVER, VALID, STALE, RANGE, UNAVAILABLE };
typedef struct { int32_t value; uint32_t age; uint16_t generation; uint8_t status; } sample;
static sample values[20];
static uint8_t raw[7][16];
static const uint8_t queries[]={4,0x0c,0x14,0x0b,9,0x15,0x26};
static uint16_t be(const uint8_t *p){return (uint16_t)(((uint16_t)p[0]<<8)|p[1]);}
static void put(unsigned i,int32_t v,int32_t min,int32_t max){
    sample *s=&values[i];s->value=v;s->age=0;++s->generation;
    s->status=v>=min && v<=max?VALID:RANGE;
}
void tele_init(void){
    for(unsigned i=0;i<20;++i){values[i]=(sample){0,AGE_MAX,0,NEVER};}
    values[10].status=values[11].status=UNAVAILABLE;
    for(unsigned i=0;i<7;++i)for(unsigned j=0;j<16;++j)raw[i][j]=0;
}
void tele_tick(uint32_t dt){
    for(unsigned i=0;i<20;++i){sample *s=&values[i];
        s->age=dt>=AGE_MAX-s->age?AGE_MAX:s->age+dt;
        if(s->status==VALID && s->age>=(i==8?10000u:TTL))s->status=STALE;
    }
}
void tele_invalidate(void){for(unsigned i=0;i<20;++i)if(values[i].status==VALID)values[i].status=STALE;}
void tele_accept(const uint8_t p[16]){
    unsigned q=0;while(q<7 && queries[q]!=p[0])++q;if(q==7)return;
    for(unsigned i=0;i<16;++i)raw[q][i]=p[i];
    switch(p[0]){
    case 4:put(8,p[1],0,255);break;
    case 0x0c:
        put(3,be(p+1),0,10000);put(4,be(p+4),0,10000);put(14,be(p+7),0,10000);break;
    case 0x14:
        put(6,(int32_t)p[12]*100,0,20000);
        put(19,p[2]|(p[3]<<1)|(p[4]<<2)|(p[5]<<3),0,15);
        if(p[2]>1 || p[3]>1 || p[4]>1 || p[5]>1)values[19].status=RANGE;
        break;
    case 0x0b:
        /* Reference uses integer Buffer[11]/2, retain its whole-degree precision. */
        put(15,((int32_t)(p[11]/2)-40)*100,-4000,8000);break;
    case 9:put(16,be(p+5),0,10000);break;
    case 0x15:{
        put(12,p[1],0,1);
        static const uint8_t codes[]={0x64,0x34,0x29,0x1f,0x14,0};
        unsigned i=0;while(i<6 && codes[i]!=p[2])++i;put(13,(int32_t)i,0,5);break;
    }
    case 0x26:put(17,be(p+8),0,10000);put(18,p[4],0,7);break;
    }
}
static sample brine(unsigned i){
    unsigned a=16+8*i;int32_t v=(int16_t)svc_read(a);
    sample s={v*100,(uint32_t)svc_read(a+3)*1000u,svc_read(a+5),NEVER};
    if(svc_read(a+6))s.status=svc_read(a+2)?VALID:STALE;
    if(s.status==VALID && (v < -40 || v > 80))s.status=RANGE;
    return s;
}
static sample combine(sample a,sample b,int power){
    sample s={0,a.age>b.age?a.age:b.age,(uint16_t)(a.generation+b.generation),VALID};
    if(a.status!=VALID || b.status!=VALID){
        s.status=(a.status==NEVER || b.status==NEVER)?NEVER:
                 (a.status==RANGE || b.status==RANGE)?RANGE:STALE;
        return s;
    }
    if(power){
        uint32_t skew=a.age>b.age?a.age-b.age:b.age-a.age;
        if(skew>2000u){s.status=STALE;return s;}
        /* a centilitres/min, b centidegrees; rho=1kg/L, cp=4180J/kg/K. */
        int64_t n=(int64_t)a.value*b.value*418;
        s.value=(int32_t)(n/60000); /* Signed W, truncation toward zero. */
    }else s.value=a.value-b.value;
    return s;
}
static sample get(unsigned i){
    if(i<2)return brine(i);
    if(i==2)return combine(brine(0),brine(1),0);
    if(i==5)return combine(values[3],values[4],0);
    if(i==7)return combine(values[6],combine(values[3],values[4],0),1);
    if(i==9){sample s=values[8];s.value=s.value>0;return s;}
    return values[i];
}
uint16_t tele_read(unsigned a){
    if(a>=200 && a<256){unsigned n=a-200;const uint8_t *p=raw[n/8]+2*(n%8);return (uint16_t)(p[0]|(p[1]<<8));}
    if(a<100 || a>=200)return 0;
    unsigned i=a<140?(a-100)/2:(a-140)%20;sample s=get(i);
    if(a<140){uint32_t v=s.status==VALID?(uint32_t)s.value:0x80000000u;return a%2?(uint16_t)v:(uint16_t)(v>>16);}
    if(a<160)return s.status;
    if(a<180)return (uint16_t)(s.age/1000u);
    return s.generation;
}
