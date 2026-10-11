/* P0076-B: native address/identity tests. No hardware or control implementation. */
#include "identity.h"
#include "modbus.h"
#include "cn105.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>

static unsigned expected_address;
#define EXPECT_ADDRESS expected_address
#define EXPECT_SOURCE IDENTITY_SOURCE_DIP

static unsigned command_calls, read_calls;
static uint8_t command_result;
static uint16_t last_command[8];
static const uint32_t uid_a[3] = {0x01234567u, 0x89abcdefu, 0x13579bdfu};
static const uint32_t uid_b[3] = {0x10203040u, 0x50607080u, 0x90a0b0c0u};

/* The mock proves identity/broadcast routing cannot enter the control boundary. */
uint8_t cn_command(const uint16_t words[8]) {
    ++command_calls;
    memcpy(last_command, words, sizeof last_command);
    return command_result;
}
uint16_t cn_read(unsigned address) {
    ++read_calls;
    assert(address < IDENTITY_FIRST || address > IDENTITY_LAST);
    return address == 0 ? 888 : address == 1 ? 76 : 0;
}

static void seal(uint8_t *request, size_t length) {
    const uint16_t c = crc16(request, length - 2);
    request[length - 2] = (uint8_t)c; request[length - 1] = (uint8_t)(c >> 8);
}
static void read_frame(uint8_t request[8], unsigned slave, unsigned address, unsigned count) {
    request[0] = (uint8_t)slave; request[1] = 4;
    request[2] = (uint8_t)(address >> 8); request[3] = (uint8_t)address;
    request[4] = (uint8_t)(count >> 8); request[5] = (uint8_t)count; seal(request, 8);
}
static void command_frame(uint8_t request[25], unsigned slave) {
    const uint16_t words[8] = {0xc072, 1, 2, 3800, 0, 30, 1, 2};
    memset(request, 0, 25); request[0] = (uint8_t)slave; request[1] = 16;
    request[2] = 1; request[3] = 44; request[5] = 8; request[6] = 16;
    for (unsigned i = 0; i < 8; ++i) {
        request[7 + i * 2] = (uint8_t)(words[i] >> 8); request[8 + i * 2] = (uint8_t)words[i];
    }
    seal(request, 25);
}
static uint16_t response_word(const uint8_t *response, unsigned index) {
    return (uint16_t)((response[3 + index * 2] << 8) | response[4 + index * 2]);
}
static void test_dip(void) {
    unsigned accepted = 0;
    for (unsigned raw = 0; raw < 256; ++raw) {
        unsigned address = raw & 31u;
        int valid = address >= 1 && address <= 30 && (raw & 0x60u) == 0x60u;
        assert(identity_validate_dip((uint8_t)raw, 1) == (valid ? address : 0));
        assert(identity_validate_dip((uint8_t)raw, 0) == 0);
        assert(identity_validate_dip((uint8_t)raw, -1) == 0);
        assert(identity_validate_dip((uint8_t)raw, 2) == 0);
        identity_init_dip(uid_a, (uint8_t)raw, 1);
        assert(identity_read(74) == address && identity_read(84) == raw);
        assert(identity_read(85) == 1 && identity_read(76) == valid);
        const unsigned reason = address == 0 ? IDENTITY_DIP_ADDRESS_ZERO :
            address == 31 ? IDENTITY_DIP_SOFTWARE_ADDRESS :
            (raw & 0x60u) != 0x60u ? IDENTITY_DIP_UNSUPPORTED_MODE : IDENTITY_DIP_VALID;
        assert(identity_read(86) == reason);
        identity_init_dip(uid_a, (uint8_t)raw, 0);
        assert(modbus_address() == 0 && identity_read(85) == 0 &&
               identity_read(86) == IDENTITY_DIP_UNSTABLE);
        accepted += valid;
    }
    assert(accepted == 60); /* 30 addresses, either SW8 position. */
}
static void boot(const uint32_t uid[3]) {
    identity_init_dip(uid, (uint8_t)(0x60u | expected_address), 1);
}
static void test_identity(void) {
    boot(uid_a);
    assert(modbus_address() == EXPECT_ADDRESS);
    assert(identity_read(72) == 1 && identity_read(73) == EXPECT_ADDRESS);
    assert(identity_read(74) == EXPECT_ADDRESS && identity_read(75) == EXPECT_SOURCE);
    assert(identity_read(76) == 1 && identity_read(77) == 1);
    const uint16_t expected[6] = {0x0123, 0x4567, 0x89ab, 0xcdef, 0x1357, 0x9bdf};
    for (unsigned i = 0; i < 6; ++i) assert(identity_read(78 + i) == expected[i]);
    assert(identity_read(71) == 0 && identity_read(87) == 0);
    uint32_t sentinel[3] = {0, 0, 0};
    boot(sentinel); assert(identity_read(77) == 0 && modbus_address() == EXPECT_ADDRESS);
    sentinel[0] = sentinel[1] = sentinel[2] = UINT32_MAX;
    boot(sentinel); assert(identity_read(77) == 0);
    sentinel[2] = 0; boot(sentinel); assert(identity_read(77) == 1);
    boot(NULL); assert(identity_read(77) == 0);
    boot(uid_a);
}
static void test_golden(void) {
    uint8_t request[25];
    const uint8_t read1[8] = {1,4,0,0,0,1,0x31,0xca};
    const uint8_t read2[8] = {2,4,0,0,0,1,0x31,0xf9};
    read_frame(request, 1, 0, 1); assert(memcmp(request, read1, 8) == 0);
    read_frame(request, 2, 0, 1); assert(memcmp(request, read2, 8) == 0);
    const uint8_t uid_read2[8] = {2,4,0,72,0,12,0x70,0x2a};
    read_frame(request, 2, 72, 12); assert(memcmp(request, uid_read2, 8) == 0);
    const uint8_t write2[25] = {2,16,1,44,0,8,16,0xc0,0x72,0,1,0,2,0x0e,0xd8,
        0,0,0,30,0,1,0,2,0x82,0xec};
    command_frame(request, 2); assert(memcmp(request, write2, 25) == 0);
}
static void test_routing(void) {
    uint8_t request[25], out[64];
    for (unsigned slave = 0; slave < 256; ++slave) {
        read_frame(request, slave, 0, 1);
        memset(out, 0xa5, sizeof out);
        const size_t count = modbus_reply(request, 8, out, sizeof out);
        assert(count == (slave == EXPECT_ADDRESS ? 7u : 0u));
        if (count) assert(out[0] == slave && response_word(out, 0) == 888 && crc16(out, count) == 0);
        else for (unsigned i = 0; i < sizeof out; ++i) assert(out[i] == 0xa5);
    }
    const unsigned before = read_calls;
    read_frame(request, EXPECT_ADDRESS, 72, 15);
    assert(modbus_reply(request, 8, out, sizeof out) == 35);
    assert(out[0] == EXPECT_ADDRESS && out[2] == 30 && crc16(out, 35) == 0);
    assert(read_calls == before); /* identity is not delegated to CN105 */
    for (unsigned i = 0; i < 15; ++i) assert(response_word(out, i) == identity_read(72 + i));
    for (unsigned bit = 0; bit < 64; ++bit) {
        uint8_t bad[8]; memcpy(bad, request, 8); bad[bit / 8] ^= (uint8_t)(1u << (bit % 8));
        assert(modbus_reply(bad, 8, out, sizeof out) == 0);
    }
    read_frame(request, EXPECT_ADDRESS, 10, 1);
    assert(modbus_reply(request, 8, out, sizeof out) == 7);
    const uint16_t count_before = response_word(out, 0);
    for (unsigned slave = 0; slave < 256; ++slave) if (slave != EXPECT_ADDRESS) {
        request[0] = (uint8_t)slave; seal(request, 8);
        assert(modbus_reply(request, 8, out, sizeof out) == 0);
    }
    request[0] = EXPECT_ADDRESS; seal(request, 8);
    assert(modbus_reply(request, 8, out, sizeof out) == 7);
    assert(response_word(out, 0) == (uint16_t)(count_before + 1));
    read_frame(request, EXPECT_ADDRESS, REGISTER_COUNT, 1);
    assert(modbus_reply(request, 8, out, sizeof out) == 5);
    assert(out[0] == EXPECT_ADDRESS && out[1] == 0x84 && out[2] == 2 && crc16(out, 5) == 0);
    request[1] = 6; seal(request, 8);
    assert(modbus_reply(request, 8, out, sizeof out) == 5 && out[0] == EXPECT_ADDRESS && out[2] == 1);
}
static void test_command_boundary(void) {
    uint8_t request[25], out[64];
    unsigned expected_calls = command_calls;
    for (unsigned slave = 0; slave < 256; ++slave) {
        command_frame(request, slave);
        const size_t count = modbus_reply(request, sizeof request, out, sizeof out);
        assert(count == (slave == EXPECT_ADDRESS ? 8u : 0u));
        if (slave == EXPECT_ADDRESS) {
            ++expected_calls; assert(memcmp(out, request, 6) == 0 && crc16(out, 8) == 0);
            assert(last_command[0] == 0xc072 && last_command[1] == 1 && last_command[3] == 3800);
        }
        assert(command_calls == expected_calls);
    }
    command_frame(request, EXPECT_ADDRESS);
    assert(modbus_reply(request, 25, out, 7) == 0 && command_calls == expected_calls);
    request[24] ^= 1;
    assert(modbus_reply(request, 25, out, sizeof out) == 0 && command_calls == expected_calls);
    request[24] ^= 1; command_result = 3;
    assert(modbus_reply(request, 25, out, sizeof out) == 5 && command_calls == expected_calls + 1);
    assert(out[0] == EXPECT_ADDRESS && out[1] == 0x90 && out[2] == 3 && crc16(out, 5) == 0);
    command_result = 0;
}
static void test_restart_and_invalid(void) {
    uint8_t request[25], out[64];
    identity_init_dip(uid_b, 0x62, 1);
    assert(modbus_address() == 2 && identity_read(78) == 0x1020 && identity_read(79) == 0x3040);
    /* SW8 has no addressing effect; selection is latched, not a live pointer. */
    uint8_t raw = 0xe2;
    identity_init_dip(uid_b, raw, 1); raw = 0x61;
    assert(modbus_address() == 2 && identity_read(84) == 0xe2 && raw == 0x61);
    const uint8_t invalid[] = {0, 0x60, 0x7f, 0xff, 1, 0x21, 0x41};
    const unsigned before = command_calls;
    for (unsigned i = 0; i < sizeof invalid + 1; ++i) {
        identity_init_dip(uid_b, i < sizeof invalid ? invalid[i] : 0x62, i < sizeof invalid);
        assert(modbus_address() == 0 && identity_read(76) == 0);
        for (unsigned slave = 0; slave < 256; ++slave) {
            read_frame(request, slave, 0, 1); assert(modbus_reply(request, 8, out, sizeof out) == 0);
            command_frame(request, slave); assert(modbus_reply(request, 25, out, sizeof out) == 0);
        }
    }
    assert(command_calls == before);
    boot(uid_a);
    assert(modbus_address() == EXPECT_ADDRESS && identity_read(75) == EXPECT_SOURCE);
    assert(identity_read(76) == 1 && identity_read(78) == 0x0123 && identity_read(79) == 0x4567);
    assert(identity_read(84) == (0x60u | EXPECT_ADDRESS));
    assert(identity_read(85) == 1 && identity_read(86) == 0);
}

