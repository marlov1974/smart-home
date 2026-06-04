# Package P0054K: LABB SE3 consumption AI with SE3 spot price forecast

## Status

planned

## Package order

P0054K

## Label

```text
LABB
```

This package is research/lab work under P0054A. It is not a G2-KANDIDAT evaluation.

## Purpose

Copy the successful SE1 workflow to SE3: create a forecast-origin-safe SE3 spot price forecast source using the same package-scoped safe method as P0054H, then train and evaluate SE3 consumption forecast models with and without that SE3 spot price forecast.

The hypothesis is that SE3 consumption may show stronger price sensitivity than SE1, so the with-price models may improve more clearly than P0054J did for SE1.

## Operator decision

Use the same train/holdout policy as P0054I/P0054J:

```text
train_fit:  2022-06-01T00:00:00Z .. 2025-05-31T23:00:00Z
holdout:    2025-06-01T00:00:00Z .. latest_available_timestamp_utc
```

Final reported comparisons must score only June 2025 and forward.

## Core questions

P0054K must answer:

```text
1. Can the P0054H forecast-safe origin-local spot price baseline be replicated for SE3?
2. What is the best SE3 consumption model without spot price forecast features?
3. What is the best SE3 consumption model with forecast-safe SE3 spot price forecast features?
4. Does SE3 show stronger price-forecast benefit than SE1/P0054J?
5. Which model family benefits most from SE3 price forecast: HGB, ExtraTrees, LightGBM, XGBoost or MLP if run?
6. Should SE3 price forecast features be kept for future spread/flaskhals/response experiments?
```

## Required phases

P0054K has two phases in one package:

```text
Phase A: SE3 forecast-safe spot price forecast log
Phase B: SE3 consumption no-price vs with-price-forecast ablation
```

Phase B must not run unless Phase A passes leakage and coverage checks.

## Phase A: SE3 spot price forecast source

Create or reuse a forecast-origin-safe SE3 anchored absolute spot price forecast log using the same safe package-scoped method as P0054H unless a better train-covered forecast-origin-safe SE3 source already exists.

Preferred table name:

```text
anchored_absolute_price_forecast_log_p0054k_se3_v1
```

Required label if using P0054H-style method:

```text
quality_flag = forecast_safe_origin_local_baseline_not_m4
training_protocol = origin_local_no_fit_pre_origin_history
```

Important label:

```text
This is not M4. It is a forecast-safe origin-local historical SE3 spot price baseline.
```

Do not call it M4 unless a true forecast-origin-safe M4/rolling-origin implementation is used and documented.

### Phase A required schema semantics

Each row must include or be joinable to:

```text
area = SE3
prediction_kind = anchored_absolute_price
forecast_origin_timestamp_utc
input_data_cutoff_utc
target_timestamp_utc
horizon_hour
predicted_price
prediction_unit
anchor_window_start_utc
anchor_window_end_utc
quality_flag
training_protocol
source_model_family / method name
package_id = P0054K
```

Names may follow local conventions, but these semantics must be documented.

### Phase A leakage rules

For every generated SE3 price forecast row:

```text
input_data_cutoff_utc <= forecast_origin_timestamp_utc
forecast_origin_timestamp_utc <= target_timestamp_utc
all prediction-source price timestamps < forecast_origin_timestamp_utc
no target-window actual price is used as forecast input
no validation/holdout actual target data is used for train-origin fitting
no holdout is used for selection or fitting
```

Forbidden price-source behavior:

```text
actual future spot price inside target_window as input
P0053C-B validation/holdout-only forecast as train feature
live market API calls
```

## Phase B: SE3 consumption target

Primary target:

```text
consumption_se3_mw
```

Use the canonical physical-balance source if it contains SE3 consumption. If the current `physical_balance_se1_se4_hourly_v1` only contains SE1 and SE4, Codex must discover the repository's best local source for SE3 consumption and document it.

Potential acceptable target source examples:

