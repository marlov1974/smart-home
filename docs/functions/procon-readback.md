# Procon readback research functions

Last changed: P0075, 2026-10-07. Implementations live only in `marlov1974/procon-melcobems-mini-a1m`; Smart Home coordinates the site experiment.

| Function / component | Contract and effects | Verification |
|---|---|---|
| `decode_discovery`, `allow_frame`, `read_request` | Validate exact discovery and checksum. Standard read builder stays blocked until the contract is proven. No network side effects. | Independent vectors, malformed/forbidden commands |
| `BoundedReceiver`, `Capture`, `compare` | Bound receive storage; durable contiguous capture; two complete capture manifests versus a pinned exact-length reference, including padding. Missing bytes are never synthesized. | Binary/split/overflow, gaps/replays, incomplete/unstable/mismatched images |
| `makeReadbackCore` and HTTP adapter | Discovery-only, authenticated sequence/cache/ACK, bounded reply and expiry, no autonomous discovery. UART mapping must be separately qualified. | 1000 mock transactions, adapter auth/base64/deadline |
| `variant_series.js` | Fixed compiled catalog indices, initial/interleaved discovery, one use per candidate, bounded response and stop on unexpected data. No arbitrary HTTP payload. | Sequence/replay, partial-send abort, overflow, malformed discovery and controls |
| `experimental_probe.validate_catalog`, `encode_read` | Independently re-encode metadata and check reviewed address/count/layout/trailer vocabulary and maximum16 frames/64 TX bytes. Unproven hypotheses remain labelled as such. | Golden/catalog checks and negative tests |
| `experimental_probe.run` | Validate saved target identity/config/own slot, upload/read back exact source, persist private records outside Git, supervise memory, verify stop after errors/success. Does not create slots, configure Serial, reboot or restore physical state. | Injected fake RPC, preflight refusal, bad source, RX/sequence errors, cleanup failure |
| `qualify_uart` | Experimental no-TX handle check with original snapshot; mode changes may require an operator-approved reboot. Cleanup never deletes; it stops/disables the slot and preserves the primary error. Deletion caused restarts even after a prior reboot. | Failure-injected restore tests; hardware anomaly remains unresolved |

These are research tools, not an updater or a working firmware reader. P0075 remains blocked on the device's read request/reply contract ; normal communication was subsequently restored and verified. Exact current limits and handoff are in [package findings](../../requirements/package-runs/P0075/findings.md).
