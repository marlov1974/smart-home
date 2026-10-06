/* P0069: inferred STM32L433 board; see docs/HARDWARE.md. */
#ifndef PROCON_PLATFORM_H
#define PROCON_PLATFORM_H
#include <stddef.h>
#include <stdint.h>
void platform_init(void);
void uart_init(void);
int uart_receive(uint8_t *byte, int *error);
int uart_send(const uint8_t *bytes, size_t n);
uint32_t micros(void);
void watchdog_refresh(void);
void heartbeat(uint32_t now);
#endif
