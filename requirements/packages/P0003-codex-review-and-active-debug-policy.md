# Package P0003: Codex review and active debug policy

## Status
implemented

## Package order
P0003

## Primary area
G2 workflow / Codex mandate / package template

## Linked requirements

Epic:
- none yet

Features:
- none yet

User stories:
- none yet

## Decision summary

Codex has two expanded mandates in G2:

1. Active debugging within package scope.
2. Independent package consistency review before implementation.

Codex is not only a passive executor. It must challenge package instructions that conflict with repository truth and may fix discovered defects within package scope during verification.

## Solution model

Before editing, Codex bootstraps the repository, reads the active package, reads relevant files and performs a consistency review.

Consistency result:

```text
PASS = continue
WARN = continue only if uncertainty is minor and within scope
STOP = do not edit
```

When live testing is allowed, Codex verifies both expected output and runtime health. Shelly log capture, KVS reads and `Shelly.GetStatus` are important sources.

Codex may use up to 3 implementation/debug attempts per package by default.

## Current behavior

P0001/P0002 defined Codex as coding/diagnostics agent, but the workflow did not explicitly give Codex package-review mandate or active debug attempt rules.

## Problem

A package may contain chat-derived assumptions or details that conflict with durable repo truth. Codex should catch that before implementation.

Also, test output may pass while logs reveal runtime problems such as slow execution, memory pressure, errors or semantically wrong side effects.

## Target behavior

Codex must:

- review packages before editing
- report PASS/WARN/STOP
- stop on real conflicts
- capture logs during live Shelly tests when required
- inspect KVS/status/logs, not only expected output
- fix package-scoped defects and retry up to 3 attempts
- stop and report after failed attempts or required scope/design expansion

## Non-goals

- No application/runtime feature code.
- No live device access.
- No change to G1 repository.
- No automatic permission for live writes.

## Invariants

- G1 and G2 remain separated.
- Live writes still require explicit package permission.
- Codex may not expand architecture outside package scope.
- Rollback remains a new forward-moving package.

## Knowledge updates

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
- this package file

## Forbidden changes

- no source code changes
- no deploy artifact changes
- no live device access
- no G1 repository changes

## Pre-implementation consistency review

This package is a workflow update. Consistency checks:

- It must preserve package-driven development.
- It must preserve G1/G2 separation.
- It must not grant implicit live-write permission.
- It must keep Codex independent enough to challenge package conflicts.

## Live test/debug policy

Live testing allowed:
no

Live write actions allowed:
no

Shelly log capture required:
no

Max implementation/debug attempts:
3

## Test cases

### TC1: Template contains consistency review section
Given a new package starts from `requirements/packages/TEMPLATE.md`
When Codex reads it
Then it sees a mandatory pre-implementation consistency review with PASS/WARN/STOP.

### TC2: Workflow gives Codex active debug mandate
Given Codex reads `memory/04-codex-workflow.md`
When live testing is allowed by a future package
Then Codex is instructed to capture logs, inspect runtime health and retry package-scoped fixes up to the attempt limit.

### TC3: Live writes remain explicit
Given Codex reads `AGENTS.md` or `memory/04-codex-workflow.md`
When live diagnostics are discussed
Then read-only log/KVS/status diagnostics are allowed only as diagnostics, while live writes/actions still require explicit package permission.

### TC4: Bootstrap includes P0003
Given a future AI/Codex session reads `memory/bootstrap-manifest.json`
When it follows `read_order`
Then it reads this package file after P0001 and P0002.

## Verification commands

```bash
git grep -n "PASS" AGENTS.md memory/04-codex-workflow.md requirements/packages/TEMPLATE.md
git grep -n "debug attempts" AGENTS.md memory/04-codex-workflow.md requirements/packages/TEMPLATE.md
git grep -n "P0003-codex-review-and-active-debug-policy" memory/bootstrap-manifest.json
```

## Runtime health checks

No live runtime test.

## Deployment plan

No runtime deploy.

## Rollback plan

If the Codex mandate is too broad or too narrow, create a new forward package that revises these workflow documents.

## Expected Codex output
- consistency review result: PASS/WARN/STOP
- understanding summary
- implementation/debug plan
- files changed
- tests run
- verification results
- uncertainty / skipped checks
- diff summary

## Completion notes

P0003 added package consistency review and active debug policy to G2 workflow, AGENTS and package template.
