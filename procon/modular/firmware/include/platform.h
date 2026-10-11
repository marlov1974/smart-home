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
void cn_uart_init(void);
int cn_uart_receive(uint8_t *byte, int *error);
int cn_uart_ready(void);
void cn_uart_write(uint8_t byte);
/* STM32L433 96-bit factory UID; index outside 0..2 returns zero. */
uint32_t platform_uid_word(unsigned index);
/* Raw DIP levels in SW1..SW8 order, bit0..7; boot sampling is owned by main. */
uint8_t platform_dip_read(void);
#endif
