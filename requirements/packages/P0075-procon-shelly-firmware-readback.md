# P0075 — Procon firmware readback through Shelly and exact build comparison

## Status
Partial readback research and the later explicitly authorized write-reference and pure opcode survey are complete on 2026-10-07. Readback remains `BLOCKED_READ_PROTOCOL`: no application bytes or backup were extracted. The full single-byte `00..FF` sweep produced responses only for `50`, `51`, `53` and `5A`; see `opcode-sweep-results.md`. The maintenance script is verified stopped/disabled. Physical restoration remains deferred by the operator until evening: `WAITING_FOR_OPERATOR_RESTORE`.

The original read-only restrictions below are the default baseline. The dated operator amendments take precedence for their distinct bounded experiments; no general updater, further experiment or heat-pump control is authorized by their completion.

## Operator amendments — 2026-10-07

The operator subsequently authorized bounded trial-and-error 0x57 request variants, one hypothesis at a time with raw responses retained locally. Later instructions explicitly authorized zero-completion probes, discovery between hypotheses instead of a physical reset each time, 10–20 ranked variants, then one hour of independent research. These amendments supersede the original proven-contract-only gate and three-attempt limit for this bounded research session. They do not authorize opcode sweeps, erase/program/EEPROM, uncontrolled frame permutations, or claims that unknown address/length semantics are validated. Discovery/transport qualification comes first; invalid discovery or unexpected read data stops the series. Valid discovery proves responsiveness, not full parser reset. Bulk application reads remain gated on validated semantics and bounds. The original conservative requirements below remain the default for future sessions unless separately amended.

The operator confirmed Shelly is the sole RS485 master and normal DIP10000110, and separately approved supervised Shelly reboots for the raw-UART transition. Existing physical handoff, restoration and no-heat-pump-reboot constraints remain. See package-run attempts for current state.

## Later write-reference authorization — 2026-10-07

The operator explicitly requested learning write behavior before returning to0x57. This supersedes earlier read-only prohibitions only for the bounded reference experiment in package-run write-reference-design.md: three fixed0x53 frames at application-relative0x17000 with eight FF bytes (one correct-format attempt, two negative controls), selected fragmentation of a negative control, and0x50 cached-ACK comparison. No erase, EEPROM, arbitrary programming, application-code overwrite or heat-pump control is included. The correct-format attempt may affect hidden ECC; it is not declared a physical no-op. No automatic retry/erase to force success. A later fixed0x57/0x50 comparison contains no write command. Current outcomes and restoration state are in write-reference-results.md; earlier reports are dated observations.

## Later full opcode mapping authorization — 2026-10-07

The operator then requested a scan from00throughFF and answered Ja to the explicit warning that unknown single-byte commands may erase firmware or alter persistent state, with recovery not guaranteed. This further expands only this experimental session. The final clarified method sends exactly one opcode byte per trial, ascending00..FF, without parameters and without interleaved discovery/last-ACK commands. Each probe has a3second observation window; record whether bytes arrived within1700ms. No fabricated packet parameters, payloads or automatic programming/erase sequence is added. Known command numbers are included as single-byte trials under the explicit risk acceptance.

Stop on partial send, overflow128bytes, unsolicited/late/ongoing receive, unhealthy Shelly, uncertain RPC or identity/config drift. No claim of Procon liveness can be inferred for silent probes because the operator requested no helper traffic. No response means only no received byte within this method/window, not absence of a handler or side effects. A standalone41 example was performed before the operator clarified it was illustrative; keep that observation separate from the full-range scan. Physical normal-mode restoration remains the operator's evening handoff.

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

### Established Windows updater protocol facts — do not re-derive

The following host-side protocol facts have already been statically audited from the lawfully held Windows updater and are durable input to P0075. Codex must use these as established evidence and **must not spend package time re-deriving them from the DLL** unless a later repository artifact contradicts them or implementation testing exposes an inconsistency. The detailed technical reference is `marlov1974/procon-melcobems-mini-a1m/docs/hardware-reference/boot-update.md`; P0075 owns the execution constraints, while that document owns the byte-level protocol description.

