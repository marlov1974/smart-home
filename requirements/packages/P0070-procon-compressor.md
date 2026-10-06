# P0070 — Procon CN105 compressor frequency

Operator request 2026-10-06: read compressor Hz after M1 r2 flash and five successful input0=888 replies. Authorizes building and publishing the next experimental firmware; operator alone flashes. No heat-pump settings or actuator commands.

Scope: CN105 USART1 bring-up, ATW connect and GET0x04 only, compressor payload byte1 in Hz, read-only Modbus diagnostics, automated host/ARM tests and packaged BIN. Preserve input0=888, USART3 settings, heartbeat, vectors and bootloader exclusion. Package source/test/docs/releases/index changes only. Publish verified build to smart-home; hardware completion pending physical flash/readback. No existing Shelly deployment changes.

Validation: malformed frames, checksums/header/length, stale vs zero, counters, reconnect, timeout/wrap, register ranges, concurrent Modbus and CN105 in ARM simulation, image checks and deterministic build. Three hardware debug attempts maximum. No claim of measured Hz until valid live CN105 response.
