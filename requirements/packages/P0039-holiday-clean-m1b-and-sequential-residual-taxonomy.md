# Package P0039: Holiday-clean M1B and sequential residual taxonomy

## Status

implemented-warn

## Package order

P0039

## Primary area

G2 / Mac tooling / spotprice V2 / model taxonomy / M1B / sequential residual contracts

## Decision summary

P0039 formalizes the current Spotprice V2 model taxonomy and adds a holiday-clean baseline:

```text
M1  = current calm normal price baseline
M1B = holiday-clean normal price baseline
```

M1B is a variant of M1 built from a training dataset where special-day contamination is removed or strongly downweighted. It is primarily used to train and evaluate exogenous delta models cleanly.

P0039 also defines the forward taxonomy:

```text
A = temperature
B = special days / holidays / bridge days
C = solar / solar generation potential
D = wind / wind generation potential
```

This preserves the current code/evidence naming:

```text
M3A = temperature delta
M3B = special-day delta
M3C = solar delta
M3D = wind delta
```

There is no required M2B because special days are calendar-defined, not weather-normalized.

## Why this package exists

P0035-P0038 introduced M3A/M3B/M3C/M3D but exposed two architectural issues:

```text
1. M3A temperature should learn temperature delta from holiday-clean data.
2. M3B special-day delta should learn holiday effects from temperature-normalized residuals.
```

Current M1 may contain special-day artifacts because fixed and movable holidays can land on weekdays and distort calendar buckets.

Examples:

```text
- Christmas Day on a weekday affects weekday profile.
- National Day or First May on Tuesday/Thursday creates bridge-day effects.
- Easter moves between weeks and may smear into week-of-year patterns.
- Midsummer Day is not an ordinary Saturday.
```

M1B is introduced to reduce this contamination.

## Model taxonomy

Required definitions:

```text
M1:
  calm normal price / baseline, current production/reference baseline

M1B:
  holiday-clean M1-style baseline, excluding or downweighting special-day contaminated rows

M2A:
  normal temperature / climate normal

M2C:
  normal solar generation potential

M2D:
  normal wind generation potential

M3A:
  temperature anomaly price delta, learned from holiday-clean rows/residuals

M3B:
  special-day / holiday / bridge-day price delta, learned after M3A

M3C:
  solar anomaly price delta, learned after M3A and M3B

M3D:
  wind anomaly price delta, learned after M3A, M3B and M3C

M4:
  residual model after M1B + M3A + M3B + M3C + M3D
```

Current policy remains:

```text
M4_SE1 = disabled / zero-gated until futures/forward/M7 exists
M4_area_diff = diagnostic/optional, enabled only if full-year holdout improves recomposed SE3
```

## Important naming decision

Do not rename existing M3A/M3B code/tables in this package.

Use this domain mapping:

```text
A = temperature
B = special days
C = solar
D = wind
```

Reason: the repository already uses:

```text
M3A = temperature delta
M3B = special-day delta
```

Changing names now would create high churn and risk. P0039 must instead document the taxonomy and add aliases/docs where needed.

## M1B definition

M1B is an M1-style calm normal baseline built from rows where special-day contamination is removed or reduced.

M1B must preserve normal weekday/weekend learning:

```text
normal_weekday: included
normal_saturday: included
normal_sunday: included
```

M1B must exclude or strongly downweight special-day affected rows:

```text
fixed_public_holiday on weekdays
movable_public_holiday on weekdays
major_social_holiday
holiday_eve
bridge_day_strong
bridge_day_weak
holiday_period_day
pre_holiday_transition_day
post_holiday_recovery_day
special_weekend_day such as Midsummer Day / All Saints Day where classified
```

M1B must not treat Midsummer Day as an ordinary Saturday.

The implementation may choose exclusion or weights, but must document the chosen policy. Default recommendation:

```text
exclude all special_day_type != normal_weekday/normal_saturday/normal_sunday
```

