/* P0080 existing supervised command adapter; no new raw packet bypass. */
#include "cn105.h"
#include <stdint.h>
uint8_t debug_command(const uint16_t words[8]) { return cn_command(words); }
