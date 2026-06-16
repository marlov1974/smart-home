# Package P0067: HA FTX Industrial SVG

## Status
planned

## Package order
P0067

## Primary area
Home Assistant / documentation

## Label
G2-KANDIDAT

## Linked requirements

Epic:
- E_HA_VISUALIZATION

Features:
- F_FTX_DASHBOARD

User stories:
- US_FTX_VISUAL_IDENTITY

## Decision summary

Create a Home Assistant-compatible SVG illustration for the FTX system with a classic industrial look and black background.

## Solution model

Home Assistant dashboard source lives under `src/ha/`. Deployable Home Assistant files live under `dep/ha/`. Static HA assets should follow the same source/deploy pairing until a more formal HA build/deploy step exists.

## Current behavior

The FTX dashboard exists as YAML in `src/ha/dashboards/ftx.yaml` and `dep/ha/dashboards/ftx.yaml`. There is no tracked Home Assistant SVG asset for FTX.

## Problem

The dashboard lacks a dedicated visual FTX asset that ChatGPT/Codex can reference and evolve.

## Target behavior

The repository contains a tracked SVG asset:

- black background
- industrial/classic ventilation cabinet look
- visible supply/extract ducts, fan elements, VVX/core section and simple telemetry labels
- valid XML/SVG
- source and deploy copies match

## Non-goals

- No live Home Assistant write.
- No dashboard card wiring unless requested later.
- No Shelly/Mac runtime behavior changes.
- No generated bitmap image.

## Invariants

- Keep G2 as source of truth.
- Keep source/deploy HA files synchronized.
- Update `REPOSITORY_FILES.md` because tracked files are added.

## Knowledge updates

None.

## Implementation updates

- Add `src/ha/assets/ftx-industrial.svg`.
- Add matching `dep/ha/assets/ftx-industrial.svg`.
- Add HA asset unit coverage.
- Update package-run evidence.
- Update `REPOSITORY_FILES.md`.

## Files to inspect

- `README.md`
- `memory/bootstrap-manifest.json`
- manifest `read_order`
- `REPOSITORY_FILES.md`
- `src/ha/dashboards/ftx.yaml`
- `dep/ha/dashboards/ftx.yaml`
- `tests/mac/ha/test_ftx_dashboard.py`

## Files allowed to change

- `src/ha/assets/ftx-industrial.svg`
- `dep/ha/assets/ftx-industrial.svg`
- `tests/mac/ha/test_ftx_dashboard.py`
- `requirements/packages/P0067-ha-ftx-industrial-svg.md`
- `requirements/package-runs/P0067/*`
- `REPOSITORY_FILES.md`

## Forbidden changes

- Shelly runtime/source/deploy changes.
- Mac services/tools changes.
- Live device or Home Assistant writes.
- G1 repository changes.

## Pre-implementation consistency review

Before editing, Codex must classify the package as PASS/WARN/STOP and store useful review evidence in `requirements/package-runs/P0067/review.md`.

## Implementation design policy

For this asset package, create package-scoped design in `requirements/package-runs/P0067/design.md` before implementation.

## Function design policy

No runtime functions are expected. If test helpers are changed, record them in `requirements/package-runs/P0067/functions.md`.

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

Package evidence belongs under `requirements/package-runs/P0067/`.

## Test cases

### TC1: Deploy asset matches source
Given the FTX SVG exists in source and deploy HA areas
When the HA tests run
Then both files are byte-identical.

### TC2: SVG parses
Given the FTX SVG asset
When parsed as XML
Then it has an SVG root with a `viewBox`.

### TC3: SVG keeps requested visual contract
Given the FTX SVG asset
When inspected by tests
Then it contains a black background and core FTX visual labels.

## Verification commands

```bash
python3 -m unittest tests.mac.ha.test_ftx_dashboard
git diff --check
```

## Runtime health checks

Not applicable.

## Deployment plan

Commit and push the repository asset only. No live Home Assistant deployment in this package.

## Rollback plan

Rollback is a future forward-moving package that removes or replaces the asset.
