# Package P0038: Solar and wind normalization (M3C/M3D)

## Status

planned

## Package order

P0038

## Primary area

G2 / Mac tooling / spotprice V2 / exogenous normalization / solar / wind / M4 area-diff policy

## Decision summary

P0038 adds the next two exogenous normalization layers:

```text
M3C = solar/cloud/radiation delta normalization
M3D = wind delta normalization
```

Both layers must run before M4 residual learning.

P0038 also records the current model policy from P0037:

```text
- M4_SE1 is disabled / zero-gated until futures/forward/M7 exists.
- M4_area_diff for SE3-SE1 may remain enabled when it improves holdout.
```

Reason: P0037 showed that M4 on SE1 tries to solve a market-regime/level problem with calendar features. Futures/forward curves will later own this signal in M7. M4 may still help the SE3-SE1 area-diff shape/spread component.

P0038 must not build M5, M6/API or M7.

## Model stack after P0038

Training normalization target:

```text
actual
- M3A_temperature_delta
- M3B_special_day_delta
- M3C_solar_delta
- M3D_wind_delta
= m3abcd_exogenous_normalized_price
```

M4 should train only where currently allowed:

```text
M4_area_diff_target = m3abcd_normalized_area_diff - M1_area_diff
M4_SE1 = 0 / disabled / not used in recomposed SE3 until M7 exists or a later package re-enables it after full-year evidence.
```

Recommended recomposition for diagnostic observed reconstruction:

```text
SE1 = M1_SE1 + M3A_SE1 + M3B_SE1 + M3C_SE1 + M3D_SE1
area_diff = M1_area + M3A_area + M3B_area + M3C_area + M3D_area + M4_area
SE3 = SE1 + area_diff
```

## Scope

P0038 owns:

```text
1. Verify required solar/wind weather signals exist in the local weather DB.
2. Add/extend weather ingest if required signals are missing.
3. Build solar proxies and solar anomalies.
4. Build wind production proxies and wind anomalies.
5. Implement conservative M3C solar delta model.
6. Implement conservative M3D wind delta model.
7. Produce M3ABCD normalized series.
8. Update M4 training/evaluation policy so only area_diff M4 is used by default.
9. Run full-year component attribution on 2025, following P0037 style.
```

## Required source review

Codex must inspect before implementation:

```text
requirements/package-runs/P0031/**
requirements/package-runs/P0032/**
requirements/package-runs/P0035/**
requirements/package-runs/P0037/**
requirements/packages/P0037-full-year-holdout-component-attribution.md
src/mac/services/spotprice_temperature_normalization/**
src/mac/services/spotprice_ml_model/**
local feature DB: ~/.smart-home/data/spotprice_model_features.sqlite3
local weather/spotprice DBs used by P0031/P0032/P0035
```

## Weather signal availability

P0038 must first document which weather variables are available for all required locations and timestamps.

Solar candidates:

```text
shortwave_radiation
direct_radiation
diffuse_radiation
cloud_cover
cloud_cover_low
cloud_cover_mid
cloud_cover_high
sunshine_duration
is_day / daylight proxy
solar_elevation if available or derivable
```

Wind candidates:

```text
wind_speed_100m
wind_direction_100m
wind_speed_10m
wind_direction_10m
wind_gusts_10m
```

Preferred wind signal:

```text
wind_speed_100m
```

If `wind_speed_100m` is missing, P0038 must either:

```text
- extend weather ingest/backfill to include it, or
- STOP/WARN with explicit missing-signal evidence and use 10m wind only as diagnostic fallback.
```

Do not silently use weak fallback signals.

## Required wind proxy locations

P0038 must use wind weather near major wind production areas, not only load/weather proxy cities.

Mandatory wind locations:

```text
Malmö
Kalmar
Kristinehamn
Piteå
Ånge
Härnösand
```

If coordinates are not already in repo/config, Codex must add deterministic location definitions with documented coordinates and source note. Do not call live device APIs.

Initial grouping:

```text
south_wind_proxy:
  Malmö
  Kalmar

central_wind_proxy:
  Kristinehamn

north_wind_proxy:
  Piteå
  Ånge
  Härnösand
```

Initial within-group weights:

```text
south_wind_proxy:
  Malmö 0.55
  Kalmar 0.45

central_wind_proxy:
  Kristinehamn 1.00

north_wind_proxy:
  Piteå 0.35
  Ånge 0.35
  Härnösand 0.30
```

Initial system/area weights:

