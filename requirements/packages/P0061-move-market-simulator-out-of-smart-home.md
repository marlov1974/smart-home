# P0061 - Move market simulator out of smart-home

## Intent

Move spot price forecasting, consumption forecasting, weather/market datasets and related market-simulation lab artifacts from G2 Smart Home into the separate `marlov74/Market-Simulator` repository.

The goal is to keep G2 focused on smart-home runtime, device control, Home Assistant integration and Shelly/FTX work.

## Scope

Move to `Market-Simulator`:

- Mac market/data services for spot history, spot forecast, weather history, temperature normalization, ML model and diagnostics.
- Weekly home optimizer POC because it is a market/energy simulation lab, not current G2 runtime.
- Market-simulation tests, fixtures and local data under `data/spot` and `data/calendar`.
- Cross-package function docs and memory/planning docs that describe market-simulation behavior.
- Historical market package specifications and package-run evidence for P0017-P0025 and P0030-P0056.

Keep in G2:

- Shelly deploy artifacts and runtime code unless a later package explicitly removes or migrates them.
- Local operator, MCP, Home Assistant, FTX and device-management code.
- Package evidence for this cleanup package.

## Safety

No live devices may be written.

No production activation is allowed.

This package authorizes commit/push only after verification passes.

## Verification

- G2 bootstrap files must remain readable.
- G2 remaining tests for FTX and local operator/tooling must pass.
- Market-Simulator must contain the migrated files and be import/test runnable with the preserved `src.mac...` namespace.
- `git diff --check` must pass in both repositories.
