# Procon readback research functions

Last changed: P0075, 2026-10-07. Implementations live only in `marlov1974/procon-melcobems-mini-a1m`; Smart Home coordinates the site experiment.

| Function / component | Contract and effects | Verification |
|---|---|---|
| `decode_discovery`, `allow_frame`, `read_request` | Validate exact discovery and checksum. Standard read builder stays blocked until the contract is proven. No network side effects. | Independent vectors, malformed/forbidden commands |
| `BoundedReceiver`, `Capture`, `compare` | Bound receive storage; durable contiguous capture; two complete capture manifests versus a pinned exact-length reference, including padding. Missing bytes are never synthesized. | Binary/split/overflow, gaps/replays, incomplete/unstable/mismatched images |
| `makeReadbackCore` and HTTP adapter | Discovery-only, authenticated sequence/cache/ACK, bounded reply and expiry, no autonomous discovery. UART mapping must be separately qualified. | 1000 mock transactions, adapter auth/base64/deadline |
| `variant_series.js` | Fixed compiled catalog indices, initial/interleaved discovery, one use per candidate, bounded response and stop on unexpected data. No arbitrary HTTP payload. | Sequence/replay, partial-send abort, overflow, malformed discovery and controls |
| `experimental_probe.validate_catalog`, `encode_read` | Independently re-encode metadata and check the reviewed address/count/layout/trailer vocabulary, with at most 16 frames and 64 transmitted bytes per frame. Unproven hypotheses remain labelled as such. | Golden/catalog checks and negative tests |
| `experimental_probe.run` | Validate saved target identity/config/own slot, upload/read back exact source, persist private records outside Git, supervise memory, verify stop after errors/success. Does not create slots, configure Serial, reboot or restore physical state. | Injected fake RPC, preflight refusal, bad source, RX/sequence errors, cleanup failure |
| `qualify_uart` | Experimental no-TX handle check with original snapshot; mode changes may require an operator-approved reboot. Cleanup never deletes; it stops/disables the slot and preserves the primary error. Deletion caused restarts even after a prior reboot. | Failure-injected restore tests; hardware anomaly remains unresolved |

These are research tools, not an updater or a working firmware reader. P0075 remains blocked on the device's read request/reply contract. Normal communication was restored and verified after the earlier read-only phase; later write-reference and opcode experiments have their own authorization and physical handoff. See [package findings](../../requirements/package-runs/P0075/findings.md) and the dated experiment reports for those separate states.

## Later P0075 write-reference functions

`makeWriteReferenceCore` accepts three fixed `0x53` frames, discovery and last-ACK. Each initialized instance permits at most one correctly formatted write frame, 16 transactions and 32 received bytes. It caches repeated sequences and supports splitting negative controls at byte 7 or 19 with defined gaps. Early reception prevents transmission of the remaining fragment. The site runner additionally prevented a second correctly formatted attempt across adapter instances. Its 46 offline cases pass. There is no erase operation or arbitrary payload interface.

`makeReadAckReferenceCore` has five fixed offline-tested candidates: three `0x57` forms, single-byte `0x59` and single-byte `0xA0`. It also permits discovery (`0x5A`) and a gated last-ACK check (`0x50`), with a limit of 12 transactions and 128 received bytes. Any candidate response is retained as unvalidated data and stops further transmission. A cached ACK is not proof of a successful read. The current suite passes **34 offline cases**.

Only the three `0x57` candidates were exercised live in the read/ACK phase before the opcode survey. Adding `0x59` and `0xA0` to offline tests does not establish a live paired-read experiment, EEPROM readout or status support. Both reference adapters arm passively with private credentials and separately qualified UART 0. Their earlier live accounting and physical handoff are in [write-reference results](../../requirements/package-runs/P0075/write-reference-results.md).

## Pure opcode survey and offline aggregation

The later `00..FF` survey has explicit user acceptance of possible erase or persistent effects and uncertain recovery. It is not covered by the earlier read-only scope. Its request is exactly one opcode byte per trial, without parameters or intervening discovery/last-ACK traffic.

| Function / component | Contract and effects | Verification |
|---|---|---|
| `makeOpcodeSweepCore` | Authenticated, ascending opcodes 0–255 with `seq = opcode + 1`; exactly one UART byte per new probe. Duplicate current requests return cached state. No startup or helper transmissions. A 3,000 ms window stores at most 128 bytes and records first reception and bytes received by 1,700 ms. Late/active reception, overflow, short sends, expiry and invalid clocks halt. | 12 offline cases, including exactly 256 ordered byte transmissions; ordering, replay, authorization, limits, timers and passive adapter |
| Private survey host | Verify target/configuration/owned slot and uploaded source; record intent and result separately; check memory every 16 opcodes; stop and disable the owned script after completion or failure. No automatic resume or script deletion. | Recorded host gates and core tests; physical outcomes belong to the live report |
| `summarize_opcode_sweep.summarize` | Offline validation of one-byte intents, sequence/coverage, base64/count bounds, callback timing, the 1,700 ms field and stopped/partial states. Reads only opcode intent/result files. Produces sanitized per-opcode records and `COMPLETE`, `PARTIAL`, `STOPPED` or `INVALID`; never treats a running prefix as a full survey. | Five offline tests: complete and partial fixtures, gap/wrong sequence/overflow, boundary and stop handling, privacy and input preservation |
| `summarize_opcode_sweep.write_summary` | Create a new output exclusively with mode `0600`; refuse overwrite and never change input files. Publish only one-byte reply hex; withhold longer payloads except decoded numeric fields from valid discovery. No device calls. | Exclusive-output and unchanged-input tests in the same five-case suite |

The aggregator reports host enum labels as documented definitions, not evidence that the device implements them. It cannot prove that old capture files were never overwritten, that a silent opcode is unsupported, that persistent state is unchanged, or that normal operation has been restored. Callback timing is not wire timing. See [opcode survey design](../../requirements/package-runs/P0075/opcode-sweep-design.md) for the complete contract and physical handoff.

## Delayed discovery comparison

`makeDelayProbeCore(io)` (P0075) isolates standalone discovery from the separately sent pairs `40 → 5A` and `57 → 5A`. `begin(prefixIndex, gap)` permits only the two compiled prefixes or baseline, integer gaps 0–5000 ms, at most 100 transactions, and one outstanding transaction. `receive` retains at most 128 bytes/callback records; pre-tail RX suppresses the pending tail, while unsolicited/late/overflow/invalid RX or send/clock errors halt. `result` exposes actual send-call timestamps and RX timing relative to both sends. `stop` invalidates scheduled callbacks. Native adapter functions `probe`, `result` and `stopProbe` add base64 encoding for the private host management RPC path; no HTTP arbitrary-byte endpoint or transmit-on-load behavior. Twenty offline cases cover the contract, timer drift, stale callback cancellation and passive keepalive.

The private host validates the pinned bridge and raw profile, records intents/results once without retries, requires a complete matching discovery before every prefix trial, and observes three seconds after each actual tail. It alternates prefix order, permits an initial 40 prefix trials and a documented refinement up to 60 total to address observed timing jitter, supervises memory, and verifies own-script stop/disable at the end. These are timing experiments, not proof of command implementation or wire timing. See the P0075 delay-probe design/results for the current evidence and physical handoff.
