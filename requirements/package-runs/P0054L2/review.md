# P0054L2 Package Consistency Review

Status: `WARN`

## Understanding

P0054L2 retries the stopped P0054L SE3 spot-price forecast experiment with an explicit serial long-run policy. It is `LABB` research only, not `G2-KANDIDAT`, and must not rerun SE3 consumption models.

The package must compare completed advanced SE3 price models against the P0054K origin-local reconstructed SE3 price baseline and preserve completed evidence even if a later model is slow or fails.

## Repository Truth Checked

- P0054K created `anchored_absolute_price_forecast_log_p0054k_se3_v1` with reconstructed SE3 price rows.
- P0054K source contract reconstructs SE3 absolute spot price as `system_proxy_se1.hour_price + area_diff_proxy_se3.hour_price` from `ai2_hour_to_day_training_targets_v2`.
- P0054K leakage review passed for the origin-local baseline.
- P0054L stopped because its all-candidate implementation did not finish in a practical package window.
- P0054E import evidence shows LightGBM and XGBoost installed in the local LABB Python environment.
- `memory/energy-market-ai-lab.md` requires LABB input classification and benchmark comparison.
- `memory/spotprice-forecast-period-policy.md` defines the global P0053C split, while P0054L2 explicitly reuses the operator-approved P0054 train-fit/holdout policy.

## Consistency Result

`WARN`.

The package is implementable and safe, but long runtime and dependency/import variability remain real risks. The package itself explicitly permits partial useful completion as `WARN` when at least two advanced model families complete and leakage checks pass.

The downstream warning from P0054L is preserved:

```text
A global model trained on train_fit can safely evaluate holdout predictions, but it is not automatically a forecast-origin-safe train-period feature source for downstream consumption model training.
```

## Safety Review

Allowed and planned:

- Local SQLite reads and package-scoped table writes.
- Local deterministic Python model training/evaluation.
- Package-run evidence and compact checkpoint files.

Forbidden and avoided:

- No live API calls.
- No Shelly, Home Assistant, KVS, device or runtime changes.
- No downstream SE3 consumption model rerun.
- No actual target-window future SE3 price as a model feature.
- No production/export/import/A61/future-flow features.
- No model binaries, virtualenvs, wheels or large raw datasets committed.

## Assumptions

- The SE3 price unit remains the repository convention of `ai2_hour_to_day_training_targets_v2.hour_price`.
- Candidate features are only target-calendar, horizon and origin-strict historical SE3 price lag/rolling features.
- Holdout is used only after models and hyperparameters are fixed by package design, not for model-family selection.
