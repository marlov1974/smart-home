# P0070 Procon CN105 and telemetry

`cn_init` clears volatile protocol state. `cn_feed(byte,ms,error)` consumes one UART event, validates bounded ATW frames and updates only valid ACK/GET04 cache. `cn_tick(ms)` handles partial-frame timeout, stale invalidation, connection timeout and bounded TX scheduling. `cn_tx_byte` peeks queued byte; `cn_tx_sent` advances after hardware accepts it. `cn_read(address)` returns diagnostic fields; read map defined by P0070 release.

`cn_uart_init/receive/ready/write` configure/service USART1 with no DMA/interrupts,24008E1,PA9/10AF7,noSWAP. `cn_service` accumulates a wrap-safe microsecond delta into milliseconds, ticks state, drains at most8RX events and sends at most1TX byte; it runs in main and RS485 wait loops. These calls write only UART/GPIO/RCC volatile registers, not flash or pump settings.

`modbus_reply` adds bounded FC04 multi-register reads0–15 and a request counter. Unknown ranges/write functions retain exceptions. Each response is assembled synchronously before transmission. All protocol and image behavior is covered by host/ARM suites; hardware validation pending.

## Verified hardware result — 2026-10-06

Operator flashed P0070 compressor r1 (firmware commit `391d903dc9e8197bfda9b83a93014788e06fced9`). Six read-only FC04 blocks at19:23:35–19:23:46 UTC (21:23 local) returned input0=888, input1=70, compressor20Hz, valid1 and sample age0–1s. Accepted CN105 replies increased109→115 and RX events2405→2537; protocol errors0, UART errors0, link1. This confirms continued CN105 updates through our firmware, not merely a cached Modbus constant. Frequency did not change during this short observation; correlation against the physical service display and long-duration stability have not been tested.

Raw evidence: `procon/analysis/live/20261006T192335Z-p0070-compressor.json`. No register/settings writes. This supersedes earlier pending-P0070 hardware notes. M3 bring-up and M4 first compressor telemetry are hardware-confirmed; brine/M5 remains future work. Exact MCU marking/density is still unknown. Immutable release artifacts retain their build-time metadata.
