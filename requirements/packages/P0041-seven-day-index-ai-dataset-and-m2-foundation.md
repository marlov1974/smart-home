# Package P0041: Seven-day index AI dataset and M2 foundation

## Status

planned

## Package order

P0041

## Primary area

G2 / Mac tooling / spotprice V2 / seven-day index forecast / AI training dataset / M2 signal foundation

## Decision summary

P0041 starts a new 7-day index forecast track.

For the 7-day forecast use case, the legacy level/delta stack is no longer the main architecture:

```text
legacy level 1:
  M1 / M1B normal price baselines

kept signal level 2:
  M2A normal temperature
  M2C normal solar generation potential
  M2D normal wind generation potential

legacy level 3:
  M3A temperature delta
  M3B special-day delta
  M3C solar delta
  M3D wind delta
  M4 residual model
```

P0041 must keep level 2 signal-normal infrastructure, and build new learning datasets for two future AI models:

```text
AI-1: day-to-local-week model
AI-2: hour-to-day model
```

P0041 must not train the AI models yet. It creates the target datasets, feature contracts and evidence.

## Use case focus

P0041 focuses 100% on the short-term 7-day index forecast use case:

```text
Input later:
  11-35 known spot anchor hours
  7-day weather forecast
  special-day calendar
  M2 normal weather signals

Model output later:
  168-hour curve shape / index representation

API later:
  converts the curve/index to absolute prices using anchor hours
```

P0041 itself must not build the API.

## Model-retention decision

P0041 must document this decision in evidence:

### Keep as active foundation

```text
M2A = normal temperature / climate normal
M2C = normal solar generation potential
M2D = normal wind generation potential
SE1 and SE3-SE1 target split
Swedish special-day calendar from P0035
weather proxy locations and wind proxy locations from P0038
```

### Keep as legacy / diagnostic / fallback only for seven-day index track

```text
M1
M1B
M3A
M3B
M3C
M3D
M4
```

These may remain in the repository and may be used for comparisons or optional features in later packages, but P0041 must not continue the old M1+M3+M4 chain as the primary 7-day architecture.

### New future models

```text
AI-1: day-to-local-week model
AI-2: hour-to-day model
```

Recommended first model class for future training:

```text
HistGradientBoostingRegressor or similar tabular gradient boosting tree ensemble
```

Neural/transformer models are explicitly not the first implementation target.

## Target split

All datasets must be built separately for:

```text
system_proxy_se1
area_diff_proxy_se3 = SE3 - SE1
```

Do not collapse these series.

SE3 may be recomposed later as:

```text
SE3 = SE1 + (SE3-SE1)
```

## AI-1: day-to-local-week dataset

AI-1 answers:

```text
For day D, how expensive and how volatile is this day relative to its local 7-day period?
```

The local 7-day period is:

```text
D-2 .. D+4
```

Do not use ISO-week as the primary training window.

Each AI-1 row represents:

```text
date × target_series
```

Required local period fields:

```text
date
local_7d_start = date - 2 days
local_7d_end   = date + 4 days
local_7d_row_count
```

Rows without a complete 7-day period must either be skipped or clearly flagged. Preferred for training datasets: skip incomplete windows.

### AI-1 price facts

For each target series:

```text
day_mean_price
local_7d_mean_price
local_7d_level_scale
day_intraday_scale
local_7d_typical_day_scale
```

Scale definitions must be robust and positive.

Suggested robust scale definition:

```text
robust_scale(values) = max(
  percentile_75(values) - percentile_25(values),
  median_absolute_deviation(values) * 1.4826,
  abs(mean(values)) * 0.10,
  fixed_min_scale
)
```

Codex may adjust this if justified, but must document the exact formula.

### AI-1 targets

P0041 must create and store at least:

```text
day_level_shape =
  (day_mean_price - local_7d_mean_price) / local_7d_level_scale

log_day_scale_index =
  log(day_intraday_scale / local_7d_typical_day_scale)

log_local_7d_scale =
  log(local_7d_level_scale)
```

Interpretation:

```text
day_level_shape:
  how high/low the day mean is relative to its local 7-day level

log_day_scale_index:
  how volatile/stormy the day is relative to typical daily volatility in its local 7-day period

log_local_7d_scale:
  how volatile/stormy the local 7-day period is
```

P0041 must store ratio-style day index only as diagnostic, not as the primary target:

```text
day_ratio_index_diagnostic = day_mean_price / local_7d_mean_price
```

