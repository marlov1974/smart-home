# P0035 consistency review

Result: WARN

## Interpretation

P0035 adds:

- deterministic Swedish special-day calendar for 2022-2035
- smoother M2 climate normals
- M3 terminology split into M3A temperature delta and M3B special-day delta
- M3AB normalized training series
- M1-anchored residual M4 with staging/active promotion and holdout evidence

Out of scope remains M5/M6/M7, forecast API, launchd activation, Home Assistant, Shelly, KVS, device calls and controls.

## Local input checks

Existing feature DB:

```text
/Users/marcus.lovenstad/.smart-home/data/spotprice_model_features.sqlite3
```

Existing P0033/P0034 coverage before P0035:

```text
start_date = 2022-05-30
end_date = 2026-05-24
row_count = 34944
```

`scikit-learn` is installed and available from the P0034 follow-up:

```text
sklearn = 1.6.1
```

## Consistency findings

P0035 is implementable, but the package is large and asks for several coordinated model changes at once. The implementation will keep compatibility views/aliases for prior P0033/P0034 names to avoid breaking existing downstream code during this package.

The preferred `HistGradientBoostingRegressor` model was already observed to be too slow in the prior P0034 follow-up for the full local dataset inside Codex. P0035 will still record candidate timing, but may select a faster deterministic sklearn residual model if it validates and promotes safely.

The package text says the 2022-2035 calendar should have 5114 rows and lists leap years 2024, 2028, 2032, with 2036 explicitly not included. The correct inclusive row count for 2022-01-01..2035-12-31 is 5113, because there are three leap days in that interval. P0035 will use the interval truth and store 5113 rows.

## Safety review

No live devices, Shelly, Home Assistant, KVS, actuator or production API paths are required. P0035 writes repo calendar/docs/tests and local Mac SQLite/model artifacts only.

Decision: WARN, proceed with scoped implementation and explicit evidence.
