# Package P0056M: LABB SE2 M6 DayAhead error slice analysis

## Status

completed

## Package order

P0056M

## Label

```text
LABB
```

## Purpose

Analyze when the current realistic DayAhead SE2 baseline works best and worst.

The package must use P0056K's realistic DayAhead protocol and the SE2 best baseline model:

```text
M6 WeightedEnsemble_no_price
```

It must produce a clear, human-readable error analysis by:

```text
weekday
month
season / part of year
cold vs mild vs warm conditions
winter vs summer
high-load / low-load periods
ramp / fast-change periods
```

It must also list the five best and five worst DayAhead forecast tests.

## Area and model in scope

```text
area = SE2
model = M6 WeightedEnsemble_no_price
protocol = P0056K realistic DayAhead
```

Do not test other areas or models in this package unless they are only used as context.

## Baseline reference

Use latest committed P0056K evidence as baseline.

Known reference:

```text
SE2 M6 DayAhead hourly MAE: 232.692807 MW
MAE percent of mean actual: 12.832409 %
daily energy error percent: 8.392545 %
origin_count: 240
delivery_day_count: 240
```

If local evidence differs, document exact source and values.

## Forecast protocol

Use the same protocol as P0056K:

```text
forecast_origin = D-1 12:00 Europe/Stockholm
delivery_day = D 00:00 through D 23:00 Europe/Stockholm
```

Only forecast-safe features are allowed.

No future actual load leakage.

## Required analysis levels

### 1. Day-level forecast quality

For every delivery day/origin, calculate:

```text
delivery_date
forecast_origin
weekday
month
season
mean_actual_load_mw
mean_forecast_load_mw
hourly_MAE
hourly_RMSE
bias_mw
signed_daily_energy_error_MWh
absolute_daily_energy_error_MWh
daily_energy_error_percent
max_absolute_hourly_error_mw
p90_absolute_hourly_error_mw
mean_temperature_2m
min_temperature_2m
max_temperature_2m
heating_degree_hours_sum
cold_spell_flag_any
load_ramp_score
```

### 2. Hour-level quality

For every forecasted hour, calculate and persist compact summary inputs:

```text
target_timestamp
local_hour
horizon_h
actual_mw
forecast_mw
error_mw
absolute_error_mw
weekday
month
season
temperature_2m
heating_degree_hours
ramp_24h_or_safe_proxy
```

Do not commit a massive full dump if it is large. If compact enough for SE2 only, CSV is allowed. Otherwise summarize.

### 3. Slices to report

Report MAE, bias, daily energy error and count for:

```text
weekday
month
season: winter, spring, summer, autumn
half-year: winter_half, summer_half
temperature bins
heating degree bins
mean load quantiles
ramp quantiles
horizon bins: 0-5, 6-11, 12-17, 18-23, 24-35 if available
local-hour bins
holiday/workday/weekend
```

Suggested temperature bins:

```text
very_cold: <= -10 C
cold: -10 to 0 C
mild: 0 to 10 C
warm: 10 to 20 C
hot: > 20 C
```

Suggested seasons:

```text
winter: Dec-Feb
spring: Mar-May
summer: Jun-Aug
autumn: Sep-Nov
```

## Required top/bottom lists

Create a list of the five best DayAhead tests and the five worst DayAhead tests.

Ranking metric:

```text
primary: daily hourly_MAE
secondary: absolute_daily_energy_error_MWh
```

For each top/bottom case include:

```text
rank
delivery_date
forecast_origin
weekday
month
season
hourly_MAE
RMSE
bias_mw
absolute_daily_energy_error_MWh
daily_energy_error_percent
mean_actual_load_mw
mean_forecast_load_mw
mean_temperature_2m
min_temperature_2m
max_temperature_2m
heating_degree_hours_sum
cold_spell_flag_any
largest_error_hour
largest_error_mw
short explanation candidate
```

The output must be readable in Markdown, not only CSV.

## Required interpretations

Answer these questions explicitly:

```text
1. Which weekday is worst for SE2 M6?
2. Which weekday is best?
3. Which month is worst?
4. Which season is worst?
5. Does cold weather increase error?
6. Does mild weather increase error?
7. Are errors worse in winter or summer?
8. Are high-load days worse than low-load days?
9. Are high-ramp days worse?
10. Are errors mainly bias, volatility, or isolated hourly spikes?
11. What are the most common patterns in the five worst tests?
12. What are the most common patterns in the five best tests?
```

## Required evidence files

Create:

```text
requirements/package-runs/P0056M/CHANGELOG.md
requirements/package-runs/P0056M/review.md
requirements/package-runs/P0056M/design.md
requirements/package-runs/P0056M/functions.md
requirements/package-runs/P0056M/labb-label.md
requirements/package-runs/P0056M/p0056k-baseline-review.md
requirements/package-runs/P0056M/dayahead-protocol.md
requirements/package-runs/P0056M/input-source-contract.md
requirements/package-runs/P0056M/leakage-review.md
requirements/package-runs/P0056M/day-level-results.md
requirements/package-runs/P0056M/hour-level-summary.md
requirements/package-runs/P0056M/weekday-slice.md
requirements/package-runs/P0056M/month-slice.md
requirements/package-runs/P0056M/season-slice.md
requirements/package-runs/P0056M/temperature-slice.md
requirements/package-runs/P0056M/load-slice.md
requirements/package-runs/P0056M/ramp-slice.md
requirements/package-runs/P0056M/horizon-hour-slice.md
requirements/package-runs/P0056M/top-5-best-tests.md
requirements/package-runs/P0056M/top-5-worst-tests.md
requirements/package-runs/P0056M/pattern-review.md
requirements/package-runs/P0056M/decision.md
requirements/package-runs/P0056M/what-we-learned.md
requirements/package-runs/P0056M/next-package-recommendation.md
```

