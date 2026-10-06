/* P0069 M1: no CN105, no control writes, no persistent configuration. */
#include "modbus.h"
#include "platform.h"
static rtu_state receiver;
int main(void) {
    platform_init();
    uart_init();
    for (;;) {
        uint8_t response[7], byte;
        int error;
        watchdog_refresh();
        size_t n = rtu_poll(&receiver, micros(), response, sizeof(response));
        if (n) (void)uart_send(response, n);
        if (uart_receive(&byte, &error)) rtu_feed(&receiver, byte, micros(), error);
    }
}
