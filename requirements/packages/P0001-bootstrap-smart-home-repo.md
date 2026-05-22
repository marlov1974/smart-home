# Package P0001: Bootstrap smart-home repository

## Status
implemented

## Package order
P0001

## Primary area
G2 repository bootstrap / workflow / documentation

## Linked requirements

Epic:
- none yet

Features:
- none yet

User stories:
- none yet

## Decision summary

Create `marlov1974/smart-home` as the G2 Smart Home source-of-truth repository.

Keep `marlov1974/shelly` as G1 maintenance repository.

Use ordered packages as the atomic solution-version unit.

Use short deploy paths:

```text
dep/s/   Shelly
dep/m/   Mac
dep/ha/  Home Assistant
```

Shelly devices should fetch deploy artifacts only from `dep/s/`.

## Solution model

G2 development is package-driven.

Each package can update memory, requirements, source, deploy artifacts, tests and diagnostics. Code structure follows runtime/environment, not requirement hierarchy.

Codex is the local coding and diagnostics agent. ChatGPT is the design/task/review agent. The human operator owns priorities and real-world validation.

## Current behavior

The repository was newly created and had only a minimal README.

## Problem

The repository needed bootstrap rules, memory structure, requirements structure, deploy/source boundaries and Codex workflow rules before real G2 implementation can begin.

## Target behavior

The repository has a minimal but usable bootstrap and package workflow.

## Non-goals

- No G2 runtime functionality is implemented in this package.
- No G1 code is changed in this package.
- No live devices are touched.

## Invariants

- G1 and G2 must remain separated.
- Every future code change must reference exactly one package id.
- Rollback is a new forward-moving package.
- Codex must bootstrap before coding.

## Knowledge updates

Created/updated:

- `README.md`
- `AGENTS.md`
- `memory/bootstrap-manifest.json`
- `memory/00-index.md`
- `memory/01-system-overview.md`
- `memory/02-design-principles.md`
- `memory/03-g1-g2-boundary.md`
- `memory/04-codex-workflow.md`
- `requirements/README.md`
- `requirements/packages/TEMPLATE.md`

## Implementation updates

Create initial folder placeholders for:

- `src/`
- `dep/`
- `tools/`
- `tests/`

## Test cases

### TC1: Bootstrap manifest is readable
Given a new AI/Codex session
When it reads `README.md` and `memory/bootstrap-manifest.json`
Then every file listed in `read_order` exists.

### TC2: Package template exists
Given a future change package
When a new package is created
Then it can start from `requirements/packages/TEMPLATE.md`.

### TC3: Deploy path boundary is defined
Given future Shelly code
When deploy artifacts are produced
Then Shelly-facing files are placed under `dep/s/`.

## Verification commands

```bash
git ls-files
```

Optional future check:

```bash
python tools/checks/check_bootstrap_manifest.py
```

## Deployment plan

No runtime deploy.

## Rollback plan

Rollback by reverting P0001 commits if the repository bootstrap needs to be redesigned before real implementation starts.

Once later packages depend on this structure, create a new forward package instead of reverting history.

## Expected Codex output

For future packages, Codex must report:

- understanding summary
- implementation plan
- files changed
- tests run
- verification results
- uncertainty / skipped checks
- diff summary

## Completion notes

Initial bootstrap structure created.
