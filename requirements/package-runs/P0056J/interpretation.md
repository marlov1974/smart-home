# P0056J Interpretation

```json
{
  "largest_feature_mismatch_candidates": [
    {
      "feature": "horizon_h",
      "max_abs_delta": 18.0,
      "mismatch_count": 432
    },
    {
      "feature": "area_consumption_lag_1h",
      "max_abs_delta": 5235.0,
      "mismatch_count": 432
    },
    {
      "feature": "area_consumption_lag_2h",
      "max_abs_delta": 4734.0,
      "mismatch_count": 432
    },
    {
      "feature": "area_consumption_lag_3h",
      "max_abs_delta": 4909.5,
      "mismatch_count": 432
    },
    {
      "feature": "area_consumption_lag_6h",
      "max_abs_delta": 5051.666666666666,
      "mismatch_count": 432
    },
    {
      "feature": "area_consumption_lag_12h",
      "max_abs_delta": 709.0,
      "mismatch_count": 432
    },
    {
      "feature": "area_consumption_lag_24h",
      "max_abs_delta": 801.25,
      "mismatch_count": 432
    },
    {
      "feature": "area_consumption_lag_48h",
      "max_abs_delta": 494.0,
      "mismatch_count": 432
    }
  ],
  "persisted_static_vs_rolling_exact_intersection": 0,
  "reconstructed_aligned_intersection_rows": 2556,
  "reconstructed_alignment_mode": "target_timestamp_closest_static_horizon",
  "root_cause_summary": "The original static and rolling headline metrics are not on the same persisted origin/horizon row set; target-aligned reconstructed rows still differ mainly by model method, horizon-bias correction and rolling per-origin training.",
  "static_vs_rolling_delta_on_aligned_intersection": 15.320298377530634
}
```
