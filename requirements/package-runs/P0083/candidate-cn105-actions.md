# P0083 candidate actions — none executed

All candidates concern the qualified 20.01 image; installed FTC21.00 may differ. See the address-level traces and provenance before implementation.

| Candidate | Evidence and next step | Status |
|---|---|---|
| GET 15 pump status/PWM | Existing P81 captures and A5BF8 agree: payload 1 status, 2 PWM, 3 separate flow-related value. Compare an already authorized operating transition against the display; do not infer hydraulic flow direction from PWM. | Strong candidate |
| GET 65 / 79 settings | A7D48 payload 10 reads 0770; A8BCC payload 7 reads 07E6, both behind CFB18. P81 gate FF means unavailable in that session, not step zero. First finish offline gate/session tracing. | PARTIAL |
| GET/A3 selectors 520–531 | 8C0B4 → CE0D2 exposes six running counters as paired BCD values. Even/odd halves must be combined and checked for consistency. Consumed/delivered paths fold pending accounting into RAM; these are not immutable reads. First qualify semantics on the installed revision. | PARTIAL, no live recommendation yet |
| GET 07 / A1 / A2 | Already captured. GET07 running quantity and dated A1/A2 snapshots have different source banks. Preserve dates, units and independent timestamps. | Existing read paths |
| SET 65 / 79 | Lookup reaches internal IDs 1A/2E; complete field, gate, range and persistence semantics not established. | Do not construct a write packet from this result |

Exclude service **340 and 532** from read-only tests. 532 snapshots and clears running energy banks. No new physical tests, device connection or actuator changes were performed. Any later supervised test needs a separate scope and authorization; this package is complete at an explicitly partial research level.
