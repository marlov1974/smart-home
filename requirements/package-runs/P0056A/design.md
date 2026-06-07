# P0056A implementation design

## Package interpretation

P0056A builds a local measured consumption layer for northern European bidding zones. It is data preparation only and remains `LABB`.

## Implementation structure

Add:

```text
src/mac/services/spotprice_model_diagnostics/p0056a.py
tests/mac/services/spotprice_model_diagnostics/test_p0056a.py
```

The module will reuse P0052A/P0054P2 ENTSO-E token, request and XML helper patterns where possible.

## Intended changes

- Define explicit P0056A area scope and EIC mapping for SE1-SE4, NO1-NO5, DK1-DK2, FI, EE, LV, LT, DE_LU, PL and NL.
- Fetch ENTSO-E `documentType=A65`, `processType=A16` actual total load by yearly chunks from `2022-06-01T00:00:00Z`.
- Store source/native rows in `area_consumption_native_v1`.
- Aggregate to hourly time-weighted average MW in `area_consumption_hourly_v1`.
- Store area catalog rows in `area_consumption_area_catalog_v1`.
- Delete/rewrite only P0056A-generated rows to keep the load rerunnable.
- Produce compact package evidence and CSV summaries under `requirements/package-runs/P0056A/`.

## Hourly aggregation

ENTSO-E actual load quantities are treated as power/average MW over the native interval.

Rules:

- 60m rows become one hourly row as-is after unit normalization.
- Subhourly rows are time-weighted into the overlapping UTC hour.
- Mixed resolution is preserved in `native_resolution_mix`.
- Hourly rows retain `input_row_count` and `coverage_flag`.

## Validation strategy

- Per-area row count, min/max timestamp, native resolution mix, coverage, missing intervals, duplicates and value distribution.
- Negative and zero hour counts.
- SE3 consistency against corrected historical target table `entsoe_consumption_area_hourly_v1` / `SE3`.
- Source access review with response roots/status/points and no token content.

## Test strategy

Unit tests cover:

- area mapping includes all required primary areas
- yearly chunking
- native 15m/60m time-weighted hourly aggregation
- rerunnable table DDL schema expectations

Full verification runs P0056A ingestion, DB row-count queries, evidence checks, unit tests, compile and `git diff --check`.

## Risks and uncertainties

- ENTSO-E may return acknowledgement/no data for some areas or recent periods.
- Latest complete data may lag by area.
- Large raw datasets must remain in SQLite only; committed evidence stays compact.
