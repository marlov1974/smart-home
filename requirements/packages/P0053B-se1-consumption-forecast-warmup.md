# Package P0053B: SE1 consumption forecast warmup

## Status

done

## Package order

P0053B

## Primary area

G2 / Mac tooling / spotprice V2 / physical market signals / SE1 consumption forecast / forecast-safe load modeling

## Decision summary

P0053A created the first complete physical-balance + internal-flow analysis dataset:

```text
P0051 production/consumption/net-load
+ P0053A A09 scheduled exchange
+ P0053A A11 physical flow
+ SE1/SE3 prices and SE3-SE1
```

Before modeling SE1 price or SE3-SE1, the next step is a clean warmup problem:

```text
Forecast SE1 consumption.
```

Rationale:

```text
- Consumption is the cleanest physical target to forecast first.
- SE1 price formation should later treat import as supply/production and export as demand/consumption.
- Production is likely partly a function of both local consumption and export demand, so it is less pure as a first target.
- Export/import is a complex chain event and can originate from southward market pressure far outside SE1.
```

P0053B must therefore build and evaluate forecast-safe SE1 consumption models only. It must not forecast SE1 price, production, export/import, SE3 price or SE3-SE1.

## Preconditions

P0053B may start only after P0051 PASS and P0053A WARN/PASS evidence exists.

Required P0051 facts:

```text
- eSett production/consumption exists for SE1-SE4.
- physical_balance_se1_se4_hourly_v1 exists.
- consumption_se1 exists across the historical modeling period.
- fixed-CET fields exist.
```

Required P0053A facts:

```text
- physical_balance_flow_exchange_analysis_v1 exists for 2022-05-29T23:00:00Z .. 2026-05-25T22:00:00Z.
- A09/A11 are historical observed only.
- A61 remains excluded from derived features.
```

P0053B should use P0051/P0053A tables for context, but target only:

```text
consumption_se1
```

## Scope

P0053B owns:

```text
1. Build a forecast-safe SE1 consumption modeling dataset.
2. Define train/validation/holdout chronological splits.
3. Build baseline consumption forecasts.
4. Build weather/calendar/load-history feature groups.
5. Train lightweight forecasting models for horizons relevant to later 7-day price modeling.
6. Evaluate accuracy by horizon, hour, weekday, season and special day.
7. Decide whether SE1 consumption forecast is good enough to become a physical intermediate signal.
8. Recommend the next consumption/production/export-import forecasting package.
```

## Hard non-goals

P0053B must not:

```text
- forecast SE1 price
- forecast SE3 price
- forecast SE3-SE1
- forecast production
- forecast export/import or flow/exchange
- use future actual consumption as feature leakage
- use future actual A09/A11 flow/exchange as feature leakage
- use A61 capacity for anything
- build production API
- anchor SE1 to SE3
- train direct SE3 AI-1/AI-2
- touch Shelly/Home Assistant/KVS/devices
- build M5/M6/M7
- ingest continental price levels
- ingest futures/forward curves
```

Exploratory models are allowed only for SE1 consumption and must be labeled non-deployable unless explicitly forecast-safe.

## Target definition

Primary target:

```text
consumption_se1_mw
```

Source should be the canonical P0051 physical balance table/view.

Unit:

```text
MW hourly mean
```

P0053B must confirm:

```text
- target source table/view
- timestamp range
- missingness
- unit
- whether values are already hourly aggregated from quarter-hour eSett data
```

## Forecast horizons

P0053B must evaluate horizons aligned with future 7-day price forecasting.

Required horizons:

```text
1h
3h
6h
12h
24h
48h
72h
96h
120h
144h
168h
```

Two evaluation modes are required:

### Direct horizon mode

For each timestamp `t`, predict:

```text
consumption_se1[t + horizon]
```

using only features known at or before `t`, plus forecast-safe calendar/weather-normal features.

### 7-day path mode

For forecast origins, predict the next 168 hourly values:

```text
t+1 .. t+168
```

Report aggregate path metrics.

## Forecast-safety rules

Allowed features:

```text
- calendar/fixed-CET fields for target timestamp
- daytype/holiday/bridge-day/special-day known in advance
- season/day-of-year sin/cos
- model_cet_hour sin/cos
- weekday one-hot/cyclical
- historical/lagged SE1 consumption observed before forecast origin
- rolling SE1 consumption statistics ending before forecast origin
- weather normal/forecast-like features if already available in repo as forecast-safe or proxy
- temperature/solar/wind normal deviations only if timestamp semantics are forecast-safe for the simulated horizon
```

Forbidden leakage features:

```text
- actual future consumption_se1
- actual future production
- actual future A09/A11 flow/exchange
- actual future prices
- actual future realized weather if not clearly modeled as forecast input
```

P0053B must classify every feature group as:

```text
forecast_safe
historical_only_diagnostic
excluded_leakage
```

## Feature groups

Required groups:

```text
G0_calendar_only
G1_calendar_plus_recent_load_lags
G2_calendar_plus_load_rollups
G3_weather_normal_or_forecast_safe_weather
G4_calendar_load_lags_weather
G5_special_day_enhanced
G6_diagnostic_historical_only_non_deployable
```

