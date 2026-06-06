# Package P0054Z: LABB SE3 climate-zone weather series

## Status

planned

## Package order

P0054Z

## Label

```text
LABB
```

This package is local research work under P0054A. It is not a G2-KANDIDAT evaluation.

## Purpose

Create weather series for each SE3 climate zone used by the P0054Y2 profiled/load-profile cluster decomposition, in addition to the broad SE3 weather proxy already used by the direct SE3 model.

These climate-zone weather series will become forecast inputs for later hierarchical consumption forecasting:

```text
SE3 direct model
profiled/load-profile cluster models
metered/non-profiled residual model
reconciled ensemble
```

P0054Z creates weather features only. It must not train final consumption forecast models.

## Background

Current best SE3 consumption candidate is direct SE3:

```text
HorizonBiasCorrected_WeightedEnsemble_no_price
weather/load/calendar features
DayAhead MAE around 252-259 MW depending on weather protocol
```

P0054Y2 created a decomposition:

```text
16 profiled/load-profile clusters
+ SE3 residual metered/non-profiled/unobserved component
```

The P0054Y2 cluster IDs use:

```text
C<climate_index><urban_load_index>
```

Climate index:

```text
1 = EAST_COAST_MALARDALEN_STOCKHOLM
2 = WEST_COAST_GOTHENBURG
3 = NORTHERN_INLAND
4 = SOUTHERN_INLAND_SMALAND_NORTH_GOTALAND
```

P0054Z must create one weather series per climate zone, plus keep/verify the broad SE3 proxy.

## Climate zones

Required climate-zone IDs:

```text
SE3_EAST_COAST_MALARDALEN_STOCKHOLM
SE3_WEST_COAST_GOTHENBURG
SE3_NORTHERN_INLAND
SE3_SOUTHERN_INLAND_SMALAND_NORTH_GOTALAND
SE3_BROAD_PROXY
```

The broad proxy must remain available for direct SE3 and residual modeling comparison.

## Weather source policy

Use existing local weather source/proxy infrastructure used by P0054R/P0054T4 where possible.

Allowed sources:

```text
existing local DB weather tables
existing local weather proxy files
existing local scripts that generated weather_proxy_* features
operator-approved weather downloads already present locally
```

Do not add a new external live weather integration unless already approved in project. If missing data requires external download, document the needed source and stop/warn rather than adding credentials or a new integration.

## Required station/proxy selection

For each climate zone, choose representative weather station(s) or local proxy points.

Document for each zone:

```text
climate_zone_id
station_or_proxy_ids
station_or_proxy_names
latitude/longitude if available
coverage_start
coverage_end
missingness
reason for selection
fallback station/proxy
```

Selection should reflect both geography and load representativeness.

Suggested intuition:

```text
EAST_COAST_MALARDALEN_STOCKHOLM:
  Stockholm/Mälardalen/east-coast representative stations or proxy grid points

WEST_COAST_GOTHENBURG:
  Göteborg/west-coast representative stations or proxy grid points

NORTHERN_INLAND:
  northern/inland SE3 stations or proxy grid points with colder inland climate

SOUTHERN_INLAND_SMALAND_NORTH_GOTALAND:
  Småland/north Götaland/southern-inland representative stations or proxy grid points
```

If station coverage is incomplete, use weighted multi-station/proxy composites with documented fallback.

## Required output table/view

If repo database ownership allows, create/populate:

```text
se3_climate_zone_weather_hourly_v1
```

Minimum columns:

```text
timestamp_utc
climate_zone_id
feature_name
feature_value
feature_unit
source_station_or_proxy_ids
aggregation_method
missingness_flag
generated_by_package = P0054Z
```

Alternatively, if the existing weather feature infrastructure is wide-table oriented, create a documented equivalent such as:

```text
se3_climate_zone_weather_features_hourly_v1
```

Minimum wide-table columns should include:

```text
timestamp_utc
climate_zone_id
temperature_2m
apparent_temperature
wind_speed
cloud_cover or cloudiness if available
relative_humidity if available
precipitation if available
snow_depth if available
heating_degree_proxy if computed
cooling_degree_proxy if computed
source_station_or_proxy_ids
missingness_flags
generated_by_package
```

Do not commit large raw weather files.

## Required features

At minimum, create for each climate zone:

```text
temperature_2m
apparent_temperature if available
heating_degree_proxy relative to defensible base temperature
rolling temperature features if used by current SE3 model
```

Preferred if source supports:

```text
wind_speed
cloud_cover
relative_humidity
precipitation
snow_depth
```

Derived features must be clearly documented:

```text
heating_degree_proxy base temperature
cooling_degree_proxy base temperature
rolling windows
local time handling
DST handling
```

## Time period

Required coverage:

```text
2022-06-01T00:00:00Z onward
```

This must align with P0054 train/holdout policy and P0054Y2 decomposition coverage.

If a weather series starts later, document the limitation and whether it blocks cluster forecasting.

## Mapping to clusters

Create or document a mapping:

```text
cluster_id -> climate_zone_id
```

Expected:

