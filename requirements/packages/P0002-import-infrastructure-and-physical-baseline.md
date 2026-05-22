# Package P0002: Import infrastructure and physical baseline

## Status
implemented

## Package order
P0002

## Primary area
G2 memory / infrastructure / physical baseline

## Linked requirements

Epic:
- none yet

Features:
- none yet

User stories:
- none yet

## Decision summary

Import curated baseline facts from G1 into G2 instead of treating the old `shelly` repository as the active G2 source of truth.

Create a structure that separates:

- general infrastructure and reachability
- FTX physical facts
- heating/heat-pump/brine facts
- floor heating/cooling placeholders
- house/comfort placeholders

## Solution model

G2 memory separates identity/reachability from physical interpretation.

Rule:

```text
Device/IP/NAT identity -> memory/infrastructure/devices.md
Sensor channel meaning -> memory/physical/<domain>/
Physical model/calibration -> memory/physical/<domain>/
```

Infrastructure is domain-neutral. FTX, heating, floor and home folders own physical interpretation.

## Current behavior

Before this package, `smart-home` had only bootstrap-level memory and no migrated device/network/physical facts.

## Problem

Future G2 design needs known IP addresses, NAT rules, FTX hardware, sensor channel mappings, K-factors and heat-pump/brine baseline values without relying on legacy G1 files as active G2 truth.

## Target behavior

G2 has a curated imported baseline under `memory/infrastructure/` and `memory/physical/`.

## Non-goals

- No code changes.
- No deploy artifacts.
- No live device access.
- No new G2 control logic.
- No complete migration of all floor-cooling details; placeholders are created for later packages.

## Invariants

- G1 and G2 remain separated.
- G1 live runtime behavior remains owned by `marlov1974/shelly`.
- G2 physical facts should be curated and explicit, not blind copies of old notes.
- Bootstrap manifest must include mandatory context files needed for future reconstruction.

## Knowledge updates

Created:

- `memory/infrastructure/00-index.md`
- `memory/infrastructure/network.md`
- `memory/infrastructure/router-nat.md`
- `memory/infrastructure/devices.md`
- `memory/physical/00-index.md`
- `memory/physical/ftx/00-index.md`
- `memory/physical/ftx/devices.md`
- `memory/physical/ftx/sensors.md`
- `memory/physical/ftx/airflow.md`
- `memory/physical/ftx/temperatures.md`
- `memory/physical/ftx/cooling-risk.md`
- `memory/physical/heating/00-index.md`
- `memory/physical/heating/heat-pumps.md`
- `memory/physical/heating/brine.md`
- `memory/physical/heating/hot-water.md`
- `memory/physical/floor/00-index.md`
- `memory/physical/floor/floor-heating.md`
- `memory/physical/floor/floor-cooling.md`
- `memory/physical/floor/shunts-pumps-valves.md`
- `memory/physical/home/00-index.md`
- `memory/physical/home/rooms-zones.md`
- `memory/physical/home/comfort-sensors.md`

Updated:

- `memory/bootstrap-manifest.json`

## Implementation updates

None.

## Files to inspect

- `marlov1974/shelly/memory/ftx-digitalt/02-device-topology.md`
- `marlov1974/shelly/memory/ftx-fysiskt/*`
- `marlov1974/shelly/memory/house-control/02-heat-pump-operating-schedules.md`

## Files allowed to change

- `memory/infrastructure/**`
- `memory/physical/**`
- `memory/bootstrap-manifest.json`
- this package file

## Forbidden changes

- no source code changes
- no deploy artifact changes
- no live device writes
- no changes to G1 repository in this package

## Test cases

### TC1: Bootstrap includes imported mandatory context
Given a future G2 AI/Codex session
When it reads `memory/bootstrap-manifest.json`
Then infrastructure and physical baseline files are included in `read_order`.

### TC2: NAT rule is recoverable
Given an internal Shelly IP `192.168.77.40`
When reading `memory/infrastructure/router-nat.md`
Then the operator URL pattern resolves to `http://192.168.86.240:8040/`.

### TC3: FTX sensor mapping is recoverable
Given future G2 reasoning about FTX telemetry
When reading `memory/physical/ftx/temperatures.md`
Then the process/extract UNI mapping includes temperature:100-104 and their meanings.

### TC4: Heat pump sacred/summer behavior is recoverable
Given future G2 heat-pump planning
When reading `memory/physical/heating/heat-pumps.md`
Then VP1/VP2 command mappings, sacred block 00-02 and protected summer L0 are documented.

## Verification commands

```bash
git ls-files memory/infrastructure memory/physical requirements/packages/P0002-import-infrastructure-and-physical-baseline.md
```

Optional future check:

```bash
python tools/checks/check_bootstrap_manifest.py
```

## Deployment plan

No runtime deploy.

## Rollback plan

If this memory structure is wrong, create a new forward package that restructures or supersedes these files.

Because this is early repository memory and no runtime code depends on it yet, reverting P0002 commits is also possible before later packages depend on the structure.

## Expected Codex output

For validation, Codex should report:

- all created files
- whether every bootstrap manifest path exists
- any imported facts it considers ambiguous or needing source confirmation

## Completion notes

P0002 imported infrastructure, FTX physical baseline, heat-pump/brine baseline and placeholders for floor and home physical context.
