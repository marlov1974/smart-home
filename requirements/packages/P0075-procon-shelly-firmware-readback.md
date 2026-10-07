# P0075 — Procon firmware readback through Shelly and exact build comparison

## Status
planned — implementation and supervised hardware readback authorized; no A1M programming authorized.

## Decision and scope

Operator request, 2026-10-07: read the firmware from the A1M currently connected through Shelly, save it on the Mac and compare it with the replacement firmware we built. The operator changes the A1M DIP switches and power-cycles the A1M. Codex prepares the tooling, temporarily changes the connected Shelly serial transport to raw UART at 115200 8N1, performs discovery and flash readback, compares the dump and restores the Shelly configuration.

This is a readback experiment, not the previously discussed general-purpose updater. Do not add or exercise A1M erase, program, unlock, write-protection changes, firmware replacement, EEPROM writes or heat-pump controls. No 9600-bootloader or alternative DIP-combination experiments are part of this package.

## Architecture and repository ownership

Mac/Codex owns the session, reference files, durable raw dumps, checksums and comparison. A temporary Shelly script owns the RS485 port, bounded binary receive buffers and local transaction timing. A1M stays by the heat pump and retains its existing CN105 power connection; no new supply wiring is needed for this experiment. The operator alone performs physical DIP/power actions. Do not power-cycle the heat pump as a substitute for restarting the adapter.

Reusable transport/protocol/comparison code, tests and independent documentation belong in `marlov1974/procon-melcobems-mini-a1m`. Package coordination and sanitized site evidence belong in `marlov1974/smart-home`. Do not create two implementations or port/change the application firmware. Preserve existing standalone licensing and no-vendor-artifact rules.

## Evidence baseline and unresolved questions

Read P0069–P0074 evidence, especially P0072 revision-specific changelogs. At package creation, Smart Home has P0072 r1, r2 and r3 artifacts; r3's changelog says hardware pending. The standalone README still describes r1. Neither latest source nor either README proves what is installed. Record both repository commits and identify the current device before selecting the expected image.

Previous site evidence used Shelly `MbRtuClient` instance 100 and A1M slave 1 at 9600 8N1. Resolve current reachability from local configuration and package evidence; verify actual Shelly identity/model/firmware and Serial instance. Do not assume a previous IP or UART instance 0 identifies the right hardware.

The documented host update path uses 115200 8N1 and discovery byte 0x5A. Its 12-byte discovery reply begins 0x7A and reports max flash, max EEPROM, erase block and max write page, with a checksum. Reproduce the decoder/checksum from evidence before transmitting. These size fields do not prove CPU identity, total readable memory or read-address semantics.

A separate static audit of the supplied v3.1.05 Windows package found unused constants in `FirmwareDownloader.bootloaderCMD`:

| Meaning | Value |
|---|---|
| READ_FROM_FLASH_REQ | 0x57 |
| READ_FROM_FLASH_ACK_OK | 0x77 |
| READ_FROM_FLASH_ACK_NG | 0x76 |

Audit identity: ZIP SHA256 `45e46af9892d16141db05bb6a03e4d51dbc06c46d88eb4dd56db5f5f853a4f12`; member `Procon_R5_Firmware_Update Tool/FirmwareDownloader.dll`, 19456 bytes, SHA256 `0de5a97616aa939f6302dacec4ce2f97de917df661b69c7208f76f6cf6330eec`. Flash-read field tokens 0x04000010–0x04000012; Constant rows at DLL offsets 0x2284/0x228A/0x2290. An unused `bufferCRC32Check` exists but has suspect comparison/index logic; do not use it as a correctness oracle. Recheck these findings using the lawfully held original package and existing analysis tooling. Original files stay immutable and are not exported.

The enum does NOT establish the request's address/length layout, response framing/CRC, absolute versus application-relative addressing, or implementation of reading in the resident bootloader. Resolving these is part of the research, not a fact to invent. Before transmitting 0x57, document a sufficiently supported complete frame and bounded reply contract. If safe framing cannot be established, stop hardware read attempts with `BLOCKED_READ_PROTOCOL`; a successful discovery is only partial progress. No opcode sweep, arbitrary command endpoint or blind frame permutations. After ambiguous framing/timeouts, stop and resynchronize through an operator-controlled new boot session rather than streaming guesses.

Relevant official API references, checked 2026-10-07:
- https://shelly-api-docs.shelly.cloud/gen2/ComponentsAndServices/Serial/
- https://shelly-api-docs.shelly.cloud/gen2/Scripts/APIs/UART/

`Serial` lists device-specific supported `modes`; `jsuart` exposes a port to one script. Runtime configuration and UART 115200 8N1 are documented, but availability, binary handling, half-duplex and DE behavior must be verified on this Shelly. Do not flash/upgrade Shelly firmware or switch to USB/JTAG if this path is unsupported; report the exact blocker.

