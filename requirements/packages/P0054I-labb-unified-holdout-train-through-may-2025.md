# Package P0054I: LABB unified holdout train-through-May-2025 policy

## Status

done

## Package order

P0054I

## Label

```text
LABB
```

This package is research/lab work under P0054A. It is not a G2-KANDIDAT evaluation.

## Purpose

Update the current LABB comparison policy for M1, M4 and the new consumption forecasters so that all compared models are trained on data from June 2022 through May 2025, and all timestamps from June 2025 onward are treated as holdout.

The operator decision is:

```text
M1, M4 and the new consumption forecasters are trained on data from June 2022 through May 2025.
After that, everything is holdout.
All models are tested from June 2025 onward.
```

This package defines and applies that policy for the next SE1 consumption no-price vs with-price-forecast ablation and related price/consumption model comparisons.

## Important scope note

This package changes the LABB comparison split for this line of experiments. It does not retroactively rewrite old package evidence. Older packages may still use the previous P0053C split:

```text
train:      2022-06-01 .. 2024-12-31
validation: 2025-01-01 .. 2025-05-31
holdout:    2025-06-01 .. latest
```

For P0054I and follow-up packages, the LABB comparison split is:

```text
train_fit:  2022-06-01T00:00:00Z .. 2025-05-31T23:00:00Z
holdout:    2025-06-01T00:00:00Z .. latest_available_timestamp_utc
```

There is no separate validation split for final reported comparison unless a model requires an internal fit/early-stopping split carved out strictly inside `train_fit`. Any internal split must not use holdout.

## Core questions

P0054I must answer:

```text
1. How should the new train-through-May-2025 split be represented in package evidence?
2. Which prior P0054F/P0054G/P0054H assumptions need updating for the SE1 consumption ablation retry?
3. Can the P0054H forecast-safe price log support the new train_fit and holdout ranges?
4. What exact downstream package should run the consumption ablation under the new policy?
```

## Required policy output

Create a clear, reusable LABB split policy snippet for this experiment family:

```text
LABB_P0054_TRAIN_THROUGH_MAY_2025
train_fit_start_utc = 2022-06-01T00:00:00Z
train_fit_end_utc   = 2025-05-31T23:00:00Z
holdout_start_utc   = 2025-06-01T00:00:00Z
holdout_end_utc     = latest_available_timestamp_utc
```

Clarify inclusive/exclusive timestamp handling in implementation. Preferred SQL-style interpretation:

```text
train_fit: target_timestamp_utc >= 2022-06-01T00:00:00Z
           and target_timestamp_utc < 2025-06-01T00:00:00Z

holdout:   target_timestamp_utc >= 2025-06-01T00:00:00Z
```

## M1/M4 requirement

For this experiment line:

```text
M1 and M4 must be fit/trained only on train_fit rows ending before 2025-06-01.
M1 and M4 must be evaluated only on 2025-06-01 and later for final holdout reporting.
```

If earlier M1/M4 package implementations used a separate validation period or global training up to 2024-12-31, P0054I should not rewrite those results. It should document that the next rerun/comparison must refit under the new policy.

## Consumption forecaster requirement

The new consumption forecasters must be trained on:

```text
2022-06-01 <= target_timestamp_utc < 2025-06-01
```

and tested on:

```text
target_timestamp_utc >= 2025-06-01
```

This applies to:

```text
SE1 consumption no-price models
SE1 consumption with forecast-safe price features
SE4 consumption models if re-run in this unified comparison style
future spread/flaskhals consumption-response models in this LABB chain
```

## Price forecast source for SE1 with-price features

Use P0054H's forecast-safe source unless a better train-covered forecast-origin-safe source exists:

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

Important label:

```text
This is not M4. It is a forecast-safe origin-local historical price baseline.
```

The later ablation must not call it M4.

## Required coverage check

P0054I must verify or cite P0054H evidence that the price forecast log covers the new split:

```text
train_fit: 2022-06-01 .. 2025-05-31
holdout:   2025-06-01 .. latest
```

If coverage is incomplete, P0054I must identify the gap before any downstream modeling package is created.

## Leakage policy

All compared models must obey:

```text
No holdout rows for training, fitting, early stopping, hyperparameter selection or model selection.
No actual future spot price as a consumption feature.
No target-window actual spot price where only forecast-origin data should be available.
No production/export/import/A61/future-flow features.
No device/API/runtime work.
```

For forecast logs:

```text
input_data_cutoff_utc <= forecast_origin_timestamp_utc
forecast_origin_timestamp_utc <= target_timestamp_utc
all prediction-source timestamps strictly before origin
no target-window actual price as forecast input
```

## Downstream package to create after P0054I

After P0054I documents the new policy and confirms required coverage, create or recommend:

```text
P0054J LABB SE1 consumption price forecast ablation train-through-May-2025
```

P0054J should run the actual model experiment:

