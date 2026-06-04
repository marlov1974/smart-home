# P0054L Package Consistency Review

Status: `WARN`

## Understanding

P0054L is a LABB package, not G2-KANDIDAT. It must train/evaluate SE3 spot-price forecast models only, compare them to the P0054K reconstructed origin-local historical baseline, and write price-forecast evidence. It must not rerun SE3 consumption models.

## Repository Truth Checked

- P0054K created `anchored_absolute_price_forecast_log_p0054k_se3_v1` with 242,088 rows and leakage review `ok`.
- P0054K reconstructed SE3 absolute price as `system_proxy_se1.hour_price + area_diff_proxy_se3.hour_price`.
- `ai2_hour_to_day_training_targets_v2` contains both required source series.
- P0054E import validation shows LightGBM and XGBoost are installed.
- P0054K evidence shows SE3 price forecast helped LightGBM consumption but worsened XGBoost consumption, motivating a better price forecast.

## Consistency Result

`WARN`.

The package is implementable and safe for holdout price forecast evaluation. The warning is about downstream scope:

```text
A global model trained on train_fit can safely evaluate holdout predictions, but it is not automatically a forecast-origin-safe train-period feature source for downstream consumption model training.
```

Therefore P0054L may create a holdout-safe advanced forecast log and a downstream recommendation. If a later P0054M needs train_fit consumption features, it should either use a rolling/out-of-fold train forecast log or explicitly limit itself to evaluation use. P0054L will document this in the downstream contract.

## Safety Review

Allowed:

- Local SQLite reads and a local P0054L forecast-log table write.
- Local deterministic LABB model training/evaluation.

Forbidden and avoided:

- No live API calls.
- No devices, Shelly, Home Assistant, KVS or runtime writes.
- No downstream SE3 consumption model rerun.
- No actual future spot price as a model feature.
- No production, export/import, A09/A11, A61 capacity/utilization/margin or continental-price features.
- No P0053C-B/M4 validation/holdout-only forecast as a train feature.

## Assumptions

- The SE3 price target unit follows existing repository convention in `ai2_hour_to_day_training_targets_v2.hour_price`; no unit conversion is performed.
- Advanced candidate feature construction uses only target-calendar and historical price features available strictly before `forecast_origin_timestamp_utc`.
- Candidate selection is based on internal validation inside train_fit; holdout is used only for final reporting.
