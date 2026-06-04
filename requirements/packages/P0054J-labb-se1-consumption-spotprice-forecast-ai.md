# Package P0054J: LABB SE1 consumption AI with spot price forecast

## Status

done

## Package order

P0054J

## Label

```text
LABB
```

This package is research/lab work under P0054A. It is not a G2-KANDIDAT evaluation.

## Purpose

Train and evaluate several SE1 consumption forecast models with and without a forecast-safe SE1 spot price forecast feature, using the operator-approved train/holdout policy:

```text
train_fit:  2022-06-01T00:00:00Z .. 2025-05-31T23:00:00Z
holdout:    2025-06-01T00:00:00Z .. latest_available_timestamp_utc
```

All final model comparisons must be scored on June 2025 and forward only.

The main question is whether advanced consumption AI benefits from a forecast-safe spot price forecast input, or whether the price forecast adds noise and worsens SE1 consumption prediction.

## Operator decision

For this experiment line:

```text
M1, M4 and the new consumption forecasters are trained on data from June 2022 through May 2025.
After that, everything is holdout.
All models are tested from June 2025 onward.
```

This package trains the new SE1 consumption forecasters under that policy.

## Core questions

P0054J must answer:

```text
1. What is the best SE1 consumption model without spot price forecast features?
2. What is the best SE1 consumption model with forecast-safe SE1 spot price forecast features?
3. Does adding P0054H spot price forecast improve or worsen each model family?
4. Do advanced models such as LightGBM/XGBoost benefit more from price forecast than HGB/ExtraTrees/MLP?
5. Should price forecast features be kept for later SE1 consumption/spread/flaskhals experiments?
```

## Required split policy

Use the P0054I operator-approved unified holdout policy regardless of older P0053C/P0054F wording:

```text
train_fit: target_timestamp_utc >= 2022-06-01T00:00:00Z
           and target_timestamp_utc < 2025-06-01T00:00:00Z

holdout:   target_timestamp_utc >= 2025-06-01T00:00:00Z
```

No holdout row may be used for fitting, early stopping, hyperparameter selection, feature selection or model-family selection.

If a model needs early stopping or bounded tuning, create an internal split strictly inside `train_fit` only, for example late-train internal validation. That internal split must be documented and must not be used as the final holdout.

## Target

Primary target:

```text
consumption_se1_mw
```

Use the canonical physical-balance source used by the P0054 LABB chain unless repository truth has a documented successor:

```text
physical_balance_se1_se4_hourly_v1
```

Codex must document exact source table/file, target column, unit, coverage, missingness and timestamp semantics.

Unit:

```text
MW hourly mean
```

## Price forecast feature source

Use the P0054H forecast-safe SE1 spot price forecast log:

```text
anchored_absolute_price_forecast_log_p0054h_se1_v1
```

Required filters:

```text
area = SE1
prediction_kind = anchored_absolute_price
quality_flag = forecast_safe_origin_local_baseline_not_m4
training_protocol = origin_local_no_fit_pre_origin_history
```

Join keys:

```text
forecast_origin_timestamp_utc
target_timestamp_utc
```

Primary feature:

```text
predicted_price
```

Important label:

```text
This is not M4. It is a forecast-safe origin-local historical spot price baseline.
```

Do not call this input M4. Do not use actual future spot price.

## Weather proxy

Use best existing SE1 weather proxy, likely:

```text
se1_core_weather
```

Weather remains LABB actual-as-forecast proxy unless a separate forecast weather source is documented:

```text
weather_actual_as_forecast_proxy
```

## Feature variants

### Variant A: no_price

Allowed feature groups:

```text
calendar/time known in advance
historical SE1 consumption lags and rollups strictly before forecast origin
SE1 weather proxy fields
```

### Variant B: with_p0054h_price_forecast

Variant A plus forecast-safe P0054H price forecast features.

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

If additional features are implemented, prove they are derived only from the forecast path rows available at `forecast_origin_timestamp_utc`.

## Forbidden inputs

The model feature matrix must not contain:

```text
actual future spot price
same-hour realized spot price for target timestamp unless it is known at forecast origin
M4/P0053C-B validation/holdout-only forecast as a train feature
production
future production
export/import
future actual A09/A11 flow/exchange
A61 capacity/utilization/margin
continental actual prices
target-window actual consumption beyond forecast origin
```