```text
M3D_SE1_system_wind_proxy:
  north_wind_proxy 0.50
  central_wind_proxy 0.25
  south_wind_proxy 0.25

M3D_area_diff_wind_proxy:
  south_wind_proxy 0.60
  central_wind_proxy 0.25
  north_wind_proxy 0.15
```

Required gradient diagnostics for SE3-SE1:

```text
south_wind_proxy - north_wind_proxy
central_wind_proxy - north_wind_proxy
south_wind_proxy - central_wind_proxy
```

## Solar proxy locations

P0038 may reuse existing P0031/P0032 weather proxy locations, but must document them.

Recommended initial solar groups:

```text
south_solar_proxy:
  Malmö
  Kalmar

se3_load_solar_proxy:
  Örebro
  Borlänge or nearest existing SE3/load proxy

north_solar_proxy:
  Umeå
  Luleå / Piteå if available
```

Solar likely matters most for area_diff because southern solar production can suppress SE3/SE4-like prices relative to SE1. But M3C must still estimate both:

```text
m3c_solar_delta_se1
m3c_solar_delta_area_diff
```

## Solar feature design

M3C should model abnormal solar production potential, not just raw sunshine.

Preferred solar proxy:

```text
solar_generation_potential = daylight_gate * radiation_proxy * clear_sky_or_seasonal_scale
```

If clear-sky radiation is unavailable, use robust cyclic normal radiation per location/hour/day-of-year as baseline.

Required solar anomaly:

```text
solar_anomaly = actual_solar_proxy - normal_solar_proxy_for_same_day_hour_location_group
```

Required gates:

```text
if daylight/solar_potential is near zero: solar_delta = 0
night hours must not learn solar effects
winter near-zero solar hours must be heavily shrunk
```

Suggested solar bucket dimensions:

```text
solar_anomaly_bucket: very_low_solar, low_solar, normal_solar, high_solar, very_high_solar
season bucket or smooth day-of-year group
hour/daylight bucket
proxy group
```

M3C must be conservative and robust:

```text
median residual by bucket
sample_count shrinkage
caps per target
minimum sample thresholds
```

## Wind feature design

M3D should model abnormal wind production potential.

Preferred wind power proxy:

```text
wind_power_proxy = capped_transform(wind_speed_100m)
```

Suggested transform:

```text
below cut-in: near 0
between cut-in and rated: wind_speed_100m^3 scaled
above rated: capped / flattened
```

Do not over-engineer turbine physics in v1. The key is to avoid treating wind speed linearly everywhere.

Required wind anomaly:

```text
wind_anomaly = wind_power_proxy - normal_wind_power_proxy_for_same_day_hour_location_group
```

Suggested wind buckets:

```text
very_low_wind
low_wind
normal_wind
high_wind
very_high_wind
```

Required gradient buckets for area_diff:

```text
south_minus_north_wind_bucket
central_minus_north_wind_bucket
```

M3D must be conservative and robust:

```text
median residual by bucket
sample_count shrinkage
caps per target
minimum sample thresholds
```

## Training order and targets

M3C target residual:

```text
m3c_target_residual = actual - M1 - M3A - M3B
```

M3D target residual:

```text
m3d_target_residual = actual - M1 - M3A - M3B - M3C
```

Both targets must be split:

```text
SE1 system_proxy
SE3-SE1 area_diff_proxy
```

Outputs:

```text
m3c_solar_delta_se1
m3c_solar_delta_area_diff
m3d_wind_delta_se1
m3d_wind_delta_area_diff
m3abcd_normalized_price_se1
m3abcd_normalized_area_diff
m3abcd_normalized_se3
```

Expected DB tables/views or equivalents:

```text
m3c_solar_normals
m3c_solar_anomalies
m3c_solar_delta
m3c_solar_delta_buckets
m3d_wind_normals
m3d_wind_anomalies
m3d_wind_delta
m3d_wind_delta_buckets
m3abcd_normalized_prices
```

## M4 policy update

P0038 must encode the current policy:

```text
M4_SE1 = disabled / zero-gated by default
M4_area_diff = enabled only if full-year holdout says it helps
```

Required evaluations:

```text
M1+M3A+M3B
M1+M3A+M3B+M3C
M1+M3A+M3B+M3C+M3D
M1+M3A+M3B+M3C+M3D+M4_area_diff_only
M1+M3A+M3B+M3C+M3D+M4_SE1_and_area_diff diagnostic only
```

