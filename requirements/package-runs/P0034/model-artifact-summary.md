# P0034 model artifact summary

Model directory:

```text
/Users/marcus.lovenstad/.smart-home/data/spotprice_ml_models/m4
```

Artifacts:

```text
m4_artifact_manifest.json        497B
system_proxy_se1_model.json      863B
area_diff_proxy_se3_model.json   872B
m4_model.sqlite3                 40M
```

Manifest:

```json
{
  "algorithm": "pure_python_ridge_normal_equation",
  "model_version": "m4_ridge_calendar_v1",
  "package_id": "P0034",
  "targets": [
    "area_diff_proxy_se3",
    "system_proxy_se1"
  ]
}
```

Dependency decision:

```text
scikit-learn unavailable. P0034 used deterministic pure-Python Ridge regression with lambda=1.0.
```
