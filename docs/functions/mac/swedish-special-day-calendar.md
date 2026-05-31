# Swedish Special-Day Calendar

Last changed: P0035

## Module

```text
src.mac.services.swedish_calendar
```

## Purpose

Deterministic Swedish special-day calendar for model normalization. P0035 uses it to keep holiday, bridge-day and major social holiday effects out of M4's normal residual model.

## Data

Committed CSV:

```text
data/calendar/se_special_days_2022_2035.csv
```

The interval is inclusive:

```text
2022-01-01..2035-12-31
```

It contains 5113 rows. The package text expected 5114, but 2036 is outside the interval, so only 2024, 2028 and 2032 contribute leap days.

## Rules

The generator computes:

- fixed public holidays
- Easter-derived movable holidays
- Midsummer Eve, Day and Sunday
- All Saints Day and All Saints Friday
- Christmas/New Year period days
- bridge days around Tuesday, Wednesday and Thursday public holidays

Precedence favors public holidays and major social holidays over bridge/period classifications.

## Important Functions

`easter_sunday(year)` computes Gregorian Easter.

`midsummer_eve(year)` returns Friday between 19 and 25 June.

`all_saints_day(year)` returns Saturday between 31 October and 6 November.

`classify_special_day(day)` returns one schema row.

`generate_calendar(start_year, end_year)` returns all rows in the inclusive interval.

`write_calendar_csv(rows, path)` writes the committed CSV schema.
