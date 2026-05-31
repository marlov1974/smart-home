# P0035 M4 residual model summary

Model:

```text
model_version = m4_residual_m1_anchor_v1
algorithm = sklearn_polynomial_features_ridge
target = m3ab_normalized_price - M1_normal_price
```

Local artifacts:

```text
model_dir = /Users/marcus.lovenstad/.smart-home/data/spotprice_ml_models/m4
active_dir = /Users/marcus.lovenstad/.smart-home/data/spotprice_ml_models/m4/active
```

Promotion:

```text
promoted_at = 2026-05-31T07:00:03Z
staging_dir = /Users/marcus.lovenstad/.smart-home/data/spotprice_ml_models/m4/staging/20260531T070003Z
files = system_proxy_se1_model.json, system_proxy_se1_model.joblib, area_diff_proxy_se3_model.json, area_diff_proxy_se3_model.joblib, m4_artifact_manifest.json, m4_model.sqlite3
```

Result classification:

```text
WARN
```

Reason: residual M4 rebuild is reproducible and promoted, but does not beat M1 on key holdout hourly and level metrics.
