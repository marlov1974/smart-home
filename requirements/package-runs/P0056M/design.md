# P0056M Implementation Design

## Package

`P0056M`

## Package interpretation

Analyze the current SE2 `M6 WeightedEnsemble_no_price` realistic DayAhead baseline from P0056K by reconstructing per-origin/per-hour predictions and producing human-readable error slices. The package must not improve, retrain outside protocol, promote, deploy or use forbidden feature families.

## Chosen implementation structure

Add a narrow module:

- `src/mac/services/spotprice_model_diagnostics/p0056m.py`

Add tests:

- `tests/mac/test_p0056m_error_slices.py`

Write package evidence under:

- `requirements/package-runs/P0056M/`

The module will reuse P0056K loaders, feature construction, model specs, scoring helpers and DayAhead origin policy. It will run only SE2, only M6, while fitting the M1-M5 base models needed for the M6 weighted ensemble exactly as P0056K does.

## Intended changes

### Files/modules to change

- `src/mac/services/spotprice_model_diagnostics/p0056m.py`: new package-scoped analysis runner.
- `tests/mac/test_p0056m_error_slices.py`: unit tests for deterministic bins, slices, top/bottom ranking and leakage metadata.
- `docs/functions/00-index.md`: add package history entry if the new diagnostics become relevant for future packages.
- `docs/functions/mac/spotprice-model-diagnostics.md`: update durable diagnostics catalog if present.
- `requirements/package-runs/P0056M/**`: review, design, function design, generated evidence and completion notes.
- `requirements/packages/P0056M-labb-se2-m6-dayahead-error-slice-analysis.md`: completion notes only.

### Files/modules intentionally not changed

- P0056K model implementation: reused unchanged to preserve baseline comparability.
- Shelly, Home Assistant and deploy paths: out of scope.
- Local DB schemas: no table change planned.

## Refactoring decisions

No broad refactor. Any helper introduced in P0056M stays package-scoped unless it becomes clearly reusable.

## Test strategy

- Unit-test pure helpers: season, temperature/load/ramp/horizon bins, slice aggregation, top/bottom ranking and pattern labels.
- Compile the new module.
- Run `python3 -m unittest tests.mac.test_p0056m_error_slices`.
- Run P0056M module to generate evidence and verify reconstructed baseline matches P0056K SE2/M6 within a small tolerance.
- Run `git diff --check`.

## Build / generated artifact strategy

Generated artifacts are Markdown plus compact CSV/JSON under `requirements/package-runs/P0056M/`. Full hour-level CSV is acceptable because SE2-only P0056K scope is 240 origins x 24 hours.

## Risks and uncertainties

- Reconstructing M6 requires fitting base models per origin and may take meaningful CPU time.
- Available weather values are LABB actual-weather proxies inherited from P0056K, not production forecasts.
- If local dependencies differ from P0056K run, reconstructed metrics could drift. The runner must compare to P0056K aggregate evidence and report WARN on drift.

## Design deviations during implementation

None yet.
