# P0053C-B Implementation Design

Package interpretation:

P0053C-B should turn the P0053C-A M4 centered SE1 shape/index into leakage-safe anchored absolute SE1 prices for rolling 168h forecast origins. The anchor is based only on actual SE1 prices from the 48 hours strictly before each forecast origin.

Implementation structure:

- Add `src/mac/services/spotprice_model_diagnostics/p0053cb.py`.
- Reuse P0045 model regeneration and P0053C-A global split window construction.
- Restrict canonical anchored output to `system_proxy_se1`.
- Validate the predecessor P0053C-A shape log exists and is shape/index only.
- Build validation and holdout rolling windows where every target row belongs to the same P0053C split.
- Use the selected P0053C-A/P0045 formula for SE1 shape generation, expected `combined_scaled`.
- Load actual SE1 prices from `ai2_hour_to_day_training_targets_v2`.
- Evaluate A0-A3 anchor candidates and forecast-safe baselines.
- Select the anchor method only from validation metrics.
- Persist selected validation and holdout rows to `m4_48h_anchored_absolute_price_forecast_log_p0053cb_v1`.
- Write package-run evidence and compact JSON/CSV artifacts.

Forecast-origin interpretation:

For each 168h rolling window, `forecast_origin_timestamp_utc` is the first target timestamp in that 168h path. This makes horizons `0..167` and keeps the anchor history strictly before the first target row.

Anchor formulas:

- A0: mean(hist48) plus centered shape multiplied by population std(hist48).
- A1: median(hist48) plus centered shape multiplied by IQR-derived robust scale, `IQR / 1.349`.
- A2: `0.5 * mean(last24) + 0.5 * mean(hist48)` plus centered shape multiplied by IQR-derived robust scale.
- A3: target-hour level from same fixed-CET hour over previous 48h, plus centered shape multiplied by IQR-derived robust scale.

Deliberate refactoring decisions:

- Keep P0053C-B as an additive diagnostics module rather than mutating P0053C-A or P0045.
- Do not add abstractions to shared model code unless needed for this package.
- Use local helper functions for anchor metrics, leakage checks and evidence writing because they are package-specific.

Test strategy:

- Run the P0053C-B module end to end.
- Verify the persisted table exists, has rows, required columns and only `prediction_kind=anchored_absolute_price`.
- Verify anchor timestamps are strictly before origin, origin is not after target, cutoff is not after origin and horizons are 0..167.
- Run focused unit tests or repository unit tests covering the diagnostics module.
- Run `git diff --check`.

Risks and uncertainties:

- Absolute price anchoring may or may not improve over forecast-safe flat/history baselines. The package outcome should report metrics rather than force PASS from performance alone.
- The P0053C-A persisted log is holdout-only, so validation shape rows must be regenerated rather than read from that local table.
- Forecasted price unit is inherited from `hour_price`; current source appears to be the local historical SE1 price unit used by prior P0043/P0044/P0045 diagnostics.
