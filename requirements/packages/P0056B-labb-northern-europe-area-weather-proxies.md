# Package P0056B: LABB northern Europe area weather proxies

## Status

completed

## Package order

P0056B

## Label

```text
LABB
```

## Purpose

Create weather proxy series for every P0056A price area so the multi-area consumption forecasts can use the same model principle as the best SE3 forecast:

```text
calendar + historical load + weather
no spot price feature
```

This package prepares weather data only. It must not train consumption forecast models.

## Required area scope

Create one weather proxy per P0056A primary area:

```text
SE1
SE2
SE3
SE4
NO1
NO2
NO3
NO4
NO5
DK1
DK2
FI
EE
LV
LT
DE_LU
PL
NL
```

If an area needs multiple sub-proxies, create a documented weighted composite but expose one canonical area weather proxy for forecasting.

## Source policy

Use existing local weather data/proxy infrastructure where possible, including prior SE3 and SE3 climate-zone weather work.

Allowed:

```text
existing local weather tables
existing local weather proxy scripts
existing local weather exports
operator-provided local data
```

Do not add a new unrelated external integration in this package. If a weather source is missing, return WARN/STOP with exact missing source.

## Time period

Required coverage:

```text
2022-06-01T00:00:00Z onward
```

Coverage should align with P0056A consumption measurements.

## Required output

Create or reuse a table/view:

```text
area_weather_proxy_hourly_v1
```

Minimum columns:

```text
timestamp_utc
area_code
weather_proxy_id
feature_name
feature_value
feature_unit
source_station_or_proxy_ids
aggregation_method
missingness_flag
generated_by_package = P0056B
```

If a wide table is more consistent with existing scripts, create a documented equivalent:

```text
area_weather_features_hourly_v1
```

Minimum wide columns:

```text
timestamp_utc
area_code
temperature_2m
apparent_temperature nullable
wind_speed nullable
cloud_cover nullable
relative_humidity nullable
precipitation nullable
snow_depth nullable
heating_degree_proxy
cooling_degree_proxy nullable
source_station_or_proxy_ids
missingness_flags
generated_by_package
```

## Required features

At minimum for every area:

```text
temperature_2m
heating_degree_proxy
rolling temperature features needed by the current SE3 model
```

Preferred where source supports:

```text
apparent_temperature
wind_speed
cloud_cover
relative_humidity
precipitation
snow_depth
```

Document all derived-feature rules:

```text
heating degree base temperature
cooling degree base temperature if used
rolling windows
UTC/local-time handling
DST handling
```

## Proxy selection

For each area, document:

```text
area_code
station_or_proxy_ids
station_or_proxy_names
country/region
latitude/longitude if available
weights
coverage_start
coverage_end
missingness
reason for selection
fallback if missing
```

Selection should be load-representative, not only geographically centered.

Examples of expected approach:

```text
SE1/SE2: colder northern Swedish proxies
SE3/SE4: reuse existing Swedish area or climate-zone proxy logic as appropriate
NO1-NO5: Norwegian zone-representative proxies
DK1/DK2: Jutland/Zealand representative proxies
FI/EE/LV/LT: country or bidding-zone representative proxies
DE_LU/PL/NL: national/bidding-zone representative composite proxies
```

## Validation

For each area report:

```text
row_count
min_timestamp_utc
max_timestamp_utc
coverage_ratio
missing_hour_count
mean_temperature
p05_temperature
p95_temperature
winter_mean_temperature
summer_mean_temperature
```

Also compare broad regional differences:

```text
NO4/SE1 should generally be colder than DK/NL/DE_LU
SE3 proxy should be consistent with previous SE3 broad proxy
```

If all area weather proxies are identical, WARN unless that is explicitly intended for a fallback.

## Forecast-safety note
These series may be actual-weather proxies for LABB training/evaluation, consistent with earlier P0054 work.

Later production-like packages must distinguish:

```text
weather_actual_proxy
weather_forecast
weather_forecast_with_noise
```

Do not claim actual-weather proxy is production forecast weather.

## Required evidence files

Create:

