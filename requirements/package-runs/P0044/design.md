# P0044 implementation design

Package interpretation:

P0044 trains and evaluates AI-1 daily/local-week shape and scale models on the corrected P0042 fixed-CET AI-1 dataset. The package produces evidence only; it does not expose or promote a production forecast API.

Implementation structure:

- Add `src/mac/services/spotprice_model_diagnostics/p0044.py`.
- Add `tests/mac/services/spotprice_model_diagnostics/test_p0044.py`.
- Update `docs/functions/mac/spotprice-ml-normal-model.md` with the AI-1 diagnostic contract.
- Store all run evidence under `requirements/package-runs/P0044/`.

Intended behavior:

- Load only `ai1_day_to_local_week_training_targets_v2`.
- Validate required columns and target series row counts.
- Split chronologically by `model_cet_date`:
  - train: earliest through 2024-12-31
  - validate: 2025-01-01 through 2025-12-31
  - holdout: 2026-01-01 through latest available
- Train six separate bounded `HistGradientBoostingRegressor` models:
  - 2 target series: `system_proxy_se1`, `area_diff_proxy_se3`
  - 3 targets: `day_level_shape`, `log_day_scale_index`, `log_local_7d_scale`
- Compare F0-F5 feature groups with deterministic categorical encoding.
- Compare train-only baselines appropriate for each target.
- Select feature groups by validation MAE with simplest-on-near-tie discipline.
- Write markdown and JSON evidence covering baselines, feature ablation, ranking, subsets, best/worst days, leakage notes and P0045 recommendation.

Deliberate scope boundaries:

- Do not retrain AI-2.
- Do not compose SE3 or 168-hour forecasts.
- Do not use absolute day price or diagnostic ratio target as training targets.
- Do not write model binaries to the repository.
- Do not perform device, Shelly, Home Assistant or KVS actions.

Test strategy:

- Unit-test dataset loader failure when v2 table is absent.
- Unit-test chronological split behavior.
- Unit-test train-only baseline behavior.
- Unit-test deterministic categorical encoding.
- Unit-test target and forbidden path constants.
- Unit-test local-window helper crosses calendar years.
- Unit-test finite prediction sanity on a small synthetic dataset.

Risks and uncertainties:

- AI-1 daily row count is small, so validation/holdout metrics are useful but noisy.
- Local-window targets overlap heavily; evidence will explicitly avoid treating adjacent daily rows as iid samples.
- Scale targets may be better handled later by API/anchor logic if they do not beat simple baselines.
