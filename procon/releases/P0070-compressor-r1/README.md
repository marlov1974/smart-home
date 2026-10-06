# P0070 — CN105 compressor r1

Experimental firmware; operator performs physical flashing. M1 r2 was verified on hardware with five FC04 input0=888 reads and visible heartbeat. This version adds read-only CN105 polling; its physical CN105 result is still pending.

Flash `procon-compressor.bin` using the same vendor procedure. File is98304bytes (96KiB), application base0x08008000; FF padding covers original application footprint, not all unknown device flash. Bootloader region is excluded. Keep original firmware and M1 r2 for recovery; see../../docs/RECOVERY.md. Do not mass-erase. Restore normal DIP/connection/power after programming. PC12 heartbeat remains.

RS485:96008N1,slave1,FC04 input registers, **zero-based raw addresses**. This is our new map, not the original Procon H73 map. Query the entire block: `MbRtuClient.ReadInputRegisters?id=100&sid=1&addr=0&qty=16`.

| Address | Meaning |
|---|---|
|0|888 sanity marker|
|1|70 build marker|
|2|Compressor frequency, whole Hz;65535 means unknown/stale|
|3|Valid frequency:1=yes,0=no|
|4|Sample age, seconds;65535=never received or saturated|
|5|Accepted0x04 reply count, low16|
|6|CN105 receive-event count, low16 (includes UART errors)|
|7|Malformed packet/gap/checksum count, low16|
|8|CN105 frames queued to UART, low16|
|9|Uptime seconds from32-bit ms clock, low16|
|10|Addressed CRC-valid Modbus request count, low16|
|11|CN105 linked:0/1; link alone does not validate frequency|
|12|CN105 UART error/queue-timeout count, low16|
|13|Last checksum-valid CN105 frame type|
|14|Last checksum-valid frame payload byte0|
|15|Accepted connect ACK count, low16|

CN105:USART1 PA9TX/PA10RX,24008E1. Only ATW connect and GET0x04; first connect after1s, retries3s, GET every2s after ACK. Reading valid zero means compressor reports0Hz. A missing/stale result is65535 with valid0; stale timeout10s. No SET/actuator commands, EEPROM/flash writes or automatic baud scan. No Modbus writes accepted.

Software validation: GCC warnings-as-errors; ASan/UBSan host suites; actual ARM ELF emulation including concurrent CN10548Hz,0Hz and corrupt replies while Modbus responds; deterministic rebuild; original hash unchanged; vector/RAM/flash/FF-tail checks. Synthetic test values are not live measurements. Exact MCU package/density and CN105 electrical routing remain physically unverified.

BIN SHA256: `566f50f5653ab94f99d0941171da328c5dfa2651fe70766893c0be6c659e5bcc`.
