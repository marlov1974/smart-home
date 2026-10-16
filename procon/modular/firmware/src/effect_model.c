/* P0080: identify offset locally; identify gain only across comparable plateaus. */
#include "effect_model.h"
#include "telemetry.h"
#include "service.h"
typedef struct { int32_t p,h,s,r,b,f; uint32_t at; uint8_t valid; } plateau;
static int32_t gain=1350,bias=-1090,candidate;
static uint16_t updates,slopes,pgen,hgen,ngen,seed_gain;
static uint8_t seen,agreements,seeded;
static uint32_t start,last,n;
static int32_t sums[6],lo[6],hi[6];
static plateau anchor;
static int32_t abs_i(int32_t x){return x<0?-x:x;}
static int32_t bound(int32_t x,int32_t lo,int32_t hi){return x<lo?lo:x>hi?hi:x;}
static void model_break(void){n=0;ngen=0;}
int32_t effect_model_op(unsigned op,int32_t arg){
    switch(op){
    case EFFECT_MODEL_RESET:
        gain=1350;bias=-1090;updates=slopes=seed_gain=0;seen=agreements=seeded=0;anchor.valid=0;
        /* fall through */
    case EFFECT_MODEL_BREAK:model_break();return 0;
    case EFFECT_MODEL_TARGET:return bound((arg-bias)*1000/gain,2000,10300);
    case EFFECT_MODEL_GAIN:return gain;
    case EFFECT_MODEL_BIAS:return bias;
    case EFFECT_MODEL_UPDATES:return updates;
    case EFFECT_MODEL_SLOPES:return slopes;
    case EFFECT_MODEL_SEED_GAIN:{
        uint16_t value=(uint16_t)arg;
        if(arg<700 || arg>2000)return -1;
        if(seeded)return value==seed_gain?gain:-1;
        gain=value;seed_gain=value;seeded=1;candidate=0;seen=agreements=0;anchor.valid=0;
        model_break();return gain;
    }
    case EFFECT_MODEL_SEEDED:return seeded;
    case EFFECT_MODEL_SEEDED_GAIN:return seed_gain;
    default:return 0;
    }
}
static void admit(plateau q){
    int32_t e=q.p-(gain*q.h/10+bias);
    bias=bound(bias+bound(e/10,-100,100),-5000,5000);++updates;
    int comparable=anchor.valid && q.at-anchor.at<7200000u &&
        abs_i(q.s-anchor.s)<=100 && abs_i(q.r-anchor.r)<=100 &&
        abs_i(q.b-anchor.b)<=100 && abs_i(q.f-anchor.f)<=100;
    if(!comparable){anchor=q;agreements=0;return;}
    if(abs_i(q.h-anchor.h)<15)return;
    int32_t a=(q.p-anchor.p)*10/(q.h-anchor.h);
    if(a>=700 && a<=2000){
        if(agreements && abs_i(a-candidate)<=200){
            int32_t next=bound(gain+(a-gain)/20,700,2000);
            bias=bound(bias+(gain-next)*q.h/10,-5000,5000);gain=next;++slopes;agreements=0;
        }else{candidate=a;agreements=1;}
    }else agreements=0;
    anchor=q;
}
void effect_model_tick(uint32_t t,int enabled){
    tele_sample v[7];
    if(!enabled){model_break();return;}
    const uint8_t ix[]={7,3,4,6,0,19,18};
    for(unsigned i=0;i<7;++i){
        if(!tele_snapshot(ix[i],&v[i]) || v[i].link_lost || v[i].age_ms>=60000u ||
           (v[i].status!=TELE_VALID && v[i].status!=TELE_STALE)){
            model_break();return;
        }
        /* CN105 updates temperatures and flow separately. The intermediate
           derived-power STALE/skew is not a new observation or a lost plateau.
           Skip it; a60s gap still starts a new window below. */
        if(v[i].status!=TELE_VALID || v[i].age_ms>=(i==4?60000u:15000u))return;
    }
    unsigned hz=svc_read(372),hg=svc_read(376);
    if(!svc_read(373) || !svc_read(377) || svc_read(374)>=60 || hz<20 || hz>120 ||
       v[5].value || (v[6].value!=2 && v[6].value!=7) || v[0].value<0 || v[0].value>20000){model_break();return;}
    if(v[1].generation!=v[2].generation || v[1].age_ms!=v[2].age_ms ||
       abs_i((int32_t)v[1].age_ms-(int32_t)v[3].age_ms)>2000)return;
    if(seen && pgen==v[0].generation)return;
    if(n && t-last<5000u)return; /* <=25 samples/window; bounded sums */
    pgen=v[0].generation;seen=1;
    if(n && t-last>=60000u)model_break();
    int32_t values[]={v[0].value,(int32_t)hz,v[1].value,v[2].value,v[4].value,v[3].value};
    static const uint16_t ranges[]={20000,2,50,50,100,100};
    if(!n){start=t;ngen=1;hgen=(uint16_t)hg;}
    else if(hgen!=hg){hgen=(uint16_t)hg;++ngen;}
    for(unsigned i=0;i<6;++i){
        int32_t v=values[i];
        if(!n){sums[i]=0;lo[i]=hi[i]=v;}
        if(v<lo[i])lo[i]=v;
        if(v>hi[i])hi[i]=v;
        if(hi[i]-lo[i]>ranges[i]){model_break();return;}
        sums[i]+=v;
    }
    last=t;++n;
    if(t-start>=120000u){
        if(n>=8 && ngen>=3){
            for(unsigned i=0;i<6;++i)values[i]=sums[i]/(int32_t)n;
            admit((plateau){values[0],values[1],values[2],values[3],values[4],values[5],t,1});
        }
        model_break();
    }
}