Optional compact evidence:

```text
day-level-results.csv
hour-level-summary.csv
slice-summary.csv
top-bottom-tests.json
metrics-summary.json
```

Do not commit large full prediction dumps if avoidable.

## Files to inspect

```text
requirements/package-runs/P0056K/area-model-results.md
requirements/package-runs/P0056K/model-ranking.md
requirements/package-runs/P0056K/dayahead-protocol.md
requirements/package-runs/P0056K/lag-protocol.md
requirements/package-runs/P0056K/leakage-review.md
requirements/package-runs/P0056L/comparison-vs-p0056k.md
src/mac/** forecast/model/feature/evaluation scripts
tests/mac/** relevant tests
memory/energy-market-ai-lab.md
```

## Files allowed to change

```text
requirements/packages/P0056M-labb-se2-m6-dayahead-error-slice-analysis.md
requirements/package-runs/P0056M/**
src/mac/** narrowly scoped diagnostic/slice-analysis code if needed
tests/mac/** narrowly scoped tests if analysis code is added
local DB metrics tables if repo owns them and only for P0056M outputs
```

## Forbidden changes

```text
No Shelly changes.
No Home Assistant changes.
No device/runtime writes.
No production deployment.
No G2-KANDIDAT promotion.
No spot price features.
No flow/exchange/A61/capacity features.
No old physical_balance target.
No future actual load leakage.
No retraining or changing M6 model logic just to improve results.
No large model artifacts or large full prediction dumps.
```

## Pass / WARN / STOP

PASS requires:

```text
SE2 M6 realistic DayAhead results are analyzed
weekday/month/season/temperature/load/ramp slices are produced
top 5 best and top 5 worst DayAhead tests are listed
pattern review explains likely failure modes
leakage review passes
```

WARN is acceptable if:

```text
some optional slice cannot be computed due to missing column
hour-level CSV is replaced by compact summary
M6 forecasts must be reconstructed instead of loaded
```

STOP if:

```text
P0056K SE2 M6 predictions cannot be loaded or reconstructed
DayAhead origin safety cannot be verified
future actual load leakage is found
required weather/load context is missing
```

## Expected Codex output

```text
PASS/WARN/STOP status
commit SHA
number of delivery days analyzed
P0056K SE2 M6 baseline confirmation
worst weekday / best weekday
worst month / best month
worst season / best season
cold vs mild vs warm conclusion
winter vs summer conclusion
high-load/high-ramp conclusion
five best tests
five worst tests
most likely failure patterns
recommended next package
files changed
tests/commands run
confirmation no forbidden features/no device/runtime/no production/no large artifacts
```

## Completion notes

Completed by Codex in package-run evidence:

```text
requirements/package-runs/P0056M/
```

Result:

```text
PASS
```

Summary:

```text
area = SE2
model = M6 WeightedEnsemble_no_price
delivery_days_analyzed = 240
hour_rows_analyzed = 5760
failures = 0
```

P0056K baseline confirmation:

```text
expected_DayAhead_hourly_MAE = 232.69280738198043 MW
reconstructed_DayAhead_hourly_MAE = 232.69280738198046 MW
delta_MW = 2.842170943040401e-14
matches_within_tolerance = true
```

Key findings:

```text
worst_weekday = Saturday, 315.61303173687025 MW
best_weekday = Tuesday, 193.08046986119035 MW
worst_month = March, 341.3950702454978 MW
best_month = July, 127.70761004306254 MW
worst_season = winter, 271.4100231609917 MW
best_season = summer, 136.58010116535152 MW
error_mode = isolated hourly spikes
cold_vs_warm_hot = cold 109.249 MW higher MAE
mild_vs_cold_warm_average = mild 50.551 MW higher MAE
winter_half_vs_summer_half = winter_half 107.678 MW higher MAE
high_load_vs_low_load = high-load 134.490 MW higher MAE
high_ramp_vs_low_ramp = high-ramp 162.673 MW higher MAE
```

Safety:

```text
No API.
No devices.
No runtime changes.
No production activation.
No spot-price, flow/exchange/A61/capacity or old physical_balance features.
No future actual load used as a prediction feature.
```

Post-run interpretation:

```text
requirements/package-runs/P0056M/forecast-error-interpretation.md
```

Interpretation summary:

```text
The primary issue appears to be missing regime/target-quality understanding, not simply weak regressor capacity.
The most suspicious case is 2026-03-28, where SE2 mean actual load jumps to 5487.607639 MW while neighboring days are near 1800..2200 MW.
Next step should audit target anomaly, native/source rows, DST/local-day handling and high-ramp/high-load regimes before model changes.
```
