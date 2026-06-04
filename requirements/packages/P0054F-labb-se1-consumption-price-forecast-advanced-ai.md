# Package P0054F: LABB SE1 consumption with SE1 price forecast advanced AI

## Status

stopped

## Package order

P0054F

## Label

```text
LABB
```

This package is research/lab work under P0054A. It is not a G2-KANDIDAT evaluation.

## Purpose

Test whether the more advanced model families from P0054E benefit from adding our SE1 price forecast as a forecast-safe input when predicting SE1 consumption.

This is a controlled SE1 ablation:

```text
SE1 consumption without price forecast
vs
SE1 consumption with our SE1 price forecast
```

The package must answer whether price forecast features help, hurt or have no material effect, especially for more advanced AI models such as LightGBM and XGBoost.

## Decision summary

Use the current SE1 consumption forecast setup and compare model families under two otherwise identical feature matrices:

```text
A. no_price:
   calendar + historical SE1 load lags/rollups + SE1 weather proxy

B. with_price_forecast:
   calendar + historical SE1 load lags/rollups + SE1 weather proxy + our SE1 price forecast features
```

This package is not allowed to use actual future spot price. It may only use a forecast that would have been available at the forecast origin, or a repository-documented anchored price forecast artifact built under the global period policy.

## Core questions

P0054F must answer:

```text
1. Does adding our SE1 price forecast improve SE1 consumption prediction?
2. Does price forecast help advanced models more than HGB/ExtraTrees?
3. Does price forecast hurt any model by adding noise or unstable interactions?
4. Which model is best for SE1 consumption with no price input?
5. Which model is best for SE1 consumption with price forecast input?
6. Is the improvement large enough to justify keeping price forecast in future SE1 consumption/spread/flaskhals experiments?
```

## Required comparison model

For each model, run both feature variants on identical target rows:

```text
model_X_no_price
model_X_with_se1_price_forecast
```

The main result is the paired delta:

```text
price_forecast_delta = with_price_forecast - no_price
```

Negative MAE delta means the price forecast helped.

## Target

Primary target:

```text
consumption_se1_mw
```

Use the canonical physical-balance source used by P0053/P0054 packages unless repository truth has a documented successor:

```text
physical_balance_se1_se4_hourly_v1
```

Expected source column may be named one of:

```text
consumption_se1
consumption_se1_mw
```

Codex must document the exact source table, target column, unit, coverage, missingness and timestamp semantics.

Unit:

```text
MW hourly mean
```

## Period and split

Use P0053C global policy:

```text
train:      2022-06-01T00:00:00Z .. 2024-12-31T23:00:00Z
validation: 2025-01-01T00:00:00Z .. 2025-05-31T23:00:00Z
holdout:    2025-06-01T00:00:00Z .. latest_available_timestamp_utc
```

No target rows before 2022-06-01.

Context-only lag warmup before 2022-06-01 is allowed only if target rows start at or after 2022-06-01 and warmup rows are not scored/trained as targets.

## Forecast-safe price input requirements

Use only our SE1 price forecast, not actual future price.

Codex must identify and document the exact price forecast source before modeling:

```text
source table/file/view
forecast generation package or evidence path
forecast target area = SE1
forecast horizon coverage
forecast origin semantics
forecast timestamp semantics
whether it is anchored at the forecast origin
```

Acceptable price forecast inputs include repository-documented M4 anchored price forecast features or a successor forecast table that is clearly forecast-origin safe.

Forbidden price inputs:

```text
actual future spot price
same-hour realized spot price for the forecast target timestamp unless it is known at forecast origin
ex-post corrected price data presented as forecast
unanchored price history shifted into the future
any price column whose forecast origin cannot be verified
```

If Codex cannot identify a forecast-safe SE1 price forecast source, it must STOP before modeling with price features. It may still report a no-price SE1 baseline only if useful, but the package is not complete without an honest STOP/WARN decision.

## Weather proxy

Use the best repository-documented SE1 weather proxy from the existing weather-history work.

Likely candidate:

```text
se1_core_weather
```

If P0033 climate weighting or a later SE1 weather proxy is better documented for SE1 consumption, Codex may use it, but must document why.

Weather remains LABB proxy weather unless a separate forecast source is used:

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

### Variant B: with_se1_price_forecast

Variant A plus forecast-safe SE1 price forecast features.

Potential price forecast feature examples:

