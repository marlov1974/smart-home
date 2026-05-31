# Package P0035: Special-day calendar, M3A/M3B normalization and residual M4

## Status

planned

## Package order

P0035

## Primary area

G2 / Mac tooling / spotprice V2 / Swedish special-day calendar / holiday normalization / M4 residual model

## Decision summary

P0035 must correct the P0034 modeling direction by adding an explicit Swedish special-day calendar and splitting normalization into:

```text
M3A: extraordinary-temperature delta normalization
M3B: special-day / holiday / bridge-day delta normalization
```

Then M4 must be rebuilt as an M1-anchored residual ML model:

```text
M4 target residual = actual_price - M3A_temp_delta - M3B_special_day_delta - M1_normal_price
M4 prediction = M1_normal_price + M4_residual_prediction
```

For evaluation against actual observed or temperature-normalized targets, special-day effects must be added back as the final evaluation step where applicable:

```text
recomposed_prediction = M1 + M4_residual + M3B_special_day_delta
```

P0035 must not build M5 forecast-time temperature model, M6 API or M7 futures model.

## Important renames

Rename current P0033 `M3` terminology to:

```text
M3A = extraordinary-temperature delta model
```

Create new:

```text
M3B = special-day delta model
```

This is a terminology and schema/model-pipeline change. Backwards-compatible views/aliases may be kept, but docs and new evidence must use M3A/M3B.

## Scope

P0035 contains five coordinated changes:

```text
1. Generate and commit a deterministic Swedish special-day calendar for 2022-01-01..2035-12-31.
2. Improve M2 normal climate model to use smooth sin/cos/cyclic seasonal normals, not sharp week artifacts.
3. Rename M3 to M3A and keep it focused on extraordinary temperature deltas.
4. Add M3B special-day delta normalization using the generated calendar.
5. Rebuild M4 as an M1-anchored residual ML model with better model class and correct evaluation/recomposition.
```

## P0035-1: Swedish special-day calendar 2022-2035

P0035 must generate all dates from:

```text
2022-01-01..2035-12-31
```

This is a deterministic one-time generation job best solved by ChatGPT/Codex logic and committed to repo.

Expected row count:

```text
14 * 365 + leap days in 2022..2035
= 5110 + 4
= 5114 rows
```

Leap years included:

```text
2024
2028
2032
2036 not included
```

Required committed data file:

```text
data/calendar/se_special_days_2022_2035.csv
```

Optional committed JSON mirror:

```text
data/calendar/se_special_days_2022_2035.json
```

Required docs:

```text
docs/functions/mac/swedish-special-day-calendar.md
```

### Calendar schema

CSV must include at least:

```text
date
year
month
day
weekday
weekday_name
iso_year
iso_week
iso_weekday
day_of_year
is_leap_day
base_day_type
special_day_type
special_day_name
special_day_group
holiday_strength
is_public_holiday
is_fixed_date_holiday
is_movable_holiday
is_major_social_holiday
is_holiday_eve
is_bridge_day
bridge_strength
bridge_direction
bridge_anchor
is_holiday_period_day
period_name
period_day_index
is_pre_holiday_transition
is_post_holiday_recovery
normal_weekday_override
notes
```

If Codex chooses additional useful fields, document them.

### Base day types

Every date must have one of:

```text
normal_weekday
normal_saturday
normal_sunday
```

Special classifications then overlay the base day.

### Fixed-date public holidays

Classify:

```text
new_years_day        1 January
 epiphany            6 January
first_may            1 May
national_day         6 June
christmas_day        25 December
boxing_day           26 December
```

These are fixed-date public holidays but change weekday by year. Weekday interaction matters for later M3B.

### Major social holidays / eves

Classify even when not formal public holidays:

```text
christmas_eve        24 December
new_years_eve        31 December
midsummer_eve        Friday between 19 and 25 June
midsummer_day        Saturday between 20 and 26 June
```

Midsummer Day must be classified as:

```text
major_social_holiday
normal_weekend_override = true
```

Rationale: Midsummer Day is not an ordinary Saturday. Cities are unusually empty, many businesses are closed, and household/load behavior is materially different from a normal Saturday.

### Movable holidays and periods

Compute Easter using a deterministic Gregorian Easter algorithm.

