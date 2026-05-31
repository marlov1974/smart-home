# P0039 Design

## Package Interpretation

P0039 adds a holiday-clean baseline and formal taxonomy for the Spotprice V2 component chain. The implementation will be a Mac-side diagnostic package, aligned with P0037/P0038, not a production forecast API or runtime promotion.

## Implementation Structure

Add `src/mac/services/spotprice_model_diagnostics/p0039.py`:

- load the same joined diagnostic rows used by P0037
- fit existing P0037 strict components as the M1-based reference chain
- fit P0039 M1B from clean calendar rows only
- fit M2A temperature normals from clean train rows
- fit M3A_m1b from `actual - M1B` on clean train rows
- fit M3B_m1b from `actual - M1B - M3A_m1b` on special train rows
- build full-year 2025 metrics for M1, M1B, M1+M3A+M3B, M1B+M3A_m1b, and M1B+M3A_m1b+M3B_m1b
- write required P0039 evidence files
- persist optional machine-readable `component-attribution-matrix.json`
- write diagnostic local feature DB tables with P0039 names

Add `tests/mac/services/spotprice_model_diagnostics/test_p0039.py` for contract tests.

Update `docs/functions/mac/spotprice-ml-normal-model.md` with taxonomy, M1B policy, and sequential residual target definitions.

## Deliberate Refactoring Decisions

- Reuse P0037 helpers instead of broad refactoring. This keeps P0039 isolated and avoids destabilizing P0037/P0038 evidence.
- Do not rename existing M3A/M3B tables or columns. P0039 adds M1B-suffixed outputs and documentation.
- Do not implement a new M4, M5, M6, M7, optimizer, API, or production activation path.

## Evidence Strategy

Required files under `requirements/package-runs/P0039/`:

- `CHANGELOG.md`
- `review.md`
- `design.md`
- `functions.md`
- `taxonomy.md`
- `m1b-training-row-policy.md`
- `m1b-baseline-summary.md`
- `m3a-temperature-m1b-summary.md`
- `m3b-special-day-m1b-summary.md`
- `sequential-residual-contract.md`
- `full-year-holdout-results.md`
- `component-attribution-summary.md`
- optional `component-attribution-matrix.json`

## Test Strategy

Run:

```bash
python3 -B -m unittest tests.mac.services.spotprice_model_diagnostics.test_p0039
python3 -B -m unittest tests.mac.services.spotprice_model_diagnostics.test_p0037 tests.mac.services.spotprice_model_diagnostics.test_p0038 tests.mac.services.spotprice_model_diagnostics.test_p0039
python3 -B -m src.mac.services.spotprice_model_diagnostics.p0039
git diff --check
```

If the local database command needs access outside the workspace, rerun with explicit escalation.

## Risks and Uncertainties

- Excluding all special days can make some week/weekday/hour buckets sparse. The existing M1 smoothing window and hourly fallback will handle sparse buckets, and evidence will report included/excluded row counts.
- P0039 can only evaluate M3C/M3D as future contract unless it reuses P0038 implementation with M1B. This package will document M3C/M3D/M4 sequential target contracts and keep current P0038 table names intact.
- Full-period existing M1 remains a production-reference diagnostic and is not strict holdout evidence.
