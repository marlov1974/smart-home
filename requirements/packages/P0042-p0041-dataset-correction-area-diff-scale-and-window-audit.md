# Package P0042: P0041 dataset correction — area-diff scale and window audit

## Status

planned

## Package order

P0042

## Primary area

G2 / Mac tooling / spotprice V2 / seven-day index AI dataset correction / area_diff scale / AI-1 skipped-window audit

## Decision summary

P0042 is a correction package that must run before any AI-2 model training.

P0041 successfully created the new seven-day index dataset foundation, but two issues must be resolved first:

```text
1. AI-2 area_diff_proxy_se3 hour_shape has extreme scaled targets.
2. AI-1 skipped_center_dates = 62 must be audited to ensure no artificial year-boundary windows were introduced.
```

P0042 must not train AI-1 or AI-2. It must correct/stabilize the dataset and produce evidence that P0043 can safely train AI-2.

## Background

P0041 made the correct architecture shift:

```text
- M1/M1B/M3/M4 are legacy/diagnostic for the seven-day index track.
- M2A/M2C/M2D remain active signal foundation.
- AI-1 day-to-local-week and AI-2 hour-to-day are the new future models.
```

However P0041 target distributions showed that `area_diff_proxy_se3` is unstable under the initial generic robust scale policy:

```text
AI-2 area_diff_proxy_se3 hour_shape:
  std ≈ 9.28
  p01 = -10
  p05 = -10
  p99 ≈ 32.72
  max = 230
```

This likely happens because `SE3-SE1` is often near zero/flat. When `day_intraday_scale` becomes too small, small spread changes divide by a tiny scale and become huge `hour_shape` values.

P0042 must solve this before model training.

## Scope

P0042 owns:

```text
1. Audit all P0041 AI-1 skipped_center_dates with exact reasons.
2. Verify D-2..D+4 windows can cross calendar-year boundaries.
3. Fix any artificial year-boundary/window-builder issue.
4. Analyze area_diff scale instability.
5. Define and implement a target-series-specific scale policy for SE1 vs SE3-SE1.
6. Rebuild AI-1 and AI-2 datasets after corrections.
7. Reproduce target distributions and prove area_diff targets are trainable.
8. Update evidence and next-training recommendation.
```

P0042 must not train AI models.

## Skipped center-date audit

P0042 must list every skipped AI-1 center date from P0041 and assign an exact reason.

Required reason categories:

```text
dataset_start_boundary
dataset_end_boundary
missing_price_hours
missing_weather_daily
missing_target_series
calendar_year_boundary_bug
dst_or_timezone_issue
other
```

Required evidence:

```text
requirements/package-runs/P0042/skipped-center-date-audit.md
requirements/package-runs/P0042/skipped-center-date-audit.csv or .json
```

The audit must explicitly answer:

```text
Are any center dates skipped only because the D-2..D+4 window crosses a calendar-year boundary?
```

Calendar-year boundaries must not be treated as dataset boundaries.

Valid example:

```text
D = 2024-12-30
local_7d_window = 2024-12-28..2025-01-03
```

This must be valid if all underlying spot/weather rows exist.

If P0041 introduced year-boundary skips, P0042 must fix the window builder and rebuild datasets.

## Area-diff scale problem

P0042 must explain the root cause of extreme `area_diff_proxy_se3` shape targets.

Expected analysis:

```text
area_diff_proxy_se3 = SE3 - SE1
area_diff can be near zero, flat, sign-changing or sparse in daily variation
therefore generic day_intraday_scale can be too small
hour_shape = (hour_price - day_mean_price) / day_intraday_scale explodes when scale is tiny
```

P0042 must produce evidence for:

```text
- distribution of day_intraday_scale for SE1 vs area_diff
- distribution of raw hour centered delta for SE1 vs area_diff
- correlation between tiny scale and extreme hour_shape
- top worst extreme examples before correction
```

Required evidence file:

```text
requirements/package-runs/P0042/area-diff-scale-root-cause.md
```

## Corrected scale policy

P0042 must implement a target-series-specific scale policy.

The generic P0041 scale formula may remain for SE1, but `area_diff_proxy_se3` needs a safer policy.

Required candidate policies to evaluate:

```text
A. current_policy_baseline
B. area_diff_higher_fixed_min_scale
C. area_diff_quantile_floor
D. area_diff_winsorized_target
E. area_diff_clipped_target
F. hybrid selected policy
```

Candidate B example:

```text
SE1 fixed_min_scale = 0.001
area_diff fixed_min_scale = 0.01 or empirically selected floor
```

Candidate C example:

```text
area_diff_min_scale = max(generic_scale, p10_or_p20_of_area_diff_day_scales)
```

Candidate D example:

```text
winsorize hour_shape at p01..p99 or p005..p995
```

Candidate E example:

```text
clip hour_shape to [-10, +10] or another documented symmetric range
```

P0042 must not silently choose clipping just to make the distribution pretty. It must justify the policy by preserving shape information while preventing scale explosions.

Recommended preferred direction:

```text
First fix the denominator/scale floor for area_diff.
Use clipping/winsorization only as a secondary safety guard.
```

## Acceptance criteria for corrected AI-2 area_diff target

P0042 must select a policy that makes `area_diff_proxy_se3` trainable.

Required after-correction criteria:

```text
- all scales strictly positive
- area_diff hour_shape max_abs not dominated by tiny-scale artifacts
- p01 and p99 are not extreme enough to dominate training
- p05/p95 range is reasonably comparable to SE1 or explicitly justified
- symmetric behavior is preferred unless data strongly justifies asymmetry
- top extreme rows are explainable as true spread events or safely bounded
```

