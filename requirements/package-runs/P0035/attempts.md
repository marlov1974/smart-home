# P0035 attempts

## Attempt 1

Status: completed

Plan:

1. Generate deterministic Swedish special-day calendar and tests.
2. Extend P0033 feature builder with smoother M2, M3A/M3B and M3AB outputs.
3. Rebuild M4 as M1-anchored residual model with staging/active promotion.
4. Backfill local feature/model artifacts and persist holdout/baseline evidence.
5. Run package tests, service tests, validation and `git diff --check`.

Result:

- Generated `data/calendar/se_special_days_2022_2035.csv` with 5113 rows.
- Documented package row-count inconsistency: 2022-2035 has three leap days, not four.
- Backfilled local feature DB with M3A/M3B/M3AB outputs.
- Rebuilt local M4 residual model and promoted artifacts to active.
- Persisted holdout/baseline evidence.
- Residual M4 remains `WARN`: M1 still wins key holdout hourly and level metrics.

Knowhow promotion: skipped. The notable workflow rule, holdout evidence persistence, already exists in `requirements/packages/ML-holdout-evidence-policy.md`.