Classify:

```text
maundy_thursday      Thursday before Easter Sunday
 good_friday         Friday before Easter Sunday
 easter_saturday     Saturday before Easter Sunday
 easter_sunday       Easter Sunday
 easter_monday       Monday after Easter Sunday
ascension_day        Easter Sunday + 39 days, always Thursday
friday_after_ascension = strong bridge day
pentecost_sunday     Easter Sunday + 49 days
midsummer_eve        Friday 19-25 June
midsummer_day        Saturday 20-26 June
midsummer_sunday     Sunday after Midsummer Day
all_saints_day       Saturday between 31 October and 6 November
all_saints_friday    Friday before All Saints Day, weak/medium transition
```

### Christmas / New Year period

Classify as period, not only individual holidays:

```text
23 December          pre_holiday_transition_day
24 December          major_social_holiday
25 December          fixed_public_holiday, major
26 December          fixed_public_holiday, major
27-30 December       holiday_period_day / bridge depending on weekday
31 December          major_social_holiday
1 January            fixed_public_holiday, major
```

The exact period representation must be documented.

### Bridge-day rules

P0035 must implement bridge-day classification. Starting policy:

```text
If a public holiday occurs on Tuesday:
  Monday before = bridge_day_strong

If a public holiday occurs on Thursday:
  Friday after = bridge_day_strong

If a public holiday occurs on Wednesday:
  Thursday after = bridge_day_weak
  Friday after = bridge_day_weak

If a public holiday occurs on Monday:
  Friday before may be weak pre-holiday transition, not strong bridge day by default.
```

Hard rule:

```text
Friday after Ascension Day = bridge_day_strong
```

Bridge days must preserve their anchor holiday in `bridge_anchor`.

### Special-day categories

Use stable category names such as:

```text
fixed_public_holiday
movable_public_holiday
major_social_holiday
holiday_eve
bridge_day_strong
bridge_day_weak
holiday_period_day
pre_holiday_transition_day
post_holiday_recovery_day
special_weekend_day
```

P0035 must define precedence rules when one date qualifies for multiple categories.

## P0035-2: M2 smooth cyclic climate normals

M2 must be reviewed and, if needed, updated so climate normals are based on smooth cyclic seasonal movement rather than sharp week/bucket artifacts.

Design intent:

```text
M2 should see smooth movement over the year.
If week 8 happened to be colder than week 7 in a couple of years, that is mostly noise, not a durable trend.
```

Required behavior:

- Use sin/cos or equivalent cyclic seasonal representation where appropriate.
- Smooth across day-of-year/hour calendar positions.
- Do not condition on year.
- Do not create sharp week-specific normal temperature artifacts.
- Keep or extend `bucket_year_count` diagnostics.
- Document before/after M2 anomaly distribution.

Allowed approaches:

```text
sin/cos regression/basis using Python stdlib
smoothed cyclic day-of-year/hour median with broad window
hybrid calendar-bucket + cyclic smoothing
```

No external dependency required unless Codex stops for explicit approval.

## P0035-3: M3A extraordinary-temperature delta

Current P0033 M3 must be renamed/conceptually split to M3A.

M3A purpose:

```text
Estimate price deltas from extraordinary temperature anomalies only.
```

M3A must stay conservative and must not learn ordinary seasonality or normal winter/summer effects.

M3A inputs:

```text
M1 residuals
M2 smooth climate anomalies
temperature anomaly / heating-degree anomaly
SE3-load vs SE1-core gradient anomaly for area_diff_proxy_se3
```

M3A outputs:

```text
m3a_temperature_delta_se1
m3a_temperature_delta_area_diff
```

Backward-compatible aliases may map old names to new names, but evidence/docs must use M3A.

## P0035-4: M3B special-day delta model

Create M3B, a conservative statistical special-day delta model analogous to M3A but driven by the special-day calendar.

M3B purpose:

```text
Estimate special-day / holiday / bridge-day deltas so M4 does not learn them as false week/year trends.
```

Targets must be split:

```text
SE1 system_proxy
SE3-SE1 area_diff_proxy
```

M3B target residual should be built after temperature normalization:

```text
m3b_target_residual = actual_price - M1_normal_price - M3A_temperature_delta
```