Suggested initial quantitative guardrails:

```text
area_diff AI-2 hour_shape:
  abs(p01) <= 10
  abs(p99) <= 10 to 15, or explicitly justified
  max_abs <= 25, or explicitly justified
```

If these guardrails are not achievable without losing real signal, P0042 must STOP/WARN and explain why.

## AI-1 area_diff targets

P0042 must also review AI-1 `area_diff_proxy_se3` targets:

P0041 showed extreme values such as:

```text
day_level_shape min ≈ -37.24
max ≈ 60.0
```

P0042 must apply the same scale-policy thinking to AI-1 area_diff targets:

```text
- day_level_shape
- log_day_scale_index
- log_local_7d_scale
```

Required evidence:

```text
requirements/package-runs/P0042/ai1-area-diff-target-stability.md
```

## Rebuild datasets

After corrections, P0042 must rebuild:

```text
ai1_day_to_local_week_training_targets
ai2_hour_to_day_training_targets
```

and update/recreate the relevant P0041-style evidence under P0042:

```text
requirements/package-runs/P0042/ai1-day-to-local-week-dataset.md
requirements/package-runs/P0042/ai2-hour-to-day-dataset.md
requirements/package-runs/P0042/robust-scale-definitions.md
requirements/package-runs/P0042/target-distributions-before-after.md
requirements/package-runs/P0042/example-rows-before-after.md
```

Do not commit local SQLite databases.

## Required outputs

P0042 must create/update local tables/views or documented equivalents with corrected policy.

Recommended naming:

```text
ai1_day_to_local_week_training_targets_v2
ai2_hour_to_day_training_targets_v2
```

or update the existing views if the repository pattern prefers stable names. Evidence must clearly show which version is used for future P0043 training.

## Tests

Required automated tests:

```text
- D-2..D+4 window builder crosses calendar-year boundaries when rows exist
- skipped center-date reasons are classified
- no center date is skipped solely because it crosses a calendar-year boundary
- area_diff fixed_min_scale/scale floor is target-series-specific
- all SE1 and area_diff scales are strictly positive
- AI-2 area_diff corrected hour_shape distribution satisfies documented guardrails or explains exception
- AI-1 area_diff corrected target distribution is documented
- mean hour_shape by date/target_series remains approximately 0 after correction where mathematically expected
- ratio diagnostics are still null/flagged for unsafe denominators
- no AI model training is performed
- no M5/M6/M7/API/device path is touched
```

## Required evidence files

P0042 must create:

```text
requirements/package-runs/P0042/CHANGELOG.md
requirements/package-runs/P0042/review.md
requirements/package-runs/P0042/design.md
requirements/package-runs/P0042/functions.md
requirements/package-runs/P0042/skipped-center-date-audit.md
requirements/package-runs/P0042/area-diff-scale-root-cause.md
requirements/package-runs/P0042/area-diff-scale-policy-comparison.md
requirements/package-runs/P0042/ai1-area-diff-target-stability.md
requirements/package-runs/P0042/ai1-day-to-local-week-dataset.md
requirements/package-runs/P0042/ai2-hour-to-day-dataset.md
requirements/package-runs/P0042/robust-scale-definitions.md
requirements/package-runs/P0042/target-distributions-before-after.md
requirements/package-runs/P0042/example-rows-before-after.md
requirements/package-runs/P0042/next-model-training-plan.md
requirements/package-runs/P0042/component-attribution-summary.md
```

Optional machine-readable summaries:

```text
requirements/package-runs/P0042/skipped-center-date-audit.json
requirements/package-runs/P0042/scale-policy-comparison.json
requirements/package-runs/P0042/dataset-summary.json
```

## Required answers

P0042 must explicitly answer:

```text
1. Why were 62 center dates skipped in P0041?
2. Were any skipped due to artificial calendar-year boundaries?
3. Did P0042 fix any window-builder issue?
4. What caused the extreme area_diff AI-2 hour_shape values?
5. Which area_diff scale policy was selected and why?
6. What are before/after target distributions for AI-2 area_diff?
7. What are before/after target distributions for AI-1 area_diff?
8. Are corrected targets safe enough for P0043 AI-2 training?
9. Should P0043 train SE1 first, area_diff first, or both?
10. Confirm no AI training, no M5/M6/M7/API/device changes.
```

## Non-goals

- No AI-1 training.
- No AI-2 training.
- No production 7-day forecast API.
- No M5 forecast-time temperature model.
- No M6 forecast API.
- No M7 futures/absolute long-term model.
- No futures/forward ingestion.
- No optimizer/control changes.
- No Shelly runtime changes.
- No Shelly deploy.
- No KVS writes.
- No Home Assistant integration.
- No live device access.

## Expected Codex output

- PASS/WARN/STOP status
- skipped-center-date audit summary
- area_diff root-cause summary
- selected scale policy
- before/after AI-2 area_diff distribution
- before/after AI-1 area_diff distribution
- corrected row counts
- tests run
- files changed
- no AI training confirmation
- no M5/M6/M7/API/device confirmation
- commit SHA after push

## Completion notes

Implemented in commit-ready package run evidence under `requirements/package-runs/P0042/`.

Result: PASS. P0042 added fixed-CET v2 datasets, reduced AI-1 skipped center dates from 62 to 6 dataset-edge windows, removed DST-caused skips, verified `calendar_year_boundary_bug = 0`, selected an area-diff median daily scale floor policy, and wrote corrected v2 local SQLite tables for P0043 AI-2 training. No AI training, M5/M6/M7/API/device path, Shelly, Home Assistant or KVS action was performed.
