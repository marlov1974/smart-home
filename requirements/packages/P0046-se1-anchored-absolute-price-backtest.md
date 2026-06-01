# Package P0046: SE1 anchored absolute-price backtest

## Status

planned

## Package order

P0046

## Primary area

G2 / Mac tooling / spotprice V2 / seven-day forecast / anchored absolute-price backtest / SE1 first

## Decision summary

P0046 is the first anchored absolute-price backtest for the new seven-day AI forecast track.

P0045 proved that the combined AI-1 + AI-2 168h shape forecast is useful for `system_proxy_se1` and weaker/less stable for `area_diff_proxy_se3`.

P0046 must therefore proceed **SE1 first**:

```text
primary target:
  system_proxy_se1 anchored absolute-price backtest

secondary diagnostics:
  area_diff_proxy_se3 only as diagnostic/fallback-constrained
  optional recomposed SE3 only as diagnostic
```

P0046 must not build a production API. It must emulate historical forecast situations and evaluate whether the P0045 168h shape curve can be anchored to known spot hours to create useful absolute price forecasts.

## Preconditions

P0046 may start only after P0042, P0043, P0044 and P0045 evidence exists.

Required facts:

```text
P0042:
  corrected fixed-CET datasets exist
  timestamp_utc remains primary truth
  model_cet_date/hour are used
  area_diff scale policy corrected

P0043:
  AI-2 trained/evaluated on corrected fixed-CET dataset

P0044:
  AI-1 trained/evaluated on corrected fixed-CET dataset
  weak area_diff scale targets flagged for fallback

P0045:
  selected deployable formula for SE1 = combined_scaled
  SE1 combined shape has useful rank/intraday metrics
  area_diff should remain diagnostic or fallback-constrained
```

P0046 must STOP if it cannot use the P0045 selected SE1 shape forecast path.

## Scope

P0046 owns:

```text
1. Build an anchored absolute-price backtest harness.
2. Use P0045 SE1 168h shape forecast as the primary shape input.
3. Emulate forecast origins with known spot anchor hours.
4. Fit only anchoring parameters from known anchor hours.
5. Forecast absolute prices for the remaining horizon.
6. Evaluate absolute and shape/rank/optimization-oriented metrics.
7. Compare against anchored baselines.
8. Decide whether P0047 can build a forecast-service/API prototype.
```

P0046 must not:

```text
- retrain AI-1
- retrain AI-2
- build production API
- build optimizer/control integration
- touch Shelly/Home Assistant/KVS/devices
```

## Forecast-origin policy

P0046 must emulate realistic seven-day forecasts.

Primary forecast origin:

```text
forecast_origin = Monday 06:00 fixed-CET model time
horizon = 168 hours from forecast_origin
```

Reason:

```text
The intended product use case is a rolling 7-day forecast where some spot hours are already known and can anchor the general price level/scale.
```

P0046 may also test diagnostic origins:

```text
- every day 06:00
- fixed-CET day 00:00
```

but Monday 06:00 must be the primary reported scenario unless data coverage makes it impossible.

## Anchor-hour policy

P0046 must test multiple anchor-hour scenarios.

Required scenarios:

```text
A11 = first 11 known spot hours from forecast origin
A16 = first 16 known spot hours from forecast origin
A24 = first 24 known spot hours from forecast origin
A35 = first 35 known spot hours from forecast origin
```

If forecast origin is Monday 06:00, then A16 roughly represents known hours through part of the same/next published day depending on publication assumptions. P0046 must document the exact historical emulation rule used.

Anchor hours are allowed to use actual historical prices because this is a backtest emulating information that would have been known at forecast time.

No future prices beyond the selected anchor hours may be used for anchoring.

## Anchoring model

P0046 must test simple deterministic anchoring first.

Given:

```text
shape[h] = P0045 centered 168h shape forecast
actual_anchor[h] = known historical price for anchor hours
```

Test at least these anchoring methods:

### Anchor L1: level-only

```text
forecast[h] = shape[h] + level
level = mean(actual_anchor - shape_anchor)
```

### Anchor L2: level + robust scale

```text
forecast[h] = level + scale * shape[h]
```

where `level` and `scale` are fitted on anchor hours only using robust regression or robust closed-form logic.

Required guardrails:

```text
scale must be finite
scale must be positive unless explicitly justified
scale must be clipped to a documented sane range
```

### Anchor L3: level + scale with shrinkage

