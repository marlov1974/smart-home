# P0054L2 Price Target Contract

```json
{
  "duplicates": 0,
  "end": "2026-05-25T22:00:00Z",
  "holdout_rows": 8615,
  "label": "reconstructed SE3 absolute spot price source for LABB forecast-safe baseline",
  "nonfinite_values": 0,
  "ok": true,
  "package_id": "P0054L2",
  "reconstruction": "se3_absolute_price = system_proxy_se1.hour_price + area_diff_proxy_se3.hour_price",
  "rows": 34968,
  "source_series": [
    "system_proxy_se1",
    "area_diff_proxy_se3"
  ],
  "source_table": "ai2_hour_to_day_training_targets_v2",
  "start": "2022-05-29T23:00:00Z",
  "target": "spot_price_se3",
  "timestamp_semantics": "timestamp_utc is the target hour start in UTC",
  "train_fit_rows": 26304,
  "unit": "repository hour_price convention"
}
```
