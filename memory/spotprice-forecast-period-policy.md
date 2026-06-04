# Spotprice Forecast Period Policy

Last changed: P0053C

## Canonical Period

Forecast modeling rows start at:

```text
2022-06-01T00:00:00Z
```

Rows before this timestamp are excluded from forecast training, validation and holdout scoring because the earlier electricity market regime is materially different from the intended deployment period.

## Canonical Split

```text
train:      2022-06-01T00:00:00Z .. 2024-12-31T23:00:00Z
validation: 2025-01-01T00:00:00Z .. 2025-05-31T23:00:00Z
holdout:    2025-06-01T00:00:00Z .. latest available data
```

Holdout rows must not be used for model selection, profile fitting or feature normalization.

## Boundary Identity

Split membership is based on `timestamp_utc`.

Fixed-CET fields use the existing project rule:

```text
model_cet_timestamp = timestamp_utc + 1h all year
```

`model_cet_*` fields are calendar/features, not split-boundary identity.

## Context-Only Lag Warmup

Rows before `2022-06-01T00:00:00Z` may be read only as lag/rolling context for target rows at or after the modeling start.

Allowed:

```text
target_timestamp_utc >= 2022-06-01T00:00:00Z
lag values read from May 2022
```

Forbidden:

```text
training/scoring/evaluating a target row before 2022-06-01T00:00:00Z
```

## Forecast-Origin Requirement

When one forecast is used as a feature for another forecast, every feature row must prove:

```text
feature_forecast_origin_timestamp_utc <= example_origin_timestamp_utc
```

Actual future values and originless prediction artifacts are not forecast-safe features.

## Stale Metrics Rule

Metrics produced with earlier split policies are historical diagnostics. They must not be compared directly to P0053C-and-later metrics unless rebuilt under this policy and labeled as such.
