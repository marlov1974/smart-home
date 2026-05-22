# G1 / G2 Boundary

## G1

G1 is the current running Shelly/FTX runtime and remains in:

```text
marlov1974/shelly
```

G1 is maintained for stability, bug fixes and safe operation until explicit migration.

G1 should not receive broad G2 architecture unless there is a deliberate migration decision.

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

When working on current G1 runtime behavior, bootstrap `marlov1974/shelly`.

When working on G2 design or implementation, bootstrap this repository.

When a task crosses the boundary, bootstrap both repositories and keep the claims separated.