## Execution stages

### A. Offline preparation and baseline

Synchronize both repos safely with origin/main without discarding local work. Use normal bootstrap for a fresh Codex session, or package/delta bootstrap in an already bootstrapped session. Read `AGENTS.md`, the active package, relevant changelogs and standalone P0074 boot/electrical references. Write review.md, design.md and functions.md before implementation.

Read the existing Shelly and A1M without settings writes. Capture:
- Shelly physical identity/model/firmware, actual Serial/UART mapping, complete restorable serial configuration including half-duplex/DE options, and affected script content/config/running/autostart states;
- current A1M marker, package/revision/API and read-only health counters using the correct revision map; identify any active external-control session before interruption;
- one connected target and all producers of normal RS485 traffic, including scripts/external pollers;
- expected immutable release BIN path, source commit, byte length and verified SHA256, selected from actual installed identity plus operator flash history.

An active control lease/session, unrelated actuator-critical dependency on the port, ambiguous target, absent binary-safe jsuart access or missing restoration snapshot blocks maintenance entry. Do not issue control commands to make a precondition pass. Wait for operator resolution when necessary.

Prepare an authenticated, session-scoped Mac-to-Shelly transport with one outstanding serial transaction. Encode binary over the network without UTF-8 conversion; handle 0x00–0xFF, split/merged callbacks, partial sends and RX overflow. Buffer locally; do not depend on network round trips per byte. Keep packet buffers small and justified by actual memory/read limits. Do not store the full image in Shelly RAM, logs or KVS. A network retry must retrieve a cached transaction result by session/sequence or fail, never mix bytes across transactions. The reference BIN must not be sent to the Shelly or A1M during readback.

Implement an allowlist at both host and Shelly transaction layers: bootloader discovery and the supported flash-read frame only. Validate whole frames and address ranges; merely filtering first opcode is not sufficient if packet framing is unknown. Response data naturally may contain any byte. No erase/program fallback, repair, checksum fixup or hidden writes.

### B. Coordinated maintenance entry

Finish offline tests and snapshot/rollback preparation before asking the operator to change switches. Pause only identified RS485 consumers, preserving state; do not stop unrelated controls. Put the verified Serial port into supported raw/jsuart mode at 115200 8N1 and confirm applied settings and direction handling. Respect actual Serial-to-UART mapping and hardware DE polarity; do not guess them. If a disruptive Shelly reboot is required, stop for separate review rather than rebooting automatically.

Use two explicit handoff states:
1. `READY_FOR_OPERATOR`: target, reference and snapshots recorded; bounded discovery receiver/loop armed; tell operator the setup is ready.
2. Operator removes A1M power, sets the firmware DIP state and reapplies power, then confirms. Allow for discovery timing by arming before power-on. Do not infer readiness from elapsed time.

Operator-reported normal DIP string is `10000110`, firmware state `00000000` (verify numbering/orientation physically). Record actual original positions; these strings are observations, not universal settings. Never change switches while the adapter is powered. Shelly does not control any supply relay in this package.

Send only validated discovery and record the full received response. Enforce timeouts, finite retries and no unframed background Modbus traffic. No response is not permission to guess new baud rates or destructive commands.

### C. Establish readback and read twice

After the read protocol gate passes, begin with a small documented application-range read. Confirm real data rather than local echo, stale buffer, ACK-only, cached reference data or an error packet. Where the protocol lacks an echoed address/sequence, explicitly document that limitation; enforce session boundaries, bounded reception and small varied-address/overlap checks before bulk reads.

Read only the application range needed for the expected image; do not dump bootloader/reserved flash, option bytes, RAM or EEPROM in this package. For the investigated STM32 build the intended image base is 0x08008000. Determine how that maps to the read protocol from evidence; do not blindly use offset zero or an absolute address. Device-reported maximum write size is not a proven maximum read size.

Perform two complete, independently requested sequential reads of the same range in the same stable boot session, without using the first dump/cache for the second. Save untouched payload bytes to separate local files, with coverage maps, addresses, timestamps, per-transaction status, retries and SHA256. Never fill missing bytes with 0x00, 0xFF or bytes from the reference BIN. Incomplete files remain explicitly partial and must not pass comparison.

Stop on repeated errors, parser ambiguity, unsupported read response, wrong target, conflicting data or buffer overflow. Maximum three supervised hardware attempts before reporting findings. Bounded retries within a known transaction are not permission for unlimited protocol guessing.

### D. Exact comparison

Use the immutable BIN actually expected on the device, not a fresh or latest build chosen by convenience. Verify its recorded hash before comparison. An optional deterministic rebuild is offline and must be reported separately; preserve the original release artifact.

