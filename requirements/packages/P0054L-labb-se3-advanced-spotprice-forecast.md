# Package P0054L: LABB SE3 advanced spot price forecast

## Status

planned

## Package order

P0054L

## Label

```text
LABB
```

This package is research/lab work under P0054A. It is not a G2-KANDIDAT evaluation.

## Purpose

Build and evaluate a better forecast-origin-safe SE3 spot price forecast than the simple origin-local historical baseline used in P0054K.

P0054K showed that the SE3 price forecast signal was useful for some model families and conditional regimes, especially LightGBM, but it worsened the strongest SE3 consumption model, XGBoost. The working hypothesis is:

```text
SE3 consumption may still have price sensitivity, but the P0054K price forecast is too noisy/weak to help the best consumption model.
```

P0054L must improve the SE3 price forecast itself before any downstream SE3 consumption ablation is retried.

## Important scope boundary

This package trains/evaluates SE3 spot price forecast models only.

It must not rerun SE3 consumption models. A later package should use the best P0054L forecast as a downstream consumption feature.

Recommended follow-up if P0054L produces a useful price forecast:

```text
P0054M LABB SE3 consumption with advanced SE3 spot price forecast
```

## Prior evidence to preserve

P0054K baseline price forecast source:

```text
anchored_absolute_price_forecast_log_p0054k_se3_v1
quality_flag = forecast_safe_origin_local_baseline_not_m4
training_protocol = origin_local_no_fit_pre_origin_history
```

P0054K result summary:

```text
Best SE3 consumption model overall: XGBoost_no_price
P0054K price forecast helped LightGBM but worsened XGBoost.
SE3 did not show stronger broad XGBoost price benefit than SE1.
```

P0054L must keep P0054K as the baseline to beat, not silently replace it.

## Core questions

P0054L must answer:

```text
1. Can a stronger forecast-origin-safe SE3 spot price model beat the P0054K origin-local historical baseline?
2. Which model family best forecasts SE3 price under the P0054 train-through-May-2025 policy?
3. Does the stronger model improve price MAE/RMSE and also spike/ramp/top-bottom ranking metrics?
4. Is the resulting forecast safe and sufficiently covered for downstream SE3 consumption use?
5. Should P0054M rerun SE3 consumption with this improved price forecast?
```

## Split policy

Use the P0054I/P0054J/P0054K operator-approved LABB split:

```text
train_fit: timestamp_utc >= 2022-06-01T00:00:00Z
           and timestamp_utc < 2025-06-01T00:00:00Z

holdout:   timestamp_utc >= 2025-06-01T00:00:00Z
```

No holdout row may be used for fitting, early stopping, hyperparameter selection, feature selection or model-family selection.

If internal validation is needed, carve it strictly from inside `train_fit`, for example the final part of train_fit:

```text
internal_train:      2022-06-01 .. 2025-02-28
internal_validation: 2025-03-01 .. 2025-05-31
```

Exact internal split may differ, but must remain fully before 2025-06-01 and must be documented.

## Target

Primary target:

```text
spot_price_se3
```

or the repository's canonical SE3 spot price column/source.

Codex must document exact source table/file, area, column, unit, currency, VAT/tax semantics if known, timestamp semantics, coverage and missingness.

Preferred unit:

```text
SEK/kWh or EUR/MWh, matching existing repository convention.
```

Do not mix units across features/targets without explicit conversion and documentation.

## Forecast product to create

Create a forecast-origin-safe SE3 price forecast log suitable for downstream consumption features.

Preferred table name:

```text
advanced_spotprice_forecast_log_p0054l_se3_v1
```

If multiple candidate models are persisted, either include `model_name` in the table or create clearly named tables/views. The downstream contract must identify the recommended model/view.

Each row must include or be joinable to:

```text
area = SE3
prediction_kind
model_name
forecast_origin_timestamp_utc
input_data_cutoff_utc
target_timestamp_utc
horizon_hour
predicted_price
prediction_unit
training_protocol
training_cutoff_utc or equivalent
feature_cutoff_utc or equivalent
package_id = P0054L
created_at / run_id if existing conventions support it
```

The forecast path should normally be 168h long per origin unless skipped and documented.

## Forecast-origin semantics

For every forecast origin:

```text
input_data_cutoff_utc = forecast_origin_timestamp_utc - 1h
forecast_origin_timestamp_utc <= target_timestamp_utc
target_window = [forecast_origin_timestamp_utc, forecast_origin_timestamp_utc + 167h]
horizon_hour = hours between origin and target timestamp
```

All features for a forecast row must be known at or before the forecast origin.

## Required baseline

Evaluate P0054K's SE3 origin-local historical baseline as the benchmark:

```text
anchored_absolute_price_forecast_log_p0054k_se3_v1
```

Report its metrics on the same comparable holdout origins/targets used for P0054L candidate models.

## Candidate models

Run bounded, dependency-safe candidates from the existing LABB environment:

```text
HGB
ExtraTrees
LightGBM
XGBoost
simple ensemble/blend of best safe candidates if useful
```

Optional if practical:

```text
Ridge/ElasticNet baseline
MLP
quantile variants or two-stage spike model
```

Do not install new large dependencies unless already approved by repository convention. LightGBM/XGBoost were installed during P0054E and should be reused if still available.

## Feature groups

Use only forecast-origin-safe price/calendar/history features.

Allowed features:

```text
calendar/time known in advance
hour/day/week/month/holiday features if already available or simple to compute
historical SE3 price lags strictly before origin
historical SE3 price rolling stats strictly before origin
historical volatility/spread/ramp stats strictly before origin
previous-week same-hour price strictly before origin
previous-48h anchor/history features strictly before origin
forecast horizon hour
known market calendar features
```

Optional allowed if locally available and forecast-origin safe:

```text
other Swedish area historical price lags strictly before origin
system price historical lags strictly before origin
```

Forbidden features:

```text
actual future SE3 price inside target_window
same-hour realized price for target timestamp unless known at origin
future production
future consumption/load
future export/import
future actual A09/A11 flow/exchange
A61 capacity/utilization/margin
future weather actuals as price features unless explicitly labeled and justified as LABB proxy
continental actual prices at target timestamp
live API data
```

Avoid physical flow/A61 features entirely in this package.

## Leakage restrictions

For every forecast row and candidate model:

```text
input_data_cutoff_utc <= forecast_origin_timestamp_utc
forecast_origin_timestamp_utc <= target_timestamp_utc
all lag/rolling/history source timestamps < forecast_origin_timestamp_utc
all model fitting rows used for a prediction are within train_fit and before any selected holdout evaluation
holdout is not used for selection or fitting
no target-window actual price is used as input
```

If a direct multi-horizon model is used, prove that horizon-specific targets are shifted correctly and no target-window values enter features.

## Origin cadence and coverage

Use the same or compatible origin cadence as P0054K/P0054H where practical.

Required coverage:

```text
train_fit origins/rows sufficient for model fitting
holdout origins/rows sufficient for direct and 168h path evaluation
```

Prefer complete 168h paths for all reported path metrics.

If candidate models cannot cover every P0054K baseline origin, compare on the intersection and document it.

## Evaluation metrics

P0054L must evaluate price forecast quality, not downstream consumption.

Required direct/path metrics:

```text
MAE
RMSE
bias
median absolute error
p90 absolute error
p95 absolute error
sMAPE
R2 where useful
MAE_full_168h
bias_full_168h
p90/p95 full path
```

Required ranking/extreme metrics:

```text
Spearman correlation
top20_168h_precision
bottom20_168h_precision
top8_day_precision
bottom8_day_precision if practical
spike detection precision/recall/F1
ramp detection precision/recall/F1
high price regime MAE
low price regime MAE
large price ramp MAE
forecast price spike MAE
```

Why ranking metrics matter:

```text
A price forecast used as a consumption feature may be more useful if it captures expensive/cheap hours, spikes and ramps, even if average MAE improves only modestly.
```

## Required comparisons

P0054L must report:

```text
1. P0054K baseline price forecast metrics on comparable holdout rows.
2. Each candidate model's holdout metrics.
3. Best model by MAE_full_168h.
4. Best model by direct holdout MAE.
5. Best model by top/bottom ranking metrics.
6. Best model by spike/ramp metrics.
7. Whether any candidate beats P0054K baseline by >= 2% MAE_full_168h or direct MAE.
8. Whether any candidate improves ranking/spike/ramp metrics materially even if MAE gain is smaller.
9. Recommended downstream forecast source for P0054M.
```

Learning threshold:

```text
An advanced price forecast is useful if it improves direct holdout MAE or MAE_full_168h by >= 2%, or materially improves ranking/spike/ramp metrics without worsening broad MAE by more than 1%.
```

This is a LABB learning threshold, not a production gate.

## Required evidence files

Create:

```text
requirements/package-runs/P0054L/CHANGELOG.md
requirements/package-runs/P0054L/review.md
requirements/package-runs/P0054L/design.md
requirements/package-runs/P0054L/functions.md
requirements/package-runs/P0054L/labb-label.md
requirements/package-runs/P0054L/split-policy-applied.md
requirements/package-runs/P0054L/source-discovery.md
requirements/package-runs/P0054L/price-target-contract.md
requirements/package-runs/P0054L/feature-groups.md
requirements/package-runs/P0054L/input-classification.md
requirements/package-runs/P0054L/model-training-evidence.md
requirements/package-runs/P0054L/baseline-p0054k-results.md
requirements/package-runs/P0054L/hgb-results.md
requirements/package-runs/P0054L/extratrees-results.md
requirements/package-runs/P0054L/lightgbm-results.md
requirements/package-runs/P0054L/xgboost-results.md
requirements/package-runs/P0054L/ensemble-results.md
requirements/package-runs/P0054L/model-comparison.md
requirements/package-runs/P0054L/direct-horizon-results.md
requirements/package-runs/P0054L/weekly-168h-path-results.md
requirements/package-runs/P0054L/ranking-spike-ramp-results.md
requirements/package-runs/P0054L/forecast-log-schema.md
requirements/package-runs/P0054L/forecast-log-coverage.md
requirements/package-runs/P0054L/leakage-review.md
requirements/package-runs/P0054L/downstream-contract-for-p0054m.md
requirements/package-runs/P0054L/interpretation.md
requirements/package-runs/P0054L/what-we-learned.md
requirements/package-runs/P0054L/next-package-recommendation.md
```