```text
no_price vs with_p0054h_price_forecast
models: HGB, ExtraTrees, LightGBM, XGBoost, MLP if practical
train_fit: 2022-06-01 .. 2025-05-31
holdout: 2025-06-01 .. latest
```

## Required evidence files

Create:

```text
requirements/package-runs/P0054I/CHANGELOG.md
requirements/package-runs/P0054I/review.md
requirements/package-runs/P0054I/design.md
requirements/package-runs/P0054I/functions.md
requirements/package-runs/P0054I/labb-label.md
requirements/package-runs/P0054I/split-policy.md
requirements/package-runs/P0054I/p0054h-coverage-for-new-split.md
requirements/package-runs/P0054I/m1-m4-implications.md
requirements/package-runs/P0054I/consumption-forecaster-implications.md
requirements/package-runs/P0054I/downstream-contract-for-p0054j.md
requirements/package-runs/P0054I/what-we-learned.md
requirements/package-runs/P0054I/next-package-recommendation.md
```

Optional compact evidence:

```text
split-policy.json
coverage-summary.json
```

Do not run the downstream model ablation in P0054I. This package is the split-policy and coverage-confirmation package.

## Files to inspect

```text
requirements/package-runs/P0054F/review.md
requirements/package-runs/P0054G/review.md
requirements/package-runs/P0054H/CHANGELOG.md
requirements/package-runs/P0054H/coverage-by-split.md
requirements/package-runs/P0054H/leakage-review.md
requirements/package-runs/P0054H/downstream-contract-for-p0054f-retry.md
requirements/package-runs/P0054H/next-package-recommendation.md
memory/spotprice-forecast-period-policy.md
memory/energy-market-ai-lab.md
docs/functions/mac/spotprice-model-diagnostics.md
```

## Files allowed to change

```text
requirements/packages/P0054I-labb-unified-holdout-train-through-may-2025.md
requirements/package-runs/P0054I/**
memory/spotprice-forecast-period-policy.md only if the project wants this policy recorded as a named LABB exception, not as a global replacement
docs/functions/mac/spotprice-model-diagnostics.md if durable docs need a pointer to the named LABB policy
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
No live API calls.
No model training in this package.
No downstream consumption ablation in this package.
No broad rewrite of historical package evidence.
```

## Verification commands

Codex must define final commands in `design.md`, but must run equivalent checks for:

```text
P0054H price forecast table coverage supports train_fit and holdout
P0054H leakage review is acceptable for downstream use
new split policy is documented with exact timestamp boundaries
no old evidence is rewritten as if it used the new split
no device/API/runtime/live-data actions occurred
git diff --check
```

## Pass / WARN / STOP interpretation

PASS requires:

```text
- new train-through-May-2025 LABB split policy is documented clearly.
- P0054H price forecast source coverage supports the new policy.
- M1/M4 and consumption forecaster implications are explicit.
- downstream contract for P0054J is ready.
```

WARN is acceptable if:

```text
- coverage is sufficient but with known warmup/hour-boundary caveats.
- docs choose to keep this as a package-local LABB policy rather than global memory policy.
```

STOP if:

```text
- P0054H source cannot support train_fit/holdout coverage.
- the proposed policy would require holdout leakage.
- applying the policy would require live API/device/runtime actions.
```

## Expected Codex output

```text
PASS/WARN/STOP status
new split policy summary
P0054H coverage confirmation
M1/M4 implications
consumption forecaster implications
downstream P0054J contract
files changed
commands/tests run
confirmation no live API/device/A61/leakage work
commit SHA after push
```

## Completion notes

P0054I completed as a policy and coverage-confirmation package.

Result:

```text
PASS
```

Defined named LABB policy:

```text
LABB_P0054_TRAIN_THROUGH_MAY_2025
train_fit: target_timestamp_utc >= 2022-06-01T00:00:00Z and target_timestamp_utc < 2025-06-01T00:00:00Z
holdout:   target_timestamp_utc >= 2025-06-01T00:00:00Z
```

Confirmed P0054H source coverage with required filters:

```text
anchored_absolute_price_forecast_log_p0054h_se1_v1
area = SE1
prediction_kind = anchored_absolute_price
quality_flag = forecast_safe_origin_local_baseline_not_m4
training_protocol = origin_local_no_fit_pre_origin_history
```

Coverage by target timestamp under the new split:

```text
train_fit rows = 181776, origins = 1082, range = 2022-06-01T23:00:00Z .. 2025-05-31T22:00:00Z
holdout rows   = 59136, origins = 352, range = 2025-06-01T23:00:00Z .. 2026-05-25T22:00:00Z
```

Warmup/hour-boundary caveat: first covered train_fit target hour is `2022-06-01T23:00:00Z`, not midnight. This is documented and acceptable for P0054J.

No model training, downstream ablation, live API, device, runtime, A61, production deployment or historical evidence rewrite was performed.
