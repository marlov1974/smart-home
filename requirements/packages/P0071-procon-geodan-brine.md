# P0071 — Procon Geodan brine temperatures

Operator request 2026-10-06: extend the hardware-verified P0070 clean-room Procon firmware with read-only Geodan brine telemetry. Preserve all working P0069/P0070 behavior. Operator alone performs physical installation. No heat-pump settings or actuator commands.

## Baseline

P0070 is mandatory baseline. Preserve:
- Modbus FC04 input0 = 888;
- heartbeat LED;
- live compressor-frequency telemetry;
- CN105 link/reconnect behavior;
- watchdog, image/vector and bootloader-exclusion checks.

Do not use the old patched-Procon scheduler experiments as implementation architecture; they are historical evidence only.

## Goal

Add a separate non-blocking CN105 service-operation state machine for service 27 and 28, identified by prior project evidence as the Geodan TH32/TH34 candidates used for brine telemetry.

Prior project evidence says the service operation is distinct from normal polling, not-ready responses remain pending, and retries should occur at about one-second cadence. Reuse the project's existing CN105 framing/checksum implementation and the protocol details already documented in procon/docs rather than duplicating protocol constants here.

## Architecture

Implement conceptually:

IDLE -> request service 27 -> WAIT_REPLY -> not-ready: WAIT_RETRY -> retry after about 1000 ms -> completed: store result -> service 28 -> same sequence -> normal schedule.

Requirements:
- no busy-wait and no blocking callback;
- watchdog and Modbus remain responsive;
- normal telemetry including compressor Hz continues updating;
- one CN105 transaction owns the link at a time;
- explicit timeout/reconnect/error recovery;
- finite documented retry limit;
- read-only requests only.

Do not assume temperature encoding until supported by a captured completed response or existing reference-parser evidence. Preserve raw response bytes so decoding can be corrected without repeating protocol discovery.

## Modbus diagnostics

Preserve every existing P0070 register/address and add new read-only registers without renumbering.

Expose at minimum:
- service 27 raw/decoded value, valid flag and sample age;
- service 28 raw/decoded value, valid flag and sample age;
- current service state and active service code;
- latest service status;
- retry count;
- accepted service-response count;
- timeout/error count;
- sufficient raw response payload for decoding diagnostics.

Only expose a signed/scaled temperature as authoritative after encoding is evidenced. Until then raw data is authoritative and decoded data must be labelled experimental.

## Automated regression

Add tests for:
- request construction/checksum for both service codes;
- not-ready retry;
- both completion statuses documented by existing project evidence;
- retry timeout/exhaustion;
- malformed/corrupt response;
- wrong echoed service code;
- interleaving with normal compressor polling;
- timer wrap;
- Modbus reads while service operation is pending;
- compressor telemetry continuing through repeated service cycles.

Add ARM/mock-peripheral regression for concurrent Modbus + normal CN105 telemetry + service operation.

## Hardware validation

Operator alone flashes and performs read-only validation.

Hardware pass should demonstrate:
1. input0 remains 888;
2. heartbeat remains active;
3. compressor Hz remains live;
4. service 27 and 28 transactions are observed;
5. echoed service/status are captured;
6. not-ready retries occur around one-second cadence;
7. Modbus remains responsive during retries;
8. any completed response is preserved in full and compared with the physical Mitsubishi service display before claiming decoded brine temperature;
9. CN105 protocol/UART error counters remain acceptable and the link recovers after service completion.

Do not claim brine temperature hardware-verified until a real completed response has been captured and the decoding is sufficiently correlated.

Maximum three hardware debug attempts before reassessing assumptions.

## Deliverables

Update source, tests, procon documentation, package-run evidence and release artifacts in the existing Smart Home repository. Include BIN/ELF/MAP/disassembly/SHA256, deterministic rebuild verification, register map, raw hardware evidence, and a clear distinction between software verification and hardware-confirmed decoding.

No unrelated Shelly/G2 runtime changes.
