# Package P0054N: LABB SE3 consumption full 36h DayAhead evaluation

## Status

planned

## Package order

P0054N

## Label

```text
LABB
```

This package is research/lab work under P0054A. It is not a G2-KANDIDAT evaluation.

## Purpose

Evaluate the SE3 consumption forecast motor on a shorter `full_36h` horizon instead of the existing weekly/full_168h horizon, with explicit DayAhead and intraday relevance.

The operator hypothesis is:

```text
If we can build an exceptionally good 36h SE3 consumption forecast motor, it may become a method candidate for DayAhead and intraday trading workflows at work.
```

P0054M showed that advanced SE3 spot-price forecast features improved SE3 consumption forecasting, including XGBoost in price-sensitive regimes. However, the main path metric was `full_168h`, which is much longer than the practical DayAhead/intraday use case. P0054N must focus on `full_36h`.

## Business/use-case context

For DayAhead bidding:

```text
Around 12:00 the day before delivery, produce a consumption forecast for the next delivery day.
Submit the bid to Nord Pool before 13:00.
The forecast for the delivery day becomes the volume basis for the DayAhead bid.
```

This package must model that timing explicitly as a LABB evaluation, without doing any live market, workplace, Nord Pool, API or production integration.

## Important scope boundary

This is still LABB diagnostics/modeling only.

Allowed:

```text
local model training/evaluation
local SQLite reads/writes
package-run evidence
small local source/test changes for evaluation logic
```

Forbidden:

```text
actual Nord Pool submission
live market API calls
workplace system integration
production deployment
device/Shelly/Home Assistant/runtime work
G2-KANDIDAT promotion
actual future spot price leakage
production/export/import/A61/future-flow features
large raw data/model binary/venv/cache commits
```

## Core questions

P0054N must answer:

```text
1. How accurate is the best SE3 consumption forecast over full_36h?
2. Does the P0054L2/P0054M advanced spot-price feature improve full_36h accuracy?
3. Which model is best for full_36h: ExtraTrees, XGBoost, LightGBM or HGB?
4. Is the 36h result materially better than full_168h and good enough to consider a future method-candidate track?
5. How accurate is the DayAhead-specific delivery-day forecast when generated at 12:00 the day before delivery?
6. Which errors matter most for bidding: total daily energy error, hourly MAE, peak/offpeak bias, morning/evening ramp error?
```

## Required split policy

Use the P0054I/P0054J/P0054K/P0054M policy:

```text
train_fit: target_timestamp_utc >= 2022-06-01T00:00:00Z
           and target_timestamp_utc < 2025-06-01T00:00:00Z

holdout:   target_timestamp_utc >= 2025-06-01T00:00:00Z
```

No holdout row may be used for model fitting, early stopping, hyperparameter selection, feature selection or model-family selection.

Any internal validation must be carved strictly inside `train_fit`.

## Target

Primary target:

```text
consumption_se3_mw
```

Use the same SE3 consumption target source as P0054M/P0054K unless repository truth has a documented successor.

Unit:

```text
MW hourly mean
```

STOP if no reliable local SE3 consumption target exists.

## Forecast-feature protocol

Use the same safe advanced price protocol as P0054M unless a documented successor exists:

```text
price_feature_protocol = rolling_oof_train_plus_holdout
train-side table = advanced_spotprice_forecast_log_p0054m_se3_train_blocked_oof_v1
holdout-side table = advanced_spotprice_forecast_log_p0054l2_se3_v1
recommended holdout model = Ensemble
```

Codex must verify that the advanced price feature is used safely and that P0054L2 holdout-only rows are not used as train_fit features.

If P0054M's train-side advanced price coverage is insufficient for the full train_fit rows used by P0054N, Codex may:

```text
1. restrict with-price training to the safely covered train rows and compare on identical rows, clearly labeled, or
2. generate additional rolling/blocked OOF price rows if practical, or
3. produce no-price full_36h results and WARN/STOP the with-price branch honestly.
```

Do not silently use unsafe price features.

## Models to evaluate

Run the same SE3 consumption model families as P0054M where practical:

```text
HGB
ExtraTrees
LightGBM
XGBoost
```

Minimum required:

```text
ExtraTrees_no_price
ExtraTrees_with_advanced_price if safe
XGBoost_no_price
XGBoost_with_advanced_price if safe
```

HGB and LightGBM are strongly preferred for comparison, but P0054N may WARN if runtime blocks a family and the key 36h answers are available.

## Main evaluation: full_36h

Define `full_36h` as a complete 36-hour forecast path from a forecast origin:

```text
forecast_origin_timestamp_utc = origin
target_window = [origin, origin + 35h]
horizon_hour = 0..35
```

