# P0089 — CN105: complete useful command contracts and installation-setting access

## Order, decision and authorization
Ordered next Codex investigation after P0088. The operator chooses to explore **CN105 further**, keeping Procon on its working connection. Use P0088's atlas and corrected analyses as the starting point; do not repeat the broad scan, restart port attribution, or rewrite completed package evidence. Do not interrupt a running package or share a writable Ghidra project concurrently.

Primary outcome: turn identified CN105 routes into **named, field-level, evidence-backed read/control transactions**, with explicit completion/readback behavior and a prioritized Procon implementation handoff. Progress means a previously unresolved meaning, guard, encoding or transaction edge was resolved, not merely more atlas rows.

Authorized: static firmware analysis, package-local offline codecs/models/tests, replay of already available captures, documentation and commit/push of verified scoped results. **No new device access, live GET/SET, service/session activation, firmware deployment, cable/DIP changes or heating-system actuation in this package.** A qualified physical test is a later handoff, not automatically authorized. No production Procon source, allowlists, BL2/OTA, EFFECT, schedules or device configurations change.

FTC20.01 remains the principal working reference. Do not wait for21.00 to do the analysis. Keep static20.01 conclusions, existing21.00 observations and new physical NOT RUN status separate. Internal addresses are image-specific. Preserve original vendor files/full listings and private logs locally.

## Starting evidence and scope discipline
Follow AGENTS.md/package bootstrap, synchronize before reading current work, and review the current modular Procon implementation read-only. Use the repository index, not a broad dump of unrelated files. Read P0088 CHANGELOG.md, command-catalog.md/json, cn105-new-capabilities.md, cn105-control-fields.md, cn105-fast-fields.md, a3-job-lifecycle.md, settings-d-events.md, settings-transfer-map.md, settings-apply-order.md, settings-store-model.md, firmware-model.md, port-sprint.md, verification.json and their directly needed evidence. Reuse P0086's energy corrections and tests; use P0087 target/controller-boundary findings without restarting its whole regulator analysis. Pin current Procon and public F1p/gekkekoe reference revisions before comparison.

Reuse the isolated repaired M16C language and evidence checks from P0088, not stale decompilation. Verify actual image hash (prior binary: d828c2e18a013a6adea8a191448b5c5f7d52ac17b3bbc1182c977e190b60976a), exact operands, indirect calls and branch conditions. For menu names/ranges use the applicable Geodan manual; public source labels are independent clues, not firmware proof.

Do not reopen CNIT/UART1/UART6/SD investigations except for the **smallest specific dependency** needed to explain a CN105 transaction. D-side events involved in settings are in scope as dependencies; assigning the entire D connector or obtaining its full firmware is not a prerequisite for all other work. A confirmed missing peer behavior is an explicit handoff, not permission to fabricate the event or loop indefinitely in the same FTC code.

## Work order and concrete questions

### 1. Finish ordinary control fields first
Start with SET32 and SET34; then inspect SET33/35 from their actual dispatchers. Produce separate read/write contracts, not a single generic control table.

For SET32, close the remaining p4/operating-request path, all enables and relevant mode/profile admission. Trace requested/accepted/effective heating target, DHW target, zone1/2 modes, temperature range and readback. Preserve P88's finding that a target-only update still consumes the supplied mode byte even when mode-update is disabled. Identify what each accepted value actually requests, what can override it, and how Procon can observe that difference.

For SET34, follow p5..9 requested inhibit bits through consumers into actual GET28 status, rather than equating RAM39A6 with399A. Finish p10 event semantics, p11's repeat-sensitive33EA/39EC/39ED path, p12/39A4 and p13 through3E06/3933/ABE04. **Do not name p13 a power percentage, direct compressor command or capacity limit just because its values look like0..100.** Follow its downstream use and units; say which claim is proved. Clarify any server-control/ownership, link-loss and timer behavior, keeping timer ticks separate from seconds until the timebase is proved.

SET32/34 zero acknowledgments do not consult setter success. For every proposed operation provide the independent readback/observable state needed to distinguish received, admitted, stored, selected and physically effective. Test repeated requests per field; do not generalize p11's non-idempotence to all SETs or assume ordinary retries are universally neutral.

