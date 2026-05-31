# P0035 model promotion summary

P0035 added staging/active promotion for M4 artifacts.

```text
base = /Users/marcus.lovenstad/.smart-home/data/spotprice_ml_models/m4
staging = /Users/marcus.lovenstad/.smart-home/data/spotprice_ml_models/m4/staging/20260531T070003Z
active = /Users/marcus.lovenstad/.smart-home/data/spotprice_ml_models/m4/active
```

Promotion succeeded after backtest/training completed.

The active directory contains:

```text
system_proxy_se1_model.json
system_proxy_se1_model.joblib
area_diff_proxy_se3_model.json
area_diff_proxy_se3_model.joblib
m4_artifact_manifest.json
m4_model.sqlite3
m4_promotion_manifest.json
```

If staging validation fails in a later run, active artifacts should be left untouched.
