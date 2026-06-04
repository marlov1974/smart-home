# Package P____: <name>

## Status
planned

## Package order
P____

## Primary area
G2 / Mac / Home Assistant / Shelly / tooling / documentation

## Label

Use `LABB` for energy-market, AI, spot-price, physical-balance and simulator experiments unless the human operator explicitly requests `G2-KANDIDAT` evaluation.

Use `G2-KANDIDAT` only when the package evaluates a lab result for possible future G2 runtime/control use and the human operator explicitly asked for that evaluation.

## Linked requirements

Epic:
- E____

Features:
- F____

User stories:
- US____

## Decision summary
Only settled decisions. Do not include exploratory discussion or discarded ideas.

## Solution model
Explain the affected part of the system well enough for Codex to understand the solution, not just the local change.

## Current behavior

## Problem

## Target behavior

## Non-goals

## Invariants
Rules that must not be broken.

## Knowledge updates
Memory files that must be created or updated.

## Implementation updates
Source/deploy areas expected to change.

## Files to inspect

## Files allowed to change

## Forbidden changes

## Pre-implementation consistency review

Before editing, Codex must verify this package against repository truth.

Codex must classify the package as:

- `PASS`: consistent; continue implementation.
- `WARN`: implementable but with stated assumptions or minor uncertainty.
- `STOP`: inconsistent, unsafe, underspecified or out of scope; do not edit.

Checks:

- package vs memory
- package vs linked requirements
- package vs previous packages
- package vs implementation/deploy structure
- package vs G1/G2 boundary
- package vs invariants
- package vs testability and rollback
- package vs chat-only assumptions that should be made durable first

Useful review output should be stored under:

```text
requirements/package-runs/<Pxxxx>/review.md
```

## Implementation design policy

For code packages, Codex must create package-scoped implementation design before coding:

```text
requirements/package-runs/<Pxxxx>/design.md
```

The design must cover:

- package interpretation
- chosen implementation structure
- files/modules intended to change
- files/modules intentionally not changed
- deliberate refactoring decisions and reasons
- test strategy
- risks and uncertainties

## Function design policy

For code packages, Codex must create package-scoped function design before coding:

```text
requirements/package-runs/<Pxxxx>/functions.md
```

The function design must list intended new, changed and removed functions, including purpose, inputs, outputs, side effects, reason and test coverage.

Codex must update function design before making an undocumented function-level change, or stop if the change expands package scope.

Durable cross-package function documentation belongs under:

```text
docs/functions/
```

Update the function catalog when functions are created, changed, removed or become relevant for future packages.

## Context-reset phase gates

For substantial code packages, Codex should use phase gates that may run in fresh context:

```text
bootstrap -> review -> design -> function design -> implementation -> build/generation -> test/debug/verify -> final evidence
```

Each phase must read repository artifacts from earlier phases instead of relying on unwritten prior reasoning.

## Live test/debug policy

Live testing allowed:
no

Live write actions allowed:
no

Shelly log capture required:
no

Max implementation/debug attempts:
3

Codex may fix defects discovered during verification if they are inside package scope. Codex must stop after the attempt limit or if the fix requires scope/design changes.

Useful debug output should be stored under:

```text
requirements/package-runs/<Pxxxx>/
```

## Evidence and learning policy

Package-specific evidence location:

```text
requirements/package-runs/<Pxxxx>/
```

Expected evidence files when relevant:

```text
review.md
design.md
functions.md
attempts.md
findings.md
logs/
```

Use package-run evidence for package-specific:

- review warnings/conflicts
- implementation design
- function design
- failed or successful debug attempts
- log excerpts
- runtime anomalies
- unexpected side effects
- findings for human/ChatGPT review

Reusable global lessons should be promoted to:

```text
memory/knowhow/
```

Do not store large raw logs by default. Prefer summaries or focused excerpts unless this package explicitly requires full logs.

## Test cases

### TC1: <name>
Given ...
When ...
Then ...

## Verification commands

## Runtime health checks

When live testing is allowed, verify expected output and inspect runtime/log health.

Check for:

- missing expected KVS/output
- HTTP/KVS/JSON errors
- script errors
- unexpected restarts
- repeated start/stop loops
- unexpectedly long execution time
- low or falling heap margin
- unexpected actuator intent
- semantically wrong side effects given the system model

## Deployment plan

## Rollback plan

Rollback is a new forward-moving package. Do not rely on lowering runtime versions.

## Expected Codex output
- consistency review result: PASS/WARN/STOP
- implementation design path
- function design path
- files changed
- tests run
- verification results
- log/runtime observations when live tested
- debug attempts used
- package-run evidence paths created/updated
- function catalog updates
- knowhow promotions created/updated
- uncertainty / skipped checks
- diff summary

## Completion notes
Filled after implementation.
