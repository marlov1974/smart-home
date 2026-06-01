# P0042 amendment: UTC storage and fixed-CET model calendar for seven-day index datasets

## Status

planned amendment to P0042

## Applies to

```text
requirements/packages/P0042-p0041-dataset-correction-area-diff-scale-and-window-audit.md
```

This amendment must be treated as part of P0042 implementation. Codex must read and satisfy both the original P0042 package and this amendment before P0042 is considered complete.

## Decision summary

P0042 must not perform a global timestamp migration.

The long-term rule is:

```text
timestamp_utc = primary storage and join truth
```

For the new seven-day index AI datasets, P0042 must add a fixed-CET model calendar layer:

```text
model_cet_timestamp = timestamp_utc + 1 hour, all year
model_cet_date      = date(model_cet_timestamp)
model_cet_hour      = hour(model_cet_timestamp)
```

This is not Europe/Stockholm civil time. It is fixed Swedish normal time, i.e. UTC+1 throughout the whole year.

Reason: P0041 skipped center dates because local Europe/Stockholm DST creates 23h/25h days. For the index AI training datasets we want stable 24h model days and 168h model seven-day windows. Fixed CET gives that without changing raw data storage.

## Required time model

P0042 must use this layered time model:

```text
1. timestamp_utc
   - primary identity for hourly rows
   - primary key for joins where possible
   - no DST ambiguity

2. stockholm_local_* diagnostics
   - derived using Europe/Stockholm
   - may have 23h/25h local days
   - used only for audit/diagnostic unless explicitly justified

3. model_cet_*
   - derived as UTC+1 fixed offset
   - used as the default calendar for AI-1/AI-2 dataset targets and features
   - always has 24 model hours per model day
```

Required fields on hourly AI dataset rows:

```text
timestamp_utc
stockholm_local_timestamp
stockholm_local_date
stockholm_local_hour
stockholm_utc_offset_hours
stockholm_is_dst
model_cet_timestamp
model_cet_date
model_cet_hour
model_cet_weekday
model_cet_day_of_year
model_cet_day_of_year_sin
model_cet_day_of_year_cos
model_cet_hour_sin
model_cet_hour_cos
```

AI features should use the `model_cet_*` calendar fields by default.

## AI-2 corrected day definition

For AI-2 hour-to-day targets, P0042 must use fixed-CET model days as the default target grouping:

```text
AI-2 model day = all hourly rows with the same model_cet_date
```

Expected complete AI-2 model day:

```text
24 hourly UTC timestamps
model_cet_hour = 0..23 exactly once each
```

This replaces the P0041 local civil day requirement that created DST skips.

AI-2 target remains:

```text
hour_shape = (hour_price - day_mean_price) / day_intraday_scale
```

but now:

```text
day_mean_price       = mean over fixed-CET model day
 day_intraday_scale   = robust scale over fixed-CET model day
```

The leading space above is not semantic; implementation should use normal field names.

## AI-1 corrected local-week definition

For AI-1 day-to-local-week targets, P0042 must use fixed-CET model dates as the default day axis.

For center model date `D`:

```text
AI-1 local seven-day period = model_cet_date D-2 .. D+4
```

A complete AI-1 local seven-day window means:

```text
7 complete fixed-CET model days
168 hourly UTC timestamps
```

This is allowed to cross calendar-year boundaries.

Valid example:

```text
D = 2024-12-30 model CET
window = 2024-12-28..2025-01-03 model CET
```

Do not skip this if the underlying UTC hourly rows exist.

## Holiday/calendar feature policy

P0042 must define which calendar is used for special-day features in the AI datasets.

Default requirement:

```text
Use model_cet_date for AI training calendar features.
```

This means summer civil-time holidays may be shifted by one civil hour relative to Europe/Stockholm, but AI model days remain stable 24h units.

P0042 must document this tradeoff explicitly:

```text
- stable fixed-CET model days avoid DST 23h/25h artifacts
- summer holiday boundaries differ by one civil hour from Europe/Stockholm
- raw data remains UTC, so future packages can compare Stockholm-local grouping if needed
```

If Codex finds that using Stockholm-local holiday date as a separate diagnostic feature is cheap/safe, it may add:

