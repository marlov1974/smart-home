# Package P0040: Weekly shape backtest and level/shape separation

## Status

planned

## Package order

P0040

## Primary area

G2 / Mac tooling / spotprice V2 / shape-first evaluation / weekly forecast backtest / level-shape separation

## Decision summary

P0040 changes the primary evaluation target for the spotprice V2 model stack from absolute-price accuracy to shape accuracy.

The model stack is intended to learn price shapes/forms, not final absolute market levels. Absolute levels will later be supplied by:

```text
short-term mode:
  known latest spot prices + current level anchoring + weather forecast + special-day calendar

long-term mode:
  futures/forward curves + shape allocation + special-day/weather-normal adjustments
```

Historical futures are not available, so P0040 must test the short-term use case by emulating weekly forecasts.

Primary backtest scenario:

```text
At Monday 06:00, the forecaster has 16 known spot prices for the current day.
It also knows the coming special days/holidays.
Actual weather is used as proxy for weather forecast.
The system predicts the price shape for the next 7 days.
```

P0040 must not build M5, M6/API or M7.

## Why this package exists

Previous packages reported MAE/RMSE in absolute price units. That is useful but insufficient and partly misleading because absolute price level is not the core purpose of M1/M3/M4 shape models.

A shape model can be useful even when absolute level is wrong, if it correctly identifies:

```text
- expensive and cheap hours
- daily shape
- weekly shape
- holiday shape deviations
- weather-adjusted shape deviations
- relative allocation of a known level across hours
```

P0040 must therefore separate:

```text
shape quality
level anchoring quality
absolute recomposition quality
```

## Primary holdout/backtest period

Use a one-year rolling weekly backtest:

```text
primary_backtest_start = 2025-06-01
primary_backtest_end   = 2026-06-01 or latest available complete week if 2026-06-01 is unavailable
```

If available data does not reach 2026-06-01, use:

```text
2025-06-01..latest complete Monday-start week
```

and document the exact range.

Every eligible forecast origin:

```text
weekday = Monday
local_time = 06:00
forecast_horizon = 7 days / 168 hours
known_spot_context = current Monday 00:00..15:00, 16 hours
```

If Monday 00:00..15:00 is unavailable for an origin, skip that origin and document it.

## Forecast emulation assumptions

For each Monday 06 forecast origin, P0040 may use:

```text
- 16 known spot prices for Monday 00:00..15:00
- special-day calendar for the forecast week
- actual historical weather as proxy for weather forecast
- model artifacts/features available before the forecast origin in strict mode where practical
```

P0040 must not use future actual spot prices from the forecast horizon except for evaluation.

Actual weather may be used as weather-forecast proxy and must be labeled:

```text
weather_oracle = actual_weather_used_as_forecast_proxy
```

This is acceptable because P0040 evaluates shape logic, not weather forecast provider accuracy.

## Required model variants

Evaluate at least these variants:

```text
V0 naive_flat_week:
  distribute anchored weekly/daily level flat across hours

V1 M1_shape_only:
  M1 shape with level anchoring from known 16 spot hours

V2 M1_plus_existing_M3A_M3B:
  current pre-P0039 M1 + M3A + M3B shape

V3 M1_plus_M3A_m1b_M3B_m1b:
  P0039 corrected chain using M1 baseplate and M1B-trained M3A/M3B deltas

V4 M1_plus_M3A_m1b_M3B_m1b_plus_M3D_if_available:
  include useful wind delta if it improves shape metrics

V5 diagnostic_with_M3C:
  include solar delta diagnostic only; do not make default unless it improves shape metrics

V6 diagnostic_with_M4_area_diff:
  include area_diff M4 diagnostic only; do not make default unless recomposed SE3 shape improves
```

If a variant cannot be computed, document why.

## Level anchoring

P0040 must define deterministic level anchoring from the 16 known Monday spot prices.

Required anchoring methods to compare:

```text
anchor_16h_mean:
  scale forecast shape so Monday 00-15 mean equals known Monday 00-15 actual mean

anchor_16h_median:
  scale forecast shape so Monday 00-15 median equals known Monday 00-15 actual median

anchor_16h_regression_or_ratio_safe:
  optional robust calibration using known 16h actual vs model 16h shape
```

The primary anchor should initially be:

```text
anchor_16h_mean
```

but P0040 must report whether median/robust anchoring is better.

Handle zero/negative prices safely. If multiplicative scaling is unstable, use an additive or hybrid anchor and document the policy.

Suggested hybrid:

```text
if known_mean and model_known_mean are safely positive:
  multiplicative ratio scaling
else:
  additive offset scaling
```

## Shape metrics

Absolute MAE/RMSE must remain secondary. Primary metrics must be shape metrics.

Required shape normalization scopes:

```text
daily_index:
  price / daily_mean or price - daily_mean, with safe handling for near-zero/negative means

weekly_index:
  price / weekly_mean or price - weekly_mean, with safe handling

monthly_index if horizon crosses month:
  optional diagnostic
```

Because Nordic spot prices can be zero or negative, P0040 must implement safe index definitions.

Required safe shape representations:

```text
centered_shape:
  price - period_mean

scaled_centered_shape:
  (price - period_mean) / robust_period_scale

rank_shape:
  rank of each hour within day/week
```

Do not rely only on ratio indices when means can be near zero or negative.

Required metrics per forecast week:

```text
weekly_centered_shape_MAE
weekly_centered_shape_RMSE
weekly_scaled_shape_MAE
weekly_rank_spearman
weekly_top_10pct_precision
weekly_bottom_10pct_precision
daily_centered_shape_MAE
daily_rank_spearman_mean
daily_top_3h_hit_rate
daily_bottom_3h_hit_rate
expensive_hour_recall
cheap_hour_recall
absolute_MAE_secondary
absolute_RMSE_secondary
signed_error_secondary
```

