# P0056I Implementation Design

## Package Interpretation

P0056I tests whether SE2 36h consumption forecast quality is sensitive to training-window length while holding the P0056H2 protocol fixed.

The controlled variables are:

- area: `SE2`
- origin schedule: P0056H/P0056H2 06:00 Europe/Stockholm every fifth day
- horizon: 36h
- lag construction: P0056H2/P0056C static-style origin-anchored lag/rolling features
- weather protocol: P0056D actual-weather proxy LABB
- model method: P0056H2 HGB no-price with SE2 W12 features

The experimental variable is train-row filtering per forecast origin:

- `TW2`: forecast origin minus 2 calendar years to forecast origin
- `TW3`: forecast origin minus 3 calendar years to forecast origin
- `TWX`: `2022-06-01T00:00:00Z` to forecast origin

## Implementation Structure

Add `src/mac/services/spotprice_model_diagnostics/p0056i.py`.

The module will:

1. Load SE2 target/weather inputs using existing P0056C/P0056D loaders.
2. Build static-style SE2 modeling rows using P0056H2 helpers.
3. Build P0056H/P0056H2 origin schedule.
4. For each origin and train-window variant, filter train rows by target timestamp.
5. Fit the P0056H HGB helper with SE2 W12 features.
6. Predict 36h origin rows, score existing P0056H metric scopes and persist compact package-owned DB metrics.
7. Generate required P0056I evidence files.

## Intended Changes

- New package-run evidence under `requirements/package-runs/P0056I/`.
- New diagnostic module `p0056i.py`.
- New unit test `tests/mac/test_p0056i_train_windows.py`.
- Update P0056I package completion notes after execution.

## Deliberate Refactoring Decisions

No shared refactor is planned. P0056I may reuse P0056H2 functions directly instead of generalizing them now, because this package is a narrow diagnostic and not a runtime API.

## Test Strategy

- Unit-test train-window start computation.
- Unit-test train-row filtering includes rows at/after train start and before origin only.
- Compile the new module.
- Run the package module against the local feature DB.
- Verify DB row counts, evidence files, `git diff --check`, and no large artifacts.

## Risks and Uncertainties

- Calendar-year subtraction can differ from exact day-count years around leap days. P0056I describes 2.0/3.0 years, and calendar-year subtraction is the most interpretable match to that wording.
- Actual-weather proxy remains non-deployable LABB evidence.
- P0056H2 had 71 complete SE2 origins; P0056I should use the same complete SE2 origin set unless local input data changed.
