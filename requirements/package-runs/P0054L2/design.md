# P0054L2 Implementation Design

## Package Interpretation

P0054L2 is a LABB-only SE3 spot-price forecast experiment. It retries P0054L by running model families serially and writing checkpoints after each completed or skipped model. It must answer whether advanced origin-safe historical-price models beat the P0054K origin-local SE3 price baseline.

## Implementation Structure

Create:

```text
src/mac/services/spotprice_model_diagnostics/p0054l2.py
tests/mac/services/spotprice_model_diagnostics/test_p0054l2.py
requirements/package-runs/P0054L2/**
```

Update:

```text
docs/functions/mac/spotprice-model-diagnostics.md
requirements/packages/P0054L2-labb-se3-advanced-spotprice-forecast-serial-longrun.md
```

## Data Sources

Target source:

```text
ai2_hour_to_day_training_targets_v2
spot_price_se3 = system_proxy_se1.hour_price + area_diff_proxy_se3.hour_price
```

Baseline:

```text
anchored_absolute_price_forecast_log_p0054k_se3_v1
quality_flag = forecast_safe_origin_local_baseline_not_m4
```

## Split Policy

Use P0054 train-through-May-2025:

```text
train_fit: 2022-06-01T00:00:00Z <= target_timestamp_utc < 2025-06-01T00:00:00Z
holdout: target_timestamp_utc >= 2025-06-01T00:00:00Z
```

Internal validation, when reported, is carved from train_fit only:

```text
internal_train: target_timestamp_utc < 2025-03-01T00:00:00Z
internal_validation: 2025-03-01T00:00:00Z <= target_timestamp_utc < 2025-06-01T00:00:00Z
```

Holdout is not used for fitting, early stopping, hyperparameter selection, feature selection or family selection.

## Feature Design

Allowed feature groups:

- horizon hour
- target calendar known in advance
- historical reconstructed SE3 price lags strictly before forecast origin
- historical reconstructed SE3 rolling mean/std/min/max/ramp stats strictly before forecast origin
- previous-week same-hour source only when the source timestamp is strictly before origin

Forbidden feature groups are not loaded or named:

- actual future SE3 price inside target window
- production, consumption/load, export/import, A09/A11 flow, A61 capacity/utilization/margin
- continental actual prices
- live API or device data

## Runtime Strategy

The generator will:

1. Evaluate P0054K baseline on comparable holdout rows.
2. Build one direct horizon matrix for complete 168h daily origin windows.
3. Run HGB, ExtraTrees, LightGBM and XGBoost serially when imports are available.
4. Write `model-checkpoints/<model>.md` and `<model>-metrics.json` immediately after every completed/skipped/failed model.
5. Build an optional simple blend when at least two candidates complete.
6. Create `advanced_spotprice_forecast_log_p0054l2_se3_v1` only if a completed model meets the learning threshold.

The initial implementation uses bounded but non-trivial hyperparameters to avoid repeating the P0054L all-candidate failure. The package policy allows long runtime; it does not require killing slow active processes.

## Test Strategy

Run:

```text
python3 -m unittest tests.mac.services.spotprice_model_diagnostics.test_p0054l2
python3 -m src.mac.services.spotprice_model_diagnostics.p0054l2
git diff --check
```

Runtime verification covers:

- P0054 split applied.
- P0054K baseline is available and comparable.
- Serial model checkpointing writes evidence per model.
- Feature matrix contains only forecast-origin-safe columns.
- Lag and rolling source timestamps are strictly before origin.
- LightGBM/XGBoost import status is either OK or documented.
- Weekly 168h paths are complete where computed.
- Leakage review passes.
- No downstream consumption model output is created.
- No large data/model/env artifacts are staged.

## Risks and Uncertainties

- XGBoost may still be slow; it runs last and previous model checkpoints remain valid.
- Advanced models may not beat P0054K by the required threshold. That is a clean negative LABB result, not a failure.
- A holdout-safe global model log is not sufficient as a train-period feature source for a future consumption model unless P0054M creates rolling/out-of-fold train forecasts or limits itself to holdout-only evaluation.