This diagnostic must be null/flagged when denominator is unsafe.

### AI-1 required features

Calendar:

```text
weekday
weekday_sin
weekday_cos
day_of_year
day_of_year_sin
day_of_year_cos
base_day_type
special_day_type
special_day_name
is_special_day
is_bridge_day
is_holiday_period
is_major_social_holiday
```

Do not use raw `week_of_year` as a categorical feature. Optional diagnostic only:

```text
week_of_year_sin
week_of_year_cos
```

Weather actual/normal/delta per day:

```text
daily_temperature_actual
daily_temperature_normal
daily_temperature_delta

daily_solar_actual
daily_solar_normal
daily_solar_delta

daily_wind_actual
daily_wind_normal
daily_wind_delta
```

Weather relative to local 7-day period:

```text
daily_temperature_delta_minus_local_7d_mean_delta
daily_solar_delta_minus_local_7d_mean_delta
daily_wind_delta_minus_local_7d_mean_delta

daily_temperature_rank_in_local_7d
daily_solar_rank_in_local_7d
daily_wind_rank_in_local_7d
```

Wind proxy diagnostics for area-diff:

```text
daily_wind_system_proxy
daily_wind_south_proxy
daily_wind_central_proxy
daily_wind_north_proxy
daily_wind_south_minus_north
daily_wind_central_minus_north
```

## AI-2: hour-to-day dataset

AI-2 answers:

```text
For hour H, how expensive is this hour relative to the fixed calendar day mean and volatility?
```

Use a fixed calendar day:

```text
00:00..23:00 local time
```

Do not use a rolling +/-12h day as the primary target.

Each AI-2 row represents:

```text
timestamp × target_series
```

### AI-2 price facts

For each target series:

```text
hour_price
day_mean_price
day_intraday_scale
```

### AI-2 target

P0041 must create and store:

```text
hour_shape =
  (hour_price - day_mean_price) / day_intraday_scale
```

Interpretation:

```text
hour_shape = +2.0 means the hour is two normal daily price movements above the day mean.
```

P0041 may store ratio-style hour index only as diagnostic:

```text
hour_ratio_index_diagnostic = hour_price / day_mean_price
```

This diagnostic must be null/flagged when denominator is unsafe.

### AI-2 required features

Calendar/time:

```text
hour
hour_sin
hour_cos
weekday
weekday_sin
weekday_cos
day_of_year
day_of_year_sin
day_of_year_cos
base_day_type
special_day_type
special_day_name
is_special_day
is_bridge_day
is_holiday_period
is_major_social_holiday
```

Weather actual/normal/delta per hour:

```text
hourly_temperature_actual
hourly_temperature_normal
hourly_temperature_delta

hourly_solar_actual
hourly_solar_normal
hourly_solar_delta

hourly_wind_actual
hourly_wind_normal
hourly_wind_delta
```

Weather relative to the fixed calendar day:

```text
hourly_temperature_delta_minus_day_mean_delta
hourly_solar_delta_minus_day_mean_delta
hourly_wind_delta_minus_day_mean_delta

hourly_temperature_rank_in_day
hourly_solar_rank_in_day
hourly_wind_rank_in_day
```

## M2A/M2C/M2D normal weather requirements

P0041 must either build or formalize explicit normal weather datasets for both daily and hourly use.

For each weather signal, store:

```text
actual
normal
delta = actual - normal
```

Required normal models:

```text
M2A = smooth/cyclic normal temperature
M2C = smooth/cyclic normal solar generation potential
M2D = smooth/cyclic normal wind generation potential
```

Normals must be smooth/cyclic and must not use sharp raw week-of-year categories as the primary seasonal representation.

### M2A temperature

Use existing P0035 climate normal work where suitable, but expose it under the M2A naming contract.

### M2C solar

Solar must represent solar generation potential, not raw radiation only.

Expected basis:

```text
solar_generation_potential =
  shortwave_radiation * cloud_adjustment * daylight_or_near_zero_gate
```

If clear-sky radiation or solar elevation is unavailable, document the fallback.

Night/near-zero potential should produce actual/normal/delta values that do not create fake nighttime solar signal.

### M2D wind

Wind must represent wind generation potential, not raw linear m/s only.

Expected basis:

```text
wind_power_proxy = capped nonlinear transform(wind_speed_100m)
```

Required wind proxy locations remain:

```text
Malmö
Kalmar
Kristinehamn
Piteå
Ånge
Härnösand
```

