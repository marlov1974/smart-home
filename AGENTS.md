# AGENTS.md

This repository is the G2 Smart Home production source of truth.

Before coding:

0. Sync the local repository before reading package files:
   - run `git fetch origin`
   - run `git status --short --branch`
   - if the current branch is only behind `origin/main`, run `git pull --ff-only`
   - if there are local changes, local commits, ahead/behind divergence, merge conflicts, or any non-fast-forward situation, stop and report `SYNC BLOCKED` with the exact git status and branch divergence
1. Read `README.md`.
2. Read `memory/bootstrap-manifest.json`.
3. Read every file in the manifest `read_order`, in order.
4. Read the active package in `requirements/packages/`.
5. Perform package consistency review before editing.
6. For code packages, create package-scoped implementation design before editing.
7. For code packages, create package-scoped function design before editing.
8. Summarize understanding, consistency result, design and plan before editing.

Rules:

- G2 (`marlov1974/smart-home`) is current production truth.
- G1 (`marlov1974/shelly`) is retired historical provenance. Use it only for explicitly historical/pre-G2 comparison tasks.
- Do not treat historical G1 code or notes as current runtime behavior.
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
- Keep `REPOSITORY_FILES.md` synchronized whenever tracked files are added, removed or moved.

## Repository synchronization

Codex must never infer that a requested package does not exist until it has synchronized the local repository with `origin/main`.

For every package run, including quick package commands, repository synchronization is part of bootstrap and must happen before reading `memory/bootstrap-manifest.json` and before searching for `requirements/packages/Pxxxx-*.md`.

Required command sequence:

```bash
git fetch origin
git status --short --branch
```

If local main is only behind `origin/main`, update with:

```bash
git pull --ff-only
```

If the branch is ahead/behind, has local modifications, or cannot fast-forward, Codex must stop and report:

```text
SYNC BLOCKED
<git status --short --branch output>
<git log --oneline --decorate --left-right HEAD...origin/main output when available>
```

Codex must not spend time reconstructing or guessing a missing package from stale local files. If a package is absent locally after successful sync, then report it missing.

## Repository file index

`REPOSITORY_FILES.md` is a tracked file index for GitHub/chat review contexts that cannot enumerate repository files directly.

When a package or direct documentation update adds, removes or moves any tracked file, Codex/ChatGPT must update `REPOSITORY_FILES.md` in the same change so the index matches `git ls-files`.

For packages, the package-run changelog must mention whether the file index changed or state that no tracked files were added, removed or moved.

Recommended verification when file paths change:

```bash
git ls-files > /tmp/g2-files.txt
# compare /tmp/g2-files.txt with the Files section in REPOSITORY_FILES.md
```

A package that changes tracked file paths but leaves `REPOSITORY_FILES.md` stale is incomplete.

## Quick package command

If the human says a short command such as `build package 9`, `bygg paket 9`, or `kör P0009`, Codex should treat it as authorization to run the full package workflow for that package in `marlov1974/smart-home`.

A quick package command starts with repository synchronization. Codex must fetch/pull first so newly created package files are visible locally before it attempts to understand or implement the package.

Codex must still perform the full workflow: repository synchronization, bootstrap, package consistency review, package-run evidence, implementation design, function design, implementation, build/generation, tests, verification and final report.

Because G2 is production, quick package commands authorize commit/push of verified package results only when the active package explicitly allows the performed live actions and clearly states the permitted completion level.

For production-critical G2 runtime packages, the active package must explicitly state what successful verification authorizes:

```text
commit/push only
commit/push plus staged deploy
commit/push plus production activation
```

Production activation means making G2 code/config the active controller for production behavior. Production activation always requires explicit package permission and operator approval.

Before committing and pushing, Codex must run `git status`, confirm the diff is inside package scope, run required verification commands and `git diff --check`.

After pushing, Codex must report commit SHA, files changed, tests run, verification result, live actions performed if any, final live state, `REPOSITORY_FILES.md` status and uncertainty.

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

## Production-mode rollback and pre-live testing

Production G2 should support simple operator rollback by version/package, for example:

```text
backa till 27
```

Rollback must be implemented as a safe forward-moving operation that restores the selected target version/config/runtime state without relying on ad-hoc manual edits.

Production G2 must use test levels that reduce risk before production activation when the change type allows it:

- Mac/Codex tests of external APIs and data contracts before Shelly runtime deploy
- non-production or low-criticality Shelly device tests before central production devices receive a script
- staged rollout where a less central device may validate a new runtime behavior before a central device such as dampers receives it
- live verification that is read-only or non-actuating whenever possible before production activation

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

Codex must explicitly consider knowhow promotion at the end of every package that includes live debugging, runtime anomalies, tool/API discoveries, memory-pressure findings, deploy/rollback lessons or repeated workflow problems. The final report must say whether a knowhow promotion was created, updated or intentionally skipped.

Do not store large raw logs by default. Prefer concise excerpts or summaries unless the package explicitly requires full logs.