If this leaves sparse buckets, use a documented fallback/smoothing strategy rather than leaking special days back into the baseline.

## Required training order

P0039 must formalize and, where practical, implement this sequential residual contract:

```text
M1B = holiday-clean baseline

M3A_temperature_delta learns from:
  actual - M1B
using:
  M2A temperature anomaly
and training rows:
  holiday-clean / special-day excluded or downweighted

M3B_special_day_delta learns from:
  actual - M1B - M3A
using:
  special-day calendar features

M3C_solar_delta learns from:
  actual - M1B - M3A - M3B
using:
  M2C solar anomaly

M3D_wind_delta learns from:
  actual - M1B - M3A - M3B - M3C
using:
  M2D wind anomaly

M4_residual learns from:
  actual - M1B - M3A - M3B - M3C - M3D
```

This contract must be written in docs and evidence so future packages do not confuse training order.

## M2 normal model requirements

P0039 must document current M2 models and ensure naming is clear.

### M2A temperature normal

```text
M2A = smooth cyclic normal temperature / climate normal
```

This corresponds to the current P0035 M2 smoothing work.

### M2C solar normal

```text
M2C = normal solar generation potential
```

M2C should use solar generation potential, not raw solar radiation only.

Expected basis from P0038:

```text
solar_generation_potential = shortwave_radiation * cloud adjustment * daylight/near-zero gate
```

M2C must define:

```text
solar_anomaly = actual_solar_generation_potential - M2C_normal_solar_generation_potential
```

Night/near-zero potential rows must be zero-gated or heavily shrunk.

### M2D wind normal

```text
M2D = normal wind generation potential
```

M2D should use capped nonlinear wind power proxy, not raw linear wind speed.

Expected basis from P0038:

```text
wind_power_proxy = capped nonlinear transform of wind_speed_100m
```

M2D must define:

```text
wind_anomaly = actual_wind_power_proxy - M2D_normal_wind_power_proxy
```

Wind proxy locations from P0038 remain required:

```text
Malmö
Kalmar
Kristinehamn
Piteå
Ånge
Härnösand
```

## Required outputs

P0039 should add tables/views or documented equivalents:

```text
m1b_holiday_clean_normal_price
m1b_training_row_policy
m3a_temperature_delta_m1b
m3b_special_day_delta_m1b
m3c_solar_delta_m1b
m3d_wind_delta_m1b
m3abcd_normalized_prices_m1b
```

If P0039 is implemented as design-only plus analysis, it must explicitly state which outputs are deferred. Preferred: implement M1B and at least recompute M3A/M3B using the M1B contract.

## Required evaluations

Use full-year 2025 holdout as primary diagnostic, matching P0037/P0038:

```text
train:    2022-05-30..2023-12-31
validate: 2024-01-01..2024-12-31
holdout:  2025-01-01..2025-12-31
```

Evaluate at least:

```text
M1
M1B
M1 + existing M3A + existing M3B
M1B + M3A_m1b
M1B + M3A_m1b + M3B_m1b
M1B + M3A_m1b + M3B_m1b + existing/updated M3C/M3D if available
```

Targets:

```text
SE1 system_proxy
SE3-SE1 area_diff_proxy
recomposed SE3
```

Metrics:

```text
MAE
RMSE
mean signed error
special-day subset metrics
non-special-day subset metrics
temperature bucket metrics
holiday weekday subset metrics
```

P0039 must explicitly answer:

```text
1. Does M1B improve training cleanliness versus M1?
2. Does M1B alone improve or worsen full-year holdout?
3. Does M3A trained on holiday-clean data improve temperature attribution?
4. Does M3B trained after M3A improve special-day attribution?
5. Does the M1B sequential chain beat the previous M1-based chain on recomposed SE3?
6. Should future M3C/M3D/M4 use M1B or M1 as their base?
```

## Leakage controls

P0039 must not compute holdout baselines from holdout rows in strict evidence.

Strict full-year holdout must fit:

```text
M1B train-only baseline without 2025
M3A_m1b without 2025
M3B_m1b without 2025
M3C/M3D_m1b without 2025 if recomputed
```

Existing full-period M1 may be reported only as production-reference or non-strict diagnostic.

## Expected evidence files

P0039 must create:

```text
requirements/package-runs/P0039/CHANGELOG.md
requirements/package-runs/P0039/review.md
requirements/package-runs/P0039/design.md
requirements/package-runs/P0039/functions.md
requirements/package-runs/P0039/taxonomy.md
requirements/package-runs/P0039/m1b-training-row-policy.md
requirements/package-runs/P0039/m1b-baseline-summary.md
requirements/package-runs/P0039/m3a-temperature-m1b-summary.md
requirements/package-runs/P0039/m3b-special-day-m1b-summary.md
requirements/package-runs/P0039/sequential-residual-contract.md
requirements/package-runs/P0039/full-year-holdout-results.md
requirements/package-runs/P0039/component-attribution-summary.md
```

Update docs:

```text
docs/functions/mac/spotprice-ml-normal-model.md
```

Optional machine-readable evidence:

```text
requirements/package-runs/P0039/component-attribution-matrix.json
```

Do not commit large SQLite databases or prediction dumps.

## Tests

Required tests:

```text
- taxonomy maps A=temperature, B=special days, C=solar, D=wind
- no required M2B normal model is expected
- M1B excludes or downweights special-day contaminated rows
- normal Saturdays and Sundays remain included unless specially classified
- Midsummer Day is not treated as a normal Saturday in M1B
- M3A_m1b target = actual - M1B
- M3A_m1b training rows exclude/downweight special days
- M3B_m1b target = actual - M1B - M3A_m1b
- M3C target contract follows actual - M1B - M3A - M3B
- M3D target contract follows actual - M1B - M3A - M3B - M3C
- M4 target contract follows actual - M1B - M3A - M3B - M3C - M3D
- full-year 2025 holdout has 8760 rows
- holdout rows are not used to fit strict M1B/M3 models
- no M5/M6/M7/API/device path is touched
```

## Non-goals

- No M5 forecast-time temperature model.
- No M6 forecast API.
- No M7 futures/absolute long-term model.
- No optimizer/control changes.
- No Shelly runtime changes.
- No Shelly deploy.
- No KVS writes.
- No Home Assistant integration.
- No live device access.
- No futures/forward ingestion.
- No production API changes.
- No full rename of existing M3A/M3B tables unless explicitly justified and approved.

## Expected Codex output

- PASS/WARN/STOP status
- taxonomy summary
- M1B row policy and row counts
- M1 vs M1B comparison
- M3A_m1b temperature attribution
- M3B_m1b special-day attribution
- sequential residual chain evaluation
- recommendation whether future M3C/M3D/M4 should use M1B
- tests run
- files changed
- no M5/M6/M7/API/device confirmation
- commit SHA after push

## Completion notes

Implemented as Mac-side diagnostics and evidence.

P0039 added a strict train-only M1B/M3A/M3B diagnostic chain and wrote M1B-suffixed local feature DB outputs.

Operator correction after first implementation: M1B is only the clean training/normalization surface. M1 remains the price baseplate. The corrected holdout chain is therefore:

```text
M1 + M3A_m1b + M3B_m1b
```

Corrected 2025 holdout:

```text
M1 recomposed SE3 MAE = 0.384666
M1B training-base-only recomposed SE3 MAE = 0.422423
M1 + existing M3A + M3B recomposed SE3 MAE = 0.374846
M1 + M3A_m1b recomposed SE3 MAE = 0.376722
M1 + M3A_m1b + M3B_m1b recomposed SE3 MAE = 0.372997
```

P0039 status is `PASS` after the correction: M1 remains the production/reference base unless a later package explicitly changes that policy, and M1B-trained M3A/M3B deltas slightly beat the current strict M1-based M3A/M3B chain on 2025 recomposed SE3 holdout.