### Calendar features

At minimum:

```text
target_model_cet_hour
target_model_cet_weekday
target_model_cet_day_of_year
target_month
target_hour_sin
target_hour_cos
target_dayofyear_sin
target_dayofyear_cos
is_weekend
is_workday
is_holiday
is_bridge_day
is_holiday_period
```

### Load lag features

Use only values observed before forecast origin:

```text
consumption_se1_lag_1h
consumption_se1_lag_2h
consumption_se1_lag_3h
consumption_se1_lag_6h
consumption_se1_lag_12h
consumption_se1_lag_24h
consumption_se1_lag_48h
consumption_se1_lag_72h
consumption_se1_lag_168h
```

Rolling windows ending before forecast origin:

```text
consumption_se1_roll_mean_6h
consumption_se1_roll_mean_12h
consumption_se1_roll_mean_24h
consumption_se1_roll_mean_48h
consumption_se1_roll_mean_168h
consumption_se1_roll_min_24h
consumption_se1_roll_max_24h
consumption_se1_roll_std_24h
```

### Weather features

Use available SE1/north/system weather fields if forecast-safe or clearly simulated as forecast input.

Candidates:

```text
temperature_north_or_se1
wind_100m_north_or_se1
solar_radiation_north_or_se1
temperature_delta_from_normal
wind_delta_from_normal
solar_delta_from_normal
heating_degree_proxy
cooling_degree_proxy if relevant
```

If only actual realized weather exists, P0053B may include it in `G6_diagnostic_historical_only_non_deployable`, but the deployable score must exclude it unless the repo already treats it as forecast input.

## Baselines

Required baselines:

```text
B0_same_hour_previous_day = consumption[t+h-24h]
B1_same_hour_previous_week = consumption[t+h-168h]
B2_calendar_hour_weekday_profile train-only
B3_seasonal_hour_weekday_profile train-only
B4_recent_24h_mean adjusted by hour profile
```

All profile baselines must be fit on train only.

## Models

Keep models lightweight and interpretable.

Allowed:

```text
LinearRegression / Ridge / Lasso
ElasticNet
HistGradientBoostingRegressor
RandomForestRegressor if already dependency-safe
shallow DecisionTreeRegressor for interpretation
simple ensemble of baseline + residual model
```

Not allowed:

```text
neural nets
transformers
AutoML
heavy dependencies
production deployment artifacts
```

## Splits

Use chronological splits.

Preferred split:

```text
train: earliest .. 2024-12-31
validation: 2025-01-01 .. 2025-12-31
holdout: 2026-01-01 .. latest
```

If data coverage requires a different split, document why.

No random split is allowed.

## Metrics

Required metrics by horizon and path:

```text
MAE
RMSE
median_absolute_error
p90_absolute_error
p95_absolute_error
bias
MAPE or sMAPE if safe around low values
R2 only as secondary diagnostic
```

Required breakdowns:

```text
by horizon
by model_cet_hour
by weekday/weekend
by month/season
by holiday/special day
by temperature bucket if weather is used
pre/post flow-based flag only as diagnostic, not expected consumption driver
```

Path metrics:

```text
MAE_0_24h
MAE_24_48h
MAE_48_72h
MAE_72_168h
MAE_full_168h
bias_full_168h
peak_hour_error
daily_energy_error_proxy = sum(predicted_mw - actual_mw) over each model_cet_date
```

## Error review

P0053B must identify where SE1 consumption is hard to forecast:

```text
- cold snaps
- holidays
- bridge days
- weekends
- early mornings/evening peaks
- rapid weather changes
- summer low-load periods
```

Report top error days and whether errors appear due to calendar, weather or missing special-day handling.

## Required evidence files

P0053B must create:

```text
requirements/package-runs/P0053B/CHANGELOG.md
requirements/package-runs/P0053B/review.md
requirements/package-runs/P0053B/design.md
requirements/package-runs/P0053B/functions.md
requirements/package-runs/P0053B/dataset-contract.md
requirements/package-runs/P0053B/forecast-safety-review.md
requirements/package-runs/P0053B/feature-groups.md
requirements/package-runs/P0053B/baseline-results.md
requirements/package-runs/P0053B/model-results.md
requirements/package-runs/P0053B/horizon-metrics.md
requirements/package-runs/P0053B/path-168h-metrics.md
requirements/package-runs/P0053B/feature-importance.md
requirements/package-runs/P0053B/error-review.md
requirements/package-runs/P0053B/forecast-readiness-assessment.md
requirements/package-runs/P0053B/next-package-recommendation.md
requirements/package-runs/P0053B/component-attribution-summary.md
```

Optional machine-readable evidence:

```text
requirements/package-runs/P0053B/metrics-summary.json
requirements/package-runs/P0053B/horizon-metrics.csv
requirements/package-runs/P0053B/path-metrics.csv
requirements/package-runs/P0053B/top-error-days.csv
requirements/package-runs/P0053B/modeling-dataset-sample.csv
```

