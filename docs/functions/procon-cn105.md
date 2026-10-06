# P0070 Procon CN105 and telemetry

`cn_init` clears volatile protocol state. `cn_feed(byte,ms,error)` consumes one UART event, validates bounded ATW frames and updates only valid ACK/GET04 cache. `cn_tick(ms)` handles partial-frame timeout, stale invalidation, connection timeout and bounded TX scheduling. `cn_tx_byte` peeks queued byte; `cn_tx_sent` advances after hardware accepts it. `cn_read(address)` returns diagnostic fields; read map defined by P0070 release.

`cn_uart_init/receive/ready/write` configure/service USART1 with no DMA/interrupts,24008E1,PA9/10AF7,noSWAP. `cn_service` accumulates a wrap-safe microsecond delta into milliseconds, ticks state, drains at most8RX events and sends at most1TX byte; it runs in main and RS485 wait loops. These calls write only UART/GPIO/RCC volatile registers, not flash or pump settings.

`modbus_reply` adds bounded FC04 multi-register reads0–15 and a request counter. Unknown ranges/write functions retain exceptions. Each response is assembled synchronously before transmission. All protocol and image behavior is covered by host/ARM suites; hardware validation pending.
