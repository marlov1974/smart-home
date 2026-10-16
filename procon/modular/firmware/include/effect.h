/* P0080 bounded demand-rate EFFECT regulator. No hardware I/O. */
#ifndef EFFECT_H
#define EFFECT_H
/* Actual-water regulation priority, independent of commanded flow ceiling.
 * Override exists for historical host fixtures, not as a live Modbus setting. */
#ifndef EFFECT_SUPPLY_LIMIT_CC
#define EFFECT_SUPPLY_LIMIT_CC 4500
#endif
#define EFFECT_THERMAL_APPROACH_CC (EFFECT_SUPPLY_LIMIT_CC-100)
#define EFFECT_THERMAL_RELEASE_CC (EFFECT_SUPPLY_LIMIT_CC-200)
#define EFFECT_THERMAL_RELEASE_FORECAST_CC (EFFECT_SUPPLY_LIMIT_CC-150)
#define EFFECT_NATIVE_RESTART_CC (EFFECT_SUPPLY_LIMIT_CC-50)
#include <stdint.h>
enum { EFFECT_OFF, EFFECT_START, EFFECT_CAPTURE, EFFECT_HOLD, EFFECT_LIMITED,
       EFFECT_INVALID_FEEDBACK, EFFECT_RESTORING, EFFECT_WAIT_NATIVE, EFFECT_SETTLING };
enum { EFFECT_OK, EFFECT_BAD_FEEDBACK, EFFECT_NATIVE_INHIBIT, EFFECT_MODE_CHANGED,
       EFFECT_TEMPERATURE_CAP, EFFECT_UNKNOWN_UNREACHABLE, EFFECT_CUMULATIVE_CAP,
       EFFECT_LINK_LOST, EFFECT_LEASE_EXPIRED, EFFECT_ABORTED, EFFECT_TEMPERATURE_FLOOR,
       EFFECT_READ_TIMEOUT, EFFECT_READBACK_MISMATCH, EFFECT_WAIT_TIMEOUT,
       EFFECT_RESPONSE_PENDING, EFFECT_REQUEST_CAP, EFFECT_MINIMUM_OUTPUT,
       EFFECT_SOURCE_STALE };
enum { EFFECT_FLAG_THERMAL=1, EFFECT_FLAG_OSCILLATION=2,
       EFFECT_FLAG_RAMP_UP=4, EFFECT_FLAG_RAMP_DOWN=8,
       EFFECT_FLAG_RESPONSE_WAIT=16, EFFECT_FLAG_MINIMUM_OUTPUT=32,
       EFFECT_FLAG_REQUEST_CAP=64, EFFECT_FLAG_TRACKING=128 };
typedef struct {
    int32_t instant_w,short_w,slow_w,supply_cC;
    uint32_t age_ms,span_ms;
    uint16_t quality,pairs,mode,hz;
    uint8_t ready;
} effect_measurement;
void effect_init(void);
void effect_begin(uint16_t target_w,uint16_t cap_cC,uint32_t now);
void effect_retarget(uint16_t target_w,uint16_t cap_cC,uint32_t now);
void effect_capture(uint16_t original_flow,uint32_t now);
/* Returns requested flow, or zero when no SET is required. */
uint16_t effect_decide(const effect_measurement *m,uint16_t flow,uint32_t now);
uint16_t effect_pause_demand(const effect_measurement *m,uint16_t flow,uint32_t now);
/* Module-private kind:0 none,1 zero-Hz demand,2 fresh-pair startup. */
int effect_pending_demand(void);
/* Initial combined mode/flow target;0 means defer. Private, not exported. */
uint16_t effect_entry_demand(const effect_measurement *m,uint16_t flow,unsigned native_mode,uint32_t now);
void effect_discard_pending(void);
void effect_wait(unsigned quality,uint32_t now);
void effect_verified(uint16_t flow,uint32_t now);
void effect_stop(unsigned reason,int restoring);
void effect_restored(void);
uint16_t effect_read(unsigned address,const effect_measurement *m,uint16_t flow,uint32_t now);
#endif
