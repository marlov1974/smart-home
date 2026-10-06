# Experiment history

- test1: repurposed old query/register paths during brine investigation.
- test2-test5: A3/service-code and timing/retry experiments; early retry interpretations were incomplete.
- test6: useful A3 debugger; exposed response count, status/stop reason and full 16-byte A3 payload. Captured `A3 00 1B 00...`.
- test7: A3 service 19 control.
- test8: A3 service 3 control. Compressor frequency could change while A3 attempts accumulated, proving normal polling continued between A3 visits.
- test9-test12: attempted scheduler locks. Debug lock markers did not execute as expected; internal scheduler assumptions were wrong.
- test13: attempted direct A3 retransmission and misused `0x08010EDC` as raw TX. CN105 communication broke. Superseded.
- test14: attempted passive TX trace. Communication was disturbed and trace magic was not observed. Do not use it as evidence of actual transmitted data.

Decision after test14: stop incremental scheduler patching. Reverse-engineer only enough hardware to create clean replacement firmware. First clean target: Modbus Input Register 0 = 888.

- P0069: original verified, L433 family inferred, fresh2KiB M1 candidate built. Native sanitizers and six compiled-ARM simulated cases pass. No original routines patched or copied. No flash performed by Codex; operator physical test pending.

P0069 attempt2: initial M1 hardware readback failed with seven timeouts. Shelly settings96008N1 verified; operator confirmed flash/reconnect/DIP/reset. Original USART3 SWAP=1 was omitted in M1; r2 corrects only CR2 bit15 and passes enhanced wiring-aware emulator. Physical r2 test pending.

## P0070 — 2026-10-06

M1 r2 hardware pass: operator reports blinking; five consecutive FC04 raw input0 reads returned888. Evidence: `analysis/live/20261006T190106Z-m1-r2-readback.json`. This supersedes older pending-M1 status.

P0070 adds USART1 read-only ATW connect/GET0x04. Input0 stays888; input1=70, input2=Hz or65535 unknown/stale; input3 validity, input4 age and further counters. UART/packet errors are visible. CN105 electrical communication remains unverified until operator flashes P0070 and live values are captured. No device setting writes by this package. Firmware tests pass; hardware milestone M3/M4 remains pending.

## Verified hardware result — 2026-10-06

Operator flashed P0070 compressor r1 (firmware commit `391d903dc9e8197bfda9b83a93014788e06fced9`). Six read-only FC04 blocks at19:23:35–19:23:46 UTC (21:23 local) returned input0=888, input1=70, compressor20Hz, valid1 and sample age0–1s. Accepted CN105 replies increased109→115 and RX events2405→2537; protocol errors0, UART errors0, link1. This confirms continued CN105 updates through our firmware, not merely a cached Modbus constant. Frequency did not change during this short observation; correlation against the physical service display and long-duration stability have not been tested.

Raw evidence: `procon/analysis/live/20261006T192335Z-p0070-compressor.json`. No register/settings writes. This supersedes earlier pending-P0070 hardware notes. M3 bring-up and M4 first compressor telemetry are hardware-confirmed; brine/M5 remains future work. Exact MCU marking/density is still unknown. Immutable release artifacts retain their build-time metadata.

## P0071 brine candidate

Adds a separate read-only service27/28 state machine with exclusive CN105 transaction ownership, bounded retries and continued GET04 telemetry. Preserves P0070 registers0–15 (build marker71); adds16–67, with max16 registers per read. Raw completed payloads are retained per service; temperature candidates use reference-backed signed little-endian encoding and remain experimental. See [BRINE.md](BRINE.md) and `../releases/P0071-brine-r1/README.md`. Software tests pass; no P0071 hardware readings or physical flash yet. Previous P0070 hardware result remains valid historical evidence.
