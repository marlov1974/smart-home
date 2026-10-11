# P0086 — FTC6 CN105 energy/settings and UART1 diagnostic qualification

## Status and package order
Planned / ordered for Codex. Package order: P0086, following the completed P0083–P0085 investigations. Primary area: Mac tooling, FTC6 protocol research and Procon diagnostic candidates.

This is the next-step package discussed with the operator: energy-counter access and the CN105 settings session, now extended with a dedicated UART1 workstream. Do not reopen or rewrite P0083–P0085 completion reports. Reuse their findings and record corrections or new evidence here.

## Decision summary
- Use the available FTC6 20.01 image as the principal working reference. Obtaining 21.00 is valuable but is NOT a general prerequisite for analysis, offline tooling or designing focused verification.
- Distinguish stable external protocol hypotheses from internal absolute addresses, which must not be transferred to installed 21.00 without evidence. The display's longevity is a compatibility argument, not proof that every diagnostic operation is unchanged.
- Finish concrete transactions and executable offline tests, not another broad scan or general port survey.
- Track A: qualify running energy-code pairs and their decoder.
- Track B: qualify the full CN105 settings session, first for read-and-close without applying settings, then define a narrow pump-level test.
- Track C: qualify UART1 mode selection, baudrate, full memory addressing and diagnostic-log export; build a Mac reader and a precise first-connection plan.
- Tracks can progress independently. Unknown UART1 connector ownership must not block CN105 work or the offline UART1 analysis.

## Authorization and completion level
Authorized now: static analysis, local code/tool changes, offline/synthetic/captured-fixture testing, documentation, and commit/push of verified package-scoped results only. No production activation or firmware deployment is authorized by this package as written.

Physical tests below are defined handoffs, not permission to execute them now. No new live requests, automatic port probing, UART connections, cable moves, DIP/configuration changes, FTC flash operations or pump actuation without a separately recorded approval for the specific stage. Previous P0081 scan permission does not automatically cover new service/session/UART1 operations. Do not request more authorization merely to continue offline work.

## Current evidence and mandatory inputs
Follow AGENTS.md synchronization/bootstrap, then inspect the current implementation and relevant package-run changelogs before coding. Start with:

- `requirements/package-runs/P0083/energy-trace.md`, `service-trace.md`, `candidate-cn105-actions.md`, `decoder-validation.md` and `provenance.md`.
- `requirements/package-runs/P0084/settings-trace.md`, `screen-cn22-trace.md` and `open-questions.md`.
- `requirements/package-runs/P0085/protocol-matrix.md`, `access-gates.md`, `cnit-investigation.md`, `address-evidence.json`, `reproduce.md` and `verification.json`.
- `procon/modular/RAW_API.md`, current CN105/service/Modbus implementation, `tools/raw_mapper.py` and `tools/service_codes.json` under that module.
- Existing `tools/ftc6/` scripts, local Ghidra project and the original MOT/ID files; verify input and tool hashes instead of reinstalling the analysis environment.
- Exact Renesas hardware/software manuals for the identified MCU when checking operands, address semantics, clocks and pins.

The binary used by P0085 has SHA-256 `d828c2e18a013a6adea8a191448b5c5f7d52ac17b3bbc1182c977e190b60976a`. All addresses below refer to that image unless explicitly stated otherwise. A mismatching image requires a separate profile and revalidation, not silent reuse of addresses.

Installation context: Procon works on CN105. The operator identified the original WiFi unit as MAC-597IF-E, attached to CNRF but never successfully working. Do not treat that connection as proof of a working alternative MELCloud port or ask for the already supplied adapter model again. Exact FTC PCB revision and connector-to-MCU routing remain separate evidence needs.

## Track A — running energy through existing CN105

### A1. Finish the decoder and accounting semantics
P0083 identifies A3 pairs 520/521 (consumed DHW candidate), 522/523 (consumed heating), 524/525 (consumed cooling), 526/527 (delivered DHW), 528/529 (delivered heating) and 530/531 (delivered cooling). Each response uses format 1 with BCD data; even/odd selectors return separate portions of a counter.

Verify byte order, BCD digits, scaling, saturation, bucket labels and update triggers from the actual handlers. Keep raw counter units separate from kWh/Wh until the input and timebase justify conversion. Do not call these calendar-day counters without tracing their rollover/reset trigger.

