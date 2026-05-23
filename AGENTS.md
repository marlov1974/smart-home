# AGENTS.md

This repository is the G2 Smart Home source of truth.

Before coding:

1. Read `README.md`.
2. Read `memory/bootstrap-manifest.json`.
3. Read every file in the manifest `read_order`, in order.
4. Read the active package in `requirements/packages/`.
5. Perform package consistency review before editing.
6. For code packages, create package-scoped implementation design before editing.
7. For code packages, create package-scoped function design before editing.
8. Summarize understanding, consistency result, design and plan before editing.

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

## Quick package command

If the human says a short command such as `build package 9`, `bygg paket 9`, or `kör P0009`, Codex should treat it as authorization to run the full package workflow for that package in `marlov1974/smart-home`.

Codex must still perform the full workflow: bootstrap, package consistency review, package-run evidence, implementation design, function design, implementation, build/generation, tests, verification and final report.

For non-live packages, the quick command also authorizes Codex to commit and push the package result when verification passes and the diff is inside package scope.

For packages that allow live writes, actuator changes, device writes, Home Assistant writes, secrets or destructive actions, the quick command does not grant extra permission. Follow the explicit package live-test/write policy.

Before committing and pushing, Codex must run `git status`, confirm the diff is inside package scope, run required verification commands and `git diff --check`.

After pushing, Codex must report commit SHA, files changed, tests run, verification result and uncertainty.

## Package consistency review

Codex is not only an executor. Codex must challenge package instructions when they conflict with repository truth.

Before editing, classify the package as:

- `PASS`: consistent; continue implementation.
- `WARN`: implementable but with stated assumptions or minor uncertainty.
- `STOP`: inconsistent, underspecified, unsafe or out of scope; do not edit.

Store useful review evidence under:

```text
requirements/package-runs/<Pxxxx>/review.md
```

## Phase-gated package execution

For substantial code packages, Codex should use explicit phase gates. Each phase may run in a fresh context.

The next phase must read repository artifacts from earlier phases instead of relying on unwritten prior reasoning.

Recommended phases:

```text
bootstrap -> review -> design -> function design -> implementation -> build/generation -> test/debug/verify -> final evidence
```

Repository state is the memory between phases.

## Implementation design

For code packages, Codex must write package-scoped implementation design before coding:

```text
requirements/package-runs/<Pxxxx>/design.md
```

The design must include package interpretation, implementation structure, intended changes, deliberate refactoring decisions, test strategy, risks and uncertainties.

Codex may refactor deliberately when required for behavior, testability, safety, contract clarity or package-scoped maintainability.

Codex must not do unrelated cleanup, broad renames, formatting churn or opportunistic refactors.

## Function design and catalog

For code packages, Codex must write package-scoped function design before coding:

```text
requirements/package-runs/<Pxxxx>/functions.md
```

Function design must list intended new, changed and removed functions, including purpose, inputs, outputs, side effects, reason and test coverage.

If implementation requires an undocumented function-level change, update `functions.md` and explain the deviation, or stop if the change expands package scope.

Durable cross-package function documentation belongs under:

```text
docs/functions/
```

Update the function catalog when functions are created, changed, removed or become relevant for future packages.

## Active debug mandate

When a package allows live testing, Codex may actively debug within package scope.

Codex may make up to 3 implementation/debug attempts per package unless the package says otherwise.

Each attempt must capture relevant logs when live Shelly testing is involved, verify expected output/state, inspect runtime health and unexpected side effects, fix defects discovered within package scope, rerun verification after fixes and store useful evidence under `requirements/package-runs/<Pxxxx>/`.

After 3 failed attempts, stop and report evidence, attempts, current hypothesis and remaining uncertainty.

Live Shelly log streaming is read-only and may be used when live testing is allowed. Live writes, script starts/stops, KVS writes and actuator changes still require explicit package permission.

## Learning and evidence storage

Use package-run evidence for package-specific output:

```text
requirements/package-runs/<Pxxxx>/
  review.md
  design.md
  functions.md
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
