# P0054M LABB

Status: `PASS`

Price feature protocol: `rolling_oof_train_plus_holdout`.

Best no-price holdout model: `ExtraTrees_no_price`.

Best with-advanced-price holdout model: `ExtraTrees_with_p0054l2_ensemble_price_forecast`.

XGBoost benefits from advanced price: `True`.

Keep advanced price for future SE3 experiments: `True`.

Weather remains LABB actual-as-forecast proxy. The train-side advanced price source is blocked and partial, not a full train_fit rolling source.