Even-code reads can fold pending accounting into the running bank. Document this side effect and whether query frequency changes the accounting outcome. A naive high-low-high retry may itself fold more accounting: establish a bounded consistency strategy using the actual update behavior rather than assuming the two halves are atomic.

### A2. Implement an offline-tested targeted reader
Extend the host decoder and, where needed, the Procon diagnostic allowlist for these specific qualified codes only. Preserve existing API600 envelopes, correlation, A3 transaction exclusion, sticky results and normal-control compatibility. Explicitly exclude service 532 (snapshot and clear), 340 and other mutating selectors; do not open a blanket A3 range.

Prepare a narrow later comparison using heating 522/523 and 528/529 first, then DHW pairs. Preserve timestamps, raw frames, format, pair consistency, mode, reset/wrap detection and measurement quality. Compare energy increments over matched intervals with GET07, independently integrated water heat and Shelly energy when available. Do not equate calculation precision with calibrated accuracy. Note GET07's full two-byte power fields from P0083 rather than reintroducing low-byte-only decoding.

## Track B — CN105 settings session and pump level

### B1. Derive a complete transaction before constructing live writes
Continue from SET C8, session state 2372, category 4981, import phase 2373 and P0085's category-6 relationship. Establish every transition, input flag, command/category check, expected response, timeout, application acknowledgment, persistence path and exit/abort behavior. Distinguish opening a session from applying settings, and a transport ACK from an effective change.

Readback candidates: GET65 payload10 for the DHW pump setting and GET79 payload7 for the heating setting, both behind CFB18. SET65/79 stage multiple neighboring fields, not just the pump byte. Trace the whole affected block, defaults, validation and range handling; never zero unknown neighbors to change one byte.

### B2. Produce two separately qualified test stages
Stage B-read: open the correct session, read the settings, close without applying changes, verify previous FTC control/session state. The operator's level 5 on both pumps is a comparison point, not an assumed readback. SET C8 changes session state even in this read-first test; document that explicitly.

Stage B-write: only after B-read and full apply/persistence/restore qualification, define one-unit/one-operating-mode 5 → 4 → 5 test. Snapshot and preserve all neighboring settings, verify the configured level, reported PWM and actual flow independently, then verify restoration. Do not promise a particular L/min from a level. If rollback after link loss or restart cannot be established, report a specific blocker and do not make the candidate executable on live hardware.

## Track C — UART1 diagnostic protocol, memory reads and log export

### C1. Separate hardware personality selection from protocol session opening
P0085 found UART1 normal mode (8N2; initialization 08AF86) and diagnostic mode (8E1; initialization 09E642). RAM 06D8 bit7 selects initialization, ISR routing and task handling, with configuration processing rooted at 08E3DE. Diagnostic session state 3D4C is a different mechanism inside the selected personality.

Trace every writer and dependency of 06D8 bit7 to its real source: physical input/DIP, configuration field, board variant or another mechanism. Identify when the selection is sampled and whether reset is required. Determine what entering or leaving diagnostic mode does to ordinary communication, watchdog/scheduler and native heating operation. Do not convert this RAM bit into a guessed DIP instruction. Do not assume a session-start packet can switch an 8N2 port into the 8E1 personality.

### C2. Derive the actual serial timing
Follow oscillator/source selection and all peripheral prescalers to the UART1 BRG configuration for each personality. Document the formula, values, possible variants and resulting baudrate or an explicit unresolved clock dependency. P0085's BRG 0xCF alone is insufficient. Check parity/stop bits, inversion, overrun handling, half/full duplex at the relevant layers and deadlines. Separate MCU UART levels from external connector voltages.

### C3. Complete the five-byte diagnostic transaction
Use dispatch 09E77A and RX/TX 09E66E/09E850/09E87A. Known leads are five-byte checksum-zero requests, low-nibble 0 for session initialization, 1 for memory read 09E938, and 2 for subrequests including 09D88C/09DAC0. Derive all bytes and upper-bit meanings, session prerequisites, busy/idle rules, responses, lengths, checksum coverage, failure outcomes and exit/reset behavior. Provide exact annotated test vectors only after the entire route is grounded. Do not present these partial nibble labels as ready-to-send commands.

