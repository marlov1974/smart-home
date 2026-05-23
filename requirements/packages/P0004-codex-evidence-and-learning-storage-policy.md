# Package P0004: Codex evidence and learning storage policy

## Status
implemented

## Package order
P0004

## Primary area
G2 workflow / evidence storage / knowhow learning

## Linked requirements

Epic:
- none yet

Features:
- none yet

User stories:
- none yet

## Decision summary

Codex review/debug output should be stored in the repository when it is useful for learning or later human/ChatGPT review.

There are two destinations:

1. Package-specific evidence under `requirements/package-runs/<Pxxxx>/`.
2. Reusable global lessons under `memory/knowhow/`.

## Solution model

Package-specific review/debug output is evidence for that package. It should be stored with the package run so humans and ChatGPT can inspect what happened, fix issues and improve future packages.

Reusable lessons are promoted to `memory/knowhow/` only when they become generally useful across packages.

Example:

```text
Package evidence:
  P0012 attempt 2 showed three parallel Shelly RPC calls inside one timer callback appeared to hang the script.

Promoted knowhow:
  Avoid multiple parallel Shelly RPC calls inside one timer callback; serialize RPC calls unless proven safe.
```

## Current behavior

P0003 gave Codex active debug and package-review mandate but did not define where to store review/debug output or how to promote reusable lessons.

## Problem

Without a storage policy, useful findings can remain only in terminal output or chat history. Then future packages cannot learn from them, and ChatGPT/human review loses evidence.

## Target behavior

Codex stores useful package-specific evidence and promotes reusable global lessons into knowhow memory.

## Non-goals

- No runtime code.
- No live device access.
- No G1 repository changes.
- No requirement to store every raw log line.

## Invariants

- Package-specific evidence must not pollute global memory unless promoted as a reusable lesson.
- Large raw logs should not be stored by default.
- Every evidence/knowhow change belongs to a package.
- G1 and G2 remain separated.

## Knowledge updates

Created:

- `memory/knowhow/00-index.md`
- `memory/knowhow/shelly.md`
- `memory/knowhow/codex.md`
- `requirements/package-runs/README.md`
- `requirements/package-runs/TEMPLATE-review.md`
- `requirements/package-runs/TEMPLATE-attempts.md`

Updated:

- `AGENTS.md`
- `memory/04-codex-workflow.md`
- `requirements/packages/TEMPLATE.md`
- `memory/bootstrap-manifest.json`

## Implementation updates

None.

## Files to inspect

- `AGENTS.md`
- `memory/04-codex-workflow.md`
- `requirements/packages/TEMPLATE.md`
- `memory/bootstrap-manifest.json`

## Files allowed to change

- `AGENTS.md`
- `memory/04-codex-workflow.md`
- `requirements/packages/TEMPLATE.md`
- `memory/bootstrap-manifest.json`
- `memory/knowhow/**`
- `requirements/package-runs/**`
- this package file

## Forbidden changes

- no source code changes
- no deploy artifact changes
- no live device access
- no G1 repository changes

## Pre-implementation consistency review

This package extends P0003 and is consistent if:

- Codex keeps package review/debug output inspectable.
- Package-specific evidence remains separate from reusable knowhow.
- Global knowhow is only used for durable reusable lessons.
- Raw logs are summarized/excerpted unless full logs are explicitly needed.

## Live test/debug policy

Live testing allowed:
no

Live write actions allowed:
no

Shelly log capture required:
no

Max implementation/debug attempts:
3

## Evidence and learning policy

Package-specific evidence location:

```text
requirements/package-runs/<Pxxxx>/
```

Reusable global lesson location:

```text
memory/knowhow/
```

## Test cases

### TC1: Package-run evidence structure exists
Given a future package run
When Codex needs to store review/debug evidence
Then `requirements/package-runs/README.md` describes the structure and templates exist.

### TC2: Knowhow structure exists
Given a reusable lesson is discovered
When it should be promoted
Then `memory/knowhow/` exists with Shelly and Codex knowhow entry points.

### TC3: Package template tells Codex where to store evidence
Given a new package starts from `requirements/packages/TEMPLATE.md`
When Codex reads it
Then it sees evidence and learning policy sections.

### TC4: Bootstrap includes the evidence/knowhow policy
Given a future AI/Codex session follows bootstrap
When it reads `memory/bootstrap-manifest.json`
Then it reads knowhow files, package-run docs and P0004.

## Verification commands

```bash
git grep -n "requirements/package-runs" AGENTS.md memory/04-codex-workflow.md requirements/packages/TEMPLATE.md requirements/package-runs/README.md
git grep -n "memory/knowhow" AGENTS.md memory/04-codex-workflow.md requirements/packages/TEMPLATE.md memory/knowhow/00-index.md
git grep -n "P0004-codex-evidence-and-learning-storage-policy" memory/bootstrap-manifest.json
```

## Runtime health checks

No live runtime test.

## Deployment plan

No runtime deploy.

## Rollback plan

If this evidence structure is wrong, create a new forward package that supersedes it.

## Expected Codex output
- consistency review result: PASS/WARN/STOP
- understanding summary
- implementation/debug plan
- files changed
- tests run
- verification results
- package-run evidence paths created/updated
- knowhow promotions created/updated
- uncertainty / skipped checks
- diff summary

## Completion notes

P0004 added package-run evidence storage and reusable knowhow promotion rules.