Serial transport used by the Windows updater is **115200 baud, 8 data bits, no parity, 1 stop bit, no handshake**. No host-side baud negotiation or auto-baud was found.

The active discovery request is exactly one byte:

```text
5A
```

The expected discovery reply is exactly 12 bytes:

```text
7A | max_flash LE32 | max_eeprom LE16 | erase_block LE16 | max_write_page LE16 | checksum8
```

where `checksum8` is the sum of bytes 0 through 10 modulo 256. The reported `max_write_page` is what the Windows writer uses as its normal write payload size. In the observed hardware/UI case that value is 8192 bytes. This value does **not** establish a read size.

The active flash-erase request is:

```text
51 | offset LE32 | byte_count LE32 | checksum8
```

Total transmitted length is 10 bytes. The Windows updater uses offset zero and the selected BIN file length. `checksum8` is the sum of all preceding bytes modulo 256. Defined/observed acknowledgement values are `71` for success and `70` for failure. P0075 must never transmit this command.

The active flash-write request is exactly:

```text
53 | data_length LE16 | offset LE32 | data[N] | CRC32 LE32 | checksum8
```

Byte layout:

```text
offset  size       meaning
0       1          0x53 WRITE_FLASH
1       2          N, payload length, little-endian
3       4          file-relative update offset, little-endian
7       N          firmware payload
7+N     4          CRC32, little-endian
11+N    1          additive checksum8
```

Total packet length is `N + 12`. The CRC32 is the standard reflected CRC-32/ISO-HDLC form: polynomial `0xEDB88320`, internal initial state `0xFFFFFFFF`, final XOR `0xFFFFFFFF`; check value for ASCII `123456789` is `0xCBF43926`. CRC covers the write header plus payload, from byte 0 through byte `N+6`, and excludes the trailing CRC field and final checksum. The CRC value is serialized least-significant byte first. The final `checksum8` is calculated after the CRC is appended and equals the sum of bytes 0 through `N+10` modulo 256.

The Windows updater loads `device_MaxWritePageSize` from discovery, uses that as N for ordinary blocks, caps the final block to remaining bytes, and advances offset only after a successful acknowledgement. This explains observed 8192-byte progress increments for a 98304-byte image. The format explicitly carries both length and offset; therefore 8192 is not implicit in the wire format. A shorter final write is represented by a smaller N. This proves variable encoded write length on the host side, but does not prove that arbitrary shorter aligned/un-aligned writes are accepted by every bootloader revision.

Defined/observed write acknowledgements are:

```text
73 = write success
72 = write failure / retry condition
```

If the normal write acknowledgement is missing, the active Windows flow can send a single-byte `50` query and then interpret the reply as the outstanding write acknowledgement. `50` is not a flash-read command and must not be confused with the unused `READ_STATUS = A0` definition.

The Windows updater does **not** read existing firmware before erase, does not perform post-write flash readback comparison, and does not save device firmware to a file. Its local `FileStream.Read` reads the selected BIN from the PC filesystem.

The DLL defines, but the inspected active GUI flow does not call:

```text
55 = WRITE_EEPROM_REQ       75 = OK   74 = NG
57 = READ_FROM_FLASH_REQ    77 = OK   76 = NG
59 = READ_FROM_EEPROM_REQ   79 = OK   78 = NG
A0 = READ_STATUS            B0 = ACK
```

These enum constants establish command identities only. They do **not** establish the frame format for `57` or `59`, the response layout, address/count widths, checksum/CRC coverage, segmentation, alignment, maximum read size, absolute versus application-relative addressing, or whether the connected resident bootloader implements those operations. The unused `bufferCRC32Check` routine is not a correctness oracle and must not be used to infer the missing read-response format.

For P0075, the unresolved research starts specifically at the `57` request/response contract. Codex should not redo discovery/erase/write reverse engineering unless evidence conflicts; it should use the established write-family structure only as a hypothesis generator, never as proof that `57` is `57 | length | offset | ...`.

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

### A1. Bounded chunks and heap qualification — operator follow-up

