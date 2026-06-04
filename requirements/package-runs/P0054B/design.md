# P0054B Implementation Design

Package: P0054B
Label: LABB

## Interpretation

Build an offline LABB experiment that forecasts SE3 hourly consumption from calendar, historical SE3 load lags/rollups and labeled weather proxy. The experiment must measure how much signal exists before adding price, production, flow, export/import, A61, or external APIs.

No API calls, devices, runtime writes, deployable model artifacts or production activation are in scope.

## Implementation Structure

Add a package module:

`src/mac/services/spotprice_model_diagnostics/p0054b.py`

Add package tests:

`tests/mac/services/spotprice_model_diagnostics/test_p0054b.py`

Write evidence under:

`requirements/package-runs/P0054B/`

The module will run end to end with:

`python3 -m src.mac.services.spotprice_model_diagnostics.p0054b`

## Dataset Construction

Source target rows from `physical_balance_se1_se4_hourly_v1`.

For every forecast origin and requested direct horizon, create a target row when:

- target timestamp is within the global modeling policy from `2022-06-01T00:00Z`;
- origin has enough prior SE3 load history for all required lags and rollups;
- target timestamp exists locally.

Inputs are built from the origin perspective:

- Calendar features are deterministic from target timestamp.
- Load lags and rollups use rows strictly before the forecast origin.
- Baselines use forecast-safe historical lookup before the origin, or train-only profile fallback.
- Weather features use realized archive values at target timestamp and are labeled `weather_actual_as_forecast_proxy`.

## Feature Groups

P0054B will implement the requested groups:

- `G0_calendar_only`
- `G1_calendar_plus_load_lags`
- `G2_calendar_plus_load_lags_rollups`
- `G3_calendar_weather_proxy`
- `G4_calendar_load_lags_rollups_weather_proxy`

All feature contracts will be checked for forbidden terms including price, production, flow, export/import and A61.

## Models

Benchmark:

- `HistGradientBoostingRegressor` on `G4_calendar_load_lags_rollups_weather_proxy`

Advanced AI:

- `MLPRegressor` on the identical G4 row set.

Sequence-aware neural models are preferred by the package but blocked locally by missing `torch`, `tensorflow` and `keras`. This is documented in review and evidence.

Both models use fixed random seed `54`. No fitted artifact is persisted.

## Metrics

Produce validation and holdout metrics for:

- direct horizons: 1, 3, 6, 12, 24, 48, 72, 96, 120, 144, 168 hours;
- weekly 168h holdout paths from origins on or after `2025-06-01T00:00Z`;
- conditional regimes such as cold hours, rapid temperature change, weekday/weekend, morning ramp, evening peak, summer low load and winter high load.

Metrics include MAE, RMSE, median absolute error, p90 absolute error, p95 absolute error, bias, sMAPE, R2 and MAE as percent of mean/median actual load.

## Deliberate Refactoring

The package will use a new module instead of changing P0053B modules. Small reusable helpers may mirror P0053B/P0053BA2 patterns where practical. No broad refactor or runtime service change is intended.

## Tests

Package tests will cover:

- lag and rollup features do not include origin or future rows;
- feature contracts exclude forbidden inputs;
- weekly holdout origin selection requires complete 168h paths and uses every seventh origin;
- model comparison row-set validation catches mismatches.

Verification will include unit tests, module execution, generated evidence inspection and `git diff --check`.

## Risks and Uncertainty

- Weather is archive proxy, not a separate forecast model, so weather-assisted results are LABB proxy results only.
- MLP is not sequence-aware. It is the strongest locally feasible advanced AI option without installing dependencies or calling network.
- No package result should be read as production readiness or G2-KANDIDAT evidence.
