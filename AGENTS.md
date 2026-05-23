# AGENTS.md

This repository is the G2 Smart Home source of truth.

Before coding:

1. Read `README.md`.
2. Read `memory/bootstrap-manifest.json`.
3. Read every file in the manifest `read_order`, in order.
4. Read the active package in `requirements/packages/`.
5. Perform package consistency review before editing.
6. Summarize understanding, consistency result and plan before editing.

Rules:

- Keep G1 (`marlov1974/shelly`) and G2 (`marlov1974/smart-home`) separate.
- Do not treat G2 design as current G1 runtime behavior.
- Every code change must reference exactly one package id.
- A package is an ordered whole-solution version: `P0001`, `P0002`, ...
- Rollback is also a new forward-moving package.
- Shelly deploy artifacts live under `dep/s/`.
- Shelly devices must not fetch from `src/`.
- Do not invent Shelly APIs.
- Prefer read-only diagnostics by default.
- Do not write to live devices unless the package explicitly allows it.
- Run package test cases and verification commands before reporting done.
- Report diff, tests run, results and uncertainty before commit unless the package explicitly allows committing.

## Package consistency review

Codex is not only an executor. Codex must challenge package instructions when they conflict with repository truth.

Before editing, classify the package as:

- `PASS`: consistent; continue implementation.
- `WARN`: implementable but with stated assumptions or minor uncertainty.
- `STOP`: inconsistent, underspecified, unsafe or out of scope; do not edit.

Review the package against:

- memory files
- linked requirements
- previous packages
- implementation/deploy structure
- G1/G2 boundary
- invariants
- testability and rollback

If the package relies on chat-only knowledge that should be durable, report it and require or make the package-scoped memory update before implementation.

Store useful review evidence under:

```text
requirements/package-runs/<Pxxxx>/review.md
```

## Active debug mandate

When a package allows live testing, Codex may actively debug within package scope.

Codex may make up to 3 implementation/debug attempts per package unless the package says otherwise.

Each attempt must:

- capture relevant logs when live Shelly testing is involved
- verify expected output/state
- inspect runtime health and unexpected side effects
- fix defects discovered within package scope
- rerun verification after fixes
- store useful attempt/debug evidence under `requirements/package-runs/<Pxxxx>/`

After 3 failed attempts, stop and report evidence, attempts, current hypothesis and remaining uncertainty.

Live Shelly log streaming is read-only and may be used when live testing is allowed. Live writes, script starts/stops, KVS writes and actuator changes still require explicit package permission.

## Learning and evidence storage

Use package-run evidence for package-specific output:

```text
requirements/package-runs/<Pxxxx>/
  review.md
  attempts.md
  logs/
  findings.md
```

Use knowhow memory for reusable global lessons:

```text
memory/knowhow/
```

Promote a package observation to knowhow when it becomes a general rule or durable lesson for future packages.

Do not store large raw logs by default. Prefer concise excerpts or summaries unless the package explicitly requires full logs.
