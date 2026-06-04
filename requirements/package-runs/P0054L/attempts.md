# P0054L Attempts

## Attempt 1

Result: stopped during model training.

The initial candidate hyperparameters were too slow for a bounded LABB package run over the full P0054L direct/path row set. The long-running `python3 -m src.mac.services.spotprice_model_diagnostics.p0054l` process was stopped at PID `79358`.

Adjustment:

```text
HGB max_iter reduced.
ExtraTrees n_estimators/max_samples reduced.
LightGBM n_estimators/leaves reduced.
XGBoost n_estimators/depth reduced.
```

No evidence was accepted from the stopped run. The next run must regenerate all P0054L evidence from scratch.

## Attempt 3

Result: stopped after the same bounded-runtime blocker recurred.

The third run used a further-reduced XGBoost candidate, but the package generator still did not complete within a practical package-run window. The active process was stopped at PID `80208`.

Package decision:

```text
STOPPED after 3 attempts.
```

Current hypothesis:

```text
The direct 168h-expanded row set is too large for the current all-candidate implementation. A follow-up package should either reduce the model matrix before fitting, train/evaluate candidates one at a time with persisted intermediate evidence, use fewer forecast origins for candidate screening before full holdout evaluation, or skip XGBoost with explicit WARN evidence.
```

No generated P0054L metric evidence was accepted from the stopped runs. No downstream consumption model was run.

## Attempt 2

Result: stopped during the remaining boosted-model stage.

The first bounded reduction was still too slow for the package run. The active process was stopped at PID `79706`.

Adjustment:

```text
XGBoost reduced further to a small diagnostic candidate.
```

No evidence was accepted from the stopped run. The next run must regenerate all P0054L evidence from scratch.
