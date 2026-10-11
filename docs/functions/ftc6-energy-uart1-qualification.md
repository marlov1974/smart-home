# FTC6 energy/settings/UART1 qualification — P0086

Offline only; no production control/allowlist changes. [Results and limitations](../../requirements/package-runs/P0086/findings.md).

| File / functions | Contract and important failures |
|---|---|
| `tools/ftc6/p86/energy.py` — `bcd`, `a3`, `pair`, `delta`, `fold`, `get07`, `observations`, `api600` | Validate frames/selectors/format/BCD, reconstruct truncated pairs, preserve uncertainty and timestamps. Exclude mutating selectors. No unit calibration or atomicity claim. |
| `uart1.py` — `profile`, `request`, `memory`, `response`, `effective_addresses`, `normal52`, `logs` | Static image identity, five-byte checksum codec, bounded near-RAM candidate, 16-bit alias model, raw log records and conservative reassembly. Normal profile rejects diagnostic framing. |
| `settings.py` — `ReadSession.event`, `capture`, `proposed_block`, `apply` | Observer with explicit internal events, complete captured-block preservation and offline single-byte diff. Unknown transitions and all apply attempts fail closed. |
| `reader.py` — `plan`, `replay`, `main` | Explicit profile; dry-run/replay only; finite deadlines, zero retries, cancellation, raw failure retention, exclusive output creation. No hardware backend. |
| `verify_local.py` — `derive`, `verify` | Exact image/opcode/operand identity, requested function coverage, two export comparisons, eight emulator markers. Mismatch is an error. |
| `P86AddressProof.java` | Emulates only reviewed MOV.b near load at9E99C, independently varying discarded upper bits. Not a full-firmware emulator. |
| `run_analysis.py` | Local pinned headless wrapper; two independently copied P85 projects and a read-only instruction proof. |

New static qualification covers odd service packing in8C0B4, forced accounting viaCDF02/CDF24 andCD8F6/CDDCA, CEE20 state callbacks/CFB18/CF9C4, UART1 mode source8E12C/8E37E/8E3DE, clocks910E4/9156E, diagnostic9E77A/9E938 and ring9D8FE/9DA08/9DA78/9D8A0. Full addresses/tool provenance and confidence are in the package reports. Physical results are NOT RUN throughout.
