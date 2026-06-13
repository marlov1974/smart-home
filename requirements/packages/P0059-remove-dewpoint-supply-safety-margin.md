# Package P0059: remove dewpoint supply safety margin

## Status
verified

## Package order
P0059

## Primary area
G2 / Shelly / FTX

## Label
G2-KANDIDAT

## Decision summary

Remove the extra safety margin added on top of calculated house dewpoint when deriving the minimum allowed FTX supply temperature.

The operator has tested the physical installation and found the ventilation pipe surface remains a few degrees warmer than the air inside the pipe, so condensation does not occur on the pipe even when the air in the pipe is a couple of degrees colder than the calculated dewpoint. The previous extra margin is therefore unnecessarily conservative.

## Solution model

The FTX brain computes:

```text
dewpoint_house_c
min_supply_temp_c
target_to_house_c
```

Before P0059, `min_supply_temp_c` used:

```text
max(dewpoint_house_c + 1.0 C, TARGET_TO_HOUSE_MIN_C)
```

P0059 changes this to:

```text
max(dewpoint_house_c, TARGET_TO_HOUSE_MIN_C)
```

The absolute lower floor `TARGET_TO_HOUSE_MIN_C = 14.0` remains unchanged.

## Current behavior

`src/shelly/ftx/brain/feature-target.js` defines `DEWPOINT_SUPPLY_MARGIN_C = 1.0` and adds it to the calculated dewpoint before setting `ctx.sig.min_supply_temp_c`.

## Problem

The margin blocks useful cooling despite physical testing showing the pipe surface temperature gives enough real-world buffer.

## Target behavior

`min_supply_temp_c` should be based on the calculated dewpoint itself, without an added safety margin.

## Non-goals

- No live Shelly deploy.
- No Home Assistant changes.
- No change to dewpoint formula constants.
- No change to absolute minimum supply target `14.0 C`.
- No change to cooling battery actuator logic beyond the lower target limit.
- No deploy artifact generation.

## Invariants

- Keep the change package-scoped.
- Do not read or edit G1.
- Do not perform live writes.
- Shelly devices must still not fetch from `src/`.

## Knowledge updates

- Update FTX cooling-risk memory with the operator's pipe-surface observation.
- Update Shelly FTX function catalog.

## Implementation updates

- Change `src/shelly/ftx/brain/feature-target.js`.
- Add focused test coverage for removal of the margin.

## Files to inspect

- `requirements/package-runs/P0057/CHANGELOG.md`
- `src/shelly/ftx/brain/feature-target.js`
- `src/shelly/ftx/brain/feature-thermal.js`
- `memory/physical/ftx/cooling-risk.md`
- `docs/functions/shelly/ftx-runtime-baseline.md`

## Files allowed to change

- `requirements/packages/P0059-remove-dewpoint-supply-safety-margin.md`
- `requirements/package-runs/P0059/**`
- `src/shelly/ftx/brain/feature-target.js`
- `tests/mac/shelly_ftx/**`
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
requirements/package-runs/P0059/review.md
```

## Implementation design policy

Codex must write:

```text
requirements/package-runs/P0059/design.md
```

## Function design policy

Codex must write:

```text
requirements/package-runs/P0059/functions.md
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
requirements/package-runs/P0059/
```

## Test cases

### TC1: margin constant removed
Given the FTX brain target source
When inspected after P0059
Then it no longer defines or uses `DEWPOINT_SUPPLY_MARGIN_C`.

### TC2: minimum supply uses dewpoint directly
Given the FTX brain target source
When inspected after P0059
Then `min_supply_temp_c` is derived from `max2(dewPointHouseC, TARGET_TO_HOUSE_MIN_C)`.

### TC3: absolute floor remains
Given the FTX brain target source
When inspected after P0059
Then `TARGET_TO_HOUSE_MIN_C = 14.0` remains unchanged.

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

Rollback is a later forward-moving package that reintroduces a margin or another condensate constraint if physical testing shows it is needed.
