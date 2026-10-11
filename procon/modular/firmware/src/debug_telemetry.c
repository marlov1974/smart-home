/* P0080 extracted P76 feedback diagnostics. */
#include "effect_feedback.h"
uint16_t feedback_read(unsigned a) {
    const effect_feedback_state *f=effect_feedback_get();
    uint32_t value=0;
    switch(a) {
    case 352:return 1;case 353:return f->quality;case 354:return f->ready;
    case 355:return f->short_count;case 356:return f->slow_count;
    case 357:return (uint16_t)(f->short_span_ms/1000u);
    case 358:return (uint16_t)(f->slow_span_ms/1000u);
    case 359:return f->last_age_ms>=65535000u?65535u:(uint16_t)(f->last_age_ms/1000u);
    case 360:return f->temp_gen;case 361:return f->flow_gen;
    case 362:case 363:value=f->accepted_count;break;
    case 364:case 365:value=(uint32_t)f->instant_w;break;
    case 366:case 367:value=(uint32_t)f->short_w;break;
    case 368:case 369:value=(uint32_t)f->slow_w;break;
    case 370:case 371:value=(uint32_t)f->derivative_w_per_min;break;
    default:return 0;
    }
    return (a&1u)?(uint16_t)value:(uint16_t)(value>>16);
}
