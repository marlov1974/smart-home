/* P0072 r2: supervised, bounded control candidate. */
#ifndef CONTROL_H
#define CONTROL_H
#include <stdint.h>
#include "effect.h"
void ctl_feedback(const effect_measurement *sample);
void ctl_link_lost(uint32_t now);
void ctl_init(void);
void ctl_observe(const uint8_t payload[16], uint32_t now);
uint8_t ctl_submit(const uint16_t words[8], uint32_t now);
void ctl_tick(uint32_t now);
int ctl_busy(void);
int ctl_next(uint8_t *type, uint8_t payload[16], uint32_t now);
int ctl_reply(uint8_t type, const uint8_t *payload, unsigned length, uint32_t now);
void ctl_timeout(uint32_t now);
uint16_t ctl_read(unsigned address);
#endif
