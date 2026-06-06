# P0054Y2 implementation design

Status: `PASS`

## Interpretation

Build a local historical SE3 decomposition:

```text
16 profiled/load-profile MGA clusters
+ 1 calculated metered/non_profiled residual
```

The decomposition is LABB evidence and future-modeling input. It is not G2-KANDIDAT and does not train a forecast model.

## Implementation structure

Add a narrow Mac diagnostics module:

```text
src/mac/services/spotprice_model_diagnostics/p0054y2.py
```

The module will:

```text
1. read P0054W `esett_mga_consumption_native_v1`
2. classify loaded MGAs into 16 target cluster ids using deterministic local heuristics
3. aggregate 15m/60m energy to hourly positive MW-equivalent
4. join ENTSO-E SE3 hourly actual load
5. write three SQLite output tables
6. write compact P0054Y2 evidence files and CSV summaries
```

## Output tables

```text
se3_profiled_mga_cluster_hourly_v1
se3_consumption_metered_residual_hourly_v1
se3_consumption_profiled_residual_decomposition_hourly_v1
```

Rows are replaced for `generated_by_package='P0054Y2'` on rerun.

## Cluster rules

No external enrichment is allowed. Classification uses:

```text
MGA name and DSO/grid-owner name keyword heuristics
load volume rank
seasonality/base-load shape heuristics from P0054W rows
safe fallback groups when uncertain
```

Cluster labels remain explicitly `profiled/load-profile`, not measured.

## Test strategy

Add focused tests for:

```text
hourly energy-to-MW aggregation math
residual quality summary including negative count
deterministic cluster id construction
```

Run:

```text
python3 -m unittest tests.mac.services.spotprice_model_diagnostics.test_p0054y2
python3 -m src.mac.services.spotprice_model_diagnostics.p0054y2
git diff --check
```

## Risks and uncertainties

The 16-cluster taxonomy is interpretable but heuristic. It is good enough for LABB decomposition and next-package modeling tests, but not a durable geographic truth layer.

Residual is dominated by missing metered/non-profiled load and may also include source/timing differences between eSett and ENTSO-E.
