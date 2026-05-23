# Package P0009: Shelly build wrapper and metadata

## Status
implemented

## Package order
P0009

## Primary area
G2 / Mac tooling / Shelly deploy generation

## Decision summary

P0008 created deterministic Shelly build/deploy tooling, but ChatGPT review found that the built fixture script is plain concatenated source. The intended wrapper/header behavior was not written durably enough into the package, memory or tests.

P0009 makes wrapper and metadata behavior explicit repository truth and implements it in the P0008 build tool.

## Solution model

Built Shelly scripts should not be plain concatenation. Build output should contain:

1. a generated metadata header
2. an IIFE-style wrapper around assembled source
3. strict mode inside the wrapper

Deploy chunks remain generated transport artifacts created from the complete built script.

## Current behavior

`src/mac/tools/shelly_build/` builds source files into `build/shelly/fixture/hello.js` by concatenating source text in manifest order.

The generated built script is runnable, but lacks generated metadata header and IIFE wrapper.

P0008 findings are stored in:

```text
requirements/package-runs/P0008/findings.md
```

## Problem

A chat-level design expectation was not durable enough for Codex. The package did not explicitly require wrapper/header behavior, so Codex correctly followed the documented package and memory instead of the transient chat expectation.

## Target behavior

Update the Shelly build tool so generated built scripts include:

- generated-file header
- role metadata
- source manifest metadata
- package/tool metadata when practical
- IIFE-style wrapper
- `use strict` inside the wrapper
- original source content inside the wrapper

The exact metadata fields may be decided in `requirements/package-runs/P0009/design.md`, but tests must verify the presence of header, role/manifest metadata, wrapper and strict mode.

Generated deploy chunks and recipes must be rebuilt from the new built script.

## Non-goals

- No Shelly installer implementation.
- No live Shelly device access.
- No real FTX runtime migration.
- No Home Assistant changes.
- No external Python packages.
- No broad refactor outside the existing Shelly build tool.

## Invariants

- Python standard library only.
- Shelly devices fetch only from `dep/s/`.
- Deploy chunks are generated artifacts.
- Build is deterministic.
- Generated chunks reconstruct the built script exactly.
- Existing P0008 validation behavior must remain.
- Wrapper/header behavior must be documented and test-covered.

## Knowledge updates

Update:

- `memory/device-management/source-build-deploy-layers.md`
- `docs/functions/mac/shelly-build-tool.md`
- `requirements/package-runs/P0009/` evidence

## Files to inspect

- `AGENTS.md`
- `memory/04-codex-workflow.md`
- `memory/05-package-lifecycle.md`
- `memory/device-management/source-build-deploy-layers.md`
- `requirements/package-runs/P0008/findings.md`
- `requirements/packages/P0008-g2-shelly-build-deploy-tools.md`
- `src/mac/tools/shelly_build/**`
- `tests/mac/tools/shelly_build/**`
- `src/shelly/fixture/**`
- `build/shelly/fixture/hello.js`
- `dep/s/ch/hello/**`
- `dep/s/rec/hello.json`
- `docs/functions/mac/shelly-build-tool.md`

## Files allowed to change

- `src/mac/tools/shelly_build/**`
- `tests/mac/tools/shelly_build/**`
- `build/shelly/fixture/hello.js`
- `dep/s/ch/hello/**`
- `dep/s/rec/hello.json`
- `docs/functions/mac/shelly-build-tool.md`
- `memory/device-management/source-build-deploy-layers.md`
- `requirements/package-runs/P0009/**`
- `requirements/packages/P0009-shelly-build-wrapper-and-metadata.md`

## Forbidden changes

- no G1 repository changes
- no live device changes
- no installer implementation
- no real FTX runtime source changes
- no external Python package dependencies
- no unrelated cleanup or broad refactor

## Codex phase requirements

Codex must create these before implementation:

```text
requirements/package-runs/P0009/review.md
requirements/package-runs/P0009/design.md
requirements/package-runs/P0009/functions.md
```

Use the P0007 phase-gate model.

## Test cases

### TC1: Built script has generated header
Given the fixture manifest
When the build command runs
Then `build/shelly/fixture/hello.js` starts with a generated metadata header.

### TC2: Built script has role and manifest metadata
Given the fixture manifest
When the build command runs
Then the built script contains the role name and manifest reference in generated metadata.

### TC3: Built script is IIFE-wrapped
Given the fixture manifest
When the build command runs
Then source content is inside an IIFE-style wrapper.

### TC4: Built script uses strict mode
Given the fixture manifest
When the build command runs
Then `use strict` appears inside the wrapper.

### TC5: Existing build and validation tests still pass
Given P0008 functionality
When tests run
Then chunk generation, reconstruction, missing chunk, oversize chunk and stdlib-only tests still pass.

### TC6: Generated deploy artifacts are rebuilt
Given wrapper/header changes the built script
When build runs
Then `dep/s/ch/hello/01.js` and `dep/s/rec/hello.json` reflect the rebuilt output and validate successfully.

## Verification commands

Codex may refine commands in `design.md`, but must run equivalents of:

```bash
python3 -m unittest discover tests/mac/tools/shelly_build
python3 -m src.mac.tools.shelly_build build --manifest src/shelly/fixture/manifest.json --build-root build/shelly/fixture --dep-root dep/s
python3 -m src.mac.tools.shelly_build validate --build-root build/shelly/fixture --dep-root dep/s --role hello
git diff --check
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
- commit SHA after push
- uncertainty
- diff summary

## Completion notes

P0009 implemented generated Shelly built-script metadata and IIFE strict-mode wrapping in the P0008 build tool.

Updated:

- `src/mac/tools/shelly_build/core.py`
- `tests/mac/tools/shelly_build/test_core.py`
- `build/shelly/fixture/hello.js`
- `dep/s/ch/hello/01.js`
- `dep/s/rec/hello.json`
- `memory/device-management/source-build-deploy-layers.md`
- `docs/functions/mac/shelly-build-tool.md`
- `requirements/package-runs/P0009/**`

Verification passed:

```bash
python3 -m unittest discover tests/mac/tools/shelly_build
python3 -m src.mac.tools.shelly_build build --manifest src/shelly/fixture/manifest.json --build-root build/shelly/fixture --dep-root dep/s
python3 -m src.mac.tools.shelly_build validate --build-root build/shelly/fixture --dep-root dep/s --role hello
git diff --check
```

No live testing or live writes were performed.