```text
forecast_price_se1_target_horizon
forecast_price_se1_lagged_origin_features
forecast_price_se1_rolling_future_window_mean_0_24h if computed only from forecast path available at origin
forecast_price_se1_peak/offpeak indicators from forecast path
forecast_price_se1_rank/percentile within forecast path
forecast_price_se1_spike_flag from forecast path
```

Do not include realized future spot price.

## Forbidden non-price inputs

The model feature matrix must not contain:

```text
production
future production
export/import
future actual A09/A11 flow/exchange
A61 capacity/utilization/margin
continental actual prices
target-window actuals beyond forecast origin
```

Historical SE1 consumption lags and rollups are allowed only when strictly before the forecast origin.

## Required models

Run the same model families as P0054E where available:

```text
HGB
MLP
ExtraTrees
LightGBM
XGBoost
```

At minimum, if runtime is constrained:

```text
HGB_no_price
HGB_with_se1_price_forecast
ExtraTrees_no_price
ExtraTrees_with_se1_price_forecast
LightGBM_no_price
LightGBM_with_se1_price_forecast
XGBoost_no_price
XGBoost_with_se1_price_forecast
```

MLP may be included if the existing P0054D/P0054E runner supports it without excessive runtime.

If LightGBM/XGBoost imports fail despite P0054E, Codex must document the environment problem and either repair within P0054E/P0054F scope or WARN/STOP according to severity.

## Fairness rules

All with-vs-without-price comparisons for a given model must use identical rows.

The winner across models must be identified only on a shared comparable row set or clearly labeled if evidence-summary comparison is used.

Do not use holdout for model selection. Validation may be used for bounded hyperparameter/early-stopping choices.

## Evaluation

Direct horizons:

```text
1h, 3h, 6h, 12h, 24h, 48h, 72h, 96h, 120h, 144h, 168h
```

Weekly 168h path evaluation on holdout:

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

P0054F must report:

```text
1. Best no-price model by direct holdout MAE.
2. Best with-price-forecast model by direct holdout MAE.
3. Best no-price model by weekly MAE_full_168h.
4. Best with-price-forecast model by weekly MAE_full_168h.
5. For each model, direct holdout MAE delta from adding price forecast.
6. For each model, weekly 168h MAE delta from adding price forecast.
7. Conditional regimes where price forecast helps or hurts.
8. Whether advanced AI benefits more from price forecast than HGB/ExtraTrees.
9. Whether price forecast should be kept for future SE1 consumption/spread/flaskhals experiments.
```

Learning threshold:

```text
Price forecast is useful if it improves holdout MAE or weekly MAE_full_168h by >= 2%, or improves >= 3% in at least two important price/temperature/load regimes without materially worsening broad holdout metrics.
```

This is a LABB learning threshold, not a production gate.

## Required evidence files

Create:

```text
requirements/package-runs/P0054F/CHANGELOG.md
requirements/package-runs/P0054F/review.md
requirements/package-runs/P0054F/design.md
requirements/package-runs/P0054F/functions.md
requirements/package-runs/P0054F/labb-label.md
requirements/package-runs/P0054F/price-forecast-source-contract.md
requirements/package-runs/P0054F/dataset-contract.md
requirements/package-runs/P0054F/input-classification.md
requirements/package-runs/P0054F/feature-groups.md
requirements/package-runs/P0054F/model-training-evidence.md
requirements/package-runs/P0054F/no-price-results.md
requirements/package-runs/P0054F/with-price-forecast-results.md
requirements/package-runs/P0054F/price-forecast-ablation.md
requirements/package-runs/P0054F/model-comparison.md
requirements/package-runs/P0054F/direct-horizon-results.md
requirements/package-runs/P0054F/weekly-168h-path-results.md
requirements/package-runs/P0054F/conditional-regime-results.md
requirements/package-runs/P0054F/feature-importance-or-attribution.md
requirements/package-runs/P0054F/interpretation.md
requirements/package-runs/P0054F/what-we-learned.md
requirements/package-runs/P0054F/next-package-recommendation.md
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
memory/energy-market-ai-lab.md
memory/energy-market-simulator-ambition.md
memory/spotprice-forecast-period-policy.md
docs/functions/mac/weather-history-dataset.md
docs/functions/mac/spotprice-model-diagnostics.md
requirements/packages/P0054E-labb-se4-lightgbm-xgboost-install-and-test.md
requirements/package-runs/P0054E/CHANGELOG.md
requirements/package-runs/P0054E/import-validation.md
requirements/package-runs/P0054E/model-comparison.md
requirements/package-runs/P0054E/lightgbm-results.md
requirements/package-runs/P0054E/xgboost-results.md
requirements/packages/P0053C-B-M4-48h-anchored-absolute-price-forecast-log.md or nearest matching P0053 price forecast package
requirements/package-runs/P0053C*/** relevant price forecast evidence
relevant local source files for P0054E modeling experiment
relevant local source/table/view for SE1 price forecast features
```

