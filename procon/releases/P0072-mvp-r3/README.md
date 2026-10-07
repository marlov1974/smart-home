# P0072 MVP r3 — operation-specific control gate

Fixes r2's blanket GET28 gate: valid cooling/Zone2 flags no longer block Zone1 heating. Relevant heating/DHW inhibits, holiday and server control remain blocking; unknown encodings still reject. No Mitsubishi prohibition flag is changed. The first live r2 failure did not expose its particular flag, so r3 cannot promise that this site's actual blocker is irrelevant.

GET28 is polled read-only in the ordinary FAST cycle. Input283–298 now expose raw payload, age/generation and exact last flag rejection. These can be inspected before any control attempt. Identity68/69/70 = 3/1/3. Existing command envelope2,20-value API and original raw200–255 unchanged. [API](../../docs/CONTROL_API.md).

Flash `procon-mvp.bin` with the established vendor procedure. Operator alone flashes. Application base0x08008000,98304-byte96KiB envelope paddedFF through0x0801FFFF; bootloader excluded. Code11320 bytes,BSS984 bytes. ELF debug-stripped with symbols; MAP paths normalized. Recovery: [previous r2](../P0072-mvp-r2/README.md) / [read-only r1](../P0072-mvp-r1/README.md), using [recovery instructions](../../docs/RECOVERY.md).

Verified: native ASan/UBSan suites with84 flag cases,9 Python unit tests,15 actual-ELF ARM scenarios including unrelated flags allowing FIXED38/AUTO and heating inhibit rejecting before SET. Service27/28 exclusivity, watchdog/heartbeat and no flash writes remain tested. Deterministic BIN rebuild passed. No live commands/flash in this build; physical SET validation remains pending, one prior r2 hardware attempt.

**Supervised candidate. Reset/power loss still loses the saved session; restoration is not guaranteed after reset or link loss.** Retain original settings externally. After flash read new raw diagnostics and telemetry first, then test short command/readback/AUTO/lease before any longer run.

SHA256: `f0d33dab1a181d133bc1d5b9c5501ceb1952e71b798d93514a6bf9a1932a2fde`.
