/* P0071: read-only CN105 telemetry. */
#ifndef CN105_H
#define CN105_H
#include <stdint.h>
#include <stddef.h>
#define REGISTER_COUNT 69u
#define REGISTER_READ_MAX 16u
void cn_init(void);
void cn_feed(uint8_t byte, uint32_t now_ms, int error);
void cn_tick(uint32_t now_ms);
int cn_tx_byte(uint8_t *byte);
void cn_tx_sent(void);
uint16_t cn_read(unsigned address);
void cn_service(void);
#endif