static void test_invalid_uid_control_gate(void) {
    uint8_t request[25], out[64];
    const uint32_t invalid_uid[2][3] = {{0, 0, 0}, {UINT32_MAX, UINT32_MAX, UINT32_MAX}};
    const unsigned before = command_calls;
    for (unsigned sentinel = 0; sentinel < 2; ++sentinel) {
        boot(invalid_uid[sentinel]);
        read_frame(request, EXPECT_ADDRESS, 72, 15);
        assert(modbus_reply(request, 8, out, sizeof out) == 35);
        assert(response_word(out, 1) == EXPECT_ADDRESS && response_word(out, 4) == 1);
        assert(response_word(out, 5) == 0 && crc16(out, 35) == 0);
        for (unsigned version = 2; version <= 3; ++version) {
            command_frame(request, EXPECT_ADDRESS);
            if (version == 3) {
                request[8] = 0x76; request[12] = 5; request[22] = 3;
                request[13] = 0x0b; request[14] = 0xb8; /* EFFECT 3000 W */
                request[15] = 0x0f; request[16] = 0xa0; /* max flow 40 C */
                seal(request, sizeof request);
            }
            assert(modbus_reply(request, sizeof request, out, sizeof out) == 5);
            assert(out[0] == EXPECT_ADDRESS && out[1] == 0x90 && out[2] == 4);
            assert(crc16(out, 5) == 0 && command_calls == before);
            assert(modbus_reply(request, sizeof request, out, 4) == 0);
            assert(command_calls == before);
        }
    }
    boot(uid_a); /* A valid factory identity restores both ordinary read and control paths. */
    command_frame(request, EXPECT_ADDRESS);
    assert(modbus_reply(request, sizeof request, out, sizeof out) == 8);
    assert(command_calls == before + 1);
    request[8] = 0x76; request[12] = 5; request[22] = 3;
    request[13] = 0x0b; request[14] = 0xb8;
    request[15] = 0x0f; request[16] = 0xa0; seal(request, sizeof request);
    assert(modbus_reply(request, sizeof request, out, sizeof out) == 8);
    assert(command_calls == before + 2 && last_command[0] == 0xc076 && last_command[1] == 1 && last_command[7] == 3);
}

int main(void) {
    assert(modbus_address() == 0); /* no listener before boot init */
    test_dip(); test_golden();
    const unsigned addresses[] = {1, 2, 30};
    for (unsigned i = 0; i < sizeof addresses / sizeof addresses[0]; ++i) {
        expected_address = addresses[i];
        test_identity(); test_routing(); test_command_boundary(); test_restart_and_invalid();
        test_invalid_uid_control_gate();
    }
    puts("PASS addressing: all 256 DIP bytes, stability/mode/reserved rejection, addresses 1/2/30, UID high/low, all request IDs, broadcast/CRC silence, FC04/FC16 gates and boot latch");
    return 0;
}

/* Snapshot dispatcher import is outside this identity-only fixture. */
uint16_t tele_read(unsigned a){(void)a;return 0;}
