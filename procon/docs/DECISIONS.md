# Decisions

- Keep this project under the existing Smart Home repository; no nested `.git`.
- First clean-room milestone is RS485/Modbus register 0 = 888.
- CN105 is deferred until M1/M2 are stable.
- Preserve failed reverse-engineering experiments rather than silently reusing their assumptions.

- P0069 operator owns physical flashing from separate computer. User explicitly allows guessed/inferred MCU; use evidence-backed STM32L433 profile and label uncertainty.
- Use HSI16 and polling-only USART3 for M1, fixed96008N1/slave1, PD2 direction. No EEPROM access, CN105 or flash writes.
- Conservative16KiB app/16KiB SRAM linker,2KiB padded candidate; retain original recovery files. Software pass is distinct from hardware milestone completion.

P0069 r2: fix proven USART3 SWAP omission before speculative start-vector changes. Add PC12 heartbeat on operator report of no LEDs, and extend delivered BIN to old application page footprint (98304bytes) using0xFF. Preserve first release unchanged for regression evidence.

P0070: M1 r2 now hardware-confirmed; next experimental build adds CN10524008E1 on PA9/10AF7 and read-only compressor telemetry. See `../releases/P0070-compressor-r1/README.md` and `CN105.md`. Same conservative flash/RAM/vector limits and96KiB FF envelope. Physical CN105 result pending. No setting writes or physical flash by Codex.

## P0071 brine candidate

Adds a separate read-only service27/28 state machine with exclusive CN105 transaction ownership, bounded retries and continued GET04 telemetry. Preserves P0070 registers0–15 (build marker71); adds16–67, with max16 registers per read. Raw completed payloads are retained per service; temperature candidates use reference-backed signed little-endian encoding and remain experimental. See [BRINE.md](BRINE.md) and `../releases/P0071-brine-r1/README.md`. Software tests pass; no P0071 hardware readings or physical flash yet. Previous P0070 hardware result remains valid historical evidence.

## P0071 r2 — operator-directed exclusive sequence

The operator explicitly changed the schedule after r1 only returned A3 status0. Send exactly one Hz GET04, then service27 including all retries, then service28 including all retries, and repeat. No Hz or other query is inserted between retries or between27and28. One request owns the link at a time; retain1s minimum retry cadence,10attempt limit,800ms reply timeout,1sTXqueue timeout and50ms turnaround. The prior20s cycle cooldown is removed. State4 now means DONE waiting for next Hz, not cooldown. Link-loss reconnect is deferred until both bounded service operations finish; then connection recovery restarts from Hz. This overrides the previous interleaved polling design under explicit user direction.

Hz freshness remains truthful: during a long service sequence it can exceed10s, so input3 becomes0 and input2 becomes65535 until the next normal response. Input4 exposes age. Do not call this an unexpected communication failure without checking the phase/counters. Brine validity/retention unchanged. Inputs0–67 unchanged except state4 semantics; new input68=2 identifies r2. Marker0=888 and build1=71 remain. Maximum16registers/read.

Native65s simulations assert every emitted request follows Hz→27→28, including not-ready,missing,corrupt,wrong-echo,terminal-status and timer-wrap cases. All12ARM cases pass; pending-service case emits only one Hz then five27 requests while Modbus responds; complete case reaches next Hz only after28. Checksums/frame whitelist, heartbeat and no flash/control writes remain tested. r2 hardware result pending; no temperature is hardware-confirmed. Physical attempt1 was r1, pending-only, evidence stored in analysis/live/20261006T200502Z-p0071-first-readback.jsonl.

## P0072 r1 — read-only MVP candidate

Latest build P0072-mvp-r1, operator flash pending. Implements FAST04/0C/14/0B/09/15/26 then one exclusive round-robin A3 service27/28 operation, preserving retry ownership. Adds20-field version1 API (18 mapped/derived candidates; brine pump run/step unavailable), status/age/generations, raw FAST payloads and fixed-point water heat. Marker1=72,revision68=1. Legacy addresses retained;42 counts individual service operations. See [MVP_API.md](MVP_API.md) and [PUMPS.md](PUMPS.md) for evidence and limits. No controls/SET/lease implementation; all writes rejected and control capability unavailable. P0071 physical evidence remains historical, not P0072 validation. No live actions performed in build.
