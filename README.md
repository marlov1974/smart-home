# smart-home

G2 Smart Home source-of-truth repository.

This repository owns the next-generation whole-house control system: Mac, Home Assistant and Shelly.

## Mandatory AI bootstrap

For every new AI/chat/Codex session working on G2:

1. Read this `README.md`.
2. Read `memory/bootstrap-manifest.json`.
3. Read every file listed in the manifest `read_order`, in order.
4. If the task touches current Gen1 runtime behavior, also bootstrap `marlov1974/shelly`.
5. If any mandatory read fails, stop and report `BOOTSTRAP FAILED` with the missing file/step.

## G1/G2 boundary

`marlov1974/shelly` owns G1: current running Shelly/FTX runtime maintenance.

`marlov1974/smart-home` owns G2: whole-house control across FTX, VP1/VP2, floor heating/cooling, VVB, VVC, Mac, Home Assistant and Shelly.

Market simulation, spot-price forecasting labs and consumption-forecast experiments live in `marlov74/Market-Simulator` after `P0061`.

Do not treat G2 design or code as current G1 runtime behavior.

## Layout

Tracked repository paths are listed in [REPOSITORY_FILES.md](REPOSITORY_FILES.md) for GitHub/chat review flows that cannot enumerate files directly.

```text
memory/        durable solution understanding
requirements/ epics, features, stories and ordered packages
src/           development source code
dep/           deployable artifacts
tools/         checks, diagnostics and Codex helpers
tests/         unit, integration and fixtures
```

Deploy path abbreviations:

```text
dep/s/   Shelly deploy artifacts
dep/m/   Mac deploy artifacts
dep/ha/  Home Assistant deploy artifacts
```

Shelly devices should fetch only from `dep/s/`, not from `src/`.

## Package model

All implementation work is package-driven.

A package is an ordered whole-solution change version:

```text
P0001, P0002, P0003, ...
```

A package may update memory, requirements, code, deploy artifacts, tests and diagnostics.

Every code change must reference exactly one package id. Rollback is also a new forward-moving package.

Current bootstrap package:

```text
requirements/packages/P0001-bootstrap-smart-home-repo.md
```
