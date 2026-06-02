# P0048 implementation design

## Package interpretation

P0048 builds a richer SE3-SE1 bottleneck modeling dataset and runs exploratory, non-deployable two-stage modeling:

```text
Stage 1: classify positive bottleneck/spike/regime.
Stage 2: predict positive-regime spread severity.
```

It also compares against continuous spread regression and produces evidence for the next architecture decision.

## Implementation structure

Add a new package module:

```text
src/mac/services/spotprice_model_diagnostics/p0048.py
```

The module will:

- load corrected P0042 AI2 v2 rows
- reconstruct SE1, SE3 and SE3-SE1 spread
- load weather proxy rows from the local weather DB
- derive actual, normal, delta and gradient features
- add lagged spread/regime diagnostic features using only earlier timestamps
- persist local table `se3_se1_bottleneck_training_dataset_v1` in the feature DB
- run chronological train/validate/holdout exploratory models
- write required package evidence under `requirements/package-runs/P0048/`

Add tests:

```text
tests/mac/services/spotprice_model_diagnostics/test_p0048.py
```

## Data and split policy

Use all joined available fixed-CET rows when safe:

```text
train:    earliest available .. 2024-12-31
validate: 2025-01-01 .. 2025-12-31
holdout:  2026-01-01 .. latest complete timestamp
```

If any split is empty, stop rather than silently using random splits.

## Feature foundation

Weather actuals are read from local weather history source tables/views.

Normals/deltas are generated with a fixed-CET seasonal-hour median smoother similar to P0042 M2 logic. The implementation will compute normal and delta for each weather proxy and gradient.

Required gradient formulas will be direct arithmetic, for example:

```text
wind_south_minus_north = wind_south_proxy - wind_north_proxy
solar_south_minus_system = solar_south_proxy - solar_system_proxy
temperature_south_minus_north = temperature_south_proxy - temperature_north_proxy
```

## Modeling approach

Use conservative sklearn models already available locally:

- logistic regression or shallow decision tree/HGB classifier for Stage 1
- HGB/random forest/linear baseline regressors for Stage 2 and continuous spread

No model binaries are committed. Metrics/evidence only.

## Intended changes

Expected changed/created files:

- `src/mac/services/spotprice_model_diagnostics/p0048.py`
- `tests/mac/services/spotprice_model_diagnostics/test_p0048.py`
- `docs/functions/mac/spotprice-model-diagnostics.md`
- `docs/functions/00-index.md`
- `requirements/package-runs/P0048/**`
- `requirements/packages/P0048-se3-se1-bottleneck-feature-foundation-and-exploratory-two-stage-model.md`

No Shelly, Home Assistant, deploy, KVS, API or device files are intended to change.

## Refactoring decisions

No broad refactor. P0048 may reuse small helpers from P0041/P0043/P0047, but keeps package-specific feature and model code in `p0048.py`.

## Test strategy

Unit tests will cover:

- spread reconstruction
- fixed-CET field presence
- gradient formulas
- documented missing feature handling
- regime labels from thresholds
- chronological split non-overlap
- lagged spread features use previous rows only
- forbidden path constants

Package verification will run:

```text
python3 -m unittest tests.mac.services.spotprice_model_diagnostics.test_p0048
python3 -m src.mac.services.spotprice_model_diagnostics.p0048
git diff --check
```

## Risks and uncertainties

Exploratory weather actuals are not production forecast weather. Evidence must label them as proxy-forecast-known diagnostics.

Rare negative regimes may be too sparse for useful separate modeling. Negative and negative-spike may be merged into one rare class.

Stage 2 severity may remain noisy. PASS can still be reached if it is evaluated honestly and the next recommendation is explicit.
