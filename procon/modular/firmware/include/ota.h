/* P0080 resident maintenance ABI. No hardware changes on import/validation. */
#ifndef OTA_H
#define OTA_H
#include <stdint.h>
#include <stddef.h>
uint32_t crc32(const void *,size_t);
int modules_valid(void);
void modules_load(void);
size_t ota_handle(const uint8_t *,size_t,uint8_t *,size_t);
void ota_reset(void);
int ota_exit_ready(void);
int flash_erase(unsigned);
int flash_write(uint32_t,const uint8_t *,unsigned);
const uint8_t *flash_at(uint32_t);
int maintenance_ready(void);
void uart_baud(unsigned);
uint32_t ota_state(void);
uint8_t debug_command(const uint16_t [8]);
uint16_t feedback_read(unsigned);
#endif
