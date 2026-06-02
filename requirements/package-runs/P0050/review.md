# P0050 consistency review

Status: PASS

## Repository facts checked

- Repository synchronized with `origin/main`; P0050 package file exists after fast-forward from `df35af8`.
- P0049 PASS evidence exists under `requirements/package-runs/P0049/`.
- Local SQLite contains both `se3_se1_bottleneck_training_dataset_v1` and `se3_se1_bottleneck_reservoir_analysis_v1`.
- `se3_se1_bottleneck_training_dataset_v1` has 34968 rows from 2022-05-30 through 2026-05-25, and `se3_minus_se1 = se3_price - se1_price` has 0 reconstruction errors.
- P0048 source table contains raw and normal/delta weather proxy fields, including `temperature_south_proxy_actual` and `temperature_south_proxy_delta`.
- P0049 derived table contains reservoir features but does not retain raw `temperature_south_proxy_actual`, so it is not sufficient as the only P0050 input.

## Interpretation

P0050 is implementable as a Mac-only diagnostics package. The source strategy will use P0048's `se3_se1_bottleneck_training_dataset_v1` as the primary input, then join P0049 reservoir fields from `se3_se1_bottleneck_reservoir_analysis_v1` by `timestamp_utc` for the P0049 feature-group comparison.

This satisfies the package's "latest P0049/P0048 dataset that contains" rule while avoiding invented heat-pump temperature data.

## Scope and safety

No Shelly, Home Assistant, KVS, device, production API, production forecast or deployable model work is required or allowed.

Expected writes are limited to:

- `src/mac/services/spotprice_model_diagnostics/p0050.py`
- `tests/mac/services/spotprice_model_diagnostics/test_p0050.py`
- `requirements/package-runs/P0050/**`
- `requirements/packages/P0050-*.md`
- `docs/functions/**`

## Risks and assumptions

- 48h price-rank windows will include an explanatory/oracle group because full 48h historical rank is behavioral evidence, not deployable forecast-origin evidence.
- Heat-pump pressure is proxy-only. No heat-pump telemetry is available, so conclusions must remain diagnostic.
- Exact model groups can be deterministic score baselines rather than heavy ML if they answer feature-family usefulness and keep the package conservative.

## Result

PASS. Continue with package-scoped design, function design and implementation.
