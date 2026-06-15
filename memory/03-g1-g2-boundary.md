# G1 / G2 Boundary

## Current production truth

G2 is now the production Smart Home control system.

Current production source of truth:

```text
marlov1974/smart-home
```

This repository owns the current production runtime, deploy artifacts, Home Assistant configuration, Mac tooling and durable solution memory for the house.

## G1

G1 was the original running Shelly/FTX runtime and remains in:

```text
marlov1974/shelly
```

G1 is now retired. Treat `marlov1974/shelly` as historical provenance and an archive of Gen1 implementation behavior, not as current production truth.

Use G1 only when a task explicitly asks for:

- historical Gen1 behavior
- pre-migration comparison
- provenance for code or physical facts that were imported into G2
- analysis of why old G1 behavior differed from current G2

Do not use G1 for new runtime changes, production fixes or current behavior claims unless the question is explicitly historical.

## P0057 FTX runtime migration

P0057 is the explicit migration decision for FTX runtime source-of-truth.

The G1 FTX runtime from commit `761cc4bc1c527d6bdffa0a0783f0cfd1761040f4` was imported into G2 under:

```text
src/shelly/ftx/
```

After P0057, future questions about FTX runtime behavior inspect the G2 source first. The G1 repository is historical provenance unless a task explicitly asks for pre-import comparison.

P0057 itself did not perform production activation, live deploy or behavior changes. Later packages moved G2 forward into live/production operation.

## G2

G2 lives in:

```text
marlov1974/smart-home
```

G2 coordinates Mac, Home Assistant and Shelly code across the whole house.

G2 is no longer only a future design or pre-production candidate. Treat G2 implementation and deploy artifacts as the current production source of truth unless a specific package or evidence file says a feature remains lab-only, disabled, staged or not production-active.

## Shared/historical knowledge

Some physical facts were historically shared between G1 and G2:

- FTX hardware
- airflow/pressure calibration
- temperature sensor placement
- network/IP facts
- heat pump physical mappings

Shared facts may be copied or imported into this repository through ordered packages.

Do not blindly copy historical G1 notes into G2. G2 memory should contain decided, curated solution knowledge.

## Bootstrap rule

When working on current FTX runtime behavior, bootstrap this repository and inspect `src/shelly/ftx/` first.

When working on G2 design, implementation, deploy, operations, Home Assistant, Mac tooling or current production behavior, bootstrap this repository.

When a task explicitly asks for historical G1 behavior or pre-G2 comparison, inspect `marlov1974/shelly` only for that historical/provenance scope and keep historical G1 claims separate from current G2 production claims.
