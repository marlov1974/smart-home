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
| `verify_artifacts.verify` | Public report directory → consistency result | Read-only local files; no private firmware needed | JSON/CSV/ledger equivalence, corrupted ledger |
| `P88SourceSwitch` | Private Ghidra project → bounded RX/TX branch listings | Research project only; no device IO | Two independent targeted exports |
| `P88A3Completion` | SHA-pinned binary + private project → bounded CECFA CFG | Verifies used project bytes; avoids stale function-body boundaries | Two identical24-instruction exports |

See `requirements/package-runs/P0088/reproduce.md`, `verification.json` and `unresolved-handlers.md`. The pending A3 job and the cached result are separate; production callers must retain selector validation and distinguish status polling from failed communication. This research does not change Procon's current retry policy.
