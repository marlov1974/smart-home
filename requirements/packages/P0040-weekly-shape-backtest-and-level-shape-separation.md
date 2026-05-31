# Package P0040: Weekly anchored forecast backtest and level/shape separation

## Status

implemented-warn

## Package order

P0040

## Primary area

G2 / Mac tooling / spotprice V2 / anchored weekly forecast backtest / level-shape separation / shape diagnostics

## Decision summary

P0040 evaluates the short-term forecast use case by emulating weekly 7-day forecasts.

The primary metric is **absolute forecast accuracy after level anchoring** from 16 known spot prices, not pure unanchored shape accuracy.

The model stack is still intended to learn price shapes/forms. However, in the short-term use case the general level is supplied by known current spot prices:

```text
At Monday 06:00, the forecaster has the 16 known spot prices for Monday 00:00..15:00.
Those known prices set the general current price level.
The model then distributes/extends that level over the next 7 days using shape, weather and special-day information.
```

Therefore P0040 must test:

```text
Given current anchored price level + holiday calendar + weather forecast proxy + shape model,
how accurate are the absolute hourly prices for the next 7 days?
```

Shape metrics remain required diagnostics because they explain why an anchored absolute forecast succeeds or fails.

P0040 must not build M5, M6/API or M7.

## Why this package exists

Previous packages reported MAE/RMSE in absolute price units without a realistic short-term level anchor. That can be misleading because the shape model should not guess the market level from nothing.

P0040 creates a realistic short-term backtest:

```text
known spot prices set the level;
model shape + weather + special days create the 7-day curve;
absolute forecast accuracy after anchoring is the primary pass/fail evidence;
shape/rank metrics are secondary diagnostics.
```

This separates:

```text
1. level anchoring quality from the 16 known spot hours
2. shape quality over the future horizon
3. final absolute recomposition quality after anchoring
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

This is acceptable because P0040 evaluates the forecast stack and shape logic, not weather-provider forecast error.

## Required model variants

Evaluate at least these variants:

```text
V0 naive_flat_week:
  use 16h anchor level and distribute it flat across the 168h horizon

V1 M1_shape_only:
  M1 shape anchored from known 16 spot hours

V2 M1_plus_existing_M3A_M3B:
  current pre-P0039 M1 + M3A + M3B shape, anchored from known 16 spot hours

V3 M1_plus_M3A_m1b_M3B_m1b:
  P0039 corrected chain using M1 baseplate and M1B-trained M3A/M3B deltas, anchored from known 16 spot hours

V4 M1_plus_M3A_m1b_M3B_m1b_plus_M3D_if_available:
  include useful wind delta if it improves anchored absolute metrics or shape diagnostics

V5 diagnostic_with_M3C:
  include solar delta diagnostic only; do not make default unless it improves anchored absolute metrics or important shape subsets

V6 diagnostic_with_M4_area_diff:
  include area_diff M4 diagnostic only; do not make default unless anchored recomposed SE3 improves
```

If a variant cannot be computed, document why.

## Level anchoring

P0040 must define deterministic level anchoring from the 16 known Monday spot prices.

Required anchoring methods to compare:

```text
anchor_16h_mean:
  calibrate forecast so Monday 00-15 mean equals known Monday 00-15 actual mean

anchor_16h_median:
  calibrate forecast so Monday 00-15 median equals known Monday 00-15 actual median

anchor_16h_robust:
  optional robust calibration using known 16h actual vs model 16h shape
```

Primary anchor:

```text
anchor_16h_mean
```

P0040 must report whether median/robust anchoring is better.

Handle zero/negative prices safely. If multiplicative scaling is unstable, use additive or hybrid anchoring and document the policy.

Suggested hybrid:

```text
if known_mean and model_known_mean are safely positive:
  multiplicative ratio scaling
else:
  additive offset scaling
```

## Primary metrics: anchored absolute forecast accuracy

The primary comparison is the final absolute 168-hour forecast after 16h level anchoring.

Required primary metrics per variant and target:

```text
anchored_absolute_MAE
anchored_absolute_RMSE
anchored_signed_error
anchored_daily_mean_MAE
anchored_weekly_mean_error
p90_weekly_absolute_MAE
best_10_weeks_by_absolute_MAE
worst_10_weeks_by_absolute_MAE
```

Primary user-facing target:

```text
recomposed SE3
```

Also report separately:

```text
SE1 system_proxy
SE3-SE1 area_diff_proxy
```

## Secondary diagnostics: shape metrics

Shape metrics are required diagnostics, not the primary pass/fail metric.

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

Required shape metrics per forecast week:

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
```

