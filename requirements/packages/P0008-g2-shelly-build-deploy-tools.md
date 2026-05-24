# Package P0008: G2 Shelly build/deploy tools

## Status
implemented

## Package order
P0008

## Primary area
G2 / Mac tooling / Shelly deploy generation

## Decision summary

Build/deploy tooling must exist before the G2 Shelly installer is implemented.

P0008 creates deterministic Python tooling that turns logical Shelly source into complete built scripts and numeric deploy chunks.

## Solution model

```text
src/shelly/     logical source
build/shelly/   complete built scripts
dep/s/          deployable Shelly artifacts
```

Generated chunks use numeric names:

```text
dep/s/ch/<role>/01.js
dep/s/ch/<role>/02.js
dep/s/rec/<role>.json
```

Recipe format:

```json
{"v":1,"n":2}
```

## Target behavior

- read a script build manifest
- include explicit helper files and role source files
- create one complete runnable Shelly script
- split the built script into numeric chunks
- create recipe JSON with chunk count
- validate that chunk concatenation equals the built script
- validate chunk size limits
- include tests and a minimal fixture

## Non-goals

- no Shelly installer
- no live device access
- no real FTX migration
- no external Python dependencies

## Invariants

- Python standard library only
- Shelly devices fetch from `dep/s/` only
- chunks are generated artifacts
- build is deterministic
- chunks reconstruct the built script exactly

## Files to inspect

- `AGENTS.md`
- `memory/04-codex-workflow.md`
- `memory/device-management/source-build-deploy-layers.md`
- `memory/device-management/mac-layer.md`
- `memory/device-management/shelly-deploy-structure.md`
- `requirements/packages/P0006-device-management-and-deploy-architecture.md`
- `requirements/packages/P0007-codex-phased-package-build-process.md`

## Files allowed to change

- `src/mac/tools/shelly_build/**`
- `tests/mac/tools/shelly_build/**`
- `src/shelly/fixture/**`
- `build/shelly/fixture/**`
- `dep/s/ch/hello/**`
- `dep/s/rec/hello.json`
- `docs/functions/**`
- `requirements/package-runs/P0008/**`

## Forbidden changes

- no G1 repository changes
- no live device changes
- no installer implementation
- no real FTX runtime source changes
- no manual edits to generated chunks after build

## Codex phase requirements

Codex must create these before implementation:

```text
requirements/package-runs/P0008/review.md
requirements/package-runs/P0008/design.md
requirements/package-runs/P0008/functions.md
```

Use the P0007 phase-gate model.

## Test cases

### TC1: Build fixture script
Given a fixture manifest, the tool creates one built script.

### TC2: Chunk generation
Given a built script, the tool creates numeric chunks and a recipe.

### TC3: Chunk reconstruction
Generated chunks concatenate exactly to the built script.

### TC4: Validation failures
Validation fails clearly for missing chunks or oversize chunks.

### TC5: Standard library only
The tooling uses Python standard library only.

## Verification commands

Codex must define final commands in `design.md`. Minimum expected:

```bash
python3 -m unittest discover tests/mac/tools/shelly_build
```

## Live test/debug policy

Live testing allowed: no

Live write actions allowed: no

Shelly log capture required: no

Max implementation/debug attempts: 3

## Expected Codex output

- PASS/WARN/STOP review
- design path
- functions path
- files changed
- tests run
- verification results
- uncertainty
- diff summary

## Completion notes

P0008 implemented the initial deterministic Shelly build/deploy generation tool used by later packages.

It created the baseline Mac-side Shelly build path:

- `src/mac/tools/shelly_build/**`
- `tests/mac/tools/shelly_build/**`
- fixture Shelly source/build/deploy artifacts
- package-run evidence under `requirements/package-runs/P0008/**`

Later packages refined and corrected the P0008 tool:

- P0009 added generated metadata header, IIFE wrapper and strict mode.
- P0010/P0011/P0013 established that Mac direct live deploy reads the complete built script and uses in-memory RPC upload chunks, not repo deploy chunks, as the direct deploy transport source.

P0008 remains the package that introduced the build/deploy generation baseline.