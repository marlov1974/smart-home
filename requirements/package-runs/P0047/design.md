# P0047 implementation design

## Package interpretation

P0047 exports and analyzes the last complete year of hourly `SE3-SE1` spread behavior. It must produce inspectable package-run evidence and recommend a future model framing. It must not train or publish a deployable model, create an API, or test SE1-to-SE3 anchoring.

## Export window

Use fixed-CET model dates:

```text
2025-01-01 .. 2025-12-31
```

This is the latest complete calendar year available in the corrected P0042 AI2 v2 dataset and matches the package's preferred example.

## Implementation structure

Add a new module:

```text
src/mac/services/spotprice_model_diagnostics/p0047.py
```

The module will:

- load `ai2_hour_to_day_training_targets_v2` through SQLite
- validate the required P0042 fixed-CET fields
- join `system_proxy_se1` and `area_diff_proxy_se3` hourly rows by `timestamp_utc`
- reconstruct `se3_price = se1_price + se3_minus_se1`
- export CSV evidence
- compute data-driven spread thresholds
- assign candidate regime labels
- compute distributions, group summaries, run lengths, spike examples and transition matrix
- write Markdown/JSON/CSV evidence under `requirements/package-runs/P0047/`

Add tests:

```text
tests/mac/services/spotprice_model_diagnostics/test_p0047.py
```

## Intended changes

Expected changed/created files:

- `src/mac/services/spotprice_model_diagnostics/p0047.py`
- `tests/mac/services/spotprice_model_diagnostics/test_p0047.py`
- `docs/functions/mac/spotprice-model-diagnostics.md`
- `docs/functions/00-index.md`
- `requirements/package-runs/P0047/**`

No source outside Mac spotprice diagnostics is intended to change.

## Refactoring decisions

No broad refactor. P0047 will reuse small helpers from P0041/P0045 where helpful (`percentile`, `robust_scale`, `write`) and keep package-specific analysis in the new P0047 module.

## Test strategy

Unit tests will cover:

- fixed-CET time fields are required
- joined export rows compute `se3_price` and `se3_minus_se1` correctly
- threshold definitions are reproducible
- regime assignment includes near-zero, positive/negative and spike states
- transition/run-length logic is deterministic
- forbidden production path constants include anchoring/API/device/model paths

Package verification will run:

```text
python3 -m unittest tests.mac.services.spotprice_model_diagnostics.test_p0047
python3 -m src.mac.services.spotprice_model_diagnostics.p0047
git diff --check
```

## Risks and uncertainties

Some requested weather columns may be unavailable in the AI2 v2 table. Missing fields will be listed explicitly in `dataset-contract.md` and `export-summary.md`.

Plots may be skipped in committed evidence if adding image-generation dependencies is not justified. P0047 will commit tables and machine-readable summaries instead.
