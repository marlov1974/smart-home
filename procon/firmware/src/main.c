/* P0071: read-only ATW CN105 and Modbus telemetry, no control writes. */
#include "modbus.h"
#include "platform.h"
#include "cn105.h"
static rtu_state receiver;
static uint32_t last_us, time_ms, remainder_us;
void cn_service(void) {
    uint32_t us=micros();
    uint32_t delta=us-last_us; last_us=us;
    time_ms+=delta/1000u;
    remainder_us+=delta%1000u;
    time_ms+=remainder_us/1000u; remainder_us%=1000u;
    cn_tick(time_ms);
    uint8_t byte; int error;
    for(unsigned i=0;i<8;++i) {
        if(!cn_uart_receive(&byte,&error)) break;
        cn_feed(byte,time_ms,error);
    }
    if(cn_uart_ready() && cn_tx_byte(&byte)) {
        cn_uart_write(byte); cn_tx_sent();
    }
}
int main(void) {
    platform_init();
    uart_init();
    cn_init(); cn_uart_init();
    last_us=micros();
    for (;;) {
        uint8_t response[5+2*REGISTER_READ_MAX], byte;
        int error;
        watchdog_refresh();
        heartbeat(micros());
        cn_service();
        size_t n = rtu_poll(&receiver, micros(), response, sizeof(response));
        if (n) (void)uart_send(response, n);
        if (uart_receive(&byte, &error)) rtu_feed(&receiver, byte, micros(), error);
    }
}
