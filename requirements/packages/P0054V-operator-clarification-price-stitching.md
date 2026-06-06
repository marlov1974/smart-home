# P0054V operator clarification: actual spot in training, forecast spot at inference

## Status

clarification for P0054V

## Operator clarification

For P0054V, the SE3 consumption model must not be trained as if historical forecasted spot price were the normal explanatory variable when actual historical spot price is available.

The intended production-like price feature semantics are:

```text
Training / train_fit rows:
  use historical actual SE3 spot price where the target timestamp is in historical train_fit
  use actual spot history before each forecast origin for lag/history/anchor features

Holdout / inference rows:
  use actual SE3 spot price only for timestamps strictly before forecast_origin_timestamp_utc
  use spot-price forecast for future target-window timestamps that are not known at forecast_origin_timestamp_utc
```

In short:

```text
actual spot trains the consumption model's price relationship
spot-price forecast fills the missing future 36h at forecast/inference time
actual spot for approximately the previous 48h is used as history/anchor
```

## Required stitched price path

P0054V must build and document a stitched price path for each forecast origin:

```text
price_history_anchor:
  actual SE3 spot price for the latest available history before forecast_origin_timestamp_utc
  required minimum: previous 48h when available

price_future_forecast:
  predicted SE3 spot price for each target horizon in the forecast window
  horizon convention must match the consumption model: 36 target hours
```

The resulting model feature construction must distinguish:

```text
actual_spot_history_feature
forecast_spot_future_feature
stitched_spot_path_feature
```

Codex must not silently collapse all of these into one generic `predicted_spot_price_se3` without documenting whether the value is actual history or future forecast.

## Train/inference skew policy

P0054V may train the primary consumption model using actual historical spot for historical target timestamps. This is allowed and intended.

However, P0054V must explicitly document the train/inference skew:

```text
train_fit target-window price values are actual spot
holdout future target-window price values are forecast spot
```

This is acceptable for the primary P0054V test because it answers the operator's current question.

A later stricter package may test an out-of-fold or forecast-like price feature in the train period. Do not make that stricter protocol a blocker for P0054V.

## Required 48h anchor features

Where available, include or test features based on the actual spot history before origin:

```text
actual_spot_lag_1h
actual_spot_lag_24h
actual_spot_lag_48h
actual_spot_history_0_24h_mean
actual_spot_history_24_48h_mean
actual_spot_history_48h_mean
actual_spot_history_48h_min
actual_spot_history_48h_max
actual_spot_history_48h_spread
actual_spot_last_known_value
```

The anchor window must use only data strictly before forecast origin.

If market publication timing means some same-day future spot prices are known at origin for specific DayAhead use cases, Codex must document the assumption and keep a conservative default:

```text
default: future target-window spot is treated as unknown and forecasted
```

## Feature-family impact

P0054V's price feature families must use the stitched path semantics:

```text
P1 raw price:
  actual history before origin + forecast future horizons

P2 path shape:
  computed from the forecast future path and, where relevant, the actual 48h anchor

P3 regimes:
  thresholds learned only inside train_fit; features computed from forecast future path and safe history

P4 spike/ramp:
  ramps may compare forecast horizon h to previous forecast horizon, or horizon 0 to last known actual spot before origin

P5 interactions:
  price inputs must use the same stitched actual-history/forecast-future semantics

P6 conditional branch:
  regime trigger must be based only on stitched features available at origin
```

## Leakage rules

Forbidden:

```text
actual SE3 spot price for target-window future timestamps during holdout/inference
same-hour realized target timestamp spot as a holdout feature
future actual load, production, flow, exchange, net position or A61 features
holdout data for threshold/model/feature selection
```

Allowed:

```text
actual SE3 spot price strictly before forecast origin
forecasted SE3 spot price for future target-window horizons
actual spot in train_fit target timestamps for primary price-relation training
```

## Required evidence additions

P0054V must add or include these evidence files/sections:

```text
requirements/package-runs/P0054V/price-stitching-policy.md
requirements/package-runs/P0054V/actual-spot-training-policy.md
requirements/package-runs/P0054V/price-history-anchor-features.md
requirements/package-runs/P0054V/train-inference-skew-review.md
```

The leakage review must explicitly answer:

```text
Did holdout target-window actual spot leak into features? expected: no
Was actual spot used in train_fit target timestamps? expected: yes
Was actual spot history before origin used as anchor? expected: yes
Was forecasted spot used for future holdout horizons? expected: yes
Was the previous 48h actual spot anchor strictly before origin? expected: yes
```

## Relationship to main package

This clarification strengthens and amends:

```text
requirements/packages/P0054V-labb-complete-spotprice-value-test-se3-consumption.md
```

If there is any conflict, follow this operator clarification.
