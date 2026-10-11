/* P0069: fixed, read-only M1 wire contract. */
#ifndef PROCON_MODBUS_H
#define PROCON_MODBUS_H
#include <stddef.h>
#include <stdint.h>
#define RTU_GAP_US 4000u
#define RTU_INTERCHAR_US 1600u
typedef struct {
    uint8_t bytes[256];
    size_t length;
    uint32_t last_us;
    uint8_t invalid;
} rtu_state;
uint16_t crc16(const uint8_t *data, size_t length);
size_t modbus_reply(const uint8_t *request, size_t length, uint8_t *out, size_t capacity);
void rtu_feed(rtu_state *state, uint8_t byte, uint32_t now_us, int error);
size_t rtu_poll(rtu_state *state, uint32_t now_us, uint8_t *out, size_t capacity);
#endif
