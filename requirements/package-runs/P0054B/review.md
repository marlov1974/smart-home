# P0054B Consistency Review

Package: P0054B-labb-se3-consumption-advanced-ai-without-price
Label: LABB
Result: WARN

## Scope Check

P0054B is an offline LABB package for SE3 consumption forecasting. It must not train or promote any deployable production model, call external APIs, access devices, use A61 utilization, use price, production, flow, export/import, or leak future actual load beyond the forecast origin.

The package is consistent with repository direction after P0054A:

- Default label for energy market, AI, spot price and simulator work is LABB.
- G2-KANDIDAT evaluation requires explicit human operator request.
- Weather realized history may be used only as a labeled LABB proxy when no true separate forecast model exists.
- Benchmark and interpretation must be explicit.

## Data Evidence

Local source table `physical_balance_se1_se4_hourly_v1` exists in `spotprice_model_features.sqlite3`.

- Rows: 34,968
- Range: `2022-05-29T23:00:00Z` through `2026-05-25T22:00:00Z`
- Target: `consumption_se3`
- Target nulls observed: 0
- Unit: MW hourly mean

Local SE3 weather proxy table `weather_proxy_se3_load_hourly` exists in `weather_history.sqlite3`.

- Rows: 35,040
- Range: `2022-05-29T22:00Z` through `2026-05-28T21:00Z`
- Source label: Open-Meteo archive / ERA5 seamless
- P0054B classification: `weather_actual_as_forecast_proxy`

The requested global split is feasible against local data:

- Train target rows: `2022-06-01T00:00Z` through `2024-12-31T23:00Z`
- Validation target rows: `2025-01-01T00:00Z` through `2025-05-31T23:00Z`
- Holdout target rows: `2025-06-01T00:00Z` through latest available local target row

## Warning

Sequence-aware GRU/LSTM/TCN is blocked by local dependencies:

- `torch`: not installed
- `tensorflow`: not installed
- `keras`: not installed

The package allows a small MLP if sequence-aware neural training is blocked. Implementation will therefore use `sklearn.neural_network.MLPRegressor` as the advanced AI model and document the blocker in `advanced-ai-training-evidence.md`.

## Decision

Classification: WARN.

Continue implementation with a deterministic, offline, package-scoped LABB run using:

- HGB as the benchmark.
- Small MLP as the advanced AI model.
- Strict forecast-origin feature construction for load lags and rollups.
- Weather actual proxy features clearly labeled as LABB proxy.
- Identical train/validation/holdout rows for HGB and MLP comparison.
