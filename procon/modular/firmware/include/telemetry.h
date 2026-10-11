/* P0072: reference-backed telemetry, no controls. */
#ifndef TELEMETRY_H
#define TELEMETRY_H
#include <stdint.h>
/* P0076: internal typed snapshot; legacy Modbus value/status encoding is unchanged. */
enum tele_status { TELE_NEVER=0, TELE_VALID=1, TELE_STALE=2, TELE_RANGE=3, TELE_UNAVAILABLE=4 };
typedef struct {
    int32_t value;
    uint32_t age_ms;
    uint16_t generation;
    uint8_t status,link_lost;
} tele_sample;
int tele_snapshot(unsigned index,tele_sample *out);
void tele_init(void);
void tele_tick(uint32_t delta_ms);
void tele_invalidate(void);
void tele_accept(const uint8_t payload[16]);
uint16_t tele_read(unsigned address);
#endif
