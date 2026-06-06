# P0054T4 Implementation Design

## Interpretation

P0054T4 tests production-realistic forecast-weather error: train on clean weather proxy, then perturb only holdout/inference temperature inputs while keeping fitted models fixed.

This supersedes P0054T3 weather-error interpretation, where W1 retrained on noisy train and holdout rows.

## Implementation Structure

Add `src/mac/services/spotprice_model_diagnostics/p0054t4.py`.

The runner will:

- run a P0054R baseline reproduction gate into a temporary directory,
- build P0054R clean no-price rows,
- fit M1 exactly once on clean train_fit/internal-validation data,
- score W0 clean holdout,
- for seeds 1000..1009, copy clean path rows, apply temperature noise only where `split == holdout`, predict with the fixed trained base models, apply the fixed ensemble weights and fixed horizon-bias correction, and score,
- write compact package evidence.

## Intended Changes

- `src/mac/services/spotprice_model_diagnostics/p0054t4.py`
- `tests/mac/services/spotprice_model_diagnostics/test_p0054t4.py`
- `requirements/package-runs/P0054T4/**`
- `requirements/packages/P0054T4-labb-se3-consumption-inference-weather-noise.md`
- `docs/functions/mac/spotprice-model-diagnostics.md`

## Non-Changes

- No spot-price features.
- No model binaries.
- No runtime, API, device, Shelly or Home Assistant changes.
- No broad P0054R/P0054T3 refactor.

## Verification Commands

```bash
PYTHONPYCACHEPREFIX=/private/tmp/p0054t4-pycache /usr/bin/python3 -m unittest tests.mac.services.spotprice_model_diagnostics.test_p0054t4
PYTHONPYCACHEPREFIX=/private/tmp/p0054t4-pycache /usr/bin/python3 -m src.mac.services.spotprice_model_diagnostics.p0054t4
git diff --check
find requirements/package-runs/P0054T4 src/mac/services/spotprice_model_diagnostics tests/mac/services/spotprice_model_diagnostics docs/functions/mac -type f -size +1M -print
```

## Risk

The main approximation is that noise is applied to final temperature model-input columns, not raw weather followed by full derived-feature recomputation. Evidence must label this clearly.
