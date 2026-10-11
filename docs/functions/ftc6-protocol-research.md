# FTC6 protocol research tools

Last changed: P0083.

Offline tools live in `tools/ftc6/p83/`. Contracts, side effects and verification are in [function design](../../requirements/package-runs/P0083/functions.md). Run only with the pinned image/module hashes and retain full Ghidra exports privately. These tools are research support, not firmware or live control APIs.

The direct-flow and ROT.w module repair is narrowly qualified. Descriptor-seeded tracing and deterministic export are reusable; decompiler far-pointer arguments must be checked against assembly. Compact JSON exposes derived routes without publishing full vendor code. Historical frame processing validates checksum/header and emits only selected fields.

See [reproduction](../../requirements/package-runs/P0083/reproduce.md) and [verification](../../requirements/package-runs/P0083/verification.json). Follow-up physical tests require their own authorization.
