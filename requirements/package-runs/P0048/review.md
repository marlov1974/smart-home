# P0048 consistency review

Status: PASS

P0048 is consistent with repository state and previous package evidence.

## Evidence checked

- `requirements/packages/P0048-se3-se1-bottleneck-feature-foundation-and-exploratory-two-stage-model.md`
- `requirements/package-runs/P0047/CHANGELOG.md`
- `requirements/package-runs/P0047/component-attribution-summary.md`
- `src/mac/services/spotprice_model_diagnostics/p0047.py`
- `src/mac/services/spotprice_model_diagnostics/p0043.py`
- local feature DB table `ai2_hour_to_day_training_targets_v2`
- local weather DB tables/views `weather_area_hourly`, `weather_proxy_*_hourly`

## P0047 precondition result

P0047 PASS evidence exists and reports:

```text
window: 2025-01-01 .. 2025-12-31 fixed-CET
row_count: 8760
near-zero share: 0.267123
positive bottleneck share: 0.576598
negative bottleneck share: 0.000571
lag1 same-regime share: 0.818130
```

P0047 also documents that requested south/north/central gradient weather fields were missing from the AI2 v2 table and recommends classification+severity exploration before any direct SE3/API path.

## Feature foundation check

The local weather DB contains source rows for:

```text
se1_core_weather
se3_load_weather
south_connected_weather
nordic_connected_weather
p0038_south_wind_proxy
p0038_central_wind_proxy
p0038_north_wind_proxy
p0038_south_solar_proxy
p0038_se3_load_solar_proxy
p0038_north_solar_proxy
weather_proxy_gradients_hourly
```

These are sufficient to materially improve P0048 weather-gradient features over P0047's AI2-only source.

## Assumptions

- `area_diff_proxy_se3.hour_price` remains the repository's current `SE3 - SE1` target.
- `se3_price` can be reconstructed as `system_proxy_se1.hour_price + area_diff_proxy_se3.hour_price`.
- Weather actuals are proxy-forecast-known exploratory features, not production forecast inputs.
- Temperature north proxy is best represented by `se1_core_weather`; south proxy by `south_connected_weather`; system proxy by the AI2/P0042 system temperature or an average of south/north where needed.

## Safety and scope

P0048 does not require live device access. It must not create a production model artifact, API, M5/M6/M7 path, KVS write, Home Assistant change, Shelly change, or SE1-to-SE3 anchoring.

## Classification

PASS. Continue with package-scoped Mac diagnostic implementation and evidence generation.
