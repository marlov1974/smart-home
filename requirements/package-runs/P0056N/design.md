# P0056N Implementation Design

## Package

`P0056N`

## Package interpretation

Audit whether the suspicious SE2 actual-load spike on `2026-03-28` and the DST-period DayAhead rows are caused by raw/source data, hourly aggregation, UTC/local conversion or DayAhead local-day construction. This package must not train, improve or change forecast models.

## Chosen implementation structure

Add a narrow diagnostics module:

- `src/mac/services/spotprice_model_diagnostics/p0056n.py`

Add pure-helper tests:

- `tests/mac/test_p0056n_dst_audit.py`

Write evidence under:

- `requirements/package-runs/P0056N/`

The module will read:

- local SQLite `area_consumption_native_v1`
- local SQLite `area_consumption_hourly_v1`
- committed P0056M `hour-level-summary.csv`
- committed P0056M `day-level-results.csv`

## Intended changes

### Files/modules to change

- `src/mac/services/spotprice_model_diagnostics/p0056n.py`: new audit runner and evidence writer.
- `tests/mac/test_p0056n_dst_audit.py`: tests for local-day expected hours, duplicate UTC detection and classification helpers.
- `requirements/package-runs/P0056N/**`: review, design, function design and generated audit evidence.
- `requirements/packages/P0056N-labb-se2-dst-target-anomaly-audit.md`: completion notes only.
- function catalog docs if the new audit functions are useful for future packages.

### Files/modules intentionally not changed

- `p0056k.py`: this package audits DayAhead behavior but does not fix it.
- `p0056a.py`: this package audits source/aggregation output but does not rewrite ingestion.
- Shelly, Home Assistant, deploy paths and runtime config: out of scope.

## Refactoring decisions

No shared refactor planned. Helpers remain in P0056N unless future packages need durable reuse.

## Test strategy

- Unit-test DST expected local-hour mapping for Europe/Stockholm spring-forward.
- Unit-test duplicate UTC target detection on a synthetic delivery-day list.
- Unit-test anomaly classification from native/hourly evidence.
- Run `python3 -m unittest tests.mac.test_p0056n_dst_audit`.
- Compile the new module.
- Run P0056N module and verify required evidence files exist.
- Run `git diff --check`.

## Build / generated artifact strategy

Generated evidence will be Markdown plus compact CSV/JSON. No raw dumps are committed; only audit summaries and short scoped rows for the requested windows.

## Risks and uncertainties

- If the local DB lacks source metadata beyond ENTSO-E native values, classification may be limited to source-observed versus aggregation/DayAhead behavior.
- If ENTSO-E source itself contains the `2026-03-28` spike, P0056N can classify it as source-observed but cannot prove whether the external source is correct without an independent source.

## Design deviations during implementation

None yet.
