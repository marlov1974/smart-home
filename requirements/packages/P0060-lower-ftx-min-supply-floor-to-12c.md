# Package P0060: lower FTX minimum supply floor to 12 C

## Status
verified

## Package order
P0060

## Primary area
G2 / Shelly / FTX

## Label
G2-KANDIDAT

## Decision summary

Lower the absolute FTX minimum supply target floor from `14.0 C` to `12.0 C`.

P0059 removed the added dewpoint margin. P0060 further relaxes the absolute lower floor so cooling can target lower supply air when dewpoint and downstream logic allow it.

## Solution model

The FTX brain uses `TARGET_TO_HOUSE_MIN_C` in `feature-target.js` for:

- the lower floor in `min_supply_temp_c`
- clipping `target_to_house_c`

P0060 changes:

```text
TARGET_TO_HOUSE_MIN_C = 14.0
```

to:

```text
TARGET_TO_HOUSE_MIN_C = 12.0
```

The dewpoint calculation remains direct after P0059:

```text
min_supply_temp_c = max(dewpoint_house_c, TARGET_TO_HOUSE_MIN_C)
```

## Current behavior

The absolute minimum supply target is `14.0 C`.

## Problem

The operator wants the floor lowered to `12.0 C` after validating that the previous condensate assumptions were too conservative for the current installation.

## Target behavior

The FTX brain uses `12.0 C` as the absolute minimum supply target floor.

## Non-goals

- No live Shelly deploy.
- No Home Assistant changes.
- No change to dewpoint formula.
- No reintroduction of dewpoint safety margin.
- No deploy artifact generation.

## Invariants

- Keep the change package-scoped.
- Do not read or edit G1.
- Do not perform live writes.
- Shelly devices must still not fetch from `src/`.

## Knowledge updates

- Update FTX cooling-risk memory.
- Update Shelly FTX function catalog.

## Implementation updates

- Change `src/shelly/ftx/brain/feature-target.js`.
- Update focused source test expectations.

## Files to inspect

- `requirements/package-runs/P0059/CHANGELOG.md`
- `src/shelly/ftx/brain/feature-target.js`
- `src/shelly/ftx/brain/feature-thermal.js`
- `tests/mac/shelly_ftx/test_dewpoint_margin.py`
- `memory/physical/ftx/cooling-risk.md`
- `docs/functions/shelly/ftx-runtime-baseline.md`

## Files allowed to change

- `requirements/packages/P0060-lower-ftx-min-supply-floor-to-12c.md`
- `requirements/package-runs/P0060/**`
- `src/shelly/ftx/brain/feature-target.js`
- `tests/mac/shelly_ftx/test_dewpoint_margin.py`
- `memory/physical/ftx/cooling-risk.md`
- `docs/functions/shelly/ftx-runtime-baseline.md`
- `docs/functions/00-index.md`

## Forbidden changes

- No G1 repository changes.
- No live Shelly writes.
- No Home Assistant writes.
- No unrelated source, deploy or memory changes.

## Pre-implementation consistency review

Codex must write:

```text
requirements/package-runs/P0060/review.md
```

## Implementation design policy

Codex must write:

```text
requirements/package-runs/P0060/design.md
```

## Function design policy

Codex must write:

```text
requirements/package-runs/P0060/functions.md
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
requirements/package-runs/P0060/
```

## Test cases

### TC1: absolute floor is 12 C
Given the FTX brain target source
When inspected after P0060
Then it defines `TARGET_TO_HOUSE_MIN_C = 12.0`.

### TC2: old 14 C floor removed
Given the FTX brain target source
When inspected after P0060
Then it no longer defines `TARGET_TO_HOUSE_MIN_C = 14.0`.

### TC3: dewpoint still has no added margin
Given the FTX brain target source
When inspected after P0060
Then `min_supply_temp_c` still uses `max2(dewPointHouseC, TARGET_TO_HOUSE_MIN_C)`.

## Verification commands

```bash
python3 -m unittest tests.mac.shelly_ftx.test_dewpoint_margin
python3 -m unittest tests.mac.shelly_ftx.test_vvx_efficiency
python3 -m unittest discover tests/mac/tools
git diff --check
```

## Runtime health checks

Not applicable; no live runtime changes are allowed.

## Deployment plan

Commit and push only. This package does not authorize deploy or production activation.

## Rollback plan

Rollback is a later forward-moving package that raises the minimum floor again if needed.
