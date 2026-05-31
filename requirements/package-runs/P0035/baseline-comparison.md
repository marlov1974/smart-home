# P0035 baseline comparison

Baselines:

```text
M1 = P0033/P0035 normal_price_v1
P0034 M4 = m4_sklearn_polynomial_ridge_v2 holdout evidence from P0034
P0035 M4 = m4_residual_m1_anchor_v1
```

## Holdout hourly comparison

| target | metric | M1 | P0034 M4 | P0035 residual M4 | winner |
|---|---:|---:|---:|---:|---|
| system_proxy_se1 | MAE | 0.33685564669429213 | 0.5955499675395327 | 0.6079521874402215 | M1 |
| system_proxy_se1 | RMSE | 0.47642915390238133 | 0.7683190174304994 | 0.7644348442048995 | M1 |
| area_diff_proxy_se3 | MAE | 0.20279122565396646 | 1.8329536040834036 | 1.8269617292981122 | M1 |
| area_diff_proxy_se3 | RMSE | 0.29322917847350166 | 1.8847956763097777 | 1.8773900197706685 | M1 |
| recomposed_se3 | MAE | 0.3831750317910952 | 1.6277238925618174 | 1.6662037682642874 | M1 |
| recomposed_se3 | RMSE | 0.4971918166163072 | 1.8226038667974305 | 1.8576351313078958 | M1 |

P0035 improves area-diff slightly versus P0034 M4, but it does not materially improve the full recomposed SE3 result and remains worse than M1.

## Status

`WARN`: M3A/M3B/M3AB and residual M4 are built and reproducible, but P0035 M4 is not replacement-quality.
