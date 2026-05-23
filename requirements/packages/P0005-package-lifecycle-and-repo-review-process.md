# Package P0005: Package lifecycle and repo review process

## Status
implemented

## Package order
P0005

## Primary area
G2 process / package lifecycle / repository-first review

## Linked requirements

Epic:
- none yet

Features:
- none yet

User stories:
- none yet

## Decision summary

Define the standard G2 lifecycle from idea to verified/live package and lessons learned.

Important decision:

```text
ChatGPT reviews Codex results directly from the repository, not from pasted Codex output, whenever repository access is available.
```

Codex should store package results and evidence in the repo. Human only needs to tell ChatGPT that Codex is done or stopped.

## Solution model

G2 changes flow through:

```text
Idea -> design with ChatGPT -> design freeze -> package -> Codex review/implementation/debug/evidence -> ChatGPT repo review -> deploy/rollback -> lessons learned
```

Codex produces repository evidence. ChatGPT reads repository evidence and reviews it with the human operator.

## Current behavior

P0001-P0004 defined bootstrap, package model, Codex review/debug mandate and evidence storage. The end-to-end lifecycle and repository-first ChatGPT review rule were not explicitly documented.

## Problem

Without a documented lifecycle, future work may drift into pasted outputs, unclear ownership of documentation updates, unclear rollback/update behavior and unclear handoff between ChatGPT and Codex.

## Target behavior

G2 has an explicit package lifecycle and review process.

## Non-goals

- No runtime code.
- No live device access.
- No G1 repository changes.
- No package-run output for a real implementation package.

## Invariants

- Every code change belongs to exactly one package.
- Codex performs consistency review before implementation.
- Codex stores useful evidence in the repo.
- ChatGPT reviews from repo state whenever possible.
- Rollback after runtime/live impact should normally be a new forward package.

## Knowledge updates

Created:

- `memory/05-package-lifecycle.md`

Updated:

- `memory/04-codex-workflow.md`
- `memory/bootstrap-manifest.json`

## Implementation updates

None.

## Files to inspect

- `memory/04-codex-workflow.md`
- `memory/05-package-lifecycle.md`
- `memory/bootstrap-manifest.json`
- `requirements/packages/P0001-bootstrap-smart-home-repo.md`
- `requirements/packages/P0003-codex-review-and-active-debug-policy.md`
- `requirements/packages/P0004-codex-evidence-and-learning-storage-policy.md`

## Files allowed to change

- `memory/04-codex-workflow.md`
- `memory/05-package-lifecycle.md`
- `memory/bootstrap-manifest.json`
- this package file

## Forbidden changes

- no source code changes
- no deploy artifact changes
- no live device access
- no G1 repository changes

## Pre-implementation consistency review

This package is consistent if it:

- preserves package-driven development
- preserves Codex package-review and evidence-storage rules
- documents ChatGPT repository-first review
- does not require pasted Codex output as the normal review path

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

No package-run evidence is required for this documentation-only package.

## Test cases

### TC1: Lifecycle document exists
Given future G2 work
When reading bootstrap memory
Then `memory/05-package-lifecycle.md` explains the end-to-end lifecycle.

### TC2: Workflow says ChatGPT reviews from repo
Given Codex completes a package
When the human tells ChatGPT Codex is done
Then ChatGPT is instructed to read package/evidence/diff from repository rather than pasted output.

### TC3: Bootstrap includes lifecycle
Given a future AI/Codex session follows bootstrap
When it reads `memory/bootstrap-manifest.json`
Then `memory/05-package-lifecycle.md` and P0005 are included.

## Verification commands

```bash
git grep -n "repository" memory/04-codex-workflow.md memory/05-package-lifecycle.md
git grep -n "P0005-package-lifecycle-and-repo-review-process" memory/bootstrap-manifest.json
git grep -n "Idea -> design" memory/05-package-lifecycle.md
```

## Runtime health checks

No live runtime test.

## Deployment plan

No runtime deploy.

## Rollback plan

If the lifecycle process is wrong, create a new forward package that supersedes it.

## Expected Codex output
- consistency review result: PASS/WARN/STOP
- understanding summary
- files changed
- tests run
- verification results
- uncertainty / skipped checks
- diff summary

## Completion notes

P0005 documents the package lifecycle and repository-first ChatGPT review process.
