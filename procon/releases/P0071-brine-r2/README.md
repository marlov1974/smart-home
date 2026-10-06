# P0071 brine r2 — exclusive service sequence

Flash `procon-brine.bin` (98304bytes/96KiB) using the same operator-controlled vendor procedure as r1/P0070. Code base0x08008000; FF to0x0801FFFF; bootloader area excluded. Keep earlier immutable releases for recovery; see../../docs/RECOVERY.md. No physical installation by Codex.

**Order: Hz once → service27 (up to10attempts) → service28 (up to10attempts) → repeat.** A retry waits at least1000ms from the prior request start. No Hz or other CN105 query is inserted during either service operation or between27and28. No20s pause between cycles. Modbus and watchdog keep working on the separate path. Missing link is recovered after the bounded27/28 sequence, not by interrupting it.

Read raw input0=888,1=71,68=2. Existing0–67map preserved, max16words per read; input32 state4 means cycle DONE. Raw payloads/experimental temperature map in../../docs/BRINE.md. Hz older than10s is honestly marked stale (input3=0,input2=65535,age in4); next cycle refreshes it. Do not infer compressor stopped from this sentinel.

Software validation: native ASan/UBSan exact outgoing-sequence assertions through65s cycles and millis wrap;12actual-ELF ARM cases with responsive Modbus and no interleaved Hz; deterministic forced rebuild; vector/image/FF bounds; previous releases untouched. Code5264bytes,BSS492. **Physical r2 service completion and temperature correlation remain unverified.** r1 hardware evidence showed status0only with interleaved polling; r2 tests that scheduling hypothesis, not a proven fix.

Operator flashes, then read-only log service status/retries/rawpayload and compare any completed27/28 result with Mitsubishi display before treating it as a confirmed temperature. This will be hardware attempt2of3. No heat-pump settings, SET commands or persistent writes.

SHA256 `958ba0f354ac9217535e2501cae8ee734347bd669e2b9929d60f65ce0d1f9092`.
