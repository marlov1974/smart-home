# G1 / G2 Boundary

## G1

G1 was the original running Shelly/FTX runtime and remains in:

```text
marlov1974/shelly
```

G1 may still be maintained for stability, bug fixes and safe operation when explicitly needed.

G1 should not receive broad G2 architecture unless there is a deliberate migration decision.

## P0057 FTX runtime migration

P0057 is the explicit migration decision for FTX runtime source-of-truth.

The current G1 FTX runtime from commit `761cc4bc1c527d6bdffa0a0783f0cfd1761040f4` was imported into G2 under:

```text
src/shelly/ftx/
```

After P0057, future questions about FTX runtime behavior should inspect the G2 imported source first. The G1 repository is historical provenance unless a package explicitly asks for pre-import comparison or current G1 maintenance.

P0057 did not perform production activation, live deploy or behavior changes.

## G2

G2 is the new Smart Home solution and lives in:

```text
marlov1974/smart-home
```

G2 coordinates Mac, Home Assistant and Shelly code across the whole house.

## Shared knowledge

Some physical facts are shared between G1 and G2:

- FTX hardware
- airflow/pressure calibration
- temperature sensor placement
- network/IP facts
- heat pump physical mappings

Shared facts may be copied or imported into this repository through ordered packages.

Do not blindly copy historical G1 notes into G2. G2 memory should contain decided, curated solution knowledge.

## Bootstrap rule

When working on post-P0057 FTX runtime behavior, bootstrap this repository and inspect `src/shelly/ftx/` first.

When working on historical G1 runtime behavior or explicit G1 maintenance, bootstrap `marlov1974/shelly`.

When working on G2 design or implementation, bootstrap this repository.

When a task crosses the boundary, bootstrap both repositories and keep the claims separated.
