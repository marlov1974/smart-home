# G2 Design Principles

## Package-driven development

Every implementation change belongs to exactly one ordered package:

```text
P0001, P0002, P0003, ...
```

A package is the atomic solution-version unit. It may update memory, requirements, source, deploy artifacts, tests and diagnostics.

Rollback is also a new forward-moving package.

## Requirements do not mirror code structure

Requirements are organized by intent and behavior:

```text
Epic -> Feature -> User Story -> Package
```

Code is organized by runtime/environment:

```text
src/mac
src/home-assistant
src/shelly
src/shared
```

A feature or package may span multiple scripts, devices and environments.

## Determinism and observability

Prefer deterministic logic, explicit state and visible failures.

Avoid broad defensive normalizers that hide bugs. Use explicit fallback behavior for missing telemetry, unavailable services or stale external inputs.

## Local hardware safety

Devices that directly control hardware should have conservative local fallback/default behavior.

Remote planners and optimizers may improve comfort/cost, but local hardware controllers must remain safe if external control disappears.

## Separation of planning and actuation

Planning can happen on Mac or Home Assistant.

Slow equipment should not be constantly replanned by fast loops.

Shelly edge code should stay small, deterministic and focused on local control/application.

## Testability

Every package must define test cases and verification commands.

Codex must run or explicitly report why it could not run them.