Operator screenshot, 2026-10-07: the Windows writer progresses in 8192-byte increments for a 98304-byte image. The inspected host IL loads `device_MaxWritePageSize` (method-relative IL 0x433), caps the last block at bytes remaining (0x49B–0x4A3), and encodes the selected length in the write request (0x4B2–0x4C1). This is evidence of the host's selected write block, not proof of minimum write size, erase granularity, read length or support for arbitrary shorter transactions. P0075 remains read-only.

Distinguish three sizes explicitly in design and diagnostics: the complete bootloader response/transaction; the UART driver/callback buffers; and the Mac–Shelly network payload. Reducing network chunks alone does not reduce a pending 8192-byte device response. Do not infer a maximum read size from `device_MaxWritePageSize` or import a Script.PutCode upload limit as a UART limit.

After the read-format gate passes, prefer individually requested small reads: initially 256 or 512 payload bytes where the protocol demonstrably supports them; 512 bytes is the design target, not a presumed accepted command length. Default network payload should not exceed 1024 raw bytes. A 2048-raw-byte chunk is the upper design limit for this package, not a guaranteed safe heap size; enable it only after supported read lengths/alignment and measured memory margins are established. Choose a smaller supported size when needed. Never automatically fall back to 8192-byte buffering or increase a request length after an error.

For the normal small-read path, retain at most one bounded response awaiting host acknowledgement. The Mac must receive, validate and durably record that response before the next read is requested. Use the existing session/sequence result cache for retries without accumulating previous blocks. Do not retain a whole image, grow an unbounded receive string, convert whole blocks into numeric JavaScript arrays or log binary contents. Incremental parsing/checksum state and all temporary copies must have explicit bounds.

Budget actual peak memory, not raw payload alone: UART/runtime buffers, raw strings, base64, JSON serialization, response/cache copies, network buffers, callbacks and authentication overhead can coexist. P0012/P0013 documented out-of-memory from large Shelly HTTP/JSON payloads; the current Mac script uploader uses 1500-byte chunks for its own distinct transport. With base64, 1024 raw bytes become 1368 characters and 2048 become 2732, before metadata. Shelly HTTPServer documents a 3072-byte total incoming-request limit including headers; apply that limit only in its actual direction and count authentication/JSON overhead. It is not evidence of a 3072-byte response limit or of a UART buffer size. Check the actual API/firmware used.

If the device only supports a larger uninterrupted read response, stop the default path with `BLOCKED_TRANSPORT_MEMORY`. A streaming design is acceptable only after documenting bounded driver/script queues, incremental frame validation, byte ordering, sustainable draining, network-stall behavior and loss detection. At 115200 8N1, 8192 data bytes take about 0.711 s and a 2048-byte buffer alone covers about 0.178 s of undrained data (excluding protocol overhead). Splitting HTTP messages or pausing Mac requests cannot stop an already-started UART reply without verified device-side flow control. Do not treat average Wi-Fi throughput as a worst-case guarantee. On overflow or connection loss, mark the transaction/read incomplete; never discard bytes silently or commit partial data as a valid block.

Add offline tests for at least 1000 repeated bounded transactions, all byte values, delayed host acknowledgements, lost network replies, split/coalesced UART callbacks, an unexpected 8192-byte response and recovery without queue growth. Before and during both physical dumps record Script.GetStatus `mem_used`, `mem_peak`, `mem_free` and errors where available, plus system free RAM and queue high-water marks. Script `mem_free` is a shared JS pool, not private free memory. The design must state an explicit justified memory budget/reserve and abort thresholds; stop on low reserve, sustained memory growth or RX overflow. Do not raise limits to hide a failure. Fixed small chunks are the baseline; throughput optimization is not an acceptance criterion.

References: existing `memory/knowhow/shelly.md`, `src/mac/tools/shelly_live/core.py`, `procon/analysis/updater-il.txt`, and official Shelly Script/HTTPServer/UART documentation. This follow-up changes only this existing package definition; no tracked paths, file index, bootstrap manifest, live device settings or application firmware change in this amendment.

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