Required proxy groups:

```text
south_wind_proxy
central_wind_proxy
north_wind_proxy
system_wind_proxy
area_diff_wind_proxy
```

## Required outputs

P0041 must create local tables/views or documented equivalents.

Recommended table/view names:

```text
m2a_temperature_normals_hourly
m2a_temperature_normals_daily
m2c_solar_normals_hourly
m2c_solar_normals_daily
m2d_wind_normals_hourly
m2d_wind_normals_daily

ai1_day_to_local_week_training_targets
ai2_hour_to_day_training_targets
```

Do not commit local SQLite databases.

## Required evidence files

P0041 must create:

```text
requirements/package-runs/P0041/CHANGELOG.md
requirements/package-runs/P0041/review.md
requirements/package-runs/P0041/design.md
requirements/package-runs/P0041/functions.md
requirements/package-runs/P0041/model-retention-decision.md
requirements/package-runs/P0041/m2-normal-weather-foundation.md
requirements/package-runs/P0041/ai1-day-to-local-week-dataset.md
requirements/package-runs/P0041/ai2-hour-to-day-dataset.md
requirements/package-runs/P0041/robust-scale-definitions.md
requirements/package-runs/P0041/target-distributions.md
requirements/package-runs/P0041/example-rows.md
requirements/package-runs/P0041/leakage-and-window-policy.md
requirements/package-runs/P0041/next-model-training-plan.md
```

Optional machine-readable summaries:

```text
requirements/package-runs/P0041/dataset-summary.json
requirements/package-runs/P0041/example-rows.json
```

## Required evidence content

P0041 must explicitly answer:

```text
1. Which legacy models are kept only as diagnostic/fallback for the 7-day index track?
2. Which M2 normal signal models are kept as active foundation?
3. How many AI-1 rows were created per target series?
4. How many AI-2 rows were created per target series?
5. How many rows were skipped due to incomplete D-2..D+4 windows?
6. What exact robust scale formula is used?
7. Are all robust scales strictly positive?
8. What are the distributions of day_level_shape, log_day_scale_index and log_local_7d_scale?
9. What is the distribution of hour_shape?
10. How are near-zero/negative price cases handled?
11. What actual/normal/delta weather features exist for temp/solar/wind?
12. Are SE1 and SE3-SE1 separate throughout?
13. What should P0042 train first?
```

## Dataset sanity checks

Required checks:

```text
- local 7-day window is exactly D-2..D+4 for AI-1
- incomplete local windows are skipped or flagged
- AI-2 uses fixed calendar days 00..23
- day_intraday_scale > 0 for every AI-1/AI-2 usable row
- local_7d_level_scale > 0 for every AI-1 usable row
- local_7d_typical_day_scale > 0 for every AI-1 usable row
- mean hour_shape within each date/target_series is approximately 0
- no raw week_of_year categorical feature is included
- day_of_year sin/cos exists
- hour sin/cos exists for AI-2
- SE1 and SE3-SE1 targets are not mixed
```

## Tests

Required automated tests:

```text
- robust scale is positive even with flat/near-zero/negative prices
- ratio diagnostic is null/flagged when denominator is unsafe
- D-2..D+4 window builder returns exactly 7 dates
- AI-1 target formulas match hand-calculated fixture data
- AI-2 hour_shape formula matches hand-calculated fixture data
- mean hour_shape by day is near zero in fixture
- M2 actual/normal/delta fields are present in generated rows
- wind proxy required locations are present
- no M1/M3/M4 production path is invoked
- no M5/M6/M7/API/device path is touched
```

## Non-goals

- No AI model training in P0041.
- No M5 forecast-time temperature model.
- No M6 forecast API.
- No M7 futures/absolute long-term model.
- No futures/forward ingestion.
- No production forecast endpoint.
- No optimizer/control changes.
- No Shelly runtime changes.
- No Shelly deploy.
- No KVS writes.
- No Home Assistant integration.
- No live device access.
- No continuation of old M1+M3+M4 chain as the primary 7-day architecture.

## Expected Codex output

- PASS/WARN/STOP status
- model retention decision summary
- M2 normal weather foundation summary
- AI-1 dataset row counts and target distributions
- AI-2 dataset row counts and target distributions
- robust scale formula
- negative/near-zero price handling
- example rows
- tests run
- files changed
- no AI training confirmation
- no M5/M6/M7/API/device confirmation
- commit SHA after push

## Completion notes

To be filled after implementation.
