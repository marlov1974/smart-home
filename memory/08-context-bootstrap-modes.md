# Context Bootstrap Modes

This document defines how ChatGPT and Codex rebuild context without reading unnecessary repository or data volume.

## Modes

### New chat/session: full bootstrap

For a new AI, ChatGPT or Codex session that has no reliable conversation context, use the mandatory bootstrap from `README.md` and `memory/bootstrap-manifest.json`:

1. read `README.md`
2. read `memory/bootstrap-manifest.json`
3. read every file in `read_order`, in order
4. if the task touches current Gen1 runtime behavior, also bootstrap `marlov1974/shelly`
5. stop with `BOOTSTRAP FAILED` if a mandatory step fails

### Follow-up fix or next package in an active work thread: package bootstrap

When the active chat already has project context and the task is to create a new fix/package or continue from the latest package, do not reread the whole repository. Use package bootstrap:

1. read `README.md`
2. read `memory/bootstrap-manifest.json`
3. read the current or latest relevant package file under `requirements/packages/`
4. read `requirements/package-runs/<Pxxxx>/CHANGELOG.md` when it exists
5. read `review.md`, `design.md`, `functions.md`, `attempts.md` and `findings.md` only when the current task needs that evidence
6. read only explicitly relevant source, deploy, test or docs files named by the package/evidence or required by the current fix

Package bootstrap is a delta-bootstrap. It is not a replacement for full bootstrap when context is absent.

## Large data and fixture rule

Do not read large data files, raw logs or fixtures during bootstrap unless the package explicitly requires inspecting that data for verification.

Spot-price files are specifically excluded from ordinary ChatGPT/Codex bootstrap and package-bootstrap. Spot-price fixtures may be used by tests or scripts, but ChatGPT/Codex should not inspect their raw contents as context unless the package explicitly requires it.

## Package changelog role

Each package-run should include:

```text
requirements/package-runs/<Pxxxx>/CHANGELOG.md
```

The changelog is the first file to read for a follow-up fix because it summarizes what Codex actually changed, which contracts moved, what was verified and what remains open.

For follow-up work, prefer the changelog over rereading broad repository areas.

## Required package-run changelog content

A package changelog should include:

- status: `done`, `partial`, `stopped`, `failed-verification`, or another explicit package state
- user-visible behavior changed
- files changed with one-line purpose per file
- contracts changed, including schemas, fields, normalization rules, public CLI/API behavior and compatibility
- important implementation notes
- verification performed
- known limitations and follow-up
- bootstrap for next package, including what to read first and what not to read

## Source of truth

For completed packages, implementation and deploy artifacts remain the strongest truth. Package-run changelogs summarize the delta and help navigate to the relevant truth without broad scanning.
