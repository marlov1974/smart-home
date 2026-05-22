# ChatGPT / Codex Workflow

## Roles

Human operator:
- owns priorities
- validates physical reality
- approves design and deploy decisions

ChatGPT:
- reasoning partner
- requirements/design author
- package framer
- reviewer

Codex:
- local coding and diagnostics agent
- reads repo context
- implements packages
- runs tests and verification
- prepares diffs/commits when allowed

## Standard flow

1. Human and ChatGPT discuss problem and design.
2. ChatGPT writes or updates an ordered package file.
3. Codex reads bootstrap and the active package.
4. Codex summarizes understanding and plan before editing.
5. Codex implements within package scope.
6. Codex runs package test cases and verification commands.
7. Codex reports diff, tests and uncertainty.
8. Human/ChatGPT reviews before deploy.

## Codex bootstrap before coding

Codex must read:

1. `README.md`
2. `AGENTS.md`
3. `memory/bootstrap-manifest.json`
4. every file in manifest `read_order`
5. the active package file
6. relevant source/deploy files listed by the package

Codex must not edit before producing a short understanding and implementation plan.

## Safety defaults

Codex may use read-only diagnostics by default.

Codex must not write to live devices unless the active package explicitly permits live write actions.

Forbidden by default:

- actuator-changing RPC calls
- `KVS.Set` against live devices
- script upload/start/stop against live devices
- Home Assistant config changes outside package scope

## Package output expectation

Codex must report:

- files changed
- tests run
- verification output
- uncertainty / skipped checks
- whether deploy artifacts changed
- rollback implications