M3B must estimate deltas for categories such as:

```text
major_social_holiday
fixed_public_holiday
movable_public_holiday
holiday_eve
bridge_day_strong
bridge_day_weak
holiday_period_day
pre_holiday_transition_day
post_holiday_recovery_day
```

M3B should use robust medians/smoothing/shrinkage because there are few examples per holiday.

M3B outputs:

```text
m3b_special_day_delta_se1
m3b_special_day_delta_area_diff
m3ab_normalized_price_se1 = actual_se1 - m3a_temperature_delta_se1 - m3b_special_day_delta_se1
m3ab_normalized_area_diff = actual_area_diff - m3a_temperature_delta_area_diff - m3b_special_day_delta_area_diff
m3ab_normalized_se3 = m3ab_normalized_price_se1 + m3ab_normalized_area_diff
```

M3B must store enough metadata for later forecast recomposition:

```text
special_day_type
special_day_name
special_day_group
bridge_anchor
holiday_strength
model_delta
sample_count
shrinkage_factor
```

## P0035-5: M4 residual ML model

P0035 must rebuild M4 as an M1-anchored residual model.

Old P0034 issue:

```text
Standalone M4 tried to predict the whole target from calendar features and lost to M1.
```

New P0035 M4:

```text
m4_residual_target = actual_price - M3A_temperature_delta - M3B_special_day_delta - M1_normal_price
```

Equivalently:

```text
m4_residual_target = m3ab_normalized_price - M1_normal_price
```

Split targets:

```text
m4_residual_se1
m4_residual_area_diff
```

Prediction:

```text
m4_normalized_prediction_se1 = M1_se1 + m4_residual_prediction_se1
m4_normalized_prediction_area_diff = M1_area_diff + m4_residual_prediction_area_diff
m4_normalized_prediction_se3 = m4_normalized_prediction_se1 + m4_normalized_prediction_area_diff
```

Evaluation where special-day effects should be present must add back M3B as the final step:

```text
m4_eval_prediction_se1 = M1_se1 + m4_residual_prediction_se1 + M3B_special_day_delta_se1
m4_eval_prediction_area_diff = M1_area_diff + m4_residual_prediction_area_diff + M3B_special_day_delta_area_diff
m4_eval_prediction_se3 = m4_eval_prediction_se1 + m4_eval_prediction_area_diff
```

If evaluating against raw observed prices rather than temperature-normalized observed prices, document whether M3A is also added back. For P0035, preferred evaluation is:

```text
M4 structure + M3B special-day addback against temperature-normalized target
```

because M5 forecast-time temperature model is not built yet.

### M4 focus

M4 must focus on:

```text
long-term trends across years
slow market-structure changes
remaining smooth calendar residuals
holiday-normalized trend behavior
```

M4 should not focus on:

```text
ordinary week spikes caused by weather leftovers
holiday/special-day effects
wind/solar residuals, which are deferred to future M3C/M3D
```

Future deferred normalizers:

```text
M3C: solar/cloud/radiation anomaly delta
M3D: wind anomaly delta
```

The residual after M1 - M3A - M3B should mostly contain slow trend behavior plus noise and future wind/solar effects.

### M4 ML model recommendation

Preferred first model:

```text
M1-anchored HistGradientBoostingRegressor residual model
```

Required candidate support:

```text
HistGradientBoostingRegressor
Polynomial/Ridge fallback only as diagnostic fallback
optionally RandomForestRegressor or ExtraTreesRegressor as candidates
```

P0035 must not downgrade to a too-fast weak model just because Codex interactive runtime is constrained. Production training may take longer.

Runtime policy:

```text
interactive smoke build budget: 2-5 minutes
production model training budget: up to 60 minutes
manual research budget: up to 24 hours if explicitly run outside Codex
```

Codex must record wall-clock timing for each candidate model:

```text
candidate
parameters
start_time
end_time
elapsed_seconds
row_count
feature_count
reason_selected_or_rejected
```

## Atomic model promotion

P0035 must implement or document atomic model promotion for M4 artifacts.

Required behavior:

```text
train into staging/temp directory
validate and write holdout evidence
only then promote to active
if training fails/times out/performs worse than active, keep existing active model
```

A failed or slow M4 rebuild must never remove or corrupt the current active model.