End this batch with a concise Swedish list of newly understood controls and a comparison with today's Procon encoder/decoder. Report actionable mismatches without patching production code. Direct thermal-kW/Hz control is an investigation question, not an assumed feature.

### 2. Map installation settings by function and complete category6 first
P88 enumerated47 settings blocks0x50..0x7E. Preserve all47 in an explicit work ledger with category, import group and known/unknown fields. Prioritize0x65/0x79 pump settings and their **entire affected category6 import set**, then blocks containing pump economy/flow control, thermo-diff/hysteresis/time settings, curve points, DHW settings and energy-monitor inputs. Avoid decoding unrelated blocks before finishing a useful vertical slice.

For each selected field trace GET source, SET enable/mask and payload, validation/defaults, staging aliases, active-RAM import, native consumer, persistence and startup restore. Keep distinct: configured pump level; runtime PWM/reduction; actual flow; power-accounting configuration. Do not rediscover the already traced0770/07E6 persistence chain as a new result.

Write a field-preserving serializer/validator only when **all bytes/blocks affected by applying that category** are qualified. GET and SET layouts can differ. Neither zero-filling unrecognized neighbors nor copying the GET payload verbatim into SET is acceptable. Keep unknown fields visible and block a proposed apply when they may be overwritten. Enumerate device/profile-specific defaults and bounds; no local pump1..5 clamp is not proof upstream validation is absent.

The user-facing deliverable must say what additional CN105 settings could be used and what transaction is still missing for each, not just quote RAM addresses.

### 3. Close the settings-session dependency, or isolate the exact missing peer event
Continue SET C8 read/write direction, action0..3, mask/category, status and end/abort behavior from P86/P88. Preserve the corrections: internal1005 advertises a request; internal1002 participates in start/close; CF978 is a specific accepted D extended tag1/selector0 event, **not an arbitrary CN105 ACK**. Those internal numbers cannot simply be sent as external A3 selectors through the >=700 filter.

Answer explicitly whether a complete sequence is possible using:
(a) CN105 alone;
(b) CN105 while the installed normal screen/peer completes its native handshake;
(c) an additional peer action for which we lack evidence.
Compare documented code gates and all relevant already enumerated CN105 families before concluding a peer action is unavoidable. Do not propose injecting D traffic or bypassing gates in this package. If the peer generator is outside the image, identify the minimum native transaction capture or missing firmware that resolves the exact edge, and continue other CN105 work.

Produce an event/state contract for read-and-close without apply, and a separate write/apply contract with readback/persistence verification. Include timeout, disconnect, restart, session ownership and partial-apply outcomes. **P88 shows action1 can import before final peer completion; timeout or reset-to-idle is not rollback.** Preserve this invariant in every model, serializer and test. A fake peer event may test a conditional branch but does not qualify a CN105-only operational sequence.

First future settings test remains read/close; a later one-unit, one-mode5->4->5 trial requires full affected-block preservation and qualified recovery. Neither trial is executed here. Do not block unrelated static findings merely because physical recovery is not yet demonstrated.

### 4. Improve useful reading: direct GET, parameterized families and A3
Use the P88 byte-source maps instead of repeating the known GET survey. Prioritize previously unnamed flags, invalid/stale markers, source update cadence and helper rounding in GET04/07/0B/0C/14/15/26/28 and settings readback. Distinguish a sampled companion byte from an established validity flag; high-byte/low-byte power and flow must preserve the full proven encoding and known truncation/wrap.

Inspect the recognized nonordinary families by **frame type plus opcode**, including5B/C9,5C/CC,5D/CC and qualified02 descriptors. Explain actual content, accepted parameter predicates and side effects, or record a precise residual. A constant response is not proof that a request has no effect. Find missed parameterized/session-dependent read paths without guessing parameter meanings from response positions. Current API600 zero-parameter GET cannot automatically send every family.

For A3, combine P88's local/forwarded lifecycle with the current Procon arbiter: pending format0, cached results, refresh/rearm, completion ownership, cancellation on other commands, native retries versus host polls, and typed formats1/2/3/4/6/7. A wider format decoder is not a new physical capability. Preserve the effectful/unsafe selector classification and an explicit independent scope for maintenance actions.