Required aggregation:

```text
mean across forecast origins
median across forecast origins
p90 error across forecast origins
best/worst 10 forecast weeks
```

## Level/shape interpretation

P0040 must explicitly classify each variant:

```text
good anchored absolute forecast + good shape
good anchored absolute forecast + weak shape
good shape but weak level anchoring
weak shape and weak anchored absolute forecast
```

Required level metrics:

```text
known_16h_anchor_error
forecast_week_mean_error
daily_mean_error
weekly_mean_error
```

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
  weather/special-day deltas adjust shape and/or absolute deviations
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

## Required subset breakdowns

Report anchored absolute metrics and shape diagnostics by:

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
requirements/package-runs/P0040/anchored-absolute-results.md
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
requirements/package-runs/P0040/anchored-absolute-results.json
requirements/package-runs/P0040/weekly-shape-results.json
requirements/package-runs/P0040/variant-comparison.json
```

Do not commit large prediction dumps.

## Required answers

P0040 must explicitly answer:

```text
1. Which variant has the best anchored absolute 7-day forecast?
2. Which 16h level anchoring method works best?
3. How much absolute error remains after level anchoring?
4. Which variant has the best weekly shape independent of absolute level?
5. Which variant best identifies expensive hours?
6. Which variant best identifies cheap hours?
7. Does P0039 M1B-trained M3A/M3B improve anchored absolute forecast vs existing M3A/M3B?
8. Does M3D improve anchored absolute forecast, shape, or only a subset?
9. Does M3C help any solar/daylight subset?
10. Does M4_area_diff help anchored absolute recomposed SE3 even if prior full-year absolute MAE was weak?
11. Is the model stack ready for short-term 7-day forecast design, or what is missing?
```

## Tests

Required tests:

```text
- forecast origins are Mondays at 06:00 local time
- each origin has exactly 16 known spot hours Monday 00-15 or is skipped with reason
- horizon is 168 hours per complete forecast week
- future forecast-horizon spot prices are not used as features
- known 16h spot prices are used only for anchoring/calibration
- actual weather is marked as forecast proxy/oracle
- recomposed SE3 = SE1 + area_diff
- anchored absolute metrics are computed after level anchoring
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
- anchored absolute forecast winner
- remaining absolute MAE/RMSE after anchoring
- weekly shape metric winner
- top/bottom hour winner
- whether M3A/M3B_m1b improves anchored forecast
- whether M3C/M3D/M4_area_diff improve anchored forecast or shape diagnostics
- short-term 7-day forecast design conclusion
- long-term futures-shape design note
- tests run
- files changed
- no M5/M6/M7/API/device confirmation
- commit SHA after push

## Completion notes

Implemented as Mac-side diagnostics and evidence.

P0040 ran a strict static pre-backtest component fit and evaluated 50 Monday-origin 7-day forecasts:

```text
backtest_start = 2025-06-02
backtest_end = 2026-05-18
forecast_origin_count = 50
known_spot_context = Monday 00:00..15:00
horizon = 168 hours
weather_oracle = actual_weather_used_as_forecast_proxy
```

Status is `WARN`: the best anchored absolute recomposed SE3 forecast was the simple `V0_naive_flat_week` with `anchor_16h_mean`:

```text
V0 anchor_16h_mean recomposed SE3 MAE = 0.333955
V2 existing M3A/M3B recomposed SE3 MAE = 0.365197
V3 M1B-trained M3A/M3B recomposed SE3 MAE = 0.364194
V4 M3D diagnostic recomposed SE3 MAE = 0.353274
```

P0039 M1B-trained M3A/M3B improves slightly versus existing M3A/M3B after anchoring, and M3D improves further, but the component shape stack does not beat the flat anchored baseline on absolute MAE. P0040 therefore does not justify production short-term API work yet.

No M5/M6/M7/API, Shelly, Home Assistant, KVS or device action was performed.