```text
scale = shrink(anchor_scale_estimate, long_run_scale_prior, weight_by_anchor_count)
```

This is expected to be more stable for A11/A16.

P0046 must document exact formulas.

Do not use complex learned anchoring in P0046 unless it is clearly separated as diagnostic. Preferred first version: deterministic formulas only.

## Targets and evaluation horizon

For each forecast window and anchor scenario, evaluate:

```text
known anchor hours:
  used only for anchoring fit diagnostics

forecast evaluation hours:
  horizon hours excluding anchor hours
```

Primary evaluation must exclude anchor hours from error metrics to avoid measuring fitted points.

P0046 may report in-sample anchor fit diagnostics separately.

## Primary target series

Primary:

```text
system_proxy_se1
```

Secondary diagnostics:

```text
area_diff_proxy_se3 anchored backtest with constrained/fallback policy
recomposed_se3 = system_proxy_se1 + area_diff_proxy_se3
```

Area_diff/recomposed diagnostics must not block SE1 progress unless they reveal a critical architecture issue.

## Baselines

P0046 must compare against anchored baselines.

Required SE1 baselines:

```text
B0_anchor_flat:
  forecast all future hours as mean(anchor_prices)

B1_anchor_last_known:
  forecast all future hours as last anchor price

B2_anchor_time_profile:
  train-only fixed-CET weekday/hour shape profile anchored with same anchoring method

B3_P0045_AI1_only_anchor:
  AI1-only shape from P0045 anchored with same method

B4_P0045_AI2_only_anchor:
  AI2-only shape from P0045 anchored with same method

B5_oracle_anchor_upper_bound:
  diagnostic only; may use actual future shape/scale but must be labeled oracle/not deployable
```

Oracle baselines must be excluded from deployable model selection.

## Metrics

Evaluate by anchor scenario and forecast window.

Primary absolute-price metrics:

```text
MAE
RMSE
median_absolute_error
mean_signed_error
p90_absolute_error
p95_absolute_error
```

Shape/rank metrics on evaluation hours:

```text
spearman_rank
kendall_tau if available
top_10_percent_hit_rate
bottom_10_percent_hit_rate
top_20h_precision
bottom_20h_precision
best_8h_hit_rate
worst_8h_hit_rate
```

Optimization-oriented metrics:

```text
cheap_hour_capture_rate
expensive_hour_avoidance_rate
regret_vs_perfect_top_N_selection
regret_vs_anchor_flat_top_N_selection
```

Daily metrics:

```text
daily_mean_MAE
daily_peak_hour_error
daily_low_hour_error
day_rank_spearman
```

Subset diagnostics:

```text
normal_week_subset
holiday_week_subset
bridge_day_week_subset
summer_subset
winter_subset
high_solar_week_subset
low_wind_week_subset
high_wind_week_subset
high_temp_delta_week_subset
low_temp_delta_week_subset
negative_price_windows
near_zero_price_windows
high_volatility_windows
```

## Chronological backtest

P0046 must use chronological backtest windows consistent with prior packages.

Required:

```text
validation: 2025 forecast-origin windows
holdout: 2026 forecast-origin windows
```

P0046 must not use 2026 holdout windows to tune anchoring choices, except to report final results. If selecting among anchoring methods, selection should be based on validation first and holdout reported after.

## Selection policy

P0046 must select one deployable SE1 anchoring configuration based on validation and confirm on holdout.

Selection criteria should prioritize:

```text
1. robust MAE/RMSE improvement vs B0_anchor_flat
2. rank/top-bottom improvement vs B0_anchor_flat
3. stable behavior across A11/A16/A24/A35
4. no severe p95 error regression
5. no leakage
```

P0046 may recommend different anchor method by anchor count only if evidence is clear.

## Required evidence files

P0046 must create:

```text
requirements/package-runs/P0046/CHANGELOG.md
requirements/package-runs/P0046/review.md
requirements/package-runs/P0046/design.md
requirements/package-runs/P0046/functions.md
requirements/package-runs/P0046/dataset-contract.md
requirements/package-runs/P0046/forecast-origin-policy.md
requirements/package-runs/P0046/anchor-hour-policy.md
requirements/package-runs/P0046/anchoring-formulas.md
requirements/package-runs/P0046/baselines.md
requirements/package-runs/P0046/se1-validation-results.md
requirements/package-runs/P0046/se1-holdout-results.md
requirements/package-runs/P0046/anchor-scenario-comparison.md
requirements/package-runs/P0046/rank-and-top-bottom-results.md
requirements/package-runs/P0046/optimization-oriented-results.md
requirements/package-runs/P0046/daily-results.md
requirements/package-runs/P0046/subset-results.md
requirements/package-runs/P0046/best-worst-windows.md
requirements/package-runs/P0046/area-diff-diagnostics.md
requirements/package-runs/P0046/recomposed-se3-diagnostics.md
requirements/package-runs/P0046/oracle-diagnostics.md
requirements/package-runs/P0046/next-api-prototype-plan.md
requirements/package-runs/P0046/component-attribution-summary.md
```

