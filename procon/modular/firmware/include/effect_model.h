/* P0080: RAM-only local thermal-power model, watt units. */
#ifndef EFFECT_MODEL_H
#define EFFECT_MODEL_H
#include <stdint.h>
/* Private Mode->Service ABI. These two veneers deliberately follow Service's
 * ten public exports without changing its public export count or layout ID. */
enum { EFFECT_MODEL_RESET, EFFECT_MODEL_BREAK, EFFECT_MODEL_TARGET,
       EFFECT_MODEL_GAIN, EFFECT_MODEL_BIAS, EFFECT_MODEL_UPDATES,
       EFFECT_MODEL_SLOPES, EFFECT_MODEL_SEED_GAIN,
       EFFECT_MODEL_SEEDED, EFFECT_MODEL_SEEDED_GAIN };
int32_t effect_model_op(unsigned operation,int32_t argument);
void effect_model_tick(uint32_t now,int enabled);
static inline void effect_model_reset(void){(void)effect_model_op(EFFECT_MODEL_RESET,0);}
static inline void effect_model_break(void){(void)effect_model_op(EFFECT_MODEL_BREAK,0);}
static inline int32_t effect_model_target(int32_t watts){return effect_model_op(EFFECT_MODEL_TARGET,watts);} /* Hz *100 */
static inline int32_t effect_model_gain(void){return effect_model_op(EFFECT_MODEL_GAIN,0);} /* W/Hz *10 */
static inline int32_t effect_model_bias(void){return effect_model_op(EFFECT_MODEL_BIAS,0);} /* W */
static inline uint16_t effect_model_updates(unsigned slope){return (uint16_t)effect_model_op(slope?EFFECT_MODEL_SLOPES:EFFECT_MODEL_UPDATES,0);}
/* Seed is deliberately RAM-only and can be accepted only once per boot. It
 * never imports bias or actuator trim. */
static inline int effect_model_seed_gain(uint16_t value){return effect_model_op(EFFECT_MODEL_SEED_GAIN,value)>=0;}
static inline int effect_model_seeded(void){return effect_model_op(EFFECT_MODEL_SEEDED,0)!=0;}
static inline uint16_t effect_model_seeded_gain(void){return (uint16_t)effect_model_op(EFFECT_MODEL_SEEDED_GAIN,0);}
#endif
