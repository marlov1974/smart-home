# P0054L Implementation Design

## Package Interpretation

P0054L evaluates whether bounded advanced ML models can improve SE3 spot-price forecasts over the P0054K origin-local baseline. It is price forecast only and must not run SE3 consumption models.

## Implementation Structure

Create:

```text
src/mac/services/spotprice_model_diagnostics/p0054l.py
tests/mac/services/spotprice_model_diagnostics/test_p0054l.py
```

Update after implementation:

```text
docs/functions/mac/spotprice-model-diagnostics.md
requirements/packages/P0054L-labb-se3-advanced-spotprice-forecast.md
```

## Data Sources

Target source:

```text
ai2_hour_to_day_training_targets_v2
spot_price_se3 = system_proxy_se1.hour_price + area_diff_proxy_se3.hour_price
```

Baseline source:

```text
anchored_absolute_price_forecast_log_p0054k_se3_v1
```

## Split and Selection

Use P0054 train-through-May-2025:

```text
train_fit: 2022-06-01T00:00:00Z <= target_timestamp_utc < 2025-06-01T00:00:00Z
holdout: target_timestamp_utc >= 2025-06-01T00:00:00Z
```

Internal validation:

```text
internal_train: target_timestamp_utc < 2025-03-01T00:00:00Z
internal_validation: 2025-03-01T00:00:00Z <= target_timestamp_utc < 2025-06-01T00:00:00Z
```

Holdout is not used for hyperparameter selection or model-family selection.

## Feature Design

Allowed features:

- target calendar and horizon known in advance
- historical SE3 price lags at origin
- historical SE3 price rolling stats ending before origin
- previous-week same-hour price, when target-168h is strictly before origin
- origin-local 48h anchor stats
- recent volatility/ramp stats ending before origin

Forbidden features:

- target-window actual SE3 price
- same-hour target actual price
- future production/consumption/load
- future flow/export/import/A09/A11
- A61 capacity/utilization/margin
- continental actual prices
- live API data

## Candidate Models

Run bounded candidates when imports are available:

```text
HGB
ExtraTrees
LightGBM
XGBoost
simple ensemble of the best validation candidates
```

No model binaries will be persisted.

## Forecast Log

Persist the recommended holdout-safe advanced forecast to:

```text
advanced_spotprice_forecast_log_p0054l_se3_v1
```

The table will include `model_name`, origin/cutoff/target/horizon fields, `predicted_price`, unit, protocol, package id and source metadata. It will be suitable for holdout-side downstream evaluation. If a later P0054M needs train-fit consumption training features, P0054M should add rolling/out-of-fold train forecasts rather than treating this holdout-safe log as a full train feature source.

## Test Strategy

Run:

```text
python3 -m unittest tests.mac.services.spotprice_model_diagnostics.test_p0054l
python3 -m src.mac.services.spotprice_model_diagnostics.p0054l
git diff --check
```

Tests cover:

- SE3 target reconstruction.
- Feature construction uses strictly pre-origin timestamps.
- Leakage review rejects forbidden feature-source timestamps.
- Ranking/spike metric helpers behave on a small known example.

Runtime verification covers:

- P0054 split applied.
- P0054K baseline available and comparable.
- HGB/ExtraTrees/LightGBM/XGBoost import/run status.
- Forecast log coverage and schema.
- Leakage review passes.
- No downstream consumption outputs are created.
- No large artifacts are staged.

## Risks and Uncertainties

- A global model is safe for holdout evaluation but not sufficient as a train-period downstream feature source without a rolling/out-of-fold train log.
- The SE3 target unit is inherited from the historical price table and must be documented as repository convention.
- Advanced models may improve ranking/spike/ramp metrics without beating broad MAE.
