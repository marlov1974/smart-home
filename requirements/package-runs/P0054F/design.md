# P0054F Design

Package: P0054F
Label: LABB

## Stop-Gated Design Outcome

P0054F stops at source-contract review.

The intended implementation would have reused the P0053B SE1 consumption row builder and added a P0053C-B anchored absolute SE1 price forecast feature group. That design is blocked because the forecast-safe price forecast source has validation and holdout rows only, with no train rows.

## Intended Structure If Unblocked

If a future package creates a train/validation/holdout forecast-origin-safe SE1 price forecast log, the implementation should:

1. Load SE1 consumption rows from `physical_balance_se1_se4_hourly_v1`.
2. Load `se1_core_weather` and derive train-only weather normals as in P0053B.
3. Load price forecast rows with explicit `forecast_origin_timestamp_utc`, `input_data_cutoff_utc`, `target_timestamp_utc`, `horizon_hours`, `area='SE1'`, `prediction_kind='anchored_absolute_price'`.
4. Join each consumption example to a price forecast path available at the same example origin.
5. Derive price path features only from rows sharing the same forecast origin.
6. Train paired no-price and with-price models on identical target rows.
7. Evaluate validation and holdout without using holdout for model selection.

## Why Implementation Stops

The train split is required:

```text
train: 2022-06-01T00:00:00Z .. 2024-12-31T23:00:00Z
```

P0053C-B forecast log starts at:

```text
2025-01-01T23:00:00Z
```

There are no price forecast rows for training examples. A with-price model cannot be trained fairly or safely under P0054F.

## Verification Performed

Read-only SQLite checks confirmed P0053C-B table coverage and absence of train rows. Repository evidence checks confirmed P0053C-B leakage review and G7 readiness for validation/holdout forecast-path-derived features.