Do not commit model binaries or large generated datasets.

## Required answers

P0053B must explicitly answer:

```text
1. Which source table/view supplied consumption_se1?
2. What timestamp range and missingness does the target have?
3. Which features were forecast-safe and which were excluded as leakage?
4. Which baseline is strongest?
5. Which model/feature group is strongest by 1h/24h/48h/168h horizon?
6. What is the 168h path MAE and bias?
7. Does weather improve SE1 consumption forecast materially over calendar+lag features?
8. Are holiday/bridge-day errors material?
9. Is SE1 consumption forecast good enough to become an intermediate feature for later SE1 price modeling?
10. What should be forecast next: SE2/SE3/SE4 consumption, SE1 production, or SE1 export/import?
11. Confirm no SE1 price model, no SE3 model, no A61 utilization, no future actual flow/exchange leakage, no API and no device actions.
```

## Tests

Required automated tests:

```text
- target consumption_se1 exists and is numeric/finite
- timestamp_utc normalized and unique
- fixed-CET fields present
- chronological splits are non-overlapping
- lag features do not peek past forecast origin
- rolling features end before forecast origin
- train-only profiles are fit on train only
- weather feature group is classified forecast-safe or diagnostic-only
- no future actual prices used
- no future actual A09/A11 flow/exchange used
- no A61 capacity used
- 168h path generation produces exactly 168 hourly predictions per full origin
- metrics are reproducible
- no production API/model artifact created
- no M5/M6/M7/API/device path touched
```

## Pass/fail interpretation

PASS requires:

```text
- forecast-safe SE1 consumption dataset is built
- baselines and at least one lightweight model are evaluated
- horizon and 168h path metrics are reported
- leakage review is explicit
- next package recommendation is explicit
- forbidden price/export/production/API/device work is not done
```

WARN is acceptable if:

```text
- weather forecast-safe status is unclear and weather is limited to diagnostic-only
- holiday errors remain high but are documented
- 168h path performance is usable only with lag/calendar features
- model beats baselines only at some horizons
```

STOP if:

```text
- target data is unreliable
- leakage is detected in deployable feature groups
- chronological splits fail
- Codex starts price/export/production modeling
- Codex uses A61 utilization or future actual A09/A11 as forecast features
- Codex creates API/device work
```

## Expected Codex output

- PASS/WARN/STOP status
- source table and target coverage
- feature-safety summary
- baseline results
- model results by horizon
- 168h path metrics
- top error patterns
- forecast readiness assessment
- recommendation for next package
- tests run
- files changed
- confirmation of no price/export/production/A61/API/device work
- commit SHA after push

## Completion notes

Completed with status: PASS.

Implemented:

- `src/mac/services/spotprice_model_diagnostics/p0053b.py`
- `tests/mac/services/spotprice_model_diagnostics/test_p0053b.py`
- P0053B evidence under `requirements/package-runs/P0053B/`
- Durable function documentation update under `docs/functions/`

Source and target:

```text
source_table = physical_balance_se1_se4_hourly_v1
target = consumption_se1
unit = MW hourly mean
source_range = 2022-05-29T23:00:00Z .. 2026-05-25T22:00:00Z
source_rows = 34968
missing/nonfinite/nonpositive target values = 0
```

Modeling output:

```text
dataset_table = se1_consumption_forecast_warmup_v1
direct_horizon_rows = 382106
train rows = 247466
validate rows = 96360
holdout rows = 38280
path metric rows = 1006
```

Best results:

```text
best baseline = pred_B0_same_hour_previous_day, horizon 1h, holdout MAE 13.390 MW
best forecast-safe model = M4_Ridge_G4_calendar_load_lags_weather, horizon 1h, holdout MAE 6.935 MW
relative improvement vs best baseline = 48.21%
168h best holdout path baseline = B4_recent_24h_adjusted_path, full-path MAE 24.285 MW, bias 4.705 MW
```

Forecast-safety result:

- Forecast-safe groups use target calendar, Swedish special-day fields, origin-safe load lags/rollups and train-only weather normals.
- Actual realized weather is limited to `G6_diagnostic_historical_only_non_deployable`.
- No future actual consumption, price, production, A09/A11 flow/exchange or A61 capacity is used in forecast-safe groups.

Recommendation:

```text
SE1 consumption is good enough to become a physical intermediate signal for later SE1 price modeling.
Forecast SE2/SE3/SE4 consumption next before SE1 production or export/import.
```

Verification:

```text
PYTHONPYCACHEPREFIX=/private/tmp/p0053b-pycache python3 -m unittest tests.mac.services.spotprice_model_diagnostics.test_p0051 tests.mac.services.spotprice_model_diagnostics.test_p0053a tests.mac.services.spotprice_model_diagnostics.test_p0053b
git diff --check
```

No SE1 price model, SE3 model, SE3-SE1 model, production forecast, export/import forecast, A61 utilization, production API, deployable model artifact, M5/M6/M7, Shelly, Home Assistant, KVS or device action was performed.
