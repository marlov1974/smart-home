# P0088 FTC6 offline command atlas

Scope: supplied20.01, hash-gated static analysis. No production firmware changes, hardware IO or deployment. Overall semantic status is PARTIAL.

| Function/tool | Inputs → output | Effects and limits | Tests |
|---|---|---|---|
| `extract.Image` / `extract` | Exact binary → bounded descriptors, lookups, class intervals, switches | Rejects identity/bounds/pointer errors; structural coverage only | Wrong image, invalid table, bounds, CN105 anchors |
| `atlas.build` / `write` | Image, private operand catalog, reviewed annotations → JSON/CSV/ledger/coverage | Local report writes; unresolved semantics retained | Missing operands, deterministic rows, schema, switch aliases |
| `matrix.render` | Manual inventory + reviewed function routes → human matrix | Local report writes; explicit parity backlog | Artifact review |
| `uart6` codec | Pure payload/frame → fields and checksums | Selected room/target/control envelopes, not whole endpoint | All-byte field bounds, frame corruption |
| `uart1_snapshot.decode` | Diagnostic snapshot → selected raw fields | No memory access; does not infer unproved units | Lengths and field anchors |
| `addressing.bit_address` | Base/index → byte address and bit | Architecture-correct offline indexed-bit calculation | Boundaries and known decoder regression |
| `source_result.decode` | Six-byte result → selector/format/raw value | Validates type/checksum; no scheduler acceptance claim | Selector/format limits, length/type/checksum corruption |
| `source_tx.descriptors` / `call_sites` | Image + private listing →37 templates and249 fields | Bounded region and contiguous caller qualification | Counts, missing/noncontiguous caller rejection |
| `source_tx.pack_logical` | Descriptor + supplied callback/memory values → logical bytes | No callback execution, symbols, GPIO or transport | Known fixture, masked fields, checksums, missing inputs |
| `settings_peer.advertisement` / `control_response` | State/direction/category + image → response tuple | Partial internal protocol model, no external transaction claim | State/mask bounds, response action matrix |
| `settings_transfer.ranges` / `resolve` / `extended_fields` / `admitted` | Image, selector and explicit gate state → staging map and local admission |33 ranges,742 selectors; aliases preserved; no packet sender | All selectors, range corruption, direction/role/kind boundaries |
| `verify_artifacts.verify` | Public report directory → consistency result | Read-only local files; no private firmware needed | JSON/CSV/ledger equivalence, corrupted ledger |
| `P88SourceSwitch` | Private Ghidra project → bounded RX/TX branch listings | Research project only; no device IO | Two independent targeted exports |
| `P88A3Completion` | SHA-pinned binary + private project → bounded A3 or settings-clock CFG | Whitelisted ranges, byte validation, no-escape traversal; original default retained | A3 regression and two identical31-instruction clock exports |
| `settings_store` | Desired/shadow images, readbacks and retry count → dirty word and verification outcome | Pure offline model; fault-accounted shadow is separate from persistence | Word pairing, two-read disagreement, third failure, bounds and raw pump bytes |

See `requirements/package-runs/P0088/reproduce.md`, `verification.json` and `unresolved-handlers.md`. The pending A3 job and the cached result are separate; production callers must retain selector validation and distinguish status polling from failed communication. This research does not change Procon's current retry policy.

Readable reconstruction entry point: [firmware model](../../requirements/package-runs/P0088/firmware-model.md), with linked module contracts and named pseudocode.

`pump_control.selected_level` reconstructs AF400/AF452 raw selection and bounded reduction. `accounting_allowance` reconstructs CE2A4 override/table/cap/enable logic. Both are pure offline functions. Tests cover mode exclusions, all reduction byte values, table boundary21/22, all level bytes, disable/cap behavior, and SHA-pinned ROM table/vector anchors. See P0088/pump-consumers-and-timing.md.

P0088 additions: `pump_control.reduction_code`, `reduction_allowed` and `sample_average` preserve native state encoding, signed16 thresholds and empty-window retention. `patch_bit_decoder.patch` validates source hash/anchors, creates a separate language variant and refuses existing output; `P88BitProof` exercises468 memory-effect cases. See reduction-and-energy-chain.md and decoder-bit-repair.md.

`pump_control.reduction_active` models the record30 phase/configuration gate (0939 nonzero, phase8). Exhaustive byte/phase tests and private ROM descriptor/callback anchors verify the finite contract. See P0088/reduction-activation.md for initialization, resets and input ownership.

P0088 gate provenance continuation: `pump_control.reduction_source_class` models C61F6's raw3A4F class; `reduction_aux_inhibit` models91A70's0A45 before overlays. Both are pure, byte-validated helpers. See reduction-activation.md for persistent07DF/07EE default/storage provenance and the unresolved B4674 candidate-output ABI.

P0088 command-level navigation: `tools/ftc6/p88/port_matrix.py` builds/renders a public-input port matrix with explicit route/template/range counting and raw-store deduplication. Read `requirements/package-runs/P0088/port-sprint.md` before selecting deeper work. Raw translations are conditional on history, not unconditional wire command handlers.
