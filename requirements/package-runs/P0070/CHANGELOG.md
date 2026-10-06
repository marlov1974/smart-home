# P0070 changelog

Attempt1: new CN105 read-only transport/parser/GET04 scheduler, compressor Hz with validity/staleness, input0–15 diagnostics. Existing RS485 and heartbeat retained. Original hardware init/reference sources reviewed; ACK confirmed1-byte zero before firstbuild. No previous reference code copied. Modbus TX waits service CN105 to prevent receive overrun.

Validation: host ASan/UBSan suites and10 actual-ELF ARM cases pass, including48Hz/0Hz/corrupt simultaneous traffic. Warnings-as-errors, deterministic forced rebuild, originalhash,FFtail and imagebounds pass. BIN3496raw bytes,98304packaged, BSS384. Physical CN105 test pending operator flash. Prior M1r2 evidence added; no live device actions in P0070.

Files: source/include/build/imagecheck/tests, P0070 package/review/design/functions/evidence, new release, relevant living docs and catalog. Fileindex regenerated. Knowhow promotion kept in domain-specific procon/docs/CN105.md: validate ACK shape and service both UARTs during blocking waits; no global Shelly rule changed.

Completion: publish reviewable build/artifacts, not hardware M3/M4 completion. Three physical attempts maximum; none performed yet. Exact MCU package/pins remain inferred. Source handoff in clean isolated /tmp/procon-compressor checkout; original dirty worktree untouched.

## Verified hardware result — 2026-10-06

Operator flashed P0070 compressor r1 (firmware commit `391d903dc9e8197bfda9b83a93014788e06fced9`). Six read-only FC04 blocks at19:23:35–19:23:46 UTC (21:23 local) returned input0=888, input1=70, compressor20Hz, valid1 and sample age0–1s. Accepted CN105 replies increased109→115 and RX events2405→2537; protocol errors0, UART errors0, link1. This confirms continued CN105 updates through our firmware, not merely a cached Modbus constant. Frequency did not change during this short observation; correlation against the physical service display and long-duration stability have not been tested.

Raw evidence: `procon/analysis/live/20261006T192335Z-p0070-compressor.json`. No register/settings writes. This supersedes earlier pending-P0070 hardware notes. M3 bring-up and M4 first compressor telemetry are hardware-confirmed; brine/M5 remains future work. Exact MCU marking/density is still unknown. Immutable release artifacts retain their build-time metadata.

Sync: code/BIN/ELF/MAP/tests were already published in391d903. This follow-up publishes live evidence and updates living status only; release bytes are unchanged. JSON assertions, release checksums and Git diff/file-index checks passed. No firmware rebuild needed. Domain knowhow remains in procon/docs/CN105.md; no new global lesson.
