/* Explicit synthetic source provenance for isolated regulator tests. */
#ifndef EFFECT_SOURCE_FIXTURE_H
#define EFFECT_SOURCE_FIXTURE_H
#include "effect.h"
#include "telemetry.h"
void effect_test_sources(const effect_measurement *m,uint32_t now);
void effect_test_source(unsigned index,tele_sample sample);
void effect_test_a3(unsigned actual,unsigned target,unsigned actual_generation,unsigned target_generation);
void effect_test_a3_mirror(void);
#ifdef EFFECT_AUTO_SOURCES
static uint16_t source_decide(const effect_measurement *m,uint16_t flow,uint32_t t){
    effect_test_sources(m,t);return effect_decide(m,flow,t);
}
#define effect_decide source_decide
#endif
#endif