```text
physical_balance_se1_se4_hourly_v1 successor with SE3
ENTSO-E/energy balance local hourly table with SE3 consumption
existing P0053/P0054 LABB table containing SE3 load/consumption
```

STOP if no reliable local SE3 consumption target exists under the required period.

Unit:

```text
MW hourly mean
```

Codex must document exact source table/file, target column, unit, coverage, missingness and timestamp semantics.

## Required split policy

Use:

```text
train_fit: target_timestamp_utc >= 2022-06-01T00:00:00Z
           and target_timestamp_utc < 2025-06-01T00:00:00Z

holdout:   target_timestamp_utc >= 2025-06-01T00:00:00Z
```

No holdout rows may be used for fitting, early stopping, hyperparameter selection, feature selection or model-family selection.

Any internal early-stopping split must be carved out strictly inside `train_fit`.

## Weather proxy

Use the best existing SE3 weather proxy if present.

If no SE3 weather proxy exists, create a minimal LABB SE3 proxy only if source architecture already supports it. Preferred SE3 load/weather representation may include major SE3 load centers such as Stockholm/Mälardalen/Göteborg depending on available project data, but do not overbuild this package.

If weather source/proxy is not available, Codex may run a no-weather baseline only if it clearly labels the limitation. Prefer using existing weather-history proxy architecture where possible.

Weather remains LABB actual-as-forecast proxy unless a separate forecast weather source is documented:

```text
weather_actual_as_forecast_proxy
```

## Feature variants

### Variant A: no_price

Allowed feature groups:

```text
calendar/time known in advance
historical SE3 consumption lags and rollups strictly before forecast origin
SE3 weather proxy fields where available
```

### Variant B: with_p0054k_se3_price_forecast

Variant A plus forecast-safe P0054K SE3 price forecast features.

Minimum price feature:

```text
predicted_price
```

Recommended bounded additional price forecast features, computed only from the forecast path available at the same origin:

```text
price_forecast_horizon_value
price_forecast_0_24h_mean
price_forecast_24_48h_mean
price_forecast_0_168h_mean
price_forecast_rank_within_path
price_forecast_spike_flag_within_path
price_forecast_ramp_from_previous_horizon
price_forecast_peak_offpeak_indicator
```

If additional features are implemented, prove they derive only from forecast rows available at `forecast_origin_timestamp_utc`.

## Forbidden inputs

The model feature matrix must not contain:

```text
actual future spot price
same-hour realized spot price for target timestamp unless known at forecast origin
M4/P0053C-B validation/holdout-only forecast as train feature
production
future production
export/import
future actual A09/A11 flow/exchange
A61 capacity/utilization/margin
continental actual prices
target-window actual consumption beyond forecast origin
```

Historical SE3 consumption lags and rollups are allowed only when strictly before the forecast origin.

## Required models

Run these model families where available:

```text
HGB
ExtraTrees
LightGBM
XGBoost
MLP if practical
```

Minimum required model set:

```text
HGB_no_price
HGB_with_p0054k_se3_price_forecast
ExtraTrees_no_price
ExtraTrees_with_p0054k_se3_price_forecast
LightGBM_no_price
LightGBM_with_p0054k_se3_price_forecast
XGBoost_no_price
XGBoost_with_p0054k_se3_price_forecast
```

MLP is optional if runtime is high or existing pipeline does not support it cleanly, but the skip must be documented.

Use identical rows for each paired no-price vs with-price comparison.

## Hyperparameter policy

Use bounded, sensible hyperparameters based on P0054J. Do not perform broad tuning. Holdout must never influence hyperparameters.

For LightGBM and XGBoost, use installed/imported versions from P0054E if still available.

## Evaluation

Final scoring period:

```text
holdout only: target_timestamp_utc >= 2025-06-01T00:00:00Z
```

Direct horizons:

```text
1h, 3h, 6h, 12h, 24h, 48h, 72h, 96h, 120h, 144h, 168h
```

Weekly 168h path evaluation:

```text
weekly origins from 2025-06-01 onward where complete 168h paths exist
```

Direct metrics:

```text
MAE
RMSE
bias
median absolute error
p90
p95
sMAPE
MAE percent of mean/median actual
R2 where useful
```

Path metrics:

```text
MAE_0_24h
MAE_24_48h
MAE_48_72h
MAE_72_168h
MAE_full_168h
bias_full_168h
p90/p95 full path
daily energy error proxy
peak load hour error
```

Conditional metrics:

```text
cold hours
very cold hours
rapid temperature drop
weekday
weekend
holiday
morning ramp
evening peak
summer low load
winter high load
high forecast price
low forecast price
large forecast price ramp
forecast price spike
```

## Required comparisons

P0054K must report:

```text
1. SE3 price forecast log coverage and leakage review.
2. Best no-price SE3 consumption model by holdout MAE.
3. Best with-price SE3 consumption model by holdout MAE.
4. Best no-price model by weekly MAE_full_168h.
5. Best with-price model by weekly MAE_full_168h.
6. Per-model delta from adding SE3 price forecast: with_price - no_price.
7. Whether SE3 price forecast improves or worsens each model.
8. Whether SE3 shows stronger price benefit than SE1/P0054J.
9. Conditional regimes where SE3 price forecast helps or hurts.
10. Whether SE3 price forecast should be kept for future experiments.
```

Negative MAE delta means the spot price forecast helped.

Learning threshold:

```text
Price forecast is useful if it improves holdout MAE or weekly MAE_full_168h by >= 2%, or improves >= 3% in at least two important price/temperature/load regimes without materially worsening broad holdout metrics.
```

Compare qualitatively and, if possible, numerically against P0054J SE1 deltas:

```text
P0054J XGBoost with-price vs no-price:
  holdout MAE improvement about 0.12%
  weekly 168h improvement about 1.31%
```

## Required evidence files

Create:

```text
requirements/package-runs/P0054K/CHANGELOG.md
requirements/package-runs/P0054K/review.md
requirements/package-runs/P0054K/design.md
requirements/package-runs/P0054K/functions.md
requirements/package-runs/P0054K/labb-label.md
requirements/package-runs/P0054K/split-policy-applied.md
requirements/package-runs/P0054K/se3-price-forecast-source-contract.md
requirements/package-runs/P0054K/se3-price-forecast-log-schema.md
requirements/package-runs/P0054K/se3-price-forecast-coverage.md
requirements/package-runs/P0054K/se3-price-forecast-leakage-review.md
requirements/package-runs/P0054K/dataset-contract.md
requirements/package-runs/P0054K/input-classification.md
requirements/package-runs/P0054K/feature-groups.md
requirements/package-runs/P0054K/model-training-evidence.md
requirements/package-runs/P0054K/no-price-results.md
requirements/package-runs/P0054K/with-price-forecast-results.md
requirements/package-runs/P0054K/price-forecast-ablation.md
requirements/package-runs/P0054K/model-comparison.md
requirements/package-runs/P0054K/direct-horizon-results.md
requirements/package-runs/P0054K/weekly-168h-path-results.md
requirements/package-runs/P0054K/conditional-regime-results.md
requirements/package-runs/P0054K/se3-vs-se1-price-effect-comparison.md
requirements/package-runs/P0054K/feature-importance-or-attribution.md
requirements/package-runs/P0054K/interpretation.md
requirements/package-runs/P0054K/what-we-learned.md
requirements/package-runs/P0054K/next-package-recommendation.md
```

Optional compact evidence:

```text
metrics-summary.json
price-ablation-summary.json
weekly-path-metrics.csv
conditional-metrics.csv
se3-price-forecast-summary.json
modeling-dataset-sample.csv
training-history.csv
```

Do not commit large raw datasets, model binaries, virtualenvs, wheels or caches.

## Files to inspect