Historical SE1 consumption lags and rollups are allowed only when strictly before the forecast origin.

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
HGB_with_p0054h_price_forecast
ExtraTrees_no_price
ExtraTrees_with_p0054h_price_forecast
LightGBM_no_price
LightGBM_with_p0054h_price_forecast
XGBoost_no_price
XGBoost_with_p0054h_price_forecast
```

MLP is optional if runtime is high or existing pipeline does not support it cleanly, but the skip must be documented.

For every model family, use identical rows for the paired no-price vs with-price comparison.

## Hyperparameter policy

Use sensible bounded hyperparameters based on the previous P0054D/P0054E SE4 experiments.

Do not perform broad hyperparameter search unless it is strictly inside `train_fit` and bounded. Holdout must never influence hyperparameters.

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

P0054J must report:

```text
1. Best no-price model by holdout MAE.
2. Best with-price-forecast model by holdout MAE.
3. Best no-price model by weekly MAE_full_168h.
4. Best with-price-forecast model by weekly MAE_full_168h.
5. Per-model delta from adding price forecast:
   with_price - no_price
6. Whether price forecast improves or worsens each model.
7. Whether advanced models benefit more from price forecast than HGB/ExtraTrees.
8. Conditional regimes where price forecast helps or hurts.
9. Whether price forecast should be kept for future SE1 experiments.
```

Negative MAE delta means the spot price forecast helped.

Learning threshold:

```text
Price forecast is useful if it improves holdout MAE or weekly MAE_full_168h by >= 2%, or improves >= 3% in at least two important price/temperature/load regimes without materially worsening broad holdout metrics.
```

This is LABB learning threshold, not production gate.

## Required evidence files

Create:

```text
requirements/package-runs/P0054J/CHANGELOG.md
requirements/package-runs/P0054J/review.md
requirements/package-runs/P0054J/design.md
requirements/package-runs/P0054J/functions.md
requirements/package-runs/P0054J/labb-label.md
requirements/package-runs/P0054J/split-policy-applied.md
requirements/package-runs/P0054J/dataset-contract.md
requirements/package-runs/P0054J/price-forecast-source-contract.md
requirements/package-runs/P0054J/input-classification.md
requirements/package-runs/P0054J/feature-groups.md
requirements/package-runs/P0054J/model-training-evidence.md
requirements/package-runs/P0054J/no-price-results.md
requirements/package-runs/P0054J/with-price-forecast-results.md
requirements/package-runs/P0054J/price-forecast-ablation.md
requirements/package-runs/P0054J/model-comparison.md
requirements/package-runs/P0054J/direct-horizon-results.md
requirements/package-runs/P0054J/weekly-168h-path-results.md
requirements/package-runs/P0054J/conditional-regime-results.md
requirements/package-runs/P0054J/feature-importance-or-attribution.md
requirements/package-runs/P0054J/interpretation.md
requirements/package-runs/P0054J/what-we-learned.md
requirements/package-runs/P0054J/next-package-recommendation.md
```

Optional compact evidence:

```text
metrics-summary.json
price-ablation-summary.json
weekly-path-metrics.csv
conditional-metrics.csv
modeling-dataset-sample.csv
training-history.csv
```

Do not commit large raw datasets, model binaries, virtualenvs, wheels or caches.

## Files to inspect

```text
requirements/packages/P0054I-labb-unified-holdout-train-through-may-2025.md
requirements/package-runs/P0054H/CHANGELOG.md
requirements/package-runs/P0054H/coverage-by-split.md
requirements/package-runs/P0054H/leakage-review.md
requirements/package-runs/P0054H/downstream-contract-for-p0054f-retry.md
requirements/package-runs/P0054H/validation-holdout-comparison-to-p0053cb.md
requirements/package-runs/P0054E/import-validation.md
requirements/package-runs/P0054E/lightgbm-results.md
requirements/package-runs/P0054E/xgboost-results.md
memory/energy-market-ai-lab.md
memory/spotprice-forecast-period-policy.md
docs/functions/mac/weather-history-dataset.md
docs/functions/mac/spotprice-model-diagnostics.md
relevant local source files for P0054D/P0054E modeling experiments
local SQLite table metadata for P0054H price forecast log
```

Do not read large raw data files during bootstrap unless required by package verification/modeling commands.

## Files allowed to change

```text
requirements/packages/P0054J-labb-se1-consumption-spotprice-forecast-ai.md
requirements/package-runs/P0054J/**
docs/functions/mac/spotprice-model-diagnostics.md if durable docs need updating
src/mac/** relevant existing LABB modeling scripts if changes are needed
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
No broad refactor unrelated to P0054J.
```

## Live/API/device policy

Live testing allowed: no.

Device/API/runtime actions allowed: no.

No external live market API calls are allowed for model features. Price forecast input must come from P0054H local forecast-safe log.

## Verification commands

Codex must define final commands in `design.md`, but must run equivalent checks for:

```text
P0054I train_fit/holdout split is applied
P0054H price forecast source contract verified
P0054H price rows cover train_fit and holdout
no-price and with-price matrices use identical target rows per model
with-price matrix contains only forecast-safe price forecast columns
feature matrix contains no actual future price/production/flow/A61 columns
LightGBM/XGBoost import status OK or documented
weekly 168h paths are complete or skipped with reason
no large data/model/env artifacts are staged
git diff --check
```

## Pass / WARN / STOP interpretation

PASS requires:

```text
- SE1 no-price and with-price experiments run under train-through-May-2025 policy.
- HGB, ExtraTrees, LightGBM and XGBoost are evaluated in paired no-price/with-price form.
- Price forecast ablation is reported on identical rows.
- Best model and price-feature effect are clear.
- No leakage or runtime/device actions occurred.
```

WARN is acceptable if:

```text
- MLP is skipped for runtime or pipeline constraints.
- one boosted model fails but the other runs with evidence.
- price forecast does not help, but the negative result is clean.
- P0054H price source remains a weaker baseline than P0053C-B but is clearly labeled and forecast-safe.
```

STOP if:

```text
- P0054H price source cannot join cleanly to train_fit and holdout rows.
- actual future spot price leaks into features.
- forbidden production/flow/A61/future features enter the matrix.
- holdout is used for fitting or model selection.
- device/API/runtime work is created.
```

## Expected Codex output

```text
PASS/WARN/STOP status
split policy summary
SE1 price forecast source contract
SE1 target/data coverage
input classification summary
models run
best no-price model
best with-price model
per-model price forecast MAE deltas
weekly 168h path deltas
conditional/regime findings
whether advanced AI benefits from price forecast
whether price forecast should be kept
what we learned
next package recommendation
tests/commands run
files changed
confirmation of no actual future price/API/device/A61/leakage work
confirmation no large artifacts committed
commit SHA after push
```

## Completion notes

P0054J completed with PASS.

Summary:

```text
label: LABB, not G2-KANDIDAT
target: physical_balance_se1_se4_hourly_v1.consumption_se1, MW hourly mean
split: train_fit target_timestamp_utc 2022-06-01T00:00:00Z..<2025-06-01T00:00:00Z; holdout >=2025-06-01T00:00:00Z
direct rows: 15730
weekly 168h path rows: 8568
weekly complete origins: 51
price source rows: 240912
```

Price forecast source:

```text
anchored_absolute_price_forecast_log_p0054h_se1_v1
area=SE1
prediction_kind=anchored_absolute_price
quality_flag=forecast_safe_origin_local_baseline_not_m4
training_protocol=origin_local_no_fit_pre_origin_history
```

This input was kept clearly labeled as a P0054H origin-local forecast-safe baseline, not M4.

Models run:

```text
HGB no_price / with_p0054h_price_forecast
ExtraTrees no_price / with_p0054h_price_forecast
LightGBM no_price / with_p0054h_price_forecast
XGBoost no_price / with_p0054h_price_forecast
```

MLP was intentionally skipped because it was optional and the required tree/boosted family set was complete.

Best models:

```text
best holdout no_price: XGBoost_no_price, MAE 12.60041062463637
best holdout with_price: XGBoost_with_p0054h_price_forecast, MAE 12.585281377945856
best weekly no_price: XGBoost_no_price, MAE_full_168h 13.831126605961474
best weekly with_price: XGBoost_with_p0054h_price_forecast, MAE_full_168h 13.650342019254719
```

Price forecast ablation:

```text
HGB: holdout worsened 0.8927455419055711%, weekly improved 2.224575014299145%
ExtraTrees: holdout worsened 0.09963703752656679%, weekly improved 0.4845746426637863%
LightGBM: holdout improved 1.029787203889473%, weekly improved 0.8106449555549822%
XGBoost: holdout improved 0.12006947345773429%, weekly improved 1.3070850398320675%
```

Interpretation:

```text
status: supports_hypothesis
decision: keep P0054H price forecast features for future SE1 LABB experiments
reason: weekly-path metrics improved for all four required families, LightGBM/XGBoost improved direct holdout, and conditional regimes showed >=3% improvements in multiple important cold/peak/price/load regimes.
```

Safety and leakage result:

```text
P0054I split applied.
P0054H source contract verified.
No-price and with-price matrices used identical target rows per family.
With-price features used only forecast-origin-safe P0054H price forecast columns.
Feature matrix contained no actual future spot price, production, flow/export/import, A61, utilization, continental price, device, API or runtime feature.
No live API, device, Shelly, Home Assistant, KVS, A61 utilization or production-runtime action was performed.
No model binaries, virtualenvs, wheels, caches or large raw datasets were committed.
```

Verification commands run:

```text
python3 -m unittest tests.mac.services.spotprice_model_diagnostics.test_p0054j
python3 -m src.mac.services.spotprice_model_diagnostics.p0054j
git diff --check
```
