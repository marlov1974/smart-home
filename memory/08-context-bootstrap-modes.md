# Context Bootstrap Modes

This document defines how ChatGPT and Codex rebuild context without reading unnecessary repository or data volume.

## Modes

### New chat/session: full bootstrap

For a new AI, ChatGPT or Codex session that has no reliable conversation context, use the mandatory bootstrap from `README.md` and `memory/bootstrap-manifest.json`:

1. read `README.md`
2. read `memory/bootstrap-manifest.json`
3. read every file in `read_order`, in order
4. read `REPOSITORY_FILES.md` when the tool context cannot enumerate tracked repository paths directly, when path discovery is needed, or when the task may add, remove or move tracked files
5. inspect `marlov1974/shelly` only when the task explicitly asks for historical Gen1 behavior, pre-G2 comparison or retired G1 provenance
6. stop with `BOOTSTRAP FAILED` if a mandatory step fails

Reading `REPOSITORY_FILES.md` is path discovery, not full content bootstrap. Do not read every tracked file listed in the index during ordinary startup.

G2 production/current runtime work starts from `marlov1974/smart-home`; do not bootstrap G1 merely because the task touches Shelly runtime behavior.

### Follow-up fix or next package in an active work thread: package bootstrap

When the active chat already has project context and the task is to create a new fix/package or continue from the latest package, do not reread the whole repository. Use package bootstrap:

1. read `README.md`
2. read `memory/bootstrap-manifest.json`
3. read `REPOSITORY_FILES.md` when file discovery is needed or when the task may add, remove or move tracked files
4. read the current or latest relevant package file under `requirements/packages/`
5. read `requirements/package-runs/<Pxxxx>/CHANGELOG.md` when it exists
6. read `review.md`, `design.md`, `functions.md`, `attempts.md` and `findings.md` only when the current task needs that evidence
7. read only explicitly relevant source, deploy, test or docs files named by the package/evidence or required by the current fix

Package bootstrap is a delta-bootstrap. It is not a replacement for full bootstrap when context is absent.

## Repository file index rule

`REPOSITORY_FILES.md` exists so GitHub/chat review contexts that cannot enumerate files can still discover tracked repository paths.

Read `REPOSITORY_FILES.md` as a catalog when path discovery is needed. It should answer which tracked files exist and where package, evidence, source, deploy, test and documentation files are located.

Do not read broad source trees just to discover filenames when `REPOSITORY_FILES.md` answers the path-discovery question.

Do not treat `REPOSITORY_FILES.md` as a command to read every listed file. The index includes generated artifacts, package-run logs, tests, fixtures and runtime source; reading all of them during startup wastes context and can obscure the active task. Read only the files required by the manifest, the active package, package-run changelog/evidence, or the current task.

When a package or direct documentation update adds, removes or moves tracked files, update `REPOSITORY_FILES.md` in the same change and mention the file-index status in the package-run changelog or final report.

## Large data, generated artifact and fixture rule

Do not read large data files, raw logs, generated build/deploy artifacts or fixtures during bootstrap unless the package explicitly requires inspecting that data for verification.

Spot-price files are specifically excluded from ordinary ChatGPT/Codex bootstrap and package-bootstrap. Spot-price fixtures may be used by tests or scripts, but ChatGPT/Codex should not inspect their raw contents as context unless the package explicitly requires it.

Generated Shelly build/deploy artifacts under `build/` and `dep/s/ch/` are implementation truth when a task is about the exact deployed/built artifact, but they are not ordinary bootstrap context. Prefer source, package-run changelogs and function docs unless the task or package asks for artifact-level verification.

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
- `REPOSITORY_FILES.md` status: updated for tracked file path changes, or explicitly unchanged because no tracked files were added, removed or moved

## Source of truth

For completed packages, implementation and deploy artifacts remain the strongest truth. Package-run changelogs summarize the delta and help navigate to the relevant truth without broad scanning.