Do not promote M4_SE1 as active unless a full-year holdout proves it improves recomposed SE3 and SE1 without material degradation.

## Evaluation and attribution

P0038 must use a full-year holdout, preferably the P0037 split:

```text
train:    2022-05-30..2023-12-31
validate: 2024-01-01..2024-12-31
holdout:  2025-01-01..2025-12-31
```

If Codex also reports 2026 partial holdout, label it secondary.

Required attribution questions:

```text
1. Does M3C improve daytime/summer/spring MAE?
2. Does M3C avoid changing night hours?
3. Does M3C improve SE3-SE1 area_diff more than SE1?
4. Does M3D improve windy/low-wind subsets?
5. Does M3D improve SE3-SE1 area_diff more than SE1?
6. Does M3D reduce residual correlation with wind anomaly?
7. Does M3C reduce residual correlation with solar anomaly?
8. Does adding M3C/M3D make M4_area_diff more stable?
9. Should M4_area_diff remain enabled after M3C/M3D?
10. Does M4_SE1 remain disabled?
```

Required subset metrics:

```text
all_hours
daylight_hours
night_hours
spring/summer/autumn/winter
solar_high_anomaly
solar_low_anomaly
wind_high_anomaly
wind_low_anomaly
normal_weekday
special_day_hours
SE1 target
area_diff target
recomposed SE3
```

Required metrics:

```text
MAE
RMSE
mean signed error
correlation before/after with solar anomaly
correlation before/after with wind anomaly
sample counts
```

## Caps and shrinkage

P0038 must not let M3C/M3D overfit rare weather combinations.

Initial caps may be conservative and must be documented, for example:

```text
M3C SE1 cap: +/-0.30
M3C area_diff cap: +/-0.30
M3D SE1 cap: +/-0.50
M3D area_diff cap: +/-0.50
```

Codex may choose different caps only if justified by residual distribution evidence.

Shrinkage must include sample count:

```text
delta = bucket_median * sample_count / (sample_count + shrinkage_k)
```

The chosen `shrinkage_k` must be documented.

## Evidence files

P0038 must create:

```text
requirements/package-runs/P0038/CHANGELOG.md
requirements/package-runs/P0038/review.md
requirements/package-runs/P0038/design.md
requirements/package-runs/P0038/functions.md
requirements/package-runs/P0038/weather-signal-availability.md
requirements/package-runs/P0038/solar-proxy-summary.md
requirements/package-runs/P0038/wind-proxy-summary.md
requirements/package-runs/P0038/m3c-solar-attribution.md
requirements/package-runs/P0038/m3d-wind-attribution.md
requirements/package-runs/P0038/m3abcd-normalized-summary.md
requirements/package-runs/P0038/m4-area-only-policy.md
requirements/package-runs/P0038/full-year-holdout-results.md
requirements/package-runs/P0038/component-attribution-summary.md
```

Optional machine-readable summaries:

```text
requirements/package-runs/P0038/component-attribution-matrix.json
requirements/package-runs/P0038/weather-proxy-definitions.json
```

Do not commit large prediction dumps or local SQLite DBs.

## Tests

Required tests:

```text
- mandatory wind locations exist with coordinates/proxy definitions
- wind groups and weights sum to 1.0 within group
- system/area wind proxy weights sum to 1.0
- wind_power_proxy is capped/nonlinear and monotonic before cap
- night solar_delta is zero or effectively zero
- solar anomaly normals do not condition on year
- wind anomaly normals do not condition on year
- M3C target = actual - M1 - M3A - M3B
- M3D target = actual - M1 - M3A - M3B - M3C
- m3abcd normalized formula is correct
- M4_SE1 disabled by default
- M4_area_diff-only recomposition equals SE1_without_M4 + area_with_M4
- full-year 2025 holdout has 8760 rows
- no M5/M6/M7/API/device code path is touched
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

## Expected Codex output

- PASS/WARN/STOP status
- weather signal availability summary
- whether wind_speed_100m exists or was added/backfilled
- solar proxy definitions and weights
- wind proxy definitions and weights, including Malmö/Kalmar/Kristinehamn/Piteå/Ånge/Härnösand
- M3C attribution result
- M3D attribution result
- M3ABCD normalized row counts
- M4 area-only policy result
- full-year 2025 holdout comparison
- whether M4_area_diff remains enabled
- confirmation M4_SE1 remains disabled
- tests run
- files changed
- no M5/M6/M7/API/device confirmation
- commit SHA after push

## Completion notes

To be filled after implementation.
