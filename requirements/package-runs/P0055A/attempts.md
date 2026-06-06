# P0055A attempts

## Attempt 1

Implemented the P0055A module, tests and evidence generation.

Initial full run completed with `PASS`, but review of `comparison-vs-direct.md` found `null` direct-vs-decomposition deltas. Root cause: decomposition aggregation used the original unscored direct rows instead of the scored direct component rows.

Fix:

- Updated aggregation input to use `component_results[forecast_direct_se3_best]["rows"]`.
- Reran unit tests, syntax check and the full P0055A analysis.

Final attempt result: `PASS`.
