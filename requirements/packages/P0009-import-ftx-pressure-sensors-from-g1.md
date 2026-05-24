# Package P0009: Import FTX pressure sensors from G1

## Status
implemented

## Package order
P0009

## Primary area
G2 memory / FTX physical sensors

## Linked requirements

Epic:
- none yet

Features:
- none yet

User stories:
- none yet

## Decision summary

Import the identified FTX pressure sensor details from the G1 physical hardware inventory into G2 memory.

The pressure sensors are:

```text
Manufacturer: Siemens
Model: QBM2030-5
Quantity: 2
Role: supply and extract differential pressure measurement
Signal: 0-10 V pressure measurement to Shelly Plus UNI
```

## Solution model

G2 already documented FTX pressure roles for `ftx-supply-uni` and `ftx-extract-uni`, but not the pressure sensor model.

This package updates G2 FTX sensor memory so future G2 design can see both:

- the Shelly/UNI source of each pressure signal
- the physical pressure sensor model and signal type
- the open checks that still require physical/config confirmation

## Current behavior

`memory/physical/ftx/sensors.md` listed supply-side and extract-side pressure roles but did not identify the pressure sensor model.

## Problem

Future G2 airflow and FTX work needs the pressure sensor hardware identity without re-opening G1 memory.

## Target behavior

G2 FTX sensor memory documents Siemens QBM2030-5 pressure sensors for supply and extract differential pressure measurement.

## Non-goals

- No runtime code changes.
- No deploy artifact changes.
- No live device access.
- No change to current G1 runtime behavior.
- No claim that the exact measurement range interpretation has been confirmed.

## Invariants

- G1 remains the source of truth for current running Gen1 runtime behavior.
- G2 memory should contain curated physical facts needed for future design.
- Pressure measurements must be tied to physical point and method.
- Do not mix pressure at stoss, fan differential pressure, duct/static pressure and house differential pressure.

## Knowledge updates

Updated:

- `memory/physical/ftx/sensors.md`
- `memory/bootstrap-manifest.json`

Created:

- `requirements/packages/P0009-import-ftx-pressure-sensors-from-g1.md`

## Implementation updates

None.

## Files inspected

G1:

- `marlov1974/shelly/memory/ftx-fysiskt/02-hardware-inventory.md`
- `marlov1974/shelly/memory/ftx-fysiskt/03-airflow-and-pressure-model.md`

G2:

- `memory/physical/ftx/sensors.md`
- `memory/bootstrap-manifest.json`

## Files allowed to change

- `memory/physical/ftx/sensors.md`
- `memory/bootstrap-manifest.json`
- this package file

## Forbidden changes

- no source code changes
- no deploy artifact changes
- no live device writes
- no G1 repository changes

## Pre-implementation consistency review

PASS.

The G1 hardware inventory explicitly identifies Siemens QBM2030-5 pressure sensors and states their role/signal. G2 already owns curated physical facts for future design, so importing this model detail is consistent with P0002 and the G1/G2 boundary.

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

No package-run evidence required for this small documentation-only memory import.

## Test cases

### TC1: Pressure sensor model is recoverable
Given future G2 FTX design work
When reading `memory/physical/ftx/sensors.md`
Then the supply and extract pressure sensor model is documented as Siemens QBM2030-5.

### TC2: Open measurement-range uncertainty is preserved
Given future calibration work
When reading `memory/physical/ftx/sensors.md`
Then it does not falsely claim exact QBM2030-5 range/config interpretation is confirmed.

### TC3: Measurement caution is recoverable
Given future pressure/airflow calibration work
When reading `memory/physical/ftx/sensors.md`
Then it warns not to mix stoss pressure, fan pressure, duct/static pressure and house differential pressure.

## Verification commands

```bash
git grep -n "QBM2030-5" memory/physical/ftx/sensors.md requirements/packages/P0009-import-ftx-pressure-sensors-from-g1.md
git grep -n "P0009-import-ftx-pressure-sensors-from-g1" memory/bootstrap-manifest.json
```

## Runtime health checks

No live runtime test.

## Deployment plan

No runtime deploy.

## Rollback plan

If the imported pressure sensor detail is later found wrong, create a new forward package that corrects or supersedes this memory.

## Expected Codex output
- consistency review result: PASS/WARN/STOP
- files changed
- tests run
- verification results
- uncertainty / skipped checks
- diff summary

## Completion notes

Imported Siemens QBM2030-5 pressure sensor details and pressure-measurement caution from G1 physical memory into G2 FTX sensor memory.
