/* P0072: reference-backed telemetry, no controls. */
#ifndef TELEMETRY_H
#define TELEMETRY_H
#include <stdint.h>
void tele_init(void);
void tele_tick(uint32_t delta_ms);
void tele_invalidate(void);
void tele_accept(const uint8_t payload[16]);
uint16_t tele_read(unsigned address);
#endif
