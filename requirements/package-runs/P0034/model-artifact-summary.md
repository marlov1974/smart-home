# P0034 model artifact summary

Model directory:

```text
/Users/marcus.lovenstad/.smart-home/data/spotprice_ml_models/m4
```

Artifacts:

```text
m4_artifact_manifest.json             798B
system_proxy_se1_model.json           640B
system_proxy_se1_model.joblib         1835B
area_diff_proxy_se3_model.json        649B
area_diff_proxy_se3_model.joblib      1835B
m4_model.sqlite3                      40M
```

Manifest:

```json
{
  "algorithm": ["sklearn_polynomial_features_ridge"],
  "model_version": "m4_sklearn_polynomial_ridge_v2",
  "package_id": "P0034",
  "targets": [
    "area_diff_proxy_se3",
    "system_proxy_se1"
  ]
}
```

Dependency decision:

```text
scikit-learn installed and used.
sklearn = 1.6.1
numpy = 2.0.2
scipy = 1.13.1
joblib = 1.5.3
threadpoolctl = 3.6.0
algorithm = PolynomialFeatures(degree=2, include_bias=False) + Ridge(alpha=1.0, fit_intercept=True)
```