Optional machine-readable evidence:

```text
requirements/package-runs/P0046/metrics-summary.json
requirements/package-runs/P0046/window-results.json
requirements/package-runs/P0046/anchor-scenario-comparison.json
requirements/package-runs/P0046/best-worst-windows.json
```

## Required answers

P0046 must explicitly answer:

```text
1. Which P0045 SE1 shape source/formula was used?
2. Which forecast-origin policy was used?
3. Which anchor scenarios were tested?
4. Which anchoring formula was selected and why?
5. Does anchored SE1 beat B0_anchor_flat on validation?
6. Does anchored SE1 beat B0_anchor_flat on holdout?
7. Does anchored SE1 beat B2 anchored time-profile baseline?
8. Does anchored SE1 beat AI1-only and AI2-only anchored baselines?
9. Which anchor count is sufficient: 11, 16, 24 or 35?
10. Are rank/top-bottom metrics still useful after anchoring?
11. Which windows fail worst and why?
12. Should P0047 build an API prototype for SE1 only?
13. What should happen with area_diff/recomposed SE3 next?
14. Confirm no production API, no AI retraining, no M5/M6/M7, no device actions.
```

## Tests

Required automated tests:

```text
- P0046 uses P0045 selected SE1 shape source
- forecast windows are exactly 168 hours
- anchor scenarios use only the first N anchor hours
- evaluation metrics exclude anchor hours
- no future prices beyond anchor hours are used for anchoring
- anchoring formulas return finite forecasts
- scale anchoring guardrails are enforced
- chronological validation/holdout separation is preserved
- oracle diagnostics are labeled and excluded from deployable selection
- area_diff/recomposed SE3 diagnostics do not override SE1-first decision
- no AI-1/AI-2 retraining is performed
- no production API is created
- no M5/M6/M7/API/device path is touched
```

## Pass/fail interpretation

PASS requires:

```text
- SE1 anchored forecast beats B0_anchor_flat on at least one primary absolute metric on validation and does not materially regress on holdout.
- SE1 anchored forecast materially improves rank/top-bottom or optimization-oriented metrics vs B0_anchor_flat.
- Selected anchoring method is stable for at least one practical anchor count, preferably A16 or A24.
- No leakage.
- Evidence clearly states whether P0047 should build an SE1 API prototype.
```

WARN is acceptable if:

```text
- absolute MAE improvement is small but rank/optimization metrics improve.
- A11 is unstable but A16/A24/A35 are useful.
- SE1 works but area_diff/recomposed SE3 remains diagnostic only.
- P0047 should build API prototype with feature flags and SE1-only limitation.
```

STOP if:

```text
- anchored SE1 cannot beat flat anchor baseline on validation or holdout.
- leakage is detected.
- scale anchoring creates unstable/non-finite forecasts.
- production API/device integration is accidentally built.
```

## Non-goals

- No production forecast API.
- No live API endpoint.
- No Home Assistant integration.
- No Shelly runtime changes.
- No Shelly deploy.
- No KVS writes.
- No optimizer/control changes.
- No AI-1 retraining.
- No AI-2 retraining.
- No M5 forecast-time temperature model.
- No M6 forecast API.
- No M7 futures/absolute long-term model.
- No futures/forward ingestion.
- No live device access.

## Expected Codex output

- PASS/WARN/STOP status
- P0045 shape source used
- forecast-origin policy
- anchor scenarios tested
- anchoring formulas tested
- selected anchoring method
- SE1 validation and holdout results
- SE1 baseline comparisons
- rank/top-bottom and optimization-oriented results
- best/worst windows
- area_diff/recomposed SE3 diagnostic summary
- recommendation for P0047
- tests run
- files changed
- no AI retraining / no production API / no device confirmation
- commit SHA after push

## Completion notes

To be filled after implementation.
