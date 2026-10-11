# P0086 findings

Offline tooling and research delivered; physical tests **NOT RUN**. No runtime, allowlist or deployment changes. The exact 20.01 image and repaired M16C decoder are pinned in verification.json. Installed 21.00 compatibility is not assumed.

| Track | Analytical status | Concrete outcome | Physical readiness |
|---|---|---|---|
| A: energy | PARTIAL; decoder PASS | Corrected odd BCD truncation; forced reads discard remainders in mode 1; frame decoder and capture quality | Calibration and atomicity unresolved; production polling not enabled |
| B: settings | PARTIAL; live BLOCKED | States 0–12, C8 status and GET side effects, staged neighboring fields; offline observer and diff | Internal ACK, persistence and rollback unqualified |
| C: UART1 | PARTIAL; codec/load proof PASS | Five-byte codec, bounded replay, address proof, log decoder; 222 identical analysis exports | Connector, mode input, absolute clock and expected 21.00 RAM value unresolved |

The most consequential result: the parser accepts wide addresses but the actual memory load uses 16-bit A0. Requested 080000 reads near 0000, not program flash. This path cannot provide a qualified full firmware dump. Eight instruction-emulator cases confirm the reviewed opcode; this is not a physical readout-protection test.

Energy-counter reads are not observationally neutral. Mode 1 rounds down and clears pending remainders; rapid polling can change the result. The odd word's low byte is zero, so reconstruction has 10 raw-unit resolution. P83's intermediate formula and retry advice are corrected here, without rewriting the historical report.

Executable offline: energy/A3 capture decoding, UART1 session/read/log packet planning, fixture replay, malformed-response handling, memory alias checks and log reassembly. The settings model consumes explicitly supplied observations; it does not fabricate the missing internal handshake.

The first ready physical handoff is passive connector/electrical qualification C0, not sending read requests. See [physical-test-plan.md](physical-test-plan.md). The adapter model MAC-597IF-E is already known. Its unsuccessful CNRF connection is not evidence of protocol compatibility.
