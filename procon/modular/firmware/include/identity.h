/* P0076: boot-latched DIP address and read-only MCU identity. */
#ifndef PROCON_IDENTITY_H
#define PROCON_IDENTITY_H
#include <stdint.h>

#define IDENTITY_FIRST 72u
#define IDENTITY_LAST 86u
#define IDENTITY_SCHEMA 1u
#define IDENTITY_SOURCE_DIP 3u
#define IDENTITY_DIP_VALID 0u
#define IDENTITY_DIP_UNSTABLE 1u
#define IDENTITY_DIP_ADDRESS_ZERO 2u
#define IDENTITY_DIP_SOFTWARE_ADDRESS 3u
#define IDENTITY_DIP_UNSUPPORTED_MODE 4u

/* Pure validation: zero disables Modbus; it never selects broadcast handling. */
uint8_t identity_validate_dip(uint8_t raw, int stable);
/* Called once at boot, before either UART is enabled. No runtime setter exists. */
void identity_init_dip(const uint32_t uid[3], uint8_t raw, int stable);
uint8_t modbus_address(void);
uint16_t identity_read(unsigned address);
#endif