```text
requirements/package-runs/P0054J/CHANGELOG.md
requirements/package-runs/P0054J/model-comparison.md
requirements/package-runs/P0054J/price-forecast-ablation.md
requirements/package-runs/P0054J/input-classification.md
requirements/package-runs/P0054J/split-policy-applied.md
requirements/package-runs/P0054H/CHANGELOG.md
requirements/package-runs/P0054H/forecast-method-contract.md
requirements/package-runs/P0054H/leakage-review.md
requirements/package-runs/P0054H/downstream-contract-for-p0054f-retry.md
requirements/package-runs/P0054E/import-validation.md
memory/energy-market-ai-lab.md
memory/spotprice-forecast-period-policy.md
docs/functions/mac/weather-history-dataset.md
docs/functions/mac/spotprice-model-diagnostics.md
local SQLite table metadata for SE3 price/consumption/weather sources
relevant local source files for P0054J modeling experiment
```

Do not read large raw data files during bootstrap unless required by package verification/modeling commands.

## Files allowed to change

```text
requirements/packages/P0054K-labb-se3-consumption-spotprice-forecast-ai.md
requirements/package-runs/P0054K/**
docs/functions/mac/spotprice-model-diagnostics.md if durable docs need updating
src/mac/** relevant existing LABB price forecast or consumption modeling scripts if changes are needed
tests/mac/** relevant tests for changed modeling code
```

## Forbidden changes

```text
No Shelly changes.
No Home Assistant changes.
No device/API/runtime writes.
No production deployment.
No G2-KANDIDAT promotion.
No actual future spot price leakage.
No P0053C-B validation/holdout-only M4 forecast as train feature.
No production/export/import/A61/future-flow features.
No live API calls.
No large raw dataset commits.
No model binary commits.
No virtualenv/wheel/cache commits.
No broad refactor unrelated to P0054K.
```

## Live/API/device policy

Live testing allowed: no.

Device/API/runtime actions allowed: no.

No external live market API calls are allowed for model features. Price forecast input must come from local forecast-safe generation/source.

## Verification commands

Codex must define final commands in `design.md`, but must run equivalent checks for:

```text
P0054I/P0054J train_fit/holdout split applied
SE3 price forecast source contract verified
SE3 price rows cover train_fit and holdout
SE3 consumption target source verified
no-price and with-price matrices use identical target rows per model
with-price matrix contains only forecast-safe SE3 price forecast columns
feature matrix contains no actual future price/production/flow/A61 columns
LightGBM/XGBoost import status OK or documented
weekly 168h paths are complete or skipped with reason
no large data/model/env artifacts are staged
git diff --check
```

## Pass / WARN / STOP interpretation

PASS requires:

```text
- forecast-safe SE3 price forecast log exists with train_fit and holdout coverage.
- SE3 consumption target is found and validated.
- HGB, ExtraTrees, LightGBM and XGBoost are evaluated in paired no-price/with-price form.
- Price forecast ablation is reported on identical rows.
- Best model and SE3 price-feature effect are clear.
- SE3-vs-SE1 price-effect comparison is reported.
- No leakage or runtime/device actions occurred.
```

WARN is acceptable if:

```text
- MLP is skipped for runtime or pipeline constraints.
- one boosted model fails but the other runs with evidence.
- weather proxy is weaker/missing but documented.
- SE3 price forecast does not help, but the negative result is clean.
```

STOP if:

```text
- no reliable local SE3 consumption target exists.
- SE3 price source cannot cover train_fit and holdout safely.
- actual future spot price leaks into features.
- forbidden production/flow/A61/future features enter the matrix.
- holdout is used for fitting or model selection.
- device/API/runtime work is created.
```

## Expected Codex output

```text
PASS/WARN/STOP status
SE3 price forecast source/log summary
SE3 target/data coverage
split policy summary
input classification summary
models run
best no-price model
best with-price model
per-model price forecast MAE deltas
weekly 168h path deltas
conditional/regime findings
SE3-vs-SE1 price-effect comparison
whether advanced AI benefits from SE3 price forecast
whether SE3 price forecast should be kept
what we learned
next package recommendation
tests/commands run
files changed
confirmation of no actual future price/API/device/A61/leakage work
confirmation no large artifacts committed
commit SHA after push
```

## Completion notes

To be filled after implementation.
