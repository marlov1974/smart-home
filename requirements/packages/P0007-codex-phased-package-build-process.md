# Package P0007: Codex phased package build process

## Status
implemented

## Package order
P0007

## Primary area
G2 process / Codex workflow / function documentation

## Linked requirements

Epic:
- none yet

Features:
- none yet

User stories:
- none yet

## Decision summary

Codex should build code packages through explicit repository-backed phases.

For substantial code packages, each phase may be run in a fresh Codex context. The next phase must read repository artifacts from earlier phases instead of relying on unwritten prior reasoning.

Codex must document implementation design and function-level design before coding. Durable cross-package function documentation belongs under `docs/functions/`.

## Solution model

Recommended code-package phases:

```text
0. bootstrap
1. package consistency review
2. implementation design
3. function design
4. implementation
5. build / generated deploy artifacts
6. test / debug / verification
7. final evidence and report
```

Package-local evidence:

```text
requirements/package-runs/<Pxxxx>/review.md
requirements/package-runs/<Pxxxx>/design.md
requirements/package-runs/<Pxxxx>/functions.md
requirements/package-runs/<Pxxxx>/attempts.md
requirements/package-runs/<Pxxxx>/findings.md
requirements/package-runs/<Pxxxx>/logs/
```

Cross-package function catalog:

```text
docs/functions/
```

## Current behavior

P0003-P0005 defined review, active debug, package evidence and repository-first review. They did not yet require phased context resets, pre-implementation design files, package-local function design or cross-package function catalog.

## Problem

Codex may otherwise continue from its own transient context, refactor without an explicit design decision, or leave function-level choices undocumented for the next Codex instance.

## Target behavior

Codex should:

- use phase gates for substantial code packages
- write package review before implementation
- write implementation design before coding
- write function design before coding
- document deliberate refactoring decisions
- update durable function catalog when functions are created, changed or removed
- treat repository evidence as memory between phases

## Non-goals

- No application/runtime code changes.
- No Shelly deploy tooling implementation.
- No live device access.
- No G1 repository changes.

## Invariants

- Package scope remains authoritative.
- Codex may refactor deliberately, but not opportunistically.
- Each phase uses repository artifacts as memory.
- Cross-package function documentation records durable current design, not temporary package thoughts.
- Package-local function design records the plan for one package.

## Knowledge updates

Created:

- `docs/functions/00-index.md`
- `docs/functions/TEMPLATE.md`
- `requirements/package-runs/TEMPLATE-design.md`
- `requirements/package-runs/TEMPLATE-functions.md`

Updated:

- `memory/04-codex-workflow.md`

Attempted but not completed due tool safety block:

- `requirements/package-runs/README.md`
- `requirements/packages/TEMPLATE.md`

These should be aligned in a later package or manual edit if needed.

## Implementation updates

None.

## Files to inspect

- `memory/04-codex-workflow.md`
- `docs/functions/00-index.md`
- `docs/functions/TEMPLATE.md`
- `requirements/package-runs/TEMPLATE-design.md`
- `requirements/package-runs/TEMPLATE-functions.md`

## Files allowed to change

- `memory/04-codex-workflow.md`
- `docs/functions/**`
- `requirements/package-runs/**`
- `requirements/packages/TEMPLATE.md`
- `memory/bootstrap-manifest.json`
- this package file

## Forbidden changes

- no source code changes
- no deploy artifact changes
- no live device access
- no G1 repository changes

## Pre-implementation consistency review

This process package is consistent if it preserves:

- package-driven development
- repository-first review
- Codex consistency review
- evidence storage
- G1/G2 boundary
- package-scoped implementation

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

This package creates templates and documentation for future package evidence. No live package-run evidence is required.

## Test cases

### TC1: Workflow defines phase gates
Given Codex reads `memory/04-codex-workflow.md`
When handling a substantial code package
Then it sees the context-reset phase gate model.

### TC2: Workflow requires implementation design
Given Codex reads `memory/04-codex-workflow.md`
When handling a code package
Then it must create `requirements/package-runs/<Pxxxx>/design.md` before coding.

### TC3: Workflow requires function design
Given Codex reads `memory/04-codex-workflow.md`
When handling a code package
Then it must create `requirements/package-runs/<Pxxxx>/functions.md` before coding.

### TC4: Cross-package function catalog exists
Given a code package changes durable functions
When Codex updates documentation
Then it has `docs/functions/` and a template for function catalog updates.

## Verification commands

```bash
git grep -n "Context-reset phase gates" memory/04-codex-workflow.md
git grep -n "Function design" memory/04-codex-workflow.md docs/functions/TEMPLATE.md requirements/package-runs/TEMPLATE-functions.md
git grep -n "Implementation design" memory/04-codex-workflow.md requirements/package-runs/TEMPLATE-design.md
```

## Runtime health checks

No live runtime test.

## Deployment plan

No runtime deploy.

## Rollback plan

If this process is too heavy or too light, create a new forward package refining the Codex phase model.

## Expected Codex output
- consistency review result: PASS/WARN/STOP
- implementation design path
- function design path
- files changed
- tests run
- verification results
- uncertainty / skipped checks
- diff summary

## Completion notes

P0007 adds phased Codex package processing, package-local implementation/function design and cross-package function catalog structure.