### C4. Resolve full memory-address semantics
Trace request address fields through assembly, any bank/far-pointer selection and the actual load at 09E99C into output buffer 1348. Verify operand width, address truncation/wrap and the role of A0 and any extension registers against Renesas documentation and targeted decoder tests, not Ghidra pseudocode alone.

Check the entire requested range, not just its first address. Test modeled boundaries around 64 KiB, 0x080000 and 0x0FFFFF, and the length table at 0832BE (reported values 1/2/4/8/16/32/64, followed by 1 entries). Distinguish parser-accepted addresses from addresses the effective load actually accesses. Identify excluded/reserved/MMIO areas and any read side effects. A software upper-bound check at 0x0FFFFF is not proof of full-flash readability.

Return an evidence-backed accessible-range matrix: RAM, programflash and other memory, with restrictions and confidence. Answer whether the code provides a technically plausible route to reading installed firmware 21.00; qualify it as static feasibility, not a completed dump or guaranteed protection bypass.

Compare the normal-mode 0x52 route through 08ACFC, including its packed 14-bit address, remapping and allowlist. Determine whether useful diagnostics are possible without switching personality. Inspect but do not implement speculative activation of 0x45/0x46 service loops, memory writes, erase/program operations or protection changes.

### C5. Decode the diagnostic log stream independently of memory-dump feasibility
Follow 09D8FE → 13B0 → 09D8A0 → 1346 and the 09D88C log request path. Establish record lengths, direction/source tags, ordering, chunking, counters/timestamps if present, overflow/loss behavior and whether reading drains or clears buffered logs. Retain unknown fields as raw values.

Distinguish internal log fragmentation from the original on-wire frames. P0085 ties the log to CN105 and D traffic; D is not yet physically proven CN22 and could include an internal controller link. Do not label D records as screen traffic or claim a 10–15 s screen delay without evidence. Deliver useful log decoding even if full memory readout remains unresolved.

### C6. Build a reproducible Mac reader with an offline default
Implement an explicit-profile Python CLI and protocol codec under `tools/ftc6/p86/`, covering session, bounded memory reads, log capture/decode and close/abort where established. Default execution is dry-run or fixture replay and must not open a serial device. Pin dependencies and provide `--help`, test vectors and deterministic outputs.

No baud/port brute force, arbitrary command injection or automatic persistent configuration change. A future live invocation must name the qualified port/profile and target explicitly and require a separate explicit execution flag after operator approval. Opening a serial interface can affect DTR/RTS; qualify those behaviors before enabling hardware execution. Enforce address/length bounds, finite retries, request/total time limits, cancellation, no overwrite of existing dumps and raw evidence retention on failure. Do not retry a stateful/log-draining operation until its duplicate semantics are understood.

For stable flash, a later reader should support repeated block comparisons, address-tagged capture, gaps and hashes. For volatile RAM, do not treat changing bytes as corruption or promise a globally atomic snapshot. No device identity, personal logs or full vendor firmware should be exported to public repositories.

### C7. Bind UART1 to the real connector and specify the first physical test
Produce the exact MCU/package UART1 RX/TX candidates from official pin data and the register initialization. Then seek an exact-board schematic or documented connector → component → MCU trace. Keep UART1 → CNIT, UART1 → CNRF and other assignments UNKNOWN until supported. Equal connector shape or supply voltage is not proof of UART interoperability.

Use available photographs and board identifiers; name the smallest missing image/net observation rather than requesting known facts again. If continuity tracing or powered waveform measurements are needed, provide a qualified-operator handoff; do not carry them out under the current offline authorization. Determine ground/reference, supply, logic amplitude, polarity/inversion and isolation before choosing an adapter. Never connect a USB–TTL or RS485 adapter by trial to CN22/CNIT/CNRF.

The first later physical stage is: verify connector/electrical profile and diagnostic-mode prerequisites, then session plus one small non-MMIO/non-destructive read with a justified expected result; repeat and verify closure and normal device state. Log observation is a separate stage. A full dump is subsequent work only if those stages establish access. Lack of the physical map blocks live execution, not completion of the offline codec and addressing proof.