Optional compact evidence:

```text
metrics-summary.json
ranking-spike-ramp-summary.json
forecast-log-summary.json
coverage-by-origin.csv
feature-importance.csv
```

Do not commit large raw datasets, model binaries, virtualenvs, wheels or caches.

## Files to inspect

```text
requirements/package-runs/P0054K/CHANGELOG.md
requirements/package-runs/P0054K/se3-price-forecast-source-contract.md
requirements/package-runs/P0054K/se3-price-forecast-log-schema.md
requirements/package-runs/P0054K/se3-price-forecast-coverage.md
requirements/package-runs/P0054K/se3-price-forecast-leakage-review.md
requirements/package-runs/P0054K/model-comparison.md
requirements/package-runs/P0054K/price-forecast-ablation.md
requirements/package-runs/P0054K/se3-vs-se1-price-effect-comparison.md
requirements/package-runs/P0054J/price-forecast-ablation.md
requirements/package-runs/P0054E/import-validation.md
memory/energy-market-ai-lab.md
memory/spotprice-forecast-period-policy.md
docs/functions/mac/spotprice-model-diagnostics.md
local SQLite table metadata for SE3 price forecast/history tables
relevant local source files for P0054H/P0054K price forecast generation
relevant local source files for P0054J/P0054K modeling experiments
```

Do not read large raw data files during bootstrap unless required by package verification/modeling commands.

## Files allowed to change

```text
requirements/packages/P0054L-labb-se3-advanced-spotprice-forecast.md
requirements/package-runs/P0054L/**
docs/functions/mac/spotprice-model-diagnostics.md if durable docs need updating
src/mac/** relevant existing LABB price forecast scripts if changes are needed
tests/mac/** relevant tests for changed price forecast code
```

## Forbidden changes

```text
No Shelly changes.
No Home Assistant changes.
No device/API/runtime writes.
No production deployment.
No G2-KANDIDAT promotion.
No downstream SE3 consumption model rerun in this package.
No actual future spot price leakage.
No P0053C-B validation/holdout-only M4 forecast as train feature.
No production/export/import/A61/future-flow features.
No live API calls.
No large raw dataset commits.
No model binary commits.
No virtualenv/wheel/cache commits.
No broad refactor unrelated to P0054L.
```

## Live/API/device policy

Live testing allowed: no.

Device/API/runtime actions allowed: no.

No external live market API calls are allowed. Use only existing local/repository-documented data.

## Verification commands

Codex must define final commands in `design.md`, but must run equivalent checks for:

```text
P0054I/P0054J/P0054K train_fit/holdout split applied
SE3 price target source contract verified
P0054K baseline forecast available for comparison
candidate model feature matrices contain only forecast-origin-safe columns
feature matrix contains no actual future price/production/flow/A61 columns
all lag/rolling/history timestamps strictly before origin
LightGBM/XGBoost import status OK or documented
weekly 168h paths are complete or skipped with reason
forecast log schema and coverage verified
leakage review passes
no downstream consumption model outputs are created
git diff --check
no large data/model/env artifacts are staged
```

## Pass / WARN / STOP interpretation

PASS requires:

```text
- SE3 price target source is found and validated.
- P0054K baseline is evaluated on comparable holdout rows.
- HGB, ExtraTrees, LightGBM and XGBoost price models are evaluated or explicitly blocked with evidence.
- Best advanced forecast model is identified.
- Forecast log/source suitable for P0054M is created or clearly identified.
- Leakage review passes.
```

WARN is acceptable if:

```text
- one model family fails but enough advanced candidates run.
- ensemble is skipped because single models dominate.
- advanced models improve ranking/spike/ramp metrics but not broad MAE.
- forecast log is evidence-only and not persisted because no candidate beats baseline, but downstream recommendation is clear.
```

STOP if:

```text
- no reliable local SE3 price target exists.
- safe forecast-origin features cannot be built.
- actual future price leaks into features.
- forbidden production/flow/A61/future features enter the matrix.
- holdout is used for fitting or model selection.
- device/API/runtime work is created.
```

## Expected Codex output

```text
PASS/WARN/STOP status
SE3 price target/source summary
split policy summary
models run
best price model by direct MAE
best price model by weekly MAE_full_168h
best ranking/spike/ramp model
comparison to P0054K baseline
whether improved forecast source should be used by P0054M
forecast log/table/view name if created
leakage review result
what we learned
next package recommendation
tests/commands run
files changed
confirmation of no actual future price/API/device/A61/leakage work
confirmation no downstream consumption ablation was run
confirmation no large artifacts committed
commit SHA after push
```

## Completion notes

To be filled after implementation.