If the repository convention starts horizon at 1h rather than 0h, Codex must document the convention and keep the 36 target hours explicit.

Report full_36h only for origins where all 36 target hours exist and all required features are available.

Required full_36h origin cadence:

```text
At least daily holdout origins where complete 36h paths exist.
Prefer all available daily or hourly origins if runtime is practical.
```

Codex must document origin count, target row count and skipped origins.

## DayAhead-specific evaluation

Create a DayAhead evaluation slice representing forecast creation around 12:00 the day before delivery.

Preferred Swedish market-time semantics:

```text
decision_time_local = 12:00 Europe/Stockholm on day D-1
delivery_day_local = day D, hours 00:00..23:00 Europe/Stockholm
submission_deadline_context = before 13:00 Europe/Stockholm on D-1
```

Equivalent UTC timestamps must be documented, including DST handling.

For each delivery day in holdout where complete delivery-day actuals and features exist:

```text
forecast_origin = D-1 12:00 Europe/Stockholm converted to UTC
target_window = D 00:00..D 23:00 Europe/Stockholm converted to UTC
```

This is a delivery-day 24h slice inside the available ~36h path.

Required DayAhead metrics:

```text
hourly_MAE_delivery_day
hourly_RMSE_delivery_day
bias_delivery_day
absolute_daily_energy_error_MWh
signed_daily_energy_error_MWh
MAPE/sMAPE where safe
peak_hour_error_MW
peak_hour_timing_error_hours
offpeak_MAE
morning_ramp_MAE
evening_peak_MAE
weekday/weekend/holiday split
cold/high-price/spike/ramp regimes if enough samples
```

## Intraday-relevant slices

Also report shorter sub-horizons inside full_36h:

```text
MAE_0_6h
MAE_0_12h
MAE_0_24h
MAE_24_36h
MAE_full_36h
bias_full_36h
p90/p95_full_36h
```

## Baselines and comparisons

Compare P0054N results to P0054M full_168h evidence:

```text
P0054M best direct holdout MAE: ExtraTrees_with_p0054l2_ensemble_price_forecast ≈ 140.548 MW
P0054M best weekly MAE_full_168h: XGBoost_with_p0054l2_ensemble_price_forecast ≈ 206.257 MW
```

Do not overcompare if full_36h uses a different origin set. Label comparisons as indicative unless row/origin sets match.

Required comparisons:

```text
1. Best no-price model by full_36h MAE.
2. Best with-advanced-price model by full_36h MAE.
3. Best model by DayAhead delivery-day hourly MAE.
4. Best model by DayAhead daily energy error.
5. Per-model delta from advanced price feature on full_36h.
6. Per-model delta from advanced price feature on DayAhead delivery-day metrics.
7. Whether full_36h is materially better than full_168h.
8. Whether the result is promising enough for a future method-candidate package.
```

## Method-candidate threshold

This is not a production gate, but P0054N must provide a practical interpretation.

Indicative LABB threshold for future method-candidate track:

```text
Promising if full_36h MAE improves materially versus full_168h and DayAhead delivery-day hourly MAE is stable across weekdays/weekends/cold/high-price regimes.
Strongly promising if daily energy error is small enough to be operationally meaningful for bidding and no severe peak/ramp bias is observed.
```

Codex must avoid claiming production readiness. It should recommend whether a later package should evaluate against workplace/market-grade acceptance criteria.

## Input classification

Expected allowed/forbidden classes:

```text
calendar = forecast_safe
historical_se3_load_lags_rollups = forecast_safe
weather = LABB proxy unless forecast weather source is documented
advanced_price_forecast = forecast_safe only under documented P0054M protocol
actual_future_spot_price = excluded_leakage
production_flow_export_import_a61 = excluded_leakage
future_actual_load = excluded_leakage
```

## Required evidence files

Create:

```text
requirements/package-runs/P0054N/CHANGELOG.md
requirements/package-runs/P0054N/review.md
requirements/package-runs/P0054N/design.md
requirements/package-runs/P0054N/functions.md
requirements/package-runs/P0054N/labb-label.md
requirements/package-runs/P0054N/split-policy-applied.md
requirements/package-runs/P0054N/dayahead-use-case.md
requirements/package-runs/P0054N/dataset-contract.md
requirements/package-runs/P0054N/price-feature-protocol-review.md
requirements/package-runs/P0054N/input-classification.md
requirements/package-runs/P0054N/feature-groups.md
requirements/package-runs/P0054N/model-training-evidence.md
requirements/package-runs/P0054N/full-36h-results.md
requirements/package-runs/P0054N/dayahead-delivery-day-results.md
requirements/package-runs/P0054N/intraday-slice-results.md
requirements/package-runs/P0054N/advanced-price-ablation-36h.md
requirements/package-runs/P0054N/model-comparison.md
requirements/package-runs/P0054N/p0054m-comparison.md
requirements/package-runs/P0054N/conditional-regime-results.md
requirements/package-runs/P0054N/leakage-review.md
requirements/package-runs/P0054N/interpretation.md
requirements/package-runs/P0054N/what-we-learned.md
requirements/package-runs/P0054N/next-package-recommendation.md
```

