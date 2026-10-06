# Project plan

## Phase A
Verify exact MCU, memory/bootloader boundary, clocks, RS485 UART, serial settings, transceiver direction GPIO and original Modbus behavior.

## Phase B
Minimal clean application: startup + clock + RS485 UART + Modbus RTU CRC/parser. Input Register 0 returns 888.

## Phase C
Add uptime, Modbus request count and build marker.

## Phase D
Only after stable Modbus, bring up CN105.

## Phase E
Read one known CN105 value, then implement Geodan A3 service 27/28.

Do not combine several unverified hardware subsystems in the first bring-up image.

## P0069 status

PhaseA: strong L433/pin mapping inference; exact physical device and device bootloader remain unavailable. Operator permits inferred MCU. PhaseB: source, build, static checks, native tests and compiled-ARM simulation complete. Deliver experimental candidate to operator; M1 not hardware-complete until FC04 input0 yields888. PhasesC–E remain deferred.

P0069 attempt2: initial M1 hardware readback failed with seven timeouts. Shelly settings96008N1 verified; operator confirmed flash/reconnect/DIP/reset. Original USART3 SWAP=1 was omitted in M1; r2 corrects only CR2 bit15 and passes enhanced wiring-aware emulator. Physical r2 test pending.

Final M1 r2: procon/releases/P0069-m1-r2/procon-m1.bin is98304bytes (96KiB),0x08008000–0x0801FFFF, including0xFF padding over the previous original application footprint. Code still limited to16KiB; bootloader excluded. PC12 heartbeat toggles every500ms as startup indication; USART3 SWAP=1. Final BIN SHA2561ad976eef711558ed180a4037e84885f7d74b76175ac2ba0daea0d171f864073. Physical verification pending.

## P0070 — 2026-10-06

M1 r2 hardware pass: operator reports blinking; five consecutive FC04 raw input0 reads returned888. Evidence: `analysis/live/20261006T190106Z-m1-r2-readback.json`. This supersedes older pending-M1 status.

P0070 adds USART1 read-only ATW connect/GET0x04. Input0 stays888; input1=70, input2=Hz or65535 unknown/stale; input3 validity, input4 age and further counters. UART/packet errors are visible. CN105 electrical communication remains unverified until operator flashes P0070 and live values are captured. No device setting writes by this package. Firmware tests pass; hardware milestone M3/M4 remains pending.

## Verified hardware result — 2026-10-06

Operator flashed P0070 compressor r1 (firmware commit `391d903dc9e8197bfda9b83a93014788e06fced9`). Six read-only FC04 blocks at19:23:35–19:23:46 UTC (21:23 local) returned input0=888, input1=70, compressor20Hz, valid1 and sample age0–1s. Accepted CN105 replies increased109→115 and RX events2405→2537; protocol errors0, UART errors0, link1. This confirms continued CN105 updates through our firmware, not merely a cached Modbus constant. Frequency did not change during this short observation; correlation against the physical service display and long-duration stability have not been tested.

Raw evidence: `procon/analysis/live/20261006T192335Z-p0070-compressor.json`. No register/settings writes. This supersedes earlier pending-P0070 hardware notes. M3 bring-up and M4 first compressor telemetry are hardware-confirmed; brine/M5 remains future work. Exact MCU marking/density is still unknown. Immutable release artifacts retain their build-time metadata.

## P0071 brine candidate

Adds a separate read-only service27/28 state machine with exclusive CN105 transaction ownership, bounded retries and continued GET04 telemetry. Preserves P0070 registers0–15 (build marker71); adds16–67, with max16 registers per read. Raw completed payloads are retained per service; temperature candidates use reference-backed signed little-endian encoding and remain experimental. See [BRINE.md](BRINE.md) and `../releases/P0071-brine-r1/README.md`. Software tests pass; no P0071 hardware readings or physical flash yet. Previous P0070 hardware result remains valid historical evidence.

## P0071 r2 — operator-directed exclusive sequence

The operator explicitly changed the schedule after r1 only returned A3 status0. Send exactly one Hz GET04, then service27 including all retries, then service28 including all retries, and repeat. No Hz or other query is inserted between retries or between27and28. One request owns the link at a time; retain1s minimum retry cadence,10attempt limit,800ms reply timeout,1sTXqueue timeout and50ms turnaround. The prior20s cycle cooldown is removed. State4 now means DONE waiting for next Hz, not cooldown. Link-loss reconnect is deferred until both bounded service operations finish; then connection recovery restarts from Hz. This overrides the previous interleaved polling design under explicit user direction.

Hz freshness remains truthful: during a long service sequence it can exceed10s, so input3 becomes0 and input2 becomes65535 until the next normal response. Input4 exposes age. Do not call this an unexpected communication failure without checking the phase/counters. Brine validity/retention unchanged. Inputs0–67 unchanged except state4 semantics; new input68=2 identifies r2. Marker0=888 and build1=71 remain. Maximum16registers/read.

Native65s simulations assert every emitted request follows Hz→27→28, including not-ready,missing,corrupt,wrong-echo,terminal-status and timer-wrap cases. All12ARM cases pass; pending-service case emits only one Hz then five27 requests while Modbus responds; complete case reaches next Hz only after28. Checksums/frame whitelist, heartbeat and no flash/control writes remain tested. r2 hardware result pending; no temperature is hardware-confirmed. Physical attempt1 was r1, pending-only, evidence stored in analysis/live/20261006T200502Z-p0071-first-readback.jsonl.

## P0071 r2 live result — 2026-10-06

45read-only sample groups show repeated completed27/28 responses,status2,raw5 for both. Completed counters27:4→9,28:4→8; UART/protocol/service errors0,exhaustions0. Operator replied "5" when asked about display027/028, matching the reference decoding at this operating point. This single response does not separately establish channel mapping or validate negative/full-range scaling. Raw evidence: procon/analysis/live/20261006T202303Z-p0071-r2-readback.jsonl; full report: requirements/package-runs/P0071/hardware-validation.md. No firmware changes. This supersedes earlier pending-r2-result notes; immutable release metadata remains as built.

## P0072 r1 — read-only MVP candidate

Latest build P0072-mvp-r1, operator flash pending. Implements FAST04/0C/14/0B/09/15/26 then one exclusive round-robin A3 service27/28 operation, preserving retry ownership. Adds20-field version1 API (18 mapped/derived candidates; brine pump run/step unavailable), status/age/generations, raw FAST payloads and fixed-point water heat. Marker1=72,revision68=1. Legacy addresses retained;42 counts individual service operations. See [MVP_API.md](MVP_API.md) and [PUMPS.md](PUMPS.md) for evidence and limits. No controls/SET/lease implementation; all writes rejected and control capability unavailable. P0071 physical evidence remains historical, not P0072 validation. No live actions performed in build.
