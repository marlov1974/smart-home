# P0035 implementation design

## Package interpretation

P0035 corrects M4 by moving holiday/special-day effects out of the normal ML model and rebuilding M4 as an M1-anchored residual model.

## Implementation structure

New calendar module:

```text
src/mac/services/swedish_calendar/
data/calendar/se_special_days_2022_2035.csv
docs/functions/mac/swedish-special-day-calendar.md
```

Changed normalization module:

```text
src/mac/services/spotprice_temperature_normalization/core.py
```

Changed M4 module:

```text
src/mac/services/spotprice_ml_model/core.py
```

## Calendar

The calendar is generated deterministically from Python date rules for 2022-01-01 through 2035-12-31.

The generator computes:

- fixed public holidays
- Easter-derived holidays
- Midsummer Eve/Day/Sunday
- All Saints Day/Friday
- Christmas/New Year period days
- bridge days and transition/recovery days

Precedence: major social holidays and public holidays override bridge/period classifications; bridge days override normal days; period/transition/recovery days override normal days.

## M2 smoothing

M2 will keep no-year conditioning and replace the narrow 7-day median normal with a broader cyclic robust mean:

```text
normal = 0.70 * median(day +/- 7) + 0.30 * mean(day +/- 21)
```

This remains stdlib-only, smooths adjacent calendar days, preserves `bucket_year_count`, and records method metadata.

## M3A/M3B

M3A remains the existing temperature-delta logic but writes new tables:

```text
m3a_temperature_delta
m3a_temperature_delta_buckets
```

Compatibility aliases/views preserve:

```text
m3_temperature_delta_v1
m3_temperature_delta_buckets
```

M3B estimates special-day deltas from residuals after M1 and M3A:

```text
actual - M1 - M3A
```

It groups by stable special-day features and applies conservative shrinkage:

```text
delta = median_residual * sample_count / (sample_count + 24)
```

Caps:

```text
system_proxy_se1 = +/-0.50
area_diff_proxy_se3 = +/-0.35
```

## M3AB output

The primary normalized series becomes:

```text
m3ab_normalized_price_se1 = actual_se1 - m3a_delta_se1 - m3b_delta_se1
m3ab_normalized_area_diff = actual_area_diff - m3a_delta_area_diff - m3b_delta_area_diff
m3ab_normalized_se3 = se1 + area_diff
```

Compatibility columns in `m3_temp_normalized_prices_v1` continue to expose the M3A-only temperature-normalized names used by earlier packages while adding M3A/M3B/M3AB columns.

## M4 residual model

P0035 M4 feature rows read `m3ab_normalized_prices` when present.

Targets:

```text
residual_se1 = m3ab_normalized_price_se1 - normal_price_v1_se1
residual_area_diff = m3ab_normalized_area_diff - normal_price_v1_area_diff
```

Predictions:

```text
normalized_prediction = M1 + residual_prediction
eval_prediction = M1 + residual_prediction + M3B_delta
```

P0035 retains comparison against:

- M1
- P0034 polynomial M4 active/local result where available
- P0035 residual M4

## Atomic model promotion

Training writes to:

```text
~/.smart-home/data/spotprice_ml_models/m4/staging/<run_id>/
```

After validation it copies only the generated files to:

```text
~/.smart-home/data/spotprice_ml_models/m4/active/
```

Failed validation leaves active untouched.

## Test strategy

Tests cover calendar generation, bridge/holiday rules, M2 smoothing method metadata, M3A/M3B/M3AB output structure, M4 residual target math, addback math and active model promotion.

## Risks

Model quality may remain `WARN` if residual M4 does not beat M1 on holdout. P0035 must preserve the evidence rather than hiding the result.
