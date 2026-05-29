# P0024 implementation design

## Package interpretation

P0024 upgrades the weekly home optimizer POC spot model from a coarse repeated period index into an hourly spot plan. The output must still contain exactly 168 hours, but each hour must now include provenance and optional actual-price patch diagnostics.

Known actual prices from `data/spot/spot_2025_hourly_europe_stockholm.csv` replace forecast shape for overlapping hours. Replacement preserves the forecast sum over the overlap period so the model scale remains stable while the hourly shape follows the actual prices.

## Implementation structure

- Add `src/mac/labs/weekly_home_optimizer_poc/spot.py`.
- Keep the existing period expansion helper as the internal forecast baseline.
- Add a `SpotPlan` dataclass to `schema.py`.
- Add `spot: SpotPlan` to `WeeklyPlan` while keeping `spot_index` stable for existing consumers.
- Update planner orchestration to build a spot plan before heat optimization.
- Update table, JSON, API and HTML rendering to expose the required summary and hourly fields.
- Add package-focused unit tests for patch math, hourly output, DST fixture uniqueness, summary/API fields and browser rendering.
- Update durable function documentation and local README files.

## Intended changes

- Spot forecast:
  - Validate requested week.
  - Build 168 forecast index values.
  - Resolve the operational week to 168 UTC hour keys using the 2025 Europe/Stockholm fixture year.
- Actual fixture:
  - Load hourly actual prices by unique `utc_hour_start`.
  - Validate duplicate UTC keys are rejected.
  - Validate all fixture rows represent complete 4-quarter hours.
- Patching:
  - Identify overlap hours by UTC key.
  - Normalize actual prices by their overlap mean.
  - Rescale proto-index values so their sum equals the forecast sum for overlap hours.
  - Mark patched rows as `actual_patched`; mark the rest as `forecast`.
  - Emit warning metadata and avoid patching for no overlap or zero-sum proto values.
- Output:
  - Add required spot summary fields.
  - Add required hourly debug fields.
  - Render spot model and provenance in the browser UI.

## Deliberate refactoring decisions

- P0024 creates a dedicated `spot.py` module instead of growing `input_profiles.py`, because spot now has fixture IO, patching, summary metadata and provenance.
- Existing `spot_indexes_for_week()` remains as a compatibility wrapper returning only `SpotPlan.spot_index`.
- `WeeklyPlan.spot_index` remains to avoid unnecessary changes in existing optimizer and output code.

## Test strategy

- Unit-test deterministic patch math with `[1, 1, 2, 2]` and `[10, 20, 30, 40]`.
- Unit-test that `build_spot_plan()` returns 168 hourly values and provenance arrays.
- Unit-test 2025 fixture DST semantics using UTC keys and local wall-hour duplicates.
- Unit-test JSON/API summary fields.
- Unit-test browser HTML renders spot metadata and `spot_source`.
- Run package-required unittest discovery commands, CLI smoke, server once-smoke and `git diff --check`.

## Risks and uncertainties

- The POC has no public year input, so actual-price fixture patching is tied to 2025 by package design.
- Week 53 does not exist in ISO year 2025; implementation must fall back to forecast-only with a warning instead of failing normal input validation.
- The internal forecast baseline is still coarse. This is allowed by P0024 as long as the public result is hourly and patching happens per hour.
