# P0053B consistency review

Status: WARN

P0053B is implementable and consistent with repository truth. The target table `physical_balance_se1_se4_hourly_v1` exists locally with `34968` hourly rows from `2022-05-29T23:00:00Z` through `2026-05-25T22:00:00Z`, and `consumption_se1` is non-null and positive for every row. P0053A evidence exists with WARN status and created `physical_balance_flow_exchange_analysis_v1` over the same range.

WARN reason:

- The repository contains historical realized weather data, not an explicit weather forecast table for the full historical simulation range.
- P0053B can safely use calendar, special-day, lag and train-only weather-normal features as forecast-safe.
- Actual realized weather and weather deltas must be classified as `historical_only_diagnostic` and excluded from deployable/readiness conclusions unless a later package supplies forecast-time weather data.

Scope decisions:

- PASS: Target only `consumption_se1`.
- PASS: Use chronological train/validation/holdout splits.
- PASS: Build direct-horizon and 168h path diagnostics.
- PASS: Exclude price, production, export/import, A09/A11 future actuals, A61 utilization and device/API work.
- WARN: Weather forecast-safety is limited to train-only normals in deployable feature groups; actual weather is diagnostic-only.

Evidence checked:

- `physical_balance_se1_se4_hourly_v1`: `34968` rows, no missing or non-positive `consumption_se1`.
- `physical_balance_flow_exchange_analysis_v1`: exists from P0053A.
- `weather_proxy_se1_core_hourly`: exists with overlapping weather history, but represents realized historical weather.
- `src.mac.services.swedish_calendar` provides deterministic known-in-advance Swedish daytype features.

Implementation may continue under WARN with conservative feature classification.
