# P0054T3 LABB

Status: `WARN`

```json
{
  "alias_headline": "internal validation rows are absent, so learned horizon biases are all zero and M1 is exactly M2",
  "bounded": true,
  "dataset_diff": {
    "intersection_origins": 448,
    "intersection_rows": 16102,
    "p0054r_origins": 1451,
    "p0054r_target_end": "2026-06-04T21:00:00Z",
    "p0054r_target_rows": 52173,
    "p0054r_target_start": "2022-06-08T10:00:00Z",
    "p0054t_origins": 448,
    "p0054t_target_end": "2026-05-24T21:00:00Z",
    "p0054t_target_rows": 16102,
    "p0054t_target_start": "2025-03-01T00:00:00Z",
    "r_only_origins": 1003,
    "r_only_rows": 36071,
    "t_only_origins": 0,
    "t_only_rows": 0
  },
  "implementation_diff_headline": "P0054T selected fewer base families and its P0054N exact-origin rowset leaves no internal validation rows for W0/P0, forcing equal weights and zero horizon bias.",
  "metric_diff": {
    "historic_r_dayahead_mae": 253.70062353819162,
    "r_like_minus_historic_abs_mw": 1.1368683772161603e-13,
    "reproduced_r_dayahead_mae": 253.70062353819173,
    "t_like_m1_dayahead_mae": 624.3881907571396,
    "t_like_minus_r_like_abs_mw": 370.68756721894783
  },
  "metric_gap_explained_by": [
    "row/origin set mismatch",
    "internal validation unavailable",
    "equal ensemble weights",
    "zero horizon bias",
    "different base-model set"
  ],
  "primary_root_cause": "P0054T W0/P0 was not a faithful P0054R reproduction. It used the P0054N exact-origin price-coverage skeleton even for no-price, producing only March-May 2025 train_fit coverage and zero internal-validation rows.",
  "secondary_root_cause": "P0054T M1 equaled M2 because horizon-bias correction fitted all-zero biases when internal validation rows were absent."
}
```
