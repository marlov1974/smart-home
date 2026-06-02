# P0049 implementation design

## Package interpretation

P0049 tests whether SE3-SE1 bottleneck behavior is better understood as an accumulated reservoir/memory process and whether price/day-type patterns suggest industrial demand response.

This package is exploratory. It produces tables, metrics and recommendations only.

## Implementation structure

Add:

```text
src/mac/services/spotprice_model_diagnostics/p0049.py
tests/mac/services/spotprice_model_diagnostics/test_p0049.py
```

The module will:

- load `se3_se1_bottleneck_training_dataset_v1`
- validate fixed-CET and spread arithmetic
- add day-type/industrial-response proxy fields
- fit train-only price thresholds
- add rolling, lagged, horizon and reservoir features using strictly prior rows
- persist `se3_se1_bottleneck_reservoir_analysis_v1`
- evaluate horizon-by-horizon feature groups and baselines
- write required P0049 evidence

## Modeling strategy

Keep complexity conservative and fast:

- primary analysis uses deterministic baselines, correlations, response tables and small sklearn models where useful
- horizon analysis uses feature-group score tables for classification and regression
- no model binaries are written

## Intended changes

- `src/mac/services/spotprice_model_diagnostics/p0049.py`
- `tests/mac/services/spotprice_model_diagnostics/test_p0049.py`
- `docs/functions/mac/spotprice-model-diagnostics.md`
- `docs/functions/00-index.md`
- `requirements/package-runs/P0049/**`
- `requirements/packages/P0049-se3-se1-bottleneck-reservoir-and-industrial-response-analysis.md`

No device, Shelly, Home Assistant, deploy, KVS or API files are intended to change.

## Test strategy

Unit tests cover:

- spread arithmetic
- fixed-CET fields
- rolling features are backward-looking
- horizon targets are shifted forward
- train-only price thresholds
- reservoir formula reproducibility
- deterministic day-type fields
- chronological split boundaries
- forbidden path constants

Verification:

```text
python3 -m unittest tests.mac.services.spotprice_model_diagnostics.test_p0049
python3 -m src.mac.services.spotprice_model_diagnostics.p0049
git diff --check
```

The package command needs write access to the local feature DB to persist the derived analysis table.

## Risks

Industrial response can only be inferred from price/day-type proxies. P0049 must not present it as proven.

Long-horizon metrics may be weak because the dataset has limited years and holdout ends in May 2026.
