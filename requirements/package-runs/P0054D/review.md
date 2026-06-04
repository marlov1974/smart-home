# P0054D Consistency Review

Package: P0054D-labb-se4-load-weighted-weather-proxy-and-advanced-model-rerun
Label: LABB
Result: WARN

## Scope Check

P0054D is an offline LABB package under P0054A governance. It must not create production runtime behavior, call devices, use price, production, export/import, future A09/A11, A61 utilization, Shelly, Home Assistant, KVS or deployable model artifacts.

The requested work is consistent with repository truth:

- `src.mac.services.weather_history` already owns local historical weather storage and weighted proxy groups.
- `weather_locations`, `weather_observations` and `weather_area_hourly` support adding a new weighted proxy group.
- P0054C implemented the SE4 no-price consumption experiment and left evidence for comparison.

## Data Evidence

SE4 target source exists:

- Table: `physical_balance_se1_se4_hourly_v1`
- Target: `consumption_se4`
- Rows: 34,968
- Range: `2022-05-29T23:00:00Z` through `2026-05-25T22:00:00Z`
- Null target rows observed: 0

Existing weather DB has `south_connected_weather`, `se3_load_weather` and observations for `south_connected_malmo`, but not the requested SE4 load proxy locations.

## Warnings

P0054D needs historical weather observations for new location IDs:

- `se4_load_malmo`
- `se4_load_helsingborg`
- `se4_load_kristianstad`

The existing weather-history workflow can backfill these via Open-Meteo archive. That is allowed by P0054D only as historical weather ingestion through the existing service. If network/weather ingestion fails, the package must stop or report WARN with evidence.

Deep/sequence and boosted external ML dependencies remain unavailable locally:

- `torch`: missing
- `tensorflow`: missing
- `keras`: missing
- `xgboost`: missing
- `lightgbm`: missing

The additional dependency-safe advanced model will therefore be `ExtraTreesRegressor`.

## Decision

Classification: WARN.

Continue with:

- new `se4_load_weather` proxy configuration in weather-history;
- local weather backfill/compute/validation for the new proxy;
- P0054D modeling rerun using corrected proxy;
- HGB, MLP and ExtraTrees identical-row comparison.
