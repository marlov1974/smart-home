/* P0069: clean implementation, no dependency on original application code. */
#include "modbus.h"
#include "cn105.h"
static uint16_t request_count;

uint16_t crc16(const uint8_t *data, size_t length) {
    uint16_t crc = 0xffffu;
    for (size_t i = 0; i < length; ++i) {
        crc ^= data[i];
        for (unsigned bit = 0; bit < 8; ++bit)
            crc = (uint16_t)((crc >> 1) ^ ((crc & 1u) ? 0xa001u : 0u));
    }
    return crc;
}

size_t modbus_reply(const uint8_t *r, size_t n, uint8_t *out, size_t capacity) {
    if (n < 4 || n > 256 || r[0] != 1 || crc16(r, n) != 0) return 0;
    ++request_count;
    uint8_t exception = 0;
    unsigned address=0, quantity=0;
    if (r[1] == 16 && n >= 9) {
        /* One atomic envelope only; no staging registers or raw packet tunnel. */
        if (r[2]!=1 || r[3]!=44 || r[4]!=0 || r[5]!=8) exception=2;
        else if (r[6]!=16 || n!=25) exception=3;
        else {
            if(capacity<8)return 0; /* never mutate if acceptance cannot be returned */
            uint16_t words[8];
            for(unsigned i=0;i<8;++i)words[i]=(uint16_t)((r[7+2*i]<<8)|r[8+2*i]);
            exception=cn_command(words);
            if(!exception){
                for(unsigned i=0;i<6;++i)out[i]=r[i];
                uint16_t c=crc16(out,6);out[6]=(uint8_t)c;out[7]=(uint8_t)(c>>8);return 8;
            }
        }
    }
    else if (r[1] != 4) exception = 1;
    else {
        if (n != 8) return 0;
        address = ((unsigned)r[2] << 8) | r[3];
        quantity = ((unsigned)r[4] << 8) | r[5];
        if (quantity == 0 || quantity > 125) exception = 3;
        else if (address >= REGISTER_COUNT || quantity > REGISTER_READ_MAX || quantity > REGISTER_COUNT-address) exception = 2;
    }
    size_t payload = exception ? 3u : 3u+quantity*2u;
    if (capacity < payload + 2) return 0;
    out[0] = 1;
    out[1] = exception ? (uint8_t)(r[1] | 0x80u) : 4;
    out[2] = exception ? exception : (uint8_t)(quantity*2u);
    if (!exception) {
        for(unsigned i=0;i<quantity;++i) {
            unsigned a=address+i;
            uint16_t value=a==10?request_count:cn_read(a);
            out[3+i*2]=(uint8_t)(value>>8);out[4+i*2]=(uint8_t)value;
        }
    }
    uint16_t crc = crc16(out, payload);
    out[payload] = (uint8_t)crc;
    out[payload + 1] = (uint8_t)(crc >> 8);
    return payload + 2;
}

void rtu_feed(rtu_state *s, uint8_t byte, uint32_t now, int error) {
    /* Caller polls before feeding a new byte; incomplete old frames never merge. */
    uint32_t gap = now - s->last_us;
    if (gap >= RTU_GAP_US) { s->length = 0; s->invalid = 0; }
    else if (s->length && gap > RTU_INTERCHAR_US) s->invalid = 1;
    if (error) s->invalid = 1;
    if (s->length < sizeof(s->bytes)) s->bytes[s->length++] = byte;
    else s->invalid = 1;
    s->last_us = now;
}

size_t rtu_poll(rtu_state *s, uint32_t now, uint8_t *out, size_t capacity) {
    if ((!s->length && !s->invalid) || now - s->last_us < RTU_GAP_US) return 0;
    size_t n = s->invalid ? 0 : modbus_reply(s->bytes, s->length, out, capacity);
    s->length = 0;
    s->invalid = 0;
    return n;
}
