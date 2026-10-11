/* P0076: persistent hardware DIP selection; no NVM or option-byte writes. */
#include "identity.h"
#include <stddef.h>

static uint32_t device_uid[3];
static uint8_t effective_address, configured_address, dip_raw, dip_stable, dip_reason;
static uint8_t uid_valid;

static uint8_t rejection_reason(uint8_t raw, int stable) {
    if (stable != 1) return IDENTITY_DIP_UNSTABLE;
    if ((raw & 31u) == 0) return IDENTITY_DIP_ADDRESS_ZERO;
    if ((raw & 31u) == 31u) return IDENTITY_DIP_SOFTWARE_ADDRESS;
    if ((raw & 0x60u) != 0x60u) return IDENTITY_DIP_UNSUPPORTED_MODE;
    return IDENTITY_DIP_VALID;
}

uint8_t identity_validate_dip(uint8_t raw, int stable) {
    return rejection_reason(raw, stable) == IDENTITY_DIP_VALID ? raw & 31u : 0;
}

void identity_init_dip(const uint32_t uid[3], uint8_t raw, int stable) {
    dip_raw = raw;
    dip_stable = stable == 1;
    dip_reason = rejection_reason(raw, stable);
    configured_address = raw & 31u;
    effective_address = identity_validate_dip(raw, stable);
    for (unsigned i = 0; i < 3; ++i) device_uid[i] = uid != NULL ? uid[i] : 0;
    uid_valid = (device_uid[0] | device_uid[1] | device_uid[2]) != 0 &&
        (device_uid[0] & device_uid[1] & device_uid[2]) != UINT32_MAX;
}

uint8_t modbus_address(void) { return effective_address; }

uint16_t identity_read(unsigned address) {
    switch (address) {
    case 72: return IDENTITY_SCHEMA;
    case 73: return effective_address;
    case 74: return configured_address;
    case 75: return IDENTITY_SOURCE_DIP;
    case 76: return effective_address != 0;
    case 77: return uid_valid;
    case 84: return dip_raw;
    case 85: return dip_stable;
    case 86: return dip_reason;
    default:
        if (address >= 78 && address <= 83) {
            const uint32_t word = device_uid[(address - 78) / 2];
            return (uint16_t)((address & 1u) ? word : word >> 16);
        }
        return 0;
    }
}