A3 energy520..531 stays research-only: P86/P88's odd BCD truncation, non-atomic pairs, forced accounting folds and remainder loss are mandatory regression facts. Do not enable frequent polling or high-low-high retries;532 and340 stay excluded from read-oriented tooling. Determine whether an already accepted **side-effect-free** direct or alternative CN105 read could expose the same required information before proposing more effectful polls. Absence of a found alternative remains bounded, not a universal impossibility claim.

## Evidence, artifacts and tool behavior
Deliver a machine-readable CN105 command/field contract and a generated Swedish report. Retain stable P88 row IDs and distinguish genuinely new findings from renamed/reformatted prior facts. Each field/action has frame type/opcode/selector, zone/category, payload positions, enable predicates, endian/scale/range/sentinels, source/consumer, side effects/retry semantics, readback, scope/version, proof addresses and exact remaining edge. Separate static effect known, offline codec ready, physical-test ready and physically verified.

Implement package-local offline decoders/encoders, state observers and preservation checks under tools/ftc6/p89/. Default execution is fixture replay or packet planning with **zero network/serial access**. Unknown operations/transitions must fail explicitly; never output guessed bytes as a ready live recipe. Preserve cached/stale/cancelled outcomes distinctly from valid fresh data. Use the current corrected language and exact P88 revisions; isolate any necessary decoder correction with positive/negative opcode tests.

Required reports under requirements/package-runs/P0089/: review.md, design.md, functions.md, provenance.md, control-contracts.md, settings-fields.md, settings-session.md, read-service-contracts.md, cn105-contracts.json, new-capabilities.md, procon-handoff.md, physical-test-plan.md, coverage.json, open-questions.md, reproduce.md, verification.json and CHANGELOG.md. Add concise per-family reports only when useful. procon-handoff.md must identify required module/API changes and measured current slot constraints without making production edits or using obsolete layout assumptions.

The physical handoff must be staged and finite: qualified non-mutating observation first; settings read/close only once its peer dependencies are understood; a setting change only with complete preservation/restore. Include expected evidence, stop conditions, actual state recovery and undecidable outcomes. Unknown peer action or missing instrumentation is reported, not treated as success. No hardware access is necessary to publish useful offline contracts.

## Acceptance and progress discipline
1. Review identifies exact P88 unresolved rows/fields chosen for the first batch; all other CN105 items remain visible in the backlog. Each work batch ends with the field/guard/sequence edges actually closed. Do not spend an entire run retrying a proved absent peer implementation.
2. SET tests exercise enabled/disabled/invalid values, mode-context requirements, zone routing, native admission, event-versus-assignment, repeat-sensitive counters, saturation/wrap and ACK-without-application. Missing downstream meanings stay explicit.
3. Settings tests preserve all affected neighbors/defaults, category masks versus numbers, read-state transitions, partial apply before final acknowledgment, persistence failure and non-rollback on timeout. A model with injected internal events is not a completed protocol emulator.
4. Read/A3 tests cover whole frame/length/checksum, correct type/opcode, byte order, sentinel/freshness, pending/cache/rearm/cancellation, duplicate effects, and P86 energy regressions. No codec or fixture runner opens a transport or alters an allowlist.
5. Every claimed new field has instruction/data-flow proof and reproducible evidence. Targeted extractions repeat; table boundaries, wrong image and missing evidence have negative tests. Existing21.00 captures are separate corroboration, not new experiments. New21.00 firmware is not a generic gate.
6. Report independent structural coverage, semantic field closure, transaction completeness and physical NOT RUN. Count meaningful newly qualified functions/fields, not table slots as features. A complete contract requires all prerequisites and effects within its explicitly bounded operation, not recovery of the whole FTC program. Honest partial results include the smallest remaining dependency.
7. Verify schema/report consistency, available regression suites, dependency pins, git diff --check and index consistency. Report public-fixture versus private-image tests honestly; no placeholder PASS results. Keep P86/P87/P88 outputs, current firmware and deployed behavior unchanged.

Permitted changes: new P89 tools/tests/reports, this package, narrowly required function-catalog/knowhow entries and repository index/bootstrap bookkeeping. Shared analysis helpers may change only with an explicit compatibility review; do not alter a running analysis environment or unrelated source. Reassess current main before commit and preserve concurrent work. Commit/push verified package-scoped results only; no production activation. Final summary leads with **what Procon could newly read/control on CN105**, what is executable offline, and the precise remaining transaction or physical-verification step.