Optional compact evidence:

```text
metrics-summary.json
full-36h-path-metrics.csv
dayahead-delivery-day-metrics.csv
intraday-slice-metrics.csv
conditional-metrics.csv
```

Do not commit large raw datasets, model binaries, virtualenvs, wheels or caches.

## Files to inspect

```text
requirements/package-runs/P0054M/CHANGELOG.md
requirements/package-runs/P0054M/model-comparison.md
requirements/package-runs/P0054M/advanced-price-ablation.md
requirements/package-runs/P0054M/weekly-168h-path-results.md
requirements/package-runs/P0054M/leakage-review.md
requirements/package-runs/P0054M/price-feature-protocol-decision.md
requirements/package-runs/P0054K/model-comparison.md
requirements/package-runs/P0054E/import-validation.md
memory/energy-market-ai-lab.md
memory/spotprice-forecast-period-policy.md
docs/functions/mac/spotprice-model-diagnostics.md
docs/functions/mac/weather-history-dataset.md
local source files for P0054M modeling and evaluation
```

Do not read large raw data files during bootstrap unless required by verification/modeling commands.

## Files allowed to change

```text
requirements/packages/P0054N-labb-se3-consumption-full-36h-dayahead.md
requirements/package-runs/P0054N/**
docs/functions/mac/spotprice-model-diagnostics.md if durable docs need updating
docs/functions/mac/weather-history-dataset.md if durable docs need updating
src/mac/** relevant existing LABB consumption evaluation scripts if changes are needed
tests/mac/** relevant tests for changed 36h/DayAhead evaluation logic
```

## Forbidden changes

```text
No Shelly changes.
No Home Assistant changes.
No device/API/runtime writes.
No production deployment.
No G2-KANDIDAT promotion.
No Nord Pool/workplace integration or submission.
No actual future spot price leakage.
No unsafe use of P0054L2 holdout-only price rows as train_fit features.
No production/export/import/A61/future-flow features.
No live API calls.
No large raw dataset/model binary/venv/cache commits.
No broad refactor unrelated to P0054N.
```

## Verification commands

Codex must define final commands in `design.md`, but must run equivalent checks for:

```text
P0054 split applied
SE3 consumption target source verified
P0054M advanced price protocol reviewed
full_36h paths complete or skipped with reason
DayAhead 12:00 D-1 delivery-day slice has correct Europe/Stockholm/UTC handling
no-price and with-price matrices use identical target rows where paired modeling is claimed
feature matrix contains no actual future price/production/flow/A61 columns
P0054L2 holdout-only rows are not used as train_fit features unless safe rolling/oof coverage exists
LightGBM/XGBoost import status OK or documented
leakage review passes
git diff --check
no large data/model/env artifacts staged
```

## Pass / WARN / STOP interpretation

PASS requires:

```text
- full_36h evaluation is reported for key SE3 models.
- DayAhead delivery-day 12:00 D-1 evaluation is reported.
- Advanced price feature effect is evaluated safely or explicitly WARN-labeled.
- Best full_36h and DayAhead models are identified.
- Leakage review passes.
```

WARN is acceptable if:

```text
- with-price branch has partial train coverage but is honestly labeled and no leakage occurs.
- one model family fails but ExtraTrees and XGBoost are available.
- some conditional regimes have too few samples.
- DayAhead DST edge cases require skipped days and are documented.
```

STOP if:

```text
- full_36h paths cannot be constructed.
- DayAhead delivery-day timing cannot be represented safely.
- unsafe price features would be required.
- actual future spot/load leaks into features.
- holdout is used for fitting or model selection.
- API/device/runtime/Nord Pool/workplace integration is attempted.
```

## Expected Codex output

```text
PASS/WARN/STOP status
full_36h model comparison
DayAhead delivery-day model comparison
best full_36h model and MAE
best DayAhead hourly MAE model
best DayAhead daily energy error model
advanced price deltas at 36h and DayAhead
comparison to P0054M full_168h/direct results
method-candidate interpretation
leakage review result
what we learned
next package recommendation
tests/commands run
files changed
confirmation no actual future price/API/device/A61/NordPool/workplace integration
confirmation no large artifacts committed
commit SHA after push
```

## Completion notes

To be filled after implementation.
