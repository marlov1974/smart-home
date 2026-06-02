# P0048 two-stage combined diagnostics

{
  "continuous_lagged_validate_MAE": 0.09374424013635566,
  "formula": "diagnostic comparison: stage1 lagged positive-bottleneck classifier plus stage2 lagged positive severity; exact probability*severity artifact is not persisted",
  "interpretation": "two-stage is promising if classifier F1/recall improves over time baseline and severity beats mean baseline",
  "stage1_validate_f1": 0.886628211851075,
  "stage2_validate_MAE": 0.14071298286546702
}
