# P0054C Consistency Review

Package: P0054C-labb-se4-consumption-advanced-ai-without-price
Label: LABB
Result: WARN

## Scope Check

P0054C is an offline LABB package under P0054A governance. It repeats the P0054B no-price consumption experiment for SE4.

The requested work is consistent with repository policy:

- LABB is the default label for energy-market AI work.
- This is not a G2-KANDIDAT evaluation.
- No API, devices, runtime changes, price, production, flow/export/import, future A09/A11, A61 or deployable model artifact is allowed.
- HGB and advanced AI must use identical rows.

## Target Evidence

Local source table `physical_balance_se1_se4_hourly_v1` exists in `spotprice_model_features.sqlite3`.

- Rows: 34,968
- Range: `2022-05-29T23:00:00Z` through `2026-05-25T22:00:00Z`
- Target: `consumption_se4`
- Target nulls observed: 0
- Mean: 1053.638 MW
- Min: 321.365 MW
- Max: 4288.201 MW

The requested global split is feasible:

- Train target rows: `2022-06-01T00:00Z` through `2024-12-31T23:00Z`
- Validation target rows: `2025-01-01T00:00Z` through `2025-05-31T23:00Z`
- Holdout target rows: `2025-06-01T00:00Z` through latest local target row

## Warnings

Sequence-aware GRU/LSTM/TCN remains blocked by local dependencies:

- `torch`: not installed
- `tensorflow`: not installed
- `keras`: not installed

The package asks to prefer the deterministic sklearn MLP family from P0054B for apples-to-apples comparison, so implementation will use `MLPRegressor`.

The default local weather DB does not expose an absolute SE4-specific proxy table. It does expose `weather_area_hourly` with `area_proxy = south_connected_weather`, including absolute temperature, apparent temperature, wind, cloud, solar, precipitation, humidity and heating/cooling degree fields. P0054C will use that as a broad LABB weather proxy and label it `weather_actual_as_forecast_proxy`. This is weaker than SE4-specific weather, but it is within the package allowance to use broader south/system proxy when documented.

## Decision

Classification: WARN.

Continue with a deterministic offline LABB run using:

- SE4 historical load lags/rollups.
- Calendar features.
- `weather_area_hourly` / `south_connected_weather` as labeled broad weather proxy.
- HGB benchmark and sklearn MLP advanced AI on identical rows.