Do not read large raw data files during bootstrap unless required by package verification commands.

## Files allowed to change

```text
requirements/packages/P0054F-labb-se1-consumption-price-forecast-advanced-ai.md
requirements/package-runs/P0054F/**
docs/functions/mac/spotprice-model-diagnostics.md if durable function/lab docs need updating
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
No production/export/import/A61/future-flow features.
No large raw dataset commits.
No model binary commits.
No virtualenv/wheel/cache commits.
No broad refactor unrelated to P0054F.
```

## Live/API/device policy

Live testing allowed: no.

Device/API/runtime actions allowed: no.

No external live market API calls are allowed for model features. Price forecast input must come from existing local/repository-documented forecast artifacts or local generated forecast logs produced under prior packages. If a required forecast artifact is missing, stop or WARN with evidence rather than calling a live API.

## Verification commands

Codex must define final commands in `design.md`, but must run equivalent checks for:

```text
SE1 price forecast source contract verified
SE1 weather proxy exists and covers modeled period
target/split validation follows P0053C
no-price and with-price feature matrices use identical target rows per model
with-price feature matrix contains only forecast-safe price columns
feature matrix contains no forbidden actual future price/production/flow/A61 columns
LightGBM/XGBoost import status is still OK from P0054E environment
weekly 168h paths are complete or skipped with reason
no large data/model/env artifacts are staged
git diff --check
```

## Pass / WARN / STOP interpretation

PASS requires:

```text
- forecast-safe SE1 price forecast source identified and documented.
- no-price and with-price SE1 experiments run for key advanced models.
- LightGBM and XGBoost are included unless blocked with explicit evidence.
- price forecast ablation is reported with identical rows.
- clear answer on whether price forecast helps advanced AI.
- no forbidden feature leakage or runtime/device actions occurred.
```

WARN is acceptable if:

```text
- price forecast source is forecast-safe but coverage is shorter than desired and rows are reduced with documentation.
- MLP is skipped for runtime but HGB/ExtraTrees/LightGBM/XGBoost are run.
- one boosted model fails but the other runs and evidence is clear.
- price forecast does not help but the negative result is clean.
```

STOP if:

```text
- forecast-safe SE1 price forecast source cannot be identified.
- actual future spot price leaks into features.
- forbidden production/flow/A61/future features enter the model matrix.
- holdout is used for model selection.
- device/API/runtime work is created.
```

## Expected Codex output

```text
PASS/WARN/STOP status
SE1 price forecast source contract
SE1 target/data coverage
input classification summary
models run
best no-price model
best with-price-forecast model
per-model price forecast MAE deltas
weekly 168h path deltas
conditional/regime findings
whether advanced AI benefits from price forecast
what we learned
next package recommendation
tests/commands run
files changed
confirmation of no actual future price/API/device/A61/leakage work
confirmation no large artifacts committed
commit SHA after push
```

## Completion notes

Stopped during package consistency/source-contract review.

Result:

```text
STOP
```

Reason:

```text
P0053C-B provides a forecast-origin-safe anchored absolute SE1 price forecast log, but the log covers validation and holdout only. It has zero train-period rows/origins.
```

Verified candidate source:

```text
source table: m4_48h_anchored_absolute_price_forecast_log_p0053cb_v1
area: SE1
prediction_kind: anchored_absolute_price
prediction_unit: source_hour_price_unit
rows: 82656
distinct forecast origins: 492
```

Coverage by target timestamp:

```text
train:      0 rows, 0 origins
validation: 24192 rows, 144 origins
holdout:    58464 rows, 348 origins
```

Coverage by forecast origin:

```text
train:      0 rows, 0 origins
validation: 24192 rows, 144 origins
holdout:    58464 rows, 348 origins
```

The package requires paired no-price vs with-price training under the P0053C split. Training a with-price model without train-period price forecast rows would require either using validation as training, using actual future spot price, or creating a new train-period price forecast log. Those options are outside P0054F or violate leakage/split rules.

No models were trained. No modeling dataset, price feature group, runtime, device, Shelly, Home Assistant, KVS, deploy, API call, production/export/import/flow/A61 feature or future price leakage was created.

Recommended next package:

```text
P0054G LABB train-period M4 anchored SE1 price forecast-origin log
```