Compare all of the following:
1. read A versus read B, same range, byte-for-byte and SHA256;
2. the complete read application interval versus the pinned release BIN, including its exact length and padding;
3. executable/load-content and padding regions separately for diagnosis only, without weakening the whole-image result.

The existing replacement BIN envelope is 98304 bytes (0x18000), corresponding to 0x08008000–0x0801FFFF on the investigated target. Confirm the selected release's actual size; do not treat this as proof of full chip flash size. A full match requires every byte of the selected envelope, including 0xFF padding, to match. A header or code-prefix match is not a full match.

Report image bounds, both dump hashes, reference hash, mismatch count, first differing file offset and absolute address where known, and bounded contiguous mismatch ranges. Distinguish `MATCH`, `MISMATCH`, `INCOMPLETE_READ`, `UNSTABLE_READ`, `REFERENCE_UNCONFIRMED`, `BLOCKED_READ_PROTOCOL`, `BLOCKED_TRANSPORT` and cleanup status. Do not label a reference mismatch as a corrupt device or repair it. Other known release hashes may be compared offline as additional diagnostics, with the expected-image mismatch retained.

This verifies application content, not full-device backup or ability to restore the bootloader.

### E. Restore and verify normal operation

On completion or failure, stop bootloader transmission and unregister/stop the temporary bridge. Restore and read back the exact saved Shelly Serial/config/script state. Keep normal bus pollers paused until the operator restores the recorded A1M DIP positions and power-cycles back to normal mode. Then resume only the previously active pollers and verify the same A1M identity plus advancing read-only telemetry/error counters. Do not synthesize settings, send SET, or restart the heat pump.

Record restoration as separate from dump success. After interruption, provide a durable local recovery record and exact minimal restore command. Network loss must leave no transmit loop or autostart flasher; the temporary script times out to a silent state. Do not blindly resume Modbus into an unconfirmed bootloader session. If the operator has not yet returned the unit to normal, report `WAITING_FOR_OPERATOR_RESTORE`, not full completion.

## Allowed changes and permissions

Smart Home: this package, `requirements/package-runs/P0075/**`, file index/manifest and a focused function-catalog entry. Existing Procon releases, vendor files, application source and unrelated G2 runtime remain unchanged.

Standalone: new read-only Mac transport/protocol/compare code, Shelly bridge source, tests, focused docs and minimal build/test/ignore integration. Do not alter firmware source, existing immutable releases, repository visibility, public CI secrets or unrelated features. Use existing Mac script deployment conventions: complete generated script with bounded transport chunks, no Shelly source-file fetching.

Live authorized writes are limited to temporary Serial configuration and one identified, non-conflicting maintenance script on the verified Shelly, plus pausing/restoring the identified bus consumers. Do not overwrite unrelated script slots or change Wi-Fi, authentication, cloud, firmware or physical outputs. A1M operations are read-only discovery/flash reads. Ordinary identity/health reads are allowed before/after; no Modbus control-register writes or direct CN105 commands.

Raw dumps, full binary traffic and snapshots stay on the operator's Mac outside tracked paths. Only sanitized summaries/hashes/protocol conclusions enter repositories. Treat read data as potentially proprietary even when replacement firmware is expected. No upload of vendor bytes, credentials, configuration secrets or full device dumps to GitHub or cloud services.

## Required tests and deliverables

Before hardware: tests must cover command allowlist rejection (including erase/program and malformed reads), independent framing/checksum vectors, all 256 byte values, partial sends and split/merged receives, errors/timeouts/local echo/overflow, missing and duplicate blocks, session/sequence replay after network failure, address bounds and wraparound, exact-length comparison, one-byte code and padding differences, incomplete/unstable dumps and restoration after each phase's failure. Simulated read data must not come from the same reference path being compared as if it were physical evidence.

Run focused transport/Shelly mock tests and existing standalone regression/build checks; record exact commands and results in verification.md. Physical success cannot be inferred from these tests.

Deliver local `application-read-1.bin`, `application-read-2.bin`, `capture-manifest.json`, `comparison.json` and restoration snapshot/log (unique session directory; no overwrites), plus sanitized package-run review/design/functions/attempts/findings/CHANGELOG/verification and hardware report. Log protocol evidence separately from interpretations. Update both affected file indexes and relevant platform known-unknowns only when evidence resolves them.

PASS requires verified identity and reference, two complete matching physical reads, exact match to the pinned BIN and restored/read-back normal Shelly/A1M operation. A sound readout with a genuine reference mismatch is a useful diagnostic result, not a match. If only discovery works or a capability/protocol gate blocks extraction, report partial/blocked with concrete evidence; do not claim backup success.

Codex may prepare, test and commit package-scoped software/documentation without another approval. Physical execution pauses at the operator handoffs above. This authorization never extends to programming A1M or modifying heat-pump behavior.
