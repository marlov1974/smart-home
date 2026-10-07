# P0072 MVP r2 — supervised control candidate

Operator flashes `procon-mvp.bin` using the established vendor procedure. 98304 bytes (96 KiB), application base 0x08008000, FF through 0x0801FFFF; bootloader excluded. Code 10776 bytes. Inferred STM32L433 target unchanged. No device writes or physical flash were performed for this build. Hardware control validation is pending (0/3 attempts).

Implements OFF, FIXED_FLOW (20–45 C), DHW boost/target (40–60 C), selected targets and AUTO restoration of the saved session. Atomic FC16 command, original snapshot, matched readback and runtime lease (30–1800 s). [Full command API and limitations](../../docs/CONTROL_API.md). Existing telemetry and complete A3 service-operation exclusivity retained. Identity inputs 68/69/70 = 2/1/3; input 71 = control state.

**Experimental: supervised testing only. Reset or power loss loses the RAM snapshot and cannot guarantee restoration.** Retain original settings externally. AUTO restores the saved original state, not necessarily curve mode. Native safety/priority still applies. Readback confirms settings, not actual delivered temperature. Link loss can delay restoration indefinitely.

Native ASan/UBSan tests, 8 Python unit tests and 14 compiled-ELF ARM cases passed. The ARM integration simulates FIXED_FLOW 38 C then AUTO, checks readback, preserved A3 sequencing and no flash writes. These are software models, not physical SET validation. Deterministic BIN rebuild verified. Distributed ELF is debug-stripped; symbols retained. MAP paths normalized.

First after flash: read identity and fresh telemetry, then supervised short control/readback/AUTO/lease-expiry validation before a 15-minute experiment. Recovery image: [previous read-only P0072 r1](../P0072-mvp-r1/README.md); recovery does not itself restore persistent Mitsubishi settings. [Recovery procedure](../../docs/RECOVERY.md).

SHA256: `a6b9d82f3b8fceafeaca2fcc1ac7100b48dd7bfe2a80d554dd3583c434933d90`.
