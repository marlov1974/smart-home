/* Diagnostic W/min. Whole-second resolution; no software 64-bit divider.
 * Inputs are bounded to +/-2MW and span>=1s. Remainder magnitude <2MW,
 * so its product by60 and the maximum result120MW fit signed32 bits. */
#ifndef EFFECT_MATH_H
#define EFFECT_MATH_H
#include <stdint.h>
static inline int32_t minute_rate(int32_t delta,uint32_t ms){
    int32_t seconds=(int32_t)(ms/1000u);
    return seconds?delta/seconds*60+(delta%seconds)*60/seconds:0;
}
#endif