```text
C1* -> SE3_EAST_COAST_MALARDALEN_STOCKHOLM
C2* -> SE3_WEST_COAST_GOTHENBURG
C3* -> SE3_NORTHERN_INLAND
C4* -> SE3_SOUTHERN_INLAND_SMALAND_NORTH_GOTALAND
residual -> SE3_BROAD_PROXY initially, plus optional tested alternatives later
```

For residual, preserve broad SE3 proxy as default, but also make zone weather available so later packages can test whether residual is better with broad or composite climate-zone weather.

## Validation requirements

P0054Z must report for each climate zone:

```text
row_count
min_timestamp
max_timestamp
missing_hour_count
coverage_ratio
mean_temperature
p05_temperature
p95_temperature
winter_mean_temperature
summer_mean_temperature
correlation_with_broad_proxy
mean_delta_vs_broad_proxy
p95_abs_delta_vs_broad_proxy
```

It must also verify that the four climate-zone series are not all identical unless the underlying source is genuinely broad-only.

If they are identical, return WARN and explain that local climate-zone weather cannot yet improve over broad proxy.

## Forecast-safety note

P0054Z may create actual-weather proxy series for LABB training/evaluation, consistent with prior P0054R/P0054T4 work.

Future production-like packages must distinguish:

```text
weather_actual_proxy
weather_forecast
weather_forecast_with_error/noise
```

Do not claim the P0054Z actual-weather series is production forecast weather.

## Required evidence files

Create:

```text
requirements/package-runs/P0054Z/CHANGELOG.md
requirements/package-runs/P0054Z/review.md
requirements/package-runs/P0054Z/design.md
requirements/package-runs/P0054Z/functions.md
requirements/package-runs/P0054Z/labb-label.md
requirements/package-runs/P0054Z/p0054y2-input-review.md
requirements/package-runs/P0054Z/weather-source-inventory.md
requirements/package-runs/P0054Z/climate-zone-definitions.md
requirements/package-runs/P0054Z/station-proxy-selection.md
requirements/package-runs/P0054Z/output-table-schema.md
requirements/package-runs/P0054Z/weather-feature-contract.md
requirements/package-runs/P0054Z/cluster-weather-mapping.md
requirements/package-runs/P0054Z/coverage-and-missingness.md
requirements/package-runs/P0054Z/climate-zone-validation.md
requirements/package-runs/P0054Z/database-output-evidence.md if DB tables are written
requirements/package-runs/P0054Z/forecast-safety-review.md
requirements/package-runs/P0054Z/modeling-readiness-review.md
requirements/package-runs/P0054Z/what-we-learned.md
requirements/package-runs/P0054Z/next-package-recommendation.md
```

Optional compact evidence:

```text
climate-zone-weather-summary.csv
cluster-weather-mapping.csv
station-proxy-selection.csv
```

Do not commit large raw weather time-series dumps.

## Files to inspect

```text
requirements/package-runs/P0054R/model-comparison.md
requirements/package-runs/P0054R/feature-groups.md
requirements/package-runs/P0054T4/inference-noise-summary.json
requirements/package-runs/P0054Y2/cluster-segment-dictionary.md
requirements/package-runs/P0054Y2/decomposition-validation.md
requirements/package-runs/P0054Y2/modeling-readiness-review.md
src/mac/** relevant weather/proxy scripts
tests/mac/** relevant tests
docs/functions/mac/**
memory/energy-market-ai-lab.md
```

## Files allowed to change

```text
requirements/packages/P0054Z-labb-se3-climate-zone-weather-series.md
requirements/package-runs/P0054Z/**
src/mac/** narrowly scoped weather series construction code if needed
tests/mac/** narrowly scoped tests for weather aggregation/mapping if code is added
docs/functions/mac/** if durable docs need updating
local database schema/migration files if this repo owns them and only for P0054Z tables
```

## Forbidden changes

```text
No Shelly changes.
No Home Assistant changes.
No device/runtime writes.
No production deployment.
No G2-KANDIDAT promotion.
No new external live weather integration without explicit approval.
No credentials or tokens.
No large raw weather data commits.
No final consumption forecast model training in this package.
No claim that actual-weather proxy is production forecast weather.
```

## Pass / WARN / STOP interpretation

PASS requires:

```text
- four SE3 climate-zone weather series are created or verified.
- broad SE3 proxy remains available.
- cluster_id to climate_zone_id mapping is documented.
- coverage/missingness and validation are reported.
- output is ready for later cluster/residual forecasting tests.
```

WARN is acceptable if:

```text
- some optional weather variables are unavailable.
- one climate zone has fallback station/proxy coverage.
- zone series are generated from broad proxy only and therefore not regionally distinct, if documented clearly.
- DB writes are skipped but compact evidence exists.
```

STOP if:

```text
- no local weather source exists.
- required temperature series cannot be built for 2022-06 onward.
- cluster/weather mapping cannot be defined.
- a new unapproved external weather integration would be required.
```

## Expected Codex output

```text
PASS/WARN/STOP status
commit SHA
weather source used
climate-zone series created
broad proxy status
station/proxy selection summary
coverage by climate zone
whether zone series are distinct from broad proxy
cluster-weather mapping
DB output tables or evidence files created
recommended next package
tests/commands run
files changed
confirmation no credentials, no external integration, no large raw weather data committed
```

## Completion notes

To be filled after implementation.
