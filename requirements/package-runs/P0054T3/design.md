# P0054T3 Implementation Design

## Interpretation

P0054T3 supersedes P0054T by rerunning the SE3 consumption model/weather/price matrix without allowing price forecast coverage to redefine P0. The primary P0 results use the P0054R full no-price row/origin contract.

## Structure

Add `src/mac/services/spotprice_model_diagnostics/p0054t3.py`.

The runner will:

- run the P0054R baseline gate through `p0054r.run_p0054r_analysis` into a temporary directory,
- build P0 full rows from `p0054r.build_p0054r_modeling_rows`,
- build P1 rows from the existing safe P0054N exact-origin P0054L2-compatible price contract,
- build a matched P0_on_price_coverage diagnostic by intersecting P0 rows with P1 row keys,
- run W0 and W1 seeds 1000..1004,
- produce 12 required matrix combinations: 3 models x 2 weather x 2 price modes,
- write matched price deltas separately when P1 coverage is narrower.

## Model Semantics

M1 uses `HorizonBiasCorrected_WeightedEnsemble`.

M2 uses `WeightedEnsemble`.

M3 uses `XGBoost`.

P0 full uses P0054R base families: HGB, ExtraTrees, LightGBM and XGBoost. P1/matched coverage uses the same available families where possible. If a coverage branch has no internal validation, evidence will show equal weights and zero horizon bias for that branch.

## Files Changed

Allowed changes:

- `src/mac/services/spotprice_model_diagnostics/p0054t3.py`
- `tests/mac/services/spotprice_model_diagnostics/test_p0054t3.py`
- `requirements/package-runs/P0054T3/**`
- `requirements/packages/P0054T3-labb-corrected-se3-consumption-weather-price-matrix.md`
- `docs/functions/mac/spotprice-model-diagnostics.md`

## Tests

Verification commands:

```bash
PYTHONPYCACHEPREFIX=/private/tmp/p0054t3-pycache /usr/bin/python3 -m unittest tests.mac.services.spotprice_model_diagnostics.test_p0054t3
PYTHONPYCACHEPREFIX=/private/tmp/p0054t3-pycache /usr/bin/python3 -m src.mac.services.spotprice_model_diagnostics.p0054t3
git diff --check
find requirements/package-runs/P0054T3 src/mac/services/spotprice_model_diagnostics tests/mac/services/spotprice_model_diagnostics docs/functions/mac -type f -size +1M -print
```

## Risks

- The full matrix is computationally heavier than P0054T because P0 uses P0054R full coverage.
- P1 likely remains narrower and therefore the package may complete with `WARN`.
- P1 M1 may alias M2 if no internal validation exists on safe price coverage; this must be reported instead of hidden.