```text
requirements/package-runs/P0056B/CHANGELOG.md
requirements/package-runs/P0056B/review.md
requirements/package-runs/P0056B/design.md
requirements/package-runs/P0056B/functions.md
requirements/package-runs/P0056B/labb-label.md
requirements/package-runs/P0056B/p0056a-input-review.md
requirements/package-runs/P0056B/weather-source-inventory.md
requirements/package-runs/P0056B/area-weather-scope.md
requirements/package-runs/P0056B/station-proxy-selection.md
requirements/package-runs/P0056B/output-table-schema.md
requirements/package-runs/P0056B/weather-feature-contract.md
requirements/package-runs/P0056B/coverage-and-missingness.md
requirements/package-runs/P0056B/weather-proxy-validation.md
requirements/package-runs/P0056B/se3-proxy-consistency-check.md
requirements/package-runs/P0056B/database-output-evidence.md if DB tables are written
requirements/package-runs/P0056B/forecast-safety-review.md
requirements/package-runs/P0056B/modeling-readiness-review.md
requirements/package-runs/P0056B/what-we-learned.md
requirements/package-runs/P0056B/next-package-recommendation.md
```

Optional compact evidence:

```text
area-weather-summary.csv
station-proxy-selection.csv
weather-coverage-summary.csv
```

Do not commit large raw weather dumps.

## Files to inspect

```text
requirements/package-runs/P0054Z/CHANGELOG.md
requirements/package-runs/P0054Z/climate-zone-validation.md
requirements/package-runs/P0054Z/station-proxy-selection.md
requirements/package-runs/P0056A/CHANGELOG.md
requirements/package-runs/P0056A/area-code-mapping.md
requirements/package-runs/P0056A/coverage-and-missingness.md
src/mac/** weather/proxy scripts
tests/mac/** weather tests
docs/functions/mac/**
memory/energy-market-ai-lab.md
```

## Files allowed to change

```text
requirements/packages/P0056B-labb-northern-europe-area-weather-proxies.md
requirements/package-runs/P0056B/**
src/mac/** narrowly scoped weather proxy construction code if needed
tests/mac/** narrowly scoped tests for weather proxy mapping/aggregation if code is added
docs/functions/mac/** if durable docs need updating
local database schema/migration files if this repo owns them and only for P0056B tables
```

## Forbidden changes

```text
No Shelly changes.
No Home Assistant changes.
No device/runtime writes.
No production deployment.
No G2-KANDIDAT promotion.
No forecast model training.
No spot price features.
No large raw weather commits.
No claim that actual-weather proxy is production forecast weather.
```

## Pass / WARN / STOP

PASS requires:

```text
weather proxy created or verified for all 18 P0056A areas
coverage documented from 2022-06-01 onward
SE3 proxy consistency checked
area proxies are ready for multi-area consumption forecasts
```

WARN is acceptable if:

```text
some optional weather variables are unavailable
some areas use fallback proxies
one area has partial coverage but is documented
```

STOP if:

```text
no local weather source exists
temperature proxy cannot be built for many primary areas
SE3 consistency cannot be checked
```

## Completion notes

Completed by package run P0056B.

Result:

```text
WARN
```

Reason for WARN:

```text
All 18 P0056A primary areas have deterministic LABB weather actual-proxy rows, but DK1, EE, LV, LT, DE_LU, PL and NL use documented fallback composites from existing local weather stations/proxies. The local source also has no snow_depth field, so snow_depth is nullable and written as null.
```

Output:

```text
area_weather_features_hourly_v1
631116 rows
18 areas
2022-06-01T00:00Z..2026-05-31T21:00Z
generated_by_package = P0056B
```

SE3 consistency:

```text
Compared P0056B SE3 temperature_2m with P0054Z SE3_BROAD_PROXY temperature_2m.
Overlap rows: 35062
Max abs delta: 0.0
Mean abs delta: 0.0
```

No API, no devices, no runtime change, no model training and no spot price features were used.

## Expected Codex output

```text
PASS/WARN/STOP status
commit SHA
weather table created/used
areas covered/missing
features created
station/proxy selection summary
coverage by area
SE3 consistency result
whether proxies are ready for multi-area consumption forecasts
tests/commands run
files changed
confirmation no device/runtime/no forecast training/no large raw weather commits
```

## Completion notes

To be filled after implementation.
