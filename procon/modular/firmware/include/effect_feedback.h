/* P0076: bounded, distinct-generation water-side heating feedback. */
#ifndef EFFECT_FEEDBACK_H
#define EFFECT_FEEDBACK_H
#include <stdint.h>
enum effect_feedback_quality {
    EF_READY=0, EF_WARMUP=1, EF_PENDING=2, EF_STALE=3,
    EF_INVALID=4, EF_ZEROFLOW=5, EF_DHW=6, EF_LINKLOSS=7,
    EF_WAIT_NATIVE=8, EF_SETTLING=9
};
typedef struct {
    int32_t instant_w,short_w,slow_w,derivative_w_per_min;
    uint32_t short_span_ms,slow_span_ms,last_age_ms,accepted_count;
    uint16_t short_count,slow_count,temp_gen,flow_gen;
    uint8_t quality,ready;
} effect_feedback_state;
void effect_feedback_init(void);
void effect_feedback_tick(uint32_t now);
const effect_feedback_state *effect_feedback_get(void);
int effect_feedback_hard_invalid(unsigned quality);
#endif
