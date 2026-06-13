# Package P0057: import G1 FTX runtime as G2 baseline

## Status
verified

## Package order
P0057

## Primary area
G2 / Shelly / FTX / migration

## Label
G2-KANDIDAT

## Decision summary

The current G1 FTX runtime has matured enough to become the first G2 FTX runtime baseline.

G2 should import the current G1 FTX Shelly runtime source into `marlov1974/smart-home` so future FTX runtime inspection, design and package work can use this repository as the source of truth.

G1 repository state used as import source:

```text
repo: marlov1974/shelly
branch/status: main...origin/main, clean
commit: 761cc4bc1c527d6bdffa0a0783f0cfd1761040f4
summary: Make VVX executor thermal-local
```

## Solution model

This package is a repository migration/import package, not a production activation package.

The package imports the G1 FTX runtime into G2 under a G2-owned Shelly source area. Imported source must preserve enough structure to reconstruct the current runtime behavior:

- FTX brain modules
- FTX state/performance modules
- shared Shelly runtime helpers used by brain/state recipes
- local device scripts for dampers, supply fan, extract fan, heat dimmer, cool dimmer and VVX
- recipe/manifest metadata needed to understand intended script composition
- concise G2 memory describing that the imported runtime is now the G2 baseline for future source inspection

After this package, future Codex/ChatGPT work should inspect G2 imported source first for FTX runtime behavior. G1 may still be consulted only as historical provenance or when explicitly comparing against pre-import behavior.

## Current behavior

G2 currently contains early Shelly examples and proofs, but the current FTX runtime lives in `marlov1974/shelly`.

Codex has to inspect G1 to answer questions about current FTX/VVX logic.

## Problem

The operator has decided that the current G1 FTX runtime is now mature enough to be treated as the first G2 runtime baseline. Continuing to inspect G1 by default would keep the source of truth split across repositories.

## Target behavior

- Current FTX runtime source is available in `marlov1974/smart-home`.
- Imported files make provenance explicit.
- G2 memory states that FTX runtime inspection should use the imported G2 source after P0057.
- No live device writes are performed.
- No production activation is performed.
- No runtime behavior changes are made during the import.

## Non-goals

- No live Shelly deploy.
- No Home Assistant production change.
- No Mac service runtime change.
- No behavior refactor.
- No functional fix to VVX efficiency or other FTX logic in this package.
- No removal or modification of the G1 repository.
- No broad reformatting of imported G1 runtime code.

## Invariants

- G1 and G2 repository histories remain separate.
- Imported code must preserve original G1 behavior unless a later package changes it deliberately.
- Shelly deploy artifacts must live under `dep/s/` when generated.
- Shelly devices must not fetch from `src/`.
- This package is commit/push only after verification; it does not authorize production activation.

## Knowledge updates

- Update G2 memory for the FTX runtime source-of-truth decision.
- Add package-run evidence under `requirements/package-runs/P0057/`.
- Consider knowhow promotion for the migration-source decision.

## Implementation updates

- Add imported FTX Shelly runtime source under `src/shelly/ftx/`.
- Add package-scoped import manifest/provenance notes.
- Add or update durable function/catalog documentation for the imported FTX runtime at a high level.
- Do not generate deploy chunks unless the package design finds an existing deterministic G2 build path that can validate the import without changing behavior.

## Files to inspect

- `README.md`
- `memory/bootstrap-manifest.json`
- manifest `read_order`
- `memory/03-g1-g2-boundary.md`
- `memory/physical/ftx/**`
- `memory/device-management/source-build-deploy-layers.md`
- `src/shelly/**`
- `dep/s/**`
- `docs/functions/shelly/**`
- G1 import source paths:
  - `/Users/marcus.lovenstad/dev/shelly/rt/common/**`
  - `/Users/marcus.lovenstad/dev/shelly/rt/brain/**`
  - `/Users/marcus.lovenstad/dev/shelly/rt/state/**`
  - `/Users/marcus.lovenstad/dev/shelly/rt/scripts/{dampers,supply-fan,extract-fan,heat-dimmer,cool-dimmer,vvx}/**`
  - `/Users/marcus.lovenstad/dev/shelly/rt/recipes/**`

## Files allowed to change

- `requirements/packages/P0057-import-g1-ftx-runtime-as-g2-baseline.md`
- `requirements/package-runs/P0057/**`
- `src/shelly/ftx/**`
- `docs/functions/shelly/**`
- `memory/03-g1-g2-boundary.md`
- `memory/physical/ftx/**`
- `memory/knowhow/**`

## Forbidden changes

- No G1 repository edits.
- No live Shelly writes.
- No Home Assistant config writes.
- No production activation.
- No unrelated spot-price, Mac lab or energy-market changes.
- No generated deploy artifacts unless produced deterministically and justified in design.

## Pre-implementation consistency review

Before editing import targets, Codex must classify the package as PASS/WARN/STOP and store review evidence in:

```text
requirements/package-runs/P0057/review.md
```

## Implementation design policy

Codex must create:

```text
requirements/package-runs/P0057/design.md
```

The design must cover:

- import scope
- provenance
- source layout
- whether deploy artifacts are generated or intentionally deferred
- memory/source-of-truth update
- verification strategy
- risks and uncertainties

## Function design policy

Codex must create:

```text
requirements/package-runs/P0057/functions.md
```

Because this is a source import, function design may document imported runtime entry points and safety-critical unchanged functions rather than new function behavior.

## Context-reset phase gates

Use the normal package flow:

```text
bootstrap -> review -> design -> function design -> implementation -> verification -> final evidence
```

## Live test/debug policy

Live testing allowed:
no

Live write actions allowed:
no

Shelly log capture required:
no

Max implementation/debug attempts:
1

## Evidence and learning policy

Package evidence belongs under:

```text
requirements/package-runs/P0057/
```

Expected evidence:

```text
review.md
design.md
functions.md
CHANGELOG.md
```

## Test cases

### TC1: import provenance exists
Given the G2 repository after P0057
When a reader inspects the package evidence
Then it records the G1 commit and source paths used for the import.

### TC2: FTX source exists in G2
Given the G2 repository after P0057
When a reader searches `src/shelly/ftx`
Then brain, state, common, device scripts and recipes are present.

### TC3: source-of-truth memory updated
Given future FTX runtime questions
When Codex reads G2 memory
Then it should inspect G2 imported FTX source first instead of defaulting to G1.

### TC4: no live changes
Given this package is an import package
When verification completes
Then there are no live Shelly, Home Assistant or G1 repository writes.

## Verification commands

```bash
git status --short
find src/shelly/ftx -type f | sort
git diff --check
```

Optional when relevant:

```bash
python3 -m unittest discover tests/mac/tools
```

## Runtime health checks

Not applicable; no live runtime changes are allowed.

## Deployment plan

Commit and push only after verification. This package does not authorize staged deploy or production activation.

## Rollback plan

Rollback is a later forward-moving package that supersedes or removes the imported baseline.

## Expected Codex output

- PASS/WARN/STOP review
- design path
- functions path
- imported source paths
- memory/docs changed
- verification commands and results
- commit SHA after push if verification passes
- uncertainty
- diff summary
