/* P0071: non-blocking, read-only Geodan service operations. */
#ifndef PROCON_SERVICE_H
#define PROCON_SERVICE_H
#include <stdint.h>
void svc_init(void);
void svc_start_cycle(void);
void svc_link(int up, uint32_t now);
void svc_tick(uint32_t delta, uint32_t now);
int svc_due(uint32_t now, uint8_t *code);
void svc_sent(uint32_t now);
int svc_reply(const uint8_t payload[16], uint32_t now, int owned);
void svc_timeout(uint32_t now);
void svc_bad_frame(void);
uint16_t svc_read(unsigned address);
#endif
