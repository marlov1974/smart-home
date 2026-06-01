# P0041 implementation design

## Interpretation

P0041 builds the foundation tables and evidence for a new seven-day index forecast track. It keeps active weather-normal signals M2A temperature, M2C solar generation potential and M2D wind generation potential, and creates two supervised learning datasets:

- AI-1 day-to-local-week rows: `date x target_series`, where the local window is exactly `D-2..D+4`.
- AI-2 hour-to-day rows: `timestamp x target_series`, where the day window is exactly local `00:00..23:00`.

Both datasets are built separately for `system_proxy_se1` and `area_diff_proxy_se3`.

## Implementation structure

Add `src/mac/services/spotprice_model_diagnostics/p0041.py`.

The module will:

- Load existing joined diagnostic rows through P0037.
- Enrich P0038 weather proxy signals and derive P0038 solar/wind proxy features.
- Build smooth/cyclic M2 normal surfaces over all available historical rows for temperature, solar and wind signals.
- Attach hourly actual/normal/delta features to rows.
- Aggregate daily weather actual/normal/delta and wind diagnostics.
- Build AI-1 and AI-2 training target rows with robust positive scales.
- Persist the required local SQLite tables in the feature DB.
- Write the required package-run evidence files and compact JSON summaries.

## Deliberate decisions

- Robust scale uses the package formula exactly with `fixed_min_scale = 0.001`.
- Unsafe ratio diagnostics are stored as null when denominator absolute value is below `fixed_min_scale`.
- AI-1 skips incomplete `D-2..D+4` windows instead of flagging them for training.
- M2 normals are cyclic day-of-year/hour median surfaces smoothed over +/-14 calendar days. Daily normals are derived from hourly normal rows aggregated by day-of-year.
- Wind required locations are inherited from P0038 and documented as the required proxy foundation.

## Test strategy

Add focused unit tests for:

- Robust scale positivity on flat, near-zero and negative input.
- Unsafe ratio handling.
- Exact `D-2..D+4` local window construction.
- AI-1 and AI-2 formulas on deterministic hand fixtures.
- AI-2 day mean of `hour_shape` near zero.
- M2 feature fields present.
- Required P0038 wind locations present.
- No production/API/device path invocation by checking package constants.

Run the package module locally to write tables and evidence, then run `git diff --check` and relevant unit tests.

## Risks and uncertainties

- Weather history coverage may be incomplete near dataset edges. P0041 records row counts and skipped windows instead of imputing price targets.
- M2 normals built over all available rows are feature-foundation normals, not strict holdout baselines. Later AI training packages should define train/validation/holdout leakage policy for model fitting.
- P0041 does not prove future forecast performance; it only validates dataset construction.
