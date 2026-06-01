# P0042 implementation design

## Package interpretation

P0042 corrects the P0041 seven-day index datasets before AI training. It adds a fixed-CET model calendar layer over UTC storage and stabilizes `area_diff_proxy_se3` scale policy.

## Chosen structure

Add `src/mac/services/spotprice_model_diagnostics/p0042.py`.

The module will:

- Load P0037 diagnostic rows and P0038 weather features.
- Keep `timestamp_utc` as the primary row identity.
- Add Stockholm-local diagnostic fields from Europe/Stockholm.
- Add fixed-CET model fields from `timestamp_utc + 1 hour`.
- Build M2A/M2C/M2D normal weather surfaces on `model_cet_day_of_year x model_cet_hour`.
- Build AI-1 v2 using complete fixed-CET model days and `D-2..D+4` model-date windows.
- Build AI-2 v2 using complete fixed-CET model days.
- Select a target-series-specific scale policy: SE1 uses generic P0041 scale, area_diff uses a data-derived median daily scale floor as denominator guard and no primary clipping.
- Persist corrected local tables `*_v2`.
- Write P0042 evidence, including before/after distributions and skip audit.

## Intended changes

Files/modules to change:

- `src/mac/services/spotprice_model_diagnostics/p0042.py`
- `tests/mac/services/spotprice_model_diagnostics/test_p0042.py`
- `requirements/package-runs/P0042/*`
- `docs/functions/mac/spotprice-ml-normal-model.md`

Files intentionally not changed:

- P0041 evidence is kept as historical baseline.
- No P0041 table names are overwritten.
- No AI training or forecast API modules are changed.

## Test strategy

Focused unit tests cover fixed-CET timestamp conversion, 24-hour model days across DST, cross-year AI-1 windows, target-specific area_diff scale floors, unique hourly timestamps, and forbidden path constants.

Package verification will run P0042 generation, P0041/P0042 unit tests, relevant P0038-P0040 regression tests and `git diff --check`.

## Risks

The selected area_diff floor is derived from historical complete model days. It is intentionally a dataset-target normalization policy, not a forecast model. Later training must persist and reuse the same policy metadata.
