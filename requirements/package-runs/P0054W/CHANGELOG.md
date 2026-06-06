# P0054W changelog

- Rebased P0054W onto operator heavy-fetch clarifications.
- Added eSett Open Data EXP03/EXP18 SE3 MGA masterdata and load-profile ingestion.
- Result: `PASS` / `full_fetch_complete`.
- Loaded rows: `14875628`.
- Completed periods: `10550`.
- No credentials, devices, runtime changes, A61 utilization, model training or raw data commits.

## 2026-06-06 clarification correction

- Added operator clarification evidence that monthly-settled and metered/profiled class must not be confused with monthly resolution.
- Confirmed P0054W local per-MGA `EXP18/LoadProfile` sum matches SE3/MBA `EXP15.profiled`.
- Confirmed `EXP15.metered` is the large missing component, but was found only at SE3/MBA level in public eSett Open Data, not per MGA.
- P0054W is therefore `STOP` for complete SE3 bottom-up per-MGA consumption until a per-MGA `metered/non_profiled` source or explicit residual model is approved.
- Added:
  - `profiled-monthly-source-search.md`
  - `coverage-vs-entsoe-by-settlement-class.md`
  - `missing-load-residual-plan.md`

## 2026-06-06 MGA type hypothesis test

- Tested the operator hypothesis that monthly-settled series may be represented as separate MGA objects.
- Public `EXP18/Aggregate` was queried for all SE3 `mgaType` groups for January 2025.
- Only `DISTRIBUTION` returned January load-profile rows; `REGIONAL`, `NONCON`, `PRODUCTION`, `TRANSMISSION` and `BORDER` returned no January `EXP18` volume.
- All `EXP18/Aggregate` rows across all SE3 MGA types still match `EXP15.profiled`, not `EXP15.metered` or `EXP15.total`.
- Added `mga-type-monthly-settlement-hypothesis.md`.
