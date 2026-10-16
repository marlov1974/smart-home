#include "effect_source_fixture.h"
static tele_sample hz,water,a3_actual,a3_target;
static uint8_t separate_a3;
void effect_test_sources(const effect_measurement *m,uint32_t t){
    hz=(tele_sample){m->hz,m->age_ms,(uint16_t)(t/5000u+1),TELE_VALID,0};
    water=(tele_sample){m->supply_cC,m->age_ms,(uint16_t)(t/5000u+1),TELE_VALID,0};
    if(!separate_a3)a3_actual=a3_target=hz;
}
void effect_test_source(unsigned i,tele_sample s){
    if(i==8){hz=s;if(!separate_a3)a3_actual=a3_target=s;}
    else if(i==3)water=s;
}
void effect_test_a3(unsigned actual,unsigned target,unsigned actual_generation,unsigned target_generation){
    separate_a3=1;
    a3_actual=(tele_sample){(int32_t)actual,0,(uint16_t)actual_generation,TELE_VALID,0};
    a3_target=(tele_sample){(int32_t)target,0,(uint16_t)target_generation,TELE_VALID,0};
}
void effect_test_a3_mirror(void){separate_a3=0;}
int tele_snapshot(unsigned i,tele_sample *out){
    if(i==8)*out=hz;else if(i==3)*out=water;else return 0;return 1;
}

uint16_t svc_read(unsigned a){
 if(a>=372 && a<384){tele_sample *s=a<378?&a3_actual:&a3_target;switch((a-372)%6){
 case 0:return (uint16_t)s->value;case 1:return s->status==TELE_VALID;
 case 2:return (uint16_t)(s->age_ms/1000u);case 3:return 2;case 4:return s->generation;default:return 1;}}return 0;
}