```text
stockholm_special_day_type
stockholm_special_day_name
```

but the primary model feature should be based on `model_cet_date`.

## M2 normal weather policy under fixed CET

P0042 must ensure M2A/M2C/M2D normal weather features are available on the fixed-CET model calendar used by AI datasets.

For hourly normals:

```text
bucket = signal × model_cet_day_of_year × model_cet_hour
```

For daily normals:

```text
bucket = signal × model_cet_day_of_year
```

Normals should remain smooth/cyclic. Do not use raw week-of-year categories.

P0042 may retain Stockholm-local normals as diagnostics, but AI datasets must use fixed-CET normals by default unless a documented STOP/WARN explains why this could not be done.

## Skipped center-date audit update

P0042 must update the skipped-center-date audit to classify the P0041 skip reason:

```text
dst_or_timezone_issue
```

where applicable.

P0042 must explicitly answer:

```text
1. How many P0041 skipped center dates were caused by DST/local-day 23h/25h behavior?
2. How many skipped center dates remain after rebuilding with fixed-CET model days?
3. Are any skipped center dates caused by calendar-year boundaries after the fixed-CET correction?
4. Are any skipped center dates caused by missing spot/weather rows after the fixed-CET correction?
```

Expected result:

```text
calendar_year_boundary_bug = 0
```

If not zero, P0042 must fix it or STOP.

## Area-diff scale interaction

The fixed-CET correction does not replace the area_diff scale fix.

P0042 must still solve:

```text
area_diff_proxy_se3 AI-2 hour_shape extreme values
```

using the scale-policy comparison required in the original P0042 package.

After fixed-CET rebuild and selected area_diff scale policy, P0042 must report before/after distributions for:

```text
AI-2 area_diff hour_shape
AI-1 area_diff day_level_shape
AI-1 area_diff log_day_scale_index
AI-1 area_diff log_local_7d_scale
```

## Required additional evidence files

P0042 must add:

```text
requirements/package-runs/P0042/fixed-cet-model-calendar.md
requirements/package-runs/P0042/time-field-contract.md
requirements/package-runs/P0042/dst-correction-summary.md
```

These are in addition to the original P0042 evidence files.

## Required tests

Add these tests to P0042:

```text
- timestamp_utc is present and unique for hourly dataset rows
- model_cet_timestamp = timestamp_utc + 1 hour
- each complete model_cet_date has exactly 24 rows per target series
- model_cet_hour is 0..23 exactly once per complete model date and target series
- AI-2 groups by model_cet_date, not Stockholm civil local date
- AI-1 D-2..D+4 windows use model_cet_date and contain 7 complete model days / 168 hours
- D-2..D+4 windows may cross calendar-year boundaries
- DST transition dates do not create 23h/25h model days in AI datasets
- original Stockholm-local DST fields are available as diagnostics or explicitly documented as omitted
- no global timestamp migration is performed
- no AI training is performed
- no M5/M6/M7/API/device path is touched
```

## Required answers

P0042 final evidence must explicitly answer:

```text
1. Did P0042 keep UTC as primary storage/join truth?
2. Did P0042 add fixed-CET model calendar fields?
3. Are AI-1 and AI-2 targets built on fixed-CET model days by default?
4. Did fixed-CET remove the DST-caused skipped center dates?
5. What tradeoff remains for summer civil-time holiday boundaries?
6. Were area_diff scale issues also corrected?
7. Is the corrected dataset ready for P0043 AI-2 training?
```

## Updated Codex instruction

Use this additional instruction together with the original P0042 prompt:

```text
Amend P0042 with a fixed-CET model calendar. Do not globally migrate data. Keep timestamp_utc as primary storage/join truth. Add model_cet_timestamp/date/hour derived as UTC+1 all year. Rebuild AI-1/AI-2 datasets using model_cet_date as the default calendar: AI-2 groups fixed 24h model days; AI-1 uses D-2..D+4 over model_cet_date with 168h windows. Keep Stockholm/Europe local time only as diagnostics. Document the one-hour summer holiday-boundary tradeoff. Rebuild M2 normal weather features on model_cet_day_of_year/hour. Continue to solve area_diff scale instability. Train no AI and build no API/device changes.
```
