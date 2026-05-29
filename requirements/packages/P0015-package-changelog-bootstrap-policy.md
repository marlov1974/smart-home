# Package P0015: package changelog bootstrap policy

## Status

done

## Package order

P0015

## Primary area

G2 / tooling / documentation / workflow

## Linked requirements

Epic:
- E0001

Features:
- F0001

User stories:
- US0001

## Decision summary

Introduce two explicit context modes:

- New chat/session uses full mandatory bootstrap.
- Follow-up fix or next package in an active thread uses package bootstrap, starting from the latest relevant package and its package-run `CHANGELOG.md`.

Every package after P0015 must produce a package-run changelog so ChatGPT and Codex can understand what was delivered without rereading broad repository areas.

Spot-price fixture/raw data files must not be read during ordinary bootstrap/package-bootstrap unless a package explicitly requires raw data inspection for verification.

## Solution model

The repository already has package-run evidence files. P0015 adds a concise `CHANGELOG.md` as the first follow-up read file for the next package/fix. The changelog records the delta from the package and points to only the evidence and implementation files needed for follow-up work.

## Current behavior

A new session performs full bootstrap. For follow-up fixes, there is no explicit lightweight bootstrap path and no guaranteed package-run changelog.

## Problem

Full bootstrap and broad repository scanning can waste context and time. Large data files and spot-price fixtures are not useful as conversation context and can cause the assistant/Codex to stall.

## Target behavior

- New chat/session: full bootstrap remains mandatory.
- Active-thread follow-up/new fix: package bootstrap is allowed and preferred.
- Package bootstrap reads only the current/latest relevant package, its `CHANGELOG.md`, relevant evidence, and named implementation files.
- Every package after P0015 creates or updates `requirements/package-runs/<Pxxxx>/CHANGELOG.md` before completion.
- The changelog captures status, behavior change, files changed, contracts changed, verification, known limitations and bootstrap hints for the next package.
- Spot-price files are not read during ordinary bootstrap/package-bootstrap unless explicitly required by package verification.

## Non-goals

- Do not remove mandatory full bootstrap for new chats or new Codex sessions.
- Do not change G1/G2 boundary rules.
- Do not alter spot-price model behavior.
- Do not require retroactive changelogs for all historic packages.

## Invariants

- Full bootstrap remains the fallback when context is absent.
- Implementation/deploy artifacts remain stronger truth than package-run summaries.
- Every code change still references exactly one package id.
- Rollback remains a new forward-moving package.

## Knowledge updates

- Create `memory/08-context-bootstrap-modes.md`.
- Update `memory/bootstrap-manifest.json` to include the new memory file, changelog template and this package.

## Implementation updates

- Create `requirements/package-runs/TEMPLATE-changelog.md`.
- Document P0015 as a completed governance package.

## Files to inspect

- `README.md`
- `memory/bootstrap-manifest.json`
- `requirements/packages/TEMPLATE.md`
- `requirements/package-runs/README.md`
- `memory/05-package-lifecycle.md`

## Files allowed to change

- `memory/bootstrap-manifest.json`
- `memory/08-context-bootstrap-modes.md`
- `requirements/package-runs/TEMPLATE-changelog.md`
- `requirements/packages/P0015-package-changelog-bootstrap-policy.md`
- `requirements/package-runs/P0015/CHANGELOG.md`

## Forbidden changes

- No source code changes.
- No deploy artifact changes.
- No test fixture changes.
- Do not inspect or edit spot-price data files.

## Pre-implementation consistency review

PASS. This is a governance/documentation package that clarifies existing package-run evidence behavior and adds a lightweight delta-bootstrap artifact.

## Implementation design policy

Documentation-only package. No code design required.

## Function design policy

No function changes.

## Context-reset phase gates

Not applicable beyond normal documentation review.

## Live test/debug policy

Live testing allowed: no

Live write actions allowed: no

Shelly log capture required: no

Max implementation/debug attempts: 1

## Evidence and learning policy

Package-specific evidence location:

```text
requirements/package-runs/P0015/
```

Expected evidence:

```text
CHANGELOG.md
```

## Test cases

### TC1: Package changelog template exists
Given repository documentation after P0015
When a future package needs a changelog
Then `requirements/package-runs/TEMPLATE-changelog.md` exists and describes the expected contents.

### TC2: Full bootstrap still exists
Given a new chat/session
When it follows repository bootstrap
Then it still reads `README.md`, `memory/bootstrap-manifest.json` and the manifest `read_order`.

### TC3: Package bootstrap avoids large irrelevant data
Given a follow-up package in an active thread
When ChatGPT/Codex uses package bootstrap
Then it reads the relevant package-run changelog first and does not inspect spot-price data files unless explicitly required.

## Verification commands

Documentation-only change. Review changed files and confirm no source/deploy/test data files changed.

## Runtime health checks

Not applicable.

## Deployment plan

Commit documentation updates to `main`.

## Rollback plan

Rollback is a new forward-moving package that supersedes this policy.

## Expected Codex output

- consistency review result: PASS
- files changed
- verification result
- commit SHA

## Completion notes

Implemented directly as documentation/governance updates. Some existing workflow files may still be further refined by a later package if stricter automation is desired.
