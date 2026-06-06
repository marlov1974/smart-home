# P0054V2 LABB

Status: `PASS`

```json
{
  "absolute_delta_MW": 1.2733356730142305,
  "absolute_tolerance_MW": 2.0,
  "hourly_MAE_delivery_day": 252.4272878651774,
  "model": "HorizonBiasCorrected_WeightedEnsemble_no_price",
  "pass_rule": "absolute_delta <= 2.0 MW OR relative_delta <= 1.0%",
  "passed": true,
  "relative_delta_percent": 0.501904825954259,
  "relative_tolerance_percent": 1.0,
  "row_counts": {
    "dayahead_delivery_days": 358,
    "direct_rows": 52173,
    "full36_complete_origins": 356,
    "holdout_rows": 13188,
    "internal_train_rows": 35675,
    "internal_validation_rows": 3310,
    "path_rows": 52173,
    "source_rows": 35125,
    "train_fit_rows": 38985
  },
  "status": "PASS",
  "target_MAE": 253.70062353819162,
  "tmp_evidence_committed": false
}
```