Required aggregation:

```text
mean across forecast origins
median across forecast origins
p90 error across forecast origins
best/worst 10 forecast weeks
```

## Level metrics

Separate level quality from shape quality.

Required level metrics:

```text
known_16h_anchor_error
forecast_week_mean_error
daily_mean_error
weekly_mean_error
absolute_MAE_after_anchor
```

P0040 must explicitly say whether a variant has good shape but poor level, or poor shape but good level.

## Short-term forecast interpretation

P0040 must produce a design note for future short-term forecast mode:

```text
Input:
  known spot prices for nearest available day/hours
  weather forecast
  special-day calendar
  current active shape model

Output:
  7-day hourly absolute forecast

Mechanism:
  shape model creates relative curve
  known spot context anchors level
  weather/special-day deltas adjust shape
```

This is design/evaluation only. Do not build production API in P0040.

## Long-term/futures interpretation

P0040 must also produce a design note for future futures mode:

```text
Input:
  futures/forward levels by year/quarter/month/week when available
  normal/specified weather assumption
  special-day calendar
  shape model

Output:
  hourly allocated expected spot cost
```

Historical futures are unavailable, so P0040 must not claim futures backtest results.

## Strict leakage controls

For each Monday-origin backtest, do not train on forecast horizon actual spot rows in strict evidence.

Minimum acceptable strictness:

```text
- use model artifacts/features whose fit period ends before the forecast origin, or
- if using precomputed package models, clearly label result as diagnostic/non-strict
```

Preferred strict implementation:

```text
rolling-origin or expanding-window fit/update for M1/M1B/M3A/M3B and optional M3D
```

If rolling refit is too expensive for P0040, Codex may implement:

```text
static model diagnostic mode
```

but must label it and not use it for PASS unless leakage is controlled.

## Targets

Evaluate separately:

```text
SE1 system_proxy
SE3-SE1 area_diff_proxy
recomposed SE3
```

Primary user-facing target:

```text
recomposed SE3
```

## Required subset breakdowns

Report shape metrics by:

```text
all forecast weeks
holiday weeks
non-holiday weeks
weeks with bridge days
weeks with major social holidays
cold weeks
warm weeks
high-wind weeks
low-wind weeks
high-solar weeks
low-solar weeks
summer weeks
winter weeks
```

Use actual weather as proxy to classify weather subsets.

## Required evidence files

P0040 must create:

```text
requirements/package-runs/P0040/CHANGELOG.md
requirements/package-runs/P0040/review.md
requirements/package-runs/P0040/design.md
requirements/package-runs/P0040/functions.md
requirements/package-runs/P0040/weekly-backtest-method.md
requirements/package-runs/P0040/level-shape-separation.md
requirements/package-runs/P0040/shape-metrics-definition.md
requirements/package-runs/P0040/weekly-shape-results.md
requirements/package-runs/P0040/level-anchor-results.md
requirements/package-runs/P0040/variant-comparison.md
requirements/package-runs/P0040/best-worst-weeks.md
requirements/package-runs/P0040/short-term-forecast-design.md
requirements/package-runs/P0040/long-term-futures-shape-design.md
requirements/package-runs/P0040/component-attribution-summary.md
```

Optional machine-readable summaries:

```text
requirements/package-runs/P0040/weekly-shape-results.json
requirements/package-runs/P0040/variant-comparison.json
```

Do not commit large prediction dumps.

## Required answers

P0040 must explicitly answer:

```text
1. Which variant has the best weekly shape, independent of absolute level?
2. Which variant best identifies expensive hours?
3. Which variant best identifies cheap hours?
4. Does P0039 M1B-trained M3A/M3B improve shape vs existing M3A/M3B?
5. Does M3D improve shape, or only absolute level?
6. Does M3C help any solar/daylight subset, despite weak absolute MAE in P0038?
7. Does M4_area_diff help shape even if it hurts absolute recomposed SE3 MAE?
8. Which level anchoring method works best from 16 known Monday spot prices?
9. How much of absolute error remains after level anchoring?
10. Is the model stack ready for short-term 7-day forecast design, or what is missing?
```

## Tests

Required tests:

```text
- forecast origins are Mondays at 06:00 local time
- each origin has exactly 16 known spot hours Monday 00-15 or is skipped with reason
- horizon is 168 hours per complete forecast week
- future forecast-horizon spot prices are not used as features
- actual weather is marked as forecast proxy/oracle
- recomposed SE3 = SE1 + area_diff
- centered shape metrics are invariant to additive level shifts
- scaled/rank metrics handle zero/negative prices safely
- top/bottom hour metrics are computed from horizon actuals only for evaluation
- all variants use same forecast origin set for comparison
- no M5/M6/M7/API/device path is touched
```

## Non-goals

- No M5 forecast-time temperature model.
- No M6 forecast API.
- No M7 futures/absolute long-term model.
- No futures/forward ingestion.
- No production forecast endpoint.
- No optimizer/control changes.
- No Shelly runtime changes.
- No Shelly deploy.
- No KVS writes.
- No Home Assistant integration.
- No live device access.

## Expected Codex output

- PASS/WARN/STOP status
- exact backtest period and forecast origin count
- skipped origins and reasons
- level anchoring methods tested
- weekly shape metric winner
- top/bottom hour winner
- absolute metric secondary results
- whether M3A/M3B_m1b improves shape
- whether M3C/M3D/M4_area_diff improve shape
- short-term 7-day forecast design conclusion
- long-term futures-shape design note
- tests run
- files changed
- no M5/M6/M7/API/device confirmation
- commit SHA after push

## Completion notes

To be filled after implementation.
