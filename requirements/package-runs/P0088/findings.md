# P88 findings — qualified checkpoint

**UART6 is a newly identified eight-room reporting/control path; UART0 is strongly consistent with an SD/storage controller. Keep Procon on CN105 for now.** CNIT has not been shown to be a more complete control port.

New concrete results:

- UART6 usesFC/04/03 with48..4C and5A, distinct fromCN105. Eight temperature channels, target routing, shared DHW-boost and holiday setters explain a strong CNRF/receiver role. Field offsets, invalid markers and clamping are documented and tested offline.
- UART0 reads/writes16 named settings files and dated log files, receiving512-byte blocks. The user's SD-reader suggestion is consistent with both code and the manual's CN108/LED4 description. A file-service bridge remains an alternative until wiring is traced.
- CN105 GET1E data bytes1..14 andGET1F bytes1..12 explicitly call a helper returningzero in20.01. They are not waiting for brine data in these handlers. Installed21.00 remains separately qualified.
- CN105 has5B/C9,5C/CC,5D/CC and02 families beyond the ordinary zero-parameterGET scan. Settings-session routes remain real but incompletely operational;FF did not establish absent pump settings.
- UART1 has four additional diagnostic snapshot forms (100/66/62/13-byte replies), not merely raw memory/log access. A pure offline decoder exposes selected raw sensor/target/flow fields.
- The source/underboard hypothesis now has a bound receive chain: P9.3 → six-byte service packet → 38A1/38A3/38A4 → shared service consumer. Its low-five-bit type is1D. CN3C remains a physical inference. P87's P6.3/UART0 register labels are corrected here.

Additional closed edges in this continuation:

- 37 outgoing source descriptors expose249 bitfields. The target/feedback packet includes selected target and feedback at0.5C resolution, return at1C resolution, and a nonlinear flow encoding. This constrains future control-model work without claiming that this profile is active on the installed unit.
- Forwarded A3 requests use a cached asynchronous result. Pending polls and native downstream retries are different. The full result consumer accepts class1 responses without an outstanding-selector comparison; unrelated command ownership changes can cancel the native service queue. See a3-job-lifecycle.md.
- The D/settings handshake now has a pending-request announcement (internal1005) and an extended selector-zero end event. The peer generator and full operational transaction remain unclosed; these are not ready-to-send CN105 sequences.
- 43 further exports agree across two independent working copies (19 routines,23 outgoing switch branches and the bounded A3 completion CFG). The artifact ledger now has2373 entries; those are not2373 independently identified features.

The primary **complete field-level atlas is not finished**. The generated ledger covers all six bounded descriptor tables, both256-entry CN105 lookups,26 class intervals,110 explicit local-service equality branches and five switch tables, with defaults and aliases. Most raw payload bytes still lack fully qualified native semantics. `coverage.json` separates this from physical and semantic coverage, using no invented total-feature denominator. `function-matrix.md` includes the manual-derived parity backlog.

Validation: synthetic boundary/error tests, P86 regression checks, two fresh targeted extractions and schema/human-ledger checks are recorded in verification.json. These do not simulate the entire FTC or qualify live compatibility. No new device connection, read, write, cable/DIP change, firmware deployment or production code change occurred. P87 remains paused; P86/P87 published outputs are preserved.
