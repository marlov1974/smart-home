# P0035 candidate timings

| candidate | target | elapsed_seconds | row_count | feature_count | decision |
|---|---|---:|---:|---:|---|
| sklearn_polynomial_features_ridge | system_proxy_se1 | 0.84526425 | 22729 | 14 | selected |
| sklearn_polynomial_features_ridge | area_diff_proxy_se3 | 0.031900166 | 22729 | 14 | selected |
| HistGradientBoostingRegressor | both | not rerun in P0035 | 22729 | 14 | rejected for Codex package build after P0034 follow-up did not complete within practical interactive window |

Production research may still evaluate HGB outside Codex's interactive package budget.
