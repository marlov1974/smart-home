# Package P____: <name>

## Status
planned

## Package order
P____

## Primary area
G2 / Mac / Home Assistant / Shelly / tooling / documentation

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
attempts.md
findings.md
logs/
```

Use package-run evidence for package-specific:

- review warnings/conflicts
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
- understanding summary
- implementation/debug plan
- files changed
- tests run
- verification results
- log/runtime observations when live tested
- debug attempts used
- package-run evidence paths created/updated
- knowhow promotions created/updated
- uncertainty / skipped checks
- diff summary

## Completion notes
Filled after implementation.