Expected local paths, final paths may differ if documented:

```text
~/.smart-home/data/spotprice_ml_models/m4/staging/<run_id>/
~/.smart-home/data/spotprice_ml_models/m4/active/
```

## Daily pipeline policy

P0033 already has a 16:00 feature rebuild job. P0035 may update feature rebuild behavior, but must avoid unsafe launchd changes unless necessary.

Allowed production timing assumption:

```text
M1/M2/M3A/M3B feature rebuild around 16:00
M4 training may start after feature rebuild and may run up to 60 minutes or more
active model remains previous version until new version is validated and promoted
```

P0035 does not need to make M4 available before every minute. It only needs to keep some valid active M4 version available at each hour boundary.

## Holdout and comparison policy

P0035 must follow:

```text
requirements/packages/ML-holdout-evidence-policy.md
```

Required holdout comparison must include:

```text
M1 baseline
P0034 M4 sklearn polynomial ridge if available
P0035 M4 residual model
```

Metrics must be reported for:

```text
SE1 system_proxy
SE3-SE1 area_diff_proxy
recomposed SE3
```

Required comparisons:

```text
1. normalized target without M3B addback
2. evaluation target with M3B addback as final step
3. special-day holdout subset metrics
4. non-special-day holdout subset metrics
```

This is important because M4 should not appear bad merely because holiday effects were intentionally normalized out. Testing must add M3B back where the evaluation target includes special-day behavior.

## Storage requirements

Committed repo data:

```text
data/calendar/se_special_days_2022_2035.csv
```

Local feature DB:

```text
~/.smart-home/data/spotprice_model_features.sqlite3
```

Local model artifacts:

```text
~/.smart-home/data/spotprice_ml_models/m4/
```

Repo evidence:

```text
requirements/package-runs/P0035/
```

Expected feature DB tables/views or equivalents:

```text
calendar_special_days
m2_smooth_climate_normals
m2_smooth_climate_anomalies
m3a_temperature_delta
m3b_special_day_delta
m3ab_normalized_prices
m4_residual_training_rows
m4_residual_predictions
m4_candidate_timings
m4_promotion_manifest
```

## Evidence files

Expected:

```text
CHANGELOG.md
review.md
design.md
functions.md
attempts.md
special-day-calendar-summary.md
m2-smoothing-summary.md
m3a-temperature-summary.md
m3b-special-day-summary.md
m4-residual-model-summary.md
holdout-results.md
baseline-comparison.md
candidate-timings.md
model-promotion-summary.md
```

## Tests

Required tests include:

```text
- calendar row count 2022-2035 equals 5114
- leap days present for 2024, 2028, 2032
- Easter dates match known dates for several years
- Ascension Day = Easter Sunday + 39 days
- Friday after Ascension is bridge_day_strong
- Midsummer Eve/Day dates are correct for several years
- Midsummer Day is major_social_holiday and not ordinary Saturday
- All Saints Day is Saturday between Oct 31 and Nov 6
- bridge-day rules for Tuesday/Wednesday/Thursday holidays
- Christmas/New Year period classification
- M2 smooth normals do not condition on year and avoid sharp week artifacts
- M3 renamed to M3A outputs/aliases behave correctly
- M3B computes special-day deltas with shrinkage/sample counts
- M4 residual target equals actual - M3A - M3B - M1
- M4 evaluation addback includes M3B as final step
- active model is not overwritten on failed staging validation
```

## Non-goals

- No M5 forecast-time temperature delta model.
- No M6 forecast API.
- No M7 futures/absolute long-term forecast.
- No optimizer/control changes.
- No Shelly runtime changes.
- No Shelly deploy.
- No KVS writes.
- No Home Assistant integration.
- No live device access.
- No wind/solar normalization except documenting future M3C/M3D.

## Expected Codex output

- generated calendar path and row count
- special-day classification summary
- M2 smoothing change summary
- M3A rename/migration summary
- M3B special-day delta summary
- M4 residual model algorithm and candidate timings
- active/staging model promotion result
- holdout metrics including special-day addback
- baseline comparisons against M1 and P0034 M4
- tests run
- files changed
- no M5/M6/M7/API/device confirmation
- commit SHA after push

## Completion notes

To be filled after implementation.
