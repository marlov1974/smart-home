# P0045 implementation design

Package interpretation:

P0045 combines the corrected AI-1 daily/local-week diagnostics from P0044 with the AI-2 hour-to-day diagnostics from P0043 into rolling fixed-CET 168-hour shape forecasts. The result is evidence for whether the new seven-day index track is ready for P0046 anchored absolute-price backtesting.

Implementation structure:

- Add `src/mac/services/spotprice_model_diagnostics/p0045.py`.
- Add `tests/mac/services/spotprice_model_diagnostics/test_p0045.py`.
- Update `docs/functions/mac/spotprice-ml-normal-model.md` with the P0045 combination contract.
- Write all P0045 evidence under `requirements/package-runs/P0045/`.

Data/model input approach:

- Load only P0042 corrected tables:
  - `ai1_day_to_local_week_training_targets_v2`
  - `ai2_hour_to_day_training_targets_v2`
- Regenerate predictions from P0043/P0044 selected groups using their existing deterministic train functions and train-period rows only.
- Do not search hyperparameters or choose new AI-1/AI-2 model groups.
- Apply P0044 fallback policy for weak area_diff scale targets:
  - `log_day_scale_index = 0.0`
  - `log_local_7d_scale = train mean` from P0044 baseline policy

Combination formulas:

- Scaled formula:
  - `local_7d_scale = exp(log_local_7d_scale)`
  - `day_scale_index = exp(log_day_scale_index)`
  - `day_scale = local_7d_scale * day_scale_index`
  - `raw = day_level_shape * local_7d_scale + hour_shape * day_scale`
  - center each 168h window to mean zero
- Dimensionless formula:
  - `raw = day_level_shape + hour_shape * day_scale_index`
  - center each 168h window to mean zero

Evaluation:

- Rolling fixed-CET 168h windows starting at model day D 00:00.
- Evaluate validation windows in 2025 and holdout windows in 2026.
- Require exactly 168 hourly rows per window and target series.
- Compare combined formulas against B0-B5 baselines.
- Primary selection is based on validation scaled shape MAE with holdout reported separately.
- Oracle diagnostics are labeled and excluded from deployable selection.

Deliberate non-changes:

- No production API.
- No anchored absolute forecast.
- No M5/M6/M7.
- No AI-1/AI-2 retraining beyond deterministic artifact regeneration.
- No Shelly, Home Assistant, KVS or device interaction.

Test strategy:

- Unit-test fixed-CET 168h window construction.
- Unit-test fallback policy for weak area_diff scale targets.
- Unit-test shape centering.
- Unit-test finite positive scale exponentiation.
- Unit-test oracle exclusion from deployable selection.
- Unit-test forbidden path constants.

Risks:

- Regenerated predictions depend on deterministic sklearn behavior and local package versions.
- Rolling 168h windows overlap heavily; evidence will note that metrics are selection diagnostics, not iid confidence estimates.
- area_diff is expected to remain weak; WARN is acceptable if SE1 is usable.