## Invariants and non-goals
- Keep installed BL2/OTA, weekly schedule, control ownership and native FTC protections unchanged. No concurrent-agent policy is added; the operator deliberately schedules physical tests.
- Do not restart completed broad scans, rename prior findings as new discoveries, or claim that failure to find a path proves it absent.
- Do not require new firmware 21.00 before completing these targeted analyses. Never use 20.01 RAM addresses as known 21.00 addresses.
- Preserve original firmware and full private disassembly locally. Publish reproducible scripts, hashes and minimal substantiating excerpts only.
- No bypass of readout protection, no firmware patch to the FTC, no flash write or automatic full-memory dump in this package.

## Files allowed to change
- New `tools/ftc6/p86/` tools, fixtures and tests; minimal shared helper changes only with declared compatibility tests.
- Package-scoped `requirements/package-runs/P0086/` evidence and designs.
- Narrow Procon energy-decoder/allowlist and host-reader candidate changes where Track A requires them, after auditing the current modular code and size impact; no deployment. Record exact affected paths in `functions.md` before editing.
- Relevant `docs/functions/` catalog entries, `memory/knowhow/` lessons, this package, bootstrap manifest and generated repository index.
- Do not change previous package-run outcomes, G1, unrelated source, GitHub workflows, board options or active device configuration.

## Required tests and acceptance
1. Input/profile mismatch and unsupported instruction evidence fail clearly; claimed memory semantics have reproducible opcode/operand checks, including address-boundary fixtures.
2. Energy BCD validates each nibble, pairing consistency, carries, saturation and reset/wrap behavior. No path can submit selector 532 or another excluded mutating selector.
3. Settings-session model covers successful read/close, wrong category/state, delayed or bad reply, abort/timeout, preservation of neighboring fields and inability to qualify apply/rollback. Unknown transitions are explicit blockers, not invented defaults.
4. UART1 tests cover both personalities, the distinction between mode selection and session opening, valid request/response checksums, truncated/oversized frames, invalid lengths/addresses, timeout, duplicate behavior and cancellation. Dry-run/fixture tests prove zero serial/network side effects.
5. Log tests distinguish source/direction, framing, loss and repeated reads where supported; missing timestamps stay missing.
6. Two fresh targeted analysis runs reproduce relevant outputs/hashes. Synthetic or mocked success is reported separately from physical validation.
7. Every track reports analytical PASS/PARTIAL/BLOCKED and physical NOT RUN separately. A tool build cannot be reported as successful live UART1 access or a verified FTC pump-setting change.

Provide concrete runnable verification commands in `reproduce.md`; run the relevant Python tests, existing affected native/ARM tests if firmware candidates change, and `git diff --check`. Record actual commands/results rather than placeholders. Follow normal package review/design/function-design phases and stop on a genuine scope conflict; preserve evidence for incomplete tracks.

## Deliverables
Under `requirements/package-runs/P0086/` create `review.md`, `design.md`, `functions.md`, `energy-qualification.md`, `settings-session.md`, `uart1-mode-selection.md`, `uart1-clock-and-framing.md`, `uart1-memory-addressing.md`, `uart1-log-format.md`, `uart1-port-binding.md`, `physical-test-plan.md`, `reproduce.md`, `findings.md`, `open-questions.md`, `verification.json` and `CHANGELOG.md`.

Supply the Mac tool, tests, compact packet/reference tables and hashes. Each technical claim must identify firmware/tool version, address or documentary source, and CONFIRMED / STRONG HYPOTHESIS / UNKNOWN confidence. Address raw capture needs and lack of an expected 21.00 byte pattern honestly.

On completion report what is now executable offline, what needs one specific physical observation, what remains unknown, and exactly which first physical stage is ready for authorization. Update the file index and function catalog; record whether knowhow was promoted. Commit/push only scoped verified tooling/research results, not active runtime changes. No tests or physical outcomes are predeclared successful by this requirement.

## Offline delivery — 2026-10-11

Implemented tooling and targeted analysis: [P0086 findings](../package-runs/P0086/findings.md), [verification](../package-runs/P0086/verification.json). Tracks A/B/C retain explicit PARTIAL/BLOCKED items; no physical stage, production activation or deployment was performed. The first prepared physical handoff is passive electrical/connector qualification, not a ready-to-send UART1 read or settings write.
