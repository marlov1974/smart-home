# P0025 review

## Classification

WARN

## Evidence

- Repository synchronized before package work:
  - `git fetch origin`
  - `git status --short --branch`
  - `git pull --ff-only`
- P0025 package exists:
  - `requirements/packages/P0025-spot-known-horizon-and-forecast-accuracy.md`
- P0024 code and evidence exist locally:
  - `src/mac/labs/weekly_home_optimizer_poc/spot.py`
  - `requirements/package-runs/P0024/findings.md`
- Current public API shape is unchanged from P0024:
  - CLI: `week`, `ppm`, `house-temp`, optional `people`, output flags.
  - HTTP API: `/api/weekly-home-poc?week=...&ppm=...&houseTemp=...&people=...`
- Current actual spot fixture schema matches P0025:
  - `utc_hour_start`
  - `local_hour_start`
  - `local_wall_hour`
  - `utc_offset`
  - `fold`
  - `quarter_count`
  - `price_mean`
  - `price_min`
  - `price_max`
- Current spot functions are:
  - `resolve_week_utc_hours`
  - `load_actual_spot_prices`
  - `patch_forecast_with_actual_prices`
  - `build_spot_plan`
  - `spot_indexes_for_week`
- Current row rendering is in:
  - `src/mac/labs/weekly_home_optimizer_poc/tables.py`
  - `src/mac/labs/weekly_home_optimizer_poc/server.py`
  - `src/mac/labs/weekly_home_optimizer_poc/html.py`

## Consistency result

The package is implementable. It is a direct refinement of P0024: P0024 currently patches every fixture-covered hour, while P0025 requires the planner to patch only the first fixed known horizon of 20 hours and expose future actuals as diagnostics only.

## Warnings and assumptions

- The package references `tests/mac/labs/weekly_home_optimizer_poc`, but the repository test path is `tests/mac/weekly_home_optimizer_poc`. Implementation and verification will use the existing repository path and document the substitution.
- The public API remains week-only. 2026 support will be implemented as internal function/test fixture capability with optional function parameters, not as public CLI or HTTP API churn.
- The existing P0024 `spot_index` field remains as a compatibility alias for the final planning index.
- Existing P0024 field names remain where useful, but P0025 adds clearer planning/outcome names and updates metadata model names.

## Scope guard

Changes are limited to weekly home optimizer POC code/tests/docs, small deterministic spot test fixture data if needed, and P0025 package-run evidence.
