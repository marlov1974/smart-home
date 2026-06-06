# P0054Y2 decomposition validation

```json
{
  "entsoe_se3_mean_mw": 9807.542648289227,
  "joined_hours": 22709,
  "missing_entsoe_hours_count": 44,
  "missing_profiled_hours_count": 0,
  "negative_residual_hours_count": 0,
  "negative_residual_hours_examples": [],
  "profiled_cluster_sum_mean_mw": 2345.31913091039,
  "profiled_share_mean": 0.232195464720034,
  "residual_max_mw": 12093.384786,
  "residual_mean_mw": 7462.223517378818,
  "residual_min_mw": 4348.202091,
  "residual_p05_mw": 5409.7417144,
  "residual_p95_mw": 9835.051692,
  "residual_share_mean": 0.7678045352799661
}
```

The decomposition is exact by construction for joined hours:

```text
profiled_cluster_sum + residual = ENTSO-E SE3 total
```
