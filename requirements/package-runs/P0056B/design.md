# Package P0056B Implementation Design

## Package

`P0056B`

## Package interpretation

Create deterministic hourly weather actual-proxy features for all 18 P0056A primary areas. The output is a LABB data-preparation artifact for later multi-area consumption forecasting, not model training and not a production weather forecast.

## Chosen implementation structure

Implement a package-scoped diagnostic module:

```text
src/mac/services/spotprice_model_diagnostics/p0056b.py
```

The module will read:

```text
/Users/marcus.lovenstad/.smart-home/data/weather_history.sqlite3
/Users/marcus.lovenstad/.smart-home/data/spotprice_model_features.sqlite3
```

It will write a wide output table in the feature DB:

```text
area_weather_features_hourly_v1
```

The wide table is selected because it matches model-feature usage better than a long feature table and is explicitly allowed by the package.

## Intended changes

### Files/modules to change

- `src/mac/services/spotprice_model_diagnostics/p0056b.py`: new package runner.
- `tests/mac/services/spotprice_model_diagnostics/test_p0056b.py`: deterministic unit tests for area scope, proxy mapping, feature derivation, and safety flags.
- `requirements/packages/P0056B-labb-northern-europe-area-weather-proxies.md`: completion note/status only.
- `requirements/package-runs/P0056B/**`: required evidence files and compact CSV summaries.

### Files/modules intentionally not changed

- `src/mac/services/weather_history/storage.py`: existing weather schema and ingestion remain unchanged.
- Forecast/model modules: no model training or scoring is part of P0056B.
- Shelly, Home Assistant, deployment, and runtime files: forbidden by package.

## Refactoring decisions

No broad refactor is planned. The package will add a standalone builder that reuses existing DB schemas.

The only deliberate structure is a package-local source abstraction for weather inputs:

- `area_proxy`: read from `weather_area_hourly` for existing proxy series such as `se3_load_weather`.
- `location`: read from `weather_observations` for configured station/location IDs.

This keeps SE3 consistency exact by allowing SE3 to reuse the existing `se3_load_weather` area proxy.

## Output feature rules

- `temperature_2m`: weighted mean, Celsius.
- `apparent_temperature`: weighted mean, Celsius, nullable if unavailable.
- `wind_speed`: weighted `wind_speed_100m`, km/h.
- `cloud_cover`: weighted mean, percent.
- `relative_humidity`: weighted `relative_humidity_2m`, percent.
- `precipitation`: weighted mean, mm.
- `snow_depth`: null because current local source has snowfall but not snow depth.
- `heating_degree_proxy`: `max(0, 17 - temperature_2m)`.
- `cooling_degree_proxy`: `max(0, temperature_2m - 22)`.
- `temperature_2m_roll_mean_24h`: rolling mean over current and prior 23 UTC hourly rows.
- UTC timestamps are used directly. No local-time or DST joins are needed for this output.

## Test strategy

- Unit test that the area proxy selection covers exactly the P0056A package scope.
- Unit test that SE3 uses the existing `se3_load_weather` proxy.
- Unit test weighted feature derivation on synthetic rows, including heating/cooling and rolling mean.
- Unit test that fallback areas are explicitly flagged.
- Run the package module to generate DB rows and evidence.
- Run `git diff --check`.

## Build / generated artifact strategy

The package runner will generate:

- required Markdown evidence files under `requirements/package-runs/P0056B/`
- compact CSV summaries under `requirements/package-runs/P0056B/`
- `area_weather_features_hourly_v1` in the local feature DB

No large raw weather dumps will be committed.

## Risks and uncertainties

- Several non-Swedish areas must use fallback composites from existing local weather observations/proxies. This makes the package `WARN`, not a clean source-quality `PASS`.
- Local weather actual-proxy data may lag the latest P0056A consumption data by several days due archive availability.
- Existing weather source lacks snow depth; only snowfall exists. P0056B will keep `snow_depth` nullable.

## Design deviations during implementation

None yet.
